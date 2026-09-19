# Delta for Coupling Verification

## MODIFIED Requirements

### Requirement: Coupling 3 — The Gap Is Assisted

Presence of both closings — the two blocks that `produces_facts` names as
`gap`'s corroborated producers (`fact-production`'s duplicate-producer
carve-out), resolved from the corpus's own producer declarations rather than
from every block that happens to name `gap` — and front-count/front-list
equality MUST be computed mechanically. "The same thing at different
depths" MUST NOT be computed; the payload MUST publish both closing texts
and both front lists verbatim, and the reading's own verdict MUST be
`unmeasured` until a human rules. `verify` MUST NOT answer or gate on that
reading (resolves proposal question 4: nobody closes it here).
(Previously: the pair was derived by scanning every block's `requires_facts`
for `gap`, which resolved to `rw-closing` and `experimental-setup.
es-assessment` — the wrong second block, since `es-assessment` names `gap`
for an unrelated reason and `introduction.block-3`, the design's intended
counterpart, did not name `gap` at all until this change.)

#### Scenario: Assisted payload published

- GIVEN both blocks exist with declared fronts
- WHEN coupling 3 runs
- THEN mechanical sub-checks report `pass`/`fail`, the depth-reading
  sub-check reports `unmeasured`, and both full texts appear in the payload

#### Scenario: Pairing resolves to the two corroborated producers of gap

- GIVEN `gap` produced by both `related-work.rw-closing` and
  `introduction.block-3` (the corroborated pair `fact-production`'s
  duplicate-producer carve-out allows), with
  `experimental-setup.es-assessment` separately naming `gap` in its own
  `requires_facts` for an unrelated purpose
- WHEN coupling 3 runs
- THEN the pair it evaluates is (`rw-closing`, `introduction.block-3`), and
  `es-assessment` is not treated as the coupling's counterpart

#### Scenario: Mutation — reverting to consumer-scan pairing is caught

- GIVEN the pairing derivation mutated to select its counterpart by
  scanning every `requires_facts` consumer of `gap`, rather than the fact's
  two declared producers
- WHEN the pairing test runs against the fixture where `es-assessment` also
  names `gap`
- THEN it fails, since the mutated derivation would select `es-assessment`
  as the counterpart instead of `introduction.block-3`
