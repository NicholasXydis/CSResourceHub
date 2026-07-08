import re
import sys

from utils import get_all_resource_files, load_json, log

BANNED_LOCATIONS = {"Canada", "North-America", "USA"}
BANNED_SUFFIXES = (", Canada", ", USA", ", United States")
BANNED_REGION_ABBREVIATIONS = {
    "AB",
    "BC",
    "CA",
    "MB",
    "NB",
    "NL",
    "NS",
    "NT",
    "NU",
    "ON",
    "PA",
    "PE",
    "QC",
    "SK",
    "TX",
    "YT",
}
REGION_ABBREVIATION_RE = re.compile(
    r",\s*(" + "|".join(sorted(BANNED_REGION_ABBREVIATIONS)) + r")$"
)


def check_locations():
    errors_found = False

    for path in get_all_resource_files():
        data = load_json(path)
        for resource in data.get("resources", []):
            if "location" not in resource:
                continue
            location = resource.get("location")
            rid = resource.get("id")
            if not isinstance(location, str) or not location.strip():
                log(f"❌ {rid}: invalid location")
                errors_found = True
                continue

            normalized = location.strip()
            if normalized in BANNED_LOCATIONS:
                log(f"❌ {rid}: broad location '{location}'")
                errors_found = True
            if normalized.endswith(BANNED_SUFFIXES):
                log(f"❌ {rid}: location should not include country suffix")
                errors_found = True
            if REGION_ABBREVIATION_RE.search(normalized):
                log(f"❌ {rid}: expand province/state abbreviation in '{location}'")
                errors_found = True

    if not errors_found:
        log("✅ All locations valid.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    check_locations()
