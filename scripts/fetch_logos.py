import io
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from urllib.parse import quote, urljoin, urlparse

import requests
from net_safety import UnsafeUrl, read_capped, safe_request, safe_session
from PIL import Image
from utils import GENERATED_DIR, ROOT, load_all_resources, log, save_json

TIMEOUT = 15
MAX_WORKERS = 12
LOGO_SIZE = 64
MIN_SOURCE_SIZE = 16
SANITY_THRESHOLD = 0.4

LOGO_DIR = ROOT / "public" / "logos"
OUTPUT_FILE = GENERATED_DIR / "logos.json"
GOOGLE_FAVICON_ENDPOINT = "https://www.google.com/s2/favicons"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,image/avif,image/webp,image/apng,image/*,*/*;q=0.8",
}

FALLBACK_DOMAINS = {
    "blitz.codes",
    "cheat.sh",
    "csapp.cs.cmu.edu",
    "defcon.org",
    "elementsofprogramminginterviews.com",
    "gaia.cs.umass.edu",
    "gameenginebook.com",
    "gchq.github.io",
    "nand2tetris.org",
    "nostarch.com",
    "outreachy.org",
    "pages.cs.wisc.edu",
    "quantlib.org",
    "scsconcordia.com",
    "stroustrup.com",
    "tojam.ca",
    "umdctf.io",
}

LINK_TAG = re.compile(r"<link[^>]+>", re.I)
TAG_ATTR = re.compile(r"([a-zA-Z:_-]+)\s*=\s*[\"']([^\"']*)[\"']")


def domain_of(url: str) -> str:
    hostname = urlparse(url).hostname or ""
    return hostname.removeprefix("www.")


def prefers_fallback(domain: str) -> bool:
    return any(
        domain == entry or domain.endswith(f".{entry}") for entry in FALLBACK_DOMAINS
    )


def google_favicon_url(domain: str) -> str:
    return f"{GOOGLE_FAVICON_ENDPOINT}?domain={quote(domain)}&sz=128"


def download(session: requests.Session, url: str) -> bytes | None:
    try:
        with safe_request(session, "GET", url, TIMEOUT) as response:
            if response.status_code != 200:
                return None
            return read_capped(response)
    except (UnsafeUrl, requests.RequestException):
        return None


def declared_icons(session: requests.Session, page_url: str) -> list[str]:
    body = download(session, page_url)
    if not body:
        return []
    html = body.decode("utf-8", "ignore")

    icons: list[tuple[int, str]] = []
    for tag in LINK_TAG.findall(html):
        attrs = {k.lower(): v for k, v in TAG_ATTR.findall(tag)}
        rel = attrs.get("rel", "").lower()
        href = attrs.get("href")
        if not href or "icon" in rel and "mask" in rel:
            continue
        if "apple-touch-icon" in rel:
            icons.append((3, urljoin(page_url, href)))
        elif "icon" in rel:
            icons.append((2, urljoin(page_url, href)))

    icons.sort(key=lambda item: -item[0])
    return [url for _, url in icons]


def rasterize(body: bytes) -> Image.Image | None:
    try:
        image = Image.open(io.BytesIO(body))
    except Exception:
        return None

    best = image
    for index in range(getattr(image, "n_frames", 1)):
        try:
            image.seek(index)
        except EOFError:
            break
        if image.size[0] > best.size[0]:
            best = image.copy()

    if best.size[0] < MIN_SOURCE_SIZE or best.size[1] < MIN_SOURCE_SIZE:
        return None
    return best.convert("RGBA")


def square(image: Image.Image) -> Image.Image:
    side = max(image.size)
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(image, ((side - image.width) // 2, (side - image.height) // 2))
    return canvas.resize((LOGO_SIZE, LOGO_SIZE), Image.LANCZOS)


def best_logo(url: str) -> Image.Image | None:
    session = safe_session()
    session.headers.update(REQUEST_HEADERS)
    domain = domain_of(url)

    candidates: list[str] = []
    seen: set[str] = set()
    for candidate in (
        *declared_icons(session, url),
        urljoin(url, "/apple-touch-icon.png"),
        urljoin(url, "/favicon.ico"),
        google_favicon_url(domain),
    ):
        if candidate not in seen:
            seen.add(candidate)
            candidates.append(candidate)

    best: Image.Image | None = None
    best_rank: tuple[int, int] | None = None
    for index, candidate in enumerate(candidates):
        body = download(session, candidate)
        if not body:
            continue
        image = rasterize(body)
        if image is None:
            continue
        rank = (image.size[0], -index)
        if best_rank is None or rank > best_rank:
            best, best_rank = image, rank

    return best


def encode(image: Image.Image) -> bytes:
    buffer = io.BytesIO()
    square(image).save(buffer, "PNG", optimize=True)
    return buffer.getvalue()


def fetch_logo(domain: str, url: str) -> tuple[str, bool]:
    target = LOGO_DIR / f"{domain}.png"
    existing = target.read_bytes() if target.exists() else None

    image = best_logo(url)
    if image is None:
        if existing is not None:
            target.write_bytes(existing)
            return domain, True
        return domain, False

    encoded = encode(image)
    if existing is not None and existing != encoded:
        with Image.open(io.BytesIO(existing)) as previous:
            if previous.size[0] >= square(image).size[0] and image.size[0] < LOGO_SIZE:
                target.write_bytes(existing)
                return domain, True

    target.write_bytes(encoded)
    return domain, True


def fetch_logos() -> None:
    resources = load_all_resources()

    by_domain: dict[str, str] = {}
    for resource in resources:
        domain = domain_of(resource["url"])
        if domain:
            by_domain.setdefault(domain, resource["url"])

    fallback = sorted(d for d in by_domain if prefers_fallback(d))
    wanted = sorted(d for d in by_domain if not prefers_fallback(d))

    LOGO_DIR.mkdir(parents=True, exist_ok=True)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        results = list(pool.map(lambda d: fetch_logo(d, by_domain[d]), wanted))

    stored = sorted(domain for domain, ok in results if ok)
    without = sorted(domain for domain, ok in results if not ok)

    if wanted and len(without) / len(wanted) > SANITY_THRESHOLD:
        log(
            f"❌ {len(without)}/{len(wanted)} domains produced no logo. "
            "This looks like a network problem, not missing icons. "
            "logos.json was left unchanged."
        )
        sys.exit(1)

    keep = set(stored)
    for existing in LOGO_DIR.glob("*.png"):
        if existing.stem not in keep:
            existing.unlink()
            log(f"🗑️ {existing.stem}: removed, no longer in the dataset")

    for domain in fallback:
        log(f"➖ {domain}: curated fallback tile")
    for domain in without:
        log(f"❌ {domain}: no usable logo, using the fallback tile")

    save_json(
        OUTPUT_FILE,
        {
            "generated": str(date.today()),
            "checked": len(by_domain),
            "stored": stored,
        },
    )
    log(
        f"✅ Stored {len(stored)}/{len(by_domain)} logos "
        f"({len(fallback)} curated, {len(without)} without an icon)"
    )


if __name__ == "__main__":
    fetch_logos()
