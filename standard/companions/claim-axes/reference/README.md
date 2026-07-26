<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# claim-axes reference adapter

An independent implementation of the claim-axes companion contract
(`../COMPANION.md`), proving the contract is implementable by a third party
from the published artifacts alone: `../claim-axes.schema.json`,
`../profile-inert-0.1.0.json`, and `../vectors/`.

It imports only the Python standard library plus `jsonschema` -- nothing
from any product that ships or consumes this companion. That isolation is
itself checked, not just asserted: `tools/check_reference_isolation.py`
AST-parses every file here and fails the build if one of them ever imports
`versum`, `loomground_solver`, or `loomground_governance`.

## Files

- `reference_adapter.py` -- `validate(record)` (consumer) and
  `build_record(axes)` (producer).
- `conformance.py` -- runs every vector in `../vectors/` (per
  `../vectors/manifest.json`) through `validate()` and asserts valid vectors
  are accepted and invalid vectors are rejected.

## Running the conformance check

```sh
python3 -m pip install jsonschema
python3 standard/companions/claim-axes/reference/conformance.py
```

Exits non-zero, with a per-vector message, on any mismatch. CI runs this on
every push and pull request, alongside the isolation check.
