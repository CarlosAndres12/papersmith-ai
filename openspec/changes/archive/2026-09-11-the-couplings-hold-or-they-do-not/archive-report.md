# Archive Report: the-couplings-hold-or-they-do-not

**Change**: `the-couplings-hold-or-they-do-not`
**Project**: papersmith-ai
**Archived**: 2026-09-11
**Status**: PASS, archived (one non-blocking WARNING carried forward, no CRITICAL findings)
**Position in build**: Phase 8 of 8 (paper-writing skill). Third and final merge into `block-substitution`; introduces `citation-integrity`, `contract-currency`, `coupling-verification` as new capabilities.

## Source Artifacts (Engram, hybrid store — filesystem copies were canonical)

| Artifact | Observation ID | Topic key |
|---|---|---|
| proposal | 1616 | `sdd/the-couplings-hold-or-they-do-not/proposal` |
| spec | 1620 | `sdd/the-couplings-hold-or-they-do-not/spec` |
| design | 1626 | `sdd/the-couplings-hold-or-they-do-not/design` |
| tasks | 1631 | `sdd/the-couplings-hold-or-they-do-not/tasks` |
| verify-report | 1690 | `sdd/the-couplings-hold-or-they-do-not/verify-report` |

All five read via `mem_get_observation` in full (not previews) before this report was written.

## What Shipped

The read-only `verify` verb: a report over seven cross-section couplings stated in `sections/*.md` against the rendered `paper/main.tex` and the declared-block record. Reports, never repairs — same posture as `skill-audit`.

