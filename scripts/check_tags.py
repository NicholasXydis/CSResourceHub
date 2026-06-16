import sys
from utils import load_json, load_all_resources, log, DATA_DIR

def check_tags():
    allowed_tags = set(load_json(DATA_DIR / "tags.json")["tags"])
    resources = load_all_resources()
    errors_found = False

    for resource in resources:
        tags = resource.get("tags", [])
        for tag in tags:
            if tag not in allowed_tags:
                log(f"❌ {resource.get('id')}: unknown tag '{tag}'")
                errors_found = True

    if not errors_found:
        log("✅ All tags valid.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    check_tags()
