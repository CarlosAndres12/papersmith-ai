# Design: The Writer May Assert Only What It Was Given

## Technical Approach

Five new stdlib-only modules beside the landed four in
`.claude/skills/paper-writing/scripts/`. The CLI is a **judge, never an invoker**: it
receives an agent's account (draft + binding map, audit verdicts, resolved samples) and
reconciles it against the artifact the agent produced. Both audits share one shape —
*the account is checked against the thing, never trusted about the thing* — which is why
`UNBOUND_SENTENCE`/`BINDING_ORPHANED` and `VERDICT_MISSING`/`VERDICT_BULLET_UNKNOWN` are
the same mechanism twice.

## Architecture Decisions

### D1 — Module layout, and how a new module cannot ship unclassified

| Option | Tradeoff | |
|---|---|---|
| Fewer, larger modules | Cheaper imports; `paper_style` holding both the tripwire and the proof is exactly the conflation the brief forbids | rejected |
| Anything under `_core/` | A test scans that tree wholesale into `proposal-implementation`'s roster | forbidden |
| **Five siblings in `scripts/`** | More files; each has one owner and one refusal family | **chosen** |

`paper_bindings.py`, `paper_audit.py`, `paper_write.py` (unit 1); `paper_style.py`,
`paper_leak.py` (unit 2). The sibling apply makes `reachable_paper_refusal_codes()` derive
its module list from `paper_cli.py`'s module-level imports — so **every new module is
imported at `paper_cli.py` module level unconditionally**, even those only `paper_write`
calls. A test asserts `{f.stem for f in scripts/*.py} == paper_cli`'s local module-level
imports ∪ `{paper_cli}`, closing the hole at its root instead of by memory.

### D2 — The suite cannot spawn an agent because nothing can

| Option | Tradeoff | |
|---|---|---|
| Adapter with a test-mode flag or env var | Discouragement. This repo already shipped one that ran a real `claude -p` per default run | rejected |
| Guard test counting subprocesses | Detects after the fact; a new call site precedes the guard | insufficient alone |
| **No agent-invoking code path exists** | The orchestrating agent shuttles transcripts; `write` cannot run unattended | **chosen** |

`write` takes `--draft <path>` and `--audit <path>` as JSON envelopes. No module under
`scripts/` imports `subprocess`, `os.system`, `os.popen`, `os.exec*` or `multiprocessing`;
an AST scan asserts it. Impossibility, not policy.

### D3 — `structural` is typed by a rule, not a blocklist

Four detections, all mechanical: a digit or closed-list number word; any `\cite*` command;
a comparative from a closed list declared in `paper_vocabulary`; and **a structural
sentence may name only what the contract prose names** — a non-sentence-initial
capitalised token, outside math and outside LaTeX commands, absent verbatim from the
block's contract prose, is a named external object. Rejected: proper-noun heuristics
(unfalsifiable) and deferring to the auditor (moves the attack surface into prose).

### D4 — `mode` widening on `section-contract`

`mode` joins `_TOP_LEVEL_OPTIONAL` and `_BLOCK_OPTIONAL` as
`{"value": "transposition"|"argument", "source": {"file", "quote"}}`; block value wins,
section value is the default. `paper_vocabulary.MODES` + `validate_mode` follow
`validate_citations`'s one-declaration pattern. `_validate_source` is **factored out of
`_validate_after_list`** so one validator serves both rather than two copies drifting.
Rejected: making `mode` top-level *required* — cleaner, but that is a Breaking change to a
closed required set, where the brief settled on a widening. Cost: a contract parses clean
and fails later; `write` refuses `MODE_ABSENT` (work-state) when neither level declares one.

### D5 — Equivalence without knowing any section's structure

The sampler agent proposes `{reference, locator, span}` per style-reference folder. The CLI
**verifies residency** — the returned span must be byte-present at that locator in the
ingested `.md` — then records it as `R`. An agent cannot invent a sample. No equivalent →
`noEquivalent` reported for that reference, which contributes nothing to `R`; all references
lacking one degrades to the empty style set, a valid value since unit 1. Rejected: a
hand-written per-reference block map (a human declaration per reference, and this skill
would then own a correspondence it cannot check) and name/ordinal matching (structure
knowledge in code).

