> **Veraltet / Outdated:** Dieses Dokument beschreibt noch das Ideal-Format vor dem Reality-first-Umbau. Maßgeblich sind [RFC-0001 v0.5](rfcs/RFC-0001-core.md) und die [JSON-Schemas](../schemas/). Beispiele hier validieren NICHT gegen die aktuellen Schemas.

# Getting Started with SVAF

## Installation

### From PyPI (when published)

```bash
pip install -e .  # aus dem Repo-Checkout; kein PyPI-Paket veroeffentlicht
```

### From Source

```bash
git clone https://github.com/svaf-project/SVAF.git
cd svaf
pip install -e .
```

### With Optional Dependencies

```bash
# CLI tools with rich output
pip install -e ".[cli]"

# Processing capabilities
pip install -e ".[processing]"

# Transcription with Whisper
pip install -e ".[transcription]"

# All features
pip install -e ".[all]"
```

## Quick Start

### 1. Parse an Existing Container

```python
from svaf import SVAFParser

parser = SVAFParser()
container = parser.parse("my-video.svaf")

# Access metadata
print(container.metadata.title)
print(f"Duration: {container.metadata.duration_seconds}s")

# Access transcript
transcript = container.get_transcript()
for segment in transcript.segments:
    print(f"[{segment.start_time}s] {segment.text}")

# Access events
for event in container.events.events:
    print(f"{event.type} at {event.start_time}s")
```

### 2. Build a New Container

```python
from svaf import SVAFBuilder

# Create builder with fluent API
container_path = (
    SVAFBuilder()
    .set_metadata(
        title="My Podcast Episode",
        duration_seconds=3600,
        primary_language="en",
        description="Episode about SVAF"
    )
    .add_author(
        name="John Doe",
        role="creator",
        email="john@example.com"
    )
    .add_identity(
        identity_id="speaker_01",
        type="speaker",
        name="John Doe",
        role="host"
    )
    .add_transcript_segment(
        language="en",
        segment_id="seg_001",
        start_time=0.0,
        end_time=5.2,
        text="Welcome to my podcast!",
        speaker_id="speaker_01",
        confidence=0.98
    )
    .add_event(
        event_id="evt_001",
        type="topic.start",
        start_time=0.0,
        metadata={"title": "Introduction"}
    )
    .save("my-podcast.svaf")
)

print(f"Container saved to: {container_path}")
```

### 3. Validate a Container

```python
from svaf import SVAFValidator
from svaf.validator import ValidationLevel

validator = SVAFValidator(
    level=ValidationLevel.CONSISTENCY,
    strict=True
)

result = validator.validate("my-video.svaf")

if result.is_valid:
    print("✓ Container is valid!")
else:
    result.print_report()
```

## CLI Usage

### Validate a Container

```bash
# Basic validation
svaf validate my-video.svaf

# Semantic validation (most thorough)
svaf validate my-video.svaf --level=semantic

# JSON output
svaf validate my-video.svaf --format=json
```

### View Container Info

```bash
# Basic info
svaf info my-video.svaf

# Detailed info with events
svaf info my-video.svaf --detailed

# JSON output
svaf info my-video.svaf --format=json
```

### Export Container

```bash
# Export as ZIP archive
svaf export my-video.svaf --format=zip -o archive.zip

# Export as SRT subtitles
svaf export my-video.svaf --format=srt -o subtitles.srt

# Export transcript as Markdown
svaf export my-video.svaf --format=markdown -o transcript.md
```

## Container Structure

A basic SVAF container looks like this:

```
my-video.svaf/
├── metadata.json          # Required: Container metadata
├── events.json            # Optional: Event timeline
├── transcript_en.json     # Optional: English transcript
├── transcript_de.json     # Optional: German transcript
├── identities.json        # Optional: Speaker/face identities
├── tracks.json            # Optional: Audio/video track info
├── annotations.json       # Optional: Annotations
└── keyframes/             # Optional: Keyframe images
    ├── slide_001.jpg
    ├── slide_002.jpg
    └── face_001.jpg
```

### Minimum Required Files

A valid SVAF container needs only `metadata.json`:

```json
{
  "svaf_version": "0.1.0",
  "container_id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "My Video",
  "duration_seconds": 300.0,
  "primary_language": "en",
  "creation_date": "2026-02-02T10:00:00Z"
}
```

## Common Use Cases

### Podcast Archival

```python
builder = (
    SVAFBuilder()
    .set_metadata(
        title="Podcast Episode #42",
        duration_seconds=3600,
        primary_language="en"
    )
    .add_source(
        source_type="podcast",
        original_file="episode_42.mp3"
    )
    .add_identity(
        identity_id="host",
        type="speaker",
        name="Host Name"
    )
    .add_identity(
        identity_id="guest",
        type="speaker",
        name="Guest Name"
    )
)

# Add transcript segments
# (from Whisper or other transcription service)
for segment in transcription_results:
    builder.add_transcript_segment(
        language="en",
        segment_id=segment["id"],
        start_time=segment["start"],
        end_time=segment["end"],
        text=segment["text"],
        speaker_id=segment["speaker"],
        confidence=segment["confidence"]
    )

builder.save("episode_42.svaf")
```

### Lecture with Slides

```python
builder = (
    SVAFBuilder()
    .set_metadata(
        title="Machine Learning 101",
        duration_seconds=5400,  # 90 minutes
        primary_language="en"
    )
)

# Add slide change events
for i, slide_time in enumerate(slide_change_times):
    builder.add_event(
        event_id=f"slide_{i:03d}",
        type="slide.change",
        start_time=slide_time,
        keyframe=f"keyframes/slide_{i:03d}.jpg",
        metadata={"slide_number": i + 1}
    )

# Add keyframe images
for i, slide_image in enumerate(slide_images):
    builder.add_keyframe(
        relative_path=f"keyframes/slide_{i:03d}.jpg",
        content=slide_image
    )

builder.save("ml101_lecture.svaf")
```

### RAG Integration

```python
from svaf import SVAFParser

# Parse container
parser = SVAFParser()
container = parser.parse("my-video.svaf")

# Extract chunks for RAG
chunks = []
for lang, transcript in container.transcripts.items():
    for segment in transcript.segments:
        # Create chunk with context
        chunk = {
            "text": segment.text,
            "metadata": {
                "source": container.metadata.title,
                "timestamp": segment.start_time,
                "speaker": segment.speaker_id,
                "language": lang,
                "container_id": str(container.metadata.container_id)
            }
        }
        chunks.append(chunk)

# Add to vector database
# vector_db.add(chunks)
```

## Next Steps

- Read the [API Documentation](api-reference.md)
- Explore [Examples](examples/)
- Learn about [Event Types](event-types.md)
- See [Best Practices](best-practices.md)
- Check the [RFC-0001 Specification](rfcs/RFC-0001-core.md)
