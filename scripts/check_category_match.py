import sys

from utils import get_all_resource_files, get_category_from_path, load_json, log


def check_category_match():
    errors_found = False

    for path in get_all_resource_files():
        expected_category = get_category_from_path(path)
        data = load_json(path)
        for resource in data.get("resources", []):
            actual_category = resource.get("category")
            if actual_category != expected_category:
                log(
                    f"❌ {resource.get('id')}: category '{actual_category}' "
                    f"should be '{expected_category}' in {path.name}"
                )
                errors_found = True

    if not errors_found:
        log("✅ All resource categories match their files.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    check_category_match()
