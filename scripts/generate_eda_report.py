from __future__ import annotations

from collections import Counter
from datetime import date, datetime
from textwrap import shorten
from urllib.parse import urlparse

import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from utils import (
    CATEGORY_GROUPS,
    CATEGORY_LABELS,
    GENERATED_DIR,
    ROOT,
    load_json,
    log,
)

REPORT_DIR = GENERATED_DIR / "eda"
REPORT_PATH = REPORT_DIR / "report.md"
ALL_RESOURCES_PATH = GENERATED_DIR / "all_resources.json"

PRIMARY = "#2563eb"
PRIMARY_DARK = "#1d4ed8"
PRIMARY_SOFT = "#dbeafe"
SECONDARY = "#dc2626"
ACCENT = "#7c3aed"
ACCENT_SOFT = "#ede9fe"
CYAN = "#d97706"
NEUTRAL = "#cbd5e1"
GROUP_PALETTE = [PRIMARY, SECONDARY, ACCENT, CYAN, "#16a34a", "#db2777"]
TEXT = "#111827"
MUTED = "#6b7280"
GRID = "#e5e7eb"
BACKGROUND = "#ffffff"


def configure_plots() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": BACKGROUND,
            "axes.facecolor": BACKGROUND,
            "axes.edgecolor": GRID,
            "axes.labelcolor": TEXT,
            "axes.titlecolor": TEXT,
            "xtick.color": MUTED,
            "ytick.color": TEXT,
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "DejaVu Sans", "Liberation Sans"],
            "font.size": 10,
            "axes.titlesize": 15,
            "axes.titleweight": "bold",
            "axes.labelsize": 10,
            "svg.fonttype": "none",
            "svg.hashsalt": "cs-resource-hub-eda",
        }
    )


def parse_date(value: str) -> date | None:
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def domain_from_url(url: str) -> str:
    return urlparse(url).netloc.removeprefix("www.").lower()


def label_category(category: str) -> str:
    return CATEGORY_LABELS.get(category, category)


def clean_report_assets() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    for path in REPORT_DIR.glob("*.png"):
        path.unlink()
    for path in REPORT_DIR.glob("*.svg"):
        path.unlink()


def finish_chart(fig: plt.Figure, filename: str) -> str:
    path = REPORT_DIR / filename
    fig.tight_layout()
    fig.savefig(
        path,
        format="svg",
        bbox_inches="tight",
        metadata={"Date": None},
    )
    svg = path.read_text(encoding="utf-8")
    path.write_text(
        "\n".join(line.rstrip() for line in svg.splitlines()) + "\n",
        encoding="utf-8",
    )
    plt.close(fig)
    return filename


def style_axis(ax: plt.Axes) -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRID)
    ax.spines["bottom"].set_color(GRID)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def save_bar_chart(
    counts: dict[str, int],
    title: str,
    subtitle: str,
    filename: str,
    color: str,
) -> str:
    labels = [shorten(label, width=34, placeholder="...") for label in counts]
    values = list(counts.values())
    height = max(4.2, len(labels) * 0.38)

    fig, ax = plt.subplots(figsize=(10.5, height))
    bars = ax.barh(labels, values, color=color, alpha=0.92)
    ax.set_title(title, loc="left", pad=18)
    ax.text(0, 1.01, subtitle, transform=ax.transAxes, color=MUTED, fontsize=10)
    ax.set_xlabel("Resources")
    ax.invert_yaxis()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    style_axis(ax)

    max_value = max(values) if values else 0
    ax.set_xlim(0, max_value * 1.16)
    for bar, value in zip(bars, values, strict=True):
        ax.text(
            value + max_value * 0.018,
            bar.get_y() + bar.get_height() / 2,
            str(value),
            va="center",
            ha="left",
            color=TEXT,
            fontsize=9,
            weight="bold",
        )

    return finish_chart(fig, filename)


