<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# Releasing

This document is self-contained: read it without needing any other file to understand
how a release of this repository happens.

## Three independent version axes

This repository carries three version numbers that look similar but answer different
questions, and none of them should be collapsed into another:

1. **Package/release** — `pyproject.toml`, `standard/language-card.json`, and
   `standard/conformance/manifest.json` share one number (currently `0.8.2`). This is
   the version PyPI installs and the version this document's release flow manages.
   `tools/check_language_summary.py` gates that the three stay equal, and that
   `standard/grammar/tree-sitter/tree-sitter.json`'s own `metadata.version` matches too.
2. **Contract/protocol** — the claim-axes version, the profile version, and the
   `loomground.language/*` media-type version named in the specification. These are
   frozen independently of the package release and change only when the governed
   contract itself changes, never as a side effect of a package release.
3. **Plugin/distribution** — `package.json` and `.claude-plugin/plugin.json` (currently
   `0.1.0`). This is the companion-skill bundle's own version; it is bumped by hand when
   the bundled skill changes and never needs to equal the package version above.
   `tools/check_companion.py` gates that these two manifests agree with *each other*,
   never that either equals the package version.

A release bumps axis 1. It must never bump axis 2, and it bumps axis 3 only if the
companion skill itself changed.

## Release flow (Release Please)

[Release Please](https://github.com/googleapis/release-please) turns conventional
commits on `main` into a reviewed release pull request:

- `fix:` increments the patch version.
- `feat:` increments the minor version.
- `feat!:` or a `BREAKING CHANGE:` footer increments the major version.
- `docs:`, `test:`, `ci:`, and `chore:` do not by themselves trigger a release.

Merging the generated release pull request updates `pyproject.toml` and
`CHANGELOG.md`, and creates a plain tag of the form `vX.Y.Z` (for example, the
existing `v0.8.2` tag) — no component prefix, because this repository publishes a
single package. Configuration lives in `release-please-config.json` and
`.release-please-manifest.json`; the workflow is
`.github/workflows/release-please.yml`.

Humans approve the version by approving the release pull request; automation only
performs the bookkeeping (computing the version, updating the changelog, creating the
tag).

## Publishing (PyPI Trusted Publishing)

Once the release pull request merges and the tag is created, the `publish` job in
`.github/workflows/release-please.yml` builds the source distribution and wheel once
and publishes them using
[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) — an OIDC
exchange (`id-token: write`) instead of a long-lived API token stored in the
repository. Publication runs only inside the protected `pypi` GitHub environment and
must pass the governance lane before anything reaches PyPI.

## Ecosystem release order (reference only — not required by this repository alone)

This language is consumed by sibling implementations. When a change here needs to
reach them, the usual order is:

1. Merge the change to this repository's `main`.
2. Merge the generated release pull request here and publish the new
   `loomground-governance` version.
3. Sibling implementation repositories pick up the new version through their own
   Dependabot pull requests, gated by their own conformance suites.
4. Those repositories cut their own releases once the dependency update passes.

This repository's own release does not wait on that downstream propagation; it is
listed here so a reader understands what a release here sets in motion.

## Local verification before tagging

```
python3 -m pytest
python3 tools/check_language_summary.py
python3 tools/check_lockstep.py
python3 tools/check_vectors.py
python3 tools/check_companion.py
reuse lint
```

All of the above run in CI (`.github/workflows/ci.yml`) on every push and pull
request; a release pull request must pass them before it merges.
