# Tasks: The Redactor Receives The Section It Must Transpose

> Paths below: every `paper_*.py` is under
> `.claude/skills/paper-writing/scripts/`; `tests/` and `openspec/` are
> repository-root relative — same convention as `design.md`.

## Review Workload Forecast

Owner accepted `size:exception` up front (delivery strategy `exception-ok`).
Owner-set engine-line ceiling: **1600 lines of code under `.claude/skills/`**.
The default PR review budget (400 changed lines) is reported honestly below
but is NOT a blocking decision here — per the orchestrator's own instruction,
do not stop, do not ask, do not recommend chained PRs as a blocker.

| Unit | Engine lines under `.claude/skills/` (est.) | Test/fixture lines (est., `tests/`) | Unit total | Running total | Against 1600 |
|---|---|---|---|---|---|
| WU0 — `assemble_packet` gains `corpus`/`paper_dir`, never re-derives what it's handed | ~40 (`paper_cli.py`) | ~50 | ~90 | 90 | Low |
| WU1 — mode gate, resolver call, set-difference, closed state vocabulary | ~60 (`paper_cli.py`) | ~170 (incl. mutation proof) | ~230 | 320 | Low |
| WU2 — `RedactorInput` fifth field | ~10 (`paper_bindings.py`) | ~30 | ~40 | 360 | Low |
| WU3 — CLI wiring: `cmd_packet --paper`, `p_packet` flag, `cmd_write` passes its own corpus | ~40 (`paper_cli.py`) | ~90 | ~130 | 490 | Low |
| WU4 — corpus contamination: 17 inherited codes reachable, unrelated-section defect, argument-mode byte-identical | 0 | ~150 | ~150 | 640 | Low |
| WU5 — D6 falsifier: verbatim paste refuses `SOURCE_SECTION_VERBATIM` end to end | 0 | ~90 | ~90 | 730 | Low |
| WU6 — docs: `redactor.md`, `SKILL.md` | ~70 (`redactor.md` + `SKILL.md`) | 0 | ~70 | 800 | Low |
| WU7 — neutrality sweep, roster re-measurement, both suites | 0 (verification only) | ~20 | ~20 | 820 | Low |

**Estimated total ~820 changed lines. Engine lines under `.claude/skills/`: ~220 —
Low risk against the owner's 1600 ceiling.** Delta specs
(`openspec/specs/redactor-packet`, `.../evidence-bound-drafting`) are already
written and committed by the `sdd-spec` phase; not counted in this diff.

```text
Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: High
```

(High against the *default* 400-line review policy — total ~820 lines,
mostly tests. Not a blocker: owner pre-accepted `size:exception` and set the
1600-line ceiling, against which this change is Low.)

## Suggested Work Units

