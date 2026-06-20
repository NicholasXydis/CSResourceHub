# Schema Reference

Every resource in `data/` follows this schema defined in `schema/resource.schema.json`.

## Fields

### Required

| Field         | Type    | Description                                  | Example                             |
| ------------- | ------- | -------------------------------------------- | ----------------------------------- |
| `id`          | string  | Unique stable identifier, lowercase, hyphens | `"uoftctf"`                         |
| `name`        | string  | Display name of the resource                 | `"UofTCTF"`                         |
| `url`         | string  | Full URL including https://                  | `"https://ctf.uoftctf.org"`         |
| `description` | string  | One sentence, ends with period               | `"Beginner-friendly CTF platform."` |
| `category`    | string  | Must match folder name                       | `"ctfs"`                            |
| `status`      | string  | `active`, `paused`, or `archived`            | `"active"`                          |
| `location`    | string  | Exact location or `Online`                   | `"Montreal, Quebec, Canada"`        |
| `date_added`  | string  | ISO date last added                          | `"2026-06-15"`                      |
| `last_verified` | string | ISO date last URL was confirmed active      | `"2026-06-15"`                      |

### Optional

| Field           | Type   | Description                              | Example        |
| --------------- | ------ | ---------------------------------------- | -------------- |
| `month`         | string | Month name for recurring or seasonal resources | `"March"` |

## Example Entry

```json
{
  "id": "uoftctf",
  "name": "UofTCTF",
  "url": "https://ctf.uoftctf.org",
  "description": "Student CTF by the University of Toronto.",
  "category": "ctfs",
  "status": "active",
  "location": "Online",
  "date_added": "2026-06-15",
  "last_verified": "2026-06-15",
  "month": "March"
}
```
