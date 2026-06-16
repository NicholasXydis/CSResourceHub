from utils import get_all_resource_files, load_json, log, save_json


def sort_resources():
    for path in get_all_resource_files():
        data = load_json(path)
        resources = data.get("resources", [])
        sorted_resources = sorted(resources, key=lambda r: r.get("name", "").lower())
        if resources != sorted_resources:
            data["resources"] = sorted_resources
            save_json(path, data)
            log(f"✅ Sorted {path.name}")
        else:
            log(f"— {path.name} already sorted")


if __name__ == "__main__":
    sort_resources()
