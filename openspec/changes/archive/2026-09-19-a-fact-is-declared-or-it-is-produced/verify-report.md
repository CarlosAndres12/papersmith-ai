```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:7f969e2e7e9a262c5cfef749e64a3f7919b66c61bf74915beb55e3f9f4f26ca4
verdict: pass
blockers: 0
critical_findings: 0
requirements: 12/12
scenarios: 30/30
test_command: ".venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing tests.test_paper_decisions tests.test_paper_citation tests.test_paper_evidence tests.test_paper_figure tests.test_paper_lifecycle -q"
test_exit_code: 0
test_output_hash: sha256:892f004f6cbf37619ab2059d5dcb86d923ebc80bc199d8d738db7997ff90e2c8
build_command: "npm run typecheck"
build_exit_code: 0
build_output_hash: sha256:0489b64b1ab5dcef532b46d77ea0fca0aa427390ec93669281021dd89abd1486
```

## Verification Report

**Change**: `a-fact-is-declared-or-it-is-produced`
**Re-verify context**: previous `sdd-verify` pass returned FAIL (1 CRITICAL, 3 WARNING, 1 SUGGESTION); Unit 4 (PR 4) closed all five findings. This pass confirms closure and checks for regressions only — it does not re-derive what the prior pass already established as MET (`fact-production`, `paper-declarations`, `coupling-verification`; MET-with-warning `writing-readiness`).
**Branch**: `u4-the-spec-and-the-code-agree` @ `d7fef1f`
**Mode**: Full artifact verification (proposal/design/specs/tasks all present)

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 5 units (0–4), all sub-items `[x]` |
| Tasks complete | All |
| Tasks incomplete | 0 |

### Requirements / Scenarios (measured from the five spec deltas)
| Capability | Requirements | Scenarios |
|---|---|---|
| `contract-input-partition` | 1 | 3 |
| `coupling-verification` | 1 | 3 |
| `fact-production` | 6 | 13 |
| `paper-declarations` | 2 | 4 |
| `writing-readiness` | 2 | 7 |
| **Total** | **12** | **30** |

### Build & Tests
**Build**: PASS — `npm run typecheck` exit 0, zero diagnostics (no TS touched by this change; run for parity with this repo's own verify-report convention).
**Tests**: PASS — `824/824` (`.venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing tests.test_paper_decisions tests.test_paper_citation tests.test_paper_evidence tests.test_paper_figure tests.test_paper_lifecycle -q`), matching the orchestrator's own just-measured baseline exactly.

### CLI evidence (`.claude/skills/paper-writing/scripts/paper_cli.py`)
- `contract`: `ok`, 47 blocks, zero dangling edges — matches baseline.
- `order`: `ok`, 47 blocks in order — matches baseline.
- `phases`: `ok`, waves `[22, 7, 11, 2, 2, 1, 1, 1]` — matches baseline exactly.
- `readiness --paper paper`: `ok`, 47 blocks; 12 carry `blocked_on_produced`, identical block set AND identical `{fact, producers}` content to `phases`'s own 12, verified by full JSON comparison (not truncated) rather than the 320-char-truncation mistake the earlier orchestrator pass made once.

---

## The five findings — re-verified independently, not trusted from Unit 4's own report

### 1. CRITICAL — `PRODUCER_CHAIN_ABSENT` row-presence mechanism — **CLOSED**

Read `paper_graph._verify_producer_chain_rows` (new function, `paper_graph.py:506-558`), called from `assemble_corpus` right after `_verify_producer_reachability` (line 192). It walks every consumer's own section body's `### Internal chain` table (via `_internal_chain_rows`/`_chain_row_id`, the SAME parser `_verify_internal_chain` already uses) and refuses `PRODUCER_CHAIN_ABSENT` naming consumer/fact/producer when the `(consumer, producer)` pair is absent from the row set — independent of whether the producer is graph-reachable.

**Independent reproduction** (not the shipped test — a synthetic corpus built fresh in this session, two sections, a producer block and a consumer block joined by a REAL DIRECT `after` edge):
- Row present (`| c.only | p.only |`): `assemble_corpus` raises nothing.
- Row absent, same edge: `assemble_corpus` raises `PRODUCER_CHAIN_ABSENT: "c.only: requires 'limitations', produced by 'p.only', but no '### Internal chain' row in 'c' names 'p.only' as a dependency"`.

This reproduces the decisive case verbatim: a real `after` edge that would have satisfied `_verify_producer_reachability` alone, with the row absent, correctly refuses — the exact defect class the whole change exists to close.

**Mutation test** (`ProducerChainRowsTests.test_removing_the_check_flips_the_refusal_test_from_green_to_red`): ran directly — PASS. It uses `_run_against_mutant` (`tests/paper_mutation.py`), a real subprocess-based harness that copies `paper_graph.py` into an isolated temp tree, asserts the anchor line (`_verify_producer_chain_rows(corpus, declarations, section_bodies)`) matches exactly once, deletes it, and re-runs the decisive test against the mutant module (imported under a unique name, bypassing any stale `sys.path` entry) — confirmed `MUTANT_IMPORTED_OK` in output and nonzero exit, i.e. the decisive test genuinely goes red when the call site is removed. This is a real mutation proof, not a self-referential assertion.

Also re-ran `ProducerChainRowsTests` (5/5) and `tests.test_paper_contract`, `tests.test_paper_writing` in full (both inside the 824/824 total) — all green.

**Verdict: CLOSED.**

### 2. WARNING — `cmd_phases` dropping `blocked_on_produced` — **CLOSED**

Compared the full, untruncated JSON of `phases` and `readiness --paper paper` directly (parsed with `json.load`, not string-truncated). Both report `blocked_on_produced` for the identical 12 blocks: `abstract.slot-2`, `conclusions.concl-block-1`, `conclusions.concl-block-4`, `experimental-setup.es-assessment`, `introduction.block-2`, `introduction.block-3`, `related-work.rw-panorama`, `related-work.rw-preamble`, `related-work.rw-problem-blocks`, `related-work.rw-synthesis-artefact`, `results-and-discussion.rd-contribution-blocks`, `title-and-keywords.title` — and the `{fact, producers}` payload for each block is byte-identical between the two commands (confirmed programmatically, not read by eye). `paper_cli.cmd_phases`'s wave-block dict now includes `.get("blocked_on_produced", [])` (matching `declined_facts`/`stale_declines`'s own convention).

