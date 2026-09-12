<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# loomground-governance

Installable distribution of the Loomground governance language: grammar, schemas, vocabulary, conformance vectors, and a data-only Python kit.

## Problem

Programs need the language as data, and copies drift from the spec. The spec as an installable package, lockstep-checked, plus the reference validator.

## Install

```
pip install "loomground-governance @ git+https://github.com/flxk1/loomground-governance@loomground-governance-v0.11.0"
```

Pin: `loomground-governance>=0.11,<0.12`.

## Usage


```python
import loomground_governance as lg
lg.language_version()        # "0.11.0"
lg.vocabulary("verdicts")    # standard/vocabulary/verdicts.json
lg.run_conformance(impl)     # impl: a LoomgroundImplementation
```


## Example

```
in : import loomground_governance as lg; lg.language_version(); lg.vocabulary("verdicts")["alphabet"]
out: language_version: 0.11.0
     verdicts: ['auto', 'human', 'refused', 'reserved', 'prohibited']
```

## Language

`.lg`, one statement per line. Nodes `actor` · `human … role` · `gate … risk … grant` · `master`; cords `a -> b` (authority, pipe, egress); declarations `reserve <kind> by <role> when <guard>`, `prohibit`, `redress`, quorum `2 of {roles}`, `mandate`, `transfer … to … within`. ```
actor  bot7
human  alice  role dpo
gate   decide  risk high  grant bot7
reserve automated_decision by dpo when risk >= high
cord   bot7   -> decide
cord   decide -> master
```

An activation of `decide` at risk high yields `reserved`; the master withholds until alice decides. Full card: `docs/language-card.md`. Normative text: `standard/spec/`.

## Interface

| Path | Content |
|---|---|
| `standard/spec/` | `SPEC.md` (normative), `SYNTAX.md` |
| `standard/grammar/` | `loomground.ebnf` (ISO/IEC 14977), `tree-sitter/` |
| `standard/schema/` | JSON Schemas: token, patch, observation, transport |
| `standard/vocabulary/` | node classes, cords, verdicts, declarations, guards, grades, roles, grounding |
| `standard/conformance/` | 65 vectors, `manifest.json` |
| `standard/companions/claim-axes/` | 14 vectors |
| `standard/language-card.json`, `llms.txt` | language as data; agent entry |
| `src/loomground_governance/` | `LoomgroundImplementation`, `run_conformance`, `canonicalize_role`, loaders |
| `tools/check_*.py` | CI gates |

## Family

The governance-language plane. `standard/` is [`loomground`](https://github.com/flxk1/loomground) **v0.11.0**, pinned in `standard/CANONICAL`; `tools/check_canonical.py` proves byte-equality against that tag in CI. What only a plane has: the `loomground_governance` kit (`artifacts`, `conformance` runner, `protocol`, `roles`), the companions, `check_language_summary` (one version), `check_lockstep` (every declaration reaches grammar, schema, vector), and the `loomground` authoring skill. No parser, evaluator, or host adapter.

- Consumes: `loomground` v0.11.0 (the standard).
- Consumed by: `loomground-solver`, `loomground-versum`, implementations via `run_conformance`.
- Release order: `loomground` first; then re-pin here.
- Pipeline: `source → loomground-ingest → loomground-versum → loomground-solver → applied or diagnostic planes`; every stage grounds governance here.

Map, versioning, provenance, licensing: `docs/`.

## Status

0.11.0 (stable) · standard = loomground v0.11.0 · 65 conformance vectors · 14 claim-axes vectors · 12 tests · 12 CI jobs · Python ≥ 3.10. §9 independence criterion open: `standard/conformance/README.md`.

## License

Apache-2.0 — `LICENSES/Apache-2.0.txt`. CC-BY-4.0 — `LICENSES/CC-BY-4.0.txt` (`standard/spec/` prose, claim-axes companion). Boundary: `REUSE.toml`.
