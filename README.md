# SVAF - Semantic Video Analysis Format

**Version:** 0.1.0-alpha
**Status:** Draft / RFC Phase

## Was ist SVAF?

SVAF (Semantic Video Analysis Format) ist ein **audio-first, event-basiertes Wissensextraktionsformat** für Videos und Audio-Inhalte. Es speichert nicht das komplette Video, sondern nur:

- **Semantisch relevante Informationen** (Wer sagt wann was?)
- **Schlüsselbilder** (Slides, Gesichter bei Stimmungswechseln, ROI-Frames)
- **Strukturierte Metadaten** (Events, Tracks, Annotations)
- **Mehrsprachige Transkripte** mit Timestamps

## Warum SVAF?

### Probleme bestehender Formate
- **Full-Video-Archivierung**: Teuer, unflexibel, nicht durchsuchbar
- **Klassische Untertitel (SRT/WebVTT)**: Nur Text, keine Semantik
- **Transkripte (TXT/DOCX)**: Kein Timing, keine Speaker-Info
- **Podcast-Metadaten (RSS)**: Keine granularen Events

### SVAF-Ziele
✅ **RAG-tauglich**: Perfekt für KI-Wissensdatenbanken
✅ **Speicher-effizient**: 50-200 MB statt 500 MB - 2 GB
✅ **Durchsuchbar**: Volltextsuche in Transkripten + Event-Queries
✅ **Privacy-aware**: Optionale Face-Keyframes, Pseudonyme
✅ **Versionierbar**: Git-freundlich (Ordner-Container, keine Binär-Blobs)
✅ **Erweiterbar**: Core + Extensions + Sidecar-Dateien

## Anwendungsfälle

| Use Case | Relevanz | Beispiel |
|----------|----------|----------|
| **Podcasts/Interviews** | ⭐⭐⭐⭐⭐ | 3h Interview → Transcript + Themen-Events |
| **Vorlesungen/Talks** | ⭐⭐⭐⭐⭐ | Folien-Extraktion + Speaker-Tracking |
| **Untertitelgenerierung** | ⭐⭐⭐⭐ | Multi-Language Transcripts mit Timecodes |
| **Compliance/Audit** | ⭐⭐⭐⭐ | "Wer hat wann was gesagt?" |
| **Content-Repurposing** | ⭐⭐⭐ | Clips aus Events generieren |

## Quick Start

### 1. SVAF-Container erstellen
```bash
mkdir my-video.svaf
cd my-video.svaf
```

### 2. Minimale Struktur
```
my-video.svaf/
├── metadata.json       # Video-Metadaten
├── events.json         # Event-Timeline
├── transcript_de.json  # Transkript (Deutsch)
└── keyframes/          # Schlüsselbilder
    └── slide_001.jpg
```

### 3. Beispiel: `metadata.json`
```json
{
  "svaf_version": "0.1.0",
  "container_id": "uuid-here",
  "title": "SVAF Einführung",
  "duration_seconds": 3600,
  "primary_language": "de",
  "creation_date": "2025-01-15T10:00:00Z",
  "source": {
    "type": "video",
    "original_file": "video.mp4"
  }
}
```

### 4. Beispiel: `events.json`
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
        "title": "Einführung"
      }
    }
  ]
}
```

## Dokumentation

- **[RFC-0001: Core Specification](docs/rfcs/RFC-0001-core.md)** - Vollständige Spezifikation
- **[Architektur-Übersicht](docs/architecture.md)** - Technische Details
- **[Beispiele](docs/examples/)** - Real-World Use Cases

## Repository-Struktur

```
SVAF/
├── docs/               # Dokumentation
│   ├── rfcs/          # RFC-Dokumente
│   ├── architecture.md
│   └── examples/
├── schemas/           # JSON-Schemas für Validierung
├── src/               # Implementierung (Python/TypeScript)
├── tests/             # Tests
└── README.md
```

## Status & Roadmap

### ✅ Phase 1: Spezifikation (aktuell)
- [x] RFC-0001 v0.4 finalisiert
- [ ] JSON-Schemas definiert
- [ ] Community-Feedback eingeholt

### 🚧 Phase 2: MVP-Implementierung
- [ ] Python-Library für SVAF-Erstellung
- [ ] CLI-Tool: `svaf create video.mp4`
- [ ] Whisper-Integration (Transkription)
- [ ] Slide-Detection (OpenCV)

### 📋 Phase 3: Erweiterte Features
- [ ] Speaker-Diarization
- [ ] Face-Tracking mit Privacy-Modus
- [ ] Multi-Language Support
- [ ] RAG-Integration (LangChain/LlamaIndex)

## Lizenz

**TBD** (vorgeschlagen: MIT oder Apache 2.0)

## Beitragen

Projekt befindet sich in aktiver RFC-Phase. Feedback erwünscht!

Kontakt: [TODO: Issue-Tracker oder Email]

---

**Erstellt:** 2025-01
**Aktualisiert:** 2026-02-02
