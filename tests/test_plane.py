# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""The governance plane descriptor (shared plane descriptor contract v1)."""
import ast
import copy
import importlib.metadata
import json
from pathlib import Path

import pytest

from loomground_governance import (
    dimension_binding, iter_vectors, language_version, load_json, vocabulary,
)
from loomground_governance.plane import (
    FIVE_DIMENSIONS, PROJECTABLE_FIELDS, RESERVED_GATE, RESERVED_KIND, binding,
    examples, nd_system, observations, plane, produce,
)

PACKAGE = Path(__file__).resolve().parents[1] / "src" / "loomground_governance"
S3 = "The controller must not make a solely automated decision on a credit application."


def test_entry_point_governance_is_registered_and_loads_the_descriptor():
    eps = [ep for ep in importlib.metadata.entry_points(group="loomground.planes")
           if ep.name == "governance"]
    assert len(eps) == 1, "reinstall with pip install --no-deps -e ."
    assert eps[0].value == "loomground_governance.plane:plane"
    descriptor = eps[0].load()()
    assert descriptor["plane"] == "governance"
    for key in ("language_version", "nd_system", "binding", "produce", "examples"):
        assert key in descriptor
    assert callable(descriptor["produce"])


def test_versions_come_from_the_kit_and_agree():
    descriptor = plane()
    assert descriptor["language_version"] == language_version()
    assert descriptor["nd_system"]["version"] == descriptor["language_version"]
    assert descriptor["nd_system"]["validation"]["unknown_values"] == "reject"
    # the plane omits every 5D version key; the consumer supplies its default
    assert not [k for k in descriptor["nd_system"] if "5d" in k.lower()]


def test_nd_system_is_derived_from_the_kit_artifacts():
    system = nd_system()
    axes = system["axes"]
    assert axes["node_class"]["vocabulary"] == [
        n["class"] for n in load_json("vocabulary", "node-classes.json")]
    assert axes["cord_type"]["vocabulary"] == [
        c["type"] for c in vocabulary("cords")["permitted"]]
    assert axes["risk"]["vocabulary"] == vocabulary("risk")["levels"]
    assert axes["grade"]["vocabulary"] == vocabulary("grades")["levels"]
    assert axes["verdict"]["vocabulary"] == vocabulary("verdicts")["alphabet"]
    assert axes["on_elapse"]["vocabulary"] == ["halt", "proceed"]
    pairs = {(r["axis"], r["left"], r["right"]) for r in system["ontology_relations"]}
    assert ("risk", "low", "critical") in pairs and ("grade", "L0", "L6") in pairs


def test_binding_is_the_one_data_file_and_names_only_the_five_dimensions():
    document = dimension_binding()
    data_files = sorted(p.name for p in (PACKAGE / "data").iterdir()
                        if p.suffix == ".json")
    assert data_files == ["dimension-binding.json"]
    assert document == json.loads((PACKAGE / "data" / "dimension-binding.json").read_text())
    assert binding() == {r: s["dimension"] for r, s in document["relations"].items()}
    assert plane()["binding"] == binding()
    assert set(binding()) == {"authority", "pipe", "egress", "on_behalf_of",
                              "reservation", "redress"}
    assert set(binding().values()) <= set(FIVE_DIMENSIONS)
    assert document["id"] == "loomground-governance-5d"


def test_binding_rejects_a_sixth_dimension(monkeypatch):
    import loomground_governance.plane as module
    bad = copy.deepcopy(dimension_binding())
    bad["relations"]["pipe"]["dimension"] = "contextual"
    monkeypatch.setattr(module, "dimension_binding", lambda: bad)
    with pytest.raises(ValueError, match="five dimensions"):
        module.binding()


def test_produce_binds_s3_to_the_reserved_decide_gate():
    claims = produce(S3)
    assert len(claims) == 1
    claim = claims[0]
    assert claim["relation"] == "reservation"
    assert claim["span"] == [0, len(S3)]
    assert claim["gate"] == "decide"
    assert claim["coordinates"] == {"node_class": "gate", "token_kind": "automated_decision",
                                    "verdict": "reserved"}
    assert claim["slots"] == {"predicate.agent": "node_class",
                              "predicate.patient": "token_kind"}
    assert claim["relation"] in binding()
    axes = nd_system()["axes"]
    assert claim["coordinates"]["verdict"] in axes["verdict"]["vocabulary"]
    assert claim["coordinates"]["node_class"] in axes["node_class"]["vocabulary"]


@pytest.mark.parametrize("sentence", [
    "The bank is a controller.",
    "The scoring model is part of the credit system.",
    "The controller may use the score to prepare a decision.",
    "A reviewer shall examine every rejection before it is sent.",
    "The review follows the automated scoring.",
    "The controller may make a solely automated decision.",   # no negated modal
    "The controller must not disclose the score.",              # no automated decision
    "",
])
def test_produce_is_empty_for_non_matching_sentences(sentence):
    assert produce(sentence) == []


def test_produce_is_pure_and_deterministic():
    context = {"source": {"jurisdiction": "EU"}}
    frozen = copy.deepcopy(context)
    assert produce(S3, context) == produce(S3) == produce(S3, None)
    assert context == frozen
    with pytest.raises(TypeError):
        produce(None)


def test_producer_cue_is_the_published_draft_decide_vector():
    vector = next(v for v in iter_vectors() if v.name == "draft-decide")
    observation = vector.json("expected.json")
    gates = {n["id"] for n in observation["nodes"] if n["class"] == "gate"}
    assert RESERVED_GATE in gates
    assert RESERVED_KIND in {r["kind"] for r in observation["reservations"]}


def test_examples_are_the_producers_own_output():
    published = examples()
    assert published and all(e["expected"] == produce(e["sentence"]) for e in published)
    assert any(e["expected"] for e in published) and any(not e["expected"] for e in published)
    json.dumps(published)


def test_observations_are_the_projectable_patch_vectors():
    published = {o["name"]: o["observation"] for o in observations()}
    patch = [v for v in iter_vectors() if v.kind == "patch"]
    for vector in patch:
        observation = vector.json("expected.json")
        if set(observation) <= PROJECTABLE_FIELDS:
            assert published[vector.name] == observation
        else:
            assert vector.name not in published
    assert "handoff" not in published          # carries transfers: not projectable
    assert "redress-decl" in published and "draft-decide" in published


def test_plane_package_never_imports_versum():
    for path in PACKAGE.rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(), filename=str(path))):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            assert not [n for n in names if n.split(".")[0] == "versum"], path


def test_descriptor_is_json_serialisable_apart_from_produce():
    descriptor = plane()
    json.dumps({k: v for k, v in descriptor.items() if k != "produce"})
