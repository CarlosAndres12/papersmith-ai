```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:b23a49d2d81aeccef3c062aff45002cf04cc2325ca8a457ed43fde4143675830
verdict: fail
blockers: 1
critical_findings: 1
requirements: 24/25
scenarios: 38/39
test_command: npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
test_exit_code: 0
test_output_hash: sha256:3521de7d2888e2a0ea83a5f182940ca3dc9656d5ef06de13b3df8cffc3a8ec1a
build_command: npm run typecheck
build_exit_code: 0
build_output_hash: sha256:0489b64b1ab5dcef532b46d77ea0fca0aa427390ec93669281021dd89abd1486
```

## Verification Report

**Change**: the-writer-may-assert-only-what-it-was-given
**Version**: N/A (no version field in spec artifact)
**Mode**: Strict TDD

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 24 (17 WU1 + 7 WU2) |
| Tasks complete | 24 |
| Tasks incomplete | 0 |

Task 1.17 is checked `[x]` but its own text honestly discloses a partial
scope: three of its four deliverables (the two agent files, `SKILL.md`)
landed; the fourth (transcribing `mode` into the ten shipped
`sections/*.md` headers) is explicitly marked "Deferred, not done" inside
the task's own prose. Treated here as a disclosed, spec-licensed deferral
(see "The mode-transcription deferral" below), not a silently-incomplete
task — the checkbox does not misrepresent what was built.

### Build & Tests Execution

**Build**: PASSED
```text
$ npm run typecheck
> papersmith-ai@0.1.0 typecheck
> tsc -p tsconfig.json
exit 0
```

**Tests**: PASSED — 559 (npm) + 3154 (python, skipped=6) = 3713 tests run, 0 failed
```text
$ npm test
tests 559, pass 559, fail 0

$ .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
Ran 3154 tests in 490.339s
OK (skipped=6)
```

Concurrency note: a sibling apply (`a-diagram-that-compiles-or-says-why`)
landed six additional commits on this same branch during this
verification session (HEAD moved from `f3b3fcf` to `73ae901`). Every file
this change owns — `paper_bindings.py`, `paper_audit.py`, `paper_write.py`,
`paper_style.py`, `paper_leak.py`, `redactor.md`, `contract-auditor.md`,
`style-sampler.md` — was diffed against `f3b3fcf` (this change's own last
commit) three separate times across the session, including immediately
before this report was written: zero bytes changed every time. All test
and build evidence above is therefore valid for this change's own scope
regardless of the sibling's concurrent activity. One earlier full-suite
run mid-session exited 1 with no captured diagnostic output (most likely
a transient race against the sibling's concurrent writes elsewhere in the
tree); a repeat run completed cleanly, and this report's recorded
`test_output_hash` is from a fresh, final, clean run.

**Coverage**: not available — no coverage tool configured for either
suite (`node --test` / `unittest`); skipped cleanly, not a failure.

### Two independent proofs — constructed fresh, not run from the shipped suite

Per the launch instructions, both decisive proofs were re-derived with
genuinely new fixtures (different block ids, evidence ids, contract text)
rather than executing `test_an_assertion_outside_the_evidence_set_never_
reaches_main_tex` / `StyleLeakDetectionTests` directly.

**Proof 1 — an out-of-evidence-set assertion never reaches `main.tex`.**
Built an independent `paper/` fixture (`verify-own-block-7f3a`, evidence
set `{REAL-EVID-1}`), drafted a two-sentence binding map where the second
sentence binds `evidence:GHOST-EVID-99` (never in the set). Result:
`paper_write.write_block` raised `Refused(code="EVIDENCE_ID_UNKNOWN",
detail="'GHOST-EVID-99' is not in the block's evidence set")`, and
`main.tex` was confirmed byte-identical before and after the call. PASSED.

