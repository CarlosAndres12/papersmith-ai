# Proposal: The agreement nothing computes

> **Budget note.** This proposal exceeds the default 450-word artifact budget,
> deliberately, on the precedent the Slice A and Slice C proposals and
> `openspec/specs/implementation-document-binding/spec.md` each record in their
> own Purpose. The overage buys four things a shorter artifact would have had to
> assert instead of show: what of §B6 Slice C already closed, a live defect
> inside a *sealed* command, one inherited blocker whose recorded cause is no
> longer in the source, and the citation-key options the operator must rule on.

## Intent

Deliver operator items **3** and **4** — detect when the two declared documents
contradict each other, **refuse**, and let the operator decide; and publish a
**successor of the experiments document** when the implementation contradicts
it, reusing Flow B's existing paths through to a test submission.

§B3 of the seam measurement states the gap exactly: *"Today `fidelity.status`
folds four conditions over ONE document. Two documents can each be internally
clean and disagree with each other, and nothing in 17,100 lines computes
that."* Slice C made the fold per-document and **deliberately did not** compute
agreement between them — `implementation-document-binding`'s own Boundary
section says why: under one document a cross-document verdict *"could be
exercised only by a fixture written to satisfy it."* Two documents now resolve
(`experimental-implementation/impl_profile.py` declares `documents[0]`
`experiments` and `documents[1]` `proposal`), so the branch has a reaching
configuration. It is D's.

## What §B6 still owes — re-derived this session, by symbol

§B6 named four missing things. **Three are now closed; one is not, and the
measurement of *where* it is open is sharper than §B6 could be.**

| §B6 piece | State at `8fb1ff3` | Evidence |
|---|---|---|
| A finding naming its document, validated at read time | **Closed** | `well_formed(declared, *, require_document=False)`; `read_findings` passes `True` only under `len(DOCUMENTS) > 1` |
| Finding-consuming call sites take the document as an argument | **Partial** | `cmd_admit` and `cmd_verify`'s `remedy_compatibility` call pass `sources_by_document`. **`cmd_handoff` does not** — it calls `finding_impact(finding, source)` with document 0's text only. `cmd_verify`'s local-count comprehension calls `finding_impact(f, source or "")["class"] == "local"` — also document 0 only |
| `admissibility.json` keyed by document | **Closed** | `admissibility_record`'s dual-shape read pairs by `entry["label"]` via `by_label` |
| `handoff` reports the cross-document consequence | **Open** | see below |

**The "against BOTH" gap is now located, not merely named.** A finding *may*
already say both — `_valid_document_field` accepts a list and `finding_impact`
returns `{label: "local"|"structural"}`. What cannot express it is the
**consumer**: `cmd_handoff` routes on `impact["class"] == "local"` at three
sites, and `cmd_verify` at one more. Hand those a mapping and every comparison
is `False`, so every finding falls to `deferToOwnSession` — silently, with no
refusal. That is the `local`/`structural` binary §B6 predicted, found at the
exact four comparisons that must change.

## Two defects found while re-deriving M1 — neither inherited

**1. A LaTeX regex runs against an experiments document inside a SEALED
command.** `remedy_compatibility` computes `tags = set(TAG_RE.findall(source))`
and then `missing = [e for e in finding.get(field, []) if e not in
finding_tags]`. `TAG_RE` matches `\tag{…}`; an experiments document has none,
so the tag set is empty and **every declared experiments locus lands in
`unknown_loci`**, making `status` `"incompatible"`. `cmd_verify` calls
`remedy_compatibility`, and `verify-a`/`verify-b` are **sealed** cases in
`tests/experiments_seal/digests.json`. The block locator is therefore not an
unsealed-command problem; it is already inside the sealed surface.

**2. `remedy_compatibility`'s field loop is still document-0 scalar.** Line-free
citation: its `for field in (LOCUS_KEY, REMEDY_LOCUS_KEY)` reads the two
module-level scalars, which `document_vocabulary(0)` supplies. A finding naming
`documents[1]` (`proposal`) has its `equations`/`remedy_equations` fields looked
up under the keys `experiments`/`remedy_experiments`, finds nothing, and reads
as **compatible**. Slice C threaded `sources_by_document` into this function's
*text* selection and left its *key* selection scalar.

