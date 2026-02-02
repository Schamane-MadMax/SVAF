# RFC SVAF-0001: Semantic Video Analysis Format - Core Specification

**Version:** 0.4
**Status:** Draft
**Autor:** Markus (mit Claude Sonnet 4.5)
**Datum:** 2025-01-15 (aktualisiert: 2026-02-02)

---

## Abstract

SVAF (Semantic Video Analysis Format) ist ein **audio-first, event-basiertes Container-Format** zur Speicherung semantisch relevanter Informationen aus Video- und Audio-Inhalten. Statt vollständiger Videostreams werden nur:

- **Transkripte** (mit Timestamps, Speaker, Sprache)
- **Events** (Slide-Wechsel, Topic-Changes, Face-Appearances)
- **Keyframes** (Folien, Gesichter bei Mood-Change, ROI-Frames)
- **Identitäten** (Speaker, Faces mit Privacy-Optionen)
- **Annotations** (Mensch & Maschine)

gespeichert. SVAF ist optimiert für **RAG-Systeme** (Retrieval-Augmented Generation), Wissensdatenbanken und Content-Archivierung.

---

## 1. Motivation

### 1.1 Probleme bestehender Formate

| Format | Problem |
|--------|---------|
| **Full-Video (MP4/MKV)** | Teuer zu speichern (~2 GB/Stunde), nicht durchsuchbar |
| **Transkripte (TXT)** | Kein Timing, keine Speaker-Info, keine Bilder |
| **Untertitel (SRT/WebVTT)** | Nur Text, keine Semantik, kein Event-Konzept |
| **Podcast-Metadaten (RSS)** | Keine granularen Events, keine Slides |
| **YouTube-Chapters** | Manuell, grob, nicht maschinenlesbar |

### 1.2 SVAF-Design-Ziele

1. **RAG-First**: Perfekt für KI-Wissensdatenbanken
2. **Speicher-effizient**: 50-200 MB statt 2 GB (Full-Video)
3. **Audio-First**: Podcasts ohne Video möglich
4. **Event-basiert**: Strukturierte Timeline statt Freitext
5. **Durchsuchbar**: Volltextsuche + Event-Queries
6. **Versionierbar**: Git-freundlich (Ordner, nicht ZIP)
7. **Privacy-aware**: Optionale Face-Keyframes, Pseudonyme
8. **Erweiterbar**: Core + Extensions + Sidecar-Dateien

---

## 2. Container-Struktur

SVAF ist ein **Ordner-Container** (nicht ZIP/TAR), um Git-freundlich zu sein.

### 2.1 Minimale Struktur

```
video.svaf/
├── metadata.json           # Pflicht
├── events.json             # Pflicht
├── transcript_de.json      # Pflicht (mind. 1 Sprache)
└── keyframes/              # Optional
    └── slide_001.jpg
```

### 2.2 Vollständige Struktur

```
video.svaf/
├── metadata.json           # Container-Metadaten
├── events.json             # Event-Timeline
├── transcript_de.json      # Transkript (Deutsch)
├── transcript_en.json      # Transkript (Englisch)
├── identities.json         # Speaker/Face-Definitionen
├── tracks.json             # Multi-Track Audio (optional)
├── annotations.json        # Mensch/Maschine-Annotationen
├── keyframes/              # Extrahierte Bilder
│   ├── slide_001.jpg
│   ├── slide_002.jpg
│   ├── face_speaker1_001.jpg
│   └── roi_123.jpg
├── proxy/                  # Optional: Low-Res-Video
│   └── proxy_360p.mp4
└── sidecar/                # Erweiterungen (nicht im Core)
    ├── quiz_questions.json
    └── sentiment.json
```

---

## 3. Core-Dateien

### 3.1 `metadata.json` (Pflicht)

Container-weite Metadaten.

