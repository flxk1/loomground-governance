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
terminal gate, the `master` decision (`act` | `withhold`). An activation MAY carry
`invalid: true`, declaring that its token deliberately fails token validation and
so denotes ⊥: it contributes no expected entry and no log entry, and a runner MUST
fail the vector if a token so marked in fact validates. It also carries `log` —
the **ordered log trace**, one `{gate, verdict}` entry per activated gate in
evaluation order, concatenated across activations in activation order (the
specification, Record and Conformance). A runner MUST check it: a missing or
misordered entry is itself a conformance failure, so the mandatory record (not only
the final verdicts) is tested.

## The vector-format contract

A runner MUST observe four rules so that passing the suite tests what it
claims to, not only what a lenient runner happens to check:

1. **Reason, not only stage.** Every negative vector's `reject.json` carries
   `stage` (`"parse"` | `"apply"`) and `reason`, a code from the closed set in
   `vocabulary/reject-reasons.json`. A runner MUST check both: an
   implementation that rejects at the right stage for the wrong cause (e.g.
   raising on a pipe cycle while calling it a parse error, or rejecting a
   well-formed graph outright) fails the vector. `reason` is machine-checkable
   because the set is closed and documented against the specification section
   that makes each case ill-formed.
2. **Parse rejection is correct only where declared.** A runner MAY treat an
   exception raised while parsing as a correct rejection *only* for a vector
   whose `reject.json` declares `"stage": "parse"`. A vector declaring
   `"stage": "apply"` requires the input to survive parsing and be rejected
   specifically at the well-formedness check named by its `reason` — a runner
   that cannot parse the input at all, or that rejects every input
   indiscriminately, MUST fail an apply-stage vector even though it "rejects".
   This closes the gap the paper names: a stub that raises on every input, or
   that rejects every patch at apply, must not score as conformant.
3. **Whole-observation equality.** A patch vector's `expected.json` is
   compared to an implementation's observation by the equality the
   specification defines (specification, Conformance §9, Equality): the full
   observation object, same members, equal values, array order significant.
   A runner MUST NOT reduce the comparison to a subset of named keys; an
   extra, missing, or misordered member anywhere in `nodes`, `cords`,
   `reservations`, or `redress` is a conformance failure, not a partial pass.
   The same whole-object rule applies to each `transport.json` run: every
   gate named in `expected`, every field of a `log` entry present in the
   vector (including `token`/`observed` where a vector carries them, below),
   and the full ordered `log` array.
4. **Determinism vectors.** A vector of kind `determinism` (`input.lg` +
   `transport.json`) carries two additional `transport.json` fields: `repeat`
   (a positive integer) and `permutations`, a list of `{file, log}` entries.
   Each `file` (a path relative to the vector's directory) denotes the same
   policy as `input.lg` with its declarations textually reordered; its `log`
   is the ordered log trace that declaration order fixes. A runner MUST
   evaluate `activations` against `input.lg` `repeat` times and fail the
   vector unless every run's per-gate verdicts and master decisions equal
   `expected` and its log equals `log` (specification §7.5, rule 1). It MUST
   then evaluate `activations` once against each permutation `file` and fail
   the vector unless the per-gate verdicts and master decisions equal the
   same `expected` (rule 2) and the log equals that entry's `log` (rule 3).
   An entry's `log` equals the top-level `log` wherever the pipes over the
   activated gates admit a single topological order; where they admit
   several, it is the log the declaration-order tie-break (specification
   §7.4) fixes for that file's declaration order, and may differ from the
   top-level `log`. A determinism vector carries no `expected.json`: because
   the canonical observation's `nodes`/`cords`/`reservations` order is
   declaration order (specification §9, Order), reordering declarations
   changes that order by construction, so only the dynamic result —
   `expected` and the logs in `transport.json` — is what a determinism
   vector pins.

The record (§7.4) requirement that a log entry carry both the declared
token and the host-observed facts is pinned, where a vector exercises it, by
two optional `transport.json` log-entry fields: `token` (the declared token
as presented) and `observed` (`{kind, risk}`, the host-observed `kind` and
gate-computed `risk` that actually produced the verdict). Most vectors omit
both because the declared and observed values coincide and the distinction
is moot; `record-declared-and-observed` is the vector that exercises the case
where they diverge (schema/transport.schema.json).

## The four vector kinds: patch, determinism, token, negative

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
- `topo-fanout-fanin-declared-order` / `topo-fanout-fanin-declared-order-variant` —
  a second fan-out/fan-in topology, distinct from `pipe-fanout`'s: two gates that
  pipe from a common source and both into a common sink, with no edge between
  them, so the pipe relation genuinely admits two topological orders. The
  declaration-order tie-break (SPEC §7.4) fixes the log; the `-variant` vector
  declares the two incomparable gates in the opposite order and so expects the
  opposite log order, with the same per-gate verdicts and master decision —
  pinning that the tie-break, not an implementation's internal traversal, is
  what the log follows. The fan-in gate's `refused` (joined from one
  incomparable predecessor) over the other's `auto` also exercises restrictions
  composing over this second topology.
