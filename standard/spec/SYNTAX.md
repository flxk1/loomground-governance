<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright 2026 flxk1 -->
# Loomground — concrete syntax

## A companion to the Loomground specification: the textual surface

**Companion — Version 0.8 (draft).**

## Abstract

This document defines Loomground's concrete textual *netlist* surface. A netlist
program denotes an abstract policy graph (the specification, Nodes; Connections
and activation); it
adds no expressiveness, and a program is well-formed if and only if the abstract
policy graph it denotes is well-formed (the specification, Terminology and
conformance). Where this document and the specification appear to differ, the
specification governs: this surface is normatively subordinate to it. This
companion defines no mechanism of execution, scheduling, storage, presentation, or
communication; those are outside the specification and outside this document.

## 1. Scope

This document specifies the lexical grammar, context-free grammar, cord
legality, one worked example, and a macro notation (*rack*) that expands to base
grammar. It introduces no node class, cord type, token field, verdict, or
declaration beyond those defined in the specification, and it allocates no
responsibility beyond the specification. The four node classes are exactly
`actor`, `human`, `gate`, and `master`
(the specification, Nodes); the three cord types are exactly authority, pipe, and
egress (the specification, Connections and activation); there is exactly one token
type and one master.

The conformance criteria are those of the specification (Conformance). This document
adds none. A surface program that does not denote a well-formed policy graph has no
effect (fail-closed); the disposition of an ill-formed program is the disposition
fixed by the specification, not by this notation.

## 2. Lexical rules

- The textual surface is a sequence of lines; encoding is UTF-8.
- One statement per line. A `#` begins a comment that runs to end of line. Blank
  lines and comment-only lines carry no statement.
- Tokens are separated by runs of spaces or tabs, treated as a single separator.
- Identifiers are case-sensitive.
- Declarations are order-independent in meaning. A cord statement SHOULD name only
  nodes declared on earlier lines; a writer of the textual surface SHOULD emit node
  declarations before cord statements. A cord that names an undeclared node denotes
  an ill-formed policy graph (the specification, Connections and activation) and has
  no effect.

## 3. Grammar (EBNF, ISO/IEC 14977)

```ebnf
program      = { line } ;
line         = [ statement ] , [ comment ] , newline ;
statement    = actor decl | human decl | gate decl | cord
             | reserve decl | prohibit decl | obligation decl | redress decl ;

actor decl   = "actor" , id ,
               { "party" , id | "on-behalf-of" , id | "grade" , grade-value
               | "mandate" , purpose set | "name" , text-to-eol } ;
purpose set  = purpose | "{" , purpose , { "," , purpose } , "}" ;
purpose      = id ;
human decl   = "human" , id , { "role" , id | "name" , text-to-eol } ;
gate decl    = "gate" , id , { gate opt } , [ grant clause ] ;
gate opt     = "risk" , risk-value | "grade" , grade-value | "party" , id | "name" , id ;   (* risk = floor; grade = required threshold, source gate only (apply-checked) *)
grant clause = "grant" , grant , { grant } ;   (* MUST be last on the line; consumes every remaining token as a grant, e.g. `grant a b` *)
grant        = id | id , "[" , kind , { "," , kind } , "]"
             | id , "[" , kind , ":" , risk set , "]" ;
risk set     = risk-value , { "," , risk-value } ;

cord         = "cord" , endpoint , "->" , endpoint ;
endpoint     = id | "master" ;

(* --- governance declarations: policy-global, keyed on the token's `kind` (matched by guard); only `obligation` names a gate, via `on id` --- *)
reserve decl = "reserve" , kind , "by" , target , [ "when" , guard ] ,
                                  [ "duration" , duration , ":" , on-elapse ] ;
prohibit decl   = "prohibit" , kind , [ "when" , guard ] ;
obligation decl = "obligation" , obligation , "on" , id ;
redress decl    = "redress" , kind , "by" , role , [ "overturn" ] , [ "within" , duration ] ;

target       = role | role , "and" , role
             | number , "of" , "{" , role , { "," , role } , "}" ;
guard        = guard-field , guard-op , guard-value ;
guard-field  = id ;   (* domain {kind, risk, reversibility, uncertainty, party, tags}; checked at apply *)
guard-op     = ">=" | "=" | "contains" ;
guard-value  = risk | id ;
on-elapse    = "halt" | "proceed" ;
obligation   = "ai-interaction-disclosure" | "synthetic-content-marking"
             | "emotion-or-biometric-disclosure" | "deepfake-disclosure"
             | "data-minimisation" | id ;

risk         = "low" | "medium" | "high" | "critical" ;
risk-value   = risk | id ;   (* any id at parse; a value outside the risk domain, or a rack $-placeholder, is rejected at apply *)
grade        = "L0" | "L1" | "L2" | "L3" | "L4" ;   (* default ladder literals *)
grade-value  = grade | id ;   (* any id at parse; a value not a level of the active ladder is rejected at apply, like risk-value *)
kind         = id ;   role = id ;   tag = id ;
duration     = number , ( "m" | "h" | "d" ) ;
id           = letter , { letter | digit | "-" | "_" } ;
number       = digit , { digit } ;
text-to-eol  = { ? any character except newline ? } ;
comment      = "#" , { ? any character except newline ? } ;
letter       = "A" .. "Z" | "a" .. "z" ;
digit        = "0" .. "9" ;
```

