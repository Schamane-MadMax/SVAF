"""SVAF data models using Pydantic."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class SourceType(str, Enum):
    """Source content type."""

    VIDEO = "video"
    AUDIO = "audio"
    PODCAST = "podcast"
    STREAM = "stream"


class AuthorRole(str, Enum):
    """Author role in container creation."""

    CREATOR = "creator"
    EDITOR = "editor"
    TRANSCRIBER = "transcriber"
    ANNOTATOR = "annotator"


class IdentityType(str, Enum):
    """Identity type."""

    SPEAKER = "speaker"
    FACE = "face"
    BOTH = "both"


class TrackType(str, Enum):
    """Track type."""

    AUDIO = "audio"
    VIDEO = "video"
    SUBTITLE = "subtitle"


class AnnotationType(str, Enum):
    """Annotation type."""

    COMMENT = "comment"
    CORRECTION = "correction"
    HIGHLIGHT = "highlight"
    QUESTION = "question"
    SUMMARY = "summary"
    CLASSIFICATION = "classification"


class Source(BaseModel):
    """Source information."""

    type: SourceType
    original_file: Optional[str] = None
    original_duration: Optional[float] = Field(None, ge=0)
    original_resolution: Optional[str] = Field(None, pattern=r"^\d+x\d+$")
    original_size_bytes: Optional[int] = Field(None, ge=0)


class Author(BaseModel):
    """Author information."""

    name: str
    role: AuthorRole
    email: Optional[str] = None


class Metadata(BaseModel):
    """SVAF container metadata."""

    svaf_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    container_id: UUID = Field(default_factory=uuid4)
    title: str = Field(min_length=1)
    description: Optional[str] = None
    duration_seconds: float = Field(ge=0)
    primary_language: str = Field(pattern=r"^[a-z]{2}(-[A-Z]{2})?$")
    languages: Optional[List[str]] = None
    creation_date: datetime
    last_modified: Optional[datetime] = None
    source: Optional[Source] = None
    authors: Optional[List[Author]] = None
    tags: Optional[List[str]] = None
    license: Optional[str] = None

    @field_validator("languages")
    @classmethod
    def validate_languages(cls, v: Optional[List[str]], info) -> Optional[List[str]]:
        """Ensure primary_language is in languages list."""
        if v is not None and "primary_language" in info.data:
            primary = info.data["primary_language"]
            if primary not in v:
                v.append(primary)
        return v

    @field_validator("last_modified")
    @classmethod
    def validate_last_modified(cls, v: Optional[datetime], info) -> Optional[datetime]:
        """Ensure last_modified >= creation_date."""
        if v is not None and "creation_date" in info.data:
            if v < info.data["creation_date"]:
                raise ValueError("last_modified must be >= creation_date")
        return v


class Event(BaseModel):
    """SVAF event."""

    event_id: str = Field(pattern=r"^[a-z_]+_\d+$")
    type: str = Field(pattern=r"^[a-z_]+\.[a-z_]+$")
    start_time: float = Field(ge=0)
    end_time: Optional[float] = Field(None, ge=0)
    keyframe: Optional[str] = None
    identity_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: Optional[float], info) -> Optional[float]:
        """Ensure end_time > start_time."""
        if v is not None and "start_time" in info.data:
            if v <= info.data["start_time"]:
                raise ValueError("end_time must be > start_time")
        return v


class Events(BaseModel):
    """Collection of events."""

    events: List[Event] = Field(default_factory=list)


class Word(BaseModel):
    """Word-level timestamp."""

    word: str
    start: float = Field(ge=0)
    end: float = Field(ge=0)
    confidence: Optional[float] = Field(None, ge=0, le=1)

    @field_validator("end")
    @classmethod
    def validate_end(cls, v: float, info) -> float:
        """Ensure end > start."""
        if "start" in info.data and v <= info.data["start"]:
            raise ValueError("end must be > start")
        return v


class TranscriptSegment(BaseModel):
    """Transcript segment."""

    segment_id: str = Field(pattern=r"^seg_\d+$")
    start_time: float = Field(ge=0)
    end_time: float = Field(ge=0)
    speaker_id: Optional[str] = None
    text: str = Field(min_length=1)
    confidence: Optional[float] = Field(None, ge=0, le=1)
    words: Optional[List[Word]] = None

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v: float, info) -> float:
        """Ensure end_time > start_time."""
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be > start_time")
        return v


class TranscriptMetadata(BaseModel):
    """Transcript metadata."""

    transcription_engine: Optional[str] = None
    transcription_date: Optional[datetime] = None
    word_level_timestamps: Optional[bool] = None


class Transcript(BaseModel):
    """SVAF transcript."""

    language: str = Field(pattern=r"^[a-z]{2}(-[A-Z]{2})?$")
    format_version: str = Field(pattern=r"^\d+\.\d+\.\d+$")
    segments: List[TranscriptSegment] = Field(default_factory=list)
    metadata: Optional[TranscriptMetadata] = None


class Privacy(BaseModel):
    """Privacy settings for identity."""

    anonymize: bool = False
    blur_face: bool = False
    pseudonym: Optional[str] = None


class Identity(BaseModel):
    """Speaker or face identity."""

    identity_id: str
    type: IdentityType
    name: Optional[str] = None
    role: Optional[str] = None
    confidence: Optional[float] = Field(None, ge=0, le=1)
    keyframes: Optional[List[str]] = None
    privacy: Optional[Privacy] = None


class Identities(BaseModel):
    """Collection of identities."""

    identities: List[Identity] = Field(default_factory=list)


class Track(BaseModel):
    """Audio/video track information."""

    track_id: str
    type: TrackType
    format: Optional[str] = None
    sample_rate: Optional[int] = Field(None, gt=0)
    channels: Optional[int] = Field(None, ge=1)
    bitrate: Optional[int] = Field(None, gt=0)
    language: Optional[str] = Field(None, pattern=r"^[a-z]{2}(-[A-Z]{2})?$")
    metadata: Optional[Dict[str, Any]] = None


class Tracks(BaseModel):
    """Collection of tracks."""

    tracks: List[Track] = Field(default_factory=list)


class TimeRange(BaseModel):
    """Time range for annotations."""

    start: float = Field(ge=0)
    end: float = Field(ge=0)

    @field_validator("end")
    @classmethod
    def validate_end(cls, v: float, info) -> float:
        """Ensure end > start."""
        if "start" in info.data and v <= info.data["start"]:
            raise ValueError("end must be > start")
        return v


class AnnotationTarget(BaseModel):
    """Annotation target reference."""

    type: str
    id: str


class Annotation(BaseModel):
    """Human or machine annotation."""

    annotation_id: str
    type: AnnotationType
    author: str
    timestamp: datetime
    time_range: Optional[TimeRange] = None
    content: str
    tags: Optional[List[str]] = None
    target: Optional[AnnotationTarget] = None


class Annotations(BaseModel):
    """Collection of annotations."""

    annotations: List[Annotation] = Field(default_factory=list)


class SVAFContainer(BaseModel):
    """Complete SVAF container representation."""

    metadata: Metadata
    events: Optional[Events] = None
    transcripts: Optional[Dict[str, Transcript]] = Field(default_factory=dict)
    identities: Optional[Identities] = None
    tracks: Optional[Tracks] = None
    annotations: Optional[Annotations] = None
    keyframes_path: Optional[Path] = None

    def get_transcript(self, language: Optional[str] = None) -> Optional[Transcript]:
        """Get transcript for language (or primary language)."""
        if not self.transcripts:
            return None

        lang = language or self.metadata.primary_language
        return self.transcripts.get(lang)

    def get_identity(self, identity_id: str) -> Optional[Identity]:
        """Get identity by ID."""
        if not self.identities:
            return None

        for identity in self.identities.identities:
            if identity.identity_id == identity_id:
                return identity
        return None

    def get_events_by_type(self, event_type: str) -> List[Event]:
        """Get all events of a specific type."""
        if not self.events:
            return []

        return [e for e in self.events.events if e.type == event_type]

    def get_events_in_range(self, start: float, end: float) -> List[Event]:
        """Get events within time range."""
        if not self.events:
            return []

        result = []
        for event in self.events.events:
            event_start = event.start_time
            event_end = event.end_time or event.start_time
            # Check if event overlaps with range
            if event_start <= end and event_end >= start:
                result.append(event)
        return result
