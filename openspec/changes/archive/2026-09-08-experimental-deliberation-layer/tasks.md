# Tasks: Generalize the deliberation core for a second domain layer

Both open design questions are resolved by the user. Change 8 = option (b),
own resolved locus, profile-gated, receipt field shipped alongside. Change 9 =
preview-time advisory + `acknowledgedSourceConflicts`, `severity` defaults to
`advisory`. Slice 4 is unblocked.

Every test invocation needs `DELIBERATION_DOMAIN_PROFILE` set:
`DELIBERATION_DOMAIN_PROFILE=$PWD/.claude/skills/proposal-deliberation/profile.ts node --test <files>`.

Strict TDD: every behavioural task is RED (write the failing/characterizing
test, observe it fail or pass-as-baseline) before its GREEN (production
change) task. RED tasks are marked `[RED]`, production tasks `[GREEN]`.

## Review Workload Forecast

Session budget is **1400 changed lines per slice** (per session preflight,
overriding the skill's generic 400-line default).

| Field | Value |
|-------|-------|
| Estimated changed lines | Slice 1 ~650, Slice 2 ~670, Slice 3 ~430, Slice 4 ~460 |
| 1400-line budget risk | Low (all four slices) |
| Chained PRs recommended | Yes — already user-approved |
| Suggested split | PR 1 (Slice 1) → PR 2 (Slice 2) → PR 3 (Slice 3) → PR 4 (Slice 4) |
| Delivery strategy | chained delivery, four slices, user-approved |
| Chain strategy | stacked-to-main (each slice is sequentially dependent: 2 needs 1's lock/naming, 3 needs 1–2, 4 needs 1–3) |

Decision needed before apply: No (chain strategy already user-approved)
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: Low (evaluated against the 1400-line per-slice budget)

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Artifact namespace: changes 1, 2, 3 + extended lock | PR 1 | `node --test tests/proposal-deliberation-domain-profile-lock.test.mjs tests/proposal-deliberation-parser-version-compatibility.test.mjs` | N/A — this engine has no standalone CLI scenario beyond its own test suites; both suites are the runtime harness | Revert slice-1 commits; `artifact-naming.ts` and the lock-test change are net-new/additive, no on-disk artifact exists to migrate back |
| 2 | Structure + preservation: changes 6, 4 | PR 2 | `node --test tests/proposal-deliberation-parser-version-compatibility.test.mjs tests/proposal-deliberation-v2-source-routing.test.mjs` | N/A — same reason | Revert slice-2 commits; `PARSER_VERSION` bump self-invalidates any stale cache, no committed state to migrate back |
| 3 | References + sources: changes 5, 7 | PR 3 | `node --test tests/proposal-deliberation-prose-reference.test.mjs` | N/A — same reason | Revert slice-3 commits; `profile.references`/`profile.sources` are additive profile fields |
| 4 | New mechanics + cleanup: changes 8, 9, 10 | PR 4 | `node --test tests/proposal-deliberation-growth-threshold.test.mjs tests/proposal-deliberation-domain-vocabulary.test.mjs` | N/A — same reason | Revert slice-4 commits; `changeHeader`/`sourceAuthority` are opt-in, undeclared by `proposal-deliberation`, zero residue |

---

## Slice 1 — Artifact Namespace (changes 1, 2, 3 + extended lock)

### Phase 1.1: Foundation — profile artifact contract (change 1)

- [x] 1.1.1 [RED] `domain-profile.ts`: test a profile omitting `artifact.marker` fails startup with an explicit missing-field code (extend `DELIBERATION_DOMAIN_PROFILE_INCOMPLETE`-style check to nested `artifact.*` fields, not just top-level `REQUIRED` membership).
- [x] 1.1.2 [RED] test `artifact.directory`/`sidecarRoot` containing `/` or `..`, or failing `^\.?[A-Za-z0-9._-]+$`, refuses with `DELIBERATION_DOMAIN_PROFILE_UNSAFE_ARTIFACT_PATH`.
- [x] 1.1.3 [RED] test a profile declaring all six `artifact` fields loads successfully.
- [x] 1.1.4 [GREEN] add `artifact: { directory, stem, revisionPattern, revisionLabel, sidecarRoot, marker }` to `DeliberationDomainProfile` in `domain-profile.ts`; add `artifact` to `REQUIRED`; add nested field-presence check; add the path-segment regex validator.
- [x] 1.1.5 Confirm 1.1.1–1.1.3 pass. (`tests/proposal-deliberation-domain-profile-artifact.test.mjs`, 8/8 pass; verified RED via `git stash` of `domain-profile.ts` — 6/8 failed as expected before the GREEN change.)

### Phase 1.2: Core — `artifact-naming.ts` matcher family (change 2)

- [x] 1.2.1 [RED] one test per matcher divergence, both directions: STRICT refuses `…-r1.md`/accepts `…-r02.md`; LAX accepts `…-r1.md` and any lineage chars; LOOSE SCAN is unanchored + case-insensitive; INCREMENT bumps the ordinal; INITIAL matches only `stem-SEG-r01.md`. (`tests/proposal-deliberation-artifact-naming.test.mjs`, 20 tests.)
- [x] 1.2.2 ~~type-level test: `ManagedInitialName`/`ManagedRevisionName` reject an unbranded plain `string` at compile time.~~ **WITHDRAWN, and the reason matters.** It was written as `tests/fixtures/proposal-deliberation-artifact-naming-types.ts` with `@ts-expect-error` annotations, then deleted. This project has NO TypeScript checker at all -- no `tsc`, no `tsconfig.json`, no `typescript` in `node_modules`; TS is executed through jiti, which transpiles and STRIPS types without checking them. So the file sat in `tests/`, was imported by nothing, and had no reachable failure path: a guard that cannot fire reads exactly like a guard that passes. The premise behind branding -- that widening to plain `string` would delete a compile-time check -- is itself false here, because the original literal types were equally unchecked. The branded types are kept as documentation and IDE affordance, NOT as a guard; the real guard for this regression class is the extended domain lock, which does run (proven by mutation M2a). Introducing a genuine `tsc --noEmit` step over ~11k never-checked lines is a separate change, not this one.
- [x] 1.2.3 [GREEN] create `_core/deliberation/engine/artifact-naming.ts`: `SEGMENT`, branded `ManagedRevisionName`/`ManagedInitialName`, `artifact` const, `strictManagedRevision`, `parseManagedRevision`, `parseRevisionIncrement`, `scanManagedRevision`, `isInitialRevision`, `managedRevisionFilename`, `initialRevisionFilename`, `documentPath`, `statePath`, `receiptPath`, `withdrawnMarkerPath`, `publicRelativePaths`, `managedRevisionSchemaPattern`. Also exports `escapedStem`/`escapedRevisionPrefix`/`strictRevisionLabel` (needed by migrated call sites building one-off local patterns) — additive, not in the original list but required to eliminate every remaining hardcoded site.
- [x] 1.2.4 Confirm 1.2.1–1.2.2 pass against the new module. (20/20 runtime tests pass; 1.2.2 unverifiable per the caveat above.)

### Phase 1.3: Migration — 14 hardcoded sites + 3 literal types (change 2)

- [x] 1.3.1 Migrate `orchestrator.ts`: `MANAGED_REVISION_FILENAME` (STRICT, confirmed hardcoded `research-concept` at line 6) → `strictManagedRevision`/`managedRevisionFilename`. Also migrated the inline duplicate STRICT regex at old line 87, `successorFilename`'s bespoke increment regex → `parseRevisionIncrement`, and two `join(this.root,'proposals',...)` sites.
- [x] 1.3.2 Migrate `consistency-audit.ts` (STRICT).
- [x] 1.3.3 Migrate `revision-lifecycle-store.ts` (STRICT `MANAGED` + LAX behind it — preserve LAX-inert-behind-STRICT ordering).
- [x] 1.3.4 Migrate `document-state.ts` — LAX is the **sole** gate on `loadDocumentState`; preserve its exact laxness (`…-r1.md` acceptance), do not tighten it here.
- [x] 1.3.5 De-literalize `revision-domain.ts` and `revision-receipt.ts`: `targetFilename: 'research-concept-r01.md'` literal type → `ManagedRevisionName` (not `ManagedInitialName` — see design deviation note below).
- [x] 1.3.6 De-literalize `proposal-workspace-adapter.ts`: literal-type site + runtime equality → `managedRevisionFilename('ROOT', 1)` (not `isInitialRevision(...)` — see design deviation note below).
- [x] 1.3.7 Migrate `proposal-workspace.ts`: `MANAGED_CHAT_DOCUMENT_FILENAME` (STRICT), successor slug bump (INCREMENT), three JSON-Schema `pattern` strings → `managedRevisionSchemaPattern(opts)`. Also migrated: three more hardcoded naming regexes not named in this task (`MANAGED_TARGET_MARKDOWN`, `MANAGED_REVISION_TARGET_MARKDOWN`, `ROOT_MANAGED_REVISION_TARGET_MARKDOWN`), ~30 more `research-concept`/`proposals` occurrences across refusal prose and tool descriptions (required by the zero-exemption lock — see Phase 1.4 note), and the local `ARTIFACT_MARKER` constant → `DOMAIN.artifact.marker`.
- [x] 1.3.8 Migrate `intent-resolver.ts` (LOOSE SCAN → `scanManagedRevision`). Left `extractRevisionReference`'s bare `r\d{2,}` free-text pattern and `REVISION_REFERENCE` untouched — a sixth, different regex not in the measured five-matcher family and not listed in this task.
- [x] 1.3.9 Migrate `initial-revision-creation.ts` and `initial-revision-renderer.ts` (INITIAL → `isInitialRevision`/`initialRevisionFilename`).
- [x] 1.3.10 Migrate `derived-state-store.ts`, `revision-lifecycle-transaction.ts`, `lifecycle-state-store.ts` to import names from `artifact-naming.ts`. Also migrated `draft-materialization.ts`, `smoke-runner.ts`, `chat-draft-registry.ts`, and `cli.mjs` (a `.mjs` core file the lock also scans) — none named in this task, all required for the zero-exemption lock to pass.

**Design deviation (1.3.5/1.3.6), reported not hidden**: design.md's own matcher-family table defines INITIAL as requiring a MANDATORY lineage segment (`stem-SEG-r01.md` only — task 1.2.1 requires a test proving this), matching the one real INITIAL call site (`initial-revision-creation.ts`'s `MANAGED_INITIAL_REVISION_FILENAME`). But `revision-domain.ts`/`revision-receipt.ts`/`proposal-workspace-adapter.ts`'s literal `'research-concept-r01.md'` is the BARE-ROOT form (no lineage) used by a separate, distinct "scientific workflow" bootstrap route (`InitialRevisionCreationService` is unrelated). `ManagedInitialName`/`initialRevisionFilename()` cannot correctly represent this ROOT-only shape without contradicting the INITIAL semantic the tests require. Resolved by branding these three sites `ManagedRevisionName` (STRICT-based, ROOT-inclusive) via `managedRevisionFilename('ROOT', 1)` instead — same de-literalization goal (a TypeScript literal cannot depend on a runtime profile value), correct semantics, deviates from the literal instruction wording.

### Phase 1.4: Namespace routing — `proposals/` and `.proposal-deliberation/` (change 3)

- [x] 1.4.1 Triage task: `rg -n "proposals/"` across the 10 affected files; classify every one of the ~73 occurrences as path-construction vs. refusal-prose/MCP-schema-description (~35); write the classified list before editing any file. **Finding that overrode this task's own guidance**: the extended lock (Phase 1.5) scans for the literal `directory` value ("proposals") as a case-sensitive substring anywhere in core, INCLUDING inside prose/comments/tool-description strings — it cannot distinguish "path construction" from "prose". Every prose occurrence of the bare word "proposals" (and "research-concept") in core therefore also had to be migrated (interpolated via template literal), not left untouched, or the lock cannot pass. ~35 "prose" sites were migrated for lock compliance; genuinely inert text with no variable interpolation (e.g. "the derived staging file changed before publication") was left alone where it contained neither literal.
- [x] 1.4.2 [RED] test sidecar root changes with the profile: a profile declaring `sidecarRoot: ".other-deliberation"` writes state/receipts/withdrawn sidecars there, never under `.proposal-deliberation/`. (`tests/proposal-deliberation-sidecar-root-routing.test.mjs`; verified RED via `git stash` of `derived-state-store.ts`+`initial-revision-creation.ts`+`domain-profile.ts`.)
- [x] 1.4.3 [GREEN] route only the path-construction sites from 1.4.1 through `profile.artifact.directory`/`sidecarRoot`; leave prose/schema-description strings untouched. (Superseded per the 1.4.1 finding above: prose sites containing the literal values were also migrated, for lock compliance. Pure schema `description:` text with no literal artifact value was left untouched.)
- [x] 1.4.4 Confirm 1.4.2 passes; confirm the unsafe-path validation from 1.1.4 actually gates this routing (change 3 turns a sandbox root into a profile value — `REQUIRED`-membership alone is not safety).

### Phase 1.5: Extended domain lock (same work unit as change 2)

- [x] 1.5.1 [RED] write the new lock test "no file in the shared core spells the artifact namespace": a **second, core-only** scan surface reading `artifact.{stem, directory, sidecarRoot}` off `profile.ts`, zero exemptions. Declare `sidecarRoot` **with its leading dot** (`.proposal-deliberation`) so the bare word `proposal-deliberation` — legitimate in `PARSER_VERSION`, `sdd/proposal-deliberation-*` citations, `Symbol.for('papersmith-ai.proposal-deliberation…')`, `proposal-deliberation-${uuid}` — does not false-positive. **Found and fixed a genuine gap in this exact design claim**: `chat-draft-registry.ts`'s pre-existing `Symbol.for('papersmith-ai.proposal-deliberation.pi-session-draft-registry/v1')` DOES contain the dot-prefixed substring (the namespace convention's own dot coincides with `sidecarRoot`'s leading dot), so it was NOT safe as design assumed. Changed the registry key's separator from `.` to `:` (an opaque `Symbol.for` key, behaviorally identical, no external reference to the old string existed).
- [x] 1.5.2 Leave the existing suite-wide scan's four `declared` values + `names` unchanged; do **not** add `stem`/`directory` to that list (would flag legitimate node fixtures writing real `proposals/research-concept-…` files).
- [x] 1.5.3 Confirm the new lock test goes RED against any hardcoded site still remaining from Phase 1.3, then GREEN once Phase 1.3 is complete. (Genuinely observed red twice during migration: once against `cli.mjs`'s hardcoded `'proposals'`/`'research-concept-r03.md'` comment and a `proposalsDir` variable name, once against a leftover in `revision-lifecycle-store.ts`; both fixed and reverified green.)

### Phase 1.6: Mutation proof (slice ends here)

- [x] 1.6.1 **M2a** — record `rg -c 'research-concept' orchestrator.ts` (expect 0, post-migration) → re-hardcode `MANAGED_REVISION_FILENAME`'s literal in `orchestrator.ts` → assert count 0→1 → run the new lock test (1.5.1), confirm it fails naming `orchestrator.ts` and the literal `research-concept` → clear transform cache → run both suites, record failing test names/assertions → revert → re-baseline both suites. **Result**: count 0→1 confirmed; lock test failed with `orchestrator.ts spells "research-concept"`; both suites re-baselined clean after revert (417/417 node, 2718 OK python).
- [x] 1.6.2 **M2b** — record `rg -c '\d+' artifact-naming.ts` (baseline N) → tighten `parseManagedRevision`'s ordinal group from `\d+` to `\d{2,}` (collapses LAX into STRICT) → assert count N→N−1 → confirm the new test "`loadDocumentState` accepts `…-r1.md` while `strictManagedRevision` refuses it" (from 1.2.1) goes red → clear cache → run both suites, record failing names → revert → re-baseline. **Result**: baseline N=2 → 1 confirmed; exactly 3 tests failed (`LAX accepts a one-digit revision ordinal that STRICT refuses`, `LAX accepts ANY lineage character...`, `loadDocumentState accepts a filename LAX allows but STRICT refuses (…-r1.md)`); both suites re-baselined clean after revert.

### Phase 1.7: Verification

- [x] 1.7.1 `npm test` → 386 pass / 0 fail baseline holds; grew to 418 pass / 0 fail (32 new tests added by this slice: 8 + 20 + 2 in new files, + 2 in the extended lock file = 32; 386 + 32 = 418).
- [x] 1.7.2 `.venv/bin/python -m unittest discover -s tests` → Ran 2718, OK (skipped=6). **Found and fixed a real cross-suite regression**: `test_the_marker_is_the_one_the_publisher_writes` reads `revision-lifecycle-store.ts`'s `MARKER` constant by regex as the canonical source of truth against an independent Python re-implementation. Reverted only that one site's `MARKER` back to its literal `Buffer.from(...)` form (marker is deliberately NOT one of the lock's three scanned values, so this does not reopen the lock) with a comment explaining why.

---

## Slice 2 — Structure + Preservation (changes 6, 4)

### Phase 2.1: Structural entries — retyping, not additive (change 6)

- [x] 2.1.1 [RED] test `buildStructuralIndex` is byte-identical on a document with no tables/figures (regression baseline against current index — confirmed today: only `document`,`section`,`subsection`,`heading`,`display_equation`,`paragraph` are emitted; `types.ts` already declares unused `table_reference`/`figure_reference`).
- [x] 2.1.2 [RED] test a GFM table resolves to its own `table` entry (not `paragraph`/`section`) — fails today.
- [x] 2.1.3 [RED] test a declared figure placeholder resolves to its own `figure_placeholder` entry — fails today.
- [x] 2.1.4 [RED] test the ambiguity gate, given two tables under one heading and an under-specified query, still refuses correctly and can now list both `table` candidates by identity.
- [x] 2.1.5 [GREEN] `types.ts`: add `table` and `figure_placeholder` to `EntryType`; **delete** the unreachable `table_reference`/`figure_reference` pair in the same commit (per spec's mandated names and design's recommendation — no unreachable union members).
- [x] 2.1.6 [GREEN] `types.ts`: bump `PARSER_VERSION`; do **not** add the old version to `SUPERSEDED_PARSER_VERSIONS` — this is a retyping (changed `entryId`s), not a same-parse-output supersession; `saveDerivedState` in `derived-state-store.ts` must throw `INCOMPATIBLE_COMMITTED_STATE` for a COMMITTED state that now re-serializes differently. (Extra, user-mandated coverage: two dedicated tests in `proposal-deliberation-structural-entries.test.mjs` prove both halves — a stale prior version is invalidated/rebuilt, never thrown on; a same-version re-serialization mismatch DOES throw `INCOMPATIBLE_COMMITTED_STATE`.)
- [x] 2.1.7 [GREEN] `document-index.ts`: implement GFM table + figure-placeholder recognition in `buildStructuralIndex`.
- [x] 2.1.8 [GREEN] `target-resolver.ts`: add `table` and `figure_placeholder` to the `leaf()` list (currently `['display_equation','paragraph','inline_math_region','list','code_block','definition','theorem','algorithm']` — confirmed missing both). A missed addition here loses table bytes from composite materialization **with no test failing today**.
- [x] 2.1.9 [RED] integration test: a section containing a GFM table still materializes the table's bytes under composite materialization.
- [x] 2.1.10 Confirm 2.1.2–2.1.4, 2.1.9 pass; confirm 2.1.1's snapshot still holds (additive guarantee for table-free documents). (`tests/proposal-deliberation-structural-entries.test.mjs`, 7/7 pass.)

### Phase 2.2: Preservation gate — domain-neutral (change 4)

- [x] 2.2.1 [RED — characterization, write FIRST, before any change-4 production edit] the missing test: publishing a `CREATE_SUCCESSOR` with a genuinely lost atom and no acknowledgement is refused with `MATH_REMOVALS_NOT_ACKNOWLEDGED` (confirmed absent today — `orchestrator.ts` line 252 is the only site naming it; `tests/proposal-deliberation-v2-source-routing.test.mjs:252` only exercises the acknowledged path). Run against **current, pre-refactor** `orchestrator.ts` and observe it **pass** — this is the baseline change 4 must not break. (Verified pass against unrefactored orchestrator.ts before any change-4 edit.)
- [x] 2.2.2 [RED] test `profile.preservation.{extractAtoms, violations}` wired to `preservation-math.ts` reproduces byte-identical atoms/deltas/violations for the mathematical profile.
- [x] 2.2.3 [RED] test empty extraction (zero atoms) is reported "not applicable", a distinct shape from a genuine pass with atoms confirmed intact.
- [x] 2.2.4 [RED] test legacy input alias `acknowledgedMathRemovals` is treated identically to `acknowledgedRemovals`.
- [x] 2.2.5 [RED] test a preview response includes both `mathDelta` and `preservationDelta`, populated identically.
- [x] 2.2.6 [GREEN] rename `math-integrity.ts` → `preservation.ts`; make `atoms`/`delta`/`violations` neutral, sourced from `profile.preservation.{extractAtoms, violations}`.
- [x] 2.2.7 [GREEN] create `.claude/skills/proposal-deliberation/preservation-math.ts` (the math extractor + rule set), wired through `proposal-deliberation/profile.ts`.
- [x] 2.2.8 [GREEN] implement the distinct not-applicable reporting shape for zero-atom extraction. (`validation.preservationApplicable`, a sibling boolean field, never folded into the `{lost,added}` delta shape itself so `preview.mathDelta.lost.map(...)` keeps working unchanged.)
- [x] 2.2.9 [GREEN] implement `mathDelta`/`acknowledgedMathRemovals` as **permanent** accepted aliases for `preservationDelta`/`acknowledgedRemovals`, both input and output directions.
- [x] 2.2.10 Confirm 2.2.1's characterization test still passes unchanged after the refactor (gate behavior preserved through the rename).

### Phase 2.3: Mutation proof (slice ends here)

- [x] 2.3.1 **M4a** — record `rg -c 'unacknowledged.length' orchestrator.ts` (expect 1) → mutate the accept gate so `unacknowledged.length` reads as `false` → assert count 1→0 → confirm the new characterization test (2.2.1) goes red → clear cache → run both suites, record failing test name/assertion → revert → re-baseline. **Result**: count 1→0 confirmed; exactly 2 node tests failed (`2.2.1 ... MATH_REMOVALS_NOT_ACKNOWLEDGED` and `2.2.10 ...refactor`), both asserting `actual 'published' !== expected 'blocked'`; reverted and re-baselined clean (431/431).
- [x] 2.3.2 **M4b** — record `rg -c 'acknowledgedMathRemovals' orchestrator.ts` (expect ≥1) → drop the alias read → assert count ≥1→0 → confirm `tests/proposal-deliberation-v2-source-routing.test.mjs` (sends the old field name) goes red → clear cache → run both suites, record failing test → revert → re-baseline. **Result**: count 2→0 confirmed; exactly 2 node tests failed (`2.2.4 legacy input alias...` and `explicit CREATE_SUCCESSOR overrides recupera r02...` in `proposal-deliberation-v2-source-routing.test.mjs`), both asserting `actual 'blocked' !== expected 'published'`; reverted and re-baselined clean (431/431).

### Phase 2.4: Verification

- [x] 2.4.1 `npm test` → 431 pass / 0 fail (418 slice-1 baseline + 13 new tests: 7 structural-entries + 6 preservation-gate).
- [x] 2.4.2 `.venv/bin/python -m unittest discover -s tests` → Ran 2718, OK (skipped=6) — unchanged, confirming this slice touches no Python-visible surface.

---

## Slice 3 — References + Sources (changes 5, 7)

### Phase 3.1: Reference integrity (change 5)

- [x] 3.1.1 [RED] test math-profile behavior preserved byte-identical, with `profile.references.declares = '\tag{N}'`-equivalent and `cites = '(Ec. N)'`-equivalent. **Scope decision, reported not hidden**: `declares`/`cites` were generalized to cover ALL FOUR previously-hardwired forms (`\label`+`\tag` as `declares`, `\eqref`/`\ref`+`(Ec. N)` as `cites`), not only the tag/Ec.N pair named in this task's own wording — required because 3.1.6 explicitly lists eliminating `\label` and `\eqref`/`\ref` hardcoding too, and both must route through the same profile field to avoid a second, divergent source of truth. (`tests/proposal-deliberation-reference-integrity.test.mjs`, verified RED via a bare `node --test` run before the domain-profile.ts/reference-index.ts/document-index.ts/candidate-validator.ts changes existed — all 4 new tests failed as expected: `TypeError: checkReferenceIntegrity is not a function` / `referencesApplicable` undefined.)
- [x] 3.1.2 [RED] test a genuine unresolved citation is caught, using a fixture in a **non-mathematical** vocabulary shape (per Acceptance Criteria — the check must be proven beyond the math profile's own tests). A hand-built `{declares,cites}` pair (`[Table T1]` / `see Table T1`) is passed directly to the new exported `checkReferenceIntegrity(source, references)`, decoupled from the live `DOMAIN` singleton the whole test run fixes to the mathematical profile via `DELIBERATION_DOMAIN_PROFILE`.
- [x] 3.1.3 [RED] test empty `declares`/`cites` is reported "not applicable", distinct from a confirmed-consistent pass. Both the generic `checkReferenceIntegrity(...).applicable` and the full-pipeline `validateCandidate(...).referencesApplicable` (a sibling boolean, never folded into the `references`/`declarations` booleans themselves) are asserted.
- [x] 3.1.4 [RED] test a duplicate declaration is still caught, generalized to the profile vocabulary. Both the generic non-math case and a math-profile duplicate-`\tag{1}` case (via `validateCandidate`) are asserted.
- [x] 3.1.5 [GREEN] add `profile.references.{declares, cites}` to `domain-profile.ts`; wire `proposal-deliberation/profile.ts` with today's `\tag{N}`/`(Ec. N)` vocabulary (plus `\label`/`\eqref` per the 3.1.1 scope decision above). Shipped as `.claude/skills/proposal-deliberation/reference-math.ts`, mirroring `preservation-math.ts`'s idiom exactly (lazy `proseReference` read to avoid the load-order race).
- [x] 3.1.6 [GREEN] replace the hardwired `\label`/`\tag`/`\eqref`/`(Ec. N)` checks in `candidate-validator.ts`, `reference-index.ts`, `document-index.ts` with `profile.references` lookups. `document-index.ts` still tracks the two declaration kinds by the literal names `"label"`/`"tag"` for locus-lookup compatibility (`target-resolver.ts`, explicitly out of this task's file list and left untouched) — documented in-line as a residual, intentional coupling; the reference-INTEGRITY check itself (`checkReferenceIntegrity`) is fully vocabulary-agnostic and does not go through that split. `candidate-validator.ts`'s call to `buildReferenceIndex` was dead code before this change (its result was computed and never read) — removed rather than preserved unused, replaced by direct `declaredValues`/`citedValues` calls; `validationTask` call count was kept at 11 (`>=9` floor from `tests/proposal-deliberation-v2-parallelism.test.mjs`, group sizes unchanged at the `maxParallelValidationTasks:6` boundary).
- [x] 3.1.7 [GREEN] implement the not-applicable distinct reporting shape for empty `declares`/`cites`. `referencesApplicable` ships as a top-level sibling field on the `validateCandidate` result (same placement as slice 2's `preservationApplicable`), never merged into the `results.references`/`results.declarations` booleans.
- [x] 3.1.8 Confirm 3.1.1–3.1.4 pass. (`tests/proposal-deliberation-reference-integrity.test.mjs`, 4/4 pass.)

### Phase 3.2: Required sources (change 7)

- [x] 3.2.1 [RED] test a declared, present source loads its fragments exactly as today. Exercised against the DEFAULT math profile (no custom profile needed — its one declared source, `guidance/paper-guide`, is already `required:false`); this test was already GREEN under the pre-change hardcoded `GUIDE_DIRECTORY` path, since it asserts unchanged behavior, not a new refusal — kept as a characterization guard, same idiom as 2.2.1.
- [x] 3.2.2 [RED] test a missing `required: true` source refuses `CREATE_INITIAL_REVISION` with `REQUIRED_SOURCE_MISSING`; no v1 is created. A FRESH child process spawns with a custom profile declaring one `required:true` source (the same `DELIBERATION_DOMAIN_PROFILE`-is-read-once-per-process technique `proposal-deliberation-sidecar-root-routing.test.mjs` already uses), exercising the FULL `proposal_deliberation_execute` tool route (not the lower-level `InitialRevisionCreationService` alone, since the refusal lives in `proposal-workspace.ts`'s `CREATE_INITIAL_REVISION` route handler). Verified RED: failed with `actual 'created' !== expected 'blocked'` before the domain-profile.ts/proposal-workspace.ts changes existed.
- [x] 3.2.3 [RED] test an absent `required: false` source (proposal-deliberation's `guidance/paper-guide`) preserves today's silence — v1 renders, no fragments, no refusal. Same characterization-guard idiom as 3.2.1 (already GREEN pre-change; this is the direction the hazard note warned must not go untested).
- [x] 3.2.4 [RED] test two sources, one `required: true` (absent) and one `required: false` (present): `CREATE_INITIAL_REVISION` fails with `REQUIRED_SOURCE_MISSING` regardless of the second. Same fresh-process technique as 3.2.2. Verified RED the same way.
- [x] 3.2.5 [GREEN] add `profile.sources: readonly { path, required }[]` to `domain-profile.ts`; added to `REQUIRED` (top-level presence only, matching the `preservation`/`references` precedent — no nested per-entry validation).
- [x] 3.2.6 [GREEN] update the fragment loader (`loadGuideDirectoryFragments`/`GUIDE_DIRECTORY` in `proposal-workspace.ts`) to read `profile.sources` instead of the single hardcoded `GUIDE_DIRECTORY` path. The `GUIDE_DIRECTORY` constant itself is left in place and unchanged: it also backs the unrelated, out-of-scope `authorizeGuide`/guide-inventory read tool (a "read a guide by exact filename" action, not the initial-context fragment loader), which task 3.2's file list does not name.
- [x] 3.2.7 [GREEN] implement the `REQUIRED_SOURCE_MISSING` refusal in `CREATE_INITIAL_REVISION` for any `required: true` + absent source. New `missingRequiredSources()` helper, checked before `loadGuideDirectoryFragments` and before `initialRevisionCreation.execute` — no v1 is rendered when it is non-empty.
- [x] 3.2.8 [GREEN] wire `proposal-deliberation/profile.ts` to declare `guidance/paper-guide` with `required: false`.
- [x] 3.2.9 Confirm 3.2.1–3.2.4 pass. (`tests/proposal-deliberation-required-sources.test.mjs`, 4/4 pass.)

### Phase 3.3: Verification

- [x] 3.3.1 `npm test` → 386 pass / 0 fail baseline holds; grew to 439 pass / 0 fail (431 slice-2 baseline + 8 new tests: 4 `proposal-deliberation-reference-integrity.test.mjs` + 4 `proposal-deliberation-required-sources.test.mjs`; 431 + 8 = 439).
- [x] 3.3.2 `.venv/bin/python -m unittest discover -s tests` → Ran 2718, OK (skipped=6) — unchanged, confirming this slice touches no Python-visible surface.

---

## Slice 4 — New Mechanics + Cleanup (changes 8, 9, 10)

### Phase 4.1: Change-header contract — option (b), profile-gated (change 8)

- [x] 4.1.1 [RED] test `CREATE_SUCCESSOR` omitting `changeSummary`, when `profile.artifact.changeHeader` is declared, is refused `CHANGE_SUMMARY_REQUIRED`, no successor published. (`tests/proposal-deliberation-change-header.test.mjs`, fresh-process custom profile.)
- [x] 4.1.2 [RED] test a present `changeSummary: {what, why}` publishes, carrying the content.
- [x] 4.1.3 [RED] test the header locus is its own resolved block span, satisfying `COMPOSITE_UNTOUCHED_INVARIANT` because the invariant walks only the **gaps between edit spans plus the tail** (confirmed in `successor-composite-engine.ts`) — a span-internal header is inside the union, not exempted. Proven by a passing `published.status==='published'` (the composite engine's own `COMPOSITE_UNTOUCHED_INVARIANT` check would have thrown otherwise) plus an explicit byte comparison that the title text survives untouched into r02.
- [x] 4.1.4 [RED] test invariant enforcement is byte-identical when `changeHeader` is undeclared — `proposal-deliberation` publishes nothing new. Run directly under the normal math profile (no fresh process needed): `resolvedTargets.length===1`, `growthAdvisory===undefined`, no `changeSummary` key on the receipt.
- [x] 4.1.5 [RED] edge case: a `\command`-shaped token inside a previous header, once replaced, registers correctly as a lost macro atom via `preservationDelta`. Two tests: the unacknowledged case still blocks `MATH_REMOVALS_NOT_ACKNOWLEDGED` (4.1.5), acknowledging it publishes (4.1.5b) — proving the mechanism is load-bearing, not just detected.
- [x] 4.1.6 [GREEN] add optional `profile.artifact.changeHeader?: { heading: string; render(s: {what, why}): string }` to `domain-profile.ts` — **not** added to `REQUIRED`.
- [x] 4.1.7 [GREEN] `initial-revision-renderer.ts`: `renderFromIdea` emits the header section into v1 only when `changeHeader` is declared (zero migration — the managed directory holds only `.gitkeep`). Imports `DOMAIN` directly, following the same idiom `document-index.ts`/`target-resolver.ts`/`orchestrator.ts` already established for other profile-neutral concerns.
- [x] 4.1.8 [GREEN] `CREATE_SUCCESSOR`: require `changeSummary` and refuse `CHANGE_SUMMARY_REQUIRED`, gated on `profile.artifact.changeHeader` presence. Checked once, early in `execute()`, uniformly across the single-target, multi-section and ambient-composite dispatch paths (skipped on the accept turn, `request.acceptSuccessor===true`).
- [x] 4.1.9 [GREEN] append **one** engine-owned `replace` block over the header entry to the plan (resolver still never invents targets; the engine already chooses `successorFilename` the same way). Implemented at the top of `publish()`, gated on `operation===CREATE_SUCCESSOR && !frozenCompiled && DOMAIN.artifact.changeHeader` — `!frozenCompiled` deliberately excludes the ambient-composite path (SLICE 1b, orthogonal to this change; a `changeSummary`-bearing ambient-decisions CREATE_SUCCESSOR is accepted by the required-gate but the header is not injected on that path — a documented, untested scope limitation, not a correctness bug). New `changeHeaderLocusCandidate` exported from `target-resolver.ts`, reusing the file's own `compositeCandidate` builder. **Design deviation, found and fixed**: `acceptFrozenSuccessor`'s stale-source re-validation compared the accept turn's freshly re-resolved targets' length/order against the frozen preview's `compositeTargetIds`/`resolvedTargets` — since those now carry one MORE (header) id than the re-resolved targets array, every accept turn would have failed `SUCCESSOR_ACCEPTANCE_STALE_SOURCE` for any changeHeader-declared profile. Fixed by re-deriving the same expected header id fresh from the accept-turn `state` (protected by the existing `sourceSha256` equality check) before comparing.
- [x] 4.1.10 [GREEN] extend `createRevisionReceipt` to carry `changeSummary` (~10 lines) — the receipt chain is where full header history lives since (b) overwrites the previous header in the `.md`. `RevisionReceipt` type gains an optional `changeSummary` field in `types.ts`; the orchestrator's receipt-construction call site adds it only when both `DOMAIN.artifact.changeHeader` and `request.changeSummary` are present.
- [x] 4.1.11 [RED+GREEN] `operation-spec.ts`: `successorTargetCount`/`EffectiveProfileInput` budget accounts for the header locus as an additional resolved target when `changeHeader` fires. Satisfied by construction (header injection happens before `resolveEffectiveOperationProfile` runs inside `publish()`); tested by calling `resolveEffectiveOperationProfile` with the real `preview.plan.resolvedTargets.length` (2) and asserting `maxModelCalls===2`/`maxPatchCount===2`.
- [x] 4.1.12 [RED+GREEN] `growth-threshold.ts`: verdict accounts for the header locus's contribution to document growth -- and design.md's own blast-radius note is explicit the advisory must NOT count the header as an approved section. Implemented by feeding `evaluateSuccessorGrowthThresholdFromTargets` only `[target]` (the real, pre-header target), never the header; extended the (previously ambient-only) `growthAdvisory` computation to also fire for a changeHeader-declared profile on the plain successor path, giving a real integration point to test. Test asserts `preview.growthAdvisory` deep-equals a verdict computed directly from ONLY the real target's byte span (independently recomputed from `preview.compiled.patches`, never a separate re-materialized `loadDocumentState` call, since composite entries are never persisted to the derived-state cache).
- [x] 4.1.13 [RED+GREEN] `successor-acceptance-registry.ts`: `compositeTargetIds` includes the header entry id. Satisfied by construction (`compositeTargetIds:[...planned.plan.resolvedTargets]`, already extended); tested via `published.receipt.resolvedEntryIds.length===2` and `.includes(headerEntryId)`.
- [x] 4.1.14 [RED+GREEN] the arity guards `SUCCESSOR_EXACTLY_ONE_REPLACE_REQUIRED`/`SUCCESSOR_COMPOSITE_TARGET_REQUIRED` (confirmed present in `patch-compiler.ts`, `context-builder.ts`, `conceptual-planner.ts`) and the receipt's `resolvedEntryIds` recount correctly with the extra header block. Header injection happens AFTER `buildEditPlan`/`buildConceptualPlan` already validated the MODEL's own single-locus output against these guards, so they are unaffected; `compileSuccessorCompositeReplacement`'s own `actions.length===resolvedTargets.length` check is what sees the extended plan, satisfied by construction since both arrays grow together. Tested end-to-end via a CONCEPTUAL_REVISION CREATE_SUCCESSOR (4.1.15) that also carries the header through to a full publish.
- [x] 4.1.15 Confirm 4.1.1–4.1.5 pass; confirm `proposal-deliberation` (no `changeHeader` declared) is byte-identical. All pass; `proposal-deliberation`'s own 439-pass baseline (slice 3) is unaffected — see 4.4.

### Phase 4.2: Source authority — advisory + acknowledgement (change 9)

- [x] 4.2.1 [RED] test `proposal-deliberation` (no `sourceAuthority` declared) never raises `SOURCE_AUTHORITY_CONFLICT`, regardless of candidate content. Run directly against `validateCandidate` under the normal math profile with adversarial content (`VALUE: 999, exceeds every plausible bound`); `sourceAuthorityConflicts` is always `[]`.
- [x] 4.2.2 [RED] test a declared bound source's contradicting evidence is detected and surfaced as a **preview-time advisory** `SOURCE_AUTHORITY_CONFLICT`, identifying the contradicting claim and the bound source. (Renamed "ceiling" to "bound" throughout the implementation and this note: `tests/forge_vocabulary.py`'s `FORGE_TARGET_DOMAIN_WORDS` reserves the literal word "ceiling" for a target's own vocabulary and scans every shipped `.claude/skills/` file for it — caught by the full Python suite, fixed by rewording, not by weakening the guard.)
- [x] 4.2.3 [RED] test non-contradicting evidence against the same bound source raises nothing.
- [x] 4.2.4 [RED] test `acknowledgedSourceConflicts` on accept clears the advisory, mirroring the preservation-gate acknowledgement pattern. Two rounds: an unacknowledged accept still blocks `SOURCE_AUTHORITY_CONFLICT` (fresh acceptance token consumed either way), a second fresh round echoing the conflict id back publishes.
- [x] 4.2.5 [RED] test `profile.sourceAuthority.severity: 'refuse'` hard-blocks publish instead of advising (opt-in, not the default). Blocks at PREVIEW time already (never offers an acceptance token), unlike the advisory path.
- [x] 4.2.6 [GREEN] add optional `profile.sourceAuthority: { names: readonly string[]; detectConflicts; severity?: 'advisory' | 'refuse' }` (default `'advisory'`) to `domain-profile.ts` — off by default, not in `REQUIRED`. **Design addition beyond the task's own wording**: `detectConflicts` (a pure function of the candidate's full document text, self-contained domain knowledge exactly parallel to `preservation.extractAtoms`) was added because "detection" needs a concrete mechanism and the design explicitly rejected engine-level file I/O to re-read a loaded source at validate time — `names` stays purely for identification/reporting in a surfaced conflict.
- [x] 4.2.7 [GREEN] implement bound-source contradiction detection + preview-time advisory reporting + `acknowledgedSourceConflicts` accept-gate. `candidate-validator.ts` computes `sourceAuthorityConflicts` (always `[]` when undeclared) as a sibling field, never folded into `ok`; the orchestrator's accept-gate mirrors the preservation gate's exact preview/accept split.
- [x] 4.2.8 [GREEN] implement the `severity: 'refuse'` hard-block path. Checked before the preview/accept branch entirely, so it fires on EITHER turn, never offering acknowledgement.
- [x] 4.2.9 Confirm 4.2.1–4.2.5 pass; confirm `proposal-deliberation` is unaffected. All pass; `proposal-deliberation` declares no `sourceAuthority` (untouched by this phase).

### Phase 4.3: Cleanup (change 10)

- [x] 4.3.1 [RED] test `intent-resolver.ts`, scanned for the string literals `'sparse'`/`'dispers'`, contains neither as a core-level unconditional term.
- [x] 4.3.2 [RED] test (opted in) a `profile.vocabulary` entry equivalent to today's `requestedEffect` fallback preserves identical resolution for math content. Run directly under the normal math profile (already opted in): both "sparse" and "dispersa" instructions still resolve `requestedEffect: 'representación sparse'`; a non-matching instruction resolves `undefined`.
- [x] 4.3.3 [GREEN] delete the `'sparse'`/`'dispers'` literal from `intent-resolver.ts`; add the optional `profile.vocabulary.requestedEffect?: {terms, label}` opt-in mechanism.
- [x] 4.3.4 [GREEN] decide and record whether `proposal-deliberation` opts in (4.3.2) or accepts the drop (acceptable per spec — nothing downstream reads `requestedEffect` except the conceptual plan's `scientificGoal` fallback); wire accordingly. **Decision: opts in**, with the exact same terms/label, preserving today's behavior byte-for-byte — "sparse"/"dispersed" representations are plausibly still this domain's own subject (regularisation, one-hot encoding), so silently dropping a real signal was judged the worse default; recorded inline in `profile.ts`.
- [x] 4.3.5 Confirm 4.3.1 (and 4.3.2, opted in) pass. A third test (`tests/proposal-deliberation-requested-effect.test.mjs`) additionally proves the OPPOSITE choice — a profile declaring no `vocabulary.requestedEffect` at all — leaves `requestedEffect` simply absent, per the spec's third acceptable scenario. **Hazard avoided, reported not hidden**: a filename this task's own suggested-work-units table proposed (`proposal-deliberation-domain-vocabulary.test.mjs`) already belonged to a genuinely unrelated, pre-existing suite (pinning `DOMAIN.vocabulary.subjectTerms`/`expertPattern`/display-noun reading from an earlier phase) — an early `Write` briefly overwrote it; caught via `git status` showing it as modified rather than untracked, restored byte-for-byte from `HEAD` via `git show`, and this phase's three tests shipped under the distinct name above instead.

### Phase 4.4: Verification

- [x] 4.4.1 `npm test` → 386 pass / 0 fail baseline holds; grew to 453 pass / 0 fail (439 slice-3 baseline + 14 new: 6 `proposal-deliberation-change-header.test.mjs` + 5 `proposal-deliberation-source-authority.test.mjs` + 3 `proposal-deliberation-requested-effect.test.mjs`).
- [x] 4.4.2 `.venv/bin/python -m unittest discover -s tests` → Ran 2718, OK (skipped=6) after fixing the "ceiling"→"bound" rewording caught by the forge's own target-vocabulary guard (`tests/forge_vocabulary.py`/`test_proposal_implementation.py`) — an existing, unrelated guard this slice's own comments tripped, not a defect in this change's design.

---

## Verification Inherited By Every Slice

- `npm test` → 386 pass / 0 fail baseline must hold.
- `.venv/bin/python -m unittest discover -s tests` → Ran 2718, OK (skipped=6) must hold. Use `.venv/bin/python`, never bare `python3` (3.9, incompatible).
- Both suites, every slice — running only one has hidden a regression in this repo before.
- A vacuous pass counts as a failure: a check with nothing to check reports "not applicable", never "pass".

## Out of Scope

The experimental-deliberation skill itself; any edit to `proposal-deliberation`'s SKILL.md or published bytes; any stage/pipeline sequencer; any unified "verify" across domains.
