# Tasks: The Domain Crosses The Seam (Cut 2)

> **Size note.** Over the 530-word budget, deliberately, for the same reason
> `design.md` gave: sixteen dotted leaves (fifteen field-landed one-at-a-time per D1/D7,
> plus `vocabulary.names` declared at S13 with the locks it serves), each needing its own
> RED case, its own landing step, its own seal run and its own two-way mutation proof — a
> compressed list is a list apply has to re-expand, and re-expansion is exactly the risk
> D7 exists to remove. Citations verified by symbol name against HEAD `ff566fa` before
> writing (`CITATION_RE`, `finding_impact`, `cmd_handoff`, `cmd_admit`, `cmd_verify`,
> `proposals_root`, `unreached_mathematics`, `_wiring_first_publication`,
> `ARMS_UNDECLARED_CONSEQUENCE`, `authored_package_init`, `remedy_compatibility`,
> `_REQUIRED_NESTED`, `_AUTHORIZATION_BINDING_KEYS`, `reachable_refusal_codes`, the six kit
> files, `tests/seal/*`, `tests/test_implementation_profile.py`,
> `tests/proposal-deliberation-domain-profile-lock.test.mjs`, `impl_profile.py`).

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1,050 (±150), per proposal Size Forecast |
| 400-line budget risk | High against the 400 default; **Low against this session's 1,400 line budget** (max ~1,200) |
| Chained PRs recommended | No — fits under the cached 1,400-line budget as one PR |
| Suggested split | Single PR. Contingency only: if S13 overruns, fall back to design D7's separable slice — PR 1 = S0–S9 + D4/D6 locks, PR 2 = S10–S13 (Lock B cannot land before S12's comment sweep) |
| Delivery strategy | single-pr |
| Chain strategy | pending (not activated — see contingency) |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: pending
400-line budget risk: Low

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | S0–S14 in full sequence, one field per commit, seal green after each | PR 1 (single) | `.venv/bin/python -m unittest tests.seal.harness -v` after every S-step | `.venv/bin/python -m unittest discover -s tests` + `npm test`, both pasted before/after | Each S-step reverts independently (D7); whole change is one revert, `tests/seal/` untouched by construction |
| 1a (contingency) | S0–S9 + D4/D6 locks only | PR 1 of 2, if split triggers | same seal command, scoped to S0–S9 | same | Revert PR 1 alone; PR 2 not yet opened |
| 1b (contingency) | S10–S13, Lock B | PR 2 of 2, if split triggers, based on PR 1 | same seal command, scoped to S10–S13 | same | Revert PR 2 alone; PR 1 stands |

---

## Phase 0 — Baseline (S0)

- [x] 0.1 `.venv/bin/python -m unittest discover -s tests`: `Ran 2849 tests in 435.174s` / `OK (skipped=6)`.
- [x] 0.2 `npm test`: `595/595` (`tests 595, pass 595, fail 0`).
- [x] 0.3 Seal run: `sha256(tests/seal/digests.json)` = `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75`; `git diff --exit-code tests/seal/` exits 0.
- [x] 0.4 L1 baseline measured fresh (not §A): **97 occurrences, 1 file** (`implementation_engine.py`) for `\bproposal\b` case-insensitive across `_core/implementation/engine/`.
- [x] 0.5 Re-derived from a fresh Lock B-shaped scan (7-word `names` list): 72 total occurrences / 63 lines across the file; the 40/25/4/10-line role breakdown was superseded during apply by the ACTUAL Lock B failure report driving Phases 11-12 directly (measured, not pre-classified) — see apply report.

## Phase 1 — RED first: one `..._INCOMPLETE` case per leaf (S1)

- [x] 1.1 `DomainFieldLeafRefusalTests`/`DocumentsDirectoryOwnTierTests` added to `tests/test_implementation_profile.py`, one case per dotted leaf, all sixteen.
- [x] 1.2 Confirmed RED (17 failures: 16 leaves + 1 threat-matrix case) before any resolver/profile change.

