"""SVAF container builder."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

from svaf.models import (
    Annotation,
    Annotations,
    AnnotationType,
    Author,
    AuthorRole,
    Event,
    Events,
    Identities,
    Identity,
    IdentityType,
    Metadata,
    Privacy,
    Source,
    SourceType,
    SVAFContainer,
    Track,
    Tracks,
    TrackType,
    Transcript,
    TranscriptMetadata,
    TranscriptSegment,
    Word,
)


class SVAFBuilderError(Exception):
    """Base exception for builder errors."""

    pass


class SVAFBuilder:
    """Fluent API builder for creating SVAF containers.

    Example:
        builder = (
            SVAFBuilder()
            .set_metadata(
                title="My Presentation",
                duration_seconds=3600,
                primary_language="en"
            )
            .add_event(
                event_id="slide_001",
                type="slide.change",
                start_time=120.5,
                keyframe="keyframes/slide_001.jpg"
            )
            .build()
        )
        builder.save("my-presentation.svaf")
    """

    def __init__(self):
        """Initialize builder with empty container."""
        self._metadata: Optional[Metadata] = None
        self._events: List[Event] = []
        self._transcripts: Dict[str, Transcript] = {}
        self._identities: List[Identity] = []
        self._tracks: List[Track] = []
        self._annotations: List[Annotation] = []
        self._keyframes: Dict[str, bytes] = {}  # filename -> content

    def set_metadata(
        self,
        title: str,
        duration_seconds: float,
        primary_language: str,
        svaf_version: str = "0.1.0",
        container_id: Optional[UUID] = None,
        description: Optional[str] = None,
        languages: Optional[List[str]] = None,
        creation_date: Optional[datetime] = None,
        source: Optional[Source] = None,
        authors: Optional[List[Author]] = None,
        tags: Optional[List[str]] = None,
        license: Optional[str] = None,
    ) -> "SVAFBuilder":
        """Set container metadata.

        Args:
            title: Container title
            duration_seconds: Content duration in seconds
            primary_language: Primary language (ISO 639-1 code)
            svaf_version: SVAF version (default: "0.1.0")
            container_id: UUID (auto-generated if not provided)
            description: Optional description
            languages: List of language codes
            creation_date: Creation timestamp (default: now)
            source: Source information
            authors: List of authors
            tags: Content tags
            license: License identifier

        Returns:
            Self for chaining
        """
        self._metadata = Metadata(
            svaf_version=svaf_version,
            container_id=container_id or uuid4(),
            title=title,
            description=description,
            duration_seconds=duration_seconds,
            primary_language=primary_language,
            languages=languages,
            creation_date=creation_date or datetime.utcnow(),
            source=source,
            authors=authors,
            tags=tags,
            license=license,
        )
        return self

    def add_source(
        self,
        source_type: Union[SourceType, str],
        original_file: Optional[str] = None,
        original_duration: Optional[float] = None,
        original_resolution: Optional[str] = None,
        original_size_bytes: Optional[int] = None,
    ) -> "SVAFBuilder":
        """Add source information to metadata.

        Args:
            source_type: Source type (video/audio/podcast/stream)
            original_file: Original filename
            original_duration: Original duration in seconds
            original_resolution: Original resolution (e.g., "1920x1080")
            original_size_bytes: Original file size in bytes

        Returns:
            Self for chaining
        """
        if self._metadata is None:
            raise SVAFBuilderError("Metadata must be set before adding source")

        source = Source(
            type=SourceType(source_type) if isinstance(source_type, str) else source_type,
            original_file=original_file,
            original_duration=original_duration,
            original_resolution=original_resolution,
            original_size_bytes=original_size_bytes,
        )
        self._metadata.source = source
        return self

    def add_author(
        self,
        name: str,
        role: Union[AuthorRole, str],
        email: Optional[str] = None,
    ) -> "SVAFBuilder":
        """Add author to metadata.

        Args:
            name: Author name
            role: Author role (creator/editor/transcriber/annotator)
            email: Author email

        Returns:
            Self for chaining
        """
        if self._metadata is None:
            raise SVAFBuilderError("Metadata must be set before adding authors")

        author = Author(
            name=name,
            role=AuthorRole(role) if isinstance(role, str) else role,
            email=email,
        )
        if self._metadata.authors is None:
            self._metadata.authors = []
        self._metadata.authors.append(author)
        return self

    def add_event(
        self,
        event_id: str,
        type: str,
        start_time: float,
        end_time: Optional[float] = None,
        keyframe: Optional[str] = None,
        identity_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "SVAFBuilder":
        """Add event to timeline.

        Args:
            event_id: Unique event identifier (e.g., "evt_001")
            type: Event type (namespace.action, e.g., "slide.change")
            start_time: Start time in seconds
            end_time: End time in seconds (optional)
            keyframe: Relative path to keyframe image
            identity_id: Reference to identity
            metadata: Event-specific metadata

        Returns:
            Self for chaining
        """
        event = Event(
            event_id=event_id,
            type=type,
            start_time=start_time,
            end_time=end_time,
            keyframe=keyframe,
            identity_id=identity_id,
            metadata=metadata,
        )
        self._events.append(event)
        return self

    def add_identity(
        self,
        identity_id: str,
        type: Union[IdentityType, str],
        name: Optional[str] = None,
        role: Optional[str] = None,
        confidence: Optional[float] = None,
        keyframes: Optional[List[str]] = None,
        privacy: Optional[Privacy] = None,
    ) -> "SVAFBuilder":
        """Add identity (speaker or face).

        Args:
            identity_id: Unique identity identifier
            type: Identity type (speaker/face/both)
            name: Person name or pseudonym
            role: Role in content (e.g., "presenter")
            confidence: Identification confidence (0.0-1.0)
            keyframes: List of keyframe paths
            privacy: Privacy settings

        Returns:
            Self for chaining
        """
        identity = Identity(
            identity_id=identity_id,
            type=IdentityType(type) if isinstance(type, str) else type,
            name=name,
            role=role,
            confidence=confidence,
            keyframes=keyframes,
            privacy=privacy,
        )
        self._identities.append(identity)
        return self

    def add_transcript_segment(
        self,
        language: str,
        segment_id: str,
        start_time: float,
        end_time: float,
        text: str,
        speaker_id: Optional[str] = None,
        confidence: Optional[float] = None,
        words: Optional[List[Word]] = None,
    ) -> "SVAFBuilder":
        """Add transcript segment.

        Args:
            language: Language code (ISO 639-1)
            segment_id: Unique segment identifier (e.g., "seg_001")
            start_time: Start time in seconds
            end_time: End time in seconds
            text: Transcript text
            speaker_id: Reference to speaker identity
            confidence: Transcription confidence (0.0-1.0)
            words: Optional word-level timestamps

        Returns:
            Self for chaining
        """
        segment = TranscriptSegment(
            segment_id=segment_id,
            start_time=start_time,
            end_time=end_time,
            speaker_id=speaker_id,
            text=text,
            confidence=confidence,
            words=words,
        )

        # Get or create transcript for language
        if language not in self._transcripts:
            self._transcripts[language] = Transcript(
                language=language,
                format_version="0.1.0",
                segments=[],
            )

        self._transcripts[language].segments.append(segment)
        return self

    def set_transcript_metadata(
        self,
        language: str,
        transcription_engine: Optional[str] = None,
        transcription_date: Optional[datetime] = None,
        word_level_timestamps: Optional[bool] = None,
    ) -> "SVAFBuilder":
        """Set metadata for a transcript.

        Args:
            language: Language code
            transcription_engine: Engine used (e.g., "whisper-large-v3")
            transcription_date: Transcription timestamp
            word_level_timestamps: Whether word-level timestamps are included

        Returns:
            Self for chaining
        """
        if language not in self._transcripts:
            raise SVAFBuilderError(f"No transcript exists for language: {language}")

        self._transcripts[language].metadata = TranscriptMetadata(
            transcription_engine=transcription_engine,
            transcription_date=transcription_date,
            word_level_timestamps=word_level_timestamps,
        )
        return self

    def add_track(
        self,
        track_id: str,
        type: Union[TrackType, str],
        format: Optional[str] = None,
        sample_rate: Optional[int] = None,
        channels: Optional[int] = None,
        bitrate: Optional[int] = None,
        language: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "SVAFBuilder":
        """Add audio/video track information.

        Args:
            track_id: Unique track identifier
            type: Track type (audio/video/subtitle)
            format: Format/codec (e.g., "opus", "h264")
            sample_rate: Sample rate in Hz
            channels: Number of channels
            bitrate: Bitrate in bits/second
            language: Language code
            metadata: Track-specific metadata

        Returns:
            Self for chaining
        """
        track = Track(
            track_id=track_id,
            type=TrackType(type) if isinstance(type, str) else type,
            format=format,
            sample_rate=sample_rate,
            channels=channels,
            bitrate=bitrate,
            language=language,
            metadata=metadata,
        )
        self._tracks.append(track)
        return self

    def add_keyframe(self, relative_path: str, content: bytes) -> "SVAFBuilder":
        """Add keyframe image to container.

        Args:
            relative_path: Relative path (e.g., "keyframes/slide_001.jpg")
            content: Image file content as bytes

        Returns:
            Self for chaining
        """
        self._keyframes[relative_path] = content
        return self

    def build(self) -> SVAFContainer:
        """Build and validate the SVAF container.

        Returns:
            Complete SVAFContainer object

        Raises:
            SVAFBuilderError: If container is invalid
        """
        if self._metadata is None:
            raise SVAFBuilderError("Metadata is required")

        # Build container
        container = SVAFContainer(
            metadata=self._metadata,
            events=Events(events=self._events) if self._events else None,
            transcripts=self._transcripts if self._transcripts else None,
            identities=Identities(identities=self._identities) if self._identities else None,
            tracks=Tracks(tracks=self._tracks) if self._tracks else None,
        )

        return container

    def save(self, path: Union[str, Path], overwrite: bool = False) -> Path:
        """Build and save container to disk.

        Args:
            path: Output directory path
            overwrite: Allow overwriting existing directory

        Returns:
            Path to created container

        Raises:
            SVAFBuilderError: If save fails
        """
        container_path = Path(path)

        if container_path.exists():
            if not overwrite:
                raise SVAFBuilderError(f"Container already exists: {container_path}")
        else:
            container_path.mkdir(parents=True, exist_ok=True)

        # Build container
        container = self.build()

        # Save metadata (required)
        self._save_json(container_path / "metadata.json", container.metadata.model_dump())

        # Save events
        if container.events:
            self._save_json(container_path / "events.json", container.events.model_dump())

        # Save transcripts
        for lang, transcript in container.transcripts.items():
            filename = f"transcript_{lang}.json"
            self._save_json(container_path / filename, transcript.model_dump())

        # Save identities
        if container.identities:
            self._save_json(container_path / "identities.json", container.identities.model_dump())

        # Save tracks
        if container.tracks:
            self._save_json(container_path / "tracks.json", container.tracks.model_dump())

        # Save keyframes
        if self._keyframes:
            keyframes_dir = container_path / "keyframes"
            keyframes_dir.mkdir(exist_ok=True)

            for relative_path, content in self._keyframes.items():
                keyframe_path = container_path / relative_path
                keyframe_path.parent.mkdir(parents=True, exist_ok=True)
                keyframe_path.write_bytes(content)

        return container_path

    def _save_json(self, path: Path, data: dict) -> None:
        """Save JSON data to file."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
