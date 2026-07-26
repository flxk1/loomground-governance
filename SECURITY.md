<!-- SPDX-License-Identifier: Apache-2.0 -->
<!-- Copyright 2026 flxk1 -->
# Security policy

## Supported versions

Loomground is currently pre-1.0. Security fixes are made on the latest release line
only.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability. Use GitHub's private
vulnerability reporting for this repository. Include the affected version or commit,
reproduction steps, impact, and any suggested mitigation. Please allow the maintainer
time to investigate before public disclosure.

This repository ships a language specification, schemas, and a data-only Python kit —
it contains no parser, evaluator, or network service of its own. A vulnerability report
against this repository is most likely to concern the packaged conformance vectors, the
build and release pipeline, or the companion validation skill in `skills/loomground/`;
please say which of these is affected.