## Phase 2 — Resolver + profile declaration, engine untouched (S2)

- [x] 2.1 `impl_domain_profile.py` grew `_REQUIRED_PRESENCE` (14 non-path leaves) — kept separate from `_REQUIRED_NESTED` rather than merged into it, since that tuple is ALSO walked by the exists()-check.
- [x] 2.2 `documents.directory` given its own `_REQUIRED_ABSOLUTE_ONLY` tier (M3): required, absolute, existence not required.
- [x] 2.3 Threat-matrix RED test added (`DocumentsDirectoryOwnTierTests`); confirmed relative refuses `UNSAFE_PATH`, non-existent absolute imports fine.
- [x] 2.4 All fifteen field-landed leaves declared in `impl_profile.py` with today's exact literal values. Engine untouched.
- [x] 2.5 Confirmed: 15 GREEN, `vocabulary.names` stays RED until S13.
- [x] 2.6 Seal run: 28/28 byte-identical (no-op confirmed).

## Phase 3 — `provenance.claim_key` (S3)

- [x] 3.1 `CLAIM_KEY` constant hoisted beside `SKILL_ROOT`/`CLI_PATH`; wired into all 4 read/write sites that actually exist (`unreached_modules` [renamed at S11], `benchmark_unfaithfulness`, `wiring_proposal`, `cmd_verify`'s module row). `authored_package_init` is S4's site (D3), not S3's — D1's P5 row names the WRITER, not a `claim_key` reader.
- [x] 3.2 `assets/kit/src/module.py` untouched.
- [x] 3.3 Seal run: 28/28 byte-identical.

## Phase 4 — `provenance.authored_init_sentence` + `vocabulary.artifact_noun` (S4, D3)

- [x] 4.1 `authored_package_init` rewritten to interpolate `AUTHORED_INIT_SENTENCE` + `ARTIFACT_NOUN`; byte-identical to the original hardcoded sentence.
- [x] 4.2 Bounded to the one sentence, not the file — `__all__ = []` line stays a literal.
- [x] 4.3 Seal run: 28/28 byte-identical. (Measured at S14: `materialize`'s STDOUT does not carry the written file's content, so this leaf is a genuine ZERO-MOVER against the seal — recorded, not papered over.)

## Phase 5 — `findings.locus_key` (S5)

- [x] 5.1 `LOCUS_KEY` wired into `remedy_compatibility`'s loop, `cmd_admit`'s verdict loop, `cmd_handoff`'s item builder, `cmd_verify`'s audit block.
- [x] 5.2 Seal run: 28/28 byte-identical.

## Phase 6 — `findings.remedy_locus_key` (S6)

- [x] 6.1 `REMEDY_LOCUS_KEY` wired into `finding_impact`, `remedy_compatibility`, `cmd_admit`, `cmd_handoff` (incl. `selectedEntryId`).
- [x] 6.2 Seal run: 28/28 byte-identical.

## Phase 7 — `findings.notation_keys` (S7)

- [x] 7.1 `NOTATION_KEYS` wired into `finding_impact`'s return, `cmd_handoff`'s item builder, `remedy_compatibility`'s two returns, `cmd_verify`'s audit block.
- [x] 7.2 Seal run: 28/28 byte-identical.

## Phase 8 — `findings.citation_pattern` (S8, M1 — the eleventh field)

- [x] 8.1 `CITATION_RE = re.compile(CITATION_PATTERN)`, sourced from `PROFILE["findings"]["citation_pattern"]`. `DISPLAY_BLOCK_RE`/`TAG_RE` untouched.
- [x] 8.2 Seal run: 28/28 byte-identical. (Measured at S14: ZERO-MOVER against these fixtures — `handoff-e1`'s citation count is unaffected by this particular pattern substitution given the fixture's own tag layout; recorded honestly.)

## Phase 9 — `documents.directory` + `documents.label` (S9, M3)

- [x] 9.1 `proposals_root()` reads `DOCUMENTS_DIRECTORY`; `ARMS_UNDECLARED_CONSEQUENCE` reads `DOCUMENTS_LABEL`. `revision_source`/`revision_discovery` inherit via `proposals_root()`.
- [x] 9.2 `DocumentsDirectoryEnvironmentOverrideTests` added: real subprocess, confirms `IMPLEMENTATION_PROPOSALS` still wins.
- [x] 9.3 Seal run: 28/28 byte-identical.

## Phase 10 — `vocabulary.*` subject leaves, one sub-step per leaf (S10)

- [x] 10.1 `SUBJECT_SINGULAR` → `ARMS_UNDECLARED_CONSEQUENCE`. Seal 28/28.
- [x] 10.2 `SUBJECT_PLURAL` → `cmd_admit`'s verdict reason. Seal 28/28.
- [x] 10.3 `SUBJECT_SINGULAR_ES` → `cmd_handoff`'s `remedy-locus-missing` and `structural-reach` reasons. Seal 28/28.
- [x] 10.4 `SUBJECT_PLURAL_ES` → `cmd_handoff`'s `structural-reach` reason and the (profile-cased) `A TOCAR:` prompt line. Seal 28/28.
- [x] 10.5 `SUBJECT_COLLECTIVE` → `_wiring_first_publication`. Seal 28/28.
- [x] 10.6 `SUBJECT_COLLECTIVE_ES` → `cmd_handoff`'s `remedy-text-missing` reason. Seal 28/28.
- [x] 10.7 M2 doctrine-tension comment recorded unresolved at the `else:` branch above the Spanish reasons. Not translated, not fixed.
- [x] 10.8 Confirmed independently revertible per sub-step (distinct constants, distinct call sites).

## Phase 11 — Identifier renames, driven by Lock B's failure report (S11)

- [x] 11.1 Lock A/B written first (pulled ahead from Phase 13, as instructed); the ACTUAL failure report named **3** domain-spelling identifiers, not the predicted 4: `unreached_mathematics` → `unreached_modules`, plus two local-variable siblings `equations` → `remedy_loci` (in `finding_impact`) and `unknown_equations` → `unknown_loci` (in `remedy_compatibility`). Recorded as a measured finding: the design's "4" assumed Lock B's word-boundary regex would also flag `unreached_mathematics` itself, but `_` blocks `\b` inside compound identifiers — only its prose neighbors originally triggered. Renamed all 3 found; no 4th exists.
- [x] 11.2 Confirmed: `unreachedModules`/`armsReached` wire keys unchanged; no digest moved from the rename (seal 28/28 before and after).
- [x] 11.3 Updated all call sites, including two docstring mentions in `tests/test_proposal_implementation.py`.
- [x] 11.4 Seal run: 28/28 byte-identical.

## Phase 12 — The comment/docstring sweep (S12)

- [x] 12.1 Swept every remaining comment/docstring occurrence of a declared `names` word (34 lines), using Lock B's own live report as the worklist. Discovered and swept 3 additional `cmd_compose` sites (docstring + 2 refusal messages + 1 wire key) that D1's site table had not enumerated — Lock B's absolute "anywhere in engine/" requirement forced them into scope; resolved by reusing the already-declared `SUBJECT_SINGULAR` field (no new field, `compose`/M1's architecture stays untouched and open).
- [x] 12.2 Asserted by seal run (28/28 unchanged) that no executable text's behavior moved.
- [x] 12.3 Seal run: 28/28 byte-identical.

