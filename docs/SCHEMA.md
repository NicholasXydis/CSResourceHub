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
| `date_added`  | string  | ISO date last added                          | `"2026-06-15"`                      |
| `last_verified` | string | ISO date last URL was confirmed active      | `"2026-06-15"`                      |

### Optional

| Field           | Type   | Description                              | Example        |
| --------------- | ------ | ---------------------------------------- | -------------- |
| `type`          | string | Optional resource type from the allowed type list | `"course"` |
| `month`         | string | Month name for recurring or seasonal resources | `"March"` |
| `location`      | string | Exact location or `Online` when useful | `"Montreal, Quebec, Canada"` |

Allowed `type` values: `book`, `course`, `website`, `video`, `reference`, `tool`, `news`, `practice`, `guide`, `system-design`, `behavioral`, `mock-interview`, `resume`, `specialized`, `discord`, `reddit`, `club`, `organization`, `project`, `resource`.

## Example Entry

```json
{
  "id": "uoftctf",
  "name": "UofTCTF",
  "url": "https://ctf.uoftctf.org",
  "description": "Student CTF by the University of Toronto.",
  "category": "ctfs",
  "type": "practice",
  "location": "Online",
  "date_added": "2026-06-15",
  "last_verified": "2026-06-15",
  "month": "March"
}
```
