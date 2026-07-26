<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# Changelog

## [0.8.2] - 2026-07-26

- Publish the privacy-clean, license-split one-root snapshot.

All notable release changes are documented here. Versions follow Semantic Versioning while
the project is pre-1.0; a minor release may intentionally change compatibility (the
specification, Versioning).

## [Unreleased]

## [0.8.1] - 2026-07-25

### Changed

- Require the agent-facing `llms.txt` artifact in the executable release
  definition of done.

## [0.8.0] - 2026-07-24

The first published release: the specification, grammar, schemas, vocabulary, and
conformance vectors, packaged as a data-only Python kit.

### Added

- `standard/spec/SPEC.md` and `standard/spec/SYNTAX.md` — the normative specification
  and concrete textual grammar for the `.lg` netlist surface.
- `standard/grammar/loomground.ebnf` — the standalone EBNF grammar (ISO/IEC 14977), and
  `standard/grammar/tree-sitter/` — a tree-sitter grammar with generated parser, AST,
  and a syntax corpus.
- `standard/schema/` — JSON Schemas for the token, the patch (a policy graph as data),
  the observation (a vector's `expected.json`), and transport runs.
- `standard/vocabulary/` — node classes, cords, the verdict lattice, the nine
  declarations, the guard domain, risk levels, autonomy grades, and the grounding map,
  each as machine-readable JSON.
- `standard/conformance/` — 47 conformance vectors (patch, token, and negative) that
  define a conforming implementation; an implementation conforms by reproducing every
  vector, not by matching an implementation.
- `standard/language-card.json` and `llms.txt` — compact, agent-facing summaries of the
  whole language, kept in sync with the canonical vocabulary and schemas by a drift
  check.
- `loomground-governance`, an installable, data-only Python package (`src/`) exposing the
  above artifacts and a neutral implementation protocol; it contains no parser,
  evaluator, or host adapter.
- `tools/` — the CI consistency gates: language-summary drift, cross-representation
  lockstep (declaration/schema/grammar reach a vector), vector-schema validation,
  companion-skill drift, and vendor-neutrality of the normative text.
- `skills/loomground/` — a non-normative companion skill that expresses an
  AI-governance requirement as a validated `.lg` patch using a bundled validation
  engine; kept aligned with the language by its own drift gate.

### Known limitation

- Specification §9's interoperability criterion — two implementations produced
  independently of each other reproducing every vector — remains **open**. The
  existing implementations were authored within the same AI-assisted project, so
  they provide differential conformance checking today, not an independence proof
  (see `standard/conformance/README.md`, Status).