## Phase 13 — The locks (S13)

- [x] 13.1 `vocabulary.names` declared in `impl_profile.py`, the exact 7-word measured list.
- [x] 13.2 `tests/test_implementation_domain_lock.py` created; Lock A (`discover_profiles()`, glob-based) implemented and green.
- [x] 13.3 Lock B implemented; green (zero declared-names-word occurrences remain in `engine/`).
- [x] 13.4 Kit agreement lock: all 6 assertions implemented with non-empty extraction guards, green. No kit file edited.
- [x] 13.5 D6 three layers implemented: L1 = 96 occurrences / 1 file (97 S0 baseline minus 1 deliberate, recorded shrink from `documents.label`'s `ARMS_UNDECLARED_CONSEQUENCE` conversion); L2 all 11 symbols resolve; L3 `proposalDigest` still in `_AUTHORIZATION_BINDING_KEYS`.
- [x] 13.6 `wiring_proposal`/`_wiring_first_publication` third-sense residue recorded and tested (`test_wiring_proposal_third_sense_residue_is_covered_by_l1_not_l2`).
- [x] 13.7 `reachable_refusal_codes()` re-asserted at 112 — unchanged (`tests.test_proposal_implementation.GatingRefusalRosterTests`, confirmed green).
- [x] 13.8 M5 deferral recorded as a comment in `test_implementation_domain_lock.py`; no `skipTest` written; `skipped=6` never moved (final: still 6).
- [x] 13.9 `tests/proposal-deliberation-domain-profile-lock.test.mjs` not touched (read only, for structure).
- [x] 13.10 Seal run: 28/28 byte-identical.

## Phase 14 — Mutation proof, both directions, per leaf (S14/D8)

- [x] 14.1 Removal proof for all sixteen leaves already proven by Phase 1's `DomainFieldLeafRefusalTests` (now all green — each leaf's absence raises `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming itself).
- [x] 14.2 Change proof: `tests/test_implementation_domain_mutation.py`'s `PerLeafChangeMutationTests`, one subtest per leaf, real scratch-profile + real `IMPLEMENTATION_DOMAIN_PROFILE` env override + real subprocess seal run over all 28 cases. Measured (not assumed) mover sets recorded in `MEASURED_MOVERS`; 7 of 14 came back as genuine zero-movers against these fixtures (see apply report for the full predicted-vs-measured table).
- [x] 14.3 Anchor discipline implemented and asserted per leaf (old=1/new=0 on the real file before; old=0/new=1 on the scratch copy after). The real `impl_profile.py` is never edited, so there is no "revert" step — a stronger guarantee than edit-then-revert.
- [x] 14.4 Every zero-mover recorded explicitly in `MEASURED_MOVERS` with a code comment naming it; none papered over.
- [x] 14.5 Lock B honesty test added and green (plant reddens a scratch copy naming the file; revert restores green).
- [x] 14.6 Kit lock honesty test added and green (scratch `module.py` mutation reddens the agreement; shipped file confirmed byte-identical after).
- [x] 14.7 `git diff --exit-code tests/seal/` confirmed exit 0 (also asserted in-suite by `SealCorpusUntouchedTests`).

## Phase 15 — Non-interference & close-out

- [x] 15.1 Final `.venv/bin/python -m unittest discover -s tests`: `Ran 2874 tests in 461.456s` / `OK (skipped=6)`. `Ran` grew by 25 (new test methods); `skipped=6` did not move.
- [x] 15.2 Final `npm test`: `595/595` exactly (`tests 595, pass 595, fail 0`).
- [x] 15.3 Confirmed via `git diff --stat 9e89d90 HEAD -- .claude/skills/proposal-deliberation/ .claude/skills/_core/deliberation/`: empty — neither directory touched.
- [x] 15.4 Final seal check: `sha256(tests/seal/digests.json)` = `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75`, identical to Phase 0.3; `git diff --exit-code tests/seal/` exits 0.
- [x] 15.5 All five Products rows confirmed true by inspection: every profile leaf's literal value equals today's hardcoded bytes (no target-visible shape change); `__benchmark__["arms"]` key untouched (`"sections"` stays hardcoded); `__init__.py`'s authored sentence composes byte-identical; no `_AUTHORIZATION_BINDING_KEYS` member renamed (L3); `cmd_admit`'s verdict prose still recomposes from the same literals.
- [x] 15.6 Committed per-phase (`0ec54e2`, `c6667ff`, `3b2f3c4`, `efdf7d9`, plus this docs commit), conventional messages, no AI attribution, single PR (not yet opened/pushed).
