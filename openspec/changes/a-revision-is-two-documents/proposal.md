# Proposal: A Revision Is Two Documents

> **Size note.** Over the 450-word budget, deliberately, on the precedent
> `the-domain-crosses-the-seam` set: this cut's central decisions are *where a
> line is drawn*, and a verdict recorded without its argument is what someone
> reverts later. The one that matters most — what Cut 3 refuses to compute — is
> only defensible with its reasoning attached.

## Intent

Cut 1 moved the engine out of the skill. Cut 2 moved the domain out of the
engine. Both left one thing untouched, and it is the last structural blocker
before `experimental-implementation` can exist: **`revision` is a scalar
everywhere.**

That skill must verify code against **both** the latest mathematical proposal
**and** the latest experiments document, and publish a successor of the
experiments document when implementation contradicts it. It cannot, because
every binding in the engine holds exactly one document. Measured at `f4e9960`,
by name:

| Site | Shape today |
|---|---|
| `revisionSha256` | **24 occurrences** in `implementation_engine.py` |
| `revision_source(args.revision)` | one document, **8 call sites** |
| `module["stale"] = bool(revision) and module["revision"] != revision` | one comparison |
| `admissibility_record` | compares one `revisionSha256`, returns one `revision` |
| `impl_position._BLOCK_OPEN_RE` (+ `_BLOCK_OPEN_MARKER`, `_LEGACY_BLOCK_OPEN_RE`) | `revision=… sha256=…` — one pair, one document |
| `position_state`'s `boundTo` | `"current"`/`"stale"` off that single comparison |
| `_AUTHORIZATION_BINDING_KEYS` | one `revisionSha256` among eight keys |
| `well_formed` | demands a non-empty `id` and nothing else |
| `fidelity_status` in `cmd_verify` | folds four conditions over **one** document |

"Validate against BOTH" converts every one of these from scalar to pair. It is
invisible to a word count and larger than the entire vocabulary extraction.

## The heart of it — `len(documents) == 1`

`documents` becomes a **list** in the profile, and every scalar field's wire
shape stays **conditional on `len(documents) == 1`**. `proposal-implementation`
declares exactly one document, so every byte it emits is unchanged — proven by
28 sealed digests, not asserted. A second document is what makes the pair
appear.

**The conditional is also this cut's hardest problem.** A branch no reachable
configuration takes cannot be mutation-proven, and by this project's own
standing rule — *a profile field nothing reads is the shape of a false guard* —
an unprovable branch is the same defect one level up. Cut 3 therefore ships a
**two-document fixture profile** and a pair corpus alongside the single-document
seal. A tmpdir fixture profile is already the sanctioned override case: the
resolver's own comment records that a "must live under `FORGE_ROOT`" rule *"was
considered and rejected"* for exactly this, and `test_implementation_domain_lock.py`
globs `*/impl_profile.py` under `.claude/skills/`, so a fixture is not picked up
as a third skill.

## The line this cut draws — and refuses to cross

§B3 names one thing with no analogue in 17,100 lines: **the agreement between
the two documents.** Two documents can each be internally clean and disagree
with each other, and nothing computes that. The decision, argued rather than
assumed:

**Per-document fidelity is in scope. The cross-document verdict is not.**

- *Per-document fidelity* is the same four conditions applied N times.
  `fidelity_status` already folds `stale or missing_provenance or untested or
  unreached`; folding it per document is the identical scalar→pair conversion as
  the other 24 sites, it is engine-shaped, and the two-document fixture proves
  it. Leaving it out would force the new skill to edit the engine to get a
  second fidelity block — precisely what the seam exists to prevent.
- *The cross-document verdict* — what it **means** for a mathematical proposal
  and an experiments document to agree — has no neutral formulation. It is a
  domain judgment. Under one declared document there is no pair, so a verdict
  computed here would be dead in every configuration this repository can reach,
  and the only thing that could exercise it is a fixture written to satisfy it.
  That is a guard validating its own test data. It belongs to the consumer.

**Cut 3 makes the pair representable and provable. It computes no verdict over
it.** That sentence is the whole scope rule, and every §B6 item below is decided
by it.

