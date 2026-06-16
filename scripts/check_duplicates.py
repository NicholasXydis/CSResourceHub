import sys
from utils import load_all_resources, log

def check_duplicates():
    resources = load_all_resources()
    seen_urls = {}
    seen_ids = {}
    errors_found = False

    for resource in resources:
        url = resource.get("url")
        rid = resource.get("id")

        if url in seen_urls:
            log(f"❌ Duplicate URL: {url} (ids: {rid}, {seen_urls[url]})")
            errors_found = True
        else:
            seen_urls[url] = rid

        if rid in seen_ids:
            log(f"❌ Duplicate ID: {rid}")
            errors_found = True
        else:
            seen_ids[rid] = True

    if not errors_found:
        log("✅ No duplicates found.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    check_duplicates()
