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
- Description must be one sentence ending with a period
- URL must include `https://`
- `id` must be unique across all files, lowercase, hyphens only
- `quality` must be honestly rated 1-5
- Check [STYLE_GUIDE.md](./STYLE_GUIDE.md) before writing descriptions

## Not Sure Which Category?

See [CATEGORIES.md](./CATEGORIES.md) for a description of each category.