## Scope

### In Scope

| # | Work | Why here |
|---|---|---|
| 1 | `documents` becomes a **list**; the resolver validates each entry **by index** (`documents[1].directory`), with `_REQUIRED_ABSOLUTE_ONLY`'s single-pair tier restructured per entry | The profile is where the count is declared |
| 2 | The **24 `revisionSha256` sites** and the 8 `revision_source(args.revision)` call sites become document-aware, wire shape gated on `len == 1` | F2's whole subject |
| 3 | `impl_position.py`'s header binds N revisions + N shas; the writer and both openers round-trip | The header is the position ledger's own binding |
| 4 | `_AUTHORIZATION_BINDING_KEYS` carries a pair **only** under two documents | See the risk below — this one can damage clones |
| 5 | `admissibility.json` keyed by document, **reading the scalar shape as valid** under one | An existing ruling on disk must not vanish |
| 6 | `well_formed` demands `document` **when `len(documents) > 1`**; under one it is implied | §B6.1, without refusing every `tests/findings.py` already written |
| 7 | `finding_impact`'s `class` becomes per-document; a finding may **name both** | §B6.4's *representation*, not its verdict |
| 8 | Per-document `fidelity` fold in `cmd_verify` | Argued above |
| 9 | A **two-document fixture profile** + pair corpus + per-branch mutation proof | Without it, items 2–8 are false guards |

### §B6, item by item — the four decisions the brief asked for

| §B6 item | Ruling | Argument |
|---|---|---|
| 1. finding names its document; `well_formed` demands it | **In — conditionally** | Demanding it unconditionally refuses every populated `tests/findings.py`, including the seal corpus's own. A digest moves; the cut fails its bar. Gate on `len > 1` and the silent-routing hole is closed exactly where it can bite |
| 2. call sites take the document as an argument | **In** | `finding_impact`/`adoption_state` already take `source`. The scalar is upstream, in `remedy_compatibility(findings, revision)`, `admissibility_record(target, revision)` and the 8 `revision_source(args.revision)` sites. Not separable from item 2 of the table above |
| 3. `admissibility.json` keyed by document | **In, with dual-shape read** | It is a persisted artifact in a target repository. A write-only migration silently invalidates every ruling already on disk |
| 4. `handoff` reports the cross-document consequence | **Split** | The `local`/`structural` binary becoming a per-document mapping is the same scalar→pair work: **in**. What word to print when a finding is against both, and how the operator routes it, is a verdict: **out**, with the skill |

### Out of Scope

- **The cross-document agreement verdict** — argued above. Recorded, not built.
- **Any rename of `proposalDigest`**, `GATE_PROPOSAL_*`, `_proposal_digest`,
  `_verify_gate_proposal`, `_gate_proposal_question`, `_verify_optional_election`,
  `cmd_propose`, `_authorization_binding`, `_verify_gate_authorization`,
  `_campaign_identity`, `_load_remote_execution_*`. `CampaignProposalExclusionTests`'
  three layers already enforce this and **must not be weakened**. Its L2 asserts
  `proposalDigest` is still in `_AUTHORIZATION_BINDING_KEYS`; item 4 above changes
  that tuple's *value shape* under two documents and must leave its *membership*
  and its one-document bytes untouched.
- **`compose` / M1** — LaTeX end to end (`DISPLAY_BLOCK_RE`, `TAG_RE`); an
  experiments document has neither `$$` nor `\tag{}`. An **open operator
  decision**. Named, not taken.
- **M2** — `cmd_handoff`'s hardcoded Spanish. Recorded unresolved.
- **M5** — the derived-denylist lock layer, deferred until a second profile
  exists. A `skipTest` would move the pinned `skipped=6`.
- **F4 / B4 / M3** — `plan` has no `--revision` and `Data/` is not demandable.
  It touches the same argument this cut is about and is **not** part of it.
- Creating `experimental-implementation` itself. **F6** (`MANAGED_ARTIFACT_MARKER`'s
  four spellings).

## Capabilities

