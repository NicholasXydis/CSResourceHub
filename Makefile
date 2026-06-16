.PHONY: validate generate lint stats add check-links check-duplicates help

validate:
	python scripts/validate.py

generate:
	python scripts/generate_readme.py
	python scripts/generate_combined.py
	python scripts/generate_site_json.py

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

help:
	@echo "validate        - Validate all JSON files against schema"
	@echo "generate        - Regenerate README and combined JSON files"
	@echo "lint            - Lint Python scripts and JSON files"
	@echo "stats           - Print resource counts per category"
	@echo "add             - Interactive CLI to add a new resource"
	@echo "check-links     - Check all URLs for dead links"
	@echo "check-duplicates - Check for duplicate URLs"