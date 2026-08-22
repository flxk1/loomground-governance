<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright 2026 flxk1 -->
# Loomground

## A declarative language for the governance of AI systems and AI agents

**Specification — Version 0.8 (draft).**

## Abstract

Loomground is a declarative language for expressing governance constraints on the actions of an AI system or AI agent ([AIA] Art. 3(1); [ISO22989]). A governance program is a *policy graph*: typed *nodes* joined by typed *cords*, evaluated from one or more source gates fed by a transport trigger; tokens are resolved at one egress node — the *master* — before any action is released at the policy enforcement point [XACML], and each evaluation is recorded so later alteration is detectable. The language describes *what* governance applies; execution, scheduling, storage, presentation, and communication are outside it (§10). The concrete syntax is a companion document, normatively subordinate to this one.

## 1. Scope

This specification defines a declarative language for governing the points at which an AI system or AI agent's action MAY take effect at the policy enforcement point [XACML]; where the output is a prediction or recommendation rather than an action, the governed point is its release as an external effect. The general case is a multi-step agent — a sequence of activations (§5.2), each governing one tool invocation or external effect and resolving at one egress; a single-checkpoint decision based solely on automated processing with legal or similarly significant effects on a person ([GDPR] Art. 22(1)) is the degenerate case. The scope partition is authoritative in §10.

**Expressing a measure in this language does not, by itself, satisfy any legal obligation** under [AIA], [GDPR], or any other instrument. Conformance is a property of an implementation (§9), not a finding of legal compliance.

## 2. The language at a glance

**Nodes (§3)**

| Class | Role | Inlets / outlet |
| --- | --- | --- |
| actor | Principal that may be granted authority and propose an action | Outlet: authority cord to a gate |
| human | Person, named by a role: referred a reserved token, or rooting a principal chain | None (not graph-connected) |
| gate | Governed checkpoint where an actor acts and a verdict is produced | Activating inlet (pipe/external); configuring inlet (authority); outlet: pipe or egress |
| master | Single sink; the release point | Activating inlet (egress); no outlet |

**Cords (§5.1)**

| From → to | Type | When legal |
| --- | --- | --- |
| actor → gate | authority | Configuring; permitted when the gate grants that actor |
| gate → gate | pipe | Activating; the pipe relation MUST be acyclic |
| gate → master | egress | Activating; lands only on the master |

Every other endpoint pairing is ill-formed.

**Token (§4)**

| Field | Meaning |
| --- | --- |
| id | Identity (guards MUST NOT range over it) |
| kind | Class of subject or action — a decision subject, or an invoked capability such as a tool [OCAP]; host-observed at the tool-call/effect boundary, not actor-declared (PROM-001) |
| risk | Ordered severity level [ISO31073]; gate-computed from a governed policy table, a self-declared hint admitted only to raise it (PROM-001) |
| party | The party currently responsible; a subject identity [ABAC] |
| provenance | The ordered prior nodes and parties traversed; firewalled out of the gate decision — attribution and redress only (PROM-001) |
| reversibility | Optional ordered level: how recoverable the effect is once released |
| uncertainty | Optional ordered level: how settled the basis for the action is |
| tags | Optional set of declared, non-id categories tested by membership |

**Declarations (§6)**

| Declaration | Form | Effect | Grounding |
| --- | --- | --- | --- |
| Reservation | Gate, optionally guarded | Refers a token of a kind to a human role; verdict `reserved` | [CW; SOD]; cf. [AIA] Art. 14/26; [GDPR] Art. 22(3) |
| Quorum | One role, conjunction, or m-of-n | Requires distinct parties (separation of duty) | [SOD; CW] |
| Prohibition | Gate, on a kind | Blocks release and discharge; verdict `prohibited` | cf. [AIA] Art. 5 |
| Temporal condition | Duration on a reserved action | Declares deadline/window/expiry and on-elapse resolution | [RBAC; ABAC] |
| Egress obligation | On egress, on a gate | Attaches an obligation to the released action | [AIA] Art. 50; [GDPR] |
| Redress | On a released kind, by a role; optional `overturn`/`within` | Names a released decision as contestable: a re-examination is owed and recorded; verdict-neutral | [GDPR] Art. 22(3)/77–79; [Charter] Art. 47; [AIA] Art. 14(4) |
| Party | Attribute on actor/gate | Sets the party currently responsible | [GDPR] Art. 4; [AIA] Art. 3 |
| Delegation | Attribute on an authority cord | Binds delegate to act on behalf of a delegator — an actor or a human; the chain is the principal chain | [OCAP]; [AGENCY] |
| Mandate | Attribute on an actor | Declares the set of purposes the actor is authorised to pursue; a delegate's mandate MUST be a subset of its delegator's | [AGENCY]; [OCAP] |
| Transfer | Policy-global, on a kind, to a consignee | Names where a released action's material goes and the purposes it is limited to there; the purposes MUST lie within the consigning actors' mandates | [AGENCY]; [GDPR] Art. 28(4)/Ch. V |
| Autonomy grade | Attribute on actor (granted) / gate (required, a source gate) | Sets the granted or required level on the active autonomy ladder; gates the §7.1 step-(4) `auto`/`human` disposition at the source gate | [AIA] Art. 14/26; [Sheridan78]; [PSW00] |

**Verdicts (§7)**

| Verdict | Meaning | Releases at master? |
| --- | --- | --- |
| auto | Releasable, subject to attached obligations | Yes |
| human | Withheld pending human oversight/intervention | No |
| refused | Acting actor holds no authorizing grant | No |
| reserved | Token matches a reservation; referred to a human | No |
| prohibited | Kind is prohibited; invariant under any privilege | No |

`inactive` is a status of a non-activated gate, not a verdict. There is deliberately no "on-the-loop" verdict: the language admits only this five-element alphabet.

