```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:180dd983f2c4a1e35bf5be2e8276ffe3948da4d4d58f51011b75a97d5dfc0a3a
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 16/16
scenarios: 35/35
test_command: .venv/bin/python -m unittest discover -s tests -p "test_*.py" -v
test_exit_code: 0
test_output_hash: sha256:877201e95d72af0287fe7e1e983d31dc751f584dddc0e95bde20b7f6ff4ec984
build_command: npm test
build_exit_code: 0
build_output_hash: sha256:1e27b000bd0479a6c913360bfb84101c0c604980d594adead1df48750b5ca52d
```

# Verification Report — a-data-directory-somebody-can-owe (Slice B)

## Change
`a-data-directory-somebody-can-owe` — Slice B, both work units B1 and B2.
Repo: `/Users/diego/.herdr/worktrees/papersmith-ai/experimental-implementation`,
branch `experimental-implementation`, HEAD `cf8252f`. Worktree clean apart
from the untracked `openspec/changes/the-agreement-nothing-computes/`
(Slice D planning), correctly out of scope and not touched by this
verification.

## Mode
Full artifact set present and read: proposal.md (including the appended
"five questions, ruled" section), five spec deltas, design.md, tasks.md,
plus Engram mirrors of all five artifacts (`sdd/a-data-directory-somebody-
can-owe/{proposal,spec,design,tasks,apply-progress}`). Full spec-driven
verification performed: completeness, correctness, and design coherence.

## Task Completeness
37 of 37 tasks checked `[x]` across 11 phases (Phase 1–7 = B1, Phase 8–11 =
B2). Zero unchecked. `git status --short` shows the worktree clean apart
from the noted untracked Slice D directory; HEAD matches the tasks/apply
artifacts' final commit `cf8252f`.

## Test/Build Evidence (re-measured this session, not inherited)

| Command | Result |
|---|---|
| `npm test` | 595/595 pass, 0 fail |
| `.venv/bin/python -m unittest discover -s tests -p "test_*.py" -v` | Ran 2998 tests, **OK (skipped=6)**, 0 FAIL/ERROR lines |
| `git diff --exit-code -- tests/seal/` | exit 0 |
| `sha256(tests/seal/digests.json)` | `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75` — unchanged |
| `reachable_refusal_codes()` count | 114 (unmoved) |

No foreign `unittest discover` processes were running before this session's
measurement (checked via `ps aux`). Full suite run in background per
instructions; both logs redirected to files and grepped for `Ran [0-9]+
test`/`FAIL`/`ERROR` — zero of the latter two.

## The Acceptance Condition — verified by execution

**Can `verify.structure.missingDirs` now contain a `Data/`? Yes.
Could it not before? Yes, confirmed.**

- **Pre-change (`fa04edc`, one commit before `c211e9f`, via `git worktree
  add --detach`)**: `cmd_verify`'s `with_data` at that commit is the single
  line `(target / name / "Data").is_dir()` — no document parameter exists
  in that command at all. Ran a real `verify` subprocess against a fresh
  git-initialized target with `Trial/` present but `Trial/Data/` absent:
  `missingDirs = ['Trial/Notebooks', 'Trial/Results', 'Trial/Models',
  'src/Trial', 'tests']` — **`Trial/Data` is absent from the list despite
  the directory itself being absent from disk**, because `with_data` is
  `False` and `expected_dirs` therefore never adds `Data/` to what could be
  missing. Structurally unreachable, not merely untested.
- **At HEAD**: ran the real `experiments_seal` cases directly (bypassing
  `digests.json`, reading raw subprocess stdout myself):
  `verify-b-declared → missingDirs=['Trial/Data'], status=drift`;
  `verify-a-declared → missingDirs=[]`; `verify-b-undeclared → missingDirs=
  []`; `verify-b` (no `--revision` at all) `→ missingDirs=[]`. The four
  results together show the gap now moves on the declaration, not the
  fixture.

## Spec Compliance Matrix (16 requirements / 35 scenarios, all covered)

