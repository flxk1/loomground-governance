<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# Positioning & prior art

Moved verbatim from the README.

In access-control terms, Loomground's evaluation model is a policy-decision point
(PDP): a proposing actor's action reaches a source gate, a verdict is produced,
and a single master node is where a policy-enforcement point attaches. That
model, and most of the individual primitives, are deliberately not new — each
parallels, and in a hosted setting could be expressed on, a stronger and more
general incumbent:

- **Decision and combining.** The verdict lattice
  (`auto → human → refused → reserved → prohibited`, joined as "most restrictive
  wins", with `prohibited` overriding any grant) is the deny-overrides combining
  algorithm of **OASIS XACML 3.0**, **AWS Cedar**, and **OPA/Rego**; `refused` is
  their deny-biased indeterminate / fail-safe default.
- **Obligations.** `egress-obligation` — the master releases only when a named
  duty is attached — is XACML obligations and **W3C ODRL** duties.
- **Attenuating delegation.** `on-behalf-of` on an authority cord, bound by a
  no-amplification invariant, is object-capability attenuation (**UCAN**; OAuth
  token exchange, RFC 8693; least privilege).
- **Tamper-evident record.** The ordered evaluation trace is meant to be
  witnessed the way a transparency log is — **Certificate Transparency**,
  **Sigstore/Rekor**, **Google Trillian** — with provenance in the shape of
  **W3C PROV**.
- **The rest.** `quorum` is dual / m-of-n control (separation of duty,
  Clark–Wilson); tag guards are label-based information-flow control (IFC/FLUME);
  autonomy grades are Sheridan-style levels of automation.

None of this is a discovery of the specification: it is recorded
construct-by-construct in the normative Grounding annex and in
`standard/vocabulary/grounding.json`. This section only names the concrete modern
tools next to the abstract sources cited there.

Keeping the vocabulary closed and building it in-house is a deliberate trade.
Loomground ships as a data-only artifact — grammar, schemas, vocabulary, and
conformance vectors, with no engine, runtime, or host dependency — so it forgoes
the breadth of a general policy engine (an arbitrary condition language, a
resource model, a distributed log) in exchange for a surface a single reviewer
can read end to end, diff in review, validate offline, and re-implement from the
vectors alone. It is a small fixed vocabulary, not a profile layered on Cedar or
a XACML dialect.

What is genuinely distinctive is not any single primitive but the shape of the
vocabulary: it is oversight-first and EU-AI-Act-legible rather than
resource-permission-first. `reserved` — refer this action to a person — is a
first-class verdict, not an obligation bolted onto a permit; `human` is a
first-class node kind that anchors answerability and confers no authority, and a
bearer that matches no role stays `unattributed` rather than being forced into
one. Each declaration carries a grounding to a specific legal instrument (EU AI
Act Art. 5/14/26/50, GDPR Art. 22/28, Charter Art. 47), so a patch is diffable
against the obligations it claims to discharge. A general PDP can encode all of
this; what Loomground adds is a closed surface where human oversight and
contestability are the primitives rather than an encoding convention.

The language declares and records *when* an action must be referred to a person
and *what* is then owed — re-examination, redress, a transparency duty. It does
not decide whether a given policy satisfies the law that policy cites, and by
construction it does not execute, store, or transport anything. That boundary is
the point.
