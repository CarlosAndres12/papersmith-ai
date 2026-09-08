# Design: Generalize the deliberation core for a second domain layer

## Technical Approach

One move, repeated ten times: the structure stays in `_core/deliberation/engine`,
the domain value moves into `profile.ts`, and `proposal-deliberation`'s profile
declares exactly today's values. Behaviour is preserved *by construction*, not by
care. Four chained slices, both suites per slice.

Three of the ten changes are not that move and are designed separately below:
change 2 (a substitution that can regress silently), change 8 (collides with the
byte-preservation invariant), change 9 (a new severity that has no precedent
either way).

### Corrections to inherited claims — measured in this phase

| Inherited claim | Measured |
| --- | --- |
| `EntryType` has no `table`/`figure` | **False.** `types.ts` already declares `table_reference` and `figure_reference`. They are *never emitted*: `buildStructuralIndex` produces only `document`, `section`, `subsection`, `heading`, `display_equation`, `paragraph`. The gap is the indexer, not the type. |
| Change 6 is "additive — no existing document gains an entry" | **False.** `entryId` is `${type}:${sha}`. Retyping a GFM table from `paragraph` to `table` changes its id, and `target-resolver.ts`'s `leaf()` list does not contain the new names, so a retyped table silently drops out of composite member selection (`materializeCompositeTarget`). Change 6 is a *retyping*, not an addition. |
| `proposals/` is 12 sites | **Undercount.** 70 occurrences across 10 core files; ~35 are refusal prose and MCP tool-schema descriptions in `proposal-workspace.ts`, not path construction. |
| The five naming regexes "agree only by luck" | **They do not agree at all** — four distinct semantics (below). Collapsing them into one regex is itself the regression. |
| `proposals/` holds documents that would need migration | **Empty.** Only `.gitkeep`. Zero migration burden for changes 6 and 8. |
| Change 4's gate is covered today | `tests/proposal-deliberation-v2-source-routing.test.mjs:252` only exercises the *acknowledged* path. Nothing asserts `MATH_REMOVALS_NOT_ACKNOWLEDGED`. |

Vacuous-pass claim **confirmed**: on a math-free document `labels`, `tags`,
`referencesOk` and `displayDelimiters` in `candidate-validator.ts` are all `true`
over empty sets, and `mathDelta` returns `{lost:[],added:[]}`.

## Architecture Decisions

### Decision: `artifact-naming.ts` exports a named matcher *family*, never one regex

**Choice**: preserve every existing acceptance semantic under its own exported
name, composed from one escaped stem.

| Semantic | Pattern today | Sites |
| --- | --- | --- |
| STRICT | `^stem-(?:SEG-)?r\d{2,}\.md$` | `orchestrator.ts`, `consistency-audit.ts`, `revision-lifecycle-store.ts` (MANAGED), `proposal-workspace-adapter.ts`, `proposal-workspace.ts` (`MANAGED_CHAT_DOCUMENT_FILENAME`) — 5 sites, byte-identical |
| LAX PARSE | `^stem-(?:(.+)-)?r(\d+)\.md$` | `document-state.ts`, `revision-lifecycle-store.ts` |
| INCREMENT | `^(stem-(?:SEG-)?r)(\d+)\.md$` | `proposal-workspace.ts` (successor slug bump) |
| LOOSE SCAN | `/\bstem-…r\d{2,}\.md\b/i` — unanchored, case-insensitive | `intent-resolver.ts` |
| INITIAL | `^stem-SEG-r01\.md$` | `initial-revision-creation.ts` |
| SCHEMA STRING | three JSON-Schema `pattern` strings, one allowing a `proposals/` prefix | `proposal-workspace.ts` |

LAX and STRICT genuinely diverge: LAX accepts `…-r1.md` and any lineage
characters. In `revision-lifecycle-store.ts` LAX runs *behind* STRICT and the
laxness is inert; in `document-state.ts` LAX is the **only** gate on
`loadDocumentState`. Collapsing them tightens `loadDocumentState` silently.

**Alternatives considered**: one canonical regex (changes acceptance at two
sites); a regex *string* on the profile (reproduces the current drift — the
profile already learned this lesson with `proseReferencePattern`).

**Rationale**: change 2's risk is not "does it still compile", it is "does it
still accept and refuse the same names". A named family makes each divergence a
decision with a test behind it.