| Spec | Requirements | Scenarios | Status |
|---|---|---|---|
| `implementation-data-demandability` (NEW) | 7 | 13 | All covered — `DatasetDeclaredDetectorTests` (6/6, incl. the None-spy, the X3 mid-sentence negative, the regex-literal test, the or-fold), `LockCDeclaredMarkerTests` (2/2), `ZeroBareDataLiteralTests`, `reachable_refusal_codes()==114`, `experiments_seal` D9 cases (live-reproduced) |
| `implementation-document-binding` (ADDED) | 2 | 6 | All covered — `RevisionThreadingAgreementTests` (5/5, real subprocess `plan→approve→apply`/`materialize --stage`), the byte-identical-stdout scenario proven by the sibling's untouched 28 digests |
| `implementation-engine-neutrality` (MODIFIED+ADDED) | 2 | 6 | All covered — `CoreNamesNoDomainTests` (2/2), `test_implementation_domain_mutation` (12/12, incl. `test_every_leaf_moves_exactly_its_measured_case_set` for the new `documents[i].dataset_marker` row), `test_implementation_profile.py`'s per-index refusal tests |
| `implementation-cli-seal` (MODIFIED+ADDED) | 3 | 7 | All covered — `.claude/skills/proposal-implementation/impl_profile.py` diff is exactly 6 insertions (1 code line + 5-line comment), zero other sibling files touched, `tests/seal/` 28 digests byte-identical, `experiments_seal` corpus coverage test |
| `experimental-implementation-skill` (ADDED) | 2 | 3 | All covered — `documents[0]` declares `"**Dataset:**"` (matches `experimental-deliberation`'s own enforced literal), `documents[1]` stays `None`; `SKILL.md` diff adds 27 lines stating the per-product-folder, presence-only demand |

**Totals**: 16/16 requirements, 35/35 scenarios — every one backed by a
passing runtime test, re-run this session, not inherited from apply's
report.

## The Five Focus Items

### 1. The `None`-marker spy proof
Reproduced `test_a_none_marker_never_opens_the_document` directly (passes).
Independently verified the spy mechanism itself is not inert: built a
parallel case with a real marker present and a real document, spied on
`revision_source` the same way, and confirmed the spy **does** register a
call (`[('r1.md', 0)]`) when a read actually happens. This closes the "spy
that cannot register" risk named in the launch brief — the branch is
structural, not merely a passing coincidence.

### 2. X3 — the line-leading → substring mutation
Reproduced independently on a scratch copy of the whole engine tree (never
the shipped file), comparing the real engine against the mutated one for
two fixtures: a mid-sentence-only occurrence and a line-start occurrence.
Real engine: mid-sentence → `False`, line-start → `True` (correct). Mutated
engine: mid-sentence → `True` (flipped — the mutation is killed), line-start
→ `True` (survives, unchanged). This exactly matches the design's claim:
every positive fixture survives, only the mid-sentence-marker negative
kills it. The shipped test `test_a_mid_sentence_only_occurrence_answers_false`
passes at HEAD, confirming this negative exists in the real suite, not only
in my scratch reproduction.

### 3. `experiments_seal` separation
Read the raw `git diff` of `tests/experiments_seal/digests.json`: only
`__corpus_fingerprint__` changed value, and four new keys were added
(`plan-b-declared`, `verify-a-declared`, `verify-b-declared`,
`verify-b-undeclared`). Every one of the pre-existing 20 entries is
byte-for-byte present with its original hash (confirmed `verify-b`'s
sha256 is identical before/after). Total case count is 24 (20 + 4),
confirmed by loading the JSON directly. Zero of the 20 pre-existing cases
moved — stricter than C3's 6-of-20 precedent, confirmed by direct
inspection rather than trust in the stated claim.

### 4. The three findings apply closed
- **In-process helper leak**: searched the entire test suite for any other
  code touching `IMPLEMENTATION_DOMAIN_PROFILE`/`sys.modules
  ["impl_domain_profile"]` in-process (not via a subprocess `env` dict).
  Found exactly three in-process helpers total: the fixed one in
  `test_experimental_implementation.py` (save/restore in `finally`, now
  correct), one in `test_experiments_seal.py` (already had save/restore),
  and one in `test_experimental_implementation_mutation.py` (a
  **pre-existing** helper from an earlier change, already pops
  `impl_domain_profile`/`impl_domain_profile_host` before **and** after,
  with a docstring that documents the exact hazard). No other in-process
  helper shares the leak shape; the fix is isolated and the class of
  defect is not repeated elsewhere.
- **`tests/pair/corpus.py` anchor staleness**: diff confirmed — the two
  anchor constants gained a `dataset_marker: None` line matching the
  fixture's own new required leaf, nothing else changed.
- **The lock catching its own docstring's literal**: confirmed by `git log
  -p` on the engine file — an earlier commit's docstring for
  `_document_declares_dataset` did spell `"**Dataset:**"` as an
  illustrative example ("a document that only DISCUSSES its own format
  (`every protocol needs a **Dataset:** line`)"), and a later commit
  reworded it to describe the shape without spelling the value, with a
  commit message stating `LockCDeclaredMarkerTests` caught it. Story
  confirmed against real commit history, not merely the reported
  narrative.

### 5. The one sanctioned sibling edit
`.claude/skills/proposal-implementation/impl_profile.py`: `git diff --stat`
shows exactly 1 file, 6 insertions, 0 deletions. Read the diff directly:
one code line (`"dataset_marker": None,`) plus a 5-line comment citing the
change and its reasoning — nothing else. `git diff --stat` for
`.claude/skills/proposal-deliberation/`, `.claude/skills/experimental-
deliberation/`, `.claude/skills/_core/deliberation/` against the pre-change
commit returns empty (zero files) in all three. `git diff --exit-code --
tests/seal/` exits 0; `npm test` 595/595; Python `OK (skipped=6)` — all
re-measured this session, matching the claimed bar exactly.

## Also Confirmed

- **`build_plan`'s three call sites agree by construction.** Ran
  `RevisionThreadingAgreementTests` directly (5/5 pass), including
  `test_a_bare_apply_after_plan_revision_cannot_produce_plan_stale` (real
  subprocesses: `plan --revision X` → approve → bare `apply`, no
  `PLAN_STALE`) and the `materialize --stage` equivalent.
- **`--revision` registered on `plan` alone, not three parsers.** Confirmed
  by reading the full `main()` argparse block: the eight-name shared set is
  untouched, `plan` gets its own `if name == "plan":` block (line ~17764),
  mirroring `walk`'s own separate block. `cmd_apply` reads the seed from
  `approved["boundTo"]["revision"]`; `boundTo` is confirmed **absent** from
  `cmd_apply`'s four-key comparison tuple (`"renames", "moves",
  "createDirs", "referenceUpdates"`), exactly as claimed.
  **Minor documentation inconsistency found** (see Warnings below):
  design.md's own "Predictions" section and D3's rationale text describe
  this as reaching "ten commands through two registrations" / "the
  eight-name set becomes nine," but the actual code adds a **third**,
  separate registration block for `plan` (matching tasks.md 3.4's own
  wording, "as its own registration, mirroring walk's separate one," which
  contradicts D3's "becomes nine" framing). Ten commands is correct; "two
  registrations" is not — there are three.
- **`dataset_marker` sits in its own tier**, confirmed by reading
  `impl_domain_profile.py`'s `_resolve()`: the required-key check is a
  standalone `if` block appended right after the `label` check, and
  `_DOCUMENT_VOCABULARY_LEAVES` (the five-leaf all-or-nothing tuple) does
  not list `dataset_marker`.
- **`LockCDeclaredMarkerTests` is over the declared VALUE, not the word
  `dataset`.** Confirmed `classify()` returns the literal reason string
  `"dataset"` at line 2814 (M4's claim), and confirmed
  `LockCDeclaredMarkerTests.test_no_declared_marker_appears_in_the_engine`
  compares `marker in source` where `marker` is the declared string value,
  never the bare word. The docstring-catch story above independently
  confirms the lock actually fires on real content.
- **Zero new skips**: `Ran 2998 tests ... OK (skipped=6)`, unmoved from the
  `2977` baseline through nine changes now.
- **Spec conformance**: 16 requirements / 35 scenarios recounted directly
  from the five spec files (not inherited from the proposal/design
  summaries), all backed by passing tests as tabulated above.

## Issues

### CRITICAL
None.

### WARNING
1. **design.md's own registration-count claim is internally
   inconsistent with the shipped code.** D3 argues "the eight-name set
   becomes nine" and the Predictions section states "`--revision` reaches
   ...ten [commands] through two registrations," but the actual
   implementation (confirmed by reading `main()`) gives `plan` its own
   third, separate `if name == "plan":` block rather than merging it into
   the eight-name set — matching tasks.md's own description of the choice,
   but contradicting D3's stated mechanism and the Predictions section's
   count. Functionally correct and spec-compliant (the spec only requires
   `--revision` to reach `plan`, not a specific registration count/shape);
   this is a design-artifact accuracy issue, not a behavioral defect.
   Recommended resolution: correct design.md's D3 text and Predictions
   bullet to say "three registrations" (or fold `plan` into the shared set
   in a follow-up, changing the code to match the original design intent)
   — orchestrator/user decision, not fixed here.

### SUGGESTION
1. `apply-progress`'s mid-session note recorded `test_implementation_
   domain_lock.py (24/24)` after task 8.2; the file now holds 26 tests, all
   passing. Not a defect (more tests were added in later phases, e.g.
   `LockCDeclaredMarkerTests`, `TwoDocumentReadProvenTests` from a different
   change); flagged only so the historical count in apply-progress is read
   as a mid-session snapshot, not a final one.
2. The tasks.md file contains 37 checked tasks across 11 phases, not "30"
   — likely a rough count carried in the launch brief rather than a claim
   made by the artifact itself; no discrepancy found in the artifact.

## Design Coherence
All ten architecture decisions (D1–D10) were checked against the shipped
code and hold, with the one documentation-only exception noted above (the
registration-block count). D1 (literal line-leading marker, required,
nullable, own tier) — confirmed in source. D2 (or-fold across every
document) — confirmed by `test_or_fold_only_index_one_declares_and_the_
demand_still_holds` passing and by `OrFoldIndexHardcodeMutationTests`
passing. D4 (one conditional key, `boundTo`, emitted only when nameable) —
confirmed byte-identical sibling stdout via the untouched 28 digests. D5
(three-statement reorder in `cmd_verify`) — confirmed inert by the same 28
digests and the new experiments_seal cases. D6 (F5 finished + derived lock)
— confirmed, `PRODUCT_DATA` appears quoted exactly once in the engine. D7
(new lock lands in B2, vacuous until 8.1) — confirmed by lock passing and
by the non-vacuity assertion. D8 (the sibling-corpus mutation) — confirmed,
`MEASURED_MOVERS["documents.dataset_marker"] == ("verify-b", "verify-t")`.
D9 (B2's corpus axis, zero of 20 existing cases move) — confirmed by direct
diff inspection. D10 (landing order) — confirmed by commit history (B1's
five phases land before B2's four).

## Final Verdict

**PASS WITH WARNINGS.**

Zero CRITICAL findings. One WARNING (a design.md documentation-accuracy
issue with no behavioral or spec impact). All 37 tasks complete, all 16
requirements / 35 scenarios covered by passing runtime tests re-measured
this session (not inherited), the acceptance condition demonstrated by
direct execution on both sides (pre-change structurally cannot produce a
`Data/` gap; at-HEAD does, with two independent controls holding empty).
`npm test` 595/595, Python `Ran 2998 tests ... OK (skipped=6)`, `tests/seal/`
28 digests byte-identical, `reachable_refusal_codes()` unmoved at 114.

Recommended next phase: **sdd-archive**.
