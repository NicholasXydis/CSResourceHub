import sys
from datetime import date, datetime

from utils import load_all_resources, log

STALE_AFTER_DAYS = 180


def days_since(value: str) -> int | None:
    try:
        verified = datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None
    return (date.today() - verified).days


def check_stale() -> None:
    missing = []
    stale = []

    for resource in load_all_resources():
        age = days_since(resource.get("last_verified", ""))
        if age is None:
            missing.append(resource["id"])
        elif age > STALE_AFTER_DAYS:
            stale.append((age, resource["id"], resource["category"]))

    for resource_id in sorted(missing):
        log(f"❌ {resource_id}: no valid last_verified date")

    for age, resource_id, category in sorted(stale, reverse=True):
        log(f"⚠️ {resource_id} ({category}): not verified for {age} days")

    if missing:
        log(f"\n{len(missing)} resource(s) without a verification date.")
        sys.exit(1)

    if stale:
        log(f"\n{len(stale)} resource(s) not verified in {STALE_AFTER_DAYS} days.")
        log("Run check-links to reverify them.")
        sys.exit(1)

    log(f"✅ All resources verified within {STALE_AFTER_DAYS} days.")


if __name__ == "__main__":
    check_stale()
