# Proposal: Each Document Names Its Own Revision

> **Budget note.** This proposal exceeds the 450-word guidance, on the precedent
> `implementation-document-binding` set. The defect is invisible precisely because
> it reads green; naming the evidence is the proposal's whole work.

## Intent

Cut 3 (`a-revision-is-two-documents`) delivered exactly what it specified. Its
specification encoded an assumption nobody tested against the real publishers:
**one revision NAME resolved against N document roots.** `revision_source`'s own
docstring states it — "a revision is the pair of files that name shares across
`DOCUMENTS[0]`'s and `DOCUMENTS[1]`'s roots, not two independently-named
artifacts."

The two real publishers can never produce a shared name (measured in
`.claude/skills/*/profile.ts`):

| skill | `directory` | `stem` | `revisionPattern` |
|---|---|---|---|
| `proposal-deliberation` | `proposals` | `research-concept` | `r` |
| `experimental-deliberation` | `experiments` | `experiments` | `v` |

`proposals/research-concept-r01.md` against `experiments/experiments-<slug>-v01.md`.
No filename exists that both would emit.

**The failure reads green.** Three measured facts compound it:

| Fact | Where |
|---|---|
| Discovery takes no index — it searches `proposals_root()` alone | `revision_discovery` |
| An unreadable second document answers `sha256: None` and does not refuse | `_extra_document_revisions` |
| The fixture writes ONE filename into BOTH roots | `TwoDocumentLifecycleTests.REVISION`, `TwoDocumentPositionWriteTests.REVISION` |

The third is the shape this project has already paid for: a guard exercised only
by data written to satisfy it. Cut 3's own verify ruled the cross-document
*agreement* verdict out for exactly that reason; the same failure sat one layer
down, unnoticed.

**Consequence.** Verifying against the latest experiments document, and validating
against both on re-invocation, are unreachable today — and nothing says so.

## Scope

### In Scope

- **The resolution rule.** `revision_source(revision, index)` stops meaning "one
  name, N roots". Its docstring is the wrong claim and goes with it.
- **Per-document derivation.** Where document N's revision name comes from. See
  the open decision below.
- **Per-document discovery.** `revision_discovery` / `latest_revision` gain the
  index they never had; `cmd_verify`'s `family` seed becomes per-document.
- **The silent null refuses.** `_extra_document_revisions` refuses on an
  unreadable declared document instead of reporting `sha256: None`. A new refusal
  code joins `reachable_refusal_codes`'s derived roster.
- **One-name consumers**, each judged: `_extra_document_fidelity_status`,
  `admissibility_record`'s extra-document staleness loop, both
  `sources_by_document` constructions (`cmd_admit`, `cmd_verify`), and anything
  else the design phase finds. **This list is not assumed complete.**
- **The fixture stops lying.** `tests/pair/corpus.py` and
  `tests/test_implementation_pair.py` adopt two stems, two directories, two
  version letters — the real pair's shape.
- **Correction, folded in:** the live spec
  `openspec/specs/implementation-engine-neutrality/spec.md` cites
  `unreached_mathematics` twice. Cut 2 renamed it `unreached_modules`. A live
  spec naming a symbol that does not exist is the `_POSITION_HEADER_RE` class of
  defect. Two lines; cheaper folded in than chased separately.

### Out of Scope

| Deferred | Reason |
|---|---|
| Creating `experimental-implementation` | The next change; this one unblocks it |
| The `vocabulary.names` collision | Belongs to the skill. `benchmark` (88), `experiment` (23), `baseline` (20) are general engine machinery, not leakage; both precedents resolve it by declaring only the namespace word. **Stated because a reader will wonder.** |
| `KitAgreementLockTests._profile`'s hardcoded `proposal-implementation` | `KIT_DIR` is hardcoded beside it, so the lock is per-kit. It binds only when a SECOND `impl_profile.py` exists — which the next change creates. It belongs there. |
| Any rename of `proposalDigest` or its relatives | — |
| The cross-document agreement VERDICT | Cut 3's recorded boundary; still has no neutral formulation |
| M2, F6 | Carried |
| Cut 3's carried SUGGESTION (a self-flagging close note) | Low priority; fold into this change's own close if cheap |

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `implementation-document-binding`: add the per-document naming rule (each entry
  in `documents` names its own revision; the shared-name reading is refused) and
  the refusal requirement (a declared document whose revision cannot be read
  refuses at every binding-write site, never reports a null sha).
- `implementation-engine-neutrality`: **text-only citation correction**
  (`unreached_mathematics` → `unreached_modules`, two occurrences). No
  requirement behaviour changes.

## Approach

**The carriers already permit it.** Measured: the position header's `documents=`
group (`impl_position._encode_extra_documents`), `admissibility.json`'s
`documents` list, and every ledger event's `documentRevisions` each carry a
per-entry `revision` STRING. Every producer simply fills that slot with the same
string today. **So this is a derivation defect, not a schema defect** — which is
what keeps `_AUTHORIZATION_BINDING_KEYS` a literal 8-tuple and leaves every
already-committed record's digest untouched.

