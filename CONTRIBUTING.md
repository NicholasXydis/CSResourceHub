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
- Read [STYLE_GUIDE.md](./docs/STYLE_GUIDE.md) before writing descriptions
- Read [ADDING_RESOURCES.md](./docs/ADDING_RESOURCES.md) for step by step instructions

## Process

1. Fork the repo
2. Create a branch: `git checkout -b add/resource-name`
3. Add your resource to the correct JSON file in `data/`
4. Run `make validate` to check your entry
5. Run `make check-duplicates` to ensure no duplicates
6. Commit and open a PR using the PR template

## Schema

Every resource must follow the schema defined in `schema/resource.schema.json`.
See [docs/SCHEMA.md](./docs/SCHEMA.md) for full field documentation.

## Questions

Open a [GitHub Discussion](https://github.com/NicholasXydis/CSResourceHub/discussions) or see [SUPPORT.md](./SUPPORT.md).
