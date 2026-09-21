# Tasks: The Block Asserts Only What Its Section Carries

> **Measured, not inherited, 2026-09-21.** `openspec/specs/transposition-grounding/spec.md`
> holds **9 Requirements, 24 Scenarios** — counted directly off the file for this
> phase, not taken from the spec phase's own claimed 27 or from design.md's
> unverified assertion. Every `file:line` below was re-read today. The sibling
> `the-redactor-receives-the-section-it-must-transpose` has **not landed**:
> `RedactorInput` still has 4 fields (`paper_bindings.py:40-44`) and
> `assemble_packet` still takes no `corpus`/`paper_dir` kwargs
> (`paper_cli.py:2052`) — confirmed by direct read, not by the sibling's own
> proposal/design existing. Phase 0's first task blocks on this.

## Review Workload Forecast

Owner accepted `size:exception` up front; engine-line ceiling **1600** lines
under `.claude/skills/`. Own estimate below is close to, and slightly under,
the proposal's own ~1400-line forecast — both are planning guides, not exact
diff counts.

| Unit | Engine lines (est.) | Test lines (est.) | Docs/agent lines (est.) | Unit total | Running total | Against 1600 |
|---|---|---|---|---|---|---|
| WU1 — ordering gate, thread bindings, subject intersection, interim `unmeasured` envelope | ~90 (`paper_write.py` one-line fix + kwarg; `paper_grounding.py` skeleton + `subjects_for`) | ~130 (intersection scenarios, interim-envelope test, gate confirmation) | ~10 | ~230 | 230 | Low |
| WU2 — `reconcile_support`, four refusals, `source_grounding_report`, full `write_block` wiring | ~220 | ~270 (burden-of-proof, both downgrades, both directions, undecidable-vs-downgraded, ordering, scope boundary) | 0 | ~490 | 720 | Low-Medium |
| WU3 — agent file, `--grounding`, import row, `REFUSAL_CLASSIFICATION`, SKILL.md/references | ~60 (`paper_cli.py` wiring, import row, classification) | ~40 (CLI wiring test) | ~150 (`section-grounding-auditor.md`, roster rows, falsifier sentence) | ~250 | 970 | Low-Medium |
| WU4 — 4 mutation proofs, neutrality sweep, roster re-measure, both suites | 0 (no new engine code expected) | ~110 (four mutation tests) | ~40 (falsifier obligation record, roster figure) | ~150 | 1120 | Low |

**Engine lines under `.claude/skills/`: ~370 (90 + 220 + 60 + 0) against the
owner's 1600 ceiling — LOW risk.** Estimated total across all files, tests and
docs included: ~1120-1450.

Corrected by the orchestrator: this section previously read "~1120-1450 against
the 1600 budget — Medium risk", comparing the TOTAL changed-line estimate
against a ceiling the owner defined four separate times as engine lines only —
code under `.claude/skills/`. Tests, fixtures, agent files and documentation do
not count toward it. The per-unit columns above were already separated
correctly; only the conclusion mixed them, and mixing them reported Medium
where the measured engine figure is Low. `design.md`'s own call inherits the
same conflation and should be read against this correction.

Against the DEFAULT 400-line review budget the total remains High, and every
unit individually exceeds it — which is precisely what the owner's accepted
`size:exception` covers. The four slices ship as chained commits under it.

```
Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: size-exception
400-line budget risk: High
```

## Suggested Work Units

