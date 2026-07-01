import sys

from utils import get_all_resource_files, load_json, log

BANNED_LOCATIONS = {"North-America", "USA"}


def check_locations():
    errors_found = False

    for path in get_all_resource_files():
        data = load_json(path)
        for resource in data.get("resources", []):
            if "location" not in resource:
                continue
            location = resource.get("location")
            if not isinstance(location, str) or not location.strip():
                log(f"❌ {resource.get('id')}: invalid location")
                errors_found = True
                continue
            if location.strip() in BANNED_LOCATIONS:
                log(f"❌ {resource.get('id')}: broad location '{location}'")
                errors_found = True

    if not errors_found:
        log("✅ All locations valid.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    check_locations()
