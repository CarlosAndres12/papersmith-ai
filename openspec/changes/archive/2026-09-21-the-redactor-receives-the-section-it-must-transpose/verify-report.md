```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:f13a1a3bf53f33e66d0f226dd8ec5db79bfedd15f0e2f37c0d716123ea82f6f6
verdict: pass
blockers: 0
critical_findings: 0
requirements: 2/2
scenarios: 11/11
test_command: .venv/bin/python -m unittest discover -s tests -p "test_*.py"
test_exit_code: 0
test_output_hash: sha256:68845e5ad887b970d7c5172e6d26dabc46bff4bae438bbce0d49fdba29c6673c
build_command: npm test
build_exit_code: 0
build_output_hash: sha256:6fd937de56c2d1816266026b30f0486509530b1d61a6b0dffef1235a56d2effc
```

## Verification Report

**Change**: the-redactor-receives-the-section-it-must-transpose
**Version**: N/A (delta specs, no version field)
**Mode**: Strict TDD (RED -> GREEN -> REFACTOR per apply-progress.md)

### Completeness

| Metric | Value |
|--------|-------|
| Tasks total | 38 |
| Tasks complete | 38 |
| Tasks incomplete | 0 |

All 38 tasks across WU0-WU7 are ticked in `tasks.md` and independently
cross-checked against `apply-progress.md`'s own per-task log. No unchecked
task found.

### Build & Tests Execution

