# Tasks: The Requirement Names the Section That Feeds It

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~470 (U1+U2 ≈ 300, U3 ≈ 170) + U3b correctness repair (engine-only, well under budget) |
| 400-line budget risk | Medium |
| Chained PRs recommended | Yes |
| Suggested split | PR 1: Phase 1+2 (U1+U2, ~300) → PR 2: Phase 3+4 (DP+U3, ~170) |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending — ask the operator |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: Medium

Six refusal codes total, not four: `SECTION_NOT_IN_SOURCE`, `SECTION_TITLE_AMBIGUOUS`,
`SECTION_BINDING_ABSENT`, `SOURCE_LINEAGE_UNRESOLVED`, `SOURCE_REVISIONS_UNDECLARED`,
`MALFORMED_SOURCE_MARKER`. The last two, and the disjoint-key cross-check against
`guidance/`'s marker, are folded into Unit 2 (Phase 2) below; the line estimate is
unchanged from design.md, which already priced the marker reader in.

### Suggested Work Units

| Unit | Goal | PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 (U1) | `document` entry shape, inert | PR 1 | `.venv/bin/python -m unittest tests.test_paper_contract` | N/A — additive, no corpus edit yet | revert `paper_contract.py`/`paper_graph.py` diffs |
| 2 (U2) | Marker + lineage resolver + existence/ambiguity, inert without U3 | PR 1 | `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions` | N/A — no binding demanded yet | revert `paper_declarations.py`/`paper_graph.py` diffs |
| 2d (U2d) | `document.section` accepts one title or a non-empty list of unique titles (design.md Decision G) | PR 2 | `.venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing` | N/A — shape only, still optional | revert `paper_contract.py` diff |
| 3 (DP) | Owner rules on unanchorable entries | — | N/A — human decision | N/A | reversible; nothing lands until ruled |
| 4 (U3) | Obligation unconditional, corpus transcribed, `write` wired for all six codes | PR 2 | full suite (both, see 4.12) | `.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py write <bound-block-id>` | `git revert` U3's single commit |
| 5 (U3b) | Correctness repair: undecided is reported (`Corpus.undecided_bindings`), `SECTION_BINDING_ABSENT` refuses at `write` only; removes the two invented bindings U3's own apply transcribed under the unconditional-obligation trap | PR 2 (same branch, engine-only lines) | `.venv/bin/python -m unittest tests.test_paper_writing.SourceSectionBindingCorpusTests tests.test_paper_writing.SourceSectionBindingWriteGateTests tests.test_paper_writing.SourceSectionBindingWriteGateMutationProofTests` | `.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py write --section introduction --block block-4a --draft draft.json --audit audit.json` (refuses `SECTION_BINDING_ABSENT` before either file is opened) | `git revert` U3b's own commit(s); U3's transcribed bindings and fixtures are untouched |
| 7 (U3d) | Owner ruling (design.md Decision I): no binding is transcribed ahead of `write` asking for it. Removes all nine `document` bindings from `sections/*.md`; renames every suite fixture borrowing the proposal's own real lineage/paper-id spelling; widens `ForgeVocabularyDerivedGuardTests.derived_denylist` to derive from `proposals/`/`experiments/`/`guidance/` too | PR 2 (same branch) | `.venv/bin/python -m unittest tests.test_proposal_implementation.ForgeVocabularyDerivedGuardTests tests.test_paper_contract tests.test_paper_writing tests.test_paper_decisions tests.test_forge_scaffolding` | N/A — decontamination, no new runtime path | `git revert` U3d's own commit(s); `sections/*.md` return to their U2d state, the widened guard reverts to `implementations/`-only |
| 8 (U3e) | Owner ruling (design.md Decision J): U3d built a lock with no key. Adds the `bind` verb (`paper_declarations.bind_section`/`reopen_binding`/`read_bindings`, `paper_cli.cmd_bind`) that RECORDS a binding into `paper/`'s own `declarations` region; the corpus merges a recorded binding with any header-declared one (`paper_graph._reconcile_source_bindings`, `SOURCE_BINDING_CONFLICT` on disagreement); `SECTION_BINDING_ABSENT`'s own detail now names the block, fact, root, and every candidate lineage/revision/section-title read from disk (`describe_binding_candidates`); fixes the `guidance/` count test's machine-dependence (U3d left behind) | PR 2 (same branch); over budget as one unit, `size:exception` recommended | `.venv/bin/python -m unittest tests.test_paper_decisions.BindingRecordTests tests.test_paper_decisions.DescribeBindingCandidatesTests tests.test_paper_writing.RecordedSourceBindingCorpusTests tests.test_paper_writing.BindCliEndToEndTests tests.test_paper_writing.SourceSectionBindingWriteGateTests` | `.claude/skills/paper-writing/scripts/paper_cli.py bind --block <qualified-id> --fact <fact-id> --lineage <lineage> --section <title>` then `write` on the same block, real worked session in the apply report | `git revert` U3e's own commit(s); no `sections/*.md` byte is ever touched, `git diff main..HEAD -- sections/` stays empty |