### D6 — The proof and the tripwire cannot be confused

| | Proof | Tripwire |
|---|---|---|
| Claim | `overlap(S,R) ≤ max(overlap(A,R), overlap(B,R))`, self-calibrating | maximal contiguous run ≥ 8 normalised tokens |
| Runs | proof harness, over recorded A/B/S transcripts | every styled `write` |
| Refusal | none; reports both numbers | `STYLE_OVERLAP`, naming span and reference |

`paper_leak.relative_overlap_holds(styled, unstyled_a, unstyled_b, samples)` **takes no
threshold parameter**, and a test asserts its signature carries none. Tuning the tripwire
therefore cannot move the guarantee: to make the proof read `N`, someone must change a
signature a test reads. Normalisation (case-fold, collapse whitespace, strip LaTeX, exclude
math) lives once in `paper_style` so both read identically. Register distance sits beside
the proof and is computed only with `d(A,B)` present — the A/B control is a required
argument, not an optional one, so mutation 6 fails to construct.

### D7 — One re-draft is enforced, not instructed

`paper/.paper-writing/attempts/<block>.json` records each audited attempt keyed by a digest
of (contract bytes, evidence set, mode). A third submission under the same key refuses
`AUDIT_EXHAUSTED` naming what fired on attempt two. Changing an input starts a fresh budget
legitimately — the staleness shape `remote-execution`'s authorization tokens already use.
Rejected: counting inside one process (the CLI is called once per attempt, so the count
would always read one). **Settled upstream**: on the second failure, report the firing
disqualifiers and stop.

### D8 — `undecidable` reports, never blocks

Uncertainty about the *work* blocks; uncertainty about the *check* does not. Outcome is
decided solely by `any(fires)`. A `fires` verdict citing no span, or citing a span not
byte-present in the draft, downgrades to `undecidable` and is reported. It joins
`unmeasured`, `unprovenanced`, `unclassified`, `ambiguous`.

## Data Flow

    contract (verbatim) ─┐
    evidence set ────────┼─→ [agent: redactor] ─→ draft.json {latex, bindings}
    mode ────────────────┤                              │
    R (recorded samples) ┘                              ▼
                                          paper_bindings: segment → reconcile
                                          → resolve → type structural → mode
                                                        │
    contract ## Disqualifiers (verbatim) ─→ [agent: contract-auditor] ─→ audit.json
                                                        │
                              paper_audit: reconcile verdicts ↔ bullets, span residency
                                                        │
                              paper_leak.tripwire (styled only) ─→ paper_write ledger
                                                        │
                                          paper_block.substitute  ── or ──  refuse

Only `paper_style` reads a reference file, and only at record time for residency. Overlap
reads `R` alone (mutation 7).

## File Changes

| File | Action | Description |
|---|---|---|
| `scripts/paper_bindings.py` | Create | segmentation, reconciliation, resolution, structural typing, mode admissibility |
| `scripts/paper_audit.py` | Create | verbatim `## Disqualifiers` extraction, verdict reconciliation, span residency, outcome |
| `scripts/paper_write.py` | Create | pipeline order, attempt ledger, exhaustion |
| `scripts/paper_style.py` | Create | sample recording + residency, normalisation, `R` |
| `scripts/paper_leak.py` | Create | tripwire and proof, separated by signature |
| `scripts/paper_cli.py` | Modify | `write` verb; five module-level imports; new `REFUSAL_CLASSIFICATION` entries |
| `scripts/paper_contract.py` | Modify | `mode` into both closed sets; `_validate_source` factored out |
| `scripts/paper_vocabulary.py` | Modify | `MODES`, `COMPARATIVES`, `NUMBER_WORDS`, `validate_mode` |
| `sections/*.md` | Modify | `mode` transcribed per block; prose byte-unchanged |
| `.claude/agents/redactor.md`, `contract-auditor.md`, `style-sampler.md` | Create | agent contracts; no code invokes them |
| `.claude/skills/paper-writing/SKILL.md` | Modify | three channels, `write`, the two audits, the shuttle procedure |
| `tests/test_paper_writing.py` | Modify | red-first; count assertion `21` moves |

