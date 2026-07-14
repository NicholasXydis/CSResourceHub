import json
from datetime import date, timedelta

import check_duplicates
import check_links
import check_stale
import fetch_logos
import generate_combined
import generate_feed
import generate_site_json
import generate_sitemap
import net_safety
import pytest
import utils
import validate_urls_normalized
from PIL import Image


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


def test_site_url_is_identical_in_python_and_vite():
    vite_config = (utils.ROOT / "vite.config.ts").read_text(encoding="utf-8")
    playwright_config = (utils.ROOT / "playwright.production.config.ts").read_text(
        encoding="utf-8"
    )
    assert f'const SITE_URL = "{utils.SITE_URL}";' in vite_config
    assert f'"{utils.SITE_URL}"' in playwright_config


def test_curated_fallback_matches_domain_and_subdomains():
    assert fetch_logos.prefers_fallback("defcon.org")
    assert fetch_logos.prefers_fallback("blitz.codes")
    assert fetch_logos.prefers_fallback("2026.blitz.codes")
    assert fetch_logos.prefers_fallback("2027.blitz.codes")


def test_curated_fallback_ignores_unrelated_domains():
    assert not fetch_logos.prefers_fallback("leetcode.com")
    assert not fetch_logos.prefers_fallback("notdefcon.org")
    assert not fetch_logos.prefers_fallback("defcon.org.evil.com")


def test_curated_domains_are_never_fetched(monkeypatch, tmp_path):
    monkeypatch.setattr(
        fetch_logos,
        "load_all_resources",
        lambda: [
            {"url": "https://defcon.org"},
            {"url": "https://2026.blitz.codes"},
            {"url": "https://example.com"},
        ],
    )
    monkeypatch.setattr(fetch_logos, "LOGO_DIR", tmp_path)

    fetched = []

    def fake_best_logo(url):
        fetched.append(url)
        return Image.new("RGBA", (128, 128))

    monkeypatch.setattr(fetch_logos, "best_logo", fake_best_logo)

    saved = {}
    monkeypatch.setattr(
        fetch_logos, "save_json", lambda _path, data: saved.update(data)
    )
    monkeypatch.setattr(fetch_logos, "log", lambda _message: None)

    fetch_logos.fetch_logos()

    assert fetched == ["https://example.com"]
    assert saved["stored"] == ["example.com"]
    assert saved["checked"] == 3


def test_a_network_outage_does_not_wipe_the_stored_logos(monkeypatch, tmp_path):
    monkeypatch.setattr(
        fetch_logos,
        "load_all_resources",
        lambda: [{"url": f"https://site{n}.com"} for n in range(10)],
    )
    monkeypatch.setattr(fetch_logos, "LOGO_DIR", tmp_path)
    monkeypatch.setattr(fetch_logos, "best_logo", lambda _url: None)

    saved = {}
    monkeypatch.setattr(
        fetch_logos, "save_json", lambda _path, data: saved.update(data)
    )
    monkeypatch.setattr(fetch_logos, "log", lambda _message: None)

    with pytest.raises(SystemExit):
        fetch_logos.fetch_logos()

    assert saved == {}


def test_stored_logos_are_written_for_fetchable_domains(monkeypatch, tmp_path):
    monkeypatch.setattr(
        fetch_logos,
        "load_all_resources",
        lambda: [{"url": "https://example.com"}, {"url": "https://other.com"}],
    )
    monkeypatch.setattr(fetch_logos, "LOGO_DIR", tmp_path)
    monkeypatch.setattr(
        fetch_logos, "best_logo", lambda _url: Image.new("RGBA", (128, 128))
    )

    saved = {}
    monkeypatch.setattr(
        fetch_logos, "save_json", lambda _path, data: saved.update(data)
    )
    monkeypatch.setattr(fetch_logos, "log", lambda _message: None)

    fetch_logos.fetch_logos()

    assert saved["stored"] == ["example.com", "other.com"]
    written = sorted(p.name for p in tmp_path.glob("*.png"))
    assert written == ["example.com.png", "other.com.png"]

    with Image.open(tmp_path / "example.com.png") as image:
        assert image.size == (fetch_logos.LOGO_SIZE, fetch_logos.LOGO_SIZE)


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


def test_schema_rejects_impossible_calendar_dates():
    import jsonschema

    schema = utils.load_json(utils.SCHEMA_FILE)
    validator = jsonschema.Draft7Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    resource = {
        "id": "one",
        "name": "One",
        "url": "https://example.com",
        "description": "A description that is long enough to satisfy the schema.",
        "category": "ctfs",
        "type": "event",
        "location": "Online",
        "date_added": "2026-01-02",
        "last_verified": "2026-02-30",
    }
    messages = [error.message for error in validator.iter_errors(resource)]
    assert any("2026-02-30" in message for message in messages)

    resource["last_verified"] = "2026-02-28"
    assert not list(validator.iter_errors(resource))


class FakeResponse:
    def __init__(self, status_code=200, headers=None, chunks=(b"ok",)):
        self.status_code = status_code
        self.headers = headers or {}
        self._chunks = chunks
        self.closed = False

    def iter_content(self, _size):
        yield from self._chunks

    def close(self):
        self.closed = True


