# Changelog

Alle nennenswerten Änderungen an Spezifikation, Schemas und Referenz-Lib.

## [Unreleased] — Branch spec/v0.5-reality (2026-08-19)

### Geändert
- **RFC-0001 auf v0.5**: Spec beschreibt jetzt das As-built-Format der
  Referenz-Pipeline (Container-Inventar mit Implementierungsstatus, Beispiele
  und Privacy-Werte an die Realität angeglichen, Metadata-Kapitel ergänzt).
  Textbasis ist die auf GitHub veröffentlichte Fassung.
- **RFC-0002 auf v1.1**: `schemas/` ist die normative Quelle; Prosa-Duplikate
  und erfundene Veröffentlichungs-URLs entfernt.
- **Alle Kern-Schemas** (metadata, transcript, events, tracks, identities) auf
  das As-built-Format umgestellt; validiert gegen reale Produktions-Container.

### Hinzugefügt
- `schemas/ocr.schema.json` — Datei existierte in realen Containern, fehlte in
  der Spec.
- `docs/spec-vs-implementation.md` — Divergenz-Analyse, die diesen Umbau
  begründet.
- `LICENSE` (MIT) — war in `pyproject.toml` deklariert, fehlte als Datei.
- `CHANGELOG.md` (diese Datei).

### Bekannt offen
- Python-Referenz-Lib (`src/svaf/`) implementiert noch das alte Ideal-Format
  und validiert reale Container nicht; Umbau als separater Schritt geplant.
- `annotations.json`, `faces/`, `metrics/`, `embeddings/`, `index/` sind
  spezifiziert, werden aber von keiner Implementierung erzeugt.

## [0.1.0-alpha] — 2026-02-02

- Projektstart: RFC-0001 v0.4, RFC-0002 v1.0, Schema-Suite, Python-Lib
  (Builder/Parser/Validator/CLI), Tests.
