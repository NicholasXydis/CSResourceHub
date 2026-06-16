from collections import defaultdict
from datetime import date

from utils import GENERATED_DIR, ROOT, load_all_resources, log, save_json

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

CATEGORY_ICONS = {
    "learning-resources": "📚",
    "communities": "💬",
    "clubs": "🎓",
    "volunteer": "❤️",
    "ctfs": "🔐",
    "competitions": "🏆",
    "hackathons": "💻",
    "game-jams": "🎮",
    "projects": "🧩",
    "repositories": "📦",
    "open-source-help": "🤝",
    "research": "🔬",
    "conferences": "📢",
    "fellowships": "🌟",
    "online-events": "🌐",
    "career-fairs": "💼",
    "scholarships": "💰",
    "startup-programs": "🚀",
    "freelance": "💸",
    "certifications": "🏅",
    "free-benefits": "🎁",
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


def category_anchor(category: str) -> str:
    return category


def category_count(by_category: dict[str, list[dict]], category: str) -> int:
    return len(by_category.get(category, []))


def shield(label: str, message: str, color: str) -> str:
    return f"![{label}](https://img.shields.io/badge/{label}-{message}-{color})"


def generate_readme():
    resources = load_all_resources()
    by_category = defaultdict(list)
    for resource in resources:
        by_category[resource["category"]].append(resource)

    total = len(resources)
    today = str(date.today())
    lines = []
    lines.append('<div align="center">\n\n')
    lines.append("# CS Resource Hub\n\n")
    lines.append(
        "**A curated, community-driven dataset of computer science student "
        "resources.**\n\n"
    )
    lines.append(
        "Structured JSON data, schema validation, automated link checks, and "
        "generated documentation for students, builders, and contributors.\n\n"
    )
    badges = [
        shield("resources", str(total), "2563eb"),
        shield("updated", today, "7c3aed"),
        shield("code_license", "MIT", "16a34a"),
        shield("data_license", "CC_BY_4.0", "0f766e"),
        shield("contributions", "welcome", "f59e0b"),
    ]
    lines.append(" ".join(badges))
    lines.append("\n\n</div>\n\n")
    lines.append("> This README is auto-generated. Do not edit manually.\n")
    lines.append("\n---\n\n")
    lines.append("## Overview\n\n")
    lines.append(
        "CS Resource Hub organizes student-friendly resources into a structured "
        "dataset that can power this README, future websites, search tools, or "
        "other apps.\n\n"
    )
    lines.append("| Area | Categories | Resources |\n")
    lines.append("| --- | ---: | ---: |\n")
    for group, categories in CATEGORY_GROUPS.items():
        group_total = sum(
            category_count(by_category, category) for category in categories
        )
        lines.append(f"| {group} | {len(categories)} | {group_total} |\n")

    lines.append("\n## Table of Contents\n\n")
    for group, categories in CATEGORY_GROUPS.items():
        lines.append(f"### {group}\n\n")
        for category in categories:
            icon = CATEGORY_ICONS[category]
            label = CATEGORY_LABELS[category]
            count = category_count(by_category, category)
            lines.append(
                f"- {icon} [{label}](#{category_anchor(category)}) "
                f"({count} resources)\n"
            )
        lines.append("\n")

    lines.append("---\n")

    for category, label in CATEGORY_LABELS.items():
        cat_resources = sorted(
            by_category.get(category, []), key=lambda x: -x.get("quality", 0)
        )
        lines.append(f'\n<a id="{category_anchor(category)}"></a>\n\n')
        lines.append(f"## {CATEGORY_ICONS[category]} {label}\n\n")
        lines.append(f"**{len(cat_resources)} resources**\n\n")
        if cat_resources:
            lines.append("| Resource | Description | Cost | Region | Tags |\n")
            lines.append("| --- | --- | --- | --- | --- |\n")
            for r in cat_resources:
                name = f"[{r['name']}]({r['url']})"
                desc = r.get("description", "")
                cost = r.get("cost", "")
                region = ", ".join(r.get("region", []))
                tags = ", ".join(r.get("tags", []))
                lines.append(f"| {name} | {desc} | {cost} | {region} | {tags} |\n")
        else:
            lines.append("_No resources yet. Contributions are welcome._\n")

    lines.append("\n---\n\n")
    lines.append("## Contributing\n\n")
    lines.append("Contributions keep this dataset useful and current.\n\n")
    lines.append("1. Read [CONTRIBUTING.md](./CONTRIBUTING.md).\n")
    lines.append("2. Pick the correct category in `data/`.\n")
    lines.append("3. Add one resource using the JSON schema.\n")
    lines.append("4. Run `make validate` and `make check-duplicates`.\n")
    lines.append("5. Open a pull request with a clear description.\n")
    lines.append("\n## License\n\n")
    lines.append("- Code and scripts: [MIT](./LICENSE)\n")
    lines.append("- Dataset/content: [CC BY 4.0](./LICENSE-CC-BY)\n")
    lines.append("\n---\n\n")
    lines.append('<div align="center">\n\n')
    lines.append(
        "Built for CS students who want one reliable place to discover what to "
        "learn, "
    )
    lines.append("join, build, attend, and apply for.\n\n")
    lines.append("</div>\n")

    readme = "".join(lines)
    readme_path = ROOT / "README.md"
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(readme)

    save_json(
        GENERATED_DIR / "README_DATA.json",
        {
            "generated": today,
            "total": total,
            "by_category": {k: len(v) for k, v in by_category.items()},
        },
    )

    log(f"✅ Generated README.md ({total} resources)")

if __name__ == "__main__":
    generate_readme()
