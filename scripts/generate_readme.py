from collections import defaultdict
from utils import load_all_resources, load_json, save_json, log, ROOT, GENERATED_DIR
from datetime import date

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

def generate_readme():
    resources = load_all_resources()
    by_category = defaultdict(list)
    for resource in resources:
        by_category[resource["category"]].append(resource)

    total = len(resources)
    lines = []
    lines.append("# CS Resource Hub\n")
    lines.append("> A curated open dataset of resources, opportunities, and tools for CS students.\n")
    lines.append(f"![Resources](https://img.shields.io/badge/resources-{total}-blue)\n")
    lines.append(f"![Last Updated](https://img.shields.io/badge/updated-{date.today()}-green)\n")
    lines.append("\n## Table of Contents\n")

    for category, label in CATEGORY_LABELS.items():
        anchor = label.lower().replace(" ", "-").replace("&", "").replace("--", "-")
        lines.append(f"- [{label}](#{anchor})\n")

    lines.append("\n---\n")

    for category, label in CATEGORY_LABELS.items():
        cat_resources = sorted(by_category.get(category, []), key=lambda x: -x.get("quality", 0))
        lines.append(f"\n## {label}\n")
        lines.append(f"> {len(cat_resources)} resources\n")
        if cat_resources:
            lines.append("| Name | Description | Cost | Region |\n")
            lines.append("|------|-------------|------|--------|\n")
            for r in cat_resources:
                name = f"[{r['name']}]({r['url']})"
                desc = r.get("description", "")
                cost = r.get("cost", "")
                region = ", ".join(r.get("region", []))
                lines.append(f"| {name} | {desc} | {cost} | {region} |\n")

    readme = "".join(lines)
    readme_path = ROOT / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)

    save_json(GENERATED_DIR / "README_DATA.json", {
        "generated": str(date.today()),
        "total": total,
        "by_category": {k: len(v) for k, v in by_category.items()}
    })

    log(f"✅ Generated README.md ({total} resources)")

if __name__ == "__main__":
    generate_readme()
