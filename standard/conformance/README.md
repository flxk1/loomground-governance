<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# Loomground conformance vectors

These vectors define conformance for a Loomground implementation. An
implementation conforms if and only if it reproduces every vector (see the
specification, Conformance). The vectors name no implementation and assume none;
implementers supply their own runner.

## The observation schema (v0.7)

A patch vector's `expected.json` records the **observation** of a policy graph:

- `nodes` — `{id, class}` for each node (`class` ∈ `actor` | `human` | `gate` |
  `master`); a `human` carries its `role`, a `gate` its `risk_floor` and, if declared,
  its `grade_required` (a graded gate is a source gate); an `actor` carries its `grade`
  (the granted autonomy grade) and its `on_behalf_of` (its delegator — one link of the
  principal chain) if declared; an `actor` or `gate` carries its `party` — on a
  partyless delegate, resolved along the chain. Listed in declaration order, the
  master last.
- `cords` — `{from, to, type}` (`type` ∈ `authority` | `pipe` | `egress`), in
  declaration order.
- `reservations` — the graph-level reservation declarations
  `{kind, by[, when][, duration, on_elapse]}`. A reservation keys on the
  token's `kind`; it is not attached to one gate. A quorum `by` target is canonical
  (`<m> of {roles}` / `role and role`); `duration`/`on_elapse` appear only when a
  temporal window is declared.

A `transport.json` adds a run: `activations` (each `{actor, source, token}`,
where `actor` is the proposing actor and `source` a source gate) and the `expected` per-gate `verdict` and, for a
terminal gate, the `master` decision (`act` | `withhold`). It also carries `log` —
the **ordered log trace**, one `{gate, verdict}` entry per activated gate in
evaluation order, concatenated across activations in activation order (the
specification, Record and Conformance). A runner MUST check it: a missing or
misordered entry is itself a conformance failure, so the mandatory record (not only
the final verdicts) is tested.

## The three vector kinds

**Patch vectors** — input `.lg` + `expected.json` (+ optional `transport.json`):
- `draft-decide` — static projection: a routine gate and a decide gate that
  reserves a high-risk automated decision; two terminal gates.
- `draft-decide-run` — one transport: routine → `auto` → act; the reserved path →
  `reserved` → withhold.
- `multi-hop-pipeline` — strictest-wins propagation: an interior gate's `reserved`
  verdict joins to the terminal gate, which withholds.
- `multi-issue-reservations` — two reservations on distinct kinds coexist.
- `rack-approval` — the `rack` abstraction expands to two parallel pipelines.
- `redress-decl` — a released decision declared contestable: redress by an appeals
  role, empowered to overturn, within a window.
- `guard-tags` — a tag-guarded reservation (information-flow): `tags contains
  non_eu` → `reserved` → withhold; without the tag → `auto` → act.
- `prohibit-tags` — a guarded prohibition: `tags contains untrusted_model` →
  `prohibited` → withhold; without the tag → `auto` → act.
- `grade-auto` / `grade-human` — granted L3 ≥ required L2 → `auto` → act; granted L1 <
  required L3 → `human` → withhold (language-determined at the source gate).
- `grade-ungraded-at-graded` — ungraded actor at a source gate requiring L2 → `human`,
  fail-closed.
- `grade-graded-at-ungraded` — static projection: a granted grade round-trips onto the
  actor; the gate carries no `grade_required`; no verdict pinned (ungated = policy, §10).
- `grade-join` — a graded source gate's grade-`human` joins strictest-wins to a plain
  piped terminal; the proposing actor's grade is read, not a second grantee's. Grade
  lives on the source gate, never on a piped gate.
- `grade-reserved-precedence` — at a source gate that is both grade-gated and reserved on
  the token's kind, step (3) `reserved` pre-empts the step-(4) grade comparison.
- `party-projection` — a gate's `party` projects as a node attribute in the observation.
- `obo-projection` — the delegation binding projects: the delegate's actor node
  carries `on_behalf_of` naming its delegator.
- `obo-chain-attenuation` — a three-link principal chain (bot → mgr → ceo); pairwise
  no-amplification composes along the acyclic chain; well-formed.
- `obo-human-root` — the chain terminates at a `human`: answerability anchored,
  no authority conferred; the delegate releases on its own grant (`auto` → act).
- `party-inheritance` — party resolution along a three-link chain: a partyless
  middle resolves through to the root's party, a declared party wins over the
  chain, and a partyless delegate takes the *nearest* declared party.
