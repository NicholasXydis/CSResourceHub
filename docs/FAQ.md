# FAQ

## What is CS Resource Hub?

An open dataset of Canadian Computer Science student resources. Anyone can contribute.

## How do I add a resource?

See [ADDING_RESOURCES.md](./ADDING_RESOURCES.md).

## How do I report a dead link?

Open an issue using the Dead Link template on GitHub.

## How do I report harmful content?

See the [Security Policy](https://github.com/NicholasXydis/CSResourceHub/blob/main/SECURITY.md).

## Why JSON instead of a spreadsheet or markdown table?

JSON is machine-readable, versionable, and can generate the README tables, website/API exports, CSV, stats, and EDA report automatically.

## Can I use this data in my own project?

Yes, under the [CC BY 4.0](../LICENSE-CC-BY) license with attribution.

## How often is this updated?

Continuously via community PRs. CI validates the dataset, checks generated outputs for freshness, and checks dead links weekly.

## What is the EDA report?

The generated EDA report is a static dataset overview at `generated/eda/report.md`. It shows category coverage, resource types, metadata completeness, source concentration, and other quality signals without requiring Jupyter.

## Why did CI say generated files were stale?

The generated-output workflow reruns the data pipeline and compares `data/`, `README.md`, and `generated/` against the committed files. If it fails, run `make generate`, review the changed files, and commit them. EDA SVG output is configured to be deterministic so rerunning the generator should not create noise.