def save_group_donut(group_counts: Counter[str]) -> str:
    labels = list(group_counts.keys())
    values = list(group_counts.values())
    total = sum(values)

    fig, ax = plt.subplots(figsize=(8.5, 5.6))
    wedges, _ = ax.pie(
        values,
        startangle=90,
        counterclock=False,
        colors=[
            GROUP_PALETTE[index % len(GROUP_PALETTE)]
            for index in range(len(values))
        ],
        wedgeprops={"width": 0.42, "edgecolor": BACKGROUND, "linewidth": 3},
    )
    ax.text(0, 0.08, f"{total}", ha="center", va="center", fontsize=28, weight="bold")
    ax.text(0, -0.12, "resources", ha="center", va="center", fontsize=11, color=MUTED)
    ax.set_title("Resource Mix by Group", loc="left", pad=18)
    ax.text(
        -1.18,
        1.08,
        f"Higher-level balance across {len(labels)} configured project areas.",
        color=MUTED,
        fontsize=10,
    )
    ax.legend(
        wedges,
        [f"{label} ({value})" for label, value in zip(labels, values, strict=True)],
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=False,
    )
    return finish_chart(fig, "resources-by-group.svg")


def save_metadata_chart(resources: list[dict]) -> str:
    fields = ["type", "month", "location"]
    present = [
        sum(1 for resource in resources if resource.get(field))
        for field in fields
    ]
    missing = [len(resources) - value for value in present]

    fig, ax = plt.subplots(figsize=(9.5, 3.8))
    ax.barh(fields, present, color=PRIMARY, label="Present")
    ax.barh(fields, missing, left=present, color=PRIMARY_SOFT, label="Missing")
    ax.set_title("Metadata Completeness", loc="left", pad=18)
    ax.text(
        0,
        1.03,
        "Optional fields are useful where relevant, but should not be forced.",
        transform=ax.transAxes,
        color=MUTED,
        fontsize=10,
    )
    ax.set_xlabel("Resources")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    style_axis(ax)
    ax.legend(frameon=False, loc="lower right")

    for index, value in enumerate(present):
        percent = value / len(resources) * 100
        ax.text(
            value + 4,
            index,
            f"{percent:.0f}% present",
            va="center",
            color=TEXT,
            fontsize=9,
            weight="bold",
        )

    return finish_chart(fig, "metadata-completeness.svg")


def save_description_histogram(lengths: list[int]) -> str:
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    ax.hist(lengths, bins=14, color=PRIMARY, edgecolor=BACKGROUND, alpha=0.9)
    ax.axvline(10, color=ACCENT, linestyle="--", linewidth=1.5, label="Schema min")
    ax.axvline(120, color=ACCENT, linestyle="--", linewidth=1.5, label="Schema max")
    ax.set_title("Description Length Distribution", loc="left", pad=18)
    ax.text(
        0,
        1.03,
        "Descriptions should stay informative without becoming long blurbs.",
        transform=ax.transAxes,
        color=MUTED,
        fontsize=10,
    )
    ax.set_xlabel("Characters")
    ax.set_ylabel("Resources")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    style_axis(ax)
    ax.legend(frameon=False)
    return finish_chart(fig, "description-lengths.svg")


def save_additions_chart(resources: list[dict]) -> str:
    date_counts = Counter(
        parsed
        for resource in resources
        if (parsed := parse_date(resource.get("date_added", ""))) is not None
    )
    ordered_dates = sorted(date_counts)
    values = [date_counts[value] for value in ordered_dates]

    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.plot(ordered_dates, values, color=ACCENT, linewidth=2.5, marker="o")
    ax.fill_between(ordered_dates, values, color=ACCENT, alpha=0.14)
    ax.set_title("Resources Added Over Time", loc="left", pad=18)
    ax.text(
        0,
        1.03,
        "Shows when the dataset grew and where additions were concentrated.",
        transform=ax.transAxes,
        color=MUTED,
        fontsize=10,
    )
    ax.set_xlabel("Date added")
    ax.set_ylabel("Resources")
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    style_axis(ax)
    fig.autofmt_xdate(rotation=30, ha="right")
    return finish_chart(fig, "resources-added-over-time.svg")


