# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""Check that the language representations stay in lockstep.

A Loomground feature lives in four places — the grammar (you can write it), the parser,
the projection + observation schema (the canonical form), and a conformance vector (it is
tested). Nothing currently asserts a feature reaches all four, so features land unevenly:
`redress … within` made it through all four; `reserve … duration : halt|proceed` and the
`quorum` target stopped at the grammar/parser and were never projected, schema'd, or
tested. This gate makes that drift a CI failure instead of a silent hole.

Three checks (stdlib only), each reporting exactly what is uncovered:

  A. declaration → vector   — every declaration in the vocabulary is
                              exercised by at least one conformance vector input.lg.
  B. schema field → vector  — every property the observation schema projects appears in
                              at least one vector expected.json.
  C. grammar literal → vector — every feature keyword in the EBNF appears in at least one
                              vector input.lg (mechanical; value-literals are ignored).

Run standalone: python3 tools/check_lockstep.py [LOOMGROUND_ROOT]
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path


# ── locate the Loomground repo root ──────────────────────────────────────────
def _root() -> Path:
    if len(sys.argv) > 1 and sys.argv[1]:
        return Path(sys.argv[1])
    env = os.environ.get("LOOMGROUND_ROOT")
    if env:
        return Path(env)
    here = Path(__file__).resolve()
    for up in here.parents:
        if (up / "standard" / "conformance" / "manifest.json").is_file():
            return up
        if (up / "Loomground" / "standard" / "conformance" / "manifest.json").is_file():
            return up / "Loomground"
    raise FileNotFoundError("set LOOMGROUND_ROOT or pass the repo root as argv[1]")


ROOT = _root()


def _vectors() -> list[Path]:
    man = json.loads((ROOT / "standard" / "conformance" / "manifest.json").read_text())
    return [ROOT / "standard" / "conformance" / "vectors" / v["name"] for v in man["vectors"]]


def _inputs() -> str:
    """All vector input.lg STATEMENTS concatenated (comments stripped — prose in a
    `# …` comment must never create false coverage for a keyword)."""
    out = []
    for d in _vectors():
        f = d / "input.lg"
        if f.is_file():
            out.append("\n".join(ln.split("#", 1)[0] for ln in f.read_text().splitlines()))
    return "\n".join(out)


def _expected_keys() -> set[str]:
    """Every JSON key that appears in any vector expected.json."""
    keys: set[str] = set()

    def walk(o):
        if isinstance(o, dict):
            keys.update(o.keys())
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    for d in _vectors():
        f = d / "expected.json"
        if f.is_file():
            walk(json.loads(f.read_text()))
    return keys


# ── A. declaration → vector ──────────────────────────────────────────────────
# Each declared declaration must have ≥1 probe that matches some vector input.lg.
# Adding a declaration with no probe here is itself a failure (forces the author to
# wire coverage), and a probe that matches nothing means no vector exercises it.
DECLARATION_PROBES: dict[str, list[str]] = {
    "reservation":       [r"(?m)^\s*reserve\b"],
    "quorum":            [r"\bby\b.*\band\b", r"\bof\s*\{"],
    "prohibition":       [r"(?m)^\s*prohibit\b"],
    "temporal":          [r"\bduration\b"],
    "egress-obligation": [r"(?m)^\s*obligation\b"],
    "redress":           [r"(?m)^\s*redress\b"],
    "party":             [r"\bparty\b"],
    "delegation":        [r"\bon-behalf-of\b"],
    "mandate":           [r"\bmandate\b"],
    "autonomy-grade":    [r"\bgrade\b"],
}


def check_declaration_coverage() -> list[str]:
    corpus = _inputs()
    declared = [d["name"] for d in json.loads(
        (ROOT / "standard" / "vocabulary" / "declarations.json").read_text())]
    fails = []
    for name in declared:
        probes = DECLARATION_PROBES.get(name)
        if probes is None:
            fails.append(f"declaration {name!r}: no coverage probe defined (add one to keep lockstep)")
            continue
        if not any(re.search(p, corpus) for p in probes):
            fails.append(f"declaration {name!r}: no conformance vector exercises it ({probes})")
    return fails


# ── B. schema field → vector ─────────────────────────────────────────────────
def _schema_property_names() -> set[str]:
    schema = json.loads(
        (ROOT / "standard" / "schema" / "observation.schema.json").read_text())
    names: set[str] = set()

    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("properties"), dict):
                names.update(o["properties"].keys())
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)

    walk(schema)
    return names


def check_schema_field_coverage() -> list[str]:
    present = _expected_keys()
    return [f"observation schema projects {n!r} but no expected.json contains it"
            for n in sorted(_schema_property_names()) if n not in present]


# ── C. grammar literal → vector ──────────────────────────────────────────────
# Mechanical: every lowercase feature keyword in the EBNF must appear in some input.lg.
# Value-literals (risk levels, grade levels, the obligation enum, structural names) are
# choices, not features, and are ignored. Extend IGNORE when the grammar adds a value set.
_IGNORE = {
    "low", "medium", "high", "critical",                       # risk values
    "master",                                                  # structural endpoint
    "ai-interaction-disclosure", "synthetic-content-marking",  # obligation enum values
    "emotion-or-biometric-disclosure", "deepfake-disclosure", "data-minimisation",
}


def _grammar_keywords() -> set[str]:
    ebnf = (ROOT / "standard" / "grammar" / "loomground.ebnf").read_text()
    lits = set(re.findall(r'"([^"]+)"', ebnf))
    kw = {t for t in lits if re.fullmatch(r"[a-z][a-z-]{2,}", t)}  # lowercase words, len≥3
    return kw - _IGNORE


def check_grammar_literal_coverage() -> list[str]:
    corpus = _inputs()
    fails = []
    for kw in sorted(_grammar_keywords()):
        if not re.search(rf"(?<![A-Za-z-]){re.escape(kw)}(?![A-Za-z-])", corpus):
            fails.append(f"grammar keyword {kw!r} appears in no vector input.lg")
    return fails


# ── pytest entry points ──────────────────────────────────────────────────────
def test_declaration_coverage():
    fails = check_declaration_coverage()
    assert not fails, "lockstep (declaration→vector):\n  " + "\n  ".join(fails)


def test_schema_field_coverage():
    fails = check_schema_field_coverage()
    assert not fails, "lockstep (schema→vector):\n  " + "\n  ".join(fails)


def test_grammar_literal_coverage():
    fails = check_grammar_literal_coverage()
    assert not fails, "lockstep (grammar→vector):\n  " + "\n  ".join(fails)


if __name__ == "__main__":
    print(f"lockstep gate against {ROOT}\n")
    total = 0
    for label, fn in (("declaration → vector", check_declaration_coverage),
                      ("schema field → vector", check_schema_field_coverage),
                      ("grammar literal → vector", check_grammar_literal_coverage)):
        fails = fn()
        total += len(fails)
        mark = "PASS" if not fails else "FAIL"
        print(f"[{mark}] {label}")
        for f in fails:
            print(f"        - {f}")
    print(f"\n{'ALL GREEN' if total == 0 else str(total) + ' lockstep gap(s)'}")
    sys.exit(0 if total == 0 else 1)
