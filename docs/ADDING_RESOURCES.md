# Adding Resources

## Quick Way

Run the interactive CLI:

```bash
make add
```

## Manual Way

1. Find the correct JSON file in `data/` based on the category
2. Add your entry following the schema in [SCHEMA.md](./SCHEMA.md)
3. Run `make validate` to check your entry
4. Run `make check-duplicates` to ensure no duplicates
5. Commit and open a PR

## Rules

- One resource per PR when possible
- Resource must be active and publicly accessible
- Resource should be useful to Computer Science students in North America
- Description must be one sentence ending with a period
- URL must include `https://`, no trailing slash, and no tracking parameters
- `id` must be unique across all files, lowercase, hyphens only
- `last_verified` is required and should be the date the URL was checked
- Do not set `quality`; maintainers set it during review
- Use only approved values from `data/tags.json`, `data/regions.json`, `data/types.json`, and `data/languages.json`
- Use `global` only for resources broadly useful to North American students
- Check [STYLE_GUIDE.md](./STYLE_GUIDE.md) before writing descriptions

## Not Sure Which Category?

See [CATEGORIES.md](./CATEGORIES.md) for a description of each category.
