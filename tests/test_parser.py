"""Tests for SVAF parser."""

import pytest
from pathlib import Path

from svaf.parser import SVAFParser, SVAFParserError
from svaf.models import SVAFContainer


FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_parse_minimal_container():
    """Test parsing minimal valid container."""
    parser = SVAFParser()
    container = parser.parse(FIXTURES_DIR / "minimal.svaf")

    assert isinstance(container, SVAFContainer)
    assert container.metadata.title == "Minimal Test Container"
    assert container.metadata.duration_seconds == 60.0
    assert container.metadata.primary_language == "en"


def test_parse_metadata():
    """Test metadata parsing."""
    parser = SVAFParser()
    container = parser.parse(FIXTURES_DIR / "minimal.svaf")

    metadata = container.metadata
    assert metadata.svaf_version == "0.1.0"
    assert str(metadata.container_id) == "550e8400-e29b-41d4-a716-446655440000"
    assert metadata.description == "A minimal valid SVAF container for testing"


def test_parse_events():
    """Test events parsing."""
    parser = SVAFParser()
    container = parser.parse(FIXTURES_DIR / "minimal.svaf")

    assert container.events is not None
    assert len(container.events.events) == 1

    event = container.events.events[0]
    assert event.event_id == "evt_001"
    assert event.type == "topic.start"
    assert event.start_time == 0.0


def test_parse_transcript():
    """Test transcript parsing."""
    parser = SVAFParser()
    container = parser.parse(FIXTURES_DIR / "minimal.svaf")

    assert "en" in container.transcripts
    transcript = container.transcripts["en"]

    assert transcript.language == "en"
    assert len(transcript.segments) == 2

    seg1 = transcript.segments[0]
    assert seg1.segment_id == "seg_001"
    assert seg1.text == "Hello, this is a test."
    assert seg1.confidence == 0.98


def test_parse_nonexistent_container():
    """Test parsing nonexistent container."""
    parser = SVAFParser()

    with pytest.raises(SVAFParserError, match="Container not found"):
        parser.parse(FIXTURES_DIR / "nonexistent.svaf")


def test_parse_file_not_directory():
    """Test parsing file instead of directory."""
    parser = SVAFParser()
    test_file = FIXTURES_DIR / "minimal.svaf" / "metadata.json"

    with pytest.raises(SVAFParserError, match="must be a directory"):
        parser.parse(test_file)


def test_get_transcript_by_language():
    """Test getting transcript by language."""
    parser = SVAFParser()
    container = parser.parse(FIXTURES_DIR / "minimal.svaf")

    # Get English transcript
    transcript = container.get_transcript("en")
    assert transcript is not None
    assert transcript.language == "en"

    # Get primary language (should be same)
    transcript = container.get_transcript()
    assert transcript is not None
    assert transcript.language == "en"


def test_get_events_by_type():
    """Test getting events by type."""
    parser = SVAFParser()
    container = parser.parse(FIXTURES_DIR / "minimal.svaf")

    events = container.get_events_by_type("topic.start")
    assert len(events) == 1
    assert events[0].event_id == "evt_001"

    # Non-existent type
    events = container.get_events_by_type("slide.change")
    assert len(events) == 0


def test_get_events_in_range():
    """Test getting events in time range."""
    parser = SVAFParser()
    container = parser.parse(FIXTURES_DIR / "minimal.svaf")

    # Event starts at 0.0, should be included
    events = container.get_events_in_range(0.0, 10.0)
    assert len(events) == 1

    # Range after event
    events = container.get_events_in_range(10.0, 20.0)
    assert len(events) == 0


def test_parser_strict_mode():
    """Test parser with strict validation enabled."""
    parser = SVAFParser(strict=True)
    # Should parse successfully
    container = parser.parse(FIXTURES_DIR / "minimal.svaf")
    assert container is not None


def test_parser_non_strict_mode():
    """Test parser with strict validation disabled."""
    parser = SVAFParser(strict=False)
    container = parser.parse(FIXTURES_DIR / "minimal.svaf")
    assert container is not None
