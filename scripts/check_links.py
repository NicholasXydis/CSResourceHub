import sys

import requests
from utils import load_all_resources, log

TIMEOUT = 10


def check_links():
    resources = load_all_resources()
    dead_links = []

    for resource in resources:
        url = resource.get("url")
        rid = resource.get("id")
        try:
            response = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
            if response.status_code >= 400:
                dead_links.append((rid, url, response.status_code))
                log(f"❌ {rid}: {url} ({response.status_code})")
            else:
                log(f"✅ {rid}: {url}")
        except Exception as e:
            dead_links.append((rid, url, str(e)))
            log(f"❌ {rid}: {url} ({e})")

    if dead_links:
        log(f"\n{len(dead_links)} dead link(s) found.")
        sys.exit(1)
    else:
        log("✅ All links alive.")

if __name__ == "__main__":
    check_links()
