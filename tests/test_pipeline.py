import json
from datetime import date, timedelta

import check_duplicates
import check_links
import check_stale
import generate_combined
import generate_feed
import generate_site_json
import generate_sitemap
import pytest
import utils
import validate_urls_normalized


def test_canonical_url_normalizes_equivalent_urls():
    first = "HTTPS://Example.COM:443/path/?b=2&a=1#section"
    second = "https://example.com/path?a=1&b=2"
    assert check_duplicates.canonical_url(first) == check_duplicates.canonical_url(
        second
    )


def test_duplicate_check_rejects_canonical_url_duplicates(monkeypatch):
    monkeypatch.setattr(
        check_duplicates,
        "load_all_resources",
        lambda: [
            {"id": "one", "name": "One", "url": "https://example.com/path/"},
            {"id": "two", "name": "Two", "url": "https://EXAMPLE.com/path"},
        ],
    )
    with pytest.raises(SystemExit):
        check_duplicates.check_duplicates()


def test_link_retry_requires_consistent_hard_dead_results(monkeypatch):
    monkeypatch.setattr(
        check_links, "check_url_once", lambda _url: ("hard_dead", 404)
    )
    monkeypatch.setattr(check_links.time, "sleep", lambda _seconds: None)
    assert check_links.check_url("https://example.com") == ("hard_dead", 404)


def test_link_retry_downgrades_mixed_results_to_inconclusive(monkeypatch):
    results = iter(
        [("hard_dead", 404), ("inconclusive", 503), ("hard_dead", 404)]
    )
    monkeypatch.setattr(check_links, "check_url_once", lambda _url: next(results))
    monkeypatch.setattr(check_links.time, "sleep", lambda _seconds: None)
    status, detail = check_links.check_url("https://example.com")
    assert status == "inconclusive"
    assert "not consistently dead" in detail


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("not-a-date", None),
        (str(date.today()), 0),
        (str(date.today() - timedelta(days=10)), 10),
        (str(date.today() + timedelta(days=1)), -1),
    ],
)
def test_days_since(value, expected):
    assert check_stale.days_since(value) == expected


def test_stale_check_rejects_future_dates(monkeypatch):
    future = str(date.today() + timedelta(days=1))
    monkeypatch.setattr(
        check_stale,
        "load_all_resources",
        lambda: [{"id": "future", "category": "ctfs", "last_verified": future}],
    )
    with pytest.raises(SystemExit):
        check_stale.check_stale()


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com",
        "https://example.com/",
        "https://example.com/path?utm_source=test",
    ],
)
def test_url_normalization_rejects_invalid_urls(monkeypatch, url):
    monkeypatch.setattr(
        validate_urls_normalized,
        "load_all_resources",
        lambda: [{"id": "invalid", "url": url}],
    )
    with pytest.raises(SystemExit):
        validate_urls_normalized.validate_urls_normalized()


def test_json_helpers_round_trip_and_reject_malformed_json(tmp_path):
    path = tmp_path / "nested" / "data.json"
    utils.save_json(path, {"name": "é"})
    assert utils.load_json(path) == {"name": "é"}
    path.write_text("{", encoding="utf-8")
    with pytest.raises(json.JSONDecodeError):
        utils.load_json(path)


def test_generated_combined_shape(monkeypatch, tmp_path):
    resources = [{"id": "one", "date_added": "2026-01-02"}]
    monkeypatch.setattr(generate_combined, "load_all_resources", lambda: resources)
    monkeypatch.setattr(generate_combined, "GENERATED_DIR", tmp_path)
    generate_combined.generate_combined()
    output = json.loads((tmp_path / "all_resources.json").read_text(encoding="utf-8"))
    assert output == {
        "generated": "2026-01-02",
        "total": 1,
        "resources": resources,
    }


def test_feed_escapes_resource_fields(monkeypatch, tmp_path):
    resource = {
        "id": "one&two",
        "name": "A < B",
        "url": "https://example.com/?a=1&b=2",
        "category": "ctfs",
        "description": 'Use <tags> & "quotes".',
        "date_added": "2026-01-02",
    }
    monkeypatch.setattr(generate_feed, "load_all_resources", lambda: [resource])
    monkeypatch.setattr(generate_feed, "PUBLIC_DIR", tmp_path)
    monkeypatch.setattr(generate_feed, "FEED_FILE", tmp_path / "feed.xml")
    generate_feed.generate_feed()
    feed = (tmp_path / "feed.xml").read_text(encoding="utf-8")
    assert "A &lt; B" in feed
    assert "one&amp;two" in feed
    assert "a=1&amp;b=2" in feed
    assert "&lt;tags&gt; &amp;" in feed


def test_sitemap_and_robots_shape(monkeypatch, tmp_path):
    monkeypatch.setattr(generate_sitemap, "PUBLIC_DIR", tmp_path)
    monkeypatch.setattr(generate_sitemap, "SITEMAP_FILE", tmp_path / "sitemap.xml")
    monkeypatch.setattr(generate_sitemap, "ROBOTS_FILE", tmp_path / "robots.txt")
    monkeypatch.setattr(generate_sitemap, "dataset_updated_date", lambda: "2026-01-02")
    generate_sitemap.generate_sitemap()
    sitemap = (tmp_path / "sitemap.xml").read_text(encoding="utf-8")
    robots = (tmp_path / "robots.txt").read_text(encoding="utf-8")
    assert "<lastmod>2026-01-02</lastmod>" in sitemap
    assert f"Sitemap: {generate_sitemap.SITE_URL}/sitemap.xml" in robots


def test_site_json_rejects_unknown_categories(monkeypatch):
    monkeypatch.setattr(
        generate_site_json,
        "load_all_resources",
        lambda: [{"id": "one", "name": "One", "category": "unknown"}],
    )
    with pytest.raises(SystemExit, match="Unknown categories"):
        generate_site_json.generate_site_json()
