> **Veraltet / Outdated:** Dieses Dokument beschreibt noch das Ideal-Format vor dem Reality-first-Umbau. Maßgeblich sind [RFC-0001 v0.5](rfcs/RFC-0001-core.md) und die [JSON-Schemas](../schemas/). Beispiele hier validieren NICHT gegen die aktuellen Schemas.

# SVAF Developer Guide

**Version:** 0.1.0
**Target Audience:** Developers implementing SVAF parsers, generators, and tools

---

## Design Philosophy (Master Prompt for AI)

When working with SVAF, follow these core principles:

### 1. Semantic Relevance over Completeness

**Ask yourself: "Is this information semantically meaningful?"**

✅ **Include:**
- Slide changes (new content)
- Topic changes (structural shifts)
- Speaker changes (new perspective)
- Mood changes in faces (emotional context)
- ROI detection (charts, code, diagrams)

❌ **Exclude:**
- Identical frames (redundancy)
- Camera wobble (technical artifact)
- Background noise (non-semantic)
- Every single frame (waste of storage)

### 2. Audio-First Philosophy

**The primary information source is audio + slides, not video.**

- Video is optional (proxy only)
- Keyframes are cherry-picked (not every frame)
- Transcripts are first-class citizens
- Events structure the timeline

### 3. Git-Friendly Architecture

**SVAF containers must be version-control friendly.**

- Use folder structure (not ZIP/TAR archives)
- Use JSON (not binary formats)
- Separate concerns (one file per concern)
- Make diffs meaningful

### 4. RAG-First Design

**Optimize for retrieval-augmented generation.**

- Chunk-friendly segments
- Rich metadata for filtering
- Multimodal references (text + images)
- Temporal context preservation

### 5. Privacy by Design

**Respect user privacy from the start.**

- Face keyframes are optional
- Privacy modes: public → pseudonymous → anonymous → redacted
- PII detection in OCR text
- Configurable data retention

---

## Core Concepts

### What is "Core" vs "Extension" vs "Sidecar"?

| Category | Definition | Examples | Required? |
|----------|------------|----------|-----------|
| **Core** | Mandatory for all SVAF containers | `metadata.json`, `events.json`, `transcript_XX.json` | ✅ Yes |
| **Extensions** | Standardized optional features | `identities.json`, `tracks.json`, `annotations.json` | ⚠️ Should support |
| **Sidecar** | Project-specific additions | `quiz_questions.json`, `sentiment.json` | ❌ Can ignore |

**Implementation Rule:**
- Your parser MUST understand Core files
- Your parser SHOULD understand Extensions
- Your parser MAY ignore Sidecar files

### Event System: Namespaces and Types

Events use dot-notation: `namespace.action`

**Standard Namespaces:**
- `slide.*` - Presentation slides
- `topic.*` - Content structure
- `face.*` - Facial appearances
- `speaker.*` - Speaker changes
- `roi.*` - Regions of interest
- `chapter.*` - Manual chapters
- `scene.*` - Visual scene changes

**Custom Namespaces:**
Extensions can define new namespaces:
```json
{
  "type": "quiz.question",
  "type": "ad.break",
  "type": "music.start"
}
```

**Collision Avoidance:**
Use vendor prefixes for custom namespaces:
```json
{
  "type": "acme.custom_event"
}
```

---

## Implementation Guidelines

### Parsing SVAF Containers

**Step 1: Validate Container**
```python
def validate_svaf_container(path):
    required = ["metadata.json", "events.json"]
    for file in required:
        if not os.path.exists(os.path.join(path, file)):
            raise ValueError(f"Missing required file: {file}")

    # Check for at least one transcript
    transcripts = glob.glob(os.path.join(path, "transcript_*.json"))
    if not transcripts:
        raise ValueError("No transcript files found")
```

**Step 2: Load Core Files**
```python
def load_svaf_container(path):
    with open(os.path.join(path, "metadata.json")) as f:
        metadata = json.load(f)

    with open(os.path.join(path, "events.json")) as f:
        events = json.load(f)

    transcripts = {}
    for transcript_file in glob.glob(os.path.join(path, "transcript_*.json")):
        lang = transcript_file.split("_")[1].split(".")[0]
        with open(transcript_file) as f:
            transcripts[lang] = json.load(f)

    return SVAFContainer(metadata, events, transcripts)
```

**Step 3: Verify Consistency**
```python
def verify_consistency(container):
    # Check all keyframe paths exist
    for event in container.events["events"]:
        if "keyframe" in event:
            path = os.path.join(container.path, event["keyframe"])
            if not os.path.exists(path):
                raise ValueError(f"Keyframe not found: {path}")

    # Check all identity_id references exist
    if container.identities:
        identity_ids = {i["identity_id"] for i in container.identities["identities"]}
        for event in container.events["events"]:
            if "identity_id" in event:
                if event["identity_id"] not in identity_ids:
                    raise ValueError(f"Unknown identity: {event['identity_id']}")
```

### Generating SVAF Containers

**Pipeline Architecture:**
```
Video/Audio Input
    ↓
[Audio Extraction] → FFmpeg
    ↓
[Transcription] → Whisper/AssemblyAI
    ↓
[Diarization] → pyannote.audio
    ↓
[Slide Detection] → OpenCV (frame diff)
    ↓
[OCR] → Tesseract/PaddleOCR
    ↓
[Event Generation] → Merge all sources
    ↓
[SVAF Writer] → JSON output
```