```json
{
  "svaf_version": "0.1.0",
  "container_id": "uuid-v4-here",
  "title": "SVAF Einführung",
  "description": "Erklärvideo zum Semantic Video Analysis Format",
  "duration_seconds": 3600,
  "primary_language": "de",
  "languages": ["de", "en"],
  "creation_date": "2025-01-15T10:00:00Z",
  "last_modified": "2025-01-16T14:30:00Z",
  "source": {
    "type": "video",
    "original_file": "video.mp4",
    "original_duration": 3605,
    "original_resolution": "1920x1080",
    "original_size_bytes": 2147483648
  },
  "authors": [
    {
      "name": "Max Mustermann",
      "role": "creator"
    }
  ],
  "tags": ["tutorial", "svaf", "knowledge-management"],
  "license": "CC-BY-4.0"
}
```

**Felder:**
- `svaf_version`: Spec-Version (Semantic Versioning)
- `container_id`: UUID für Referenzierung
- `duration_seconds`: Dauer des Inhalts (nicht Original-Video!)
- `primary_language`: Haupt-Transkript-Sprache (ISO 639-1)
- `source.type`: `video`, `audio`, `podcast`, `stream`

### 3.2 `events.json` (Pflicht)

Event-Timeline - das Herzstück von SVAF.

```json
{
  "events": [
    {
      "event_id": "evt_001",
      "type": "slide.change",
      "start_time": 120.5,
      "end_time": 245.0,
      "keyframe": "keyframes/slide_001.jpg",
      "metadata": {
        "slide_number": 1,
        "title": "Einführung",
        "ocr_text": "SVAF: Semantic Video Analysis Format",
        "confidence": 0.98
      }
    },
    {
      "event_id": "evt_002",
      "type": "topic.change",
      "start_time": 245.0,
      "end_time": 580.0,
      "metadata": {
        "topic": "Container-Struktur",
        "keywords": ["ordner", "git", "versionierung"]
      }
    },
    {
      "event_id": "evt_003",
      "type": "face.appearance",
      "start_time": 0.0,
      "end_time": 120.0,
      "identity_id": "speaker_1",
      "keyframe": "keyframes/face_speaker1_001.jpg",
      "metadata": {
        "mood": "neutral",
        "confidence": 0.92
      }
    }
  ]
}
```

**Event-Felder:**
- `event_id`: Eindeutige ID (z.B. `evt_001`)
- `type`: Event-Typ (siehe 3.2.1)
- `start_time`: Beginn (Sekunden, Float)
- `end_time`: Ende (optional bei Instant-Events)
- `keyframe`: Pfad zu Bild (relativ zum Container)
- `identity_id`: Referenz zu `identities.json`
- `metadata`: Event-spezifische Daten

#### 3.2.1 Standard-Event-Typen

| Event-Typ | Beschreibung | Pflichtfelder | Optional |
|-----------|--------------|---------------|----------|
| `slide.change` | Folienwechsel | `keyframe` | `slide_number`, `title` |
| `topic.change` | Themenwechsel | `start_time` | `topic`, `keywords` |
| `face.appearance` | Gesicht erscheint | `identity_id` | `keyframe`, `mood` |
| `face.mood_change` | Stimmungswechsel | `identity_id`, `keyframe` | `mood_from`, `mood_to` |
| `speaker.change` | Sprecher wechselt | `identity_id` | - |
| `roi.detected` | ROI (Chart/Code) | `keyframe` | `roi_type`, `bbox` |
| `chapter.start` | Kapitel-Beginn | `title` | `chapter_number` |
| `scene.change` | Szenenwechsel | - | `scene_type` |

**Erweiterbar**: Custom-Types erlaubt (z.B. `quiz.question`, `ad.break`)

### 3.3 `transcript_XX.json` (Pflicht, mind. 1)

Transkript mit Timestamps, Speaker, Sprache.

```json
{
  "language": "de",
  "format_version": "0.1.0",
  "segments": [
    {
      "segment_id": "seg_001",
      "start_time": 0.0,
      "end_time": 5.2,
      "speaker_id": "speaker_1",
      "text": "Willkommen zu SVAF - dem Semantic Video Analysis Format.",
      "confidence": 0.95,
      "words": [
        {"word": "Willkommen", "start": 0.0, "end": 0.6},
        {"word": "zu", "start": 0.7, "end": 0.8},
        {"word": "SVAF", "start": 0.9, "end": 1.3}
      ]
    },
    {
      "segment_id": "seg_002",
      "start_time": 5.2,
      "end_time": 10.8,
      "speaker_id": "speaker_1",
      "text": "In diesem Video erkläre ich die Container-Struktur.",
      "confidence": 0.92
    }
  ],
  "metadata": {
    "transcription_engine": "whisper-large-v3",
    "transcription_date": "2025-01-15T12:00:00Z",
    "word_level_timestamps": true
  }
}
```

