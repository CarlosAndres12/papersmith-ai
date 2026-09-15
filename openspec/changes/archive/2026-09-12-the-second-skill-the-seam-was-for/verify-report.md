# Verification Report: the-second-skill-the-seam-was-for (Slice A)

**Change**: `the-second-skill-the-seam-was-for` — Slice A only (single-document
`experimental-implementation`, zero engine bytes)
**Mode**: Full artifacts (proposal, specs ×3, design + D1-revisited appendix, tasks)
**HEAD verified**: `587399e4eda5cf03d3f4739d3a4d38483a943ae2`
**Verdict**: **PASS**

## Completeness

| Check | Result |
|---|---|
| Tasks checked/total | 33/33 (0 unchecked) — **not** 40/40 as apply's commit message and this SDD prompt state; see Issue W1 |
| Spec requirements (measured, not inherited) | 10 total: 5 (`experimental-implementation-skill`) + 3 (`implementation-engine-neutrality` delta) + 2 (`implementation-cli-seal` delta) |
| Spec scenarios (measured, not inherited) | 24 total: 10 + 7 + 7 |
| Design decisions (D1–D11, plus D1-revisited) | All present in design.md; D1-revisited appendix read |

## Build/Test Evidence (re-run this session, not inherited)

| Command | Result | Matches apply's report? |
|---|---|---|
| `npm test` | `tests 595 / pass 595 / fail 0` (50.2s) | Yes, exact match |
| `.venv/bin/python -m unittest discover -s tests -p "*.py" -v` | `Ran 2956 tests in 562.8s` / `OK (skipped=6)` | Yes, exact match |
| `sha256(tests/seal/digests.json)` | `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75` | Yes, exact match |
| `git diff --exit-code -- tests/seal/ tests/pair/` | exit 0 (both, before and after live re-run of the new corpus) | Yes |

No foreign `unittest discover` process was found touching this worktree before measurement; one unrelated `unittest discover -p test_*.py` process was observed mid-session running with `cwd=/Users/diego/Proyectos/papersmith-ai` (a different checkout entirely) — not this worktree, ignored per instructions.

## The five spend-your-effort-here items — all independently reproduced

### 1. The M1 guard can be made to fail — YES, confirmed live

Planted `"zzz-nothing-anywhere"` into the **real, shipped**
`.claude/skills/experimental-implementation/impl_profile.py`'s
`vocabulary.names` list (not a scratch copy), cleared `__pycache__`, ran
`LockADiscoveryTests.test_every_declared_name_really_is_that_domain_speaking`
live:

- **Before fix / vacuous check would have passed** — not applicable here since
  the shipped code already carries the D6 fix; the mutation went **RED**:
  `AssertionError: Lists differ: ['zzz-nothing-anywhere'] != []`.
- Reverted via `cp` from a pre-mutation backup; `shasum -a 256` confirmed
  **byte-identical** restoration (`eac872fe70f378b965885d4f79cf2489631d390c8d51507760cb3007ee9686db`
  before and after); `git diff --exit-code` on the file returned 0; test
  re-ran **GREEN**.
- Sibling check: ran the full `LockADiscoveryTests` class (all 4 methods,
  including the `subTest` for both skills) — **OK**, `proposal-implementation`
  passes unedited. `git diff --exit-code e3e1438 587399e --
  .claude/skills/proposal-implementation/impl_profile.py` — exit 0 (untouched
  across all of Slice A).

**Answer to the mandated question: yes, the M1 guard can now be made to fail.**
It is not merely asserted to be non-vacuous — a real mutation against the
shipped file, not a synthetic scratch string, was independently observed
turning it red and clean again.

### 2. The `sys.modules` caching defect — reproduced, load-bearing

Removed the two `sys.modules.pop("impl_domain_profile", ...)` /
`sys.modules.pop("impl_domain_profile_host", ...)` blocks from
`_fresh_engine_under` in `tests/test_experimental_implementation_mutation.py`,
cleared `__pycache__`, ran `PerLeafChangeMutationTests` standalone:

- Result: **14/14 subTests failed**, every one with `old_value == new_value`
  (e.g. `AssertionError: 'experiments' == 'experiments'`) — the exact caching
  signature apply-progress describes: the fresh engine load under a mutated
  scratch profile silently kept reading the FIRST profile ever resolved in
  that process (the real, unmutated one), because `implementation_engine.py`'s
  `from impl_domain_profile import PROFILE` is a regular cached import.
- Restored the file via `cp` from backup; `git diff --exit-code` on it
  returned 0 (byte-identical); re-ran the same test — **GREEN**, 1/1.

