# Tasks: The Tripwire Reaches The Section That Feeds It

## Review Workload Forecast

Owner-raised delivery budget: **1600 changed lines** (raised twice today by owner ruling).
Design's own estimate is ~1050 total. Engine and test/fixture lines are forecast separately
per owner ruling — a combined total that hides the split is not acceptable.

| Unit | Engine lines (est.) | Test/fixture lines (est.) | Docs/spec lines (est.) | Unit total (est.) | Running total | Against 1600 |
|---|---|---|---|---|---|---|
| WU0 — `$$` fence fix + blast radius | ~50 (`paper_style.py`, `paper_bindings.py`, derived-sweep helper) | ~185 (fixture corpus files, M1 harness, unit + sweep + mutation tests) | ~15 (`math-fence-blast-radius.md`) | ~250 | 250 | Low |
| WU1 — wiring (`_resolve_write_gate` → `Corpus`, `paper_source_span.py`, `BlockContract.source_sections`, `sourceFidelity: unmeasured`) | ~120 | ~175 (resolution tests, `undecided`/`unmeasured` tests, stop-and-report contingency documented, not coded) | 0 | ~295 | 545 | Low |
| WU2 — threshold, sibling check, mode derivation, wiring into `write_block` | ~110 (`SOURCE_RUN_BACKSTOP`, `source_section_floor`, `check_source_section_verbatim`, `MODE_TRANSPOSITION`/`MODE_ARGUMENT`, `REFUSAL_CLASSIFICATION` entry) | ~230 (scenario tests + 6 of 8 mutation tests) | ~15 (`SKILL.md` roster entry + stage doc) | ~355 | 900 | Low-Medium |
| WU3 — neutrality gate, roster re-measure, both suites, falsification obligation recorded | ~0 (no new engine code expected) | ~140 (generality sweep tests, roster re-measurement assertion, remaining 2 of 8 mutation tests if not already covered in WU2) | ~10 (Open Questions / falsification-obligation note) | ~150 | 1050 | Low |

**Estimated total ~1050 changed lines against the 1600 budget — Low risk.** Against the
default 400-line review-policy threshold every unit individually exceeds it, so the four
slices ship as **chained PRs**, each targeting its predecessor's branch, per design.md's
own ruling (`400-line budget risk: High` against the default, `Low`/`Low-Medium` against
1600).

```
Decision needed before apply: No
Chained PRs recommended: Yes
Chain order: WU0 -> WU1 -> WU2 -> WU3 (WU0 is the gate for everything after it)
400-line budget risk (default 400): High
1600-line budget risk (owner-raised): Low / Low-Medium (WU2)
```

## Suggested Work Units

| Unit | Goal | Depends on | Focused test command | Parallel-safe internally? | Rollback boundary |
|---|---|---|---|---|---|
| WU0 | `$$` fence fix, measured, in both `strip_math` implementations, derived cross-module sweep | none (runs first against `main`) | `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_contract` (targeted classes once named) | The two file fixes (0.6/0.9) are independent of each other; the before-table (0.3) MUST precede both, the after-table (0.10) MUST follow both | `git revert` WU0's commit(s); `paper_style.py`/`paper_bindings.py` regex reverts cleanly |
| WU1 | `_resolve_write_gate` returns `Corpus`; `paper_source_span.py`; `BlockContract.source_sections`; `sourceFidelity` reported `unmeasured`/resolved, no verdict yet | WU0 landed (blast-radius gate); concurrent `the-whole-cut-is-argued-before-any-section-is-claimed` landed with the outline-shaped memo | `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_contract` | 1.2 (return-value change) and 1.4 (`paper_source_span.py` creation) can proceed in parallel once 1.1's gate check passes; wiring (1.6-1.7) is sequential after both | `git revert` WU1's commit(s); `BlockContract.source_sections` is defaulted so existing construction sites stay green |
| WU2 | `SOURCE_RUN_BACKSTOP`, `source_section_floor`, `check_source_section_verbatim`, the `write_block` stage, `MODE_TRANSPOSITION`/`MODE_ARGUMENT`, `REFUSAL_CLASSIFICATION`, `SKILL.md`, six of eight mutations | WU1 landed | `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_leak` (once module-scoped test class exists) | 2.1-2.4 (threshold/floor engine) and 2.9-2.10 (`MODE_TRANSPOSITION` vocabulary) are independent and parallel-safe; the `write_block` wiring (2.11+) is sequential after both land | `git revert` WU2's commit(s); `write_block` reverts to its pre-stage shape |
| WU3 | Neutrality/generality audit as an apply-gate, roster re-measured live, both suites, falsification obligation recorded | WU2 landed | full suite (both, see 3.5) | 3.1 (generality sweep) and 3.2 (roster re-measure) are independent and parallel-safe | `git revert` WU3's commit(s); no engine code is expected to need reverting |

