# implementation-comparison-deferral Specification

## Purpose

The first flow (Flow A) implements a mathematical proposal, proves it against
the paper, and stops. It MUST leave behind only what it itself needs — the
method's modules, its own declaration, and the piece that lets its own
verification notebook stamp what it proved. It MUST NOT bring comparison
machinery (a benchmark package) into existence before a comparison has been
proposed and accepted. This capability governs the scaffold-stage destination
list, the benchmark-declaration's on-disk location, the verification seal's
location, the harness-stage destination list, and the baseline finder's
exclusion of the skill's own benchmark package.

**The package the comparison currently lives in is not the comparison's own
file.** It carries four independent top-level literals, and only one of them —
`revision`/`premises` — declares the comparison. The other three — `__levels__`
(the target's own position rung ladder), `__steps__` (the target's own declared
flow: order, what each step produces, where it runs, and which job carries it),
and `__records__` (named records a leveled witness reaches) — declare the
target's own first-flow state and are read by first-flow commands
(`cmd_probe`, `cmd_verify`, `cmd_step`), not by anything behind a comparison.
This capability therefore also governs where those three relocate to, and
that the first flow keeps working, unchanged, once they do. `revision` itself
has two independent readers inside `verify` — a drift comparison and the
revision family that seeds the whole command's staleness and dataset
reporting — and both must keep working once a benchmark package is no longer
the ordinary state of a first-flow target.

