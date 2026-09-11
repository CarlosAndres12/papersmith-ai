# Proposal: The Writer May Assert Only What It Was Given

Phases 4 and 5 of the `paper-writing` build. Phase 1 (`only-the-block-changes`) landed.
Phase 2 (`the-contract-is-data-not-code`) is mid-apply — its reader is on disk, the ten
contracts do not yet carry headers. Phases 3 and 6 are interfaces, not code.

## Intent

Ten prose contracts sit under `sections/` and **nothing reads their `## Disqualifiers`
lists**, so every rule the operator wrote is decorative. There is no writer, and the first
writer built without a mechanism becomes a writer that asserts whatever it finds plausible.

Three channels reach the writer, each with one job and none able to do another's:

| Channel | Supplies | Source |
|---|---|---|
| **Contract** | structure: which blocks, in what order, what disqualifies | `sections/NN-*.md`, prose passed **verbatim, uninterpreted** |
| **Evidence** | what it is permitted to assert, each claim with its source | Phase 6's claim↔source pairs |
| **Style** | register, rhythm, how an equation is introduced, where a citation falls | the **equivalent block** of each style-registered reference |

The separation is the point. Style cannot leak content **because content does not arrive
through it**. This change makes that a measurement rather than a sentence.

## One change, two work units — decided

They share the writer's input contract, and that decides it. Land Phase 4 alone and the
writer's channel set is fixed at two; Phase 5 then reshapes the input contract of a verb
already shipped — the retrofit `no-claim-without-a-source-that-holds-it` refused for itself.
So: **one change**, with the channel set declared as *data* from unit 1 (style simply
empty), so unit 2 **adds a channel** rather than rewriting the contract.

Two sequential work-unit commits, stacked, each carrying its own proof:

| # | Work unit | Ends at |
|---|---|---|
| 1 | the writer and the contract auditor | a planted out-of-evidence claim never reaches `main.tex` |
| 2 | the style channel and its price | register moves, overlap does not |

## Scope

### In Scope

**Unit 1 — the writer and the auditor**

1. **`redactor` agent.** Inputs: the block's contract prose (verbatim), its evidence set,
   its mode, its style set (possibly empty). Output: LaTeX for **one** block **plus a
   binding map**. Prohibition: it asserts nothing outside the evidence set.
2. **The binding map is the mechanism** (see below), not the promise.
3. **`contract-auditor` agent.** Takes a drafted block and its contract's `## Disqualifiers`
   bullets, passed through with zero interpretation in code. Returns per bullet `fires` /
   `clear` / `undecidable`, and a `fires` verdict **must quote the offending draft span** —
   a verdict citing no span is `undecidable`, and `undecidable` fails exactly as `fires`
   does. This is what makes the contracts enforceable instead of decorative.
4. **`DISQUALIFIERS_ABSENT`.** A contract with no `## Disqualifiers` heading refuses. A
   silently un-audited block is how "enforceable" quietly becomes "decorative" again. All
   ten shipped contracts carry the heading today; a test holds that.
5. **`write` verb**: readiness → gate → draft → evidence-audit → contract-audit →
   `substitute --contract`. One bounded re-draft carrying the named findings, audited by the
   same auditor with the same inputs. Then `AUDIT_EXHAUSTED`, naming what fired, and **the
   block is not written**.
