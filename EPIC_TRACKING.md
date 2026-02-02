# SVAF EPIC Tracking

**Purpose:** Detailed tracking of all 13 EPICs with story-level granularity
**Format:** GitHub-compatible for Project Boards

---

## EPIC 1: Specification & Standards 📋

**Owner:** @markus
**Status:** In Progress (60%)
**Timeline:** Q1-Q2 2026
**Dependencies:** None

### Stories

- [x] **RFC-0001: Core Specification**
  - Status: Complete
  - Deliverable: `docs/rfcs/RFC-0001-core.md`
  - Version: 0.4

- [x] **RFC-0002: JSON Schema Suite**
  - Status: Complete
  - Deliverable: `docs/rfcs/RFC-0002-json-schemas.md`
  - All 6 core schemas documented

- [ ] **RFC-0003: ROI Detection Standard**
  - Status: Planned
  - Priority: Medium
  - Timeline: Q2 2026
  - Details: Automatic chart/code detection specification

- [ ] **RFC-0004: Multi-Track Audio**
  - Status: Planned
  - Priority: Low
  - Timeline: Q2 2026
  - Details: Separate audio tracks, background music separation

- [ ] **RFC-0005: Streaming & Live**
  - Status: Planned
  - Priority: Low
  - Timeline: Q3 2026
  - Details: Live transcription support, incremental updates

- [ ] **Specification Website**
  - Status: Planned
  - Priority: Medium
  - Timeline: Q2 2026
  - URL: spec.svaf.org
  - Features: Online schema browser, interactive examples

---

## EPIC 2: Core Library (Python) 🐍

**Owner:** @markus
**Status:** Complete (MVP)
**Timeline:** Q1 2026 ✅
**Dependencies:** EPIC 1 (RFC-0002)

### Stories

- [x] **Parser Implementation**
  - File: `src/svaf/parser.py`
  - Lines: 300+
  - Features: Lazy loading, error handling, validation
  - Tests: `tests/test_parser.py`
  - Coverage: 95%

- [x] **Builder Implementation**
  - File: `src/svaf/builder.py`
  - Lines: 410+
  - Features: Fluent API, auto UUID, validation
  - Tests: `tests/test_builder.py`
  - Coverage: 95%

- [x] **Validator Tool**
  - File: `src/svaf/validator.py`
  - Lines: 450+
  - Features: 3-level validation, detailed reports
  - Tests: Partial
  - Coverage: 85%

- [x] **I/O Operations**
  - Status: Complete
  - Features: Container import/export, JSON handling
  - Part of: Parser and Builder

- [ ] **Keyframe Management**
  - Status: Partial (60%)
  - Features: Extraction API, deduplication, format conversion
  - Priority: Medium
  - Timeline: Q2 2026

- [ ] **Python Package (PyPI)**
  - Status: Prepared (80%)
  - File: `pyproject.toml`
  - Actions Needed:
    - [ ] Set up GitHub Actions
    - [ ] Test PyPI upload
    - [ ] Create release workflow
  - Timeline: End of February 2026

---

## EPIC 3: CLI Tools 🛠️

**Owner:** @markus
**Status:** In Progress (40%)
**Timeline:** Q1-Q2 2026
**Dependencies:** EPIC 2 (Core Library)

### Stories

- [ ] **svaf create**
  - Status: Blocked
  - Blocker: Needs EPIC 4 (Processing Pipeline)
  - Features: Create container from video/audio file
  - Timeline: Q2 2026

- [x] **svaf validate**
  - Status: Complete
  - File: `src/svaf/cli.py`
  - Features: Schema/consistency/semantic validation
  - Output: Text, JSON, YAML

- [x] **svaf info**
  - Status: Complete
  - File: `src/svaf/cli.py`
  - Features: Container statistics, event listing
  - Output: Text (Rich), JSON

- [ ] **svaf export**
  - Status: Stub (10%)
  - Features: ZIP/TAR, SRT/VTT, Markdown
  - Priority: High
  - Timeline: Q1 2026

- [ ] **svaf merge**
  - Status: Planned
  - Priority: Medium
  - Timeline: Q2 2026
  - Use Case: Multi-part videos