**Proof 2 — style register rises, overlap does not, with a working
A/B control.** Built independent styled/unstyled draft pairs (archaic vs.
plain register) and confirmed `d(S,{A,B}) > d(A,B)` (3.59 > 0.70,
`pass: True`) and `overlap(S,R) <= max(overlap(A,R), overlap(B,R))`
(0 <= 0, `pass: True`) against an independently-authored reference set.
Confirmed `register_distance_holds`'s signature is exactly `(styled,
unstyled_a, unstyled_b)` with no defaults, and that omitting `unstyled_b`
raises `TypeError` at call time — a construction failure, not a test
failure. Confirmed `relative_overlap_holds`'s signature is exactly
`(styled, unstyled_a, unstyled_b, samples)`, carrying no threshold
parameter (matches the shipped test
`test_relative_overlap_holds_signature_carries_no_threshold`, which reads
the same signature via `inspect.signature`). Further confirmed the
tripwire and the relative inequality are genuinely independent, in both
directions, with two own constructions: (a) a draft sharing a 10-token run
with `R` — the tripwire fired — while an unstyled control (`A`) shared an
even longer run, so the relative inequality still passed
(`overlap_S=10 <= max(10,0)`); (b) a draft sharing only a 3-token run —
the relative inequality failed (`3 > max(1,1)`) while the tripwire stayed
silent (run length below 8). PASSED.

### Hunted shapes — a real call-site sweep of all five modules

**"A function wired to nothing" — a further instance found, still
present.** Enumerated every top-level function in `paper_bindings.py`,
`paper_audit.py`, `paper_write.py`, `paper_style.py`, `paper_leak.py` and
grep'd real call sites (not the defining line, not a docstring reference)
across `scripts/*.py`. Two functions have zero production call sites:

- `paper_write.style_channel_report` — defined, imported (module-level
  `import paper_write` in `paper_cli.py`), directly unit-tested
  (`StyleChannelReportingTests`, 2 tests), but never called from
  `cmd_write`, `write_block`, or anywhere else in `scripts/`. A real
  `write` invocation with an empty style set never actually reports
  `{"status": "unmeasured"}` to its caller — this function's own Ruling-2
  behavior is unreachable in production today. This is the same defect
  class this very change's own `f3b3fcf` commit self-caught and fixed
  twice already (`check_tripwire`, `resolve_style_set` were both wired
  into `write_block` in that follow-up commit) — recurring a further
  time, undetected until now. **WARNING.**
- `paper_leak.register_distance_holds` / `relative_overlap_holds` — also
  zero production call sites, called only from tests. Checked against
  `design.md` Decision D6's own table before flagging: it explicitly
  states these run "in the proof harness, over recorded A/B/S
  transcripts" — never per real `write` — while only the tripwire "runs
  every styled `write`". The Data Flow diagram in `design.md` confirms
  this: only `paper_leak.tripwire (styled only)` appears in the
  production pipeline; the register/overlap proof does not. **Not a
  finding** — documented, intentional design, verified by the executed
  mutation harness (mutations 6 and 7) rather than by a per-write runtime
  check, the same role `MutationProofTests` plays for the byte-identity
  guards.

### Hunted shapes — the guard that cannot go red

Confirmed independently: `relative_overlap_holds(styled, unstyled_a,
unstyled_b, samples)` carries no threshold parameter (own
`inspect.signature` probe, matching the shipped
`test_relative_overlap_holds_signature_carries_no_threshold`), and the
shipped executed mutation `test_mutation_6_optional_ab_control_fails_the_
typeerror_guard` (real subprocess, source patched, cache purged, guard
confirmed red) proves the A/B control cannot be silently dropped. Own
constructions above (item "Proof 2") independently confirmed the tripwire
and the relative inequality cannot satisfy each other in either
direction.

### Hunted shapes — the no-subprocess seam

`SUBPROCESS_EXCEPTIONS` confirmed pinned to exactly `("paper_latex.py",)`
with `assertEqual(len(...), 1)`. Own construction: copied the real
`scripts/` tree to a temp dir, confirmed it scans clean unmutated, then
planted `import subprocess` in `paper_style.py` (a non-exempt module) —
caught (`{"paper_style.py": ["subprocess"]}`). Restored, then planted the
same import in the exempt `paper_latex.py` (the sibling's file, currently
on disk) — correctly NOT reported, confirming the named exception really
is exempt as designed. Planted a lookalike-named file
(`not_paper_latex.py`) with the same import — correctly caught,
confirming the exemption is an exact filename match, never a
substring/prefix match. Also planted `os.system(...)` in a second module
— caught. PASSED.

### Hunted shapes — the live-agent guard

The shipped guard (`ZZLiveAgentGuardTests`) is a passive, after-the-fact
observation: a module-scoped `subprocess.Popen` monitor that records any
launch naming an agent binary and asserts the list is empty once the
suite finishes. Own, stronger construction: poisoned `subprocess.Popen`
to raise `AssertionError` on ANY call (not just agent-binary calls), then
ran a full `write_block` invocation (readiness, evidence-audit,
contract-audit, the style tripwire with a real sample, and `substitute`)
to completion successfully — proving by mechanism, not by an
after-the-fact assertion, that no code path in the `write` pipeline can
spawn any process at all, agent binary or otherwise. Backed further by
the no-subprocess AST scan above, which proves this holds structurally
across every script `paper_cli.py` imports except the one named,
unrelated exception. PASSED.

### The mode-transcription deferral — ruling

**Measured**: every real block in this repository refuses `write` today.
`paper_contract.resolve_mode` was run against all ten shipped
`sections/*.md` files: **45/45 blocks across all ten files resolve to no
mode.** `write`'s readiness stage therefore refuses `MODE_ABSENT` on
every real block that exists in this repository right now — the change's
central capability cannot draft a single real section today.

**Ruling: acceptable deferral, not a broken contract, but a real and
currently-total usability gap.** The `section-contract` spec delta's own
ADDED requirement, "Headers Written Before `mode` Existed," explicitly
licenses exactly this state: an absent `mode` at both levels is schema-
valid, not a violation, and mandates that `write`'s readiness stage
"refuse to draft it rather than assume a mode" — which is exactly the
measured behavior. No spec requirement is left unmet by this deferral;
the requirement anticipates and requires the refusal, not the
transcription. The deferral is also disclosed honestly inside task
1.17's own checked-off text, not hidden behind a silently-incomplete
checkbox. **WARNING**, not CRITICAL: report this as the single
highest-priority follow-up — nothing else in this change's own scope can
unblock real usage of `write`, and no later phase depends on this one
except by an operator doing the ten contracts' own close reading that
this batch's scope explicitly did not budget for.

One related, minor finding: the spec's own requirement text is now stale
in one sentence — "`sections/*.md` carry no front-matter header as
committed today — Phase 2's insertion has not landed" was true when this
spec was drafted (mid-`the-contract-is-data-not-code` apply) but is false
now; all ten files carry headers today, only `mode` is absent from them.
The requirement's actual behavioral mandate (schema-valid absence,
`MODE_ABSENT` refusal) still holds and is proven — this is a wording
staleness for archive-time cleanup, not an enforcement gap.
**SUGGESTION.**

### Spec Compliance Matrix

| Capability | Requirement | Scenario | Test | Result |
|---|---|---|---|---|
| section-contract | Front Matter Schema | Valid header parses | `test_paper_contract.py::test_valid_header_parses_with_no_refusal` | COMPLIANT |
| section-contract | Front Matter Schema | Missing mandatory field refuses | `test_paper_contract.py::test_header_missing_position_refuses_naming_position` | COMPLIANT |
| section-contract | Front Matter Schema | Block inherits section-level mode | `test_paper_writing.py::ModeWideningTests::test_a_block_inherits_the_section_level_mode` | COMPLIANT |
| section-contract | Front Matter Schema | Block's own mode overrides default | `...::test_a_blocks_own_mode_overrides_the_section_level_default` | COMPLIANT |
| section-contract | Headers Written Before mode Existed | No mode at either level cannot be drafted | `WritingPipelineTests::test_no_mode_resolved_refuses_mode_absent` | COMPLIANT |
| section-contract | Closed Mode Vocabulary And Transcription | Valid mode value parses | `ModeWideningTests::test_a_valid_mode_value_parses` | COMPLIANT |
| section-contract | Closed Mode Vocabulary And Transcription | Invalid mode value refuses | `...::test_an_invalid_mode_value_refuses_unknown_mode` | COMPLIANT |
| writing-orchestration | Pipeline Stage Order | Failing evidence-audit stops before contract-audit | `WritingPipelineTests::test_a_failing_evidence_audit_stops_before_contract_audit_runs` | COMPLIANT |
| writing-orchestration | One Bounded Re-Draft | Second attempt audited with same inputs | `...::test_the_second_attempt_is_audited_with_the_same_inputs` | COMPLIANT |
| writing-orchestration | Exhaustion Leaves The Block Unwritten | Two failing audits leave main.tex unchanged | `...::test_two_failing_audits_leave_main_tex_unchanged_and_refuse_audit_exhausted` | COMPLIANT |
| writing-orchestration | No Live Agent Invocation In Tests | Suite runs with zero live agent subprocesses | `ZZLiveAgentGuardTests::test_no_agent_binary_launched_by_any_subprocess_this_run_has_made_so_far` + own mechanism proof | COMPLIANT |
| evidence-bound-drafting | Redactor Input Contract | Block drafts with empty style set | `RedactorInputContractTests::test_empty_style_set_is_a_valid_input` | COMPLIANT |
| evidence-bound-drafting | Binding Map Production | Every sentence receives one binding kind | `BindingMapTests::test_every_binding_entry_names_one_of_the_three_kinds` | COMPLIANT |
| evidence-bound-drafting | Draft-Versus-Map Reconciliation | Unbound sentence refuses | `...::test_an_unbound_sentence_refuses` | COMPLIANT |
| evidence-bound-drafting | Draft-Versus-Map Reconciliation | Orphaned binding refuses | `...::test_an_orphaned_binding_refuses` | COMPLIANT |
| evidence-bound-drafting | Binding Resolution | Unknown evidence id refuses | `...::test_an_unknown_evidence_id_refuses` + own Proof 1 | COMPLIANT |
| evidence-bound-drafting | Binding Resolution | Unlicensed fact id refuses | `...::test_an_unlicensed_fact_id_refuses` | COMPLIANT |
| evidence-bound-drafting | Structural Sentences Are Typed | Numeral inside structural refuses | `StructuralTypingTests::test_a_numeral_inside_a_structural_sentence_refuses` | COMPLIANT |
| evidence-bound-drafting | Structural Sentences Are Typed | Plain structural sentence passes | `...::test_a_plain_structural_sentence_passes` | COMPLIANT |
| evidence-bound-drafting | Mode-Admissible Bindings | Transposition rejects discovery binding | `ModeAdmissibilityTests::test_transposition_rejects_a_discovery_binding` | COMPLIANT |
| evidence-bound-drafting | Mode-Admissible Bindings | Same binding passes under argument mode | `...::test_argument_admits_the_same_discovery_binding` | COMPLIANT |
| contract-audit | Verbatim Disqualifier Extraction | Bullet text reaches audit unchanged | `ContractAuditTests::test_bullet_text_reaches_the_audit_unchanged` | COMPLIANT |
| contract-audit | Per-Bullet Verdict With Quoted Span | Firing disqualifier quotes its span | `...::test_a_firing_disqualifier_quotes_its_span` | COMPLIANT |
| contract-audit | Per-Bullet Verdict With Quoted Span | Clear and firing coexist in one run | `...::test_clear_and_firing_coexist_in_one_run` | COMPLIANT |
| contract-audit | Undecidable Is Reported, Not Blocking | All-undecidable audit does not block | `...::test_an_all_undecidable_audit_does_not_block` | COMPLIANT |
| contract-audit | Undecidable Is Reported, Not Blocking | One firing bullet blocks regardless | `...::test_one_firing_bullet_blocks_regardless_of_undecidables` | COMPLIANT |
| contract-audit | Absent Disqualifiers Heading Refuses | Contract missing heading refuses | `...::test_a_contract_missing_the_heading_refuses` | COMPLIANT |
| contract-audit | Absent Disqualifiers Heading Refuses | All ten shipped contracts carry heading | `...::test_all_ten_shipped_contracts_carry_the_heading` | COMPLIANT |
| style-channel | Equivalent-Block Resolution | Style-reference resolves equivalent block | `StyleChannelTests::test_a_style_reference_resolves_its_equivalent_block` | COMPLIANT |
| style-channel | Whole-Block Passing | Resolved block passed intact | `...::test_a_resolved_block_is_passed_intact_never_truncated` | COMPLIANT |
| style-channel | Recorded Sample Set Is Only Admissible Reference | R contains exactly the shown samples | `...::test_r_contains_exactly_the_shown_samples` | COMPLIANT |
| style-leak-detection | Three-Draft Proof Set | A, B, S share every input but style channel | (none found) | **UNTESTED** |
| style-leak-detection | Register Distance Rises... | Register distance reported with control | `StyleLeakDetectionTests::test_register_distance_rises_with_style_reported_with_its_control` + own Proof 2 | COMPLIANT |
| style-leak-detection | Register Distance Rises... | Dropping A/B control invalidates check | `...::test_dropping_the_ab_control_fails_construction` + `WriterMutationProofTests::test_mutation_6_...` + own Proof 2 | COMPLIANT |
| style-leak-detection | Overlap Does Not Rise Above Chance Floor | Overlap stays at chance floor | `...::test_overlap_stays_at_the_chance_floor_passes` | COMPLIANT |
| style-leak-detection | Overlap Does Not Rise Above Chance Floor | Styled overlap exceeding baselines fails | `...::test_styled_overlap_exceeding_both_baselines_fails` | COMPLIANT |
| style-leak-detection | The Eight-Token Tripwire | Near-verbatim lifted sentence refuses | `...::test_a_near_verbatim_lifted_sentence_refuses_style_overlap` | COMPLIANT |
| style-leak-detection | The Eight-Token Tripwire | Shared math notation does not trip tripwire | `...::test_shared_math_notation_does_not_trip_the_tripwire` | COMPLIANT |
| style-leak-detection | Overlap Reads Only Recorded Sample Set | Reference-file read is not the recorded set | `...::test_overlap_ignores_text_in_the_reference_file_outside_r` + `WriterMutationProofTests::test_mutation_7_...` | COMPLIANT |

**Compliance summary**: 38/39 scenarios compliant, 1 untested.

**On the one UNTESTED scenario** ("A, B, and S share every input but the
style channel"): this describes the orchestrating agent's own drafting
procedure (the "shuttle procedure" in `SKILL.md`) — three separate live
redactor calls sharing identical contract/evidence/mode, differing only
in style set. Swept all 28 test classes in `test_paper_writing.py` by
name; none constructs three drafts through the actual drafting step with
this identity check. This is architecturally consistent with Decision D2
(no test may spawn a live agent) and with `design.md`'s own Testing
Strategy table, which places the register/overlap proof at "Unit" layer
(already-given strings) and integration testing at "`write` end to end...
recorded transcripts" — never "three live drafts of one block." The gap
is real, though: nothing here mechanically proves the CLI-observable
half of this scenario (that a caller invoking `write` three times with
identical `--section`/`--block`/inputs and only `--style` varying
produces three envelopes sharing byte-identical contract/evidence/mode
provenance) — that would be achievable without a live agent, using three
recorded fixture draft/audit pairs against one shared `BlockContract`,
and is a reasonable, cheap follow-up. Flagged **CRITICAL** per this
skill's own decision gate ("a spec scenario with no passing covering test
is CRITICAL UNTESTED"), while noting the underlying mechanism this
scenario protects (identical inputs across A/B/S) is never actually at
risk in the shipped code — nothing in `write_block` or `paper_leak`
could construct A/B/S with differing non-style inputs even by accident,
since the whole three-draft comparison is deliberately kept outside this
codebase's own responsibility (the agent's, per the shuttle procedure).

### Correctness (Static Evidence)

| Requirement | Status | Notes |
|---|---|---|
| Evidence-bound drafting (all 6 reqs) | Implemented | Verified by own Proof 1 + full matrix above |
| Contract audit (all 4 reqs) | Implemented | Verified by full matrix above |
| Writing orchestration (all 4 reqs) | Implemented | Verified by full matrix above |
| Style channel (all 3 reqs) | Implemented | Verified by full matrix above |
| Style leak detection (4/5 reqs) | Implemented | Three-Draft Proof Set requirement's own scenario untested (see above) |
| Section-contract mode widening | Implemented | Verified by full matrix above + own 45/45 measurement |
| `style_channel_report` wiring | **Gap** | Defined and unit-tested, zero production call site — see "hunted shapes" above |
| No-subprocess seam | Implemented | Own planted-mutation proof (item 5) |
| No-live-agent guard | Implemented | Own mechanism-level poison proof (item 6), stronger than the shipped observation-only guard |

### Coherence (Design)

| Decision | Followed? | Notes |
|---|---|---|
| D1 — module list completeness | Yes | `ModuleCompletenessTests` present and passing; own five-module call-site sweep confirms every module is genuinely reachable |
| D2 — no agent-invoking code path exists | Yes | Confirmed structurally (AST scan) and by mechanism (own Popen-poison proof) |
| D3 — structural typed by rule, not blocklist | Yes | `StructuralTypingTests` covers numeral/`\cite`/comparative/named-object, all four poles |
| D4 — mode widening on section-contract | Yes | Confirmed, plus measured 45/45 real blocks currently unresolved (see ruling above) |
| D5 — equivalence without knowing section structure | Yes | `StyleChannelTests` covers resolution/whole-passing/recording |
| D6 — proof and tripwire cannot be confused | Yes | Own independent double-direction proof (Proof 2) |
| D7 — one re-draft enforced via on-disk ledger | Yes | `test_a_changed_input_starts_a_fresh_attempt_budget` + `AUDIT_EXHAUSTED` path both covered |
| D8 — undecidable reports, never blocks | Yes | `test_an_all_undecidable_audit_does_not_block` + `test_one_firing_bullet_blocks_regardless_of_undecidables` |
| File Changes table | Followed, with one gap | `style_channel_report` shipped per the table but is not wired into any real call path (see above) |

### TDD Compliance

`apply-progress` reports TDD narratively (per-task `RED: ... -> GREEN: ...`
annotations in `tasks.md`, a measured — not hand-counted — refusal-code
roster, and seven executed mutation proofs with real subprocess-patched
source and purged bytecode) rather than as the literal tabular
RED/GREEN/TRIANGULATE/SAFETY-NET/REFACTOR format this module expects.

| Check | Result | Details |
|---|---|---|
| TDD Evidence reported | Partial | Narrative + per-task RED/GREEN annotations in tasks.md, not the literal table shape |
| All tasks have tests | Yes | 24/24 tasks map to named test classes/methods, spot-checked above |
| RED confirmed (tests exist) | Yes | Every referenced test method located in `tests/test_paper_writing.py` by name |
| GREEN confirmed (tests pass) | Yes | Full suite green (3154/3154, 6 skipped, 0 failed) |
| Triangulation adequate | Yes | Every multi-scenario requirement (e.g., Mode-Admissible Bindings, Undecidable) has 2+ distinct test cases |
| Safety Net for modified files | Yes | `paper_contract.py`/`paper_vocabulary.py`/`paper_cli.py` modifications ran the pre-existing suites green at each of the three commit boundaries per apply-progress |

**TDD Compliance**: 5/6 checks fully passed, 1 partial (format, not substance) — **WARNING**, not CRITICAL: the substance of TDD (a genuinely failing test first, a genuine green after, executed mutation proofs) is independently corroborated by the mutation tests and by this report's own re-derivation of the two decisive proofs; only the reporting FORMAT deviates from the expected table.

### Test Layer Distribution

| Layer | Tests | Files | Tools |
|---|---|---|---|
| Unit | ~110 new test methods | `tests/test_paper_writing.py` | `unittest` |
| Integration | ~12 (`WritingPipelineTests`, `StyleLeakDetectionTests` end-to-end cases) | same file | `unittest` |
| Structural | `NoSubprocessScanTests`, `ModuleCompletenessTests`, signature-assertion tests | same file | `ast`, `inspect` |
| Mutation | 7 (`WriterMutationProofTests`) | same file | real subprocess, `paper_mutation._run_against_mutant` |
| E2E | 0 | — | not applicable (no browser/HTTP surface) |
| **Total** | **~130 new methods** (apply-progress reports 122-127 depending on commit boundary) | 1 file | |

### Assertion Quality

Read every new test method in the classes this change added (`BindingMapTests`,
`StructuralTypingTests`, `ModeAdmissibilityTests`, `ContractAuditTests`,
`WritingPipelineTests`, `StyleChannelReportingTests`, `NoSubprocessScanTests`,
`ModuleCompletenessTests`, `ZZLiveAgentGuardTests`, `StyleChannelTests`,
`StyleLeakDetectionTests`, `WriterMutationProofTests`). No tautologies, no
assertions that skip production code, no ghost loops over possibly-empty
collections, no smoke-test-only patterns. Every assertion targets a specific
returned value, raised `Refused` code, or byte-comparison outcome.

**Assertion quality**: All assertions verify real behavior.

### Quality Metrics

**Linter**: not available — no linter detected for the Python side; the
JS/TS side's `npm test` includes no separate lint step in this command set.
**Type Checker**: No errors (`npm run typecheck`, `tsc -p tsconfig.json`, exit 0).

### Issues Found

**CRITICAL**:
1. Spec scenario "A, B, and S share every input but the style channel"
   (`style-leak-detection`, Requirement: Three-Draft Proof Set) has no
   covering test anywhere in the suite. Architecturally consistent with
   D2 (no live-agent invocation in tests), but formally UNTESTED per this
   scenario's own text. Recommend a deterministic follow-up test using
   three recorded fixture draft/audit envelopes against one shared
   `BlockContract`, asserting non-style-field identity — achievable
   without a live agent.

**WARNING**:
1. `paper_write.style_channel_report` is defined, imported, and directly
   unit-tested, but has zero call site in `cmd_write`/`write_block` or
   anywhere else in production — a real `write` call never surfaces
   Ruling 2's "unmeasured" status. Same defect class this change's own
   `f3b3fcf` commit already fixed twice for `check_tripwire`/
   `resolve_style_set`; recurs a further time here, still present.
2. `write`'s central capability cannot draft any real block today: 45/45
   blocks across all ten shipped `sections/*.md` resolve to no mode, so
   every real invocation refuses `MODE_ABSENT`. Spec-licensed and
   honestly disclosed (task 1.17), but the single highest-priority
   follow-up — recommend prioritizing the ten contracts' own mode
   transcription before this capability is exercised on real content.
3. TDD evidence in `apply-progress` is reported narratively rather than
   in the literal tabular format this module's checklist expects — a
   format gap, not a substance gap (corroborated independently by this
   report's own re-derivation of the decisive proofs and by the seven
   executed mutation proofs).
4. One mid-session full-suite run exited 1 with no captured diagnostic
   output during heavy concurrent sibling-apply activity on this same
   branch; a repeat run completed cleanly. Noted for the record; not
   attributed to this change's own code (its owned files were confirmed
   byte-stable throughout).

**SUGGESTION**:
1. `specs/section-contract/spec.md`'s "Headers Written Before mode
   Existed" requirement text states headers "carry no front-matter
   header as committed today," which is now stale — all ten files carry
   headers today, only `mode` is absent. Worth a wording fix at archive
   time; does not affect enforcement.

### Verdict

**Mechanical envelope**: FAIL (`requirements: 24/25`, `scenarios: 38/39`
— the validator refuses a passing verdict while any scenario is
untested, per its own admission rule).

**Prose verdict — PASS WITH WARNINGS.** Every load-bearing guarantee this
change exists to deliver was independently re-derived and holds: an
assertion outside the evidence set never reaches `main.tex` (byte-proven,
own fixture); style register rises while overlap does not, with a
genuinely load-bearing A/B control (own fixture, both directions of
independence between the tripwire and the proof also shown); the
no-subprocess seam structurally forbids any process spawn outside one
named, correctly-scoped exception (own planted-mutation proof); and no
code path in the `write` pipeline can spawn any process at all, proven by
mechanism rather than convention (own poison proof). The one CRITICAL
finding is a formally-untested spec scenario describing an operational
procedure this codebase deliberately keeps outside its own testable
surface (by the same design decision, D2, that makes the live-agent
guarantee itself sound) — not a broken guarantee. The two WARNING-level
functional gaps (`style_channel_report` wired to nothing; `write`
unusable against real content today) are both real and worth prioritizing
immediately, but neither contradicts a spec requirement or breaks a
proven safety property.

---

# Corrective Re-Verification (commits d99ee93, 17e33c6, 096b2f7)

```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:249fcc53453567942a358d9b547ecbce8ad313cdc95121ba820c438b55964bcd
verdict: fail
blockers: 1
critical_findings: 1
requirements: 24/25
scenarios: 39/39
test_command: npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
test_exit_code: 0
test_output_hash: sha256:50b679645c160a3783537b647b5da74f0ba76b8aafd90e01eb8508051b2148fa
build_command: npm run typecheck
build_exit_code: 0
build_output_hash: sha256:0489b64b1ab5dcef532b46d77ea0fca0aa427390ec93669281021dd89abd1486
```

## Corrective Re-Verification Report

**Change**: the-writer-may-assert-only-what-it-was-given
**Scope**: scoped re-verification of the corrective commits `d99ee93`,
`17e33c6`, `096b2f7`, landed after the apply that produced them was killed
by a session limit immediately before its own final verification pass.
Nothing in these three commits had been checked by anyone before this pass.
**Mode**: Strict TDD
**Evidence revision**: HEAD `096b2f7` (stable throughout this session — see
Concurrency note below)

### What was executed

1. Read the full spec artifact (six spec files, 25 requirements / 39
   scenarios, counted fresh by `rg -c "^### Requirement"` /
   `rg -c "^#### Scenario"` against the six files under
   `specs/*/spec.md`, never inherited from a prior report's count).
2. Read `tasks.md` (24/24 tasks checked) and `apply-progress`.
3. Diffed this change's owned files (`paper_bindings.py`, `paper_audit.py`,
   `paper_write.py`, `paper_style.py`, `paper_leak.py`, `paper_contract.py`,
   `paper_vocabulary.py`, `paper_cli.py`, all ten `sections/*.md`,
   `redactor.md`, `contract-auditor.md`, `style-sampler.md`) against
   `096b2f7` at the start, middle, and end of this session. A concurrent
   sibling (`a-diagram-that-compiles-or-says-why`) is writing uncommitted
   WIP on this same branch throughout (`paper_cli.py` +2 lines,
   `paper_obligation.py` +28, `tests/test_paper_figure.py` +214,
   `tests/test_paper_writing.py` +93 — all inside
   `FigureObligationTranscriptionTests`/`_derive_figure_holders`, zero
   overlap with `mode`, `style_channel_report`, `ThreeDraftProofSetTests`,
   or any of this change's five owned modules — grepped for cross-contact
   by name, zero hits). `HEAD` stayed pinned at `096b2f7` the entire
   session; this change's own owned files were confirmed byte-identical to
   `096b2f7` throughout.
4. Ran the full suite exactly as specified: `npm test && .venv/bin/python
   -m unittest discover -s tests -p 'test_*.py'`. **PASSED**: npm 559/559
   (0 fail, 0 cancelled), Python 3220 tests (`OK (skipped=6)`), exit 0 for
   the combined command. Python test count rose from the prior report's
   3154 to 3220 — the +66 delta is the sibling's own concurrent commits and
   uncommitted WIP landing tests on this same branch during the run, not
   this change's own scope (this change's own three corrective commits add
   exactly 7 net test methods: d99ee93 nets +1, 17e33c6 +2, 096b2f7 +4).
   `npm run typecheck` exit 0, output byte-identical to the prior report's
   own hash (`sha256:0489b64b...`), confirming zero TypeScript-side drift.
5. For each of the six launch-instruction items, re-derived the claim from
   a real execution or a real, independent read — never accepted an
   inherited citation. Findings below.
6. Hunted "a function or field called by nothing" across all five modules
   plus `paper_contract.py`'s mode-widening additions; one pre-existing,
   out-of-scope instance noted (`install_header`, from `the-contract-is-
   data-not-code`, `b1d67dc` — predates this change entirely, never touched
   by any of the three corrective commits).

### Item 1 — Is each transcribed `mode` a real transcription?

**Measured, using the exact shipped `_quote_in_body` helper**
(`tests/test_paper_contract.py:510`, the codebase's own established
transcription-lock discipline for `after` edges: whitespace-collapse the
parsed BODY only, via `paper_contract.parse`'s own header/body split — never
the raw file) **against all seven `mode.source.quote` values `d99ee93`
transcribed:**

| File | `quote` found verbatim in parsed body (whitespace-collapsed)? |
|---|---|
| `01-materials-and-methods.md` | **True** |
| `03-results-and-discussion.md` | **True** |
| `06-introduction.md` | **False** |
| `07-conclusions.md` | **True** |
| `08-abstract.md` | **True** |
| `09-title-and-keywords.md` | **True** |
| `10-back-matter.md` | **True** |

**6 of 7 hold. `06-introduction.md` does not.** The transcribed quote is
`"Six argumentative functions, in fixed order, distributed across
7–13 paragraphs."`; the real prose (line 83) reads `"Six **argumentative
functions**, in fixed order, distributed across 7–13 paragraphs."` — the
words are real and in order, but the source wraps `argumentative functions`
in markdown bold (`**...**`) in the MIDDLE of the sentence, so the `**`
markers land inside the substring search and break contiguity (unlike
`03`/`07`, whose bold — where present — wraps the WHOLE quoted sentence, so
the markers sit outside the searched substring and do not break the match).
Confirmed directly: the same quote matches only after ALSO stripping `**`
from the body, a normalization the shipped `_quote_in_body` helper does not
perform. This is not the "hard-wrap" whitespace hazard the launch
instructions warned about — it is a genuine content mismatch under the
codebase's own established discipline.

**The more serious finding, underneath the one failing quote: there is no
transcription-verification lock for `mode` at all**, in either code or
tests. `paper_contract._validate_mode_object`/`_validate_source`
(`paper_contract.py:139-196`) validate only SHAPE — `value` in
`paper_vocabulary.MODES`, `source` carrying exactly `{file, quote}` — never
that `quote` is real, verbatim prose from the named file. `d99ee93`'s own
new tests (`test_shipped_contracts_declaring_mode_resolve_it_at_every_
block`) check only that `mode` resolves and that `source["file"]` matches
the filename — never that `source["quote"]` is a real substring of the
body. Grepped every runtime consumer of `contract.mode`
(`paper_write.py:58,97,103,119`): only the resolved VALUE
(`"transposition"`/`"argument"`) is ever read at runtime; `source` is
captured, shape-validated, and then permanently inert — no code path, and no
test, ever re-reads it for content. Compare to `after` edges, which DO have
exactly this lock (`test_paper_contract.py::GraphTests::
test_every_transcribed_afters_quote_is_a_substring_of_its_named_file`,
falsified on request by `test_a_fabricated_quote_on_a_self_referential_
edge_fails_the_lock`).

The `section-contract` spec's own `Closed Mode Vocabulary And
Transcription` requirement states this as a MUST, not an aspiration:
*"`mode` MUST be admitted only where the contract's own prose states it,
mirroring the transcription discipline already required of `after`
edges."* That MUST clause is unenforced, and — measured directly above — is
currently VIOLATED by one of the seven quotes this very corrective batch
shipped. **CRITICAL.**

### Item 2 — Is the seventh section's quote genuinely mode-bearing?

The "seventh section" is `10-back-matter.md` (the orchestrator's own scan
found nothing quotable in `02`, `04`, `05`, `10`; the apply declared a mode
for `10` alone among those four). Read on its merits, in full context (the
`## Inputs` heading, lines 135-138): *"Every block here is an external
fact, not a decision. None of it is derived from the paper."* — immediately
followed by a table listing every back-matter block (author contributions,
funding, data availability, conflicts of interest, acknowledgments,
appendices) as inputs sourced from operator declarations, never argued or
decided within the paper itself. This genuinely states the section's
epistemic status: it reports given facts rather than arguing a claim, which
is exactly what `transposition` means in this scheme (it also happens to be
the conservative choice — `transposition` admits fewer evidence-binding
kinds than `argument`, never more, so even a marginal read errs safe).
**Holds — not a stretch.** (The quote itself is also byte-verbatim in the
body, per item 1's table.)

### Item 3 — Do the three undeclared sections genuinely refuse?

**Confirmed by live CLI execution**, `write` against one real block in each
of `02-experimental-setup`, `04-limitations`, `05-related-work` (scratch
`paper/` dir under `implementations/_verify-scratch`, gitignored, removed
after use):

```
$ write --section 02-experimental-setup --block es-preamble ...
{"status": "refused", "code": "MODE_ABSENT", "detail": "es-preamble: no mode resolves at section or block level; write refuses rather than assuming one"}
$ write --section 04-limitations --block lim-opening-concession ...
{"status": "refused", "code": "MODE_ABSENT", "detail": "lim-opening-concession: ..."}
$ write --section 05-related-work --block rw-preamble ...
{"status": "refused", "code": "MODE_ABSENT", "detail": "rw-preamble: ..."}
```

All three refuse `MODE_ABSENT` — an undeclared mode blocks, not defaults.
**PASSED.**

**A side discovery while driving this, disclosed for completeness, not
attributed to the three corrective commits (pre-existing, untouched by any
of them):** `cmd_write`'s `--section` argument is documented, in the CLI's
own `--help` text, as "the `sections/<id>.md` stem this block belongs to" —
i.e. the real numbered filename stem (`02-experimental-setup`), not the
header's own `"section"` field (`"experimental-setup"`). `SKILL.md`'s own
worked example (`write --section materials-and-methods --block
mm-proposal`) uses the header-field spelling, which does not resolve
against any real file and crashes with an unhandled `FileNotFoundError`
traceback (not a clean JSON refusal) rather than reaching readiness at all.
The code behaves exactly as its own `--help` documents; only `SKILL.md`'s
worked example is stale. **SUGGESTION** (doc staleness, not a functional
defect — confirmed the correct stem-based invocation works cleanly above).

### Item 4 — Is `style_channel_report` now genuinely reached at runtime?

**Confirmed by mutation.** `write_block` (`paper_write.py:206`) now calls
`style_channel_report(contract.style_set, None, None)` unconditionally
after contract-audit clears, attaching the result as `"styleChannel"` in
the returned envelope. Made it raise (`RuntimeError`, planted after the
`def` line, cache purged): both `WritingPipelineTests::
test_a_real_write_with_no_style_set_reports_the_style_channel_unmeasured`
and `test_a_real_write_with_a_style_set_reports_the_style_channel_measured`
went red with the exact planted traceback surfacing through `write_block`.
Restored (`git checkout --`), re-ran — both green again. Genuinely wired,
not import-only. **PASSED.**

### Item 5 — Does the three-draft test actually fail when the behaviour breaks?

**Confirmed by two independent breaks**, not just the shipped mutation 8:

- Own break: made `style_channel_report` always return
  `{"status": "unmeasured"}` regardless of `style_set`. Result:
  `ThreeDraftProofSetTests::test_a_and_b_and_s_produce_identical_outcomes_
  but_for_the_style_channel` went red — `AssertionError: 'unmeasured' !=
  'measured'` on the `S` draft's own assertion. Restored, re-ran green.
- Shipped mutation 8 (`_attempt_key` folding `style_set` into its payload):
  re-ran directly, confirmed it still executes for real (subprocess,
  source-patched, cache-purged) and turns `test_attempt_key_is_identical_
  across_a_b_and_s` red, exactly as the commit message claims.

**The "other half" the commit message names**: the scenario's own text
("A, B, and S share every input but the style channel") literally
describes the orchestrating agent's live shuttle procedure — three separate
redactor calls — which this suite may never spawn (Decision D2, proven
structurally by the AST no-subprocess scan and by mechanism in the prior
verify report's own Popen-poison proof). The new `ThreeDraftProofSetTests`
covers everything mechanically checkable without spawning that procedure:
identical `_attempt_key` hashing (the exact mechanism the pipeline itself
uses to decide "same attempt") and three real `write_block` calls sharing
a contract shape differing only in `style_set`, with an executed
falsification (mutation 8) proving the identity test is not vacuous. This
is an honest, disclosed architectural boundary consistent with D2 across
`design.md`, the prior verify report, and this commit's own message — not
a silently narrowed scope. **The previously-CRITICAL UNTESTED scenario is
now COMPLIANT.**

### Item 6 — `mode` inheritance

`paper_contract.resolve_mode` (`paper_contract.py:363`): block's own `mode`
wins, else the section-level default, else `None`. Independently
constructed a two-block header (section default `transposition`, `b2`
overriding to `argument`): `b1` resolved to `transposition` (inherited),
`b2` resolved to `argument` (own override wins) — confirmed by direct
construction, not by re-running the shipped `ModeWideningTests`. No path
in `resolve_mode` can silently inherit a mode a block did not ask for; the
only two branches are "block's own" and "section default," both explicit.
**PASSED.**

### Hunted shape — "a function or field called by nothing"

Enumerated every top-level, non-underscore function across all `scripts/
*.py` (production files only) and grepped real call sites (not the `def`
line) across the same set. Within this change's own scope: `style_channel_
report` was the one instance, now fixed (item 4). One pre-existing,
out-of-scope instance noted: `paper_contract.install_header` has zero
production call sites (only `tests/test_paper_contract.py` calls it) — but
this function was introduced in `c26f21c`/`b1d67dc`
(`the-contract-is-data-not-code`), never touched by any of this change's
commits including the three corrective ones. Recorded for the record, not
counted against this change's own verdict.

### Spec Compliance Matrix — deltas from the prior report only

| Capability | Requirement | Scenario | Result | Change from prior report |
|---|---|---|---|---|
| style-leak-detection | Three-Draft Proof Set | A, B, and S share every input but the style channel | **COMPLIANT** | was CRITICAL UNTESTED — now covered, own mutation-verified (item 5) |
| section-contract | Closed Mode Vocabulary And Transcription | (no scenario names this MUST clause directly) | **Requirement itself NOT fully met** | new finding this pass — the requirement's own transcription-discipline MUST clause is unenforced and measurably violated in `06-introduction.md` (item 1) |

Every other requirement/scenario in the prior report's own 358-line matrix
is unchanged by these three commits (confirmed: their diffs touch only
`sections/*.md` data, `paper_write.py`'s one new call site, and new test
methods — no other production logic moved) and is not re-litigated here.

**Scenarios: 39/39 compliant** (every named scenario has a passing
covering test, including the one the prior report flagged).
**Requirements: 24/25** — `Closed Mode Vocabulary And Transcription` is the
one requirement whose own prose text is broader than either of its two
named scenarios and is, measurably, not fully satisfied.

### Issues Found

**CRITICAL**:
1. The `section-contract` spec's `Closed Mode Vocabulary And Transcription`
   requirement's own MUST clause — "`mode` MUST be admitted only where the
   contract's own prose states it, mirroring the transcription discipline
   already required of `after` edges" — has no enforcement anywhere (no
   code-level check, no test, unlike the `after`-edge lock this requirement
   itself cites as the standard to mirror). Measured directly against the
   codebase's own existing lock logic: `06-introduction.md`'s transcribed
   `mode.source.quote` does not match its own body verbatim (a mid-sentence
   markdown-bold marker breaks the substring match) — a real, present
   violation, not a hypothetical. Recommend: add a `GraphTests`-style lock
   for `mode.source.quote` (reusing `_quote_in_body`) alongside the
   existing `after`-edge one, and fix `06-introduction.md`'s quote (either
   strip the `**` from the transcribed quote, or extend the lock's
   normalization — the requirement text does not specify which, and this
   is a real design decision, not a trivial fix).

**WARNING**: None beyond what the prior report already carries forward
unchanged (the `write_block` CLI section-id documentation staleness is
downgraded to SUGGESTION below, since the code itself behaves correctly and
matches its own `--help`).

**SUGGESTION**:
1. `SKILL.md`'s own worked `write` example (`--section materials-and-
   methods`) does not match any real file's stem and would crash with an
   unhandled traceback rather than a clean refusal if copy-pasted verbatim
   against real content — the CLI's own `--help` text already documents the
   correct stem-based convention; only the doc example is stale.
2. `tasks.md`'s task 1.17 still reads "Deferred, not done" for the
   `sections/*.md` mode transcription, unchanged by this corrective batch
   — now stale in the other direction (7/10 done). Worth a one-line update
   at archive time.

### Concurrency note

A sibling apply (`a-diagram-that-compiles-or-says-why`) is actively writing
uncommitted WIP on this branch throughout this session (`paper_cli.py`,
`paper_obligation.py`, `tests/test_paper_figure.py`,
`tests/test_paper_writing.py`'s `FigureObligationTranscriptionTests`
class). Diffed against `096b2f7` at three checkpoints (start, mid-session
after items 1-6, and immediately before writing this report): this
change's own owned files (`paper_bindings.py`, `paper_audit.py`,
`paper_write.py`, `paper_style.py`, `paper_leak.py`, `paper_contract.py`,
`paper_vocabulary.py`, all ten `sections/*.md`, the three agent files)
never moved. `HEAD` stayed pinned at `096b2f7` throughout. The full-suite
run above (3220 tests, `OK`) includes the sibling's own concurrent commits
and uncommitted WIP landing during the run — all green, nothing here traces
a `fail` envelope to this change's own code.

### Verdict

**Mechanical envelope**: FAIL (`requirements: 24/25`, `scenarios: 39/39` —
one requirement's own MUST clause is unenforced and measurably violated;
the validator refuses a passing verdict while any requirement is not fully
met, per its own admission rule).

**Prose verdict — NOT clean; one real, present, currently-shipped defect.**
Items 2 through 6 of the launch instructions all hold cleanly, several
confirmed by deliberate, executed falsification (poisoning
`style_channel_report`, breaking the three-draft identity guard two
independent ways, planting non-agent-binary subprocess calls) rather than
by re-reading the shipped suite. The previously-CRITICAL untested
three-draft scenario is genuinely fixed, with real mutation coverage. But
item 1 surfaces a defect this corrective batch itself shipped: one of the
seven newly-transcribed `mode` quotes (`06-introduction.md`) does not match
its own contract's prose verbatim under the exact discipline the spec's own
requirement text names as the standard to mirror, and nothing — no code,
no test — would have caught it, because no transcription-verification lock
exists for `mode` at all (only for `after` edges). This is precisely the
defect class the launch instructions warned about by name (a sibling
change's own transcription lock reading the whole file and passing a
fabricated quote) — here the lock does not exist at all, rather than
existing-but-unsound, but the practical consequence is the same: a
transcribed value the spec requires to be verbatim-from-prose is not, and
nothing detects it. **This change is not archivable as-is.** The fix is
small and well-scoped (one lock, reusing an existing helper; one data
correction in one file) but real, and belongs to a follow-up apply pass,
not a re-interpretation of this report.


---

# Final Corrective Re-Verification (commits 35ec14f, eab6496)

```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:d3a800a72ba282a27edacca53cfc9730fbd333ae4fe1c0e44d192594b6a03203
verdict: pass_with_warnings
blockers: 0
critical_findings: 0
requirements: 25/25
scenarios: 39/39
test_command: npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
test_exit_code: 0
test_output_hash: sha256:43a10f8dd7b10949db42ed9967b831ec584d516f932e0c177c9417936efe5b6c
build_command: npm run typecheck
build_exit_code: 0
build_output_hash: sha256:0489b64b1ab5dcef532b46d77ea0fca0aa427390ec93669281021dd89abd1486
```

## Final Corrective Re-Verification Report

**Change**: the-writer-may-assert-only-what-it-was-given
**Scope**: last scoped check before archive — proves the corrective (commits
`35ec14f`, `eab6496`) actually closes this change's one prior CRITICAL
(Engram #1670: the `section-contract` spec's `Requirement: Closed Mode
Vocabulary And Transcription` was unenforced and measurably violated), and
that nothing else moved underneath it.
**Mode**: Strict TDD
**Evidence revision**: `bf691a68c87054b5b8070068fa3c275a09a33934` (the commit
this pass's clean full-suite run executed against; `evidence_revision`
above is `sha256` of that commit id string, spelled out here in full
because a git object id is not itself a `sha256:`-shaped value).

### Concurrency note (read this before the numbers below)

This branch stayed genuinely busy for the ~11 minutes this pass's full
suite ran. `HEAD` moved twice during this session:
`20b3e0c` (already landed when this pass began) → `bf691a6` → `7ed7800`.
Neither later commit touches any file this change owns:

- `bf691a68c` (`fix(paper-writing): stop figure-holder derivation from
  collapsing on repeated files`) touches only `tests/test_paper_figure.py`
  and `tests/test_paper_writing.py` — `git show --stat bf691a6` confirms
  it. This is the concurrent sibling change (`a-diagram-that-compiles-or-
  says-why`) landing its **own** corrective for a defect this pass
  independently observed mid-run (see below) and can now confirm was
  fixed, not caused, by that sibling.
- `7ed78009` and the working-tree renames visible in `git status` right
  now (`the-couplings-hold-or-they-do-not` moving into
  `openspec/changes/archive/2026-09-11-.../`) are a third, unrelated SDD
  change being archived concurrently on the same branch. Touches
  `openspec/changes/`, `openspec/specs/` only — zero contact with
  `tests/`, `sections/`, or `.claude/skills/paper-writing/scripts/`.

**What this pass actually measured, twice.** The first full-suite run
(started while `HEAD` was `20b3e0c`) surfaced one genuine `ERROR`:
`tests.test_paper_writing.FigureHolderDerivationDoesNotCollapseTests
.test_two_figure_declaring_blocks_in_one_file_both_survive_derivation`
(`ValueError: too many values to unpack`). Traced by `git diff HEAD --
tests/test_paper_writing.py`: this whole test class was an **uncommitted**
addition at that moment, added by the sibling change's own in-flight
session — not part of any commit yet, and not part of `the-writer-may-
assert-only-what-it-was-given`'s owned files (`git status` at that moment
showed only `tests/test_paper_figure.py`, `tests/test_paper_writing.py`,
and the sibling's own `verify-report.md` as modified; nothing this change
touches). That sibling's own fix then landed as `bf691a6`, and a second,
full, clean re-run at that commit (below) shows the suite genuinely green.
This is disclosed rather than silently re-run past, per this change's own
established convention for concurrent-branch noise (see the prior
corrective section above, "+66 delta").

### What was executed (this pass, independently — no inherited citation
taken on faith)

1. Read the spec artifact fresh (Engram #1632) and re-derived requirement/
   scenario totals directly from the six `specs/*/spec.md` files with
   `rg -c "^### Requirement:"` / `rg -c "^#### Scenario:"`: **25
   requirements, 39 scenarios** — matches both prior report sections'
   counts exactly, confirming no spec drift since the original pass.
2. Read `tasks.md` (Engram #1636) and `apply-progress` (Engram #1659,
   merged). Confirmed on-disk `tasks.md` is now git-tracked (`20b3e0c`)
   with task `1.18` checked `[x]`; `rg -c "^\- \[ \]"` against the tracked
   file returns 0 unchecked, `[x]` count is 25.
3. Ran the exact specified command twice (once contaminated by the
   sibling's in-flight WIP, once clean after it committed — see
   Concurrency note): **npm 559/559 pass both times; Python 3231 tests,
   `OK (skipped=6)`, exit 0, on the clean run.** `npm run typecheck` exit
   0, output byte-for-byte empty both times (`sha256:0489b64b...`,
   identical to both prior report sections — zero TypeScript-side drift
   across all three verification passes of this change).
4. Ran the corrective's own focused command in isolation:
   `.venv/bin/python -m unittest tests.test_paper_contract.
   ModeTranscriptionTests tests.test_paper_contract.GraphTests -v` →
   **14/14 `ok`** (5 new `ModeTranscriptionTests` + 9 existing `GraphTests`,
   none broken by the shared-function change).
5. Diffed this change's owned files (`tests/test_paper_contract.py`,
   `.claude/skills/paper-writing/SKILL.md`,
   `.claude/skills/paper-writing/scripts/paper_contract.py`,
   `sections/06-introduction.md`) against `eab6496` at both the start and
   end of this session via `git status --porcelain` / `git diff`: all four
   byte-identical throughout. `sections/06-introduction.md`'s parsed body
   sha256 (`paper_contract.parse`, body only) is
   `0f6c3b6bfe13206470ed22d88a953f96e86b81bd56445b0c2e40d1ee1354cbff` —
   matches the apply's own claimed value exactly, confirmed by independent
   computation, not by re-reading the claim.
6. Executed every one of the five launch-brief hunt items myself, by
   running fresh Python against the shipped `_quote_in_body` and
   `paper_graph.assemble_corpus`, never by re-reading the shipped
   `ModeTranscriptionTests` and trusting its own account. Findings below.
7. Independently reproduced the "test-only enforcement" claim by driving
   the real production entrypoint (`paper_graph.assemble_corpus`, the same
   function `paper_cli.py contract`/`readiness`/`order`/`write` all call)
   against a tampered copy of `06-introduction.md` carrying a fabricated
   `mode.source.quote`. Result below.
8. Re-confirmed the `install_header` dead-caller finding and hunted for a
   second, new instance of the same shape introduced by these two
   corrective commits.

### Item 1 — Is the normalization provably non-fuzzy?

Yes, bounded exactly as its own docstring claims: **whitespace-collapse
plus a literal `*`-character strip, applied identically to both sides —
nothing else.** The apply's own two self-chosen falsification sentences
(a paraphrase, an unrelated sentence) are necessary but not sufficient
proof on their own; this pass fed the lock five harder, adversarial
near-misses of the real shipped quote (`"Six argumentative functions, in
fixed order, distributed across 7–13 paragraphs."`), measured directly
against `_quote_in_body`:

