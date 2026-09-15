# Archive Report: The Writer May Assert Only What It Was Given

**Change**: `the-writer-may-assert-only-what-it-was-given`
**Archived**: 2026-09-11
**Archived to**: `openspec/changes/archive/2026-09-11-the-writer-may-assert-only-what-it-was-given/`
**Sequence**: sixth of seven archives closing the `paper-writing` eight-phase build.
Order note: this change owns a **delta merge** into `section-contract` — the
second of three deltas that requirement/scenario set absorbs. Archived before
this change: `only-the-block-changes` (`337de69`), `the-contract-is-data-not-code`
(`ba59360`, created `section-contract`), `no-claim-without-a-source-that-holds-it`
(`a07b0fb`/`d042cd9`), `the-paper-carries-its-own-decisions` (`0279e89`/`7ed7800`),
`the-couplings-hold-or-they-do-not` (`0fdb866`). After this: `a-diagram-that-
compiles-or-says-why`, which merges into `section-contract` last. `section-
contract` is left able to absorb that one further delta — this merge appended
requirements rather than replacing the file wholesale, and nothing here closes
the file to future ADDED/MODIFIED sections.

## Artifacts read (Engram observation IDs)

| Artifact | Observation ID |
|---|---|
| proposal | #1623 |
| spec | #1632 |
| design | #1634 |
| tasks | #1636 |
| verify-report | #1670 (merged: original pass + first corrective + this pass's final corrective re-verification) |

## Final-State Authority