**Felder:**
- `language`: ISO 639-1 Code (z.B. `de`, `en`, `fr`)
- `segments[]`: Array von Sprach-Segmenten
- `speaker_id`: Referenz zu `identities.json`
- `words[]`: Optional, word-level timestamps (für bessere RAG-Suche)

**Multi-Language:**
- `transcript_de.json` + `transcript_en.json` für mehrsprachige Videos
- `segments[].language` für Code-Switching innerhalb eines Transkripts

### 3.4 `identities.json` (Optional, aber empfohlen)

Definition von Sprechern und Gesichtern.

```json
{
  "identities": [
    {
      "identity_id": "speaker_1",
      "type": "speaker",
      "name": "Max Mustermann",
      "pseudonym": "Sprecher A",
      "privacy_mode": "public",
      "metadata": {
        "role": "presenter",
        "affiliation": "Universität XYZ",
        "bio": "Professor für Informatik"
      }
    },
    {
      "identity_id": "face_unknown_1",
      "type": "face",
      "name": null,
      "pseudonym": "Person B",
      "privacy_mode": "pseudonymous",
      "face_keyframes": [
        "keyframes/face_unknown_1_001.jpg"
      ],
      "metadata": {
        "detected_count": 5,
        "first_appearance": 120.5
      }
    }
  ]
}
```

**Privacy-Modi:**
- `public`: Name und Bilder öffentlich
- `pseudonymous`: Pseudonym verwenden, Bilder optional
- `anonymous`: Keine Keyframes, nur Speaker-ID

### 3.5 `annotations.json` (Optional)

Mensch- und Maschinen-Annotationen.

```json
{
  "annotations": [
    {
      "annotation_id": "anno_001",
      "type": "correction",
      "target": {
        "type": "transcript",
        "segment_id": "seg_001"
      },
      "author_type": "human",
      "author_id": "user_123",
      "timestamp": "2025-01-16T10:00:00Z",
      "content": {
        "original": "SVAF",
        "corrected": "S-V-A-F",
        "reason": "Akronym sollte buchstabiert werden"
      }
    },
    {
      "annotation_id": "anno_002",
      "type": "summary",
      "target": {
        "type": "event",
        "event_id": "evt_001"
      },
      "author_type": "machine",
      "author_id": "gpt-4",
      "timestamp": "2025-01-16T12:00:00Z",
      "content": {
        "summary": "Einführung in SVAF-Container-Struktur",
        "confidence": 0.89
      }
    },
    {
      "annotation_id": "anno_003",
      "type": "tag",
      "target": {
        "type": "timerange",
        "start_time": 120.0,
        "end_time": 245.0
      },
      "author_type": "human",
      "author_id": "user_456",
      "tags": ["wichtig", "für-prüfung"]
    }
  ]
}
```

**Annotation-Typen:**
- `correction`: Transkript-Korrektur
- `summary`: Zusammenfassung
- `tag`: Freitext-Tags
- `comment`: Kommentar
- `highlight`: Markierung

---

## 4. Keyframes

### 4.1 Typen

| Typ | Beschreibung | Format | Auflösung |
|-----|--------------|--------|-----------|
| **Slides** | Folienwechsel | JPEG/PNG | Original (z.B. 1920x1080) |
| **Faces** | Mood-Change | JPEG | 512x512 (Crop) |
| **ROI** | Charts/Code | PNG | Variable (1:1 Crop) |
| **Scene** | Szenenwechsel | JPEG | Thumbnail (640x360) |

### 4.2 Naming Convention

