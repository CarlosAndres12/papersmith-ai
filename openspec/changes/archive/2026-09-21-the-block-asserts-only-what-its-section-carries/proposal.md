# Proposal: The Block Asserts Only What Its Section Carries

Change: `the-block-asserts-only-what-its-section-carries` · Subject:
`.claude/skills/paper-writing` · Store: hybrid · Baseline: `main` at `bf00e17`,
clean · Every `file:line` below re-read on disk 2026-09-21, not inherited from
the exploration.

## Intent

A block whose contract declares `mode: transposition` must carry its bound
source section into the paper's own style. `write` judges the returned draft
through five stages and **none of them asks whether what the draft asserts is
in the section at all.**

The one stage that opens the section is
`paper_leak.check_source_section_verbatim` (`paper_leak.py:215-273`). Re-read
today: it computes the longest shared normalized-token run and refuses when it
exceeds `max(source_section_floor(...), SOURCE_RUN_BACKSTOP)`. That is a
**copying** measurement, and its own capability says so
(`openspec/specs/transposition-fidelity/spec.md`, `## Purpose`).

The failure mode is not a suspicion, it is arithmetic. A faithful paraphrase
shares near-zero overlap by design. So does an invented claim. **The further a
draft drifts from the truth, the quieter the only check that reads the
section gets.** A draft that paraphrases freely and asserts something the
section never states clears all five stages and reaches `substitute`.

Newly possible now: `source_sections` is already resolved from disk into
`BlockContract` (`paper_write.py:51-59`, `paper_source_span.py:27-77`), and the
sibling change is about to hand the redactor those same bytes — so there is
finally a concrete thing to hold a draft to, and a drafter who saw it.

## Scope

### In Scope

| Deliverable | Where |
|---|---|
| Thread `_stage_evidence_audit`'s currently discarded return value through `write_block`; derive the subject set from it | `paper_write.py:121-129`, `:159` |
| A new sibling agent that judges support per sentence and returns an account, never a decision | `.claude/agents/section-grounding-auditor.md` |
| A new module that reconciles that account against re-derived bytes in both directions | `scripts/paper_grounding.py` |
| Three refusal codes, their import-registry row, their `REFUSAL_CLASSIFICATION` pins, and their SKILL.md roster rows | `paper_grounding.py`, `paper_cli.py:75-107`, `SKILL.md` |
| A `sourceGrounding` envelope key beside `sourceFidelity` | `paper_write.py:249-259` |
| Mutation proof of reachability for each new code | `tests/paper_mutation.py` |
| A pre-apply neutrality audit over `.claude/skills/` | gate, not a note |

### Out of Scope — with reasons

- **`evidence:`-bound sentences.** They are held by a separately shipped
  mechanism (`citation-validation`, `evidence-set`). Folding them in conflates
  two contracts that were deliberately built apart. Named here so nobody reads
  this change as closing them.
- **`structural` sentences.** `paper_bindings.type_structural` already refuses
  `STRUCTURAL_CARRIES_CLAIM` for a structural sentence that asserts anything.
  A structural sentence that survives that stage asserts nothing to ground.
- **Any `argument`-mode block.** Out the same way it is already out of
  `SOURCE_SECTION_VERBATIM` (`transposition-fidelity` spec,
  `Requirement: Only A Transposition-Mode Block Is Checked, Mode Derived From
  The Contract On Disk, Never Listed`).
- **A `fact:`-bound sentence whose fact has no measured document-rooted
  half.** `resolve_bound_sections` already skips a fact absent from
  `FACT_SOURCE_ROOT` or whose root reports `unmeasured`
  (`paper_source_span.py:52-57`). There are no bytes to compare against, and
  inventing a second, stricter gate here is the "fixed the instance, never
  swept the class" defect that module's own docstring cites.
- **Editing `check_source_section_verbatim` or `check_tripwire`.** See §2.
- **Widening `assemble_packet` or `RedactorInput`.** That is the sibling
  change's whole subject.
- **Any post-change refusal-roster count.** The literal the suite pins today
  reads **161** (`tests/test_paper_writing.py:7942`, read 2026-09-21). The
  post-change number is measured live at apply, never forecast here.

## Capabilities

### New Capabilities

- `transposition-grounding`: a `fact:`-bound sentence in a transposition block
  must be supported by the bound source section its fact names; an agent
  proposes the verdict, `write` re-derives both sides and reconciles against
  real bytes, and any verdict it cannot ground is downgraded rather than
  trusted.

### Modified Capabilities