```ts
export const SEGMENT = '[a-z0-9]+(?:-[a-z0-9]+)*';
export type ManagedRevisionName = string & { readonly __managedRevision: unique symbol };
export type ManagedInitialName  = string & { readonly __managedInitial:  unique symbol };

export const artifact: { directory; sidecarRoot; stem; marker: Buffer; revisionLabel(n: number): string };

export function strictManagedRevision(name: string): name is ManagedRevisionName;
export function parseManagedRevision(name: string): { lineage: 'ROOT' | string; revision: string; ordinal: number } | undefined; // LAX
export function parseRevisionIncrement(name: string): { prefix: string; ordinal: number } | undefined;
export function scanManagedRevision(text: string): string | undefined;      // loose, case-insensitive
export function isInitialRevision(name: string): boolean;

export function managedRevisionFilename(lineage: 'ROOT' | string, ordinal: number): ManagedRevisionName;
export function initialRevisionFilename(lineage: 'ROOT' | string): ManagedInitialName;
export function documentPath(filename: string): string;      // `${directory}/${filename}`
export function statePath(filename): string; export function receiptPath(filename): string;
export function withdrawnMarkerPath(operationId: string): string;
export function publicRelativePaths(filename: string): readonly [string, string, string];
export function managedRevisionSchemaPattern(opts?: { directoryPrefix?: boolean }): string;
```

### Decision: the three literal types become **branded** strings, not `string`

`revision-domain.ts`, `revision-receipt.ts` and `proposal-workspace-adapter.ts`
type `targetFilename` as the literal `'research-concept-r01.md'`. A TypeScript
literal type cannot depend on a runtime profile value. Widening it to `string`
deletes a compile-time check and nothing announces the loss.

**Choice**: `ManagedInitialName`, producible only by `initialRevisionFilename()`.
The compile-time constraint survives the de-literalization; the runtime equality
in `proposal-workspace-adapter.ts` becomes `isInitialRevision(...)`.
**Alternative rejected**: plain `string` — silently weaker, which is exactly the
failure mode change 2 exists to prevent.

### Decision: the extended lock gets a **second core-only surface**, not a longer `declared` list

The existing lock scans two surfaces with the same value list: core, *and* the
whole node suite. Adding `stem`/`directory` to `declared` would make ~every node
fixture a leak, because fixtures must write real files named
`proposals/research-concept-…`.

**Choice**: a new test `no file in the shared core spells the artifact
namespace`, reading `artifact.{stem, directory, sidecarRoot}` off `profile.ts`
and scanning **core only**, with **zero exemptions** (`artifact-naming.ts` reads
`DOMAIN`, so it spells nothing either). The suite scan keeps today's four
`declared` values plus `names`, unchanged.

**Declare `sidecarRoot` with its leading dot** (`.proposal-deliberation`). The
bare word legitimately survives in core as `PARSER_VERSION`
(`'proposal-deliberation/1'`), the `sdd/proposal-deliberation-*` design
citations, `Symbol.for('papersmith-ai.proposal-deliberation…')` and the
`proposal-deliberation-${uuid}` operation-id factories — none of which is the
sidecar namespace. Without the dot the lock goes red on all of them.

### Decision (change 8): **(b) — the header is its own resolved locus, profile-gated**

**Recommended. The user makes the final call.**

| Option | Survives the invariant unmodified | Human sees it in the `.md` | Slice cost | Cost to `proposal-deliberation` |
| --- | --- | --- | --- | --- |
| (a) sidecar-only | Yes, untouched | **No** — nobody reads `.proposal-deliberation/receipts/` | ~40 lines | A required `changeSummary` would force an edit to its published SKILL.md |
| **(b) own resolved locus** | **Yes — satisfied, not bypassed** | **Yes** | ~180 lines | **Zero, if profile-gated** |
| (c) declared prefix exemption | **No — puts a hole in it** | Yes | ~120 lines | Weakens its strongest guarantee for a feature it does not use |

The mechanism, read out of the code rather than assumed:
`composeSuccessorBlockCandidate` checks preservation only over the *gaps between
block spans*. A header that is itself a block span is inside the union, so the
invariant holds by construction — no exemption, no weakening. `patch-compiler.ts`
already builds blocks from spans in both successor paths.

Shape:

