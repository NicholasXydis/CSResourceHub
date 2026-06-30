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
- Resource should be useful to Computer Science students in Canada
- Description must be one sentence ending with a period
- URL must include `https://`, no trailing slash, and no tracking parameters
- `id` must be unique across all files, lowercase, hyphens only
- `last_verified` is required and should be the date the URL was checked
- Use `month` only when a resource has a clear recurring or seasonal month
- Use an exact `location` such as `Montreal, Quebec, Canada` when known
- Use `Online` for fully virtual resources
- Check [STYLE_GUIDE.md](./STYLE_GUIDE.md) before writing descriptions

## Not Sure Which Category?

See [CATEGORIES.md](./CATEGORIES.md) for a description of each category.