## 3. Nodes

A policy graph is built from four node classes; the abstract syntax admits no other.

- **actor** — a principal ([OCAP]; subject [XACML]) that MAY be granted authority at a gate by an explicit authority cord, and bears none otherwise. When so granted, an actor MAY propose an *action* — a tool invocation or other external effect — for evaluation at that gate. The transport delivers the proposing actor's action to a source gate as its activation token, as an external stimulus rather than over a cord (§5.2), and is thereby the recorded cause of that gate's evaluation. An AI agent is modelled as an `actor` exercising autonomy.
- **human** — a person named by a role: the role of a reservation (§6), to whom a reserved token is referred, or the delegator anchoring a principal chain (§6); not graph-connected. A role does not by itself confer authority.
- **gate** — a governed checkpoint at which an actor acts and a verdict is produced (attributes: minimum risk level, party, declarations §6). A gate that egresses to the master is *terminal*; a gate that is the source of a pipe is *interior*. Only a terminal gate's proposed action is releasable (§7.3); an interior gate contributes a verdict to propagation (§7.2).
- **master** — the unique sink vertex (out-degree zero over all cords), designated as the release point — the node at which the policy enforcement point [XACML] attaches. The master has no action of its own; what is released at it is the action of a terminal gate (§7.3). A policy graph MUST contain exactly one master.

## 4. The token

A single data type flows along a cord: the token, with fields as in §2.

A guard or declaration that distinguishes tool invocations does so on `kind`. **`kind` is host-observed** (PROM-001): it is derived from the operation actually performed at the tool-call/effect boundary — the invoked capability or decision subject as the host sees it — not asserted by the acting actor. There is no actor-set `kind`, and for a structurally-typable operation under-declaration of `kind` is unrepresentable: the host records the operation it performed, so a token cannot present a `kind` narrower than the boundary observed. A guard over `kind` (§6) therefore ranges over an observed fact, not a declaration.

The `risk` field is an ordered severity level [ISO31073] within a risk-management process [ISO31000]; the scale (illustratively `low < medium < high < critical`) is a deployer choice ([AIA] Art. 3(4)). **`risk` is gate-computed** (PROM-001): the gate derives it from a governed, versioned, signed policy table keyed on (observed-`kind` × target/resource × context × autonomy-grade), and it is carried on the token thereafter. A self-declared risk hint is admitted only as a **monotonic ratchet** — it MAY raise the computed tier, never lower it — so no supplier attenuates risk by asserting a milder value. A pattern the table does not map resolves to the strictest tier by construction, and `unknown` is itself a strict-tier value, never a permissive null. A gate MAY additionally declare a minimum risk level; a token there is treated as having at least that level — the maximum of the computed `risk` and the gate's floor, a further raise-only step. The table's content is policy (§10); that `risk` is computed from it, and that a declared hint may only raise it, is language.

**Fail-closed floor (PROM-001).** A token the gate cannot classify — an operation not structurally typable to a `kind`, or a `risk` the policy table cannot key — resolves to the strictest tier, as does any token whose self-declared hint contradicts the host-observed facts: a declared-hint-vs-observed mismatch is never resolved in the token's favour. The record (§7.4) MUST carry both the declared token and the host-observed facts, so that later redress (§6) weighs what was claimed against what was observed rather than a reconciled summary.

The `reversibility` and `uncertainty` fields are ordered levels that are **declared, not derived** — unlike `risk` (§4 above, now gate-computed, PROM-001), these two remain supplier-asserted. `reversibility` states how recoverable the action's effect is once released; `uncertainty` states how settled the basis for it is, which is orthogonal to whether the action is on the merits correct. Their scales (illustratively `reversible < compensable < irreversible` and `settled < contested < unknown`) are deployer choices, recorded in `vocabulary/reversibility.json` and `vocabulary/uncertainty.json`, and both order ascending in concern so a `>=` guard catches the severe end exactly as it does for risk. Neither has a gate floor: a gate may raise a token's effective `risk` (above), and raises nothing else.

The language computes neither `reversibility` nor `uncertainty`. Whoever supplies the token asserts them, as it asserts `party`, and a conforming implementation infers them from no other field. (`risk` is the exception: the gate computes it, and a self-declared value is admitted only to raise it — above, PROM-001.) **This is what lets an autonomy level vary with circumstance without the notation acquiring the power to compute one:** a host may derive a `reversibility` or `uncertainty` value by any means it likes and hand it in as a declared property, and the language then only compares declared values (§6, the guard domain). The wall the guard domain describes is a constraint on the *notation*, not on the host.

The `party` field denotes the party currently responsible — the in-language governance-responsibility attribute. Where a guard ranges over `party` (§6) it denotes the party the token carries at the evaluating gate. **The language does not authenticate party assignments; binding a `party` to an authenticated identity is outside this specification, and the party-guard and the separation-of-duty distinctness check (§6 Quorum) carry their intended security property only relative to such an external binding.**

A conforming implementation MUST reject a token lacking a required field or bearing a risk outside its domain, and MUST preserve fields it does not recognise. Rejection is the mapping into ⊥ (below): a rejected token activates no node and produces no log entry. Exactly one token arrives at a node's activating inlet per activation (§5.2).

Evaluation reads the token and MUST NOT modify it: `provenance` is supplied by the transport per activation and is never appended to during evaluation. No verdict or observation can depend on such a mutation — a guard MUST NOT range over `provenance` (§6) — so this invariant is pinned by this text and has no distinguishing vector.

**Totality.** A well-formed graph (§5.1) denotes a total function from a valid (token, policy) pair to a verdict-labelled trace over the log; an invalid token (this section) or ill-formed graph denotes ⊥ — no node activated, no log entry. ⊥ never enters a join (§7.2). The operational reading is a well-founded recursion over the directed acyclic graph [PLOTKIN].

