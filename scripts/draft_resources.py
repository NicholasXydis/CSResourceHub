import argparse
import random
import re
import sys
import time
from datetime import date
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import requests
from jsonschema import Draft7Validator
from sort_resources import sort_resources
from utils import (
    CATEGORY_GROUPS,
    GENERATED_DIR,
    ROOT,
    SCHEMA_FILE,
    get_all_resource_files,
    load_all_resources,
    load_json,
    log,
    save_json,
)
from validate_all import validate_all

DRAFTS_FILE = GENERATED_DIR / "import_drafts.json"
FAILURES_FILE = GENERATED_DIR / "import_failures.json"
DEFAULT_LINKS_FILE = ROOT / "imports" / "links.txt"
USER_AGENT = "CSResourceHubDraftBot/1.0 (+https://github.com/NicholasXydis/CSResourceHub)"
TIMEOUT = 10
MAX_REDIRECTS = 5
BOT_HOSTILE_DOMAINS = {
    "facebook.com",
    "instagram.com",
    "linkedin.com",
    "twitter.com",
    "x.com",
}
TRACKING_PREFIXES = ("utm_",)
TRACKING_PARAMS = {"fbclid", "gclid", "mc_cid", "mc_eid", "ref"}
EDITABLE_FIELDS = [
    "name",
    "description",
    "category",
    "month",
    "cost",
    "location",
]

CATEGORY_KEYWORDS = {
    "learning-resources": [
        "course",
        "learn",
        "tutorial",
        "book",
        "lesson",
        "education",
        "curriculum",
    ],
    "communities": ["community", "discord", "forum", "slack", "group"],
    "clubs": ["club", "student organization", "chapter"],
    "hackathons": ["hackathon", "hackathons", "mlh"],
    "ctfs": ["ctf", "capture the flag", "cybersecurity challenge"],
    "game-jams": ["game jam", "gamejam", "game development jam"],
    "competitions": ["competition", "contest", "competitive programming"],
    "volunteer": ["volunteer", "non-profit", "nonprofit", "charity"],
    "projects": ["project idea", "portfolio project", "build project"],
    "repositories": ["github", "repository", "repo", "codebase"],
    "open-source-help": ["open source", "contribution", "contribute"],
    "fellowships": ["fellowship", "student program", "internship program"],
    "research": ["research", "lab", "paper", "undergraduate research"],
    "conferences": ["conference", "symposium", "summit"],
    "career-fairs": ["career fair", "recruiting", "employer"],
    "online-events": ["webinar", "online event", "virtual event", "meetup"],
    "scholarships": ["scholarship", "grant", "bursary", "financial aid"],
    "startup-programs": ["startup", "incubator", "accelerator", "founder"],
    "freelance": ["freelance", "client", "gig"],
    "certifications": ["certification", "certificate", "exam"],
    "free-benefits": ["benefit", "perk", "student pack", "free tools"],
}

class MetadataParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_title = False
        self.title_parts = []
        self.meta = {}
        self.lang = ""

    def handle_starttag(self, tag, attrs):
        attr_map = {key.lower(): value for key, value in attrs if value is not None}
        if tag.lower() == "html":
            self.lang = attr_map.get("lang", "")
        if tag.lower() == "title":
            self.in_title = True
        if tag.lower() == "meta":
            key = (
                attr_map.get("property")
                or attr_map.get("name")
                or attr_map.get("http-equiv")
            )
            content = attr_map.get("content")
            if key and content:
                self.meta[key.lower()] = content

    def handle_endtag(self, tag):
        if tag.lower() == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title_parts.append(data)

    @property
    def title(self):
        return clean_text(" ".join(self.title_parts))


def clean_text(value):
    return re.sub(r"\s+", " ", unescape(value or "")).strip()


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "resource"