**The refusal lands only on writers.** All consumers of
`_extra_document_revisions` are binding-write sites (`cmd_admit`, `cmd_position`,
`cmd_gate`, `cmd_offer`, `cmd_close`, `_authorization_binding`). `cmd_verify`'s
fidelity fold does not use it — it goes through
`_extra_document_fidelity_status`, which already answers a named `"unknown"`
rather than a null. So refusing here does not contradict `revision_discovery`'s
standing "reported, never refused; `verify` is a reader" stance.

**Red first, by reshaping the fixture.** Slice 1 makes the fixture tell the
truth; the existing pair tests go red on their own, with no assertion edited.
That red IS the control this project keeps asking for — a measurement of an
absence with something that could have seen a presence.

### Open decision for sdd-design

Where does document N's revision NAME come from? Three candidates, none chosen
here:

1. An explicit per-document CLI argument beside `--revision`.
2. Per-document discovery seeded from that document's own directory.
3. Read back from the carrier — the position header and `admissibility.json`
   already record document N's bound revision by label.

(2) and (3) differ sharply on first invocation, when nothing is bound yet.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/_core/implementation/engine/implementation_engine.py` | Modified | `revision_source`, `revision_discovery`, `latest_revision`, `_extra_document_revisions`, `_extra_document_fidelity_status`, `admissibility_record`, both `sources_by_document` sites |
| `tests/pair/corpus.py`, `tests/fixtures/two_documents/impl_profile.py` | Modified | two stems, two directories, two version letters |
| `tests/test_implementation_pair.py` | Modified | the shared `REVISION` constant splits per document |
| `tests/test_proposal_implementation.py` | Modified | the `index=1` fixture writing `r1.md` |
| `openspec/specs/implementation-document-binding/spec.md` | Modified | delta |
| `openspec/specs/implementation-engine-neutrality/spec.md` | Modified | citation correction only |
| `.claude/skills/proposal-deliberation/**`, `_core/deliberation/**` | **Unchanged** | structurally, per `proposal-deliberation/SKILL.md` |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| A seal digest moves | Low | 28 digests are document-0-only; every change is gated on `len(DOCUMENTS) > 1`. Any movement is a defect, never a new golden. |
| The authorization binding shape grows | Low | The carriers already hold per-entry `revision`. `_AUTHORIZATION_BINDING_KEYS` stays a literal 8-tuple carrying `proposalDigest`; the ninth key arrives by presence. |
| The new refusal is unreachable, or reachable only by a fixture written to satisfy it | **Med** | The reshaped fixture is a genuinely two-named pair; mutation-prove the refusal, and pick a mutation a weaker lock would survive. |
| The "anything else that assumed one name" list is incomplete | **Med** | Named as a design obligation, not a proposal claim. Derive the set; do not inherit this list. |
| Size overrun | **High** | See below. Chained slices, pre-authorized by `auto-chain`. |

## Rollback Plan

Three slices, each its own PR on the chain. Revert the chain tip-first. No
committed target artifact changes shape, so no clone's
`.implementation/position.jsonl` needs migration at any point — revert is a code
revert, not a data one.

## Dependencies

None external. Blocks the next change (`experimental-implementation`).

## Success Criteria

- [ ] Two genuinely different revision names, in two different directories, with
      two different version letters, resolve and bind end to end.
- [ ] Reverting the per-document resolution reddens a test — proven by mutation,
      not by reading the roster.
- [ ] A declared document whose revision cannot be read refuses, by code, at
      every binding-write site. No `sha256: None` reaches any carrier.
- [ ] `sha256(tests/seal/digests.json)` unmoved:
      `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75`
      (inherited from the launch brief; **not verified in this phase — no shell**).
- [ ] `npm test` 595/595; Python `Ran` may grow, `skipped=6` must not move.
- [ ] `rg unreached_mathematics openspec/specs/` returns nothing.

## Proposal question round

Answer, skip, correct the framing, or ask for a second round.

1. **Derivation.** Of the three candidates above, which should document N's
   revision name come from on a FIRST invocation, when no carrier has recorded
   one yet — an explicit argument the operator types, or discovery inside that
   document's own directory?
2. **Refusal blast radius.** Should a declared-but-unreadable second document
   refuse at every binding-write site, or only where a token is minted
   (`offer`/`gate`)? The first is stricter and can block a `position` write on a
   document the operator has not published yet.
3. **Re-invocation.** "Validate against BOTH" — is disagreement between the two
   documents a REFUSAL, or a reported status the operator decides on? Cut 3
   ruled the verdict out of the engine for lacking a neutral formulation; this
   change can report the pair without judging it.
4. **Slicing.** Three chained PRs (fixture-red → resolution → refusal), or one?
5. **Kit lock.** Confirm `KitAgreementLockTests._profile` defers to the next
   change, where the second `impl_profile.py` actually appears.