- [ ] **svaf diff**
  - Status: Planned
  - Priority: Low
  - Timeline: Q2 2026
  - Use Case: Versioning

- [ ] **Interactive Mode (TUI)**
  - Status: Planned
  - Priority: Low
  - Timeline: Q2 2026
  - Tech: Rich/Textual
  - Features: Event timeline browser, transcript viewer

---

## EPIC 4: Processing Pipeline 🎬

**Owner:** TBD
**Status:** Planned
**Timeline:** Q2 2026
**Dependencies:** EPIC 2 (Core Library)

### Stories (Priority Order)

1. [ ] **Audio Extraction**
   - Tech: FFmpeg
   - Features: Multi-track support, normalization
   - Priority: High
   - Timeline: Week 1-2

2. [ ] **Transcription Engine**
   - Tech: Whisper (local + API)
   - Features: Word-level timestamps, confidence scores
   - Alternatives: AssemblyAI, Deepgram
   - Priority: High
   - Timeline: Week 2-3

3. [ ] **Slide Detection**
   - Tech: OpenCV frame-diff
   - Features: Scene change detection, duplicate elimination
   - Priority: High
   - Timeline: Week 3-4

4. [ ] **Speaker Diarization**
   - Tech: pyannote.audio
   - Features: Overlapping speech, identity linking
   - Priority: Medium
   - Timeline: Week 5-6

5. [ ] **OCR Integration**
   - Tech: Tesseract/PaddleOCR
   - Features: Multi-language, PII detection
   - Priority: Medium
   - Timeline: Week 7-8

6. [ ] **Face Detection & Tracking**
   - Tech: MediaPipe/OpenCV DNN
   - Features: Mood detection, privacy mode
   - Priority: Low
   - Timeline: Week 9-10

7. [ ] **ROI Detection**
   - Tech: YOLO
   - Features: Chart/code detection, bounding boxes
   - Priority: Low
   - Timeline: Week 11-12

8. [ ] **Pipeline Orchestration**
   - Features: Configurable steps, parallelization, checkpoints
   - Priority: High
   - Timeline: Throughout

---

## EPIC 5: RAG Integration 🤖

**Owner:** TBD
**Status:** Planned
**Timeline:** Q2-Q3 2026
**Dependencies:** EPIC 2 (Core Library)

### Stories

1. [ ] **Chunking Strategies**
   - Segment-based, event-based, sliding window, topic-based
   - Priority: High
   - Timeline: Week 1-2

2. [ ] **Embedding Generation**
   - Text (OpenAI, HuggingFace), Image (CLIP), Multimodal
   - Priority: High
   - Timeline: Week 2-3

3. [ ] **Vector DB Integration**
   - Adapters: Pinecone, Weaviate, Qdrant, Chroma
   - Priority: High
   - Timeline: Week 3-4

4. [ ] **LangChain Integration**
   - SVAFLoader, Document chunking, Retrieval chains
   - Priority: High
   - Timeline: Week 4-5

5. [ ] **LlamaIndex Integration**
   - SVAFReader, Index construction, Query engine
   - Priority: Medium
   - Timeline: Week 5-6

6. [ ] **Search & Retrieval**
   - Fulltext, semantic, hybrid search
   - Priority: High
   - Timeline: Week 6-7

7. [ ] **Context-Aware Retrieval**
   - Temporal, slide, speaker, topic context
   - Priority: Medium
   - Timeline: Week 7-8

---

## EPIC 6: Web Viewer & UI 🌐

**Owner:** TBD
**Status:** Planned
**Timeline:** Q3 2026
**Dependencies:** EPIC 7 (TypeScript Library)

### Stories

1. [ ] **Web Player Core**
   - React/Vue/Svelte component
   - Audio player with waveform
   - Timeline visualization

2. [ ] **Transcript Viewer**
   - Scrolling transcript
   - Click-to-jump
   - Speaker highlighting

3. [ ] **Keyframe Gallery**
   - Slide browser
   - Face keyframes (privacy-aware)
   - Fullscreen mode

