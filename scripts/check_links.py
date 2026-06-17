import sys
from datetime import date

import requests
from utils import get_all_resource_files, load_json, log, save_json

TIMEOUT = 10


def check_url(url):
    try:
        response = requests.head(url, timeout=TIMEOUT, allow_redirects=True)
    except requests.RequestException:
        response = None

    if response is not None and response.status_code < 400:
        return True, response.status_code

    try:
        response = requests.get(url, timeout=TIMEOUT, allow_redirects=True)
    except requests.RequestException as exc:
        return False, str(exc)

    return response.status_code < 400, response.status_code


def check_links():
    dead_links = []
    today = str(date.today())
    touched_files = []

    for path in get_all_resource_files():
        data = load_json(path)
        file_changed = False
        for resource in data.get("resources", []):
            url = resource.get("url")
            rid = resource.get("id")
            ok, result = check_url(url)
            if ok:
                if resource.get("last_verified") != today:
                    resource["last_verified"] = today
                    file_changed = True
                log(f"✅ {rid}: {url}")
            else:
                dead_links.append((rid, url, result))
                log(f"❌ {rid}: {url} ({result})")

        if file_changed:
            save_json(path, data)
            touched_files.append(path.name)

    if dead_links:
        log(f"\n{len(dead_links)} dead link(s) found.")
        sys.exit(1)
    else:
        if touched_files:
            log("Updated last_verified in: " + ", ".join(touched_files))
        log("✅ All links alive.")

if __name__ == "__main__":
    check_links()
