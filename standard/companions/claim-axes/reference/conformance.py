# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 flxk1
"""Conformance runner for the independent claim-axes reference adapter.

Reads vectors/manifest.json (the index, not filename guesswork) and, for
every listed vector, runs its `record` through the reference adapter's
`validate()`, asserting the outcome matches the vector's `valid` flag.

The shared vectors are declared `"kind": "wire-record"` (manifest.json) --
schema-level conformance vectors (COMPANION.md sec 4), not scoped to any one
profile version. Several valid vectors use axis values the shipped
inert-0.1.0 profile does not allow (for example valid-five-axes.json's
predicate "causes"), which is expected: they exercise the wire schema, not a
profile's closed sets. This runner therefore validates with
`profile=None` (wire-schema-only). Profile-level conformance is exercised
separately -- see the round trip and self-check in reference_adapter.py.

Run standalone: python3 standard/companions/claim-axes/reference/conformance.py [ROOT]
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def _load_reference_adapter():
    spec = importlib.util.spec_from_file_location(
        "claim_axes_reference_adapter", HERE / "reference_adapter.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def run_conformance(root: Path) -> tuple[list[str], int]:
    adapter = _load_reference_adapter()
    vectors_dir = root / "standard" / "companions" / "claim-axes" / "vectors"
    manifest = json.loads((vectors_dir / "manifest.json").read_text())

    failures: list[str] = []
    checked = 0
    for name in manifest["vectors"]:
        vector = json.loads((vectors_dir / name).read_text())
        checked += 1
        accepted, reason = adapter.validate(vector["record"], profile=None)
        if vector["valid"] and not accepted:
            failures.append(f"{vector['name']}: expected accept, got reject ({reason})")
        elif not vector["valid"] and accepted:
            failures.append(f"{vector['name']}: expected reject, got accept")
    return failures, checked


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent.parent.parent.parent
    failures, checked = run_conformance(root)

    print(f"claim-axes reference conformance against {root}\n")
    print(f"[{'FAIL' if failures else 'PASS'}] wire-record vectors ({checked} checked)")
    if failures:
        print()
        for f in failures:
            print(f"  {f}")
        return 1
    print("\nALL GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
