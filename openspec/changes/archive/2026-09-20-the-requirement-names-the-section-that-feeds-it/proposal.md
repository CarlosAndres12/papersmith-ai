# Proposal: The Requirement Names the Section That Feeds It

## Intent

Every `requires_facts` entry carries `{value, source:{file, quote}}`, and in
all ten shipped contracts `source.file` is **the contract file itself**. The
lock proves "this block's own prose asks for this fact." It has never proved,
and cannot prove, **which part of the real source document backs it**.

Measured, on the live corpus (`sections/01-materials-and-methods.md:44-66`):
`mm-borrowed-machinery` and `mm-proposal` carry **byte-identical** requirement
entries — same fact (`formulation`), same file, same quote
(`"The mathematical formulation of the proposal"`). One block is contracted to
transpose the machinery this work borrows; the other, the delta this work
proposes. Nothing in the header, and nothing any verb can check, distinguishes
what feeds one from what feeds the other.

`FACT_SOURCE_ROOT` (`paper_declarations.py:641-647`) is the only link to a real
document root, and it names five **directory names**, used exactly once, to
check a root is non-empty. It never names a file, a section, or a span.

## Scope

### In Scope

- **Piece 1 — section-granular sourcing.** A requirement entry for a
  document-rooted fact gains a second, distinct half: the source **document**
  and the **section of it** that feeds this block.
- **Piece 2 — named, never numbered.** The binding stores the heading's own
  **title text**. Never an ordinal, never a byte offset: both silently re-point
  when a preceding section is inserted. Offsets are computed at read time by
  `paper_guidance.segment_markdown`, already shipped and already correct about
  the appendix it must not swallow — never persisted.
- Resolving a lineage to its current revision on disk, off an on-disk
  declaration rather than a pattern literal (ruling below).
- Four refusal codes, SUBJECT_PREDICATE per the measured 133-code roster
  (12 qualifier-led exceptions, all membership checks — this is not one).
- Transcribe the real bindings into the shipped corpus; an entry that cannot be
  anchored is REPORTED for the owner's ruling, never deleted and never invented.

### Out of Scope

- **Piece 3, the separation loop** — dividing one document's sections across
  blocks so each is fed exactly once. Deferred on a **dependency**, not size: a
  block must be able to name a section before there is anything to divide.
- **Piece 4, transposition enforcement** — proving a `transposition`-mode block
  asserted only what its bound section carries.
- **The in-place digest.** Sealing a bound section's `sha256` to catch a
  same-name rewrite, deferred by the owner's ruling with its reason recorded
  below.
- Widening `FACT_SOURCE_ROOT`'s roots, `after`, `mode`, or `produces_facts`.
- Any change to the seven `requires_facts` consumers; none reads a source.

## Capabilities

### New Capabilities

- `source-section-binding`: the document/section half of a requirement entry,
  which facts must carry one, the named-not-numbered rule, lineage resolution
  to the current revision, section existence and ambiguity, and the
  unmeasured-root report.

### Modified Capabilities

- `section-contract`: front-matter schema widens the requirement entry.
- `requirement-transcription`: the self-file quote keeps proving the contract
  asks; the new half proves what answers.
- `writing-orchestration`: `write` refuses an unresolved binding before any
  draft/audit byte is read.

## Approach

**Additive second half, derived obligation.** The existing
`{value, source:{file,quote}}` is untouched. An entry gains
`document: {lineage, section}` — the document's **lineage**, never a revision
file, and the section's own **title**. Which entries MUST carry one is
computed, never listed:

- A fact is bindable **iff** it resolves through the declarable route **and**
  appears in `FACT_SOURCE_ROOT`. The four PRODUCED facts (`contributions`,
  `problem-statement`, `gap`, `limitations`) and `skeleton` are excluded **by
  construction** — they are absent from `FACT_SOURCE_ROOT` precisely because
  they have no document, and `a-fact-is-declared-or-it-is-produced` already made
  the two routes disjoint and derived. No engine-side list of fact ids exists,
  and none may be added.
- The lineage resolves to its **current revision on disk**, under
  `FACT_SOURCE_ROOT[fact]`'s own root — so `formulation` cannot silently bind
  to an experiments document. The revision pattern is read from a declaration
  on disk, **never a literal**: the deliberation half of this forge already
  does exactly this — `artifact-naming.ts` builds its regex from
  `DOMAIN.artifact.revisionPattern`, and its own source comment warns "never a
  literal `r`". That engine is TypeScript and this CLI may not call it (no
  `subprocess`), so the resolution is reimplemented in Python off the same
  kind of on-disk declaration — never off a pattern copied into the engine.
