# Delta for Writing Readiness

## MODIFIED Requirements

### Requirement: Per-Block Readiness

Given a set of satisfied fact ids and a set of satisfied declaration ids, the
reader MUST report every block of every section as either `writable`, or
`blocked` naming each of its still-missing `requires_facts` entries and each
of its still-missing `requires_declarations` entries separately. A block
whose facts are all satisfied but whose declarations are not MUST report
`blocked`, never `writable` — a fact-only check that ignores declarations
reports this case wrong. A still-missing entry for a fact whose producer is a
block (`fact-production`) MUST report both the fact id and its producing
block id, so the operator is told to write the producer, never to `declare`
it.
(Previously: a missing fact was named by id alone, with no distinction
between a fact awaiting an operator declaration and a fact awaiting its
producing block's own prose.)

#### Scenario: A block with every requirement satisfied is writable

- GIVEN a block requiring `requires_facts: [dataset]` and no declarations,
  with `dataset` in the satisfied-facts set
- WHEN readiness is computed
- THEN the block reports `writable`

#### Scenario: A block blocked only by a declaration is not writable

- GIVEN a block requiring `requires_facts: [dataset]` (satisfied) and
  `requires_declarations: [repository-url]` (not satisfied)
- WHEN readiness is computed
- THEN the block reports `blocked`, naming `repository-url` as the missing
  requirement, even though every fact is satisfied

#### Scenario: Back matter reports zero missing facts and its declarations missing

- GIVEN back matter's blocks, which require no facts and several
  declarations, none of which are satisfied
- WHEN readiness is computed
- THEN each block reports `blocked` with zero missing facts and its
  declarations named as missing

#### Scenario: A block blocked on a produced fact names its producer

- GIVEN `introduction.block-3` requiring `gap`, produced by
  `related-work.rw-closing`, not yet written
- WHEN readiness is computed
- THEN the block reports `blocked`, naming `gap` as missing together with
  `related-work.rw-closing` as its producer

### Requirement: Readiness Resolves Declared State From The Paper Directory

When a `paper_dir` resolves, the `readiness` verb MUST include, in its
satisfied-facts and satisfied-declarations sets: every fact resolution and
declaration already recorded in that paper's own `declarations` region
(`paper-declarations`), for facts whose producer is external; every fact
whose producer is a block (`fact-production`) and that block's own written
status reports opened; merged with any `--fact` / `--declaration` flags
explicitly given on the invocation. It MUST NOT compute readiness from CLI
flags alone while ignoring an existing `declarations` region or an
already-written producer block. This closes the regression where
`cmd_readiness` never opened `main.tex`, so its answer never changed after
`declare`.
(Previously: satisfied facts came from the declarations region and CLI flags
only, with no path for a fact produced by a block to become satisfied by
that block being written.)

#### Scenario: Readiness changes after declare, with no flags repeated

- GIVEN a paper whose `declarations` region already records `formulation`
  as a satisfied fact resolution
- WHEN `readiness` is invoked with no `--fact` flags
- THEN every block whose only missing requirement was `formulation` reports
  `writable`

#### Scenario: Explicit flags still add to the recorded state

- GIVEN the same paper, with `formulation` recorded and `dataset` not
  recorded anywhere
- WHEN `readiness` is invoked with `--fact dataset`
- THEN a block requiring both `formulation` and `dataset` reports
  `writable`, combining the recorded state with the given flag

#### Scenario: A produced fact becomes satisfied once its producer is written

- GIVEN `gap` (produced by `related-work.rw-closing`), with `rw-closing`
  already opened in `main.tex` and no `declarations` region entry for `gap`
- WHEN `readiness` is invoked with no `--fact` flags
- THEN every block requiring only `gap` reports `writable`