### New Capabilities

- `implementation-document-binding`: the wire shape of every revision binding —
  scalar under one declared document, pair under two — and the stability
  guarantee for artifacts already written into target repositories
  (`position.jsonl` gate tokens, `admissibility.json`, the `AGREED.md` position
  header). `implementation-engine-neutrality`'s own Purpose states it governs
  *"not … the scalar→pair revision shape (Cut 3)"*; this is that capability.

### Modified Capabilities

- `implementation-engine-neutrality`: its Cut-2 requirement table names
  `documents.directory` and `documents.label` as single leaves. They become
  per-entry leaves of a list, refused by index. Nothing else in that spec moves.
- `implementation-cli-seal`: the seal gains the two-document branch as its own
  corpus; and its `Non-Interference` requirement pins `Ran 2849`, which is
  already stale at `f4e9960` (`Ran 2874`). The invariant that has actually held
  across three cuts is **`skipped=6`**. Restate the pin as `skipped=6` with `Ran`
  free to grow — a spec-level correction, recorded here rather than applied
  silently.

## Approach

Red-first, one binding site class at a time, each landed with its mutation
before the next — Cut 2's method at a harder bar.

**Commit granularity, fixing the gap Cut 2 carried.** Cut 2 recorded that
bundling RED tests with their implementation in one commit destroys the
git-verifiability of RED-first. Every work unit here lands as **two commits**: a
`test(...)` commit carrying only the failing test(s), then the implementation
commit. The RED commit must be individually checkoutable with the test red at
it. Cost: roughly double the commit count, **zero** changed lines.

