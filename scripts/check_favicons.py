import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from hashlib import sha256
from urllib.parse import quote, urljoin, urlparse

import requests
from utils import GENERATED_DIR, load_all_resources, load_json, log, save_json

TIMEOUT = 10
MAX_WORKERS = 12
OUTPUT_FILE = GENERATED_DIR / "favicons.json"
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}
DEFINITELY_MISSING_STATUSES = {404, 410}
GOOGLE_FAVICON_ENDPOINT = "https://www.google.com/s2/favicons"
UNRESOLVABLE_DOMAIN = "no-such-host.invalid"
SANITY_THRESHOLD = 0.5


def domain_of(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    return hostname.removeprefix("www.")


def favicon_url(url: str) -> str:
    return urljoin(url, "/favicon.ico")


def google_favicon_url(domain: str) -> str:
    return f"{GOOGLE_FAVICON_ENDPOINT}?domain={quote(domain)}&sz=128"


def fetch(session: requests.Session, url: str) -> requests.Response | None:
    try:
        return session.get(url, timeout=TIMEOUT, allow_redirects=True)
    except requests.RequestException:
        return None


def google_default_icon_hash(session: requests.Session) -> str | None:
    response = fetch(session, google_favicon_url(UNRESOLVABLE_DOMAIN))
    if response is None or not response.content:
        return None
    return sha256(response.content).hexdigest()


def probe_site_icon(session: requests.Session, url: str) -> str:
    response = fetch(session, favicon_url(url))
    if response is None:
        return "inconclusive"

    status = response.status_code
    if status in DEFINITELY_MISSING_STATUSES:
        return "missing"
    if status >= 400:
        return "inconclusive"

    content_type = response.headers.get("Content-Type", "").lower()

    if "html" in content_type:
        return "missing"
    if not response.content:
        return "missing"
    if content_type and not (
        content_type.startswith("image/")
        or "icon" in content_type
        or "octet-stream" in content_type
    ):
        return "missing"
    return "present"


def probe_google_icon(session: requests.Session, domain: str, default_hash: str) -> str:
    response = fetch(session, google_favicon_url(domain))
    if response is None or not response.content:
        return "inconclusive"

    is_default = sha256(response.content).hexdigest() == default_hash
    if response.status_code == 404 and is_default:
        return "missing"
    if response.status_code == 200 and not is_default:
        return "present"
    return "inconclusive"


def probe_favicon(url: str, default_hash: str) -> tuple[str, str, bool]:
    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)
    domain = domain_of(url)

    site = probe_site_icon(session, url)
    google = probe_google_icon(session, domain, default_hash)
    unresolved = site == "inconclusive" and google == "inconclusive"

    if google == "present":
        return "google", "google favicon", unresolved
    if site == "present":
        return "site", "site favicon only", unresolved
    if site == "missing" and google == "missing":
        return "missing", "no icon from site or google", unresolved

    detail = f"google unconfirmed (site={site}, google={google})"
    return "site", detail, unresolved


def check_favicons() -> None:
    resources = load_all_resources()

    by_domain: dict[str, str] = {}
    for resource in resources:
        domain = domain_of(resource["url"])
        if domain:
            by_domain.setdefault(domain, resource["url"])

    previous: set[str] = set()
    if OUTPUT_FILE.exists():
        previous = set(load_json(OUTPUT_FILE).get("missing", []))

    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)
    default_hash = google_default_icon_hash(session)
    if default_hash is None:
        log(
            "❌ Could not fingerprint Google's default favicon. "
            "favicons.json was left unchanged."
        )
        sys.exit(1)

    domains = sorted(by_domain)
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        verdicts = list(
            pool.map(lambda d: probe_favicon(by_domain[d], default_hash), domains)
        )

    missing: set[str] = set()
    site_first: set[str] = set()
    inconclusive: list[str] = []
    for domain, (verdict, detail, unresolved) in zip(domains, verdicts):
        if unresolved:
            inconclusive.append(domain)
        if verdict == "missing":
            missing.add(domain)
            log(f"❌ {domain}: no usable favicon ({detail})")
        elif verdict == "site":
            if unresolved and domain in previous:
                missing.add(domain)
            else:
                site_first.add(domain)
            log(f"✅ {domain}: {detail}")
        else:
            log(f"✅ {domain}: {detail}")

    if domains and len(inconclusive) / len(domains) > SANITY_THRESHOLD:
        log(
            f"❌ {len(inconclusive)}/{len(domains)} domains were inconclusive. "
            "This looks like a local network problem, not missing favicons. "
            "favicons.json was left unchanged."
        )
        sys.exit(1)

    output = {
        "generated": str(date.today()),
        "checked": len(domains),
        "missing": sorted(missing),
        "siteOnly": sorted(site_first - missing),
    }
    save_json(OUTPUT_FILE, output)

    added = sorted(missing - previous)
    removed = sorted(previous - missing)
    if added:
        log("Newly missing: " + ", ".join(added))
    if removed:
        log("Now serving a favicon: " + ", ".join(removed))
    if inconclusive:
        log(f"{len(inconclusive)} inconclusive domain(s); left unchanged.")
    log(f"✅ Generated favicons.json ({len(missing)}/{len(domains)} missing)")


if __name__ == "__main__":
    check_favicons()
