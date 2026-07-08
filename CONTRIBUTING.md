# Contributing

Thank you for helping make CS Resource Hub better.

## Ways to Contribute

- Add a new resource
- Fix a dead link
- Update outdated information
- Improve descriptions

## Before You Start

- Check existing resources to avoid duplicates
- Make sure the resource is active and high quality
- Make sure the resource is useful to Computer Science students in Canada
- Read [STYLE_GUIDE.md](./docs/STYLE_GUIDE.md) before writing descriptions
- Read [ADDING_RESOURCES.md](./docs/ADDING_RESOURCES.md) for step by step instructions

## Process

1. Fork the repo
2. Create a branch: `git checkout -b add/resource-name`
3. Add your resource to the correct JSON file in `data/`
4. Run validation to check your entry
5. Run duplicate checks to ensure no duplicates
6. Commit and open a PR using the PR template

With Make:

```bash
make validate
make check-duplicates
make lint
```

Without Make:

```bash
python3 scripts/validate_all.py
python3 scripts/check_duplicates.py
python3 -m ruff check scripts/
python3 scripts/lint_json.py
```

On Windows, if `python3` is not available on `PATH`, use the Python launcher:

```powershell
py -3 scripts\validate_all.py
py -3 scripts\check_duplicates.py
py -3 -m ruff check scripts\
py -3 scripts\lint_json.py
```

If Make is installed on Windows, pass the launcher explicitly:

```powershell
make validate PYTHON="py -3"
make check-duplicates PYTHON="py -3"
make lint PYTHON="py -3"
```

## Schema

Every resource must follow the schema defined in `schema/resource.schema.json`.
See [docs/SCHEMA.md](./docs/SCHEMA.md) for full field documentation.

## Questions

Use [Discussions](https://github.com/NicholasXydis/CSResourceHub/discussions) or see [SUPPORT.md](./SUPPORT.md).

