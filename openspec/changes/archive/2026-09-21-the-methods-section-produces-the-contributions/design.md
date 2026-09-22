# Design: The Methods Section Produces the Contributions

## Technical Approach

Header-and-prose change only; no Python changes. `mm-proposal` gains `produces_facts:
contributions`, `block-4b` drops it and gains `requires_facts: contributions`. Every
`after` entry that pointed at `block-4b` **for the contribution list** is retargeted to
`mm-proposal`. **Eight** `### Internal chain` rows change, not seven: the proposal missed
`block-4b`'s own row, which `_verify_producer_chain_rows` demands in `sections/06`.

## Architecture Decisions

### D2 — the Components Check referent (owned here)

`_resolve_expected_components` (`paper_cli.py:2580-2600`) reads the producer's `main.tex`
body through `paper_verify.item_lines`, which matches `^\\item (.*)$` and nothing else
(`paper_verify.py:80`). `mm-proposal`'s contract mandates prose, equations and a diagram —
no itemized list. So **option (a) is not available: the outcome is not a tautology but a
`COMPONENTS_FACT_NOT_A_LIST` refusal.** Option (c) is not available either —
`related-work.rw-synthesis-artefact` (`05-related-work.md:134`) resolves through the same
function, so dropping `components_from` from `mm-proposal` leaves the identical refusal
standing on related work. *Ruled, not measured: `paper/main.tex:66` carries `mm-proposal`
as an empty block, so nothing can be run against real rendered text today.*

**Choice.** Section 01's contract mandates an ordered `\item` roster of contribution names
immediately before the closing diagram pointer, and `components_from` stays on **both**
blocks. This is forced, not preferred: `fact-production`'s *A Produced Fact's Value Is Its
Producer's Own Rendered Text* means a block cannot produce a list fact without carrying the
list.

**Referent honesty (the pattern-2 obligation).** After the move, `mm-proposal`'s check
compares its diagram manifest against its own block's roster — **intra-block drift, not
cross-section corroboration**. Section 01 prose must say that in those words.
`rw-synthesis-artefact` remains the cross-section check; its referent moves from the
introduction to methods, and section 05 prose must say that too.

**Rejected:** resolving against `block-4b`'s restated text. It inverts the spec requirement
above and restores the exact circle this change removes — the methods diagram deriving from
introduction text the introduction is supposed to inherit.

**Falsifiers.** (1) Mutate one roster item in a rendered `mm-proposal` and re-run `render
--section 01 --block mm-proposal`; if it stays green, the guard cannot fire and
`components_from` must be removed from that block. (2) If the operator rules Methods may
not carry a roster, the only admissible remainder is a code-level list-bearing referent plus
an amendment to that spec requirement.

| # | Decision | Rejected | Rationale |
|---|---|---|---|
| D3 | Retarget the six existing `after` entries; never add alongside | keep both edges | a residual edge to `block-4b` keeps every consumer transitively waiting on `results`; the proposal's measured side benefit only materializes if the old edges go |
| D4 | Reuse each entry's existing `source.quote` verbatim | author new quoted prose per file | measured: all six quotes stay true under the inversion, and `block-4b`'s new entry reuses `06-introduction.md:459` "It is inherited, never a drafting target." Zero new quoted prose means `SPAN_NOT_IN_SOURCE` has nothing new to break |
| D5 | Re-run `phases`, quote raw output, date it; add no test pinning wave counts | assert the numbers | pattern 7 — a count test guards a choice. The property test asserts every block's dependencies land in a strictly earlier wave |

## Data Flow

    mm-proposal (produces contributions, \item roster)
       │  ├─ own diagram ─── intra-block drift check
       │  ├──→ block-4b (restates the list)  ── new after + new row
       │  └──→ rw-synthesis-artefact ── cross-section components check
       └──→ block-2, es-assessment, rd-contribution-blocks, slot-2, concl-block-1
                                          (retargeted after + row)
    mm-proposal ──(position-derived, 2 < 5 < 10)──→ title   (row only, no after)

Cycle check, measured from section 01's complete header: no `after` entry outside
`materials-and-methods` targets it, and `_position_derived_edges` holds only
`title-and-keywords`. Nothing enters M&M, so the inversion cannot produce `ORDER_CYCLE`.
`derive_order`/`derive_waves` must still be run to confirm.

## File Changes

| File | Action | Description |
|---|---|---|
| `sections/01-materials-and-methods.md` | Modify | `produces_facts` (quote `This section defines the contributions.`); mandate the ordered roster; invert naming-authority prose at 104-105, 182, 186-188, 217-218, 356; state the intra-block reading of its own Components Check |
| `sections/06-introduction.md` | Modify | `block-4b` producer→requirer, new `after`, new chain row; `block-2` retarget; invert 466-467 |
| `sections/02,03,05,07,08` | Modify | one `after` retarget + one row gloss each; 05 states its referent moved to methods |
| `sections/09-title-and-keywords.md` | Modify | row only — no header change |
| `.claude/skills/paper-writing/SKILL.md:225-229` | Modify | re-measured wave shape, dated, with the command |
| `openspec/specs/fact-production/spec.md:175-181` | Modify | delta spec (owned by `sdd-spec`) |
| `tests/test_paper_writing.py` | Modify | mutation and property tests below |

**Invariant for every prose edit:** no edit may alter a byte span that some header
`source.quote` matches. Row glosses are free prose (only the leading backticked token is
read); quotes are not.

## Interfaces / Contracts

No new interfaces. `figure.components_from` keeps its shape; only its resolved producer
changes.

## Testing Strategy

| Layer | What to test | Approach |
|---|---|---|
| Mutation | each of the 8 rows | delete one row → `PRODUCER_CHAIN_ABSENT`; delete one `after` → `CHAIN_ROW_UNBACKED`. Red observed, not assumed |
| Mutation | D2's surviving guard | alter one roster item → components check refuses |
| Property | wave shape | every block's `after` dependencies resolve to a strictly earlier wave; no count asserted |
| Integration | corpus | `assemble_corpus` + `derive_order` acyclic with `mm-proposal` sole producer |

Run `PYTHONDONTWRITEBYTECODE=1` for every mutation: a same-size edit otherwise reuses stale
bytecode and the mutant never runs.

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or
process-integration boundary.

## Migration / Rollout

No migration. Single-commit revert.

## Open Questions

- [ ] Operator: is an ordered `\item` roster inside the methods proposal editorially
      acceptable, given the caption already enumerates the same components?
- [ ] Wave shape is **unmeasured in this phase** — this agent had no Bash tool. `phases`
      and `order` must be run in apply before `SKILL.md` is touched. Do not inherit
      `22/7/11/2/2/1/1/1`.

## Known and orthogonal

- `check_contribution_list` reads only requirers. Measured side effect: `block-4b` becomes a
  requirer, so the list-bearing block enters that check for the first time. A strengthening,
  not a blocker.
- `_verify_producer_duplication`'s corroboration exception matches `gap` by the coincidence
  `"gap" in CHECKS`; this fact's check is `contribution-list`. Unreachable here — this design
  keeps exactly one producer.
