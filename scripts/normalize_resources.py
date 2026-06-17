import sys

from utils import DATA_DIR, get_all_resource_files, load_json, log, save_json

COST_VALUES = ["free", "freemium", "paid"]
MONTH_VALUES = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def canonical_map(values):
    return {value.casefold(): value for value in values}


def normalize_resources():
    allowed_regions = load_json(DATA_DIR / "regions.json")["regions"]
    region_map = canonical_map(allowed_regions)
    cost_map = canonical_map(COST_VALUES)
    month_map = canonical_map(MONTH_VALUES)
    errors_found = False
    changed_files = []

    for path in get_all_resource_files():
        data = load_json(path)
        file_changed = False
        for resource in data.get("resources", []):
            rid = resource.get("id")
            normalized_regions = []
            for region in resource.get("region", []):
                cleaned = region.strip()
                canonical = region_map.get(cleaned.casefold())
                if not canonical:
                    log(f"❌ {rid}: unknown region '{region}'")
                    errors_found = True
                    normalized_regions.append(cleaned)
                else:
                    normalized_regions.append(canonical)
                    if region != canonical:
                        file_changed = True

            if resource.get("region") != normalized_regions:
                resource["region"] = normalized_regions
                file_changed = True

            if "cost" in resource:
                cost = resource["cost"]
                cleaned_cost = cost.strip()
                canonical_cost = cost_map.get(cleaned_cost.casefold())
                if not canonical_cost:
                    log(f"❌ {rid}: unknown cost '{cost}'")
                    errors_found = True
                elif cost != canonical_cost:
                    resource["cost"] = canonical_cost
                    file_changed = True

            if "month" in resource:
                month = resource["month"]
                cleaned_month = month.strip()
                canonical_month = month_map.get(cleaned_month.casefold())
                if not canonical_month:
                    log(f"❌ {rid}: unknown month '{month}'")
                    errors_found = True
                elif month != canonical_month:
                    resource["month"] = canonical_month
                    file_changed = True

        if file_changed:
            save_json(path, data)
            changed_files.append(path.name)

    if errors_found:
        sys.exit(1)

    if changed_files:
        log("✅ Normalized resources in: " + ", ".join(changed_files))
    else:
        log("✅ Resources already normalized.")


if __name__ == "__main__":
    normalize_resources()
