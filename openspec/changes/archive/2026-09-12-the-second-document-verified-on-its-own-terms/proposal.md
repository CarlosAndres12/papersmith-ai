# Proposal: The second document, verified on its own terms

> **Budget note.** This proposal exceeds the default 450-word artifact budget,
> deliberately, on the precedent `openspec/specs/implementation-document-binding/spec.md`
> records in its own Purpose. The overage is spent on two things a shorter
> artifact would have had to assert instead of show: the measured defect, and
> one inherited claim that measurement contradicts.

## Intent

Deliver operator items 2 and 5 — verify the code against the latest
**experiments** document as well as the latest **mathematical proposal**, and on
re-invocation validate against **both**.

Slice A ships the second skill with **one** declared document plus a
shipped-surface lock that forbids a second. C removes that lock by making a
second document *mean* something first.

### The defect, measured this session

`.claude/skills/_core/implementation/engine/implementation_engine.py` reads the
whole claim vocabulary as **module-level scalars**, one per profile, never per
document:

| Scalar | Source leaf | Engine lines reading it |
|---|---|---:|
| `CLAIM_KEY` | `PROFILE["provenance"]["claim_key"]` | 5 |
| `LOCUS_KEY` | `PROFILE["findings"]["locus_key"]` | 5 |
| `REMEDY_LOCUS_KEY` | `PROFILE["findings"]["remedy_locus_key"]` | 11 |
| `NOTATION_KEYS` | `PROFILE["findings"]["notation_keys"]` | 9 |
| `CITATION_RE` | `PROFILE["findings"]["citation_pattern"]` | 2 |

**26 distinct engine lines** carry these five (32 symbol-line hits; six lines
carry two or more — the count is lines, and it is reported as lines, because
this project has already been misled once by line counts presented as
occurrences). Meanwhile `impl_domain_profile._resolve()` validates exactly two
leaves per entry — `documents[N].directory` and `documents[N].label`.

**So `documents[1]` can name its own root, label and revision, and still cannot
say that its claims are experiments rather than equations.**

The consequence is already in the tree and already confessed.
`_extra_document_fidelity_status`'s own docstring calls its four conditions
*document-count-invariant* — *"none of `stale`/`missing_provenance`/`untested`/
`unreached` names a per-document fact — they are all about the shared source
tree"* — and the `fidelityByDocument` comprehension in `cmd_verify` passes the
**same four lists** to every index ≥ 1. Those lists are computed once
(`untested`, `stale` assigned in `cmd_verify`'s own body). A second document
reports `drift` when **document 0** drifted.

### The strongest argument: a live spec already requires this and the engine does not do it

`openspec/specs/implementation-document-binding/spec.md` carries
**Requirement: `cmd_verify`'s Fidelity Fold Runs Per Document** — *"MUST run
once per declared document under `len(documents) > 1`, producing one fidelity
result per document"* — with the scenario *"each document's result reflects only
its own four conditions"*. The shipped engine does not satisfy that scenario.

C is therefore not a new appetite. It is a **live contract the implementation
does not hold**, reachable today only because no profile in
`.claude/skills/*/impl_profile.py` declares two documents, so the requirement
has never had a configuration that could fail it.

**Declaring `documents[1]` before C makes item 2 a check that reads green having
measured nothing.** That is the failure class these cycles have been paying off.

## An inherited claim that measurement contradicts — read this before design

The brief for this change states that **A's single document is the mathematical
proposal**. Every committed record at `e3e1438` says the opposite:

| Record | Says |
|---|---|
| `the-second-skill-the-seam-was-for/design.md` D1 | `documents[0] = experiments/`, label `experiments`; explicitly rejects `proposals/` |
| `…/design.md` D2 | `provenance.claim_key` = `"experiments"`, `findings.locus_key` = `"experiments"`, `remedy_locus_key` = `"remedy_experiments"`, citation `(Exp. N)` |
| `…/tasks.md` 1.1 `[x]` | `documents[0]` = `experiments/`, label `experiments` |
| `…/tasks.md` 1.5 `[x]` | names-exclusion measured over the **experiment** word family |
| `…/specs/experimental-implementation-skill/spec.md` | single document, no direction named |

Three independent committed records corroborate `experiments` at index 0. I
could **not** read `.claude/skills/experimental-implementation/impl_profile.py`
to settle it — that path is under concurrent write by the Slice A apply run, and
this session has no shell to read the pinned ref.

**This is not C's ruling to re-open.** It is recorded because C's whole subject
is which document sits at which index. Two readings, both survivable:

- If A landed `experiments` at index 0, **C adds the mathematical proposal as
  `documents[1]`**, and the operator's dependency-direction argument (verify
  upstream before downstream) was not honoured by A — an **A-level**
  reconciliation, not C's.
