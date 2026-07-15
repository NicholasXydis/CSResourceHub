import os
import sys
import time
from datetime import date
from pathlib import Path

import requests
from net_safety import UnsafeUrl, safe_request, safe_session
from requests.exceptions import SSLError
from utils import get_all_resource_files, load_json, log, save_json

TIMEOUT = 10
MAX_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 2
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
VERIFIED_STATUSES = set(range(200, 400))
HARD_DEAD_STATUSES = {404, 410}
INCONCLUSIVE_STATUSES = {401, 403, 408, 425, 429, 500, 502, 503, 504}


def request_url(session, method, url):
    with safe_request(session, method, url, TIMEOUT) as response:
        return response


def classify_response(response):
    status_code = response.status_code
    if status_code in VERIFIED_STATUSES:
        return "verified", status_code
    if status_code in HARD_DEAD_STATUSES:
        return "hard_dead", status_code
    if status_code in INCONCLUSIVE_STATUSES:
        return "inconclusive", f"{status_code} (blocked, rate-limited, or temporary)"
    return "inconclusive", f"{status_code} (unexpected status)"


def check_url_once(url):
    session = safe_session()
    session.headers.update(REQUEST_HEADERS)
    hard_dead_results = []
    inconclusive_results = []

    for method in ("HEAD", "GET"):
        try:
            response = request_url(session, method, url)
        except UnsafeUrl as exc:
            return "unsafe", str(exc)
        except SSLError as exc:
            inconclusive_results.append(f"certificate error: {exc}")
            continue
        except requests.RequestException as exc:
            inconclusive_results.append(str(exc))
            continue

        status, result = classify_response(response)
        if status == "verified":
            return status, result
        if status == "hard_dead":
            hard_dead_results.append(result)
        else:
            inconclusive_results.append(result)

    if hard_dead_results and not inconclusive_results:
        return "hard_dead", hard_dead_results[-1]
    if hard_dead_results:
        result = f"hard status {hard_dead_results[-1]} with inconclusive fallback"
        return "inconclusive", result
    result = "; ".join(str(value) for value in inconclusive_results)
    return "inconclusive", result or "no response"


def check_url(url):
    results = []
    for attempt in range(MAX_ATTEMPTS):
        status, result = check_url_once(url)
        results.append((status, result))
        if status in ("verified", "unsafe"):
            return status, result
        if attempt < MAX_ATTEMPTS - 1:
            time.sleep(RETRY_DELAY_SECONDS * (attempt + 1))

    if all(status == "hard_dead" for status, _ in results):
        return "hard_dead", results[-1][1]
    details = "; ".join(str(result) for _, result in results)
    message = f"not consistently dead after {MAX_ATTEMPTS} attempts: {details}"
    return "inconclusive", message


def check_links():
    hard_dead_links = []
    inconclusive_links = []
    unsafe_links = []
    today = str(date.today())
    touched_files = []

    for path in get_all_resource_files():
        data = load_json(path)
        file_changed = False
        for resource in data.get("resources", []):
            url = resource.get("url")
            rid = resource.get("id")
            status, result = check_url(url)
            if status == "verified":
                if resource.get("last_verified") != today:
                    resource["last_verified"] = today
                    file_changed = True
                log(f"✅ {rid}: {url} ({result})")
            elif status == "unsafe":
                unsafe_links.append((rid, url, result))
                log(f"🚫 {rid}: {url} ({result})")
            elif status == "hard_dead":
                hard_dead_links.append((rid, url, result))
                log(f"❌ {rid}: {url} ({result})")
            else:
                inconclusive_links.append((rid, url, result))
                log(f"⚠️ {rid}: {url} ({result})")

        if file_changed:
            save_json(path, data)
            touched_files.append(path.name)

    if touched_files:
        log("Updated last_verified in: " + ", ".join(touched_files))

    report_path = os.environ.get("LINK_REPORT_PATH")
    if report_path:
        save_json(
            Path(report_path),
            {
                "checked": today,
                "attempts": MAX_ATTEMPTS,
                "hard_dead": [
                    {"id": rid, "url": url, "result": result}
                    for rid, url, result in hard_dead_links
                ],
                "inconclusive": [
                    {"id": rid, "url": url, "result": result}
                    for rid, url, result in inconclusive_links
                ],
                "unsafe": [
                    {"id": rid, "url": url, "result": result}
                    for rid, url, result in unsafe_links
                ],
            },
        )
    if inconclusive_links:
        log(f"\n{len(inconclusive_links)} inconclusive link check(s); left unchanged.")
    if unsafe_links:
        log(f"\n{len(unsafe_links)} unsafe destination(s) blocked before request.")
        sys.exit(1)
    if hard_dead_links:
        log(f"\n{len(hard_dead_links)} hard-dead link(s) found.")
        sys.exit(1)
    log("✅ Link check finished without hard-dead links.")


if __name__ == "__main__":
    check_links()
