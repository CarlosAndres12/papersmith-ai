# Tasks: Only the Block Changes

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1600-2000 (SKILL.md ~200, paper_cli.py ~250, paper_block.py ~350, paper_scaffold.py ~100, .gitignore +2, paper/.gitkeep 0, tests/test_paper_writing.py ~700-1000) |
| Review budget (project override) | 1400 lines (`review_budget_lines`, not the skill's generic 400 default) |
| 1400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR1 scaffold → PR2 block core → PR3 CLI wiring + mutation + roster |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending — user must choose stacked-to-main vs feature-branch-chain |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High (also High against this project's 1400-line override)

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | `paper-scaffold`: create/re-enter `paper/` idempotently | PR 1 | `.venv/bin/python -m unittest tests.test_paper_writing.ScaffoldTests -v` | N/A — filesystem-only, no live service | `git rm -r .claude/skills/paper-writing/scripts/paper_scaffold.py`; `paper/` untouched |
| 2 | Marker grammar, binary I/O, CRLF fixture, substitution algorithm + invariant, hand-edit/`--adopt`, pre-image | PR 2 | `.venv/bin/python -m unittest tests.test_paper_writing.BlockCoreTests tests.test_paper_writing.CRLFTests tests.test_paper_writing.InvariantTests -v` | N/A — no LaTeX toolchain needed to test (proposal `Dependencies`) | `git rm .claude/skills/paper-writing/scripts/paper_block.py`; PR1 stands alone |
| 3 | CLI wiring (`open`/`status`/`substitute`), mutation proof (M1-M3), refusal roster, SKILL.md | PR 3 | `.venv/bin/python -m unittest discover -s tests -p 'test_paper_writing*.py'` | N/A — mutation harness runs its own subprocess against a temp copy, not a live service | `git rm -r .claude/skills/paper-writing`; PR1/PR2 stand alone |

Units 1 and 2 touch disjoint files and can be built in parallel; Unit 3 depends on Unit 2's `paper_block.py` API and runs sequentially after it.

**Units 1 and 2: done.** Commits `325806a` (Unit 1 — scaffold) and `36144c5` (Unit 2 —
block core) on `paper-writing`. Focused commands green (7 tests for Unit 1, 25
including Unit 1's for Unit 2). Full `npm test && .venv/bin/python -m unittest
discover -s tests -p 'test_*.py'` run clean after both commits: 559/559 Node tests,
2807/2807 Python tests (skipped=6, pre-existing and unrelated), no regressions.
Unit 3 (CLI wiring for `open`/`status`/`substitute`, mutation proof M1-M3, refusal
roster, `SKILL.md`) is a separate, later work unit — not started here.

## Phase 1: Scaffold (`paper-scaffold` spec)

- [x] 1.1 RED: `ScaffoldTests` — first run creates `main.tex`/`refs.bib`/`Figures/`/`.gitkeep`; second run byte-identical after hand-edit; `paper/` as a file refuses `PAPER_NOT_A_DIRECTORY`; `Figures` as a file refuses `SCAFFOLD_ENTRY_WRONG_TYPE`; `--paper ../elsewhere` refuses `PAPER_OUTSIDE_REPOSITORY`
- [x] 1.2 GREEN: `paper_scaffold.py` — idempotent create, path-arithmetic root resolution, wrong-type refusals. **Deviation from design.md**: design's text names `parents[3]`; measured against this file's actual depth (`<root>/.claude/skills/paper-writing/scripts/paper_scaffold.py`, 5 path components — the same depth as `_core/implementation/impl_layout.py`'s own `FORGE_ROOT`), the correct index is `parents[4]`. Implemented as `parents[4]`, proven by `test_paper_outside_repository_refuses` and `test_cli_scaffold_verb_runs_and_emits_json` (the latter resolves against the real repo root via a subprocess, not an injected one)
- [x] 1.3 Add `.gitignore` entries `paper/*` / `!paper/.gitkeep`; create tracked `paper/.gitkeep`
- [x] 1.4 Wire `scaffold` verb in `paper_cli.py`: JSON envelope, exit 0/2

## Phase 2: Marker grammar, binary I/O, CRLF fixture

- [x] 2.1 RED: well-formed pair parses via `status`; malformed marker line (no `sha256=`) refuses `MARKER_MALFORMED` naming the line; duplicated id refuses `BLOCK_DUPLICATED`; unpaired begin refuses `BLOCK_UNPAIRED`; nested begin refuses `BLOCK_NESTED`
- [x] 2.2 GREEN: `paper_block.py` scan/pair/order; region start = begin-marker line's first byte, end = end-marker line's terminator; preceding newline excluded
- [x] 2.3 RED — CRLF fixture (first-class, built as explicit `b"...\r\n..."` in code, never committed): mid-paragraph CRLF block round-trips untouched; a text-mode open of the same fixture must fail this test
- [x] 2.4 GREEN: binary I/O end-to-end in `paper_block.py` — no text-mode open anywhere. (`paper_cli.py`'s own binary I/O applies once `open`/`status`/`substitute` are wired to it in the CLI-wiring work unit; this unit's CLI surface is `scaffold` only, which writes no `main.tex` content.)

## Phase 3: Substitution algorithm and invariant

- [x] 3.1 RED: `substitute` on an absent block refuses `BLOCK_ABSENT` and creates nothing; body containing a marker-prefixed line refuses `CONTENT_CARRIES_MARKER`
- [x] 3.2 RED: hand-edited body refuses `BLOCK_HAND_EDITED` naming expected+found digest; `--adopt` updates digest without touching body; `--adopt` on a matching digest refuses `NOTHING_TO_ADOPT`
- [x] 3.3 RED — identity invariant, three conjuncts so a no-op write cannot pass trivially: `project(pre) == project(post)` AND `post != pre` AND substituted block's body equals the new body; `project()` re-parses from scratch (independent of `prefix+new+suffix`)
- [x] 3.4 GREEN: implement the 9-step algorithm (resolve → read+digest → scan/pair → hand-edit check → marker-in-body check → build candidate → in-memory invariant → CAS re-read (`TEX_MOVED`) → pre-image then atomic same-dir temp + `os.replace`)
- [x] 3.5 RED+GREEN: `SUBSTITUTION_NOT_LOCAL` when the in-memory invariant fails; write is refused before touching disk

## Phase 4: One-deep pre-image (recovery boundary)

- [x] 4.1 RED: after one substitution, `paper/.paper-writing/main.tex.prev` holds exactly the pre-write bytes
- [x] 4.2 RED: after two successive substitutions, the pre-image holds only the state immediately before the second; the state before the first is unrecoverable through this mechanism or git (untracked `main.tex`) — proves the one-deep limit, not just names it
- [x] 4.3 GREEN: pre-image write ordered before `os.replace`; a crash between the two leaves pre-image == `main.tex` (harmless)

## Phase 5: `open`/`status` CLI verbs

- [ ] 5.1 RED: `open b --after a` inserts empty pair after `a`'s end marker, bytes before insertion unchanged; `open` on existing id refuses `BLOCK_DUPLICATED`; `--after missing` refuses `ANCHOR_ABSENT`; no position flag refuses `OPEN_POSITION_REQUIRED`; both flags refuses `OPEN_POSITION_CONFLICT`
- [ ] 5.2 GREEN: `open` in `paper_block.py` + `paper_cli.py` wiring
- [ ] 5.3 RED: `status` lists ids/digest/region without writing; reports `adjacency:{before,after}` and `handEdited:[ids]`
- [ ] 5.4 GREEN: `status` implementation; every successful `substitute` emits `"rendering": "unproven"`

## Phase 6: Mutation proof (executed, not asserted)

- [ ] 6.1 Build mutation harness: copies engine to temp dir, patches source, asserts the anchor matched exactly once and bytes changed, unique module name, purges `__pycache__`, runs named test in subprocess, asserts non-zero exit
- [ ] 6.2 M1 — region start shifted one byte earlier: run harness, confirm the byte-identity test goes red
- [ ] 6.3 M2 — text-mode open against the CRLF fixture: run harness, confirm the byte-identity test goes red
- [ ] 6.4 M3 — digest comparison skipped: run harness, confirm the `BLOCK_HAND_EDITED` test goes red

## Phase 7: Refusal roster, vocabulary guard, SKILL.md

- [ ] 7.1 Implement roster derivation from `paper_cli.py` source (shape of `reachable_refusal_codes`, never hand-listed); classify every code invocation-defect vs work-state
- [ ] 7.2 RED+GREEN: roster test — every refusal in the spec table plus design's added codes (`BLOCK_ID_MALFORMED`, `OPEN_POSITION_REQUIRED`/`_CONFLICT`, `BLOCK_EXISTS`, `NOTHING_TO_ADOPT`, `TEX_MOVED`, `SUBSTITUTION_NOT_LOCAL`) is reachable and classified
- [ ] 7.3 Run `tests/forge_vocabulary.py` scan against the new SKILL.md and scripts — no target-word leakage
- [ ] 7.4 Write `.claude/skills/paper-writing/SKILL.md`, sibling idiom; confirm `tests/test_suite_collects.py` picks up the new modules (stdlib-only)
