# Security Policy

## Reporting a vulnerability

Please report security issues **privately** via GitHub's private vulnerability
reporting on this repository (Security → Report a vulnerability). Do not open
a public issue for security-relevant findings.

You can expect an initial response within 14 days. Please include a
description, reproduction steps, and the affected files or schema versions.

## Scope

- Specification texts (`docs/rfcs/`) and JSON Schemas (`schemas/`)
- The Python reference library (`src/svaf/`)

## Privacy-relevant reports

SVAF containers can describe identity-related and biometric-adjacent data
(speaker tracks, voice embeddings). Reports about privacy weaknesses in the
format design — for example, ways the fail-closed rule of RFC-0001
section 11.3 can be bypassed, or fields that leak personal data — are treated
with the same priority as code vulnerabilities. Please use the same private
reporting channel.

## Supported versions

| Version | Supported |
|---|---|
| v0.5 (current) | yes |
| earlier drafts | no |
