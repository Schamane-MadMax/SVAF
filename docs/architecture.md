> **Veraltet / Outdated:** Dieses Dokument beschreibt noch das Ideal-Format vor dem Reality-first-Umbau. Maßgeblich sind [RFC-0001 v0.5](rfcs/RFC-0001-core.md) und die [JSON-Schemas](../schemas/). Beispiele hier validieren NICHT gegen die aktuellen Schemas.

# SVAF Architecture Overview

**Version:** 0.1.0
**Last Updated:** 2026-02-02

---

## 1. Design Philosophy

SVAF folgt diesen Kernprinzipien:

### 1.1 Audio-First, Not Video-First
- **Primär:** Transkripte + Events + Keyframes
- **Sekundär:** Proxy-Video (optional)
- **Grund:** 90% der Information liegt in Audio + Slides

### 1.2 Event-Based Timeline
- Statt "kontinuierlicher Stream" → "diskrete Events"
- Jedes Event hat Typ, Timestamp, Metadaten
- Erweiterbar durch Custom-Types

### 1.3 Semantic Relevance
**Was ist semantisch relevant?**

✅ **JA:**
- Folienwechsel (neuer Inhalt)
- Themenwechsel (neues Kapitel)
- Sprecherwechsel (neue Perspektive)
- Stimmungswechsel im Gesicht (Emotion ändert sich)
- ROI-Detection (Chart/Code wird gezeigt)

❌ **NEIN:**
- Jedes Frame des Videos
- Identische Face-Frames pro Segment
- Redundante Slides (gleicher Inhalt)
- Kamerawackeln (technisches Artefakt)

### 1.4 Git-Friendly
- Ordner-Container (nicht ZIP/TAR)
- JSON-Dateien (textbasiert, diffbar)
- Separate Keyframes (binär, aber selten geändert)

### 1.5 RAG-Optimized
- Chunking-freundlich (Segmente, Events)
- Metadaten für Retrieval (Speaker, Topic, Language)
- Referenzen zu Keyframes (für multimodale RAG)

---

## 2. Container-Architektur

### 2.1 Ordner-basiert (nicht Archive)

**Warum kein ZIP/TAR?**
- ❌ Git kann Archive nicht diffen
- ❌ Partielle Updates unmöglich
- ❌ Transparenz fehlt (binärer Blob)

**Vorteile Ordner:**
- ✅ Git-freundlich (Text-Dateien diffbar)
- ✅ Partielle Updates (nur `events.json` ändern)
- ✅ Transparenz (alle Dateien sichtbar)
- ✅ Erweiterbar (neue Dateien hinzufügen)

**Für Distribution:**
- Ordner → ZIP/TAR erst bei Export
- Oder: Git-Repository als "natives Format"

### 2.2 Core vs. Extensions vs. Sidecar

```
┌─────────────────────────────────────────┐
│           CORE (Pflicht)                │
│  metadata.json, events.json,            │
│  transcript_XX.json                     │
└─────────────────────────────────────────┘
              │
              ├─> EXTENSIONS (Optional, aber standardisiert)
              │   identities.json, tracks.json, annotations.json
              │
              └─> SIDECAR (Projekt-spezifisch)
                  quiz_questions.json, sentiment.json, ...
```

**Regeln:**
- **Core:** Jede SVAF-Implementierung MUSS diese verstehen
- **Extensions:** SOLLTE verstanden werden, aber optional
- **Sidecar:** KANN ignoriert werden

---

## 3. Event-System

### 3.1 Event-Struktur

```json
{
  "event_id": "unique-id",
  "type": "namespace.action",
  "start_time": 120.5,
  "end_time": 245.0,
  "keyframe": "path/to/image.jpg",
  "identity_id": "speaker_1",
  "metadata": { /* type-specific */ }
}
```

### 3.2 Event-Typen (Namespaces)

| Namespace | Beschreibung | Beispiele |
|-----------|--------------|-----------|
| `slide.*` | Folien-Events | `slide.change`, `slide.animation` |
| `topic.*` | Inhaltliche Struktur | `topic.change`, `topic.end` |
| `face.*` | Gesichts-Events | `face.appearance`, `face.mood_change` |
| `speaker.*` | Sprecher-Events | `speaker.change`, `speaker.pause` |
| `roi.*` | Region of Interest | `roi.detected`, `roi.highlight` |
| `chapter.*` | Manuelle Struktur | `chapter.start`, `chapter.end` |
| `scene.*` | Visuelle Änderungen | `scene.change`, `scene.cut` |

**Custom Namespaces:**
- Extensions können eigene definieren (z.B. `quiz.*`, `ad.*`)
- Empfohlen: Namespace-Prefix für Kollisionsvermeidung