```
keyframes/
├── slide_001.jpg           # Folie 1
├── slide_002_roi_001.png   # ROI aus Folie 2
├── face_speaker1_001.jpg   # Sprecher 1, erstes Keyframe
├── face_speaker1_002.jpg   # Sprecher 1, Mood-Change
└── roi_123.png             # ROI mit Event-ID
```

**Pattern:**
- `{type}_{identifier}_{number}.{ext}`
- `type`: `slide`, `face`, `roi`, `scene`
- `identifier`: Speaker-ID, Slide-Nummer, Event-ID
- `number`: Laufnummer (3-stellig, zero-padded)

### 4.3 Wann Keyframes speichern?

| Situation | Keyframe? | Grund |
|-----------|-----------|-------|
| Folienwechsel | ✅ Immer | Core-Feature |
| Face Mood-Change | ✅ Ja | Semantisch relevant |
| Face pro Segment | ❌ Nein | Redundant (außer bei Stimmungswechsel) |
| ROI (Chart/Code) | ✅ Ja | Wichtige Info |
| Szenenwechsel | ⚠️ Optional | Bei signifikanter Änderung |
| Talking Head (statisch) | ❌ Nein | 1x bei `face.appearance` reicht |

---

## 5. Proxy-Video (Optional)

Für schnelles Scrubbing/Preview.

```
proxy/
└── proxy_360p.mp4   # H.264, 360p, 500 kbps
```

**Eigenschaften:**
- Auflösung: 360p oder 480p
- Codec: H.264 (Kompatibilität)
- Bitrate: 300-500 kbps
- Framerate: 15-30 fps
- Audio: Mono, 64 kbps

**Alternativen:**
- Nur Keyframe-Slideshow (kein Video)
- Link zu Cloud-Video (YouTube/Vimeo)
- Gar kein Proxy (bei Podcasts)

---

## 6. RAG-Integration

SVAF ist optimiert für **Retrieval-Augmented Generation**.

### 6.1 Chunking-Strategien

| Strategie | Chunk-Größe | Use Case |
|-----------|-------------|----------|
| **Segment-basiert** | 1 Transcript-Segment | Frage-Antwort |
| **Event-basiert** | 1 Event | Themen-Suche |
| **Sliding Window** | 30s überlappend | Context-Suche |
| **Topic-basiert** | 1 Topic-Change-Event | Kapitel-Suche |

### 6.2 Metadaten für RAG

```json
{
  "chunk_id": "chunk_001",
  "source": "video.svaf",
  "type": "transcript_segment",
  "start_time": 120.5,
  "end_time": 145.2,
  "speaker": "Max Mustermann",
  "topic": "Container-Struktur",
  "language": "de",
  "text": "SVAF verwendet einen Ordner-Container...",
  "keyframe_url": "keyframes/slide_001.jpg",
  "embedding": [0.123, -0.456, ...]
}
```

### 6.3 Suchindex

Empfohlene Felder für Volltextsuche:
- `transcript[].text` (Volltext)
- `events[].metadata.title` (Folientitel)
- `events[].metadata.ocr_text` (OCR von Slides)
- `events[].metadata.keywords` (Topic-Keywords)

---

## 7. Versionierung & Git

SVAF ist **Git-freundlich** durch:

1. **Ordner-Container** (nicht ZIP)
2. **JSON-Dateien** (textbasiert, diffbar)
3. **Separate Keyframes** (binär, aber wenige Änderungen)
4. **Proxy optional** (kann in `.gitignore`)

### 7.1 `.gitignore` Template

```gitignore
# Optional: Proxy-Videos
proxy/

# Optional: Große Original-Dateien
*.mp4
*.mov

# Build-Artefakte
__pycache__/
*.pyc
```

### 7.2 Versionierungs-Workflow

```bash
# Initial Commit
git init
git add metadata.json events.json transcript_de.json keyframes/
git commit -m "feat: initial SVAF container"

# Transkript-Korrektur
git add transcript_de.json
git commit -m "fix: correct speaker attribution in seg_042"

# Neue Sprache hinzufügen
git add transcript_en.json
git commit -m "feat: add English translation"
```

---

## 8. Erweiterbarkeit

