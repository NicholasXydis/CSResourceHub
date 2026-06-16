from utils import get_all_resource_files, load_json, log

def stats():
    total = 0
    for path in get_all_resource_files():
        data = load_json(path)
        count = len(data.get("resources", []))
        total += count
        log(f"{path.parent.name}/{path.name}: {count} resources")
    log(f"\nTotal: {total} resources")

if __name__ == "__main__":
    stats()
