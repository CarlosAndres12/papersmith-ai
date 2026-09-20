```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:afeb4325df730103adc6ba5a1571422eeb072cba99ab184ac6660e9eed2779cc
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 9/9
scenarios: 29/29
test_command: .venv/bin/python -m unittest tests.test_paper_writing
test_exit_code: 0
test_output_hash: sha256:b91dcb2b573bc67b1d71c67b3fed075a7b0ac6f42f8c958d825f759cdac5cf5c
build_command: npx tsc -p tsconfig.json
build_exit_code: 0
build_output_hash: sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

## Verification Report

**Change**: the-tripwire-reaches-the-section-that-feeds-it
**Branch**: wu0-the-math-fence-stops-leaking (5 commits ahead of main), tree clean
**Mode**: Standard (red-first tasks, mutation proofs; not orchestrator-declared Strict TDD)

### Completeness
Tasks total 53, complete 53 (`[x]`), incomplete 0. All four work units (WU0-WU3) closed.

### Build & Tests
- `npx tsc -p tsconfig.json`: exit 0, empty output.
- `npm test`: **640/640**, exit 0 (re-run personally).
- Python suite, run in 6 sequential chunks per this project's own documented cross-chunk
  `implementations/` race discipline (never concurrently):
  - `test_paper_writing`: 526/526 (re-run personally, matches apply's own reported count).
  - `test_paper_citation`, `test_paper_contract`, `test_paper_decisions`, `test_paper_evidence`,
    `test_paper_figure`, `test_paper_lifecycle`, `test_paper_separation`: 582/582 (re-run personally).
  - `test_agents`, `test_experimental_implementation(+_mutation)`, `test_experiments_seal`,
    `test_extract_pdf`, `test_forge_gate`, `test_forge_scaffolding`,
    `test_implementation_authorization_binding`, `test_implementation_core`,
    `test_implementation_domain_lock(+_mutation)`, `test_implementation_pair`,
    `test_implementation_profile`, `test_implementation_seal`: 485/485 (re-run personally).
  - `test_kaggle_accounts`: 63/63 (re-run personally).
  - `PYTHONPATH=tests test_orphan_sweep`: 7/7 (re-run personally).
  - `test_proposal_implementation`, `test_remote_execution`, `test_skill_audit`,
    `test_suite_collects`: 2743 tests, **exactly 1 known pre-existing failure**
    (`ForgeVocabularyDerivedGuardTests.test_rule_b_finds_no_target_vocabulary_in_the_forge`,
    the generic word "mechanisms" in `experimental-deliberation/SKILL.md`), 3 skipped.
  - **Total: 4406 tests, exactly 1 known pre-existing failure — confirmed by re-running the
    entire baseline myself, not by trusting the apply report.**
  - **First attempt at the heaviest sub-chunk produced a genuine second failure** —
    `test_the_toy_targets_left_nothing_behind` — caused by a stray
    `implementations/_smokebox_pub-wiring-first_6715` scratch directory. Root-caused: MY OWN
    earlier truncated invocation of the same test module (killed at a 100s shell timeout before
    it finished) left this directory behind — a live, self-inflicted instance of the exact
    cross-chunk `implementations/` race this repository has already documented and that the
    applier itself hit once during apply (Engram `sdd/.../apply-progress`, WU3, Learned #2).
    Removed the stray directory and re-ran the sub-chunk clean: back to exactly 1 known failure.
    This is a verification-methodology artifact, not a defect in this change's own code — recorded
    here for transparency rather than silently discarded.

### Spec Compliance

Three delta specs, 9 requirements / 29 scenarios total, counted directly from `### Requirement:`
and `#### Scenario:` headings (never taken from an artifact's own claimed count):

**`transposition-fidelity` (new)** — 6 requirements / 18 scenarios, all COMPLIANT:
- "The Verbatim Check Is A Sibling, Never An Extension" — confirmed: `check_source_section_verbatim`
  is a distinct function in `paper_leak.py`; `git diff` on that file shows **zero deletions**, only
  additions (`SOURCE_RUN_BACKSTOP`, `source_section_floor`, `check_source_section_verbatim`) —
  `check_tripwire`'s own bytes are byte-for-byte unmoved. Both scenarios covered by
  `SourceSectionVerbatimWriteGateTests`, re-run personally, green.
- "The Threshold Self-Calibrates Against The Contract's Own Prose" — confirmed:
  `threshold = max(source_section_floor(...), SOURCE_RUN_BACKSTOP)`, `SOURCE_RUN_BACKSTOP = 16`,
  strict `>` enforced via `tripwire_spans(..., min_tokens=threshold + 1)`. All 5 scenarios
  (verbatim refuses, register-shift passes, contract-licensed run passes, both threshold
  mutations) covered and re-run personally in `SourceSectionVerbatimMutationProofTests` — green.
- "The Floor And Threshold Are Reported, Never Inferred Silently" — confirmed:
  `source_fidelity_report`/`check_source_section_verbatim` populate `{"lineage", "title", "floor",
  "threshold", "longest_run"}` per section on every path, including the inert-floor case. Both
  scenarios covered, re-run personally, green.
- "The Guard Fires Inside `write`, Before Substitution" — confirmed: the new stage in
  `write_block` runs after `check_tripwire` and before `substitute`; the ledger is written only on
  the audit-fired branch (this stage runs strictly after that branch returns, so a refusal here
  writes nothing). All 3 scenarios (direct-invocation refusal, read-only-verb mutation, no-ledger-
  write) re-run personally, green.
- "Only A Transposition-Mode Block Is Checked, Mode Derived From The Contract" — confirmed: the
  stage guard reads `contract.mode == paper_vocabulary.MODE_TRANSPOSITION`; `argument`-mode is
  exempt. Both scenarios plus the mode-flip mutation (which must redden BOTH the transposition and
  the argument test) re-run personally, green.
- "A Block With No Measured Bound Section Reports Unmeasured, Never Refused" — confirmed:
  `source_fidelity_report` returns `{"status": "unmeasured"}` when `source_sections` is empty. Both
  scenarios, including the mutation forcing `source_sections=()` regardless of resolution, re-run
  personally, green.

**`style-leak-detection` (modified)** — 2 requirements / 7 scenarios, all COMPLIANT:
- "The Eight-Token Tripwire" ($$ fence exclusion) — confirmed: `_MATH_DISPLAY_RE` in both
  `paper_style.py` and `paper_bindings.py` carries the identical `\$\$.*?\$\$|` alternative ahead
  of the `\[...\]`/`\begin{...}` alternatives, `\1` backreference intact. The DERIVED cross-module
  sweep (`_every_strip_math_callable`, introspection over `SKILL_SCRIPTS.glob("*.py")`, never a
  hand-listed pair) and its own mutation test (dropping the alternative from ONLY
  `paper_bindings._strip_math` and confirming the sweep — not a hand list — catches it) re-run
  personally: `MathFenceExclusionSweepTests`, 2/2 green.
- "Overlap Reads Only The Recorded Sample Set" — confirmed: `check_source_section_verbatim` reads
  the bound section's bytes directly and calls `tripwire_spans`/`overlap_against_set` with its own
  `[{"span": ...}]` list, never touching or appending to `contract.style_set`/`R`. No code path
  folds a bound section into `R`.

**`evidence-bound-drafting` (modified)** — 1 requirement / 4 scenarios, COMPLIANT: the identical
`$$` alternative lands in `paper_bindings.py`'s own `_MATH_DISPLAY_RE`, proven by the same derived
sweep above (which explicitly covers this file) plus its own dedicated mutation test.

### Correctness — mutations run personally, not merely read

Every one of the design's/spec's named mutations was executed by me directly, not taken on trust:

| Mutation | Ran it myself | Observed |
|---|---|---|
| Drop `$$` alt from `paper_style.py` | Yes (existing test asserts this) | Display-fence unit reddens |
| Drop `$$` alt from `paper_bindings.py` | Yes | Derived cross-module sweep reddens (not the unit test — proving the sweep, not a hand list, catches it) |
| Backstop alone (`SOURCE_RUN_BACKSTOP`) discarding the floor | Yes | Contract-licensed 40-token-run test reddens |
| Floor alone discarding the backstop | Yes | Near-zero-floor six-token-idiom test reddens |
| Refusal's own minimum raised far above any draft length | Yes | Verbatim-paste `write` test reddens |
| Guard wired only into a read-only verb, `write_block` skips it | Yes | Direct-`write` verbatim-paste test reddens |
| Stage guard `MODE_TRANSPOSITION` → `MODE_ARGUMENT` | Yes | BOTH the transposition test and the argument-exemption test redden |
| `source_sections=bound_sections` → `source_sections=()` | Covered by WU1's own mutation test, re-run | Resolved-triple test reddens |

All 8 (`SourceSectionVerbatimMutationProofTests` + `MathFenceExclusionSweepTests`) pass as designed
— i.e., each test asserting "the mutant goes red" itself passed, confirming the guard is
load-bearing in every dimension the spec claims.

### Roster — measured live, not quoted from an artifact

Executed `tests.test_paper_writing.reachable_paper_refusal_codes()` myself:
**153**, `SOURCE_SECTION_VERBATIM` present — matches both design.md's post-WU2 figure and the
apply report's WU3 re-measurement exactly. `reachable_paper_refusal_codes` is confirmed
genuinely static: an AST walk over `paper_cli.py`'s `cmd_*` roots plus a closure over every module
`paper_cli.py` imports, never a runtime call trace — meaning it would NOT have silently
absorbed the design-flagged trap (a caller-side `raise Refused(exc.code, ...)` making the CODE
argument a runtime value). Confirmed the actual shipped code avoids that trap: `paper_leak.
check_source_section_verbatim` raises `Refused("SOURCE_SECTION_VERBATIM", ...)` with the literal
string directly, `block_id` passed as a separate plain parameter — exactly the fix design.md
describes the applier making, verified by reading the source. Also confirmed `paper_write.
write_block` passes `contract.block_id` straight through without any `except Refused: raise
Refused(exc.code, ...)` re-wrap.

### Migration / nothing deleted

- `git diff main -- sections/`: 0 lines.
- `git diff --summary main`: only `create mode` lines; **zero `delete mode` lines** anywhere.
- No on-disk format/digest/marker-grammar change; `BlockContract.source_sections` defaults to `()`.

### Generality — swept personally, not trusted from the apply report

- Zero hits for real paper-guidance document names (`s41597-026-06758-7`, `Li_2026...`,
  `brainsci-16-00363`, `computation-13-00116`/`computation-14-00002`, `computers-13-00176`/
  `computers-15-00428`, `mathematics-13-02602`) anywhere under `.claude/skills/paper-writing/` or
  its own test modules/fixtures.
- The worked-example names in `proposal.md`/`design.md`/the spec (`widget-study-r4.md`,
  `analysis.an-core`, "2. Widget Calibration") are stated as invented and do not appear in shipped
  code or tests — confirmed by grep.
- `lumen-thesis`/`3. Something`/`formulation` fixture names in `tests/test_paper_writing.py` are
  pre-existing invented fixtures from an earlier change (`SourceSectionBindingWriteGateTests`),
  reused rather than newly invented by this change — confirmed by their presence outside this
  change's new test classes too.
- `ForgeVocabularyDerivedGuardTests` re-run personally: 21 run, exactly the one disclosed
  pre-existing failure (`experimental-deliberation/SKILL.md`, "mechanisms"), unrelated to
  `paper-writing` and unchanged by this branch.
- The disclosed 48-collision, three-sibling-skill (`proposal-deliberation`,
  `proposal-implementation`, `experimental-deliberation`) vocabulary overlap is out of this
  change's scope, as stated in the task brief — not re-litigated here.

### Synthetic boundary — confirmed in the artifact, not only in a report

`transposition-fidelity/spec.md`'s own Purpose section states explicitly: "No real `document`
binding exists on disk in this repository today... every bindable entry is `undecided`... every
end-to-end scenario below is necessarily synthetic." Confirmed independently: no `paper/` directory
and no `kind: document` binding exist anywhere on disk in this checkout. No test depends on a real
binding existing — every integration test constructs its own `bind`-recorded fixture.

### Falsification obligation — confirmed recorded, not silently waived

`tasks.md` 3.4 records the two falsifiers (a transposed draft reaching the 16-token backstop; a
verbatim paste staying under it) verbatim from `design.md` Decision C, states the obligation is
unexecutable today (no real bindings), and design.md's own Open Questions section points back at
this record. Confirmed present in both files.

### Deviations disclosed by the applier — independently confirmed

1. **The `raise Refused(exc.code, ...)` trap** (design's interface sketch implied catch-and-reraise;
   applier changed the shape to keep the literal statically readable) — confirmed accurate by
   reading `paper_leak.py` and `paper_write.py` directly (see Roster section above).
2. **The orphaned-scratch-directory mishap during apply** — confirmed the applier's own account
   (Engram `apply-progress`, WU3) is accurate, AND independently reproduced the identical failure
   mode myself during this verification (see Build & Tests section) — strong corroborating evidence
   this is a real, repeatable defect in the test harness's own concurrency discipline (documented,
   not new), not a one-off.
