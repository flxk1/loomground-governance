# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""Structural sanity of the claim-axes companion (standard/companions/claim-axes).

The vocabulary itself is proven by the two independent implementations that
vendor these vectors (COMPANION.md, Conformance); this test keeps the canonical
copy well-formed: the manifest indexes exactly the vector files that exist,
every vector is a valid/invalid-flagged record, and the profile document only
declares choices for recognized axes.
"""
import json
from pathlib import Path

COMPANION = Path(__file__).resolve().parents[1] / "standard" / "companions" / "claim-axes"
AXES = ("predicate", "modality", "polarity", "quantification", "domain")


def test_manifest_indexes_exactly_the_vector_files():
    manifest = json.loads((COMPANION / "vectors" / "manifest.json").read_text())
    assert manifest["kind"] == "wire-record"
    listed = set(manifest["vectors"])
    on_disk = {p.name for p in (COMPANION / "vectors").glob("*.json")} - {"manifest.json"}
    assert listed == on_disk
    assert len(listed) == len(manifest["vectors"])  # no duplicates


def test_every_vector_is_a_flagged_record():
    manifest = json.loads((COMPANION / "vectors" / "manifest.json").read_text())
    seen = set()
    for name in manifest["vectors"]:
        vector = json.loads((COMPANION / "vectors" / name).read_text())
        assert vector["name"] + ".json" == name
        assert isinstance(vector["valid"], bool)
        assert isinstance(vector["record"], dict)
        assert vector["description"]
        seen.add(vector["valid"])
    assert seen == {True, False}  # both accept and reject sides are covered


def test_profile_declares_only_recognized_axes_with_closed_sets():
    profile = json.loads((COMPANION / "profile-inert-0.1.0.json").read_text())
    assert profile["schema"] == "loomground.versum.claim-axes/v1"
    assert set(profile["choices"]) == set(AXES)
    for axis, allowed in profile["choices"].items():
        assert isinstance(allowed, list) and allowed, axis


def test_schema_recognizes_the_same_axes():
    schema = json.loads((COMPANION / "claim-axes.schema.json").read_text())
    assert set(schema["properties"]["axes"]["properties"]) == set(AXES)
    assert schema["properties"]["axes"]["additionalProperties"] is False
    assert schema["additionalProperties"] is False
    assert schema["required"] == ["schema", "axes"]
