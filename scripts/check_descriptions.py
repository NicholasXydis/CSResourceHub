import sys

from utils import load_all_resources, log

MAX_DESCRIPTION_LENGTH = 120


def check_descriptions():
    errors_found = False

    for resource in load_all_resources():
        description = resource.get("description", "")
        rid = resource.get("id")
        if not description.endswith("."):
            log(f"❌ {rid}: description must end with a period")
            errors_found = True
        if len(description) > MAX_DESCRIPTION_LENGTH:
            log(
                f"❌ {rid}: description is {len(description)} characters "
                f"(max {MAX_DESCRIPTION_LENGTH})"
            )
            errors_found = True

    if not errors_found:
        log("✅ All descriptions valid.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    check_descriptions()
