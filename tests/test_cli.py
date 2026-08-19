"""Tests des CLI (validate + info) gegen die As-built-Fixture."""
import json
import shutil
from pathlib import Path

import pytest
from click.testing import CliRunner

from svaf.cli import cli

REPO = Path(__file__).resolve().parent.parent
ASBUILT = REPO / "tests" / "fixtures" / "asbuilt.svaf"
LEGACY = REPO / "tests" / "fixtures" / "minimal.svaf"


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


def test_validate_asbuilt_exits_zero(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["validate", str(ASBUILT)])
    assert result.exit_code == 0, result.output
    assert "valid" in result.output.lower()


def test_validate_legacy_exits_one_with_schema_errors(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["validate", str(LEGACY)])
    assert result.exit_code == 1
    assert "metadata.json" in result.output


def test_validate_warning_only_fails_with_strict(
    runner: CliRunner, tmp_path: Path
) -> None:
    dst = tmp_path / "session.svaf"
    shutil.copytree(ASBUILT, dst)
    events = json.loads((dst / "events.json").read_text())
    events["events"].append(
        {"t": 5.0, "type": "speaker_change", "speaker_track": "spk:99"}
    )
    (dst / "events.json").write_text(json.dumps(events))

    lenient = runner.invoke(cli, ["validate", str(dst), "--level", "referential"])
    assert lenient.exit_code == 0, lenient.output

    strict = runner.invoke(
        cli, ["validate", str(dst), "--level", "referential", "--strict"]
    )
    assert strict.exit_code == 1
    assert "spk:99" in strict.output


def test_info_shows_metadata(runner: CliRunner) -> None:
    result = runner.invoke(cli, ["info", str(ASBUILT)])
    assert result.exit_code == 0, result.output
    assert "0.4" in result.output
    assert "de" in result.output
