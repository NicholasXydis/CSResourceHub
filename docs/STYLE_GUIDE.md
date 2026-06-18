# Style Guide

## Descriptions

- One sentence only, ends with a period
- No marketing language ("amazing", "best", "ultimate")
- State what it is and who it is for
- Maximum 120 characters

Good: `"Beginner-friendly CTF platform by Carnegie Mellon."`

Good: `"Annual hackathon for university students across Canada."`

Bad: `"The best resource for learning to code!"`

Bad: `"Amazing platform that will help you get a job."`

## IDs

- Lowercase only
- Hyphens instead of spaces
- No special characters
- Must be unique across all files

Good: `"picoctf"`, `"google-summer-of-code"`, `"mlh-fellowship"`

Bad: `"PicoCTF"`, `"google summer of code"`, `"mlh_fellowship"`

## URLs

- Always include `https://`
- No trailing slashes
- No tracking parameters such as `utm_source`
- Link to the most specific relevant page

Good: `"https://picoctf.org"`

Bad: `"picoctf.org"`, `"https://picoctf.org/"`

## Metadata

- `last_verified` is required for every resource
- Use `month` only for recurring or seasonal resources with a clear month

## Locations

- Use exact Canadian locations when an event has a known physical location
- Use `Online` for fully virtual resources
- Use `Canada` only when a Canadian resource moves between cities or locations are not yet published
- Include top United States options only when they are especially useful to Canadian students

## Names

- Use the official capitalization
- No abbreviations unless the abbreviation is the official name

Good: `"PicoCTF"`, `"Google Summer of Code"`, `"MLH Fellowship"`

Bad: `"Pico CTF"`, `"GSoC"`, `"mlh fellowship"`

## Cost

| Value      | Meaning                      |
| ---------- | ---------------------------- |
| `free`     | Completely free              |
| `freemium` | Free tier with paid upgrades |
| `paid`     | Requires payment             |
