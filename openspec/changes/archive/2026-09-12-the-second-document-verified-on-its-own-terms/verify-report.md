```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:c490348706f9da6affca19bfe13685977a4fb80c3ca0da1b55c2723c558faf4f
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 10/10
scenarios: 23/23
test_command: .venv/bin/python -m unittest discover -s tests -p "test_*.py" -v
test_exit_code: 0
test_output_hash: sha256:40075532da38306a1e96092b75ca931992d9fc36afc588b873e6c3009230dfde
build_command: npm test
build_exit_code: 0
build_output_hash: sha256:27a9f3eaaaf1d1a14c77ae324f12562839da65baa20a4facb5c412236d5ce098
```

## Verification Report

**Change**: `the-second-document-verified-on-its-own-terms` (Slice C)
**HEAD verified**: `ba996bc2ac47f3563ff1ab531d711ad1d8281ec8` (worktree clean before and after)
**Mode**: Strict TDD, hybrid persistence (OpenSpec is source of truth)
**Commits**: `0eeecbe..ba996bc` (10 commits: C1 RED/GREEN, C2a RED/GREEN, C2b RED/GREEN, C3 RED/GREEN, a fix commit, a docs commit)

All measurements below were re-executed by this verify session against a
clean worktree at HEAD. No foreign `unittest discover` process was found
running against this worktree before measurement (only this session's own
`ps`/monitor commands matched the grep).

