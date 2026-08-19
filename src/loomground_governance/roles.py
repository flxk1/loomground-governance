# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""Role canonicalization — the language owns the contract, policy owns the roles.

Maps a raw bearer span ("the controller", "supervisory authority which is
competent…", "controllers or processors") to a canonical governance role and its
node kind (agent / human), per the remappable ``vocabulary/roles.json``. First
match in listed order wins; a bearer matching no alias is *unattributed* and is
returned as ``None`` — never forced into a role. Standard library only.
"""
from __future__ import annotations

import re
from typing import Any, Optional

from .artifacts import vocabulary

_ROLES: Optional[list[dict[str, Any]]] = None
_COMPILED: Optional[list[tuple[Any, dict[str, str]]]] = None


def _load() -> list[tuple[Any, dict[str, str]]]:
    global _ROLES, _COMPILED
    if _COMPILED is None:
        _ROLES = vocabulary("roles")["roles"]
        _COMPILED = [
            (re.compile(alias, re.I), {"role": e["role"], "kind": e["kind"]})
            for e in _ROLES for alias in e["aliases"]
        ]
    return _COMPILED


def canonical_roles() -> list[dict[str, Any]]:
    """The published role vocabulary (role + kind + aliases), in match order."""
    _load()
    return list(_ROLES or [])


def canonicalize_role(bearer: str) -> Optional[dict[str, str]]:
    """Return ``{"role", "kind"}`` for a raw bearer, or ``None`` if unattributed."""
    text = bearer or ""
    for pattern, out in _load():
        if pattern.search(text):
            return dict(out)
    return None
