from datetime import date

from utils import DATA_DIR, load_json, log, save_json

CATEGORIES = {
    "1": ("learning-development", "learning-resources"),
    "2": ("learning-development", "communities"),
    "3": ("learning-development", "clubs"),
    "4": ("experience-involvement", "volunteer"),
    "5": ("experience-involvement", "ctfs"),
    "6": ("experience-involvement", "competitions"),
    "7": ("experience-involvement", "hackathons"),
    "8": ("experience-involvement", "game-jams"),
    "9": ("building-open-source", "projects"),
    "10": ("building-open-source", "repositories"),
    "11": ("building-open-source", "open-source-help"),
    "12": ("academic-professional", "research"),
    "13": ("academic-professional", "conferences"),
    "14": ("academic-professional", "fellowships"),
    "15": ("networking-opportunities", "online-events"),
    "16": ("networking-opportunities", "career-fairs"),
    "17": ("networking-opportunities", "scholarships"),
    "18": ("networking-opportunities", "startup-programs"),
    "19": ("networking-opportunities", "freelance"),
    "20": ("credentials-perks", "certifications"),
    "21": ("credentials-perks", "free-benefits"),
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
    location = prompt("Location (e.g. Online or Montreal, Quebec, Canada)")
    month = prompt("Month (optional)", required=False)
    date_added = prompt("Date added (YYYY-MM-DD)")

    resource = {
        "id": resource_id,
        "name": name,
        "url": url,
        "description": description,
        "category": category,
    }

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
