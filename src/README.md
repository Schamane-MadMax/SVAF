# SVAF Reference Tooling (Python)

Deliberately small: the JSON Schemas in `../schemas/` are the single source
of truth for the format; this package only checks containers against them.

## Structure

```
src/
└── svaf/
    ├── validator.py  # schema-driven validation (RFC-0002 §3, levels 1–3)
    └── cli.py        # svaf validate / svaf info
```

## Usage

```bash
pip install -e .
svaf validate path/to/session.svaf            # levels 1–3, warnings tolerated
svaf validate path/to/session.svaf --strict   # warnings fail the run
svaf info path/to/session.svaf
```

Container construction and a parsing object model are intentionally not part
of this package until a real consumer exists (see CHANGELOG); earlier drafts
of such code remain available in the git history.
