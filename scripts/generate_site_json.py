from collections import defaultdict

from check_types import ALLOWED_TYPES_BY_CATEGORY
from utils import (
    CATEGORY_GROUPS,
    CATEGORY_LABELS,
    GENERATED_DIR,
    GROUP_ICONS,
    SCHEMA_FILE,
    dataset_updated_date,
    load_all_resources,
    load_json,
    log,
    save_json,
)

MONTH_ORDER = {
    "January": 1,
    "February": 2,
    "March": 3,
    "April": 4,
    "May": 5,
    "June": 6,
    "July": 7,
    "August": 8,
    "September": 9,
    "October": 10,
    "November": 11,
    "December": 12,
}


def resource_sort_key(resource):
    resource_type = resource.get("type")
    month = resource.get("month")
    month_order = MONTH_ORDER.get(month, len(MONTH_ORDER) + 1)
    name = resource["name"].lower()
    if resource_type:
        return (0, resource_type, month_order, name)
    return (1, "", month_order, name)


def generate_site_json():
    resources = load_all_resources()
    by_category = defaultdict(list)
    for resource in resources:
        by_category[resource["category"]].append(resource)

    unknown = sorted(set(by_category) - set(CATEGORY_LABELS))
    if unknown:
        raise SystemExit(
            "❌ Unknown categories with no label in utils.CATEGORY_LABELS: "
            + ", ".join(unknown)
        )

    categories = {
        category: sorted(by_category.get(category, []), key=resource_sort_key)
        for category in CATEGORY_LABELS
    }
    groups = {
        group: {
            "icon": GROUP_ICONS[group],
            "categories": group_categories,
            "total": sum(len(categories[category]) for category in group_categories),
        }
        for group, group_categories in CATEGORY_GROUPS.items()
    }

    schema = load_json(SCHEMA_FILE)
    resource_types = schema["properties"]["type"]["enum"]

    output = {
        "generated": dataset_updated_date(resources),
        "total": len(resources),
        "labels": dict(CATEGORY_LABELS),
        "types": resource_types,
        "allowedTypes": {
            category: sorted(ALLOWED_TYPES_BY_CATEGORY[category])
            for category in CATEGORY_LABELS
        },
        "groups": groups,
        "categories": categories,
    }
    save_json(GENERATED_DIR / "site.json", output)
    log(f"✅ Generated site.json ({len(resources)} resources)")


if __name__ == "__main__":
    generate_site_json()