## Phase 1 — U1: Entry shape, inert

- [x] 1.1 RED: add failing tests in `tests/test_paper_contract.py` for `section-contract` scenarios "A document binding parses", "A malformed document binding refuses", "A document binding on a declaration entry refuses".
- [x] 1.2 Add `_REQUIREMENT_OPTIONAL = ("document",)`, `_DOCUMENT_REQUIRED = ("lineage","section")` to `.claude/skills/paper-writing/scripts/paper_contract.py`; refuse `MALFORMED_HEADER` per 1.1; reject `document` on `requires_declarations` entries.
- [x] 1.3 Add `requirement_documents()` accessor to `.claude/skills/paper-writing/scripts/paper_contract.py`.
- [x] 1.4 Add `BlockRecord.source_bindings: tuple = ()` to `.claude/skills/paper-writing/scripts/paper_graph.py`; confirm every existing construction site stays green.
- [x] 1.5 Add bindable-fact derivation (sole test: key of `FACT_SOURCE_ROOT`) to `.claude/skills/paper-writing/scripts/paper_declarations.py`. Mutation: extend `FACT_SOURCE_ROOT` with a sixth root in a test fixture; assert bindable with zero engine edit.
- [x] 1.6 Run `.venv/bin/python -m unittest tests.test_paper_contract`; confirm 1.1 now green and the shipped corpus still assembles byte-identically.

## Phase 2 — U2: Resolution, inert without U3

**Marker grammar — `MALFORMED_SOURCE_MARKER`**

- [x] 2.1 RED: add failing marker-grammar tests in `tests/test_paper_writing.py` for `MALFORMED_SOURCE_MARKER` (non-UTF-8, non-JSON, non-object, missing `revisions`, missing `revision_prefix`/`ordinal_digits`, unknown key at either level, wrong-typed value).
- [x] 2.2 Add `read_revisions_marker()` to `.claude/skills/paper-writing/scripts/paper_declarations.py`; refuse `MALFORMED_SOURCE_MARKER` naming the offending file and key, per 2.1.
- [x] 2.3 Mutation: add a sixth key to a fixture marker; separately flip `ordinal_digits` to a string; confirm both refuse `MALFORMED_SOURCE_MARKER`.

**Disjoint-key cross-check with `guidance/`'s own marker (both directions)**

- [x] 2.4 RED: add a failing test asserting the source-root reader (`read_revisions_marker()`) refuses a `guidance/`-shaped marker (`{"class": "style-reference"}`), naming `revisions` as missing — `MALFORMED_SOURCE_MARKER`.
- [x] 2.5 RED: add a test asserting `.claude/skills/paper-writing/scripts/paper_guidance.py`'s existing `resolve_guidance_dir` reader refuses a source-root-shaped marker (`{"revisions": {...}}`) as an unknown key — `MALFORMED_GUIDANCE_MARKER`. This is a regression proof: `_MARKER_ALLOWED_KEYS = ("class",)` already excludes `revisions`, so no production edit is expected here — only the test is new.
- [x] 2.6 Run 2.4 and 2.5 green; confirm neither reader was widened to accept the other's key set (each refuses loudly on the other's shape, per `source-section-binding`'s disjoint-key requirement).

**Marker-driven resolution, no literal — generality**

- [x] 2.7 RED: add a failing test asserting a marker declaring `{"revisions": {"revision_prefix": "v", "ordinal_digits": 3}}` resolves lineage `lineage` to `lineage-v007.md` — the marker's own declared values drive resolution, never a literal.
- [x] 2.8 Confirm `resolve_lineage()` (2.14 below) composes its regex only from the marker's declared `revision_prefix`/`ordinal_digits`; `rg` under `.claude/skills/paper-writing/scripts/` confirms no revision-pattern literal governs resolution.

**Undeclared marker — `SOURCE_REVISIONS_UNDECLARED`**

- [x] 2.9 RED: add a failing test asserting a document-rooted root (contains `*.md`) carrying no `.paper-writing.json` marker refuses `SOURCE_REVISIONS_UNDECLARED` naming the root.
- [x] 2.10 RED: add a failing test distinguishing the two outcomes: a document-rooted root that HAD a marker, now deleted, MUST refuse `SOURCE_REVISIONS_UNDECLARED` — it MUST NOT degrade to the `unmeasured` report, which is reserved only for a root that is not document-rooted at all (e.g. `experiments/` holding only `.gitkeep`).
- [x] 2.11 Wire `SOURCE_REVISIONS_UNDECLARED` into `source_root_status()`/`_verify_source_section_bindings()` (`paper_declarations.py`/`paper_graph.py`): document-rooted + no marker refuses; only a non-document-rooted root reports `unmeasured`; these two outcomes are never collapsible.
- [x] 2.12 Mutation (design.md Testing Strategy): delete `proposals/.paper-writing.json` in the fixture root; confirm `SOURCE_REVISIONS_UNDECLARED` fires and the outcome is never `unmeasured`.