| Unit | Goal | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|
| WU0 | `assemble_packet(..., *, corpus=None, paper_dir=None)`; never assembles a corpus it was handed, never derives a root it was not given | `.venv/bin/python -m unittest tests.test_paper_writing` | N/A — pure function-signature change, no CLI surface yet | `git revert` WU0; `corpus`/`paper_dir` are keyword-only and defaulted, no existing caller breaks |
| WU1 | Mode gate (D5), resolver call, set-difference, `source_sections`/`source_sections_state` keys (D1, D4) | `.venv/bin/python -m unittest tests.test_paper_writing` | N/A — still no CLI wiring | `git revert` WU1; `assemble_packet`'s four original keys stay byte-identical when `corpus`/`paper_dir` are omitted |
| WU2 | `RedactorInput.source_sections: tuple = ()` appended fifth (D3) | `.venv/bin/python -m unittest tests.test_paper_writing.RedactorInputContractTests` | N/A | `git revert` WU2; defaulted field, the one keyword-only construction site at `tests/test_paper_writing.py:4616` stays green untouched |
| WU3 | `cmd_packet` resolves `--paper`; `cmd_write:2228` passes its own `corpus`/`paper_dir` instead of letting `assemble_packet` re-derive | `.venv/bin/python -m unittest tests.test_paper_writing.SourceSectionBindingWriteGateTests tests.test_paper_writing.BindCliEndToEndTests` | Real `cmd_write`/`cmd_packet` roots under `FORGE_ROOT/implementations/`, same pattern as `SourceSectionBindingWriteGateTests.setUp` | `git revert` WU3; every other verb's `--paper` wiring is untouched precedent |
| WU4 | Accepted tradeoff (17 inherited codes) has a test, not a comment; argument-mode byte-identity proven | `.venv/bin/python -m unittest tests.test_paper_writing` | Real `cmd_packet` over two fixtures (clean + one corrupted sibling section) | `git revert` WU4; test-only, no engine change |
| WU5 | D6 falsifier ships and passes: a fixture draft pasting its own bound section verbatim still refuses `SOURCE_SECTION_VERBATIM` | `.venv/bin/python -m unittest tests.test_paper_writing.SourceSectionBindingWriteGateTests` (or new class housing the fixture) | Real `cmd_packet` → `cmd_write` path, end to end | `git revert` WU5; test-only |
| WU6 | `redactor.md` says five inputs, prohibition re-anchored to a sixth; `SKILL.md` packet surface + refusal roster updated | N/A — docs | N/A | `git revert` WU6; prose-only |
| WU7 | Zero new refusal codes measured; generality sweep clean; both suites green | `.venv/bin/python -m unittest discover -s tests -p "test_*.py"` AND `npm test` | Full suite, both runtimes | N/A — verification-only, nothing to roll back |

## Phase 0 — WU0: `assemble_packet` gains `corpus`/`paper_dir`, on its own contract first

Satisfies `design.md` D2, D3(interface). Touches `paper_cli.py:2052-2113`
(`assemble_packet`).

- [x] 0.1 RED: add a failing test asserting `assemble_packet(sections_dir,
      guidance_dir, section, block_id)` — called with no `corpus`/`paper_dir`
      — still returns exactly the four existing keys, byte-identical to
      today, confirming the widened signature changes nothing for an
      existing caller.
- [x] 0.2 RED: add a failing test asserting that when `assemble_packet` is
      called WITH a pre-built `corpus` (constructed the way `_resolve_write_
      gate` builds one, `paper_cli.py:1822`), it never calls
      `paper_graph.assemble_corpus` (read-only) a second time — patch/spy on
      `assemble_corpus` and assert zero additional calls.
