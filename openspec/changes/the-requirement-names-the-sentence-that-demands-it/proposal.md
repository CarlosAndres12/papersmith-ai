# Proposal: The Requirement Names the Sentence That Demands It

## Intent

`mode` and `after` carry `{value|target, source:{file,quote}}`, verified as a literal substring of the named contract's prose. `requires_facts` / `requires_declarations` carry a bare list. **The one field that decides what is writable is the only one with no provenance.**

Measured cost: `mm-proposal` demanded `implementation` with no sentence behind it. No guard saw it; a human found it by hand. Exploration found a second, previously unknown instance (`experimental-setup.es-assessment` requires `experimental-design` and `gap` with zero anchor anywhere in its file). The class is open and unreachable to every existing check.

## Scope

### In Scope
- Header schema: each `requires_facts` / `requires_declarations` entry MAY carry `{value, source:{file,quote}}`, following `after`'s list-of-objects precedent (not `mode`'s scalar).
- Reuse `_validate_source` + `paper_contract.quote_in_body` for self-file quotes and `paper_graph`'s cross-file path for quotes living in another contract (already shipped for `abstract`'s `after`).
- `BlockRecord` keeps a **derived plain tuple** of ids; a sibling field carries the anchored entries.
- Transcribe the ~47 anchorable requirements across the 10 `sections/*.md` contracts.
- An unconditional corpus-wide verifier wired into `assemble_corpus`.
- Update test fixtures that build **raw JSON headers**.

### Out of Scope
- Changing any of the 7 downstream consumers of `requires_facts` — none needs the source, only validation does.
- New refusal codes. `MALFORMED_HEADER`, `UNKNOWN_FACT`, `UNKNOWN_DECLARATION`, `SPAN_NOT_IN_SOURCE` cover every failure mode.
- Deleting any requirement, or authoring prose into a contract, on executor judgment.
- Widening `mode` / `after`; the `declarations` region; per-fact resolution.

## Capabilities

### New Capabilities
- `requirement-transcription`: every declared requirement is admitted only when a named contract's own prose states it; the rich entry shape, the derived plain tuple, the cross-file quote case, and the corpus-wide gate.

### Modified Capabilities
- `section-contract`: front-matter schema widens `requires_facts` / `requires_declarations` from bare id lists to transcribed entries, alongside the existing `mode` / `after` transcription requirements.

## Approach

**Additive split-field.** The rich shape lives in the header and validation layer; `paper_graph.BlockRecord.requires_facts` stays a plain tuple derived from it. This mirrors how `mode` already separates its rich object from its resolved value, and is why the seven consumers across six modules (`paper_readiness.compute_block_readiness`, `paper_coupling_evidence._blocks_by_fact`, `paper_declarations.dataset_placement_candidates` / `affected_blocks`, `paper_cli`'s `BlockContract`, `paper_write._stage_evidence_audit`, `paper_bindings.resolve_bindings`) are untouched.

Rejected: full replacement to `list[{value,source}]` everywhere — large diff, seven consumers rewritten, and nothing downstream reads the source.

**Generality.** The engine derives from the parsed corpus. No hand-listed tuple of block ids, no literal fact id of this paper, no id of this paper anywhere in `scripts/`.

**Enforcement lives in the skill.** A note describing the defect is a worse outcome than a refusal that makes it unreachable.

## Work-Unit Shape

The gate is corpus-wide: the moment it goes unconditional it breaks every real file and every raw-header fixture. So the sequence is shaped around one blocking decision point.

| Unit | Content | Gate state |
|---|---|---|
| U1 | Schema + validators + derived tuple + sibling field; both shapes accepted | Inert — corpus untouched, suite green |
| U2 | Transcribe every anchorable requirement; **report the unanchorable ones one by one** | Still inert |
| **DP** | **Operator rules on the 2 confirmed + 2 borderline unanchored requirements** | **Blocking handoff** |
| U3 | Apply the rulings, wire the verifier unconditionally, update raw-header fixtures, re-derive the roster | Atomic — one commit |

**DP sits between U2 and U3, never inside apply.** Each unanchorable requirement has two readings — the requirement is spurious, or the contract never wrote it down — and only the operator chooses. Letting an executor choose there is exactly how the spurious `implementation` entered.

Known DP inputs (from exploration, confirmed by full read + grep):
- `experimental-setup.es-assessment` → `experimental-design`, `gap`: zero anchor.
- `es-assessment` → `dataset`: duplicates what that file frames as an internal chain edge to `es-dataset`.
- `title-and-keywords.keywords` → `contributions`: anchored only by reusing its own ordering-edge quote.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/paper-writing/scripts/paper_contract.py` | Modified | `_parse_block`, entry validation reusing `_validate_source` / `quote_in_body` |
| `.claude/skills/paper-writing/scripts/paper_graph.py` | Modified | `BlockRecord` sibling field; cross-file verifier; `assemble_corpus` wiring |
| `sections/*.md` (10, **repo root**) | Modified | Headers gain transcribed entries; prose bodies byte-identical |
| `tests/*.py` (**repo root**) | Modified | Raw-JSON-header fixtures only |
| `.claude/skills/paper-writing/SKILL.md` | Modified | Documents the transcription obligation |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Unconditional gate breaks corpus + fixtures mid-sequence | High | Gate lands only in U3, atomically, after DP |
| Fixture blast radius misjudged | Med | Fixtures building raw JSON headers need updating; fixtures constructing `BlockRecord` directly do **not** — that distinction decides the diff size |
| Executor silently deletes or invents to clear the gate | Med | Option C is contractual: report, never rule. U3 may not start before DP returns |
| Roster arithmetic quoted stale | Med | It reads **127** today. Verify bidirectionally with `reachable_paper_refusal_codes()` once code lands — **never forecast**; that number drifted stale four times last change |
| Paper-specific ids leak into the engine | Low | Already happened once here (`MM_DATASET_ID`, undone). Derive from the corpus; a grep for this paper's ids under `scripts/` is part of verification |
| Cross-file quote path under-tested | Low | `abstract.slot-2`'s quote lives in `06-introduction.md`; the shipped `after` cross-file path is the precedent to reuse, not re-invent |
| U3 exceeds the 1200-line PR budget | Med | 10 contracts + fixtures in one commit; `ask-on-risk` surfaces it at tasks time |

## Rollback Plan

- U3 is one atomic commit: `git revert` restores the pre-gate corpus and fixtures together.
- U1 and U2 are inert without U3 — accepted-but-unverified provenance. Reverting U3 alone leaves a green suite.
- No data migration, no persisted state, no generation counter touched.

## Dependencies

- Operator ruling at DP. Nothing in U3 may start before it returns.
- No external dependency. Stdlib-only, keyless, fail-closed, no `subprocess`.

## Success Criteria

- [ ] Every `requires_facts` / `requires_declarations` entry in the shipped corpus is backed by a verified prose quote; a header edited to add an unbacked requirement refuses `SPAN_NOT_IN_SOURCE`.
- [ ] The verifier is unconditional in `assemble_corpus` — proven by mutation, not by reading the roster.
- [ ] The 7 downstream consumers are unchanged and the derived tuple is proven equal to the pre-change value set.
- [ ] `reachable_paper_refusal_codes()` derives bidirectionally with no new code; measured after the code lands.
- [ ] All six paper suites green (695 tests before this change).
- [ ] No id of this paper appears anywhere under `scripts/`.