- `profile.artifact.changeHeader?: { heading: string; render(s: {what,why}): string }`.
  `proposal-deliberation` **declares none** → `CREATE_SUCCESSOR` requires
  nothing, `renderFromIdea` emits nothing, bytes are identical. Same opt-in
  pattern already agreed for changes 7 and 9.
- When declared: `renderFromIdea` emits the header section into v1 (zero
  migration — `proposals/` is empty); `CREATE_SUCCESSOR` requires
  `changeSummary:{what,why}` or refuses `CHANGE_SUMMARY_REQUIRED`; the engine
  appends **one** engine-owned `replace` block over that entry.
- The engine chooses the *target* (it already chooses `successorFilename`); the
  *content* is the caller's `changeSummary` through a pure renderer. The
  resolver's "never chooses targets" contract is untouched — the block is added
  to the plan, not invented by the resolver.
- Ship (a) **as well**: `createRevisionReceipt` also carries `changeSummary`.
  (b) overwrites the previous header, so the receipt chain is where full history
  lives. This costs ~10 lines and closes the one real weakness of (b).

Blast radius to carry into tasks — the synthetic block reaches
`plan.resolvedTargets`, therefore: `operation-spec.ts` `successorTargetCount`
budgets, `growth-threshold.ts`, `successor-acceptance-registry` `compositeTargetIds`,
the receipt's `resolvedEntryIds`, and the arity guards
`SUCCESSOR_EXACTLY_ONE_REPLACE_REQUIRED` / `SUCCESSOR_COMPOSITE_TARGET_REQUIRED`.
Edge case: the header's replaced text runs through `preservationDelta`; a
`\command`-shaped token in a previous header would register as a lost macro atom.

**Alternative found in code, recorded and rejected**:
`compileSuccessorCompositeChangeset` already supports `op:'insert'` at a
zero-width span, so a header could be inserted at the document head without
existing in v1. Rejected: it needs a second code path (insert-first, replace-
after) and grows an unbounded document prefix that `growth-threshold` then sees.

### Decision (change 9): advisory + acknowledgement — **USER DECISION, not settled here**

The engine already contains both severities and states its own test.
`canonicalFormViolations` blocks outright *"because they are never intentional"*.
`mathDelta` is reported on preview and refused on accept unless echoed by id,
because *"the caller has to SEE what disappeared before it can acknowledge it"*.

A source-authority conflict is intentional almost by definition — the ceiling
exists because a human may want to assert past it — which places it in the
acknowledge class, yet acknowledging is what defeats a ceiling. The deciding
difference is **who can competently acknowledge**: a lost atom is verifiable from
the preview by the caller; a ceiling conflict requires knowing whether the source
truly bounds *this* claim, which the detector inferred by pattern.

**Argued position**: preview-time advisory + `acknowledgedSourceConflicts` on
accept, mirroring the preservation gate, with
`profile.sourceAuthority.severity: 'advisory' | 'refuse'` defaulting to
`advisory` so a domain that wants a hard ceiling declares one. A heuristic
detector behind a hard refusal makes a false positive unrecoverable inside the
engine; a soft gate an agent clears reflexively is the opposite failure.
`proposal-deliberation` declares no `sourceAuthority` at all, so both readings
are byte-identical for it and this decision can be deferred to slice 4.

### Decision (change 1): profile-supplied path segments are validated at load

`domain-profile.ts` must refuse `artifact.directory`/`sidecarRoot` that are not a
single safe segment (`^\.?[A-Za-z0-9._-]+$`, no `/`, no `..`) with
`DELIBERATION_DOMAIN_PROFILE_UNSAFE_ARTIFACT_PATH`. Change 3 turns a sandbox root
into a profile value; `REQUIRED`-membership alone does not make it safe.

### Decision (change 6): bump `PARSER_VERSION`, and do **not** supersede the old one

Retyping tables changes `entryId`s. `derived-state-store.ts` accepts a cached
index whose `parserVersion` is in `SUPERSEDED_PARSER_VERSIONS`, and
`saveDerivedState` throws `INCOMPATIBLE_COMMITTED_STATE` when a COMMITTED state
re-serializes differently. So change 6 bumps `PARSER_VERSION` and leaves
`SUPERSEDED_PARSER_VERSIONS` alone — supersession means "same parse output under
a new name", which is precisely what this is not. The new types must also be
added to `target-resolver.ts`'s `leaf()` in the same commit.

