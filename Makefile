.PHONY: validate generate lint stats add check-links check-duplicates check-regions sort check-category check-descriptions stats-json export-csv check-optional check-urls check-types check-languages help

validate:
	python scripts/validate_all.py

generate:
	python scripts/sort_resources.py
	python scripts/generate_readme.py
	python scripts/generate_combined.py
	python scripts/generate_site_json.py
	python scripts/generate_stats_json.py
	python scripts/export_csv.py

lint:
	ruff check scripts/
	python scripts/lint_json.py

stats:
	python scripts/stats.py

add:
	python scripts/add_resource.py

check-links:
	python scripts/check_links.py

check-duplicates:
	python scripts/check_duplicates.py

check-regions:
	python scripts/check_regions.py

sort:
	python scripts/sort_resources.py

check-category:
	python scripts/check_category_match.py

check-descriptions:
	python scripts/check_descriptions.py

stats-json:
	python scripts/generate_stats_json.py

export-csv:
	python scripts/export_csv.py

check-optional:
	python scripts/check_optional_fields.py

check-urls:
	python scripts/validate_urls_normalized.py

check-types:
	python scripts/check_types.py

check-languages:
	python scripts/check_languages.py

help:
	@echo "validate        - Run all schema and dataset quality checks"
	@echo "generate        - Regenerate README and combined JSON files"
	@echo "lint            - Lint Python scripts and JSON files"
	@echo "stats           - Print resource counts per category"
	@echo "add             - Interactive CLI to add a new resource"
	@echo "check-links     - Check all URLs for dead links"
	@echo "check-duplicates - Check for duplicate URLs"
	@echo "check-regions   - Validate region values"
	@echo "sort            - Sort resources alphabetically by name"
	@echo "check-category  - Ensure resources match their category files"
	@echo "check-descriptions - Check description style"
	@echo "stats-json      - Generate machine-readable stats"
	@echo "export-csv      - Export resources to CSV"
	@echo "check-optional  - Report optional field coverage"
	@echo "check-urls      - Validate URL normalization"
	@echo "check-types     - Validate type values"
	@echo "check-languages - Validate language values"
