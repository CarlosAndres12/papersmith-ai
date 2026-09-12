# Delta for implementation-document-binding

## ADDED Requirements

### Requirement: `plan` Gains `--revision` And Is Bound To A Document At All Three `build_plan` Call Sites

`--revision` MUST be registered for `plan`, joining the eight commands that
already carry it (`verify`, `admit`, `handoff`, `probe`, `position`, `gate`,
`offer`, `close`). The resolved document path MUST reach `build_plan`
identically at all three of its call sites — `cmd_plan`, `cmd_apply`, and
`_materialize_plan_gate` — never only the first. A parameter threaded to one
of three call sites and not the other two MUST NOT be treated as complete.

#### Scenario: A plan built with a revision applies without `PLAN_STALE`
- GIVEN a plan built by `cmd_plan` with `--revision` naming a document that
  declares a dataset
- WHEN `cmd_apply` re-derives `build_plan` and compares `createDirs`
- THEN the two agree and `apply` does not refuse `PLAN_STALE`

#### Scenario: `_materialize_plan_gate` agrees with both
- GIVEN the same plan and revision
- WHEN `_materialize_plan_gate` re-derives `build_plan`
- THEN its `createDirs` also agrees, and materialization does not refuse
  `PLAN_STALE`

#### Scenario: A revision reaching only `cmd_plan` is caught
- GIVEN a mutation that threads the document path into `cmd_plan` alone
- WHEN `apply` re-derives the plan for a target whose declared dataset is
  absent
- THEN the three-call-site agreement test fails, naming the site that
  disagrees

### Requirement: `plan` Without A Nameable Document Leaves `with_data` Unchanged, And Names What It Read When It Could

When no document is nameable (a bare clone, `--revision` omitted, or no
document readable), `plan`'s `with_data` derivation MUST remain exactly as
today — unchanged by this capability, never refused, so `plan` stays
runnable on a bare clone. When a document IS nameable, `plan`'s output MUST
carry a conditional key naming the exact document it read, emitted only in
that case; a profile declaring no dataset marker (or a call with no
nameable document) MUST produce byte-identical stdout to before this
capability, since the key is absent, not empty.

#### Scenario: An unnameable document leaves `plan` runnable and unchanged
- GIVEN `plan` runs on a bare clone with no `--revision` and no readable
  document
- WHEN `build_plan` computes `with_data`
- THEN it is derived exactly as before this capability, and no document-name
  key appears in the output

#### Scenario: A nameable document adds the conditional key, and nothing else moves
- GIVEN `plan` runs with `--revision` naming a readable document
- WHEN `build_plan` runs
- THEN the output carries a key naming that document, and every other key's
  value is unaffected by the key's presence

#### Scenario: The sibling's silence keeps its digests unmoved
- GIVEN `proposal-implementation`'s sealed 28-case corpus, none of whose
  cases name a dataset-declaring document
- WHEN the seal re-runs after this capability lands
- THEN none of the 28 digests move, because the conditional key never
  appears for them
