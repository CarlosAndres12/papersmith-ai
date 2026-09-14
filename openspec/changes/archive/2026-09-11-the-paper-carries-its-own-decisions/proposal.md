# Proposal: The Paper Carries Its Own Decisions

Phase 3 of the `paper-writing` build. Phase 1 (`only-the-block-changes`) has landed;
Phase 2 (`the-contract-is-data-not-code`) is applying in parallel and is treated here as
an interface, not as code on disk.

## Intent

A decision made in session N is re-asked in session N+1 because nothing wrote it down.
Three classes of decision are homeless: which `guidance/` folder is read for style and
which for evidence; what has been decided and approved; and which contract each written
block actually stood on. `main.tex` must become self-describing, so a later session
resumes by **reading** rather than re-asking.

## Scope

### In Scope

| # | Deliverable |
|---|---|
| 1 | Per-folder class declaration under `guidance/`, closed vocabulary, `unclassified` reported |
| 2 | A `%% paper-writing declarations` region in `main.tex` — self-digesting, invisible to Phase 1 |
| 3 | Progressive collection at each section gate; fixed entries immutable; explicit `--reopen` |
| 4 | A `%% paper-writing provenance` region: contract sha256 + declaration generation per written block |
| 5 | `insumos-observer` agent — reads four sources, reports fact satisfaction, decides nothing |
| 6 | `plan` and `declare` registered into the existing `paper_cli.py` |

### Out of Scope

Redactor, style sampler, citations, MCP wiring, figures, cross-obligation verifier
(Phases 4–8). This change **never rewrites a drifted block** — it names it. It also never
widens either of Phase 2's closed vocabularies.

## Capabilities

### New Capabilities
- `guidance-registry`: classifying `guidance/` folders as style-reference or evidence
- `paper-declarations`: two record kinds, collection, approval, fixing, immutability, reopening
- `contract-provenance`: what each written block stood on, and drift reporting

### Modified Capabilities
- `block-substitution`: `substitute` gains an optional `--contract <path>`. Provenance is
  recorded **at write time**; it cannot be reconstructed afterwards, so the parameter is
  added now, not deferred. Phase 1 left the CLI surface extensible for exactly this.

## Approach

**The gate does two different things, and they are not the same record.** It *collects
declarations* — operator inputs the paper cannot derive — and it *records fact
resolutions*: what a fact actually says once it is settled. Both are "what was decided"
and both live in the declarations region as two record kinds, and neither widens the
other's vocabulary. The brief's emergent "declarations" (contributions, problem-statement)
are Phase 2 **facts** — `contributions` is fact 2 of ten — not declarations. Phase 2's
declaration vocabulary is closed to six operator inputs that derive from no fact
(`author-roles`, `grant-title`, `grant-code`, `repository-url`, `keyword-bounds`,
`classification-line`), and it stays closed. Collapsing the two kinds would have opened it
silently.

**One drift ledger, two inputs.** A written block records the contract hash and the
declaration generation it stood on. Any later change to either is *reported*, never
repaired. Reopening a declaration and editing a contract become one mechanism.

**Reopening is derived, never blunt.** Phase 2's header declares, per block, its
`requires_facts` and `requires_declarations`. Reopening a fact marks stale exactly the
blocks whose contracts name it; blocks that never needed it are untouched. "Everything
written after it" would make reopening unusable.

**Two regions, one grammar, split by lifecycle.** `%% paper-writing <kind> begin
sha256=<hex>` … `end`, as `declarations` (written at the gate) and `provenance` (written
at `substitute` time). One grammar means one parser; they stay distinct because one
records a decision and the other records an event. This is load-bearing, not incidental:
Phase 1's `MARKER_PREFIX` is `b"%% paper-writing block"` and its scanner skips every line
not starting with it, so both regions are prose to Phase 1 and can never be read as a
block. Narrowing that constant is what makes the two grammars coexist.

**Integrity is ours alone.** The regions land in the one area Phase 1 declares undigested
— prose between blocks — and `paper/*` is gitignored, so no history recovers a bad hand
edit. Each region carries a digest over its own body, checked before every write.

**Classes live with the folder, not in a central file.** `guidance/<folder>/.paper-writing.json`
is already ignored by the existing `guidance/*/*` rule, so it needs no `.gitignore` edit;
the class travels with the folder it describes, so a new evidence folder arrives carrying
its own; and a file directly under `guidance/` would publish the operator's folder names.
A folder with no marker is `unclassified` — **reported and never guessed**. The registry
is the derived view `plan` reports. A central file would be the second source of truth
Phase 1 rejected for offset indices.