class FakeSession:
    def __init__(self, responses):
        self._responses = list(responses)
        self.urls = []

    def request(self, _method, url, **_kwargs):
        self.urls.append(url)
        return self._responses.pop(0)


def resolve_to(monkeypatch, mapping):
    def fake_getaddrinfo(host, port, **_kwargs):
        if host not in mapping:
            raise net_safety.socket.gaierror(host)
        return [(None, None, None, "", (mapping[host], port))]

    monkeypatch.setattr(net_safety.socket, "getaddrinfo", fake_getaddrinfo)


@pytest.mark.parametrize(
    "url",
    [
        "https://127.0.0.1",
        "https://[::1]",
        "https://10.0.0.5",
        "https://169.254.169.254",
        "https://192.168.1.1",
    ],
)
def test_assert_safe_url_rejects_non_public_addresses(url):
    with pytest.raises(net_safety.UnsafeUrl):
        net_safety.assert_safe_url(url)


def test_assert_safe_url_rejects_plain_http(monkeypatch):
    resolve_to(monkeypatch, {"example.com": "93.184.216.34"})
    with pytest.raises(net_safety.UnsafeUrl, match="non-https"):
        net_safety.assert_safe_url("http://example.com")


def test_assert_safe_url_allows_a_public_host(monkeypatch):
    resolve_to(monkeypatch, {"example.com": "93.184.216.34"})
    net_safety.assert_safe_url("https://example.com")


def test_safe_request_blocks_a_redirect_into_a_private_address(monkeypatch):
    resolve_to(
        monkeypatch, {"example.com": "93.184.216.34", "internal.test": "10.0.0.5"}
    )
    session = FakeSession(
        [FakeResponse(302, {"Location": "https://internal.test/admin"})]
    )
    with pytest.raises(net_safety.UnsafeUrl, match="non-public"):
        with net_safety.safe_request(session, "GET", "https://example.com", 5):
            pass


def test_safe_request_follows_a_public_redirect(monkeypatch):
    resolve_to(monkeypatch, {"a.test": "93.184.216.34", "b.test": "93.184.216.35"})
    session = FakeSession(
        [FakeResponse(301, {"Location": "https://b.test/final"}), FakeResponse(200)]
    )
    with net_safety.safe_request(session, "GET", "https://a.test", 5) as response:
        assert response.status_code == 200
    assert session.urls == ["https://a.test", "https://b.test/final"]


def test_safe_request_detects_a_redirect_loop(monkeypatch):
    resolve_to(monkeypatch, {"a.test": "93.184.216.34"})
    session = FakeSession(
        [
            FakeResponse(302, {"Location": "https://a.test/"}),
            FakeResponse(302, {"Location": "https://a.test/"}),
        ]
    )
    with pytest.raises(net_safety.UnsafeUrl, match="redirect loop"):
        with net_safety.safe_request(session, "GET", "https://a.test/", 5):
            pass


def test_safe_request_caps_the_redirect_chain(monkeypatch):
    resolve_to(monkeypatch, {"a.test": "93.184.216.34"})
    session = FakeSession(
        [
            FakeResponse(302, {"Location": f"https://a.test/{index}"})
            for index in range(net_safety.MAX_REDIRECTS + 1)
        ]
    )
    with pytest.raises(net_safety.UnsafeUrl, match="more than"):
        with net_safety.safe_request(session, "GET", "https://a.test/start", 5):
            pass


def test_read_capped_rejects_an_oversized_body():
    response = FakeResponse(chunks=(b"x" * 4096,) * 8)
    with pytest.raises(net_safety.UnsafeUrl, match="exceeded"):
        net_safety.read_capped(response, max_bytes=1024)


def test_read_capped_returns_a_small_body():
    assert net_safety.read_capped(FakeResponse(chunks=(b"ab", b"cd"))) == b"abcd"


def test_check_links_reports_unsafe_without_marking_dead(monkeypatch):
    monkeypatch.setattr(
        check_links,
        "request_url",
        lambda *_args: (_ for _ in ()).throw(
            net_safety.UnsafeUrl("resolves to non-public address 10.0.0.5")
        ),
    )
    status, detail = check_links.check_url("https://internal.test")
    assert status == "unsafe"
    assert "non-public" in detail


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com:99999",
        "https://example.com:abc",
        "https://example.com:-1",
        "https://[oops",
    ],
)
def test_assert_safe_url_rejects_malformed_urls_without_crashing(url):
    with pytest.raises(net_safety.UnsafeUrl):
        net_safety.assert_safe_url(url)


def test_check_links_classifies_a_malformed_url_as_unsafe(monkeypatch):
    monkeypatch.setattr(check_links.time, "sleep", lambda _seconds: None)
    status, detail = check_links.check_url("https://example.com:99999")
    assert status == "unsafe"
    assert "malformed" in detail


@pytest.mark.parametrize(
    "hostname",
    ["a" * 64 + ".example.com", "xn--" + "a" * 70 + ".example.com"],
)
def test_assert_safe_url_survives_hostnames_the_resolver_rejects(hostname):
    with pytest.raises(net_safety.UnsafeUrl):
        net_safety.assert_safe_url(f"https://{hostname}")