## 5. Connections and activation

### 5.1 Typed cords

A cord's type is determined by its endpoints, per the table in §2. Every other pairing is ill-formed. A human MUST NOT be the source or target of any cord; an actor MUST NOT connect directly to the master; a cord MUST NOT terminate at an undeclared node. A policy graph containing any non-conforming cord is ill-formed, and a conforming implementation MUST give it no effect (fail-closed; fail-safe defaults [PROT]).

A policy graph is **well-formed** if and only if: every cord is a permitted endpoint pairing; the `pipe` relation is acyclic (its transitive closure irreflexive); the graph contains exactly one master (§3); every gate lies on a `pipe ∪ egress` path to the master (reachability — no inert or dangling gate); a gate that declares a required grade is a source gate (§6, §7.1); the on-behalf-of relation names only a declared `actor` or `human`, declares at most one delegator per actor, and is acyclic (its transitive closure irreflexive, §6); an actor declares at most one mandate (§6); a gate declaring a consignee is terminal and every transfer names a declared consignee with a non-empty purpose set (§6); and every actor→actor delegation binding satisfies both the no-amplification and the mandate-attenuation invariants (§6). A graph that is not well-formed is ill-formed, and a conforming implementation MUST give it no effect (fail-closed).

The path MAY be of length zero, where one gate is both a source gate and a terminal gate egressing directly to the master (the single-checkpoint case of §1).

**Authority is conferred only by an explicit cord, never ambiently** (designation-based access [OCAP]). The authority cord is `actor → gate` for a specific gate, so the actor's authority is a per-gate fact. For an act to be `auto`-releasable the proposing actor MUST hold an authorizing grant, and meet every gate-property declaration, at every gate on its path to the master; a single ungranted gate yields `refused` (§7.1) and the join (§7.2) carries it upward.

A gate's required `grade` (§6) is not an authority grant. Insufficient or absent grade is resolved at §7.1 step (4) as `human`, not as `refused`.

### 5.2 Activation

Each node has a single activating inlet, which activates it, and zero or more configuring inlets, which set configuration without activating it. The `pipe` and `egress` cords land on the activating inlet and carry activation; the `authority` cord lands on a configuring inlet and is configuring only. The activation relation is the set of (source, target) pairs induced by `pipe` and `egress` cords.

A node MUST be activated only upon a token at its activating inlet, and exactly one token arrives there per activation. A **source gate** is any gate whose activating inlet is fed not by a cord but by a proposing actor's action delivered by the transport as an external stimulus (necessarily a gate, since pipe and egress originate only at gates), and is therefore in-degree zero in the cord-induced relation. A policy graph MAY have one or more source gates. No node self-activates, so each action is attributable to its proposing actor as the recorded cause at its source gate.

One activation is one evaluation of the whole policy graph from its source gates to the master, with the §7.2 join operating *within* that one activation across the piped gates traversed. A multi-step agent run is a *sequence* of activations: each tool invocation or external effect is a distinct activation, hence a distinct decision request at the policy decision point [XACML]; the join does not operate across activations. Authority is fixed per activation.

## 6. Governance declarations

The expressiveness of the language comes from a fixed vocabulary of declarations. A declaration states a governance condition and specifies no computation. A guard ranges over exactly {`kind`, `risk`, `party`, `tags`} and MUST NOT range over `id`; it MAY refer to the parties recorded in `provenance` only for the Quorum distinctness predicate. It MUST NOT denote a computed value. The `kind` and `risk` a guard ranges over are the host-observed and gate-computed values of §4, not actor assertions; the guard compares them and computes nothing itself. The exclusion of `provenance` from the guard domain firewalls attribution out of the gate decision: the prior nodes and parties feed the record (§7.4) and any redress (§6), never the verdict — reinforcing the no-`id` wall of §4 (PROM-001).

The `tags` of a token are a set of declared, non-`id` categories (data origin, lineage, synthetic-content, taint); a guard tests them by membership (`tags contains <tag>`), which denotes no computed value — *which* tags exist and what they signify is policy (§10).

**A guard constrains but never confers authority:** a `party`-guard selects which declaration applies, but an actor lacking the §5.1 authority cord is `refused` (§7.1) regardless of any guard outcome. The `party` over which a guard ranges is the governance-responsibility attribute carried by the token (§4), distinct from the acting actor's authority.

