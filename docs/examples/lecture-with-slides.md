# Lecture with Slides Example

A complete example of a university lecture with slide changes and speaker tracking.

## Directory Structure

```
lecture.svaf/
├── metadata.json
├── events.json
├── transcript_de.json
├── identities.json
└── keyframes/
    ├── slide_001.jpg
    ├── slide_002.jpg
    ├── slide_003.jpg
    └── face_prof_001.jpg
```

## metadata.json

```json
{
  "svaf_version": "0.1.0",
  "container_id": "123e4567-e89b-12d3-a456-426614174000",
  "title": "Informatik Vorlesung 03: Datenstrukturen",
  "description": "Einführung in verkettete Listen und Bäume",
  "duration_seconds": 5400,
  "primary_language": "de",
  "languages": ["de"],
  "creation_date": "2025-01-15T14:00:00Z",
  "source": {
    "type": "video",
    "original_file": "lecture_03.mp4",
    "original_duration": 5405,
    "original_resolution": "1920x1080",
    "original_size_bytes": 1800000000
  },
  "authors": [
    {
      "name": "Prof. Dr. Schmidt",
      "role": "creator"
    }
  ],
  "tags": ["informatik", "vorlesung", "datenstrukturen"],
  "license": "CC-BY-NC-4.0"
}
```

## events.json

```json
{
  "events": [
    {
      "event_id": "evt_001",
      "type": "chapter.start",
      "start_time": 0.0,
      "metadata": {
        "chapter_number": 1,
        "title": "Einführung"
      }
    },
    {
      "event_id": "evt_002",
      "type": "face.appearance",
      "start_time": 0.0,
      "end_time": 120.0,
      "identity_id": "prof_1",
      "keyframe": "keyframes/face_prof_001.jpg",
      "metadata": {
        "mood": "neutral"
      }
    },
    {
      "event_id": "evt_003",
      "type": "slide.change",
      "start_time": 120.0,
      "end_time": 480.0,
      "keyframe": "keyframes/slide_001.jpg",
      "metadata": {
        "slide_number": 1,
        "title": "Verkettete Listen",
        "ocr_text": "Verkettete Listen\n- Dynamische Datenstruktur\n- Effizienz: O(1) Insert\n- Speicher: O(n)",
        "confidence": 0.96
      }
    },
    {
      "event_id": "evt_004",
      "type": "topic.change",
      "start_time": 480.0,
      "metadata": {
        "topic": "Implementierung",
        "keywords": ["code", "python", "node"]
      }
    },
    {
      "event_id": "evt_005",
      "type": "slide.change",
      "start_time": 480.0,
      "end_time": 1200.0,
      "keyframe": "keyframes/slide_002.jpg",
      "metadata": {
        "slide_number": 2,
        "title": "Code-Beispiel: Node-Klasse",
        "has_code": true
      }
    },
    {
      "event_id": "evt_006",
      "type": "slide.change",
      "start_time": 1200.0,
      "end_time": 2400.0,
      "keyframe": "keyframes/slide_003.jpg",
      "metadata": {
        "slide_number": 3,
        "title": "Baumstrukturen"
      }
    }
  ]
}
```

## transcript_de.json (excerpt)

```json
{
  "language": "de",
  "format_version": "0.1.0",
  "segments": [
    {
      "segment_id": "seg_001",
      "start_time": 0.0,
      "end_time": 6.2,
      "speaker_id": "prof_1",
      "text": "Guten Tag zu Vorlesung 3. Heute geht es um Datenstrukturen.",
      "confidence": 0.94
    },
    {
      "segment_id": "seg_002",
      "start_time": 6.2,
      "end_time": 12.8,
      "speaker_id": "prof_1",
      "text": "Wir beginnen mit verketteten Listen - eine fundamentale dynamische Struktur.",
      "confidence": 0.91
    },
    {
      "segment_id": "seg_003",
      "start_time": 120.5,
      "end_time": 128.3,
      "speaker_id": "prof_1",
      "text": "Wie Sie auf der Folie sehen, besteht eine verkettete Liste aus Knoten.",
      "confidence": 0.96
    }
  ],
  "metadata": {
    "transcription_engine": "whisper-large-v3",
    "transcription_date": "2025-01-15T16:00:00Z",
    "word_level_timestamps": false
  }
}
```

## identities.json

```json
{
  "identities": [
    {
      "identity_id": "prof_1",
      "type": "person",
      "name": "Prof. Dr. Schmidt",
      "privacy_mode": "public",
      "face_keyframes": [
        "keyframes/face_prof_001.jpg"
      ],
      "metadata": {
        "role": "professor",
        "affiliation": "TU München",
        "bio": "Professor für Algorithmen und Datenstrukturen"
      }
    }
  ]
}
```

## RAG Integration Example

This container can be indexed for RAG with:

```python
chunks = [
    {
        "text": "Verkettete Listen - Dynamische Datenstruktur - Effizienz: O(1) Insert - Speicher: O(n)",
        "type": "slide",
        "slide_number": 1,
        "start_time": 120.0,
        "topic": "Verkettete Listen",
        "image_url": "keyframes/slide_001.jpg"
    },
    {
        "text": "Wie Sie auf der Folie sehen, besteht eine verkettete Liste aus Knoten.",
        "type": "transcript",
        "speaker": "Prof. Dr. Schmidt",
        "start_time": 120.5,
        "slide_context": "Verkettete Listen"
    }
]
```

## Use Cases

- University lecture archives
- Online course platforms
- Student note-taking systems
- Searchable knowledge bases