Notes on the grammar, each tied to the abstract language:

- A `gate` is the governed checkpoint at which an actor acts and a verdict is
  produced (the specification, Nodes). A gate that sources a `pipe` cord is an
  interior gate; a gate that egresses to the master is a terminal gate.
- **Grade** is a configuration attribute — not a token field, not guardable (a guard
  MUST NOT range over `grade`). `grade` on an `actor` is the *granted* grade; `grade` on
  a `gate` is the *required* grade, which makes it a **source gate** (a `grade` on a
  piped, non-source gate is ill-formed at apply). Written `L0..L4` by default, but the
  lexer accepts any identifier (so a `rack` `$`-placeholder expands, §7); a value not in
  the active ladder is rejected at **apply**, not parse (`reject-bad-grade`). The
  comparison rule, its fail-closed disposition, and the delegation grade bound are
  normative (the specification, §6, §7.1; pinned by `reject-delegation-grade-amplify`,
  `reject-delegation-grade-from-nothing`). The ladder itself — levels, meanings, order —
  is policy (`vocabulary/grades.json`).
- **Risk** on a `gate` is a *floor* — a lower bound in the `risk` order; a token there is
  treated as at least that level (the specification, The token). Per-activation `risk` is
  a property of the token, not the gate. Written `low|medium|high|critical`, but the lexer
  accepts any identifier (`risk-value = risk | id`; a `rack` `$`-placeholder expands, §7);
  a value outside the domain is rejected at **apply**, not parse (`reject-bad-risk`).
- A guard ranges over exactly the declared token properties `kind`, `risk`,
  `reversibility`, `uncertainty`, `party`, and `tags`, and MUST NOT range over `id` or
  denote a computed value (the specification, Governance declarations). `tags` is a set
  of declared, non-`id` categories tested by membership (`tags contains <tag>`).
  `reversibility` and `uncertainty` are ordered properties admitted on exactly the terms
  `risk` is: the token asserts them and the language only compares them, so a host may
  compute a value by any means and hand it in — the restriction binds the notation, not
  the host. This restriction and
  the valid `(field, op)` pairings (`kind`/`party` with `=`, `risk`/`reversibility`/
  `uncertainty` with `>=`|`=`, `tags` with `contains`) are enforced at **apply**, not at parse: the surface accepts
  a generic `<field> <op> <value>` guard, and a guard over `id` or `provenance` (or an
  invalid pairing) parses but is rejected at apply, exactly as a `risk` value outside
  the domain is. The separation-of-duty distinctness of a quorum target is evaluated
  over the parties recorded in the token's `provenance`, not over `role`.