- [x] 0.3 Widen `assemble_packet`'s signature to `(sections_dir, guidance_dir,
      section, block_id, *, corpus=None, paper_dir=None)`. Update its
      docstring (currently `:2053-2083`) to state the new never-re-assemble,
      never-re-derive contract from `design.md`'s Interfaces section
      verbatim. Confirm 0.1 and 0.2 go green.
- [x] 0.4 Confirm `paper_cli.py:2228`'s existing bare call,
      `assemble_packet(sections_dir, guidance_dir, args.section, args.block)`,
      still compiles and its existing behavior (gate-only, return value
      unused) is UNCHANGED at this point in the sequence — WU3 is what
      rewires it, not this task.

## Phase 1 — WU1: mode gate, resolver, closed state vocabulary

Satisfies `design.md` D1, D4, D5; `redactor-packet` spec scenarios
"A transposition block with a resolved binding...", "...reports unbound...",
"No paper root reachable reports unmeasured...", "An argument-mode block
reports not-applicable...". Calls `paper_source_span.resolve_bound_sections`
(read-only, `paper_source_span.py`) and `paper_contract.resolve_mode`
(already parsed by `assemble_packet`, no extra disk read).

- [x] 1.1 RED: add a failing test — `transposition`-mode block, resolvable
      binding, corpus+paper_dir supplied — asserts `source_sections` carries
      the shipped shape (`{fact, lineage, title, path, byte_start, byte_end,
      text}`) and `source_sections_state == {"state": "resolved", "reason":
      None, "unresolved": []}`.
- [x] 1.2 RED: add a failing test — same block, no `(fact, lineage, title)`
      triple declared at all — asserts `source_sections == []` and
      `source_sections_state.state == "unbound"`, no refusal raised.
- [x] 1.3 RED: add a failing test — same block WITH a declared triple, but
      `paper_dir=None` (or a `--paper` that does not resolve) — asserts
      `source_sections_state.state == "unmeasured"`, `reason` names the flag
      or root that would answer it, and `unresolved` lists the undecided
      triple. **This is constraint 4 (its own assertion, not folded into
      1.2)**: assert this state's dict is unequal to 1.2's `unbound` dict —
      same empty `source_sections`, distinguishable envelope.
- [x] 1.4 RED: add a failing test — `argument`-mode block with a bound
      section that WOULD resolve — asserts `source_sections_state.state ==
      "not-applicable"`, `source_sections == []`, AND the other three packet
      keys (`block`, `section`, `contract`, `references`) are byte-identical
      to calling `assemble_packet` with no `corpus`/`paper_dir` at all
      (**constraint 5 — the narrowing D2 rests on, measured not assumed**).
- [x] 1.5 RED: add a failing test — `mode is None` (no mode declaration) —
      asserts `source_sections_state.state == "unmeasured"`, `reason` names
      the absent `mode` declaration, and `assemble_packet` raises no
      `MODE_ABSENT` (that refusal stays `write`'s, `paper_write.py:106-111`).
- [x] 1.6 Implement inside `assemble_packet`: resolve mode via
      `paper_contract.resolve_mode`; when not `transposition`, set
      `not-applicable`/`unmeasured` per 1.4/1.5 and skip corpus assembly
      entirely (D2 — never assemble for a block that cannot use the result);
      when `transposition`, assemble the corpus only if `corpus is None` (D2
      — never re-assemble what was handed), call
      `paper_source_span.resolve_bound_sections` (read-only), and compute
      the `unbound`/`unmeasured`/`resolved` split by set difference between
      the record's `source_bindings` and the resolver's return. Confirm
      1.1-1.5 all green.
- [x] 1.7 Mutation: replace the `state`/`reason` assignment for the
      `unmeasured` branch with a constant `"resolved"` (or drop the branch);
      confirm 1.3 goes RED — proving `unmeasured` is reachable, not
      decorative. Use `tests.paper_mutation._run_against_mutant(anchor,
      replacement, dotted_test, source_path=SKILL_SCRIPTS / "paper_cli.py")`
      (`tests/paper_mutation.py`, read-only — pass `source_path` explicitly,
      the default is `paper_block.py`). Restore.
- [x] 1.8 Generality sweep for this phase's own new code: `rg` under
      `.claude/skills/paper-writing/scripts/paper_cli.py` and this phase's
      new test code for any lineage name, method name, or paper-specific
      literal. Confirm zero matches — every fixture name invented.

## Phase 2 — WU2: `RedactorInput` fifth field

Satisfies `design.md` D3; `evidence-bound-drafting` spec, "Requirement:
Redactor Input Contract". Touches `paper_bindings.py:39-44`.

- [x] 2.1 RED: add a failing test asserting `len(dataclasses.fields(paper_
      bindings.RedactorInput)) == 5` — the shape's only enforcement per D3.
- [x] 2.2 Add `source_sections: tuple = ()` to `RedactorInput`, appended
      AFTER `style_set`, exact `BlockContract.source_sections` precedent
      (`paper_write.py:51-59`). Update the module docstring at
      `paper_bindings.py:14` from "four-input" to "five-input" (measured
      claim, not just code). Confirm 2.1 green.
- [x] 2.3 Confirm the one existing construction site,
      `tests/test_paper_writing.py:4616` (`RedactorInputContractTests`,
      fully keyword), still passes unmodified — it already omits the new
      defaulted field, exactly as the zero-positional-caller sweep in
      `design.md` D3 measured. Add one new keyword-including case in the
      same test class asserting `source_sections` round-trips.

## Phase 3 — WU3: CLI wiring — `cmd_packet --paper`, `cmd_write` passes its own corpus

Satisfies `design.md` D1 (invocation-defect boundary), D2 (never assemble
twice). Touches `paper_cli.py:2116-2127` (`cmd_packet`), `paper_cli.py:2228`
(`cmd_write`'s existing bare `assemble_packet` call), `paper_cli.py:3089-3103`
(`p_packet` parser).

- [x] 3.1 RED: add a failing test — `cmd_packet` called with `--paper`
      resolving OUTSIDE the repository root — asserts `Refused` with code
      `PAPER_OUTSIDE_REPOSITORY` (`paper_scaffold.py:42-55`, same boundary
      `write`/`place` already enforce).
- [x] 3.2 Add `--paper` to `p_packet` (`paper_cli.py:3089-3103`), same
      `default=None, help="override paper/ location; must resolve inside
      the repository root"` shape every other verb already uses (e.g.
      `p_write.add_argument("--paper", ...)` at `:2983-2986`).
