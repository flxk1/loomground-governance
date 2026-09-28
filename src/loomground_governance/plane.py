# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""The governance plane descriptor (shared plane descriptor contract v1).

Registered under the entry-point group ``loomground.planes`` as ``governance``.
``plane()`` takes no arguments and returns plain data plus one pure function; this
module never imports a consumer of the descriptor.

Everything is derived from the kit's own artifacts at call time:

* ``language_version``: ``language-card.json``;
* ``nd_system``: the node classes, cord types, risk and grade ladders, verdict alphabet
  and on-elapse resolutions published by the kit (vocabularies and grammar);
* ``binding``: the one relation -> 5D data file ``data/dimension-binding.json``;
* ``examples``: the producer's worked sentences;
* ``observations``: the published patch conformance vectors whose canonical
  observation is projectable (only ``nodes``, ``cords``, ``reservations``, ``redress``).
"""
from __future__ import annotations

import json
import re
from importlib.resources import files
from typing import Any

from .artifacts import grammar, language_version, load_json, vocabulary
from .conformance import iter_vectors

PLANE_ID = "governance"
SYSTEM_ID = "loomground-governance"
NAMESPACE = "loomground"
BINDING_FILE = "dimension-binding.json"
FIVE_DIMENSIONS = ("structural", "causal", "intentional", "temporal", "relational")
#: Top-level observation fields a governance observation projection carries.
PROJECTABLE_FIELDS = frozenset({"nodes", "cords", "reservations", "redress"})

# Producer cues. The reserved decision is the one the kit's own draft-decide vector
# publishes: a ``decide`` gate whose ``automated_decision`` kind is reserved to a human
# role (GDPR Art. 22(3), grounded on the ``reservation`` declaration).
RESERVED_GATE = "decide"
RESERVED_KIND = "automated_decision"
RESERVED_VERDICT = "reserved"
_NEGATED_MODAL = re.compile(
    r"\b(?:must|shall|may|should)\s+(?:not|never)\b|\bmustn[’']t\b|\bshan[’']t\b"
    r"|\bcannot\b|\bcan\s*not\b|\bis\s+not\s+(?:permitted|allowed)\s+to\b",
    re.IGNORECASE)
_SOLELY_AUTOMATED_DECISION = re.compile(
    r"\bsolely\s+automated\s+decisions?\b"
    r"|\bdecisions?\s+based\s+solely\s+on\s+automated\s+processing\b",
    re.IGNORECASE)


def dimension_binding() -> dict:
    """The governance relation -> 5D binding document (the one data file)."""
    raw = files("loomground_governance").joinpath("data", BINDING_FILE)
    return json.loads(raw.read_text(encoding="utf-8"))


def binding() -> dict[str, str]:
    """``{relation: dimension}`` from the data file; fails closed on a non-5D value."""
    out: dict[str, str] = {}
    for relation, spec in dimension_binding()["relations"].items():
        dimension = spec["dimension"]
        if dimension not in FIVE_DIMENSIONS:
            raise ValueError(f"relation {relation!r} binds {dimension!r}, "
                             f"not one of the five dimensions")
        out[str(relation)] = str(dimension)
    return out


def _ordered(axis: str, values: list[str]) -> list[dict]:
    """Transitive ``precedes`` pairs of a ladder (nD relations are attestation-based)."""
    return [{"axis": axis, "left": left, "right": right, "relation": "precedes"}
            for index, left in enumerate(values) for right in values[index + 1:]]


def _on_elapse() -> list[str]:
    match = re.search(r"^on-elapse\s*=\s*(.+?);", grammar(), re.MULTILINE)
    if match is None:
        raise ValueError("grammar declares no on-elapse production")
    return re.findall(r'"([^"]+)"', match.group(1))


def nd_system() -> dict:
    """The governance nD-system document, versioned with the language."""
    node_classes = [str(item["class"]) for item in load_json("vocabulary", "node-classes.json")]
    cord_types = list(dict.fromkeys(
        str(item["type"]) for item in vocabulary("cords")["permitted"]))
    risk = list(vocabulary("risk")["levels"])
    grades = list(vocabulary("grades")["levels"])
    return {
        "id": SYSTEM_ID,
        "namespace": NAMESPACE,
        "version": language_version(),
        "axes": {
            "node_class": {"value_type": "controlled_identifier", "cardinality": "one",
                           "vocabulary": node_classes},
            "cord_type": {"value_type": "controlled_identifier", "cardinality": "one",
                          "vocabulary": cord_types},
            "risk": {"value_type": "controlled_identifier", "cardinality": "one",
                     "vocabulary": risk, "primitives": ["equal", "precedes"]},
            "grade": {"value_type": "controlled_identifier", "cardinality": "one",
                      "vocabulary": grades, "primitives": ["equal", "precedes"]},
            "party": {"value_type": "entity_reference", "cardinality": "one",
                      "vocabulary_mode": "open", "primitives": ["equal"]},
            "token_kind": {"value_type": "concept_reference", "vocabulary_mode": "open",
                           "primitives": ["equal", "contains"]},
            "tags": {"value_type": "concept_reference", "cardinality": "many",
                     "vocabulary_mode": "open", "primitives": ["equal", "contains"]},
            "verdict": {"value_type": "controlled_identifier", "cardinality": "one",
                        "vocabulary": list(vocabulary("verdicts")["alphabet"])},
            "reservation_role": {"value_type": "entity_reference", "cardinality": "many",
                                 "vocabulary_mode": "open"},
            "duration": {"value_type": "interval", "cardinality": "one",
                         "vocabulary_mode": "open", "primitives": ["equal", "precedes"]},
            "on_elapse": {"value_type": "controlled_identifier", "cardinality": "one",
                          "vocabulary": _on_elapse()},
            "redress_role": {"value_type": "entity_reference", "cardinality": "many",
                             "vocabulary_mode": "open"},
        },
        "bindings": [
            {"form_slot": "predicate.agent", "allowed_axes": ["party", "node_class"]},
            {"form_slot": "predicate.patient", "allowed_axes": ["party", "token_kind"]},
            {"form_slot": "modality.bearer", "allowed_axes": ["party", "reservation_role",
                                                                "redress_role"]},
            {"form_slot": "condition.antecedent", "allowed_axes": ["risk", "grade",
                                                                     "token_kind", "tags"]},
        ],
        "ontology_relations": [*_ordered("risk", risk), *_ordered("grade", grades)],
        "validation": {"unknown_values": "reject", "missing_coordinates": "preserve_unknown",
                       "provenance_required": True},
    }


def produce(sentence: str, context: dict | None = None) -> list[dict]:
    """Governance observation bindings for one sentence (pure, deterministic).

    A sentence that forbids a solely automated decision is a reservation of the
    ``automated_decision`` kind at the ``decide`` gate: the gate's verdict is
    ``reserved`` and the decision is referred to a human role. Any other sentence
    yields ``[]``. ``context`` is accepted for the contract and not read.
    """
    if not isinstance(sentence, str):
        raise TypeError("sentence must be a string")
    if not (_NEGATED_MODAL.search(sentence) and _SOLELY_AUTOMATED_DECISION.search(sentence)):
        return []
    return [{
        "relation": "reservation",
        "span": [0, len(sentence)],
        "gate": RESERVED_GATE,
        "coordinates": {"node_class": "gate", "token_kind": RESERVED_KIND,
                        "verdict": RESERVED_VERDICT},
        "slots": {"predicate.agent": "node_class", "predicate.patient": "token_kind"},
        "links": [],
        "method": f"{SYSTEM_ID}.plane.produce@{language_version()}",
    }]


EXAMPLE_SENTENCES = (
    "The controller must not make a solely automated decision on a credit application.",
    "The bank is a controller.",
    "The controller may use the score to prepare a decision.",
)


def examples() -> list[dict]:
    """The producer's published worked sentences with their expected claims."""
    return [{"sentence": s, "expected": produce(s)} for s in EXAMPLE_SENTENCES]


def observations() -> list[dict]:
    """Published patch conformance vectors whose observation is projectable as a whole."""
    out = []
    for vector in iter_vectors():
        if vector.kind != "patch" or "expected.json" not in vector.files:
            continue
        observation = vector.json("expected.json")
        if set(observation) <= PROJECTABLE_FIELDS:
            out.append({"name": vector.name, "observation": observation})
    return out


def plane() -> dict[str, Any]:
    """The shared plane descriptor (contract v1) for the governance plane."""
    version = language_version()
    return {
        "plane": PLANE_ID,
        "language_version": version,
        "nd_system": nd_system(),
        "binding": binding(),
        "produce": produce,
        "examples": examples(),
        "observations": observations(),
    }
