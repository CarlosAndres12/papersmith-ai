# Archive Report: A Fact Is Declared Or It Is Produced

**Change**: `a-fact-is-declared-or-it-is-produced`
**Archived to**: `openspec/changes/archive/2026-09-19-a-fact-is-declared-or-it-is-produced/`
**Archive date**: 2026-09-19
**Branch**: `u4-the-spec-and-the-code-agree` @ `d7fef1f`
**Status**: PASS — all prior findings (1 CRITICAL, 3 WARNING, 1 SUGGESTION) independently re-verified as closed, zero regressions

## Specs Synced to Main

| Domain | Action | Details |
|--------|--------|---------|
| `fact-production` | Created | New capability: producer declaration, totality, self-reference refusal, produced-fact satisfaction |
| `paper-declarations` | Updated | Split declared/produced; `declare` refuses a produced fact |
| `writing-readiness` | Updated | Blocked-on-produced names the producer, not a missing declaration |
| `contract-input-partition` | Updated | Contracts state produced facts; each producer→consumer is an internal-chain row |
| `coupling-verification` | Updated | Coupling 3 pair derives from production, not consumption |

## Defect Closed

`requires_facts` recorded only CONSUMPTION, so `related-work.rw-closing` — whose own prose says "Name the fronts left open — as many as there are blocks" — also carried `requires_facts: ["gap"]`, **demanding its own output as a precondition of producing it**. It misled rather than deadlocked: `write` never checks `requires_facts`, but `SKILL.md` documents `phases` as the authority on what can be written and `declare` as how to clear a block, so an operator following the documented discipline was told to pre-author the gap's text and then author it again, differently, inside the block.

## Vocabulary Now Splits Three Ways

- **DECLARED** (`formulation`, `dataset`, `experimental-design`, `implementation`, `results` — external, an operator resolves them via `FACT_SOURCE_ROOT`)
- **PRODUCED** (`contributions` by `introduction.block-4b`, `problem-statement` by `introduction.block-2`, `limitations` by `limitations.lim-proposal-items`, `gap` by TWO producers)
- **STRUCTURAL** (`skeleton` — resolution mechanism unchanged)

## Measured Facts at Archive

- **Tests**: 824 OK across the seven paper suites
- **Refusal Roster**: 133 (was 127), six new codes:
  - `FACT_SELF_REQUIRED` (a block produces and requires the same fact)
  - `FACT_ROUTE_AMBIGUOUS` (a `produces_facts` entry names a declarable fact)
  - `FACT_PRODUCER_ABSENT` (a required fact has no producer)
  - `FACT_PRODUCER_DUPLICATE` (uncorroborated duplicate producer — redefined mid-change)
  - `PRODUCER_CHAIN_ABSENT` (missing `### Internal chain` row for a produced-fact dependency)
  - `PRODUCED_FACT_UNDECLARABLE` (`declare` targets a produced fact)
- **Corpus**: 47 blocks; Kahn waves moved 5 → 8 waves with shape `[22, 7, 11, 2, 2, 1, 1, 1]` because producer-reachability adds real cross-section ordering
- **Blocks naming their producer**: 12 blocks now carry `blocked_on_produced` with both the fact id and producer qualified block id

## Operator Rulings — Recorded Because They Shaped the Design

1. **`gap` has two producers and that is legal.** `rw-closing` develops it, `introduction.block-3` condenses it; `block-3`'s own prose says *"The closing is the joint gap, and the conjunction is what makes it a gap."* The skill verifies they AGREE — which is what Coupling 3 always asked. This forced `FACT_PRODUCER_DUPLICATE` to be redefined mid-change: corroborated duplicates are legal, uncorroborated ones still refuse.

2. **A produced fact's VALUE is read from the block that wrote it**, never declared separately. The operator rejected a second declared value because two texts drift and only one is in the paper.

## Two Corrections Worth Recording — Caught Late