- [x] 3.3 Wire `cmd_packet`: resolve `paper_dir =
      paper_scaffold.resolve_paper_dir(args.paper)` and pass it to
      `assemble_packet(..., paper_dir=paper_dir)`. Confirm 3.1 green.
- [x] 3.4 RED: add a failing integration test — construct a corpus via
      `_resolve_write_gate` under a `paper_dir` that DIFFERS from
      `sections_dir.parent / "paper"` (`paper_graph.py:299`'s own default),
      call `assemble_packet(..., corpus=that_corpus, paper_dir=that_paper_
      dir)`, and assert the resolved `source_sections` reflect bindings from
      the SUPPLIED root, not the derived default — proving `assemble_packet`
      never re-derives a root it was not given.
- [x] 3.5 Fix `cmd_write`'s existing line `paper_cli.py:2228`:
      `assemble_packet(sections_dir, guidance_dir, args.section, args.block)`
      → `assemble_packet(sections_dir, guidance_dir, args.section,
      args.block, corpus=corpus, paper_dir=paper_dir)`, using the `corpus`
      already bound at `:2218` and the `paper_dir` already resolved at
      `:2215`. This is the concrete site `design.md`'s Data Flow diagram
      names: `cmd_write` must never let `assemble_packet` assemble a SECOND
      corpus against a possibly-different derived root. Confirm 3.4 green
      and re-confirm `SourceSectionBindingWriteGateTests` (existing suite)
      unaffected.
- [x] 3.6 RED-then-GREEN: add a test asserting a transposition-mode `write`
      call, with `--paper` differing from the corpus-derivation default, now
      resolves `source_sections`/`source_sections_state` inside the gate's
      own `assemble_packet` call consistently with `BlockContract.source_
      sections` computed at `:2260` — same corpus, same root, both places.

## Phase 4 — WU4: corpus contamination is a tested consequence, not a comment

Satisfies constraints 2 and 5 from the tasks brief; `redactor-packet` spec
scenario "An unrelated section's defect blocks a transposition block's
packet"; `design.md` category B (17 inherited codes) and category D
(widened blast radius, not new reachability).

- [x] 4.1 RED: add a failing test — a `transposition`-mode block with a
      resolvable binding, where the SAME `paper_dir`'s `declarations` region
      has been hand-edited (triggering `paper_declarations._verify_not_hand_
      edited`, `paper_declarations.py:707`) — asserts `cmd_packet` refuses
      `DECLARATIONS_HAND_EDITED` (`paper_declarations.py:186`), proving at
      least one of the 17 codes in `design.md`'s category B table is
      reachable from `packet`, not merely documented as reachable.
- [x] 4.2 RED: add a failing test — a `transposition`-mode block with a
      resolvable binding, and a DIFFERENT `sections/*.md` file under the
      same `sections_dir` carrying a malformed header (`MALFORMED_HEADER`,
      `paper_contract.py`) — asserts `cmd_packet` refuses on the unrelated
      file's own code, not this block's binding.
- [x] 4.3 RED: add a failing test — the SAME corrupted-sibling fixture from
      4.2, but the target block is `argument`-mode instead — asserts
      `cmd_packet` does NOT refuse (mode gate in Phase 1 skips corpus
      assembly entirely for a non-transposition block, so the unrelated
      defect never surfaces).
- [x] 4.4 Implement/confirm: no new code should be required if Phase 1's
      mode gate (1.6) and Phase 3's corpus wiring (3.3) are correct — 4.1-4.3
      exist to PROVE that, not to introduce new logic. If any of 4.1-4.3
      needs an unplanned code change, stop and reconcile against `design.md`
      before proceeding.
- [x] 4.5 Record the accepted tradeoff, verbatim, as a code comment beside
      the Phase 1 corpus-assembly branch in `assemble_packet`: "corpus-wide
      refusal contamination on `packet` is accepted, see `design.md` D2 and
      `redactor-packet` spec scenario 'An unrelated section's defect blocks
      a transposition block's packet' — the tests, not this comment, are the
      enforcement."

## Phase 5 — WU5: D6 falsifier — its own task, required at apply

Satisfies `design.md` D6 exactly: *"Apply MUST ship
`test_a_verbatim_paste_of_the_fixture_bound_section_refuses`... A green
suite without it leaves D6 asserted rather than measured."*

- [x] 5.1 Build a synthetic fixture — invented names only, following
      `SourceSectionBindingWriteGateTests.setUp`'s own pattern
      (`tests/test_paper_writing.py:9282-9339`): a `paper_dir` scaffolded via
      `paper_scaffold.scaffold`, one `sections/*.md` with a `transposition`-
      mode block bound to a real synthetic source document/lineage, and a
      completed `bind` round recording that binding (`paper/.paper-
      writing/`).
- [x] 5.2 Assemble the packet for that block through the real `cmd_packet`
      path (not a hand-built corpus) and confirm `source_sections` carries
      the fixture section's own resolved text with `state == "resolved"`.
- [x] 5.3 Write `test_a_verbatim_paste_of_the_fixture_bound_section_refuses`:
      construct a draft whose LaTeX body pastes the fixture's own bound
      section text VERBATIM (run length exceeding `max(source_section_floor,
      SOURCE_RUN_BACKSTOP=16)`), drive it through `cmd_write` end to end
      using the packet's `source_sections` as the redactor's fifth input,
      and assert `write` refuses `SOURCE_SECTION_VERBATIM`
      (`paper_leak.py:185-212`, read-only — unedited by this change). A
      failure here means D6 is wrong and `design.md` must be revisited
      before this change ships.
- [x] 5.4 Companion case in the same fixture: the SAME block drafted with a
      genuinely restated (non-verbatim) version of the section text, run
      length under threshold, passes `check_source_section_verbatim` and
      `write` succeeds — proves the guard is not simply always-refuse.

## Phase 6 — WU6: docs — `redactor.md`, `SKILL.md`

Satisfies proposal Success Criteria "`redactor.md` says five inputs and
still forbids opening a file to find a sixth" and "Both shipped requirements
carry delta specs" (specs already written; this phase covers the remaining
non-spec docs).

