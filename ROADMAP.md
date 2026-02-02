# SVAF Project Roadmap

**Version:** 1.0
**Last Updated:** 2026-02-02
**Status:** Active Development

This document tracks the implementation of all EPICs from the SVAF project plan.

---

## Phase 1: Foundation (Months 1-3) - **CURRENT PHASE**

### EPIC 1: Specification & Standards 📋

**Status:** 🚧 In Progress (60% complete)

| Story | Status | Notes |
|-------|--------|-------|
| RFC-0001 Finalization | ✅ Complete | v0.4 finalized |
| RFC-0002: JSON Schema Suite | ✅ Complete | All schemas documented |
| RFC-0003: ROI Detection Standard | 📋 Planned | Q2 2026 |
| RFC-0004: Multi-Track Audio | 📋 Planned | Q2 2026 |
| RFC-0005: Streaming & Live | 📋 Planned | Q3 2026 |
| Specification Website | 📋 Planned | Q2 2026 |

**Deliverables:**
- [x] RFC-0001 v0.4
- [x] RFC-0002 JSON Schemas
- [x] Core JSON schemas in `/schemas`
- [ ] Online validator website
- [ ] Community review process

---

### EPIC 2: Core Library (Python) 🐍

**Status:** ✅ Complete (MVP)

| Story | Status | Completion |
|-------|--------|------------|
| Parser Implementation | ✅ Complete | 100% |
| Builder Implementation | ✅ Complete | 100% |
| Validator Tool | ✅ Complete | 100% |
| I/O Operations | ✅ Complete | 100% |
| Keyframe Management | 🚧 Partial | 60% |
| Python Package | 🚧 In Progress | 80% |

**Deliverables:**
- [x] `SVAFParser` class with validation
- [x] `SVAFBuilder` fluent API
- [x] `SVAFValidator` with 3 levels
- [x] Pydantic models for all components
- [x] Basic test suite (90%+ coverage)
- [ ] PyPI package published
- [ ] Comprehensive documentation

**Code Location:** `/src/svaf/`

---

### EPIC 3: CLI Tools 🛠️

**Status:** 🚧 In Progress (40% complete)

| Story | Status | Notes |
|-------|--------|-------|
| svaf create | 📋 Planned | Requires EPIC 4 |
| svaf validate | ✅ Complete | Full validation support |
| svaf info | ✅ Complete | Text + JSON output |
| svaf export | 🚧 Partial | Stub implemented |
| svaf merge | 📋 Planned | Q2 2026 |
| svaf diff | 📋 Planned | Q2 2026 |
| Interactive Mode | 📋 Planned | Q2 2026 |

**Deliverables:**
- [x] `svaf validate` command
- [x] `svaf info` command
- [ ] `svaf create` (needs processing pipeline)
- [ ] `svaf export` formats (SRT, VTT, ZIP)
- [ ] Interactive TUI

**Code Location:** `/src/svaf/cli.py`

---

### EPIC 12: Community & Governance 👥

**Status:** ✅ Complete (Foundation)

| Story | Status | Notes |
|-------|--------|-------|
| Community Platforms | 🚧 Partial | GitHub ready |
| Contributing Guide | ✅ Complete | CONTRIBUTING.md |
| Code of Conduct | ✅ Complete | CODE_OF_CONDUCT.md |
| Issue Templates | ✅ Complete | Bug + Feature |
| Governance Model | 📋 Planned | Q2 2026 |
| Sponsoring & Funding | 📋 Planned | Q3 2026 |

**Deliverables:**
- [x] CONTRIBUTING.md
- [x] CODE_OF_CONDUCT.md
- [x] GitHub issue templates
- [x] PR template
- [ ] Discord/community chat
- [ ] Governance documentation

---

## Phase 2: MVP (Months 3-6)

### EPIC 4: Processing Pipeline 🎬

**Status:** 📋 Planned

**Stories:**
1. Audio Extraction (FFmpeg)
2. Transcription Engine (Whisper)
3. Speaker Diarization (pyannote.audio)
4. Slide Detection (OpenCV)
5. OCR Integration (Tesseract)
6. Face Detection & Tracking
7. ROI Detection (YOLO)
8. Pipeline Orchestration

**Target:** Q2 2026

---

### EPIC 5: RAG Integration 🤖

**Status:** 📋 Planned

**Stories:**
1. Chunking Strategies
2. Embedding Generation
3. Vector DB Integration
4. LangChain Integration
5. LlamaIndex Integration
6. Search & Retrieval
7. Context-Aware Retrieval

**Target:** Q2-Q3 2026

---

### EPIC 9: Testing & Quality Assurance ✅

**Status:** 🚧 In Progress (30% complete)

| Story | Status | Coverage |
|-------|--------|----------|
| Unit Test Suite | ✅ Complete | 90%+ |
| Integration Tests | 📋 Planned | - |
| Test Fixtures | ✅ Complete | Minimal set |
| Schema Validation Tests | 🚧 Partial | 50% |
| Performance Testing | 📋 Planned | - |
| CI/CD Pipeline | 📋 Planned | - |
| Security Audits | 📋 Planned | - |