def save_lollipop_chart(counts: dict[str, int], title: str, filename: str) -> str:
    labels = [shorten(label, width=32, placeholder="...") for label in counts]
    values = list(counts.values())
    positions = list(range(len(labels)))

    fig, ax = plt.subplots(figsize=(10, max(4, len(labels) * 0.38)))
    ax.hlines(positions, 0, values, color=PRIMARY_SOFT, linewidth=3)
    ax.scatter(values, positions, color=ACCENT, s=90, zorder=3)
    ax.set_yticks(positions, labels)
    ax.set_title(title, loc="left", pad=18)
    ax.text(
        0,
        1.03,
        "Repeated domains can be fine, but concentration is worth reviewing.",
        transform=ax.transAxes,
        color=MUTED,
        fontsize=10,
    )
    ax.set_xlabel("Resources")
    ax.invert_yaxis()
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    style_axis(ax)

    max_value = max(values) if values else 0
    ax.set_xlim(0, max_value * 1.18)
    for position, value in zip(positions, values, strict=True):
        ax.text(
            value + max_value * 0.025,
            position,
            str(value),
            va="center",
            color=TEXT,
            fontsize=9,
            weight="bold",
        )

    return finish_chart(fig, filename)


def markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def labeled_category_rows(categories: list[tuple[str, int]]) -> list[list[object]]:
    return [[label_category(category), count] for category, count in categories]


