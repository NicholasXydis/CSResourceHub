import ipaddress
import socket
from contextlib import contextmanager
from urllib.parse import urljoin, urlparse

import requests
from urllib3.util import connection as urllib3_connection

MAX_REDIRECTS = 5
MAX_BYTES = 2 * 1024 * 1024
REDIRECT_STATUSES = {301, 302, 303, 307, 308}


class UnsafeUrl(Exception):
    pass


def resolved_addresses(hostname: str, port: int) -> list[str]:
    try:
        infos = socket.getaddrinfo(hostname, port, proto=socket.IPPROTO_TCP)
    except (OSError, UnicodeError, ValueError) as exc:
        raise UnsafeUrl(f"cannot resolve {hostname}: {exc}") from exc
    return [info[4][0] for info in infos]


def assert_public_addresses(hostname: str, port: int) -> list[str]:
    addresses = resolved_addresses(hostname, port)
    for address in addresses:
        if not ipaddress.ip_address(address).is_global:
            raise UnsafeUrl(f"{hostname} resolves to non-public address {address}")
    return addresses


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
    assert_public_addresses(hostname, port)


_original_create_connection = urllib3_connection.create_connection


def _guarded_create_connection(address, *args, **kwargs):
    host, port = address[0], address[1]
    addresses = assert_public_addresses(host, port)

    last_error: OSError | None = None
    for ip in addresses:
        try:
            # ``ip`` is a literal, so no second name resolution happens here:
            # the socket connects to the exact address we just validated.
            return _original_create_connection((ip, port), *args, **kwargs)
        except OSError as exc:
            last_error = exc
    raise last_error if last_error else UnsafeUrl(f"cannot connect to {host}")


def _install_connection_guard() -> None:
    if getattr(urllib3_connection.create_connection, "_ssrf_guarded", False):
        return
    _guarded_create_connection._ssrf_guarded = True
    urllib3_connection.create_connection = _guarded_create_connection


_install_connection_guard()


def safe_session() -> requests.Session:
    session = requests.Session()
    # Ignore HTTP(S)_PROXY / NO_PROXY: a proxy resolves the destination itself,
    # which would bypass the DNS-pinning guard above.
    session.trust_env = False
    return session


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
