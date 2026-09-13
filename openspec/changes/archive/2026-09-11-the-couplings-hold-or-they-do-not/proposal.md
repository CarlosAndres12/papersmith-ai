# Proposal: The Couplings Hold Or They Do Not

## Intent

Ten contracts state obligations that span two sections. Nothing checks them, so a finished
`paper/main.tex` can satisfy every section alone and be incoherent across them. `verify` is a
read-only report that says which couplings hold, which need a human, and which nobody can reach —
and refuses rather than reporting green when it cannot look.

## Scope

### In Scope — the classification is the deliverable

| # | Coupling | Verdict | Fails on |
|---|---|---|---|
| 1 | Contribution list: count, order, naming across intro 4b / methods slot 3 / abstract slot 4 / conclusions block 1 | **mechanical** | four ordered string lists not equal |
| 2 | Chain problem→contribution→property→instrument→evidence, same words per link | **mechanical** | set closure; token inequality. The contract demands identity, not synonymy — string equality *is* its test |
| 3 | The gap in intro block 3 and related-work block 4 | **assisted** — presence and front-count are mechanical; "same thing at different depths" is a reading | both closings and their front lists published for a human |
| 4 | Results artefacts locatable in the setup diagram; no box shared with the methods diagram | **mechanical** | cell ∉ declared cells; non-empty intersection. The methods side is *derived* from coupling 1, not declared twice |
| 5 | Future work ⊆ limitations, one reference per direction | **mechanical** for direction→limitation totality and the shared citation key (contract 04, movement 5); **out of reach** for "relevant" and "specific enough to be a paper" | a direction answering no declared limitation |
| A | `\cite` ↔ `refs.bib`, both directions as sets | **mechanical**, both halves derived from the document, no declaration anywhere | dangling cite (hard); orphan entry (reported) |
| B | Blocks standing against a changed contract hash | **out of reach today** | refuses `CONTRACT_RECORD_ABSENT` |

Every coupling reads **declared data** from the block record, never prose. A declared name must
also occur literally in its block's bytes — presence proves the words are there, never that the
block enumerates them. That limit ships in the payload.

`unmeasured` is a third value, never folded into pass.

### Out of Scope

Writing, repairing, rendering, compiling, extent/word-count checks, register proportions, reading
any diagram image, and writing the declaration record.

## Capabilities

### New Capabilities
- `coupling-verification`: the five couplings, the verdict vocabulary, `unmeasured`.
- `citation-integrity`: the two-way `\cite`/`refs.bib` set comparison.
- `contract-currency`: stale-contract reporting, refusing when the record is absent.

### Modified Capabilities
- `block-substitution`: `verify` joins the CLI. No engine change.

## Approach

`skill-audit`'s shape: derive both sides where possible, report, never repair. Exit `0` for any
verdict including findings; exit `2` only for inability to look. Fixtures carry a fully-declared
synthetic paper so every check is proven reachable-red and reachable-green now, without waiting on
phases 3–7.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/paper-writing/scripts/paper_verify.py` | New | The seven checks |
| `.claude/skills/paper-writing/scripts/paper_cli.py` | Modified | `verify` verb |
| `.claude/skills/paper-writing/SKILL.md` | Modified | Verb table, refusals, decision gates |
| `tests/test_paper_writing.py` | Modified | Red-first; mutations executed |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| **Every check green because nothing was declared** | High | M6: empty the record, run `verify`. It must refuse, not pass. This is the change's most important test |
| Declarations agree with each other and not with the paper | High | Declared-name literal presence in block bytes; its limit stated in the payload |
| Check B iterates an absent record and reports zero stale blocks | High | Refuses `CONTRACT_RECORD_ABSENT`; M7 deletes the record and observes the refusal |
| A synonym matcher passes by containment | Med | M2 substitutes a synonym that is not a substring of the original |
| A mutation runs against a cached `.pyc` | Med | `PYTHONDONTWRITEBYTECODE=1` in every child env, per `skill-audit` |
| No sibling phase ever writes the record | Med | Named as a dependency, not assumed. `verify` refuses visibly rather than degrading |

## How to break it — mutations, executed, not asserted

M1 reorder two contribution names · M2 synonym at one chain link · M3 dangling cite, then orphan
entry (two mutations; one direction firing proves nothing about the other) · M4 cell that does not
exist, then a contribution name added to the setup diagram · M5 direction answering no limitation ·
**M6 empty declaration record → must refuse** · M7 absent contract record → must refuse.

## Rollback Plan

Remove `paper_verify.py`, the CLI verb, and its tests. `verify` writes nothing, so rollback
destroys no user data and `paper/` is untouched.

## Dependencies

- `the-contract-is-data-not-code` — the front-matter reader. Real, on disk.
- **Unresolved**: the prompt cites `openspec/changes/the-paper-carries-its-own-decisions/` as the
  owner of the per-block contract hash. **That directory does not exist**, on disk or in Engram
  (searched both). Check B is specified against an interface nothing implements yet, and ships
  refusing.
- A per-block declaration record. No landed phase writes one. See question 1.

## Success Criteria

- [ ] Each of the seven checks is proven reachable-red by its named mutation, run and recorded.
- [ ] M6 and M7 observed refusing; neither reports clean.
- [ ] `unmeasured` is reachable and never counted as pass.
- [ ] Every refusal code derived from source, not hand-listed.
- [ ] The assisted finding (coupling 3) publishes both texts and never self-resolves.

## Proposal question round

Answering these sharpens the proposal; skipping accepts the assumption beside each.

1. **Where do block declarations live?** Assumed: a record beside `paper/`, read-only to `verify`.
   Phase 1 rejected a sidecar *offsets* index; names are content, not offsets. If declarations
   belong in the marker line instead, coupling 1 changes shape.
2. **A hand-written or `--adopt`ed block has no declarations.** Assumed: `unmeasured`, reported,
   never green. Or should `verify` refuse outright?
3. **Is an orphan `refs.bib` entry a failure?** Assumed: reported, not failed — it renders nothing,
   while a dangling `\cite` renders `[?]`.
4. **Who closes an assisted finding?** Assumed: an unanswered assisted item is never clean, and
   `verify` neither answers nor gates it.
5. **Check B's record owner does not exist.** Assumed: this change defines the read interface and
   refuses; it does not write the record. Should it define the record instead?
