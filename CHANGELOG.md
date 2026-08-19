# Changelog

Alle nennenswerten Änderungen an Spezifikation, Schemas und Referenz-Lib.

## [Unreleased]

### Hinzugefügt
- Repo-Hygiene für den öffentlichen Betrieb: `SECURITY.md` (privater
  Meldeweg, ausdrücklich auch für Privacy-Schwächen im Format),
  Privacy-Regeln in `CONTRIBUTING.md` (keine echten Personendaten in
  Fixtures/Beispielen), PR-Template mit Datenschutz-Checkpunkt,
  Dependabot, `CITATION.cff`, CI-/Lizenz-Badges im README.

## [0.5.0] — 2026-08-19

### Geändert
- **RFC-0001 auf v0.5**: Spec beschreibt jetzt das As-built-Format der
  Referenz-Pipeline (Container-Inventar mit Implementierungsstatus, Beispiele
  und Privacy-Werte an die Realität angeglichen, Metadata-Kapitel ergänzt).
  Textbasis ist die auf GitHub veröffentlichte Fassung.
- **RFC-0002 auf v1.1**: `schemas/` ist die normative Quelle; Prosa-Duplikate
  und erfundene Veröffentlichungs-URLs entfernt.
- **Alle Kern-Schemas** (metadata, transcript, events, tracks, identities) auf
  das As-built-Format umgestellt; validiert gegen reale Produktions-Container.

- **RFC-0001 Kapitel 11.3**: DSGVO-Verantwortlichkeit, Art.-9-Einordnung
  biometrischer Embeddings, Fail-closed-Regel bei fehlendem Consent
  (Auflagen aus dem Rechts-Review). Beispiel-Identitäten pseudonymisiert.
- `pyproject.toml`: erfundene Projekt-URLs durch das reale Repo ersetzt,
  Platzhalter-E-Mail durch GitHub-noreply-Adresse.
- `CODE_OF_CONDUCT.md`: Kontakt-Platzhalter durch GitHub-Issues ersetzt.

### Hinzugefügt
- `schemas/ocr.schema.json` — Datei existierte in realen Containern, fehlte in
  der Spec.
- `docs/spec-vs-implementation.md` — Divergenz-Analyse, die diesen Umbau
  begründet.
- `LICENSE` (MIT) — war in `pyproject.toml` deklariert, fehlte als Datei.
- `CHANGELOG.md` (diese Datei).

### Nach Review (Verifier, Code-Reviewer, Rechts-Review) nachgezogen
- `schemas/embeddings.schema.json` neu: `embeddings.json` (Stimm-Embeddings,
  biometrisch) wird real von der Referenz-Pipeline erzeugt, war aber unspezifiziert;
  RFC-0001 Kap. 4 und Fail-closed-Regel entsprechend erweitert.
- `annotations.schema.json` an RFC-0001 §8 angeglichen (vorher beschrieben
  Schema und RFC zwei verschiedene Zielformate).
- Schema-`$id`s auf URN-Form (`urn:svaf:schemas:<name>`) umgestellt — die
  bisherige Domain svaf.org gehört dem Projekt nicht.
- `identities.tags` erlaubt String-Arrays (RFC-Beispiel §6.2), `tracks.json`
  erlaubt reine Face-Track-Dateien (`anyOf`).
- Redaktions-Hinweise wiederhergestellt: `metadata.source` kann interne Pfade,
  OCR-Text kann personenbezogene Daten enthalten (§11.3).
- Englisches README ist jetzt `README.md`; deutsche Fassung als `README.de.md`
  mit Veraltet-Banner. Sekundärdoku (architecture, getting-started, examples,
  DEVELOPER_GUIDE) trägt Veraltet-Banner statt stillschweigend falsch zu sein.
- Klarstellung Lizenz: Der alte lokale RFC-Entwurf schlug CC-BY-4.0 für den
  Spec-Text vor; auf GitHub ist der Stand seit März unter MIT veröffentlicht.
  Dieses Repo bleibt einheitlich MIT (Besitzer-Entscheidung, dokumentiert).

### Bekannt offen
- Python-Referenz-Lib (`src/svaf/`) implementiert noch das alte Ideal-Format;
  `svaf validate` wendet die JSON-Schemas derzeit NICHT an (prüft nur
  Dateipräsenz und JSON-Syntax) — im README ausgewiesen, Umbau als separater
  Schritt geplant.
- `annotations.json`, `faces/`, `metrics/`, `embeddings/`, `index/` sind
  spezifiziert, werden aber von keiner Implementierung erzeugt.

## [0.1.0-alpha] — 2026-02-02

- Projektstart: RFC-0001 v0.4, RFC-0002 v1.0, Schema-Suite, Python-Lib
  (Builder/Parser/Validator/CLI), Tests.