- `reserve <kind> by <target>` and `prohibit <kind>` attach to a gate. When a token's
  `kind` matches (and any `when` guard holds), the gate's verdict is `reserved` (the
  action is referred to a human role; a separation-of-duty measure) or `prohibited`
  (the action is never released and never discharged, taking precedence over any
  authority an actor holds). *Which* kinds are reserved or prohibited — to whom and on
  what basis — is policy, not language.
- A `reserve` declaration MAY carry a `duration` (deadline, window, expiry,
  cooling-off) and its on-elapse resolution (`halt` or `proceed`). The duration and
  its resolution are declared in the surface; the measurement of elapsed time is
  outside the specification.
- An `obligation … on <gate>` declares an obligation attached on egress — for example
  the transparency obligations of Regulation (EU) 2024/1689 (AI Act) Art. 50: AI-
  interaction disclosure (Art. 50(1)), synthetic-content marking in a machine-readable
  format (Art. 50(2)), emotion-recognition or biometric-categorisation disclosure
  (Art. 50(3)), deepfake disclosure (Art. 50(4)). A `data-minimisation` obligation
  derives illustratively from Regulation (EU) 2016/679 (GDPR) Art. 5(1)(c), not from
  Art. 50. The named gate MUST be declared: an obligation `on` an undeclared gate is
  ill-formed at apply, like every other undeclared-node reference. The surface
  provides only the point of attachment; the discharge of an
  obligation is outside the specification, and the surface allocates the duty to no
  one.
- A `redress <kind> by <role>` declaration makes a released decision of a matched
  `kind` *contestable*: a fresh re-examination by `<role>` is owed and recorded.
  `overturn` qualifies that role as empowered to reverse the outcome, not merely
  review it; `within <duration>` declares the appeal or recall window. The language
  declares and records the right; the re-examination is a fresh activation and
  any reversal or recall is outside the specification. Cf. GDPR
  Art. 22(3) (contest and human intervention), Arts. 77–79 / Charter Art. 47
  (effective remedy), and AI Act Art. 14(4) (intervene, override, halt). Redress
  adds no cord and no node; the policy graph stays forward-only.
- A `grant` clause MUST be the last clause on a gate line: it consumes every remaining
  token on the line as a grant. Place `risk`, `party`, and `name` before it.
- `grant <actor>` on a gate line and an `authority` cord `cord <actor> -> <gate>`
  denote the same authority conferral; a writer MAY emit either. A `grant` MAY narrow
  the conferral to particular `kind` classes, and to a particular set of `risk` levels
  over a `kind`, expressing the granted authority of that actor at that gate over that
  `kind`. These are declared grant facts and denote no computed value.
- An `actor` declaration MAY carry `on-behalf-of <id>`, the delegation binding: the
  declaring actor is the *delegate*, the named node the *delegator* — a declared
  `actor` or a declared `human`. This rides the authority cord as an attribute and
  adds no node class and no cord. The bindings form the *principal chain*; the
  on-behalf-of relation MUST be acyclic, an actor declares at most one delegator
  (a second `on-behalf-of` on the same actor is ill-formed), and a binding naming
  an undeclared node, or a node that is neither an actor nor a human, is
  ill-formed — all rejected at apply. A delegation binding between two actors MUST
  satisfy the no-amplification invariant (the specification, Terminology
  and conformance; Governance declarations): at every gate at which the delegate is
  granted authority, for each `kind` granted there, the delegate's granted `risk` set
  over that `kind` at that gate MUST be a subset of the delegator's granted `risk` set
  over that same `kind` at that same gate — an ungranted delegator has the empty set,
  so a delegate is never granted where its actor-delegator is not. A binding that
  violates this is ill-formed and has no effect. The invariant bounds delegated grants only; it does not propagate
  the delegator's reservation or quorum restrictiveness to the delegate. Where the
  delegator is a `human`, the binding anchors answerability and constrains no grant:
  a role does not by itself confer authority, none is conferred here, and the human
  stays graph-disconnected. A delegate that declares no `party` bears its delegator's
  party, resolved along the (acyclic) chain to the nearest declared party; this
  resolved party is what the observation projects on the delegate's node.
