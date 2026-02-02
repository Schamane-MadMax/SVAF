"""SVAF - Semantic Video Analysis Format

A Python library for creating and parsing SVAF containers.
"""

__version__ = "0.1.0"

from svaf.parser import SVAFParser
from svaf.builder import SVAFBuilder
from svaf.validator import SVAFValidator
from svaf.models import (
    SVAFContainer,
    Metadata,
    Event,
    Transcript,
    TranscriptSegment,
    Identity,
)

__all__ = [
    "SVAFParser",
    "SVAFBuilder",
    "SVAFValidator",
    "SVAFContainer",
    "Metadata",
    "Event",
    "Transcript",
    "TranscriptSegment",
    "Identity",
    "__version__",
]