- A lineage that resolves to no file under its root refuses
  `SOURCE_LINEAGE_UNRESOLVED`. A root absent or empty on a checkout is
  `unmeasured`, which is a report, not a refusal.

**Where each check fires.** Shape in `paper_contract.parse` (always,
`MALFORMED_HEADER`). Section existence in `assemble_corpus`, gating every
corpus-reading verb, **only where the root resolves**: a root absent or empty
on this checkout reports `unmeasured`, never a silent pass — `experiments/`
holds only `.gitkeep` here today. Section existence refuses at `write` too,
never only from a read-only verb.

**`write`, not only `plan`.** Unit 6 wired `PHASE_NOT_READY` to the read-only
`phases` verb alone and `write` walked past it for a whole change. Repeating
that here — reporting a missing section on a read-only verb while `write`
proceeds — would
ship a guard wired to nothing, the ninth instance this repository has measured.

**Generality.** The engine reads `sections/*.md` and the documents those
headers name, both of which are data. No block id, section title, document
filename, or subject word of this paper enters `.claude/skills/`; a grep for
them under `scripts/` is part of verification. This CLI invokes no agent: no
`subprocess` import joins `scripts/`, held by `NoSubprocessScanTests`.

## Following a revision — the owner's ruling

The first draft of this proposal sealed each binding with the bound section's
`sha256` and refused on an in-place rewrite. **The owner ruled against that
framing**, and the reason reframes the whole decision: an in-place rewrite of a
revision is an anomaly — theirs, and they said so — while the **normal** event
is that a new revision is published. `proposals/` holds `research-concept-r14`
through `r21` today; `r22` is what happens next, not a rewritten `r21`.

**A binding therefore names the lineage, and the skill resolves the current
revision from disk.** A version bump then costs nothing: `r22` lands, every
binding follows it, and nobody re-stamps anything. That is the flow that
actually recurs, and it must be free.

What must stop the work is the event that only a version bump can reveal: the
section that fed a block **no longer exists** in the new revision — renamed,
split into subsections, merged away. Then `SECTION_NOT_IN_SOURCE` refuses and
names the binding, and a person decides what it re-binds to. That is not
bureaucracy; it is the one moment the disappearance is visible at all.

**Deferred by name: the in-place digest.** Sealing each bound section's
`sha256` to catch a same-name rewrite is NOT in this change. It is deferred
because the owner rules that path an anomaly of their own making, and because
it buys nothing on the recurring path while charging a re-stamp for every
legitimate edit. This is recorded as a deferral with its reason, not as an
unasked question — if in-place rewrites turn out to recur, the digest is an
additive third field on a binding this change already ships.

## Worked example — one real block, one real document

`materials-and-methods.mm-borrowed-machinery` requires `formulation`.
`FACT_SOURCE_ROOT["formulation"] == "proposals"`. The document on disk is
`proposals/research-concept-r21.md`, whose ATX headings `segment_markdown`
returns include `1. Fundamentos de métodos de kernel`,
`3. Formulación MIL-CREDA y kernel de bolsas ponderado por relevancia`, and
`5. Normalización de los términos de adaptación`.

| Entry | Bound section |
|---|---|
| `mm-borrowed-machinery` → `formulation` | `1. Fundamentos de métodos de kernel` |
| `mm-proposal` → `formulation` | `3. Formulación MIL-CREDA y kernel de bolsas ponderado por relevancia` |

Two entries that are byte-identical today become two different bindings. The
refusals, each against this exact pair:

Neither binding names `r21`. Both name the lineage `research-concept`, and
the skill resolves `r21` because that is the current revision on this disk.
Publish `r22` whose section 3 keeps its title, and both bindings follow with
no edit anywhere. Publish an `r22` that splits section 3 into `3.1`/`3.2`, and
`mm-proposal` refuses by name.

| Condition | Refusal |
|---|---|
| Named title is no heading in the current revision | `SECTION_NOT_IN_SOURCE` |
| Title matches two headings | `SECTION_TITLE_AMBIGUOUS` |
| Bindable fact, no `document` half | `SECTION_BINDING_ABSENT` |
| Lineage resolves to no file under its root | `SOURCE_LINEAGE_UNRESOLVED` |

