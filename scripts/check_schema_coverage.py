from utils import load_all_resources, log

OPTIONAL_FIELDS = ["deadline", "last_verified"]

def check_coverage():
    resources = load_all_resources()
    if not resources:
        log("No resources found.")
        return

    for field in OPTIONAL_FIELDS:
        count = sum(1 for r in resources if field in r)
        pct = (count / len(resources)) * 100
        log(f"{field}: {count}/{len(resources)} ({pct:.1f}%)")

if __name__ == "__main__":
    check_coverage()