- **Reservation** — a gate MAY declare that a token of a kind (optionally guarded) reserves the proposed action to a human role; verdict `reserved`. A reserved token MUST NOT be released without human intervention and MUST be referred to a human role rather than discharged by the actor — a separation-of-duty measure [CW; SOD]. Cf. the human-oversight measures of [AIA] Art. 14 and Art. 26 and the human-intervention safeguard of [GDPR] Art. 22(3).
- **Quorum** — the target MAY be one role, a conjunction (all required), or m of a set (m-of-n control). Because exactly one token arrives per activation (§5.2), distinctness is observed over the parties recorded in `provenance` (§4): the predicate that the provenance parties satisfying the target are pairwise distinct. Distinct-`party` is the language's separation-of-duty primitive [SOD; CW]; the n = 2 case is dual control [CW] (unauthenticated; see §4). Role-based mutual exclusion (separation of duty over roles) is outside this specification.
- **Prohibition** — a gate MAY declare a kind prohibited, optionally guarded; verdict `prohibited`. A prohibited token MUST NOT be released or discharged; `prohibited` MUST take precedence over any authority an actor holds, and no grant attenuates it. A guard (the reservation rule, ranging over {`kind`, `risk`, `party`, `tags`} only) narrows *which* tokens are prohibited: a guarded prohibition prohibits exactly those its guard matches — invariant under any grant — and silence on the rest is the absence of this prohibition, not a permission (policy, §10). Where the basis is [AIA] Art. 5 the prohibition arises by law; whether a practice is in fact prohibited is a matter of law and policy (§10), not of this language.
- **Temporal condition** — a reserved action MAY carry a duration (deadline, window, expiry, cooling-off) and its on-elapse resolution. The duration and resolution are declared; the measurement of elapsed time is outside this specification.
- **Egress obligation** — a gate MAY declare an obligation on egress — for example the transparency obligations of [AIA] Art. 50. These are borne by the provider or deployer; the language provides only the point of attachment and does not allocate the duty.
- **Redress** — a gate MAY declare that a released decision of a kind is *contestable*: a fresh re-examination by a human role is owed and recorded; an optional `overturn` qualifies that role as empowered to reverse the outcome, not merely review it; an optional `within <duration>` declares the appeal or recall window. The language declares and records the right; the re-examination is a separate activation (§7.3), and any reversal or recall of the released action is outside this specification. Cf. the right to contest a solely-automated decision and to obtain human intervention [GDPR Art. 22(3)], the right to an effective remedy [GDPR Arts. 77–79; Charter Art. 47], and the oversight power to intervene upon, override, or halt an action [AIA Art. 14(4)]. Redress adds no cord and no node; the policy graph remains forward-only and the right is a declaration, not a backward edge.
- **Party** — each actor and gate bears a party; where the party differs across a boundary, the party currently responsible changes accordingly. An actor that declares no party bears its delegator's party, resolved along the principal chain (below) to the nearest declared party — a selection between declared values, not a computed one (cf. §4); where no party is declared anywhere on the chain, the actor bears none. A human's role is not a party. Communication of a party change is outside this specification.

Which kinds are reserved or prohibited is policy, not language (§10).

**Autonomy grade.** An `actor` MAY carry a *granted* grade and a `gate` MAY declare a *required* grade. Grades live on one ordered autonomy axis. The language fixes the axis and the comparison rule; the level names and meanings are policy (§10).

A granted grade is the actor's standing autonomy. A required grade is the threshold for unattended action at a checkpoint. A gate with a required grade MUST be a source gate; a required grade on a piped gate is ill-formed at apply. At an ungraded gate, an actor's granted grade has no effect.

`grade` is configuration, not a token field. It is not guardable: guards range only over {`kind`, `risk`, `party`, `tags`}. `risk` is per-action token data; `grade` is per-actor/per-gate configuration.

**Re-grading is a fresh activation.** A granted or required grade is configuration and does not change during an evaluation; there is no runtime mutation of either. Where a deployment varies autonomy with circumstance, it does so by activating a gate again with a different token — whose `risk`, `reversibility` and `uncertainty` may differ (§4) — or against a graph whose configuration was itself re-authored. Each such change is therefore an ordinary activation with an ordinary log entry (§7.4), and an observation stays a projection of the graph rather than of its history. An implementation that mutated a grade mid-evaluation would make the same graph yield different observations at different moments, and is non-conforming.

The default ladder is `L0 < L1 < L2 < L3 < L4 < L5 < L6`, recorded in `vocabulary/grades.json`. A deployer MAY replace that ladder. The active ladder MUST declare a total order over its levels, and each declared grade in a graph MUST be a member of that active ladder; otherwise the graph is ill-formed.

**Delegation binding (on-behalf-of).** An authority cord (§5.1) MAY declare that the actor (the *delegate*) acts on behalf of a *delegator* — another actor, or a human, named in the graph. This is a declarative designation over declared nodes; it adds no node class and no cord, riding the existing authority cord as an attribute. A binding naming an undeclared node, or a node that is neither an actor nor a human, is ill-formed; an actor declares at most one delegator, and a second binding on the same actor is ill-formed. The on-behalf-of relation MUST be acyclic (§5.1); the chain it forms — delegate to delegator, to that delegator's delegator — is the **principal chain**: the in-language statement of on whose behalf an actor acts [AGENCY; RFC8693].

Where the delegator is a **human**, the binding anchors answerability and constrains no grant: a role does not by itself confer authority (§3), and the binding confers none — the human remains graph-disconnected (§5.1), and the no-amplification invariant below ranges over actor→actor links only. A chain terminating at a human is *rooted in a person*; whether a deployment requires every chain to be so rooted is policy (§10).

**No-amplification invariant (well-formedness).** The delegate's granted `risk` set over a `kind` at a gate MUST be a subset of the delegator's over that `kind` at that gate. A delegator holding no grant over a `kind` at a gate has the empty set there, so any grant to its delegate at that gate over that `kind` amplifies: a delegate is never granted where its actor-delegator is not. Delegation MUST NOT amplify granted authority [OCAP; PROT]. The same attenuation applies to grade: a delegate's granted grade MUST NOT be above the delegator's on the active ladder; if the delegator is ungraded, the delegate MUST also be ungraded. The check ranges over declared grants only. It does not propagate the delegator's reservation, quorum, or prohibition to the delegate (policy, §10). Along a chain of actor→actor bindings the pairwise invariant composes: attenuation is transitive over the (acyclic) principal chain, and needs no separate rule. A graph violating this invariant is ill-formed and has no effect.

**Mandate.** An `actor` MAY carry a *mandate*: the set of declared purposes it is authorised to pursue. A mandate is a set of declared ids and denotes no computed value; a single-element mandate MAY be written without braces. An actor declares at most one mandate, and a second on the same actor is ill-formed.

`mandate` is configuration on an actor, in the same register as `grade`. It is not a token field and is not guardable: guards range only over {`kind`, `risk`, `party`, `tags`} (§4). A grant says *what* an actor may do; a mandate says *what for*. The two are independent — a mandate neither confers authority nor withholds it, and an action within a mandate but outside a grant is refused exactly as before.