SVAF ist **modular** erweiterbar:

### 8.1 Core vs. Extensions vs. Sidecar

| Kategorie | Beschreibung | Beispiel |
|-----------|--------------|----------|
| **Core** | Pflicht für alle SVAF-Container | `metadata.json`, `events.json` |
| **Extensions** | Standardisierte optionale Features | `identities.json`, `tracks.json` |
| **Sidecar** | Projekt-spezifische Zusatzdaten | `quiz_questions.json`, `sentiment.json` |

### 8.2 Custom Event-Typen

Erweiterungen können eigene Event-Typen definieren:

```json
{
  "event_id": "evt_quiz_001",
  "type": "quiz.question",
  "start_time": 300.0,
  "metadata": {
    "question": "Was ist SVAF?",
    "answers": ["A", "B", "C"],
    "correct": "A"
  }
}
```

### 8.3 Sidecar-Dateien

Beliebige JSON-Dateien im `sidecar/`-Ordner:

```
sidecar/
├── quiz_questions.json
├── sentiment_analysis.json
├── advertising_markers.json
└── custom_tags.json
```

**Regeln:**
- Nicht im Core-Spec definiert
- Können referenzieren: `event_id`, `segment_id`, Timestamps
- Sollten dokumentiert sein (README im Sidecar-Ordner)

---

## 9. Validierung

SVAF-Container müssen folgende Regeln erfüllen:

### 9.1 Pflicht-Dateien

✅ `metadata.json` existiert
✅ `events.json` existiert
✅ Mind. 1 `transcript_XX.json` existiert

### 9.2 Konsistenz-Checks

✅ Alle `keyframe`-Pfade in `events.json` existieren
✅ Alle `identity_id` in `events.json` existieren in `identities.json`
✅ Alle `speaker_id` in `transcript_XX.json` existieren in `identities.json`
✅ `events[].start_time` < `events[].end_time`
✅ Keine überlappenden Events desselben Typs (außer erlaubt)

### 9.3 JSON-Schema

Verfügbar unter `schemas/*.schema.json` (siehe RFC-0002).

---

## 10. Sicherheit & Privacy

### 10.1 Face-Keyframes

**Problem:** Gesichter sind personenbezogene Daten (DSGVO).

**Lösungen:**
1. **Privacy-Mode** in `identities.json`:
   - `public`: Bilder erlaubt
   - `pseudonymous`: Nur mit Einwilligung
   - `anonymous`: Keine Bilder

2. **Redacted Faces**:
   ```json
   {
     "identity_id": "speaker_1",
     "privacy_mode": "redacted",
     "face_keyframes": [],
     "metadata": {
       "face_detection": "disabled_by_user"
     }
   }
   ```

3. **Blur-Option**:
   Keyframes mit Weichzeichner (`keyframes/face_speaker1_001_blurred.jpg`)

### 10.2 OCR & PII

**Warnung:** OCR-Text aus Slides kann sensitive Daten enthalten (z.B. Email-Adressen, Kundendaten).

**Best Practice:**
- `events[].metadata.ocr_text_redacted` für öffentliche Versionen
- PII-Scanner vor Veröffentlichung

### 10.3 Source-Informationen

**Problem:** `metadata.source.original_file` könnte interne Pfade leaken.

**Lösung:**
```json
{
  "source": {
    "type": "video",
    "original_file": "video.mp4",  // Relativ oder Basename
    "original_path_redacted": true
  }
}
```

---

## 11. Performance & Speicherbedarf

### 11.1 Typische Größen

| Inhalt | Dauer | SVAF-Größe | Original-Video |
|--------|-------|------------|----------------|
| Podcast (Audio-only) | 60 min | 5-10 MB | ~50 MB (MP3) |
| Talking Head (statisch) | 30 min | 20-30 MB | ~500 MB (MP4) |
| Vortrag mit Slides | 60 min | 50-100 MB | ~1.5 GB (MP4) |
| Interview (2 Sprecher) | 90 min | 80-150 MB | ~2 GB (MP4) |

