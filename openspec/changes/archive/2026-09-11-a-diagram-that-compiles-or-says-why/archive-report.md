# Archive Report: a-diagram-that-compiles-or-says-why

**Change**: `a-diagram-that-compiles-or-says-why` (paper-writing phase 7 — seventh and final archive of this build)
**Archived to**: `openspec/changes/archive/2026-09-11-a-diagram-that-compiles-or-says-why/`
**Artifact store**: hybrid (Engram + openspec filesystem)
**Verdict at close**: PASS WITH WARNINGS, 0 CRITICAL, archivable

## Observation IDs Read (traceability)

| Artifact | Engram ID | Topic key |
|---|---|---|
| proposal | #1615 | `sdd/a-diagram-that-compiles-or-says-why/proposal` |
| spec | #1621 | `sdd/a-diagram-that-compiles-or-says-why/spec` |
| design | #1627 | `sdd/a-diagram-that-compiles-or-says-why/design` |
| tasks | #1630 | `sdd/a-diagram-that-compiles-or-says-why/tasks` |
| tasks (apply session summary) | #1666 | manual |
| verify-report | #1671 | `sdd/a-diagram-that-compiles-or-says-why/verify-report` |

## Task Completion Gate

`openspec/changes/a-diagram-that-compiles-or-says-why/tasks.md` (pre-archive, on disk): 41/41 tasks checked, 0 unchecked (`rg -c '^\s*- \[ \]'` → no matches). All phases 0–7, including both correctives, are complete. No stale-checkbox reconciliation was needed.

## Specs Synced

| Domain | Action | Details |
|---|---|---|
| `section-contract` | Modified (third and final delta merge on this capability) | Merged this change's `figure` object (subkeys `ordered`, `excludes`, `caption_enumerates`, `caption_decodes`, `mandatory`, optional `components_from`) into the `Front Matter Schema` requirement, alongside the `mode` fields already merged by two prior archives. Requirement count unchanged (8); scenario count 16→19 (+3 `figure`-object scenarios). |
| `authored-diagram` | Created (new capability, mechanical copy, `diff -r` empty) | 8 requirements, 12 scenarios. |
| `diagram-obligation` | Created (new capability, mechanical copy, `diff -r` empty) | 7 requirements, 11 scenarios. |

**Independent drift check** (requested by the launch prompt): sum of this change's own capability requirement/scenario counts — `authored-diagram` (8/12) + `diagram-obligation` (7/11) + `section-contract` delta's own contribution (1 requirement, 5 scenarios) = **16 requirements / 28 scenarios**, matching the verify-report's `requirements: 16/16` and `scenarios: 28/28` exactly. No drift between verify and archive.

### `diff -r` readback (mandatory, verbatim)

New-capability mechanical copies, source vs. destination in `openspec/specs/`:
```
$ diff -r openspec/changes/.../specs/authored-diagram/spec.md openspec/specs/authored-diagram/spec.md
(no output, exit 0)
$ diff -r openspec/changes/.../specs/diagram-obligation/spec.md openspec/specs/diagram-obligation/spec.md
(no output, exit 0)
```

Archive folder move, pre-move recursive snapshot vs. archived tree (archive-report.md excluded, additive, written after this comparison):
```
$ diff -r "$snapshot_root/source" "openspec/changes/archive/2026-09-11-a-diagram-that-compiles-or-says-why"
(no output, exit 0)
```

`section-contract` was a text-merged delta (per skill: structural verification, not `diff -r`), verified by requirement count (8, unchanged), scenario count (19, +3), and tail readback of the merged file — all confirmed above.

## Final-State Authority — resolving what the newest verify section left open

The verify-report at `openspec/changes/archive/.../verify-report.md` is layered, prepended newest-first. Its final (newest) section is the scoped re-verification of the second corrective (`9ad7d43`/`8817103`), verdict `pass_with_warnings`, `16/16` requirements, `28/28` scenarios, `0` CRITICAL, `1` WARNING at time of writing:

> **Learned #1** (verify-report, 2026-09-11 08:34:33): `_derive_figure_holders` returns `dict[str, str]` (filename → a single block id), so a file that later grows a second figure-declaring block would silently drop the first block's entry from the derived holder set. Confirmed latent (not live — all three real section files carried exactly one figure-declaring block each at verify time), fix shape named as `dict[str, list[str]]`.

