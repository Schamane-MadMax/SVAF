# RFC SVAF-0001
## Semantic Video Analysis Format (SVAF)

**Status:** Draft  
**Version:** 0.5  
**Category:** Proposed Standard  
**Last Updated:** 2026-08-19  

**Changes in 0.5:** The container inventory and all examples now describe the
format as actually produced by the reference pipeline (validated against
production containers). `ocr.json` is standardized; `speaker.rttm` and
RAG export files are classified as sidecars; components that are specified
but not yet produced by any implementation are marked as such.

---

## 1. Abstract

This document specifies the **Semantic Video Analysis Format (SVAF)**, an open, event-based format for transforming audiovisual media into **machine-readable knowledge representations** with minimal storage overhead.

SVAF is explicitly designed to make content from video, audio, and recorded sessions usable for:
- analysis
- search
- retrieval
- Retrieval-Augmented Generation (RAG)
- knowledge systems
- downstream AI pipelines

SVAF is **not a conventional playback-oriented media container**.  
It is a **knowledge extraction and representation format for audiovisual sources**.

---

## 2. Goals

SVAF has three primary goals:

### 2.1 Machine availability
Content should be structured, indexable, semantically addressable, and directly usable for:
- RAG systems
- LLMs
- search engines
- graph systems
- analytics pipelines

### 2.2 Storage efficiency
Full-resolution continuous video should not be the primary knowledge representation.

Storage should focus on what is semantically relevant:
- audio
- text
- events
- identities
- annotations
- visual evidence such as keyframes, slides, overlays, or face crops

### 2.3 Traceability and extensibility
SVAF should support:
- versioned annotations
- multilingual representations
- reproducible extraction pipelines
- extensible metadata and event models
- optional advanced analysis layers

> SVAF is not a movie archive format.  
> SVAF is a knowledge extraction format for media.

---

## 3. Design principles (Normative)

### 3.1 Audio-first
Audio is the source of truth for time alignment.  
All timeline references MUST be addressable against the audio timeline.

### 3.2 State- and event-based representation
SVAF does not model content as a continuous frame stream.  
States change only when semantically relevant events occur.

### 3.3 Semantics before pixels
The format prioritizes meaning over visual continuity:
- faces represent identity or speaker evidence
- slides represent content-bearing visual states
- overlays represent contextual enrichments
- background detail is secondary unless semantically relevant

### 3.4 Layer separation
SVAF separates:
- **Core**: stable, compact, interoperable
- **Extensions**: structured analysis data
- **Sidecars**: model-specific or vendor-specific outputs

### 3.5 Machine- and human-readable structure
SVAF SHOULD use structured JSON plus referenced assets.  
The format SHOULD remain deterministic, versionable, portable, and inspectable.

---

## 4. Container structure (Reference)

A reference SVAF session is represented as a directory:

```text
<session>.svaf/
├── metadata.json          (required)
├── audio.opus             (required)
├── transcript.json        (required)
├── events.json            (required)
├── tracks.json            (optional, recommended)
├── identities.json        (optional, recommended)
├── ocr.json               (optional)
├── slides/                (optional)
├── proxy.mkv              (optional)
├── embeddings.json        (optional; BIOMETRIC, see section 11)
├── annotations.json       (specified, not yet produced)
├── faces/                 (specified, not yet produced)
├── metrics/               (specified, not yet produced)
├── embeddings/            (specified, not yet produced; privacy-relevant)
└── index/                 (specified, not yet produced)
```

Notes:
- `audio.opus`, `transcript.json`, `events.json`, and `metadata.json` are REQUIRED.
- `ocr.json` contains extracted text per slide keyframe (see schemas/ocr.schema.json).
- `embeddings.json` contains per-speaker voice embedding centroids
  (see schemas/embeddings.schema.json). It is biometric data: the fail-closed
  rule of section 11.3 applies to this file exactly as to the `embeddings/`
  directory.
- Components marked "specified, not yet produced" are part of this specification
  but are not written by any known implementation yet; readers MUST NOT rely on
  their presence.
- Future RFCs MAY define additional standardized files.

