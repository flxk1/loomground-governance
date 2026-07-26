# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""Neutral protocol implemented by any Loomground runtime."""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class LoomgroundImplementation(Protocol):
    """Operations required by the language conformance runner."""

    def parse(self, source: str) -> Any: ...

    def validate(self, program: Any) -> dict: ...

    def project(self, program: Any) -> dict: ...

    def validate_token(self, token: Any) -> bool: ...

    def evaluate(self, program: Any, transport: dict) -> dict: ...

    def evaluate_log(self, program: Any, transport: dict) -> list[dict]: ...
