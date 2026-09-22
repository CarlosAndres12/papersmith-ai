# Apply Progress: The Redactor Receives The Section It Must Transpose

**Mode**: Strict TDD (RED → GREEN → REFACTOR, verified per work unit)

## Status

**38/38 tasks complete.** All phases (WU0-WU7) done and measured.
`.venv/bin/python -m unittest discover -s tests -p "test_*.py"` ran to
completion: **4518 tests, 0 failures, 0 errors, 3 skipped (unrelated),
662.4s**. `npm test`: **646/646 pass**. Both suites full-green.

## Completed Tasks

### Phase 0 — WU0: `assemble_packet` gains `corpus`/`paper_dir`
- [x] 0.1 RED: no-corpus/no-paper_dir call keeps the four original keys
- [x] 0.2 RED: a supplied corpus is never re-assembled (spied)
- [x] 0.3 Widened signature `(sections_dir, guidance_dir, section, block_id, *, corpus=None, paper_dir=None)`, docstring updated with the never-re-assemble/never-re-derive contract
- [x] 0.4 Confirmed `cmd_write`'s original bare call still compiled at this point in the sequence

### Phase 1 — WU1: mode gate, resolver, closed state vocabulary
- [x] 1.1 RED/GREEN: resolvable binding → `resolved`
- [x] 1.2 RED/GREEN: no triple declared → `unbound`, no refusal
- [x] 1.3 RED/GREEN: declared triple, no paper root → `unmeasured`, distinguishable from `unbound`
- [x] 1.4 RED/GREEN: `argument`-mode → `not-applicable`, other 3 keys byte-identical to a no-corpus/no-paper_dir call
- [x] 1.5 RED/GREEN: `mode is None` → `unmeasured`, names the absent mode, no `MODE_ABSENT` raised
- [x] 1.6 Implemented `_resolve_packet_source_sections` helper: mode gate, corpus-only-if-`transposition`, corpus-only-if-not-handed, set-difference over `record.source_bindings` vs `resolve_bound_sections`' return
- [x] 1.7 Mutation: broke the no-paper-root branch's `state`/`reason` assignment → 1.3's pinning test went RED under mutation; restored
- [x] 1.8 Generality sweep of Phase 1 engine/test code: zero matches for any lineage/method/paper-specific literal

### Phase 2 — WU2: `RedactorInput` fifth field
- [x] 2.1 RED: field-count assertion (5)
- [x] 2.2 `source_sections: tuple = ()` appended after `style_set`; module docstring "four-input" → "five-input"
- [x] 2.3 Existing construction site (test_paper_writing.py, `RedactorInputContractTests`) unaffected; new keyword-including round-trip case added

### Phase 3 — WU3: CLI wiring
- [x] 3.1 RED/GREEN: `cmd_packet --paper` outside repo → `PAPER_OUTSIDE_REPOSITORY`
- [x] 3.2 `--paper` added to `p_packet`
- [x] 3.3 `cmd_packet` resolves `paper_dir` via `paper_scaffold.resolve_paper_dir` and passes it through
- [x] 3.4 RED/GREEN: a corpus assembled under a supplied (non-default) `paper_dir`, with a `bind`-recorded (not header-declared) binding, is used verbatim; a fresh `assemble_packet(paper_dir=...)` call resolves against the SUPPLIED root, not the derived default (measured: custom root → `resolved`, default root → `unbound`)
- [x] 3.5 `cmd_write`'s bare `assemble_packet` call now passes `corpus=corpus, paper_dir=paper_dir` (the same corpus/root already resolved for the write gate)
- [x] 3.6 RED/GREEN: spied `paper_source_span.resolve_bound_sections` — called exactly twice through a real `cmd_write` run, both times against the identical corpus object (`id()` equality) and `qualified_id`

