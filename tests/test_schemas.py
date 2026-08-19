"""Tests der normativen JSON-Schemas gegen As-built- und Negativ-Fixtures."""
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parent.parent
SCHEMA_DIR = REPO / "schemas"
ASBUILT = REPO / "tests" / "fixtures" / "asbuilt.svaf"
LEGACY = REPO / "tests" / "fixtures" / "minimal.svaf"

CORE_FILES = [
    "metadata", "transcript", "events", "tracks", "identities", "ocr", "embeddings",
]


def load_schema(name: str) -> dict:
    return json.loads((SCHEMA_DIR / f"{name}.schema.json").read_text())


@pytest.mark.parametrize("schema_file", sorted(SCHEMA_DIR.glob("*.schema.json")),
                         ids=lambda p: p.name)
def test_schema_is_valid_draft2020(schema_file: Path) -> None:
    Draft202012Validator.check_schema(json.loads(schema_file.read_text()))


@pytest.mark.parametrize("name", CORE_FILES)
def test_asbuilt_fixture_validates(name: str) -> None:
    data = json.loads((ASBUILT / f"{name}.json").read_text())
    errors = list(Draft202012Validator(load_schema(name)).iter_errors(data))
    assert not errors, [e.message for e in errors]


def test_legacy_ideal_format_fails_metadata_schema() -> None:
    """Das alte Ideal-Format (minimal.svaf) darf NICHT gegen die
    As-built-Schemas validieren — sonst pruefen die Schemas nichts."""
    data = json.loads((LEGACY / "metadata.json").read_text())
    errors = list(Draft202012Validator(load_schema("metadata")).iter_errors(data))
    assert errors, "Legacy-Metadata validiert unerwartet — Schema zu permissiv"


def test_missing_required_event_fields_fail() -> None:
    data = {"events": [{"type": "state_start"}]}  # 't' fehlt
    errors = list(Draft202012Validator(load_schema("events")).iter_errors(data))
    assert errors
