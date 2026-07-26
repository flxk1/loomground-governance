# SPDX-License-Identifier: Apache-2.0
# Copyright 2026 flxk1
"""Load packaged language artifacts without interpreting their semantics."""
from __future__ import annotations

import json
from importlib.resources import files
from pathlib import Path
from typing import Any


def artifact_path(*parts: str):
    """Return a traversable path inside the packaged authoritative artifact tree."""
    packaged = files("loomground_governance").joinpath("artifacts")
    path = packaged if packaged.is_dir() else Path(__file__).resolve().parents[2] / "standard"
    for part in parts:
        path = path.joinpath(part)
    return path


def load_json(*parts: str) -> Any:
    return json.loads(artifact_path(*parts).read_text(encoding="utf-8"))


def language_card() -> dict:
    return load_json("language-card.json")


def language_version() -> str:
    return str(language_card()["version"])


def language_status() -> str:
    return str(language_card()["status"])


def grammar(name: str = "loomground.ebnf") -> str:
    return artifact_path("grammar", name).read_text(encoding="utf-8")


def vocabulary(name: str) -> dict:
    return load_json("vocabulary", f"{name}.json")


def schema(name: str) -> dict:
    return load_json("schema", f"{name}.schema.json")


def conformance_manifest() -> dict:
    return load_json("conformance", "manifest.json")
