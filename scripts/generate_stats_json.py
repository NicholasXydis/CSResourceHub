from datetime import date

from utils import (
    CATEGORY_GROUPS,
    CATEGORY_LABELS,
    GENERATED_DIR,
    get_all_resource_files,
    load_json,
    log,
    save_json,
)


def generate_stats_json():
    discovered_categories = {}
    for path in get_all_resource_files():
        data = load_json(path)
        discovered_categories[data["category"]] = len(data.get("resources", []))

    categories = {
        category: discovered_categories.get(category, 0) for category in CATEGORY_LABELS
    }

    groups = {}
    for group, group_categories in CATEGORY_GROUPS.items():
        group_counts = {
            category: categories.get(category, 0) for category in group_categories
        }
        groups[group] = {
            "total": sum(group_counts.values()),
            "categories": group_counts,
        }

    output = {
        "generated": str(date.today()),
        "total": sum(categories.values()),
        "categories": categories,
        "groups": groups,
    }
    save_json(GENERATED_DIR / "stats.json", output)
    log(f"✅ Generated stats.json ({output['total']} resources)")


if __name__ == "__main__":
    generate_stats_json()