**Unmeasured-root report**

- [x] 2.13 RED: add failing `source_root_status()` tests (document-rooted; root holding only `.gitkeep`; root absent) for the `unmeasured` report.
- [x] 2.14 Add `source_root_status(base, root_name)` to `paper_declarations.py`; add `Corpus.source_roots: dict` to `.claude/skills/paper-writing/scripts/paper_graph.py`, echoed by every corpus-reading verb.

**Lineage resolution — `SOURCE_LINEAGE_UNRESOLVED`**

- [x] 2.15 RED: add failing `resolve_lineage()` tests — max ordinal, gap-tolerant, zero-candidate foreign lineage refuses, tie between two ordinal spellings refuses naming both candidates.
- [x] 2.16 Add `resolve_lineage(root, lineage, marker)` to `paper_declarations.py`; refuse `SOURCE_LINEAGE_UNRESOLVED` naming the lineage, the root, and every candidate found on zero or >1 matches.
- [x] 2.17 Mutation: rename the newest fixture revision to a foreign lineage (zero case); add `research-concept-r021.md` beside `research-concept-r21.md` (tie case); confirm both refuse, naming both candidates on the tie.

**Section existence/ambiguity — `SECTION_NOT_IN_SOURCE` / `SECTION_TITLE_AMBIGUOUS`**

- [x] 2.18 RED: add failing section existence/ambiguity tests against `segment_markdown` headings of a resolved fixture revision.
- [x] 2.19 Add `_verify_source_section_bindings()` to `paper_graph.py`, called once per `assemble_corpus`, memoizing one `{title: count}` per distinct `(root, lineage)`; refuse `SECTION_NOT_IN_SOURCE` / `SECTION_TITLE_AMBIGUOUS`.
- [x] 2.20 Mutation: rename the bound heading in a fixture revision (expect `SECTION_NOT_IN_SOURCE`); duplicate the bound heading (expect `SECTION_TITLE_AMBIGUOUS`).

**Source base and version-bump freedom**

- [x] 2.21 Add `source_base: Path | None = None` kwarg to `assemble_corpus` (default `sections_dir.parent`); add a synthetic `experiments/`-only-`.gitkeep`-style fixture proving unmeasured with zero edits to any existing minimal fixture.
- [x] 2.22 Integration test: fixture adds a `…-r22.md` revision preserving a bound title; assert the corpus assembles byte-identically untouched (success criterion 4).
- [x] 2.23 Run `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions`; confirm green; bindings still optional (U3 not landed).

## Phase 2d — U2d: A binding may name more than one section (shape only)

- [x] 2d.1 RED: add failing tests in `tests/test_paper_contract.py` for `document.section` accepting a non-empty list of unique titles; and for an empty list, a repeated title, and a non-string list entry each refusing `MALFORMED_HEADER` naming `section`.
- [x] 2d.2 Widen `_validate_document_object` in `.claude/skills/paper-writing/scripts/paper_contract.py`: `section` accepts a non-empty string (unchanged) or a non-empty list of unique non-empty-string titles; reuses `MALFORMED_HEADER`, no new code.
- [x] 2d.3 Widen `requirement_documents()` to expand a list-shaped `section` into one `(fact_id, lineage, title)` triple per title, in declaration order; a single-string `section` still contributes exactly one triple.
- [x] 2d.4 RED: add a failing integration test in `tests/test_paper_writing.py` asserting a binding naming two sections resolves both, and that one missing title among several refuses `SECTION_NOT_IN_SOURCE` naming only that title (the resolvable sibling does not mask it). Confirm `_verify_source_section_bindings` needs zero changes — the per-triple loop already covers this once `requirement_documents` expands the list.
- [x] 2d.5 Mutation: collapse the list expansion to its first title only; confirm the multi-title test goes red.
- [x] 2d.6 Update `specs/section-contract/spec.md` and `specs/source-section-binding/spec.md` for the widened shape and per-title resolution; update `design.md` (Decision G, Work Units table, `BlockRecord.source_bindings` docstring note).
- [x] 2d.7 Run `.venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing tests.test_paper_decisions`; confirm green; re-derive `reachable_paper_refusal_codes()` and confirm it is still 139 (no new code).

## Phase 3 — DP: Owner decision point (BLOCKING, before Phase 4)