def normalize_url(raw_url):
    raw_url = raw_url.strip()
    if not raw_url:
        return ""
    if "://" not in raw_url:
        raw_url = "https://" + raw_url
    parsed = urlparse(raw_url)
    scheme = "https"
    netloc = parsed.netloc.lower()
    path = parsed.path.rstrip("/") or ""
    query_items = []
    for key, value in parse_qsl(parsed.query, keep_blank_values=True):
        lower_key = key.lower()
        if lower_key in TRACKING_PARAMS or lower_key.startswith(TRACKING_PREFIXES):
            continue
        query_items.append((key, value))
    query = urlencode(query_items)
    return urlunparse((scheme, netloc, path, "", query, ""))


def comparable_url(url):
    parsed = urlparse(normalize_url(url))
    netloc = parsed.netloc.removeprefix("www.")
    return urlunparse((parsed.scheme, netloc, parsed.path, "", parsed.query, ""))


def domain_for(url):
    return urlparse(url).netloc.lower().removeprefix("www.")


def is_bot_hostile(url):
    domain = domain_for(url)
    return any(
        domain == blocked or domain.endswith("." + blocked)
        for blocked in BOT_HOSTILE_DOMAINS
    )


def load_json_file(path, default):
    if not path.exists():
        return default
    return load_json(path)


def save_json_file(path, data):
    save_json(path, data)


def existing_url_set():
    return {comparable_url(resource["url"]) for resource in load_all_resources()}


def existing_id_set():
    return {resource["id"] for resource in load_all_resources()}


def draft_url_set(drafts):
    return {
        comparable_url(draft.get("normalized_url") or draft["resource"]["url"])
        for draft in drafts
        if draft.get("resource", {}).get("url")
    }


def draft_id_set(drafts):
    return {
        draft["resource"]["id"]
        for draft in drafts
        if draft.get("resource", {}).get("id")
    }


def find_category_file(category):
    for path in get_all_resource_files():
        if path.stem == category:
            return path
    return None


def category_choices():
    return [
        category
        for categories in CATEGORY_GROUPS.values()
        for category in categories
    ]


def read_links(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing links file: {path}")
    links = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if cleaned and not cleaned.startswith("#"):
            links.append(cleaned)
    return links


def fetch_metadata(url, session, cache):
    if url in cache:
        return cache[url]
    if is_bot_hostile(url):
        result = {
            "ok": False,
            "reason": "skipped: bot-hostile domain",
            "url": url,
        }
        cache[url] = result
        return result

    try:
        response = session.get(url, timeout=TIMEOUT, allow_redirects=True)
    except requests.RequestException as exc:
        result = {"ok": False, "reason": f"fetch failed: {exc}", "url": url}
        cache[url] = result
        return result

    content_type = response.headers.get("content-type", "").lower()
    if response.status_code >= 400:
        result = {
            "ok": False,
            "reason": f"http {response.status_code}",
            "url": url,
        }
    elif "text/html" not in content_type:
        result = {
            "ok": False,
            "reason": f"non-html content-type: {content_type or 'unknown'}",
            "url": url,
        }
    else:
        parser = MetadataParser()
        parser.feed(response.text[:200000])
        result = {
            "ok": True,
            "url": normalize_url(response.url),
            "title": best_title(parser, url),
            "description": best_description(parser),
            "lang": clean_text(parser.lang).lower(),
            "content_type": content_type,
        }
    cache[url] = result
    return result


def best_title(parser, url):
    title = (
        clean_text(parser.meta.get("og:title"))
        or clean_text(parser.meta.get("twitter:title"))
        or parser.title
    )
    if not title:
        title = slugify(Path(urlparse(url).path).stem or domain_for(url)).replace(
            "-",
            " ",
        )
    return strip_title_suffix(title)


def strip_title_suffix(title):
    for separator in [" | ", " - ", " – ", " — "]:
        if separator in title:
            first = title.split(separator)[0].strip()
            if len(first) >= 3:
                return first
    return title


def best_description(parser):
    return (
        clean_text(parser.meta.get("og:description"))
        or clean_text(parser.meta.get("twitter:description"))
        or clean_text(parser.meta.get("description"))
    )


def draft_warnings(name, description):
    warnings = []
    lower_desc = description.lower()
    if len(name) <= 2:
        warnings.append("name is very short")
    if not description:
        warnings.append("missing description")
    elif len(description) < 25:
        warnings.append("description is short")
    elif len(description) > 120:
        warnings.append("description is longer than schema limit")
    bad_phrases = [
        "cookie",
        "javascript required",
        "enable javascript",
        "enable cookies",
        "403",
        "access denied",
        "forbidden",
        "welcome to",
    ]
    if any(phrase in lower_desc for phrase in bad_phrases):
        warnings.append("description may be boilerplate")
    warnings.append("verify location and optional cost")
    return warnings


def guess_category(text):
    lower_text = text.lower()
    scores = {}
    for category, keywords in CATEGORY_KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in lower_text)
        if score:
            scores[category] = score
    if not scores:
        return "learning-resources", 0.2, ["communities", "projects"]
    ordered = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    best_category, best_score = ordered[0]
    alternatives = [category for category, _ in ordered[1:4]]
    if len(alternatives) < 2:
        alternatives.extend(
            category
            for category in category_choices()
            if category != best_category and category not in alternatives
        )
    confidence = min(0.95, 0.35 + best_score * 0.15)
    return best_category, confidence, alternatives[:3]


