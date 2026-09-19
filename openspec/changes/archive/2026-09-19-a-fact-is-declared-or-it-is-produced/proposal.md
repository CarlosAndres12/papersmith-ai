# Proposal: A Fact Is Declared Or It Is Produced

## Intent

`FACTS` records consumption (`requires_facts`) and never production. Measured on the live corpus:

- `related-work.rw-closing` requires `gap` while its prose tells it to write the gap — a block demanding its own output.
- `paper_verify.check_gap` derives its pair from consumers alone, resolving to `rw-closing` + `es-assessment`, not the design's `rw-closing` + `introduction.block-3`. Always `unmeasured`, so no false pass — but evidence about the wrong blocks.
- `contributions`, `problem-statement`, `limitations` each have a producer and remote consumers with zero `after` edge.

No code deadlock (`_stage_readiness` ignores `requires_facts`), but `SKILL.md` makes `phases`/`declare` the discipline, so an operator pre-authors the gap and then authors it again. Add the missing half; refuse the defect instead of noting it.

## Scope

### In Scope
- `produces_facts` in the contract header grammar, quote-anchored like every other field.
- Totality: one producer per fact, corroborated duplicates aside — an external source
  (`FACT_SOURCE_ROOT`) or exactly one block, except the one corroborated pair an existing
  coupling-verification check names as agreeing (`gap`).
- Refuse a block that produces and requires the same fact.
- Produced-fact satisfaction from the producer's written status, not `declare`.
- Corpus edits: `rw-closing` produces `gap` and stops requiring it, `introduction.block-3` requires it; same shape for the other three; each producer→consumer stated as an `### Internal chain` row with its backing `after` edge.
- `check_gap` pairing re-derived from producer + consumers — fixed here, not deferred.

### Out of Scope
- Change `12` (distributing a proposal at section granularity).
- Reclassifying `skeleton` (design D4).
- A third `main.tex` region; the DECLINED mechanism; `FACT_SOURCE_ROOT` roots.

## Capabilities

### New Capabilities
- `fact-production`: producer declaration, totality, self-reference refusal, produced-fact satisfaction.

### Modified Capabilities
- `paper-declarations`: the ten facts split declared/produced; `declare` refuses a produced fact.
- `writing-readiness`: blocked-on-produced names the producer, not a missing declaration.
- `contract-input-partition`: contracts state produced facts; each producer→consumer is an internal-chain row.
- `coupling-verification`: coupling 3's pair derives from production.

## Approach

Option 2 — record production explicitly — but in the parsed corpus, not a new `main.tex` region: production is a property of the contracts, not of one paper's run, so it costs no third digest or hand-edit guard and stays derived, never hand-listed.

Option 1 (auto-satisfy from `read_status`) is kept as the satisfaction signal only; with no declared producer it cannot see `rw-closing`'s self-reference. Option 3 (drop the four facts for `after` edges) loses `declare`'s audit trail and denies `es-assessment` a resolved gap value.

Change `12` builds on this: it must know whether a distributed claim lands as declared input or produced prose.

Work units, each under the 1200-line ceiling: (1) grammar, parser, refusals; (2) corpus edits and their edges; (3) consumers — `readiness`, `phases`, `declare`, `check_gap`.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `scripts/paper_vocabulary.py`, `paper_contract.py` | Modified | Producer half of the schema |
| `sections/*.md` (10) | Modified | `produces_facts`, chain rows |
| The seven `requires_facts` consumers | Modified | `readiness`, `declarations`, `cli`, `graph`, `write`, `bindings`, `coupling_evidence` |
| `paper_verify.py`, `tests/*.py` | Modified | Pairing; red-first mutation proofs |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Refusal roster arithmetic drifts | High | `reachable_paper_refusal_codes()`, never forecast |
| Corpus edits redden the 51 quote anchors | Med | Re-anchor inside the same work unit |
| `es-assessment` needs a gap value, not ordering | Med | `sdd-design` decides whether `declare` still records produced values |
| Engine leaks this paper's ids | Low | Derive from the corpus; no literal block id |

## Rollback Plan

Revert the branch. Only a header field and refusals are added — no region format, digest, or on-disk state changes — so an existing `paper/main.tex`, DECLINED `experimental-design` included, stays readable by the prior revision.

## Dependencies

- Archived `the-requirement-names-the-sentence-that-demands-it`, which deferred this defect.

## Success Criteria

- [ ] No block produces and requires the same fact — proven by an executed mutation.
- [ ] Every fact resolves to a producer; missing refuses, and an uncorroborated duplicate refuses
      — a corroborated pair (an existing coupling-verification check names it, e.g. `gap`) is
      legal.
- [ ] `check_gap` publishes evidence about `rw-closing` and `introduction.block-3`.
- [ ] Every producer→consumer pair carries a backing `after` edge.
- [ ] Roster derived and bidirectional; all paper suites green under `unittest`.
