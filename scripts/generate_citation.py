import re

from utils import ROOT, dataset_updated_date, log

CITATION_FILE = ROOT / "CITATION.cff"


def generate_citation() -> None:
    updated = dataset_updated_date()
    text = CITATION_FILE.read_text(encoding="utf-8")

    new_text, count = re.subn(
        r'^date-released: ".*"$',
        f'date-released: "{updated}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count != 1:
        raise SystemExit("❌ CITATION.cff has no date-released field to update")

    if new_text != text:
        CITATION_FILE.write_text(new_text, encoding="utf-8")

    log(f"✅ Generated CITATION.cff (date-released {updated})")


if __name__ == "__main__":
    generate_citation()
