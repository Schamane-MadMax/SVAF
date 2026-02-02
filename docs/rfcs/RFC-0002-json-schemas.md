# RFC SVAF-0002: JSON Schema Suite

**Version:** 1.0
**Status:** Draft
**Author:** Markus
**Date:** 2026-02-02
**Depends on:** RFC-0001

---

## Abstract

This RFC defines the complete JSON Schema suite for SVAF containers, providing formal validation rules, type definitions, and consistency requirements for all core files in a SVAF container.

---

## 1. Motivation

### 1.1 Why JSON Schemas?

- **Validation**: Automated checking of SVAF container integrity
- **Tooling**: IDE support, auto-completion, inline documentation
- **Interoperability**: Cross-language validation (Python, TypeScript, etc.)
- **Documentation**: Schemas serve as machine-readable specifications
- **Testing**: Enable comprehensive validation test suites

### 1.2 Design Goals

1. **Strict by default**: Core fields must be valid
2. **Extensible**: Allow custom fields via `additionalProperties`
3. **Self-documenting**: Rich descriptions in schemas
4. **Versioned**: Schemas track SVAF version compatibility
5. **Composable**: Shared definitions via `$ref`

---

## 2. Schema Overview

### 2.1 Core Schemas

| Schema File | Purpose | Required |
|-------------|---------|----------|
| `metadata.schema.json` | Container metadata | ✅ Yes |
| `events.schema.json` | Event timeline | ✅ Yes |
| `transcript.schema.json` | Transcription data | ⚠️ Conditional |
| `identities.schema.json` | Speaker/face identities | ⚠️ Conditional |
| `tracks.schema.json` | Audio/video track info | ⚠️ Conditional |
| `annotations.schema.json` | Human/machine annotations | ❌ Optional |

### 2.2 Schema Locations

All schemas are published at:
- **GitHub**: `https://github.com/svaf-project/svaf/schemas/`
- **Website**: `https://svaf.org/schemas/`
- **CDN**: `https://cdn.svaf.org/schemas/v1/`

---

## 3. Common Definitions

### 3.1 Shared Types

```json
{
  "$defs": {
    "timestamp": {
      "type": "number",
      "minimum": 0,
      "description": "Time in seconds from start"
    },
    "uuid": {
      "type": "string",
      "format": "uuid"
    },
    "language_code": {
      "type": "string",
      "pattern": "^[a-z]{2}(-[A-Z]{2})?$",
      "description": "ISO 639-1 language code (e.g., 'en', 'de-DE')"
    },
    "semver": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Semantic version (e.g., '1.0.0')"
    }
  }
}
```

---

## 4. Schema Specifications

### 4.1 metadata.schema.json

**Purpose**: Container-level metadata

**Required fields**:
- `svaf_version` (string, semver)
- `container_id` (UUID)
- `title` (string)
- `duration_seconds` (number ≥ 0)
- `primary_language` (ISO 639-1 code)
- `creation_date` (ISO 8601 datetime)

**Optional fields**:
- `description` (string)
- `languages` (array of language codes)
- `last_modified` (ISO 8601 datetime)
- `source` (object with type, original_file, etc.)
- `authors` (array of author objects)
- `tags` (array of strings)
- `license` (string)

**Validation rules**:
- `duration_seconds` must be ≥ 0
- `primary_language` must be in ISO 639-1 format
- `languages` must include `primary_language`
- `creation_date` ≤ `last_modified` if both present

### 4.2 events.schema.json

**Purpose**: Event timeline with typed events

**Structure**:
```json
{
  "events": [
    {
      "event_id": "evt_001",
      "type": "slide.change",
      "start_time": 120.5,
      "end_time": 245.0,
      "keyframe": "keyframes/slide_001.jpg",
      "identity_id": "speaker_01",
      "metadata": { ... }
    }
  ]
}
```

**Event types** (namespace.action):
- `slide.change` - Slide transitions
- `slide.appear` - New slide appears
- `topic.start` / `topic.end` - Topic boundaries
- `face.appear` / `face.disappear` - Face tracking
- `mood.change` - Detected mood shift
- `roi.detected` - Region of interest (chart, code)
- `audio.silence` - Silent periods
- `audio.music_start` / `audio.music_end` - Background music
- Custom types: `custom.*`

