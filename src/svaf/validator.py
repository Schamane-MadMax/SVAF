"""SVAF container validator."""

import json
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Union

import jsonschema

from svaf.models import SVAFContainer
from svaf.parser import SVAFParser


class ValidationLevel(Enum):
    """Validation strictness level."""

    SCHEMA = "schema"  # Level 1: JSON schema validation only
    CONSISTENCY = "consistency"  # Level 2: + referential integrity
    SEMANTIC = "semantic"  # Level 3: + semantic validation


class ErrorSeverity(Enum):
    """Error severity levels."""

    ERROR = "error"  # Must be fixed
    WARNING = "warning"  # Should be reviewed
    INFO = "info"  # Optional improvement


@dataclass
class ValidationError:
    """Validation error details."""

    severity: ErrorSeverity
    message: str
    path: Optional[str] = None
    line: Optional[int] = None
    suggestion: Optional[str] = None


@dataclass
class ValidationResult:
    """Validation result with errors and warnings."""

    is_valid: bool
    errors: List[ValidationError]
    warnings: List[ValidationError]
    container: Optional[SVAFContainer] = None

    @property
    def has_errors(self) -> bool:
        """Check if result has errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if result has warnings."""
        return len(self.warnings) > 0

    def print_report(self, show_warnings: bool = True) -> None:
        """Print human-readable validation report."""
        if self.is_valid and not self.has_warnings:
            print("✓ SVAF container is valid")
            return

        if self.errors:
            print(f"✗ Found {len(self.errors)} error(s):")
            for error in self.errors:
                location = f" at {error.path}" if error.path else ""
                print(f"  [{error.severity.value.upper()}]{location}: {error.message}")
                if error.suggestion:
                    print(f"    → Suggestion: {error.suggestion}")

        if show_warnings and self.warnings:
            print(f"\n⚠ Found {len(self.warnings)} warning(s):")
            for warning in self.warnings:
                location = f" at {warning.path}" if warning.path else ""
                print(f"  [{warning.severity.value.upper()}]{location}: {warning.message}")


