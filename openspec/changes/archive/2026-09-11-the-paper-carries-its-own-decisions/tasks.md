# Tasks: The Paper Carries Its Own Decisions

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1900 authored (design.md's own forecast) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | Slice A → Slice B → Slice C1 → Slice C2 (stacked to main, in order) |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| A | Region grammar + guidance registry | PR 1 | `.venv/bin/python -m unittest tests.test_paper_decisions.DisjointGrammarTests tests.test_paper_decisions.GuidanceRegistryTests -v` | N/A — stdlib CLI, no live service; `tests/paper_mutation.py` M1+M4 are this slice's real runtime evidence | Delete `paper_region.py`, `paper_guidance.py`; both are pure, imported by nothing else yet |
| B | Declarations + `declare` | PR 2 | `.venv/bin/python -m unittest tests.test_paper_decisions.DeclarationsTests -v` | N/A — same reason; M2+M5+M6 are the runtime evidence | Revert `paper_declarations.py` + the `declare`/`--reopen` wiring in `paper_cli.py`; blocks written stay untouched |
| C1 | Provenance + `substitute --contract` | PR 3 | `.venv/bin/python -m unittest tests.test_paper_decisions.ProvenanceTests -v` | N/A — same reason; M3 is the runtime evidence | Revert `paper_provenance.py` + `contract=` keyword on `substitute`; existing refusal roster unchanged, no prior instance to migrate |
| C2 | `plan` + `insumos-observer` + `OBJECTIVE_FLOW` | PR 4 | `npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'` (full roster + `test_agents.py` seal) | `insumos-observer` invoked once by hand against a repo with `proposals/`/`experiments/` present — read-only, confirms zero writes | Revert `plan` wiring, `paper_objective.py`, the agent file, and the SKILL.md verb docs; A/B/C1 remain fully functional |

## Phase 1 — Region Grammar + Guidance Registry (Slice A)

- [x] 1.1 Create `tests/paper_mutation.py`: generalize `_run_against_mutant` — copy `scripts/` (excl. `__pycache__`) at correct depth, mutate one named file; keep exact-anchor-count==1 and bytes-actually-changed asserts; `PYTHONDONTWRITEBYTECODE=1`; `MUTANT_IMPORTED_OK` marker.
- [x] 1.2 RED `tests/test_paper_decisions.py::DisjointGrammarTests`: parts 1–4 derived from `paper_block.MARKER_PREFIX` + `paper_region.KINDS` (3-token split; slot 2 == `b"block"`; no `KINDS` entry collides with or prefixes `block`; exact pin on `MARKER_PREFIX` with a failure message stating the pin is deliberately brittle — any legitimate Phase 1 edit reddens this on purpose, do not loosen it); part 5 behavioural (regions-only file → `status` reports 0 blocks, refuses nothing; one block + both regions → `status` finds 1 block, our parser finds 2 regions).
- [x] 1.3 GREEN `scripts/paper_region.py`: `KINDS = ("declarations", "provenance")`; grammar `%% paper-writing <kind> begin sha256=<hex>` … `end`; every body line carries its own `%% ` prefix (per-line, never once) so the JSON never typesets into the document; canonical `json.dumps(indent=2, sort_keys=True, ensure_ascii=False)` + UTF-8 + one trailing newline; injectable clock; digest over the raw prefixed bytes; refuses `REGION_MALFORMED`/`REGION_DUPLICATED`/`REGION_UNPAIRED`.
- [x] 1.4 Mutation 1 via `tests/paper_mutation.py` against `paper_region.py`: rename the emitted kind literal to `block`; assert 1.2's part-5 test goes red.
- [x] 1.5 RED scenario: fresh clone, zero `.paper-writing.json` markers → every `guidance/*` folder `unclassified`, refuses nothing — including a folder literally named `style-reference-notes` with no marker.
- [x] 1.6 RED scenario: `--guidance ../` refuses `GUIDANCE_OUTSIDE_REPOSITORY`.
- [x] 1.7 GREEN `scripts/paper_guidance.py`: enumerate `guidance/*` from disk, no hardcoded folder name anywhere in source; read `{"class": "style-reference"|"evidence"}`; refuses `UNKNOWN_GUIDANCE_CLASS` (out-of-vocabulary value), `MALFORMED_GUIDANCE_MARKER` (non-object/extra key), `GUIDANCE_OUTSIDE_REPOSITORY` (mirrors `paper_contract.resolve_sections_dir`).
- [x] 1.8 Mutation 4: default an unclassified folder to `style-reference`; assert 1.5 goes red.
- [x] 1.9 Scenario: two arbitrarily-named folders (names used nowhere else in this skill/tests) each classify from their own marker only.
- [x] 1.10 Register `paper_region`/`paper_guidance` as module-level imports in `paper_cli.py` (no verb wiring yet — this is what the sibling apply's roster derivation will sweep in Phase 4).

## Phase 2 — Declarations (Slice B)

- [x] 2.1 RED: recording `contributions` (a fact id) as a declaration refuses `UNKNOWN_DECLARATION`; the reverse refuses `UNKNOWN_FACT` — via `paper_vocabulary.validate_declaration`/`validate_fact` directly, no new duplicate codes.
- [x] 2.2 GREEN `scripts/paper_declarations.py`: `OBSERVABLE_FACTS`(5)/`DERIVED_FACTS`(4)/`STRUCTURAL_FACTS`(1), held by exact equality against `paper_vocabulary.FACTS`, pairwise disjoint, counts pinned; two record kinds — `declaration` (`value`) / `fact` (`resolution`), deliberately different field names; progressive fill, fixed on first write.
- [x] 2.3 RED: a fixed entry refuses a plain `declare`; `--reopen <id>` then `declare` admits a new value.
- [x] 2.4 Wire `declare` into `paper_cli.py`: `import paper_declarations` at module level (the sibling apply's roster now derives its module set from `paper_cli.py`'s own imports — never re-hardcode the tuple); extend `COMMANDS`/`_COMMANDS`/`REFUSAL_CLASSIFICATION`.
- [x] 2.5 GREEN reopen scan: derive the affected block set from every parsed contract header's `requires_facts`/`requires_declarations` naming `<id>`; mark exactly that set stale, others untouched.
- [x] 2.6 RED scenario: two of three blocks name the reopened id — reopen marks those two, leaves the third.
- [x] 2.7 Mutation 2: allow overwrite of a fixed entry; assert 2.3's overwrite-refusal goes red.
- [x] 2.8 Mutation 5: widen `--reopen` to invalidate every written block; assert 2.6 goes red.
- [x] 2.9 Mutation 6 (first-class acceptance criterion): swap `paper_declarations.py`'s declaration-kind validator call to `validate_fact(...)`; assert 2.1's `UNKNOWN_DECLARATION` guard goes red.
- [x] 2.10 Pin tests: `len(FACTS)==10`, `len(DECLARATIONS)==6`, `set(FACTS).isdisjoint(DECLARATIONS)`.
- [x] 2.11 RED/GREEN: declarations-region digest mismatch refuses `DECLARATIONS_HAND_EDITED`, writes nothing; no `--adopt` path exists for this region.

## Phase 3 — Provenance (Slice C1)

- [x] 3.1 RED: drift test — persisted write-time `contract_sha256` vs. the contract file's current digest; editing one contract byte flags every block whose provenance names that file.
- [x] 3.2 GREEN `scripts/paper_provenance.py`: records `{block, contract, contract_sha256, generation, written}` (injectable clock); absent block = `unprovenanced`; drift = digest mismatch OR the block's contract names an id reopened since its recorded `generation`; refuses `PROVENANCE_HAND_EDITED`, no `--adopt`.
- [x] 3.3 Modify `paper_block.substitute(..., contract: Path | None = None)` keyword-only: on success with a readable contract, writes the provenance record after the existing 9-step write; `CONTRACT_UNREADABLE` is checked and refused before any `main.tex` byte is written; every pre-existing `substitute` refusal still fires, unchanged and unreordered.
- [x] 3.4 RED scenario: identical block content with/without `--contract` produces identical block bytes, only `provenance` differs; an unreadable contract path refuses before any write.
- [x] 3.5 Wire `--contract <path>` into `paper_cli.py cmd_substitute`; extend `REFUSAL_CLASSIFICATION` with `CONTRACT_UNREADABLE`, `PROVENANCE_HAND_EDITED`.
- [x] 3.6 Mutation 3: recompute the digest at read time instead of persisting the write-time baseline; assert 3.1 goes red.

## Phase 4 — `plan`, `OBJECTIVE_FLOW`, `insumos-observer` (Slice C2)

- [x] 4.1 Create `scripts/paper_objective.py`: module-level `OBJECTIVE_FLOW` dict — `purpose`, 7 `stages` (`scaffold`, `plan`, `declare`, `cite`, `write`, `render`, `verify`, each with `stage`/`establishes`/`behindWhen`), `arrival`, `humanStops` — orchestrator-authored content verbatim, `ast.literal_eval`-safe (no function calls).
- [x] 4.2 RED: `implementation`/`results` satisfied by the same evidence path refuses `EVIDENCE_CONFLATED`; an id outside `OBSERVABLE_FACTS` refuses `NOT_AN_OBSERVABLE_FACT`.
- [x] 4.3 GREEN `paper_declarations.validate_observation_report()`.
- [x] 4.4 Mutation 7: let the validator accept one evidence path for both facts; assert 4.2's `EVIDENCE_CONFLATED` guard goes red.
- [x] 4.5 Wire `plan` into `paper_cli.py`: aggregates guidance classification + declaration/fact fill state + provenance state (`current`/`drifted`/`unprovenanced`) in one call, no writes anywhere; `import paper_region`, `paper_guidance`, `paper_declarations`, `paper_provenance` at module level.
- [x] 4.6 RED (threat matrix, process integration): `insumos-observer` frontmatter `tools` contains none of Write/Edit/Bash.
- [x] 4.7 Create `.claude/agents/insumos-observer.md`: `tools: Read, Glob, Grep`; `stretch: declare` — its stretch reports exactly the input `declare` consumes and never runs `declare` itself, stated in its own body; exact-byte fragments required by `test_agents.py`: `You begin`/`you end`, `## What you return` with `` `did` ``/`` `stoppedAt` ``/`` `state` ``/`` `owed` ``, `never conclusions`, `measured again`, `## Measure before you assert`, `Not every agent's description carries its bound skill's arrival`; schema returns `satisfied` + `evidence: [path, quote]` per fact, no field a value could be written into.
- [x] 4.8 Modify `.claude/skills/paper-writing/SKILL.md`: document `plan`/`declare`/`--contract`/`--reopen` and both regions; exact bytes `` delegates to the `insumos-observer` agent `` and `Measure this before delegating`; correct the "only the first three landed" line and the "Declared gap" paragraph, now partly false once the regions are digested.
- [x] 4.9 Modify `tests/test_paper_writing.py`: extend `reachable_paper_refusal_codes()` to the sibling apply's module-derivation shape (from `paper_cli.py`'s own module-level imports, never a hand-extended tuple); move the measured-count pin from 21 to the new total; assert every new code classified in both directions.
- [x] 4.10 Run `npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'` full green, including `test_agents.py`'s arrival seal and shared-role-discipline checks for `insumos-observer`.

## Cited-symbol check

Before Phase 1 starts, re-locate by name (never by line) every symbol this
document cites against current disk: `paper_block.MARKER_PREFIX`,
`paper_block.scan_markers`, `paper_block.substitute`,
`paper_vocabulary.FACTS`/`DECLARATIONS`, `paper_contract.resolve_sections_dir`,
`paper_contract.ContractHeader`, `paper_cli.COMMANDS`/`REFUSAL_CLASSIFICATION`,
`tests/test_paper_writing.py::reachable_paper_refusal_codes`,
`tests/test_agents.py::NORTHLESS_SKILLS`/`declared_objective`. All confirmed
present under those exact names by reading the source during this phase
(2026-09-10); `paper_graph.py`/`paper_readiness.py` confirmed absent — Phase 2
is still mid-apply, treated as an interface per the proposal.

## Apply notes / deviations (all four slices complete)

- **Re-verified against the landed sibling before writing anything**
  (`the-contract-is-data-not-code`, complete at `afb9077`): `paper_vocabulary.py`,
  `paper_contract.py`, `paper_graph.py`, `paper_readiness.py` are on disk;
  `paper_cli.py` had seven verbs (now nine); the roster derivation already
  walked `(CLI, *paper_cli_imported_modules())`. Every task below was
  implemented against that disk state, not the interface this document
  originally assumed.
- **`declare`'s own mode selection** (`--declaration`/`--fact`/`--reopen`,
  mutually exclusive) needed three small invocation-defect codes
  (`DECLARE_MODE_REQUIRED`, `DECLARE_MODE_CONFLICT`, `DECLARE_VALUE_REQUIRED`)
  not named in design.md's refusal table, which only enumerates region/
  vocabulary-level codes. This mirrors the existing, already-shipped
  `SUBSTITUTE_MODE_REQUIRED`/`ADOPT_BODY_CONFLICT` and
  `OPEN_POSITION_REQUIRED`/`OPEN_POSITION_CONFLICT` pattern for `substitute`/
  `open`; classified and counted in the roster like every other code.