**Budget note.** This spec exceeds 650 words because the owner's binding
directive for this change is "must cover everything, nothing pending" plus a
no-regression mandate: every preserved behaviour (the existence gate, the
notebook's stamping, the remaining declaration blocks, fidelity reporting,
the probe ladder, the drift/adopt machinery, the three sibling declarations,
and `revision`'s two independent readers) needs its own requirement and
scenario, in addition to the new deferral behaviour, or a regression in any
of them would pass review unnoticed.

## Requirements

### Requirement: The Scaffold Stage Does Not Create A Benchmark Package

Flow A's scaffold stage MUST NOT include `src/<Package>_Benchmark/__init__.py`
among its destinations. The scaffold destination list MUST contain ten
unconditional entries; the scaffold gap report MUST name at most twelve
entries (ten unconditional plus up to two conditional merge anchors), and
that figure MUST be computed from the destination list at read time, never
transcribed as a literal in any document.

#### Scenario: A fresh target has no benchmark directory after scaffolding
- GIVEN a target that has just completed Flow A's scaffold stage
- WHEN `src/` is inspected
- THEN no `<Package>_Benchmark` directory exists anywhere under it

#### Scenario: The gap report is derived, not transcribed
- GIVEN the scaffold destination list at its post-change size
- WHEN the gap report is produced
- THEN it names at most twelve entries, computed from the list, and no
  document states that figure as a hand-written literal

### Requirement: The Benchmark Declaration Lives In The Method's Own Package

`src/<Package>/__init__.py` MUST carry `revision` and `premises` as a
top-level declaration. This file is already one of the scaffold stage's
unconditional destinations; no new file is introduced to hold it.

#### Scenario: The declaration is written to the method's own package
- GIVEN Flow A step 8 collects `revision` and `premises`
- WHEN they are written to disk
- THEN they land in `src/<Package>/__init__.py`, not in any `_Benchmark`
  directory

### Requirement: The Target's Own Flow Declarations Relocate Alongside The Method's Declaration, Not With The Comparison

`__levels__` (the target's own position rung ladder), `__steps__` (the
target's own declared flow — order, what each step produces, where it runs,
and which job carries it), and `__records__` (named records a leveled
witness reaches) are the target's own first-flow declarations, not the
comparison's. They MUST relocate to the method's own package alongside
`revision`/`premises`, and MUST remain fully readable there, declaring
exactly what they declared before relocation — the same rungs, the same
steps, the same named records, resolved from the new location.

#### Scenario: The declared position ladder is unaffected by relocation
- GIVEN `__levels__` relocated to the method's own package
- WHEN the position ladder is resolved
- THEN it names the same rungs, in the same order, as before relocation

#### Scenario: The declared flow still resolves and runs
- GIVEN `__steps__` relocated to the method's own package
- WHEN a declared step is run
- THEN it resolves and executes exactly as it did before relocation

#### Scenario: Named records are still reached and graded identically
- GIVEN `__records__` relocated to the method's own package
- WHEN a leveled witness addresses a named record
- THEN it reaches the same entry and is graded exactly as before relocation

### Requirement: First-Flow Commands Do Not Depend On A Benchmark Package For The Target's Own Declarations

`cmd_probe`'s position, pilot-completeness, walk, and flow-acts machinery,
`cmd_step`, and the parts of `cmd_verify` that read the target's own
declared flow MUST continue to function identically for a target that has
never had, and may never have, a benchmark package. None of these MUST
depend on `src/<Package>_Benchmark/` existing.

#### Scenario: Position and pilot state resolve with no benchmark package present
- GIVEN a first-flow-only target with no `_Benchmark` directory ever created
- WHEN `probe` evaluates position state and pilot completeness
- THEN both resolve fully from the relocated declarations, unaffected by the
  absence of a benchmark package

#### Scenario: A declared step still runs with no benchmark package present
- GIVEN the same target
- WHEN a declared step is run through `cmd_step`
- THEN it executes exactly as it would if a benchmark package existed

### Requirement: `revision`'s Two Independent Readers In `verify` Are Both Preserved, Unconditionally

`revision` feeds two separate things inside `verify`: a drift reader that
compares it against what a benchmark declares itself bound to, and a
revision-family reader that seeds the command's reported latest revision,
each module's staleness, its dataset declaration, and the data-directory
branch of structural correctness. Both MUST read `revision` from its
relocated location. The revision-family reader MUST NOT be conditioned on a
benchmark package being declared — after this change, no benchmark
declared is the *ordinary* pre-acceptance state of every first-flow target,
not an error state, and `verify` MUST NOT report a stale revision against an
empty set of changed sections, nor silently fall back to a different
revision source, merely because no benchmark package exists yet.

#### Scenario: The revision family resolves with no benchmark package present
- GIVEN a first-flow-only target with no benchmark package
- WHEN `verify` runs
- THEN it reports the correct revision family, module staleness, and
  dataset declaration, read from the relocated `revision`

#### Scenario: `verify` does not report spurious staleness for a target with no benchmark
- GIVEN the same target, whose relocated `revision` correctly names what the
  method is built against
- WHEN `verify` runs
- THEN it does not report a stale revision paired with an empty set of
  changed sections merely because no benchmark package exists

#### Scenario: The drift reader still compares correctly once a comparison exists
- GIVEN a target with an accepted comparison and a benchmark declaration
- WHEN `verify`'s drift reader runs
- THEN it compares the relocated `revision` against the benchmark's own
  bound revision exactly as it did before relocation

### Requirement: The Object-Map Existence Gate Refuses By Behaviour, Unchanged

Step 9's existence gate MUST continue to refuse with `OBJECT_MAP_NOT_APPROVED`
whenever `revision` or `premises` is blank, and MUST proceed once both are
non-blank — the identical refusal, under the identical condition, reading
from the declaration's new location rather than the old one.

#### Scenario: A blank revision still refuses
- GIVEN `premises` is populated and `revision` is blank
- WHEN step 9 evaluates the object map
- THEN it refuses with `OBJECT_MAP_NOT_APPROVED`

#### Scenario: A blank premises still refuses
- GIVEN `revision` is populated and `premises` is blank
- WHEN step 9 evaluates the object map
- THEN it refuses with `OBJECT_MAP_NOT_APPROVED`

#### Scenario: Both populated proceeds
- GIVEN both `revision` and `premises` are non-blank in the new location
- WHEN step 9 evaluates the object map
- THEN it proceeds without refusing

### Requirement: `premises` Remains Write-Only

The declaration's `premises` field MUST have no downstream reader that
parses or validates its content. It exists for a person reading a drift
report; only its location changed, never its purpose.

#### Scenario: Arbitrary premises content does not block the gate
- GIVEN `premises` holds free-form prose of any shape
- WHEN step 9 evaluates the object map
- THEN non-blankness alone decides the outcome; content shape is irrelevant

### Requirement: The First Flow's Verification Notebook Stamps Unaffected By Relocation

The notebook Flow A executes MUST import the stamping module from its new
location inside `src/<Package>/` and MUST produce the same stamped output it
produced before relocation, for the same inputs.

#### Scenario: The notebook runs and stamps successfully at the new path
- GIVEN the stamping module now lives at `src/<Package>/report_digest.py`
- WHEN Flow A's verification notebook executes
- THEN the import succeeds and the notebook stamps what it proved

#### Scenario: The stamped content is unaffected by the module's relocation
- GIVEN identical proof inputs, once before and once after relocation
- WHEN the notebook stamps its output
- THEN the stamped content is the same; only the module's import path changed

### Requirement: Harness Destinations Gain The Benchmark Package, Written Only On Acceptance

`harness_destinations()` MUST grow from three entries to four, gaining
`src/<Package>_Benchmark/__init__.py`. This file MUST be materialized only by
the second flow's wiring-first rung, after a comparison has been accepted.
No fifth materialization stage is introduced.

#### Scenario: No benchmark package exists before acceptance
- GIVEN a target with a trainable method and no accepted comparison
- WHEN `src/` is inspected
- THEN no `<Package>_Benchmark` directory exists

#### Scenario: Acceptance materializes the benchmark package via the harness stage
- GIVEN a comparison has just been accepted
- WHEN the second flow's wiring-first rung runs
- THEN `src/<Package>_Benchmark/__init__.py` is created as a harness
  destination, and no new stage beyond the existing scaffold/harness pair is
  invoked

### Requirement: The Baseline Finder Excludes The Skill's Own Benchmark Package

`previous_implementations()` MUST exclude any directory whose name ends with
the `_Benchmark` suffix when enumerating prior work, making `nothing-to-compare`
reachable for a scaffolded target for the first time.

#### Scenario: A target with no genuine prior work reports nothing-to-compare
- GIVEN a scaffolded target whose only `_Benchmark`-suffixed directory is its
  own (if any exists on disk)
- WHEN `previous_implementations()` runs
- THEN it returns an empty list, and the flow reports `nothing-to-compare`

#### Scenario: A real baseline is still found alongside an excluded suffix
- GIVEN a target with one genuine baseline package and, separately, a
  `_Benchmark`-suffixed directory
- WHEN `previous_implementations()` runs
- THEN it returns only the genuine baseline, never the excluded directory

### Requirement: The Remaining Five Declaration Blocks Are Unaffected Once The Harness Stage Has Run

`arms`, `search`, `report`, `distribution`, and `entry` MUST keep their
existing three-way `absent`/`undeclared`/`declared` resolution, including the
blank-literal rule: a parsed-but-empty declaration resolves to `undeclared`,
never `declared`.

#### Scenario: A missing declaration file resolves absent
- GIVEN the benchmark declaration file does not exist
- WHEN a block is resolved
- THEN it resolves `absent`

#### Scenario: A present but empty block resolves undeclared, never declared
- GIVEN the declaration file exists and a block is parsed as blank
- WHEN it is resolved
- THEN it resolves `undeclared`

#### Scenario: A populated block resolves declared
- GIVEN the declaration file exists and a block carries content
- WHEN it is resolved
- THEN it resolves `declared`

### Requirement: Fidelity Reporting For A Target With A Benchmark Is Unchanged

`absent` MUST remain deliberately excluded from fidelity reporting, while
`undeclared` MUST remain folded into it — for any target that does have a
benchmark declared.

#### Scenario: An absent block does not affect fidelity
- GIVEN a target's benchmark declaration is absent
- WHEN fidelity is reported
- THEN the absent state is not folded into the fidelity figure

#### Scenario: An undeclared block does affect fidelity
- GIVEN a target's benchmark declaration exists with an undeclared block
- WHEN fidelity is reported
- THEN the undeclared state is folded into the fidelity figure

### Requirement: Every Pre-Existing Probe Rung Fires Under Its Exact Prior Condition

Every state and override in `PROBE_NEXT_STEPS` that exists before this
change — including `nothing-to-compare` and `already-benchmarked` — MUST
continue to fire under exactly the condition it fires under today. Adding
the `"declined"` rung and its acid-test follow-up (specified in full by
`implementation-declined-comparison`) MUST NOT reorder or shadow any
existing rung.

#### Scenario: Each pre-existing rung is unaffected by the new entry
- GIVEN the probe ladder after the new terminal state is added
- WHEN each pre-existing state's precondition is exercised in isolation
- THEN it fires exactly as it did before the new state was added

### Requirement: Materialization Receipt Machinery Detects Drift And Unrecorded Scaffolds Against The New Destination Lists

`SCAFFOLD_DRIFT` and `UNRECORDED_SCAFFOLD` detection, and `materialize
--adopt`, MUST continue to operate correctly against the updated scaffold
and harness destination lists.

#### Scenario: A hand-edited relocated file is flagged as drift
- GIVEN `src/<Package>/report_digest.py` was hand-edited after materialization
- WHEN the receipt is checked
- THEN it reports `SCAFFOLD_DRIFT` for that file at its new location

#### Scenario: An unrecorded benchmark package is flagged
- GIVEN `src/<Package>_Benchmark/__init__.py` exists on disk without having
  gone through `materialize`
- WHEN the receipt is checked
- THEN it reports `UNRECORDED_SCAFFOLD` against the harness destination list

#### Scenario: `--adopt` records an unrecorded destination at its correct membership
- GIVEN an unrecorded file matching either the scaffold or the harness list
- WHEN `materialize --adopt` runs against it
- THEN it is recorded as adopted, scoped to the stage list it actually
  belongs to (scaffold or harness)

### Requirement: Both Scaffold Mappings Agree

The engine's destination lists and `materialize.py`'s independently
duplicated mapping MUST agree on both the scaffold and harness destination
lists, enforced by a test rather than by review.

#### Scenario: Agreement holds when both sites are updated together
- GIVEN both the engine and `materialize.py` updated in the same commit
- WHEN the agreement test runs
- THEN it passes

#### Scenario: Disagreement is caught
- GIVEN only one site is updated
- WHEN the agreement test runs
- THEN it fails, naming the divergent list

### Requirement: A Declaration Predating This Change Is Migrated In Full, Never Silently Read As Undeclared Or Silently Dropped

A target scaffolded before this change carries its `revision`/`premises`
declaration, and any of `__levels__`/`__steps__`/`__records__` it declared,
at the old home, `src/<Package>_Benchmark/__init__.py`. After this change,
the resolvers read only the new home, `src/<Package>/__init__.py`. These are
opposite facts and MUST NOT share an outcome:

- **A target that never declared at all** — new home blank, no declaration
  ever written anywhere — resolves exactly as it does today: undeclared,
  gated by `OBJECT_MAP_NOT_APPROVED` inside Flow A.
- **A target whose declaration predates this change** — new home blank, but
  the old home carries a non-blank `revision`/`premises` — MUST be detected
  as a distinct, named condition, not silently folded into "undeclared."

**Resolution: a one-time migration path, not a permanent dual read.** The
resolver MUST NOT read both homes indefinitely — that would leave the old
home a live input forever, contradicting Movement 2's own destination
decision. Instead, on detecting the old-home condition, the system MUST
refuse by a named code identifying both locations (the old home the
declaration was found at, and the new home it belongs at), and a one-time
`materialize --adopt`-shaped remedy MUST move the declaration's content from
the old home into the new home. Editing the old file's fields in place is
not the remedy, because nothing about the fields themselves is wrong — only
their location is; the remedy relocates the value, mirroring exactly what
this change already does to the file itself for newly-scaffolded targets.
After the move, the target behaves identically to a target that was always
scaffolded under the new layout.

**Every top-level literal at the old home MUST be carried to the new home,
including any the forge itself never reads.** A pre-existing declaration
file may carry a literal the engine has no reader for at all — nothing in
`.claude/` or in the test suite ever looks at it. The migration remedy MUST
preserve that literal's content unchanged regardless. This is its own
requirement, separate from the named-refusal-and-remedy shape above, because
an unread literal's loss is invisible to every check the engine could ever
run: nothing that never looked for a value can report it missing, so a
silent drop and a clean migration are indistinguishable by any forge-owned
signal. Only naming the obligation explicitly closes that gap.

#### Scenario: A never-declared target is unaffected
- GIVEN a target whose declaration was never written at either home
- WHEN the gate evaluates it
- THEN it refuses `OBJECT_MAP_NOT_APPROVED`, exactly as before this change

#### Scenario: A pre-existing declaration at the old home is named, not silently lost
- GIVEN a target whose old home carries non-blank `revision` and `premises`,
  and whose new home is blank
- WHEN the declaration is resolved
- THEN the system refuses by a named code identifying both the old and the
  new location, distinct from the plain `OBJECT_MAP_NOT_APPROVED` refusal for
  a target that never declared

#### Scenario: The one-time remedy moves the declaration and the gap closes
- GIVEN the named pre-existing-declaration refusal above
- WHEN the one-time migration remedy runs
- THEN `revision` and `premises` are present and non-blank at the new home,
  and the gate proceeds exactly as it would for a natively-scaffolded target

#### Scenario: The engine-recognized sibling declarations migrate in full
- GIVEN `__levels__`, `__steps__`, and `__records__` all declared at the old
  home
- WHEN the one-time migration remedy runs
- THEN all three are present, unchanged, at the new home

#### Scenario: A literal the forge has no reader for is still preserved
- GIVEN the old-home file declares an additional top-level literal the forge
  has no reader for anywhere
- WHEN the migration remedy runs
- THEN that literal's content is present, unchanged, at the new home — even
  though no forge-owned check would ever have reported its absence