Sidecars observed in practice (implementation-specific, non-normative):
- `speaker.rttm` — raw diarization output the speaker tracks were derived from
- `rag/` — retrieval export artifacts (chunk export, enrichment, ingestion state)
- `_work/` — temporary pipeline working files; MUST be ignored by readers
- `transcript_corrected.txt` — manually corrected plain-text transcript

Sidecars follow the layer separation rule (section 3.4): compliant readers
MUST function without them.

---

## 5. Core components

### 5.1 Audio (Required)

File: `audio.opus`

Role:
- master time reference
- primary speech and discourse source
- basis for transcription and diarization alignment

Recommendation:
- Opus
- 48 kHz
- speech-optimized bitrate

---

### 5.2 Transcript layer (Required, multilingual)

`transcript.json` MUST support multiple language variants.

Example:

```json
{
  "primary_language": "de",
  "transcripts": [
    {
      "lang": "de",
      "source": "asr",
      "model": "whisper-large-v3",
      "segments": [
        {
          "start": 142.1,
          "end": 148.4,
          "text": "Das ist der entscheidende Punkt",
          "words": [
            {"w": "Das", "start": 142.1, "end": 142.4, "prob": 0.99},
            {"w": "ist", "start": 142.4, "end": 142.7, "prob": 0.98},
            {"w": "der", "start": 142.7, "end": 143.2, "prob": 0.99},
            {"w": "entscheidende", "start": 143.2, "end": 144.6, "prob": 0.97},
            {"w": "Punkt", "start": 144.6, "end": 145.1, "prob": 0.99}
          ]
        }
      ]
    },
    {
      "lang": "en",
      "source": "translation",
      "model": "mt-v1",
      "segments": [
        {
          "start": 142.1,
          "end": 148.4,
          "text": "This is the decisive point"
        }
      ]
    }
  ]
}
```

Normative rules:
- The original language SHOULD be preserved whenever available.
- Transcript variants MUST be language-tagged.
- Time alignment MUST refer to the same master timeline.
- Translated variants MAY be less granular than the original transcript.
- Word-level timing SHOULD be present for at least one primary transcript variant when technically feasible.

Rationale:
- multilingual search
- multilingual retrieval
- translation-aware downstream RAG
- human and machine inspection

---

### 5.3 Events (Required)

`events.json` is the semantic heart of SVAF.

Events describe semantically relevant changes and markers in time.

Example:

```json
{
  "events": [
    { "t": 0.0, "type": "state_start", "state": "intro" },
    { "t": 83.2, "type": "slide_start", "asset": "slides/0002.webp", "roi": "screen" },
    { "t": 146.8, "type": "mood_change", "identity_id": "p:speaker_a" },
    { "t": 210.0, "type": "speaker_change", "speaker_track": "spk:02", "identity_id": "p:guest01" }
  ]
}
```

Normative event properties:
- `t` MUST represent a timestamp on the master timeline
- `type` MUST identify the event class
- additional fields MAY be event-type-specific
- unknown event types MUST be ignored gracefully by compliant readers

Standard event types (initial set):
- `state_start`
- `slide_start`
- `overlay_start`
- `overlay_end`
- `speaker_change`
- `speaker_active`
- `speaker_inactive`
- `mood_change`
- `topic_shift`
- `keyword_peak`

Future RFCs MAY define additional event classes and schemas.

---

### 5.4 Proxy video (Optional, recommended)

File: `proxy.mkv`

Role:
- human orientation
- visual debugging
- timeline navigation aid in the player

Properties:
- low frame rate
- reduced resolution
- strongly compressed

Normative note:
- Proxy video MUST NOT be treated as the source of truth for content semantics.

---

### 5.5 Metadata (Required)

File: `metadata.json`

Role:
- format version (`svaf_version`, major.minor)
- source reference (path or URI of the original media)
- creation timestamp (`created_utc`)
- extraction configuration (audio, ASR, diarization, slides, OCR)
- container-level privacy state (section 11)

The authoritative field definitions are given by `schemas/metadata.schema.json`
(RFC-0002).

---

## 6. Identity layer

### 6.1 Motivation

