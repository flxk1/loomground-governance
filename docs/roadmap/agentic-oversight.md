<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# Roadmap slice — language work for agentic oversight

Status: **draft, not committed scope.** Non-normative. Nothing here is part of
the specification until it lands in `standard/` under the lockstep gate.

This slice records the *language-level* gaps that a set of open problems in
agentic oversight exposes, and what closing each would require. It names no
implementation, no vendor and no product, consistent with the neutrality rule in
`.github/CONTRIBUTING.md`.

---

## What the language already carries

Stated first, so the roadmap is not credited with work already done. The
specification already provides:

- the **principal chain** — the `on-behalf-of` binding on an authority cord, its
  acyclicity, and its projection in the observation (§6);
- the **no-amplification invariant** over grants and over grade, pairwise across
  actor-to-actor links and transitive along the chain (§6);
- **party resolution** along the chain, and human-rooted answerability (§6);
- the **autonomy-grade axis** — a policy-owned ladder with a language-owned
  comparison rule at a source gate (§7.1);
- **reservation, quorum, prohibition, temporal, redress** declarations (§6);
- the **verdict lattice** and the ordered, verdict-labelled log trace (§7.4);
- **fail-closed** treatment of every ill-formed graph.

In the vocabulary of the delegation relation

```
principal ──mandate──▶ agent ──permissions──▶ actions ──effects──▶ world
```

the language modelled the principal relation and the permissions, and not the
**mandate** — the arrow authority is conferred along. It models all four now
(G1, G2 below), and a fifth term the diagram does not show: where a release
*goes* (G7).

---

## Status

G1, G2, G3 and G4 are **closed** — the mandate and its attenuation invariant, and
`reversibility` / `uncertainty` with the re-grading rule, are in the language and
exercised by conformance vectors. Their sections below are kept as the record of
what was missing and why, because the reasoning is the durable part; each now opens
with what landed.

G5 is **open and blocked on a design decision** (see below). G6 remains open. A
seventh gap, G7, was found by testing the language against a real agent-handoff
protocol and is **closed**.

## The gaps

### G1 · No mandate — CLOSED

Authority is recorded; the purpose for which it was conferred is not. A policy
graph can state that an actor acts on behalf of a delegator, and what it may do,
but not what it was authorised to *achieve*. Without that term, no conforming
implementation can express — let alone evaluate — the proposition that an actor
satisfied its instructions while defeating their purpose.

*Candidate shape.* A `mandate` attribute on the authority cord, naming a declared
purpose, riding that cord exactly as `on-behalf-of` does. It names; it does not
compute. It adds no node class and no cord.

### G2 · No mandate attenuation — CLOSED

The no-amplification invariant bounds *grants* along the chain. Nothing bounds
purpose. A five-hop chain can therefore terminate in an actor whose declared
purpose bears no relation to the one at the root — with every grant properly
attenuated the whole way down.

*Candidate shape.* A well-formedness invariant in the shape of §6's existing one:
a delegate's mandate MUST lie within its delegator's; a graph that widens it is
ill-formed and has no effect. Attenuation composes transitively along the acyclic
chain, so no separate rule is needed — the same argument §6 already makes.

### G3 · Autonomy is static configuration — CLOSED

`vocabulary/grades.json` records grade as "a configuration attribute, not a token
field and not guardable", and `vocabulary/guard-domain.json` forbids "any
computed value" — deliberately, as "the wall between an expressive notation and a
programming language."

That wall should stay up. The pressure from agentic deployment is nonetheless
real: an autonomy level that is a function of risk, uncertainty, reversibility,
context and competence cannot be expressed at all today, because three of those
five terms are absent from the token and the fourth is not a token field.

*Candidate shape, preserving the wall.* The function is computed **outside** the
language and its result admitted as **declared** token properties — the treatment
`risk` already receives. Two additions:

- **`reversibility`** — a declared, ordered token property with the operators
  `risk` already permits;
- **`uncertainty`** — likewise declared and ordered.

Both are declared, guardable and non-computed. Neither introduces a computed
guard, and `grade` remains configuration.

### G4 · Autonomy change has no declared form — CLOSED

If an autonomy level may vary with circumstance, the language must say how it
varies without permitting a runtime mutation — which would make the observation
of a graph a function of when it was taken.

*Candidate shape.* Re-grading is a **fresh activation with a different token**,
never an edit to a granted or required grade. Every autonomy change is then an
ordinary activation with an ordinary log entry, and the observation stays a
projection of the graph rather than of its history.

### G5 · No interruptibility invariant — OPEN, blocked on design