### Phase 4 — WU4: corpus contamination, tested not commented
- [x] 4.1 RED/GREEN: hand-edited `declarations` region blocks `packet` — `DECLARATIONS_HAND_EDITED` reachable, proving at least one of the 17 category-B codes
- [x] 4.2 RED/GREEN: unrelated malformed sibling section blocks a transposition packet — `MALFORMED_HEADER`
- [x] 4.3 RED/GREEN: same corrupted sibling does NOT block an `argument`-mode packet (mode gate skips corpus assembly entirely)
- [x] 4.4 Confirmed: no new logic required beyond 1.6/3.3 — 4.1-4.3 are proof-only
- [x] 4.5 Accepted-tradeoff comment recorded beside the Phase 1 corpus-assembly branch

### Phase 5 — WU5: D6 falsifier
- [x] 5.1 Synthetic fixture: scaffolded `paper/`, one `sections/*.md` transposition-mode block header-bound to a real synthetic source document/lineage (invented names: `widget-cascade`)
- [x] 5.2 Packet assembled through the REAL `cmd_packet` path — `state == "resolved"`
- [x] 5.3 `test_a_verbatim_paste_of_the_fixture_bound_section_refuses` — drives the packet's own `source_sections` through `cmd_write` end to end; refuses `SOURCE_SECTION_VERBATIM`. D6 holds, measured.
- [x] 5.4 Companion case: genuinely restated draft, run length under threshold, `write` succeeds (`status: "written"`)

### Phase 6 — WU6: docs
- [x] 6.1 `redactor.md` rewritten to five inputs; prohibition re-anchored to "a sixth input"
- [x] 6.2 `SKILL.md` `packet` section updated: fifth key, `--paper` flag, four-state vocabulary table, 17 category-B codes, `PAPER_OUTSIDE_REPOSITORY` (category C), widened-blast-radius note (category D)
- [x] 6.3 Confirmed zero "four input"/"two-part packet" matches in either file

### Phase 7 — WU7: neutrality, roster, both suites
- [x] 7.1 **Roster measured live: `len(reachable_paper_refusal_codes()) == 161`, unchanged.** Zero new refusal codes.
- [x] 7.2 4.1's passing test is the proof the 17 codes were already counted in 161 and are merely newly reachable from `packet`
- [x] 7.3 `ForgeVocabularyDerivedGuardTests` (22/22 green) plus a manual `rg` sweep over every added line: only the invented fixture literal `widget-cascade` appears — no target/researcher vocabulary
- [x] 7.4 **Measured, both suites, in full.** `.venv/bin/python -m unittest discover -s tests -p "test_*.py"`: 4518 tests, 0 failures, 0 errors, 3 skipped (unrelated to this change), 662.4s. `npm test`: 646/646 pass. Both full-green — no second failure beyond the discover run's own baseline.
- [x] 7.5 `git diff main --summary`: zero `delete mode` entries; `git diff main -- sections/` empty

## TDD Cycle Evidence

| Task | RED | GREEN | REFACTOR |
|---|---|---|---|
| 0.1/0.2 | Failing (TypeError: unexpected kwarg) | `assemble_packet` widened signature | Extracted `_resolve_packet_source_sections` helper |
| 1.1-1.5 | Failing (KeyError/TypeError) | Mode gate + set-difference implemented | N/A |
| 1.7 | Mutation forced RED on 1.3 | Restored | N/A |
| 2.1 | Failing (4 != 5) | Field appended | N/A |
| 3.1 | Failing (Refused not raised) | `--paper` wired into `cmd_packet` | N/A |
| 3.4/3.6 | Failing (containment/TypeError) | `cmd_write` passes `corpus=corpus, paper_dir=paper_dir` | N/A |
| 4.1-4.3 | Failing (no refusal reachable) | Proven by 1.6+3.3 alone, zero new code | N/A |
| 5.3 | Failing (segmentation split cost real debugging) | Fixture title changed to single-word to avoid a `paper_bindings.type_structural` false positive | N/A |

## Work Unit Evidence