**Mandate-attenuation invariant (well-formedness).** The delegate's mandate MUST be a subset of its delegator's. A delegator declaring no mandate has the empty set, so its delegate MUST declare none either: an actor cannot confer a purpose it was not itself given. Delegation MUST NOT widen a mandate [AGENCY; OCAP]. As with grade, the check ranges over declared mandates only, and along a chain of actor→actor bindings the pairwise invariant composes: attenuation is transitive over the (acyclic) principal chain and needs no separate rule. Where the delegator is a **human**, the binding constrains no mandate — exactly as it constrains no grant (above). A graph violating this invariant is ill-formed and has no effect.

Attenuation is the whole of what the language says about a mandate. Whether a delegate's conduct in fact served its mandate is not a graph property and is outside this specification; the language records the purpose an actor was given and bounds how it may narrow, and a host or reasoner judges conduct against it.

**Consignment and transfer.** A `gate` MAY declare a **consignee**: the party to which what that gate releases goes. A consignee is a declared id in the register of `party`, not a node — the four node classes (§3) are unchanged, and a consignee is never a cord endpoint. A gate that declares a consignee MUST be terminal (it egresses to the master); a consignee on an interior gate is ill-formed at apply, exactly as a required grade on a non-source gate is (§7.1).

This is what lets the language say *to whom* something released. The master answers whether an action releases (§7.3) and decides each egress path independently; the consignee names where that particular path leads. No second master is introduced and the release rule is unchanged.

A **transfer** declaration states that material of a `kind`, released to a named consignee, is limited there to a declared set of purposes: `transfer <kind> to <consignee> within <purposes>`. A transfer naming a consignee that no gate declares is ill-formed, and so is a transfer whose purposes are empty.

**Transfer-attenuation invariant (well-formedness).** For every actor granted over that `kind` at a gate consigning to that consignee, the transfer's purpose set MUST be a subset of that actor's mandate (§6). An actor holding no mandate holds the empty set, so it can license no purpose onward: an actor cannot hand on a purpose it was not itself given. This is the mandate-attenuation rule applied to a **lateral** relation — a transfer is not a delegation, the consignee acts on nobody's behalf, and no principal chain is formed — but the reason is identical, so the rule is. A graph violating this invariant is ill-formed and has no effect.

What the language does **not** say is what the consignee then does. A transfer records the purposes material was released under and bounds them by what the releaser held; whether the consignee honours them is conduct, outside this specification (§10), and no verdict here is a finding about a recipient's behaviour. The declaration makes the question answerable, not the answer automatic.

The runtime conferral of authority on a sub-actor is outside this specification; the language fixes only the on-behalf-of binding and the attenuation invariants in force at an evaluation.

## 7. Evaluation

### 7.1 Verdict assignment

On activation, each gate assigns exactly one verdict to its token by priority selection — a total ordering producing exactly one verdict, not a join. In order of precedence, a conforming implementation MUST assign: **(1)** `prohibited` if the token matches a prohibition; **(2)** `refused` if the acting actor holds no authority at the gate; **(3)** `reserved` if it matches a reservation; **(4)** otherwise the `auto`/`human` disposition, determined as follows. The `risk` these steps range over is the gate-computed value with the fail-closed floor already applied (§4): an unclassifiable token or a declared-hint-vs-observed mismatch enters verdict assignment at the strictest tier, so no precedence step runs against an under-stated risk (PROM-001).

The grade comparison is evaluated only at a source gate. Let `R` be the gate's required grade and `G` the proposing actor's granted grade, each a level on the active autonomy ladder.

- if the gate declares `R` and the proposing actor declares `G`: the disposition is `auto` if `G` is **at least** `R` in the active ladder's order, else `human`;
- if the gate declares `R` but the proposing actor declares no grade: the disposition is `human` (fail-closed — an ungraded actor has not been granted the autonomy a graded checkpoint requires);
- if the gate declares no `R`: the disposition is `auto` — the proposing actor's granted grade is inert at a gate that declares no `R` (the threshold is gate-owned, §6). A deployment that wants unattended action withheld at a checkpoint declares a required grade; that declaration is the language's mechanism for it.

The comparison is a selection between declared ordered values, not a computed value. It participates only in step (4), produces the source gate's own verdict, and adds no verdict to the alphabet. Steps (1)–(3) retain precedence.

`prohibited` and `reserved` are properties of the gate evaluated on the token's `kind`, independent of which actor presents it; `refused` concerns only the absence of an authorizing grant. This ordering is pinned as a conformance vector (§9).

**That actor-independence is where this language locates correctability.** A reservation refers the token to a human role without being evaluated against the acting actor at all, so no grant and no grade reaches it: there is no position an actor can be conferred that puts it beyond a human referral. The property therefore holds by construction rather than by a rule forbidding its negation, and it needs no notion of an intervention directed at a named actor — an act carries no target field (§4), and one is not required here. What the language guarantees is that release is withheld (§7.3); whether a runtime then pauses, corrects or terminates the actor is enforcement, and is policy (§10). A maximally granted actor meeting a gate's required grade — for which step (4) would dispose `auto` — still receiving `reserved` is pinned as a conformance vector (§9).

The `auto`/`human` disposition of step (4) is assigned per token. `human` denotes that release is withheld at the master pending human oversight or intervention. A grade-determined `human` is role-less: unlike `reserved`, it names no human role. A non-activated gate bears the status `inactive`, which is not a verdict.

Priority selection (one verdict at one gate) and the join (§7.2, across predecessors) operate on different inputs; their orderings need not agree on the `refused`/`reserved` pair.

### 7.2 Propagation

