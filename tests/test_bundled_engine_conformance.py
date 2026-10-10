# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""The bundled skill engine (skills/loomground/loomground.py) is a real,
non-stub implementation -- it conforms, or it does not. This drives it through
the same run_conformance the kit exposes to any implementation, via a thin
adapter satisfying LoomgroundImplementation, so the engine is held to the full
contract (conformance/README.md): stage AND reason on every negative vector,
whole-observation equality, and the determinism rules -- not just the
stage-only check tools/check_companion.py already runs independently.

The engine ships beside the skill, loaded by path here, the same way
test_rack_expansion.py and tools/check_companion.py load it.
"""
import importlib.util
from pathlib import Path

from loomground_governance import run_conformance

ENGINE = Path(__file__).resolve().parents[1] / "skills" / "loomground" / "loomground.py"


def _load_engine():
    spec = importlib.util.spec_from_file_location("loomground_engine", ENGINE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class _EngineAdapter:
    """Adapts the module-level engine functions to LoomgroundImplementation."""

    def __init__(self, engine):
        self._engine = engine

    def parse(self, source):
        return self._engine.parse(source)

    def validate(self, program):
        try:
            self._engine.check(program)
        except self._engine.Reject as exc:
            report = {"ok": False, "stage": exc.stage, "errors": [str(exc)]}
            report["reason"] = exc.reason
            return report
        return {"ok": True}

    def project(self, program):
        patch = self._engine.check(program)
        return self._engine.project(patch)

    def validate_token(self, token):
        return self._engine.validate_token(token)

    def evaluate(self, program, transport):
        patch = self._engine.check(program)
        results, _log = self._engine.evaluate(patch, transport["activations"])
        return results

    def evaluate_log(self, program, transport):
        patch = self._engine.check(program)
        _results, log = self._engine.evaluate(patch, transport["activations"])
        return log


def test_bundled_engine_reproduces_every_conformance_vector():
    report = run_conformance(_EngineAdapter(_load_engine()))
    assert report.ok, report.failures
    assert report.passed == report.total
