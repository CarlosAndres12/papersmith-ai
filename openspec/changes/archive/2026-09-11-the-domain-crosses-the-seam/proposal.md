# Proposal: The Domain Crosses the Seam

> **Size note.** Over the 450-word budget, deliberately, for the reason
> `the-engine-leaves-its-skill/design.md` gave: the B2 ruling's *argument* has to travel with
> its verdict. A verdict recorded without its reasoning is what someone reverts later.

## Intent

Cut 1 moved the engine out of the skill. It is shared **by location** and still
domain-carrying **by content**: 167 of its 17,100 lines name the mathematical proposal
(seam measurement §A.1). A second implementation domain can now import the engine and
still cannot use it — its modules would declare `equations`, its refusals would speak of
ecuaciones, and its documents would be read from `proposals/`.

Cut 2 moves those 167 lines into the profile. It is also the cut that makes the deferred
guard possible: Cut 1 put the Python mirror of the TS domain-profile lock here *"because
with no domain words yet moved it would pass vacuously"* (Cut-1 `design.md` D3, open
question 3). Until this lands, neutrality is a claim with no instrument.

## The B2 ruling this proposal is built on — Option A, already taken

The coarse key `sections` **stays a shared word**; only the fine key `equations` becomes
profile-supplied. Three reasons, and the line count is not one of them:

1. **`sections` is not a domain word.** It names document structure, not subject matter.
   Every managed markdown revision in this forge is organized in numbered sections.
   Profiling it would profile something that is not domain-specific — the mirror of the
   error this seam exists to correct.
2. **The join must not be able to drift.** `unreached_mathematics` crosses
   `__provenance__["sections"]` with `__benchmark__["arms"][x]["sections"]` — its own
   docstring calls this *"the join nothing else in the flow crosses"*. A profile-supplied
   coarse key lets two domains pick different words, after which the join returns `[]` —
   **and an empty list there reads as success**: "nothing left unreached". Silent, and
   confidence-inspiring.
3. **The flexibility Option B bought already exists elsewhere.** `document_reader.drift_units`
   supplies *how* units are extracted while the key stays `sections`.

Options C (changes `proposal-implementation`'s existing behaviour) and D (lets an
experiments target declare `equations`) stay rejected. **Do not re-open B2.**

## Scope

### In Scope

1. **The 40 schema lines**, split by consumer: the provenance side (14) and the findings
   side. Every quoted `"equations"`, `remedy_equations` and `remedyEquations` becomes a
   profile read. `"sections"` is not touched.
2. **The one writer.** `authored_package_init` writes "Each module declares the sections
   and equations it implements in `__provenance__`…" *into the target's*
   `src/<Package>/__init__.py`. That sentence becomes `provenance.authored_init_sentence`.
3. **The 25 executable strings** — including the Spanish refusal prose in `cmd_handoff`
   that spells *ecuación/ecuaciones* — behind `vocabulary`.
4. **The 4 identifiers** (`unreached_mathematics` and siblings) renamed to what they do.
5. **The 10 hardcoded paths** — `proposals_root()`'s `FORGE_ROOT / "proposals"` and the
   refusals naming it — behind `documents`.
6. **The 88 comment/docstring lines.** Not cosmetic: the `names` lock reads the engine's
   whole text, so an unswept comment keeps it red.
7. **The two locks**, which are what makes any of the above provable: a Python mirror of
   `tests/proposal-deliberation-domain-profile-lock.test.mjs` (globbing `*/impl_profile.py`
   rather than hardcoding one), plus a neutrality lock over `_core/implementation/engine/`
   that fails when the engine spells any declared `names` word.
8. **The kit agreement.** `assets/kit/src/module.py`'s `"equations": ["{{EQUATION}}"]` must
   equal `PROFILE.provenance.claim_key`. Nothing moves — the kit already ships under
   `kit.root` — but the divergence is silent today and gets a test.

### The proposed field set, and what reads each one

Every field earns its place the same way Cut 1's did: **a profile field nothing reads
cannot be mutation-proven, and an unprovable field is the shape of a false guard.**

| Field | Read by | Mutation moves |
|---|---|---|
| `provenance.claim_key` | the 14 provenance sites; the kit lock | `verify`, `handoff` |
| `provenance.authored_init_sentence` | `authored_package_init` | `materialize` |
| `findings.locus_key` | `cmd_admit`'s field loop, finding impact | `admit` |
| `findings.remedy_locus_key` | the same loop, `cmd_handoff` | `admit`, `handoff` |
| `findings.notation_keys` | the `handoff` / report wire payloads | `handoff` |
| `vocabulary.subject_singular` / `_plural` | the three Spanish refusal builders | `handoff` |
| `vocabulary.artifact_noun` | `authored_package_init`'s "{name} formulation" | `materialize` |
| `vocabulary.names` | both locks, and nothing else — which is the TS field's own justification | lock goes red |
| `documents.directory` | `proposals_root()` → `bound_revision_text` + 5 refusals | the 5 path refusals |
| `documents.label` | those same refusals | the same |

