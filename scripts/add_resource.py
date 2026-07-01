from datetime import date

from utils import DATA_DIR, load_json, log, save_json

CATEGORIES = {
    "1": ("learning-development", "learning-resources"),
    "2": ("learning-development", "interview-prep"),
    "3": ("learning-development", "communities-clubs"),
    "4": ("experience-involvement", "hackathons"),
    "5": ("experience-involvement", "ctfs"),
    "6": ("experience-involvement", "game-jams"),
    "7": ("experience-involvement", "competitions"),
    "8": ("building-open-source", "open-source"),
    "9": ("building-open-source", "useful-repositories"),
    "10": ("building-open-source", "project-starters-kits"),
    "11": ("careers-perks", "internships-fellowships"),
    "12": ("careers-perks", "recruitment-events"),
    "13": ("careers-perks", "certifications"),
    "14": ("careers-perks", "free-developer-tools"),
}

def prompt(label, required=True):
    while True:
        val = input(f"{label}: ").strip()
        if val or not required:
            return val
        print("  Required.")


def add_resource():
    print("\nAvailable categories:")
    for k, (_, cat) in CATEGORIES.items():
        print(f"  {k}. {cat}")

    choice = prompt("Category number")
    if choice not in CATEGORIES:
        print("Invalid choice.")
        return

    folder, category = CATEGORIES[choice]
    file_path = DATA_DIR / folder / f"{category}.json"
    data = load_json(file_path)

    resource_id = prompt("ID (lowercase, hyphens)")
    name = prompt("Name")
    url = prompt("URL (https://)")
    description = prompt("Description (one sentence, ends with period)")
    location = prompt(
        "Location (optional; e.g. Online or Montreal, Quebec, Canada)",
        required=False,
    )
    month = prompt("Month (optional)", required=False)
    date_added = prompt("Date added (YYYY-MM-DD)")

    resource = {
        "id": resource_id,
        "name": name,
        "url": url,
        "description": description,
        "category": category,
    }

    if location:
        resource["location"] = location
    if month:
        resource["month"] = month
    if date_added:
        resource["date_added"] = date_added
    resource["last_verified"] = str(date.today())

    data["resources"].append(resource)
    save_json(file_path, data)
    log(f"\n✅ Added {resource['name']} to {category}")


if __name__ == "__main__":
    add_resource()
