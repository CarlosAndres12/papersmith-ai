# Proposal: The Methods Section Produces the Contributions

## Intent

`introduction.block-4b` declares `produces_facts: contributions` while its own prose
(`sections/06-introduction.md:459`) says the list "is inherited, never a drafting target"
and must agree with "the components of the methods section". Header and prose contradict
each other; enforcement is only downstream, after both blocks are written. Operator
ruling: the mathematics is materialized in Materials and Methods, the contributions fall
out of it, the introduction receives them.

Measured side benefit: `block-4b` requires `results`, so every consumer of `contributions`
transitively waits on results today. `mm-proposal` requires only `formulation`.

## Scope

### In Scope

| File | Change |
|---|---|
| `sections/01-materials-and-methods.md` | `mm-proposal` gains `produces_facts: contributions` |
| `sections/06-introduction.md` | `block-4b` drops `produces_facts`, gains `requires_facts: contributions` and an `after` edge to `mm-proposal` |
| 7 consumer files | each `### Internal chain` gains a row naming `materials-and-methods.mm-proposal`, plus a direct `after` edge, each with a literal quote |
| `.claude/skills/paper-writing/SKILL.md:225-229` | re-measure "47 blocks, eight waves 22/7/11/2/2/1/1/1" by running `phases` |

Consumers: `introduction.block-2`, `related-work.rw-synthesis-artefact`,
`experimental-setup.es-assessment`, `results-and-discussion.rd-contribution-blocks`,
`abstract.slot-2`, `conclusions.concl-block-1`, `title-and-keywords.title`.

`sections/*.md` are shipped data, contract-validated — never free-form edits.

### Out of Scope

- Candidates 2 and 3, rejected in exploration.
- `check_contribution_list` never reads the producer side.
- `_verify_producer_duplication` matches `gap` by the coincidence `"gap" in CHECKS`; this
  fact's check is `"contribution-list"`.
- `block-4b`'s pre-existing hard `results` requirement.

Unless design shows one blocks this change.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `fact-production`: scenario "A consumer reads the producer's own words"
  (`spec.md:175-181`) names `introduction.block-4b` as the source of
  `rw-synthesis-artefact`'s components. It becomes false.

## Approach

Candidate 1: move the sole producer. `_verify_producer_reachability` is satisfied
transitively once `block-4b` sits after `mm-proposal`; `_verify_internal_chain` still
demands a **direct** edge per row, which is why six new `after` entries are needed.
`title-and-keywords.title` is exempt — `_position_derived_edges` already yields
M&M→title (abstract 2 < M&M 5 < back-matter 10). No cycle: `mm-proposal`'s own `after`
targets stay inside M&M.

## Open Decision — D2 (owner: `sdd-design`)

`mm-proposal` declares `figure.components_from: "contributions"`, and
`_resolve_expected_components` reads the producer's rendered `main.tex`. As producer, its
diagram checks itself. **Options:** accept the tautology and say so in prose, or redesign
against `block-4b`'s restated text. Do not leave it silent — pattern 2.

**Correction to exploration:** `related-work.rw-synthesis-artefact` also declares
`components_from: "contributions"` (`05-related-work.md:134`). It stays a real
cross-section check, but its referent moves from the introduction to methods.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `sections/01,02,03,05,06,07,08,09` | Modified | producer move, rows, edges |
| `.claude/skills/paper-writing/SKILL.md` | Modified | re-measured wave shape |
| `openspec/specs/fact-production/spec.md` | Modified | delta spec |
| `tests/test_paper_writing.py` | Modified | no test pins corpus order by name today |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| A chain row without its direct edge | High | `CHAIN_ROW_UNBACKED` refuses at assembly |
| Wave shape silently stale | High | re-run `phases`, quote the output |
| D2 decided implicitly | Med | named here, owned by design |
| New tests ratify counts | Med | assert the property, not the number (pattern 7) |

## Rollback Plan

Single-commit revert of the `sections/*.md`, `SKILL.md` and spec edits. No persisted
state, no migration: the producer assignment lives entirely in shipped headers.

## Success Criteria

- [ ] Corpus assembles with `mm-proposal` as the sole `contributions` producer.
- [ ] Each of the seven consumers carries its row and a backing edge.
- [ ] `phases` output re-measured and quoted in `SKILL.md`.
- [ ] D2 decided and recorded in `design.md`.
- [ ] Removing any one new row turns the corpus red under mutation.
