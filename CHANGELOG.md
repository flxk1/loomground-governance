<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# Changelog

## [0.11.0](https://github.com/flxk1/loomground-governance/compare/loomground-governance-v0.10.0...loomground-governance-v0.11.0) (2026-08-22)


### Features

* **roles:** recover role canonicalization + vocabulary ([55aab13](https://github.com/flxk1/loomground-governance/commit/55aab138f3876e43b3ba9f169bda7de793622afb))
* **roles:** recover role canonicalization + vocabulary ([96b8797](https://github.com/flxk1/loomground-governance/commit/96b8797ef6710e6c7281a78bbbc8b5ff2594d25b))
* **schema:** token schema for governed-risk model (PROM-001) ([e1b339c](https://github.com/flxk1/loomground-governance/commit/e1b339cd6237b60647a26349b02ed7d478d5defa))
* **spec:** observed-kind and governed risk (PROM-001) ([f2439a1](https://github.com/flxk1/loomground-governance/commit/f2439a15a420a3727289eca7824e8de4f65af390))
* **spec:** token integrity — observed kind, gate-computed risk (PROM-001, slice 1/5) ([f7ff301](https://github.com/flxk1/loomground-governance/commit/f7ff301d6d737d17af470cddee7556892e08fbac))


### Bug Fixes

* **release:** sync language artifacts to pyproject 0.10.0 ([4662971](https://github.com/flxk1/loomground-governance/commit/466297162d14baca6977bd4d6a28fb93ed848abb))
* **release:** sync language artifacts to pyproject 0.10.0 ([f8b20f8](https://github.com/flxk1/loomground-governance/commit/f8b20f895b75fefc44dfdc8b19ef4098e7d32782))

## [0.10.0](https://github.com/flxk1/loomground-governance/compare/loomground-governance-v0.9.0...loomground-governance-v0.10.0) (2026-08-19)


### Features

* **grammar:** align autonomy ladder to ISO/IEC 22989 §5.13 (0–6) ([6cdc0a4](https://github.com/flxk1/loomground-governance/commit/6cdc0a4d5ea5941d10d965d55916edd35bf627aa))
* **grammar:** align autonomy ladder to ISO/IEC 22989 §5.13 (0–6) ([799f0e3](https://github.com/flxk1/loomground-governance/commit/799f0e3724adc3c05201285f37e8fe2f9a0fd4ab))

## [0.9.0](https://github.com/flxk1/loomground-governance/compare/loomground-governance-v0.8.2...loomground-governance-v0.9.0) (2026-08-18)


### Features

* **mandate:** declare the purpose authority is conferred for ([9ee8a6f](https://github.com/flxk1/loomground-governance/commit/9ee8a6fc124a3f3552c822e288e343e127df41a6))
* **token:** reversibility and uncertainty, declared and ordered ([abcc3cc](https://github.com/flxk1/loomground-governance/commit/abcc3cc26f78fc59185f7a269a2f730a8568c9fb))
* **transfer:** name where a release goes and what it travels under ([4608d56](https://github.com/flxk1/loomground-governance/commit/4608d5654a0aa83dd2292901c242b3b7ec388489))


### Documentation

* decouple release docs from a named consumer (general FOSS repo) ([51b2e3b](https://github.com/flxk1/loomground-governance/commit/51b2e3b854a87cb07d2991ac8a9c2c93b9439fa1))
* **roadmap:** language gaps for agentic oversight ([e467723](https://github.com/flxk1/loomground-governance/commit/e467723ee701c9dba3d3f2d98ed36dc2ea9a2aac))
* **roadmap:** language gaps for agentic oversight ([c9b35dc](https://github.com/flxk1/loomground-governance/commit/c9b35dc39bd90114f31622c7df83afc233c1673a))
* **roadmap:** mark the closed language gaps and record the blocked one ([3d085bd](https://github.com/flxk1/loomground-governance/commit/3d085bd404511c4f993e3a19596891c59445d0ae))
* **spec:** name where the language locates correctability ([cf26bfa](https://github.com/flxk1/loomground-governance/commit/cf26bfa2078cbd1eb917155e71bf5a2dab706918))

## [0.8.2](https://github.com/flxk1/loomground-governance/compare/loomground-governance-v0.8.1...loomground-governance-v0.8.2) (2026-08-01)


### Documentation

* add autonomy grades to the vocabulary file list ([3184991](https://github.com/flxk1/loomground-governance/commit/3184991dfb8f8e8645db86ccfa00ff57a733cb51))
* add autonomy grades to the vocabulary file list ([183b9fd](https://github.com/flxk1/loomground-governance/commit/183b9fd4f89ddd7d4914c9622f28342441ba9cda))

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
