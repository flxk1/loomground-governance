<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# Status and versioning

Moved verbatim from the README (sections "Status", "Versioning").

## Status

Pre-1.0, specification v0.11.0 (stable).
This repository carries only the language:
specification, grammar, schemas, vocabulary, and conformance vectors. Reference
implementations are out of scope. An implementation conforms by reproducing the
vectors in `standard/conformance/`.

This is a single-author specification engineered to standards discipline so
that it *could* become a standard; it is not one, and no institutional status
is claimed. §9's interoperability criterion — two implementations produced
independently of each other reproducing every vector — accordingly remains
**open**: the two existing implementations were authored within this same
AI-assisted project, so they provide differential conformance checking, not
an independence proof (see `standard/conformance/README.md`, Status).

## Versioning

The language card, conformance manifest, and Python package share one PEP 440
version. Maturity is a separate machine-readable `status`; draft builds use
alpha releases rather than mutable `.dev` versions. Before 1.0, a minor version
may change compatibility and a patch version is backward-compatible. Dependent
tools may now declare `loomground-governance>=0.11,<0.12` (each pre-1.0 minor is its own compatibility band, so pin to the current minor).

The three version axes (package/release, contract/protocol, plugin/distribution)
and the release flow: `RELEASING.md`.