None. `writing-orchestration`'s `Requirement: Pipeline Stage Order`
(`spec.md:13-17`) names six stages and already does **not** name the style
tripwire or the verbatim check, both of which shipped into the same
post-contract-audit band without modifying it. This stage follows that shipped
precedent rather than reopening the requirement.

## Approach

Exploration's Approach 1: a new sibling agent plus byte-level reconciliation,
shaped exactly like the already-shipped `contract-audit` mechanism
(`paper_audit.py:56-92`, `.claude/agents/contract-auditor.md`).

### 1. Nothing passes by authority — how reconciliation actually works

This is the load-bearing property of the change. An agent's verdict that the
code trusts is the "deciding instead of asking" failure this repository names
by name. The mechanism, concretely, in the order it runs:

**(a) `write` derives the subject set itself, from bytes.** It re-uses the
`list[Binding]` that `_stage_evidence_audit` (`paper_write.py:121-129`) already
produced from `paper_bindings.reconcile(draft["latex"], draft["bindings"])` —
which segments the emitted LaTeX independently of the redactor's account
(`paper_bindings.py:99-125`). A subject is any `Binding` with
`kind == "fact"` whose `ref` equals the `"fact"` key of some entry in
`contract.source_sections`. That join is real: `resolve_bound_sections` returns
`{"fact", "lineage", "title", "path", "byte_start", "byte_end", "text"}` per
entry (`paper_source_span.py:68-76`), and `Binding.ref` is the same fact id
(`paper_bindings.py:123`). **The scope is an intersection of two independently
derived sets. No block id, no section title, no list.**

**(b) The account.** The agent returns one entry per subject sentence:
`{"sentence", "fact", "verdict": "supported"|"unsupported"|"undecidable",
"span"}`, where `span` on a `supported` verdict is the excerpt of the **bound
section** that carries the sentence's claim.

**(c) Reconciliation, both directions.**

| Condition | Result |
|---|---|
| An account entry whose `sentence` is not in `write`'s own segmentation | refuse `GROUNDING_SENTENCE_UNKNOWN` |
| A subject sentence with no account entry | refuse `GROUNDING_VERDICT_MISSING` |
| `supported` with an empty `span`, or a `span` not byte-present in that fact's own `section["text"]` | **downgrade to `undecidable`**, span cleared |
| `supported` whose `span` is present, but in a section belonging to a different fact | **downgrade to `undecidable`** |
| `unsupported` | refuse `SECTION_UNSUPPORTED_CLAIM`, naming the block, the fact, the lineage, the section title, and the sentence |

The bytes compared against are the ones `resolve_bound_sections` sliced from
the resolved revision on disk — never a copy the agent returns.

**(d) The asymmetry is deliberate and inverts `contract-audit`'s.** There,
`fires` is the blocking verdict and therefore the one that must cite a span.
Here the **permissive** verdict is the dangerous one: `supported` is what lets
a sentence through, so `supported` is what must be grounded. An agent cannot
mint support by quoting text the section does not contain.

