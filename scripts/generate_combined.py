from utils import (
    GENERATED_DIR,
    dataset_updated_date,
    load_all_resources,
    log,
    save_json,
)


def generate_combined():
    resources = load_all_resources()
    output = {
        "generated": dataset_updated_date(resources),
        "total": len(resources),
        "resources": resources,
    }
    save_json(GENERATED_DIR / "all_resources.json", output)
    log(f"✅ Generated all_resources.json ({len(resources)} resources)")

if __name__ == "__main__":
    generate_combined()
