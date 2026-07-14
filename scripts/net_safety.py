import ipaddress
import socket
from contextlib import contextmanager
from urllib.parse import urljoin, urlparse

import requests

MAX_REDIRECTS = 5
MAX_BYTES = 2 * 1024 * 1024
REDIRECT_STATUSES = {301, 302, 303, 307, 308}


class UnsafeUrl(Exception):
    pass


def resolved_addresses(hostname: str, port: int) -> list[str]:
    try:
        infos = socket.getaddrinfo(hostname, port, proto=socket.IPPROTO_TCP)
    except socket.gaierror as exc:
        raise UnsafeUrl(f"cannot resolve {hostname}") from exc
    return [info[4][0] for info in infos]


def assert_safe_url(url: str) -> None:
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        port = parsed.port or 443
    except ValueError as exc:
        raise UnsafeUrl(f"malformed url {url}: {exc}") from exc

    if parsed.scheme != "https":
        raise UnsafeUrl(f"non-https scheme: {parsed.scheme or 'none'}")

    if not hostname:
        raise UnsafeUrl("missing hostname")
    for address in resolved_addresses(hostname, port):
        if not ipaddress.ip_address(address).is_global:
            raise UnsafeUrl(f"{hostname} resolves to non-public address {address}")


@contextmanager
def safe_request(session: requests.Session, method: str, url: str, timeout: int):
    current = url
    seen = set()

    for _ in range(MAX_REDIRECTS + 1):
        if current in seen:
            raise UnsafeUrl(f"redirect loop at {current}")
        seen.add(current)
        assert_safe_url(current)

        response = session.request(
            method,
            current,
            timeout=timeout,
            allow_redirects=False,
            stream=True,
        )
        location = response.headers.get("Location")
        if response.status_code in REDIRECT_STATUSES and location:
            response.close()
            current = urljoin(current, location)
            continue

        try:
            yield response
        finally:
            response.close()
        return

    raise UnsafeUrl(f"more than {MAX_REDIRECTS} redirects from {url}")


def read_capped(response: requests.Response, max_bytes: int = MAX_BYTES) -> bytes:
    chunks = []
    total = 0
    for chunk in response.iter_content(8192):
        total += len(chunk)
        if total > max_bytes:
            raise UnsafeUrl(f"response exceeded {max_bytes} bytes")
        chunks.append(chunk)
    return b"".join(chunks)
