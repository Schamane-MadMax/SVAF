"""SVAF CLI tool."""

import json
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

from svaf import __version__
from svaf.parser import SVAFParser, SVAFParserError
from svaf.validator import SVAFValidator, ValidationLevel


console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="svaf")
def cli():
    """SVAF - Semantic Video Analysis Format

    A command-line tool for working with SVAF containers.
    """
    pass


@cli.command()
@click.argument("container_path", type=click.Path(exists=True))
@click.option(
    "--level",
    type=click.Choice(["schema", "consistency", "semantic"], case_sensitive=False),
    default="consistency",
    help="Validation level (default: consistency)",
)
@click.option(
    "--strict/--no-strict",
    default=True,
    help="Treat warnings as errors (default: strict)",
)
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json", "yaml"], case_sensitive=False),
    default="text",
    help="Output format (default: text)",
)
def validate(
    container_path: str,
    level: str,
    strict: bool,
    output_format: str,
):
    """Validate SVAF container.

    Checks container structure, JSON schemas, referential integrity,
    and semantic correctness.

    Example:
        svaf validate my-video.svaf
        svaf validate my-video.svaf --level=semantic --format=json
    """
    validation_level = ValidationLevel[level.upper()]

    try:
        validator = SVAFValidator(level=validation_level, strict=strict)
        result = validator.validate(container_path)

        if output_format == "json":
            output = {
                "valid": result.is_valid,
                "errors": [
                    {
                        "severity": e.severity.value,
                        "message": e.message,
                        "path": e.path,
                    }
                    for e in result.errors
                ],
                "warnings": [
                    {
                        "severity": w.severity.value,
                        "message": w.message,
                        "path": w.path,
                    }
                    for w in result.warnings
                ],
            }
            console.print_json(json.dumps(output))
        else:
            # Text output
            if result.is_valid and not result.has_warnings:
                console.print("[green]✓[/green] SVAF container is valid", style="bold")
            else:
                result.print_report()

        sys.exit(0 if result.is_valid else 1)

    except Exception as e:
        console.print(f"[red]✗[/red] Validation failed: {e}", style="bold red")
        sys.exit(1)


