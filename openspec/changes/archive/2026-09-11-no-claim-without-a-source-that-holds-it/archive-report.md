# Archive Report: no-claim-without-a-source-that-holds-it

**Archived**: 2026-09-11
**Project**: papersmith-ai
**Mode**: hybrid (Engram + filesystem)

## Summary

The evidence channel that kills the invented citation. Ships as ONE change in
THREE sequential work-unit commits (`cc863ab` WU1 evidence channel,
`8ed7c7e` WU2 sourced bibliography, `a5b5484` WU3 citation validation/
placement, plus `0ea0e7c` a small self-audit fix), with a corrective test
commit (`97baecc`) closing 3 CRITICAL findings raised by the first verify
pass, and a scoped re-verification confirming the fix by independent
mutation testing.

Five new capabilities, all creates (no prior spec existed for any):
`citation-placement`, `citation-validation`, `evidence-set`,
`literature-search`, `sourced-bibliography`. No overlap with any sibling
change archived in this batch.

## Observation IDs Read (traceability)

| Artifact | Observation ID | Notes |
|---|---|---|
| proposal | #1617 | COMPLETE, all 5 open questions answered |
| spec | #1624 | 5 domains, full specs not deltas |
| design | #1628 | 7 decisions, 2 findings not in proposal |
| tasks | #1629 | 33/33 tasks complete, filesystem authoritative |
| verify-report (first pass) | referenced inside #1661 as prior pass | FAIL → 3 CRITICAL |
| verify-report (re-verification) | #1661 | PASS, 0 CRITICAL |

## Final-State Authority Applied

Per the Final-State Authority hierarchy, this report reflects state AT CLOSE,
not the state of the first (intermediate) verify pass:

- The **first verify pass** (prose only, embedded as history inside the
  `verify-report.md` file, not a separate top-ranked observation) found 3
  CRITICAL/UNTESTED findings in the `literature-search` domain: "Discovery
  issues an open search", "Discovery candidate reaches resolution",
  "Consensus cannot supply a verdict" — true by static inspection only, no
  named executing test.
- Corrective commit `97baecc` (test-only, `tests/test_paper_evidence.py` +
  `tasks.md` Phase 6, zero production diff) added
  `LiteratureSearchAbsenceTests` (3 tests) closing exactly the gap the first
  pass itself proposed as the fix.
- The **re-verification** (#1661, the authoritative, most-recent verify
  artifact) independently re-ran all three mutations from scratch — not
  trusting the corrective's own commit message — and confirmed all three
  tests fail exactly as expected when the guarded absence is violated, then
  pass again after revert. Verdict: **PASS, 0 CRITICAL**.
- This report states the re-verification's PASS as the current, final fact.
  It does NOT carry forward the first pass's "3 CRITICAL" as a currently-open
  claim — that claim was true only at the time it was written and was
  resolved by `97baecc`, confirmed independently at archive time.

### Carried-forward, still-open findings (not dissolved into the archive)

These remain open at archive time and are recorded explicitly rather than
allowed to disappear:

1. **WARNING** (unchanged, disclosed, out of scope): `classify_guidance_child`
   has no production caller — deliberate per `design.md` Decision 6; the
   registry that consumes it belongs to a later change
   (`the-paper-carries-its-own-decisions`).
2. **SUGGESTION** (carried): metadata-cache hand-edit guard gap.
3. **SUGGESTION** (carried): `check_citations.py` false positive on
   `tasks.md`.
4. **SUGGESTION** (new in re-verification, non-blocking): of the three
   `LiteratureSearchAbsenceTests`, two genuinely derive their surface from
   the live filesystem/module and were **empirically confirmed** already
   generalizing — `test_no_skill_script_references_an_mcp_config` (iterates
   `SKILL_SCRIPTS.glob("*.py")`) and
   `test_no_free_text_query_construction_function_exists` (iterates
   `inspect.getmembers(paper_resolve, inspect.isfunction)`) already swept
   two brand-new sibling modules (`paper_coupling_evidence.py`,
   `paper_verify.py`) that did not exist when the tests were written, with
   zero test-file edits required. The third,
   `test_consensus_is_not_a_resolver`, hand-names exactly three attributes
   (`RESOLVERS`, `ROLES`, `_ENDPOINT_BUILDERS`) — verified via a `vars()`
   scan of the module to be a **complete enumeration of the module's current
   resolver surface today, but by coincidence of the module's current shape,
   not by construction**. It is correct today and mutation-proven correct
   today; it would not automatically be swept by a future refactor that
   moved the resolver surface into a fourth container or a class-based
   registry. Filed as a non-blocking SUGGESTION at re-verification time and,
   as far as this archive is aware, still stands — carried forward here
   explicitly rather than left to dissolve. Recommended fix (from the
   re-verification report): derive it, e.g. scan `vars(paper_resolve)` for
   any top-level tuple/list/dict/set whose values contain the substring
   `"consensus"`, in a future hardening pass.