3. **`_resolve_write_gate`'s signature** — confirmed changed from the design-quoted `-> None` to
   `-> "paper_graph.Corpus"`, and the docstring itself narrates the exact prior-change discrepancy
   this change was built to close (the archived predecessor's File Changes row claimed the return
   value shipped when it had not) — read directly, accurate.

### Artifact vs. code discrepancy found

**The "engine lines" figure could not be corroborated from any retrievable artifact and does not
match my own measurement.** I was told to confirm "Ceiling 1600, measured 323" for engine lines
under `.claude/skills/paper-writing/scripts/`. No file in
`openspec/changes/the-tripwire-reaches-the-section-that-feeds-it/` contains the figure "323", and
Engram's `apply-progress` topic key is an upserting slot — only the final WU3 revision (docs-only,
no engine code) is retrievable; the WU0-WU2 revisions that would have carried this figure are
gone. My own direct measurement, `git diff main -- .claude/skills/paper-writing/scripts/ --stat`
(and independently confirmed identical via three-dot `main...HEAD`, since `main` is exactly the
merge-base): **278 insertions + 11 deletions = 289 changed lines**, across the 7 engine files
`design.md`'s own File Changes table names. This is a WARNING, not a CRITICAL: both 289 and 323
are comfortably under the 1600 ceiling, so no budget rule is violated either way, and no artifact
in this change actually asserts "323" for me to call stale — the number was only ever given
verbally in the verify task itself. Flagged for the record rather than silently reconciled.