## Data Flow

    profile.ts ──artifact{}──► domain-profile.ts (validate + freeze)
                                     │  DOMAIN
                                     ▼
                            artifact-naming.ts  ◄── the ONLY speller of names
                       ┌────────────┼─────────────┬──────────────┐
                       ▼            ▼             ▼              ▼
              orchestrator   document-state  lifecycle-store  workspace(+schemas)
                       │
    CREATE_SUCCESSOR   ▼
      resolve ─► plan ─► [+ engine-owned header block, if profile.changeHeader]
              ─► patch-compiler ─► composeSuccessorBlockCandidate
                                     │ preservation checked over the GAPS only
              ─► candidate-validator (profile.preservation / profile.references)
              ─► preview (delta reported) ─► accept (echoed ids) ─► publish
                                                                     │
                                              receipt + changeSummar ─┘

## File Changes

| File | Action | Description |
| --- | --- | --- |
| `_core/…/artifact-naming.ts` | Create | The matcher family, builders, branded types, schema-pattern strings |
| `_core/…/preservation.ts` | Create (from `math-integrity.ts`) | Neutral atoms/delta/violations over `profile.preservation` |
| `_core/…/domain-profile.ts` | Modify | `artifact`, `preservation`, `references`, `sources`, `sourceAuthority`; `REQUIRED`; path-segment validation |
| `_core/…/{orchestrator,consistency-audit,revision-lifecycle-store,document-state,intent-resolver,initial-revision-creation,initial-revision-renderer,revision-domain,revision-receipt,proposal-workspace-adapter,proposal-workspace,derived-state-store,revision-lifecycle-transaction,lifecycle-state-store}.ts` | Modify | Import names from `artifact-naming.ts`; spell none |
| `_core/…/{types,document-index,target-resolver}.ts` | Modify | New entry types, GFM table recognition, `leaf()`, `PARSER_VERSION` bump |
| `_core/…/{candidate-validator,reference-index}.ts` | Modify | `profile.preservation` / `profile.references`; alias fields |
| `proposal-deliberation/profile.ts` | Modify | Declares today's values; no `sourceAuthority`, no `changeHeader`, `guidance/paper-guide` not required |
| `proposal-deliberation/preservation-math.ts` | Create | The math extractor + rule set |
| `tests/proposal-deliberation-domain-profile-lock.test.mjs` | Modify | New core-only artifact-namespace test; suite scan unchanged |

## Testing Strategy

| Layer | What to test | Approach |
| --- | --- | --- |
| Unit | each matcher's divergence (LAX accepts `r1`, STRICT refuses; LOOSE is unanchored + case-insensitive) | one assertion per divergence, both directions |
| Unit | branded types reject an unbranded string | type-level test |
| Unit | preservation/reference guards over a **non-empty** atom set | `assert.ok(atoms.size > 0)` **before** asserting the delta — an empty fixture is a failure |
| Integration | header block satisfies the invariant | successor with a `changeHeader` profile publishes; `preservedRegions` cover every gap |
| Integration | a section containing a GFM table still materializes the table's bytes | composite materialization over a table fixture |
| Lock | core spells no artifact value | new core-only scan, zero exemptions |
| Suite | `npm test` 386/0 **and** `.venv/bin/python -m unittest discover -s tests` Ran 2718 OK (skipped=6) | both, every slice |

### Mutation proof — procedure

For every mutation: (1) record `rg -c '<anchor>' <file>` **before**; (2) mutate;
(3) assert the after-count equals the expected value and differs from before —
`git diff --stat` proves nothing for untracked files and a same-size edit can be
masked; (4) clear any jiti/transform cache so the mutated source actually runs;
(5) run **both** suites and record the failing test *names and assertion text*,
not just "red"; (6) revert and re-run both suites to baseline.

| # | File / line | Mutation | Must go red | Anchor count before → after |
| --- | --- | --- | --- | --- |
| M2a | `orchestrator.ts`, `MANAGED_REVISION_FILENAME` | re-hardcode the literal regex | new lock test, message naming `orchestrator.ts spells "research-concept"` | `rg -c 'research-concept'` 0 → 1 |
| M2b | `artifact-naming.ts`, `parseManagedRevision` ordinal group | tighten `\d+` to `\d{2,}` (collapse LAX into STRICT) | `loadDocumentState` accepts `…-r1.md` while `strictManagedRevision` refuses it | `rg -c '\\d\+'` N → N−1 |
| M4a | `orchestrator.ts` accept gate | `unacknowledged.length` → `false` | a **new** test publishing a genuinely lost atom without acknowledging it, asserting `MATH_REMOVALS_NOT_ACKNOWLEDGED` (no such test exists today) | `rg -c 'unacknowledged.length'` 1 → 0 |
| M4b | `orchestrator.ts` alias read | drop the `acknowledgedMathRemovals` alias | `tests/proposal-deliberation-v2-source-routing.test.mjs` (it sends the old name) | `rg -c 'acknowledgedMathRemovals'` ≥1 → 0 |

