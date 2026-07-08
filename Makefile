PYTHON ?= python3
RUFF ?= $(PYTHON) -m ruff

.PHONY: validate generate lint stats add check-links check-duplicates check-locations sort check-category check-descriptions stats-json export-csv check-urls help

validate:
	$(PYTHON) scripts/validate_all.py

generate:
	$(PYTHON) scripts/sort_resources.py
	$(PYTHON) scripts/generate_readme.py
	$(PYTHON) scripts/generate_combined.py
	$(PYTHON) scripts/generate_site_json.py
	$(PYTHON) scripts/generate_stats_json.py
	$(PYTHON) scripts/export_csv.py

lint:
	$(RUFF) check scripts/
	$(PYTHON) scripts/lint_json.py

stats:
	$(PYTHON) scripts/stats.py

add:
	$(PYTHON) scripts/add_resource.py

check-links:
	$(PYTHON) scripts/check_links.py

check-duplicates:
	$(PYTHON) scripts/check_duplicates.py

check-locations:
	$(PYTHON) scripts/check_locations.py

sort:
	$(PYTHON) scripts/sort_resources.py

check-category:
	$(PYTHON) scripts/check_category_match.py

check-descriptions:
	$(PYTHON) scripts/check_descriptions.py

stats-json:
	$(PYTHON) scripts/generate_stats_json.py

export-csv:
	$(PYTHON) scripts/export_csv.py

check-urls:
	$(PYTHON) scripts/validate_urls_normalized.py

help:
	@echo "validate        - Run all schema and dataset validation checks"
	@echo "generate        - Regenerate README and generated data exports"
	@echo "lint            - Lint Python scripts and JSON files"
	@echo "stats           - Print resource counts per category"
	@echo "add             - Interactive CLI to add a new resource"
	@echo "check-links     - Check all URLs for dead links"
	@echo "check-duplicates - Check for duplicate URLs"
	@echo "check-locations - Validate location values"
	@echo "sort            - Sort resources alphabetically by name"
	@echo "check-category  - Ensure resources match their category files"
	@echo "check-descriptions - Check description style"
	@echo "stats-json      - Generate machine-readable stats"
	@echo "export-csv      - Export resources to CSV"
	@echo "check-urls      - Validate URL normalization"

