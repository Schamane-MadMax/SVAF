"""Tests for SVAF builder."""

import pytest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory

from svaf.builder import SVAFBuilder, SVAFBuilderError
from svaf.models import SVAFContainer, SourceType, AuthorRole, IdentityType
from svaf.parser import SVAFParser


def test_builder_minimal_container():
    """Test building minimal container."""
    builder = SVAFBuilder()
    builder.set_metadata(
        title="Test Container",
        duration_seconds=120.0,
        primary_language="en",
    )

    container = builder.build()
    assert isinstance(container, SVAFContainer)
    assert container.metadata.title == "Test Container"
    assert container.metadata.duration_seconds == 120.0


def test_builder_without_metadata():
    """Test building without metadata should fail."""
    builder = SVAFBuilder()

    with pytest.raises(SVAFBuilderError, match="Metadata is required"):
        builder.build()


def test_builder_with_source():
    """Test adding source information."""
    builder = (
        SVAFBuilder()
        .set_metadata(
            title="Test",
            duration_seconds=100.0,
            primary_language="en",
        )
        .add_source(
            source_type=SourceType.VIDEO,
            original_file="video.mp4",
            original_duration=100.0,
            original_resolution="1920x1080",
        )
    )

    container = builder.build()
    assert container.metadata.source is not None
    assert container.metadata.source.type == SourceType.VIDEO
    assert container.metadata.source.original_file == "video.mp4"


def test_builder_add_author():
    """Test adding authors."""
    builder = (
        SVAFBuilder()
        .set_metadata(
            title="Test",
            duration_seconds=100.0,
            primary_language="en",
        )
        .add_author(
            name="John Doe",
            role=AuthorRole.CREATOR,
            email="john@example.com",
        )
        .add_author(
            name="Jane Smith",
            role=AuthorRole.TRANSCRIBER,
        )
    )

    container = builder.build()
    assert len(container.metadata.authors) == 2
    assert container.metadata.authors[0].name == "John Doe"
    assert container.metadata.authors[1].role == AuthorRole.TRANSCRIBER


def test_builder_add_event():
    """Test adding events."""
    builder = (
        SVAFBuilder()
        .set_metadata(
            title="Test",
            duration_seconds=100.0,
            primary_language="en",
        )
        .add_event(
            event_id="evt_001",
            type="slide.change",
            start_time=10.0,
            end_time=20.0,
            keyframe="keyframes/slide_001.jpg",
        )
    )

    container = builder.build()
    assert container.events is not None
    assert len(container.events.events) == 1

    event = container.events.events[0]
    assert event.event_id == "evt_001"
    assert event.type == "slide.change"
    assert event.start_time == 10.0


def test_builder_add_identity():
    """Test adding identities."""
    builder = (
        SVAFBuilder()
        .set_metadata(
            title="Test",
            duration_seconds=100.0,
            primary_language="en",
        )
        .add_identity(
            identity_id="speaker_01",
            type=IdentityType.SPEAKER,
            name="John Doe",
            role="presenter",
            confidence=0.95,
        )
    )

    container = builder.build()
    assert container.identities is not None
    assert len(container.identities.identities) == 1

    identity = container.identities.identities[0]
    assert identity.identity_id == "speaker_01"
    assert identity.name == "John Doe"


def test_builder_add_transcript_segment():
    """Test adding transcript segments."""
    builder = (
        SVAFBuilder()
        .set_metadata(
            title="Test",
            duration_seconds=100.0,
            primary_language="en",
        )
        .add_transcript_segment(
            language="en",
            segment_id="seg_001",
            start_time=0.0,
            end_time=5.0,
            text="Hello world",
            confidence=0.98,
        )
        .add_transcript_segment(
            language="en",
            segment_id="seg_002",
            start_time=5.0,
            end_time=10.0,
            text="This is a test",
        )
    )

    container = builder.build()
    assert "en" in container.transcripts

    transcript = container.transcripts["en"]
    assert len(transcript.segments) == 2
    assert transcript.segments[0].text == "Hello world"


@pytest.mark.xfail(reason="Alt-Lib (Ideal-Format) defekt, Umbau geplant — siehe CHANGELOG", strict=True)
def test_builder_save_and_load():
    """Test saving and loading container."""
    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.svaf"

        # Build and save
        builder = (
            SVAFBuilder()
            .set_metadata(
                title="Test Container",
                duration_seconds=60.0,
                primary_language="en",
                description="Test description",
            )
            .add_event(
                event_id="evt_001",
                type="topic.start",
                start_time=0.0,
            )
        )

        saved_path = builder.save(output_path)
        assert saved_path.exists()
        assert (saved_path / "metadata.json").exists()
        assert (saved_path / "events.json").exists()

        # Load and verify
        parser = SVAFParser()
        container = parser.parse(saved_path)

        assert container.metadata.title == "Test Container"
        assert container.events is not None
        assert len(container.events.events) == 1


def test_builder_fluent_api():
    """Test fluent API chaining."""
    container = (
        SVAFBuilder()
        .set_metadata(
            title="Fluent Test",
            duration_seconds=100.0,
            primary_language="en",
        )
        .add_event(
            event_id="evt_001",
            type="slide.change",
            start_time=10.0,
        )
        .add_identity(
            identity_id="speaker_01",
            type="speaker",
            name="John",
        )
        .add_transcript_segment(
            language="en",
            segment_id="seg_001",
            start_time=0.0,
            end_time=5.0,
            text="Test",
        )
        .build()
    )

    assert container.metadata.title == "Fluent Test"
    assert container.events is not None
    assert container.identities is not None
    assert "en" in container.transcripts


@pytest.mark.xfail(reason="Alt-Lib (Ideal-Format) defekt, Umbau geplant — siehe CHANGELOG", strict=True)
def test_builder_overwrite_protection():
    """Test that builder prevents overwriting existing containers."""
    with TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.svaf"

        builder = SVAFBuilder().set_metadata(
            title="Test",
            duration_seconds=60.0,
            primary_language="en",
        )

        # First save
        builder.save(output_path)

        # Second save without overwrite should fail
        with pytest.raises(SVAFBuilderError, match="already exists"):
            builder.save(output_path, overwrite=False)

        # With overwrite should succeed
        builder.save(output_path, overwrite=True)