- If A landed the mathematical proposal at index 0, C adds `experiments` as
  `documents[1]`.

**C's mechanism is direction-agnostic**: per-document vocabulary, per-document
fidelity, indexed refusals. Nothing below depends on the answer except the two
labels. Design must not start until the answer is one word from the operator
(Q1).

## The dependency the slice table hides

Slice A's proposal lists **A, B, C, D**, which reads as B before C. **B depends
on C.**

`Data/` becomes demandable when *the document declares a dataset*. Measured:
`**Dataset:**` appears **8 times across 3 files**, all of them under
`.claude/skills/experimental-deliberation/` (`preservation-experimental.ts` 4,
`SKILL.md` 3, `profile.ts` 1). `proposal-deliberation/preservation-math.ts` has
**zero**. (The brief's attribution of all 8 to `preservation-experimental.ts` is
corrected here; its conclusion stands.)

With A declaring a single document, **no dataset declaration is readable at all**
until the experiments document is a declared, vocabulary-bearing entry. B before
C would ship a branch **no reachable configuration takes** — and this project's
own scar says such a branch cannot be mutation-proven.

**The real order is A → C → {B, D}. Record it in the slice table.**

## Scope

### In Scope

- **Per-document claim vocabulary.** `claim_key`, `locus_key`,
  `remedy_locus_key`, `notation_keys`, `citation_pattern` declarable on
  `documents[N]`, with their own resolver tier and **indexed** refusal names
  (`documents[1].claim_key`), matching the tier `documents[N].directory` already
  has.
- **Back-compatible resolution.** Document 0 keeps resolving from
  `provenance.*`/`findings.*` when no per-document override is declared, so
  `proposal-implementation/impl_profile.py` is **not edited** and its 28 digests
  cannot move.
- **A real per-document fidelity fold.** `stale`, `missing_provenance`,
  `untested`, `unreached` computed against **document N's own** claim vocabulary
  and its own provenance join, satisfying the live requirement above. The
  `document-count-invariant` docstring is deleted, not amended.
- **`citation_pattern` group-count validation in `_resolve()`** — A's design Q3,
  explicitly deferred to C. `_impact_class` reads
  `match.group(1) or match.group(2) or match.group(3)`; a two-group pattern
  raises `IndexError` at runtime, a four-group pattern drops the fourth
  silently.
- **Declaring `documents[1]`** in `experimental-implementation/impl_profile.py`,
  and **deleting A's D10 single-document shipped-surface lock** as this change's
  first act, replaced by a lock that proves the per-document read instead.
- **A two-document corpus whose document 0 is clean and whose document 1 has
  drifted** — the fixture that makes the new fold falsifiable.

### Out of Scope — named, not proposed

- **Slice B** (`Data/` demandable per product folder) and **Slice D**
  (cross-document agreement, the successor composer, Flow B to a submission).
  D's cross-document refusals need C's per-document vocabulary first.
- **Any cross-document verdict.** `implementation-document-binding`'s own
  Boundary section already forbids it here.
- **Any inference of repair direction.** When code and document disagree, either
  the code drifted or the code is deliberately ahead. `proposal-implementation`'s
  Flow B step 5 already asks. **Nothing may infer it** — a system that chose
  would rewrite the operator's document to agree with a bug. C emits the
  disagreement and stops.
- **Any per-document revision pin.** `verify` answers one question: does this
  match the LATEST. By intent, not deferral.
- **The coarse provenance key.** Per the appended B2 ruling (option A):
  `sections` stays **shared**; only the fine key is profile-supplied. A
  profile-supplied coarse key lets two domains pick different words, after which
  the join returns an empty list — **and an empty list there reads as success.**
