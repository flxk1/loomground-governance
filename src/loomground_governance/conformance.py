# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""Implementation-neutral access to and execution of conformance vectors."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Iterable

from .artifacts import artifact_path, conformance_manifest
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


def _check(implementation: LoomgroundImplementation, vector: Vector) -> None:
    if vector.kind == "token":
        for case in vector.json("tokens.json"):
            if implementation.validate_token(case["token"]) != case["valid"]:
                raise AssertionError("token classification mismatch")
        return

    source = vector.text("input.lg")
    if vector.kind == "negative":
        try:
            program = implementation.parse(source)
        except Exception:
            if vector.stage == "parse":
                return
            raise AssertionError("rejected at parse instead of apply")
        report = implementation.validate(program)
        if vector.stage != "apply" or report.get("ok", True):
            raise AssertionError(f"expected {vector.stage} rejection")
        return

    program = implementation.parse(source)
    report = implementation.validate(program)
    if not report.get("ok"):
        raise AssertionError(f"unexpected apply rejection: {report.get('errors', [])}")
    if implementation.project(program) != vector.json("expected.json"):
        raise AssertionError("canonical observation mismatch")
    if "transport.json" in vector.files:
        transport = vector.json("transport.json")
        if implementation.evaluate(program, transport) != transport.get("expected", {}):
            raise AssertionError("transport evaluation mismatch")
        if "log" in transport and implementation.evaluate_log(program, transport) != transport["log"]:
            raise AssertionError("ordered log mismatch")


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