**Non-negotiable discipline carried into every phase below** (from the operator's own
ruling, not restated per task): red first; a mutation is the only proof a guard holds;
generality is a task, not an assumption; the roster is measured, never forecast; nothing
deletes files; never edit any file under `sections/`.

## Phase 0 — WU0: The `$$` fence fix, measured, first

Design.md, Decision A. Satisfies `style-leak-detection` (modified) — "Requirement: The
Eight-Token Tripwire" — and `evidence-bound-drafting` (modified) — "Requirement:
Structural Sentences Are Typed".

**This phase runs against an otherwise-unmodified tree until 0.3 is captured.** Do not
touch `paper_style.py` or `paper_bindings.py` before the before-table exists.

- [x] 0.1 Create `tests/fixtures/math_fence_corpus/` — six invented markdown files, no
      product name, no real paper vocabulary: a `$$…$$` display fence, an inline `$…$`, a
      `\[…\]` display form, a `\begin{equation}…\end{equation}` form, an unpaired `$`, and
      plain prose with no math markers. (`style-leak-detection`, "Requirement: The
      Eight-Token Tripwire", Scenario "A `$$` display fence is excluded, body and all".)
- [x] 0.2 Write the M1 harness (a test module or a small script under `tests/`) that, for
      every ordered pair `(styled, sample)` drawn from the fixture corpus, records
      `len(paper_style.normalize_tokens(styled))`, `len(paper_leak.tripwire_spans(styled,
      [sample]))`, and `paper_leak.overlap_against_set(styled, [sample])`. The harness must
      be executable and must produce a delta report naming every pair whose tripwire hit
      count changed and every file whose normalized token count changed (design.md,
      Measurement M1).
- [x] 0.3 **Execute M1 on the current, unmodified tree** (before either `strip_math` is
      touched) and capture its output verbatim into
      `openspec/changes/the-tripwire-reaches-the-section-that-feeds-it/math-fence-blast-radius.md`
      as the **before-table**. State the exact command that produced it. Do not author any
      number in this file by hand.
- [x] 0.4 In the same run, execute M1 additionally over whatever document-sourced `.md`
      this checkout happens to hold (ambient content), and record that result in the same
      file under a section explicitly marked `ambient, not asserted` — a fresh clone holds
      none of this, and no gate condition may depend on it (design.md, Decision A gate
      table, third row).
- [x] 0.5 RED: add a failing unit test asserting `paper_style.strip_math` excludes a `$$…$$`
      fence body entirely (not merely its delimiters), against the fixture corpus. Confirm
      it fails against the current, unmodified `_MATH_DISPLAY_RE`/`_MATH_INLINE_RE` pair
      (`paper_style.py` lines 33-48). (`style-leak-detection`, Scenario "A `$$` display
      fence is excluded, body and all".)
- [x] 0.6 Fix `paper_style.py`: add the `\$\$.*?\$\$|` alternative to `_MATH_DISPLAY_RE`
      (design.md, Decision A — the exact regex is given there), ahead of the existing
      `\\\[.*?\\\]|\\begin{...}` alternatives, preserving the `\1` backreference to the
      environment group. Confirm 0.5 goes green.
- [x] 0.7 RED: add a failing unit test asserting `paper_bindings._strip_math` (lines
      140-152) carries the identical `$$` defect — a display equation containing a numeral
      inside a `structural`-typed sentence wrongly reaches `STRUCTURAL_CARRIES_CLAIM`
      today. Confirm it fails against the current, unmodified pattern.
      (`evidence-bound-drafting`, Scenario "A numeral inside a display-math fence does not
      refuse".)
- [x] 0.8 Fix `paper_bindings.py`: add the identical `$$` alternative to its own
      `_MATH_DISPLAY_RE`. Do NOT merge the two implementations (design.md, Decision A: the
      local-import discipline `paper_leak` exists under forbids pulling `paper_style` into
      `paper_bindings`). Confirm 0.7 goes green.
- [x] 0.9 RED-then-GREEN: add the DERIVED cross-module sweep test — introspects every
      module under `scripts/` for a callable literally named `strip_math` or `_strip_math`
      (never a two-item hand-maintained list) and asserts each excludes a `$$` fence.
      Confirm it is red before 0.6/0.8 land (both implementations still defective) and
      green after both land. (`style-leak-detection`, Scenario "Mutation — a third
      normalizer is caught by the derived sweep, never a hand-edited list".)
- [x] 0.10 **Execute M1 again**, on the tree with 0.6 and 0.8 applied, and append the
      **after-table** plus the delta (every pair whose hit count changed, every file whose
      normalized token count changed) to `math-fence-blast-radius.md`. This is the gate:
      WU1 may not open until this file carries both executed tables (design.md, Work
      Units — "WU0 is the gate for everything after it").
- [x] 0.11 Mutation: drop the `$$` alternative from `paper_style.py`'s pattern; confirm the
      display-fence unit test (0.5) goes red. Restore.
- [x] 0.12 Mutation: drop the same alternative from `paper_bindings.py`'s pattern; confirm
      the cross-module sweep test (0.9) goes red — proving the sweep, not a hand-listed
      pair, is what catches drift. Restore.
- [x] 0.13 Generality sweep: `rg` under `.claude/skills/` and `tests/` for any literal from
      the fixture corpus filenames bleeding into engine code (there should be none — the
      corpus is test-only). Confirm zero matches outside `tests/fixtures/math_fence_corpus/`
      and its own test module.
- [x] 0.14 Run `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_contract`
      (or the narrower module/class once named) and confirm green with no new failures.

## Phase 1 — WU1: The wiring gap is closed

Design.md, Decision E. Satisfies `transposition-fidelity` (new) — the prerequisite
plumbing every Requirement in that spec depends on (`source_sections` must arrive at
`write_block` before any check can run against it).

- [x] 1.1 **Concurrency gate — read this before touching `paper_graph.py`.**
      `the-whole-cut-is-argued-before-any-section-is-claimed` owns `paper_graph.py` this
      cycle and must land first with `_verify_source_section_bindings`'s per-`(root,
      lineage)` memo widened from `{title: count}` to `(revision_path, segment_markdown
      outline)` — the outline, not just counts, since byte offsets do not derive from
      counts. **Confirm this by reading `paper_graph.py` directly**: if the memo at
      `_verify_source_section_bindings` (currently around line 481: `memo[memo_key] =
      (revision_path, counts)`) still stores counts rather than the outline, the
      concurrent change has not landed callable. **If it has not landed, STOP and REPORT.**
      Do not re-walk `FACT_SOURCE_ROOT -> source_root_status -> resolve_lineage /
      resolve_ingested_document -> segment_markdown` into a second implementation, and do
      not edit `paper_graph.py` yourself under any circumstance — this is the applier
      instruction from design.md, Decision E, carried here verbatim so it survives
      apply-time pressure to "just fix it forward."
      **Confirmed landed**: read `paper_graph.py` directly — `resolve_section_index`
      (extracted function, not the inline memo) returns `(revision_path, counts, outline)`,
      and `_verify_source_section_bindings`'s own memo at line ~511-515 stores that whole
      triple (`memo[memo_key] = resolve_section_index(...)`), keeping `outline` alongside
      `counts` rather than discarding it. The outline shape is `paper_guidance.
      segment_markdown`'s own `{"headings": [{"title", "level", "byte_start", "byte_end"}]}`.
      Callable and correct; proceeded per instruction without editing `paper_graph.py`.
- [x] 1.2 RED: add a failing test asserting `paper_cli._resolve_write_gate` returns the
      assembled `Corpus` rather than `None` (currently `-> None` at line ~1222, returning
      nothing after its `assemble_corpus(..., enforce_bindings=True)` call at line ~1253).
- [x] 1.3 Change `_resolve_write_gate`'s signature and body to return the `Corpus` it
      already builds; confirm every existing caller (`cmd_write`) still works with the
      returned value ignored where not yet consumed. Confirm 1.2 goes green.
- [x] 1.4 RED: add failing tests for `paper_source_span.resolve_bound_sections(corpus,
      qualified_block_id)` — a block's own `(fact, lineage, title)` triples resolve to
      `{"fact", "lineage", "title", "path", "byte_start", "byte_end", "text"}` entries,
      using `segment_markdown` offsets against a `bind`-recorded fixture; a block with no
      bindable measured fact returns `()`.
- [x] 1.5 Create `scripts/paper_source_span.py`: `resolve_bound_sections` CALLS the landed
      per-`(root, lineage)` memo/accessor from `paper_graph.py` (never re-resolves lineage
      or re-reads the marker itself) and slices `body.encode("utf-8")[byte_start:byte_end]`
      per matching heading. Confirm 1.4 goes green.
- [x] 1.6 If `paper_source_span.py` needs any import from `_core/implementation/` beyond
      what is already copied by `tests/paper_mutation.py`'s hardcoded core-file list
      (currently `impl_refusals.py` and `impl_layout.py` only — see `paper_mutation.py`
      lines 77-87), add that file to the mutation-sandbox copy list in the same commit.
      This is a known trap in this repository: a new production `_core` import not added
      there crashes every mutation test on import before any mutation is exercised.
      **Confirmed not needed**: `paper_source_span.py` imports only `paper_declarations`
      and `paper_graph` (sibling `scripts/` modules, already copied by `paper_mutation.py`'s
      own `SKILL_SCRIPTS.glob("*.py")` loop) and raises no `Refused` of its own, so it never
      touches `_core/implementation/` directly.
- [x] 1.7 Add `BlockContract.source_sections: tuple = ()` to `paper_write.py` (the
      `produces_facts`/`source_bindings` defaulting precedent). Confirm every existing
      `BlockContract(...)` construction site in tests stays green with no change.
- [x] 1.8 Wire `cmd_write`: call `paper_source_span.resolve_bound_sections(corpus,
      qualified_id)` and fill `BlockContract.source_sections` from the result. Resolution
      and disk reading stay in the CLI; `write_block` still receives plain text/tuples,
      never touching disk itself.
- [x] 1.9 RED-then-GREEN: add a `write_block` test asserting the envelope gains a
      `sourceFidelity` key reporting `{"status": "unmeasured"}` when `source_sections` is
      empty — mirroring `style_channel_report`'s own shape. No verdict logic yet (that is
      WU2); this phase only wires the plumbing and the `unmeasured` report.
      (`transposition-fidelity`, "Requirement: A Block With No Measured Bound Section
      Reports Unmeasured, Never Refused", scenario "A block with no bound section reports
      unmeasured".)
- [x] 1.10 Mutation: force `cmd_write` to always pass `source_sections=()` regardless of
      what `resolve_bound_sections` resolved; confirm the resolved-triple test (1.4/1.8)
      goes red, proving the resolved bindings actually have to arrive for anything to
      change. (This mutation is re-used, not duplicated, by WU2's own "resolved bindings
      really arrive" mutation once the verdict logic exists.)
- [x] 1.11 Generality sweep: `rg` under `.claude/skills/paper-writing/scripts/` and
      `tests/` for any block id, section title, document filename, paper id, or subject
      word belonging to the paper being written, introduced by this phase's new code,
      comments, or fixtures. Confirm zero matches. Confirmed: WU1's new/changed content
      (`paper_source_span.py`, the `paper_cli.py`/`paper_write.py` diffs, and this phase's
      own tests) introduces zero new invented literals — every fixture name it uses
      (`lumen-thesis`, `1. Intro`, `3. Something`, `formulation`) is a pre-existing invented
      fixture already established by `SourceSectionBindingWriteGateTests`/
      `BindCliEndToEndTests`, never a new one. `ForgeVocabularyDerivedGuardTests` (rule
      B, the widened derived denylist) still shows exactly the one disclosed pre-existing
      failure (`experimental-deliberation/SKILL.md`, "mechanisms"), unrelated to this
      phase and unchanged by it.
- [x] 1.12 Run `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_contract`;
      confirm green, no new failures beyond the known pre-existing baseline.
      Confirmed: `Ran 625 tests ... OK` (0 failures, 0 errors).

## Phase 2 — WU2: The threshold, the sibling check, and the wire into `write_block`

Design.md, Decisions B, C, D. Satisfies `transposition-fidelity` (new) —
"Requirement: The Verbatim Check Is A Sibling, Never An Extension Of The Style Tripwire",
"Requirement: The Threshold Self-Calibrates Against The Contract's Own Prose",
"Requirement: The Floor And Threshold Are Reported, Never Inferred Silently",
"Requirement: The Guard Fires Inside `write`, Before Substitution, Never Only From A
Read-Only Verb", "Requirement: Only A Transposition-Mode Block Is Checked, Mode Derived
From The Contract On Disk, Never Listed" — and `style-leak-detection` (modified) —
"Requirement: Overlap Reads Only The Recorded Sample Set" (the negative requirement this
sibling design must not violate).

**Threshold and floor (parallel-safe against 2.5-2.6 below)**

- [ ] 2.1 RED: add failing tests for `paper_leak.source_section_floor(contract_prose,
      section_text)` returning `overlap_against_set(contract_prose, [{"span":
      section_text}])` — reusing the shipped primitive verbatim, computing no new overlap
      logic.
- [ ] 2.2 Add `SOURCE_RUN_BACKSTOP = 16` and `source_section_floor` to `paper_leak.py`.
      Confirm 2.1 goes green.
- [ ] 2.3 RED: add failing tests for `check_source_section_verbatim(draft_latex,
      contract_prose, sections)`: per section, `threshold = max(floor, SOURCE_RUN_BACKSTOP)`;
      refuses `SOURCE_SECTION_VERBATIM` (naming the block, fact, lineage, section title,
      and offending span) on the first run STRICTLY exceeding threshold; returns the
      per-section report `{"lineage", "title", "floor", "threshold", "longest_run"}` when
      nothing exceeds. Cover: (a) verbatim paste refuses; (b) same claim in the paper's
      own register passes; (c) a run EQUAL to threshold passes (strict inequality only);
      (d) a contract-licensed forty-token floor makes the guard inert for that run.
- [ ] 2.4 Add `check_source_section_verbatim` to `paper_leak.py`, reusing
      `overlap_against_set` and `tripwire_spans` verbatim (never re-implementing the
      overlap/hit-scan machinery). Confirm 2.3 goes green.

**Mode derivation (parallel-safe against 2.1-2.4 above)**

- [ ] 2.5 RED: add a failing test asserting `paper_vocabulary.MODE_TRANSPOSITION ==
      "transposition"` and `MODE_ARGUMENT == "argument"` exist as named constants, and
      `MODES == (MODE_TRANSPOSITION, MODE_ARGUMENT)` (currently `MODES` at line 62 is a
      bare literal tuple `("transposition", "argument")` with no named constants backing
      it).
- [ ] 2.6 Add `MODE_TRANSPOSITION`/`MODE_ARGUMENT` to `paper_vocabulary.py`; compose
      `MODES` from them. Confirm no string literal for a mode is introduced into
      `paper_write.py` or `paper_leak.py` by this phase's own new code (checked by 2.15
      below, not assumed here).

**Wiring into `write_block` (sequential — depends on both groups above)**

- [ ] 2.7 RED: add a failing `write_block` integration test — a transposition-mode block
      (`contract.mode == paper_vocabulary.MODE_TRANSPOSITION`) with a bound section and a
      verbatim-pasting draft refuses `SOURCE_SECTION_VERBATIM` before `substitute` runs,
      and `main.tex` stays byte-identical to its pre-`write` state.
- [ ] 2.8 Wire the new stage into `paper_write.write_block`, placed AFTER the style
      tripwire call (`paper_leak.check_tripwire`, currently line 195) and BEFORE
      `style_channel_report`/`substitute` (currently lines 206/208) — so a draft failing
      both checks always names `STYLE_OVERLAP` deterministically (design.md, Data Flow).
      Guard the call on `contract.mode == paper_vocabulary.MODE_TRANSPOSITION`; lazily
      import `paper_leak` exactly as the style tripwire already does at line 194, so
      `paper_write.py` stays importable without it. Confirm 2.7 goes green.
- [ ] 2.9 RED-then-GREEN: add a test asserting a refusal here writes NOTHING to the
      on-disk attempt ledger (`_write_ledger` is only called on the audit-fired branch,
      lines 152-168 — this new stage runs strictly after that branch has already returned,
      so no code change should be needed here; the test exists to prove it, not to
      introduce new logic).
- [ ] 2.10 RED-then-GREEN: add a test asserting an `argument`-mode block with the
      IDENTICAL binding and an identical verbatim draft is never checked — no
      `SOURCE_SECTION_VERBATIM` refusal is possible regardless of overlap.
- [ ] 2.11 RED-then-GREEN: add a test asserting the `write` envelope reports
      `sourceFidelity: {"status": "measured", "sections": [...]}` for a PASSING
      transposition-mode block with at least one measured bound section — per-section
      floor, threshold, and longest observed run all present, whether or not the check
      refused (`transposition-fidelity`, "Requirement: The Floor And Threshold Are
      Reported, Never Inferred Silently").
- [ ] 2.12 Add one `REFUSAL_CLASSIFICATION` entry for `SOURCE_SECTION_VERBATIM` in
      `paper_cli.py` (`work-state` tier, per design.md's Refusal Codes table).
- [ ] 2.13 Update `.claude/skills/paper-writing/SKILL.md`: one roster entry for
      `SOURCE_SECTION_VERBATIM`, and a note on the new `write` stage's position (after
      contract-audit, beside and after the style tripwire, before `substitute`).
- [ ] 2.14 Mutation: the backstop alone (`SOURCE_RUN_BACKSTOP` in place of
      `max(floor, SOURCE_RUN_BACKSTOP)`); confirm the contract-licensed-floor test (2.3d)
      goes red — a licensed forty-token run wrongly refuses under the backstop alone.
      Restore.
- [ ] 2.15 Mutation: the floor alone (`floor` in place of `max(floor,
      SOURCE_RUN_BACKSTOP)`); confirm a near-zero-floor / six-token-idiom test goes red —
      a near-zero floor wrongly refuses a six-token idiom. Restore. (Add this idiom test
      first if 2.3 did not already cover it.)
- [ ] 2.16 Mutation: raise the refusal's own effective minimum far above any real draft
      length (for example `min_tokens=10_000` at the call site); confirm the verbatim-paste
      test (2.7) goes red, proving `SOURCE_SECTION_VERBATIM` is reachable under an
      unmutated implementation, not merely asserted never to fire. Restore.
- [ ] 2.17 Mutation: wire the guard only into a read-only verb (e.g. `phases`) and have
      `write_block` skip it; confirm the direct-`write` verbatim-paste test (2.7) fails —
      proving the guard is wired to the enforcing verb, not merely a reachable function.
      Restore.
- [ ] 2.18 Mutation: mutate the stage guard's own condition from `contract.mode ==
      MODE_TRANSPOSITION` to `contract.mode == MODE_ARGUMENT`; confirm BOTH the
      transposition-mode test (2.7) and the argument-mode test (2.10) go red — the
      transposition block that should be checked is no longer checked, and the argument
      block that should be exempt is now wrongly checked. Restore.
- [ ] 2.19 Generality sweep: `rg` under `.claude/skills/paper-writing/scripts/` and
      `tests/` for any block id, section title, document filename, paper id, or subject
      word introduced by this phase's new code, comments, docstrings, or fixtures. Confirm
      zero matches.
- [ ] 2.20 Confirm `check_tripwire`'s own bytes are unchanged by this phase (`git diff` on
      `paper_leak.py` shows only additions: `SOURCE_RUN_BACKSTOP`, `source_section_floor`,
      `check_source_section_verbatim` — no line inside `check_tripwire`/`tripwire_spans`/
      `overlap_against_set` moves). (`style-leak-detection`, "Requirement: Overlap Reads
      Only The Recorded Sample Set", scenario "A bound source section is never folded into
      `R`".)
- [ ] 2.21 Run `.venv/bin/python -m unittest tests.test_paper_writing`; confirm green, no
      new failures beyond the known pre-existing baseline.

## Phase 3 — WU3: Neutrality gate, roster re-measured, both suites

Satisfies the operator's own non-negotiable discipline items (generality, roster
measurement) plus design.md's Migration/Rollout note (nothing deleted, no format change).

- [ ] 3.1 Run `ForgeVocabularyDerivedGuardTests` (widened denylist, derived from every
      product root) as a **pre-apply-completion gate**: confirm it reports no NEW leak
      introduced by this change's own code, comments, docstrings, or fixtures across all
      three prior phases. Also run a plain `rg` sweep under
      `.claude/skills/paper-writing/scripts/` and the forge's own suite for any block id,
      section title, document filename, paper id, subject word, or revision-pattern
      literal belonging to the paper being written; confirm it comes back empty. Record
      the exact commands run.
- [ ] 3.2 Re-derive the refusal roster by EXECUTING `reachable_paper_refusal_codes()`
      after all engine code from WU0-WU2 has landed. Record the measured number in the
      final apply report. **Do not write a predicted number into any artifact before this
      task runs** — the live figure today is 144; the post-change figure is whatever this
      execution reports (`SOURCE_SECTION_VERBATIM` is the only new code this change adds
      to the roster).
- [ ] 3.3 Confirm `git diff main -- sections/` is empty (never edit any file under
      `sections/`) and that no file was deleted anywhere in the change (`git diff
      --stat main` shows only additions/modifications, zero deletions).
- [ ] 3.4 Record the falsification obligation from design.md, Decision C, verbatim into
      this change's own tracking (not silently dropped): the moment three real
      `document` bindings exist on disk, execute the two falsifiers — (a) a transposed
      draft in the paper's own register whose longest shared run with its bound section
      reaches 16 (implies 16 is too low); (b) a verbatim sentence pasted from the bound
      section whose normalized run is under 16 and passes (implies 16 is too high). Either
      observation moves exactly one named constant in `paper_leak.py`, nothing else. State
      that this obligation is unexecutable today (no real bindings exist) and is not being
      silently waived.
- [ ] 3.5 Run the full baseline in four chunks (per the project's own known ~650s discover
      time against a 600s foreground timeout): `npm test`, then
      `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` split into four
      foreground chunks as recorded in
      `openspec/changes/archive/2026-09-20-the-requirement-names-the-section-that-feeds-it/verify-report.md`.
      Confirm `npm test` is 640/640, and confirm the Python suite shows AT MOST the one
      known pre-existing failure
      (`test_proposal_implementation.ForgeVocabularyDerivedGuardTests.test_rule_b_finds_no_target_vocabulary_in_the_forge`,
      the generic-word-"mechanisms" baseline). **Any second failure belongs to this change
      and blocks delivery.**
- [ ] 3.6 Update `design.md`'s Open Questions section to mark the three ruled questions
      (A, C, E) as landed, and confirm the two "recorded, not folded in" items (content
      verification against a bound span; widening to `argument` mode; `_attempt_key` not
      resetting on a new source revision) are still explicitly named as out of scope,
      never silently resolved by this change.

## Key discipline carried forward, not to be reinterpreted at apply time

- Red first, every guard, every phase above.
- A mutation is the only proof a guard holds — every refusal code introduced here
  (`SOURCE_SECTION_VERBATIM`) has its own mutation tasks (2.14-2.18), not merely a
  passing-case test.
- Generality is a task, not an assumption — 0.13, 1.11, 2.19, 3.1 are each their own
  task, not a side effect of another task.
- The roster is measured, never forecast — 3.2 runs after the code lands; no number is
  written into any artifact before that.
- Nothing deletes files; never edit any file under `sections/` — checked explicitly at 3.3.
- WU0 gates WU1: `math-fence-blast-radius.md` must carry both executed tables (0.3, 0.10)
  before WU1's phase opens.
- The concurrency gate (1.1) is a stop-and-report instruction, not a suggestion: if
  `paper_graph.py`'s memo has not been widened to the outline shape by the concurrent
  change, WU1 halts and reports rather than re-implementing or editing `paper_graph.py`.
