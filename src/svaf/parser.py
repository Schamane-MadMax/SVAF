"""SVAF container parser."""

import json
from pathlib import Path
from typing import Optional, Union

from svaf.models import (
    Annotations,
    Events,
    Identities,
    Metadata,
    SVAFContainer,
    Tracks,
    Transcript,
)


class SVAFParserError(Exception):
    """Base exception for parser errors."""

    pass


class SVAFParser:
    """Parser for SVAF containers.

    Supports reading SVAF containers from directory structure and
    validating the content against the specification.

    Example:
        parser = SVAFParser()
        container = parser.parse("my-video.svaf")
        print(container.metadata.title)
    """

    def __init__(self, strict: bool = True, lazy: bool = False):
        """Initialize parser.

        Args:
            strict: Enable strict validation (default: True)
            lazy: Enable lazy loading for large containers (default: False)
        """
        self.strict = strict
        self.lazy = lazy

    def parse(self, path: Union[str, Path]) -> SVAFContainer:
        """Parse SVAF container from directory.

        Args:
            path: Path to SVAF container directory

        Returns:
            Parsed SVAFContainer object

        Raises:
            SVAFParserError: If container is invalid or cannot be parsed
        """
        container_path = Path(path)

        if not container_path.exists():
            raise SVAFParserError(f"Container not found: {container_path}")

        if not container_path.is_dir():
            raise SVAFParserError(f"Container must be a directory: {container_path}")

        # Parse required metadata
        metadata = self._parse_metadata(container_path)

        # Parse optional components
        events = self._parse_events(container_path)
        transcripts = self._parse_transcripts(container_path)
        identities = self._parse_identities(container_path)
        tracks = self._parse_tracks(container_path)
        annotations = self._parse_annotations(container_path)

        # Create container
        container = SVAFContainer(
            metadata=metadata,
            events=events,
            transcripts=transcripts,
            identities=identities,
            tracks=tracks,
            annotations=annotations,
            keyframes_path=container_path / "keyframes",
        )

        # Run validation if strict mode
        if self.strict:
            self._validate_container(container, container_path)

        return container

    def _parse_metadata(self, container_path: Path) -> Metadata:
        """Parse metadata.json file."""
        metadata_file = container_path / "metadata.json"

        if not metadata_file.exists():
            raise SVAFParserError("Required file missing: metadata.json")

        try:
            with open(metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Metadata(**data)
        except json.JSONDecodeError as e:
            raise SVAFParserError(f"Invalid JSON in metadata.json: {e}")
        except Exception as e:
            raise SVAFParserError(f"Failed to parse metadata.json: {e}")

    def _parse_events(self, container_path: Path) -> Optional[Events]:
        """Parse events.json file."""
        events_file = container_path / "events.json"

        if not events_file.exists():
            return None

        try:
            with open(events_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Events(**data)
        except json.JSONDecodeError as e:
            raise SVAFParserError(f"Invalid JSON in events.json: {e}")
        except Exception as e:
            raise SVAFParserError(f"Failed to parse events.json: {e}")

    def _parse_transcripts(self, container_path: Path) -> dict[str, Transcript]:
        """Parse all transcript files (transcript_*.json)."""
        transcripts = {}

        for transcript_file in container_path.glob("transcript_*.json"):
            # Extract language code from filename (e.g., transcript_en.json -> en)
            lang = transcript_file.stem.replace("transcript_", "")

            try:
                with open(transcript_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                transcripts[lang] = Transcript(**data)
            except json.JSONDecodeError as e:
                raise SVAFParserError(f"Invalid JSON in {transcript_file.name}: {e}")
            except Exception as e:
                raise SVAFParserError(f"Failed to parse {transcript_file.name}: {e}")

        return transcripts

    def _parse_identities(self, container_path: Path) -> Optional[Identities]:
        """Parse identities.json file."""
        identities_file = container_path / "identities.json"

        if not identities_file.exists():
            return None

        try:
            with open(identities_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Identities(**data)
        except json.JSONDecodeError as e:
            raise SVAFParserError(f"Invalid JSON in identities.json: {e}")
        except Exception as e:
            raise SVAFParserError(f"Failed to parse identities.json: {e}")

    def _parse_tracks(self, container_path: Path) -> Optional[Tracks]:
        """Parse tracks.json file."""
        tracks_file = container_path / "tracks.json"

        if not tracks_file.exists():
            return None

        try:
            with open(tracks_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Tracks(**data)
        except json.JSONDecodeError as e:
            raise SVAFParserError(f"Invalid JSON in tracks.json: {e}")
        except Exception as e:
            raise SVAFParserError(f"Failed to parse tracks.json: {e}")

    def _parse_annotations(self, container_path: Path) -> Optional[Annotations]:
        """Parse annotations.json file."""
        annotations_file = container_path / "annotations.json"

        if not annotations_file.exists():
            return None

        try:
            with open(annotations_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return Annotations(**data)
        except json.JSONDecodeError as e:
            raise SVAFParserError(f"Invalid JSON in annotations.json: {e}")
        except Exception as e:
            raise SVAFParserError(f"Failed to parse annotations.json: {e}")

    def _validate_container(self, container: SVAFContainer, container_path: Path) -> None:
        """Perform additional validation on parsed container."""
        errors = []

        # Validate timestamp bounds
        max_time = container.metadata.duration_seconds
        if container.events:
            for event in container.events.events:
                if event.start_time > max_time:
                    errors.append(
                        f"Event {event.event_id} start_time ({event.start_time}s) "
                        f"exceeds duration ({max_time}s)"
                    )
                if event.end_time and event.end_time > max_time:
                    errors.append(
                        f"Event {event.event_id} end_time ({event.end_time}s) "
                        f"exceeds duration ({max_time}s)"
                    )

        # Validate transcript timestamps
        for lang, transcript in container.transcripts.items():
            for segment in transcript.segments:
                if segment.end_time > max_time:
                    errors.append(
                        f"Transcript {lang} segment {segment.segment_id} end_time "
                        f"({segment.end_time}s) exceeds duration ({max_time}s)"
                    )

        # Validate identity references
        identity_ids = set()
        if container.identities:
            identity_ids = {i.identity_id for i in container.identities.identities}

        # Check speaker_id references in transcripts
        for lang, transcript in container.transcripts.items():
            for segment in transcript.segments:
                if segment.speaker_id and segment.speaker_id not in identity_ids:
                    errors.append(
                        f"Transcript {lang} segment {segment.segment_id} references "
                        f"unknown speaker: {segment.speaker_id}"
                    )

        # Check identity_id references in events
        if container.events:
            for event in container.events.events:
                if event.identity_id and event.identity_id not in identity_ids:
                    errors.append(
                        f"Event {event.event_id} references unknown identity: {event.identity_id}"
                    )

        # Validate keyframe references
        if container.keyframes_path and container.keyframes_path.exists():
            # Check events
            if container.events:
                for event in container.events.events:
                    if event.keyframe:
                        keyframe_path = container_path / event.keyframe
                        if not keyframe_path.exists():
                            errors.append(
                                f"Event {event.event_id} references missing keyframe: "
                                f"{event.keyframe}"
                            )

            # Check identities
            if container.identities:
                for identity in container.identities.identities:
                    if identity.keyframes:
                        for keyframe in identity.keyframes:
                            keyframe_path = container_path / keyframe
                            if not keyframe_path.exists():
                                errors.append(
                                    f"Identity {identity.identity_id} references missing "
                                    f"keyframe: {keyframe}"
                                )

        # Check for duplicate IDs
        if container.events:
            event_ids = [e.event_id for e in container.events.events]
            duplicates = {x for x in event_ids if event_ids.count(x) > 1}
            if duplicates:
                errors.append(f"Duplicate event IDs found: {duplicates}")

        # Raise if errors found
        if errors:
            error_msg = "Container validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            raise SVAFParserError(error_msg)