### Out of Scope

Not proposed, and **not listed as future work**:

- **Cut 3** — `revisionSha256` scalar→pair at 24 sites, and `documents` becoming a LIST.
  `documents` exists here as a **single-entry shape only**; making it plural is Cut 3's
  whole job.
- **Any rename of `proposalDigest`**, `GATE_PROPOSAL_*`, `_proposal_digest`,
  `_verify_gate_proposal`, `_gate_proposal_question`, `_verify_optional_election`,
  `cmd_propose`, `_authorization_binding`, `_verify_gate_authorization`,
  `_campaign_identity`, `_load_remote_execution_*`. 78 of the 152 `proposal` hits are the
  **campaign** proposal. `proposalDigest` is a member of `_AUTHORIZATION_BINDING_KEYS` and
  is written into minted gate authorization tokens inside every target's committed
  `.implementation/position.jsonl` — a ledger that travels in clones. A sweep driven by the
  152 number would invalidate every previously minted authorization.
- **`compose` / M1.** LaTeX end to end (`DISPLAY_BLOCK_RE = \$\$.*?\$\$` plus
  `TAG_RE = \\tag\{…\}`); an experiments document has neither. Whether composition becomes a
  profile-supplied callable or `compose` stays the one per-skill command is an **open
  operator decision**. This proposal does not take it.