- **Coupling 1** (contribution list identity across intro/methods/abstract/conclusions) — mechanical.
- **Coupling 2** (problem→contribution→property→instrument→evidence chain, word identity) — mechanical, strongest coupling; contract demands string equality, not synonymy.
- **Coupling 3** (intro gap vs related-work gap, "same thing at different depths") — assisted. Three mechanical sub-checks (both closings present, front-count/list equality) plus one human reading that verify never computes. Verdict vocabulary for this coupling is the single value `unmeasured`; `pass`/`holds` is **structurally absent**, not merely unused, and `_entry`'s own runtime assertion (`unmeasured_reason set on a non-unmeasured verdict`) raises before a false pass verdict could ever be returned — proven in verification by hand-mutating `check_gap` to compute a verdict from the three clean mechanical sub-results and watching the guard fire first. This is a stronger guarantee than the design document states.
- **Coupling 4** (results-artifact diagram cells vs methods diagram, disjointness) — mechanical over declarations; methods side is *derived* from coupling 1's contribution list, not separately declared.
- **Coupling 5** (future work ⊆ limitations) — mixed: totality and shared citation key mechanical, "relevant subset"/"specific enough" out-of-reach (unmeasured).
- **Check A** (`\cite` ↔ `refs.bib`) — mechanical, both sides derived from the document, no declaration read at all.
- **Check B** (blocks vs. contract hash currency) — out-of-reach today; refuses `CONTRACT_RECORD_ABSENT` because nothing yet writes the provenance record this check would read (Phase 3's `the-paper-carries-its-own-decisions` owns that write; this change only reads the interface).

New modules: `.claude/skills/paper-writing/scripts/paper_evidence.py` (all disk reads) and `paper_verify.py` (pure checks, refusal roster, report shape), kept split so the read-only AST lock can distinguish reader from check. `verify` registered in `paper_cli.py` beside `scaffold`/`status`/`open`/`substitute`; exit 0 for any verdict including findings/unmeasured, exit 2 only for inability to look (`DECLARATION_RECORD_ABSENT`).

Three tiers of inability: whole declaration record absent → refuses the run (`DECLARATION_RECORD_ABSENT`, exit 2, M6); one block's declaration entry absent → `unmeasured`/`BLOCK_NOT_DECLARED` only for that block's dependent couplings, run proceeds; provenance region absent → check B alone `unmeasured`/`CONTRACT_RECORD_ABSENT`, exit 0 (M7). Tasks.md records a real design/spec wording conflict on this last point (design said "unmeasured, exit 0"; the spec's M7 scenario as originally drafted said "refuses, non-zero exit") that was resolved during implementation per design (task 1.5) with the spec wording reconciled (task 3.13) — resolved in the archived spec, not left open.

## Delta Spec Merge (openspec/hybrid)

Merged against `openspec/specs/block-substitution/spec.md` **as read from disk at merge time**, not against any verify-report's description of it — per this build's own established caution (a sibling archive found and corrected a stale "12 codes" claim by doing the same thing).

| Domain | Action | Before | After | Detail |
|---|---|---|---|---|
| `block-substitution` | Modified (delta merge) | 14 requirements, 21 Refusal Roster rows | 15 requirements, 21 Refusal Roster rows | Appended one ADDED requirement, "verify Verb Is Registered And Read-Only" (3 scenarios), verbatim from the delta. The delta added no new Refusal Roster table rows — `DECLARATION_RECORD_ABSENT` and `CONTRACT_RECORD_ABSENT` are refusal codes belonging to the new `coupling-verification`/`contract-currency` capabilities' own domains, not to `block-substitution`'s table, and the delta's own text confirms this (no ADDED Refusal Roster row present in the delta file). |
| `citation-integrity` | Created (new capability) | — | 4 requirements | Mechanical copy, delta spec file IS the full spec (no prior main spec existed). |
| `contract-currency` | Created (new capability) | — | 4 requirements | Mechanical copy, same as above. |
| `coupling-verification` | Created (new capability) | — | 9 requirements | Mechanical copy, same as above. |

**Verification method, per capability**:
- `block-substitution`: structural verification (this is a genuine delta merge into an existing file, not a byte-identical copy — `diff -r` does not apply here). Verified by requirement-count delta (14→15, exact +1 expected from one ADDED requirement) and Refusal-Roster-row-count stability (21→21, expected since the delta added zero roster rows), plus `git diff` confirming the change is purely additive — 33 insertions, 0 deletions, 0 modifications to any pre-existing line. The appended text is an exact match to the delta spec file's content.
- `citation-integrity`, `contract-currency`, `coupling-verification`: mechanical `cp` via temp-file-then-`mv`, each followed by `diff -r` against the delta source. All three diffs returned empty (byte-identical). Verbatim output below.

```
DIFF_EMPTY:coupling-verification
DIFF_EMPTY:citation-integrity
DIFF_EMPTY:contract-currency
```

## Archive Folder Move — Mechanical Copy Contract

```bash
snapshot_root=$(mktemp -d ...)
cp -R "openspec/changes/the-couplings-hold-or-they-do-not" "$snapshot_root/source"
git mv openspec/changes/the-couplings-hold-or-they-do-not openspec/changes/archive/2026-09-11-the-couplings-hold-or-they-do-not
diff -r "$snapshot_root/source" "openspec/changes/archive/2026-09-11-the-couplings-hold-or-they-do-not"
```

`diff -r` output: **empty** (`DIFF_STATUS=0`). The archived folder is byte-identical to the pre-move snapshot; this report file is additive and was written after the comparison, per the Mechanical Copy Contract's exclusion of the archive-report itself.

Contents confirmed present in the archived folder: `proposal.md`, `design.md`, `tasks.md`, `verify-report.md`, `specs/block-substitution/spec.md`, `specs/citation-integrity/spec.md`, `specs/contract-currency/spec.md`, `specs/coupling-verification/spec.md`, plus this `archive-report.md`.

## Task Completion Gate

`tasks.md`: 32/32 tasks checked (`- [x]`), 0 unchecked (`- [ ]`), confirmed by direct count against the tracked file, not inherited from any snapshot's claim.

## Final State (per the Final-State Authority hierarchy)

No `reviewGate` was discovered for this candidate in structured status — receipt-driven development did not gate this archive; ordinary repository policy applies. No native review artifacts exist to read.

Verify-report (1690, PASS, `gentle-ai sdd-verify-validate` admitted `valid: true`) is the highest-ranked source available and is itself close to the archive point in time (2026-09-11, same day), so nothing in it is stale as of this archive:

- 32/32 tasks, 18/18 requirements, 22/22 scenarios. Full test suite green: 559 npm + 3202 Python, 6 pre-existing skips, 0 failures. `npm run typecheck` exit 0 — no stale toolchain claim to correct here (checked; nothing in this change's trail claims `tsc: command not found` or similar).
- Five independent by-hand mutation probes beyond the apply's own proof, all confirming design claims rather than merely re-asserting them (see below).
- One non-blocking WARNING, carried forward verbatim because it was not disclosed by the apply and would otherwise be lost at archive:

**WARNING — the read-only AST lock proves write-freedom, not read-freedom.** `ReadOnlyTests._forbidden_write_calls` scans `paper_coupling_evidence.py` and `paper_verify.py` (module names as they exist in the built tree) for write-shaped calls (`open` in write mode, `write_bytes`, `mkdir`, `replace`, `shutil`, `tempfile`, `paper_block.substitute`/`open_block`) — it never checks for reads. `paper_verify.py`'s internal docstring claim of "no disk read anywhere in this module" currently rests entirely on the absence of a `pathlib`-style import, not on any executable guard. Verified live during sdd-verify: a real `Path(...).read_bytes()` call was injected into a sandboxed mutant of `paper_verify.py`, and the entire 174-test module — including the AST-lock test itself — passed against it, because that test reads the real on-disk `paper_verify.py` by a fixed path rather than through the mutant's `sys.modules` entry, so it never even saw the mutant. This is the same reachability gap independently confirmed for `_run_against_mutant` generally (see below); it was previously disclosed only for the roster-derivation test (M9), never for the AST-lock test specifically, until this verification pass. No spec requirement is violated — every spec requirement here is about write-freedom, which IS proven — this is a coverage gap in an internal comment's claim, not a functional defect, and does not block archive.

**Reachability mechanism, worth preserving beyond this change**: `_run_against_mutant` (the test harness's mutation-testing helper) cannot reach any test that reads its target source by a fixed real path instead of through `sys.modules`. This affects both the refusal-roster derivation walk and the AST read-only lock test. Any future mutation proof written against `paper_verify.py` or `paper_coupling_evidence.py` must match this actual reachability mechanism (in-process `sys.modules` substitution) rather than assume the general shape of the existing test harness works uniformly — it does not, for tests that open the real file by path.

No contradictions found between the launch prompt's final-state facts and the verify-report; both agree PASS/archivable with the one WARNING above. No stale claim required correction beyond the general caution already applied to the spec-merge step (verified against disk, not report prose).

## Concurrency Note

At archive time, `openspec/changes/a-diagram-that-compiles-or-says-why/verify-report.md` was modified but uncommitted in the shared working tree — the work of a concurrently-running sibling archive for a different change in this same eight-phase build. That file was left untouched and excluded from this change's commit; only paths under `openspec/changes/the-couplings-hold-or-they-do-not/` (now moved), `openspec/changes/archive/2026-09-11-the-couplings-hold-or-they-do-not/`, and the four `openspec/specs/{block-substitution,citation-integrity,contract-currency,coupling-verification}/` paths were staged and committed by this archive.

## Remaining Build Sequence

Archived so far (in order): `only-the-block-changes`, `the-contract-is-data-not-code`, `no-claim-without-a-source-that-holds-it`, `the-paper-carries-its-own-decisions`, and now `the-couplings-hold-or-they-do-not` (this report). Still to come: `the-writer-may-assert-only-what-it-was-given`, then `a-diagram-that-compiles-or-says-why`.
