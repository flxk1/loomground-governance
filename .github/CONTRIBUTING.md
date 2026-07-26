<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# Contributing

## Neutrality

The language is tool- and vendor-neutral. No normative document (`standard/`
and `llms.txt`) may depend on or reference a specific AI model, vendor,
product, or agent framework. A design note may name one only as a clearly marked
example. Non-normative provenance may name an assisting tool solely for
attribution; that acknowledgement creates no dependency or endorsement. The
standard also names no implementation —
conformance is a criterion (reproduce every vector), not a product list.

## Commit convention (enforced by the commit-discipline CI job)

- Subjects are at most 72 characters.
- Do **not** add a `Co-Authored-By: <AI tool> ...` — or any AI — trailer.
  AI tools cannot author or hold copyright; only humans can.
- An AI-assisted commit instead ends the body with a plain line naming the
  tool actually used:

  ```
  Assisted by <tool> (<vendor>); not an author or copyright holder.
  ```

## Gates (run before every commit)

```
python3 tools/check_language_summary.py # llms.txt / language-card drift
python3 tools/check_lockstep.py          # every feature reaches grammar, schema, a vector
python3 tools/check_vectors.py           # schemas validate the vectors (needs jsonschema)
python3 tools/check_companion.py         # companion skill tracks the language
python3 -m pytest                  # Python adoption-kit contract
reuse lint                    # SPDX / REUSE compliance
```

All new files carry an Apache-2.0 SPDX header (the whole tree is
single-licensed Apache-2.0; `REUSE.toml` covers files that cannot carry one).
Do not quote the raw SPDX tag string in prose — the REUSE extractor scans whole
files and chokes on it.

## Lockstep

A feature change is complete only when the spec, the grammar, the schemas, the
vocabulary, `llms.txt`, and a conformance vector agree — the lockstep gate
fails otherwise. A conformance claim is real only when both independent
implementations reproduce every vector (specification, Conformance §9).

## Versioning

`pyproject.toml`, `standard/language-card.json`, and
`standard/conformance/manifest.json` carry the same PEP 440 version;
`tools/check_language_summary.py` enforces this. Drafts use
incrementing alpha releases (`0.8.0a1`, `0.8.0a2`, …), never a mutable `.dev`
version. Promote the version to `0.8.0` and set the language-card status to
`stable` only when making the corresponding release and tag.