Audiovisual knowledge often depends on:
- who is speaking
- who is visible
- what role a person has
- what context or event they belong to

SVAF therefore includes an identity layer inspired by EXIF-style tagged metadata.

---

### 6.2 Identities

`identities.json` contains real, pseudonymous, or anonymous identities.

Example:

```json
{
  "identities": [
    {
      "id": "p:speaker_a",
      "type": "person",
      "display_name": "Speaker A",
      "tags": {
        "svaf:identity.role": "speaker",
        "svaf:identity.language": ["de"],
        "svaf:context.event": "SVAF Talk",
        "svaf:context.project": "SVAF Standardization"
      }
    }
  ]
}
```

Normative rules:
- each identity MUST have a stable `id`
- identities MAY be pseudonymous
- `tags` SHOULD use namespaced keys
- implementations MUST ignore unknown tags gracefully

Recommended tag families:
- `svaf:identity.*`
- `svaf:context.*`
- `svaf:geo.*`
- `svaf:privacy.*`

Examples:
- `svaf:identity.role`
- `svaf:identity.language`
- `svaf:context.event`
- `svaf:geo.recording.place_name`
- `svaf:privacy.mode`

---

## 7. Speaker and face tracks

### 7.1 Motivation

Speech and visual identity evidence should be represented as time-bounded tracks.

This allows:
- diarization
- speaker-specific retrieval
- face-to-speaker linking
- confidence-aware analysis

---

### 7.2 Speaker tracks

Example:

```json
{
  "speaker_tracks": [
    {
      "track_id": "spk:01",
      "identity_id": "p:speaker_a",
      "segments": [
        { "t_start": 12.4, "t_end": 48.9, "confidence": 0.94 },
        { "t_start": 62.1, "t_end": 98.0, "confidence": 0.91 }
      ],
      "quality": {
        "snr_db": 21.5,
        "overlap_pct": 2.1,
        "speech_prob": 0.97
      }
    }
  ]
}
```

Normative rules:
- speaker segments MUST use master-timeline time references
- `identity_id` MAY be omitted or unresolved if identity is unknown
- confidence SHOULD be normalized to a predictable scale such as 0..1
- quality fields MAY be present

---

### 7.3 Face tracks

Example:

```json
{
  "face_tracks": [
    {
      "track_id": "face:01",
      "identity_id": "p:speaker_a",
      "segments": [
        { "t_start": 15.0, "t_end": 44.0, "confidence": 0.91 }
      ],
      "quality": {
        "blur_score": 0.12,
        "occlusion_pct": 5.0,
        "frontal_score": 0.87,
        "face_size_pct": 8.4
      }
    }
  ]
}
```

Normative rules:
- face tracks SHOULD be time-aligned to the master timeline
- confidence and quality metrics MAY be included
- face identity linking MAY remain unresolved if unknown

---

## 8. Annotation and notes layer

### 8.1 Motivation

Machine-extracted content is not the only useful knowledge layer.

Human and machine-added notes may include:
- notes
- summaries
- corrections
- links
- highlights
- questions
- hypotheses

These MUST NOT overwrite the source-derived data.

---

### 8.2 Annotations

Example:

```json
{
  "annotations": [
    {
      "id": "ann:001",
      "type": "note",
      "author": "p:speaker_a",
      "created_utc": "2026-02-02T18:40:00Z",
      "lang": "de",
      "targets": [
        { "type": "time_range", "start": 140.0, "end": 160.0 }
      ],
      "content": "Hier erklärt der Sprecher die Kernaussage des Modells.",
      "confidence": 0.95,
      "version": 1
    }
  ]
}
```

Annotation types MAY include:
- `note`
- `summary`
- `correction`
- `question`
- `link`
- `highlight`
- `hypothesis`

Normative rules:
- annotations MUST be separable from source-derived transcript/event data
- annotations SHOULD support language tagging
- annotations SHOULD explicitly reference their targets
- annotations MAY be human-authored or machine-authored

---

## 9. Versioning of knowledge

### 9.1 Principle

SVAF distinguishes between:
- **immutable source-derived data** such as audio and extracted events
- **versionable knowledge layers** such as annotations, summaries, and corrections

