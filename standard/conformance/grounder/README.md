<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# Grounder support gold corpus

Labelled claim–quote pairs for evaluating a grounder's support judgement
(`supports` / `does_not_support` / `insufficient`), with the acceptance bar
in the corpus `_meta` line. This is conformance *data*, not a vector set:
implementations gate their grounder against it; it does not define language
semantics. The template file is a worked example — three annotated rows, one
per label, with a `_comment` row giving the target size and the pass bar —
for producing a fresh annotation round; it is not a copy of the gold set's 36
records with labels stripped.

The corpus lives here because the language project owns all conformance
data; consumers read it from the packaged artifact tree
(`artifacts/conformance/grounder/`).
