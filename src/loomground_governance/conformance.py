# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""Implementation-neutral access to and execution of conformance vectors."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable

from .artifacts import artifact_path, conformance_manifest, vocabulary
from .protocol import LoomgroundImplementation


@dataclass(frozen=True)
class Vector:
    name: str
    kind: str
    files: tuple[str, ...]
    stage: str = ""

    def text(self, filename: str) -> str:
        return artifact_path("conformance", "vectors", self.name, filename).read_text(
            encoding="utf-8")

    def json(self, filename: str) -> Any:
        return json.loads(self.text(filename))


@dataclass(frozen=True)
class ConformanceReport:
    total: int
    passed: int
    failures: tuple[dict, ...]

    @property
    def ok(self) -> bool:
        return not self.failures


def iter_vectors() -> Iterable[Vector]:
    for item in conformance_manifest()["vectors"]:
        yield Vector(item["name"], item["kind"], tuple(item["files"]),
                     str(item.get("stage", "")))


def _reason_code(outcome: Any) -> Any:
    """Extract a rejection reason from either a `validate()` report (a dict,
    checked by key) or an exception raised during `parse()` (checked by
    attribute, since parse failures are implementation-defined exceptions,
    not report dicts)."""
    if isinstance(outcome, dict):
        return outcome.get("reason")
    return getattr(outcome, "reason", None)


def _closed_reason_codes() -> frozenset[str]:
    return frozenset(entry["code"] for entry in vocabulary("reject-reasons")["codes"])


def _check_transport_run(implementation: LoomgroundImplementation, program: Any,
                          transport: dict, expected: dict, log: list,
                          where: str) -> None:
    """`log` is required on every transport run (schema/transport.schema.json:
    `required: [activations, expected, log]`, on both a top-level transport.json
    and each permutations entry) -- a vector missing it is itself malformed, not
    a vector that opts out of the ordered-log check."""
    for act in transport.get("activations", []):
        if act.get("invalid") and implementation.validate_token(act["token"]):
            raise AssertionError(f"{where}: mislabelled vector: invalid=true but token validates")
    if implementation.evaluate(program, transport) != expected:
        raise AssertionError(f"{where}: transport evaluation mismatch")
    if implementation.evaluate_log(program, transport) != log:
        raise AssertionError(f"{where}: ordered log mismatch")


def _check_determinism(implementation: LoomgroundImplementation, vector: Vector) -> None:
    """SPEC §7.5 / conformance/README.md, Determinism vectors: no expected.json —
    only the dynamic result (`transport.json`'s `expected` and logs) is pinned.
    `repeat` reruns of input.lg MUST reproduce identical verdicts/decisions and the
    same log (rule 1); each declaration-order `permutations` entry MUST reproduce the
    same verdicts/decisions (rule 2) against its own ordered log (rule 3)."""
    source = vector.text("input.lg")
    program = implementation.parse(source)
    report = implementation.validate(program)
    if not report.get("ok"):
        raise AssertionError(f"unexpected apply rejection: {report.get('errors', [])}")
    transport = vector.json("transport.json")
    expected = transport.get("expected", {})
    log = transport["log"]
    for i in range(transport.get("repeat", 1)):
        _check_transport_run(implementation, program, transport, expected, log,
                              where=f"determinism repeat {i + 1}")
    for perm in transport.get("permutations", []):
        perm_source = artifact_path("conformance", "vectors", vector.name, perm["file"]).read_text(
            encoding="utf-8")
        perm_program = implementation.parse(perm_source)
        perm_report = implementation.validate(perm_program)
        if not perm_report.get("ok"):
            raise AssertionError(f"determinism permutation {perm['file']}: unexpectedly rejected")
        _check_transport_run(implementation, perm_program, transport, expected, perm["log"],
                              where=f"determinism permutation {perm['file']}")


def _check(implementation: LoomgroundImplementation, vector: Vector) -> None:
    if vector.kind == "token":
        for case in vector.json("tokens.json"):
            if implementation.validate_token(case["token"]) != case["valid"]:
                raise AssertionError("token classification mismatch")
        return

    if vector.kind == "determinism":
        _check_determinism(implementation, vector)
        return

    source = vector.text("input.lg")
    if vector.kind == "negative":
        reject = vector.json("reject.json")
        stage, reason = reject["stage"], reject.get("reason")
        codes = _closed_reason_codes()
        if reason is not None and reason not in codes:
            raise AssertionError(f"vector names a reason {reason!r} outside the closed set")
        try:
            program = implementation.parse(source)
        except Exception as exc:
            # An apply-stage vector's input MUST survive parsing; any exception
            # raised while parsing fails it regardless of what it reports as its
            # own stage — a stub that raises on every input must not pass here.
            if stage != "parse":
                raise AssertionError(f"rejected at parse instead of {stage}") from None
            got = _reason_code(exc)
            if got != reason:
                raise AssertionError(f"parse reason {got!r} != expected {reason!r}") from None
            return
        if stage == "parse":
            raise AssertionError("expected parse rejection; input parsed")
        report = implementation.validate(program)
        if report.get("ok", True):
            raise AssertionError(f"expected {stage} rejection")
        got = _reason_code(report)
        if got != reason:
            raise AssertionError(f"apply reason {got!r} != expected {reason!r}")
        return

    program = implementation.parse(source)
    report = implementation.validate(program)
    if not report.get("ok"):
        raise AssertionError(f"unexpected apply rejection: {report.get('errors', [])}")
    expected = vector.json("expected.json")
    observed = implementation.project(program)
    if observed != expected:
        raise AssertionError("canonical observation mismatch")
    if "transport.json" in vector.files:
        transport = vector.json("transport.json")
        _check_transport_run(implementation, program, transport, transport.get("expected", {}),
                              transport["log"], where="transport")


def run_conformance(implementation: LoomgroundImplementation) -> ConformanceReport:
    """Run every published vector against an implementation object or module."""
    vectors = tuple(iter_vectors())
    failures = []
    for vector in vectors:
        try:
            _check(implementation, vector)
        except Exception as exc:
            failures.append({"name": vector.name, "kind": vector.kind,
                             "error": f"{type(exc).__name__}: {exc}"})
    return ConformanceReport(len(vectors), len(vectors) - len(failures), tuple(failures))
