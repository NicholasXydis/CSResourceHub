# Schema Reference

Every resource in `data/` follows this schema defined in `schema/resource.schema.json`.

## Fields

### Required

| Field         | Type    | Description                                  | Example                             |
| ------------- | ------- | -------------------------------------------- | ----------------------------------- |
| `id`          | string  | Unique stable identifier, lowercase, hyphens | `"picoctf"`                         |
| `name`        | string  | Display name of the resource                 | `"PicoCTF"`                         |
| `url`         | string  | Full URL including https://                  | `"https://picoctf.org"`             |
| `description` | string  | One sentence, ends with period               | `"Beginner-friendly CTF platform."` |
| `category`    | string  | Must match folder name                       | `"ctfs"`                            |
| `cost`        | string  | `free`, `freemium`, or `paid`                | `"free"`                            |
| `status`      | string  | `active`, `paused`, or `archived`            | `"active"`                          |
| `region`      | array   | List of regions from `data/regions.json`     | `["North-America"]`                 |
| `source`      | string  | Where you found it                           | `"official-website"`                |
| `date_added`  | string  | ISO date YYYY-MM-DD                          | `"2026-06-15"`                      |
| `last_verified` | string | ISO date last URL was confirmed active     | `"2026-06-15"`                      |

### Optional

| Field           | Type   | Description                              | Example        |
| --------------- | ------ | ---------------------------------------- | -------------- |
| `quality`       | integer | 1-5 maintainer rating                    | `5`            |
| `tags`          | array  | Tags from `data/tags.json`               | `["security"]` |
| `type`          | string | Resource type from `data/types.json`     | `"platform"`   |
| `language`      | array  | Languages from `data/languages.json`     | `["english"]`  |
| `deadline`      | string | Month name, for time-sensitive resources | `"March"`      |

## Example Entry

```json
{
  "id": "picoctf",
  "name": "PicoCTF",
  "url": "https://picoctf.org",
  "description": "Beginner-friendly CTF platform by Carnegie Mellon.",
  "category": "ctfs",
  "cost": "free",
  "status": "active",
  "region": ["North-America"],
  "source": "official-website",
  "date_added": "2026-06-15",
  "last_verified": "2026-06-15"
}
```