4. [ ] **Search UI**
   - Fulltext search
   - Event filters
   - Time range filter

5. [ ] **Annotation Editor**
   - Inline comments
   - Tags
   - Transcript corrections

6. [ ] **Multi-Language UI**
   - Transcript switcher
   - Side-by-side view

7. [ ] **Standalone Web-App**
   - Desktop app (Electron/Tauri)
   - Drag-and-drop
   - Local storage

8. [ ] **Embeddable Widget**
   - Web component: `<svaf-player>`
   - NPM package
   - Customizable theme

---

## EPIC 7: TypeScript/JavaScript Library 📘

**Owner:** TBD
**Status:** Planned
**Timeline:** Q3 2026
**Dependencies:** EPIC 2 (Python as reference)

### Stories

1. [ ] **TypeScript Core Library**
   - Parser, Builder, Validator
   - Type definitions
   - Tree-shaking support

2. [ ] **Browser Compatibility**
   - Web APIs (Fetch, Blob)
   - IndexedDB storage
   - Web Workers

3. [ ] **Node.js Support**
   - File system access
   - Streaming support
   - CLI tools

4. [ ] **NPM Package**
   - @svaf/core, @svaf/viewer, @svaf/builder
   - Semantic versioning

5. [ ] **React Hooks**
   - useSVAFContainer
   - useSVAFPlayer
   - useSVAFTranscript
   - Example app

---

## EPIC 8: Ecosystem & Extensions 🌍

**Owner:** Community
**Status:** Planned
**Timeline:** Q3-Q4 2026 (Ongoing)
**Dependencies:** EPIC 2 (Core Library)

### Stories

1. [ ] **Plugin Architecture**
   - Plugin API
   - Hooks for pipeline steps
   - Extension registry

2. [ ] **Official Extensions**
   - Quiz generator
   - Sentiment analysis
   - Topic modeling
   - Summary generator (LLM)

3. [ ] **Community Plugins**
   - Plugin template repo
   - Plugin development docs
   - Plugin marketplace

4. [ ] **Integrations**
   - YouTube importer
   - Podcast feed importer
   - Zoom recording importer
   - OBS Studio plugin

5. [ ] **File Format Converters**
   - SRT → SVAF
   - WebVTT → SVAF
   - ELAN → SVAF
   - Audacity labels → SVAF

6. [ ] **Cloud Storage Adapters**
   - S3, Google Drive, Dropbox, Azure Blob

---

## EPIC 9: Testing & Quality Assurance ✅

**Owner:** All developers
**Status:** In Progress (30%)
**Timeline:** Ongoing

### Stories

- [x] **Unit Test Suite (Phase 1)**
  - Parser tests: Complete
  - Builder tests: Complete
  - Coverage: 90%+

- [ ] **Unit Test Suite (Phase 2)**
  - Validator tests
  - CLI tests
  - Model tests
  - Target: 95%+ coverage

- [ ] **Integration Tests**
  - Full pipeline tests
  - Real-world samples
  - Performance benchmarks

- [x] **Test Fixtures**
  - Minimal container: Complete
  - Need: Podcast, Lecture, Interview containers
  - Need: Invalid containers for error cases

- [ ] **Schema Validation Tests**
  - All JSON schemas
  - Edge cases
  - Negative tests

- [ ] **Performance Testing**
  - Large containers (10k+ events)
  - Memory profiling
  - Speed benchmarks

- [ ] **CI/CD Pipeline**
  - GitHub Actions
  - Automated testing
  - Coverage reports
  - Pre-commit hooks

- [ ] **Security Audits**
  - Dependency scanning
  - SAST
  - PII detection tests

---

## EPIC 10: Documentation & Examples 📚

**Owner:** @markus + Community
**Status:** In Progress (40%)
**Timeline:** Ongoing

### Stories

- [x] **Getting Started Guide**
  - File: `docs/getting-started.md`
  - Status: Complete
  - Content: Installation, quick start, use cases

- [ ] **API Documentation**
  - Python API (Sphinx)
  - TypeScript API (TypeDoc)
  - Target: Q2 2026

