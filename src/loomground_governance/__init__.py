# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""Data-only access to the authoritative Loomground language artifacts."""

from .artifacts import (
    artifact_path, conformance_manifest, grammar, language_card,
    language_status, language_version, load_json, schema, vocabulary,
)
from .conformance import ConformanceReport, Vector, iter_vectors, run_conformance
from .protocol import LoomgroundImplementation
from .roles import canonical_roles, canonicalize_role

__all__ = [
    "ConformanceReport", "LoomgroundImplementation", "Vector", "artifact_path",
    "conformance_manifest", "grammar", "iter_vectors", "language_card",
    "language_status", "language_version", "load_json", "run_conformance",
    "schema", "vocabulary", "canonical_roles", "canonicalize_role",
]