**This WARNING is closed, not open, at archive time.** Per the launch prompt's explicit final-state fact and confirmed independently against the tracked repository: commit `bf691a6` (`fix(paper-writing): stop figure-holder derivation from collapsing on repeated files`), which landed in `git log` after the verify-report was written and after tasks.md's Phase 7 bookkeeping commit `8817103`, changes `_derive_figure_holders` to return a list of `(filename, block_id)` pairs instead of a collapsing dict, with a red-first regression test proving nothing is lost when a second figure-declaring block is added to a file. This archive report records the WARNING as **closed by `bf691a6`**, not as a carried-forward open item — echoing it forward as still-open would misstate final state per the Final-State Authority hierarchy (explicit final-state facts in the launch prompt, corroborated by repository evidence, outrank an intermediate verify snapshot's "latent" claim).

No other open items remain. `typecheck`/build claims in older layers of this same verify-report (superseded by the newest section) are not carried forward.

## Native Review Receipt Gate

No `reviewGate` was present in structured status for this candidate (kill switch off / no review discovered) — archive proceeds under ordinary repository policy. No `sdd/{change-name}/review/*` topics exist to read.

## Test Evidence at Close

Per `tasks.md` Phase 7 summary and the verify-report's re-executed combined run: `npm test` 559/559; Python full discovery (`unittest discover -s tests -p 'test_*.py'`) 3230 tests, `OK (skipped=6)`, exit 0 (the verify-report's own literal combined-command re-run, background execution, confirmed clean after ruling out two stray `F` characters as an unrelated `nbformat` deprecation string substring, not failures); `npm run typecheck` exit 0, no output. Not re-run by this archive phase per instruction (green at HEAD).

## The Defect Story This Change Leaves Behind

This change's build history is this project's clearest record of a defect that repaired itself into a worse shape before landing correctly, across three attempts:

1. **The CRITICAL** (original verify FAIL): `components_from` — the field naming which declared fact a diagram's boxes must equal — was read by no code path in any section. An empty diagram passed with the flag omitted.
2. **First corrective attempt (reverted in full)**: rewrote a docstring to call the hole "intended design," moved the burden onto the operator, and added three tests that constructed both sides of the equality themselves — tests that would have passed even if the field read `"banana"`, one of which asserted the inversion as a permanent target state.
3. **The real fix** (`653e0cf`): derives the expected component list from the named fact's own declaration rather than accepting it as free-form input. Mutation-proven — flipping `"contributions"` → `"dataset"` in section 01's real header flips the verdict.
4. **Making `components_from` optional reopened the same defect by omission** — no live instance, but no guard against a future one either. Closed by `9ad7d43` with a derived guard (`_derive_figure_holders`).
5. **The derived guard inherited its own version of the same illness**: it returned a filename-keyed dict assigned inside a loop over blocks, so a second figure-declaring block in one file would silently overwrite the first — a derivation reopening, through a data-structure choice, the exact defect class it was built to close. Latent, never live. Closed by `bf691a6`, list-of-pairs return type, red-first regression test.

`sections/02-experimental-setup.md` lost its `components_from` deliberately: its closing diagram is a composite crossing over several content categories that no single declared fact can equal — this was a contract-shape decision, not a regression. Its prose body was verified byte-identical across the change; only JSON front matter moved.

This change also introduced a real operator workflow requirement: rendering section 01's methods diagram now requires that its named fact be declared as a JSON list first — the diagram cannot be rendered ahead of its own source of truth.

## Build Closure (all seven changes)

This is the seventh and final archive of the paper-writing build:

| # | Change | Archived commit(s) |
|---|---|---|
| 1 | `only-the-block-changes` | `337de69` |
| 2 | `the-contract-is-data-not-code` | `ba59360` |
| 3 | `no-claim-without-a-source-that-holds-it` | `a07b0fb` / `d042cd9` |
| 4 | `the-paper-carries-its-own-decisions` | `0279e89` / `7ed7800` |
| 5 | `the-couplings-hold-or-they-do-not` | `0fdb866` |
| 6 | `the-writer-may-assert-only-what-it-was-given` | `bc94e36` / `b91002f` |
| 7 | `a-diagram-that-compiles-or-says-why` | this archive |

All eight `openspec/specs/` capabilities this build touched are now on main: `block-substitution`, `paper-scaffold`, `section-contract` (three cumulative deltas across changes 2, 6, and this one), `citation-placement`, `citation-validation`, `evidence-set`, `literature-search`, `sourced-bibliography`, `contract-audit`, `evidence-bound-drafting`, `style-channel`, `style-leak-detection`, `writing-orchestration`, `authored-diagram` (new), `diagram-obligation` (new). The `paper-writing` skill now has a complete pipeline: scaffold → contract → sourced drafting → style enforcement → coupling verification → evidence-bound assertion → diagram authoring with a bounded compile-and-repair loop, each stage refusing loudly rather than silently passing on missing input.

## Risks / Open Items Carried Forward

None from this change. The one WARNING this change's verify-report ever raised (`_derive_figure_holders` holder collapse) is confirmed closed by `bf691a6` per the section above.

## SDD Cycle Complete

`a-diagram-that-compiles-or-says-why` has been fully planned, implemented, verified, and archived. This closes the eight-phase paper-writing build. Ready for the next change.
