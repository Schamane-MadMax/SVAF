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