@cli.command()
@click.argument("container_path", type=click.Path(exists=True))
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["text", "json"], case_sensitive=False),
    default="text",
    help="Output format (default: text)",
)
@click.option(
    "--detailed",
    is_flag=True,
    help="Show detailed information",
)
def info(container_path: str, output_format: str, detailed: bool):
    """Display container information and statistics.

    Shows metadata, events, transcripts, and other container details.

    Example:
        svaf info my-video.svaf
        svaf info my-video.svaf --format=json --detailed
    """
    try:
        parser = SVAFParser(strict=False)
        container = parser.parse(container_path)

        if output_format == "json":
            output = {
                "metadata": {
                    "title": container.metadata.title,
                    "duration_seconds": container.metadata.duration_seconds,
                    "primary_language": container.metadata.primary_language,
                    "svaf_version": container.metadata.svaf_version,
                },
                "statistics": {
                    "events": len(container.events.events) if container.events else 0,
                    "transcripts": len(container.transcripts),
                    "identities": (
                        len(container.identities.identities) if container.identities else 0
                    ),
                },
            }

            if detailed:
                if container.events:
                    output["events"] = [
                        {
                            "id": e.event_id,
                            "type": e.type,
                            "start_time": e.start_time,
                            "end_time": e.end_time,
                        }
                        for e in container.events.events
                    ]

            console.print_json(json.dumps(output, indent=2))

        else:
            # Text output with rich formatting
            console.print()
            console.print(
                Panel.fit(
                    f"[bold]{container.metadata.title}[/bold]",
                    title="SVAF Container",
                    border_style="blue",
                )
            )

            # Metadata table
            meta_table = Table(title="Metadata", show_header=False)
            meta_table.add_column("Key", style="cyan")
            meta_table.add_column("Value", style="white")

            meta_table.add_row("Container ID", str(container.metadata.container_id))
            meta_table.add_row("SVAF Version", container.metadata.svaf_version)
            meta_table.add_row(
                "Duration",
                f"{container.metadata.duration_seconds:.1f}s "
                f"({container.metadata.duration_seconds / 60:.1f}min)",
            )
            meta_table.add_row("Primary Language", container.metadata.primary_language)

            if container.metadata.description:
                meta_table.add_row("Description", container.metadata.description)

            if container.metadata.source:
                meta_table.add_row("Source Type", container.metadata.source.type.value)
                if container.metadata.source.original_file:
                    meta_table.add_row("Original File", container.metadata.source.original_file)

            console.print(meta_table)

            # Statistics table
            stats_table = Table(title="Statistics", show_header=True)
            stats_table.add_column("Component", style="cyan")
            stats_table.add_column("Count", justify="right", style="green")

            stats_table.add_row(
                "Events",
                str(len(container.events.events)) if container.events else "0",
            )
            stats_table.add_row("Transcripts", str(len(container.transcripts)))
            stats_table.add_row(
                "Identities",
                str(len(container.identities.identities)) if container.identities else "0",
            )
            stats_table.add_row(
                "Tracks",
                str(len(container.tracks.tracks)) if container.tracks else "0",
            )

            console.print()
            console.print(stats_table)

            # Detailed event listing
            if detailed and container.events:
                console.print()
                events_table = Table(title="Events", show_header=True)
                events_table.add_column("ID", style="cyan")
                events_table.add_column("Type", style="yellow")
                events_table.add_column("Start", justify="right", style="green")
                events_table.add_column("End", justify="right", style="green")

                for event in container.events.events[:10]:  # Show first 10
                    events_table.add_row(
                        event.event_id,
                        event.type,
                        f"{event.start_time:.1f}s",
                        f"{event.end_time:.1f}s" if event.end_time else "-",
                    )

                if len(container.events.events) > 10:
                    events_table.add_row(
                        "...",
                        f"({len(container.events.events) - 10} more)",
                        "",
                        "",
                        style="dim",
                    )

                console.print(events_table)

            # Transcript summary
            if container.transcripts:
                console.print()
                for lang, transcript in container.transcripts.items():
                    total_words = sum(len(seg.text.split()) for seg in transcript.segments)
                    avg_confidence = (
                        sum(
                            seg.confidence
                            for seg in transcript.segments
                            if seg.confidence is not None
                        )
                        / len(transcript.segments)
                        if transcript.segments
                        else 0
                    )

                    console.print(
                        f"[cyan]Transcript ({lang})[/cyan]: "
                        f"{len(transcript.segments)} segments, "
                        f"~{total_words} words, "
                        f"avg confidence: {avg_confidence:.2%}"
                    )

            console.print()

    except SVAFParserError as e:
        console.print(f"[red]✗[/red] Failed to parse container: {e}", style="bold red")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]✗[/red] Error: {e}", style="bold red")
        sys.exit(1)


@cli.command()
@click.argument("container_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Output file path",
)
@click.option(
    "--format",
    "export_format",
    type=click.Choice(["zip", "tar", "srt", "vtt", "markdown", "json"], case_sensitive=False),
    default="zip",
    help="Export format (default: zip)",
)
def export(container_path: str, output: Optional[str], export_format: str):
    """Export container to different formats.

    Supports ZIP/TAR archives, subtitle formats (SRT, VTT),
    markdown transcripts, and JSON-only exports.

    Example:
        svaf export my-video.svaf --format=srt -o subtitles.srt
        svaf export my-video.svaf --format=zip -o archive.zip
    """
    console.print(f"[yellow]Export functionality coming soon![/yellow]")
    console.print(f"Will export {container_path} to {export_format} format")
    sys.exit(0)


def main():
    """Main entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