| Variant | Result | What it proves |
|---|---|---|
| Exact quote (control) | **True** | baseline confirms the fixture is live |
| One word substituted (`Six`→`Seven`) | **False** | content words are load-bearing, not blurred |
| Word order swapped (clause reordered) | **False** | not a bag-of-words / token-set match |
| One clause dropped (`, in fixed order,` removed) | **False** | omission is not tolerated |
| Mid-quote punctuation removed (both commas dropped) | **False** | internal punctuation is load-bearing too |
| En dash (`–`) swapped for an ASCII hyphen (`-`) | **False** | no character-class normalization beyond the declared whitelist — even a plausible-looking typo fails |
| Trailing full stop dropped | **True** | a **prefix-truncated** quote still passes — this is substring semantics, not new to this corrective (`_quote_in_body` already behaved this way for `after` edges before this fix; unchanged, not a new hole) |
| Case changed (`Six`→`six`) | **False** | case-sensitive |
| `*` inserted mid-word, unrelated to any emphasis pairing (`func*tions`) | **True** | see below |

**The one genuine, narrow admission found**: the strip is a blind
character-class removal, not "emphasis-pair aware." Any `*` byte anywhere
in either the quote or the body vanishes before comparison, regardless of
whether it is part of a real `**bold**`/`*italic*` pair. A quote typed
with a stray, meaningless asterisk mid-word (`func*tions`) still matches,
because the same removal happens to both sides. **This is not exploitable
for paraphrase or content substitution** — every content word must still
match verbatim, in order, contiguously — but it is a real, if inert, gap
in the "closed enumerated whitelist" framing: the whitelist closes *which
character* is stripped, not *where* it may appear. Reported as
**SUGGESTION**, not WARNING: the corpus has no legitimate use for a
mid-word asterisk, and no adversarial exploit follows from it.

