# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""Prove the claim-axes reference adapter is genuinely third-party.

standard/companions/claim-axes/reference/ exists to prove the claim-axes
companion contract is implementable by a party with no access to this
project's product code -- only the published schema, profile, and
conformance vectors. That is only a checked property, not a claim, if
something forbids the reference from quietly importing the product it is
supposed to be independent of.

This gate AST-parses every .py file under that directory and fails if any
of them import `versum`, `loomground_solver`, or `loomground_governance` (or
any submodule of those) -- by `import x`, `import x.y`, or `from x import y`.

Run standalone: python3 tools/check_reference_isolation.py [LOOMGROUND_ROOT]
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
REFERENCE = ROOT / "standard" / "companions" / "claim-axes" / "reference"

BANNED_ROOTS = {"versum", "loomground_solver", "loomground_governance"}


def _banned_root(module_name: str | None) -> str | None:
    if not module_name:
        return None
    top = module_name.split(".")[0]
    return top if top in BANNED_ROOTS else None


def check_file(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    failures = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                bad = _banned_root(alias.name)
                if bad:
                    failures.append(
                        f"{path}: `import {alias.name}` imports banned product "
                        f"root {bad!r}")
        elif isinstance(node, ast.ImportFrom):
            bad = _banned_root(node.module)
            if bad:
                failures.append(
                    f"{path}: `from {node.module} import ...` imports banned "
                    f"product root {bad!r}")
    return failures


def main() -> int:
    if not REFERENCE.is_dir():
        sys.exit(f"check_reference_isolation.py: no such directory: {REFERENCE}")

    failures: list[str] = []
    files = sorted(REFERENCE.rglob("*.py"))
    for path in files:
        failures.extend(check_file(path))

    print(f"reference isolation gate against {REFERENCE}\n")
    print(f"[{'FAIL' if failures else 'PASS'}] no product imports ({len(files)} files checked)")
    if failures:
        print()
        for f in failures:
            print(f"  {f}")
        return 1
    print("\nALL GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