- [x] 3.1 Scan every bindable `requires_facts` entry across ALL shipped contracts (not only `01`/`02` — `03` through `10` also carry bindable `formulation`/`dataset` entries once `dataset` is `INGESTED`-kind, per U2c) against `proposals/research-concept-r21.md` and the ingested evidence document under `guidance/data-paper/` (read-only); list every entry, its derived candidate section(s), and its confidence.
- [x] 3.2 Report the full table to the owner (see apply-progress / final report). Three bindings were already ruled by the owner (`mm-borrowed-machinery`, `mm-proposal`, `lim-proposal-items`); the remainder were derived from each block's own contract prose and transcribed at medium-to-high confidence; none were left unanchorable — every bindable+measured entry now carries a binding. `experimental-design`/`implementation`/`results` entries carry no obligation (root unmeasured or `REPOSITORY`-kind) and were left untouched.

## Phase 4 — U3: Obligation unconditional, atomic (single commit)

- [x] 4.1 RED: add a failing test for `SECTION_BINDING_ABSENT` on a bindable entry carrying no `document` half.
- [x] 4.2 Wire `SECTION_BINDING_ABSENT` unconditionally into `_verify_source_section_bindings()` for every bindable entry.
- [x] 4.3 Mutation: delete the `document` half from one shipped entry (fixture-level: remove the absence check itself); confirm `SECTION_BINDING_ABSENT` fires.
- [x] 4.4 Transcribe real bindings into `sections/01-materials-and-methods.md`, `02-experimental-setup.md`, `04-limitations.md`, `06-introduction.md`, `08-abstract.md` per the Phase-3 table, prose bytes untouched; distinguish `mm-borrowed-machinery` (sections 1-2) from `mm-proposal` (sections 3-5) against `proposals/research-concept-r21.md` (read-only).
- [x] 4.5 Create `proposals/.paper-writing.json`: `{"revisions":{"revision_prefix":"r","ordinal_digits":2}}`.
- [x] 4.6 RED: add failing `write`-gate tests for ALL SIX codes reaching `write` through its own corpus assembly: `SECTION_NOT_IN_SOURCE`, `SECTION_TITLE_AMBIGUOUS`, `SECTION_BINDING_ABSENT`, `SOURCE_LINEAGE_UNRESOLVED`, `SOURCE_REVISIONS_UNDECLARED`, `MALFORMED_SOURCE_MARKER` — each refuses before the draft stage runs, `main.tex` stays byte-identical. Also added `EVIDENCE_ROOT_AMBIGUOUS` (U2c amendment, reconciled into `writing-orchestration` spec).
- [x] 4.7 Confirmed `_resolve_write_gate` already calls `paper_graph.assemble_corpus` unconditionally as its first statement — the SAME corpus assembly `_verify_source_section_bindings` raises all seven codes from, so no additional wiring was needed for the refusals themselves. Did not change `_resolve_write_gate`'s return signature: nothing consumes a returned corpus (no `source_roots` echo is required by any spec scenario), so a "return the corpus" change would be untested scope creep; noted as a deviation in the final report.
- [x] 4.8 Confirm `write` refuses `SOURCE_REVISIONS_UNDECLARED` specifically: a document-rooted root missing its marker, invoked directly via `write` (never only via `phases`) — the marker codes reach `write` through the same corpus assembly as the binding codes.
- [x] 4.9 Mutation: remove `_resolve_write_gate`'s own call to `assemble_corpus` from `cmd_write` (its only path to that assembly — `assemble_packet` never assembles a corpus); confirm direct-`write` tests fail for both the binding-code family (`SECTION_NOT_IN_SOURCE`, `SECTION_BINDING_ABSENT`) and the marker-code family (`SOURCE_REVISIONS_UNDECLARED`), proving the wiring-gap mutation this guard must survive.
- [x] 4.10 Generality check: `rg` under `.claude/skills/paper-writing/scripts/` for `research-concept`, `MIL-CREDA`, `s41597`, `Rényi`, section titles, and every new block id; zero NEW matches (pre-existing illustrative block-id mentions in comments predate this unit and are untouched).
- [x] 4.11 Re-derive the refusal roster with `reachable_paper_refusal_codes()`; measured **140** (up from 139 after U2c/U2d).
- [x] 4.12 Ran `npm test` (640/640) AND `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` (4225 tests, 1 failure — the same known pre-existing `test_proposal_implementation.ForgeVocabularyDerivedGuardTests.test_rule_b_finds_no_target_vocabulary_in_the_forge`, 3 skipped) from the repository root; confirmed zero new failures.

## Phase 5 — U3b: Correctness repair, undecided is reported not invented

