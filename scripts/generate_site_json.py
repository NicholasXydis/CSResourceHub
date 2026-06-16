from collections import defaultdict
from datetime import date

from utils import GENERATED_DIR, load_all_resources, log, save_json


def generate_site_json():
    resources = load_all_resources()
    by_category = defaultdict(list)
    for resource in resources:
        by_category[resource["category"]].append(resource)

    output = {
        "generated": str(date.today()),
        "total": len(resources),
        "categories": {
            k: sorted(v, key=lambda x: -x.get("quality", 0))
            for k, v in by_category.items()
        },
    }
    save_json(GENERATED_DIR / "site.json", output)
    log(f"✅ Generated site.json ({len(resources)} resources)")

if __name__ == "__main__":
    generate_site_json()