**(e) `undecidable` is reported, never blocking on its own.** This mirrors
`contract-audit`'s shipped `Requirement: Undecidable Is Reported, Not Blocking
On Its Own` (`paper_audit.py:95-101`), for the reason that requirement exists:
a mechanism that blocks on its own uncertainty trains the agent to guess, and a
guess is exactly what this change is built to refuse. The residual — a
blanket-`undecidable` account waving a whole block through — is **R1** below.
It is not papered over: every `undecidable` is counted and reported per
sentence in the envelope, so it is visible rather than silent. Whether a
ratio threshold belongs in this mechanism at all is **`sdd-design`'s to rule
on**; it does not own the right to inherit a blocking rule silently.

**(f) The envelope.** `source_grounding_report(subjects, measured)` mirrors
`source_fidelity_report`'s shipped shape (`paper_write.py:262-279`): no subject
sentence resolved → `{"status": "unmeasured"}`, never a silent pass inferred
from the absence of a refusal.

### 2. A sibling, never an extension — and why, verbatim

`check_source_section_verbatim`'s own docstring records the precedent and its
reason (`paper_leak.py:218-225`, re-read today): `style-leak-detection`'s
`Requirement: Overlap Reads Only The Recorded Sample Set` forbids
`STYLE_OVERLAP` comparing against a reference file read directly, so folding a
bound section's bytes into `check_tripwire`'s sample set **would break a
shipped requirement rather than merely overload a function.**

The grounding check must not extend `check_source_section_verbatim` either,
for a second and different reason: that function is a pure overlap measurement
over three strings and returns a floor/threshold report. Grounding takes an
agent account, reconciles it, and refuses on semantics. Merging them would put
a verdict-bearing input inside a function whose whole contract is that it
computes its answer from the bytes alone — and would make one refusal code
stand for two unrelated failures, which the roster derivation reads statically
and cannot separate.

So: a new module, new codes, lazily imported exactly as `paper_leak` already is
at `paper_write.py:203` and `:237`, keeping `paper_write.py` importable
without it.

### 3. Where it fires

In `write_block`, **after** `check_source_section_verbatim` and **before**
`paper_block.substitute`. Copying is decided before meaning, so a draft failing
both names `SOURCE_SECTION_VERBATIM` deterministically — the same ordering rule
that already puts `STYLE_OVERLAP` first. A guard wired only to a read-only verb
is wired to nothing; this repository has nine measured instances.

### 4. Roster cost, stated rather than discovered

A new refusal code touches five places, and this repository has already paid
for omitting the first one:

| Place | Why |
|---|---|
| `paper_cli.py:75-107` module-level import | The `# for the roster derivation` convention. Omit it and the code is **silently unreachable to the roster walk** — recorded here as having happened before |
| `paper_cli.REFUSAL_CLASSIFICATION` | `tests/test_paper_writing.py:7545,7553` refuse in both directions |
| `tests/test_paper_writing.py:7942` | The pinned count literal, re-measured live, never forecast |
| `SKILL.md` + `references/` | A demand must ship the way to answer it, and the refusal must name that way |
| `tests/paper_mutation.py` | Reachability **proven by mutation**, never asserted |

Three codes, so five places each.

### Worked example (invented names — not this paper)

Source `widget-study-r4.md`, section `2. Widget Calibration`, bound to block
`analysis.an-core` (`mode: transposition`), fact `calibration-regime`.

- **Refused.** The draft sentence "Calibration was repeated after every third
  trial." is bound `fact:calibration-regime`. The section states the constant is
  held across every trial and never mentions repetition. Agent returns
  `unsupported` → `SECTION_UNSUPPORTED_CLAIM`, naming block, fact, lineage,
  section title, and the sentence.
- **Passes.** "Calibration fixes that constant at the interval's midpoint,
  unchanged across trials." → `supported`, span quoted from the section, and
  `write` finds those bytes in the sliced section text.
- **Downgraded, not trusted.** Same sentence, `supported`, but the quoted span
  appears nowhere in the section's bytes → `undecidable`, span cleared,
  reported. The agent's word bought nothing.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `scripts/paper_grounding.py` | New | Subject derivation, both-direction reconciliation, the three refusals, the report shape |
| `scripts/paper_write.py` | Modified | `_stage_evidence_audit`'s return threaded; new stage; `sourceGrounding` in the envelope |
| `scripts/paper_cli.py` | Modified | Import registry row; `--grounding <path>` on `write`; `REFUSAL_CLASSIFICATION` pins |
| `.claude/agents/section-grounding-auditor.md` | New | `tools: Read, Glob, Grep`; `stretch: write`; never invoked by code |
| `SKILL.md`, `references/` | Modified | Roster rows and the next action each refusal names |
| `openspec/specs/transposition-grounding/` | New | The capability's spec |
| `scripts/paper_leak.py` | Read-only | Explicitly untouched (§2) |
| `tests/test_paper_writing.py`, `tests/paper_mutation.py` | Modified | Red-first locks; mutation proofs; roster re-measure |

## Risks

| # | Risk | Likelihood | Mitigation |
|---|---|---|---|
| R1 | A blanket-`undecidable` account waves a block through | High | Every `undecidable` counted and reported per sentence, never silent. The ratio-threshold question is handed to `sdd-design` explicitly, not decided by default |
| R2 | The agent's verdict is trusted somewhere the reconciliation does not reach | Med | The downgrade is over `section["text"]`, the bytes `resolve_bound_sections` sliced; a red-first lock plants a `supported` whose span is absent and asserts `undecidable` |
| R3 | No real `document` binding exists on disk (`transposition-fidelity/spec.md:28-34`) | High | Synthetic `bind`-recorded fixtures with invented names; the synthetic boundary is stated in verify, never implied away |
| R4 | Scope creep toward `evidence:`-bound sentences | Med | The subject set is an intersection derived in code; a lock asserts an `evidence:` binding is never a subject |
| R5 | The import-registry row is omitted and a refusal is unreachable to the roster walk | Med | Mutation proof per code, and the roster re-measured live after the code lands |
| R6 | A same-size mutation reuses stale bytecode and the mutant never runs | Med | The harness purges `__pycache__`; the mutation asserts its anchor count changed, never `git diff --stat` |
| R7 | A paper's own names leak into the forge | Med | Pre-apply neutrality audit is a gate; fixtures use invented names only |
| R8 | The sibling change lands second and this guard demands fidelity to bytes the drafter never saw | Med | Ordering is a stated dependency, not an assumption — see below |

