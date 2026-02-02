# SVAF Implementation

**Status:** Placeholder - Implementation coming in Phase 2

## Planned Structure

```
src/
├── python/              # Python library
│   ├── svaf/
│   │   ├── __init__.py
│   │   ├── builder.py   # SVAFBuilder class
│   │   ├── parser.py    # Container parsing
│   │   ├── validator.py # Schema validation
│   │   └── rag.py       # RAG integration helpers
│   └── setup.py
├── typescript/          # TypeScript library
│   ├── src/
│   │   ├── builder.ts
│   │   ├── parser.ts
│   │   └── validator.ts
│   └── package.json
└── cli/                 # Command-line tools
    └── svaf-cli.py      # CLI: svaf create/validate/export
```

## MVP Scope (Phase 2)

### Python Library
- [ ] Container creation (`SVAFBuilder`)
- [ ] Container parsing (`SVAFParser`)
- [ ] JSON Schema validation
- [ ] Whisper integration (transcription)
- [ ] OpenCV slide detection
- [ ] Basic event generation

### CLI Tool
- [ ] `svaf create video.mp4 -o output.svaf`
- [ ] `svaf validate container.svaf`
- [ ] `svaf export container.svaf --format=zip`
- [ ] `svaf info container.svaf` (statistics)

### Integration Targets
- [ ] FFmpeg (audio extraction)
- [ ] Whisper (transcription)
- [ ] OpenCV (slide detection)
- [ ] pyannote.audio (speaker diarization)

## Installation (Future)

```bash
# Python
pip install svaf

# CLI
svaf --version
```

## Usage Example (Future)

```python
from svaf import SVAFBuilder

# Create SVAF container from video
builder = SVAFBuilder("lecture.mp4")
builder.extract_audio()
builder.transcribe(language="de")
builder.detect_slides(threshold=0.85)
builder.save("lecture.svaf")

# Parse existing container
from svaf import SVAFParser

parser = SVAFParser("lecture.svaf")
container = parser.load()
print(f"Duration: {container.metadata['duration_seconds']}s")
print(f"Events: {len(container.events['events'])}")
```

---

**Current Phase:** RFC & Documentation
**Next Phase:** MVP Implementation (Python library + CLI)
