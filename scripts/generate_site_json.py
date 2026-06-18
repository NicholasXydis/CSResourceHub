from collections import defaultdict
from datetime import date

from utils import GENERATED_DIR, load_all_resources, log, save_json

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
    month = resource.get("month")
    if month in MONTH_ORDER:
        return (0, MONTH_ORDER[month], resource["name"].lower())
    return (1, resource["name"].lower())


def generate_site_json():
    resources = load_all_resources()
    by_category = defaultdict(list)
    for resource in resources:
        by_category[resource["category"]].append(resource)

    output = {
        "generated": str(date.today()),
        "total": len(resources),
        "categories": {
            k: sorted(v, key=resource_sort_key) for k, v in by_category.items()
        },
    }
    save_json(GENERATED_DIR / "site.json", output)
    log(f"✅ Generated site.json ({len(resources)} resources)")

if __name__ == "__main__":
    generate_site_json()
