from datetime import datetime, timezone
from xml.sax.saxutils import escape

from utils import (
    CATEGORY_LABELS,
    PUBLIC_DIR,
    SITE_NAME,
    SITE_TAGLINE,
    SITE_URL,
    load_all_resources,
    log,
)

FEED_FILE = PUBLIC_DIR / "feed.xml"
FEED_LIMIT = 40


def rfc_2822(date_added: str) -> str:
    parsed = datetime.strptime(date_added, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    return parsed.strftime("%a, %d %b %Y %H:%M:%S +0000")


def feed_sort_key(resource: dict) -> tuple[str, str]:
    return (resource.get("date_added", ""), resource["name"].lower())


def generate_feed() -> None:
    resources = [r for r in load_all_resources() if r.get("date_added")]
    newest = sorted(resources, key=feed_sort_key, reverse=True)[:FEED_LIMIT]

    items = []
    for resource in newest:
        category = CATEGORY_LABELS.get(resource["category"], resource["category"])
        items += [
            "    <item>",
            f"      <title>{escape(resource['name'])}</title>",
            f"      <link>{escape(resource['url'])}</link>",
            f"      <guid isPermaLink=\"false\">{escape(resource['id'])}</guid>",
            f"      <category>{escape(category)}</category>",
            f"      <description>{escape(resource['description'])}</description>",
            f"      <pubDate>{rfc_2822(resource['date_added'])}</pubDate>",
            "    </item>",
        ]

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "  <channel>",
        f"    <title>{escape(SITE_NAME)}</title>",
        f"    <link>{SITE_URL}/</link>",
        f"    <description>{escape(SITE_TAGLINE)}</description>",
        "    <language>en-ca</language>",
        f'    <atom:link href="{SITE_URL}/feed.xml" rel="self" '
        'type="application/rss+xml" />',
        *items,
        "  </channel>",
        "</rss>",
        "",
    ]

    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    FEED_FILE.write_text("\n".join(lines), encoding="utf-8")
    log(f"✅ Generated feed.xml ({len(newest)} newest resources)")


if __name__ == "__main__":
    generate_feed()