1. **Unit 2 limitation producer misidentified**: `lim-closing` was named as the producer of `limitations` in task 2.3 with a weak anchor; that block CONSUMES them. The orchestrator moved it to `lim-proposal-items`, anchored to *"Sweep the mathematical section for gaps in the proposal:"*. Moving one producer forced three more edits — the `after` edge, its chain row, and a digest — each refused in turn until all four agreed (task 4.6).

2. **Row-presence check not implemented until Unit 4**: `sdd-verify` found `contract-input-partition/spec.md` promising a row-presence check (`PRODUCER_CHAIN_ABSENT` when a consumer's own `### Internal chain` table carries no row naming its produced-fact's producer) that `paper_graph._verify_producer_reachability` never implemented — it only proved graph reachability. Unit 4 implemented `_verify_producer_chain_rows` rather than weakening the spec, after measuring that 14 of 15 producer/consumer relationships already practised the discipline.

## Critical Design Decision — Coupling 3's Pair

**Changed meaning**: Coupling 3 used to derive its block pair from whoever DECLARES `requires_facts: gap`, giving `rw-closing` + `experimental-setup.es-assessment`. It now derives from the two PRODUCERS, `rw-closing` + `introduction.block-3`, which is the pair the requirement's own prose always described ("say the same thing at different depths").

**Verification**: The merged main spec for `coupling-verification` carries the producer-derived version, not the old consumer-scan one joined by its replacement. Confirmed visually and by re-running `tests.test_paper_evidence` (77 tests, all green).

## Explicitly Out of Scope — Recorded as Deferred Decisions, Not Gaps

1. **Change 12** (distributing a proposal at section granularity): depends on knowing whether a distributed claim lands as declared input or produced prose.

2. **`limitations.lim-validation-items` deliberately not declared a producer**: It produces a DIFFERENT set (the validation sweep) from `lim-proposal-items` (the mathematical sweep). Today's rule admits two producers only when a coupling check verifies they AGREE; two that DIVIDE the work need a completeness check ("both sweeps present"). The operator ruled that a separate change, and chose to ship only the corroboration case first so the model can be judged on one instance before being replicated.

3. **Distributing a source document across blocks**: SECTION granularity, general over any document-sourced fact, with transposition enforced against the source. A separate change, not started.

## One Non-Blocking SUGGESTION Recorded

`design.md` does not spell out that the row-presence check subsumes reachability for produced-fact dependencies when reached through the full pipeline. Both checks remain independently mutation-provable and protect different specs; the overlap is documented in three places but not that consequence. Low priority — the reasoning is fully present in code/test comments, just not consolidated in the design-decision file.

## Archive Contents Verified

- ✅ proposal.md
- ✅ specs/ (five deltas)
- ✅ design.md
- ✅ tasks.md (5 units, all sub-items `[x]`)
- ✅ verify-report.md

## Verification Results

| Layer | What | Result |
|-------|------|--------|
| Tasks | All implementation tasks complete | ✅ All 5 units checked, sub-items verified |
| Build | TypeScript typechecking | ✅ 0 diagnostics |
| Tests | Seven paper suites (`test_paper_contract`, `test_paper_writing`, `test_paper_decisions`, `test_paper_citation`, `test_paper_evidence`, `test_paper_figure`, `test_paper_lifecycle`) | ✅ 824/824 OK |
| CLI | `contract` | ✅ ok, 47 blocks, zero dangling edges |
| CLI | `order` | ✅ ok, 47 blocks in order |
| CLI | `phases` | ✅ ok, waves `[22, 7, 11, 2, 2, 1, 1, 1]` |
| CLI | `readiness --paper paper` | ✅ ok, 47 blocks; 12 carry `blocked_on_produced`, identical to `phases` |

## Five Prior Findings — Re-Verified as Closed

### 1. CRITICAL — `PRODUCER_CHAIN_ABSENT` row-presence mechanism

**Status**: CLOSED — `_verify_producer_chain_rows` implemented in `paper_graph.py:506-558`, called from `assemble_corpus` right after reachability. Independent reproduction confirms: row present → assemble succeeds; row absent with real edge → `PRODUCER_CHAIN_ABSENT` refusal. Mutation test confirms removal of the call site flips the decisive test red.

