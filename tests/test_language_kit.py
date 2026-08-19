# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
from loomground_governance import (
    LoomgroundImplementation, conformance_manifest, grammar, iter_vectors,
    language_status, language_version, schema, vocabulary,
)


def test_authoritative_artifacts_are_available_from_the_package():
    assert language_version() == "0.10.0"  # x-release-please-version
    assert language_status() == "stable"
    assert "program" in grammar()
    assert vocabulary("verdicts")["restrictiveness_order"][0] == "auto"
    assert schema("token")["type"] == "object"


def test_manifest_and_vector_loader_stay_in_lockstep():
    manifest = conformance_manifest()
    assert manifest["version"] == language_version()
    vectors = tuple(iter_vectors())
    assert len(vectors) == len(manifest["vectors"])
    assert {v.name for v in vectors} == {v["name"] for v in manifest["vectors"]}


def test_protocol_is_structural_and_runtime_neutral():
    class Runtime:
        parse = validate = project = validate_token = evaluate = evaluate_log = lambda *a: None

    assert isinstance(Runtime(), LoomgroundImplementation)