**Validation rules**:
- `event_id` must be unique within container
- `start_time` < `end_time` (if both present)
- Events should not overlap (same type)
- `keyframe` path must exist in container
- `identity_id` must reference valid identity

### 4.3 transcript.schema.json

**Purpose**: Multi-language transcriptions with timestamps

**Required fields**:
- `language` (ISO 639-1)
- `format_version` (semver)
- `segments` (array)

**Segment structure**:
```json
{
  "segment_id": "seg_001",
  "start_time": 0.0,
  "end_time": 5.2,
  "speaker_id": "speaker_01",
  "text": "Welcome to this presentation.",
  "confidence": 0.95,
  "words": [ ... ]
}
```

**Validation rules**:
- Segments must not overlap (same speaker)
- `start_time` < `end_time`
- `speaker_id` must reference valid identity
- `confidence` between 0.0 and 1.0
- Word timestamps must be within segment bounds

### 4.4 identities.schema.json

**Purpose**: Speaker and face identity management

**Structure**:
```json
{
  "identities": [
    {
      "identity_id": "speaker_01",
      "type": "speaker",
      "name": "John Doe",
      "role": "presenter",
      "confidence": 0.9,
      "keyframes": ["keyframes/face_001.jpg"],
      "privacy": {
        "anonymize": false,
        "blur_face": false,
        "pseudonym": null
      }
    }
  ]
}
```

**Identity types**:
- `speaker` - Voice-identified person
- `face` - Visually-identified person
- `both` - Linked voice + face

**Validation rules**:
- `identity_id` must be unique
- `confidence` between 0.0 and 1.0
- `keyframes` paths must exist
- If `privacy.anonymize = true`, `name` should be pseudonym

### 4.5 tracks.schema.json

**Purpose**: Audio/video track information

**Structure**:
```json
{
  "tracks": [
    {
      "track_id": "audio_01",
      "type": "audio",
      "format": "opus",
      "sample_rate": 48000,
      "channels": 2,
      "bitrate": 128000,
      "language": "en",
      "metadata": {
        "track_name": "Main Audio",
        "is_default": true
      }
    }
  ]
}
```

**Track types**:
- `audio` - Audio stream
- `video` - Video stream (if keyframes not sufficient)
- `subtitle` - Embedded subtitles

**Validation rules**:
- `track_id` must be unique
- Audio tracks: `sample_rate` > 0, `channels` ∈ {1, 2, 6, 8}
- `language` must be ISO 639-1

### 4.6 annotations.schema.json

**Purpose**: Human and machine annotations

**Structure**:
```json
{
  "annotations": [
    {
      "annotation_id": "ann_001",
      "type": "comment",
      "author": "reviewer@example.com",
      "timestamp": "2026-02-02T10:00:00Z",
      "time_range": {
        "start": 120.0,
        "end": 125.0
      },
      "content": "Great explanation of the concept!",
      "tags": ["important", "review"],
      "target": {
        "type": "segment",
        "id": "seg_042"
      }
    }
  ]
}
```

**Annotation types**:
- `comment` - Text comment
- `correction` - Transcript correction
- `highlight` - Important section marker
- `question` - Question/clarification needed
- `summary` - AI-generated summary
- `classification` - Content classification

**Validation rules**:
- `annotation_id` must be unique
- `timestamp` is creation time (ISO 8601)
- `time_range.start` < `time_range.end`
- `target.id` must reference valid entity

---

## 5. Cross-Schema Validation

### 5.1 Referential Integrity

**Identity references**:
- All `speaker_id` in transcripts must exist in `identities.json`
- All `identity_id` in events must exist in `identities.json`

**Keyframe references**:
- All `keyframe` paths in events must exist in container
- All `keyframes` in identities must exist in container

**Time consistency**:
- All timestamps must be ≤ `metadata.duration_seconds`
- Event timelines must be sorted by `start_time`
- Transcript segments must be sorted by `start_time`

### 5.2 Validation Levels

