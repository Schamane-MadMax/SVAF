"""Tests des schema-getriebenen Validators (RFC-0002 §3, Level 1–3)."""
import json
import shutil
from pathlib import Path

import pytest

from svaf.validator import SVAFValidator

REPO = Path(__file__).resolve().parent.parent
ASBUILT = REPO / "tests" / "fixtures" / "asbuilt.svaf"
LEGACY = REPO / "tests" / "fixtures" / "minimal.svaf"


@pytest.fixture
def validator() -> SVAFValidator:
    return SVAFValidator(schema_dir=REPO / "schemas")


@pytest.fixture
def asbuilt_copy(tmp_path: Path) -> Path:
    dst = tmp_path / "session.svaf"
    shutil.copytree(ASBUILT, dst)
    return dst


def test_asbuilt_container_is_valid(validator: SVAFValidator) -> None:
    result = validator.validate(ASBUILT, level="semantic")
    assert result.is_valid, [i.message for i in result.errors]
    assert result.warnings == []


def test_legacy_ideal_container_fails(validator: SVAFValidator) -> None:
    result = validator.validate(LEGACY)
    assert not result.is_valid
    assert any("metadata" in i.file for i in result.errors)


def test_missing_required_file_is_error(validator: SVAFValidator, asbuilt_copy: Path) -> None:
    (asbuilt_copy / "events.json").unlink()
    result = validator.validate(asbuilt_copy)
    assert not result.is_valid
    assert any("events.json" in i.file for i in result.errors)


def test_missing_optional_file_is_ok(validator: SVAFValidator, asbuilt_copy: Path) -> None:
    (asbuilt_copy / "ocr.json").unlink()
    (asbuilt_copy / "embeddings.json").unlink()
    result = validator.validate(asbuilt_copy, level="semantic")
    assert result.is_valid


def test_unknown_speaker_track_reference_warns(
    validator: SVAFValidator, asbuilt_copy: Path
) -> None:
    events = json.loads((asbuilt_copy / "events.json").read_text())
    events["events"].append(
        {"t": 5.0, "type": "speaker_change", "speaker_track": "spk:99", "identity_id": "p:spk_01"}
    )
    (asbuilt_copy / "events.json").write_text(json.dumps(events))
    result = validator.validate(asbuilt_copy, level="referential")
    assert result.is_valid  # Level 2 ist RECOMMENDED -> Warnung, kein Fehler
    assert any("spk:99" in w.message for w in result.warnings)


def test_missing_slide_asset_warns(validator: SVAFValidator, asbuilt_copy: Path) -> None:
    (asbuilt_copy / "slides" / "0001.webp").unlink()
    result = validator.validate(asbuilt_copy, level="referential")
    assert any("slides/0001.webp" in w.message for w in result.warnings)


def test_segment_time_order_warns(validator: SVAFValidator, asbuilt_copy: Path) -> None:
    tracks = json.loads((asbuilt_copy / "tracks.json").read_text())
    tracks["speaker_tracks"][0]["segments"][0] = {"t_start": 44.9, "t_end": 2.0}
    (asbuilt_copy / "tracks.json").write_text(json.dumps(tracks))
    result = validator.validate(asbuilt_copy, level="semantic")
    assert result.is_valid
    assert any("t_end" in w.message for w in result.warnings)


def test_level_schema_skips_higher_levels(
    validator: SVAFValidator, asbuilt_copy: Path
) -> None:
    events = json.loads((asbuilt_copy / "events.json").read_text())
    events["events"].append(
        {"t": 5.0, "type": "speaker_change", "speaker_track": "spk:99"}
    )
    (asbuilt_copy / "events.json").write_text(json.dumps(events))
    result = validator.validate(asbuilt_copy, level="schema")
    assert result.is_valid
    assert result.warnings == []


def test_schema_dir_autodiscovery_in_repo() -> None:
    result = SVAFValidator().validate(ASBUILT)
    assert result.is_valid


# -- Review-Befunde (Robustheit) ----------------------------------------


def test_schema_invalid_file_does_not_crash_higher_levels(
    validator: SVAFValidator, asbuilt_copy: Path
) -> None:
    """Schema-invalide Datei (tracks.json als Liste) darf Level 2/3 nicht crashen."""
    (asbuilt_copy / "tracks.json").write_text("[]")
    result = validator.validate(asbuilt_copy, level="semantic")
    assert not result.is_valid
    assert any(i.file == "tracks.json" for i in result.errors)


