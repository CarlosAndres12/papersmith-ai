# Proposal: The Phases Are Derived, Not Remembered

## Intent

Each `sections/*.md` is a JSON header plus prose, and `SKILL.md:165-166` says the skill never reads the prose for meaning — the halves are never compared, so the real dependency data, written in prose tables, is invisible. `requires_facts` is the only header field with no provenance and its ten-fact vocabulary cannot express "depends on sibling block X"; nine of ten blocks called writable demanded more than their header said. `cmd_readiness` never opens `main.tex`, so no verb answers "given what is declared, what can I write". Order lives in the agent's memory. It must live on disk, quote-anchored, re-derived every call.

## Scope

### In Scope
- Normalize the ten contracts into explicit `### External inputs` / `### Internal chain` (shape of `06-introduction.md`).
- Turn every Internal-chain row into a quote-anchored block-level `after` edge (`<section>.<block>`, already supported by `_resolve_target`); no persisted second copy. Refuse when a row names a block the graph lacks no edge for.
- Phase waves 1..N (Kahn frontier grouping, net-new beside `derive_order`), phase N gated on N-1, plan approved before writing; readiness reads the declarations region.
- Skeleton startup: two blocking questions once (Related Work y/n; dataset in Materials or Experimental Setup), skeleton = every section/block id opened empty; thereafter both decisions are INFERRED from the opened ids on disk. Disk reporting includes ignored paths.
- Create `es-dataset` (`optional: true`) in `02-experimental-setup.md`, mirroring `mm-dataset`.
- Give `optional` real semantics in `derive_order`, `compute_readiness`, `paper_verify.py` (today read by zero consumers).
- Drop `implementation` from `mm-proposal.requires_facts`.
- Redactor packet: emit, for one block, the section's contract prose plus the same section extracted from every `guidance/` reference — style only, zero content — over `paper_guidance`, `paper_style`, `paper_leak` and `style-sampler`.
- Corrections: `SKILL.md` `readiness` row; `insumos-observer` write-tool/shuttle mismatch; `paper_cli.py` "thirteen verbs" → 17.

### Out of Scope
- **Distributing r21 across blocks — DEFERRED** to a follow-up change. No machinery exists; `set_fact("formulation", …)` stores an opaque string. A proposal-section→block map is a second source of truth unless it is quote-anchored, which is its own design pass, and its natural inputs (normalized contracts, phase waves) are outputs of this change.
- Any skill other than `paper-writing`; drafting content; replacing the leak tripwires.

## Capabilities

### New Capabilities
- `contract-input-partition`: every contract separates external inputs from internal chain.
- `internal-chain-edges`: each internal-chain row is a quote-anchored `after` edge; an unbacked row refuses.
- `writing-phases`: Kahn waves, sequential gating, declaration-aware "what can I write now".
- `skeleton-startup`: asked once, inferred from disk forever after.
- `optional-block-semantics`: `optional` read by order, readiness and verify.
- `redactor-packet`: per-block contract + style-only reference extracts.

### Modified Capabilities
- `section-contract`: edge set is no longer "exactly three"; `es-dataset` added; `mm-proposal` facts narrowed.
- `writing-readiness`: derived order becomes waves; `optional` participates; readiness resolves `paper_dir`.
- `writing-orchestration`: packet emission and the hand-shuttle contract (no `subprocess`).
- `paper-declarations`: skeleton inference and declaration-aware readiness.
- `style-channel`: packet is a new consumer of equivalent-block resolution.

## Approach

Reuse, do not invent. `after` already carries `{target, source:{file,quote}}` and `_verify_after_transcription` already raises `SPAN_NOT_IN_SOURCE` on an edited quote — the lock was proven by mutation. The "heist" is therefore normalization plus transcription, not a new asset; precedent is `paper_provenance.py`, which stores a digest and recomputes. Phase waves are the only genuinely new algorithm. Skeleton questions are answered once into structure; structure is then the answer.

### Work-unit shape (≈9 units, chained PRs, `ask-on-risk`)

| # | Unit | Budget risk |
|---|---|---|
| 1 | Contract normalization, split by contract group (~300-500 lines, needs splitting) | High |
| 2 | `es-dataset` + `mm-proposal` fact narrowing | Low |
| 3 | `optional` semantics across three consumers | Med |
| 4 | Internal-chain → `after` transcription + unbacked-row refusal | High |
| 5 | Kahn wave grouping | Med |
| 6 | Declaration-aware readiness verb | Med |
| 7 | Skeleton flow + disk inference | High |
| 8 | Redactor packet emission | Med |
| 9 | Doc/agent corrections | Low |

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `sections/*.md` | Modified | Ten contracts normalized; `es-dataset` added |
| `.claude/skills/paper-writing/scripts/paper_graph.py` | Modified | Waves, `optional`, block-level edges |
| `.../paper_readiness.py`, `paper_cli.py` | Modified | Declaration-aware readiness, new verb(s), docstring |
| `.../paper_style.py`, `paper_guidance.py`, `paper_leak.py` | Modified | Packet assembly |
| `.claude/agents/insumos-observer.md`, `style-sampler.md` | Modified | Tools/shuttle fix |
| `tests/test_paper*.py` | Modified | Roster count, new scenarios |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Any new verb forces bidirectional `paper_cli.REFUSAL_CLASSIFICATION` edits and moves `assertEqual(len(reachable_paper_refusal_codes()), 96)` at `tests/test_paper_writing.py:3614` | High | Treat as part of every unit's definition of done |
| Unit 1 exceeds the 400-line budget | High | Split per contract group; `ask-on-risk` decision before apply |
| Contract tables speak prose names, not block ids | High | Transcription maps name→id explicitly and refuses unmapped rows |
| Only three `after` edges exist today; waves collapse to 35/8/2 | Med | Units 1+4 land before unit 5 so waves are measured, not assumed |
| Packet leaks content, not only style | Med | Keep `STYLE_OVERLAP`, register-distance and relative-overlap proofs as gates |
| `mm-preamble` sits in the same wave as blocks it must name | Med | Its internal chain becomes real edges in unit 4 |

## Rollback Plan

Each unit is an independent PR on a chain; revert the offending PR. Contract edits are text-only and digest-verified — reverting `sections/*.md` restores the previous edge set, and `_verify_after_transcription` refuses any header left pointing at a removed quote, so a partial revert fails closed rather than silently disagreeing. No persisted derived state is created, so nothing to migrate back.

## Dependencies

- None external. Stdlib-only, keyless, fail-closed, one JSON object per invocation, `Refused(code, detail)` exit 2.
- Unit ordering is internal: 5 depends on 1+4; 7 depends on 2+3; 6 depends on 5.

## Success Criteria

- [ ] All ten contracts carry `### External inputs` and `### Internal chain`.
- [ ] Every internal-chain row has a quote-anchored `after` edge; a row naming a block with no edge refuses.
- [ ] Editing a transcribed quote makes the skill refuse (proven by mutation, not by reading).
- [ ] `readiness` resolves `paper_dir` and its answer changes after `declare`.
- [ ] A phase plan lists waves 1..N; phase N is refused while N-1 is incomplete.
- [ ] Both startup decisions are recoverable from the opened block ids alone with the skeleton present and no question re-asked.
- [ ] `optional` changes at least one observable outcome in each of order, readiness and verify.
- [ ] The packet for one block carries contract prose plus same-section reference extracts and passes the leak tripwires.
- [ ] `npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'` green, refusal roster count updated.
