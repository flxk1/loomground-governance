# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""standard/ must equal the canonical loomground tree at the tag named in standard/CANONICAL.

Usage: python3 tools/check_canonical.py <path-to-loomground-checkout>   (or $LOOMGROUND_ROOT)
Exit 0 identical · 1 drift · 2 canonical checkout unavailable (never a pass).
"""
from __future__ import annotations
import filecmp, json, os, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
STD = HERE / "standard"
AREAS = ["spec", "grammar", "schema", "vocabulary", "conformance", "examples"]
IGNORE = {"OPERATORS.md", "end-to-end", "__pycache__", ".DS_Store"}


def _diff(a: Path, b: Path, rel: str = "") -> list[str]:
    out: list[str] = []
    cmp = filecmp.dircmp(a, b, ignore=list(IGNORE))
    gen = {"src"} if rel == "grammar/tree-sitter/" else set()  # generated parser; untracked in both repos
    out += [f"only in standard/: {rel}{n}" for n in cmp.left_only if n not in gen]
    out += [f"only in loomground: {rel}{n}" for n in cmp.right_only if n not in gen]
    out += [f"differs: {rel}{n}" for n in cmp.diff_files]
    for d, sub in cmp.subdirs.items():
        if rel == "grammar/tree-sitter/" and d == "src":
            continue
        out += _diff(sub.left, sub.right, f"{rel}{d}/")
    return out


def main() -> int:
    arg = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("LOOMGROUND_ROOT", "")
    root = Path(arg) if arg else None
    pin = (STD / "CANONICAL").read_text().split()
    if not root or not (root / "language-card.json").exists():
        print(f"UNAVAILABLE: no loomground checkout given (want {' '.join(pin)}); pass a path or set LOOMGROUND_ROOT")
        return 2
    problems: list[str] = []
    want = pin[1].lstrip("v")
    for label, card in (("standard/", STD / "language-card.json"), ("loomground", root / "language-card.json")):
        v = json.loads(card.read_text()).get("version")
        if v != want:
            problems.append(f"{label} language-card version {v} != pinned {want}")
    for area in AREAS:
        if (STD / area).exists() and (root / area).exists():
            problems += _diff(STD / area, root / area, f"{area}/")
        else:
            problems.append(f"area missing: {area}")
    if not filecmp.cmp(HERE / "llms.txt", root / "llms.txt", shallow=False):
        problems.append("differs: llms.txt")
    for p in problems:
        print("[DRIFT]", p)
    print("CANONICAL OK: standard/ == loomground", pin[1]) if not problems else print(f"{len(problems)} drift(s) from loomground {pin[1]}")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
