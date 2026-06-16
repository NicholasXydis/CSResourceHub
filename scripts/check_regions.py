import sys

from utils import DATA_DIR, load_all_resources, load_json, log


def check_regions():
    allowed_regions = set(load_json(DATA_DIR / "regions.json")["regions"])
    resources = load_all_resources()
    errors_found = False

    for resource in resources:
        for region in resource.get("region", []):
            if region not in allowed_regions:
                log(f"❌ {resource.get('id')}: unknown region '{region}'")
                errors_found = True

    if not errors_found:
        log("✅ All regions valid.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    check_regions()