- `reserve-quorum` — a quorum reservation target projects verbatim in canonical form
  (`<m> of {roles}` and `role and role`); a matching token yields `reserved`.
- `reserve-temporal` — a reserved kind's `duration` window and `on_elapse` (`halt`/`proceed`)
  project onto the reservation; the elapse resolution itself is the host's.
- `egress-obligation` — an obligation on a terminal gate is attached (declared) and not
  projected; an `auto` gate still releases.
- `refused-precedence` — an unauthorized actor yields `refused`; `refused` pre-empts
  `reserved`, and `prohibited` pre-empts `refused`.
- `grant-narrowing` — a narrowed grant `a[kind]` / `a[kind:risks]` scopes authority; a
  token outside the grant's kind or risk scope is `refused`.

**Token vectors** — `tokens.json`, a list of `{valid, token}` an implementation
MUST classify identically (see the specification, The token):
- `token-validation` — a well-formed token has `id`, `kind`, `risk`, `party`,
  `provenance`, and an optional `tags` (an array of strings); each defect (missing
  field, out-of-domain `risk`, malformed `provenance` or `tags`, non-object) is
  rejected.

**Negative vectors** — input `.lg` + `reject.json`
(`{"stage": "parse" | "apply"}`) pinning what MUST be rejected, fail-closed:
- `reject-human-authority`, `reject-agent-to-master`, `reject-pipe-cycle`,
  `reject-unknown-target`, `reject-bad-risk` (apply-time);
- `reject-guard-id`, `reject-guard-provenance` — the no-id wall on a reservation
  guard; `reject-prohibit-guard-id`, `reject-prohibit-guard-provenance` — the same
  wall on a prohibition guard (apply-time);
- `reject-bad-grade` — a grade outside the active ladder (on both carrier positions);
  `reject-delegation-grade-amplify`, `reject-delegation-grade-from-nothing` — a delegate
  grade above the delegator's (pairwise) and a graded delegate under an ungraded
  delegator (apply-time);
- `reject-delegation-risk-amplify` — a delegate's granted risk set over a kind exceeds
  the delegator's; no-amplification (§6) makes the graph ill-formed;
  `reject-delegation-ungranted-delegator` — the empty-set corner: a delegate
  granted at a gate where its actor-delegator holds no grant (both apply-time);
- `reject-obo-cycle` — a cycle in the on-behalf-of relation; the principal chain
  must be acyclic; `reject-obo-undeclared` — on-behalf-of naming an undeclared
  node; `reject-obo-duplicate` — a second delegator on the same actor (all
  apply-time);
- `reject-obligation-undeclared-gate` — an obligation `on` an undeclared gate
  (apply-time);
- `reject-missing-arrow`, `reject-unknown-keyword` (parse-time);
- `reject-rack-unknown`, `reject-rack-arity` — a failed rack expansion (unknown
  rack name; missing binding) rejects at parse: the pre-pass precedes the grammar.

## Status

Aligned to specification v0.8.2 (stable). Every vector — the v0.7.0 suite and the
three new in the v0.8 cycle (`reject-rack-unknown`, `reject-rack-arity`,
`reject-obligation-undeclared-gate`) — has been reproduced by two
implementations, which this repository does not name as products: the
specification states criteria, not products, and any implementation
demonstrates conformance the same way — by reproducing every vector. The
*standard* — this directory's parent, `standard/` — carries no implementation:
grammar, schemas, vocabulary, and vectors only, no code. One of the two
implementations is bundled elsewhere in this repository, outside `standard/`,
as the non-normative companion skill's checker (`skills/loomground/`); it is
excluded from the §9 count below because it was authored inside this project,
not independently of it. The other remains a separate, unnamed project.
(`reject-obligation-undeclared-gate` caught a real accept-and-defer gap in
each implementation independently before landing — the vectors are doing
their job.) Each `expected.json` is the observation a conforming
implementation emits; each negative vector rejects at the stage shown;
`token-validation` classifies identically.

The §9 interoperability criterion — two implementations produced
independently of each other reproducing every vector — remains **open**.
Both existing implementations were authored within the same AI-assisted
project by the same author-fleet, with no controlled isolation between them,
so their agreement is differential verification (valuable for catching
divergence) rather than an independence proof (which requires convergence
from the specification text alone). The criterion is met when an
implementation produced without access to this project's implementations
reproduces every vector.
