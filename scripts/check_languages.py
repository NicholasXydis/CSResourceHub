import sys

from utils import DATA_DIR, load_all_resources, load_json, log


def check_languages():
    allowed_languages = set(load_json(DATA_DIR / "languages.json")["languages"])
    errors_found = False

    for resource in load_all_resources():
        for language in resource.get("language", []):
            if language not in allowed_languages:
                log(f"❌ {resource.get('id')}: unknown language '{language}'")
                errors_found = True

    if not errors_found:
        log("✅ All languages valid.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    check_languages()
