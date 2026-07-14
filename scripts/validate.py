import sys

import jsonschema
from utils import SCHEMA_FILE, get_all_resource_files, load_json, log


def validate():
    schema = load_json(SCHEMA_FILE)
    validator = jsonschema.Draft7Validator(
        schema, format_checker=jsonschema.FormatChecker()
    )
    errors_found = False

    for path in get_all_resource_files():
        data = load_json(path)
        resources = data.get("resources", [])
        for resource in resources:
            errors = list(validator.iter_errors(resource))
            if errors:
                errors_found = True
                log(f"❌ {path.name} — {resource.get('id', 'unknown')}")
                for error in errors:
                    log(f"   {error.message}")

    if not errors_found:
        log("✅ All resources valid.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    validate()
