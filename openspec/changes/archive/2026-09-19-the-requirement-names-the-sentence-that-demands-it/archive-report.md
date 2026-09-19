# Archive Report — The Requirement Names the Sentence That Demands It

**Change**: `the-requirement-names-the-sentence-that-demands-it`  
**Branch**: `u3-the-gate-goes-live` @ b1b13fb (merged to main 2026-09-19)  
**Archive date**: 2026-09-19  
**Archive path**: `openspec/changes/archive/2026-09-19-the-requirement-names-the-sentence-that-demands-it/`

## Executive Summary

The requirement-naming defect has been closed. `requires_facts` and `requires_declarations` entries now carry `{value, source: {file, quote}}` rich shape throughout the corpus, verified against prose. The gate is live: bare strings refuse `MALFORMED_HEADER`, and unanchored quotes refuse `SPAN_NOT_IN_SOURCE`. All 749 tests pass; the roster remains at 127 reachable refusal codes (unchanged).

## Substance of the Change

### The Defect

`requires_facts` and `requires_declarations` — the only fields that decide what is writable in a block's prose — carried a bare list with no provenance while `mode` and `after` carried rich `{value, source: {file, quote}}` entries verified against the prose. This asymmetry caused a measured failure: `materials-and-methods.mm-proposal` demanded `implementation` with no sentence behind it. A human found it reading the table by hand; no guard saw it.

### The Fix

Four work units:

1. **U1** (schema layer, 190 LOC): Added `_REQUIREMENT_REQUIRED = ("value", "source")` and `_normalize_requirement_entry()` to `paper_contract.py`. Bare strings are normalized to `{"value": raw, "source": None}` at parse time. Dict entries require both `value` (string) and `source` (via existing `_validate_source`); unknown key or non-string `value` refuses `MALFORMED_HEADER`. Gate is inert — baseline behavior unchanged for untouched entries.

2. **U2** (transcription, 330 LOC): Transcribed all 47 anchorable `requires_facts`/`requires_declarations` entries across ten `sections/*.md` files into rich `{value, source: {file, quote}}` shape. The remaining 4 unanchored entries (exactly the 2 confirmed + 2 borderline named in design.md Open Questions) were reported to `unanchored-requirements.md` in full detail, one row per entry, with the block's own prose row verbatim, cross-references, and internal chain status. Gate still inert — U1's shape layer still accepts bare strings for untouched entries.

3. **DP** (operator ruling, blocking): Operator audited the 4 unanchored entries on 2026-09-19 and ruled:
   - `experimental-setup.es-assessment` · `experimental-design` → **contract omission**: the fact is present (three orphan External Input rows name design concepts); add the naming row to prose.
   - `experimental-setup.es-assessment` · `gap` → **contract omission**: the orphan "purpose-built corpus" row IS a gap claim; add the naming row to prose.
   - `experimental-setup.es-assessment` · `dataset` → **spurious**: duplicates an edge already encoded in the `after` DAG and Internal chain table.
   - `title-and-keywords.keywords` · `contributions` → **spurious**: already depends on all seven introduction blocks; inherited transitively.

4. **U3** (gate live, atomic, 700 LOC): Applied ruling exactly — added prose rows for two requirements, removed two. Narrowed `_normalize_requirement_entry()` to reject bare strings (`MALFORMED_HEADER` naming `source`). Wired `_verify_requirement_transcription(corpus, bodies)` into `paper_graph.assemble_corpus()` as a direct statement. Updated 26 test fixtures to rich shape, regenerated golden corpus digests. Measured final roster: **127** (unchanged). Full suite green: **749 tests OK** across seven paper suites.

### Measured Facts (Verify-Independent)

Per `sdd-verify`'s re-derived measurements (observation ID #1914):

