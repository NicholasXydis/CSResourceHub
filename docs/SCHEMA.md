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

Allowed `type` values are category-specific:

| Category | Allowed `type` values |
| --- | --- |
| `learning-resources` | `book`, `course`, `website`, `video`, `reference`, `tool`, `news` |
| `interview-prep` | `book`, `course`, `guide`, `platform`, `tool` |
| `communities-clubs` | `club`, `discord`, `organization`, `reddit` |
| `open-source` | `project`, `organization`, `resource` |

## Example Entry

```json
{
  "id": "leetcode",
  "name": "LeetCode",
  "url": "https://leetcode.com",
  "description": "Coding interview platform with algorithms, data structures, SQL, and system design problems.",
  "category": "interview-prep",
  "type": "platform",
  "date_added": "2026-06-15",
  "last_verified": "2026-06-15"
}
```
