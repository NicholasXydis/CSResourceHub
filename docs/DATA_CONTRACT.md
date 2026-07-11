# Data Contract

CS Resource Hub stores curated resources as JSON and publishes generated outputs for docs, analysis, spreadsheet use, and the static frontend in `src/`. The source files in `data/` remain the source of truth.

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
| `type` | Category-specific resource type. Required and always `event` for the Experience categories; optional elsewhere. See [SCHEMA.md](./SCHEMA.md). |
| `month` | Month name for recurring or seasonal resources. |
| `location` | Physical location or `Online` when location is meaningful. |

## Generated Outputs

Generated files are committed so the dataset can be consumed without running scripts.

| Output | Shape | Intended use |
| --- | --- | --- |
| `README.md` | Markdown tables grouped by area and category. | Human browsing on GitHub. |
| `docs/SCHEMA.md` | Field and allowed-type reference. | Generated from the schema and the type allow-list, so it cannot drift from validation. |
| `generated/all_resources.json` | `{ generated, total, resources }` with a flat `resources` array. | General machine-readable dataset export. |
| `generated/site.json` | `{ generated, total, labels, types, groups, categories }` where `groups` and `categories` are keyed objects, plus the category labels and the schema's type enum. | Static frontend input. The frontend derives every category, collection, count, and type from this file. |
| `generated/favicons.json` | `{ generated, checked, missing, siteOnly }`. `missing` lists domains with no icon anywhere; `siteOnly` lists domains Google has no icon for but which serve their own. | Tells the frontend which logo source to request first, and when to skip straight to the placeholder. Refreshed by `make check-favicons`. |
| `generated/stats.json` | `{ generated, total, categories, groups }` summary counts. | Stats cards, dashboards, and EDA checks. |
| `generated/resources.csv` | Flat CSV with resource fields as columns. | Excel, spreadsheets, and data analysis tools. |
| `generated/eda/report.md` | Static Markdown report with deterministic SVG charts. | Portfolio-friendly dataset quality overview. |

The `generated` field records the latest dataset update date derived from resource metadata, not the time the script was run.

## Compatibility Notes

- Treat `id`, `category`, and `url` as stable identifiers for joins and links.
- Optional fields may be absent; consumers should handle missing `type`, `month`, and `location`. Resources in the Experience categories always carry `type: "event"`.
- Generated output order is deterministic but should not be used as a permanent identity.
- Add new fields through the schema first, then update validation, generated outputs, and documentation together.

## Refreshing Outputs

Run the generation pipeline after changing source data or generation scripts:

```bash
make generate
```

On Windows without Make, run the direct commands listed in [ADDING_RESOURCES.md](./ADDING_RESOURCES.md).