- Any rename of `proposalDigest` or its ten campaign-proposal relatives — it is
  in `_AUTHORIZATION_BINDING_KEYS`, written into minted tokens in committed
  ledgers that travel in clones.
- M2's resolver-level fix. F6. The kit crossing the seam.

## Capabilities

### New Capabilities

- `implementation-per-document-vocabulary`: the per-`documents[N]` claim
  vocabulary leaves, their resolver tier, their indexed refusals, the
  `citation_pattern` group-count contract, and the document-0 fallback that
  keeps a single-document profile byte-identical.

### Modified Capabilities

- `implementation-document-binding`: its **`cmd_verify`'s Fidelity Fold Runs Per
  Document** requirement becomes held rather than stated; the fold's four
  conditions gain a per-document derivation; `finding_impact`'s per-document
  mapping gains a per-document citation pattern.
- `implementation-cli-seal`: seal cases exercising a declared second document;
  the existing 28 digests asserted byte-identical.
- `experimental-implementation-skill`: "exactly one `documents` entry" becomes
  two; A's D10 lock is deleted and replaced.

## Approach

Additive-with-fallback, then prove, then declare — in that order.

1. **Resolver first, engine unchanged in behaviour.** Per-document leaves are
   optional; absent, document N inherits the existing top-level value, so every
   currently-resolving profile (including `tests/fixtures/two_documents/`)
   resolves unchanged and every digest holds.
2. **Thread the index, do not copy the arithmetic.** The five scalars become
   per-index lookups at their 26 reader lines. `_impact_class` already exists
   precisely so "the identical arithmetic serves a per-document mapping without a
   second copy drifting beside the scalar path" — that extraction is the shape to
   follow, not to duplicate.
3. **The fold last, and RED first.** The first test written is the criterion
   itself: *document 1's fidelity status changes when document 1's own text
   changes, with document 0 clean.* It must be red against the shipped engine
   before one engine byte moves.
4. **Declare `documents[1]` only after 1–3 are green.** Declaring it earlier is
   the defect.

The engine refuses and names; judgment stays with the operator.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `_core/implementation/impl_domain_profile.py` | Modified | Per-`documents[N]` vocabulary leaves, their tier, indexed refusals, `citation_pattern` group-count validation |
| `_core/implementation/engine/implementation_engine.py` | Modified | 26 scalar reader lines become per-index; `_extra_document_fidelity_status` replaced by a real per-document fold; `cmd_verify`'s four condition lists derived per document |
| `.claude/skills/experimental-implementation/impl_profile.py` | Modified | `documents[1]` with its own claim vocabulary |
| `.claude/skills/experimental-implementation/SKILL.md` | Modified | The second document, and what `verify` now answers |
| `.claude/skills/proposal-implementation/**`, `proposal-deliberation/**`, `tests/seal/**` | **Untouched** | the bar |
| `tests/` (pair corpus, experiments seal, domain lock) | Modified | A's D10 lock deleted; two-document drift fixture; per-leaf mutation proofs |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| The new leaves force an edit to the sibling's profile, moving its digests | **High** | The document-0 fallback exists for exactly this; assert `git diff --exit-code` on the sibling's tree, do not infer it |
| `documents[1]` declared before the fold is real — item 2 reads green having measured nothing | **High** | Slice ordering: declaration is the last work unit, gated on the drift fixture being green |
| A fixture written to satisfy the new fold proves nothing | **High** | The control is document 0 **clean** while document 1 drifts; a fold that ignores the index cannot pass it. Mutate the index away and watch it die |
| A branch no reachable configuration takes | **High** | The two-document profile IS the reaching configuration; name the case per branch before writing the assertion |
| The engine's 26 reader lines are lines, not occurrences | Med | Re-derive at apply, per symbol, word-boundary; never quote this table as occurrences |
| `tests/pair/` and `tests/fixtures/two_documents/` stop resolving | Med | Optional leaves with fallback; run that suite before and after |
| A method halts before its second mechanism | Med | `subTest` or separate methods per mechanism |
| `L1_EXPECTED_COUNT` / `L1_EXPECTED_FILES` move — C **does** edit engine bytes | Med | Assert, do not infer; A could claim immunity by editing zero engine bytes and C cannot |
| New refusal codes miss `reachable_refusal_codes`'s derived roster | Med | The roster is referenced from the engine but defined outside `_core/`; locate it at apply and add every new code |
| Which document A declared is unsettled | **High** | Q1 below. Design does not start without it |