**Example Implementation:**
```python
class SVAFBuilder:
    def __init__(self, source_file):
        self.source = source_file
        self.container_path = None
        self.metadata = {}
        self.events = []
        self.transcripts = {}

    def extract_audio(self):
        # Use FFmpeg to extract audio
        pass

    def transcribe(self, language="auto"):
        # Use Whisper for transcription
        pass

    def detect_slides(self, threshold=0.8):
        # Use OpenCV for slide detection
        pass

    def diarize_speakers(self):
        # Use pyannote for speaker diarization
        pass

    def generate_events(self):
        # Merge all sources into events timeline
        pass

    def save(self, output_path):
        # Write SVAF container
        os.makedirs(output_path, exist_ok=True)

        with open(os.path.join(output_path, "metadata.json"), "w") as f:
            json.dump(self.metadata, f, indent=2)

        with open(os.path.join(output_path, "events.json"), "w") as f:
            json.dump({"events": self.events}, f, indent=2)

        for lang, transcript in self.transcripts.items():
            with open(os.path.join(output_path, f"transcript_{lang}.json"), "w") as f:
                json.dump(transcript, f, indent=2)
```

---

## Testing Strategy

### Unit Tests

Test individual components:
```python
def test_metadata_validation():
    metadata = load_metadata("test_container/metadata.json")
    assert metadata["svaf_version"] == "0.1.0"
    assert "container_id" in metadata
    assert metadata["duration_seconds"] > 0

def test_event_timestamps():
    events = load_events("test_container/events.json")
    for event in events["events"]:
        if "end_time" in event:
            assert event["start_time"] < event["end_time"]

def test_transcript_segments():
    transcript = load_transcript("test_container/transcript_en.json")
    for segment in transcript["segments"]:
        assert segment["start_time"] < segment["end_time"]
        assert len(segment["text"]) > 0
```

### Integration Tests

Test full pipelines:
```python
def test_full_pipeline():
    builder = SVAFBuilder("test_video.mp4")
    builder.extract_audio()
    builder.transcribe(language="en")
    builder.detect_slides()
    builder.save("test_output.svaf")

    # Validate output
    container = load_svaf_container("test_output.svaf")
    assert len(container.events["events"]) > 0
    assert len(container.transcripts["en"]["segments"]) > 0
```

### Test Fixtures

Maintain standard test containers:
```
tests/fixtures/
├── minimal.svaf/           # Bare minimum
├── podcast.svaf/           # Audio-only
├── lecture.svaf/           # Slides + speaker
├── interview.svaf/         # Multi-speaker
└── invalid/                # Invalid containers for error testing
```

---

## Performance Optimization

### JSON Size Reduction

**Problem:** Large containers (5000+ events) can be slow to parse.

**Solutions:**

1. **Lazy Loading**
   - Load only `metadata.json` initially
   - Load `events.json` on demand
   - Stream large transcripts

2. **Compression**
   - Gzip JSON files for distribution
   - Use shorter field names (trade-off: readability)
   - Remove whitespace in production builds

3. **Indexing**
   - Create `index/events.idx.json` for fast lookups
   - Pre-compute common queries

### Keyframe Storage

**Problem:** Many keyframes consume disk space.

**Solutions:**

1. **Deduplication**
   - Use perceptual hashing (pHash)
   - Reference duplicate slides

2. **Format Optimization**
   - Use WebP instead of JPEG (30% smaller)
   - Optimize JPEG quality (85% instead of 95%)
   - Use PNG only for ROIs with text

3. **Progressive Loading**
   - Store thumbnails separately
   - Load full-resolution on demand

---

## Security Considerations

### Privacy

**Face Keyframes:**
- Always respect `privacy_mode` in `identities.json`
- Implement face blurring for `redacted` mode
- Never store faces without consent

**PII in OCR:**
- Scan OCR text for emails, phone numbers
- Provide `ocr_text_redacted` option
- Warn users before publishing

**Source Paths:**
- Redact internal file paths in `metadata.source`
- Use relative paths only
- Sanitize filenames

### Validation

**JSON Schema:**
- Always validate against schemas before writing
- Reject malformed containers
- Provide clear error messages

**Path Traversal:**
- Sanitize all file paths
- Prevent `../` attacks
- Validate keyframe paths

---

## Best Practices

### DO:
✅ Use semantic event types (not generic markers)
✅ Include confidence scores for machine-generated data
✅ Provide word-level timestamps for RAG use cases
✅ Document custom event types in README
✅ Test with multiple languages
✅ Version your container format

### DON'T:
❌ Store full videos in container (use proxy/ or external links)
❌ Create events for every frame
❌ Duplicate identical keyframes
❌ Mix languages in single transcript (use separate files)
❌ Hardcode absolute paths
❌ Skip validation

---

## Roadmap & Future RFCs

### Planned Specifications

- **RFC-0002:** JSON Schema validation suite
- **RFC-0003:** ROI detection and annotation
- **RFC-0004:** Multi-track audio support
- **RFC-0005:** Streaming and live transcription
- **RFC-0006:** Container compression and archiving

### Community Contributions

See [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.

---

## Resources

- **RFC-0001:** [Core Specification](rfcs/RFC-0001-core.md)
- **Architecture:** [Architecture Overview](architecture.md)
- **Examples:** [Example Containers](examples/)
- **Schemas:** [JSON Schemas](../schemas/)

---

**Questions?** Open an issue on GitHub or join our Discord.