**Faktoren:**
- Anzahl Slides (größter Faktor)
- Face-Keyframes (optional)
- Word-level timestamps (2-3x größere Transkripte)
- Proxy-Video (optional, +50-100 MB)

### 11.2 Optimierungen

1. **Keyframe-Kompression:**
   - JPEG Quality 85 (statt 95)
   - WebP statt JPEG (30% kleiner)

2. **Transcript-Kompression:**
   - Weglassen von `words[]` wenn nicht benötigt
   - Gzip-Kompression für JSON-Dateien (außerhalb Container)

3. **Proxy-Video:**
   - Nur wenn UI-Preview benötigt
   - 360p statt 480p
   - H.264 statt H.265 (Kompatibilität)

---

## 12. Implementierungs-Hinweise

### 12.1 Empfohlene Tools

| Task | Tool | Alternativen |
|------|------|--------------|
| **Transkription** | Whisper (large-v3) | AssemblyAI, Deepgram |
| **Slide-Detection** | OpenCV (Diff) | FFmpeg Scene-Detection |
| **Speaker-Diarization** | pyannote.audio | NVIDIA NeMo |
| **Face-Detection** | MediaPipe | OpenCV DNN |
| **OCR** | Tesseract, PaddleOCR | Google Vision API |
| **ROI-Detection** | YOLO (custom) | Manuelle Bbox-Annotation |

### 12.2 Pipeline-Architektur

```
Input (video.mp4)
  │
  ├─> Audio-Extraktion (FFmpeg)
  │     └─> Transkription (Whisper)
  │           └─> Speaker-Diarization (pyannote)
  │
  ├─> Keyframe-Extraktion
  │     ├─> Slide-Detection (OpenCV)
  │     ├─> Face-Detection (MediaPipe)
  │     └─> ROI-Detection (YOLO)
  │
  └─> Event-Generierung
        └─> SVAF-Container schreiben
```

### 12.3 MVP-Scope

**Phase 1** (MVP):
- ✅ Audio-Transkription (Whisper)
- ✅ Slide-Detection (OpenCV Diff)
- ✅ Basic Events (`slide.change`, `topic.change`)
- ✅ JSON-Export

**Phase 2**:
- ⬜ Speaker-Diarization
- ⬜ Face-Tracking
- ⬜ OCR für Slides
- ⬜ ROI-Detection

**Phase 3**:
- ⬜ Multi-Language Transcripts
- ⬜ RAG-Integration (LangChain)
- ⬜ Annotations-UI
- ⬜ Git-Workflow

---

## 13. Offene Fragen & Zukünftige RFCs

### RFC-0002: JSON-Schema
- Vollständige Schema-Definitionen
- Validierungs-Rules
- Test-Suite

### RFC-0003: ROI-Detection
- Automatische Erkennung von Charts/Code
- Manuelle Annotation-Tools
- Bbox-Format

### RFC-0004: Multi-Track Audio
- Separate Audio-Spuren
- Stereo-Tracks
- Background-Music-Separation

### RFC-0005: Streaming-Support
- Live-Transkription
- Inkrementelle Events
- Delta-Updates

### RFC-0006: Komprimierung
- Container-Archivierung (ZIP vs. TAR)
- JSON-Kompression
- Deduplizierung von Keyframes

---

## 14. Änderungshistorie

| Version | Datum | Änderungen |
|---------|-------|------------|
| 0.1 | 2025-01-10 | Initial Draft |
| 0.2 | 2025-01-12 | Hinzufügen von `identities.json` |
| 0.3 | 2025-01-14 | Privacy-Modi, ROI-Events |
| 0.4 | 2025-01-15 | Annotations, RAG-Hinweise, Git-Workflow |

---

## 15. Lizenz & Nutzung

**Spec-Lizenz:** CC-BY-4.0 (Dokumentation frei nutzbar)
**Implementierung:** TBD (vorgeschlagen: MIT oder Apache 2.0)

---

**Kontakt:**
- GitHub: TBD
- Email: TBD
- Discord: TBD

**Mitwirkende:**
- Markus (Konzept & Design)
- Claude Sonnet 4.5 (Co-Autor, Struktur)

---

*Ende RFC SVAF-0001*
