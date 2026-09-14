# Proposal: The Contract Is Data, Not Code

## Intent

`sections/` holds ten prose contracts. A skill that reads them must interpret them, and
interpretation is exactly how `sections/` ends up copied inside the skill. Give each contract a
mechanical header, so the skill reads structure and never prose — and a user who rewrites, adds,
reorders, or deletes a contract still has a working skill.

## Scope

### In Scope

- **Ten fact ids, closed**: `formulation`, `contributions`, `problem-statement`, `gap`,
  `dataset`, `experimental-design`, `implementation`, `results`, `limitations`, `skeleton`.
  `implementation` is the target repository as code; `results` are the numbers it produced. An
  eleventh name is a named refusal, never a guess.
- **`requires_declarations`**: operator-supplied inputs derived from no fact — author roles,
  grant title and code, repository URL, the journal's keyword bounds and classification line.
  This change names them in the header and reports them missing; a later phase gates them.
- **Front matter** per contract: `section`, `position` (rendering place in the finished
  document), optional `after: [<section-id>]`, and `blocks` in order, each with `id`,
  `requires_facts`, `requires_declarations`, `citations` (`discovery` | `resolution` | `none`),
  `optional`, and its own optional `after`.
- Header added to all ten contracts. **Every byte below it unchanged.**
- **Readiness**, per section and per block: writable, or blocked naming each missing fact and
  each missing declaration.
- **Writing order derived from the block graph.** Never a literal list.
- **Two mutations, executed**: an invented eleventh contract enters the plan with no code
  changed; a fact outside the ten refuses `UNKNOWN_FACT`.

### Out of Scope

`paper/`, the substitution engine, `main.tex`, declaration collection and its gate, the guidance
registry, agents, MCP, citations, figures.

## Capabilities

### New Capabilities

- `section-contract`: the front-matter interface, the ten-fact vocabulary, the declaration
  vocabulary, the citation regime, and the refusals for anything outside them.
- `writing-readiness`: per-block readiness, and the writing order derived from the block graph.

### Modified Capabilities

None.

## Settled interfaces

| Decision | Consequence in the header |
|---|---|
| The **block graph is authoritative**; a section order is a human-readable summary of it | Introduction blocks 1, 2 and 4a precede Related Work; its block 3 carries `after: [related-work]` and the section does not move as a unit |
| **`position` is a rendering fact**, independent of writing time | Back matter's last place is `position`, not a dependency |
| **`after` is transcribed, never invented** | Exactly three contracts state a section edge in their own prose: `07` (the abstract compresses this section), `09` (every keyword appears in the body), `06` block 3 (it summarizes Related Work). A contract stating no edge gets no `after` |
| **Facts and declarations are different requirements** | Back matter requires zero facts and several declarations — which is why an unqualified fact sort put it first, and why that sort meant nothing |
| **One contract block = one substitutable region = one id** | This change owns the id's *meaning*; the sibling change `only-the-block-changes` owns its *shape*. Neither encodes the other's knowledge |

## Approach

Fail-closed CLI over the ten files, `proposal-implementation`'s shape. Parse only front matter;
pass prose through untouched. The fact vocabulary, the declaration vocabulary and the refusal
roster each derive from one declaration, `skill-audit` style, so an unclassified value goes red
rather than silent.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `sections/*.md` | Modified | Front matter prepended to all ten. Prose untouched. |
| `.claude/skills/paper-writing/` | New | Contract reader, readiness, derived order, refusals. |
| `tests/` | New | Red-first; both mutations executed, never asserted. |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Prose mutated while inserting headers — ten files edited mechanically | Medium | Byte-clean body digest per file before and after; a single changed byte fails. Nothing else is accepted as evidence |
| An `after` edge invented rather than transcribed | Medium | Each `after` cites the sentence it transcribes; a test asserts the edge set is exactly those three |
| The eleventh-section mutation passes vacuously — an invented contract built from the schema the reader was written against proves round-tripping, not generality | Medium | It must declare a combination **none of the ten shipped contracts use**: an unused fact combination, or a block ordering no shipped contract has |

## Rollback Plan

`git revert` the change commit. The ten contracts return to headerless prose; nothing reads them
yet, so no consumer breaks.

## Dependencies

- `sections/` as committed on `paper-writing`: ten files. `ORDER.md` was deliberately deleted and
  its cross-section couplings written into the individual contracts; that is the intended state.
- The block id shape from `only-the-block-changes` — settled, not open.

## Success Criteria

- [ ] All ten contracts carry front matter; each body byte-identical to its committed form, by digest.
- [ ] Readiness reports every block of every section, writable or blocked by a named fact or declaration.
- [ ] Back matter reports zero missing facts and its declarations as missing.
- [ ] The eleventh-contract mutation uses a combination no shipped contract has, and enters the plan with zero code changed.
- [ ] The out-of-vocabulary fact refuses `UNKNOWN_FACT`, observed by execution.
- [ ] The derived writing order places Related Work before introduction block 3 and after blocks 1, 2, 4a; `position` reports the rendering order separately.