### 3.3 Event-Überlappungen

**Erlaubt:**
- `topic.change` + `slide.change` zur gleichen Zeit
- `speaker.change` + `face.appearance` zur gleichen Zeit

**Nicht erlaubt:**
- Zwei `slide.change` Events zur gleichen Zeit
- Zwei `speaker.change` Events für denselben Speaker

---

## 4. Transcript-Architektur

### 4.1 Multi-Language Support

**Option 1: Separate Dateien** (empfohlen)
```
transcript_de.json
transcript_en.json
transcript_fr.json
```

**Option 2: Language-Tags in Segmenten**
```json
{
  "segments": [
    {"text": "Guten Tag", "language": "de"},
    {"text": "Hello", "language": "en"}
  ]
}
```

**Wann Option 2?**
- Code-Switching (Sprache wechselt innerhalb Segment)
- Mehrsprachige Sprecher

### 4.2 Word-Level Timestamps

**Trade-off:**
- ✅ Bessere RAG-Suche (präzise Timestamps)
- ✅ Synchronisation mit Untertiteln
- ❌ 2-3x größere Dateien
- ❌ Mehr Rechenaufwand bei Transkription

**Empfehlung:**
- MVP: Nur Segment-Level
- Production: Word-Level für RAG-Use-Cases

### 4.3 Speaker-Diarization

**Pipeline:**
```
Audio → Transkription (Whisper) → Diarization (pyannote)
  ↓
Segmente mit speaker_id
  ↓
Referenz zu identities.json
```

**Herausforderungen:**
- Overlapping Speech (2 Sprecher gleichzeitig)
- Unbekannte Sprecher (Guest-Appearances)
- Echo/Background-Noise

**Lösung:**
```json
{
  "speaker_id": "unknown_1",
  "metadata": {
    "speaker_confidence": 0.65,
    "overlap_detected": true
  }
}
```

---

## 5. Keyframe-Strategie

### 5.1 Wann Keyframes extrahieren?

| Event-Typ | Keyframe-Rule | Grund |
|-----------|---------------|-------|
| `slide.change` | ✅ Immer | Hauptinhalt |
| `face.appearance` | ✅ Einmal pro Speaker | Identifikation |
| `face.mood_change` | ✅ Ja | Semantisch relevant |
| `face` (jedes Segment) | ❌ Nein | Redundant |
| `roi.detected` | ✅ Ja | Wichtige Detail-Info |
| `scene.change` | ⚠️ Optional | Nur bei signifikanter Änderung |

### 5.2 Keyframe-Formate

| Typ | Format | Auflösung | Quality | Grund |
|-----|--------|-----------|---------|-------|
| Slides | JPEG/PNG | Original (1920x1080) | 85% | Lesbarkeit |
| Faces | JPEG | 512x512 (crop) | 90% | Details wichtig |
| ROI | PNG | Variable (1:1 crop) | Lossless | Charts/Code |
| Thumbnails | JPEG | 320x180 | 75% | Preview |

### 5.3 Deduplizierung

**Problem:** Gleiche Folie mehrfach im Video.

**Lösung 1: Perceptual Hashing**
```python
import imagehash
hash1 = imagehash.phash(Image.open("slide_001.jpg"))
hash2 = imagehash.phash(Image.open("slide_002.jpg"))
if hash1 - hash2 < 5:  # Ähnlich
    # Referenziere statt duplizieren
```

**Lösung 2: Event-Referenzen**
```json
{
  "event_id": "evt_042",
  "type": "slide.change",
  "keyframe": "keyframes/slide_001.jpg",  // Referenz zu früherem Event
  "metadata": {
    "duplicate_of": "evt_001"
  }
}
```

---

## 6. Identity-Management

### 6.1 Privacy-Modi

```
public → pseudonymous → anonymous → redacted
  ↓          ↓              ↓           ↓
Name+Bild   Pseudo+Bild   Nur ID    Keine Daten
```

**Use Cases:**
- **Public:** Öffentliche Personen (Professoren, Influencer)
- **Pseudonymous:** Interne Meetings (mit Einwilligung)
- **Anonymous:** Compliance (nur Speaker-ID)
- **Redacted:** Nachträgliche Löschung (DSGVO)

### 6.2 Face vs. Speaker

**Wichtig:** Face ≠ Speaker!

**Beispiele:**
- **Speaker ohne Face:** Podcast (nur Audio)
- **Face ohne Speaker:** Stummfilm, B-Roll-Footage
- **Face + Speaker verbunden:** Standard-Interview

**Implementierung:**
```json
{
  "identity_id": "person_1",
  "type": "person",  // Übergeordnet
  "speaker_id": "speaker_1",
  "face_id": "face_1",
  "linked": true
}
```