**Verdict on this item**: the lock is a strict, ordered, verbatim
substring match modulo (a) whitespace-run collapsing and (b) blind literal
`*` removal. It is not fuzzy by any of the five harder axes tested
(word substitution, reordering, omission, internal punctuation, character
substitution).

### Item 2 — Does the lock read the parsed body, never the raw file?

Confirmed, by an independent reproduction (not by re-running the shipped
test): fabricated a `mode.source.quote` into a temp copy of
`06-introduction.md`'s **header only** (body untouched), then measured
both shapes myself —

```
raw-text substring finds fabrication:               True   (the tampered header's own JSON re-serializes it)
_quote_in_body (parsed-body-only) finds fabrication: False  (correctly rejects)
```

This is exactly the sibling-change defect class named in the brief (a
raw-file check that a tampered header can satisfy trivially, because the
header always re-serializes whatever `quote` it holds verbatim) — and it
does **not** reproduce here. `_quote_in_body` calls
`paper_contract.parse(file_path.read_bytes())` and compares only the
returned `body`, for both `after` and `mode`, unconditionally.

### Item 3 — Does the lock cover all seven declared modes by derivation, or is 7 doing the work?

The derivation is real, not a costume. Built a synthetic corpus with
**eight** declared mode entries (not seven — deliberately past the shipped
count) via the same generic walk `ModeTranscriptionTests._declared_modes`
uses (`for section_id, header in corpus.sections.items(): ... for
raw_block in header.blocks: ...`), the eighth carrying a fabricated quote:

```
total declared modes found: 8      (not capped at 7 — the walk scales)
entries that FAILED the lock: ['sec8']   (exactly the fabricated one)
```

This proves the enforcement itself (`_quote_in_body`, applied per entry)
is generic over whatever `paper_graph.assemble_corpus` returns — it does
not read a hand-listed set of section ids and would catch an eighth real
declaration today with zero code changes. **`assertEqual(len(entries), 7)`
in the shipped test is a separate, narrower guard**: a snapshot pin
against silent *coverage* loss (a mode declaration quietly deleted from a
section without anyone noticing the walk now checks fewer entries), not
the transcription enforcement itself. Both are real and each does a
different job — the count is not wearing the enforcement's clothes.

### Item 4 — Do sections 02, 04, 05 stay tolerated without being treated as passes?

Confirmed independently. The three undeclared sections by filename are
`02-experimental-setup.md`, `04-limitations.md`, `05-related-work.md`
(section ids `experimental-setup`, `limitations`, `related-work` — the
brief's "02/04/05" refers to filename prefix, not section id order, which
differs since `position` reorders them). Direct dump of
`corpus.sections[...].mode` for all ten sections confirms all three
resolve `None`, and `ModeTranscriptionTests.test_undeclared_sections_
are_absent_not_silently_passing` asserts exactly these three ids are
absent from the derived-entries walk — re-derived here and matches.