Per the Final-State Authority hierarchy, this report states the state AT
CLOSE, not any earlier snapshot. `verify-report` (#1670) is itself layered:
an original pass, a first corrective section, and a **final corrective
re-verification** re-verifying commits `35ec14f`/`eab6496`. That final section
is the authoritative current state and is what this report carries forward —
the earlier FAIL/CRITICAL recorded mid-document in the same observation is
historical, already superseded within the observation itself, and is not
echoed here as current.

**Current verified state** (final corrective re-verification, commits
`35ec14f`, `eab6496`):
- Verdict: **PASS WITH WARNINGS**, archivable: **YES**
- 0 CRITICAL, 1 WARNING, 2 SUGGESTION
- Requirements 25/25, scenarios 39/39
- Full suite green on a clean isolated re-run: npm 559/559, Python
  `unittest discover` 3231 tests `OK (skipped=6)`, exit 0 both; typecheck
  clean, output byte-identical (`sha256:0489b64b...`) across all three
  verification passes of this change
- Validated via `gentle-ai sdd-verify-validate`: `valid:true`,
  `verdict: pass_with_warnings`

This closed the change's one prior CRITICAL: the `section-contract` spec's
`Requirement: Closed Mode Vocabulary And Transcription` was unenforced and
measurably violated (`06-introduction.md`'s real quote failed the existing
`after`-edge lock because the prose wraps two of its words in `**bold**`
mid-sentence). Fix: `tests/test_paper_contract.py`'s `_quote_in_body` was
extended with a closed, enumerated markdown-emphasis strip (`*` only) shared
by both `after` and `mode`; `ModeTranscriptionTests` was added
(corpus-derived, all seven modes, self-sourced fabrication proof,
paraphrase/unrelated-sentence proof against fuzzy-match risk). No further
CRITICAL exists.

## Context that must survive the archive (recorded as-is, per instruction)

- **The transcription discipline is enforced only by the test suite.** The
  final corrective re-verification independently drove the real production
  entrypoint (`paper_graph.assemble_corpus` — what every CLI verb calls)
  against a tampered `mode.source.quote`, and it was **accepted silently**.
  `_quote_in_body` lives exclusively in `tests/test_paper_contract.py`, a
  module `paper_cli.py` never imports. This is a measured property of the
  design, inherited from the pre-existing `after`-edge design — already true
  before this change touched anything, not scope-creep introduced here, and
  not something a future reader should have to rediscover. Reported as the
  change's one WARNING (informational, disclosed, non-blocking).
- **`mode`'s validator was copied from the `after` edges' shape without
  copying the test that made it honest.** A spec-mandated MUST
  (`Closed Mode Vocabulary And Transcription`) went unenforced and a false
  quote shipped on the first apply attempt. General form worth carrying
  forward: a validator copied from a sibling carries the sibling's shape,
  not the sibling's guarantees.
- **The lock strips markdown emphasis** — a closed whitelist of exactly one
  character (`*`) — applied identically to `after` and `mode`. Independently
  re-derived (not re-read from the shipped test's own account) against 5
  adversarial near-misses: one-word substitution, word-order swap, dropped
  clause, mid-quote punctuation removal, en-dash→hyphen — all 5 correctly
  FAIL the lock; case-sensitive too. One genuine admission: the `*` strip is
  **positionally blind** (not emphasis-pair-aware) — `"func*tions"` still
  matches `"functions"` since both sides get the same strip. Inert today (no
  content-word blur, no exploit found), filed as a SUGGESTION — carry
  forward.
- **Three contracts deliberately have no declared mode** —
  `02-experimental-setup`, `04-limitations`, `05-related-work`. `write`
  correctly refuses `MODE_ABSENT` for them (independently confirmed: a
  corpus dump shows `mode=None` for exactly these three). This is not
  incomplete work: no sentence in those contracts' prose states a mode, and
  choosing one would put the implementer's editorial judgement into the
  operator's files. They await the operator's own transcription, exactly as
  any `after` edge is operator-transcribed, never code-guessed. Record this
  plainly so nobody later reads it as a gap to fill.
- `paper_contract.install_header` has zero production callers — pre-existing,
  owned by the already-archived `the-contract-is-data-not-code`, deliberately
  left with a docstring note. Re-confirmed by the final corrective pass: no
  second new dead-function instance was introduced by either corrective
  commit. Still open, still not this change's to fix.

## Task Completion Gate

`tasks.md` (git-tracked since `20b3e0c`): 25/25 tasks checked (`[x]`), 0
unchecked implementation tasks (`rg -c '^\- \[ \]'` → 0 on the archived
file). Task 1.18 (the corrective mode-transcription verification lock) is
checked and its evidence is the final corrective re-verification above.
Gate passes; no reconciliation was needed.

## Native Review Receipt Gate

No `reviewGate` key was present in this launch's context (no structured
status payload was supplied to this archive run). Per the skill's absent-key
convention, an absent `reviewGate` is not itself evidence of a defect or a
reason to investigate — archive proceeds under ordinary repository policy.
No `sdd/{change-name}/review/*` topics were read because none were indicated
as present.

## Specs Synced

| Domain | Action | Requirements | Scenarios |
|---|---|---|---|
| `contract-audit` | Created (new capability) | 4 | 7 |
| `evidence-bound-drafting` | Created (new capability) | 6 | 10 |
| `style-channel` | Created (new capability) | 3 | 3 |
| `style-leak-detection` | Created (new capability) | 5 | 8 |
| `writing-orchestration` | Created (new capability) | 4 | 4 |
| `section-contract` | Delta-merged (MODIFIED + ADDED) | +2 net (6→8) | +5 net (11→16) |

**`section-contract` merge detail** (structural verification, per the
delta-merge convention — `diff -r` does not apply to a merge into an
existing file):
- MODIFIED `Requirement: Front Matter Schema` — replaced in place; widened to
  admit an optional `mode` at section and block level. Word-normalized diff
  against the delta's MODIFIED text (line-wrap differences only): empty —
  semantically identical.
- ADDED `Requirement: Headers Written Before 'mode' Existed` and
  `Requirement: Closed Mode Vocabulary And Transcription` — appended after
  the existing `Transcribed 'after' Edges Only` requirement. Word-normalized
  diff against the delta's ADDED text: empty — semantically identical.
- Requirement count: 6 → 8 (net +2: 1 replaced 1-for-1, 2 added).
- Scenario count: 11 → 16 (net +5: Front Matter Schema gained 2 scenarios,
  the 2 new requirements carry 1 and 2 scenarios respectively).
- Tail readback performed on the merged file; new content confirmed present
  and correctly terminated.
- All 6 pre-existing requirements not touched by this delta (`Closed Fact
  Vocabulary`, `Closed Declaration Vocabulary`, `Closed Citations Regime`,
  `Byte-Clean Header Insertion`, `Transcribed 'after' Edges Only`, and the
  replaced `Front Matter Schema` itself in its new form) are preserved.
- File remains open for one further delta (`a-diagram-that-compiles-or-
  says-why`, archiving next).

**New-capability specs** (no main spec existed for any of the five — each
delta file IS the full spec, copied mechanically per the Mechanical Copy
Contract):

```
--- diff -r contract-audit (source vs installed target) ---
(empty)
--- diff -r evidence-bound-drafting (source vs installed target) ---
(empty)
--- diff -r style-channel (source vs installed target) ---
(empty)
--- diff -r style-leak-detection (source vs installed target) ---
(empty)
--- diff -r writing-orchestration (source vs installed target) ---
(empty)
```

All five verified via mktemp-staged `cp` → `diff -r` (empty) → `mv`, then a
second `diff -r` of source against the final installed path (also empty).

## Archive Move

```
$ diff -r "$snapshot_root/source" "openspec/changes/archive/2026-09-11-the-writer-may-assert-only-what-it-was-given"
(empty — EMPTY DIFF - PASS)
```

Moved via `git mv`; `git status` confirms both sides of every rename are
staged together (no dangling deletion). Active `openspec/changes/` directory
no longer contains this change.

## Archive Contents

- proposal.md ✅
- design.md ✅
- specs/ (6 domains) ✅
- tasks.md ✅ (25/25 tasks complete)
- verify-report.md ✅ (merged, three sections, final corrective re-verification is authoritative)
- archive-report.md ✅ (this file, additive)

## Source of Truth Updated

- `openspec/specs/section-contract/spec.md` (delta-merged, 8 requirements, 16 scenarios)
- `openspec/specs/contract-audit/spec.md` (new)
- `openspec/specs/evidence-bound-drafting/spec.md` (new)
- `openspec/specs/style-channel/spec.md` (new)
- `openspec/specs/style-leak-detection/spec.md` (new)
- `openspec/specs/writing-orchestration/spec.md` (new)

## SDD Cycle Complete

The change has been fully planned, implemented, verified (through one
corrective re-verification pass), and archived. Ready for the next change.
