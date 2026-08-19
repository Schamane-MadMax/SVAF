"""SVAF — Semantic Video Analysis Format.

Referenz-Werkzeug: schema-getriebener Container-Validator plus CLI.
Die normative Formatdefinition sind die JSON-Schemas in ``schemas/``
(RFC-0002); diese Bibliothek hält bewusst kein paralleles Datenmodell vor.
"""

from svaf.validator import Issue, SVAFValidator, ValidationResult

__version__ = "0.5.0"
__all__ = ["SVAFValidator", "ValidationResult", "Issue", "__version__"]
