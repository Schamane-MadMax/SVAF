# SVAF – Semantic Video Analysis Format

> Transform audio and video into machine-readable knowledge.

SVAF is an **event-based, audio-first format** for converting audiovisual media
into **structured, searchable, storage-efficient, and RAG-ready knowledge
representations**.

Instead of treating media as a continuous frame stream, SVAF treats it as a
**timeline of meaning**:
- **Audio** provides the master time reference
- **Transcripts** provide searchable text
- **Events** describe semantically relevant changes
- **Identities and tracks** connect speakers, faces, and context
- **Optional visual assets** (slides, OCR) preserve important visual evidence
  with minimal storage cost

## Why SVAF exists

Traditional media formats such as MP4, MKV, and WebM are optimized for
playback, not for knowledge extraction. They are frame-centric, hard to search,
difficult to index semantically, and oversized for many lecture, podcast,
meeting, and presentation use cases.

SVAF turns audiovisual recordings into machine-available knowledge with low
storage overhead. Typical target domains: podcasts, talks and lectures,
slide-based recordings, interviews, meetings, audiovisual knowledge archives.

## Status

**Draft / RFC phase.** The specification (RFC-0001 v0.5) and the JSON schemas
(RFC-0002 v1.1) describe the format **as actually produced** by a production
pipeline; the schemas are validated against real containers. The Python
reference library in `src/svaf/` predates this alignment and is being reworked.

## Repository structure

```text
.
├── docs/
│   ├── rfcs/                  RFC-INDEX, RFC-0001 (core), RFC-0002 (schemas)
│   └── spec-vs-implementation.md
├── schemas/                   normative JSON Schemas (draft 2020-12)
├── src/svaf/                  Python reference library (being reworked)
├── tests/                     library tests and synthetic fixtures
├── CHANGELOG.md
└── LICENSE                    MIT
```

## Documentation

- [RFC Index](docs/rfcs/RFC-INDEX.md)
- [RFC-0001 – Core Specification](docs/rfcs/RFC-0001-core.md)
- [RFC-0002 – JSON Schema Suite](docs/rfcs/RFC-0002-json-schemas.md)

## What a SVAF session contains

- `audio.opus` — master audio (required)
- `transcript.json` — multilingual transcripts with word timing (required)
- `events.json` — semantic timeline events (required)
- `metadata.json` — format version, source, extraction config, privacy state (required)
- `tracks.json` — speaker tracks from diarization
- `identities.json` — pseudonymous identity layer
- `ocr.json`, `slides/` — slide keyframes and extracted text
- `proxy.mkv` — optional low-cost orientation video

See RFC-0001 section 4 for the full inventory including planned components.

## Privacy and biometrics

SVAF may describe identity-related data (speaker assignments, face tracks,
optional biometric sidecars). Privacy metadata is part of the format design,
not an afterthought: containers carry explicit `mode`, `biometrics`, `consent`,
and `retention_days` fields, and RFC-0001 section 11 defines a fail-closed rule
for biometric sidecars without consent. Operators of SVAF pipelines remain
responsible for GDPR compliance (see RFC-0001 section 11.3).

## License

Code and specification: MIT — see [LICENSE](LICENSE).

## Vision

> SVAF does not primarily store media for playback.
> SVAF stores **meaning in time**.
