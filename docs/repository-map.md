<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# Repository map

Moved verbatim from the README (sections "Patch and Observation", "Read the
specification", "Repository map").

## Patch and Observation

A Loomground patch has an authored surface and a canonical projection:

- **Netlist** — the authored, diffable text form (`standard/spec/SYNTAX.md`,
  `standard/examples/`).
  Files end in `.lg`. (`.loom`, the pre-v0.6 name, was replaced at v0.6.0; its
  one-minor-version deprecation window has closed, and a v0.7 reader need not
  accept it.)
- **Observation** — the machine-checkable projection: graph and reservation data
  (`standard/schema/observation.schema.json`). Prohibitions and obligations act during
  evaluation and are not projected. Evaluation also produces an ordered log trace;
  that runtime record is not a patch view.

## Read the specification

- `standard/spec/SPEC.md` — the normative specification (nodes, cords, the token, evaluation,
  the governance declarations, conformance).
- `standard/spec/SYNTAX.md` — the concrete textual grammar.
- `standard/conformance/` — the vectors that define a conforming implementation.
- `standard/examples/` — sample patches (`.lg` netlists).

## Repository map

The normative content is also available as data, so tools and agents consume the
language without parsing prose:

- `standard/grammar/loomground.ebnf` — the textual grammar, standalone (ISO/IEC 14977).
- `standard/grammar/tree-sitter/` — a tree-sitter grammar. `tree-sitter generate` builds
  the parser, AST, and editor tooling; syntax corpus tests are included.
- `standard/schema/` — JSON Schemas for the `token`, the `patch` (a policy graph as data),
  the `observation` (a vector's `expected.json`), and transport runs. Validated
  against the vectors.
- `standard/vocabulary/` — node classes, cords, the verdict lattice, declarations, the guard
  domain, risk levels, autonomy grades, and the grounding map, each as JSON.
- `standard/conformance/manifest.json` — a machine index of every vector.
- `standard/language-card.json` — a compact, agent-facing summary of the whole language.
- `llms.txt` — the agent/tool entry point: a compact guide to
  reading, emitting, and validating Loomground, kept in sync by a drift check.
- `loomground-governance` — an optional installable, data-only Python kit exposing
  these same artifacts, conformance vectors and a neutral implementation
  protocol (`src/`). It contains no parser, evaluator or host adapter.
- `tools/` — consistency checks run by CI (stdlib-only, except the
  schema↔vector check, which needs `jsonschema`).
