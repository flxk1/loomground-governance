# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""The conformance harness runs end-to-end over every published vector and returns
a well-formed ConformanceReport.

Reference implementations are out of scope for this repository (README, Status), so
this exercises ``run_conformance`` against a minimal, deliberately non-conforming
stub. It pins that the harness *processes every vector and reports* — not that any
real implementation conforms — closing the gap where the flagship ``run_conformance``
path had no test coverage.
"""
from loomground_governance import (
    ConformanceReport,
    LoomgroundImplementation,
    conformance_manifest,
    iter_vectors,
    run_conformance,
)


class _StubImplementation:
    """Minimal stand-in satisfying the structural ``LoomgroundImplementation``
    protocol so ``run_conformance`` can drive it. It implements nothing, so it
    conforms to nothing — which is exactly what exercises the harness's failure path.
    """

    def parse(self, source):
        return {"source": source}

    def validate(self, program):
        return {"ok": False, "errors": ["stub: not implemented"]}

    def project(self, program):
        return {}

    def validate_token(self, token):
        return False

    def evaluate(self, program, transport):
        return {}

    def evaluate_log(self, program, transport):
        return []


def test_run_conformance_processes_every_vector_and_returns_a_report():
    impl = _StubImplementation()
    assert isinstance(impl, LoomgroundImplementation)  # structural protocol satisfied
    report = run_conformance(impl)
    assert isinstance(report, ConformanceReport)
    total = len(tuple(iter_vectors()))
    assert total == len(conformance_manifest()["vectors"]) > 0
    # every vector is processed exactly once: passed + failed == total
    assert report.passed + len(report.failures) == total


def test_run_conformance_detects_a_non_conforming_implementation():
    report = run_conformance(_StubImplementation())
    # a stub that implements nothing cannot pass the whole suite
    assert not report.ok
    assert report.failures
    # ConformanceReport.ok stays consistent with its failures
    assert report.ok == (not report.failures)