**Level 1: Schema validation**
- Check JSON syntax
- Validate against JSON Schema
- Type checking, required fields

**Level 2: Consistency validation**
- Referential integrity
- Timestamp bounds
- Unique IDs

**Level 3: Semantic validation**
- Event overlap detection
- Speaker diarization consistency
- Keyframe quality checks

---

## 6. Schema Versioning

### 6.1 Version Format

Schemas follow semantic versioning:
- **Major**: Breaking changes (incompatible)
- **Minor**: New optional fields
- **Patch**: Bug fixes, clarifications

### 6.2 Compatibility Matrix

| SVAF Version | Schema Version | Status |
|--------------|----------------|--------|
| 0.1.x | 0.1.0 | Draft |
| 1.0.x | 1.0.0 | Stable (target) |

### 6.3 Migration Strategy

When schemas change:
1. **Backward compatible**: Tools must accept old versions
2. **Forward migration**: Tool to upgrade containers
3. **Deprecation**: Minimum 6 months warning
4. **Documentation**: Migration guides published

---

## 7. Validation Tools

### 7.1 CLI Validator

```bash
# Basic validation
svaf validate container.svaf

# Strict mode (all levels)
svaf validate container.svaf --strict

# JSON output
svaf validate container.svaf --format=json
```

### 7.2 Python API

```python
from svaf.validator import SVAFValidator

validator = SVAFValidator(strict=True)
result = validator.validate("container.svaf")

if result.is_valid:
    print("✓ Valid SVAF container")
else:
    for error in result.errors:
        print(f"✗ {error.message} at {error.path}")
```

### 7.3 Online Validator

Web-based validator at `https://validator.svaf.org`:
- Drag-and-drop container
- Real-time validation
- Detailed error reports
- Download corrected version

---

## 8. Test Suite

### 8.1 Valid Test Cases

Minimal valid containers for each use case:
- `minimal.svaf` - Absolute minimum
- `podcast.svaf` - Audio-only with transcript
- `lecture.svaf` - Slides + transcript
- `interview.svaf` - Multi-speaker

### 8.2 Invalid Test Cases

Containers that should fail validation:
- `missing_required_fields.svaf`
- `invalid_timestamps.svaf`
- `broken_references.svaf`
- `duplicate_ids.svaf`

### 8.3 Edge Cases

- Empty transcript (audio-only)
- Single-frame video
- Overlapping events (intentional)
- Multi-language (5+ languages)
- Large container (10k+ events)

---

## 9. Implementation Checklist

### Phase 1: Core Schemas (Week 1-2)
- [x] metadata.schema.json (basic)
- [x] events.schema.json (basic)
- [x] transcript.schema.json (basic)
- [x] identities.schema.json (basic)
- [x] tracks.schema.json (basic)
- [x] annotations.schema.json (basic)
- [ ] Add detailed examples to each schema
- [ ] Add common definitions ($defs)

### Phase 2: Validation Rules (Week 2-3)
- [ ] Implement referential integrity checks
- [ ] Implement timestamp validation
- [ ] Implement unique ID checks
- [ ] Implement cross-file validation

### Phase 3: Tooling (Week 3-4)
- [ ] Python validator implementation
- [ ] CLI tool `svaf validate`
- [ ] Test fixtures (valid + invalid)
- [ ] Online validator prototype

### Phase 4: Documentation (Week 4)
- [ ] Schema documentation website
- [ ] Validation error catalog
- [ ] Migration guides
- [ ] Best practices guide

---

## 10. Open Questions

1. **Custom event types**: Require registration or free-form?
2. **Schema strictness**: Allow additional properties at root level?
3. **Validation performance**: Stream large files or load fully?
4. **Error messages**: Technical vs. user-friendly?
5. **Schema hosting**: GitHub-only or dedicated CDN?

---

## 11. References

- **JSON Schema**: https://json-schema.org/
- **RFC-0001**: Core SVAF Specification
- **ISO 639-1**: Language codes
- **ISO 8601**: Datetime format

---

## Changelog

- **2026-02-02**: Initial draft (v1.0)

---

**Status**: Ready for implementation
**Next Steps**: Enhance existing schemas, implement validator