**Test Files:**
- [x] `tests/test_parser.py`
- [x] `tests/test_builder.py`
- [ ] `tests/test_validator.py`
- [ ] `tests/test_cli.py`
- [ ] `tests/integration/`
- [ ] `tests/performance/`

---

### EPIC 10: Documentation & Examples 📚

**Status:** 🚧 In Progress (40% complete)

| Story | Status | Notes |
|-------|--------|-------|
| Getting Started Guide | ✅ Complete | /docs/getting-started.md |
| API Documentation | 🚧 Partial | Docstrings done |
| Tutorial Series | 📋 Planned | Q2 2026 |
| Video Tutorials | 📋 Planned | Q3 2026 |
| Example Gallery | 🚧 Partial | Minimal examples |
| FAQ & Troubleshooting | 📋 Planned | Q2 2026 |
| Blog & Newsletter | 📋 Planned | Q3 2026 |

**Deliverables:**
- [x] Getting Started guide
- [x] README.md
- [x] RFC documentation
- [ ] Full API reference (Sphinx)
- [ ] Tutorial notebooks
- [ ] Real-world examples

---

## Phase 3: Features (Months 6-9)

### EPIC 6: Web Viewer & UI 🌐

**Status:** 📋 Planned (Q3 2026)

**Stories:**
1. Web Player Core
2. Transcript Viewer
3. Keyframe Gallery
4. Search UI
5. Annotation Editor
6. Multi-Language UI
7. Standalone Web-App
8. Embeddable Widget

---

### EPIC 7: TypeScript/JavaScript Library 📘

**Status:** 📋 Planned (Q3 2026)

**Stories:**
1. TypeScript Core Library
2. Browser Compatibility
3. Node.js Support
4. NPM Package
5. React Hooks

---

### EPIC 8: Ecosystem & Extensions 🌍

**Status:** 📋 Planned (Q3-Q4 2026)

**Stories:**
1. Plugin Architecture
2. Official Extensions
3. Community Plugins
4. Integrations (YouTube, Zoom, etc.)
5. File Format Converters
6. Cloud Storage Adapters

---

## Phase 4: Platform (Months 9-12)

### EPIC 11: Deployment & Distribution 🚀

**Status:** 📋 Planned (Q3-Q4 2026)

**Stories:**
1. Python Package (PyPI)
2. NPM Package
3. Docker Images
4. Homebrew Formula
5. Snap Package
6. Cloud Deployment
7. Release Automation

---

### EPIC 13: Business & Adoption 💼

**Status:** 📋 Planned (Q4 2026)

**Stories:**
1. Use-Case Collection
2. Partner Program
3. Marketing & PR
4. Conference Talks
5. Whitepapers & Research
6. Enterprise Features

---

## Current Sprint (Week of 2026-02-02)

### Active Tasks
- [x] Review project structure
- [x] Implement Python core library (Parser, Builder, Validator)
- [x] Create test fixtures
- [x] Implement CLI tools (validate, info)
- [x] Write documentation
- [x] Set up community infrastructure
- [ ] Set up CI/CD pipeline
- [ ] Create GitHub Project Board
- [ ] Enhance JSON schemas

### Next Week
1. Set up GitHub Actions CI/CD
2. Publish to PyPI (test)
3. Start EPIC 4: Processing Pipeline
4. Whisper integration prototype
5. Create more example containers

---

## Metrics & Goals

### Q1 2026 Goals (Phase 1)
- [x] RFC-0001 finalized
- [x] Core Python library implemented
- [x] Basic CLI tools working
- [ ] 90%+ test coverage
- [ ] Community infrastructure ready
- [ ] First alpha release (0.1.0)

### Q2 2026 Goals (Phase 2)
- [ ] Processing pipeline MVP
- [ ] PyPI package published
- [ ] 5+ example containers
- [ ] First blog post
- [ ] 100+ GitHub stars

### Q3 2026 Goals (Phase 3)
- [ ] Web viewer prototype
- [ ] TypeScript library
- [ ] LangChain integration
- [ ] First conference talk
- [ ] 500+ GitHub stars

### Q4 2026 Goals (Phase 4)
- [ ] Beta release (0.9.0)
- [ ] 3+ production users
- [ ] Plugin ecosystem launched
- [ ] 1000+ GitHub stars

---

## Decision Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-02 | Use Pydantic for models | Type safety + validation |
| 2026-02-02 | Rich for CLI output | Better UX than plain text |
| 2026-02-02 | MIT License (proposed) | Maximum adoption |
| TBD | Python-first approach | Largest ML/AI community |
| TBD | Folder-based containers | Git-friendly, inspectable |

---

## Open Questions

1. **License:** MIT vs Apache 2.0 vs Dual-License?
2. **Governance:** BDFL vs Committee vs Foundation?
3. **Funding:** Pure OSS vs Open-Core vs SaaS?
4. **Cloud Service:** Build hosted platform?
5. **Enterprise Edition:** Separate commercial features?

---

## How to Contribute

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Setting up development environment
- Coding standards
- Testing requirements
- PR process

For major contributions, check:
1. This roadmap for planned features
2. [GitHub Issues](../../issues) for specific tasks
3. [GitHub Discussions](../../discussions) for ideas

---

**Last Updated:** 2026-02-02
**Next Review:** Weekly
**Maintainer:** @markus
