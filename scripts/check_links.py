import sys
from datetime import date

import requests
from requests.exceptions import SSLError
from urllib3.exceptions import InsecureRequestWarning
from utils import get_all_resource_files, load_json, log, save_json

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

TIMEOUT = 10
REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;"
        "q=0.9,image/avif,image/webp,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}
SOFT_OK_STATUSES = {403}


def request_url(session, method, url, verify=True):
    return session.request(
        method,
        url,
        timeout=TIMEOUT,
        allow_redirects=True,
        verify=verify,
    )


def check_url(url):
    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)

    try:
        response = request_url(session, "HEAD", url)
    except requests.RequestException:
        response = None

    if response is not None and response.status_code < 400:
        return True, response.status_code
    if response is not None and response.status_code in SOFT_OK_STATUSES:
        return True, f"{response.status_code} (blocked to automated checks)"

    try:
        response = request_url(session, "GET", url)
    except SSLError:
        try:
            response = request_url(session, "GET", url, verify=False)
        except requests.RequestException as exc:
            return False, str(exc)
    except requests.RequestException as exc:
        return False, str(exc)

    if response.status_code < 400:
        return True, response.status_code
    if response.status_code in SOFT_OK_STATUSES:
        return True, f"{response.status_code} (blocked to automated checks)"
    return False, response.status_code


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
                if isinstance(result, str):
                    log(f"⚠️ {rid}: {url} ({result})")
                else:
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
