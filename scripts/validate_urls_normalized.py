import sys
from urllib.parse import parse_qsl, urlparse

from utils import load_all_resources, log


def validate_urls_normalized():
    errors_found = False

    for resource in load_all_resources():
        url = resource.get("url", "")
        rid = resource.get("id")
        parsed_url = urlparse(url)

        if not url.startswith("https://"):
            log(f"❌ {rid}: URL must start with https://")
            errors_found = True
        if parsed_url.path.endswith("/") and parsed_url.path:
            log(f"❌ {rid}: URL must not have a trailing slash")
            errors_found = True
        for param, _ in parse_qsl(parsed_url.query):
            if param.lower().startswith("utm_"):
                log(f"❌ {rid}: URL must not include tracking param '{param}'")
                errors_found = True

    if not errors_found:
        log("✅ All URLs normalized.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    validate_urls_normalized()
