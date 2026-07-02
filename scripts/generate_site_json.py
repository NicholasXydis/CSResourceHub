from collections import defaultdict

from utils import (
    GENERATED_DIR,
    dataset_updated_date,
    load_all_resources,
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
    return (1, month_order, name)


def generate_site_json():
    resources = load_all_resources()
    by_category = defaultdict(list)
    for resource in resources:
        by_category[resource["category"]].append(resource)

    output = {
        "generated": dataset_updated_date(resources),
        "total": len(resources),
        "categories": {
            k: sorted(v, key=resource_sort_key) for k, v in by_category.items()
        },
    }
    save_json(GENERATED_DIR / "site.json", output)
    log(f"✅ Generated site.json ({len(resources)} resources)")

if __name__ == "__main__":
    generate_site_json()