U3's own apply agent faced exactly the trap `4.2` created: two entries had no owner-ruled or
confidently-derived section, and the unconditional obligation left it invent-or-break. It invented
(`introduction.block-4a`, `abstract.slot-3`, both flagged low-confidence in its own report). This
phase removes the invention and closes the trap at its source: `SECTION_BINDING_ABSENT` refuses only
where drafting actually depends on knowing the section — `write` — and reports `undecided`
everywhere else, mirroring `source_roots`'s own report shape.

- [x] 5.1 RED: add a failing test asserting a bindable, measured, unbound entry's `assemble_corpus()` call (no `enforce_bindings`) raises NOTHING and reports the entry in `Corpus.undecided_bindings` (`{"state": "undecided", "root": ...}`); confirm it fails against the still-unconditional U3 code before any production edit.
- [x] 5.2 Add `Corpus.undecided_bindings: dict` and `_compute_undecided_bindings()` to `paper_graph.py`, computed before `Corpus` is constructed (a frozen dataclass has nowhere to gain a field after the fact); add `assemble_corpus`'s `enforce_bindings: bool = False` kwarg, threaded into `_verify_source_section_bindings`, which raises `SECTION_BINDING_ABSENT` (naming the same block/fact the old unconditional loop would have named first) only when `enforce_bindings=True`.
- [x] 5.3 Wire `enforce_bindings=True` into `paper_cli._resolve_write_gate`'s own `assemble_corpus` call — the ONLY call site in the skill that passes it; every other call site (`cmd_contract`, `compute_phases`, `cmd_plan`, and `_resolve_write_gate`'s own siblings) keeps the default.
- [x] 5.4 Move the assembly-time `SECTION_BINDING_ABSENT` test (task 4.1) into the read-time `undecided` assertion (5.1); the pre-existing `write`-gate test (`SourceSectionBindingWriteGateTests.test_write_refuses_section_binding_absent`, task 4.6) already proves the refusal at `write` and needed no change. A moved test, never a deleted one.
- [x] 5.5 Retarget the mutation proof (task 4.3's `test_mutation_removing_the_absence_check_lets_an_unbound_fact_pass`) through `cmd_write` (`SourceSectionBindingWriteGateTests.test_write_refuses_section_binding_absent`) rather than the now-nonraising assembly path; confirm it still fails under the mutation.
- [x] 5.6 Remove the two invented `document` halves from `sections/06-introduction.md` (`block-4a`) and `sections/08-abstract.md` (`slot-3`); verify prose bytes below the JSON header are byte-identical to `HEAD` for both files, and that no other block's binding changed.
- [x] 5.7 Update `design.md` (Decision H), `specs/source-section-binding/spec.md` (undecided requirement/scenarios), and `specs/writing-orchestration/spec.md` (write-only reachability note + scenario) to describe the corrected behaviour; a spec still demanding the assembly-time refusal would contradict the code.
- [x] 5.8 Re-derive the refusal roster with `reachable_paper_refusal_codes()`; confirm it stays **140** — the raise site is still a static AST scan target, only WHEN it fires changed.
- [x] 5.9 Generality check: `rg` under `.claude/skills/paper-writing/scripts/` for the paper's own subject words, section titles, and block ids in every new comment/docstring this phase adds; zero new matches.
- [x] 5.10 Report the corpus's remaining nine bindings to the owner, marked owner-ruled vs agent-derived, so the owner may strike any of them; remove none beyond the two named in 5.6. **Superseded by Phase 7 (U3d) below**: the owner ruled that none of the nine survive, including the three settled in conversation about a table — see design.md Decision I.
- [x] 5.11 Ran `.venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing tests.test_paper_decisions` (732/732, green) AND the full baseline (`npm test`; `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`); confirmed zero new failures beyond the known pre-existing one.

## Phase 6 — U3c: A second prose root is proven by fixture, not waived for being empty

The design's own stated risk — "generality over `experiments/` rests entirely on a synthetic
fixture" — was recorded but never discharged: every full-path test (marker read, lineage
resolution, section existence/ambiguity, the `undecided`/`write` tier boundary) ran only against
`proposals`, the one `PROSE`-kind root this checkout happens to populate. Tests only; zero engine
edits landed or were needed.

- [x] 6.1 Add `SecondProseRootGeneralityTests` (`tests/test_paper_writing.py`) driving the full
      corpus-assembly path — marker read, lineage resolution, section existence/ambiguity,
      multi-title binding, the `unmeasured`/`SOURCE_REVISIONS_UNDECLARED` distinction, and the
      read-time `undecided` report — against `experiments` (the second `PROSE`-kind root
      `FACT_SOURCE_ROOT` already declares), using an invented lineage (`field-log`) and invented,
      generic section titles at a marker width (3 digits) that is deliberately not the live root's
      own (2).