## Rollback Plan

C is the one slice that reshapes shared reads, so revert is proved, not assumed:
revert the change's commits, re-run the 28-digest seal and the second skill's own
seal corpus, and require `git diff --exit-code tests/seal/` to exit 0. Restoring
A's D10 single-document lock is part of the revert, not an afterthought — without
it a stray `documents[1]` survives the rollback silently.

## Dependencies

- **Slice A must be landed and archived** — C edits the profile A creates and
  deletes the lock A ships.
- **Q1 answered** (which document A declared).
- `experimental-deliberation` must publish an experiments document
  (`experiments/experiments-<slug>-v01.md`). `experiments/` and `proposals/` hold
  only `.gitkeep`; **every fixture must be authored from nothing.**

## Success Criteria

- [ ] Document 1's fidelity status changes when **document 1's own text**
      changes, proven by a fixture where document 0 is clean — and the inverse
      case is present as the control.
- [ ] `_extra_document_fidelity_status`'s `document-count-invariant` docstring is
      gone because the property is gone, not because the wording was softened.
- [ ] Every per-document leaf is mutation-proven: removed → indexed refusal
      naming that exact leaf; changed → a named case moves, or it is recorded as
      a measured zero-mover with its defence.
- [ ] A two-group and a four-group `citation_pattern` each refuse at resolve
      time, by name.
- [ ] All 28 sealed digests byte-identical; `npm test` 595/595; Python
      `OK (skipped=6)` with `Ran` grown — **`skipped=6` must not move.**
- [ ] No file under `proposal-implementation/` or `proposal-deliberation/` is
      modified.
- [ ] `tests/pair/` and `tests/fixtures/two_documents/` resolve unchanged.
- [ ] The engine emits no cross-document verdict and infers no repair direction.
- [x] The slice table records **A → C → {B, D}** with B's dependency on C stated.
      **Closed after verify (W2).** No literal table anywhere carried the order; the
      Slice A proposal's A/B/C/D listing is archived and, per this proposal's own Q5
      ruling, is not edited. The ordering and its evidence now live in this document's
      own prose (above) AND in Slice A's archive report, which carries a correction
      naming the inversion. That inversion has recurred **twice** in this project --
      once in the Slice A proposal, once in its archive report -- because an A/B/C/D
      listing reads as a sequence to anyone skimming. The evidence, stated wherever
      the order appears: `Data/` becomes demandable only when a document declares a
      dataset, and `**Dataset:**` is enforced solely in the experimental deliberation
      domain -- the mathematical one has none. B before C would ship a branch no
      configuration can reach.

## Size — and how many changes

**Estimate: 1,400–2,300 changed lines.**

The A proposal's **900–1,500** for C is **low**, and the reason is the same one
that made A's own estimate low: it priced the mechanism and not the proof. It
prices neither the two-document drift corpus authored from nothing, nor the
back-compatibility proof that the sibling's profile does not change, nor the
per-leaf mutation suite. A's own design re-derived A from 1,500–2,400 to
2,150–3,300 (**+43%**) for exactly those two omissions; applying the same
correction to 900–1,500 gives 1,290–2,150, and the range above rounds that out.
Every estimate this session came in over except one (865 against an ~870 floor).

| Slice | Delivers | Gate at the end | Estimate |
|---|---|---|---:|
| **C1** | Per-document leaves + resolver tier + indexed refusals + `citation_pattern` group count; document-0 fallback | 28 digests identical; `tests/pair/` unchanged; sibling profile untouched | 450–750 |
| **C2** | The real per-document fidelity fold; 26 reader lines threaded by index | The drift fixture: document 1 moves, document 0 clean | 600–1,000 |
| **C3** | Declare `documents[1]`; delete A's D10 lock; second-document seal cases; `SKILL.md` | Item 2 measured, not asserted | 350–550 |
| | | | **1,400–2,300** |