---

## 7. Annotations

### 7.1 Human vs. Machine

```json
{
  "author_type": "human",  // oder "machine"
  "author_id": "user_123",  // oder "gpt-4"
  "confidence": 1.0  // Menschen = 1.0, KI = 0.0-1.0
}
```

**Use Cases:**
- **Human:** Transkript-Korrekturen, Tags, Kommentare
- **Machine:** Auto-Summaries, Sentiment, Topics

### 7.2 Target-Typen

| Target | Beschreibung | Beispiel |
|--------|--------------|----------|
| `transcript` | Segment-ID | Korrektur von Transkript |
| `event` | Event-ID | Kommentar zu Folie |
| `timerange` | Start-/End-Time | Tag für Abschnitt |
| `keyframe` | Keyframe-Path | ROI-Annotation |
| `container` | Gesamtes Video | Rating, Kategorie |

### 7.3 Versionierung

**Problem:** Annotations ändern sich über Zeit.

**Lösung: Git-History**
```bash
git log annotations.json  # Historie sehen
git diff HEAD~1 annotations.json  # Änderungen
```

**Alternative: Embedded History**
```json
{
  "annotation_id": "anno_001",
  "version": 2,
  "history": [
    {"version": 1, "content": "alte Annotation", "timestamp": "..."},
    {"version": 2, "content": "neue Annotation", "timestamp": "..."}
  ]
}
```

---

## 8. RAG-Integration

### 8.1 Chunking-Strategien

**Strategie 1: Segment-basiert** (einfach)
```python
for segment in transcript["segments"]:
    chunk = {
        "text": segment["text"],
        "start_time": segment["start_time"],
        "speaker": segment["speaker_id"],
        "metadata": {...}
    }
    add_to_vector_db(chunk)
```

**Strategie 2: Event-basiert** (semantisch)
```python
for event in events["events"]:
    # Text von allen Segmenten im Event-Zeitraum
    text = get_transcript_text(event["start_time"], event["end_time"])
    chunk = {
        "text": text,
        "event_type": event["type"],
        "keyframe": event.get("keyframe"),
        "metadata": event["metadata"]
    }
    add_to_vector_db(chunk)
```

**Strategie 3: Hybrid** (empfohlen)
- Events als "primäre Chunks"
- Segmente als "fallback" (falls kein passendes Event)

### 8.2 Metadaten für Retrieval

```json
{
  "chunk_id": "chunk_001",
  "source": "video.svaf",
  "type": "event",
  "event_type": "slide.change",
  "start_time": 120.5,
  "end_time": 245.0,
  "speaker": "Max Mustermann",
  "topic": "Container-Struktur",
  "language": "de",
  "text": "SVAF verwendet einen Ordner-Container...",
  "keyframe_url": "keyframes/slide_001.jpg",
  "slide_number": 1
}
```

**Filter-Queries:**
- "Nur Sprecher X": `metadata.speaker == "Max Mustermann"`
- "Nur Slides": `metadata.event_type == "slide.change"`
- "Nur Deutsch": `metadata.language == "de"`
- "Zeitraum": `metadata.start_time BETWEEN 100 AND 200`

### 8.3 Multimodal RAG

**Text + Bild:**
```python
# Text-Embedding
text_embedding = embed_text(chunk["text"])

# Image-Embedding (CLIP)
if chunk["keyframe"]:
    image_embedding = embed_image(chunk["keyframe"])

    # Combined-Embedding
    combined = concat([text_embedding, image_embedding])
```

**Use Case:**
- Nutzer fragt: "Zeige mir alle Folien über Architektur"
- System sucht: Text-Match + Bild-Match (Diagramme erkannt)

---

## 9. Performance-Optimierung

### 9.1 JSON-Größe reduzieren

**Ohne Optimierung:**
```json
{
  "segment_id": "segment_001",
  "start_time": 120.5,
  "end_time": 125.2,
  "text": "Hallo Welt"
}
```

**Mit Optimierung:**
```json
{
  "id": "s001",
  "t": [120.5, 125.2],
  "txt": "Hallo Welt"
}
```

**Trade-off:**
- ✅ 30-40% kleiner
- ❌ Schlechter lesbar
- ❌ Nicht selbstdokumentierend

**Empfehlung:** Nur bei sehr großen Containern (>1000 Segmente)

### 9.2 Lazy Loading

**Problem:** Große Container (5000+ Events) langsam zu laden.

**Lösung: Manifest-Datei**
```json
// manifest.json
{
  "svaf_version": "0.1.0",
  "files": [
    {"path": "metadata.json", "size": 1024},
    {"path": "events.json", "size": 524288, "lazy": true},
    {"path": "transcript_de.json", "size": 1048576, "lazy": true}
  ]
}
```

