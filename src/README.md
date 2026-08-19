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

Schemas are resolved in this order: `--schema-dir` / `SVAF_SCHEMA_DIR`, the
packaged copy inside the wheel, then the repo layout (`schemas/` next to
`src/`).

Known limitations:
- RFC-0002 §3 level 3 also asks for "segment times within the audio
  duration"; the as-built `metadata.json` carries no duration field, so this
  check is not implementable yet.
- `src/svaf/schemas` is a symlink to the normative `schemas/` directory.
  Wheels and sdists resolve it to real files; a Windows or ZIP checkout
  without symlink support falls back to the repo layout when run from the
  source tree, but `pip install .` from such a checkout produces a wheel
  without schemas.

Container construction and a parsing object model are intentionally not part
of this package until a real consumer exists (see CHANGELOG); earlier drafts
of such code remain available in the git history.