**Verdict: CLOSED.**

### 3. WARNING — `SKILL.md` stale/missing documentation — **CLOSED**

`SKILL.md` now carries a full "A fact is declared, or it is produced" section (lines ~225-253) documenting `produces_facts`'s rich shape, all six refusal codes (`FACT_SELF_REQUIRED`, `FACT_ROUTE_AMBIGUOUS`, `FACT_PRODUCER_ABSENT`, `FACT_PRODUCER_DUPLICATE`, `PRODUCER_CHAIN_ABSENT`, `PRODUCED_FACT_UNDECLARABLE`), and `blocked_on_produced`. The wave-count claim ("Over the shipped corpus (47 blocks) `phases` reports eight waves shaped 22 / 7 / 11 / 2 / 2 / 1 / 1 / 1") was re-measured live against `paper_cli.py phases` in this session and matches exactly.

**Verdict: CLOSED.**

### 4. WARNING — stale `limitations` producer citation — **CLOSED**

`specs/fact-production/spec.md`'s "Mutation — deleting the only producer is caught" scenario (line 115) and `tasks.md` 2.3/2.4 now both cite `limitations.lim-proposal-items`, matching the shipped corpus: `sections/04-limitations.md` shows `lim-proposal-items` (not `lim-closing`) carrying `produces_facts: [limitations]`, sourced from its own opening sentence "Sweep the mathematical section for gaps in the proposal:". `tasks.md` 4.6 documents the correction explicitly. No remaining reference to `lim-closing` as a producer anywhere in the change's own artifacts or the shipped corpus.

**Verdict: CLOSED.**

### 5. SUGGESTION — Decision F comment overclaiming — **CLOSED**

`design.md`'s Decision F section (lines 141-145) now states the implemented check verifies "structurally that SOME coupling-verification check exists for that fact id... not that the check names this exact competing PAIR of blocks," and explicitly notes it is "safe by construction today only because both `gap`'s producers and `check_gap`'s own pair derivation independently re-read the same corpus... but the code does not itself prove pair-identity." This matches the actual code (`paper_graph._verify_producer_duplication`: `len(producer_ids) == 2 and fact_id in paper_verify.CHECKS`) exactly — the docstring in `paper_graph.py:353-361` (`"corroboration is checked structurally, by asking the real, existing coupling roster"`) makes the identical, non-overclaiming statement.

**Verdict: CLOSED.**

---

## Side-effect adjudication — is the reachability/chain-rows overlap the right shape?

**Ruling: right shape, not dead weight — with one SUGGESTION to strengthen cross-referencing.**

Traced the actual pipeline order in `assemble_corpus` (lines 181-192): `_verify_internal_chain` (ROW → edge, refuses `CHAIN_ROW_UNBACKED` for any row not backed by a real DIRECT edge) runs at line 184, strictly before `_verify_producer_reachability` (line 191) and `_verify_producer_chain_rows` (line 192). This ordering means: by the time chain-rows executes, every surviving row is already guaranteed backed by a direct edge — so a passing chain-rows check (row present) always implies direct, hence trivial, reachability. Conversely, `_verify_producer_chain_rows` requires a DIRECT edge-backed row (stricter than mere transitive reachability, which `_verify_producer_reachability` alone accepts per Decision C). This means: for the specific case of a produced-fact dependency, chain-rows is strictly stronger than reachability — every input reachability would refuse, chain-rows would also refuse (no direct edge can exist without one for the row to be backed by), and every input chain-rows refuses, reachability might still accept (a transitively-reachable-but-undocumented producer). So `_verify_producer_reachability`'s own CRITICAL refusal is real (it still fires FIRST in the pipeline for a totally-unreachable producer, since it runs at line 191 before line 192) but for produced-fact dependencies specifically its refusal condition is now a strict subset of what chain-rows would also catch.

