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
- `type` must come from `data/types.json`
- `language` must come from `data/languages.json`
- `tags` must come from `data/tags.json`

## Regions

- Use `North-America` for resources broadly relevant across North America
- Use `Canada` for Canada-specific resources
- Use `USA` for United States-specific resources
- Use `global` only when the resource is broadly useful to North American students

## Names

- Use the official capitalization
- No abbreviations unless the abbreviation is the official name

Good: `"PicoCTF"`, `"Google Summer of Code"`, `"MLH Fellowship"`

Bad: `"Pico CTF"`, `"GSoC"`, `"mlh fellowship"`

## Quality Ratings

| Rating | Meaning                                  |
| ------ | ---------------------------------------- |
| 5      | Essential, widely recognized, high value |
| 4      | Strongly recommended                     |
| 3      | Good, worth knowing about                |
| 2      | Niche, limited audience                  |
| 1      | Low priority, include for completeness   |

## Cost

| Value      | Meaning                      |
| ---------- | ---------------------------- |
| `free`     | Completely free              |
| `freemium` | Free tier with paid upgrades |
| `paid`     | Requires payment             |

## Source

| Value              | Meaning                          |
| ------------------ | -------------------------------- |
| `official-website` | Found on the resource's own site |
| `community`        | Suggested by a community member  |
| `research`         | Found through research           |
| `social-media`     | Found on Twitter, Reddit, etc.   |

## Quality

Quality is set by maintainers only. Contributors should not include the `quality` field in their submissions — it will be added on review.
