from utils import get_all_resource_files, load_json, log

ALLOWED_TYPES_BY_CATEGORY = {
    "learning-resources": {
        "book",
        "course",
        "news",
        "reference",
        "tool",
        "video",
        "website",
    },
    "interview-prep": {
        "book",
        "course",
        "guide",
        "platform",
        "tool",
    },
    "communities-clubs": {
        "club",
        "discord",
        "organization",
        "reddit",
    },
    "open-source": {
        "organization",
        "project",
        "resource",
    },
}


def check_types():
    errors = []
    for path in get_all_resource_files():
        data = load_json(path)
        category = data.get("category")
        allowed_types = ALLOWED_TYPES_BY_CATEGORY.get(category)
        for resource in data.get("resources", []):
            resource_type = resource.get("type")
            if resource_type is None:
                continue
            if allowed_types is None:
                errors.append(
                    f"{path.name} -> {resource.get('id')}: "
                    f"type is not enabled for category '{category}'"
                )
            elif resource_type not in allowed_types:
                allowed = ", ".join(sorted(allowed_types))
                errors.append(
                    f"{path.name} -> {resource.get('id')}: "
                    f"type '{resource_type}' is not allowed for {category}; "
                    f"allowed: {allowed}"
                )

    if errors:
        for error in errors:
            log(f"❌ {error}")
        raise SystemExit(1)
    log("✅ All resource types valid.")


if __name__ == "__main__":
    check_types()