This confirms the pop is genuinely load-bearing, not decorative, and the
underlying defect (silent cross-profile cache reuse) is real and
reproducible. One nuance for the record: in this harness specifically the
effect surfaces as a **loud, 14-way RED** (a hard `assertNotEqual`), not a
silent green — the "false zero-movers" framing in apply-progress describes
the risk class this defect belongs to (the same shape as Cut 2's
defended-zero-mover architecture, where an unmeasured non-move can be
absorbed as legitimate), not a claim that *this specific* test would pass
silently. The finding and the fix are both real; the phrasing is imprecise
about which artifact would have gone silently green. Not blocking.

### 3. Zero engine bytes — confirmed, existence checked first

`git cat-file -e e3e1438:.claude/skills/_core` and
`e3e1438:.claude/skills/proposal-implementation` both confirmed **present**
(non-trivial pathspec) before diffing. `git diff --stat e3e1438 587399e --
.claude/skills/_core .claude/skills/proposal-implementation` produced **zero
output** (genuinely empty, not a vacuous non-existent-path pass). Full
touched-file list for the whole change range (`git diff --name-only e3e1438
587399e`) contains 19 files, none under `_core/` or `proposal-implementation/`.

### 4. Second sealed corpus beside the first, run live — confirmed

`tests/seal/` and `tests/experiments_seal/` are sibling directories (verified
by listing). Ran `tests.test_experiments_seal` live from a freshly cleared
`__pycache__` (not replayed from the earlier full-suite log): **12/12 pass**.
`sha256(tests/seal/digests.json)` identical before and after
(`011300df...`). `git diff --exit-code -- tests/seal/ tests/pair/` — exit 0
both times.

### 5. D10 single-document guard, both halves — confirmed

- Half 1 (new skill cannot declare a second document):
  `SingleDocumentGuaranteeTests` (2/2 live) — the vacuity-guarded per-profile
  assertion, plus mutation X8 applied inline to an in-memory copy (never the
  shipped file). Confirmed the guard is implemented via `discover_profiles()`
  (globs `.claude/skills/*/impl_profile.py` only), never inside
  `impl_domain_profile._resolve()`.
- Half 2 (pair fixtures still resolve two documents):
  `tests/fixtures/two_documents/impl_profile.py` lives under `tests/`, outside
  the glob root, so it is structurally invisible to the new lock. Ran
  `tests.test_implementation_pair` live — **23/23 pass**, including
  `TwoDocumentsResolveTests.test_the_valid_profile_resolves_and_the_command_succeeds`.

## Additional claims checked

| Claim | Re-measured | Match |
|---|---|---|
| M5 denylist: 74 total / 69 pinned / 5 absent | Ran `DerivedDenylistTests` (4/4 live) + independently recomputed `build_denylist()` size and the pinned/absent split via a standalone script | Exact match: 74 / 69 / absent = `formulation, mathematical, mathematics, statistical, traced` |
| Subject-word occurrence counts (word-boundary, case-insensitive) | `experiment` 24, `experiments` 6, `protocol` 1, four Spanish/derived forms 0 each | Exact match, independently re-derived via `rg -oi` |
| Design's own 89/30/28 line counts (`rg -c`) for benchmark(s)/experiment(s)/baseline(s) | Independently re-derived | Exact match — confirms these are a **different instrument** (line counts) answering a different question than the occurrence counts above, as both design.md and apply-progress state |
| Six design predictions "all HELD" | Spot-checked 3 of 6 by direct execution: (2) namespace word occurs 0× in engine — confirmed (`rg` returned 0); (3) byte-identical launcher — confirmed (`diff` clean); (6) `citation_pattern` exactly 3 groups — confirmed (`CitationPatternGroupCountTests` green). (1) confirmed as a byproduct of item 1's sibling check. (4) and (5) accepted on the strength of the passing `ThreatMatrixTests`/`DerivedDenylistTests` suites already re-run live above, not independently re-derived from first principles | 3/6 directly spot-checked, 1/6 confirmed as a byproduct, 2/6 accepted via passing test evidence only |
| `ENTRANCE_CLAIMS` trap | Checked all 5 phrases (`pair of skills`, `entrance from outside`, `arrives through a handoff`, `handed over by`, `the implementation skill`) against both `experiments-build.md` and `experiments-walk.md` | Clean — none present. `tests.test_agents` (16/16) also re-run live |
| Kit-lock glob (D9) | `KitAgreementLockTests` (8/8 live), including `test_this_skill_is_recorded_kitless` | Pass |

## Spec Compliance Matrix

All 10 requirements / 24 scenarios across the three spec files map to a
passing, live-executed test at HEAD:

