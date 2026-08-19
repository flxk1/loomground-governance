# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""Role canonicalization quality gate — the formalized output of the ingest-side
canonicalization loop (raw GDPR/AI-Act bearers -> canonical governance roles)."""
from __future__ import annotations

from loomground_governance import canonical_roles, canonicalize_role


def _role(bearer):
    r = canonicalize_role(bearer)
    return r["role"] if r else None


CASES = [
    ("the controller", "controller"),
    ("controllers or processors", "controller"),      # first-match, plural
    ("supervisory authority which is competent pursuant to Article 55", "supervisory authority"),
    ("lead supervisory authority", "supervisory authority"),
    ("Member States", "member state"),
    ("the data subject", "data subject"),
    ("the European Data Protection Board", "board"),
    ("certification bodies", "certification body"),
    ("the data protection officer", "data protection officer"),
    ("a provider of a high-risk AI system", "provider"),
    # genuine non-actors stay unattributed, never forced:
    ("those implementing acts", None),
    ("proceedings", None),
    ("it", None),
]


def test_role_canonicalization():
    for bearer, expected in CASES:
        assert _role(bearer) == expected, (bearer, _role(bearer), expected)


def test_every_role_carries_a_node_kind():
    for entry in canonical_roles():
        assert entry["kind"] in ("agent", "human"), entry
        assert entry["role"] and entry["aliases"]
