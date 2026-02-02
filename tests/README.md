# SVAF Tests

**Status:** Placeholder - Tests coming in Phase 2

## Test Structure

```
tests/
├── unit/                  # Unit tests
│   ├── test_builder.py
│   ├── test_parser.py
│   ├── test_validator.py
│   └── test_events.py
├── integration/           # Integration tests
│   ├── test_pipeline.py
│   ├── test_whisper.py
│   └── test_slide_detection.py
├── fixtures/              # Test data
│   ├── minimal.svaf/
│   ├── podcast.svaf/
│   ├── lecture.svaf/
│   └── invalid/
└── conftest.py            # Pytest configuration
```

## Running Tests (Future)

```bash
# All tests
pytest

# Unit tests only
pytest tests/unit/

# Integration tests
pytest tests/integration/

# With coverage
pytest --cov=svaf --cov-report=html
```

## Test Coverage Goals

- [ ] 90%+ coverage for core modules
- [ ] JSON Schema validation tests
- [ ] Edge case handling
- [ ] Error message clarity
- [ ] Cross-platform compatibility

---

**Current Phase:** RFC & Documentation
**Next Phase:** Test suite implementation
