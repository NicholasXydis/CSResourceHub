from utils import (
    CATEGORY_LABELS,
    EVENT_CATEGORIES,
    EVENT_TYPE,
    SCHEMA_FILE,
    get_all_resource_files,
    load_json,
    log,
)

ALLOWED_TYPES_BY_CATEGORY = {
    category: {EVENT_TYPE} for category in sorted(EVENT_CATEGORIES)
} | {
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
    "developer-resources": {
        "api",
        "data",
        "frontend",
        "tool",
    },
    "project-based-learning": {
        "build",
        "inspiration",
    },
    "internships-fellowships": {
        "fellowship",
        "internship",
    },
    "recruitment-events": {
        "career",
        "conference",
    },
    "student-benefits": {
        "discounts",
        "free",
    },
    "certifications": {
        "cloud",
        "cybersecurity",
    },
}


def check_allowlist_matches_schema(errors):
    schema_types = set(load_json(SCHEMA_FILE)["properties"]["type"]["enum"])
    for category, allowed_types in ALLOWED_TYPES_BY_CATEGORY.items():
        unknown = sorted(allowed_types - schema_types)
        if unknown:
            errors.append(
                f"check_types.py -> {category}: type(s) {', '.join(unknown)} "
                "are not in the schema's type enum"
            )

        is_event_category = category in EVENT_CATEGORIES
        allows_event = EVENT_TYPE in allowed_types
        if is_event_category and allowed_types != {EVENT_TYPE}:
            errors.append(
                f"check_types.py -> {category}: an Experience category must allow "
                f"only '{EVENT_TYPE}'"
            )
        if not is_event_category and allows_event:
            errors.append(
                f"check_types.py -> {category}: '{EVENT_TYPE}' is reserved for the "
                "Experience collection"
            )

    known = set(CATEGORY_LABELS)
    listed = set(ALLOWED_TYPES_BY_CATEGORY)
    for category in sorted(known - listed):
        errors.append(f"check_types.py: category '{category}' has no allowed types")
    for category in sorted(listed - known):
        errors.append(f"check_types.py: '{category}' is not a known category")


def check_types():
    errors = []
    check_allowlist_matches_schema(errors)

    for path in get_all_resource_files():
        data = load_json(path)
        category = data.get("category")
        allowed_types = ALLOWED_TYPES_BY_CATEGORY.get(category)
        for resource in data.get("resources", []):
            resource_type = resource.get("type")
            if resource_type is None:
                if category in EVENT_CATEGORIES:
                    errors.append(
                        f"{path.name} -> {resource.get('id')}: "
                        f"Experience resources require type '{EVENT_TYPE}'"
                    )
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