## Dependencies

- **`the-redactor-receives-the-section-it-must-transpose` applies first.** It
  widens `assemble_packet` and `RedactorInput` so the redactor receives the
  bound section it must transpose. Without it this change demands fidelity to a
  text the drafter was never shown, which turns a fidelity guard into a
  guessing game. Its own exploration already scopes this change out by name
  (`the-redactor-receives-the-section-it-must-transpose/exploration.md:107-112`),
  and this proposal accepts that ordering rather than racing it.
- Archived `2026-09-20-the-tripwire-reaches-the-section-that-feeds-it`
  (`source_sections`, `paper_source_span.py`).
- Archived `2026-09-11-the-writer-may-assert-only-what-it-was-given`
  (`paper_bindings`, `paper_audit`, the reconciliation precedent).

## Review Workload Forecast

Owner accepted `size:exception` up front; engine-line ceiling for this change
is **1600** lines under `.claude/skills/`.

| # | Slice | Depends on | Lines (est.) |
|---|---|---|---|
| 1 | Thread the discarded bindings; derive the subject set; `unmeasured` envelope | — | ~200 |
| 2 | `paper_grounding.py`: reconciliation, three refusals, report shape | 1 | ~450 |
| 3 | Agent file, `--grounding` wiring, import row, classification, SKILL.md/`references/` | 2 | ~400 |
| 4 | Mutation proofs, neutrality audit, roster re-measure, both suites | 3 | ~350 |

```
Decision needed before apply: No
Chained PRs recommended: Yes
400-line budget risk: High
```

Against the accepted exception and the 1600-line ceiling the risk is Medium;
against the default 400 it is High, so the four slices ship chained.

## Rollback Plan

Purely additive. Each slice is one commit and reverts in reverse order
(4, 3, 2, 1). No on-disk state format, digest, marker grammar or envelope key
that a prior revision reads is changed — `sourceGrounding` is a **new** key
beside `sourceFidelity`, so an existing `paper/main.tex`, every recorded
binding, and every attempt ledger stay readable by the prior revision. Slice 1
alone is a discarded return value becoming a used one, with no behaviour
change. `paper_leak.py` is untouched, so the shipped verbatim check's measured
behaviour cannot move. Reverting slice 3 removes the three codes from the
import registry, `REFUSAL_CLASSIFICATION` and the roster together, in one
commit, so the count locks stay consistent. No file is deleted.

## Success Criteria

- [ ] A draft sentence bound `fact:` to a document-backed fact, asserting
      something its bound section does not carry, refuses
      `SECTION_UNSUPPORTED_CLAIM` at `write` — proven by an **executed
      mutation**, not a read-only verb.
- [ ] A faithful paraphrase of the same section passes, with the supporting
      span reported.
- [ ] A `supported` verdict whose quoted span is not byte-present in the
      section's own sliced text downgrades to `undecidable` — proven red-first
      by planting the absent span.
- [ ] An account entry naming a sentence `write` did not segment refuses
      `GROUNDING_SENTENCE_UNKNOWN`; a subject sentence with no entry refuses
      `GROUNDING_VERDICT_MISSING`. Both proven by mutation.
- [ ] An `evidence:`-bound sentence and an `argument`-mode block are never
      subjects — proven by a lock, not by absence of a failure.
- [ ] A block with no document-backed `fact:` subject reports `unmeasured`,
      never a silent pass.
- [ ] The subject set is derived from the intersection of re-segmented draft
      bindings and resolved `source_sections`; no block id, section title,
      document filename, lineage literal or paper id appears anywhere in
      `.claude/skills/` or its suite.
- [ ] `_stage_evidence_audit` is called exactly once per `write`; nothing
      segments the draft a second time.
- [ ] Each new code appears in the `paper_cli.py` import registry, in
      `REFUSAL_CLASSIFICATION`, and in the SKILL.md roster, and the pinned
      count is **re-measured live** after the code lands, never forecast.
- [ ] Both suites green: `npm test` and
      `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`.
