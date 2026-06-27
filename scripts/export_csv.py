import csv

from utils import GENERATED_DIR, load_all_resources, log

CSV_FIELDS = [
    "id",
    "name",
    "url",
    "description",
    "category",
    "month",
    "location",
    "date_added",
    "last_verified",
]


def normalize_value(value):
    if isinstance(value, list):
        return ", ".join(str(item) for item in value)
    if value is None:
        return ""
    return value


def export_csv():
    resources = load_all_resources()
    output_path = GENERATED_DIR / "resources.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for resource in resources:
            writer.writerow(
                {field: normalize_value(resource.get(field)) for field in CSV_FIELDS}
            )

    log(f"✅ Generated resources.csv ({len(resources)} resources)")


if __name__ == "__main__":
    export_csv()
