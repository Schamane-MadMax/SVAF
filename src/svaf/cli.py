"""SVAF-CLI: Container validieren und inspizieren."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click

from svaf import __version__
from svaf.validator import LEVELS, SVAFValidator


@click.group()
@click.version_option(version=__version__, prog_name="svaf")
def cli() -> None:
    """SVAF — Semantic Video Analysis Format."""


@cli.command()
@click.argument("container_path", type=click.Path(exists=True, file_okay=False))
@click.option("--level", type=click.Choice(LEVELS), default="semantic",
              help="Prüftiefe nach RFC-0002 §3 (Default: semantic)")
@click.option("--strict", is_flag=True,
              help="Warnungen (Level 2/3) führen zu Exit-Code 1")
@click.option("--schema-dir", type=click.Path(exists=True, file_okay=False),
              help="Pfad zu den normativen Schemas (Default: Repo-Layout/SVAF_SCHEMA_DIR)")
def validate(container_path: str, level: str, strict: bool, schema_dir: str | None) -> None:
    """Validiert einen SVAF-Container gegen die normativen JSON-Schemas."""
    try:
        validator = SVAFValidator(schema_dir=schema_dir)
        result = validator.validate(container_path, level=level)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        click.echo(f"Schema-Fehler: {e}", err=True)
        sys.exit(1)

    for issue in result.errors + result.warnings:
        click.echo(f"{issue.severity.upper():7s} {issue.file} {issue.path}: {issue.message}")

    if result.is_valid and not result.warnings:
        click.echo(f"valid ({level})")
    elif result.is_valid:
        click.echo(f"valid ({level}) — {len(result.warnings)} warning(s)")
    else:
        click.echo(f"INVALID — {len(result.errors)} error(s), "
                   f"{len(result.warnings)} warning(s)")

    failed = not result.is_valid or (strict and result.warnings)
    sys.exit(1 if failed else 0)


@cli.command()
@click.argument("container_path", type=click.Path(exists=True, file_okay=False))
def info(container_path: str) -> None:
    """Zeigt Metadaten und Bestandsübersicht eines Containers."""
    root = Path(container_path)
    meta_file = root / "metadata.json"
    if not meta_file.is_file():
        click.echo("metadata.json fehlt", err=True)
        sys.exit(1)
    try:
        meta = json.loads(meta_file.read_text())
    except json.JSONDecodeError as e:
        click.echo(f"metadata.json ist kein gültiges JSON: {e}", err=True)
        sys.exit(1)

    click.echo(f"svaf_version: {meta.get('svaf_version', '?')}")
    click.echo(f"source:       {meta.get('source', '?')}")
    click.echo(f"created_utc:  {meta.get('created_utc', '?')}")
    privacy = meta.get("privacy") or {}
    has_biometrics = (root / "embeddings.json").is_file() or (root / "embeddings").is_dir()
    biometrics = privacy.get("biometrics")
    consent = privacy.get("consent")
    if has_biometrics:
        # RFC-0001 §11.3: fehlende Angaben bei vorhandener Biometrie zaehlen
        # als present bzw. unknown (fail-closed)
        if biometrics is None:
            biometrics = "present (angenommen, RFC-0001 §11.3)"
        if consent is None:
            consent = "unknown (angenommen, RFC-0001 §11.3)"
    click.echo(f"privacy:      mode={privacy.get('mode', '?')} "
               f"biometrics={biometrics or '?'} "
               f"consent={consent or '?'}")
    if has_biometrics and not str(consent).startswith("given"):
        click.echo("privacy:      WARNUNG — biometrische Artefakte ohne "
                   "erklaerten Consent (Fail-closed-Regel, RFC-0001 §11.3)")

    def load(f: Path) -> dict:
        try:
            return json.loads(f.read_text())
        except json.JSONDecodeError:
            click.echo(f"{f.name}: kein gültiges JSON — übersprungen", err=True)
            return {}

    transcript_file = root / "transcript.json"
    if transcript_file.is_file():
        transcript = load(transcript_file)
        langs = ", ".join(v.get("lang", "?") for v in transcript.get("transcripts", []))
        segments = sum(len(v.get("segments", [])) for v in transcript.get("transcripts", []))
        click.echo(f"transcript:   {langs} "
                   f"(primary {transcript.get('primary_language', '?')}, "
                   f"{segments} segments)")

    counts = []
    for name, key in [("events", "events"), ("tracks", "speaker_tracks"),
                      ("identities", "identities"), ("ocr", "slides")]:
        f = root / f"{name}.json"
        if f.is_file():
            counts.append(f"{name}={len(load(f).get(key, []))}")
    if (root / "embeddings.json").is_file():
        emb = load(root / "embeddings.json")
        counts.append(f"embeddings={len(emb.get('tracks', {}))} (BIOMETRIC)")
    if counts:
        click.echo("inventory:    " + ", ".join(counts))


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