def test_null_values_do_not_crash_semantic_level(
    validator: SVAFValidator, asbuilt_copy: Path
) -> None:
    tracks = json.loads((asbuilt_copy / "tracks.json").read_text())
    tracks["speaker_tracks"][0]["segments"][0]["t_end"] = None
    (asbuilt_copy / "tracks.json").write_text(json.dumps(tracks))
    result = validator.validate(asbuilt_copy, level="semantic")
    assert not result.is_valid  # null verletzt das Schema -> Fehler, kein Crash


def test_broken_json_is_error(validator: SVAFValidator, asbuilt_copy: Path) -> None:
    (asbuilt_copy / "metadata.json").write_text("{nicht json")
    result = validator.validate(asbuilt_copy)
    assert not result.is_valid
    assert any("JSON" in i.message for i in result.errors)


def test_missing_audio_is_error(validator: SVAFValidator, asbuilt_copy: Path) -> None:
    (asbuilt_copy / "audio.opus").unlink()
    result = validator.validate(asbuilt_copy)
    assert not result.is_valid
    assert any("audio.opus" in i.file for i in result.errors)


def test_unknown_level_raises(validator: SVAFValidator) -> None:
    with pytest.raises(ValueError):
        validator.validate(ASBUILT, level="alles")


def test_unknown_identity_reference_warns(
    validator: SVAFValidator, asbuilt_copy: Path
) -> None:
    events = json.loads((asbuilt_copy / "events.json").read_text())
    events["events"].append(
        {"t": 6.0, "type": "speaker_change", "speaker_track": "spk:01",
         "identity_id": "p:unbekannt"}
    )
    (asbuilt_copy / "events.json").write_text(json.dumps(events))
    result = validator.validate(asbuilt_copy, level="referential")
    assert any("p:unbekannt" in w.message for w in result.warnings)


def test_embeddings_reference_warns_even_without_identities(
    validator: SVAFValidator, asbuilt_copy: Path
) -> None:
    (asbuilt_copy / "identities.json").unlink()
    result = validator.validate(asbuilt_copy, level="referential")
    assert any(w.file == "embeddings.json" for w in result.warnings)


def test_track_segments_not_monotonic_warns(
    validator: SVAFValidator, asbuilt_copy: Path
) -> None:
    tracks = json.loads((asbuilt_copy / "tracks.json").read_text())
    tracks["speaker_tracks"][0]["segments"] = [
        {"t_start": 10.0, "t_end": 20.0},
        {"t_start": 0.0, "t_end": 5.0},
    ]
    (asbuilt_copy / "tracks.json").write_text(json.dumps(tracks))
    result = validator.validate(asbuilt_copy, level="semantic")
    assert any("monoton" in w.message for w in result.warnings)


def test_transcript_end_before_start_warns(
    validator: SVAFValidator, asbuilt_copy: Path
) -> None:
    transcript = json.loads((asbuilt_copy / "transcript.json").read_text())
    seg = transcript["transcripts"][0]["segments"][0]
    seg["start"], seg["end"] = 10.0, 2.0
    (asbuilt_copy / "transcript.json").write_text(json.dumps(transcript))
    result = validator.validate(asbuilt_copy, level="semantic")
    assert any(w.file == "transcript.json" for w in result.warnings)


def test_events_not_chronological_warns(
    validator: SVAFValidator, asbuilt_copy: Path
) -> None:
    events = json.loads((asbuilt_copy / "events.json").read_text())
    events["events"].insert(0, {"t": 99.0, "type": "state_start", "state": "spaet"})
    (asbuilt_copy / "events.json").write_text(json.dumps(events))
    result = validator.validate(asbuilt_copy, level="semantic")
    assert any("chronologisch" in w.message for w in result.warnings)


def test_broken_annotations_is_error(
    validator: SVAFValidator, asbuilt_copy: Path
) -> None:
    (asbuilt_copy / "annotations.json").write_text(json.dumps({"annotations": [{}]}))
    result = validator.validate(asbuilt_copy)
    assert not result.is_valid
    assert any(i.file == "annotations.json" for i in result.errors)


def test_schema_dir_env_override(asbuilt_copy: Path, monkeypatch) -> None:
    monkeypatch.setenv("SVAF_SCHEMA_DIR", str(REPO / "schemas"))
    result = SVAFValidator().validate(asbuilt_copy)
    assert result.is_valid