def build_draft(raw_url, metadata, existing_ids, current_draft_ids):
    normalized_url = metadata.get("url") or normalize_url(raw_url)
    name = clean_text(metadata.get("title"))[:100] or domain_for(normalized_url)
    description = clean_text(metadata.get("description"))
    text = " ".join([name, description, normalized_url])
    category, confidence, alternatives = guess_category(text)
    resource_id = slugify(name)
    warnings = draft_warnings(name, description)
    has_id_collision = resource_id in existing_ids or resource_id in current_draft_ids
    if has_id_collision:
        warnings.append(f"id collision: {resource_id}")
    resource = {
        "id": resource_id,
        "name": name,
        "url": normalized_url,
        "description": description[:120],
        "category": category,
        "status": "active",
        "location": "Online",
        "date_added": str(date.today()),
        "last_verified": str(date.today()),
    }
    return {
        "status": "needs_edit" if has_id_collision else "pending",
        "approved": False,
        "confidence": round(confidence, 2),
        "category_guess": category,
        "category_alternatives": alternatives,
        "warnings": warnings,
        "original_url": raw_url,
        "normalized_url": normalized_url,
        "resource": resource,
    }


def failure_entry(raw_url, normalized_url, reason):
    return {
        "url": raw_url,
        "normalized_url": normalized_url,
        "reason": reason,
        "date": str(date.today()),
    }


