# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""Check that the schemas and the conformance vectors agree.

The README states that the JSON Schemas are validated against the vectors.
Nothing enforced that: a schema edit could silently orphan every vector, or a
new vector could ship a shape no schema admits. This gate makes the claim
checkable:

  A. observation — every vector expected.json validates against
                   standard/schema/observation.schema.json.
  B. transport   — every vector transport.json validates against
                   standard/schema/transport.schema.json.
  C. token       — every record in token-validation/tokens.json agrees with
                   standard/schema/token.schema.json: a record marked valid
                   validates, a record marked invalid does not.
  D. patch       — standard/schema/patch.schema.json describes the authored
                   interchange form (nodes, grants, cords, reservations,
                   prohibitions, obligations, redress), not the post-evaluation
                   observation, so no vector ships in its shape on disk. It is
                   derived per "patch"-kind vector via the companion skill's
                   parser (skills/loomground/loomground.py: parse -> check ->
                   to_patch) and validated. This is the one check here that
                   needs the companion engine rather than only on-disk vector
                   files; without it, patch.schema.json is untested and can
                   silently reject grammar the language actually permits (as
                   it did for the `name` node clause until this check caught it).

Requires jsonschema (the one tools/ check with a dependency; CI installs it).

Run standalone: python3 tools/check_vectors.py [LOOMGROUND_ROOT]
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

try:
    from jsonschema import Draft202012Validator
except ImportError:
    sys.exit("check_vectors.py needs jsonschema: python3 -m pip install jsonschema")

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
VECTORS = ROOT / "standard" / "conformance" / "vectors"
SCHEMA = ROOT / "standard" / "schema"
ENGINE = ROOT / "skills" / "loomground" / "loomground.py"


def _load(path: Path):
    return json.loads(path.read_text())


def _load_engine():
    spec = importlib.util.spec_from_file_location("loomground", ENGINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main() -> int:
    obs = Draft202012Validator(_load(SCHEMA / "observation.schema.json"))
    tra = Draft202012Validator(_load(SCHEMA / "transport.schema.json"))
    tok = Draft202012Validator(_load(SCHEMA / "token.schema.json"))
    failures: list[str] = []

    checked_obs = 0
    for f in sorted(VECTORS.glob("*/expected.json")):
        errs = list(obs.iter_errors(_load(f)))
        checked_obs += 1
        if errs:
            failures.append(f"observation: {f.parent.name}: {errs[0].message}")

    checked_tra = 0
    for f in sorted(VECTORS.glob("*/transport.json")):
        errs = list(tra.iter_errors(_load(f)))
        checked_tra += 1
        if errs:
            failures.append(f"transport: {f.parent.name}: {errs[0].message}")

    checked_tok = 0
    for rec in _load(VECTORS / "token-validation" / "tokens.json"):
        errs = list(tok.iter_errors(rec["token"]))
        checked_tok += 1
        if rec["valid"] and errs:
            failures.append(f"token: valid record rejected "
                            f"({rec['token'].get('id', '?')}): {errs[0].message}")
        if not rec["valid"] and not errs:
            failures.append(f"token: invalid record accepted: {json.dumps(rec['token'])}")

    L = _load_engine()
    pat = Draft202012Validator(_load(SCHEMA / "patch.schema.json"))
    checked_pat = 0
    for d in sorted(p for p in VECTORS.iterdir() if p.is_dir()):
        lg = d / "input.lg"
        if not lg.exists() or not (d / "expected.json").exists():
            continue  # only well-formed "patch"-kind vectors parse+check to a patch
        patch = L.check(L.parse(lg.read_text()))
        errs = list(pat.iter_errors(L.to_patch(patch)))
        checked_pat += 1
        if errs:
            failures.append(f"patch: {d.name}: {errs[0].message}")

    print(f"schema gate against {ROOT}\n")
    for name, n in (("observation", checked_obs), ("transport", checked_tra),
                    ("token", checked_tok), ("patch", checked_pat)):
        print(f"[{'FAIL' if any(x.startswith(name) for x in failures) else 'PASS'}] "
              f"{name} schema ↔ vectors ({n} checked)")
    if failures:
        print()
        for f in failures:
            print(f"  {f}")
        return 1
    print("\nALL GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
