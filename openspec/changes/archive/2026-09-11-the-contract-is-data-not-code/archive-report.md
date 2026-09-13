# Archive Report: The Contract Is Data, Not Code

**Change**: `the-contract-is-data-not-code`
**Phase**: Phase 2 of 8 in the `paper-writing` skill build (sequence position 2 of 7 archives)
**Archived**: 2026-09-11
**Archive mode**: hybrid (filesystem + Engram)

## Source Artifacts Read (traceability)

| Artifact | Engram observation | Notes |
|---|---|---|
| proposal | #1601 (`sdd/the-contract-is-data-not-code/proposal`) | 2 revisions |
| spec | #1605 (`sdd/the-contract-is-data-not-code/spec`) | 1 revision |
| design | #1607 (`sdd/the-contract-is-data-not-code/design`) | 1 revision |
| tasks | #1609 (`sdd/the-contract-is-data-not-code/tasks`) | 3 revisions |
| verify-report | #1640 (`sdd/the-contract-is-data-not-code/verify-report`) | re-verification addendum, 2 revisions |

`reviewGate` was structurally absent for this candidate — no receipt-driven-development review was ever started for it — so the Native Review Receipt Gate imposed no additional artifact reads; archive proceeds under ordinary repository policy.

## Final-State Authority Resolution

Three sources bear on this change's closure state, and they must be read in the order below, not flattened into one summary:

1. **`tasks.md` at archive time (highest available rank for this change)**: all 23 numbered tasks (1.1–4.6) are `[x]`. No stale unchecked box. Task Completion Gate passes with no exceptional reconciliation needed.
2. **Explicit final-state fact in this archive's launch prompt**: "Verify status: closed/PASS." This outranks the verify-report snapshot's machine-readable `verdict: fail` field.
3. **`verify-report.md` (intermediate snapshot, lowest rank, read in full)**: records its own internal correction. The *original* pass found one CRITICAL (`C1`, an untested `writing-readiness` spec scenario) and one WARNING (`W1`, a vacuous transcription-quote lock for a self-sourced `after` edge). A corrective commit `0422dd1` (test-file-only, zero production code) closed both, and a **Re-verification Addendum**, dated 2026-09-11, independently re-falsified both fixes rather than accepting them on the corrective's own say-so:
   - **C1** — resolved by `OrderTests.test_back_matter_renders_last_while_its_writing_order_place_is_graph_derived_not_fact_derived`; independently confirmed by monkeypatching `paper_graph._sort_key` to neutralize `position` and observing the test go red.
   - **W1** — resolved by `_quote_in_body()`, which reads `paper_contract.parse()`'s parsed prose body instead of the whole file; independently reproduced the original vacuity on a temp-copy fabricated quote (old check: false-positive `True`; new check: correctly `False`), and confirmed the fix generalizes across both shipped literal edges with no per-edge special case.

   The verify-report's machine-readable `verdict:` field still literally reads `fail`, but the report itself explains this is a schema artifact: `gentle-ai sdd-verify-validate` refuses `pass`/`pass_with_warnings` whenever `build_exit_code` is non-zero, and this environment's `npm run typecheck` fails (`tsc: command not found`) for a pre-existing, unrelated reason (`W2`) — confirmed by a minimal isolated probe that flipped only `build_exit_code` 127→0 on an otherwise identical report and watched admission flip from denied to valid. `blockers: 0` and `critical_findings: 0` in the same envelope. This is the verify-report's own stated position, not an inference made at archive time.

**Resolution**: per the Final-State Authority hierarchy, the archive treats this change as closed/PASS — both findings the verify pass raised (C1 CRITICAL, W1 WARNING) are independently proven resolved, and no source (including the verify-report itself) claims either is still open. The stale-sounding machine `verdict: fail` is not echoed as a current blocking fact; it is attributed to its source (`verify-report.md`, W2, pre-existing environment gap) exactly as the report itself frames it. No CRITICAL issue blocks this archive.

**Still open, non-blocking, carried forward as follow-ups (not resolved by this archive, not blocking it):**
- **W2** — `npm run typecheck` fails in this environment (`tsc: command not found`). Pre-existing, environment-only, unrelated to any file this change touches.
- **S1** — a cosmetic task-count bookkeeping mismatch in an earlier revision of the `tasks` Engram note ("26/26" vs. the 23 actual numbered checkboxes in `tasks.md`). `tasks.md` itself never made the wrong claim; already corrected in the tasks observation's final revision (#1609).

## Specs Synced