**M1's reach, re-derived.** `TAG_RE` has three readers —
`remedy_compatibility`, `cmd_compose`, `cmd_admit`. `DISPLAY_BLOCK_RE` has one,
`cmd_compose`. The measurement's note stands. `tests/experiments_seal/
unsealed.json` excludes **both** `compose` and `admit` for exactly this reason,
so the locator un-excludes two commands, not one.

## An inherited blocker whose recorded cause is not in the source

`experimental-deliberation/SKILL.md` carries **"Known limit: the accept turn
does not publish in this domain"**, measured **2026-09-08**: `CREATE_SUCCESSOR`
accept answers `INVALID_TARGET_REVISION`, and the recorded cause is
*"`proposal-workspace-adapter.ts` derives the published revision label by
matching the target filename against a hardcoded `-r(\d+)\.md$`."*

**That regex is not in `proposal-workspace-adapter.ts` today.** The throw site
is real — `publishSuccessor` raises `INVALID_TARGET_REVISION` when
`parseManagedRevision(targetFilename)?.revision` is falsy — but
`parseManagedRevision` now matches `LAX_RE`, built from
`escapeRegExp(DOMAIN.artifact.revisionPattern)`, and
`experimental-deliberation/profile.ts` declares `revisionPattern: "v"` with a
two-digit `revisionLabel`. The cause is profile-derived, not hardcoded.

**This is not a claim that the blocker is gone.** No suite was run here. It is a
claim that a dated diagnosis no longer describes the code, and **item 4's
end-to-end outcome must be re-measured before it is priced**, not inherited.
This project has already been misled in both directions by an undated
"pre-existing".

## Scope

### In Scope

- **A cross-document citation key** — one per-document profile leaf, its
  resolver tier, its **indexed** refusals (`documents[0].cross_citation_pattern`),
  and the declaration form on the deliberation side. **Shape is the operator's
  ruling; see the open decision below.**
- **The two mechanical, byte-decidable refusals.** Kind 1: the experiments
  document tests a claim the proposal no longer declares. Kind 2: the proposal
  declares a claim no experiment tests.
- **Fail closed ONCE, not N times.** A document declaring no crossing at all
  refuses by a single named code, never one discrepancy per claim.
- **Per-discrepancy acknowledgment by exact id**, mirroring
  `acknowledgedRemovals` in `_core/deliberation/engine/orchestrator.ts` — which
  blocks with `reason: 'MATH_REMOVALS_NOT_ACKNOWLEDGED'` plus an
  `unacknowledged` list and clears only ids echoed back. Stronger than a general
  "continue": per item, and recorded.
- **The block locator beside the profile (ruling: option A).** Profile-supplied,
  precedent `preservation-math.ts` / `preservation-experimental.ts`. Re-points
  all three `TAG_RE` readers and `cmd_compose`'s `DISPLAY_BLOCK_RE`; removes
  `compose` and `admit` from `tests/experiments_seal/unsealed.json`.
- **`remedy_compatibility`'s field loop made per-document**, closing defect 2.
- **`cmd_handoff`'s cross-document consequence**, and the four
  `impact["class"] == "local"` comparisons taught to read a mapping.
- **The experiments-successor handoff** and **Flow B's existing paths to a test
  submission**, in `SKILL.md`.
- **A tutor bullet, never a check**, for the third kind: *the experiment's
  metric or protocol does not correspond to what the claim asserts*. Judging it
  requires reading both documents; a check that tried would block correct work
  and pass broken work.

### Out of Scope — named, not proposed

- **Any engine-generated resolution proposal.** The engine refuses and *names*
  the discrepancy. The agent reads both documents and proposes a resolution **in
  conversation**; the operator decides. This project's own rule is that
  `deliberated` has no observable condition precisely so an agent cannot close a
  stage on its own word.
- **Any inference of repair direction.** Code drifted, or code is deliberately
  ahead — `proposal-implementation`'s Flow B step 5 already asks. A system that
  chose would rewrite the operator's document to agree with a bug.
- **Slice B** (`Data/` demandable), proposed in parallel; D does not depend on
  it and must not touch it.
- Any rename of `proposalDigest` or its ten campaign-proposal relatives —
  `_AUTHORIZATION_BINDING_KEYS` is written into minted tokens in committed
  ledgers that travel in clones.
- **M2** (`cmd_handoff`'s hardcoded Spanish) — still recorded unresolved, and D
  edits `cmd_handoff` without resolving it. **F6.** The kit crossing the seam.
- Repairing `experimental-deliberation`'s accept-turn limit if re-measurement
  shows it still fires. It lives in `_core/deliberation/`, a different engine.

## Capabilities

### New Capabilities

- `implementation-cross-document-agreement`: the two mechanical refusals, the
  cross-document key and its indexed refusals, the fail-closed-once rule, the
  per-discrepancy acknowledgment by exact id, and the explicit boundary that the
  engine emits **no verdict, no resolution proposal, and no repair direction**.
- `implementation-block-locator`: the profile-supplied block locator, its three
  `TAG_RE` consumers and one `DISPLAY_BLOCK_RE` consumer, and the per-document
  locus-key correction inside `remedy_compatibility`.

### Modified Capabilities

- `implementation-document-binding`: its Boundary section — *"the cross-document
  agreement verdict … belongs to the consuming skill"* — is **discharged by**
  this change, not deleted; and `finding_impact`'s per-document `class` mapping
  gains its first consumer.
- `implementation-per-document-vocabulary`: the cross-document key and the block
  locator join the per-`documents[N]` tier, under the same all-or-nothing rule
  and the same indexed refusal naming.
- `implementation-cli-seal`: `compose` and `admit` leave
  `tests/experiments_seal/unsealed.json`; agreement cases added; the sibling's
  **28 digests asserted byte-identical**.
- `experimental-implementation-skill`: `SKILL.md`'s "Which commands are not
  available yet, and why" loses two entries; the tutor bullet and Flow B to a
  submission are added.

## Approach

Locator first, then the key, then the refusals, then the consumer — and RED
before each.

1. **The locator is independent of the operator's open decision**, so it starts
   immediately. It also carries the sharpest existing proof: `verify-a`/
   `verify-b` are sealed against a `TAG_RE` that matches nothing in this
   domain's document, so the seal **must move**, deliberately, and each moved
   case is read before acceptance — the discipline C3 already exercised on 6 of
   20 cases.
2. **The key is a gate, not a design choice.** Nothing below it may be written
   until the operator rules; without a key, refusal kind 1 fires on every
   document from day one.
3. **The refusals land RED first**, each with the corpus case that reaches it
   named *before* the assertion is written, and each mutation-proven. A branch
   no reachable configuration takes cannot be mutation-proven; a fixture written
   to satisfy a guard proves nothing.
4. **The consumer last.** `cmd_handoff`'s four comparisons are where a mapping
   silently degrades to `False`; the test that proves it must be the one that
   fails against the shipped engine first.

The engine refuses and names; judgment stays with the operator.

## The one open operator decision — the cross-document citation key

`reference-experimental.ts` declares `[exp:X]` (core kind `tag`) and cites
`[tests:X]`; `reference-math.ts` declares `\label{id}`/`\tag{id}` and cites
`(Ec. N)`. **`checkReferenceIntegrity` resolves cited values against declared
values in the SAME document** — its own docstring: *"a claim with no experiment
behind it cites an identifier nothing declares, which the core reports as an
unresolved reference and fails validation on."* So `[tests:X]` **cannot** be
re-pointed at the proposal: every such citation would dangle and fail
deliberation validation. **There is no key today by which an experiments
document cites a claim in the proposal.**

| Option | What it is | Cost | What it buys | What it risks |
|---|---|---|---|---|
| **1. A new explicit cross-document form** (e.g. `[claims:39]`) declared in the experiments document, matched by a new per-`documents[N]` profile leaf | A form neither `declares` nor `cites` matches today | One profile leaf + tier + indexed refusals; one new form documented on the deliberation side. **Migration cost is zero today** — `experiments/` and `proposals/` hold only `.gitkeep` | The agreement becomes a property of **the two documents**, which is what was asked. `checkReferenceIntegrity` is byte-untouched | A second declaration vocabulary the deliberation side does not validate; a typo refuses instead of being caught upstream (arguably correct) |
| **2. Reuse `__provenance__` as the crossing** — a module declaring both `experiments` and `equations` IS the join | Near-zero new vocabulary; the provenance join already exists, and B2's ruling keeps `sections` shared | Cheapest by far | Nothing new to author or maintain | **Makes the agreement a property of the CODE.** Two documents can disagree with no module written at all and this cannot see it. It reads clean on an empty target — a check that measures nothing |
| **3. A declared mapping table** in the target's `tests/` | A third artifact naming locus↔claim pairs | A new artifact, its reader, its staleness story | Explicit and readable | A third place the truth can drift from; an unmaintained table **reads as agreement** |
| **4. Ship one refusal, defer the other** | — | Smallest slice | — | **Measured false: neither kind is decidable without a key.** Both need "which proposal claim does experiment E1 test", and nothing carries it. Recorded so it is not proposed again |

**Recommendation: option 1, plus the fail-closed-once rule** — an experiments
document declaring no crossing refuses by one named code rather than producing N
discrepancies. Option 1 is the only one where the agreement is a property of the
documents rather than of the code, its migration cost is genuinely zero today,
and it leaves the deliberation core untouched. **The operator rules; nothing
below the key is written until then.**

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `_core/implementation/engine/implementation_engine.py` | Modified | Block locator indirection at `remedy_compatibility`, `cmd_compose`, `cmd_admit`; `remedy_compatibility`'s field loop per-document; the two refusals; acknowledgment; `cmd_handoff`'s cross-document consequence and its three `class` comparisons; `cmd_verify`'s fourth |
| `_core/implementation/impl_domain_profile.py` | Modified | Cross-document key and block-locator leaves on `documents[N]`, their tier, their indexed refusals |
| `.claude/skills/experimental-implementation/impl_profile.py` | Modified | The new per-document leaves; a block locator module beside it |
| `.claude/skills/experimental-implementation/SKILL.md` | Modified | `compose`/`admit` available; the tutor bullet; Flow B to a submission |
| `.claude/skills/experimental-deliberation/` | Modified (option 1 only) | The declaration form, if the operator rules option 1 |
| `tests/experiments_seal/` | **Moves, deliberately** | `unsealed.json` loses two entries; `verify-a`/`verify-b` digests move; each read before acceptance |
| `tests/seal/`, `proposal-implementation/**`, `proposal-deliberation/**` | **Untouched** | the bar |
| `tests/test_proposal_implementation.py` | Modified | `reachable_refusal_codes`'s derived roster — every new code must join it |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Refusal kind 1 fires on every document because no key resolves | **High** | The open decision above is a gate; nothing below it is written first. Plus the fail-closed-once rule |
| The engine drifts into proposing a resolution | **High** | The boundary is a spec requirement with its own mutation proof, not prose; `deliberated` having no observable condition is the standing precedent |
| A fixture written to satisfy the agreement check proves nothing | **High** | Each refusal's corpus case is named **before** its assertion; mutate the guard away and watch it die |
| `cmd_handoff`'s `class` comparisons degrade silently to `False` under a mapping | **High** | This is the measured shape; the test that proves it must be RED against the shipped engine first |
| `tests/seal/`'s 28 digests move | **High** | D edits shared engine bytes. `git diff --exit-code tests/seal/` — assert, never infer |
| `skipped=6` moves in a ninth change | Med | A `skipTest` is never the way past a hard case; assert the count |
| The accept-turn blocker is priced from a stale diagnosis | **High** | Re-measure before pricing item 4; the recorded cause is not in today's source |
| The experiments seal moves for a reason nobody read | Med | C3's discipline: every moved case read and defended individually, 6 of 20 was not a rounding error |
| A new refusal code misses `reachable_refusal_codes` | Med | The roster is derived but lives in `tests/test_proposal_implementation.py`, outside `_core/`; locate it at apply |
| Counts in this document are inherited | Med | 28 and 20 were re-derived from `digests.json` here (29 and 21 top-level keys, one of which is `__corpus_fingerprint__`). Re-derive again at apply |

## Rollback Plan

Each slice is its own branch. The locator slice is the only one that moves an
existing seal, so its revert is proved, not assumed: revert its commits,
re-capture **both** corpora, and require `git diff --exit-code tests/seal/` to
exit 0 and `tests/experiments_seal/digests.json` to return to its pre-slice
bytes. Restoring `compose`/`admit` to `unsealed.json` is part of the revert, not
an afterthought — without it two commands are documented available and are not.
The agreement slices are additive: delete the new leaves, the refusals and their
corpus cases and the two-document configuration is exactly Slice C's.

## Dependencies

- **Slice C landed and archived** — done (`2026-09-12-the-second-document-verified-on-its-own-terms`).
- **The citation-key ruling.** Blocks everything except the locator slice.
- **A re-measurement of `experimental-deliberation`'s accept turn** before item
  4 is priced or promised.
- `experiments/` and `proposals/` hold only `.gitkeep`; **every fixture is
  authored from nothing.**

## Success Criteria

- [ ] Both refusals are mutation-proven, each with the corpus case that reaches
      it named before its assertion was written.
- [ ] A discrepancy acknowledged by exact id clears **only that id**; a general
      "continue" clears nothing. Proven by a case with two discrepancies.
- [ ] A document declaring no crossing refuses **once**, by a named code — not
      once per claim.
- [ ] The engine emits no verdict word, no resolution proposal, and no repair
      direction — each proven by mutation, not by reading the source.
- [ ] `remedy_compatibility` reads **document N's own** locus keys: a finding
      naming `documents[1]` whose `remedy_equations` locus is absent from the
      proposal is reported, where today it reads compatible.
- [ ] `compose` and `admit` leave `tests/experiments_seal/unsealed.json` and are
      sealed cases.
- [ ] Every moved `experiments_seal` digest is individually read and defended in
      the verify report.
- [ ] `tests/seal/`'s 28 digests byte-identical; `npm test` 595/595; Python
      `OK (skipped=6)` with `Ran` grown — **`skipped=6` must not move.**
- [ ] No file under `proposal-implementation/` or `proposal-deliberation/` is
      modified.
- [ ] Every new refusal code appears in `reachable_refusal_codes`'s roster.

## Size — and how many changes

**Estimate: 2,000–3,350 changed lines.** The Slice A proposal's **1,200–1,900**
is low, for the reason every low estimate this session was low: it priced the
mechanism and not the proof. Specifically it priced neither the block locator's
**three** consumers (it recorded the reach as a note), nor the cross-document key
(it was an open question, so it cost nothing), nor the corpus authored from
nothing. A's own design re-derived A by **+43%** for the same two omissions;
Cut 3 came in **+78%**. Applying +43% to 1,200–1,900 gives 1,716–2,717, and the
locator's second and third consumers plus the sealed-verify movement push the
top out.

| Slice | Delivers | Gate at the end | Estimate |
|---|---|---|---:|
| **D1** | Block locator beside the profile; all three `TAG_RE` readers + `DISPLAY_BLOCK_RE`; `remedy_compatibility`'s per-document field loop; `compose`/`admit` unsealed → sealed | Both corpora re-captured; every moved digest read; `tests/seal/` untouched | 550–900 |
| **D2** | The cross-document key: leaf, tier, indexed refusals, declaration form | A two-document corpus where the crossing resolves, and one where it does not | 400–650 |
| **D3** | The two refusals; fail-closed-once; per-discrepancy acknowledgment by exact id | Each refusal mutation-proven; two-discrepancy acknowledgment case | 600–1,000 |
| **D4** | `cmd_handoff`'s cross-document consequence; the four `class` comparisons; the successor handoff; Flow B to a submission; the tutor bullet | A finding against BOTH routes correctly, proven RED-first | 450–800 |
| | | | **2,000–3,350** |

**Recommendation: four chained changes, in that order — emphatically not one.**

**D1 can start today; D2–D4 cannot.** D1 depends on no operator ruling and
delivers standalone value (two commands become available, and a live defect
inside a sealed command is closed). D2 is the ruling gate. D3 is the only slice
whose subject is refusal, and putting it in the same reviewable unit as the
locator would let a green suite hide which half is actually reading. D4 is last
because its consumer change is where a mapping degrades silently.

Against `review_budget_lines: 1400`, **no slice above may merge unstacked**, and
D3 alone is at or near the budget — it may need splitting again at design time
(the two refusals, then the acknowledgment).

```text
Decision needed before apply: Yes
Chained PRs recommended: Yes
400-line budget risk: High
```

## Proposal question round

Interactive mode; this executor has no channel to prompt. Each question changes
the artifact; the assumption used meanwhile is stated.

1. **The cross-document citation key** — the one open decision above. *Assumed
   meanwhile: option 1. Nothing below the key may be designed until this is
   ruled.*
2. **Is the acknowledgment recorded in the position ledger, or only in the
   command's own output?** `acknowledgedRemovals` is request-scoped on the
   deliberation side and nothing persists it. *Assumed: request-scoped, matching
   the precedent — but "recorded" in the operator's ruling may mean durable, and
   a durable record would touch `position.jsonl`, a ledger that travels in
   clones.*
3. **Does the agreement check run inside `verify`, or as its own command?**
   `verify` is a reader by standing position ("reported, never refused"); a
   refusal inside it would break that. *Assumed: its own command, or a
   binding-write-site refusal — never a new refusal inside `verify`.*
4. **Does item 4 mean the composer produces `replacementText` for the
   deliberation to publish, or an end-to-end published successor?** The second
   depends on `experimental-deliberation`'s accept turn, whose recorded blocking
   cause is not in today's source. *Assumed: the composer and the handoff are
   D's; the published write is re-measured and reported, not promised.*
5. **Must the block locator be per-document?** Document 1 is the mathematical
   proposal and `TAG_RE` is exactly right for it; document 0 is not. *Assumed:
   per-`documents[N]`, same tier as the claim vocabulary — a single
   skill-level locator would be wrong for one of this skill's own two
   documents.*

## Citations checked

Every symbol named above was resolved in source **this session, by name, never
by line, never inherited**: `TAG_RE`, `DISPLAY_BLOCK_RE`, `remedy_compatibility`,
`cmd_compose`, `cmd_admit`, `cmd_handoff`, `cmd_verify`, `finding_impact`,
`_impact_class`, `document_citation_re`, `document_vocabulary`, `well_formed`,
`_valid_document_field`, `read_findings`, `admissibility_record`,
`sources_by_document`, `verify_sources_by_document`, `CLAIM_KEY`, `LOCUS_KEY`,
`REMEDY_LOCUS_KEY`, `NOTATION_KEYS`, `CITATION_RE`,
`DOCUMENT_CITATION_PATTERNS`, `DOCUMENT_INDEX_BY_LABEL`, `DOCUMENTS`,
`reachable_refusal_codes`, `_AUTHORIZATION_BINDING_KEYS`, `proposalDigest`,
`acknowledgedRemovals`, `acknowledgedSourceConflicts`, `publishSuccessor`,
`parseManagedRevision`, `LAX_RE`, `checkReferenceIntegrity`, `declares`,
`cites`, `revisionPattern`.

**Four inherited claims were re-measured; three were corrected or sharpened:**

1. §B6's four routing pieces: **three of four are closed by Slice C**, not
   outstanding. The open one is located at four exact comparisons.
2. §B6's *"a way to say a finding is against BOTH"*: **representable already**
   (`_valid_document_field` accepts a list); the gap is in the **consumer**.
3. `experimental-deliberation/SKILL.md`'s recorded accept-turn cause (a
   hardcoded `-r(\d+)\.md$`) **is not in `proposal-workspace-adapter.ts`
   today**; `parseManagedRevision` reads `DOMAIN.artifact.revisionPattern`.
4. M1's statement of the locator's reach **stands**, re-derived: `TAG_RE` three
   readers, `DISPLAY_BLOCK_RE` one.

**No test suite was run** — a parallel `sdd-propose` is writing under
`openspec/changes/a-data-directory-somebody-can-owe/`, and the session brief
forbids it. Every count here (28 sealed digests, 20 experiments-seal cases, four
`class` comparisons, three `TAG_RE` readers) is derived from files read this
session and must be re-derived at apply.

---

## The citation-key ruling (operator, in session)

**Option 1: a new explicit cross-document citation form**, declared on a
per-`documents[N]` leaf. An experiments document writes, in the experiment's own
body, a citation resolving against a claim the proposal already declares:

```markdown
## Experiment [exp:E3] — the ceiling sweep

Sustains claim [claims:39] of the proposal.
```

Plus: **an unresolved crossing refuses ONCE, under its own named code**, never N
discrepancies at a time.

### Why, and it is not the price

Option 1 is the only one where **agreement is a property of the documents**,
which is what agreement is about. The alternatives each move it somewhere it does
not belong:

- **Option 2 (reuse `__provenance__`)** is nearly free and moves agreement into
  **the code**. A repository with no modules written would pass clean having
  measured nothing — the exact unprovable-guard shape ten changes have been
  removing. Cheap, and wrong in the direction this project has already paid for.
- **Option 3 (a declared mapping table)** adds a third place the truth can drift.
  Unmaintained, it **reads as agreement** while being none.
- **Option 4 (one refusal, defer the other)** was measured false: without a key,
  **neither** kind is decidable.

### The migration cost is zero, and that was measured

`proposals/` in the operator's main checkout holds **17 revisions**, and the
latest (`research-concept-r17.md`) declares **39 claims** as `\tag{1}` … `\tag{39}`.
**Nothing is retrofitted** — those tags are exactly what a `[claims:N]` citation
resolves against.

And `experiments/` holds **zero** documents. The experiments document does not
exist yet, so it is born carrying the new form rather than migrated into it.

### What this does NOT change

`checkReferenceIntegrity` stays untouched: `[tests:X]` keeps resolving against
`[exp:X]` **within** the experiments document. The cross-document form is
additional, not a repurposing — which is what kept every existing citation from
dangling, and was the deciding cost against re-pointing `[tests:X]`.