(Those ids are named here because this document is a record of **this paper's**
work. They may never become a literal in `.claude/skills/`.)

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `scripts/paper_contract.py` | Modified | Entry shape, `document` validator |
| `scripts/paper_graph.py` | Modified | Section resolution wired into `assemble_corpus`; unmeasured-root report |
| `scripts/paper_declarations.py` | Modified | Bindable-fact derivation off `FACT_SOURCE_ROOT`; lineage-to-revision resolution |
| `scripts/paper_guidance.py` | Read | `segment_markdown` reused over source roots; no change expected |
| `scripts/paper_write.py`, `paper_cli.py` | Modified | Existence refusal at `write`; four codes into the roster |
| `sections/01-*.md`, `sections/02-*.md` (repo root) | Modified | Bindings transcribed; prose bytes untouched |
| `tests/test_paper_writing.py`, `test_paper_contract.py`, `test_paper_decisions.py` | Modified | Raw-JSON-header fixtures; a synthetic `experiments/` fixture |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Obligation made unconditional mid-sequence reddens corpus + fixtures | High | Lands atomically in the last unit, after the owner's ruling on unanchorable entries |
| Refusal roster quoted stale | High | Measured **133** today (`REFUSAL_CLASSIFICATION`). Re-derive with `reachable_paper_refusal_codes()` after code lands — never forecast; it drifted stale four times here |
| `experiments/` is empty on this checkout | High | `experimental-design` binds `unmeasured`; generality over that root is proven by a synthetic fixture, and that limit is stated, not hidden |
| `implementation`/`results` roots are a repository, not a prose document, and `--implementation` has no default path | Med | **Open for `sdd-design`**: rule whether the derived bindable test excludes them, or whether they bind an unmeasured root |
| A section's prose changes under an unchanged title, same revision | Med | **Accepted, deferred by name** (ruling above): an in-place rewrite is an anomaly; the recurring path is a version bump, which is free |
| The revision pattern gets copied into the engine as a literal | High | It must be read from an on-disk declaration. The deliberation half already warns about this in its own source; a grep under `scripts/` is a verification step |
| Paper-specific literal leaks into the engine | Low | Happened once (`MM_DATASET_ID`, undone). Grep under `scripts/` is a verification step |
| Existence guard ships reported-but-unwired | Med | Proven by executed mutation at `write`, never by reading the roster |

## Review Workload Forecast

| Unit | Content | Est. lines |
|---|---|---|
| U1 | Entry shape, `document` validator, bindable-fact derivation — inert, both shapes accepted | ~120 |
| U2 | Lineage-to-revision resolution, section existence/ambiguity refusals, unmeasured-root report | ~150 |
| **DP** | **Owner rules on any entry that cannot be anchored** | **blocking** |
| U3 | Transcribe corpus bindings, obligation unconditional, existence refusal at `write`, fixtures, roster re-derived | ~170 |

Estimated total **~440 changed lines** against the **400-line** budget under
`ask-on-risk`. **400-line budget risk: Medium.** Two chained PRs recommended:
(U1+U2) ≈ 270, then (U3) ≈ 170 — each independently green, since U1 and U2 are
inert without U3. Dropping the digest removed machinery; adding the revision
resolver put a comparable amount back, so the total did not move.

## Rollback Plan

- U3 is one commit: `git revert` restores the pre-obligation corpus and fixtures
  together.
- U1 and U2 are inert without it — bindings accepted but not demanded. Reverting
  U3 alone leaves a green suite and an unchanged corpus.
- No on-disk state, region format, digest or generation counter changes; an
  existing `paper/main.tex` stays readable by the prior revision.

## Dependencies

- Archived `a-fact-is-declared-or-it-is-produced` — supplies the disjoint
  declarable/produced routes this change derives its exclusion from.
- Owner ruling at DP before U3 starts.
- Stdlib-only, keyless, offline, fail-closed. No `subprocess`.

## Success Criteria

- [ ] `mm-borrowed-machinery` and `mm-proposal` no longer carry identical
      requirement entries; each names a different section of the same document.
- [ ] Every bindable requirement in the shipped corpus carries a resolved
      binding, or is reported for the owner — none deleted, none invented.
- [ ] A header naming a section absent from the current revision refuses
      `SECTION_NOT_IN_SOURCE` at `write` — proven by executed mutation.
- [ ] Publishing a NEW revision whose bound section titles survive requires no
      edit to any binding — proven by a fixture that adds a revision and
      asserts the corpus still assembles untouched.
- [ ] No revision pattern literal appears under `scripts/`; the pattern is read
      from an on-disk declaration.
- [ ] Produced facts and `skeleton` are excluded with no fact-id list anywhere
      under `scripts/` — proven by a mutation adding a sixth root.
- [ ] `reachable_paper_refusal_codes()` derives bidirectionally; the roster count
      is measured after the code lands, never forecast.
- [ ] No block id, section title, document filename or subject word of this paper
      appears under `.claude/skills/`.
- [ ] Both suites green: `npm test` AND
      `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`.