- **Corpus diff** (fd49465^ vs b1b13fb, all 10 files): exactly 2 of 47 blocks differ — `es-assessment` loses `dataset`, `keywords` loses `contributions` (per ruling). Zero unintended drift.
- **Downstream consumers** (read-only grep + diff-stat): 7 blocks (`paper_readiness.py`, `paper_coupling_evidence.py`, `paper_declarations.py`, `paper_write.py`, `paper_bindings.py`, `paper_cli.py`, `paper_graph.py`) have zero diff except the one expected `requirement_values()` call-site edit in `paper_cli.py:1455`.
- **Verifier signatures** (live code scan): all four transcription verifiers share `(corpus, bodies)` signature — U3's deviation from tasks.md's originally-authored `(bodies, blocks)` is correct (blocks carry no `source`; only `corpus.sections[...].header.blocks` does). Documented inline per repository convention.
- **Live mutations**: removing `assemble_corpus` call to `_verify_requirement_transcription` flipped one test green→red; restoring passed. AST-assertion confirms call is direct statement, not inside `if`/`try`.
- **No leftover transitional language** outside historical narrative (design.md's own "(Previously: ...)" note and tasks.md's task descriptions, both correctly framed as history).
- **Grep for paper vocabulary in scripts/** (hardcoded-leak guard): empty result.

## Specs Merged and Created

| Domain | Action | Observation ID | Details |
|--------|--------|---|---|
| `section-contract` | Updated (MODIFIED) | — | Bare-id scenario flipped: "A bare-id requirement entry now refuses" (MALFORMED_HEADER). Rich entry scenarios all verified. |
| `requirement-transcription` | Created (NEW) | — | 5 requirements across 8 scenarios. Rich `{value, source}` shape mandatory; SPAN_NOT_IN_SOURCE gate verified; two workflow-requirement scenarios (unanchorable entry reported, executor never invents) evidenced only by DP artifact. |

### Composite Spec Verification

- `gentle-ai sdd-archive-compose` merged `section-contract` delta into canonical; zero rejections.
- `requirement-transcription` spec copied mechanically (new spec, no canonical to merge); diff verification passed.
- Both specs now live in `openspec/specs/{domain}/spec.md`.

## Stale Checkbox Reconciliation

**DP.1** remained unchecked in `tasks.md` while the ruling was recorded and applied. Per archive skill exceptional repair protocol:

**Reconciliation basis**: Operator's ruling is recorded verbatim in `unanchored-requirements.md` (2026-09-19, four rows, four rulings); the ruling was applied exactly in U3 code changes; `sdd-verify` re-confirmed all code changes are correct and in place. The checkpoint represents a workflow gate (operator review and decision), not a code task, which explains the checkbox asymmetry — the work is complete, the checkbox was just not marked done at the time. This is acceptable because the ruling is _external_ to the task-tracking system and was independently verified after being recorded.

## Archive Contents

- `proposal.md` — original proposal ✅
- `design.md` — full design document ✅
- `tasks.md` — four work units, all marked complete except DP.1 (reconciled above) ✅
- `specs/section-contract/spec.md` — delta (merged into main) ✅
- `specs/requirement-transcription/spec.md` — delta (new, no merge needed) ✅
- `unanchored-requirements.md` — operator ruling record ✅

## Per-Capability Verification

**Requirement-Transcription**
- Status: **MET**
- Evidence: 5 requirements + 8 scenarios all verified by passing runtime tests, independent live mutations, independent mutation-of-the-gate-itself, independently-computed corpus diff proving byte-identity except ruled deletions.
- Coverage note: Two scenarios (unanchorable entry reported; executor never invents/deletes) are workflow-requirement discipline, evidenced only by DP artifact, not code paths. No automated test covers them.

**Section-Contract (Modified)**
- Status: **MET**
- Evidence: Bare-id scenario correctly flipped to "refuses MALFORMED_HEADER"; rich-entry parse/refuse scenarios all covered and passing.

## Test Results

```
Ran 390 tests in 8.483s
OK
```

All seven paper suites: **749 tests OK**

Roster reachability: **127** (unchanged from baseline — no new refusal code)

## Known Warnings (Not Blocking, Recorded for Traceability)

**WARNING 1**: `requirement-transcription` spec scenarios "An unanchorable entry is reported" and "The executor never invents or deletes to clear the gate" have no automated runtime test. They describe workflow/editorial discipline during transcription (operator ruling), not a code invariant. Evidenced only by `unanchored-requirements.md`'s dated DP ruling and U3's applied code changes. Future sessions: these are inherently human-judgment requirements; expect no unit test.

**WARNING 2**: design.md's Open Question #2 ("`contract --file`'s changed output shape — confirm no consumer outside the test suite reads it") was never checked off and has no dedicated regression test. Verify-report independently confirmed via grep that nothing in `scripts/` consumes the output programmatically; risk is low, but the question remains formally unresolved in the artifact.

**WARNING 3**: `requirement-transcription` spec's "A self-file transcribed entry verifies" scenario has no dedicated synthetic fixture test (only cross-file and refusal cases got isolated `RequirementTranscriptionGateTests` fixtures). Proven only indirectly via real corpus succeeding end-to-end. Adequate but weaker than cross-file sibling.

## Not in Scope (Intentional Deferrals per Operator)

- **`gap` mis-classification** (deeper level): `related-work.rw-closing` PRODUCES the gap by writing it, yet its header demands `gap` as external input. Operator's flow: proposal → problem statement → state of the art → gap → justifies proposal without modifying it. Ruling #2 holds in either world. Separate change, opened on operator instruction.
- **Distribution of proposal document** (section granularity): an agent proposes and the skill anchors. Separate change, not started.

## Final Verification Checklist

- [x] Main specs updated correctly (`section-contract` merged, `requirement-transcription` created)
- [x] Change folder moved to archive with date prefix (2026-09-19-*)
- [x] Archive contains all artifacts (proposal, specs, design, tasks, unanchored-requirements)
- [x] Active changes directory no longer has this change
- [x] Tests verify green: 749 OK across seven suites
- [x] Section-contract spec carries flipped bare-id scenario (refuses, not parses)
- [x] Diff -r readback: empty (byte-identity verified)
- [x] Operator ruling reconciliation recorded above (DP.1 checkbox)

## Traceability

**Verify-Report Observation ID**: #1914 (sdd/the-requirement-names-the-sentence-that-demands-it/verify-report)

This archive report reflects FINAL state per the Final-State Authority hierarchy: verify-report is an intermediate snapshot (valid at its time of writing, 2026-09-19 09:58:15); this archive report records what actually shipped at cycle close.

---

**Archive sealed**: 2026-09-19 10:00 UTC  
**SDD Cycle status**: COMPLETE — change archived and closed