Each activated gate has a well-defined own verdict drawn from the five-element chain (§7.1 is total over one token, §5.2). Along pipes, a gate's *effective verdict* is the join of its own verdict and the effective verdicts of all gates that pipe into it — the endpoint discipline of information-flow control, taking the most restrictive outcome [IFC, FLUME].

The verdict alphabet is a finite chain, a join-semilattice under the restrictiveness order

`auto ⊑ human ⊑ refused ⊑ reserved ⊑ prohibited`

with the join ⊔ equal to the maximum. The effective verdict satisfies *eff(g) = own(g) ⊔ ⊔{ eff(h) : h pipe→ g }*. Acyclicity (§5.1) and idempotent ⊔ make `eff` well-defined and order-independent, so traversal order is an implementation detail. `inactive` contributes no term to the join (an inactive predecessor is not in the index set), and ⊥ never enters a join (§4).

### 7.3 Release

The master decides each egress path independently. For each terminal gate, the master MUST release that gate's action if and only if that gate's effective verdict equals `auto` and every egress obligation is attached; otherwise it MUST withhold. The master also withholds when the evaluation denotes ⊥ (§4). Every value other than `auto`, and the ⊥ case, withholds (fail-closed). The master MUST NOT weaken the effective verdict.

Attachment (not discharge, §6/§10) is the in-language condition; discharge is out of scope. A gate's declared obligation (§6) is thereby attached by declaration — the language defines no separate attach step and no construct that leaves a declared obligation unattached, so the master rule's withhold-for-non-attachment branch guards against a host's failure to honor what a patch declares, not against any well-formed patch. Within this specification only `auto` releases: `human` and `reserved` denote withhold-pending-intervention. The recorded reason for a withholding SHOULD be the most restrictive contributing verdict.

The language does not relate a post-intervention activation to the withholding evaluation: the subsequent activation is a fresh evaluation with its own source gates, declarations, and parties, and the language imposes no carry-over. A reader MUST NOT assume the reserved action's constraints bind the follow-on activation. Any such binding is policy (§10). A **redress** declaration (§6) names such a re-examination as *owed* for a contestable released decision — and, where it carries `overturn`, that the re-examiner is empowered to reverse the outcome — while the re-examination remains a fresh activation: redress records the right without adding a backward edge to the graph.

### 7.4 Record

Every evaluation step MUST be recorded: one log entry per activated gate, carrying that gate's effective verdict (§7.2), in evaluation order, such that any later alteration, deletion, or reordering is detectable (tamper-evident log; accountability, [GDPR] Art. 5(2)). The entry MUST carry both the declared token and the host-observed facts that produced its host-observed `kind` and gate-computed `risk` (§4), so that redress (§6) is not theatre — the later re-examination sees the claim and the observation, not a reconciled value (PROM-001). The presence and ordering of these verdict-labelled entries is part of the observation (§9) and is conformance-tested; the mechanism (e.g. a transparency log [CT]) and any external witness are outside this specification and not part of the observation.

### 7.5 Determinism

The verdict assignment — dispositions, effective verdicts, and log entries — MUST be a deterministic function of the recorded inputs (the activation token and the resolved policy), and is therefore reproducible across conforming implementations. The content produced by an actor is not so constrained. Reproducibility is what makes the log usable to demonstrate accountability ([GDPR] Art. 5(2); [ISO42001]).

## 8. Invariants

Each invariant has its home section; this is a checklist, not a restatement.

1. **Single egress** (§3).
2. **Mandatory record** — one verdict-labelled log entry per activated gate, in evaluation order (§7.4).
3. **Reservation and prohibition are terminal** (§6).
4. **No self-activation** — every run originates from one transport trigger; no node self-starts (§5.2).
5. **Fail-safe defaults** — an ill-formed policy graph has no effect (§5.1).
6. **Default-deny** — absent an authority cord, `refused` [PROT] (§5.1, §7.1).
7. **No amplification** — a delegation binding satisfies the no-amplification invariant (§6).
8. **No mandate widening** — a delegation binding satisfies the mandate-attenuation invariant (§6).
9. **No transfer widening** — a transfer satisfies the transfer-attenuation invariant (§6).
8. **Complete mediation within an activation** — every act passes a mediating gate at every gate on its path; the relation to any post-intervention activation is not fixed by this language (§5.1, §7.3).
10. **Token integrity (fail-closed floor)** — `kind` is host-observed and `risk` is gate-computed; an unclassifiable token or a declared-hint-vs-observed mismatch resolves to the strictest tier, and the record carries both the declared token and the host-observed facts (§4, §7.4; PROM-001).

A non-reserved, non-prohibited action at a gate declaring no required grade is `auto`; where a source gate declares a required grade, the `auto`/`human` disposition is fixed by the §7.1 grade comparison (§6, §7.1).

## 9. Conformance

**Observation canonical form.** The observation of a policy graph is an object with:

- **Members** — exactly `nodes`, `cords`, `reservations`, and (optionally) `redress`. `nodes`, `cords`, and `reservations` MUST always be present; `reservations` is the empty array `[]` when none is declared (not omitted, not `null`). `redress` is present if and only if at least one redress declaration exists.
- **Reservation form** — each reservation projects as `{kind, by[, when][, duration, on_elapse]}`. A quorum `by` target is in canonical form — `<m> of {role, role}` (m-of-n) or `role and role` (conjunction), whitespace normalised: exactly one space after `of`, after each comma, and around `and`; none adjacent to the braces — so two spellings of the same target compare equal. `duration` and `on_elapse` appear only when a temporal window is declared.
- **Not projected** — a `prohibition` (it severs at apply, §5.1) and an egress `obligation` (it conditions the master, §7.3) act on evaluation; neither appears in the observation.
- **Order** — `nodes` and `reservations` are in source-declaration order (after `rack` expansion). `cords` list the authority conferrals from `grant` clauses first (in gate-declaration order), then the explicitly written cords (in cord-declaration order), with duplicates removed: a `grant` and an equivalent `authority` cord denote the same conferral and appear once.
- **Node attributes** — a node's configuration is projected on the node, never as a separate member: a `gate`'s `risk_floor` and `party`, a `human`'s `role`, an `actor`'s granted `grade`, `mandate` (its declared purposes, projected as a set in ascending lexicographic order, §6) and `on_behalf_of` (its delegator, §6), and a source gate's required `grade_required`. A `gate`'s declared `consignee` is projected on the gate; transfers are projected as a separate ordered member, since a transfer is policy-global and belongs to no single node. An `actor`'s projected `party` is its declared party or, for a partyless delegate, the party resolved along the principal chain (§6).
- **Equality** — two observations are equal if and only if they have the same members with equal values, array order significant. This is the canonical form conformance compares ([`schema/observation.schema.json`](../schema/observation.schema.json)).