**Recommendation: three chained changes, in that order — not one.**

The ordering is the whole safety argument, not a convenience. C3 declares the
second document, and declaring it before C2 is precisely the defect C exists to
fix; C2's fixture cannot be authored before C1 gives a second document a
vocabulary to differ in. A single change would put the declaration and the
mechanism in one reviewable unit, where a green suite cannot distinguish "the
fold reads document 1" from "the fixture was written to pass".

Against `review_budget_lines: 1400`, **no single slice above may merge
unstacked**, and C2 alone is at or near the budget — it may need splitting again
at design time (reader threading, then the fold).

```text
Decision needed before apply: Yes
Chained PRs recommended: Yes
400-line budget risk: High
```

## Proposal question round

Interactive mode; this executor cannot prompt. Each question changes the
artifact; the assumption used meanwhile is stated.

1. **Which document did A actually declare at `documents[0]`?** Three committed
   records say `experiments/`; the brief says the mathematical proposal. *Assumed:
   C adds whichever A did not, and nothing below depends on the answer beyond two
   labels.* **This is the one question design cannot start without.**
2. **Do the per-document leaves replace the top-level ones, or overlay them?**
   Replacing forces an edit to `proposal-implementation/impl_profile.py` and
   risks its 28 digests; overlaying keeps a second way to say the same thing.
   *Assumed: overlay with a document-0 fallback, because the sibling-untouched
   bar outranks schema tidiness.*
3. **What makes `missing_provenance`/`untested`/`unreached` per-document?** Each
   currently joins the shared source tree against one claim key. Is a module's
   provenance expected to declare *which* document it implements against, or is
   the per-document split derived from the claim key alone? *Assumed: derived
   from the claim key alone — a provenance schema change is not in C's scope and
   would touch every target's committed `__provenance__`.*
4. **Does `verify` report per-document fidelity for a document whose revision is
   simply absent?** Today that is `"unknown"`, reported and never refused.
   *Assumed: unchanged — `verify` is a reader.*
5. **Should C also correct the slice table in A's proposal, or only record the
   ordering here?** *Assumed: record it here; A is archived work and editing an
   archived proposal is its own decision.*

## Citations checked

Every symbol named above was resolved in source **this session, by name, never by
line, never inherited**: `CLAIM_KEY`, `LOCUS_KEY`, `REMEDY_LOCUS_KEY`,
`NOTATION_KEYS`, `CITATION_RE`, `CITATION_PATTERN`, `DOCUMENTS`,
`DOCUMENTS_DIRECTORY`, `DOCUMENTS_LABEL`, `PRODUCT_DIRS`, `TAG_RE`,
`DISPLAY_BLOCK_RE`, `_impact_class`, `finding_impact`,
`_extra_document_fidelity_status`, `cmd_verify`, `_document_extra_sources`,
`revision_source`, `discover_document_revision`, `document_revision_names`,
`_resolve`, `_REQUIRED_NESTED`, `_REQUIRED_PRESENCE`,
`IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE`, `reachable_refusal_codes`,
`_AUTHORIZATION_BINDING_KEYS`, `proposalDigest`.

**Three inherited claims were re-measured and corrected:**

1. The brief's *"`**Dataset:**` is enforced only in `preservation-experimental.ts`
   (8 occurrences)"* — measured: 8 across **three** files
   (`preservation-experimental.ts` 4, `SKILL.md` 3, `profile.ts` 1), all under
   `experimental-deliberation`. `preservation-math.ts`: **zero**. The conclusion
   (B depends on C) stands; the attribution did not.
2. The brief's *"seven archived changes"* under `openspec/changes/archive/2026-09-1*`
   — measured: **six** match that glob (14 archived in total).
3. The brief's *"A shipped the skill with a single document — the mathematical
   proposal"* — contradicted by three committed records. Reported above as Q1,
   **not** silently resolved.

**Two citations could not be checked** and are reported as unchecked rather than
repeated as fact: `.claude/skills/experimental-implementation/impl_profile.py`
and everything under `tests/` are under concurrent write by the Slice A apply
run, and this session has no shell to read the pinned ref `e3e1438`. No test
suite was run, for the same reason.