| Unit | Focused test command | Result | Runtime harness | Result |
|---|---|---|---|---|
| WU0 | `.venv/bin/python -m unittest tests.test_paper_writing.AssemblePacketCorpusParamsTests` | 2/2 pass | N/A (pure function) | N/A |
| WU1 | `tests.test_paper_writing.PacketSourceSectionsStateTests` | 6/6 pass incl. mutation | N/A | N/A |
| WU2 | `tests.test_paper_writing.RedactorInputContractTests` | 3/3 pass | N/A | N/A |
| WU3 | `tests.test_paper_writing.PacketPaperFlagTests tests.test_paper_writing.PacketCorpusReuseTests` | 2/2 + 3/3 pass | Real `cmd_write`/`cmd_packet` under `FORGE_ROOT/implementations/` | pass |
| WU4 | `tests.test_paper_writing.PacketCorpusContaminationTests` | 3/3 pass | Real `cmd_packet` over two fixtures | pass |
| WU5 | `tests.test_paper_writing.SourceSectionVerbatimFalsifierTests` | 3/3 pass | Real `cmd_packet` → `cmd_write`, end to end | pass |
| WU6 | N/A — docs | N/A | N/A | N/A |
| WU7 | Roster + lexicon guard + both suites | 161 roster, 22/22 lexicon, npm 646/646 | Full discover: 4518 tests, 0 fail, 0 error, 3 skipped, 662.4s | pass |

Rollback boundary: each work unit's own files are isolated per the
`design.md` File Changes table; no file outside `paper_cli.py`,
`paper_bindings.py`, `redactor.md`, `SKILL.md`, and `tests/test_paper_writing.py`
was touched. `git revert` of the relevant commit removes exactly that unit.

## Files Changed

| File | Action | What |
|---|---|---|
| `.claude/skills/paper-writing/scripts/paper_cli.py` | Modified | `assemble_packet` widened + `_resolve_packet_source_sections` helper; `cmd_packet` resolves `--paper`; `cmd_write` passes its own corpus/paper_dir; `p_packet` gains `--paper` |
| `.claude/skills/paper-writing/scripts/paper_bindings.py` | Modified | `RedactorInput.source_sections` fifth field; docstrings updated |
| `.claude/agents/redactor.md` | Modified | Five inputs, sixth-input prohibition |
| `.claude/skills/paper-writing/SKILL.md` | Modified | `packet` section: fifth key, `--paper`, state vocabulary, refusal roster additions |
| `tests/test_paper_writing.py` | Modified | New test classes for every phase; two pre-existing mutation-anchor tests updated to match the new signature/call site |

## Deviations from Design

None — implementation matches `design.md` D1-D6 exactly, including the
[corrected] 17th category-B code (`DECLARATIONS_HAND_EDITED`).

Commit granularity deviates from strict per-work-unit: WU0-WU5 landed in one
commit (`feat(paper-writing): ...`) because the underlying edits are
interleaved in the same functions/files and were implemented as one
integrated increment before any commit was made; WU6 (docs) is its own
commit. The owner's `exception-ok` delivery strategy and 1600-line engine
ceiling (measured ~130 engine lines, comfortably under) make this an
acceptable tradeoff rather than a blocking risk.

## Issues Found

One real fixture bug caught during RED-first work, not a design defect: a
heading title containing "3. Something" (matching existing repo precedent)
produces a resolved source-section span that starts at the markdown
heading LINE itself (`paper_guidance.segment_markdown`'s own `byte_start`
convention). Pasting that span verbatim into a draft therefore also pastes
the heading marker, and a multi-word heading title puts a second
capitalized token into the segmented "sentence" at a non-zero index, which
`paper_bindings.type_structural`'s named-external-object check correctly
flags — an accurate refusal, but the WRONG one for what WU5's D6 falsifier
needs to prove. Fixed by using a single-word heading title
(`Formulation`) in the WU5 fixture only; every other fixture in this
change keeps the existing repo-precedent multi-word titles since they
never paste the resolved text into a draft.

## Measured Numbers (never forecast)

- `reachable_paper_refusal_codes()`: **161** (pinned value, unchanged)
- Engine lines under `.claude/skills/`: measured via `git diff main --stat`
  against the owner's 1600-line ceiling (see final report)
- `npm test`: 646/646 pass
- `tests/test_paper_writing.py`: 591/591 pass (standalone)
- `tests/test_paper_decisions.py`: 289/289 pass (standalone)
- `tests.test_proposal_implementation.ForgeVocabularyDerivedGuardTests`: 22/22 pass

## Remaining Tasks

None. All 38 tasks complete.
