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

**Units 1, 2 and 3: done.** Commits `325806a` (Unit 1 — scaffold), `36144c5`
(Unit 2 — block core) and the Unit 3 commit below, on `paper-writing`. Focused
commands green throughout (7 tests for Unit 1, 25 including Unit 1's for Unit
2, 50 including both for Unit 3). Full `npm test && .venv/bin/python -m
unittest discover -s tests -p 'test_*.py'` run clean after all three commits:
559/559 Node tests, 2832/2832 Python tests (skipped=6, pre-existing and
unrelated), no regressions.

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

- [x] 5.1 RED: `open b --after a` inserts empty pair after `a`'s end marker, bytes before insertion unchanged; `open` on existing id refuses `BLOCK_DUPLICATED`; `--after missing` refuses `ANCHOR_ABSENT`; no position flag refuses `OPEN_POSITION_REQUIRED`; both flags refuses `OPEN_POSITION_CONFLICT`
- [x] 5.2 GREEN: `open` in `paper_block.py` (`build_open_candidate` + `open_block`, reusing the shared `identity_invariant`/pre-image/atomic-replace machinery as-is) + `paper_cli.py` wiring
- [x] 5.3 RED: `status` lists ids/digest/region without writing
- [x] 5.4 GREEN: `status` implementation; every successful `substitute` emits `"rendering": "unproven"` (already true since Unit 2)

  **Deviations from tasks.md's own wording, recorded rather than silently applied:**
  - The operator's explicit apply-scope instruction for this run states
    `paper_block.status()` "already exists as a pure engine function. Wire
    it into the CLI; do not reimplement it." Task 5.3's `adjacency:{before,
    after}` and `handEdited:[ids]` enrichment (design.md's own "Answering
    the three known risks" table, never promoted into `specs/block-
    substitution/spec.md`'s own `status` Requirement, which asks only for
    id/digest/region) would be a reimplementation of `status()`, not a
    wiring of it. Left unbuilt this run; `read_status(paper_dir)` is the
    thin disk-reading wrapper Unit 3 adds, calling the unchanged `status()`.
  - `OPEN_POSITION_REQUIRED`/`_CONFLICT` (named here) and design.md's own
    CLI-first-slice prose ("each an argparse
    `add_mutually_exclusive_group(required=True)`") disagree: a native
    argparse group answers with a bare usage error on stderr, never the
    JSON envelope this design's own opening paragraph makes invariant
    ("one JSON object on stdout ... exit 0/2"), and would be invisible to
    the roster derivation (7.1) entirely, since it never calls `Refused`.
    Implemented instead as a manual mode-flag check inside `cmd_open`/
    `cmd_substitute` — the exact shape `implementation_cli.py`'s own
    `cmd_materialize` already uses for `--stage`/`--authored`/`--adopt`
    (`MATERIALIZE_MODE_REQUIRED`/`_CONFLICT`), which design.md's own step-4a
    paragraph names as the precedent for `--adopt`'s shape. Applied
    symmetrically to `substitute`'s `--body`/`--adopt` selection, which also
    needed a "neither given" code no artifact had named:
    `SUBSTITUTE_MODE_REQUIRED`, classified invocation-defect beside
    `ADOPT_BODY_CONFLICT` (design.md's own code for "both given").
  - `TEX_UNDECODABLE` (spec.md's own roster, design step 2) had no raiser
    anywhere after Unit 2 — genuinely unreachable, not merely unwired.
    Added as `paper_block._check_decodable`, called from `parse()` so every
    entry point gets it for free, rather than treated as dead weight the
    roster derivation would need to special-case.
  - `PAPER_ABSENT`/`PAPER_NOT_A_DIRECTORY` were raised only by
    `paper_scaffold.scaffold()`; `substitute()` read `paper_dir / "main.tex"`
    directly and would have raised a raw, uncaught `FileNotFoundError`
    through the CLI's fail-closed contract the first time `open`/`status`/
    `substitute` ran against an unscaffolded `paper/`. Closed by
    `paper_block.resolve_main_tex`, called from `substitute()`,
    `open_block()` and `read_status()` alike.
  - `BLOCK_ID_MALFORMED` (design step 1) lives in `paper_block.py`
    (`validate_block_id`, called from `substitute()`/`open_block()`), not
    in `paper_cli.py`: matches Unit 2's own placement of every other guard
    in the engine rather than the CLI, so a future caller of the engine
    gets the guard for free too.

## Phase 6: Mutation proof (executed, not asserted)

- [x] 6.1 Build mutation harness: copies `paper_block.py` to a fresh temp tree (preserving the depth `Path(__file__).resolve().parents[2]` needs to find `_core/implementation`), patches source, asserts the anchor matched exactly once and the bytes changed, unique module name (both the temp filename and the `importlib` spec name), purges via a directory that is guaranteed fresh (never reused across mutations) plus `PYTHONDONTWRITEBYTECODE=1`, runs the named test in a subprocess via `sys.modules` pre-seeding, asserts non-zero exit AND a `MUTANT_IMPORTED_OK` marker (see Learned below)
- [x] 6.2 M1 — region start shifted one byte earlier: run harness, confirm the byte-identity test goes red. **Measured, not the design's literal anchor**: mutating `project()`'s own region list (the independent verification function) is invisible by construction — the shift applies symmetrically to both `project(pre)` and `project(candidate)`, which a real run confirmed passes green with no guard ever firing. Mutated `build_candidate`'s write-path slice instead (`pre[:begin["start"]]` → `pre[:begin["start"] - 1]`), a real corruption the unmutated `project()` then genuinely disagrees about
- [x] 6.3 M2 — text-mode open against the CRLF fixture: run harness, confirm the byte-identity test goes red
- [x] 6.4 M3 — digest comparison skipped: run harness, confirm the `BLOCK_HAND_EDITED` test goes red

  **Learned, and load-bearing for the whole harness.** The first working
  version of every one of the three mutations above returned a non-zero
  exit code for the WRONG reason: `spec.loader.exec_module(mutant)` was
  crashing on `@dataclass(frozen=True)` field-type resolution, because the
  mutant was registered in `sys.modules` only under the key `'paper_block'`
  and not under its own `spec.name` — `@dataclass` reads
  `sys.modules[cls.__module__]` during class construction, found nothing,
  and raised `AttributeError` before a single line of the mutation logic
  ever ran. A crashed import and a genuinely red guard test are the same
  non-zero exit code, so this failure mode was invisible until each
  mutation's raw subprocess output was read by hand — measured, not
  assumed, matching this project's own "assert the anchor count and assert
  the bytes changed" discipline one layer further down. Fixed by
  registering the mutant under both names, and permanently guarded by a
  `MUTANT_IMPORTED_OK` marker the bootstrap prints only after a successful
  `exec_module`, asserted in every one of the three tests.

## Phase 7: Refusal roster, vocabulary guard, SKILL.md

- [x] 7.1 Implement roster derivation from `paper_cli.py`/`paper_block.py`/`paper_scaffold.py` source (shape of `reachable_refusal_codes`: a closure from `paper_cli.py`'s `cmd_*` roots, unioned with a whole-module scan of this skill's own two helper modules — `impl_refusals.py` contributes nothing, since it raises no `Refused` of its own); classify every code invocation-defect vs work-state in `paper_cli.REFUSAL_CLASSIFICATION`
- [x] 7.2 RED+GREEN: roster test — every refusal in the spec table plus the codes actually implemented this unit (`BLOCK_ID_MALFORMED`, `OPEN_POSITION_REQUIRED`/`_CONFLICT`, `SUBSTITUTE_MODE_REQUIRED`, `ADOPT_BODY_CONFLICT`, `NOTHING_TO_ADOPT`, `TEX_MOVED`, `SUBSTITUTION_NOT_LOCAL`, `TEX_UNDECODABLE`) is reachable and classified, in both directions (21 codes total). `BLOCK_EXISTS`, named in this task's original text, does not exist anywhere in spec.md or design.md — read as a slip for `BLOCK_DUPLICATED`, which `open` does raise and which is classified
- [x] 7.3 Run `tests/test_proposal_implementation.py`'s `ReportFirstSectionProseTests.test_the_whole_forge_borrows_no_repository_s_vocabulary` (the actual forge-wide scan built on `tests/forge_vocabulary.py`, already walking every shipped file of every skill) against the new `SKILL.md` and scripts — clean, no admission needed
- [x] 7.4 Write `.claude/skills/paper-writing/SKILL.md`, sibling idiom, sized to the four verbs this unit actually ships (not the thousands-line precedents' full scope); confirmed `tests/test_suite_collects.py` picks up the new modules (stdlib-only)