M2a re-hardcodes rather than inverting an assertion on purpose: inverting proves
only reachability, re-hardcoding proves the lock catches the exact regression
class change 2 exists to prevent. M2b exists because a collapse that
type-checks and passes every current test is change 2's real failure mode.

## Threat Matrix

`N/A` — no routing, shell, subprocess, VCS/PR automation, executable-file
classification, or process-integration boundary changes. Documentation-like
paths: N/A (no file is classified or executed). Git selection / commit / push /
PR rows: N/A (nothing in this change touches VCS). The one adjacent risk — a
profile-supplied path segment escaping the workspace sandbox — is handled as a
design requirement under change 1 above, with its own RED test, rather than
stretched into an inapplicable matrix row.

## Migration / Rollout

Per slice, on its own branch, reverted by its own commits.

**Products already written under the old shapes** (not only producers):

| Product | Verdict |
| --- | --- |
| `proposals/*.md` managed documents | **None exist** — only `.gitkeep`. Zero migration for changes 2, 3, 6, 8. |
| `.proposal-deliberation/state/*.json` derived caches | Invalidated by change 6's `PARSER_VERSION` bump — intentional, and not listed as superseded |
| `.proposal-deliberation/receipts/*.json` | Untouched by 1–7; change 8 adds an optional `changeSummary`, and `validatePublicationReceipt` ignores unknown fields |
| `.proposal-deliberation/withdrawn/<id>/audit-marker.json` | Path becomes profile-derived under change 3; none exist on disk |
| `PARSER_VERSION 'proposal-deliberation/1'` | **Stays.** It is a version tag, not the sidecar namespace; the dot-prefixed `sidecarRoot` keeps the lock off it |

## Open Questions

- [ ] **Change 8 (user)**: adopt recommendation (b), profile-gated, with the
      receipt field from (a) shipped alongside? Slice 4 is gated on this.
- [ ] **Change 9 (user)**: `SOURCE_AUTHORITY_CONFLICT` as advisory +
      acknowledgement (argued above) or hard refusal? Deferrable to slice 4 —
      `proposal-deliberation` is unaffected either way.
- [ ] Change 6 renames: reuse the already-declared-but-never-emitted
      `table_reference`/`figure_reference`, or add `table`/`figure_placeholder`
      and delete the dead pair? Recommendation: add the new names and delete the
      dead pair in the same commit, so the union has no unreachable members.

## Citation Check

Every symbol below was located in the source by name in this phase:
`COMPOSITE_UNTOUCHED_INVARIANT` and `composeSuccessorBlockCandidate`
(`successor-composite-engine.ts`), `compileSuccessorCompositeReplacement` /
`compileSuccessorCompositeChangeset` (`patch-compiler.ts`), `mathDelta` /
`canonicalFormViolations` (`math-integrity.ts`), the `MATH_REMOVALS_NOT_ACKNOWLEDGED`
accept gate (`orchestrator.ts`), `buildStructuralIndex` (`document-index.ts`),
`leaf` (`target-resolver.ts`), `PARSER_VERSION` / `SUPERSEDED_PARSER_VERSIONS` /
`isAcceptedParserVersion` (`types.ts`), `validateStoredState` /
`saveDerivedState` (`derived-state-store.ts`), `renderFromIdea`
(`initial-revision-renderer.ts`), `loadGuideDirectoryFragments` and
`GUIDE_DIRECTORY` (`proposal-workspace.ts`), and the six-test lock. No line
number from `exploration.md` was reused. `REQUIRED_SOURCE_MISSING`,
`SOURCE_AUTHORITY_CONFLICT`, `CHANGE_SUMMARY_REQUIRED` and
`DELIBERATION_DOMAIN_PROFILE_UNSAFE_ARTIFACT_PATH` are absent from core —
correct, they are new.