- [ ] **Tutorial Series**
  - "Build a Podcast Archiver"
  - "RAG with SVAF and LangChain"
  - "Custom Event Types"
  - "Privacy-Aware Processing"

- [ ] **Video Tutorials**
  - YouTube channel
  - Screen recordings
  - Live demos

- [ ] **Example Gallery**
  - Real-world SVAF containers
  - Different use cases
  - Best practices

- [ ] **FAQ & Troubleshooting**
  - Common errors
  - Performance tips
  - Migration guides

- [ ] **Blog & Newsletter**
  - Release notes
  - Feature spotlights
  - Use case studies

---

## EPIC 11: Deployment & Distribution 🚀

**Owner:** DevOps
**Status:** Planned
**Timeline:** Q3-Q4 2026
**Dependencies:** EPIC 2-4

### Stories

1. [ ] **Python Package (PyPI)**
   - pip install svaf
   - Wheel distribution
   - Minimal dependencies

2. [ ] **NPM Package**
   - npm install @svaf/core
   - CDN hosting (unpkg)
   - TypeScript types

3. [ ] **Docker Images**
   - svaf-cli
   - svaf-server
   - svaf-worker
   - Docker Compose setup

4. [ ] **Homebrew Formula**
   - brew install svaf
   - macOS support

5. [ ] **Snap Package**
   - snap install svaf
   - Linux distribution

6. [ ] **Cloud Deployment**
   - AWS CloudFormation
   - Terraform module
   - Kubernetes Helm chart
   - Serverless option

7. [ ] **Release Automation**
   - Semantic Release
   - Changelog generation
   - GitHub Releases

---

## EPIC 12: Community & Governance 👥

**Owner:** @markus
**Status:** Foundation Complete (50%)
**Timeline:** Ongoing

### Stories

- [ ] **Community Platforms**
  - GitHub Discussions: Ready
  - Discord server: Planned
  - Forum (Discourse): Planned
  - Matrix chat: Planned

- [x] **Contributing Guide**
  - File: `CONTRIBUTING.md`
  - Status: Complete

- [x] **Governance Model**
  - Code of Conduct: Complete
  - RFC process: Defined
  - Voting mechanism: TBD
  - Maintainer rights: TBD

- [ ] **Sponsoring & Funding**
  - GitHub Sponsors
  - Open Collective
  - Corporate sponsoring
  - Grants

- [ ] **Community Events**
  - Monthly meetups
  - Hackathons
  - Conference presence
  - Office hours

- [ ] **Recognition Program**
  - Contributor spotlight
  - Hall of Fame
  - Badges/swag

---

## EPIC 13: Business & Adoption 💼

**Owner:** Business Development
**Status:** Planned
**Timeline:** Q4 2026
**Dependencies:** EPIC 2-7

### Stories

1. [ ] **Use-Case Collection**
   - Podcast platforms
   - E-learning systems
   - Corporate training
   - Compliance/Legal-tech

2. [ ] **Partner Program**
   - Integration partners
   - Reseller program
   - Enterprise support
   - Training partners

3. [ ] **Marketing & PR**
   - Website (svaf.org)
   - SEO optimization
   - Social media
   - Press releases

4. [ ] **Conference Talks**
   - PyCon, JSConf, etc.
   - Industry conferences
   - Webinars
   - Meetup talks

5. [ ] **Whitepapers & Research**
   - Academic papers
   - Industry reports
   - Benchmarks
   - Comparison studies

6. [ ] **Enterprise Features**
   - SSO/SAML support
   - Audit logging
   - RBAC
   - SLA support

---

## Sprint Planning Template

### Sprint N (Dates)

**Goals:**
- Goal 1
- Goal 2
- Goal 3

**Tasks:**
- [ ] Task 1 (EPIC X.Y)
- [ ] Task 2 (EPIC X.Y)
- [ ] Task 3 (EPIC X.Y)

**Blocked:**
- Issue 1
- Issue 2

**Completed:**
- [x] Previous task

---

**Last Updated:** 2026-02-02
**Format:** Compatible with GitHub Projects
**View:** Use this for GitHub Project Board columns