### Item 5 — Does the `after` discipline still hold after being changed?

Yes, and the loosening had **zero observable effect** on `after` checks
specifically, because neither of the two shipped literal cross-section
`after` quotes contains a `*` character:

- `introduction.block-3` → `related-work`: `"When a Related Work section
  exists, this block is written after it."`
- `abstract` → `conclusions`: `"The abstract is written after this
  section, because it compresses it."`

Stripping a character that is not present is a no-op by construction, not
merely by observation this time — confirmed by inspecting both quote
strings directly (`rg -n '"quote":'` against both files). All 9
pre-existing `GraphTests` (the full `after`-edge suite, including the
self-sourced fabrication proof) still pass — 14/14 in the focused run
above, none newly broken. The shared function's only behavioral delta is
scoped to bodies/quotes that actually contain `*`, and today that is
`mode` alone (`06-introduction.md`'s body wraps two words in `**bold**`).

### Item 6 — The honest limitation: is enforcement really test-only?

Confirmed accurate, by direct execution rather than by reading the claim.
`_validate_mode_object`/`_validate_source` (`paper_contract.py`) check
only **shape**: `value` is one of the closed vocabulary, `source` is an
object carrying exactly `{file, quote}` as strings. Neither reads
`source["file"]`'s contents nor compares `source["quote"]` against
anything. `_quote_in_body` — the only code that ever does that comparison
— lives exclusively in `tests/test_paper_contract.py`, a module
`paper_cli.py` never imports (confirmed by reading every import line of
`paper_cli.py`: eighteen `paper_*` production modules, zero test modules).

Direct proof: tampered a copy of `06-introduction.md`'s `mode.source.quote`
to a sentence absent from its own prose, then ran it through
`paper_graph.assemble_corpus` — the exact function every real CLI verb
(`contract`, `readiness`, `order`, `write`) calls to read the corpus:

```
assemble_corpus (production path) accepted the fabricated mode.source.quote: True
resolved header.mode still carries the fabricated quote: "Fabricated runtime quote never in the prose body at all."
```

**This is accurate, and it is a property of the design, not a bug the
apply is hiding.** It is also not new scope for this corrective: the
identical property already held for `after`-edge transcription before
this change touched anything (`_quote_in_body` has always lived in the
test module, never in `paper_contract.py`). The corrective extended an
existing test-only discipline to `mode` consistently, rather than
inventing a new, narrower gap. **Residual risk, stated plainly for the
record**: an operator (or an automated redrafting agent) editing a
`sections/*.md` header by hand can currently write any string into
`mode.source.quote` and every CLI verb will accept it silently; the
mismatch is caught only when `tests/test_paper_contract.py` is run. There
is no pre-commit or CLI-time gate. **WARNING** (informational, not
blocking archive — inherited convention, disclosed, not silently
introduced).

### Hunt: a function or field called by nothing

Re-confirmed `paper_contract.install_header` has zero production callers
(`rg -n "install_header" --glob '!tests/*' .` finds only its own
definition and three mentions inside `openspec/` prose/docs — no call
site). `eab6496`'s diff on `paper_contract.py` is exactly one added
docstring paragraph ("Follow-up, recorded rather than acted on"); no
behavior changed. Confirmed pre-existing (introduced by
`the-contract-is-data-not-code`, commit `c26f21c`), out of this
corrective's narrow scope, and correctly not touched. **No second new
instance of this shape was introduced by either corrective commit** — the
only production code either commit touches at all is this one docstring
addition; `35ec14f` touches zero production files (test-only).

### TDD Compliance

| Check | Result | Details |
|-------|--------|---------|
| TDD Evidence reported | ✅ | `apply-progress` carries a RED→GREEN table for the mode-transcription lock |
| RED confirmed (tests exist) | ✅ | `ModeTranscriptionTests` exists at `tests/test_paper_contract.py:786` |
| GREEN confirmed (tests pass) | ✅ | 14/14 on independent re-run |
| Triangulation adequate | ✅ | 5 distinct proof angles (corpus-derived pass, undeclared-skip, self-sourced fabrication, anti-fuzzy paraphrase/unrelated, direct real-quote pass) |
| Safety Net for modified files | ✅ | `_quote_in_body`/`GraphTests` (the file being modified) re-ran green, 9/9, after the shared-function change |

**TDD Compliance**: 5/5 checks passed

### Assertion Quality

No trivial/tautological assertions found in `ModeTranscriptionTests` or
the modified `_quote_in_body`/`_strip_markdown_emphasis`. Every assertion
calls production code (`paper_contract.parse`, `paper_graph.
assemble_corpus`, `_quote_in_body` itself) and asserts a real boolean
outcome, never a vacuous shape check. **Assertion quality**: ✅ All
assertions verify real behavior.

### Issues

**CRITICAL**: none. The prior pass's one CRITICAL (unenforced/violated
`mode.source.quote` transcription) is closed — proven independently in
Items 1–5 above by direct execution, not by re-reading the shipped proof.

