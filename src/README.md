# SVAF Reference Library (Python)

**Status:** predates the reality-first alignment of the schemas (RFC-0001 v0.5)
and is being reworked. In particular, `svaf validate` does not yet apply the
JSON schemas — see the repository README and CHANGELOG.

## Structure

```
src/
└── svaf/
    ├── models.py     # Pydantic models (old ideal format)
    ├── builder.py    # Container builder
    ├── parser.py     # Container parsing
    ├── validator.py  # Presence/syntax checks (schema application pending)
    └── cli.py        # svaf command-line interface
```

For validating containers against the normative schemas today, use the
`jsonschema` snippet in RFC-0002 section 6.