6. **Mode: transposition or argument.** Methods transposes maths that already exists; the
   introduction constructs an argument that did not. The contracts say so in prose
   (`01-materials-and-methods.md`: *"The proposal already exists. This section does not
   choose it, improve it, or argue for it"*; `06-introduction.md`: *"Six **argumentative
   functions**, in fixed order"*). The skill may not read prose, so the mode is
   **transcribed into Phase 2's header** as a closed field with the `source: {file, quote}`
   shape `after` edges already use.

**Unit 2 — the style channel**

7. **`style-sampler`.** Given the block about to be written, resolve the **equivalent block**
   in each reference the Phase 3 registry classes `style-reference`, and pass that block
   whole. Not extracted samples — register lives in whole sentences. It **records exactly
   what it showed**; an unrecorded sample is unmeasurable and therefore inadmissible.
8. **The similarity check — the price of the verbatim channel.** A near-verbatim lifted
   sentence is not an unsupported claim, so no validator in Phases 1–6 catches it.
   `STYLE_OVERLAP` fires on any contiguous normalized n-gram shared with a recorded sample,
   naming the span and the reference. Normalization case-folds, collapses whitespace, strips
   LaTeX commands, and **excludes math environments** — shared notation would otherwise trip
   every methods block.

### Out of Scope

Search, ingestion, `refs.bib`, the citation validator (Phase 6). The declarations gate and
the guidance registry themselves (Phase 3 — consumed, not changed). Figures, LaTeX
rendering, the cross-obligation verifier (Phases 7–8). MCP connector configuration. This
change widens no Phase 2 vocabulary other than adding `mode`, and invents no `after` edge.

## The mechanism: how an unbound assertion is *detected*

An instruction is not a mechanism. The redactor emits, beside the LaTeX, a **binding map**:
every sentence of the draft → `evidence:<record-id>` | `fact:<fact-id>` | `structural`.

1. **The map is checked against the draft, never trusted.** Sentences are segmented from the
   emitted LaTeX by the CLI. A draft sentence absent from the map is `UNBOUND_SENTENCE`;
   a map entry matching no draft sentence is `BINDING_ORPHANED`. This is what makes the map
   non-optional — it cannot be quietly under-filled.
2. **Each binding must resolve.** An `evidence:` id absent from that block's evidence set is
   `EVIDENCE_ID_UNKNOWN`. A `fact:` id outside the block's `requires_facts` is
   `FACT_NOT_LICENSED`.
3. **`structural` is the escape hatch, therefore the attack surface, therefore typed.** A
   `structural` sentence carrying a numeral, a `\cite`, a comparative, or a named external
   object is `STRUCTURAL_CARRIES_CLAIM`. Classification cannot launder a claim.
4. **Mode constrains admissible binding kinds.** A `transposition` block admits `fact`,
   `structural`, and `resolution`-class evidence; `argument` additionally admits
   `discovery`-class evidence. Otherwise `MODE_VIOLATION`.

**The seam, named honestly.** This change detects an assertion *bound to nothing*. An
assertion bound to a real record that the record does not actually support is Phase 6's
validator (`holds` / `does-not-hold` / `insufficient`). Neither covers the other, and
neither pretends to.

## The measurement: how the style channel is proven not to leak

Draft the same block twice with no style channel (call them A and B) and once with it (S).
The sampler's recorded samples R are the reference text.

| Property | Measurement | Passes when |
|---|---|---|
| **Register changes** | distance over a computable register profile — sentence-length distribution and function-word frequencies | `d(S, {A,B})` exceeds `d(A, B)`, the unstyled baseline variation |
| **Overlap does not rise** | maximal contiguous normalized n-gram shared with R | `overlap(S, R)` stays at or below `max(overlap(A,R), overlap(B,R))`, the chance floor, and under the threshold |

The A/B control is load-bearing: two LLM drafts differ from sampling alone, so "S differs
from A" measures nothing without it.

## Capabilities

### New Capabilities

- `evidence-bound-drafting`: the redactor's input contract, the binding map, the four
  detections above, mode-admissible bindings.
- `contract-audit`: verbatim disqualifier extraction, per-bullet verdict with quoted span,
  `undecidable` as failure, `DISQUALIFIERS_ABSENT`.
- `writing-orchestration`: the `write` verb, its pipeline, the bounded re-draft, exhaustion
  leaving the block unwritten.
- `style-channel`: equivalent-block resolution, whole-block passing, the recorded sample set.
- `style-leak-detection`: the overlap check and the two-measurement proof.

### Modified Capabilities

- `section-contract`: a closed `mode` field (`transposition` | `argument`), transcribed with
  `source: {file, quote}`, refusing `UNKNOWN_MODE` outside the pair. `paper_contract`'s
  `_BLOCK_ALLOWED` / `_TOP_LEVEL_ALLOWED` are closed sets, so this must be an explicit
  widening — a `mode` key added without it refuses `MALFORMED_HEADER`.

## Approach

Fail-closed stdlib CLI in `proposal-implementation`'s shape, three agents as contracts.
`paper_vocabulary.validate_citations`'s one-declaration pattern extends to `validate_mode`.
Agents are **never invoked by the suite**: this repository has already shipped a suite that
spawned live `claude -p` processes per default run. Every proof here runs the CLI against
recorded agent transcripts and fixture evidence sets.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/paper-writing/scripts/` | New | `paper_bindings.py`, `paper_audit.py`, `paper_style.py`, `paper_write.py` |
| `.claude/skills/paper-writing/scripts/paper_cli.py` | Modified | `write` verb; new codes in `REFUSAL_CLASSIFICATION` |
| `.claude/skills/paper-writing/scripts/paper_contract.py` | Modified | `mode` admitted into the closed key sets |
| `.claude/skills/paper-writing/scripts/paper_vocabulary.py` | Modified | `validate_mode`, derived from one declaration |
| `sections/*.md` | Modified | `mode` transcribed per block, prose byte-unchanged |
| `.claude/agents/redactor.md`, `contract-auditor.md`, `style-sampler.md` | New | three agent contracts |
| `.claude/skills/paper-writing/SKILL.md` | Modified | the three channels, `write`, the two audits |
| `tests/` | New | red-first; every proof below executed |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Phases 3 and 6 are unlanded interfaces | High | Consume a **minimal evidence-record interface** (`id`, claim text, citation key, span, locator, regime class) and drive every test from fixtures. Land after Phase 6 |
| The suite spawns live agents | Medium | Recorded transcripts only; a test asserting no subprocess reaches an agent binary. This has happened here before |
| `structural` launders claims | High | Typed and bounded (detection 3); a mutation removing the type check must go red |
| n-gram threshold false-positives on shared technical vocabulary | Medium | Math excluded; the threshold is calibrated against A/B, whose overlap with R is the chance floor, and reported — never hidden |
| Register distance is noise | High | The A/B control pair. Without it the measurement is unfalsifiable and must not ship |
| `mode` conflated with `citations` | Medium | `citations` says where a citation comes from; `mode` says whether a claim may be constructed at all. A test exercises a block with each of the four combinations |
| Two units against 1400 lines | High | Two stacked work-unit commits; unit 2 adds a channel to a data-declared channel set |

## Proof Discipline — mutations executed, never asserted

| # | Mutation | Goes red because |
|---|---|---|
| 1 | Drop the draft-vs-map sentence reconciliation | `UNBOUND_SENTENCE` can never fire; the map becomes a promise |
| 2 | Let `undecidable` pass the contract audit | Unfalsifiable audits become passes |
| 3 | Let `write` call `substitute` on an exhausted audit | A failed block reaches `main.tex` |
| 4 | Hardcode any one disqualifier bullet in skill code | The verbatim-pass-through invariant |
| 5 | Treat an absent `## Disqualifiers` heading as zero disqualifiers | Silent non-enforcement |
| 6 | Compare S against A alone, dropping the A/B control | The register measurement stops measuring |
| 7 | Let `STYLE_OVERLAP` read the reference file instead of the recorded samples | Measuring something the writer never saw |

Each harness purges `__pycache__` before re-running and asserts both an exact anchor count
**and** a changed file digest — a matched anchor is not a mutation that ran. Both traps are
recorded from this repository.

## Rollback Plan

`git revert` the work-unit commits; unit 2 reverts independently of unit 1. The `mode` field
reverts with `sections/`, where only the header lines change. `main.tex` is untracked, so no
tracked data unwinds; a block already written stays written and is simply unaudited again.

## Dependencies

- **Phase 2 landed** — the header, the ten facts, the six declarations, per-block readiness,
  the derived order, and the closed key sets `mode` must be admitted into.
- **Phase 3** — the `style-reference` guidance class the sampler resolves against, the
  declarations gate `write` calls, and `substitute --contract`.
- **Phase 6** — the evidence-set record with its verbatim span. Consumed as an interface.
- Phase 1's `substitute`, landed.

## Success Criteria

- [ ] A planted claim outside the evidence set is refused by execution and `main.tex` is
      byte-identical afterwards — absence proven, not flagged.
- [ ] A draft sentence missing from the binding map refuses `UNBOUND_SENTENCE`.
- [ ] A `structural` sentence carrying a numeral refuses `STRUCTURAL_CARRIES_CLAIM`.
- [ ] A disqualifier that genuinely fires is reported **with the quoted draft span**; one
      that does not fire reports `clear` in the same run — both poles, one run.
- [ ] A contract stripped of `## Disqualifiers` refuses `DISQUALIFIERS_ABSENT`; all ten
      shipped contracts carry it.
- [ ] Two audits fail, and the block is absent from `main.tex` with `AUDIT_EXHAUSTED` naming
      what fired.
- [ ] A `transposition` block binding a `discovery` claim refuses `MODE_VIOLATION`; the same
      binding in an `argument` block passes.
- [ ] `d(S,{A,B}) > d(A,B)` on the register profile, reported with both numbers.
- [ ] `overlap(S,R) ≤ max(overlap(A,R), overlap(B,R))` and under threshold, both reported.
- [ ] A planted near-verbatim lifted sentence refuses `STYLE_OVERLAP` naming span and source.
- [ ] Renaming a section id in `sections/` moves the whole pipeline with zero code changed.
- [ ] Every new `Refused` is classified in `paper_cli.REFUSAL_CLASSIFICATION`; the derived
      roster test fails on an unclassified code.
- [ ] No test invokes a live agent; a guard asserts it.

## Proposal question round

This phase could not ask interactively. These need the operator's answer before `sdd-spec`;
each is stated with the assumption the proposal currently carries.

1. **The n-gram threshold.** The proposal leaves N unset and calibrates against the A/B
   chance floor. Do you want a fixed N (8 was considered), or is calibrate-and-report right?
2. **`mode` granularity.** Assumed **per block**, defaulting to the section's value. Some
   sections may mix — is per-block right, or is per-section enough?
3. **The bounded retry.** Assumed **one** re-draft, then refuse. Is one right, or should it
   match Phase 6's three rounds?
4. **`undecidable` as failure.** Assumed to fail exactly as `fires` does, mirroring Phase 6's
   `insufficient`. This will refuse blocks a human would have passed. Accepted?
5. **The seam.** This change detects *unbound* assertion; Phase 6 detects *unsupported*
   binding. Nothing detects an assertion bound to a record that exists but was never
   validated, if Phase 6 has not run. Should `write` require Phase 6's verdicts, or report
   the block as unvalidated?

## Citations checked

Read from disk in this phase, cited by symbol and quoted text, never by line number:
`paper_cli.REFUSAL_CLASSIFICATION`; `paper_contract._TOP_LEVEL_ALLOWED`,
`_BLOCK_ALLOWED`, `_validate_after_list`'s `source: {file, quote}` shape;
`paper_vocabulary.validate_citations`; `## Disqualifiers` present in all ten `sections/*.md`
(measured, not assumed); the two mode sentences quoted above from
`01-materials-and-methods.md` and `06-introduction.md`. `sections/*.md` carry no front matter
yet — Phase 2's reader is on disk, its header insertion is not.

---

**Budget note**: this artifact exceeds the 450-word proposal budget. The overage is the
mechanism section, the measurement table, and the mutation table — the three things the
brief asked to be named rather than promised. This repository has shipped guards that could
not go red and measurements with no control; both are cheaper to prevent here.