- [x] 6.2 Add `SecondProseRootWriteGateTests`, proving the `write`-only `SECTION_BINDING_ABSENT`
      tier boundary (U3b, Decision H) through the REAL `cmd_write` root against this second root,
      mirroring `SourceSectionBindingWriteGateTests.test_write_refuses_section_binding_absent`.
- [x] 6.3 RED: for each behaviour, mutate the engine and confirm the corresponding new test on
      this second root goes red before it is trusted green — marker-declared width overriding the
      live root's own default (`digits = marker["ordinal_digits"]` → `digits = 2`), highest-ordinal
      selection (`max` → `min`), multi-title masking (`paper_contract.requirement_documents`'s list
      expansion collapsed to its first title), the undeclared-marker guard (`if marker is None:` →
      `if False:`), and the `write`-gate absence check (`if fact_id not in bound_fact_ids:` →
      `if False:`) — six mutation runs total, all confirmed red under mutation and green on the
      unmutated engine.
- [x] 6.4 Generality check: `rg` under `.claude/skills/paper-writing/scripts/` for every invented
      fixture word this phase adds (`field-log`, its section titles); zero matches — the engine
      remains untouched.
- [x] 6.5 Update `design.md` (Decision C) to record the risk as discharged, with what discharged
      it, and add a Work Units row for U3c.
- [x] 6.6 Ran `.venv/bin/python -m unittest tests.test_paper_writing.SecondProseRootGeneralityTests tests.test_paper_writing.SecondProseRootWriteGateTests` (13/13, green) AND the full baseline
      (`npm test`: 640/640; `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`);
      confirmed zero new failures beyond the known pre-existing one.

## Phase 7 — U3d: The forge carries no paper of its own

The owner ruled on all nine `document` bindings U3/U3b transcribed into shipped section contracts:
none survive, not even the three settled in conversation about a table (`mm-borrowed-machinery`,
`mm-proposal`, `lim-proposal-items`) — a decision taken in conversation is not a decision taken by
using the skill, and the only moment that decision belongs to is `write` asking for it. This phase
also closes the blindness that let it happen: `ForgeVocabularyDerivedGuardTests.derived_denylist`
derived its denylist from `implementations/` alone.

- [x] 7.1 Remove all nine `document` bindings from `sections/01-materials-and-methods.md`,
      `02-experimental-setup.md`, `04-limitations.md`, `06-introduction.md`, `08-abstract.md` by
      restoring each file to its `main` content (`git checkout main -- sections/...`); confirmed
      `git diff main -- sections/` is empty and `rg -n -i 'MIL.?CREDA|research-concept|s41597|Rényi
      |Renyi' sections/*.md` returns nothing.
- [x] 7.2 Rename every suite fixture across `tests/test_paper_contract.py`, `test_paper_writing.py`,
      `test_paper_decisions.py` that had borrowed the proposal's own real lineage
      (`research-concept` → `lumen-thesis`) or the ingested paper's own real id
      (`s41597-026-06758-7` → `q77213-004-11029-2`) or the evidence folder's own real name
      (`data-paper` → `source-manuscript`); left the two assertions in
      `test_paper_decisions.py::GuidanceRegistryTests.test_against_the_real_shipped_guidance_tree`
      and `SourceDatasetRootTests.test_dataset_root_name_is_never_the_paper_specific_folder` that
      legitimately assert against the real shipped tree unchanged, genericizing only their
      docstrings' literal restatement of the same real name.
- [x] 7.3 RED: widen `tests.test_proposal_implementation.ForgeVocabularyDerivedGuardTests` with
      `paper_product_root_words()`, deriving vocabulary from `paper_declarations.FACT_SOURCE_ROOT`'s
      `PROSE`/`INGESTED` roots (`proposals/`, `experiments/`, whichever `guidance/` folder
      `paper_guidance.read_registry` classes `evidence`) and merge it into `derived_denylist()`;
      confirmed red against the pre-7.1/7.2 tree (`experimental-deliberation`'s hardcoded
      `guidance/data-paper` plus every occurrence 7.1/7.2 later cleaned).
- [x] 7.4 Measured: splitting a live lineage/evidence-folder/paper-id name into parts (mirroring
      `target_words`) put ordinary English nouns (`data`, `paper`, `concept`, `research`) on the
      denylist and reported ~70 shipped files as leaking, none an actual mention of either real name;
      only the UNDIVIDED compound is derived.
- [x] 7.5 Isolate `derived_denylist`'s two existing exact-list/skip assertions
      (`test_rule_b_names_the_file_and_the_word_a_planted_leak_is_in`,
      `test_a_clone_with_no_target_skips_instead_of_passing`) from this checkout's own real
      `proposals/`/`guidance/` content via the new `forge_root` parameter, defaulting to `FORGE`
      everywhere else.