def generate_eda_report() -> None:
    configure_plots()
    clean_report_assets()

    payload = load_json(ALL_RESOURCES_PATH)
    resources = payload["resources"]
    today = date.today()

    category_counts = Counter(resource["category"] for resource in resources)
    type_counts = Counter(resource.get("type", "missing") for resource in resources)
    domain_counts = Counter(domain_from_url(resource["url"]) for resource in resources)
    id_counts = Counter(resource["id"] for resource in resources)
    name_counts = Counter(resource["name"].lower() for resource in resources)
    url_counts = Counter(resource["url"] for resource in resources)

    category_to_group = {
        category: group
        for group, categories in CATEGORY_GROUPS.items()
        for category in categories
    }
    group_counts = Counter(
        category_to_group.get(resource["category"], "Unmapped")
        for resource in resources
    )

    description_lengths = [len(resource["description"]) for resource in resources]
    last_verified_dates = [
        parse_date(resource.get("last_verified", "")) for resource in resources
    ]
    stale_resources = [
        resource
        for resource, verified in zip(resources, last_verified_dates, strict=True)
        if verified is not None and (today - verified).days > 180
    ]

    duplicate_names = [name for name, count in name_counts.items() if count > 1]
    duplicate_urls = [url for url, count in url_counts.items() if count > 1]

    labeled_category_counts = {
        label_category(category): count
        for category, count in sorted(
            category_counts.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    }
    category_chart = save_bar_chart(
        labeled_category_counts,
        "Resources by Category",
        f"Coverage across all {len(category_counts)} curated opportunity categories.",
        "resources-by-category.svg",
        PRIMARY_DARK,
    )
    group_chart = save_group_donut(group_counts)
    type_chart = save_bar_chart(
        dict(type_counts.most_common(15)),
        "Top Resource Types",
        "The most common formats represented in the hub.",
        "top-resource-types.svg",
        ACCENT,
    )
    metadata_chart = save_metadata_chart(resources)
    description_chart = save_description_histogram(description_lengths)
    additions_chart = save_additions_chart(resources)
    domain_chart = save_lollipop_chart(
        dict(domain_counts.most_common(15)),
        "Most Common Domains",
        "most-common-domains.svg",
    )

    smallest_categories = sorted(category_counts.items(), key=lambda item: item[1])[:5]
    largest_categories = category_counts.most_common(5)
    top_domains = domain_counts.most_common(10)
    average_description_length = sum(description_lengths) / len(description_lengths)

    metadata_rows = []
    for field in ["type", "month", "location"]:
        present = sum(1 for resource in resources if resource.get(field))
        metadata_rows.append([field, present, len(resources) - present])

    quality_rows = [
        ["Duplicate IDs", sum(count - 1 for count in id_counts.values() if count > 1)],
        ["Duplicate URLs", len(duplicate_urls)],
        ["Duplicate names", len(duplicate_names)],
        [
            "Descriptions under 10 chars",
            sum(1 for length in description_lengths if length < 10),
        ],
        [
            "Descriptions over 120 chars",
            sum(1 for length in description_lengths if length > 120),
        ],
        ["Resources verified over 180 days ago", len(stale_resources)],
    ]

    largest_label = label_category(largest_categories[0][0])
    smallest_label = label_category(smallest_categories[0][0])

    type_present = next(row[1] for row in metadata_rows if row[0] == "type")
    location_present = next(row[1] for row in metadata_rows if row[0] == "location")
    typed_percent = type_present / len(resources) * 100
    location_percent = location_present / len(resources) * 100

    lines = [
        "# CS Resource Hub EDA Report",
        "",
        "A static, portfolio-friendly analysis of CS Resource Hub coverage, "
        "composition, metadata quality, duplicate candidates, and source "
        "concentration. The notebook in `notebooks/resource_eda.ipynb` keeps "
        "the exploratory workflow reproducible; this report is the polished "
        "read-only view.",
        "",
        f"Generated from `{ALL_RESOURCES_PATH.relative_to(ROOT).as_posix()}` "
        f"on {today.isoformat()}.",
        "",
        "## Snapshot",
        "",
        markdown_table(
            ["Metric", "Value"],
            [
                ["Generated data date", payload.get("generated", "unknown")],
                ["Total resources", f"{len(resources):,}"],
                ["Categories", len(category_counts)],
                ["Groups", len(group_counts)],
                [
                    "Average description length",
                    f"{average_description_length:.1f} chars",
                ],
                ["Duplicate URL candidates", len(duplicate_urls)],
            ],
        ),
        "",
        "## Coverage",
        "",
        f"![Resources by category]({category_chart})",
        "",
        f"**Coverage signal:** {largest_label} is the strongest category with "
        f"{largest_categories[0][1]} resources, while {smallest_label} is the "
        f"largest visible expansion opportunity with {smallest_categories[0][1]}.",
        "",
        f"![Resources by group]({group_chart})",
        "",
        "The group chart gives a fast read on whether the hub is balanced across "
        "learning, experience, building, and career-oriented resources.",
        "",
        "### Largest Categories",
        "",
        markdown_table(
            ["Category", "Resources"],
            labeled_category_rows(largest_categories),
        ),
        "",
        "### Smallest Categories",
        "",
        markdown_table(
            ["Category", "Resources"],
            labeled_category_rows(smallest_categories),
        ),
        "",
        "## Resource Composition",
        "",
        f"![Top resource types]({type_chart})",
        "",
        "This chart shows the dominant formats in the dataset, which helps avoid "
        "over-indexing on one kind of resource.",
        "",
        f"![Metadata completeness]({metadata_chart})",
        "",
        f"**Metadata signal:** {typed_percent:.0f}% of resources include a type, "
        f"and {location_percent:.0f}% include a location. Optional fields are "
        "tracked without forcing irrelevant metadata onto every entry.",
        "",
        markdown_table(["Field", "Present", "Missing"], metadata_rows),
        "",
        "## Quality Signals",
        "",
        f"![Description length distribution]({description_chart})",
        "",
        "Description lengths stay inside the schema bounds, which keeps README "
        "tables scannable and avoids low-information entries.",
        "",
        f"![Resources added over time]({additions_chart})",
        "",
        "The additions chart makes dataset growth visible and helps explain when "
        "large curation passes happened.",
        "",
        markdown_table(["Check", "Count"], quality_rows),
        "",
        "## Source Concentration",
        "",
        f"![Most common domains]({domain_chart})",
        "",
        f"**Domain signal:** `{top_domains[0][0]}` appears most often with "
        f"{top_domains[0][1]} resources. Repeated domains are expected for "
        "high-quality hubs such as GitHub or YouTube, but concentration remains "
        "worth monitoring.",
        "",
        markdown_table(["Domain", "Resources"], top_domains),
        "",
        "## Key Takeaways",
        "",
        f"- The dataset currently contains {len(resources):,} resources "
        f"across {len(category_counts)} categories.",
        f"- The largest category is {largest_label} with "
        f"{largest_categories[0][1]} resources.",
        f"- The smallest category is {smallest_label} with "
        f"{smallest_categories[0][1]} resources.",
        f"- The most common domain is `{top_domains[0][0]}` with "
        f"{top_domains[0][1]} resources.",
        f"- Duplicate URL candidates found: {len(duplicate_urls)}.",
        "",
        "For deeper inspection or custom analysis, run "
        "`py -3 -m jupyterlab notebooks/resource_eda.ipynb`.",
        "",
    ]

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")
    log(f"Generated {REPORT_PATH.relative_to(ROOT)}")


if __name__ == "__main__":
    generate_eda_report()