The language can express that an action is reserved to a human, prohibited, or
subject to a deadline. It cannot express that a principal **retains the ability
to intervene** — and, more importantly, it cannot reject a graph that grants an
actor a position immune to intervention.

The vocabulary for this already exists one plane over, in the general deontic
language: the power/liability and immunity/disability correlative pairs are the
formal statement of correctability. A principal holding a power to pause,
correct, constrain or terminate correlates with a delegate under a liability; a
delegate holding an immunity correlates with a principal under a **disability**.

*Candidate shape.* A well-formedness invariant: for every actor, the root of its
principal chain retains a power over the declared intervention kinds, and no
actor may be granted an immunity against them. Fail-closed, in the shape of the
existing invariants.

*Boundary, stated plainly.* Such an invariant constrains what a policy graph may
**grant**. It says nothing about the behaviour of any system, and nothing about
action taken outside the governed path. It is a well-formedness property, not a
behavioural guarantee, and should not be read as one.

**Blocked, and the blocker is real.** The candidate shape above cannot be
implemented as written. It says no actor may be granted an immunity "against the
declared intervention kinds" — but a grant in this language is over a `kind` at a
gate, and a `kind` has no *target*. There is nothing in the graph that makes
`terminate` an act directed **at** a particular actor rather than simply an act.
Without a target, the invariant has nothing to range over, and any implementation
would be quietly weaker than the sentence promises.

Two ways out, both design decisions rather than implementation:
give a grant an optional target, which enlarges the grant model for one case; or
express interruptibility as a *reachability* property — every actor lies on a path
to a gate that reserves some intervention kind to a human — which needs no new
term but says something weaker than immunity. The second is cheaper and honest
about being weaker. Neither should be picked by an implementer alone.

### G7 · No term for where a release goes — CLOSED

Found by testing the language against a published agent-handoff protocol, in which
a lawyer moves work product from one AI platform to another. The language could say
whether an action released; it had no way to say **to whom**, so every governance
question about the handoff — where the context goes, who may see it, under what
agreement — was a question about a term that did not exist.

The tell was already in the specification: §6 said "where the party differs *across
a boundary*, the party currently responsible changes accordingly". The boundary was
load-bearing and unnamed.

Closed by `consign` on a terminal gate and the `transfer` declaration, with a
transfer-attenuation invariant that is the mandate rule applied to a lateral
relation. No second master: §7.3 already decides each egress path independently, so
a destination is a property of the egress path. A consignee is a declared id, not a
node, so the four node classes stand.

*What it deliberately does not do.* It records the purposes material travels under
and bounds them by what the releaser held. Whether a recipient honours them is
conduct, outside this specification. Testing against a real protocol is worth more
than inventing scenarios, and is how G7 was found at all.

### G6 · Meaningful control is not expressible as a measurement

Oversight can be present formally and absent functionally. The distinction is
usually decomposed into observability, intervenability, comprehensibility,
authority and timeliness — a conjunction in which any one term at zero collapses
the whole.

The language is the wrong home for the *measurement*: it computes nothing, and
comprehensibility is a property of a person, not of a graph. What the language
can carry is the **declaration** of which constituents a deployment claims, so an
observation records the claim and a consumer can check it. Whether that belongs
in the language at all is an open question this slice does not settle.

---

## Sequencing

| Step | Gaps | Lockstep reach |
|---|---|---|
| ~~1~~ | ~~G1, G2~~ | **landed** — mandate + attenuation, 5 vectors |
| ~~2~~ | ~~G3, G4~~ | **landed** — `reversibility`/`uncertainty` + re-grading, 4 vectors |
| ~~3~~ | ~~G7~~ | **landed** — `consign` + `transfer` + attenuation, 5 vectors |
| 4 | G5 | blocked: needs a target on grants, or a weaker reachability reading. A decision, not an implementation |
| 5 | G6 | open — may resolve to "not language" |

Each step is a compatibility-affecting change and implies a minor version before
1.0, per the versioning policy in `README.md`.

## Gates

A step is complete only when the lockstep gate passes — specification, grammar,
schemas, vocabulary, `llms.txt` and at least one conformance vector in
agreement — and `reuse lint` is clean.

Two vectors are load-bearing rather than illustrative:

- a delegation chain that **widens** a mandate is ill-formed and has no effect;
- a grant of an **immunity** against a declared intervention kind is ill-formed
  and has no effect.

## Standing limitation

The interoperability criterion in Conformance §9 — two independently produced
implementations reproducing every vector — remains **open**, and nothing in this
slice closes it. New vectors extend what conformance covers; they do not supply
the independence the criterion requires.