- `prohibit-grade-reservation-precedence` — one gate combines an unguarded
  prohibition, a reservation, and a required grade a maximal granted grade
  would otherwise satisfy, all on the same kind: `prohibited`, withhold. Pins
  that a prohibition beats a grant, a high grade, and a same-kind reservation
  together, not merely pairwise (cf. specification §7.1, probe H3a).
- `record-declared-and-observed` — a token declares `risk low` at a gate whose
  floor is `high`; the gate-computed risk (`high`) matches a reservation the
  declared value would not. The log entry carries both the declared token and
  the host-observed facts (SPEC §7.4) — pinning that the record, not only the
  final verdict, is auditable.

**Determinism vectors** — `input.lg` + `transport.json` with `repeat` and
`permutations` (no `expected.json`; see The vector-format contract, above):
- `determinism-repeat-permute` — the `draft-decide-run` graph; each
  activation reaches one gate, so there is no topological tie. Repeating the
  same activations three times, and running them once against a
  declaration-order permutation of the same policy, MUST reproduce the same
  per-gate verdicts, master decisions, and log trace every time
  (specification §7.5, rules 1–3).
- `determinism-topo-tie` — a fan-out/fan-in graph with a three-way
  topological tie (A fans out to B, C, E; all three fan in to D). Repeats
  MUST reproduce the same result (rule 1); three declaration-order
  permutations MUST reproduce the same per-gate verdicts and master decision
  (rule 2); the log is the one the declaration-order tie-break fixes for each
  file — unchanged where only the actor and cords move, `A, E, C, B, D` and
  `A, C, E, B, D` where the gates are reversed or rotated (rule 3). Pins that
  log order under reordering follows §7.4, not the original file.

**Token vectors** — `tokens.json`, a list of `{valid, token}` an implementation
MUST classify identically (see the specification, The token):
- `token-validation` — a well-formed token has `id`, `kind`, `risk`, `party`,
  `provenance`, and an optional `tags` (an array of strings); each defect (missing
  field, out-of-domain `risk`, malformed `provenance` or `tags`, non-object) is
  rejected.

**Negative vectors** — input `.lg` + `reject.json`
(`{"stage": "parse" | "apply", "reason": <code>}`, `reason` a code from the
closed set in `vocabulary/reject-reasons.json`; see The vector-format
contract, above) pinning what MUST be rejected, fail-closed, and why:
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

Aligned to specification v0.11.2 (stable). This repository — `loomground` — carries
only the language: `spec/`, `grammar/`, `schema/`, `vocabulary/`, and this
`conformance/` directory. It contains no implementation of its own; the
non-normative companion skill under `skills/loomground/` is a generator that
derives agent-facing guidance from the vocabulary and manifest files
(`skills/loomground/make_skill.py`) — it evaluates nothing and is not a
conformance checker. Any implementation, wherever it lives, demonstrates
conformance the same way: by reproducing every vector. Each `expected.json` is
the observation a conforming implementation emits; each negative vector
rejects at the stage shown; `token-validation` classifies identically.

The §9 interoperability criterion — two implementations produced
independently of each other reproducing every vector — remains **open**.
Both existing implementations were authored within the same AI-assisted
project by the same author-fleet, with no controlled isolation between them,
so their agreement is differential verification (valuable for catching
divergence) rather than an independence proof (which requires convergence
from the specification text alone). The criterion is met when an
implementation produced without access to this project's implementations
reproduces every vector.