## Native Review Receipt Gate

`reviewGate` is structurally absent for this candidate — no review artifacts
(`sdd/{change-name}/review/*`) exist for this change, and none were searched
for beyond confirming their absence. Archive proceeds under ordinary
repository policy per the gate's default branch (kill switch off / no review
ever started for this candidate).

## Task Completion Gate

Filesystem `tasks.md` (pre-move) verified with `rg -c '^\s*- \[ \]'`: **0
unchecked tasks**. 33/33 tasks complete across 5 phases / 3 work-unit
commits. No stale-checkbox reconciliation was needed or performed.

## Architectural Decisions Carried Forward

1. **MCP fork, settled**: discovery runs through the agent's MCP (a
   hallucinated candidate is acceptable there because resolution re-checks
   it); resolution and metadata run through the CLI over stdlib `urllib`,
   keyless, against OpenAlex/Crossref/arXiv only. The tool that fetched the
   resolved metadata bytes is the same tool that writes the `refs.bib`
   entry — no component synthesizes an entry from data it did not itself
   fetch.
2. **Consensus deliberately excluded from the verdict path.** A connector
   answering "does the literature support X" would make the verdict an
   external opinion instead of a check against text this codebase ingested
   and can quote. This reasoning generalizes to any future connector
   proposed for that path — recorded so it is not re-litigated per
   connector.
3. **`insufficient` is never a soft `holds`** — it fails the citation and
   consumes a search-round iteration exactly like `does-not-hold`,
   structurally (via `Verdict`'s constructor shape), not by a later
   validator judgment call.
4. **Placement dispatches on regime as a table**, never one universal rule:
   `discovery` → end of sentence; `resolution` → attached to the object it
   credits, wherever it sits; `none` → no rule. The noun-phrase prohibition
   is `discovery`-only.

## Specs Synced

| Domain | Action | Details |
|--------|--------|---------|
| citation-placement | Created | full spec (delta = full spec, no prior main spec existed) |
| citation-validation | Created | full spec |
| evidence-set | Created | full spec |
| literature-search | Created | full spec |
| sourced-bibliography | Created | full spec |

All five copied mechanically via `cp` + `mktemp` + `mv` (shell only, never
Read→Write). Verbatim `diff -r` readback for each (source vs. destination),
run individually:

```
--- citation-placement ---
exit: 0
--- citation-validation ---
exit: 0
--- evidence-set ---
exit: 0
--- literature-search ---
exit: 0
--- sourced-bibliography ---
exit: 0
```

All five diffs empty — byte-identical copies confirmed.

## Archive Move

`git mv openspec/changes/no-claim-without-a-source-that-holds-it
openspec/changes/archive/2026-09-11-no-claim-without-a-source-that-holds-it`
— succeeded via `git mv` (tracked since `20b3e0c`).

Verbatim `diff -r` readback (pre-move recursive snapshot vs. archived
folder, this file excluded as additive):

```
diff exit: 0
```

Empty — byte-identical move confirmed. Source directory
`openspec/changes/no-claim-without-a-source-that-holds-it` confirmed absent
after the move.

## Archive Contents

- proposal.md ✅
- specs/{citation-placement,citation-validation,evidence-set,
  literature-search,sourced-bibliography}/spec.md ✅ (5 domains)
- design.md ✅
- tasks.md ✅ (33/33 tasks complete)
- verify-report.md ✅ (2 sections: first pass FAIL→3 CRITICAL, then
  re-verification PASS→0 CRITICAL, history preserved not replaced)

## Source of Truth Updated

The following specs now reflect the new behavior:
- `openspec/specs/citation-placement/spec.md`
- `openspec/specs/citation-validation/spec.md`
- `openspec/specs/evidence-set/spec.md`
- `openspec/specs/literature-search/spec.md`
- `openspec/specs/sourced-bibliography/spec.md`

## SDD Cycle Complete

The change has been fully planned, implemented, verified (including a
scoped re-verification closing all 3 CRITICAL findings by independent
mutation testing), and archived. One WARNING and 3 SUGGESTIONs remain open
and are carried forward above rather than dissolved. Ready for the next
change.