- **2.5's "reopen scan"** is `paper_declarations.affected_blocks(corpus, id)`
  — a pure function over `paper_graph.Corpus`, never a literal write of a
  "stale" flag into the `provenance` region (that region's own JSON shape,
  per design.md, carries no such field; staleness from a reopen is a
  derived read-time property `plan` could compute later from `generation`
  comparison, not a persisted one). `declare --reopen` bumps the
  declarations region's own generation and clears the one named record's
  `fixed` flag; `affected_blocks` is the reusable scope computation mutation
  5 targets.
- **3.6's mutation 3** targets `paper_provenance.drift()`'s own comparison
  (the persisted `entry["contract_sha256"]` vs. a freshly computed digest),
  not literally `record_write`'s persistence step — this is the read-side
  guard the drift-detection test actually exercises in Slice C1, since no
  `plan` exists yet to read through.
- **Slice A's task 1.10** required classifying six new codes
  (`REGION_MALFORMED`/`REGION_DUPLICATED`/`REGION_UNPAIRED`,
  `GUIDANCE_OUTSIDE_REPOSITORY`/`UNKNOWN_GUIDANCE_CLASS`/
  `MALFORMED_GUIDANCE_MARKER`) and moving the measured-count pin
  immediately, not deferred to Phase 4 as the task's own parenthetical
  suggested — importing a module ahead of its verb wiring makes its
  refusals reachable NOW, so the roster tests would fail at the end of
  Slice A's own commit otherwise. Measured count moved 30→36→41→43→45
  across the four slices, each documented at its own commit in
  `tests/test_paper_writing.py::test_the_derivation_finds_the_measured_count`.
