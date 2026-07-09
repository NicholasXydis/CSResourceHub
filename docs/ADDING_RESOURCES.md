# Adding Resources

## Quick Way

Run the interactive CLI with Make when available:

```bash
make add
```

Or run the Python script directly:

```bash
python3 scripts/add_resource.py
```

On Windows, if `python3` is not on `PATH`, use the Python launcher:

```powershell
py -3 scripts\add_resource.py
```

## Manual Way

1. Find the correct JSON file in `data/` based on the category
2. Add your entry following the schema in [SCHEMA.md](./SCHEMA.md)
3. Run validation to check your entry
4. Regenerate derived outputs so README, exports, stats, and EDA charts stay current
5. Run duplicate checks to ensure no duplicates
6. Commit the source and generated changes, then open a PR

With Make:

```bash
make validate
make generate
make check-duplicates
```

Without Make:

```bash
python3 scripts/validate_all.py
python3 scripts/sort_resources.py
python3 scripts/generate_readme.py
python3 scripts/generate_combined.py
python3 scripts/generate_site_json.py
python3 scripts/generate_stats_json.py
python3 scripts/export_csv.py
python3 scripts/generate_eda_report.py
python3 scripts/check_duplicates.py
```

On Windows, if `python3` is not on `PATH`:

```powershell
py -3 scripts\validate_all.py
py -3 scripts\sort_resources.py
py -3 scripts\generate_readme.py
py -3 scripts\generate_combined.py
py -3 scripts\generate_site_json.py
py -3 scripts\generate_stats_json.py
py -3 scripts\export_csv.py
py -3 scripts\generate_eda_report.py
py -3 scripts\check_duplicates.py
```

You can also pass the Python launcher through Make when Make is installed:

```powershell
make validate PYTHON="py -3"
make generate PYTHON="py -3"
make check-duplicates PYTHON="py -3"
```

## Generated Outputs

`make generate` refreshes every derived artifact checked by CI:

- `README.md`
- `generated/all_resources.json`
- `generated/site.json`
- `generated/stats.json`
- `generated/resources.csv`
- `generated/eda/report.md`
- `generated/eda/*.svg`

The EDA SVGs are generated deterministically. If CI reports `Generated files committed` as `FAIL`, run `make generate`, review the listed files, and commit the regenerated outputs.

## Rules

- One resource per PR when possible
- Resource must be active and publicly accessible
- Resource should be useful to Computer Science students in Canada
- Description must be one sentence ending with a period
- URL must include `https://`, no trailing slash, and no tracking parameters
- `id` must be unique across all files, lowercase, hyphens only
- `last_verified` is required and should be the date the URL was checked
- Only use `type` in categories that explicitly allow it in [SCHEMA.md](./SCHEMA.md)
- Use `month` only when a resource has a clear recurring or seasonal month
- Use `location` only when the resource has a meaningful online or physical location
- Leave `location` out when it is unknown; generated README tables show `~` for omitted locations
- Use `Online` for fully virtual resources
- Check [STYLE_GUIDE.md](./STYLE_GUIDE.md) before writing descriptions

## Not Sure Which Category?

See [CATEGORIES.md](./CATEGORIES.md) for a description of each category.
