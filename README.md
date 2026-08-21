<p align="center">
  <img src="docs/assets/logo.svg" alt="SVAF logo" width="160">
</p>

# SVAF – Semantic Video Analysis Format

[![tests](https://github.com/svaf-project/SVAF/actions/workflows/tests.yml/badge.svg)](https://github.com/svaf-project/SVAF/actions/workflows/tests.yml)
[![PyPI](https://img.shields.io/pypi/v/svaf.svg)](https://pypi.org/project/svaf/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Spec](https://img.shields.io/badge/spec-v0.5%20draft-orange.svg)](docs/rfcs/RFC-0001-core.md)

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
package in `src/svaf/` is deliberately small: a schema-driven validator
(`svaf validate`, RFC-0002 §3 levels 1–3) and a container inspector
(`svaf info`). Container construction and a parsing object model are out of
scope until a real consumer exists — the JSON Schemas are the single source
of truth.

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

## Install and use the validator

```bash
pip install svaf

svaf validate path/to/session.svaf            # levels 1–3, warnings tolerated
svaf validate path/to/session.svaf --strict   # warnings fail the run
svaf info path/to/session.svaf                # inventory and privacy state
```

Requires Python 3.9 or newer. Details in [src/README.md](src/README.md).

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

## Contributing and security

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md), including
its privacy rules (no real personal data in examples or fixtures). Security
and privacy weaknesses: please report privately, see [SECURITY.md](SECURITY.md).

## License

Code and specification: MIT — see [LICENSE](LICENSE).
To cite the specification, see [CITATION.cff](CITATION.cff).

## Vision

> SVAF does not primarily store media for playback.
> SVAF stores **meaning in time**.