**Anti-pattern named, not fixed.** `proposal-workspace.ts` hardcodes
`GUIDE_DIRECTORY = "guidance/paper-guide"`. That is exactly the name-coupling this
registry must not repeat. `openspec/specs/deliberation-required-sources/spec.md` is the
in-repo precedent for declaring sources as **data** instead. Neither is this change's to
repair.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/paper-writing/scripts/paper_cli.py` | Modified | Two verbs + refusal classes |
| `.claude/skills/paper-writing/scripts/paper_block.py` | Modified | Optional `--contract` record |
| `.claude/skills/paper-writing/scripts/` | New | `paper_guidance.py`, `paper_declarations.py`, `paper_provenance.py` |
| `.claude/agents/insumos-observer.md` | New | First agent of this build; non-terminal stretch |
| `.claude/skills/paper-writing/SKILL.md` | Modified | Two verbs, two regions, the drift posture |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Phase 2's modules absent on disk; this change reads its header schema | High | Land after Phase 2; propose against its artifacts |
| Declarations region hand-edited between sessions, no git history behind it | Medium | Own digest; refuse `DECLARATIONS_HAND_EDITED`, never overwrite |
| Whole-file contract hashing over-reports drift | Medium | **Accepted, not solved** — see below |
| A block written without `--contract` | Low | `plan` reports it `unprovenanced` — never silently assumed current |
| Fresh clone reports every guidance folder `unclassified` | High | Designed behaviour, stated as such — not a default, not a fault |
| Six deliverables against a 1400-line budget | High | Slice: (a) guidance, (b) declarations + `declare`, (c) provenance + `plan` + agent |

**On the accepted risk.** Editing one block's guidance flags every block of that section.
Contract prose is not block-delimited and cannot be without restructuring files the
operator wrote by hand, so per-block hashing is not available. The error leans toward
over-reporting: a contract edit flags every block of that section and the operator rules
per block. Over-reporting never misses drift; under-reporting would, and a missed drift is
a block silently standing on bytes that no longer exist. Over-reporting is the safe
direction.

## Rollback Plan

`git revert` the change. Both regions live only in `paper/main.tex`, which is untracked,
so revert leaves a document whose regions no code reads — inert LaTeX comments, rendering
nothing. `guidance/<folder>/.paper-writing.json` files are untracked and may be deleted by
hand. No migration and no tracked data to unwind.

## Dependencies

- Phase 2 landed: the ten facts, the six declarations, per-block `requires_facts` /
  `requires_declarations`, the derived order.
- Phase 1's `MARKER_PREFIX` staying `b"%% paper-writing block"`. A test asserts the two
  grammars are disjoint, so narrowing it there goes red here.

## Success Criteria

- [ ] A declarations region is written, re-read, and a second session resumes from it without re-asking
- [ ] A fact resolution and a declaration are both recorded, and recording a fact resolution does not admit a seventh declaration id
- [ ] A fixed entry refuses overwrite; `--reopen` names exactly the blocks whose contracts require that entry, and leaves the others untouched
- [ ] Editing one contract byte makes `plan` name the blocks written against the old bytes — and rewrites none
- [ ] A block written without `--contract` reports `unprovenanced`, and is never treated as current
- [ ] A third guidance folder, named like neither shipped folder, reports `unclassified`
- [ ] `status` reports zero blocks for a `main.tex` holding only the two regions, and refuses nothing
- [ ] Every new `Refused` is classified in `paper_cli.REFUSAL_CLASSIFICATION` (the roster test derives it)

## Proof Discipline — mutations to be executed, not asserted

| # | Mutation | Goes red because |
|---|---|---|
| 1 | Rename the region marker to start `%% paper-writing block` | `status` must then refuse; proves the disjointness test can fire |
| 2 | Let `declare` overwrite a fixed entry | Immutability guard |
| 3 | Recompute the contract hash on read instead of recording it at write | Drift becomes structurally undetectable |
| 4 | Default an unclassified folder to style-reference | Unclassified reporting |
| 5 | Widen `--reopen` to invalidate every written block | Over-invalidation guard (the mirror case) |
| 6 | Admit a fact-resolution id into `requires_declarations` | The closed vocabulary is still closed |

Every harness purges `__pycache__` before re-running (a same-size edit otherwise reuses a
stale `.pyc` and the mutation never runs), and asserts **both** that the anchor matched an
exact count **and** that the file digest changed — a matched anchor is not a mutation that
executed. Both traps are recorded from this repository.

---

**Budget note**: this artifact exceeds the 450-word proposal budget. The overage is the
mutation table and the two vocabulary paragraphs. Kept deliberately: this repository has
been bitten three times by guards that could not go red, and by a closed vocabulary
opened without anyone noticing.
