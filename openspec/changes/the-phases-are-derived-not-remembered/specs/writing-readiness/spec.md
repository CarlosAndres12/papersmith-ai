# Delta for Writing Readiness

## ADDED Requirements

### Requirement: Readiness Resolves Declared State From The Paper Directory

When a `paper_dir` resolves, the `readiness` verb MUST include, in its
satisfied-facts and satisfied-declarations sets, every fact resolution and
declaration already recorded in that paper's own `declarations` region
(`paper-declarations`), merged with any `--fact` / `--declaration` flags
explicitly given on the invocation. It MUST NOT compute readiness from CLI
flags alone while ignoring an existing `declarations` region. This closes
the regression where `cmd_readiness` never opened `main.tex`, so its answer
never changed after `declare`.

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

### Requirement: Optional Flag Surfaces In Readiness Reports

Every block's readiness report MUST include `optional`, read from the
block's own declaration, alongside `status`, `missing_facts`, and
`missing_declarations`. This is a report-shape addition; the `writable` /
`blocked` computation itself is unchanged.

#### Scenario: The optional flag is present on every entry

- GIVEN readiness computed over the shipped corpus
- WHEN any block's report is read
- THEN it carries an `optional` field matching that block's own header
  declaration
