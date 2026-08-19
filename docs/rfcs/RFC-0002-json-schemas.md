# RFC SVAF-0002: JSON Schema Suite

**Version:** 1.1
**Status:** Draft
**Date:** 2026-08-19
**Depends on:** RFC-0001 (v0.5)

**Changes in 1.1:** The schemas now describe the format as actually produced
by the reference pipeline and are validated against production containers.
`ocr.schema.json` was added. Fictional publication URLs were removed; the
`schemas/` directory of this repository is the single normative source.

---

## Abstract

This RFC defines the JSON Schema suite for SVAF containers. The machine-readable
schema files in the [`schemas/`](../../schemas/) directory of this repository are
**normative**; this document explains their scope, validation levels, and
versioning rules. Where prose and schema file disagree, the schema file wins.

---

## 1. Schema Overview

All schemas use JSON Schema draft 2020-12.

| Schema file | Validates | Presence in container |
|---|---|---|
| `metadata.schema.json` | `metadata.json` | required |
| `transcript.schema.json` | `transcript.json` | required |
| `events.schema.json` | `events.json` | required |
| `tracks.schema.json` | `tracks.json` | optional, recommended |
| `identities.schema.json` | `identities.json` | optional, recommended |
| `ocr.schema.json` | `ocr.json` | optional |
| `annotations.schema.json` | `annotations.json` | specified, not yet produced |

`annotations.schema.json` describes a component of RFC-0001 (section 8) that no
known implementation writes yet; it is retained as the target definition.

Implementation-specific sidecars (`speaker.rttm`, `rag/`, `_work/`, see
RFC-0001 section 4) are intentionally not schema-governed.

---

## 2. Design Rules

- **Reality-first:** Every published schema MUST validate the containers the
  reference pipeline actually produces. Aspirational fields belong in future
  RFC drafts, not in released schemas.
- **Open by default:** All object schemas allow additional properties
  (`additionalProperties: true`) so implementations can attach extra data
  without breaking validation. Readers MUST ignore unknown fields.
- **Flat event types:** Event `type` values are flat lower_snake_case names
  (RFC-0001 section 5.3). Unknown types MUST be ignored by readers.
- **Timestamps:** All times are seconds (number, ≥ 0) on the master audio
  timeline.
- **Format version:** `svaf_version` uses `major.minor` (e.g. `"0.4"`), not
  three-part SemVer.

---

## 3. Validation Levels

1. **Syntactic:** each JSON file parses and validates against its schema.
2. **Referential:** `events[].speaker_track` resolves to a
   `speaker_tracks[].track_id`; `identity_id` values resolve to
   `identities[].id`; `events[].asset` and `ocr.slides[].asset` point to files
   existing in the container.
3. **Semantic:** segment times are monotonic per track, `t_end >= t_start`,
   transcript segment times lie within the audio duration.

Level 1 is REQUIRED for conformance. Levels 2 and 3 are RECOMMENDED and may be
reported as warnings.

---

## 4. Known Format Inconsistencies

Documented as-built quirks that schemas deliberately tolerate:

- `identities[].tags` is canonically an object with string values; existing
  containers also contain an empty array, which MUST be read as "no tags".

---

## 5. Schema Versioning

- Schemas evolve with the format version in RFC-0001. A change that makes
  previously valid containers invalid requires a new `svaf_version` minor bump
  and an RFC changelog entry.
- Each schema carries a stable `$id`. Consumers SHOULD pin schemas by
  repository tag, not by `$id` URL (no hosted schema endpoint exists).

---

## 6. Validating a Container

Example with Python and the `jsonschema` package:

```python
import json, pathlib, jsonschema

session = pathlib.Path("session.svaf")
schemas = pathlib.Path("schemas")

for name in ["metadata", "transcript", "events", "tracks", "identities", "ocr"]:
    data_file = session / f"{name}.json"
    if not data_file.exists():
        continue  # optional files may be absent
    schema = json.loads((schemas / f"{name}.schema.json").read_text())
    jsonschema.validate(json.loads(data_file.read_text()), schema)
```
