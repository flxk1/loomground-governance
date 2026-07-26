# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""Check that the companion skill tracks the language it ships beside.

The skill (skills/loomground/) is non-normative, so the neutrality and
lockstep gates do not scan it — which is exactly how it once drifted a full
language version (`.loom`, 8 declarations, a 5-field token) without any gate
firing. This gate closes that hole (stdlib only):

  A. engine ↔ vectors — the bundled validation engine reproduces every
     conformance vector: projection, rejection stage, transport run
     (per-gate verdict and master decision), the ordered log trace, and
     the token-validation records.
  B. skill text ↔ language — the skill and the plugin manifests speak the
     current language: the retired `.loom` extension and the phrase
     "reference implementation" (the standard names no implementation)
     appear nowhere; SKILL.md states the current declaration count and
     names every token field.
  C. manifest ↔ manifest — package.json and .claude-plugin/plugin.json
     agree on the fields they share (name, version, description, keywords,
     author). This is the plugin/distribution version axis: it is
     independent of the package/release version in pyproject.toml (see
     tools/check_language_summary.py) and is never required to equal it —
     the two manifests must only agree with *each other*.

Run standalone: python3 tools/check_companion.py [LOOMGROUND_ROOT]
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
SKILL = ROOT / "skills" / "loomground"
VECTORS = ROOT / "standard" / "conformance" / "vectors"

BANNED = [
    (re.compile(r"\.loom\b"), "retired extension `.loom` (replaced by `.lg` at v0.6.0)"),
    (re.compile(r"reference\s+implementation", re.I),
     "phrase 'reference implementation' (the standard names no implementation)"),
]
SCANNED = ["skills/loomground/SKILL.md", "skills/loomground/validate.py",
           "package.json", ".claude-plugin/plugin.json"]
SHARED_MANIFEST_FIELDS = ["name", "version", "description", "keywords", "author"]


def _load_engine():
    spec = importlib.util.spec_from_file_location("loomground", SKILL / "loomground.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check_engine(fail):
    L = _load_engine()
    n = 0
    for d in sorted(p for p in VECTORS.iterdir() if p.is_dir()):
        lg = d / "input.lg"
        if not lg.exists():
            continue
        n += 1
        reject = d / "reject.json"
        try:
            patch = L.check(L.parse(lg.read_text()))
        except L.Reject as e:
            if not reject.exists():
                fail.append(f"engine: {d.name}: unexpected reject: {e}")
            elif e.stage != json.loads(reject.read_text())["stage"]:
                fail.append(f"engine: {d.name}: rejected at {e.stage}, "
                            f"expected {json.loads(reject.read_text())['stage']}")
            continue
        if reject.exists():
            fail.append(f"engine: {d.name}: expected reject, got well-formed")
            continue
        expected = json.loads((d / "expected.json").read_text())
        if L.project(patch) != expected:
            fail.append(f"engine: {d.name}: projection mismatch")
        transport = d / "transport.json"
        if transport.exists():
            t = json.loads(transport.read_text())
            results, log = L.evaluate(patch, t["activations"])
            for gate, exp in t["expected"].items():
                got = results.get(gate, {})
                if got.get("verdict") != exp["verdict"]:
                    fail.append(f"engine: {d.name}: {gate} verdict "
                                f"{got.get('verdict')} != {exp['verdict']}")
                if "master" in exp and got.get("master") != exp["master"]:
                    fail.append(f"engine: {d.name}: {gate} master "
                                f"{got.get('master')} != {exp['master']}")
            if log != t["log"]:
                fail.append(f"engine: {d.name}: ordered log trace mismatch")
    for rec in json.loads((VECTORS / "token-validation" / "tokens.json").read_text()):
        if L.validate_token(rec["token"]) != rec["valid"]:
            fail.append(f"engine: token-validation: {rec['token'].get('id', '?')} "
                        f"judged {not rec['valid']}, gold says {rec['valid']}")
    return n


def check_text(fail):
    for rel in SCANNED:
        text = (ROOT / rel).read_text()
        for pattern, why in BANNED:
            if pattern.search(text):
                fail.append(f"text: {rel}: {why}")
    skill_md = (SKILL / "SKILL.md").read_text()
    declarations = json.loads(
        (ROOT / "standard" / "vocabulary" / "declarations.json").read_text())
    if f"the {len(declarations)} declarations" not in skill_md:
        fail.append(f"text: SKILL.md does not state 'the {len(declarations)} "
                    f"declarations' (the current count)")
    token_schema = json.loads(
        (ROOT / "standard" / "schema" / "token.schema.json").read_text())
    for field in token_schema["properties"]:
        if not re.search(rf"\b{field}\b", skill_md):
            fail.append(f"text: SKILL.md never names token field '{field}'")
    guard = json.loads(
        (ROOT / "standard" / "vocabulary" / "guard-domain.json").read_text())
    for field in guard["ranges_over"]:
        if not re.search(rf"`{field}`", skill_md):
            fail.append(f"text: SKILL.md guard list misses `{field}` "
                        f"(guard-domain ranges_over)")


def check_manifests(fail):
    # Plugin/distribution axis only: package.json and plugin.json must agree with
    # each other, but neither is compared against the package/release version
    # (pyproject.toml) — that is a deliberately separate axis, not a drift.
    pkg = json.loads((ROOT / "package.json").read_text())
    plg = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    for field in SHARED_MANIFEST_FIELDS:
        if pkg.get(field) != plg.get(field):
            fail.append(f"manifest: '{field}' differs between package.json "
                        f"and .claude-plugin/plugin.json")


def main() -> int:
    fail: list[str] = []
    n = check_engine(fail)
    check_text(fail)
    check_manifests(fail)
    print(f"companion gate against {ROOT}\n")
    for name, prefix in (("engine ↔ vectors", "engine"),
                         ("skill text ↔ language", "text"),
                         ("manifest ↔ manifest", "manifest")):
        status = "FAIL" if any(x.startswith(prefix) for x in fail) else "PASS"
        extra = f" ({n} vectors)" if prefix == "engine" else ""
        print(f"[{status}] {name}{extra}")
    if fail:
        print()
        for f in fail:
            print(f"  {f}")
        return 1
    print("\nALL GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
