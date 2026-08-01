<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# Loomground

A declarative language for governing when an AI system or agent action may take
effect. A patch is a typed policy graph evaluated before release; each evaluation
is recorded so later alteration is detectable.

This repository contains the language specification: grammar, schemas,
vocabulary, and conformance vectors. It describes *what* governance applies; it
does not define execution, scheduling, storage, or communication. The
specification references no host program.

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

## Licensing

The normative prose in `standard/spec/` and the adopted claim-axes companion
standard is licensed under CC-BY-4.0. Implementations, executable grammars,
vocabulary and schema data, conformance vectors, examples, reference adapters,
and tooling are licensed under Apache-2.0. See
`LICENSES/CC-BY-4.0.txt`, `LICENSES/Apache-2.0.txt`, and `REUSE.toml`.

Per-file SPDX headers throughout; `REUSE.toml` records the precise boundary and
covers files that cannot carry one.
The tree is REUSE-compliant (checked in CI).

## Status

Pre-1.0, specification v0.8.2 (stable).
This repository carries only the language:
specification, grammar, schemas, vocabulary, and conformance vectors. Reference
implementations are out of scope. An implementation conforms by reproducing the
vectors in `standard/conformance/`.

This is a single-author specification engineered to standards discipline so
that it *could* become a standard; it is not one, and no institutional status
is claimed. §9's interoperability criterion — two implementations produced
independently of each other reproducing every vector — accordingly remains
**open**: the two existing implementations were authored within this same
AI-assisted project, so they provide differential conformance checking, not
an independence proof (see `standard/conformance/README.md`, Status).

## Versioning

The language card, conformance manifest, and Python package share one PEP 440
version. Maturity is a separate machine-readable `status`; draft builds use
alpha releases rather than mutable `.dev` versions. Before 1.0, a minor version
may change compatibility and a patch version is backward-compatible. Dependent
tools may now declare `loomground-governance>=0.8,<0.9`; `>=0.7,<0.8` remains
valid for consumers not yet migrated to v0.8.

## Provenance

This work is authored by **Loomground Contributors** and was assisted by Claude and Codex. Claude
and Codex are acknowledged as tools, not authors or co-authors.

This specification and its supporting materials were drafted with AI assistance
under human direction. The human author makes the design
decisions and is responsible for the content; AI was used as a drafting and
review tool. This assistance is acknowledged here and in `NOTICE` (which names
the tools used); it is not
recorded as authorship. An assisted commit ends with a plain assisted line
naming the tool, never an authorship or co-authorship trailer (see
`.github/CONTRIBUTING.md`; enforced in CI). The language itself is tool- and
vendor-neutral: no normative document depends on or references any model,
vendor, or agent framework.
