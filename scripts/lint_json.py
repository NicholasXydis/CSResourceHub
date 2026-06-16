import json
from utils import get_all_resource_files, log, DATA_DIR

def lint_json():
    files = get_all_resource_files()
    files += [DATA_DIR / "tags.json", DATA_DIR / "regions.json", DATA_DIR / "LAST_UPDATED.json"]

    for path in files:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        data = json.loads(content)
        formatted = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
        if content != formatted:
            with open(path, "w", encoding="utf-8") as f:
                f.write(formatted)
            log(f"✅ Reformatted {path.name}")
        else:
            log(f"— {path.name} already formatted")

if __name__ == "__main__":
    lint_json()
