import sys

from utils import DATA_DIR, load_all_resources, load_json, log


def check_types():
    allowed_types = set(load_json(DATA_DIR / "types.json")["types"])
    errors_found = False

    for resource in load_all_resources():
        resource_type = resource.get("type")
        if resource_type and resource_type not in allowed_types:
            log(f"❌ {resource.get('id')}: unknown type '{resource_type}'")
            errors_found = True

    if not errors_found:
        log("✅ All types valid.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    check_types()
