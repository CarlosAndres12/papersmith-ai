# Exploration — a second deliberation domain over the shared core

Measured against `_core/deliberation/engine` (55 files, 10 925 lines) and
`.claude/skills/proposal-deliberation` (4 files, 610 lines) at branch
`experimental-deliberation`. Baseline:
`tests/proposal-deliberation-domain-profile-lock.test.mjs` is 6/6 green.

## 1. What the core already governs

| Concern | Where | Domain-neutral today? |
| --- | --- | --- |
| Revision identity, lineage, `rNN` ordering | `document-state.ts`, `revision-lifecycle-store.ts` | Shape yes, **naming no** |
| Byte-exact patching, unchanged-byte coverage | `patch-compiler.ts` | Yes |
| Structural index (headings → entries → byte spans) | `document-index.ts` | Mostly |
| Locus resolution + ambiguity refusal | `target-resolver.ts`, `ambiguity-gate.ts` | Via profile |
| Preview → acceptance token → publish | `orchestrator.ts`, `successor-acceptance-registry.ts` | Yes |
| Transactional publish, receipts, self-audit | `revision-lifecycle-transaction.ts`, `consistency-audit.ts` | Shape yes, **paths no** |
| Growth advisory (>4 sections / >40 % bytes) | `growth-threshold.ts` | Yes |
| Candidate validation verdict | `candidate-validator.ts` | Shape yes, **checks no** |

The extension point is `domain-profile.ts`: `DELIBERATION_DOMAIN_PROFILE` names an
absolute module exporting `profile`. No default, fails closed. A skill is
`profile.ts` + a 13-line `cli.mjs`.

## 2. Classified inventory

Everything in `proposal-deliberation` that is not in core, one row per item.

### Bucket A — Promote to core (general mechanics that stayed up only because there was one consumer)

