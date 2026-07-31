# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""Rack pre-pass substitution is literal in the bundled validation engine.

The engine ships beside the skill (skills/loomground/loomground.py), not in the
adoption-kit package, so it is loaded by path here — the same way the companion
gate (tools/check_companion.py) loads it.
"""
import importlib.util
from pathlib import Path

ENGINE = Path(__file__).resolve().parents[1] / "skills" / "loomground" / "loomground.py"


def _load_engine():
    spec = importlib.util.spec_from_file_location("loomground_engine", ENGINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_rack_binding_value_with_backslash_group_substitutes_literally():
    engine = _load_engine()
    # `\1` is a regex backreference; used as an unguarded re.sub replacement it
    # raises re.error. The binding value must be treated as literal text.
    lines = ["rack r(x):", "gate g name $x", "end", "rack-use r(x=v\\1)"]
    out = engine.expand_racks(lines)
    assert "gate g name v\\1" in out
