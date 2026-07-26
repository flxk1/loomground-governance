#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 flxk1
"""Check the compact language summaries against canonical machine sources.

Expectations are derived from the canonical machine sources in `standard/` — the
vocabulary and token schema, which track the spec — not from the hand-maintained
language card. The check then also asserts the card matches those canonical
sources, so neither llms.txt nor the card can silently drift from the language.

Three independent version axes exist by design and this gate must never collapse
them into one number:

  1. package/release  — pyproject.toml, the language card, the conformance
                         manifest, and the tree-sitter grammar's own metadata.
                         This gate asserts all four agree (this file).
  2. contract/protocol — the claim-axes version, the profile version, and the
                         `loomground.language/*` media-type version. Frozen
                         independently of the package release; this gate does
                         not touch it.
  3. plugin/distribution — package.json and .claude-plugin/plugin.json. This
                         gate asserts those two agree with each other (see
                         tools/check_companion.py, check_manifests) but never
                         requires the plugin version to equal the package
                         version above — the plugin ships on its own cadence.

Run by CI; exits non-zero on any drift.
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _load(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return json.load(fh)


def _text(rel):
    with open(os.path.join(ROOT, rel), encoding="utf-8") as fh:
        return fh.read()


# ── canonical truth: the vocabulary + the token schema (these track the spec) ──
NODES = [c["class"] for c in _load("standard/vocabulary/node-classes.json")]
CORDS = [c["type"] for c in _load("standard/vocabulary/cords.json")["permitted"]]
VERDICTS = _load("standard/vocabulary/verdicts.json")["alphabet"]
DECLS = [d["name"] for d in _load("standard/vocabulary/declarations.json")]
GUARD_FIELDS = _load("standard/vocabulary/guard-domain.json")["ranges_over"]
GRADES = _load("standard/vocabulary/grades.json")["levels"]
_tok_schema = _load("standard/schema/token.schema.json")
TOKEN_FIELDS = list(_tok_schema["required"]) + [
    p for p in _tok_schema["properties"] if p not in _tok_schema["required"]
]  # required + optional (tags)

llms = _text("llms.txt")
card = _load("standard/language-card.json")
manifest = _load("standard/conformance/manifest.json")
errors: list[str] = []

# declaration name (canonical) -> the surface keyword it appears as in llms.txt
DECL_KEYWORD = {
    "reservation": "reserve", "quorum": "quorum", "prohibition": "prohibit",
    "temporal": "temporal", "egress-obligation": "obligation", "redress": "redress",
    "party": "party", "delegation": "delegation", "autonomy-grade": "grade",
}


def need(token, what):
    # Word-boundary match, not substring: `auto` must not match inside `automated`,
    # `id` inside `valid`, `L0` inside `L05`. Letters/digits count as word chars.
    if not re.search(r"(?<![A-Za-z0-9])" + re.escape(token) + r"(?![A-Za-z0-9])", llms):
        errors.append(f"llms.txt {what}: {token!r} not found (as a whole word)")


def count_header(label, expected):
    m = re.search(rf"{label} \((\d+)\)", llms)
    if not m:
        errors.append(f"llms.txt: missing count header '{label} (N)'")
    elif int(m.group(1)) != expected:
        errors.append(f"llms.txt: '{label} ({m.group(1)})' header != {expected}")


# ── 1. llms.txt covers every element of the canonical language ──
for n in NODES: need(n, "node class")
for v in VERDICTS: need(v, "verdict")
for t in TOKEN_FIELDS: need(t, "token field")
for f in GUARD_FIELDS: need(f, "guard field")
for lvl in GRADES: need(lvl, "grade level")
for d in DECLS: need(DECL_KEYWORD.get(d, d), f"declaration '{d}'")
count_header("Nodes", len(NODES))
count_header("Cords", len(CORDS))
count_header("Declarations", len(DECLS))

# ── 2. the hand-maintained card must itself match the canonical sources ──
def card_eq(field, canonical):
    got = card.get(field)
    if got != canonical:
        errors.append(f"language-card.json {field} {got} != canonical {canonical}")

card_eq("nodes", NODES)
card_eq("verdicts", VERDICTS)
card_eq("token", TOKEN_FIELDS)
card_eq("declarations", DECLS)
for ct in CORDS:  # card cords are formatted strings, e.g. "authority (actor -> gate)"
    if not any(ct in c for c in card.get("cords", [])):
        errors.append(f"language-card.json cords omit the {ct!r} cord type")

# Package, language card, and conformance kit are released as one compatibility unit.
project = _text("pyproject.toml")
project_version = re.search(r'^version\s*=\s*"([^"]+)"', project, re.MULTILINE)
if not project_version:
    errors.append("pyproject.toml has no project version")
elif project_version.group(1) != card.get("version"):
    errors.append(
        f"pyproject.toml version {project_version.group(1)!r} != "
        f"language-card.json version {card.get('version')!r}"
    )
if manifest.get("version") != card.get("version"):
    errors.append(
        f"conformance manifest version {manifest.get('version')!r} != "
        f"language-card.json version {card.get('version')!r}"
    )
tree_sitter = _load("standard/grammar/tree-sitter/tree-sitter.json")
tree_sitter_version = tree_sitter.get("metadata", {}).get("version")
if tree_sitter_version != card.get("version"):
    errors.append(
        f"tree-sitter.json metadata.version {tree_sitter_version!r} != "
        f"language-card.json version {card.get('version')!r}"
    )
if card.get("status") not in {"draft", "stable", "deprecated"}:
    errors.append(f"language-card.json has invalid status {card.get('status')!r}")


def artifact_refs(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for nested in value.values():
            yield from artifact_refs(nested)


card_root = os.path.join(ROOT, "standard")
for rel in artifact_refs(card.get("artifacts", {})):
    if not os.path.exists(os.path.join(card_root, rel)):
        errors.append(f"language-card.json artifact does not resolve: {rel!r}")

if errors:
    print("DRIFT — out of sync with the canonical language:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(
    "in sync with the canonical language (vocabulary + token schema): "
    f"{len(NODES)} nodes, {len(CORDS)} cords, {len(VERDICTS)} verdicts, "
    f"{len(TOKEN_FIELDS)} token fields, {len(GUARD_FIELDS)} guard fields, "
    f"{len(GRADES)} grade levels, {len(DECLS)} declarations — llms.txt covers all, "
    f"the card matches, and version {card['version']} ({card['status']}) is aligned."
)