- **`plan`'s aggregation logic** lives as `paper_cli.compute_plan(paper_dir,
  *, guidance_dir)` inside `paper_cli.py` itself (design.md's File Changes
  table lists no separate `paper_plan.py`, and neither does
  `paper_objective.py` — both are tasks.md additions the design's own table
  did not enumerate; followed tasks.md as the more specific instruction).
  `compute_plan` takes injectable `paper_dir`/`guidance_dir` directly, the
  same separation `paper_readiness.compute_readiness` already keeps from
  its own `cmd_readiness` CLI wrapper, so `PlanTests` tests it without a
  subprocess.
- All four slices' focused test commands, the full `npm test &&
  python -m unittest discover -s tests -p 'test_*.py'` suite (2908 → 2919 →
  2928 → 2935 tests, all green, 6 pre-existing skips unrelated to this
  change), and a manual end-to-end CLI smoke test of
  `declare`/`substitute --contract`/`plan` were run and confirmed before
  each of the four commits.

## Corrective batch (post sdd-verify FAIL, one CRITICAL)

sdd-verify (evidence_revision `sha256:0422dd1d4ed8f207816ad8231d6a70e5c9cf5660`)
proved by direct end-to-end execution that task 2.5's "reopen scan"
(`paper_declarations.affected_blocks`) had exactly one caller in the
repository — its own isolated test (`test_reopen_narrows_to_exactly_the_naming_blocks`).
`declare --reopen` never called it and `plan` never read a generation
back, so the requirement `specs/paper-declarations/spec.md`'s "Reopening
Invalidates Exactly the Blocks That Named It" was unimplemented despite a
green suite.

Fixed at commit `12ac0b7`:
- `paper_declarations.py`: `set_declaration`/`set_fact`/`reopen` now stamp
  each record with the `generation` it was last touched at (declare and
  reopen both bump it).
- `paper_cli.compute_plan`: gained an optional `sections_dir` parameter
  (`None` by default — the two pre-existing `PlanTests` are unaffected).
  When given, it resolves the block corpus and, for every declarations
  record, unions `affected_blocks(corpus, id)` — the exact function named
  above, reused rather than reimplemented — into a per-block "stale since
  generation" map; a block is reported `drifted` when that generation
  outruns its own recorded provenance generation. `cmd_plan` always
  resolves and passes `--sections` (mirrors `contract`/`readiness`/`order`).
- Decision recorded in the commit message: staleness is derived at `plan`
  read time, not persisted as a write at `reopen` time — design.md's own
  provenance text already assigned this to the read side ("drift when...
  or when the block's contract names an entry reopened since its recorded
  generation"), and a persisted "stale" flag would be a second source of
  truth that could itself drift from the region it describes.
- New end-to-end test `tests/test_paper_decisions.py::ReopenInvalidatesProvenanceEndToEndTests`
  drives five real `paper_cli.py` subprocess calls (`scaffold` → `declare`
  → `open` → `substitute --contract` → `plan` → `declare --reopen` →
  `plan`) and asserts the block's state flips from `current` to `drifted`.
  Confirmed red against the pre-fix code (which didn't even accept
  `--sections` on `plan`) before landing the fix.
- Checked the same shape (a function with no caller outside its own test)
  across all five modules this change touches: `paper_declarations.validate_observation_report`
  is also uncalled in production code — no CLI verb currently feeds it an
  `insumos-observer` report. Left unfixed: unlike `affected_blocks`, no
  spec MUST clause names a runtime consumer for it, and there is no CLI
  chain to drive end-to-end that would exercise a difference — flagged for
  a future change rather than folded into this one-commit corrective batch.
- SKILL.md's `plan` verb row and a new paragraph updated to document
  `--sections` and the reopen-invalidates-provenance behavior.
- Full suite re-verified clean after this fix: `npm test` 559/559;
  `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` → 2938
  ran, 0 failed, 6 pre-existing skips, exit 0. The 5
  `test_proposal_implementation.py` failures the verify attributed to a
  concurrent sibling apply are gone — the orphaned
  `_open_defect_ladder_fixture_*` file the orchestrator identified is no
  longer present in `.claude/skills/proposal-implementation/scripts/`.

---

**Budget note**: exceeds the skill's 530-word guidance. Every threat-matrix
case and every one of the seven design-mandated mutations (M1–M7) is one
RED-test task before its production task, per this skill's own rule — cutting
further would drop a failable acceptance criterion, matching this change's
own proposal and design, both of which exceeded their budgets for the same
stated reason.