Both capabilities are **new** — no prior main spec existed under `openspec/specs/` for either domain (which held only `deliberation-*` capabilities before this archive). Both delta specs ARE full specs; mechanically copied, never Read→Write, with an independent `diff -r` readback:

| Domain | Action | Requirements | Diff readback |
|---|---|---|---|
| `section-contract` | Created | 6 (Front Matter Schema, Closed Fact Vocabulary, Closed Declaration Vocabulary, Closed Citations Regime, Byte-Clean Header Insertion, Transcribed `after` Edges Only) | empty (byte-identical) |
| `writing-readiness` | Created | 4 (Per-Block Readiness, Derived Writing Order, Eleventh Contract Enters With No Code Change, A Fact Outside the Ten Refuses) | empty (byte-identical) |

```
$ diff -r openspec/changes/the-contract-is-data-not-code/specs/section-contract/spec.md openspec/specs/section-contract/spec.md
(no output, exit 0)

$ diff -r openspec/changes/the-contract-is-data-not-code/specs/writing-readiness/spec.md openspec/specs/writing-readiness/spec.md
(no output, exit 0)
```

### Left open for the two siblings that merge into `section-contract` next

`section-contract` is shared: the next two archives in sequence (`the-writer-may-assert-only-what-it-was-given`, then `a-diagram-that-compiles-or-says-why`) merge deltas into this same main spec. This copy is the sibling changes' full starting point, not a final shape:

- Written as a plain copy of this change's full spec, with no structure that assumes finality (no closed "this is every requirement this capability will ever have" framing).
- The **`mode` field and its closed mode vocabulary do not exist yet** in this spec. A later sibling adds them. This archive did not add, forecast, or foreclose that field — future archivists merging into `section-contract` should treat its absence here as expected, not a gap to backfill from this side.
- `block-substitution` is not owned by this change and was not touched (owned by `only-the-block-changes`, archived separately by a concurrent sibling in this same session).

## Archive Contents

- `proposal.md` ✅
- `specs/section-contract/spec.md` ✅
- `specs/writing-readiness/spec.md` ✅
- `design.md` ✅
- `tasks.md` ✅ (23/23 numbered tasks complete)
- `verify-report.md` ✅ (includes original pass + re-verification addendum, kept as history)

## Mechanical Copy / Move Evidence (MANDATORY)

Both operations used shell-only `cp`/`git mv`, never Read→Write, each followed by an independent `diff -r` readback. Both readbacks were empty (the only passing evidence):

```
=== spec sync: section-contract ===
(no output, exit 0)

=== spec sync: writing-readiness ===
(no output, exit 0)

=== archive folder move readback ===
(no output, exit 0)
```

## Load-Bearing Precedent for the Rest of the Build

Recorded here because a later archive in this same sequence depends on it and must not lose the thread:

**The transcription discipline for `after` edges is the load-bearing precedent of the whole build.** Every `after` edge carries `{value, source: {file, quote}}`, and the quote is checked against the named file's parsed prose body (never the whole file, never the header's own re-serialized JSON) after collapsing whitespace runs on both sides. This lock is **test-only** — it lives in `tests/test_paper_contract.py` and is never enforced at runtime by the reader itself. That is a real property of this design, not an oversight: the reader trusts the header at read time; only the test suite falsifies a fabricated quote. **A later change in this build copied this exact `{value, source}` shape for a new `mode` field without copying the test that made it honest, and shipped a false quote immediately** — direct evidence that the shape alone does not carry the discipline; the covering test must be copied with it, every time this shape is reused.

## Explicit Follow-Up Not Fixed By This Change

`paper_contract.install_header` has **zero production callers** anywhere in the repository. This was found late during this change's build, belongs to this change's own module, and was deliberately left in place with a docstring note rather than removed or wired up — recorded here explicitly so it does not silently vanish into the archive. A future change should either wire a caller to it or remove it; neither happened in this change.

## Rollback

`git revert` the archived change's commits (`b1d67dc`, `c26f21c`, `e602e9b`, `afb9077`, `0422dd1`) returns the ten `sections/*.md` contracts to headerless prose. No consumer breaks on revert — no other code in the repository reads `sections/` (verified repo-wide at design time and unchanged since).

## SDD Cycle Complete

This change has been fully planned, implemented, verified (with an independently re-checked corrective addendum), and archived. `openspec/specs/section-contract/spec.md` and `openspec/specs/writing-readiness/spec.md` are now source of truth. Ready for the next change in sequence to merge into `section-contract`.