| Item | Where it lives now | Why it is general |
| --- | --- | --- |
| **A1. Base-version decision tree** (7 branches over `STATUS`: `LATEST` / `OLDER_MANAGED` / `UNMANAGED` / no-managed-revision cases) | SKILL.md prose | Nothing in it is mathematical. Any domain with versioned managed artifacts needs the same classification and the same "ask, never guess" rule. `STATUS` already computes the classification; only the branching is prose. |
| **A2. Backup-and-audit reconciliation protocol** (`backup/proposals/<ts>/`, move sidecars together, then require `consistency-audit` PASS) | SKILL.md prose | The failure it prevents — orphaned `state/` + `receipts/` sidecars that `STATUS` reports as healthy — is a property of the sidecar layout, which is core's. |
| **A3. Round-closing criterion** | `growth-threshold.ts` (already core) + SKILL.md restatement | Already core. Only the *restatement* is duplicated in the skill; the skill copy should cite it, not re-declare 4 / 40 %. |
| **A4. "Resolve, never invent" contract** (`RESOLVE_TARGET` first; the query-writing rules: heading words only, no punctuation, accent-sensitive, remove words when blocked) | SKILL.md prose | These are properties of `target-resolver.ts`'s scorer and `ambiguityGate`'s shared-term hint, not of mathematics. Any domain writing queries against the same scorer needs the identical advice. |
| **A5. Engine-rejection catalogue** (`WRONG_TARGET_ENTRY_ID`, `ALTERED_REPLACEMENT_TEXT`, `MALFORMED_DECISION_SHAPE`, `NO_MATCHING_DECISION`, `SOURCE_EQUALS_DESTINATION`, …) | SKILL.md table | Every code is raised by core. A per-skill copy drifts the moment core adds one. |
| **A6. `--serve` session discipline** (one process; the acceptance token lives in that process's memory only) | SKILL.md prose | A property of `successor-acceptance-registry.ts`. |
| **A7. Markdown block-safety rules** (preserve block-boundary blank lines, patch whole blocks) | SKILL.md prose | Enforced by `successor-markdown-block-safety` in core. Only the *display-math* clause is domain (see B2). |

**Not promotable, because it does not exist yet — reported as a false premise:**

> **A8. "Header of what changed and why between versions."** The brief says the
> new artifact carries one *"igual al de deliberación matemática."* There is no
> such header. `grep -rin 'cambió|changed|changelog'` over core returns zero.
> A published successor carries a `receiptId`, a `documentShaAfter`, and an
> HTML comment `<!-- proposal-workspace:revision:start id=sha256:… -->`; the
> document itself gains no human-readable change note. **This has to be built,
> and it belongs in core** (it is pure version mechanics), which also gives the
> mathematical skill something it currently lacks.

> **A9. "User vs. source-document conflict handling."** Also absent. The
> decision tree (A1) resolves *which file is the base*; nothing resolves *the
> user asserting something the source document contradicts*. For the
> mathematical domain that gap is survivable — the tutor derives internally. For
> an experimental domain it is not: the data paper is a hard ceiling on claims,
> so a user asking for an experiment the guidance does not support must be
> refused, not accommodated. **New mechanic, and the new layer is the reason it
> is needed.**

### Bucket B — Parametrize (general structure, domain vocabulary baked in)

| Item | Core file(s) | Structure that stays | What the layer must supply |
| --- | --- | --- | --- |
| **B1. Managed artifact naming** — `research-concept-<slug>-rNN.md` | 14 core sites: `consistency-audit.ts:9`, `document-state.ts:2`, `initial-revision-creation.ts:15,63`, `initial-revision-renderer.ts:58`, `intent-resolver.ts:3`, `orchestrator.ts:6,87`, `revision-receipt.ts:6`, `proposal-workspace-adapter.ts:12,27,48,58,66`, `revision-domain.ts:68`, `proposal-workspace.ts:69-71,334,489,492,736,740,744,1119,3453,4332,4439` | lineage + monotonic revision + a marker byte prefix | the stem (`experiments`) and the revision spelling (`v1` vs `r01`) |
| **B2. Artifact directory** — `proposals/` | `orchestrator.ts`, `document-state.ts`, `consistency-audit.ts:251`, `initial-revision-creation.ts:83`, `revision-lifecycle-store.ts:128,170,173,295`, `cli.mjs:216`, `proposal-workspace.ts:26` | one flat directory of managed artifacts | the directory name |
| **B3. Sidecar root** — `.proposal-deliberation/{state,receipts,withdrawn}/` | 8 core files | three sibling sidecar kinds | the root name |
| **B4. Pre-draft reference sources** — `guidance/paper-guide`, loaded once at v1 | `proposal-workspace.ts:25` (`GUIDE_DIRECTORY`), `loadGuideDirectoryFragments` | "read these read-only fragments before rendering v1, never per turn" | *which* sources, **and whether each is required** — the new layer needs three, two of them mandatory |
| **B5. Preservation gate** — `mathDelta` / `acknowledgedMathRemovals` | `math-integrity.ts:77-106`, `candidate-validator.ts:13`, orchestrator accept gate | "extract atoms that must not vanish silently; report `lost` on preview; refuse accept until each is acknowledged by id" — **this is the single best mechanic in the engine and it is entirely general** | the atom extractor. Math: display/inline/`\tag`/macro/`(Ec. N)`. Experimental: table skeletons, figure placeholders, baseline rows, declared success criteria, cited URLs |
| **B6. Canonical-form validator** — LaTeX spelling rules | `math-integrity.ts:109-137`, `candidate-validator.ts` | "a list of `{rule, line, detail}` violations that block outright, because they are never intentional" | the rule set. Experimental: *no example numbers in a report table*, *every baseline row carries a URL*, *no unverified URL without the pending marker* |
| **B7. Reference integrity** — `\label`/`\tag`/`\eqref` + `(Ec. N)` | `reference-index.ts`, `candidate-validator.ts:3-7`, `document-index.ts:3-4` | "declarations and citations of numbered things must resolve" | what declares (a `\tag` vs a table id) and what cites |
| **B8. Structural entry types** — `display_equation`, `inline_math_region`, `theorem`, `algorithm` | `types.ts:80`, `document-index.ts:9-10`, `target-resolver.ts:54,60,246` | leaf-vs-container classification driving locus resolution | which block kinds are leaves. Experimental needs `table` and `figure_placeholder` as first-class leaves; today a Markdown table is just `paragraph` |
| **B9. Tutor assessment fields** — `mathematicalIssues`, `notationIssues`, `assumptionIssues` | `tutor-adapter.ts:3` | a decision + typed issue channels + risk level | the channel names. Experimental: `protocolIssues`, `comparabilityIssues`, `sourceIssues` |

### Bucket C — Leave where it is (genuinely mathematical, no experimental analogue)

| Item | Where |
| --- | --- |
| C1. The rigor doctrine: mathematical necessity before formalization, symbol means one thing for the document's lifetime, assumptions stay explicit | SKILL.md |
| C2. Chat rendering of LaTeX at three levels (transliterate / decompose / raw) | SKILL.md |
| C3. The canonical LaTeX form itself — `$…$`, `$$` on its own line, commands not glyphs, `\tag{N}` + `(Ec. N)` | SKILL.md + `profile.ts` |
| C4. `equationSymbols()` and symbol-conflict scoring | `target-resolver.ts:52`, `symbol-index.ts` |
| C5. The four `conceptualTerms` / `subjectTerms` and the `(Ec. N)` citation pattern | `profile.ts` — already correctly placed |

### Bucket D — False friends (look shared, are not)

| # | Looks shared | Why it is not |
| --- | --- | --- |
| **D1. "Verify"** | Mathematical: derive it and close internally — sufficiency is *the derivation holds*, and it is timeless. Experimental: cite an external source — sufficiency is *a real, reachable, current source says so*, and it decays. They share the writing scaffold (locus → patch → preview → acknowledge → publish) and **nothing about sufficiency**. Do not unify them under one `verified` predicate. Concretely: the mathematical layer has no notion of *stale*, and the experimental layer must carry `pending-verification` as a first-class document state. |
| **D2. "Preservation"** | B5's *machinery* is shared; the *atoms* are not, and the mathematical atom set is worthless on an experiments document (zero `$$`, zero `\tag` → `mathDelta` returns empty and the gate passes vacuously). A vacuous pass is worse than no gate. |
| **D3. "Consistency"** | Mathematical consistency = notation coherence across the document. Experimental consistency = every experiment maps to a proposal claim, every claim has an experiment, and every metric/split matches the benchmark. Both are graph checks; the graphs have nothing in common. |
| **D4. "Citation"** | `(Ec. N)` points inward at a numbered display in the same file. An experimental citation points outward at a repo, a venue, a year. `reference-index.ts` resolves the first; it cannot express the second, and `missing` would be vacuously empty. |
| **D5. "Claim"** | In core, `MaterializationClaimProvenance.claimId` is an *accepted decision* in the deliberation. In the new layer, "claim" is a **proposition in the upstream proposal document** that an experiment must sustain. Same word, different referents, and the new layer will use the second meaning constantly. Rename in the new layer's prose to avoid collision. |

## 3. Audit: math assumptions that leaked into core during extraction

Reported per the brief's item 4. The lock test only scans for the values
`profile.ts` **declares** (`CREDA`, `matematica_propuesta_CREDA.md`, …), so
none of these were ever caught.

| # | Site | Leak | Severity for the new layer |
| --- | --- | --- | --- |
| **L1** | `intent-resolver.ts:59` — `requestedEffect: has('sparse','dispers') ? 'representación sparse' : undefined` | An unprofiled ML/math domain literal in core intent resolution. Nothing in `profile.ts` produces it. | Low (inert), but it is a leak by the same rule that produced `domain-profile.ts`. |
| **L2** | `types.ts:80` `EntryType` | `display_equation`, `inline_math_region`, `theorem`, `algorithm` are core vocabulary. | Medium — an experiments document's **tables have no entry type**, so a table cannot be a locus. |
| **L3** | `candidate-validator.ts:3-14` | `\label`/`\tag`/`\eqref` uniqueness and `mathCanonicalForm` are unconditional terms of `ok`. | Medium — on a math-free document these pass **vacuously**, so the validator reports a clean bill of health while checking nothing. |
| **L4** | `document-index.ts:9-10` | Display-equation chunking and the `$$` exclusion in paragraph boundaries are hardcoded. | Low. |
| **L5** | `tutor-adapter.ts:3` | The core adapter contract's field names are mathematical. | Low (names only). |
| **L6** | `initial-revision-renderer.ts:78` | Emits a literal `## Paper Guide Reference` heading into v1. | Low. |
| **L7** | `revision-domain.ts:68`, `revision-receipt.ts:6`, `proposal-workspace-adapter.ts:12` | `'research-concept-r01.md'` is a **literal TypeScript type**, not a string. | **High** — a second domain cannot type-check against it. |

**Verdict on "will the new layer fight the engine?"** Yes, in three places, and
all three are B-bucket, not doctrine: the artifact namespace (B1–B3, L7), the
validation vocabulary (B5–B7, L3), and the absence of a table/figure entry type
(B8, L2). Nowhere does the engine's *rigor doctrine* leak — that stayed in
SKILL.md, correctly.

## 4. The external-validation stage — corrected

The brief proposes adding it to core "as an optional stage the layer enables,
since the engine governs the stage sequence."

**The engine governs no stage sequence.** It exposes eight unordered operations
(`STATUS`, `RESOLVE_TARGET`, `CREATE_INITIAL_REVISION`, `CREATE_SUCCESSOR`,
`WITHDRAW_REVISION`, `RESTORE_WITHDRAWN_REVISION`, `CHAT_DELIBERATION`,
`CLOSE_DELIBERATION`, `MAINTENANCE`). Ordering is prose in SKILL.md. There is
nothing to insert a stage into.

What core *does* have is the right hook, one layer down: `CREATE_INITIAL_REVISION`
loads read-only reference fragments before rendering (B4). Generalizing that into
a **declared, required source set** gives the stage real teeth:

- the layer declares its sources and which are mandatory;
- core refuses `CREATE_INITIAL_REVISION` when a mandatory source is absent
  (`REQUIRED_SOURCE_MISSING`), instead of today's silent `return []`;
- the *searching* stays the agent's job (prose), but its **product** —
  the evidence block — becomes a mandatory section whose absence blocks the
  draft, enforced by B6's parametrized canonical-form validator.

That is the honest version: core enforces *presence and shape*, the layer's
prose drives *the search*, and the third skill inherits the same hook.

## 5. Proposed core diff

Ten changes. Every one keeps `proposal-deliberation` byte-identical in behaviour
by having its `profile.ts` declare exactly today's values as defaults.

| # | Change | Files | Bucket | Risk |
| --- | --- | --- | --- | --- |
| **1** | Extend `DeliberationDomainProfile` with an `artifact` block: `{ directory, stem, revisionPattern, revisionLabel, sidecarRoot, marker }`. Add each to `REQUIRED`. | `domain-profile.ts` | B1–B3 | low |
| **2** | Replace the 14 hardcoded `research-concept-…` regexes and the `'research-concept-r01.md'` literal types with profile-derived builders in one new `artifact-naming.ts`; every site imports from there. | 14 files + new | B1, L7 | **high — the big one** |
| **3** | Route `proposals/` and `.proposal-deliberation/` through the same profile block. | 12 sites | B2–B3 | medium |
| **4** | Generalize `math-integrity.ts` → `preservation.ts`: keep `atoms/delta/violations`; move the extractor and rule set behind `profile.preservation.{extractAtoms, violations}`. Ship the math implementation as `proposal-deliberation/preservation-math.ts`. Rename the wire fields `mathDelta`→`preservationDelta`, `acknowledgedMathRemovals`→`acknowledgedRemovals`, **keeping the old names as accepted aliases** so the mathematical SKILL.md needs no edit. | `math-integrity.ts`, `candidate-validator.ts`, `orchestrator.ts` | B5–B6, L3 | medium |
| **5** | Make reference integrity profile-driven: `profile.references.{declares, cites}`. | `reference-index.ts`, `candidate-validator.ts`, `document-index.ts` | B7, L3 | medium |
| **6** | Add `table` and `figure_placeholder` to `EntryType`; recognize GFM tables in `buildStructuralIndex`; add both to `target-resolver`'s leaf list. Additive — no existing document gains an entry. | `types.ts`, `document-index.ts`, `target-resolver.ts` | B8, L2 | medium |
| **7** | Generalize B4: `profile.sources: readonly { path, required }[]`. `loadGuideDirectoryFragments` reads the list; a missing **required** source becomes `REQUIRED_SOURCE_MISSING` instead of `[]`. `proposal-deliberation` declares `guidance/paper-guide` as **not** required, preserving today's silence. | `proposal-workspace.ts:25,5336`, `initial-revision-creation.ts` | B4, §4 | medium |
| **8** | **New (A8):** a change-header contract. `CREATE_SUCCESSOR` gains a required `changeSummary: { what, why }`; the published successor carries it as a rendered header block. Refuse `CHANGE_SUMMARY_REQUIRED` when absent. Both skills benefit. | `orchestrator.ts`, `patch-compiler.ts`, `revision-receipt.ts` | A8 | medium |
| **9** | **New (A9):** a source-conflict refusal. `profile.sourceAuthority` names which loaded sources are *ceilings*; a decision whose evidence contradicts a ceiling source is refused `SOURCE_AUTHORITY_CONFLICT` rather than published. Off by default — `proposal-deliberation` declares none. | `candidate-validator.ts`, `orchestrator.ts` | A9 | medium |
| **10** | Delete the `'sparse'/'dispers'` literal from `intent-resolver.ts:59`; move it to `profile.vocabulary` (or drop it — nothing reads `requestedEffect` downstream except the conceptual plan's `scientificGoal` fallback). | `intent-resolver.ts` | L1 | low |

**Extend the lock** (`proposal-deliberation-domain-profile-lock.test.mjs`) to
scan core for the *new* declared values too — the stem, directory and sidecar
root — so change 2 cannot silently regress. That is the test that would have
caught all of L1–L7 had it read those fields.

**Order:** 1 → 2 → 3 (namespace, unblocks everything) → 6 (tables, needed before
the artifact schema is expressible) → 4 → 5 → 7 → 8 → 9 → 10.

Changes 1–3 alone are the minimum that lets a second skill exist at all; 4–7 are
what stop it fighting the engine; 8–9 are new mechanics the brief asked for and
the core does not have.

## 6. What I am NOT proposing

- No new engine. No fork of `proposal-workspace.ts`.
- No unification of `verify` (D1). The experimental layer gets its own
  sufficiency criterion in its own prose, on top of the shared scaffold.
- No change to the mathematical skill's SKILL.md, doctrine, or published bytes.
- No stage machine in core (§4).

---

# CORRECTIONS (appended after the design phase measured them)

Six claims above did not survive measurement. They are left in place rather than
edited away, so the record of what was assumed stays readable. **Where this
document and `design.md` conflict, `design.md` is authoritative.**

| # | Claim above | Measured truth |
| --- | --- | --- |
| C1 | §3/L2 and §5 change 6: "`EntryType` does not list a table" | **False.** `types.ts:80` already declares `table_reference` AND `figure_reference`. They are never emitted: `buildStructuralIndex` produces only `document`, `section`, `subsection`, `heading`, `display_equation`, `paragraph`. The gap is the **indexer**, not the type. This document quotes the line verbatim and then states the opposite. |
| C2 | §5 change 6: "Purely additive — no existing document gains an entry" | **False.** `entryId` is `${type}:${sha256(...)}`, so retyping a table **changes its id**. `target-resolver.ts`'s `leaf()` list would also lack the new names, dropping a retyped table out of composite member selection. And `saveDerivedState` throws `INCOMPATIBLE_COMMITTED_STATE` when a COMMITTED state re-serializes differently — a hard failure on published documents, not a silent stale read. Change 6 is a **retyping**: it must bump `PARSER_VERSION` and must NOT supersede the old one (supersession means "same parse output, new name"; this is not that). |
| C3 | §5 change 2: the five regexes "agree only by luck" | **They do not agree.** Four distinct semantics. `document-state.ts:2` accepts ANY lineage character and a ONE-digit revision (`(?:(.+)-)?r(\d+)`); `consistency-audit.ts:9` / `orchestrator.ts:6` are anchored, lowercase-alnum, min two digits; `intent-resolver.ts:3` is unanchored and case-insensitive; `initial-revision-creation.ts:15` requires a lineage and pins `-r01`. The lax one is the **sole gate on `loadDocumentState`**, so collapsing them silently TIGHTENS document loading. Mutation M2b exists for exactly this. |
| C4 | §5 change 3: "`proposals/` — 12 sites" | **73 occurrences across 10 files.** Roughly 35 are refusal prose and MCP tool-schema descriptions in `proposal-workspace.ts`, not path construction. Separating namespace from prose is real, unestimated work. |
| C5 | Implied throughout: change 4's accept gate is covered | **Nothing asserts `MATH_REMOVALS_NOT_ACKNOWLEDGED`.** It appears only at `orchestrator.ts:252` (the gate itself) and in two documents. `proposal-deliberation-v2-source-routing.test.mjs:252` exercises only the acknowledged path. The guard the whole preservation mechanic rests on is untested, and change 4 rewrites it. The test must be written **before** the change. |
| C6 | §4 and §5 change 8: a header in the body "collides with `COMPOSITE_UNTOUCHED_INVARIANT`" | **False premise.** `successor-composite-engine.ts:214-225` walks the **gaps between edit spans** plus the tail; it never inspects bytes INSIDE a span. A header that is its own block span sits inside the union, so the invariant is **satisfied, not bypassed**. No exemption is needed and none will be added. |

Only the vacuous-pass finding (§D2, L3) survived unchanged: on a math-free
document `labels`, `tags`, `referencesOk` and `displayDelimiters` are all true
over empty sets.

## Decisions taken after this document was written

- **Change 8**: option (b) — the header is its own resolved block, gated on
  `profile.artifact.changeHeader`, with the receipt carrying the same summary
  alongside. `proposal-deliberation` declares no header: nothing rendered,
  bytes identical. A fourth option found in code — inserting at a zero-width
  span via `compileSuccessorCompositeChangeset` — was rejected: two code paths
  and an unbounded document prefix that `growth-threshold` would then see.
- **Change 9**: preview-time advisory with `acknowledgedSourceConflicts`, plus
  `profile.sourceAuthority.severity: 'advisory' | 'refuse'` defaulting to
  advisory. Byte-identical for `proposal-deliberation`, which declares no
  `sourceAuthority`.
- **Delivery**: four chained slices, one branch and PR each.