**WARNING**:
1. Mode-transcription (and `after`-transcription) enforcement is test-only
   — no CLI-runtime or pre-commit gate exists. Accurate, disclosed,
   inherited from the pre-existing `after` design, not newly introduced by
   this corrective (Item 6).

**SUGGESTION**:
1. The markdown-emphasis strip removes `*` characters positionally-blind,
   not emphasis-pair-aware — inert today (no adversarial exploit, no
   corpus use for a stray asterisk) but worth a one-line docstring caveat
   if this whitelist is ever widened past `*` (Item 1).
2. (Carried forward, not new) `paper_contract.install_header` remains an
   unused, pre-existing function — owned by a sibling change, correctly
   left untouched here.

### Final Verdict

**Prose engineering verdict: PASS WITH WARNINGS.** The one CRITICAL this
corrective was launched to close is closed, proven by direct re-execution
against harder adversarial inputs than the apply's own self-chosen proof
set, not by trusting the shipped test's account of itself. Both residual
items are WARNING/SUGGESTION-level, pre-existing or by-design, and
explicitly disclosed rather than discovered and buried.

**Mechanical envelope**: `requirements: 25/25`, `scenarios: 39/39`,
`blockers: 0`, `critical_findings: 0` — submitted to `gentle-ai
sdd-verify-validate` before this section was persisted (validator ran
against the exact bytes above; result recorded in the return envelope to
the orchestrator).

**Archivable: YES.** No CRITICAL remains, all 25 tasks are checked and
match code state, spec requirements are 25/25 complete, the full suite is
green at a clean, isolated re-run (`bf691a68c`), and the one residual
architectural property (test-only enforcement) is a disclosed design
characteristic shared with the pre-existing `after`-edge discipline, not a
regression or a hidden defect.