- [ ] 6.1 Edit `.claude/agents/redactor.md:15-24`: rewrite the four-input
      paragraph to five, adding the block's own bound source sections as the
      fifth declared input. Re-anchor "you never open a file yourself to
      find a fifth input" to "a sixth input" — the prohibition's WORDS
      change, its MEANING does not: the redactor still never reads a file
      itself.
- [ ] 6.2 Edit `.claude/skills/paper-writing/SKILL.md`: update the `packet`
      surface description (fifth key `source_sections` +
      `source_sections_state`, the `--paper` flag, the four-state
      vocabulary) and the refusal roster: add the 17 codes newly reachable
      from `packet` for a transposition block (`design.md` category B table,
      including the corrected 17th — `DECLARATIONS_HAND_EDITED`),
      `PAPER_OUTSIDE_REPOSITORY` as reachable on every `packet` invocation
      (category C), and a note on the widened-blast-radius codes
      (`MALFORMED_HEADER`/`MALFORMED_FIGURE_OBLIGATION`, category D) —
      reachable via an UNRELATED section file, not new codes.
- [ ] 6.3 Confirm neither `redactor.md` nor `SKILL.md` still reads "four
      inputs" or "two-part packet" anywhere (`rg -n "four input" .claude/`).

## Phase 7 — WU7: neutrality, roster, both suites

