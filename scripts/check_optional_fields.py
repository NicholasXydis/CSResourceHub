from utils import load_all_resources, log

OPTIONAL_FIELDS = ["deadline", "quality", "tags", "type", "language"]


def check_optional_fields():
    resources = load_all_resources()
    if not resources:
        log("No resources found.")
        return

    for field in OPTIONAL_FIELDS:
        count = sum(1 for resource in resources if field in resource)
        pct = (count / len(resources)) * 100
        log(f"{field}: {count}/{len(resources)} ({pct:.1f}%)")


if __name__ == "__main__":
    check_optional_fields()