def draft_links(links, limit=None, retry_failures=False):
    if limit is not None:
        links = links[:limit]
    if not links:
        log("No links to draft.")
        return

    GENERATED_DIR.mkdir(parents=True, exist_ok=True)
    drafts = load_json_file(DRAFTS_FILE, [])
    failures = [] if retry_failures else load_json_file(FAILURES_FILE, [])
    existing_urls = existing_url_set()
    existing_ids = existing_id_set()
    known_draft_urls = draft_url_set(drafts)
    known_draft_ids = draft_id_set(drafts)
    seen_batch = set()
    fetch_cache = {}
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    session.max_redirects = MAX_REDIRECTS
    summary = {"drafted": 0, "duplicates": [], "failed": []}

    for raw_url in links:
        normalized = normalize_url(raw_url)
        comparable = comparable_url(normalized)
        if not normalized:
            continue
        if comparable in existing_urls:
            summary["duplicates"].append(normalized)
            continue
        if comparable in known_draft_urls or comparable in seen_batch:
            summary["duplicates"].append(normalized)
            continue
        seen_batch.add(comparable)
        metadata = fetch_metadata(normalized, session, fetch_cache)
        time.sleep(random.uniform(1, 3))
        if not metadata["ok"]:
            failure = failure_entry(raw_url, normalized, metadata["reason"])
            failures.append(failure)
            summary["failed"].append(normalized)
            continue
        draft = build_draft(raw_url, metadata, existing_ids, known_draft_ids)
        drafts.append(draft)
        known_draft_urls.add(comparable_url(draft["normalized_url"]))
        known_draft_ids.add(draft["resource"]["id"])
        summary["drafted"] += 1

    save_json_file(DRAFTS_FILE, drafts)
    save_json_file(FAILURES_FILE, failures)
    log(
        "Draft summary: "
        f"{summary['drafted']} drafted, "
        f"{len(summary['duplicates'])} duplicate(s), "
        f"{len(summary['failed'])} failed."
    )
    if summary["duplicates"]:
        log("Skipped duplicates:")
        for url in summary["duplicates"]:
            log(f"  - {url}")
    if summary["failed"]:
        log(f"Failures written to {FAILURES_FILE}")


def retry_failures(limit=None):
    failures = load_json_file(FAILURES_FILE, [])
    if not failures:
        log("No failures to retry.")
        return
    links = [failure["url"] for failure in failures]
    draft_links(links, limit=limit, retry_failures=True)


def print_draft(draft, index, total):
    resource = draft["resource"]
    log(f"\n[{index + 1}/{total}] {resource['name']}")
    log(f"URL: {resource['url']}")
    log(f"Description: {resource.get('description', '')}")
    log(
        f"Category: {resource['category']} "
        f"({draft.get('confidence', 0):.0%})"
    )
    log(f"Alternatives: {', '.join(draft.get('category_alternatives', []))}")
    if draft.get("warnings"):
        log("Warnings:")
        for warning in draft["warnings"]:
            log(f"  - {warning}")


def parse_list(value):
    return [item.strip() for item in value.split(",") if item.strip()]


def edit_resource(resource):
    log("Editable fields: " + ", ".join(EDITABLE_FIELDS))
    while True:
        field = input("Field to edit (Enter to finish): ").strip()
        if not field:
            return
        if field not in EDITABLE_FIELDS:
            log("Not editable.")
            continue
        current = resource.get(field, "")
        log(f"Current {field}: {current}")
        value = input("New value: ").strip()
        if value:
            resource[field] = value


def review_drafts():
    drafts = load_json_file(DRAFTS_FILE, [])
    if not drafts:
        log("No drafts found. Run make draft first.")
        return
    index = 0
    history = []
    while index < len(drafts):
        draft = drafts[index]
        if draft.get("status") in {"approved", "rejected"}:
            index += 1
            continue
        print_draft(draft, index, len(drafts))
        choice = input("Approve? [y/n/e/u/q]: ").strip().lower()
        if choice == "y":
            draft["status"] = "approved"
            draft["approved"] = True
            history.append(index)
            index += 1
        elif choice == "n":
            draft["status"] = "rejected"
            draft["approved"] = False
            history.append(index)
            index += 1
        elif choice == "e":
            edit_resource(draft["resource"])
            draft["status"] = "needs_edit"
            draft["approved"] = False
            history.append(index)
            index += 1
        elif choice == "u":
            if not history:
                log("Nothing to undo.")
                continue
            previous = history.pop()
            drafts[previous]["status"] = "pending"
            drafts[previous]["approved"] = False
            index = previous
        elif choice == "q":
            break
        else:
            log("Choose y, n, e, u, or q.")
            continue
        save_json_file(DRAFTS_FILE, drafts)
    save_json_file(DRAFTS_FILE, drafts)
    log("Review saved.")


