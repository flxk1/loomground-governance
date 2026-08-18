<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# ADR 001: The mandate, and why purpose attenuates

- Status: Accepted
- Date: 2026-08-17
- Decision owner: product owner
- Scope: the `mandate` declaration and the mandate-attenuation invariant (§6)

## Context

The delegation relation is `principal --mandate--> agent --permissions--> actions
--effects--> world`. The language already modelled three of those four arrows: the
principal chain via `on-behalf-of`, the permissions via grants and grades, and the
effects at the master. It did not model the **mandate** — the purpose for which
authority was conferred.

The consequence was structural, not cosmetic. A five-hop chain could terminate in
an actor whose declared purpose bore no relation to the one at its root, with
every grant correctly attenuated the whole way down, and nothing in the language
could say so. An implementation could not even express the proposition that an
actor satisfied its instructions while defeating their purpose.

## Decision

### 1. A mandate is a declared set, on an actor

`mandate <purpose>` or `mandate { <purpose>, … }`, in the same register as
`grade`: configuration on an actor, not a token field. A single purpose may be
written without braces, mirroring how `risk set` admits a single value.

A **set** rather than a single id, because attenuation then has an obvious and
checkable meaning — subset — which is exactly the shape the existing
no-amplification invariant already uses for granted `risk` sets. No new comparison
rule had to be invented.

### 2. Not guardable, and not computed

`mandate` does not enter the guard domain, which stays `{kind, risk, party,
tags}`. `guard-domain.json` calls that restriction "the wall between an expressive
notation and a programming language", and a purpose-matching guard would be the
first crack in it. The mandate is declared, projected, and attenuation-checked;
nothing computes over it.

### 3. An undeclared mandate is the empty set, not a wildcard

The alternative — undeclared means unbounded — was rejected. It would make the
invariant vacuous exactly where it matters: an unmandated delegator could confer
any purpose at all, which is the amplification the invariant exists to prevent.

The chosen rule mirrors grade's, which the specification already states: *"if the
delegator is ungraded, the delegate MUST also be ungraded."* An actor cannot
confer a purpose it was not itself given. A root actor with no delegator may
declare any mandate freely; the constraint binds actor→actor links only.

This is also why the change is backward-compatible in practice: a graph declaring
no mandate anywhere is unconstrained by the invariant, and all 47 pre-existing
conformance vectors reproduce byte-identically.

### 4. A mandate confers nothing

A grant says *what* an actor may do; a mandate says *what for*. They are
independent. An action within a mandate but outside a grant is `refused` exactly
as before, and a mandate never widens authority. Conflating the two would have
made the mandate a second, weaker grant mechanism.

### 5. The language records purpose and bounds narrowing — nothing more

Whether a delegate's conduct in fact served its mandate is not a graph property.
It depends on what the agent did, which the language never sees. So the
specification says exactly two things: the purpose an actor was given, and that
delegation may only narrow it. Judging conduct against a mandate is a host's or a
reasoner's job, and §6 says so explicitly so the declaration is not over-read.

### 6. Attenuation composes; no separate chain rule

As with grants and grade, the pairwise invariant over an acyclic relation is
transitive, so no chain-level rule is needed. `mandate-chain-attenuation` pins
that over three hops.

## Consequences

**Gained.** A deep delegation chain becomes analysable on purpose as well as on
authority, and the widening case is rejected fail-closed like every other
well-formedness violation. This is the term the semantic-monitoring and
principal–agent problems were missing; downstream planes can now ground a mandate
as a span claim and test a trajectory against it.

**Cost.** One more declaration on a language heading for 1.0, and a new keyword in
the actor clause. Lockstep reach was ten artefacts plus five vectors — that is the
price of the discipline working.

**Given up.** No purpose *hierarchy*. `deploy` does not subsume `deploy-staging`;
subset is plain set inclusion over opaque ids. A hierarchy would need a
declaration of the ordering, which is policy, not language. Deployments wanting
one express it by enumerating the narrower set.

**Open.** Whether 1.0 ships with the mandate or freezes without it is a
scheduling call, not a design one. Shipping 1.0 first would freeze the gap this
work exists to close.
