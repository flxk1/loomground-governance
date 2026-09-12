<!-- SPDX-License-Identifier: CC-BY-4.0 -->
<!-- Copyright 2026 flxk1 -->
# Loomground `.lg` reference card

Rendered from `standard/vocabulary/*.json` and `standard/spec/SYNTAX.md` (loomground v0.11.0).


**Nodes**
| keyword | meaning | attributes |
|---|---|---|
| `actor <id>` | a principal that may be granted authority and propose an action | `grade L0…L4` (granted) |
| `human <id>` | a person named by a role; reserved tokens are referred to it; never a cord endpoint | `role <id>` · `name <text>` |
| `gate <id>` | a governed checkpoint where an actor acts and a verdict is produced | `risk <low\|medium\|high\|critical>` (floor) · `grade <L0…L4>` (required, source gate only) · `party <id>` · `grant <actor>` |
| `master` | the single sink; where the policy enforcement point attaches | none |

**Cords** `cord <from> -> <to>` — permitted pairs only: actor → gate (authority), gate → gate (pipe), gate → master (egress). A human is never an endpoint; an actor never reaches the master directly.

**Declarations**
| form | effect |
|---|---|
| `reserve <kind> by <target> [when <guard>] [duration <n>(m\|h\|d):(halt\|proceed)]` | verdict `reserved`; the action is referred to a human role; on elapse halt or proceed |
| `prohibit <kind> [when <guard>]` | verdict `prohibited`; never released, overrides any grant |
| `redress <kind> by <role> [overturn] [within <duration>]` | records the right to re-examination |
| target = `role` · `role and role` · `<m> of { roles }` | quorum: distinct parties (separation of duty) |

**Guards** range over declared token fields only: `kind`, `risk`, `party`, `tags contains <tag>`; operators on risk `< <= = >= >`. Never over `id`, `provenance`, `grade`, or anything computed.

**Token** (what activates a gate; supplied by the host at runtime): `id`, `kind`, `risk`, `party`, `provenance[]`, `tags[]`.

**Verdicts**: `auto < human < refused < reserved < prohibited` (join = the most restrictive); the master releases or withholds accordingly.

**Values owned by policy, not the language**: the risk scale meanings, the grade ladder meanings, the set of kinds and tags, the roles.

**Grammar** (SYNTAX.md §3, ISO/IEC 14977): ~25 rules; the card links it and shows the six statement forms above; `parse` = any conforming implementation, including `loomground-ref`.