This is the right shape, not a guard-that-cannot-fire, for three reasons directly verified in the code and tests:
1. **The two checks protect different specs.** Reachability protects `fact-production`'s ordering guarantee (feeding the same graph `derive_order`/`derive_waves` consume); chain-rows protects `contract-input-partition`'s NEW, separate documentation requirement. Design.md's own Decision C (lines 75-79) explicitly frames chain-rows as "intentionally stricter... for the specific case of a produced-fact dependency" than reachability's general leniency — this is not an accident discovered after the fact, it is a stated design choice.
2. **Both checks remain independently, mutation-provably reachable-red.** `ProducerReachabilityTests.test_unreachable_refuses_at_the_reachability_layer_in_isolation` calls `_verify_producer_reachability` directly against a hand-built `Corpus` with zero `after` edges, bypassing `_verify_internal_chain`/chain-rows entirely, and its own mutation test (`test_removing_the_check_flips_the_refusal_test_from_green_to_red`, mutating the `_reaches(...)` condition, not the call site) — ran directly, PASS, confirmed `MUTANT_IMPORTED_OK` and nonzero exit. This is a genuinely different verification strategy from `ProducerChainRowsTests`'s own mutation test (which mutates the call site), and both remain live, not vacuous.
3. **The overlap is documented, not silent.** Unlike this repository's own recorded history of "a refusal that cannot fire reads as protection while protecting nothing," the overlap here is explicitly called out in three places: `_verify_producer_chain_rows`'s own docstring (`paper_graph.py:508-520`), `test_unreachable_refuses_at_the_reachability_layer_in_isolation`'s docstring, and `design.md` lines 75-79. A future reader hits the explanation at the first place they'd look.

**SUGGESTION (not blocking):** `design.md`'s Decision C/F sections document the STRICTNESS relationship but do not explicitly spell out that `_verify_producer_reachability`'s refusal is now unreachable-in-practice through the full pipeline for produced-fact dependencies specifically (only the isolated test's docstring and `tasks.md` 4.3 say so). A future architectural reader consulting only `design.md` would learn the two checks differ in strictness but not that one is pipeline-subsumed by the other today. Low priority — the reasoning is fully present in code/test comments, just not consolidated in the one file design decisions are supposed to live in.

## Fixture-edit audit — did the ~15 touched test classes get weaker?

Read the shared fixture helpers directly, not Unit 4's own characterization of them:
- `_produces_facts_body`'s new `chain_rows` parameter (`tests/test_paper_writing.py:1565`) defaults to empty and reproduces the old body byte-for-byte for every caller that never crosses two blocks — verified by reading the function body directly.
- `_write_coupling_sections`/`_coupling_internal_chain_rows` (lines 3608-3660), shared by `EvidenceTests`, `ReportShapeTests`, `CouplingOneTests`, `CouplingTwoTests`, `ArtefactsTests`, `FutureWorkTests`, `GapTests`, `OptionalVerifyTests` via `_build_coupling_paper`: rows are DERIVED programmatically from the fixture's own `requires_facts`/`produces_facts` declarations (one row per block requiring a fact `00-produced-facts.md`'s blocks produce, naming the exact producer), not hand-typed once and reused blindly — this is a strengthening of fixture realism, not a shortcut.
- `_write_optional_contribution_section` (line 5411): adds a real second producer section (`front-matter.contrib-source`) plus a direct `after` edge and matching row, rather than declaring `contributions` with no producer at all (which would now refuse `FACT_PRODUCER_ABSENT`) — this is the minimum real fix the new totality/reachability/row checks force, not a weakened assertion.

No fixture edit removes an assertion, widens a tolerance, or substitutes a mock for what was previously real corpus assembly. All three inspected fixtures use production code paths (`paper_scaffold.scaffold`, `paper_block.open_block`/`substitute`, real `assemble_corpus` calls) exactly as before.

**Verdict: no test class was weakened.**

---

## Regression check

No CRITICAL, WARNING, or new UNMET items surfaced. Full suite (824/824) matches the orchestrator's just-measured baseline exactly; `contract`/`order`/`phases`/`readiness` outputs match the baseline exactly (47 blocks, waves `[22, 7, 11, 2, 2, 1, 1, 1]`, 12 `blocked_on_produced` blocks). The prior pass's MET/MET-with-warning verdicts for `fact-production`, `paper-declarations`, `coupling-verification`, and `writing-readiness` are not contradicted by anything found in this session.

## Issues

**CRITICAL**: None.

**WARNING**: None.

**SUGGESTION**:
1. `design.md` documents the reachability/chain-rows strictness relationship (Decision C/F) but not the pipeline-subsumption consequence for produced-fact dependencies specifically — currently only in code/test docstrings and `tasks.md` 4.3. Low priority; would help a future architectural reader, not a functional gap.

## Final Verdict

**PASS.** All five prior findings (1 CRITICAL, 3 WARNING, 1 SUGGESTION) are genuinely closed, independently re-verified rather than trusted from Unit 4's own report. No regressions. The reachability/chain-rows overlap is the right shape, well-documented, and independently mutation-provable on both sides. Fixture edits strengthen rather than weaken test realism.
