<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright 2026 flxk1 -->
# Claim-axes companion profile

**Companion standard — claim-axes/1. Status: adopted 2026-07-22 (P4 placement
ruling).**

A companion document beside the Loomground language, not part of it. The
language's scope partition (SPEC §10) excludes communication; this companion
therefore defines no envelopes, no negotiation, and no transport. It defines
one thing: the **shared semantic vocabulary** for the claim-axes structural
schema that Loomground tools exchange inside their own, tool-owned
`reasoning.interop` records, plus the closed decision sets a semantic profile
may declare over that vocabulary.

Operational interoperability remains tool-owned (solver ADR 001): every tool
keeps its adapter, limits, and operational contract at its own boundary. What
this companion owns is the vocabulary those adapters must agree on, proven by
the shared conformance vectors in `vectors/`.

## 1. Schema identity

The wire identifier is frozen for compatibility with the shipped M1
implementations:

```
loomground.versum.claim-axes/v1
```

The `versum` segment records the schema's origin; it does not grant Versum
ownership of this vocabulary. A future major version may re-home the
identifier; v1 never will.

## 2. The record

A claim-axes record is the `structural_evidence` object of an interop
candidate:

```json
{"schema": "loomground.versum.claim-axes/v1",
 "axes": {"predicate": "causes", "modality": "asserted"}}
```

Normative constraints (each backed by a vector):

- The object carries **exactly** the members `schema` and `axes`; any other
  member is a rejection, not an extension point.
- `axes` is **required**, and must be an object. A conforming producer always
  emits the member; its absence signals malformed or version-skewed output,
  never "no axes". The empty object is valid.
- Recognized axes, in canonical order: `predicate`, `modality`, `polarity`,
  `quantification`, `domain`. Any other key is out of bounds.
- Every present value is a string containing at least one non-whitespace
  character, at most **256** characters. Non-string, empty, blank-only, and
  oversized values are rejections.
- Consumers reject fail-closed: anything outside these bounds is an error,
  never a silently dropped or repaired value.

## 3. Profiles

A **semantic profile** is a versioned declaration of one decision per axis,
validated against closed per-version sets. A profile is a declaration attached
to inert output, not a semantic compiler: an unrecognized decision is a
construction error, never a silently serialized claim.

Profile `loomground.versum.claim-axes.inert` version `0.1.0` — the M1 profile,
recorded in [`profile-inert-0.1.0.json`](profile-inert-0.1.0.json) — allows
exactly:

| axis | closed set |
| --- | --- |
| predicate | `descriptive` |
| modality | `inert` |
| polarity | `annotation` |
| quantification | `inert` |
| domain | `inert` |

Later semantic versions (typed relations, deontic operators, scope behavior,
retrieval selection) arrive as **new** profile versions with their own closed
sets — never by widening an existing version's sets. Ruling D′ is permanent:
`polarity` may in some future version map to negation or annotation, never to
an auto-minted attack relation.

## 4. Conformance

`vectors/manifest.json` indexes the shared vectors (kind `wire-record`): each
vector file carries a `record` and a `valid` flag. An implementation conforms
when it accepts every valid record and rejects every invalid one. Two
implementations exercise every vector at adoption — the Solver's
`ClaimAxesDecoder` (consumer) and Versum's `candidate_from_claim` emission
(producer) — as differential conformance checks; the language's independence
criterion (SPEC §9) applies to this companion the same way it applies to the
core, and remains open for the same reason (both implementations share this
project's authorship).

Tools vendor these vectors as versioned copies for differential testing; the
copies carry no runtime adapter code and this companion ships none.
