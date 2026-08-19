# Spec vs. Implementierung — Divergenz-Analyse (Stand 2026-08-19)

Abgleich zwischen RFC-0001 v0.4 / RFC-0002 v1.0 (Schemas) und dem Format, das die
produktive Referenz-Implementierung tatsächlich schreibt.
Datenbasis: drei reale Produktions-Sessions (Archiv-Storage), validiert mit
`jsonschema` (Draft 2020-12) gegen `schemas/*.schema.json`.

**Ergebnis: Alle fünf Kerndateien scheitern in allen drei Sessions an den Schemas.**
Die Spec beschreibt ein Ideal-Format, das keine Implementierung je geschrieben hat.
Die Python-Lib in `src/svaf/` implementiert das Ideal-Format, wird in der Pipeline
aber nicht verwendet.

## Datei-Inventar

| Datei | RFC-0001 | Realität (Pipeline) |
|---|---|---|
| `metadata.json` | erforderlich | vorhanden, anderes Schema |
| `audio.opus` | erforderlich | vorhanden |
| `transcript.json` | erforderlich | vorhanden, anderes Schema |
| `events.json` | erforderlich | vorhanden, anderes Schema |
| `tracks.json` | optional | vorhanden, anderes Schema |
| `identities.json` | optional | vorhanden, anderes Schema |
| `annotations.json` | spezifiziert | existiert nirgends |
| `index/` | optional | existiert nirgends |
| `ocr.json` | **fehlt in Spec** | vorhanden (svaf_ocr) |
| `speaker.rttm` | **fehlt in Spec** | vorhanden (svaf_diarize, Rohformat) |
| `rag/` (rag_export.jsonl, enrichment.json, rag_manifest.json, ingest_done.json, verification.json) | **fehlt in Spec** | vorhanden (svaf_export_rag bis svaf_verify) |
| `slides/*.webp` | vorgesehen | vorhanden |
| `_work/` | **fehlt in Spec** | vorhanden (Arbeitsdateien, z. B. input_16k.wav) |
| `transcript_corrected.txt` | **fehlt in Spec** | teils vorhanden (manuelle Korrektur) |

## Schema-Divergenzen im Detail

### metadata.json

| Schema (Ideal) | Realität |
|---|---|
| `container_id`, `title`, `duration_seconds` erforderlich | existieren nicht |
| `svaf_version` als SemVer `X.Y.Z` | `"0.4"` (zweistellig) |
| `source` als Objekt | String (Quellpfad) |
| — | Blöcke `audio`, `proxy`, `asr`, `diarization`, `speaker_events`, `index`, `slides`, `ocr`, `privacy` (Pipeline-Konfiguration + Privacy-Metadaten) |

### transcript.json

| Schema (Ideal) | Realität |
|---|---|
| Root: `language`, `format_version`, `segments` | Root: `primary_language`, `transcripts[]` (mehrsprachig, je `lang`/`source`/`model`/`segments`) |
| — | `segments[].words[]` mit `w`/`start`/`end`/`prob` |

Die reale Struktur ist näher an RFC-0001 Kap. 5.2 (mehrsprachige Varianten) als das
Schema aus RFC-0002 — die beiden RFCs widersprechen sich hier gegenseitig.

### events.json

| Schema (Ideal) | Realität |
|---|---|
| `event_id`, `start_time` erforderlich | `t` (Sekunden), kein event_id |
| Typ-Pattern `namespace.name` | flache Typen: `state_start`, `speaker_change`, `slide_start` |
| — | Zusatzfelder je Typ: `state`, `speaker_track`, `identity_id`, `asset` |

### tracks.json

| Schema (Ideal) | Realität |
|---|---|
| Root-Key `tracks` | Root-Key `speaker_tracks` |
| Segmente mit `start_time`/`end_time` | `t_start`/`t_end` |
| — | `track_id` (`spk:NN`), `identity_id`, `label` (RTTM-Label), `quality.source` |

### identities.json

| Schema (Ideal) | Realität |
|---|---|
| `identity_id`, `privacy_mode` pro Identity erforderlich | `id`, `type`, `display_name`, `tags` (`svaf:identity.role`) |
| Privacy pro Identity | Privacy global in `metadata.json.privacy` |

### annotations.json

Schema existiert, Datei wird von keiner Implementierung erzeugt.

## Konsequenz

Eine öffentliche Spec, deren einzige produktive Implementierung
jede Kerndatei anders schreibt, ist nicht glaubwürdig. Vor der Veröffentlichung muss
entweder die Spec das As-built-Format beschreiben oder die Abweichung ausdrücklich
als Migrationspfad dokumentiert sein. Entscheidung siehe RFC-0001 v0.5 (Changelog).