### 9.2 Implications

- Raw source artifacts SHOULD be treated as immutable once generated for a given pipeline version.
- Annotation-like content SHOULD be versionable.
- Implementations MAY keep revisions inline or in separate history structures.
- Future RFCs MAY define a formal revision model.

Example revision object:

```json
{
  "annotation_id": "ann:001",
  "revision": 2,
  "updated_utc": "2026-02-05T09:12:00Z",
  "changes": {
    "content": "Präzisierte Kernaussage des Modells."
  }
}
```

---

## 10. Metrics extension

### 10.1 Rationale

Some analysis pipelines produce metrics useful for:
- filtering
- quality control
- confidence-aware retrieval
- debugging
- analytics

However, raw model-specific tensors or embeddings should not bloat the core format.

---

### 10.2 Core-level aggregated metrics

The following aggregated metrics are considered reasonable for inclusion in core or near-core structures:

Voice:
- `snr_db`
- `speech_prob`
- `overlap_pct`
- `loudness_lufs`
- `diarization_confidence`

Face:
- `blur_score`
- `occlusion_pct`
- `face_size_pct`
- `frontal_score`
- `tracking_confidence`

These metrics:
- SHOULD remain compact
- SHOULD be interpretable across implementations
- SHOULD avoid vendor lock-in where possible

---

### 10.3 Sidecar metrics and embeddings

More detailed model outputs SHOULD be stored outside the core JSON structures.

Reference locations:
- `metrics/`
- `embeddings/`

Examples:
- frame-level scores
- embedding vectors
- model-specific confidence tensors
- experiment outputs

Normative guidance:
- detailed metrics SHOULD be externalized
- biometric sidecars SHOULD be protected according to privacy metadata
- players MUST NOT require model-specific sidecars for baseline interoperability

---

## 11. Privacy and biometrics (Normative)

### 11.1 Motivation

SVAF may contain identity-related and biometric-adjacent data:
- speaker assignments
- face tracks
- voice metrics
- face or voice embeddings in sidecars

Therefore privacy metadata is an explicit part of the format design.

---

### 11.2 Privacy metadata

Container-level privacy state lives in `metadata.json` under `privacy`
(as produced by the reference pipeline):

```json
{
  "privacy": {
    "mode": "pseudonymous",
    "biometrics": "absent",
    "consent": "unknown",
    "retention_days": null
  }
}
```

Recommended values:
- `mode`: `public`, `pseudonymous`, `anonymous`, `restricted`
- `biometrics`: `absent`, `present`, `encrypted`
- `consent`: `unknown`, `given`, `denied`, `not_required`

Identity-level privacy tags (`svaf:privacy.*` in `identities.json`) MAY
additionally override the container-level state per identity:

```json
{
  "svaf:privacy.mode": "pseudonymous",
  "svaf:privacy.consent": "given"
}
```

Normative rules:
- implementations handling biometric sidecars SHOULD expose privacy state clearly
- players and tools SHOULD respect privacy-related metadata
- sidecar biometric data SHOULD be encrypted or otherwise protected where required

---

### 11.3 Responsibilities and legal context (Normative)

- Operators of SVAF-producing pipelines are controllers within the meaning of
  Art. 4(7) GDPR for all identity-related data they generate. This
  specification does not transfer, reduce, or discharge any such obligation.
- Voice or face embeddings used for unique identification constitute
  special-category (biometric) data under Art. 9(1) GDPR. Processing them
  requires a legal basis under Art. 9(2) — in practice, explicit consent.
  Encryption is a protective measure (Art. 32 GDPR), not a legal basis.
- **Fail-closed rule:** If `privacy.biometrics` is `present` and
  `privacy.consent` is not `given`, conforming tools MUST NOT create, export,
  or retain biometric artifacts (`embeddings.json`, `embeddings/`, face crops)
  for that container. A missing `privacy` block or an unknown `biometrics`
  value MUST be treated as `present` whenever biometric artifacts exist in
  the container.