| Unit | Goal | Depends on | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| WU1 | Ordering gate confirmed; `_stage_evidence_audit`'s return captured; `paper_grounding.subjects_for` (the D3 intersection); interim `sourceGrounding: unmeasured` envelope | Sibling `the-redactor-receives-the-section-it-must-transpose` landed (0.1 blocks otherwise) | `.venv/bin/python -m unittest tests.test_paper_writing` (subject-intersection class once named) | N/A — no real `document`-rooted binding exists on disk (`transposition-fidelity/spec.md:28-34`); every scenario is a `bind`-recorded fixture, invented names only | `git revert` WU1's commit(s); `paper_write.py:159` reverts to the bare statement, `paper_grounding.py` is deleted, `write_block`'s new kwarg is defaulted so untouched callers stay green either way |
| WU2 | `reconcile_support`, the four refusals, `source_grounding_report`, full guard wired into `write_block` after the verbatim check and before `substitute` | WU1 landed | `.venv/bin/python -m unittest tests.test_paper_writing` (reconciliation class) | N/A — same synthetic boundary as WU1 | `git revert` WU2's commit(s); `sourceGrounding` is a new envelope key, so reverting drops it cleanly with no prior format touched |
| WU3 | `.claude/agents/section-grounding-auditor.md`; `--grounding` CLI wiring; import row; `REFUSAL_CLASSIFICATION`; SKILL.md/references roster + delegation phrase + D2 falsifier | WU2 landed | `.venv/bin/python -m unittest tests.test_paper_writing tests.test_agents` | N/A — agent is never invoked by code (D9); wiring test uses a recorded fixture, never a live agent call | `git revert` WU3's commit(s); import row + classification + roster rows removed together in one commit so the count locks stay consistent (design.md, Migration/Rollout) |
| WU4 | Four mutation proofs (one per code, on four distinct anchor lines); neutrality/generality sweep; roster re-measured live; both suites green | WU3 landed | Full suite (3.9) | N/A — mutation harness runs against a temp-tree copy, never a real invocation | No engine code to revert; test-only, reverting drops the mutation/sweep tests and the updated roster literal |

## Phase 0 — WU1: Ordering gate; thread the discarded bindings; subject intersection; interim `unmeasured` envelope

Satisfies `transposition-grounding`, "Requirement: The Subject Set Is An
Intersection Derived From Bytes, Never A List" (all 5 scenarios) and the
`subjects == 0` half of "Requirement: A Block With No Decided Subject Reports
Unmeasured, Never A Silent Pass".

