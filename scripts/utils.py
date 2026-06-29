import json
import os
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_DIR = ROOT / "data"
SCHEMA_FILE = ROOT / "schema" / "resource.schema.json"
GENERATED_DIR = ROOT / "generated"

CATEGORY_LABELS = {
    "learning-resources": "Learning Resources",
    "interview-prep": "Interview Prep",
    "communities-clubs": "Communities & Clubs",
    "hackathons": "Hackathons",
    "ctfs": "CTFs",
    "game-jams": "Game Jams",
    "competitions": "Competitions",
    "open-source": "Open Source",
    "useful-repositories": "Useful Repositories",
    "project-starters-kits": "Project Starters & Kits",
    "internships-fellowships": "Internships & Fellowships",
    "recruitment-events": "Recruitment & Events",
    "certifications": "Certifications",
    "free-developer-tools": "Free Developer Tools",
}

CATEGORY_GROUPS = {
    "Learning & Development": [
        "learning-resources",
        "interview-prep",
        "communities-clubs",
    ],
    "Experience": [
        "hackathons",
        "ctfs",
        "game-jams",
        "competitions",
    ],
    "Building & Open Source": [
        "open-source",
        "useful-repositories",
        "project-starters-kits",
    ],
    "Careers & Perks": [
        "internships-fellowships",
        "recruitment-events",
        "certifications",
        "free-developer-tools",
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


def dataset_updated_date(resources: list[dict] | None = None) -> str:
    resources = resources if resources is not None else load_all_resources()
    dates = [resource.get("date_added", "") for resource in resources]
    return max((value for value in dates if value), default="unknown")