- **Redaction before publication:** `metadata.source` is a free-form path or
  URI and may leak internal storage layout; OCR text in `ocr.json` may contain
  incidental personal data (e-mail addresses, names on slides). Containers
  intended for publication SHOULD have `source` redacted and OCR text screened.
- `mode: pseudonymous` data remains personal data (GDPR Recital 26). Only
  `anonymous` containers fall outside the GDPR's scope.
- When `privacy.biometrics` is `present`, `retention_days` SHOULD be set to a
  concrete value. Deletion MUST extend to derived artifacts (embeddings, raw
  diarization output, retrieval chunks, and vector-index entries), otherwise
  an identity survives its own erasure.
- Systematic biometric processing typically triggers a data protection impact
  assessment (Art. 35(3)(b) GDPR). Data subject rights (Art. 15, 17, 20 GDPR)
  apply to SVAF containers like to any other personal-data store.

---

## 12. Search and indexing (Normative)

### 12.1 Searchable sources

A conforming SVAF ecosystem SHOULD support search across:
- transcripts in all available languages
- annotations
- slide OCR or equivalent extracted text
- identity and context tags

### 12.2 Search behavior

A conforming SVAF player SHOULD provide:
- keyword search
- phrase search
- timestamped results
- filters by speaker, slide, and time range where data is available

Optional advanced filters MAY include:
- language
- event type
- confidence threshold
- topic state

### 12.3 Index storage

Search indexes MAY be:
- built on the fly
- shipped as part of the session in `index/`

Reference implementation candidates include:
- SQLite FTS
- other local inverted-index approaches

Index files are OPTIONAL but recommended for large sessions or collections.

---

## 13. RAG integration model

### 13.1 Primary intention

SVAF is designed to make audiovisual media directly usable for retrieval and context injection.

### 13.2 Retrieval units

Retrieval units SHOULD be derived from natural structures such as:
- transcript segments
- speaker segments
- slide intervals
- annotation targets
- event-bounded topic segments

### 13.3 Chunking philosophy

SVAF avoids hardcoding a single chunking strategy into the base format.

Instead:
- the source remains semantically structured
- retrieval systems derive chunks dynamically
- provenance remains intact

Every retrieved chunk SHOULD be traceable to:
- time range
- speaker or identity if available
- active slide or event context if available
- source transcript language
- confidence or quality metadata where relevant

---

## 14. Storage efficiency considerations

A typical two-hour lecture-oriented session may result in approximately:

| Artifact | Typical Size |
|---|---:|
| audio.opus | 40–80 MB |
| proxy.mkv | 50–200 MB |
| slides / keyframes | 1–10 MB |
| transcript + annotations | < 5 MB |
| events + metadata | < 1 MB |

This can preserve the large majority of knowledge value for many RAG and search use cases while using only a fraction of the storage of continuous high-quality video.

---

## 15. Player model (Non-normative overview)

A reference SVAF player is expected to be:
- read-only
- event-driven
- audio-centered
- search-first

Suggested UI tracks:
- audio
- transcript
- slides
- speaker / identity
- optional face / mood
- proxy video

Key interactions:
- click search result → jump to time
- click transcript word or segment → play audio
- click slide → view visual evidence
- filter by speaker, slide, time, language

The player is a **view over SVAF data**, not the authoritative source of semantics.

---

## 16. Compatibility and extensibility

SVAF is designed for forward compatibility.

Normative guidance:
- unknown event types MUST be ignored gracefully
- unknown tags MUST be ignored gracefully
- optional files MAY be absent
- future RFCs MAY standardize additional components without breaking baseline readers

---

## 17. Essence

> SVAF does not primarily store what a viewer sees frame by frame.  
> SVAF stores what is relevant, when it is relevant, and why it matters.

> SVAF is not a movie format.  
> SVAF is a knowledge extraction and representation format for audiovisual sources.

---

## 18. Follow-up RFCs

- **RFC-0002:** SVAF JSON Schema — published (see docs/rfcs/RFC-0002-json-schemas.md)
- **RFC-0003:** SVAF Query and Retrieval Model — planned
- **RFC-0004:** SVAF Reference Encoder / Converter — planned
- **RFC-0005:** SVAF Player Specification — planned
