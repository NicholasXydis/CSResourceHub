import json
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
SCHEMA_FILE = ROOT / "schema" / "resource.schema.json"
GENERATED_DIR = ROOT / "generated"

CATEGORY_LABELS = {
    "learning-resources": "Learning Resources",
    "communities": "Communities",
    "clubs": "Clubs",
    "volunteer": "Volunteer & Non-Profit",
    "ctfs": "CTFs",
    "competitions": "Competitions",
    "hackathons": "Hackathons",
    "game-jams": "Game Jams",
    "projects": "Projects",
    "repositories": "Repositories",
    "open-source-help": "Open Source Help",
    "research": "Research",
    "conferences": "Conferences",
    "fellowships": "Fellowships & Student Programs",
    "online-events": "Online Events",
    "career-fairs": "Career Fairs",
    "scholarships": "Scholarships",
    "startup-programs": "Startup Programs",
    "freelance": "Freelance",
    "certifications": "Certifications",
    "free-benefits": "Free Benefits",
}

CATEGORY_GROUPS = {
    "Learning & Development": [
        "learning-resources",
        "communities",
        "clubs",
    ],
    "Experience & Involvement": [
        "volunteer",
        "ctfs",
        "competitions",
        "hackathons",
        "game-jams",
    ],
    "Building & Open Source": [
        "projects",
        "repositories",
        "open-source-help",
    ],
    "Academic & Professional": [
        "research",
        "conferences",
        "fellowships",
    ],
    "Networking & Opportunities": [
        "online-events",
        "career-fairs",
        "scholarships",
        "startup-programs",
        "freelance",
    ],
    "Credentials & Perks": [
        "certifications",
        "free-benefits",
    ],
}


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def get_all_resource_files() -> list[Path]:
    files = []
    for root, _, filenames in os.walk(DATA_DIR):
        for filename in filenames:
            if filename.endswith(".json") and not filename.startswith("_"):
                path = Path(root) / filename
                if path.parent != DATA_DIR:
                    files.append(path)
    return sorted(files)


def load_all_resources() -> list[dict]:
    resources = []
    for path in get_all_resource_files():
        data = load_json(path)
        resources.extend(data.get("resources", []))
    return resources


def get_category_from_path(path: Path) -> str:
    return path.stem


def log(msg: str) -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", errors="replace").decode("ascii"))
