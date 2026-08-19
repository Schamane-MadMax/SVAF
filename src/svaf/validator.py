"""Schema-getriebener SVAF-Container-Validator (RFC-0002 §3).

Level 1 (schema): Pflicht-Dateien vorhanden, jede JSON-Datei validiert gegen
ihr normatives Schema aus ``schemas/`` — Verstöße sind Fehler.
Level 2 (referential): IDs und Asset-Pfade lösen auf — Verstöße sind Warnungen.
Level 3 (semantic): Zeiten sind plausibel — Verstöße sind Warnungen.

Bewusste Lücke: RFC-0002 §3 nennt als Level-3-Prüfung auch "Segmentzeiten
innerhalb der Audio-Dauer"; metadata.json führt im As-built-Format keine
Dauer, daher ist diese Prüfung derzeit nicht umsetzbar.

Schema-invalide Dateien werden von Level 2/3 ausgenommen — deren Inhalt ist
nicht vertrauenswürdig genug für Folgeprüfungen.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from jsonschema import Draft202012Validator

#: Dateiname -> Schemaname; True = Pflicht im Container (RFC-0001 §4)
CORE_FILES: dict[str, bool] = {
    "metadata": True,
    "transcript": True,
    "events": True,
    "tracks": False,
    "identities": False,
    "ocr": False,
    "embeddings": False,
    "annotations": False,
}
REQUIRED_ASSETS = ("audio.opus",)
LEVELS = ("schema", "referential", "semantic")


@dataclass
class Issue:
    severity: str  # "error" | "warning"
    file: str
    path: str
    message: str


@dataclass
class ValidationResult:
    errors: list[Issue] = field(default_factory=list)
    warnings: list[Issue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def error(self, file: str, path: str, message: str) -> None:
        self.errors.append(Issue("error", file, path, message))

    def warn(self, file: str, path: str, message: str) -> None:
        self.warnings.append(Issue("warning", file, path, message))


def _find_schema_dir() -> Path:
    """Sucht schemas/: Env-Variable, Paket-Kopie, dann Repo-Layout."""
    env = os.environ.get("SVAF_SCHEMA_DIR")
    if env:
        return Path(env)
    packaged = Path(__file__).resolve().parent / "schemas"
    if packaged.is_dir():
        return packaged
    repo = Path(__file__).resolve().parent.parent.parent / "schemas"
    if repo.is_dir():
        return repo
    raise FileNotFoundError(
        "schemas/ nicht gefunden — schema_dir angeben oder SVAF_SCHEMA_DIR setzen"
    )


class SVAFValidator:
    """Validiert einen SVAF-Container gegen die normativen JSON-Schemas."""

    def __init__(self, schema_dir: Path | str | None = None) -> None:
        self.schema_dir = Path(schema_dir) if schema_dir else _find_schema_dir()
        self._validators: dict[str, Draft202012Validator] = {}

    def _validator_for(self, name: str) -> Draft202012Validator:
        if name not in self._validators:
            schema = json.loads((self.schema_dir / f"{name}.schema.json").read_text())
            self._validators[name] = Draft202012Validator(schema)
        return self._validators[name]

    def validate(self, container: Path | str, level: str = "schema") -> ValidationResult:
        if level not in LEVELS:
            raise ValueError(f"Unbekanntes Level {level!r}, erlaubt: {LEVELS}")
        root = Path(container)
        result = ValidationResult()
        data = self._level_schema(root, result)
        if LEVELS.index(level) >= 1:
            self._level_referential(root, data, result)
        if LEVELS.index(level) >= 2:
            self._level_semantic(data, result)
        return result

    # -- Level 1 ---------------------------------------------------------

    def _level_schema(self, root: Path, result: ValidationResult) -> dict[str, dict]:
        """Prüft Präsenz + Schema-Konformität; gibt geparste Dateien zurück."""
        data: dict[str, dict] = {}
        if not root.is_dir():
            result.error(str(root), "", "Container-Verzeichnis existiert nicht")
            return data
        for asset in REQUIRED_ASSETS:
            if not (root / asset).is_file():
                result.error(asset, "", f"Pflicht-Datei {asset} fehlt")
        for name, required in CORE_FILES.items():
            f = root / f"{name}.json"
            if not f.is_file():
                if required:
                    result.error(f.name, "", f"Pflicht-Datei {f.name} fehlt")
                continue
            try:
                parsed = json.loads(f.read_text())
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                result.error(f.name, "", f"kein gültiges JSON: {e}")
                continue
            file_errors = 0
            for err in self._validator_for(name).iter_errors(parsed):
                json_path = "/".join(str(p) for p in err.path) or "(root)"
                result.error(f.name, json_path, err.message)
                file_errors += 1
            if file_errors == 0:
                data[name] = parsed
        return data

    # -- Level 2 ---------------------------------------------------------

    def _level_referential(
        self, root: Path, data: dict[str, dict], result: ValidationResult
    ) -> None:
        track_ids = {
            t.get("track_id")
            for t in data.get("tracks", {}).get("speaker_tracks", [])
        }
        identity_ids = {i.get("id") for i in data.get("identities", {}).get("identities", [])}

        for idx, event in enumerate(data.get("events", {}).get("events", [])):
            path = f"events/{idx}"
            ref = event.get("speaker_track")
            if ref is not None and ref not in track_ids:
                result.warn("events.json", path,
                            f"speaker_track {ref!r} existiert nicht in tracks.json")
            ref = event.get("identity_id")
            if ref is not None and ref not in identity_ids:
                result.warn("events.json", path,
                            f"identity_id {ref!r} existiert nicht in identities.json")
            asset = event.get("asset")
            if asset is not None and not (root / asset).is_file():
                result.warn("events.json", path, f"Asset {asset!r} fehlt im Container")

        for idx, slide in enumerate(data.get("ocr", {}).get("slides", [])):
            asset = slide.get("asset")
            if asset is not None and not (root / asset).is_file():
                result.warn("ocr.json", f"slides/{idx}",
                            f"Asset {asset!r} fehlt im Container")

        for track_ref in data.get("embeddings", {}).get("tracks", {}):
            if track_ref not in identity_ids:
                result.warn("embeddings.json", f"tracks/{track_ref}",
                            f"identity {track_ref!r} existiert nicht in identities.json")

    # -- Level 3 ---------------------------------------------------------

    def _level_semantic(self, data: dict[str, dict], result: ValidationResult) -> None:
        def num(value: object, default: float) -> float:
            return value if isinstance(value, (int, float)) else default

        for t_idx, track in enumerate(data.get("tracks", {}).get("speaker_tracks", [])):
            prev_start = -1.0
            for s_idx, seg in enumerate(track.get("segments", [])):
                path = f"speaker_tracks/{t_idx}/segments/{s_idx}"
                t_start = num(seg.get("t_start"), 0.0)
                if num(seg.get("t_end"), 0.0) < t_start:
                    result.warn("tracks.json", path,
                                f"t_end ({seg.get('t_end')}) liegt vor "
                                f"t_start ({seg.get('t_start')})")
                if t_start < prev_start:
                    result.warn("tracks.json", path,
                                "Track-Segmente nicht monoton sortiert")
                prev_start = t_start

        for v_idx, variant in enumerate(data.get("transcript", {}).get("transcripts", [])):
            prev_start = -1.0
            for s_idx, seg in enumerate(variant.get("segments", [])):
                path = f"transcripts/{v_idx}/segments/{s_idx}"
                start = num(seg.get("start"), 0.0)
                if num(seg.get("end"), 0.0) < start:
                    result.warn("transcript.json", path,
                                "Segment-end liegt vor Segment-start")
                if start < prev_start:
                    result.warn("transcript.json", path,
                                "Segmente nicht monoton sortiert")
                prev_start = start

        prev_t = -1.0
        for idx, event in enumerate(data.get("events", {}).get("events", [])):
            t = num(event.get("t"), 0.0)
            if t < prev_t:
                result.warn("events.json", f"events/{idx}",
                            "Events nicht chronologisch sortiert")
            prev_t = t