- [x] 7.6 Add `scratch_paper_product_root()` and three reachability tests: derivation proves
      compound-only (never split parts), a planted mention in a scratch shipped file is named by
      file and word (mutation-shaped proof mirroring `test_rule_b_names_the_file_and_the_word_a_
      planted_leak_is_in`), and an `implementations/`-less clone with a live paper product root does
      NOT skip (the OR half of the skip condition).
- [x] 7.7 Fix the two genuine leaks the widened guard found inside `paper-writing`'s own shipped
      surface: `.claude/skills/paper-writing/SKILL.md`'s illustrative folder-name list named the real
      evidence folder (`data-paper`) as if it were a generic example; `tests/test_forge_scaffolding.py`'s
      module docstring named the same real folder in a historical-incident narrative. Both
      genericized without changing any assertion.
- [x] 7.8 Report two further hits the widened guard found and did NOT fix, judged collisions/
      out-of-scope rather than leaks belonging to this change: `experimental-deliberation/profile.ts`'s
      hardcoded `const DATA_PAPER = "guidance/data-paper"` (a real architectural leak in a DIFFERENT
      skill's engine, needing the same registry-derived repair Decision F gave `paper-writing`'s own
      `dataset` fact — out of scope/budget here); `proposal-deliberation/profile.ts`'s `stem:
      "research-concept"` (that skill's own sanctioned single point of per-project configuration, not
      a leak) and the pervasive `research-concept-rNN.md` worked-example convention across
      `proposal-deliberation`'s and `proposal-implementation`'s `references/usage.md` (dozens of
      lines, pre-existing, already a partially-tracked doctrine question unrelated to
      `source-section-binding`). Recorded in design.md's Open Questions for the owner to rule on.
- [x] 7.9 Update `design.md` (new Decision I, File Changes table, Work Units table, Open Questions)
      and this file so no artifact still claims the shipped corpus carries a transcribed binding.
- [x] 7.10 Ran `.venv/bin/python -m unittest tests.test_proposal_implementation.ForgeVocabularyDerivedGuardTests`
      (21/21, green) AND `tests.test_paper_contract tests.test_paper_writing tests.test_paper_decisions
      tests.test_forge_scaffolding` (748/748, green) AND the full baseline (`npm test`;
      `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`); confirmed the ONLY
      `test_proposal_implementation` failure is the SAME `test_rule_b_finds_no_target_vocabulary_in_
      the_forge` test as the pre-existing `mechanisms` baseline, now additionally naming the two
      reported-not-fixed collisions from 7.8 — zero failures beyond those, zero new failing test
      methods.

## Phase 8 — U3e: The skill records the binding it demands

U3d built a lock (`SECTION_BINDING_ABSENT`) and no key: nothing in the skill could record a
binding once all nine transcribed ones were removed, and the only way to answer the refusal was
still a hand edit to `sections/*.md` — exactly the act Decision I ruled out. The owner's rule: a
binding is decided by USING the skill, never by editing a file or by an agent reading prose.

- [x] 8.1 RED: added failing tests for `paper_declarations.bind_section`/`reopen_binding`/
      `read_bindings` (`tests/test_paper_decisions.py::BindingRecordTests`, 14 tests) and
      `describe_binding_candidates` (`DescribeBindingCandidatesTests`, 3 tests); confirmed all 14
      of the former failed with `AttributeError: module 'paper_declarations' has no attribute
      'bind_section'` before any production edit.
- [x] 8.2 Added `bind_section`/`reopen_binding`/`read_bindings`/`describe_binding_candidates`/
      `_binding_record_id`/`_heading_titles` to `.claude/skills/paper-writing/scripts/
      paper_declarations.py` — a THIRD `declarations`-region record kind (`binding`, keyed by
      `{block}::{fact}`), reusing `paper_region.py`'s existing region machinery, never a second
      store. Refuses `UNKNOWN_FACT` (reused), `BINDING_FACT_NOT_BINDABLE`, `BINDING_LINEAGE_
      REQUIRED`, `BINDING_SECTIONS_REQUIRED`, `DECLARATION_FIXED` (reused).
- [x] 8.3 Ran 8.1's tests green (17/17).
- [x] 8.4 RED: added failing tests asserting the corpus reads a recorded binding with no header
      half (`tests/test_paper_writing.py::RecordedSourceBindingCorpusTests`); confirmed red before
      any production edit (`AssertionError: ('formulation', 'lumen-thesis', '3. Something') not
      found in ()`).
- [x] 8.5 Added `assemble_corpus`'s `paper_dir` kwarg and `_reconcile_source_bindings` to
      `.claude/skills/paper-writing/scripts/paper_graph.py`: merges `paper_declarations.
      read_bindings` per block with `paper_contract.requirement_documents`'s own header triples;
      refuses `SOURCE_BINDING_CONFLICT` naming the block, the fact, and both sides' values when
      both name the same fact and disagree.
- [x] 8.6 RED-then-GREEN: added a disagreement test and its mutation proof (collapsing the
      conflict comparison to `if False:`), confirming the mutation goes red under
      `tests.test_paper_writing.RecordedSourceBindingCorpusTests
      .test_a_recorded_binding_disagreeing_with_the_header_refuses` and green on the unmutated
      engine.
- [x] 8.7 RED: added a failing test asserting `SECTION_BINDING_ABSENT`'s own detail names the
      block, fact, root, the CURRENT (highest-ordinal) revision only, and every section title that
      revision holds, read from disk (`SourceSectionBindingWriteGateTests
      .test_section_binding_absent_names_the_block_fact_root_and_candidates`).
- [x] 8.8 Added `_describe_binding_absent` (`paper_graph.py`) calling `paper_declarations.
      describe_binding_candidates`, wired into `_verify_source_section_bindings`'s own
      `enforce_bindings` branch; the refusal now also names the exact `bind` invocation that
      answers it. Ran 8.7 green.
- [x] 8.9 Mutation: reverted the refusal detail to U3's own bare message; confirmed 8.7's test
      goes red under the mutation and green on the unmutated engine
      (`test_mutation_reverting_the_refusal_detail_to_bare_fails_the_candidates_test`).
- [x] 8.10 Added `paper_cli.cmd_bind`, a new `bind` argparse subparser, registered `bind` in
      `COMMANDS`/`_COMMANDS`, and four new `REFUSAL_CLASSIFICATION` entries. `_resolve_write_gate`
      now passes `paper_dir=paper_dir` explicitly to `assemble_corpus`.
- [x] 8.11 RED-then-GREEN: added `tests/test_paper_writing.py::BindCliEndToEndTests` (4 tests) —
      the full worked session (`write` refuses `SECTION_BINDING_ABSENT`, `bind` records the
      answer, `write` no longer refuses it), plus `--reopen`, plus both invocation-defect refusals;
      confirmed red (`AttributeError: module 'paper_cli' has no attribute 'cmd_bind'`) before the
      CLI wiring, green after.
- [x] 8.12 Fixed a mutation-anchor collision `describe_binding_candidates` introduced (a duplicate
      `digits = marker["ordinal_digits"]` line broke `SecondProseRootGeneralityTests
      .test_mutation_hardcoding_the_live_roots_default_width_breaks_this_roots_resolution`'s own
      anchor-uniqueness assumption) by renaming the new function's local variables
      (`marker_prefix`/`marker_digits`); confirmed no other anchor collisions across the full
      `tests.test_paper_contract tests.test_paper_writing tests.test_paper_decisions` run (772/772
      green).
- [x] 8.13 Fixed the `guidance/` count test U3d left machine-dependent
      (`tests/test_paper_decisions.py::GuidanceRegistryTests
      .test_against_the_real_shipped_guidance_tree`): `len(registry["data-paper"]) == 1`,
      `total_papers == 8` etc. depend on this checkout's own ambient, gitignored content — `git
      ls-files guidance/` shows only five `.gitkeep` files travel, so those exact counts are false
      on a fresh clone. Rewrote to assert the PROPERTY (the four tracked root folders, and that
      `ingested_papers` matches an independently-taken, gitignore-blind `Path.iterdir()` walk of
      the SAME real tree at test time) rather than fixed counts; confirmed the property holds both
      against this machine's real ambient content and against a simulated fresh-clone tree (every
      root empty except `.gitkeep`).
- [x] 8.14 Generality check: `rg` under `.claude/skills/paper-writing/scripts/` for the proposal's
      own lineage/paper-id/section-title literals; zero matches. `git diff main..HEAD --
      sections/` returns empty.
- [x] 8.15 Update `design.md` (new Decision J, Refusal Codes table, File Changes table, Interfaces,
      Work Units table, Migration/Rollout note), `specs/source-section-binding/spec.md` (two new
      Requirements: recording, and the header/recorded merge conflict), `specs/writing-
      orchestration/spec.md` (one new Requirement: the refusal names its own next action), and
      this file.
- [x] 8.16 Re-derived the refusal roster with `reachable_paper_refusal_codes()`; measured **144**
      (up from 140) — `BINDING_FACT_NOT_BINDABLE`, `BINDING_LINEAGE_REQUIRED`, `BINDING_SECTIONS_
      REQUIRED` (via the new `cmd_bind` root) and `SOURCE_BINDING_CONFLICT` (via `paper_graph.py`,
      already imported).
- [x] 8.17 Ran `.venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing
      tests.test_paper_decisions tests.test_forge_scaffolding
      tests.test_proposal_implementation.ForgeVocabularyDerivedGuardTests` AND the full baseline
      (`npm test`; `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`); confirmed zero
      new failures beyond the known pre-existing `mechanisms`/collision baseline.