## Interfaces / Contracts

```python
# paper_leak.py — the guarantee cannot read the tripwire's number
def relative_overlap_holds(styled, unstyled_a, unstyled_b, samples) -> dict: ...
def tripwire_spans(styled, samples, *, min_tokens: int = 8) -> list[dict]: ...
```

Minimal evidence-record interface consumed from Phase 6 (fixtures only): `id`, `claim`,
`citation_key`, `span`, `locator`, `regime` ∈ `{discovery, resolution}`.

## What Breaks — Producers and Products

| Class | Site | Effect |
|---|---|---|
| Producer | `paper_contract._BLOCK_ALLOWED` / `_TOP_LEVEL_ALLOWED` | widened; a `mode` key without this refuses `MALFORMED_HEADER` |
| Producer | `paper_cli.REFUSAL_CLASSIFICATION` | ~16 new codes; roster test red until classified |
| Producer | `test_the_derivation_finds_the_measured_count` (21) | must move with the new codes |
| Producer | `_run_against_mutant` / `PAPER_BLOCK_SOURCE` | sibling widens it; new mutations name other modules |
| **Product** | `sections/*.md` front matter | **none exist** — Phase 2's header insertion has not run; nothing is invalidated |
| **Product** | `paper/main.tex` blocks already written | untouched. `substitute` is unchanged; a written block stays written and is simply unaudited |
| **Product** | `paper/.paper-writing/main.tex.prev` | untouched; `write` ends in the same `substitute` |
| **Product** | attempt ledgers, `R` records, guidance markers | **none exist** — all introduced here or by unlanded Phase 3 |

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | reconciliation, structural typing, mode admissibility, verdict downgrade, normalisation, tripwire, proof | fixtures; both poles per rule |
| Integration | `write` end to end, ledger exhaustion, `main.tex` byte-identity after refusal | recorded transcripts + fixture evidence sets |
| Structural | no-subprocess AST scan; module↔import completeness; `relative_overlap_holds` signature | source scans, not behaviour |
| Mutation | the seven from the proposal, in `paper_bindings`/`paper_audit`/`paper_write`/`paper_leak` | widened `_run_against_mutant`; exact anchor count **and** changed digest |

## Threat Matrix

| Boundary | Applicability | Design response | Planned RED test |
|---|---|---|---|
| Documentation-like paths | N/A — no file is classified as executable; `sections/*.md` and `main.tex` are read as bytes | — | — |
| Git repository selection | N/A — no git invocation; `resolve_sections_dir`/`resolve_paper_dir` already bound to `FORGE_ROOT` | — | — |
| Commit state | N/A — writes no index | — | — |
| Push state | N/A — no remote | — | — |
| PR commands | N/A — no PR automation | — | — |
| **Process integration (agent invocation)** | **Applicable** | No module under `scripts/` may import `subprocess`, `os.system`, `os.popen`, `os.exec*`, `multiprocessing`. Safe: transcript paths only. Failure: an import added anywhere fails the scan | AST scan over `scripts/*.py`, red on a planted `import subprocess` |
| **Path containment (`--draft`/`--audit`/`--transcript`)** | **Applicable** | Resolved through the existing `FORGE_ROOT` containment; outside → `PAPER_OUTSIDE_REPOSITORY` shape | one test per operand with an escaping path |

## Migration / Rollout

Two stacked work-unit commits, unit 2 revertible alone. No data migration: every product
shape this change judges is introduced by it. `sections/*.md` gains header lines only.

## Open Questions

- [ ] Proposal Q5 unanswered: should `write` require Phase 6 verdicts, or report the block
      `unvalidated`? Design assumes **report `unvalidated`** — consistent with D8, since a
      validator that has not run is uncertainty about the check.
- [ ] Whether `noEquivalent` on *every* style reference should warn louder than a report
      field, given a silently unstyled `S` still passes both measurements trivially.
