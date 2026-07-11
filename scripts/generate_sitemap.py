from utils import (
    PUBLIC_DIR,
    SITE_URL,
    dataset_updated_date,
    log,
)

SITEMAP_FILE = PUBLIC_DIR / "sitemap.xml"
ROBOTS_FILE = PUBLIC_DIR / "robots.txt"


def generate_sitemap() -> None:
    updated = dataset_updated_date()

    sitemap = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        "  <url>",
        f"    <loc>{SITE_URL}/</loc>",
        f"    <lastmod>{updated}</lastmod>",
        "    <changefreq>weekly</changefreq>",
        "    <priority>1.0</priority>",
        "  </url>",
        "</urlset>",
        "",
    ]
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    SITEMAP_FILE.write_text("\n".join(sitemap), encoding="utf-8")

    robots = [
        "User-agent: *",
        "Allow: /",
        "",
        f"Sitemap: {SITE_URL}/sitemap.xml",
        "",
    ]
    ROBOTS_FILE.write_text("\n".join(robots), encoding="utf-8")

    log("✅ Generated sitemap.xml and robots.txt")


if __name__ == "__main__":
    generate_sitemap()