- Creating `experimental-implementation`. F6 (`MANAGED_ARTIFACT_MARKER`'s four spellings).

### Fields deliberately NOT proposed, each with its reason

| Field (from §B1) | Why not |
|---|---|
| `provenance.drift_unit_key` | **Removed by the B2 ruling.** It is the coarse key; supplying it is exactly the drift reason 2 forbids |
| `provenance.revision_key` | `revision` is general as a *word* (F2). Its *shape* is Cut 3 |
| `document_reader.drift_units` | No Cut-2 reader. `revision_sections` extracts numbered Markdown headings — document structure, not subject matter, by the ruling's own reason 1. It lands the day a domain that does not number its sections exists |
| `documents.marker` | F6: the marker has four spellings across two languages. A profile-supplied fifth cannot pull the other four with it, so this would worsen the coupling F6 records. Record, do not act |
| `cli_invocation` | Rejected at Cut 1 for a reason that still holds: the profile supplies the path, the engine composes |

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `implementation-engine-neutrality`: extends from *host-location* (`kit.root`, `cli.path`,
  `objective`) to *host-domain* — the engine sources its provenance claim key, its findings
  keys, its subject vocabulary, its document location and the sentence it authors into a
  target from the profile; and it gains the neutrality lock Cut 1 deferred, including the
  requirement that a declared `names` word appearing anywhere under
  `_core/implementation/engine/` is a failure.

## Approach

Red-first, one field at a time, each landed with its own mutation before the next. The
resolver's `_REQUIRED_NESTED` grows; the refusal codes do not change shape.

**The proof is the same instrument and a harder bar.** Cut 1 touched 61 original lines and
held 28 sealed digests byte-identical. Cut 2 touches 167 across three commands whose purpose
*is* the document (`admit`, `handoff`, `compose` — 235 lines). **All 28 sealed digests must
still be byte-identical. Any movement is a defect, never a new golden** — per
`proposal-deliberation/SKILL.md:301`, structurally, not as a courtesy.

Two things make that reachable: a profile supplying the same literal composes the same bytes,
and the seal corpus already exercises all 14 provenance sites, all 14 findings sites and the
5 hardcoded-path refusals both with and without `IMPLEMENTATION_PROPOSALS` set (§C).

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/_core/implementation/engine/implementation_engine.py` | Modified | the 167 lines |
| `.claude/skills/_core/implementation/impl_domain_profile.py` | Modified | new required nested keys, validated by leaf |
| `.claude/skills/proposal-implementation/impl_profile.py` | Modified | the ten fields above |
| `.claude/skills/proposal-implementation/assets/kit/src/module.py` | Unchanged | asserted against `claim_key`, not edited |
| `tests/test_implementation_profile.py` | Modified | one mutation per new field |
| `tests/test_implementation_domain_lock.py` | New | the Python mirror + the engine neutrality lock |
| `tests/seal/*` | **Unchanged** | `git diff --exit-code` must exit 0 |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| A sealed digest moves | **High** | The whole cut is judged on this. Land field by field, re-run the seal per field, never batch |
| A grep-driven sweep hits the 78 campaign-proposal lines | **High** | The named exclusion list above, asserted as a test, not a discipline |
| `claim_key` diverges from the kit template silently | Med | The kit agreement lock (scope item 8) |
| The `names` lock lands green because `names` was declared dishonestly | Med | Plant a domain word in `engine/`; the lock must redden. Declare `names` from the measurement's own token list, not from what happens to pass |
| Moving the Spanish prose hardens M2's doctrine violation into a contract shape | Med | Correct for the extraction, unresolved as doctrine. **Recorded, not fixed here** |
| The comment sweep is cut for budget, leaving the lock unlandable | Med | The lock is scope item 7 and the comments are item 6; they are one unit |
| A surviving mutation is read as a weak test | Low | Measure the property first. A surviving mutation has two explanations |

## Rollback Plan

One revert. The engine's 167 lines, the two profile files and the two new tests are one
commit; `tests/seal/` is untouched by construction, so the pre-change seal is still the
post-revert seal. No migration, no target ledger written, no minted authorization touched —
no binding key is a schema key.

## Dependencies

- `the-engine-leaves-its-skill` archived (it is), with 28 sealed digests green.
- `.venv/bin/python` (3.12). Bare `python3` here is 3.9 and cannot import these modules.

## Success Criteria

- [ ] All **28 sealed digests byte-identical**; `sha256(tests/seal/digests.json)` unchanged;
      `git diff --exit-code tests/seal/` exits 0. **Zero declared delta.**
- [ ] Every new profile field is mutation-proven **both ways**: removing it raises a named
      `…_INCOMPLETE` refusal naming the missing *leaf*, and changing it moves the named digest
      in the table above. A field that can do neither is deleted, not shipped.
- [ ] The neutrality lock goes **red** when a declared `names` word is planted anywhere under
      `_core/implementation/engine/`, and green after the plant is reverted.
- [ ] The Python domain-profile lock discovers profiles by globbing, so a third skill is held
      to the rule without editing the lock.
- [ ] The kit template's provenance keys equal `PROFILE.provenance.claim_key` plus the shared
      `sections`, asserted.
- [ ] `npm test` **595/595** and `.venv/bin/python -m unittest discover -s tests`
      **Ran 2849, OK (skipped=6)** both held; outputs pasted before and after.
- [ ] `reachable_refusal_codes()`'s pinned count is re-asserted, moved only if a refusal was
      genuinely added, and the new number recorded.

## Size Forecast

~1,050 authored changed lines (±150): engine ~330 (167 touched, add+del), resolver ~70,
profile ~90, the two locks ~180, per-field mutation tests ~330, kit lock ~30. **Inside the
1,400-line budget; single PR**, with ~25% headroom. If it overruns, the separable slice is
items 3–6 (vocabulary, identifiers, paths, comments) — but item 7's lock cannot land without
item 6, so the split is *schema + locks* / *vocabulary + comments + locks*, never
locks-alone.

## Proposal Question Round

Five decisions this proposal took. Each is answerable now or correctable at design; none
blocks writing specs. B2 is **not** among them and is not re-opened.

1. **`document_reader.drift_units` deferred to the cut that has a reader.** Assumed: yes —
   the B2 ruling cites it as where flexibility *will* live, not as Cut-2 work, and
   `revision_sections` is document structure by the ruling's own reason 1. Correct this if
   the ruling intended the field to land now.
2. **`documents.marker` excluded on F6 grounds.** Assumed: excluded. A profile-supplied fifth
   spelling makes F6 worse, and F6 is out of scope.
3. **`documents.label` is a field rather than derived from `directory`.** Assumed: a field —
   a refusal naming "the proposals directory" is prose, not a path, and the two diverge the
   moment a domain's directory is not its noun.
4. **The 4 domain identifiers are renamed, not aliased.** Assumed: renamed. An alias leaves
   the domain word in the engine and the `names` lock red.
5. **The Spanish prose moves as-is.** Assumed: moved verbatim into `vocabulary`, with M2
   recorded unresolved. Translating it here would be a behavioural delta the seal must
   refuse.

## Citations Checked

Every symbol below was located **by name** in the source during this phase, never inherited
by line: `unreached_mathematics` (and its "the join nothing else in the flow crosses"
docstring), `authored_package_init` (and its authored sentence), `revision_sections`,
`proposals_root` (and `IMPLEMENTATION_PROPOSALS`), `MANAGED_ARTIFACT_MARKER`,
`DISPLAY_BLOCK_RE`, `TAG_RE`, `cmd_admit`, `cmd_handoff`, `cmd_compose`, the 19 quoted
`"sections"`/`"equations"` sites, `remedy_equations` / `remedyEquations`, the kit's
`src/module.py` `{{SECTION}}`/`{{EQUATION}}` tokens and `src_benchmark/__init__.py`'s `arms`,
`impl_domain_profile._REQUIRED_NESTED` / `_OBJECTIVE_REQUIRED` / `ImplementationProfileError`,
`impl_profile.PROFILE`, and `tests/proposal-deliberation-domain-profile-lock.test.mjs`'s
`discoverProfiles`.

**One inherited citation did not resolve.** The launch brief cites
`openspec/changes/archive/2026-09-11-the-engine-leaves-its-skill/archive-report.md`. That file
does not exist; the archive holds `proposal.md`, `design.md`, `tasks.md` and
`verify-report.md`. Cut 1's seam description was read from `design.md`, which does carry it.
**F3 is reported here as already closed**: all five refusals now spell `proposals_root()`, so
the measurement's "one declared delta" is behind us and is not a Cut-2 delta.
