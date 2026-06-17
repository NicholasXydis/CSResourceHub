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
| `status`      | string  | `active`, `paused`, or `archived`            | `"active"`                          |
| `region`      | array   | List of regions from `data/regions.json`     | `["North-America"]`                 |
| `date_added`  | string  | ISO date YYYY-MM-DD                          | `"2026-06-15"`                      |
| `last_verified` | string | ISO date last URL was confirmed active     | `"2026-06-15"`                      |

### Optional

| Field           | Type   | Description                              | Example        |
| --------------- | ------ | ---------------------------------------- | -------------- |
| `cost`          | string | `free`, `freemium`, or `paid`            | `"free"`      |

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
  "date_added": "2026-06-15",
  "last_verified": "2026-06-15"
}
```