- An `actor` declaration MAY carry `mandate <purpose>` or `mandate { <purpose>, … }`,
  the set of declared purposes the actor is authorised to pursue. A single purpose
  MAY be written without braces. The set is declared, never computed; `mandate` is
  configuration on an actor, is not a token field, and is never guardable — guards
  range only over {`kind`, `risk`, `party`, `tags`}. An actor declares at most one
  `mandate`; a second on the same actor is ill-formed. A delegation binding between
  two actors MUST satisfy the mandate-attenuation invariant (the specification,
  Governance declarations): the delegate's mandate MUST be a subset of its
  delegator's, and a delegator declaring no mandate has the empty set, so its
  delegate MUST also declare none. A binding that widens a mandate is ill-formed at
  apply and has no effect. Attenuation composes pairwise along the acyclic principal
  chain and needs no separate rule. Where the delegator is a `human`, the binding
  constrains no mandate, exactly as it constrains no grant.
- `master` is a reserved endpoint name denoting the single egress node — the unique
  sink at which the policy enforcement point attaches (the specification, Nodes). It
  is never declared; a policy graph contains exactly one master.

## 4. Cord legality (typed cords)

A cord `A -> B` is legal if and only if its endpoint classes form one of the three
permitted pairings below and, for an authority cord, the gate grants that actor.
Every other pairing is ill-formed. A program containing any non-conforming cord
denotes an ill-formed policy graph and has no effect (fail-closed; fail-safe
defaults).

| Cord | From → To | Type | Condition |
|---|---|---|---|
| authority | `actor` → `gate` | authority | the gate grants that actor |
| pipe | `gate` → `gate` | pipe | the pipe relation is acyclic |
| egress | `gate` → `master` | egress | verdict resolved at evaluation |

An authority cord lands on a configuring inlet and is configuring only; pipe and
egress cords land on an activating inlet and carry activation (the specification,
Activation). A `pipe` feeds one gate's effective verdict into the next; a gate with an
outgoing pipe is an interior gate and does not egress, and effective verdicts
propagate to the terminal gate as the join (the most restrictive outcome) along the
chain `auto ⊑ human ⊑ refused ⊑ reserved ⊑ prohibited` (the specification,
Propagation).

These cases are ill-formed and give the program no effect: a `human` as source or
target of any cord; `actor -> master`; any cord into an undeclared node; a cycle
in the pipe relation; more than one master; a gate on no `pipe ∪ egress` path to
the master, including a gate bearing only a reservation, prohibition, or egress
obligation; a cycle in the on-behalf-of relation, or an on-behalf-of naming an
undeclared node; and a delegation binding that violates the no-amplification
invariant.

## 5. Activation (the single activating inlet)

Each node has a single activating inlet and zero or more configuring inlets. A token
at the activating inlet activates the node; a value at a configuring inlet sets
configuration — a gate's `risk` floor or `party`, or an authority conferral — without
activating it (the specification, Activation).

No node self-activates. A run originates from one transport trigger — there is no
internal timer. A *source gate* is a gate whose activating inlet is fed not by a cord
but by the proposing actor's action as an external stimulus, so that it has in-degree
zero in the cord-induced activation relation. A policy graph MAY have one or more
source gates. Exactly one token arrives at a node's activating inlet per activation.
One transport is one evaluation of the whole policy graph from its source gates through
the `pipe ∪ egress` graph, the master deciding each egress path: every activated gate
is evaluated, effective verdicts propagate strictest-wins along pipes, and the master
decides each egress path independently. A multi-step agent run is a *sequence of
activations*, one per tool invocation or other external effect, and the join does not
operate across activations.