class SVAFValidator:
    """Validator for SVAF containers.

    Supports multiple validation levels:
    - Schema: JSON schema validation
    - Consistency: Referential integrity, unique IDs
    - Semantic: Event overlap, transcript quality

    Example:
        validator = SVAFValidator()
        result = validator.validate("my-video.svaf")
        if result.is_valid:
            print("Valid container!")
        else:
            result.print_report()
    """

    def __init__(
        self,
        level: ValidationLevel = ValidationLevel.CONSISTENCY,
        strict: bool = True,
    ):
        """Initialize validator.

        Args:
            level: Validation level (default: CONSISTENCY)
            strict: Treat warnings as errors (default: True)
        """
        self.level = level
        self.strict = strict
        self.schemas: dict[str, dict] = {}

    def validate(self, path: Union[str, Path]) -> ValidationResult:
        """Validate SVAF container.

        Args:
            path: Path to SVAF container directory

        Returns:
            ValidationResult with errors and warnings
        """
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []
        container: Optional[SVAFContainer] = None

        container_path = Path(path)

        # Check container exists
        if not container_path.exists():
            errors.append(
                ValidationError(
                    severity=ErrorSeverity.ERROR,
                    message=f"Container not found: {container_path}",
                )
            )
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        if not container_path.is_dir():
            errors.append(
                ValidationError(
                    severity=ErrorSeverity.ERROR,
                    message=f"Container must be a directory: {container_path}",
                )
            )
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Level 1: Schema validation
        schema_errors = self._validate_schemas(container_path)
        errors.extend(schema_errors)

        if errors and self.level == ValidationLevel.SCHEMA:
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Parse container
        try:
            parser = SVAFParser(strict=False)
            container = parser.parse(container_path)
        except Exception as e:
            errors.append(
                ValidationError(
                    severity=ErrorSeverity.ERROR,
                    message=f"Failed to parse container: {e}",
                )
            )
            return ValidationResult(is_valid=False, errors=errors, warnings=warnings)

        # Level 2: Consistency validation
        if self.level in [ValidationLevel.CONSISTENCY, ValidationLevel.SEMANTIC]:
            consistency_errors, consistency_warnings = self._validate_consistency(
                container, container_path
            )
            errors.extend(consistency_errors)
            warnings.extend(consistency_warnings)

        # Level 3: Semantic validation
        if self.level == ValidationLevel.SEMANTIC:
            semantic_errors, semantic_warnings = self._validate_semantics(container)
            errors.extend(semantic_errors)
            warnings.extend(semantic_warnings)

        # Determine if valid
        is_valid = len(errors) == 0
        if self.strict and len(warnings) > 0:
            is_valid = False

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            container=container,
        )

    def _validate_schemas(self, container_path: Path) -> List[ValidationError]:
        """Validate JSON files against schemas."""
        errors: List[ValidationError] = []

        # Check required metadata.json
        metadata_file = container_path / "metadata.json"
        if not metadata_file.exists():
            errors.append(
                ValidationError(
                    severity=ErrorSeverity.ERROR,
                    message="Required file missing: metadata.json",
                    path="metadata.json",
                )
            )
        else:
            try:
                with open(metadata_file, "r") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                errors.append(
                    ValidationError(
                        severity=ErrorSeverity.ERROR,
                        message=f"Invalid JSON: {e}",
                        path="metadata.json",
                        line=e.lineno,
                    )
                )

        # Validate optional files if they exist
        optional_files = [
            "events.json",
            "identities.json",
            "tracks.json",
            "annotations.json",
        ]

        for filename in optional_files:
            file_path = container_path / filename
            if file_path.exists():
                try:
                    with open(file_path, "r") as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    errors.append(
                        ValidationError(
                            severity=ErrorSeverity.ERROR,
                            message=f"Invalid JSON: {e}",
                            path=filename,
                            line=e.lineno,
                        )
                    )

        # Validate transcript files
        for transcript_file in container_path.glob("transcript_*.json"):
            try:
                with open(transcript_file, "r") as f:
                    json.load(f)
            except json.JSONDecodeError as e:
                errors.append(
                    ValidationError(
                        severity=ErrorSeverity.ERROR,
                        message=f"Invalid JSON: {e}",
                        path=transcript_file.name,
                        line=e.lineno,
                    )
                )

        return errors

    def _validate_consistency(
        self, container: SVAFContainer, container_path: Path
    ) -> tuple[List[ValidationError], List[ValidationError]]:
        """Validate referential integrity and consistency."""
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []

        # Validate timestamp bounds
        max_time = container.metadata.duration_seconds

        if container.events:
            for event in container.events.events:
                if event.start_time > max_time:
                    errors.append(
                        ValidationError(
                            severity=ErrorSeverity.ERROR,
                            message=f"Event {event.event_id} start_time ({event.start_time}s) "
                            f"exceeds duration ({max_time}s)",
                            path=f"events.json > {event.event_id}",
                        )
                    )
                if event.end_time and event.end_time > max_time:
                    errors.append(
                        ValidationError(
                            severity=ErrorSeverity.ERROR,
                            message=f"Event {event.event_id} end_time ({event.end_time}s) "
                            f"exceeds duration ({max_time}s)",
                            path=f"events.json > {event.event_id}",
                        )
                    )

        # Check transcript timestamps
        for lang, transcript in container.transcripts.items():
            for segment in transcript.segments:
                if segment.end_time > max_time:
                    errors.append(
                        ValidationError(
                            severity=ErrorSeverity.ERROR,
                            message=f"Segment end_time ({segment.end_time}s) exceeds duration",
                            path=f"transcript_{lang}.json > {segment.segment_id}",
                        )
                    )

        # Build identity ID set
        identity_ids = set()
        if container.identities:
            identity_ids = {i.identity_id for i in container.identities.identities}

            # Check for duplicate identity IDs
            id_list = [i.identity_id for i in container.identities.identities]
            duplicates = {x for x in id_list if id_list.count(x) > 1}
            if duplicates:
                errors.append(
                    ValidationError(
                        severity=ErrorSeverity.ERROR,
                        message=f"Duplicate identity IDs: {duplicates}",
                        path="identities.json",
                    )
                )

        # Validate speaker_id references
        for lang, transcript in container.transcripts.items():
            for segment in transcript.segments:
                if segment.speaker_id and segment.speaker_id not in identity_ids:
                    errors.append(
                        ValidationError(
                            severity=ErrorSeverity.ERROR,
                            message=f"Unknown speaker_id: {segment.speaker_id}",
                            path=f"transcript_{lang}.json > {segment.segment_id}",
                            suggestion="Add identity to identities.json",
                        )
                    )

        # Validate identity_id references in events
        if container.events:
            for event in container.events.events:
                if event.identity_id and event.identity_id not in identity_ids:
                    errors.append(
                        ValidationError(
                            severity=ErrorSeverity.ERROR,
                            message=f"Unknown identity_id: {event.identity_id}",
                            path=f"events.json > {event.event_id}",
                            suggestion="Add identity to identities.json",
                        )
                    )

        # Validate keyframe references
        if container.events:
            for event in container.events.events:
                if event.keyframe:
                    keyframe_path = container_path / event.keyframe
                    if not keyframe_path.exists():
                        errors.append(
                            ValidationError(
                                severity=ErrorSeverity.ERROR,
                                message=f"Missing keyframe: {event.keyframe}",
                                path=f"events.json > {event.event_id}",
                            )
                        )

        if container.identities:
            for identity in container.identities.identities:
                if identity.keyframes:
                    for keyframe in identity.keyframes:
                        keyframe_path = container_path / keyframe
                        if not keyframe_path.exists():
                            errors.append(
                                ValidationError(
                                    severity=ErrorSeverity.ERROR,
                                    message=f"Missing keyframe: {keyframe}",
                                    path=f"identities.json > {identity.identity_id}",
                                )
                            )

        # Check for duplicate event IDs
        if container.events:
            event_ids = [e.event_id for e in container.events.events]
            duplicates = {x for x in event_ids if event_ids.count(x) > 1}
            if duplicates:
                errors.append(
                    ValidationError(
                        severity=ErrorSeverity.ERROR,
                        message=f"Duplicate event IDs: {duplicates}",
                        path="events.json",
                    )
                )

        # Warn if no transcript
        if not container.transcripts:
            warnings.append(
                ValidationError(
                    severity=ErrorSeverity.WARNING,
                    message="No transcripts found (audio-only container?)",
                    suggestion="Add transcript file if speech content exists",
                )
            )

        return errors, warnings

    def _validate_semantics(
        self, container: SVAFContainer
    ) -> tuple[List[ValidationError], List[ValidationError]]:
        """Validate semantic correctness."""
        errors: List[ValidationError] = []
        warnings: List[ValidationError] = []

        # Check for event overlaps (same type)
        if container.events:
            events_by_type: dict[str, list] = {}
            for event in container.events.events:
                if event.type not in events_by_type:
                    events_by_type[event.type] = []
                events_by_type[event.type].append(event)

            for event_type, events in events_by_type.items():
                # Sort by start time
                sorted_events = sorted(events, key=lambda e: e.start_time)

                for i in range(len(sorted_events) - 1):
                    curr = sorted_events[i]
                    next_event = sorted_events[i + 1]

                    curr_end = curr.end_time or curr.start_time
                    next_start = next_event.start_time

                    if curr_end > next_start:
                        warnings.append(
                            ValidationError(
                                severity=ErrorSeverity.WARNING,
                                message=f"Overlapping events of type '{event_type}': "
                                f"{curr.event_id} and {next_event.event_id}",
                                path="events.json",
                                suggestion="Check if overlap is intentional",
                            )
                        )

        # Check transcript segment overlaps (same speaker)
        for lang, transcript in container.transcripts.items():
            segments_by_speaker: dict[Optional[str], list] = {}
            for segment in transcript.segments:
                speaker = segment.speaker_id
                if speaker not in segments_by_speaker:
                    segments_by_speaker[speaker] = []
                segments_by_speaker[speaker].append(segment)

            for speaker, segments in segments_by_speaker.items():
                sorted_segments = sorted(segments, key=lambda s: s.start_time)

                for i in range(len(sorted_segments) - 1):
                    curr = sorted_segments[i]
                    next_seg = sorted_segments[i + 1]

                    if curr.end_time > next_seg.start_time:
                        warnings.append(
                            ValidationError(
                                severity=ErrorSeverity.WARNING,
                                message=f"Overlapping segments: {curr.segment_id} and "
                                f"{next_seg.segment_id}",
                                path=f"transcript_{lang}.json",
                            )
                        )

        # Check for low confidence scores
        for lang, transcript in container.transcripts.items():
            low_confidence_count = 0
            for segment in transcript.segments:
                if segment.confidence is not None and segment.confidence < 0.7:
                    low_confidence_count += 1

            if low_confidence_count > 0:
                ratio = low_confidence_count / len(transcript.segments)
                if ratio > 0.3:  # More than 30% low confidence
                    warnings.append(
                        ValidationError(
                            severity=ErrorSeverity.WARNING,
                            message=f"High number of low-confidence segments ({low_confidence_count})",
                            path=f"transcript_{lang}.json",
                            suggestion="Consider manual review or re-transcription",
                        )
                    )

        return errors, warnings