**Order.** (a) profile list + resolver, no wire shape moves at all; (b) the
fixture profile and pair corpus, so every later branch has an instrument before
it exists; (c) the 24 sites, the position header, the binding, admissibility,
findings routing, fidelity — each with its own two commits.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/_core/implementation/engine/implementation_engine.py` | Modified | the 24 sites, the 8 call sites, `well_formed`, `finding_impact`, `remedy_compatibility`, `admissibility_record`, `cmd_admit`, `cmd_handoff`, `cmd_verify`'s fidelity fold |
| `.claude/skills/_core/implementation/impl_position.py` | Modified | header regexes, `header` dict, the writer |
| `.claude/skills/_core/implementation/impl_domain_profile.py` | Modified | list-shaped `documents`, per-index refusals |
| `.claude/skills/proposal-implementation/impl_profile.py` | Modified | `documents` becomes a one-entry list |
| `tests/fixtures/` | New | the two-document profile + pair corpus |
| `tests/test_implementation_domain_mutation.py` | Modified | per-branch mutation, `MEASURED_MOVERS` extended |
| `tests/test_implementation_domain_lock.py` | Unchanged | `CampaignProposalExclusionTests` must stay as-is |
| `tests/seal/` | **Unchanged** | `git diff --exit-code` must exit 0 |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| **A minted gate authorization stops validating.** The token is `sha256` over `{**own_binding, session, at, mintOrdinal}` with `sort_keys=True`. *Any* change to that dict's shape moves every token — in `position.jsonl`, a ledger that travels in clones. Same damage class as F1, for a **value** rather than a name | **High** | Under one document the binding dict is byte-identical, key name unchanged. A dedicated test re-derives a token from a committed fixture binding and asserts the digest is unchanged. This test lands **first**, before item 4 |
| A sealed digest moves | **High** | The whole cut is judged on it. Land one site class at a time, re-run the seal per class, never batch |
| The pair branch ships unproven — the false-guard shape | **High** | Scope item 9 is not optional and lands before the branches it proves |
| A "this branch does not move a digest" reading is a harness artifact | Med | A **positive control that does move one** runs first, in the same harness, under `.venv/bin/python`. An earlier Cut-2 pass under system `python3` broke `CLI_INVOCATION` and crashed every subprocess identically on both sides, which reads as "zero movers" for every leaf |
| An existing `admissibility.json` or position header is silently invalidated | Med | Dual-shape read, asserted from a fixture written in the scalar shape. `_LEGACY_BLOCK_OPEN_RE` already keeps a legacy opener readable — the precedent is in the file |
| A new refusal moves `reachable_refusal_codes()`'s pinned count | Med | Re-assert it; move it only for a genuinely added refusal and record the new number |
| This design's predictions about which digests move are treated as facts | Med | Cut 1 predicted a git rename similarity reproducing at no threshold and predicted movers that did not move. **Every number in design is a claim until verify measures it** |
| The scope creeps into the cross-document verdict | Med | The scope rule is one sentence and is quoted in tasks |

## Rollback Plan

Revert per slice. `tests/seal/` is untouched by construction, so the pre-change
seal is the post-revert seal. **One asymmetry:** if item 4 has landed and any
target minted an authorization under a two-document profile, that token was
minted under a shape that has never existed in this repository (which declares
one document), so no `proposal-implementation` ledger can hold one. Reverting
before a second skill exists is therefore clean; after one exists, it is not,
and that is the point at which this becomes irreversible.

## Dependencies

- `the-engine-leaves-its-skill` and `the-domain-crosses-the-seam` archived (both
  are), 28 sealed digests green at `f4e9960`.
- `.venv/bin/python` (3.12). Bare `python3` is 3.9 and cannot import these
  modules.

## Success Criteria

- [ ] All **28 sealed digests byte-identical**; `git diff --exit-code tests/seal/`
      exits 0. **Zero declared delta.**
- [ ] A committed-fixture gate token re-derives to the **same digest** after item
      4; `proposalDigest` membership in `_AUTHORIZATION_BINDING_KEYS` unchanged;
      `CampaignProposalExclusionTests` unedited and green.
- [ ] The two-document fixture profile resolves, and **every** pair branch is
      exercised by the pair corpus — each one named, with the case that reaches it.
- [ ] Each branch is mutation-proven **both ways**: collapsing it to the scalar
      path reddens a named test, and a positive control that genuinely moves a
      digest ran first in the same harness.
- [ ] Removing `documents[1].directory` refuses by that **exact indexed name**.
- [ ] An `admissibility.json` and an `AGREED.md` position header written in the
      scalar shape still read under one document, asserted from committed fixtures.
- [ ] Every work unit has a **`test(...)` commit that is red at its own sha**,
      verified by checkout, not by claim.
- [ ] `npm test` **595/595**; `.venv/bin/python -m unittest discover -s tests`
      **OK, `skipped=6`** — `Ran` may grow, `skipped` must not. Outputs pasted
      before and after.

## Size Forecast — it does not comfortably fit

Authored changed lines, honestly estimated and **not compressed to reach a
number**:

| Work | Lines |
|---|---|
| engine: 24 sites + 8 call sites + findings routing | 350–450 |
| `cmd_verify` per-document fidelity fold | ~60 |
| `impl_position.py` header pair | ~80 |
| resolver list validation, per-index refusals | ~90 |
| `impl_profile.py` `documents` list | ~40 |
| authorization binding shape + its dedicated token test | ~110 |
| two-document fixture profile | ~120 |
| pair corpus + harness | ~200 |
| mutation + back-compat tests | ~350 |
| **Total** | **~1,400–1,500 (±150)** |

**Decision needed before apply: Yes**
**Chained PRs recommended: Yes**
**1400-line budget risk: High**

At best it lands exactly on the budget; at worst 8% over, and the estimate's own
error bar is larger than its headroom. **State plainly: this is not a
single-PR-sized change,** and compressing the scope to make the number work would
mean shipping the pair branch without the fixture that proves it.

**Proposed chain, split along a seam that is itself provable:**

- **Slice A — the pair becomes representable (~480 lines).** `documents` a list;
  resolver per-index validation; every engine read routed through an accessor
  that returns exactly today's value at `len == 1`; the two-document fixture
  profile and pair corpus. **No wire shape changes at all**, so A is a pure
  zero-delta cut provable by the existing seal alone.
- **Slice B — the scalar bindings become conditional pairs (~950 lines).** The
  24 sites, position header, authorization binding, admissibility, findings
  routing, per-document fidelity. Every byte-risk lives here — and A has already
  built the instrument that proves B's new branch is reachable.

The operator decides. A single oversized PR with an accepted `size:exception` is
the alternative; splitting is recommended.

## Proposal Question Round

Five decisions this proposal took. Each is answerable now or correctable at
design; none blocks writing specs.

1. **The cross-document agreement verdict goes to the skill, not here.** Assumed:
   out. The argument is that it has no neutral formulation and nothing reachable
   in this repository could prove it. Correct this if the intent was for the
   engine to own a domain-neutral *shape* for the verdict even without its content.
2. **Per-document `fidelity` stays here** even though the verdict leaves. Assumed:
   in — otherwise the new skill must edit the engine to get a second fidelity
   block, which is the coupling the seam removes.
3. **`well_formed` demands `document` only when `len(documents) > 1`.** Assumed:
   conditional. Unconditional would refuse every `tests/findings.py` already on
   disk and move a sealed digest.
4. **A finding may name BOTH documents**, and `impact["class"]` becomes a
   per-document mapping. Assumed: yes, as representation. What `handoff` *prints*
   for such a finding is the skill's.
5. **The A/B chain over a single oversized PR.** Assumed: chained, per the
   forecast above. The brief invited this decision explicitly; it is the
   operator's.

## Citations Checked

Located **by name** in the source during this phase, never inherited by line:
`revisionSha256` (24 occurrences in `implementation_engine.py`),
`_AUTHORIZATION_BINDING_KEYS` (its eight keys and the `sort_keys=True` token
digest in `_verify_gate_authorization`), `_verify_gate_proposal`,
`_proposal_digest`, `well_formed`, `read_findings`, `finding_impact` (and its
`"class": "local" if local else "structural"`), `adoption_state`,
`remedy_compatibility`, `admissibility_record`, `revision_source`,
`revision_discovery`, `cmd_verify` (and its `fidelity_status` four-condition
fold), `module["stale"]`, `boundTo`, `impl_position._BLOCK_OPEN_RE` and its
legacy opener, `impl_domain_profile._REQUIRED_NESTED` / `_REQUIRED_PRESENCE` /
`_REQUIRED_ABSOLUTE_ONLY` / `ImplementationProfileError`, `impl_profile.PROFILE`'s
`documents` block, `tests/test_implementation_domain_lock.py::CampaignProposalExclusionTests`,
`tests/test_implementation_domain_mutation.py::MEASURED_MOVERS` and
`SealCorpusUntouchedTests`.

**Two inherited claims were checked and one did not hold.** The measurement's
F4 states `--revision` is *"registered for eight commands"*; the literal
`"--revision"` appears **4 times** in the engine — a helper may register it more
broadly, so the count was **not repeated** anywhere above. F4 is out of scope
regardless. The `implementation-cli-seal` spec's `Ran 2849` pin is stale against
`f4e9960`'s `Ran 2874`, reported under Modified Capabilities rather than
silently corrected.


---

## Correction: a symbol three artifacts cited and none of them grepped

This proposal originally named `impl_position._POSITION_HEADER_RE` in three
places. **It does not exist.** `grep -rn '_POSITION_HEADER_RE' .claude/skills/`
returns nothing. The real symbols in `impl_position.py` are
`_BLOCK_OPEN_MARKER`, `_BLOCK_OPEN_RE` and `_LEGACY_BLOCK_OPEN_RE`, and all
three references above are corrected to them.

The name travelled from the seam measurement into this proposal and into the
orchestrator's own launch brief, surviving all three because each artifact read
it from the one before instead of from the source. `sdd-design` caught it by
grepping for it rather than repeating it.

The lesson is the one this change already encodes elsewhere and paid for twice:
**an inherited citation is a claim, not a fact.** The same pass also found that
"8 `revision_source(args.revision)` call sites" is **7** — thirteen call sites
total, seven reading `args.revision`, with `cmd_verify` the eighth
revision-consuming *command* but reaching the already-resolved value, which is
the likely origin of the wrong number. Both counts are marked re-derive,
never-repeat.