The master takes a token at its activating inlet and either releases the action of a
terminal gate or withholds, deciding each egress path independently: for a given
terminal gate it releases if and only if that gate's effective verdict is `auto` and
every egress obligation is attached; every other verdict, and the ⊥ case (an
ill-formed policy graph or a rejected token), withholds. The master never weakens the
effective verdict. This document does not define what physically supplies the
activation stimulus or the release point; that is outside the specification.

## 6. Worked example

A routine drafting gate and a deciding gate that reserves a solely-automated decision
to a human role when the token is high-risk:

```
actor bot7
human alice  role dpo
gate  draft   risk low    grant bot7
gate  decide  risk high   grant bot7
reserve automated_decision by dpo when risk >= high   # cf. GDPR Art. 22 (policy)
cord bot7   -> draft
cord bot7   -> decide
cord draft  -> master
cord decide -> master
```

This denotes a policy graph with two terminal gates. Consider two separate
activations. In the first, a low-risk token whose `kind` matches no reservation is
proposed at `draft`: the gate assigns `auto`, every egress obligation (here none) is
attached, and the master releases the drafting action; the evaluation is recorded as
one verdict-labelled log entry. In the second, a high-risk token of `kind`
`automated_decision` is proposed at `decide`: the reservation matches, the gate
assigns `reserved`, the action is referred to the `dpo` role, and the master
withholds. A reserved path is never `auto`, whatever the policy grants; any
subsequent release is a separate activation (the specification, Release), which this
language does not relate to the withholding evaluation.

## 7. Abstraction (rack)

A *rack* is a macro notation: a named body with parameters, instantiated with
arguments and expanded by a textual pre-pass before the grammar of §3 is applied. A
rack is therefore pure sugar — anything it expands to is ordinary program text, and a
rack adds no expressiveness to the language. Expressiveness comes from declarations,
never from computation; the rack notation performs textual substitution only and
denotes no computed value.

```ebnf
rack def     = "rack" , name , "(" , [ param , { "," , param } ] , ")" , ":" , newline ,
               { body line } , "end" , newline ;
rack use     = "rack-use" , name , "(" , [ binding , { "," , binding } ] , ")" ;
binding      = param , "=" , value ;
```

Within a body, `$param` is replaced by the bound argument. The token `$0` expands to a
per-`rack-use` instance index, so the same rack instantiated with identical arguments
still expands to distinct node identifiers (for example `actor a$0` becomes `a0`, then
`a1` on the next use), giving instance-unique identifiers without the author managing
them by hand. Expansion is fail-closed: an unknown rack name, missing or extra
arguments, an undefined `$name`, or a missing `end` causes the program to denote an
ill-formed policy graph, which has no effect. An expansion failure is a
**parse**-stage rejection — the pre-pass precedes the grammar of §3, so a program
whose expansion fails never reaches it.

```
rack approval(actor, g, level):
    actor $actor
    gate  $g risk $level grant $actor
    cord  $actor -> $g
    cord  $g -> master
end
rack-use approval(actor=bot7, g=c1, level=high)
rack-use approval(actor=bot9, g=c2, level=critical)
```

After expansion, each `rack-use` above contributes one actor, one gate granting that
actor, one authority cord, and one egress cord — ordinary program text whose
legality is judged exactly as in §4. Because a rack is expanded before parsing, it can
express nothing the base grammar cannot.

## 8. Relationship to the specification

This companion is normatively subordinate to the specification. The textual
surface of §3 presents one abstract policy graph; a program in that surface
denotes that graph. Its well-formedness, evaluation, verdicts, release rule, log
requirement, and conformance are those fixed by the specification (Terminology
and conformance; Evaluation; Conformance). This document defines no execution,
scheduling, storage, presentation, communication, or disclosure mechanism,
measures no duration, and discharges no obligation; each is outside the
specification.
Where a concept here needs grounding, it is grounded in the specification or in the
public standards and regulations the specification cites — Regulation (EU) 2024/1689
(AI Act), Regulation (EU) 2016/679 (GDPR), and the access-control, information-flow,
separation-of-duty, and transparency-log literature referenced there — and nowhere
else.
