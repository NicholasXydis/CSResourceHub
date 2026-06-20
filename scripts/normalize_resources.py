import sys

from utils import get_all_resource_files, load_json, log, save_json

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
    month_map = canonical_map(MONTH_VALUES)
    errors_found = False
    changed_files = []

    for path in get_all_resource_files():
        data = load_json(path)
        file_changed = False
        for resource in data.get("resources", []):
            rid = resource.get("id")
            if "location" in resource:
                cleaned_location = resource["location"].strip()
                if resource["location"] != cleaned_location:
                    resource["location"] = cleaned_location
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
