from utils import get_all_resource_files, load_json, log, save_json

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
    name = resource.get("name", "").lower()
    if resource_type:
        return (0, resource_type, month_order, name)
    return (1, month_order, name)


def sort_resources():
    for path in get_all_resource_files():
        data = load_json(path)
        resources = data.get("resources", [])
        sorted_resources = sorted(resources, key=resource_sort_key)
        if resources != sorted_resources:
            data["resources"] = sorted_resources
            save_json(path, data)
            log(f"✅ Sorted {path.name}")
        else:
            log(f"— {path.name} already sorted")


if __name__ == "__main__":
    sort_resources()