A conforming implementation reproduces every conformance vector: the *observation* of a policy graph as nodes, cords, and verdicts in their order (canonical form above); token validation (§4); master decisions, including the precedence of `prohibited` over policy, of `refused` over `reserved` for an unauthorized actor, and of `prohibited` over `refused` for an unauthorized actor presenting a prohibited `kind` (§7.1); the presence and ordering of the verdict-labelled log trace — one entry per activated gate, in evaluation order — where a missing or misordered entry is itself a failure (§7.4); and the fail-closed treatment of ill-formed policy graphs, including a non-conforming cord, a gate on no path to the master, a delegation binding violating the no-amplification invariant, and an on-behalf-of cycle or a binding naming an undeclared node (§5.1, §6).

Conformance is agreement of observations across implementations on every conformance vector (observational equivalence), explicitly excluding the cryptographic tamper-evidence representation, which §7.4 places outside this specification. Independent interoperability is demonstrated when two implementations, neither derived from the other, each pass every vector (cf. the two-implementation exit criterion of [W3CPROCESS]; the interoperability criteria of [RFC2026] as amended by [RFC6410]).

## 10. The language and policy

- **Language** (this specification): node and cord vocabulary, the token, the activation rule, the verdict alphabet, the master rule, the log requirement, the declarations, the delegation binding with its no-amplification invariant, **the host-observed `kind` and the gate-computed `risk` — that `kind` is derived from the operation at the tool-call/effect boundary rather than actor-declared, and that `risk` is computed by the gate from a governed, versioned, signed policy table with a self-declared hint admitted only as a raise-only ratchet and an unmapped or unclassifiable pattern resolving to the strictest tier (the fail-closed floor, PROM-001)**, and **the autonomy-grade axis — the requirement of an active total order over the grade levels, together with the §7.1 step-(4) comparison rule** (the granted-grade/required-grade comparison evaluated at a source gate, its `auto`-when-`G`-at-least-`R` disposition, its fail-closed treatment of an ungraded actor, the `auto` disposition of a gate declaring no required grade, and the gate-owned threshold).
- **Policy** (not normative here): which kinds are reserved or prohibited; the content of the governed risk policy table — which (observed-`kind` × target/resource × context × autonomy-grade) patterns map to which risk tier, and the risk tier scale itself (§4); **the autonomy ladder itself — the grade levels, their labels and meanings, and their order (`vocabulary/grades.json`), which granted grade an actor is conferred, and which required grade a checkpoint sets**; which authority a delegator may pass; whether a delegate inherits the delegator's reservation/quorum restrictiveness; whether every principal chain must be rooted — terminate at a `human` or at a party-bearing actor (§6); and the relation (if any) between a withheld evaluation and a post-intervention activation.
- **Outside this specification**: the means of execution, scheduling, storage, presentation, communication, and disclosure; the measurement of durations; the means of tamper-evidence and external witnessing; the runtime conferral of authority on a sub-actor; the authentication of party assignments (on which the separation-of-duty distinctness check depends, §4, §6); the integrity of `tags` assignments (on which a tag-guard's information-flow property depends, exactly as the party-guard depends on an external party binding, §4, §6); and the discharge of any obligation attached at egress.

This specification does not execute, schedule, branch, iterate, compute, or communicate.

## 11. Grounding annex — relationship to established terminology

This language adopts established terminology where one exists and declares as primitives those concepts no standard names — the role-names *master* and *source gate*, and "AI agent", undefined by [ISO22989], [NIST], and [AIA].

| Loomground construct | Established term / source |
| --- | --- |
| object of governance | AI system [AIA Art. 3(1)]; autonomy/heteronomy concepts [ISO22989] |
| `actor` node | object-capability subject / principal [OCAP]; subject [XACML] |
| `master` node | the node at which the policy enforcement point [XACML] attaches; graph-theoretic sink (role-name a language primitive) |
| source gate | gate fed by a proposing actor's action delivered by the transport; a decision request at the policy decision point [XACML] (role-name a language primitive) |
| authority cord / no ambient authority | designation-based access, capability [OCAP]; least privilege, complete mediation [PROT]; AC-3/AC-6 [NIST80053]; [RBAC, ABAC] |
| delegation / attenuation | on-behalf-of binding; delegation MUST NOT amplify granted authority [OCAP]; bounds grants only (§6) |
| `prohibited` verdict | a policy-declared `Deny` invariant under the subject's privileges (explicit deny rule) [XACML] |
| `refused` verdict | denial for want of an authorizing grant: `Deny` or deny-biased `Indeterminate` [XACML]; AC-3 [NIST80053]; fail-safe defaults [PROT] |
| `party` | accountability role: controller/processor [GDPR Art. 4(7), 4(8), 24, 28, 29]; provider/deployer [AIA Art. 3(3), 3(4)]; illustrative, not definitional |
| token `risk` | a level of risk [ISO31073] per a risk-management process [ISO31000; ISO23894; NIST]; not the [AIA] Arts. 6–7 tier |
| autonomy grade (ordered axis) | a level on a degree-of-automation scale [Sheridan78]; types and levels of human–automation interaction [PSW00]; the level-of-autonomy concept [ISO22989] — the axis is a language primitive, the ordered ladder and level meanings are policy (`vocabulary/grades.json`) |
| grade-gated `human` disposition | human-oversight measures [AIA Art. 14 (provider), Art. 26 (deployer)]; human-in-/on-the-loop; an insufficient granted grade withholds pending oversight — the existing role-less `human`, not a new verdict |
| grade attenuation under delegation | granted grade MUST NOT be amplified by delegation, pairwise over actor→actor links [OCAP; PROT]; bounds delegated autonomy only (§6) |
| consignment / transfer | the recipient of a released action, and the purposes it is released under; an actor cannot license onward a purpose it was not itself given (onward-transfer restriction, sub-processor flow-down) [AGENCY]; [GDPR] Art. 28(4), Ch. V |
| mandate attenuation under delegation | the purpose authority was conferred for; a delegate's mandate MUST be a subset of its delegator's, pairwise over actor→actor links, so an agent cannot confer a purpose it was not itself given [AGENCY; OCAP]; records and bounds purpose only, and judges no conduct (§6) |
| principal chain (on-behalf-of, rooted) | agency: the agent acts on the principal's behalf and subject to the principal's control [AGENCY]; chained actor claims (`act`, `may_act`) [RFC8693]; the acyclic chain and its projection are language, rooting it is policy (§6, §10) |
| `reserved` verdict | human oversight [AIA Art. 14 (provider), Art. 26 (deployer)]; MAY support human intervention [GDPR Art. 22(3)] where the human is competent to reconsider — a condition the language does not guarantee |
| quorum | separation of duties, dual/m-of-n control [SOD; CW]; distinctness over `party` (§6) |
| egress obligation | transparency obligations attached on egress [AIA Art. 50] |
| redress | right to contest a solely-automated decision and obtain human intervention [GDPR Art. 22(3)]; right to an effective remedy [GDPR Arts. 77–79; Charter Art. 47]; the oversight power to intervene, override, or halt [AIA Art. 14(4)]. Declares the right (re-examination owed, empowered to overturn, within a window); the re-examination is a fresh activation and any reversal/recall is outside this specification (§6, §7.3) |
| tag guard / information-flow constraint | a release condition over declared data-flow categories (origin, lineage, synthetic, taint), tested by membership; label-based flow control [IFC; FLUME]; cross-border-transfer and purpose-limitation bases [GDPR Art. 44–49; Art. 5(1)(b)] |
| log / provenance | provenance [PROV-DM]; tamper-evident log dependent on external witnessing [CT, TS]; accountability [GDPR Art. 5(2)] |

## 12. References

### Normative

[RFC2119] IETF RFC 2119 (BCP 14), 1997. [RFC8174] IETF RFC 8174 (BCP 14 update), 2017.

### Informative

[RFC2026] IETF RFC 2026, "The Internet Standards Process — Revision 3", 1996. [RFC6410] IETF RFC 6410, "Reducing the Standards Track to Two Maturity Levels", 2011. [W3CPROCESS] W3C Process Document, current edition (Candidate Recommendation exit criteria). [PLOTKIN] Plotkin, "A Structural Approach to Operational Semantics", 1981. [OCAP] Miller, Robust Composition, 2006. [PROT] Saltzer & Schroeder, "The Protection of Information in Computer Systems", 1975. [IFC] Denning, "A Lattice Model of Secure Information Flow", 1976. [FLUME] Krohn et al., SOSP 2007. [CW] Clark & Wilson, 1987. [CT] IETF RFC 6962, "Certificate Transparency", 2013. [TS] Haber & Stornetta, "How to Time-Stamp a Digital Document", 1991. [PROV-DM] W3C PROV-DM, W3C Recommendation, 2013. [AIA] Reg (EU) 2024/1689 (Artificial Intelligence Act), Arts. 3, 5, 6–7, 14, 26, 50, 85, 86. [GDPR] Reg (EU) 2016/679, Arts. 4, 5, 22, 24, 28, 29, 44–49, 77–79. [Charter] Charter of Fundamental Rights of the European Union (2012/C 326/02), Art. 47. [ISO22989] ISO/IEC 22989:2022. [ISO42001] ISO/IEC 42001:2023. [ISO31000] ISO 31000:2018. [ISO31073] ISO 31073:2022 (which replaced ISO Guide 73:2009). [ISO23894] ISO/IEC 23894:2023. [ISO27001] ISO/IEC 27001:2022. [NIST] NIST AI RMF 1.0 (NIST AI 100-1), 2023. [NIST80053] NIST SP 800-53 Rev. 5, 2020. [Sheridan78] Sheridan, T. B. & Verplank, W. L., "Human and Computer Control of Undersea Teleoperators", MIT Man–Machine Systems Laboratory, 1978. [PSW00] Parasuraman, R., Sheridan, T. B. & Wickens, C. D., "A Model for Types and Levels of Human Interaction with Automation", IEEE Trans. SMC–A, 30(3):286–297, 2000. [SOD] ISO/IEC 27001:2022 Annex A 5.3; NIST SP 800-53 AC-5. [RBAC] ANSI/INCITS 359-2004. [ABAC] NIST SP 800-162. [XACML] OASIS XACML 3.0 (Core, 22 January 2013). [AGENCY] Restatement (Third) of Agency §1.01, American Law Institute, 2006 (cf. BGB §§164–181, Stellvertretung). [RFC8693] IETF RFC 8693, "OAuth 2.0 Token Exchange", 2020 (the `act` and `may_act` claims).
