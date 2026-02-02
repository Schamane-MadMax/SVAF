# Minimal SVAF Example

This is the absolute minimum required for a valid SVAF container.

## Directory Structure

```
minimal-podcast.svaf/
├── metadata.json
├── events.json
└── transcript_en.json
```

## metadata.json

```json
{
  "svaf_version": "0.1.0",
  "container_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "My First Podcast Episode",
  "description": "A simple podcast about SVAF",
  "duration_seconds": 600,
  "primary_language": "en",
  "creation_date": "2025-01-15T10:00:00Z",
  "source": {
    "type": "audio",
    "original_file": "podcast.mp3"
  }
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
        "title": "Introduction"
      }
    },
    {
      "event_id": "evt_002",
      "type": "topic.change",
      "start_time": 120.0,
      "metadata": {
        "topic": "SVAF Basics"
      }
    }
  ]
}
```

## transcript_en.json

```json
{
  "language": "en",
  "format_version": "0.1.0",
  "segments": [
    {
      "segment_id": "seg_001",
      "start_time": 0.0,
      "end_time": 5.8,
      "text": "Welcome to my podcast about SVAF, the Semantic Video Analysis Format.",
      "confidence": 0.95
    },
    {
      "segment_id": "seg_002",
      "start_time": 5.8,
      "end_time": 12.4,
      "text": "Today we'll explore how SVAF revolutionizes video and audio archiving.",
      "confidence": 0.93
    }
  ],
  "metadata": {
    "transcription_engine": "whisper-large-v3",
    "transcription_date": "2025-01-15T12:00:00Z",
    "word_level_timestamps": false
  }
}
```

## Validation

This container is valid because it contains:
- ✅ `metadata.json` with required fields
- ✅ `events.json` with at least one event
- ✅ `transcript_XX.json` with at least one segment

## Use Case

This minimal example is perfect for:
- Audio-only podcasts
- Simple interviews
- Voice memos
- Quick prototypes
