# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""Check that the token schema's risk/kind invariants hold.

The token's `risk` field is gate-computed from a governed, versioned, signed
policy table (specification, The token) — its enum is a fixed, ordered
severity scale, not an open vocabulary. The token's `kind` field is
host-observed at the tool-call/effect boundary — derived from the operation
actually performed as the host sees it, never asserted or declared by the
acting actor — so it must stay an open string with no closed enum.

Nothing currently stops either property from drifting silently: reordering
`risk.enum`, dropping or adding a risk value, or fixing an `enum` onto `kind`
would each break a documented, load-bearing property of the standard without
any gate firing. This gate makes that drift a CI failure instead (stdlib
only):

  i.  risk enum   — properties.risk.enum equals exactly
                    ["low", "medium", "high", "critical"], in that order.
  ii. kind open   — properties.kind carries no "enum" key.

Run standalone: python3 tools/check_schema_invariants.py [LOOMGROUND_ROOT]
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
SCHEMA = ROOT / "standard" / "schema" / "token.schema.json"

RISK_ENUM = ["low", "medium", "high", "critical"]


def check_risk_enum(schema: dict, fail: list[str]) -> None:
    risk = schema.get("properties", {}).get("risk", {})
    enum = risk.get("enum")
    if enum is None:
        fail.append("properties.risk has no 'enum' key (expected "
                    f"{RISK_ENUM!r})")
    elif enum != RISK_ENUM:
        fail.append(f"properties.risk.enum is {enum!r}, expected exactly "
                    f"{RISK_ENUM!r} in that order")


def check_kind_open(schema: dict, fail: list[str]) -> None:
    kind = schema.get("properties", {}).get("kind", {})
    if "enum" in kind:
        fail.append("properties.kind carries an 'enum' key "
                    f"({kind['enum']!r}) — kind is host-observed and must "
                    "stay an open string")


def main() -> int:
    schema = json.loads(SCHEMA.read_text())
    fail: list[str] = []
    check_risk_enum(schema, fail)
    check_kind_open(schema, fail)

    print(f"schema-invariants gate against {ROOT}\n")
    print(f"[{'FAIL' if any(f.startswith('properties.risk') for f in fail) else 'PASS'}] "
          f"risk enum is exactly {RISK_ENUM!r}")
    print(f"[{'FAIL' if any(f.startswith('properties.kind') for f in fail) else 'PASS'}] "
          "kind carries no enum")
    if fail:
        print()
        for f in fail:
            print(f"  - {f}")
        return 1
    print("\nALL GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
