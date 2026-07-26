# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 flxk1
"""Independent reference adapter for the claim-axes companion contract.

This is a neutral third-party implementation: it derives everything it does
from the published artifacts beside it (claim-axes.schema.json,
profile-inert-0.1.0.json, vectors/) and imports nothing from any product that
ships or consumes the contract. A genuine third party integrating this
companion has only those published files to work from, so this adapter is
held to the same limit — see tools/check_reference_isolation.py, which fails
the build if that ever stops being true.

Two directions, matching COMPANION.md sec 2-4:

  consumer  validate(record)     -- accept or reject a wire record, with a reason
  producer  build_record(axes)   -- construct a wire-conformant record from axes

`validate()` always checks the wire schema (claim-axes.schema.json). By
default it additionally checks the shipped inert-0.1.0 profile's closed
per-axis value sets (profile-inert-0.1.0.json) -- pass `profile=None` to
check the wire schema alone. The shared conformance vectors in vectors/ are
themselves schema-level ("wire-record") vectors, not scoped to any one
profile version (several valid vectors use axis values the inert profile
does not allow), so conformance.py validates them with `profile=None` -- see
its docstring. The profile round trip is exercised directly below and by the
self-check at the bottom of this file.
"""
from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

HERE = Path(__file__).resolve().parent
COMPANION_ROOT = HERE.parent  # standard/companions/claim-axes

SCHEMA_PATH = COMPANION_ROOT / "claim-axes.schema.json"
INERT_PROFILE_PATH = COMPANION_ROOT / "profile-inert-0.1.0.json"

WIRE_SCHEMA_ID = "loomground.versum.claim-axes/v1"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text())


_SCHEMA = _load_json(SCHEMA_PATH)
_VALIDATOR = Draft202012Validator(_SCHEMA)
INERT_PROFILE = _load_json(INERT_PROFILE_PATH)


def validate(record: dict, *, profile: dict | None = INERT_PROFILE) -> tuple[bool, str | None]:
    """Validate a claim-axes wire record. Returns (accepted, reason).

    `reason` is None when accepted, and a short human-readable explanation
    of the first violation found when rejected.

    Always enforces claim-axes.schema.json: exactly the members `schema`
    (the frozen wire identifier) and `axes` (an object of at most the five
    recognized axes, each value a string of 1-256 non-whitespace-containing
    characters). When `profile` is given (the shipped inert-0.1.0 profile by
    default), additionally enforces that profile's closed per-axis value
    sets. Pass `profile=None` for wire-schema-only conformance.
    """
    if not isinstance(record, dict):
        return False, "record is not a JSON object"

    errors = sorted(_VALIDATOR.iter_errors(record), key=lambda e: list(e.absolute_path))
    if errors:
        first = errors[0]
        loc = "/".join(str(p) for p in first.absolute_path) or "<root>"
        return False, f"schema: {loc}: {first.message}"

    if profile is not None:
        ok, reason = _check_profile(record, profile)
        if not ok:
            return False, reason

    return True, None


def _check_profile(record: dict, profile: dict) -> tuple[bool, str | None]:
    """Enforce a semantic profile's closed per-axis value sets (COMPANION.md sec 3).

    Assumes `record` has already passed wire-schema validation, so `axes`
    is known to be present and to be an object of recognized-axis strings.
    """
    if record.get("schema") != profile.get("schema"):
        return False, (
            f"profile: record schema {record.get('schema')!r} does not match "
            f"profile schema {profile.get('schema')!r}"
        )
    choices = profile.get("choices", {})
    for axis, value in record.get("axes", {}).items():
        allowed = choices.get(axis)
        if allowed is None:
            return False, f"profile: axis {axis!r} has no declared choice set"
        if value not in allowed:
            return False, (
                f"profile: axis {axis!r} value {value!r} is not in the closed "
                f"set {allowed!r}"
            )
    return True, None


def build_record(axes: dict) -> dict:
    """Construct a wire-conformant claim-axes record from an axes mapping.

    Stamps the frozen wire identifier and carries `axes` through unchanged.
    build_record(axes) round-trips through validate() as accepted whenever
    `axes` is itself conformant (recognized axis keys; non-blank string
    values of at most 256 characters) under whatever `profile` the caller
    validates against -- including the default inert-0.1.0 profile, when
    `axes` uses only that profile's closed values.
    """
    return {"schema": WIRE_SCHEMA_ID, "axes": dict(axes)}


if __name__ == "__main__":
    # Self-check: the producer/consumer round trip this module exists to prove,
    # run directly (not via conformance.py, which exercises the shared vectors).
    inert_axes = {axis: choices[0] for axis, choices in INERT_PROFILE["choices"].items()}
    inert_record = build_record(inert_axes)
    accepted, reason = validate(inert_record)
    assert accepted, f"inert-profile round trip rejected: {reason}"
    print(f"round trip (schema + inert-0.1.0 profile): accepted -- {inert_record}")

    off_profile_record = build_record({"predicate": "causes"})
    wire_ok, _ = validate(off_profile_record, profile=None)
    assert wire_ok, "wire-schema-only validation should accept a schema-conformant record"
    profile_ok, profile_reason = validate(off_profile_record)
    assert not profile_ok, "a value outside the inert profile's closed set must be rejected"
    print(f"wire-schema-only: accepted; inert-profile-checked: rejected -- {profile_reason}")