**Build** (`npm test`, this project's second full-suite gate): PASSED

```text
$ npm test
ℹ tests 646
ℹ pass 646
ℹ fail 0
ℹ skipped 0
ℹ duration_ms 34062.605333
```

Run independently TWICE in this verify session (once mid-session, once for
the hash captured above) — both runs: 646/646, 0 failures.

**Tests** (`.venv/bin/python -m unittest discover -s tests -p "test_*.py"`): PASSED

```text
Ran 4518 tests in 661.932s
OK (skipped=3)
```

Run independently in this verify session, full discover, foreground,
uninterrupted (~11m2s wall clock: started 03:23, finished 03:34:42). Zero
`FAILED`/`ERROR:` lines in the captured log (grepped explicitly). Matches
`apply-progress.md`'s claimed 4518/0/0/3/662.4s within measurement noise
(661.9s vs 662.4s — same run class, not a discrepancy).

Additionally ran standalone, independently, to cross-check apply's
per-module numbers:
- `tests.test_paper_writing`: **591/591 pass** (20.26s) — matches claim exactly.
- `tests.test_paper_decisions`: **289/289 pass** (5.80s) — matches claim exactly.
- The 7 new/relevant test classes named in `apply-progress.md`, run
  together in isolation: **22/22 pass** (0.225s) — `AssemblePacketCorpusParamsTests`,
  `PacketSourceSectionsStateTests`, `RedactorInputContractTests`,
  `PacketPaperFlagTests`, `PacketCorpusReuseTests`,
  `PacketCorpusContaminationTests`, `SourceSectionVerbatimFalsifierTests`.
- `tests.test_proposal_implementation.ForgeVocabularyDerivedGuardTests`:
  **22/22 pass** (5.11s) — matches claim exactly.

**Coverage**: Not available (no coverage tool configured in this project) —
➖ Not available, same as prior changes in this repository.

### Roster and engine-size claims, measured directly (not inherited)

- `reachable_paper_refusal_codes()` **== 161**, measured live via a fresh
  interpreter import (`from tests.test_paper_writing import
  reachable_paper_refusal_codes; len(...)` → `161`). Zero new refusal
  codes. Confirms `design.md` category A ("Zero") and `apply-progress.md`
  7.1.
- Engine diff, measured via `git diff main --numstat`:
  `paper_cli.py` 148 insertions / 10 deletions,
  `paper_bindings.py` 15 insertions / 4 deletions →
  **163 insertions + 14 deletions = 177 lines**, matching apply's claim
  exactly. Against the owner's 1600-line ceiling: Low.
- `git diff main --summary`: **zero `delete mode` entries** — nothing
  deleted anywhere in the change (confirms task 7.5).
- `git diff main -- sections/`: **empty** — nothing under `sections/`
  touched (confirms task 7.5).

### Spec Compliance Matrix

**`redactor-packet` (7 scenarios)**

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Packet Carries Contract Prose, Style Extracts, Bound Source Sections | A packet for one block assembles both style parts | `test_paper_writing.py::PacketAssemblyTests::test_packet_assembles_contract_prose_and_reference_outlines` | ✅ COMPLIANT (pre-existing, still green) |
| same | A reference with no equivalent block contributes nothing | `PacketAssemblyTests::test_a_non_style_reference_root_contributes_nothing` / `test_an_unclassified_root_contributes_nothing_either` | ✅ COMPLIANT (pre-existing, still green) |
| same | A transposition block with a resolved binding carries its own section text | `PacketSourceSectionsStateTests::test_a_resolvable_binding_reports_resolved` | ✅ COMPLIANT |
| same | A transposition block with no binding decided reports unbound, not a refusal | `PacketSourceSectionsStateTests::test_no_triple_declared_at_all_reports_unbound_never_a_refusal` | ✅ COMPLIANT |
| same | No paper root reachable reports unmeasured, distinguishable from unbound | `PacketSourceSectionsStateTests::test_a_declared_triple_with_no_paper_root_reports_unmeasured` + its own mutation proof `test_mutation_the_no_paper_root_branch_is_reachable_not_decorative` | ✅ COMPLIANT — mutation-proven, not merely a passing-case test |
| same | An argument-mode block reports not-applicable and stays byte-identical | `PacketSourceSectionsStateTests::test_an_argument_mode_block_reports_not_applicable_and_stays_byte_identical` | ✅ COMPLIANT — byte-identity of the other 3 keys independently verified by reading the assertion body, not just its name |
| same | An unrelated section's defect blocks a transposition block's packet | `PacketCorpusContaminationTests::test_an_unrelated_malformed_section_blocks_a_transposition_packet` (+ non-block companion `test_the_same_corrupted_sibling_does_not_block_an_argument_mode_packet`) | ✅ COMPLIANT |

**`evidence-bound-drafting` (4 scenarios)**

| Requirement | Scenario | Test | Result |
|-------------|----------|------|--------|
| Redactor Input Contract | A block drafts with an empty style set | `RedactorInputContractTests::test_empty_style_set_is_a_valid_input` | ✅ COMPLIANT (pre-existing, still green) |
| same | The redactor receives five declared inputs and opens no file for a sixth | `RedactorInputContractTests::test_the_shape_carries_exactly_five_fields` + `test_source_sections_round_trips_as_a_keyword`; "opens no file" half is an agent-prompt contract (`redactor.md`), verified by source inspection, not runtime-testable | ✅ COMPLIANT (shape half test-covered; prohibition half is prose-contract, consistent with the rest of this skill's agent-boundary design) |
| same | A non-transposition block drafts with empty source sections | `PacketSourceSectionsStateTests::test_an_argument_mode_block_reports_not_applicable_and_stays_byte_identical` (feeds the empty tuple `RedactorInput.source_sections` would receive) | ✅ COMPLIANT |
| same | The fifth input widens visibility, never the verbatim guard | `SourceSectionVerbatimFalsifierTests::test_a_verbatim_paste_of_the_fixture_bound_section_refuses` (D6 falsifier, run end-to-end through real `cmd_packet` -> `cmd_write`) + companion `test_a_genuinely_restated_draft_under_threshold_still_writes` (proves the guard is not simply always-refuse) | ✅ COMPLIANT |

**Compliance summary**: 11/11 scenarios compliant.

### Priority checks (per orchestrator instructions), each re-verified independently

1. **`unbound` vs `unmeasured` distinguishable from the envelope alone** —
   read `_resolve_packet_source_sections` (`paper_cli.py:2052-2144`)
   directly: `unbound` returns early with `state="unbound"` when
   `header_triples`/`declared_triples` is empty (nothing declared);
   `unmeasured` returns when a triple IS declared but cannot resolve (no
   `paper_dir`, or resolution left an `unresolved` remainder). Both report an empty
   `source_sections` list when nothing resolves, but `state`/`reason`
   differ. Verified by running BOTH branches via the actual test class
   (`PacketSourceSectionsStateTests`) — both pass, and 1.3's own docstring
   asserts inequality between the two dicts. Mutation-proven for the
   `unmeasured` no-paper-root branch (1.7): re-ran that exact mutation test
   myself, still green (mutant correctly makes it fail, restore correctly
   makes it pass).

2. **Argument-mode packet byte-identical to today's** — read the test body
   of `test_an_argument_mode_block_reports_not_applicable_and_stays_byte_identical`
   directly: it asserts the argument-mode packet's `block`/`section`/`contract`/`references`
   keys equal a packet assembled with no `corpus`/`paper_dir` supplied at
   all (i.e., today's pre-change call shape). Ran it: PASS.

3. **`cmd_write` passes its own corpus, never re-derives a second one** —
   read `paper_cli.py:2298-2395` (`cmd_write`) directly: `corpus =
   _resolve_write_gate(paper_dir, sections_dir, qualified_id)` at line
   2344, then `assemble_packet(..., corpus=corpus, paper_dir=paper_dir)`
   at line 2359-2361, with an explicit comment naming the exact defect
   this prevents. `paper_source_span.resolve_bound_sections(corpus, ...)`
   is called twice in `cmd_write` (once inside `assemble_packet`'s gate,
   once directly for `BlockContract.source_sections` at line 2393) but
   against the SAME corpus object both times — this is read-only reuse,
   not re-assembly. `PacketCorpusReuseTests::test_cmd_write_resolves_source_sections_consistently_with_assemble_packet`
   spies on `resolve_bound_sections`, asserting exactly 2 calls against
   `id()`-equal corpus objects. Ran it: PASS.

4. **Five declared inputs, no sixth door** — `RedactorInput`
   (`paper_bindings.py:45-55`) has exactly 5 fields, confirmed by direct
   source read AND `RedactorInputContractTests::test_the_shape_carries_exactly_five_fields`
   (dataclasses.fields() length assertion, the shape's only enforcement
   per D3). `redactor.md` re-anchors the prohibition to "a sixth input"
   (confirmed by direct read of `.claude/agents/redactor.md:15-27`).

5. **17 inherited codes reachable from `packet`, covered by an executed
   test** — `PacketCorpusContaminationTests::test_a_hand_edited_declarations_region_blocks_the_packet`
   proves `DECLARATIONS_HAND_EDITED` reachable (one of the 17); the roster
   staying at 161 (measured live, independently, above) together with this
   passing test is the proof the other 16 were already counted pre-change
   and are merely newly reachable from `packet`. This is a comment-plus-
   roster-count proof for 16 of 17 and a direct test for 1 of 17 — matches
   `design.md`'s own stated proof shape (roster pin + one concrete raise),
   not a gap.

6. **D6 falsifier — verbatim paste still refuses `SOURCE_SECTION_VERBATIM`**
   — ran `SourceSectionVerbatimFalsifierTests` directly (not inherited from
   apply's report): `test_a_verbatim_paste_of_the_fixture_bound_section_refuses`
   PASSES (refuses `SOURCE_SECTION_VERBATIM`), and the companion
   `test_a_genuinely_restated_draft_under_threshold_still_writes` PASSES
   (`write` succeeds), proving the guard is not simply always-refuse. D6
   holds, measured.

### Also checked

- **Generality** — ran `ForgeVocabularyDerivedGuardTests` directly: 22/22
  pass. Additionally ran my OWN `rg` sweep (not apply's) over the full
  `git diff main` for `paper_cli.py`, `paper_bindings.py`, `SKILL.md`,
  `redactor.md`: zero matches for any lineage/method name from this
  session's own memory (`widget`, `milcreda`, `creda`, `batchnorm`,
  `domain.adapt`, `kaggle`, `multi.instance`, `abmil`, `attention`,
  `histopatholog`, `whole.slide`). The new TEST code (not shipped under
  `.claude/skills/`) carries exactly one invented fixture literal,
  `widget-cascade`, consistent with apply's own claim.
- **Both suites, full, myself** — see Build & Tests Execution above; both
  run independently in this session, not copy-pasted from apply's report.
- **Docs match code** — `SKILL.md` (`packet` section, lines 800-887) and
  `redactor.md` both read directly and cross-checked against the running
  code's actual signature, state vocabulary, and refusal roster (see
  Priority checks 1-5 above). `rg -ni "four input|two-part packet"
  .claude/` returns zero matches inside this skill's files (one unrelated
  hit in `_core/implementation/engine/implementation_engine.py`, a
  different skill's "four inputs" phrase, not this one's).

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|------------|--------|-------|
| `assemble_packet` corpus/paper_dir params, never re-assembles/re-derives | ✅ Implemented | Read directly, `paper_cli.py:2147-2232` |
| Mode gate + closed 4-value state vocabulary | ✅ Implemented | `_resolve_packet_source_sections`, `paper_cli.py:2052-2144` |
| `RedactorInput` fifth field | ✅ Implemented | `paper_bindings.py:45-55` |
| `cmd_packet --paper`, `cmd_write` single-corpus wiring | ✅ Implemented | `paper_cli.py:2235-2252`, `:2341-2361` |
| Zero new refusal codes | ✅ Confirmed | Roster measured live: 161, unchanged |

### Coherence (Design)

| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 — missing/unreadable paper root is a named state, never a refusal | ✅ Yes | Confirmed by source + tests |
| D2 — corpus assembled only for transposition; never assembled twice | ✅ Yes | Confirmed by source + spy test |
| D3 — `source_sections` appended fifth, defaulted | ✅ Yes | One construction site, unaffected |
| D4 — fifth input mirrors `BlockContract.source_sections` exactly | ✅ Yes | Same dict shape in all 3 places, confirmed by source read |
| D5 — only transposition resolves; argument gets not-applicable | ✅ Yes | Confirmed |
| D6 — `SOURCE_RUN_BACKSTOP=16` unchanged, falsifier ships and passes | ✅ Yes | Ran the falsifier myself |
| Deviation: commit granularity (WU0-5 one commit, WU6 separate) | ⚠️ Noted | Disclosed in `apply-progress.md`, accepted as non-blocking under `exception-ok` |

### Issues Found

**CRITICAL**: None.

**WARNING**: None.

**SUGGESTION** (out-of-scope finding, reported per orchestrator instruction,
not fixed):

1. **`paper_contract.resolve_section_path`'s scan-every-file lookup order
   is a real, pre-existing, broader-than-documented latent defect** —
   confirmed by direct reproduction, not just by reading the code or
   trusting apply's Key Learning #3. `resolve_section_path`
   (`paper_contract.py:768-798`, read-only, NOT touched by this change)
   globs `sections_dir.glob("*.md")` in SORTED order and calls `parse()`
   on EVERY file until the target section's own header is found. I built
   a minimal reproduction (two synthetic files, no `sections/` fixture
   reused) where a corrupted sibling file sorting alphabetically BEFORE an
   unrelated target section causes `resolve_section_path` to raise
   `MALFORMED_HEADER` for a lookup that has nothing to do with the
   corrupted file. Confirmed output:
   `Refused MALFORMED_HEADER invalid JSON in header at line 1 column 1:
   Expecting value`.

   This is BROADER than `design.md` category D ("widened blast radius"),
   which scopes the equivalent hazard to `assemble_corpus` and
   `transposition`-mode `packet` calls only. `resolve_section_path` runs
   unconditionally inside `assemble_packet` (`paper_cli.py:2201`) for
   EVERY block regardless of mode, and is also on `write`'s and `place`'s
   own paths — so an `argument`-mode block, or a block with no source
   binding at all, can be blocked by an unrelated corrupted sibling
   through THIS earlier path, even where `packet`'s own mode gate (D5)
   correctly skips corpus assembly. `PacketCorpusContaminationTests
   ::test_the_same_corrupted_sibling_does_not_block_an_argument_mode_packet`
   sidesteps this exact hazard by name-ordering its fixture
   (`00-c` before `02-b`) with an explicit comment acknowledging it: "this
   test is about `assemble_packet`'s NEW mode gate ... never about that
   unrelated, already-shipped lookup order." That comment is accurate and
   the sidestep is reasonable for THIS change's own scope, but the
   underlying defect it sidesteps is real, pre-existing (this change does
   not touch `paper_contract.py`), and not tracked by any open issue this
   verify pass could find. Recommend a follow-up change scoped to
   `resolve_section_path` alone (e.g. catch-and-skip a malformed sibling
   rather than propagating its refusal, or resolve by filename-declared
   `section` field first and only fall back to the scan). Not a blocker
   for this change: `paper_contract.py` is explicitly out of scope
   (design.md File Changes table marks it read-only), and this change
   introduces neither the defect nor a new path that reaches it beyond
   what already existed.

2. Two other Key Learnings from `apply-progress.md` independently
   confirmed as accurate, not just plausible: `resolve_bound_sections`'
   returned `text` DOES include the markdown heading line itself
   (`paper_guidance.segment_markdown`'s `byte_start = match.start()` —
   the regex match starts at the `#` of the heading line, confirmed by
   direct source read of `paper_guidance.py:385-434`); and the WU5 fixture
   does use a single-word heading title (`Formulation`, confirmed by
   `rg` against `tests/test_paper_writing.py:10968,10976`), consistent
   with the claimed `type_structural` named-external-object interaction
   for multi-word titles.

### Verdict

**PASS**

All 38 tasks complete and independently cross-checked against running
code, not inherited from `apply-progress.md`'s prose. Both full suites
(Python 4518/4518, npm 646/646) re-run in this verify session with zero
failures. All 11 spec scenarios across both delta specs map to a passing,
independently-executed covering test. Zero new refusal codes (161,
measured live). Zero deletions, `sections/` untouched. One real,
pre-existing, out-of-scope latent defect found and reported
(`resolve_section_path`'s scan-every-file lookup order) — not a blocker
for this change, recommended as a follow-up.