Satisfies constraints 1, 6, 7 from the tasks brief; proposal Success
Criteria "Roster re-measured live..." and "No paper id... appears anywhere
under `.claude/skills/`."

- [ ] 7.1 **Zero new refusal codes, measured.** Run
      `reachable_paper_refusal_codes()` (`tests/test_paper_writing.py:7486`)
      after all engine code from Phases 0-4 has landed. Confirm the pinning
      assertion at `tests/test_paper_writing.py:7942`
      (`self.assertEqual(len(reachable_paper_refusal_codes()), 161)`) still
      passes UNCHANGED — this change adds zero `raise Refused(...)` sites
      (`design.md`, "Refusal Codes — A. New refusal codes introduced by this
      change: Zero"). If the count moved, stop and reconcile before
      proceeding — do not edit the pin to match an unexplained delta.
- [ ] 7.2 **17 inherited codes recorded as reachable, not silently
      widened.** Confirm 4.1 (or an equivalent) is present in the final test
      suite and passing — the roster count staying at 161 in 7.1 together
      with 4.1's passing test is the proof that these 17 codes were already
      counted in 161 (reachable from `write` before this change) and are
      merely NEWLY REACHABLE FROM `packet`, not new to the codebase.
- [ ] 7.3 Generality sweep, whole-change: run
      `tests.test_proposal_implementation`'s rule B / `FORGE_LEXICON`-derived
      guard (`ForgeVocabularyDerivedGuardTests`) and confirm no NEW leak
      introduced by this change's own code, comments, docstrings, or
      fixtures — same discipline as the sibling precedent change's WU3.
      Follow with a plain `rg` sweep under `.claude/skills/paper-writing/`
      and this change's own new test code for any lineage name, method name,
      or researcher's folder name; confirm zero matches outside invented
      fixture literals.
- [ ] 7.4 Run `.venv/bin/python -m unittest discover -s tests -p
      "test_*.py"` (chunked if the project's own known ~650s discover time
      exceeds the foreground timeout, per the precedent change's own
      recorded chunking) AND `npm test`. Both. Confirm `npm test` is
      full-green and the Python suite shows AT MOST the one known
      pre-existing failure
      (`ForgeVocabularyDerivedGuardTests.test_rule_b_finds_no_target_
      vocabulary_in_the_forge`, the generic-word-"mechanisms" baseline).
      **Any second failure belongs to this change and blocks delivery.**
- [ ] 7.5 Confirm `git diff main -- sections/` is empty and no file was
      deleted anywhere in the change (`git diff --summary main` shows only
      `create`/`modify`, zero `delete mode`).

## Key discipline carried forward

- Red first, every phase above.
- A mutation is the only proof a guard holds — 1.7 is `unmeasured`'s own
  mutation task, not merely a passing-case test.
- The roster is measured, never forecast — 7.1 runs after all engine code
  lands; no number is written into any artifact before that.
- The 17 inherited codes and the argument-mode byte-identity guarantee are
  each proven by an executed test (4.1, 1.4), never asserted in prose alone.
- D6's falsifier (Phase 5) is required at apply, not optional polish — a
  green suite without it leaves D6 asserted rather than measured.
- Nothing under `sections/` is edited; nothing is deleted — checked at 7.5.
- Read-only, never edited by this change: `paper_source_span.py`,
  `paper_leak.py`, `paper_graph.py`, `tests/paper_mutation.py`.
