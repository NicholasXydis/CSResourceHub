from utils import load_all_resources, save_json, log, GENERATED_DIR
from datetime import date

def generate_combined():
    resources = load_all_resources()
    output = {
        "generated": str(date.today()),
        "total": len(resources),
        "resources": resources
    }
    save_json(GENERATED_DIR / "all_resources.json", output)
    log(f"✅ Generated all_resources.json ({len(resources)} resources)")

if __name__ == "__main__":
    generate_combined()
