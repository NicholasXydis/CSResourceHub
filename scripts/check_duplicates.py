import sys
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from utils import load_all_resources, log


def canonical_url(value: str) -> str:
    parsed = urlsplit(value.strip())
    hostname = (parsed.hostname or "").casefold()
    port = parsed.port
    if port and not (parsed.scheme.casefold() == "https" and port == 443):
        hostname = f"{hostname}:{port}"
    path = parsed.path.rstrip("/") or "/"
    query = urlencode(sorted(parse_qsl(parsed.query, keep_blank_values=True)))
    return urlunsplit((parsed.scheme.casefold(), hostname, path, query, ""))


def check_duplicates():
    resources = load_all_resources()
    seen_urls = {}
    seen_ids = {}
    seen_names = {}
    errors_found = False

    for resource in resources:
        url = resource.get("url")
        canonical = canonical_url(url) if isinstance(url, str) else url
        rid = resource.get("id")
        name = resource.get("name", "").casefold()

        if canonical in seen_urls:
            log(f"❌ Duplicate URL: {url} (ids: {rid}, {seen_urls[canonical]})")
            errors_found = True
        else:
            seen_urls[canonical] = rid

        if rid in seen_ids:
            log(f"❌ Duplicate ID: {rid}")
            errors_found = True
        else:
            seen_ids[rid] = True

        if name in seen_names:
            log(
                "❌ Duplicate name: "
                f"{resource.get('name')} (ids: {rid}, {seen_names[name]})"
            )
            errors_found = True
        else:
            seen_names[name] = rid

    if not errors_found:
        log("✅ No duplicates found.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    check_duplicates()