| Spec | Requirement | Covering test(s) | Status |
|---|---|---|---|
| experimental-implementation-skill | The Skill Declares Its Own Domain Profile | `LeafRefusalTests` (2 scenarios) | ✅ COVERED |
| experimental-implementation-skill | One Skill, One North — No Dual Declaration | `declared_objective` behavior, exercised via existing `test_agents.py`/profile-resolution path (no planted `profile.ts` fixture re-run this session; accepted on source inspection + green `test_agents`) | ✅ COVERED (design-level) |
| experimental-implementation-skill | The North Belongs To This Skill Alone | `test_agents.py` cross-skill north lock (16/16 green) | ✅ COVERED |
| experimental-implementation-skill | The Two Agents Carry No Logic And Bind To This Skill's Own Stage | `AgentBindingTests` (16/16 green, incl. stretch/stage checks) | ✅ COVERED |
| experimental-implementation-skill | A Single Document Reproduces The Existing Byte-Identical Guarantee | `SingleDocumentGuaranteeTests` (2/2), `DoctrineVocabularyLeakTests` | ✅ COVERED |
| implementation-engine-neutrality | Kit Template Provenance Agreement (MODIFIED) | `KitAgreementLockTests` (8/8) | ✅ COVERED |
| implementation-engine-neutrality | Derived-Denylist Lock Satisfiable (ADDED) | `DerivedDenylistTests` (4/4) | ✅ COVERED |
| implementation-engine-neutrality | Namespace Word's Self-Check Is Not The Leak Proof (ADDED) | `LockADiscoveryTests` + `LockBEngineNeutralityTests` (live mutation reproduced this session) | ✅ COVERED |
| implementation-cli-seal | Non-Interference With Sibling Suites (MODIFIED) | `npm test` 595/595, Python `OK (skipped=6)`, seal digest hash match | ✅ COVERED |
| implementation-cli-seal | Second Skill Ships Its Own Seal Beside The Existing One (ADDED) | `test_experiments_seal` (12/12, live from scratch) | ✅ COVERED |

## Design Coherence

Design.md's D1–D11 decisions are all reflected in shipped code; the
D1-revisited appendix (documenting the operator's flipped ruling and the
orchestrator's framing error) is consistent with what actually shipped:
`documents[0]` is the experiments directory, matching D1's original ruling,
not the mid-flight contradicting brief. No design deviation found that
breaks a spec.

## Issues

**CRITICAL**: None.

**WARNING**:
- **W1 — Task-count bookkeeping is wrong, twice.** Commit `8074618`'s message
  and this SDD prompt both say "40/40" or "all 40 A1-A4 tasks measured and
  ticked." An independent count of `tasks.md`'s numbered checkboxes gives
  **33**, all checked, zero unchecked. This does not affect completeness (no
  task is missing or incomplete) — it is a numeral that was never verified
  against the artifact it describes, the same class of defect this project's
  own memory has repeatedly flagged ("Cited Symbols Are Claims, Not Facts").
  Recommend correcting the figure wherever it is repeated (commit message
  cannot be rewritten after archive, but the task/apply-progress artifacts
  can note the correction).
- **W2 — HEAD commit commingles two unrelated changes' artifacts.** `587399e`
  ("the ruling that flipped, and the orchestrator error behind it") is
  described as a design-record commit for Slice A, but its diff also adds
  `openspec/changes/the-second-document-verified-on-its-own-terms/proposal.md`
  (371 lines) — the parallel Slice C planning agent's own artifact — in the
  *same* commit. Per this session's explicit scope instruction, that
  directory's *content* was not read or evaluated, and it does not touch any
  engine, skill, or test path, so it does not threaten the zero-engine-bytes
  bar. It is flagged purely as commit hygiene: a commit whose message
  describes one change's design correction silently carries a second,
  unrelated change's 371-line artifact.

**SUGGESTION**:
- The design-prediction spot-check in this report covers 3 of 6 predictions
  by direct, independent execution/inspection; predictions 4 and 5 were
  accepted on the strength of already-passing test suites re-run live this
  session (`ThreatMatrixTests`, `DerivedDenylistTests`) rather than re-derived
  from first principles a second time. Given all suites are green and the
  underlying tests were themselves re-run live, this is not a compliance gap,
  only a note on verification depth for a future reviewer.

## Final Verdict: **PASS**

Zero CRITICAL issues. Two WARNINGs, both non-blocking (a bookkeeping numeral
and a commit-hygiene note, neither of which affects correctness, spec
compliance, or the zero-engine-bytes bar). All five explicitly-requested
"spend your effort here" items were independently reproduced by mutation
against the shipped files (not scratch copies, where the design allowed
testing the real file) or by live, from-scratch test execution. Both pinned
invariants (`npm test` 595/595, Python `OK (skipped=6)`) held exactly, and
`tests/seal/`'s 28-digest baseline is byte-identical before and after this
session's own live re-run of the new corpus.