### Issues

**CRITICAL**: none.

**WARNING**:
1. The "engine lines = 323" figure given in the verify task could not be corroborated by any
   artifact and does not match my own direct measurement (289) — see above. Does not affect the
   1600-line budget conclusion either way.
2. No test asserts the exact wording of the `SOURCE_SECTION_VERBATIM` refusal detail message
   (block id / fact / lineage / section title / span) beyond the code's own assertion checks in
   `SourceSectionVerbatimWriteGateTests` — sufficient for the spec's own requirements, but a
   dedicated "detail names all five things" test does not exist as its own named unit.

**SUGGESTION**:
1. Record the final, executed engine-line total in `tasks.md`'s own budget-ruling table on close,
   the same suggestion made for the concurrent sibling change, so a verifier never has to
   reconstruct it from `git diff` alone.
2. Consider a `mem_timeline`-style retrieval path (or explicit per-WU topic keys) for
   `apply-progress` so intermediate work-unit evidence (e.g., WU2's own engine-line count) survives
   past the final upsert.

### Verdict

**PASS WITH WARNINGS.** Archive-ready — no CRITICAL findings. All 53 tasks verified complete
against real, personally re-executed passing evidence (640/640 npm, 4406/4406 Python minus 1 known
pre-existing unrelated failure). All 9 requirements / 29 scenarios across the three delta specs are
COMPLIANT with runtime-covering tests I ran myself, including every named mutation. Roster (153),
generality sweep (zero hits), and the synthetic-boundary/falsification-obligation statements are
all independently confirmed rather than trusted. The one artifact/code mismatch found (289 vs. the
verbally-given 323 engine lines) is immaterial to the budget conclusion and is disclosed rather
than silently reconciled.

## Key Learnings

1. `reachable_paper_refusal_codes()` derives the refusal roster via an AST walk over `paper_cli.py`'s command roots, never a runtime call trace, so a caller-side `raise Refused(exc.code, ...)` re-wrap would silently vanish from the roster.
2. The derived cross-module `strip_math`/`_strip_math` sweep discovers callables by introspecting every module under `scripts/`, so a mutation dropping the `$$` alternative from only one implementation is caught by the sweep test itself rather than by a hand-maintained list.
3. A truncated (killed mid-run) invocation of `test_proposal_implementation` can leave an orphaned `implementations/_smokebox_*` scratch directory that produces a spurious second test failure on the next run — the same documented cross-chunk race this repository has already paid for once during apply.
4. Engram's `apply-progress` topic key upserts per work unit, so only the latest revision (here, WU3's docs-only summary) is retrievable — intermediate work-unit evidence such as an engine-line count from WU2 is not recoverable through `mem_get_observation` once superseded.
5. `_resolve_write_gate`'s return-type annotation changing from `-> None` to `-> "paper_graph.Corpus"` is a direct, greppable confirmation that the archived predecessor's claimed-but-unshipped return value has now actually landed.
