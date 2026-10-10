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


class _StubAlwaysRaises:
    """Raises on every input. Before the reason-code check existed, this stub
    scored 4/69: it slipped past the 4 parse-stage negative vectors (any
    exception during parse looked like a correct rejection, whatever the
    exception actually said). It MUST now score zero: a bare exception
    carries no `reason`, so it cannot match any vector's closed-set code."""

    def parse(self, source):
        raise RuntimeError("stub: raises on every input")

    def validate(self, program):
        return {"ok": True}

    def project(self, program):
        return {}

    def validate_token(self, token):
        return True

    def evaluate(self, program, transport):
        return {}

    def evaluate_log(self, program, transport):
        return []


class _StubRejectsEveryPatchAtApply:
    """Parses everything, then rejects every patch at apply with no reason.
    Before the reason-code check existed, this stub scored 27/69: every
    apply-stage negative vector looked satisfied by `ok: False` alone. It
    MUST now score zero: it never reports a `reason`, so it cannot match any
    vector's declared code, and it still fails every positive vector by
    rejecting a well-formed graph outright."""

    def parse(self, source):
        return {"source": source}

    def validate(self, program):
        return {"ok": False, "errors": ["stub: rejects every patch at apply"]}

    def project(self, program):
        return {}

    def validate_token(self, token):
        return False

    def evaluate(self, program, transport):
        return {}

    def evaluate_log(self, program, transport):
        return []


class _StubParseReraisesApply:
    """Runs the semantic check inside ``parse()`` and raises there instead of
    deferring the failure to ``validate()``. The exception it raises carries
    the *correct* ``reason`` for the vector (and even claims ``stage: apply``
    on itself) — proving that correctness does not matter here: an exception
    raised while parsing MUST fail an apply-stage vector regardless of what
    it reports about itself, because the rule is architectural (the input
    must survive parsing), not about whether the cause named happens to be
    right."""

    def __init__(self, reasons_by_source):
        self._reasons_by_source = reasons_by_source

    def parse(self, source):
        if source in self._reasons_by_source:
            exc = AssertionError("stub: semantic check ran inside parse")
            exc.reason = self._reasons_by_source[source]
            exc.stage = "apply"
            raise exc
        return {"source": source}

    def validate(self, program):
        return {"ok": True}

    def project(self, program):
        return {}

    def validate_token(self, token):
        return True

    def evaluate(self, program, transport):
        return {}

    def evaluate_log(self, program, transport):
        return []


def test_stub_that_raises_on_every_input_fails_the_whole_kit():
    report = run_conformance(_StubAlwaysRaises())
    assert not report.ok
    assert report.passed == 0


def test_stub_that_rejects_every_patch_at_apply_fails_the_whole_kit():
    report = run_conformance(_StubRejectsEveryPatchAtApply())
    assert not report.ok
    assert report.passed == 0


def test_stub_that_reraises_the_right_reason_inside_parse_still_fails_apply_vectors():
    reasons_by_source = {}
    apply_stage_names = set()
    for vector in iter_vectors():
        if vector.kind != "negative":
            continue
        reject = vector.json("reject.json")
        if reject.get("stage") == "apply":
            reasons_by_source[vector.text("input.lg")] = reject.get("reason")
            apply_stage_names.add(vector.name)
    assert apply_stage_names  # the fixture set is non-empty

    report = run_conformance(_StubParseReraisesApply(reasons_by_source))
    assert not report.ok
    failed_names = {failure["name"] for failure in report.failures}
    assert apply_stage_names <= failed_names