**UI-Workflow:**
1. Lade nur `manifest.json` + `metadata.json`
2. Zeige Preview/Übersicht
3. Lade `events.json` bei Bedarf (User scrollt)

### 9.3 Index-Dateien

**Für schnelle Suche:**
```json
// index/events.idx.json
{
  "slide.change": ["evt_001", "evt_005", "evt_012"],
  "topic.change": ["evt_003", "evt_007"],
  "speaker_1": ["evt_001", "evt_002", "evt_003"]
}
```

**Query:**
```python
# Finde alle Slide-Events von Speaker 1
slide_events = index["slide.change"]
speaker_events = index["speaker_1"]
result = set(slide_events) & set(speaker_events)
```

---

## 10. Implementierungs-Patterns

### 10.1 Builder-Pattern

```python
builder = SVAFBuilder("video.mp4")
builder.extract_audio()
builder.transcribe(language="de")
builder.detect_slides()
builder.diarize_speakers()
builder.save("output.svaf")
```

### 10.2 Pipeline-Pattern

```python
pipeline = Pipeline([
    AudioExtractor(),
    Transcriber(model="whisper-large-v3"),
    SlideDetector(threshold=0.8),
    SpeakerDiarizer(),
    EventGenerator(),
    SVAFWriter()
])
pipeline.run("video.mp4", output="output.svaf")
```

### 10.3 Plugin-System

```python
# Custom-Plugin
class QuizDetector(SVAFPlugin):
    def process(self, container):
        # Erkenne Quiz-Questions in Transcript
        for segment in container.transcript:
            if "?" in segment["text"]:
                container.add_event({
                    "type": "quiz.question",
                    "start_time": segment["start_time"],
                    "text": segment["text"]
                })

# Registrieren
pipeline.add_plugin(QuizDetector())
```

---

## 11. Testing-Strategie

### 11.1 Unit-Tests

- JSON-Schema-Validierung
- Event-Konsistenz-Checks
- Timestamp-Validierung
- Referenz-Integrität (IDs)

### 11.2 Integration-Tests

- Full-Pipeline (Video → SVAF)
- Keyframe-Extraktion
- Transkription-Qualität
- RAG-Integration

### 11.3 Test-Fixtures

```
tests/fixtures/
├── minimal.svaf/           # Minimale Container
├── podcast.svaf/           # Audio-only
├── lecture.svaf/           # Slides + Speaker
└── interview.svaf/         # Multi-Speaker
```

---

## 12. Migration & Kompatibilität

### 12.1 Version-Migration

**v0.1.0 → v0.2.0:**
```python
def migrate_v1_to_v2(container_path):
    # Ändere `svaf_version` in metadata.json
    # Füge neue Pflichtfelder hinzu
    # Migriere alte Event-Typen
```

**Backward-Compatibility:**
- Parser MUSS alte Versionen verstehen
- Writer SOLLTE neueste Version schreiben

### 12.2 Import aus anderen Formaten

| Format | Import-Strategie |
|--------|------------------|
| **SRT/WebVTT** | → `transcript.json` (ohne Speaker) |
| **YouTube-XML** | → `transcript.json` + `metadata.json` |
| **Podcast-RSS** | → `metadata.json` (Show-Notes) |
| **ELAN (.eaf)** | → `annotations.json` |

---

## 13. Deployment-Szenarien

### 13.1 Local-First

```bash
# CLI-Tool
svaf create video.mp4 -o output.svaf
svaf validate output.svaf
svaf export output.svaf --format=zip
```

### 13.2 Cloud-Service

```python
# API-Endpoint
POST /api/v1/svaf/create
{
  "video_url": "https://...",
  "options": {
    "language": "de",
    "detect_faces": false
  }
}

# Response
{
  "container_id": "uuid",
  "status": "processing",
  "download_url": "https://.../output.svaf.zip"
}
```

### 13.3 Batch-Processing

```bash
# Ordner mit Videos
for video in videos/*.mp4; do
  svaf create "$video" -o "output/$(basename $video .mp4).svaf"
done
```

---

## 14. Future-Proofing

### 14.1 Erweiterbarkeit

- Neue Event-Typen via Extensions
- Neue Metadaten-Felder via `metadata.*`
- Neue Dateien via `sidecar/`

### 14.2 Breaking Changes vermeiden

- Pflichtfelder NIEMALS entfernen
- Neue Pflichtfelder → optionale Extension
- Deprecation-Warnings in Parser

### 14.3 Community-Driven

- RFCs für große Änderungen
- GitHub-Issues für Feature-Requests
- Voting-System für Prioritäten

---

**Ende Architecture Overview**