def validate_resource_for_import(resource, existing_urls, existing_ids, validator):
    errors = []
    if comparable_url(resource["url"]) in existing_urls:
        errors.append("duplicate URL")
    if resource["id"] in existing_ids:
        errors.append("duplicate id")
    if resource["category"] not in category_choices():
        errors.append("unknown category")
    if not find_category_file(resource["category"]):
        errors.append("missing category data file")
    errors.extend(error.message for error in validator.iter_errors(resource))
    return errors


def import_approved(dry_run=False):
    drafts = load_json_file(DRAFTS_FILE, [])
    approved = [draft for draft in drafts if draft.get("status") == "approved"]
    if not approved:
        log("No approved drafts to import.")
        return

    existing_urls = existing_url_set()
    existing_ids = existing_id_set()
    validator = Draft7Validator(load_json(SCHEMA_FILE))
    added = []
    skipped = []
    touched = set()
    for draft in approved:
        resource = draft["resource"]
        errors = validate_resource_for_import(
            resource,
            existing_urls,
            existing_ids,
            validator,
        )
        if errors:
            skipped.append((resource["name"], ", ".join(errors)))
            continue
        category_file = find_category_file(resource["category"])
        added.append((category_file, resource))
        existing_urls.add(comparable_url(resource["url"]))
        existing_ids.add(resource["id"])
        touched.add(resource["category"])

    if dry_run:
        log(f"Dry run: {len(added)} resource(s) would be added.")
        for _, resource in added:
            log(f"  - {resource['name']} -> {resource['category']}")
        if skipped:
            log(f"{len(skipped)} resource(s) would be skipped:")
            for name, reason in skipped:
                log(f"  - {name}: {reason}")
        return

    for category_file, resource in added:
        data = load_json(category_file)
        data.setdefault("resources", []).append(resource)
        save_json(category_file, data)

    sort_resources()
    validate_all()
    log(
        "Import summary: "
        f"{len(added)} added, {len(skipped)} skipped, 0 failed, "
        f"{len(touched)} categor(ies) touched."
    )
    log("Validation result: passed.")
    if touched:
        log("Touched categories: " + ", ".join(sorted(touched)))
    if skipped:
        log("Skipped:")
        for name, reason in skipped:
            log(f"  - {name}: {reason}")


def clean_drafts(force=False):
    drafts = load_json_file(DRAFTS_FILE, [])
    active = [
        draft
        for draft in drafts
        if draft.get("status") in {"pending", "approved", "needs_edit"}
    ]
    if active and not force:
        answer = input(
            f"{len(active)} active draft(s) will be deleted. Continue? [y/N]: "
        ).strip().lower()
        if answer != "y":
            log("Clean cancelled.")
            return
    for path in [DRAFTS_FILE, FAILURES_FILE]:
        if path.exists():
            path.unlink()
            log(f"Deleted {path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Draft and import resource links.")
    parser.add_argument("links_file", nargs="?", type=Path)
    parser.add_argument("--url", help="Draft one URL and append it to drafts.")
    parser.add_argument("--limit", type=int, help="Draft only the first N links.")
    parser.add_argument("--retry-failures", action="store_true")
    parser.add_argument("--review", action="store_true")
    parser.add_argument("--import-approved", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--clean-drafts", action="store_true")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.review:
        review_drafts()
    elif args.import_approved:
        import_approved(dry_run=args.dry_run)
    elif args.clean_drafts:
        clean_drafts(force=args.force)
    elif args.retry_failures:
        retry_failures(limit=args.limit)
    elif args.url:
        draft_links([args.url], limit=args.limit)
    else:
        links_file = args.links_file or DEFAULT_LINKS_FILE
        try:
            links = read_links(links_file)
        except FileNotFoundError as exc:
            log(str(exc))
            log("Create imports/links.txt or pass a links file path.")
            sys.exit(1)
        if not links:
            log(f"No links found in {links_file}.")
            return
        draft_links(links, limit=args.limit)


if __name__ == "__main__":
    main()
