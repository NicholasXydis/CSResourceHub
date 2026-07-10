# Data Contract

CS Resource Hub stores curated resources as JSON and publishes generated outputs for docs, analysis, spreadsheet use, and future static frontends. The source files in `data/` remain the source of truth.

## Source Data

Each `data/*.json` file contains resources for one category. Every resource must satisfy `schema/resource.schema.json` and the field guidance in [SCHEMA.md](./SCHEMA.md).

Required resource fields:

| Field | Contract |
| --- | --- |
| `id` | Stable lowercase identifier using letters, numbers, and hyphens. Unique across the dataset. |
| `name` | Human-readable resource name. |
| `url` | Public `https://` URL without tracking parameters or a trailing slash. |
| `description` | One concise sentence that describes the resource. |
| `category` | Category slug matching one configured category. |
| `date_added` | ISO date when the resource entered the dataset. |
| `last_verified` | ISO date when the URL was last confirmed active. |

Optional resource fields:

| Field | Contract |
| --- | --- |
| `type` | Category-specific resource type when useful for filtering or grouping. |
| `month` | Month name for recurring or seasonal resources. |
| `location` | Physical location or `Online` when location is meaningful. |

## Generated Outputs

Generated files are committed so the dataset can be consumed without running scripts.

| Output | Shape | Intended use |
| --- | --- | --- |
| `README.md` | Markdown tables grouped by area and category. | Human browsing on GitHub. |
| `generated/all_resources.json` | `{ generated, total, resources }` with a flat `resources` array. | General machine-readable dataset export. |
| `generated/site.json` | `{ generated, total, categories }` with resources grouped by category. | Static frontend/resource browser input. |
| `generated/stats.json` | `{ generated, total, categories, groups }` summary counts. | Stats cards, dashboards, and EDA checks. |
| `generated/resources.csv` | Flat CSV with resource fields as columns. | Excel, spreadsheets, and data analysis tools. |
| `generated/eda/report.md` | Static Markdown report with deterministic SVG charts. | Portfolio-friendly dataset quality overview. |

The `generated` field records the latest dataset update date derived from resource metadata, not the time the script was run.

## Compatibility Notes

- Treat `id`, `category`, and `url` as stable identifiers for joins and links.
- Optional fields may be absent; consumers should handle missing `type`, `month`, and `location`.
- Generated output order is deterministic but should not be used as a permanent identity.
- Add new fields through the schema first, then update validation, generated outputs, and documentation together.

## Refreshing Outputs

Run the generation pipeline after changing source data or generation scripts:

```bash
make generate
```

On Windows without Make, run the direct commands listed in [ADDING_RESOURCES.md](./ADDING_RESOURCES.md).