### Completeness (tasks.md)
| Metric | Value |
|--------|-------|
| Tasks total | 44 (`1.1`–`4.9`, independently counted; **not** 45 as the launch brief stated — apply's own correction confirmed) |
| Tasks complete | 44 (`[x]`, zero unchecked) |
| Tasks incomplete | 0 |

### Build & Tests Execution — RE-RUN this session, not inherited

**npm test**: ✅ 595 passed / 0 failed / 0 skipped (41.7s)
```text
ℹ tests 595
ℹ suites 0
ℹ pass 595
ℹ fail 0
ℹ cancelled 0
ℹ skipped 0
```

**Python full suite**: ✅ 2977 passed / 0 failed / 6 skipped (499.7s, backgrounded, `.venv/bin/python`)
```text
Ran 2977 tests in 499.675s

OK (skipped=6)
```
Grown from the pre-change baseline of 2956 by exactly **+21** — the number of
new tests this change added across its four phases. `skipped=6` unmoved (no
`skipTest` added anywhere — confirmed via `git diff` on every touched test
file, zero `+.*skipTest` lines).

**Digest/pin re-derivation (measured this session, not inherited)**:
| Pin | Claimed | Measured | Match |
|---|---|---|---|
| `sha256(tests/seal/digests.json)` | `011300df…` | `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75` | ✅ exact, unchanged after the full mutation-laden suite run too |
| `L1_EXPECTED_COUNT` (`\bproposal\b` over `_core/implementation/engine/`, word-boundary, case-insensitive) | 96 | 96 (independently re-derived via a standalone script, one file: `implementation_engine.py`) | ✅ exact |
| `L1_EXPECTED_FILES` | 1 file | 1 file (`implementation_engine.py`) | ✅ exact |
| `reachable_refusal_codes()` | 114 | 114 (`test_the_derivation_finds_the_measured_one_hundred_and_thirteen` — a pre-existing, stale test *name* from a prior slice; its body asserts `== 114` and passed) | ✅ exact |
| M1's 26 distinct lines / 32 symbol-line hits, decomposed 5 def + 21 reader | 26 / 32 / 5+21 | Independently re-derived via a standalone AST-free script (word-boundary match, excluding comment/docstring-prose lines): **26 distinct lines, 32 symbol-line hits, 5 definitions + 21 readers** | ✅ exact, matched on first derivation |
| `git diff --exit-code` on `proposal-implementation/`, `proposal-deliberation/`, `experimental-deliberation/`, `_core/deliberation/` | clean | exit 0 | ✅ confirmed |
| `tests/experiments_seal/digests.json` movement | 6 of 20 cases moved in C3 only | Confirmed via `git diff e1f853d~1 e1f853d`: `__corpus_fingerprint__` + `handoff-e1`/`offer-e1`/`position-e1`/`probe`/`verify-a`/`verify-b` — exactly 6 case entries, all other 14 unchanged | ✅ exact |

### The account of "6 of 20 moved" — verified by reading the diff, not inherited

The claim that `handoff-e1`/`offer-e1`/`position-e1` moved from a **spurious
refusal** back to success, "matching pre-slice-A behaviour," could not be
confirmed from the committed `digests.json` diff alone (both before and
after this commit, their `"exit"` field already reads `0` — the transient
refusal state lived only in apply's own working session, never committed).
It **is** confirmed by reading commit `e1f853d`'s own message and its
`tests/experiments_seal/corpus.py`/`harness.py` diff: the pre-existing
corpus's findings carried no `document` field (an existing gate,
`require_document`, that had never had a chance to fire against this
skill's own corpus before `documents[1]` existed) and document 1 had no
discoverable revision (`proposals/` holds only `.gitkeep`). Both are
genuine, structural consequences of declaring a second document against an
unready fixture — not a defect papered over by editing away a real
refusal. `verify-a`/`verify-b`/`probe` growing in byte size is explained by
the same commit adding `fidelityByDocument` content to the captured output.
**Confirmed: the account is accurate.**

### Spend-your-effort-here items — all four independently verified by execution

**1. Does the fold recompute per document, or filter a shared list?**
**Answer: it genuinely recomputes per document.** Read
`cmd_verify`'s `conditions_by_index` build in
`implementation_engine.py` (~L15195-15228): `stale_n` is computed by
comparing each module's own `revision` against `document_names[index]`
(that document's own independently-discovered name), not by filtering the
whole-tree `stale` list. The code's own comment names the exact bug this
avoids: filtering the shared list "would reproduce Y5's exact described
defect, since the shared `stale` list is always computed against the bare
top-level `revision`." `TwoDocumentReadProvenTests.test_a_reverted_fold_is
_caught_even_with_two_documents_declared` (in
`tests/test_implementation_domain_lock.py`) mutates the **real, shipped**
engine file on disk (`doc_revision_n = document_names[index]` →
`doc_revision_n = revision`), runs the real shipped launcher, confirms
document 1 wrongly reports `drift`, then restores and re-asserts
byte-identity — this is a live, repeatable mutation proof, not merely
static reading. Ran green this session as part of the full suite.

**2. Was the pre-C red structural, not asserted?**
**Confirmed by checking out `0eeecbe~1` in a scratch `git worktree
add --detach` (removed after).** At that commit,
`_extra_document_fidelity_status` received the SAME `stale`,
`missing_provenance`, `untested`, `unreached` variables for every index ≥
1 (`_extra_document_fidelity_status(document_names[index], index, stale,
missing_provenance, untested, unreached, …)`), and document 0's own
`fidelity_status` used the literal-identical boolean expression (`stale or
missing_provenance or untested or unreached`). Since both document 0's and
document 1's drift/ok classification reduce to the same shared boolean
whenever both revisions resolve, the pre-C engine could not have reported
different statuses for the two — the red was inexpressible, not an
authored-to-fail assertion. Matches design D6 and Prediction 7 exactly.

**3. Do three conditions split and two stay shared, and is the C-shared
guard real?** Confirmed by code (`conditions_by_index`: `staleModules`,
`invariantsWithoutTest`, `unreachedModules` all computed per-index against
`scope_paths`/`document_names[index]`; `missingProvenance` is the
unchanged whole-tree list, repeated at every index) and by execution:
`TwoDocumentDriftControlTests.test_c_shared_missing_provenance_reports_on
_both` asserts `doc0["status"] == doc1["status"] == "drift"` for an
unreadable-provenance module — passed. Y6's mutation record
(`test_y6_scoping_missing_provenance_reddens_only_c_shared`, in
`tests/test_implementation_pair.py`) independently proves the guard: it
fakes a per-document split of `missing_provenance` and confirms only
`test_c_shared…` goes red — ran green this session.

**4. Does `citation_pattern` group-count validation cover the top-level
pattern, not only overlays?** Confirmed by code
(`impl_domain_profile.py`'s `citation_pattern_leaves` list always
seeds `findings.citation_pattern` before appending any overlay) and by
`CitationPatternGroupCountTests` (`tests/test_implementation_profile.py`):
four cases — 2-group and 4-group, each declared once at
`findings.citation_pattern` (top-level) and once at
`documents[1].citation_pattern` (overlay) — all four refuse by name with
`IMPLEMENTATION_DOMAIN_PROFILE_INVALID_CITATION_PATTERN`, plus a fifth
case (`test_a_three_group_pattern_passes`) proving the accepting boundary.
All ran green.

### Also confirmed

- **All ten design predictions held**, spot-checked by direct execution/
  measurement (not all ten individually re-run, but every one that could
  be independently re-derived was): the five scalars byte-identical after
  D2's re-derivation (`DocumentVocabularyZeroDeltaTests`, green);
  `tests/seal/digests.json` byte-identical (measured, sha256 match);
  `tests/pair/digests.json` unmoved (2 cases, both run `name` not
  `verify`, confirmed by reading `tests/pair/cases.json`); `L1` = 96 / one
  file (re-derived); `reachable_refusal_codes()` = 114 (re-derived);
  `skipped=6` unmoved, no `skipTest` added; C-fwd and C-inv both
  structurally red pre-C (confirmed via scratch worktree, item 2 above);
  C-shared green pre- and post-C2a (confirmed); **the engine threads 21
  reader lines, not 26** — independently re-derived from source this
  session (26 distinct lines = 5 definitions + 21 readers, 32 symbol-line
  hits — exact match on first derivation, methodology: word-boundary
  match over the five symbols, excluding comment/docstring-prose lines);
  `tests/experiments_seal/` digests moved only in C3 (confirmed via `git
  log --follow` and the `e1f853d` diff).

- **`tasks.md` carries 44 tasks, not 45** — independently counted
  (`1.1`–`4.9`, no gaps), matching apply's own correction.

- **Two real findings closed during apply, both judged sound:**
  1. The self-authored fold bug (filtering the shared `stale` list instead
     of recomputing per document) was caught by writing the C-inv test
     *before* the fix shipped (commits `0ce5158`/`730f6ba`) — confirmed by
     reading the commit sequence and the final code's comment describing
     exactly this near-miss.
  2. Two pre-existing test files
     (`tests/test_experimental_implementation_mutation.py`,
     `tests/test_proposal_implementation.py::ExtraDocumentFidelityStatusTests`)
     were broken by this change's own signature/regex changes and fixed
     in commit `87af4b2`. Read the diff: both are genuine, narrow
     adaptations to an already-shipped signature/behavior change (the
     mutation test's citation pattern gained back its third capturing
     group; the fidelity-status test call site was updated from a
     7-argument to a 4-argument signature, still covering all four
     condition keys) — not new behavior, not a weakened assertion.

- **Zero new skips**: confirmed, `skipped=6` unmoved, and no `skipTest`
  literal added in the diff.

- **Spec conformance, re-counted, not inherited**: 4 spec files, **10
  Requirements / 23 Scenarios** total (5+4+7+7 scenarios;
  2+2+2+4 requirements) — see Spec Compliance Matrix below.

### Spec Compliance Matrix

| Spec | Requirement | Scenario(s) | Covering test(s) | Result |
|---|---|---|---|---|
| implementation-per-document-vocabulary | Overlays, Never Replaces | 2 | `DocumentVocabularyOverlayTests` | ✅ COMPLIANT |
| implementation-per-document-vocabulary | Pre-Existing Silence Is Not An Error | 1 | `DocumentVocabularyOverlayTests.test_declaring_none…`, `DocumentVocabularyZeroDeltaTests` | ✅ COMPLIANT |
| implementation-per-document-vocabulary | `citation_pattern` Group Count | 3 | `CitationPatternGroupCountTests` (4 refusal cases + 1 passing case, top-level and overlay) | ✅ COMPLIANT |
| implementation-per-document-vocabulary | No Vocabulary Inferred From Another's | 1 | `DocumentVocabularyIndependenceTests`, `DocumentVocabularyOverlayTests.test_document_one_missing_override…` | ✅ COMPLIANT |
| implementation-document-binding | Fold Runs Per Document (MODIFIED) | 4 | `TwoDocumentDriftControlTests` (C-fwd/C-inv/C-shared) + `tests/seal/` byte-identity for the single-document scenario | ✅ COMPLIANT |
| implementation-document-binding | Finding Names Either/Both Documents (MODIFIED) | 3 | `PerDocumentCitationImpactClassTests` | ✅ COMPLIANT |
| implementation-cli-seal | Sealed By A Drift-Control Fixture (ADDED) | 3 | `TwoDocumentDriftControlTests` (functional proof of the drift behavior, real subprocesses) + `git diff --exit-code tests/seal/` (28 untouched) — see W1 for a spec-wording note | ✅ COMPLIANT (W1) |
| implementation-cli-seal | Second Document's Vocabulary Exercised, Not Only Directory/Label (ADDED) | 1 | `tests/experiments_seal`'s `both-documents-citation` finding, captured and digested (confirmed in the `e1f853d` diff) | ✅ COMPLIANT |
| experimental-implementation-skill | Two Documents Reproduce Doc 0's Guarantee (MODIFIED) | 3 | `impl_profile.py` (documents[1] declared), `discover_profiles()`-based `LockADiscoveryTests`/`LockBEngineNeutralityTests` | ✅ COMPLIANT |
| experimental-implementation-skill | Proven By Reading, Not By Counting (ADDED) | 2 | `TwoDocumentReadProvenTests` (both methods) | ✅ COMPLIANT |

**Compliance summary**: 23/23 scenarios compliant, 10/10 requirements compliant (see W1 for a non-blocking spec-wording note on one requirement).

### Correctness (Static + Runtime Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| All-or-nothing per-entry overlay (D1) | ✅ Implemented | `_resolve()`'s `_DOCUMENT_VOCABULARY_LEAVES` walk, confirmed by reading and by `DocumentVocabularyOverlayTests` |
| `notation_keys` shape validation (D3 tier 2) | ✅ Implemented | `NotationKeysShapeOverlayTests`, 3 subTests |
| `citation_pattern` group count, top-level AND overlay (D3 tier 3) | ✅ Implemented | Confirmed by reading `_resolve()`; the top-level pattern is always the first entry in `citation_pattern_leaves` |
| Per-document fidelity fold (D4/D5) | ✅ Implemented | Confirmed by reading `cmd_verify`'s `conditions_by_index` and by `TwoDocumentDriftControlTests` |
| Per-document citation matching (D7) | ✅ Implemented | Confirmed by reading `finding_impact`/`_impact_class`/`document_citation_re` and by `PerDocumentCitationImpactClassTests` |
| No new engine prose spells `proposal` (D9) | ✅ Held | `L1_EXPECTED_COUNT` re-derived at 96, one file |
| Ordering: declaration last (D8) | ✅ Held | `documents[1]` landed in the final commit `e1f853d`, after C2a/C2b; `Y8`'s ordering proof (task 4.1) ran |

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 (all-or-nothing overlay) | ✅ Yes | |
| D2 (five scalars re-derived at index 0) | ✅ Yes | Zero-delta, asserted |
| D3 (resolver tier, group count both levels) | ✅ Yes | |
| D4 (claim-key scope, 3 split / 2 shared) | ✅ Yes | |
| D5 (`conditions` block, additive) | ✅ Yes | |
| D6 (structural red, 3 separate methods) | ✅ Yes | Confirmed via scratch-worktree checkout |
| D7 (per-document `CITATION_RE`, compiled once) | ✅ Yes | |
| D8 (declaration last, C2 splits) | ✅ Yes | |
| D9 (no `proposal` in engine prose) | ✅ Yes | |
| Reconciliation appendix (overlay vs all-or-nothing, two granularities) | ✅ Yes | Both levels independently confirmed in `_resolve()` |

## Issues Found

**CRITICAL**: None.

**WARNING**:
- **W1 — `implementation-cli-seal`'s "Sealed By A Drift-Control Fixture" requirement is not literally satisfied.** Its scenarios say "the two-document seal captures it" and "both digested" for the C-fwd/C-inv arrangements. No seal/digest artifact (no JSON file with a captured sha256) exists for these two fixtures anywhere in the repository — confirmed by inspecting `tests/pair/digests.json` (unmoved, 2 unrelated cases) and `tests/seal/digests.json` (unmoved, 28 unrelated cases). The underlying functional guarantee IS proven, and arguably more rigorously — `TwoDocumentDriftControlTests`'s three real-subprocess methods in `tests/test_implementation_pair.py`, explicitly classified by design.md's own Testing Strategy table as "Integration," never planned as a seal/digest capture. This looks like spec prose that over-specified a delivery mechanism (digest capture) that design.md and tasks.md never intended to build and did not build. Not a functional defect. **Recommend**: either (a) amend this spec requirement's wording to describe assertion-based proof, matching what shipped, or (b) if literal digest-capture matters for this fixture family, add it in a follow-up change.
- **W2 — `proposal.md`'s own Success Criteria checklist was never edited during apply; all nine items remain `[ ]`, including "The slice table records A → C → {B, D}".** Confirmed via `git log` — `proposal.md` has not been touched since its creation commit (`587399e`); `ba996bc` (apply's final commit) touches only `tasks.md`. This specific criterion's *substance* IS satisfied: the corrected ordering is stated prominently and repeatedly in this exact proposal's own prose ("**The real order is A → C → {B, D}. Record it in the slice table.**"), consistent with the proposal's own Q5 ruling ("record it here; A is archived, editing an archived proposal is its own decision"). But no literal "slice table" (a data structure with A/B/C/D rows) was ever corrected anywhere — the archived Slice A proposal's own table (`openspec/changes/archive/2026-09-12-the-second-skill-the-seam-was-for/proposal.md`, lines 136-142) still lists rows in the original `A, B, C, D` order, unedited, exactly per Q5's decision not to touch it. This is the **second time** an ordering inversion has needed recording in this project (per this proposal's own account of the first). Apply correctly treated this as out-of-scope for a code phase (no task in tasks.md references it). **Recommend**: either tick this checklist item now (the substance is satisfied in this document) or create one canonical, actively-maintained slice-ordering record, since prose-only correction has already needed repeating once.

**SUGGESTION**:
- Total authored diff across the 10 commits is ~1,782 lines (1,680 insertions + 218 deletions, minus the 28-line generated digest and the 88-line `tasks.md` bookkeeping), against a 1,400-line review budget — correctly handled via the planned 4-way stacked chain (C1→C2a→C2b→C3), each individually reviewable. No action needed; noted for delivery-strategy continuity.

## Final Verdict: **PASS WITH WARNINGS**

Zero CRITICAL issues. Two WARNINGs, both non-blocking:

- **W1** is a spec-wording/mechanism mismatch, not a functional gap — the
  exact property the spec cares about (`fidelityByDocument`'s fold
  reflecting only its own document's conditions, proven both directions)
  is proven by real-subprocess, structurally-red-before-C tests, just not
  through a seal/digest artifact the spec's prose implies.
- **W2** is a documentation-bookkeeping gap in an already-frozen planning
  artifact (`proposal.md`), whose substance is already recorded in this
  same document's own prose, per an explicit prior design ruling not to
  touch archived material.

Every "spend your effort here" item was independently verified by
execution — including a real mutation of the shipped engine file
(`TwoDocumentReadProvenTests`) and a scratch `git worktree` checkout of the
pre-C commit to confirm the structural (not authored) nature of the red.
Both pinned invariants (`npm test` 595/595, Python `Ran 2977, OK
(skipped=6)`) held exactly, matching apply's own report byte-for-byte.
`tests/seal/`'s 28-digest baseline is byte-identical before, during (after
every mutation test's own restore), and after this session's full suite
run. `git diff --exit-code` on all four excluded sibling directories
(`proposal-implementation/`, `proposal-deliberation/`,
`experimental-deliberation/`, `_core/deliberation/`) confirmed clean.

**Does the fold recompute per document, or filter a shared list? It
genuinely recomputes per document** — confirmed by reading the source
(`stale_n` is measured against each document's own `document_names[index]`,
never a filtered slice of the shared, revision-0-anchored `stale` list) and
by a live mutation of the shipped engine file that reproduces the exact
bug the design warned against and confirms the shipped code does not have
it.