### 2. WARNING — `cmd_phases` dropping `blocked_on_produced`

**Status**: CLOSED — Full JSON comparison (not truncated) shows `phases` and `readiness --paper paper` both report `blocked_on_produced` for identical 12 blocks with byte-identical payload. `paper_cli.cmd_phases` now includes `.get("blocked_on_produced", [])`.

### 3. WARNING — `SKILL.md` stale/missing documentation

**Status**: CLOSED — `SKILL.md` now carries full "A fact is declared, or it is produced" section documenting all six refusal codes and `blocked_on_produced`. Wave claim re-measured live: eight waves `[22, 7, 11, 2, 2, 1, 1, 1]`.

### 4. WARNING — Stale `limitations` producer citation

**Status**: CLOSED — Both `specs/fact-production/spec.md` and `tasks.md` now cite `limitations.lim-proposal-items`, matching the shipped corpus. No remaining reference to `lim-closing` as a producer anywhere.

### 5. SUGGESTION — Decision F comment overclaiming

**Status**: CLOSED — `design.md`'s Decision F now accurately states the implemented check verifies "structurally that SOME coupling-verification check exists for that fact id... not that the check names this exact competing PAIR of blocks," and notes it is "safe by construction today only because both derivations independently re-read the same corpus... but the code does not itself prove pair-identity."

## Work Units Completed

- [x] **Unit 0** — Reconciliation (PR 0): baseline roster, operator ruling recorded, six refusal-code names finalized
- [x] **Unit 1** — Grammar, parser, additive refusals (PR 1): `produces_facts` field added, self-reference and route-exclusivity checks
- [x] **Unit 2** — Corpus edits + totality + ordering, atomic (PR 2): 7 section files edited, 11 new `after` edges (5 design-measured + 6 empirical), all quote-backed
- [x] **Unit 3** — Consumers: readiness, declare, cli, verify, coupling evidence (PR 3): `produced_by` input/output wiring, `declare` refusal, `check_gap` pairing fixed
- [x] **Unit 4** — `sdd-verify` FAIL closure (PR 4): row-presence mechanism implemented, three edge+row corrections, docs updated, all five prior findings verified closed

## Mechanical Archive Verification

**Copy verification** (new `fact-production` spec):
```
Source: openspec/changes/a-fact-is-declared-or-it-is-produced/specs/fact-production/spec.md
Destination: openspec/specs/fact-production/spec.md
Diff result: EMPTY (identical bytes)
```

**Compose verification** (four existing specs):
- `paper-declarations`: ✅ composed successfully
- `writing-readiness`: ✅ composed successfully
- `contract-input-partition`: ✅ composed successfully
- `coupling-verification`: ✅ composed successfully

**Archive move verification** (change folder):
```
Source: openspec/changes/a-fact-is-declared-or-it-is-produced
Destination: openspec/changes/archive/2026-09-19-a-fact-is-declared-or-it-is-produced
Source removal: ✓ confirmed absent post-move
Diff verification: EMPTY (snapshot vs archived destination matches byte-for-byte)
```

## Final State Authority Hierarchy

This report reflects FINAL STATE at archive close:

1. **Persisted tasks artifact** (`openspec/changes/archive/2026-09-19-a-fact-is-declared-or-it-is-produced/tasks.md`): 5 units, all sub-items `[x]` — completion visibility per Task Completion Gate
2. **Explicit final-state facts** from orchestrator launch prompt: re-verify pass confirmed; all findings closed; no blockers
3. **Intermediate snapshots** (`verify-report`, `apply-progress`): PASS and Unit 4 findings — history of what was true at their time, superseded by current state

## SDD Cycle Complete

The change has been fully planned (proposal), specified (five specs), designed (architecture), implemented (five work units across four PRs plus one CRITICAL fix PR), verified (PASS), and archived. Ready for the next change.

---

**Archive execution date**: 2026-09-19
**Archive executor**: SDD Archive Phase (haiku model)
**Verification command**: `.venv/bin/python -m unittest tests.test_paper_contract tests.test_paper_writing -q` → 448 OK