- [x] 0.1 **Ordering gate — read this before touching any file.** Confirm
      `the-redactor-receives-the-section-it-must-transpose` has landed by
      reading two files directly: `paper_bindings.py` (`class RedactorInput`,
      `:40-44`) must declare a fifth field `source_sections: tuple = ()`
      beside `contract_prose`/`evidence_set`/`mode`/`style_set`; and
      `paper_cli.py` (`def assemble_packet`, `:2052`) must accept keyword
      params `corpus=None, paper_dir=None` and its return dict must gain
      `source_sections`/`source_sections_state` keys. **If either check
      fails, STOP and REPORT** — do not implement the sibling change
      yourself; this task's whole obligation is confirming the seam already
      exists (design.md, "The seam with its sibling"; "Apply blocks on the
      sibling being landed; it does not race it"). Measured today
      (2026-09-21): **NOT landed** — `RedactorInput` has 4 fields,
      `assemble_packet` takes no `corpus`/`paper_dir`, and
      `openspec/changes/the-redactor-receives-the-section-it-must-transpose/`
      has no `tasks.md`.
- [x] 0.2 RED: add a failing test asserting `write_block` (`paper_write.py`)
      actually consumes `_stage_evidence_audit`'s return value — spy or count
      that the `list[Binding]` it produces reaches a later step, against a
      fixture with at least one bound sentence. Confirm it fails against the
      current bare-statement call at `:159`.
- [x] 0.3 Fix `paper_write.py:159`: `_stage_evidence_audit(contract, draft)`
      → `bindings = _stage_evidence_audit(contract, draft)`. No signature
      change — it already returns `list` (`:121`, `return bindings` at
      `:129`) and has exactly this one caller. Confirm 0.2 goes green.
- [x] 0.4 Add `grounding_account: dict | None = None` as a keyword-only
      defaulted parameter to `write_block`'s signature (`:139`), the same
      `source_sections: tuple = ()` precedent `BlockContract` already sets.
      Confirm every existing positional `write_block(paper_dir, contract,
      draft, audit_account)` call site in tests stays green, unchanged.
- [x] 0.5 RED: failing tests for `paper_grounding.subjects_for(bindings,
      source_sections)` (design.md, Interfaces): a `fact:`-bound `Binding`
      whose `ref` names a `source_sections` entry's `"fact"` key is a
      subject; an `evidence:`-bound binding is never a subject regardless of
      any bound section; a `structural`-typed binding is never a subject; a
      `fact:`-bound binding whose fact has no bound-section entry is never a
      subject. Invented fixture names only. (`transposition-grounding`,
      Scenarios "A licensed fact with a bound section is a subject", "An
      evidence-bound sentence is never a subject", "A structural sentence is
      never a subject", "A fact-bound sentence whose fact carries no bound
      section is never a subject".)
- [x] 0.6 Create `.claude/skills/paper-writing/scripts/paper_grounding.py`.
      Implement `subjects_for(bindings: list, source_sections: tuple) ->
      list`: `bound_facts = {section["fact"] for section in
      source_sections}`, then `[b for b in bindings if b.kind == "fact" and
      b.ref in bound_facts]` — the exact intersection (design.md, D3). No
      block id, section title, document filename, or lineage literal decides
      membership. Confirm 0.5 goes green.
- [x] 0.7 RED-then-GREEN: an `argument`-mode block (`contract.mode !=
      MODE_TRANSPOSITION`) never reaches subject derivation — the grounding
      stage added next must not call `subjects_for` at all for a
      non-transposition block, mirroring `check_source_section_verbatim`'s
      own `contract.mode == MODE_TRANSPOSITION` guard at `paper_write.py:236`.
      (`transposition-grounding`, Scenario "An argument-mode block has no
      subjects".)
- [x] 0.8 Wire the subject-derivation half of the grounding stage into
      `write_block`: after the existing `source_fidelity_report` call
      (`:249`), before `substitute` (`:251`), guarded on `contract.mode ==
      paper_vocabulary.MODE_TRANSPOSITION`, lazily import `paper_grounding`
      (same local-import discipline `paper_leak` uses at `:203`/`:237`),
      compute `subjects = paper_grounding.subjects_for(bindings,
      contract.source_sections)`, and set `source_grounding = {"status":
      "unmeasured", "subjects": len(subjects)}` — **no account processing
      yet**, that is Phase 1. For an `argument`-mode block, or empty
      `contract.source_sections`, report `{"status": "unmeasured",
      "subjects": 0}` without importing `paper_grounding` at all.
- [x] 0.9 RED-then-GREEN: the `write` envelope gains a `sourceGrounding` key
      beside `sourceFidelity`, reporting `{"status": "unmeasured",
      "subjects": 0}` for a block with an empty subject set.
      (`transposition-grounding`, "Requirement: A Block With No Decided
      Subject Reports Unmeasured...", Scenario "No subjects reports
      unmeasured with a zero count".)
- [x] 0.10 Generality sweep: `rg` under
      `.claude/skills/paper-writing/scripts/paper_grounding.py`, this
      phase's `paper_write.py` diff, and its new tests/fixtures for any
      block id, section title, document filename, paper id, or lineage
      literal belonging to a real paper. Confirm zero matches.
- [x] 0.11 Run `.venv/bin/python -m unittest tests.test_paper_writing`;
      confirm green, no new failures beyond the known pre-existing baseline.

## Phase 1 — WU2: Reconciliation, the four refusals, the report shape

Satisfies `transposition-grounding`, "Requirement: An Absent Account
Refuses...", "Requirement: The Account Is Reconciled...", "Requirement: The
Permissive Verdict Carries The Burden Of Proof", "Requirement: An Unsupported
Claim Refuses", "Requirement: Undecidable Never Blocks Alone...", "Requirement:
A Sibling Check, Never An Extension...", "Requirement: The Guard Fires After
The Verbatim Check And Before Substitution", and the `decided == 0` half of
"Requirement: A Block With No Decided Subject Reports Unmeasured...".

- [ ] 1.1 **The load-bearing property — its own task, written RED first.**
      Plant an ungrounded `supported` verdict (empty span) for a subject
      sentence and assert it must NOT let that sentence pass as `supported`.
      Confirm this fails before `reconcile_support` exists (or trusts the
      account). Get this wrong and the whole guard is ceremonial — copy
      `contract-audit`'s asymmetry naively and an ungrounded `supported`
      waves everything past (design.md, D1). (`transposition-grounding`,
      "Requirement: The Permissive Verdict Carries The Burden Of Proof",
      Scenario "A supported verdict with an absent span downgrades".)
- [ ] 1.2 Implement `paper_grounding.reconcile_support(subjects, account,
      source_sections, *, block_id)` (design.md, Interfaces), byte-derived
      from `source_sections`' own `"text"` field, never the account's copy:
      `account is None` and `subjects` non-empty → refuse
      `GROUNDING_ACCOUNT_ABSENT` naming the block and `len(subjects)`; an
      account entry's `sentence` absent from the subjects' segmented text →
      refuse `GROUNDING_SENTENCE_UNKNOWN` quoting the entry verbatim; a
      subject sentence with no account entry → refuse
      `GROUNDING_VERDICT_MISSING` naming block and sentence; `supported`
      with an empty or not-byte-present span → downgrade to `undecidable`,
      span cleared, `downgraded: True`; `supported` byte-present only in a
      DIFFERENT fact's section → same downgrade; `unsupported` → refuse
      `SECTION_UNSUPPORTED_CLAIM` naming block, fact, lineage, section
      title, sentence; agent-returned `undecidable` passes through with
      `downgraded: False`. Confirm 1.1 goes green.
- [ ] 1.3 RED-then-GREEN: the different-fact downgrade — a `supported` span
      byte-present only in a different fact's bound section downgrades to
      `undecidable`. (`transposition-grounding`, Scenario "A supported
      verdict grounded in a different fact's section downgrades".)
- [ ] 1.4 RED-then-GREEN: the pass-through case — a `supported` span present
      verbatim in its own bound section passes as `supported`, span
      reported unchanged. (Scenario "A supported verdict with a
      byte-present span passes".)
- [ ] 1.5 RED-then-GREEN: `unsupported` refuses `SECTION_UNSUPPORTED_CLAIM`,
      message names block, fact, lineage, section title, sentence verbatim.
      (`transposition-grounding`, "Requirement: An Unsupported Claim
      Refuses".)
- [ ] 1.6 RED-then-GREEN, both directions independently: an account entry
      naming an unsegmented sentence refuses `GROUNDING_SENTENCE_UNKNOWN`; a
      subject sentence with no account entry refuses
      `GROUNDING_VERDICT_MISSING`. (`transposition-grounding`, "Requirement:
      The Account Is Reconciled...", both non-mutation scenarios.)
- [ ] 1.7 RED-then-GREEN: subjects non-empty, `account is None` → refuses
      `GROUNDING_ACCOUNT_ABSENT` naming block and subject count, and asserts
      NO `GROUNDING_VERDICT_MISSING` fires instead (the alternative
      design.md explicitly rejects, D7). Also: an empty subject set with
      `account is None` raises no grounding refusal at all.
      (`transposition-grounding`, "Requirement: An Absent Account
      Refuses...", both non-mutation scenarios.)
- [ ] 1.8 Implement `paper_grounding.source_grounding_report(subjects,
      reconciled) -> dict` (design.md D8, mirroring `source_fidelity_report`
      /`style_channel_report`'s shipped shape): `subjects: N, decided,
      undecidable` (agent-returned only), `downgraded` (reconciliation-
      produced only) as SEPARATE counts; `status = "measured"` only when
      `decided > 0`, else `"unmeasured"` with the true `subjects` count.
- [ ] 1.9 **Its own task, per design.md D2** — RED-then-GREEN: `downgraded`
      and agent-returned `undecidable` NEVER merge into one count: one
      subject returned `undecidable` directly, a second `supported` with an
      absent span; report counts the first as `undecidable`, exactly the
      second as `downgraded`. (`transposition-grounding`, "Requirement:
      Undecidable Never Blocks Alone...", Scenario "A downgrade is never
      counted as an agent-returned undecidable".)
- [ ] 1.10 RED-then-GREEN: a block whose subjects are ALL either returned or
      downgraded to `undecidable` (none `unsupported`) is NOT refused for
      grounding, and both counts report non-zero. (Scenario "An
      all-undecidable-or-downgraded account does not block".)
- [ ] 1.11 RED-then-GREEN: subjects exist, none decided → `{"status":
      "unmeasured", "subjects": N}` with `N > 0`, distinct from Phase 0's
      `subjects == 0` case. (`transposition-grounding`, Scenario "Subjects
      exist but none decided reports unmeasured with a nonzero count".)
- [ ] 1.12 Wire the full guard into `write_block`, replacing Phase 0's
      interim unconditional-`unmeasured` report: AFTER
      `check_source_section_verbatim` clears (`:238-241`), BEFORE
      `paper_block.substitute` (`:251`) — a draft failing both always names
      `SOURCE_SECTION_VERBATIM` first (design.md, D6). Call
      `reconcile_support(subjects, grounding_account, contract.source_sections,
      block_id=contract.block_id)`, then `source_grounding_report(...)`; add
      `"sourceGrounding": source_grounding` to the returned envelope beside
      `"sourceFidelity"`.
- [ ] 1.13 **Scope boundary — its own task.** An `evidence:`-bound sentence
      and an `argument`-mode block NEVER reach reconciliation, even when a
      grounding account names them — proven by a lock (an account entry
      naming a non-subject sentence is ignored, never
      `GROUNDING_SENTENCE_UNKNOWN`), not by the absence of a failure.
      (`transposition-grounding`, "Requirement: A Sibling Check, Never An
      Extension...", plus design.md Scope, "what this change does NOT
      check".)
- [ ] 1.14 RED-then-GREEN: a draft failing BOTH `check_source_section_verbatim`
      and grounding reconciliation refuses `SOURCE_SECTION_VERBATIM`, never
      `SECTION_UNSUPPORTED_CLAIM`. (`transposition-grounding`, "Requirement:
      The Guard Fires After The Verbatim Check...", Scenario "A draft
      failing both checks names the verbatim refusal".)
- [ ] 1.15 Generality sweep over `paper_grounding.py`'s reconciliation logic
      and this phase's tests/fixtures. Confirm zero real block id / section
      title / document filename / lineage literal.
- [ ] 1.16 Run `.venv/bin/python -m unittest tests.test_paper_writing`;
      confirm green, no new failures beyond baseline.

## Phase 2 — WU3: Agent file, `--grounding`, import row, classification, SKILL.md/references

Satisfies design.md D9 (`tests/test_agents.py`'s shipped gates), D7 (the
absent-account/CLI boundary), and §1's roster-registration table.

- [ ] 2.1 Create `.claude/agents/section-grounding-auditor.md`, shaped on
      `.claude/agents/contract-auditor.md`'s own `stretch: write` precedent.
      Must carry verbatim: `name: section-grounding-auditor` matching its
      filename stem (`tests/test_agents.py:316`); non-empty `tools:`
      (`Read, Glob, Grep`) (`:376`); `stretch: write`; `You begin` and
      `you end`/`You end` (`:382-391`); `## What you return` naming
      `` `did` ``, `` `stoppedAt` ``, `` `state` ``, `` `owed` `` in order
      (`:398-403`); the literals `never conclusions` and `measured again`
      (`:410-413`); a `## Measure before you assert` heading; and the
      literal sentence `Not every agent's description carries its bound
      skill's arrival` (`:512-522`). The role-discipline tuple is COPIED
      into this agent's own bytes, never referenced (`:496-501`) — adapt
      `contract-auditor.md`'s equivalent prose to per-sentence support
      judgment (`supported`/`unsupported`/`undecidable`, quoted `span` on
      `supported`) rather than per-bullet disqualifiers.
- [ ] 2.2 Add the literal phrase `` delegates to the
      `section-grounding-auditor` agent `` to
      `.claude/skills/paper-writing/SKILL.md`
      (`tests/test_agents.py:345-351,360-370` — an agent missing this is an
      orphan and the suite reddens). Confirm the existing `Measure this
      before delegating` line (`SKILL.md:1046`) covers `:415-432`'s
      obligation, or add the equivalent for this delegation.
- [ ] 2.3 Add `--grounding` to `p_write` in `paper_cli.py` (near `:3006-3009`'s
      `--style`, same `default=None` shape — D7: required would break every
      `argument`-mode and non-transposition fixture): help text names the
      account envelope `{support: [{sentence, fact, verdict, span}, ...]}`
      and that it must resolve inside the repository root.
- [ ] 2.4 Wire `cmd_write` (`:2230-2262`): resolve `--grounding` through
      `_resolve_repo_path` when supplied (reusing `PAPER_OUTSIDE_REPOSITORY`,
      never a second code — D7), load its JSON, pass it to
      `paper_write.write_block(..., grounding_account=grounding_account)`.
      `grounding_account` stays `None` when omitted — `GROUNDING_ACCOUNT_ABSENT`
      is `paper_grounding`'s to raise, never a flag check in the CLI.
- [ ] 2.5 Add the module-level import row to `paper_cli.py`'s registry
      (`:75-107`, after `paper_source_span` at `:95`): `import
      paper_grounding  # noqa: E402 -- the-block-asserts-only-what-its-
      section-carries: per-sentence support reconciliation against the
      bound section's own bytes; for the roster derivation`.
- [ ] 2.6 Add four `REFUSAL_CLASSIFICATION` entries (`:182-554`), all
      `WORK_STATE`: `GROUNDING_ACCOUNT_ABSENT`, `GROUNDING_SENTENCE_UNKNOWN`,
      `GROUNDING_VERDICT_MISSING`, `SECTION_UNSUPPORTED_CLAIM`.
- [ ] 2.7 Update `.claude/skills/paper-writing/SKILL.md` and `references/`:
      roster rows for the four codes (each naming its answer, per
      design.md §1's table), a note on the stage's position (after the
      verbatim check, before `substitute`), and D2's falsifier sentence
      verbatim — this ships in SKILL.md and the capability spec so the
      ruling stays arguable, not folklore.
- [ ] 2.8 RED-then-GREEN: `cmd_write` reads `--grounding`, resolves it
      through `_resolve_repo_path`, threads it to `write_block`; a path
      outside the repository root refuses `PAPER_OUTSIDE_REPOSITORY`.
- [ ] 2.9 Confirm every `Refused(...)` first argument added in Phases 0-2 is
      a string literal — grep `paper_grounding.py` and the `paper_write.py`/
      `paper_cli.py` diffs for `raise Refused(exc.code`; there must be none
      (design.md §1: `_refusal_code_argument` reads only `ast.Constant`; a
      non-literal is invisible to the roster walk).
- [ ] 2.10 Run `.venv/bin/python -m unittest tests.test_paper_writing
      tests.test_agents`; confirm green.

## Phase 3 — WU4: Mutation proofs, neutrality sweep, roster re-measure, both suites

Satisfies design.md's Testing Strategy "Mutation" row and the operator's
non-negotiable discipline: a mutation is the only proof a guard holds.

- [ ] 3.1 Mutation 1/4 — `GROUNDING_ACCOUNT_ABSENT`: anchor the check with a
      source string occurring EXACTLY ONCE in `paper_grounding.py`
      (`tests/paper_mutation.py:64-68` raises otherwise); mutate it to treat
      `None` as empty; confirm the absent-account test (1.7) goes red via
      `_run_against_mutant(..., source_path=SKILL_SCRIPTS /
      "paper_grounding.py")`. Restore. (`transposition-grounding`, Scenario
      "Mutation — the absent-account refusal is reachable".)
- [ ] 3.2 Mutation 2/4 — `GROUNDING_SENTENCE_UNKNOWN` and
      `GROUNDING_VERDICT_MISSING`, EACH its own mutant, one direction
      disabled at a time; confirm each mutant reddens ONLY its own scenario
      (1.6), never the other. Anchors must not share a line with each other
      or with 3.1's. Restore both. (Scenario "Mutation — each direction is
      independently reachable".)
- [ ] 3.3 Mutation 3/4 — the span-presence check on `supported`: remove the
      byte-presence re-read so any span is accepted without re-reading the
      section's bytes; confirm the absent-span downgrade test (1.1/1.3)
      goes red. Restore. (Scenario "Mutation — the downgrade is caught only
      by span reconciliation".)
- [ ] 3.4 Mutation 4/4 — `SECTION_UNSUPPORTED_CLAIM`: mutate the
      `unsupported` branch to treat that verdict as `undecidable` instead
      of refusing; confirm the unsupported-claim test (1.5) goes red.
      Restore. (Scenario "Mutation — the unsupported refusal is
      reachable".) Confirm all four anchors from 3.1-3.4 sit on four
      DISTINCT lines in `paper_grounding.py` — a design constraint on the
      module, not an apply-time accident (design.md, "Mutation anchors").
- [ ] 3.5 Do NOT "fix" `tests/paper_mutation.py`'s stale-bytecode handling —
      it already purges `__pycache__` via a fresh `tempfile.mkdtemp` per
      call, a `uuid4`-named mutant module, and `PYTHONDONTWRITEBYTECODE=1`
      (`:74-75,139`). Pass `source_path=SKILL_SCRIPTS / "paper_grounding.py"`
      explicitly at every call site above (the default is `paper_block.py`).
- [ ] 3.6 Generality sweep, whole change: `rg` under `.claude/skills/` for
      any lineage name, method name, researcher's folder name, block id,
      section title, document filename, or paper id introduced by Phases
      0-2 together, not only the last phase. Run
      `ForgeVocabularyDerivedGuardTests` (rule B, `FORGE_LEXICON`); confirm
      no NEW leak beyond the one disclosed pre-existing failure this
      repository already carries.
- [ ] 3.7 Re-derive the roster by EXECUTING
      `reachable_paper_refusal_codes()` after all engine code from Phases
      0-2 has landed. Update the pinned literal at
      `tests/test_paper_writing.py:7942` (today **161**) to the MEASURED
      figure. Do not write a predicted number into any artifact before this
      task runs — the four new codes are the only newly-authored additions;
      further movement is codes becoming reachable through the widened
      import graph, the same mechanic this repository's own roster section
      already documents.
- [ ] 3.8 Confirm `git diff --stat` shows zero deletions anywhere in the
      change, and `paper_leak.py` is byte-identical to its pre-change state
      (design.md, D5: "`paper_leak.py` is touched by this change not at
      all").
- [ ] 3.9 Run the FULL suite, both runners — never a narrower module list
      for either: `npm test` (confirm N/N, exit 0); then
      `.venv/bin/python -m unittest discover -s tests -p "test_*.py"`
      (chunk into sequential foreground runs if the ~650s discover time
      risks a timeout, per this repository's own precedent —
      `openspec/changes/archive/2026-09-20-the-tripwire-reaches-the-section-that-feeds-it/tasks.md:380-412`
      — but every chunk TOGETHER must cover every `test_*.py` file; a
      partial module list that silently skips a suite is a defect this
      repository has already shipped once). Confirm AT MOST the one known
      pre-existing failure
      (`ForgeVocabularyDerivedGuardTests.test_rule_b_finds_no_target_vocabulary_in_the_forge`);
      any second failure belongs to this change and blocks delivery.
- [ ] 3.10 Record D2's falsifier as a live, unexecuted obligation
      (design.md, D2 — over ten or more recorded real `write` runs, if any
      block reaches `written` with `downgraded > 0`, or with `subjects > 0`
      and `decided == 0`, the ruling is wrong) in this change's tracking,
      stating it is unexecutable today (no real `document`-rooted binding
      exists on disk) and is not silently waived.

## Key discipline carried forward, not to be reinterpreted at apply time

- The ordering gate (0.1) is a stop-and-report instruction, not a
  suggestion: if the sibling has not landed, halt and report rather than
  implementing it or guessing at its shape.
- Red first, every guard, every phase above.
- A mutation is the only proof a guard holds — each of the four new codes
  has its own mutation task (3.1-3.4), on four distinct anchor lines.
- The burden-of-proof inversion (1.1) is the load-bearing property of the
  whole change — get it wrong and the guard is ceremonial.
- `downgraded` and agent-returned `undecidable` never merge (1.9) — this is
  what closes the silent half of D2's risk without a ratio threshold.
- Generality is a task, not an assumption — 0.10, 1.15, 3.6 are each their
  own task.
- The roster is measured, never forecast — 3.7 runs after all engine code
  lands; no number is written into any artifact before that.
- `paper_leak.py` stays untouched (D5) — checked explicitly at 3.8.
- Both suites, in full — 3.9 names why a partial module list is not enough.
