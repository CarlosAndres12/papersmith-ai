# implementation-data-demandability Specification

## Purpose

`Data/` is already a first-class product category (`PRODUCT_DIRS`, `PRODUCT_DATA`,
`DATA_EXT`, `classify`, `detect_product_dir`) — only demandability is missing.
This capability adds a per-`documents[N]` leaf naming a domain's own dataset
declaration, a detector that reads it from the bound document's own bytes,
and the wiring that makes `cmd_verify`'s `with_data` — and therefore
`verify.structure.missingDirs` — reflect that declaration instead of the
repository's own contents. `Data/` remains demanded per product folder
(`expected_dirs`'s existing `f"{name}/{d}"` shape), never at the repository
root, because a run binds to one method (`--name`) and its data may not
apply to a sibling method or a later paper in the same clone.

**Budget note**, on this spec's own precedent: this exceeds 650 words because
three of its requirements are the change's own headline acceptance
conditions — that `missingDirs` can newly contain `Data/`, that the required
leaf's silent-typo failure mode is the reason it is required at all, and
that the fixture must prove the detector before the shipped marker does —
and asserting them without their reasoning would repeat the exact
unprovable-guard shape this project has spent eight changes removing.

## Requirements

### Requirement: Every `documents[N]` Entry Declares A Dataset-Marker Leaf, Required Not Optional

Each `documents[N]` entry MUST declare a `dataset_marker` leaf, validated at
the same `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` tier as `directory` and
`label`. Its value MUST be either a domain-specific marker string or the
literal `None`. A profile omitting the leaf on any entry MUST be refused,
naming that exact indexed leaf (`documents[N].dataset_marker`). `None` is a
valid, accepted declaration meaning "this document never owes a dataset" —
distinct from, and never conflated with, an omitted leaf.

#### Scenario: An omitted leaf refuses by its indexed name
- GIVEN a `documents[N]` entry declaring `directory` and `label` but no
  `dataset_marker`
- WHEN the resolver validates the profile
- THEN it raises `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming
  `documents[N].dataset_marker` exactly
- AND `documents[N].dataset_marker` set to `None` passes validation with no
  refusal

#### Scenario: Why required — a typo becomes a refusal, not silence
- GIVEN a profile author misspells an optional key under a hypothetical
  optional design
- WHEN the demand would have silently disabled itself
- THEN under this requirement, the same misspelling is instead an omitted
  required leaf, refused before any command runs

### Requirement: The Detector Reads The Bound Document's Own Bytes, Never An Engine Literal

The dataset-declared detector MUST answer "does the document bound to this
run declare a dataset?" by reading that document's own bytes (via
`revision_source`/`document_revision_names`) and searching for the entry's
own declared `dataset_marker` string. The engine MUST NOT spell any
domain's dataset-marker text as a literal; the marker is profile-supplied by
construction. When `dataset_marker` is `None` for an entry, the detector
MUST answer false for that entry unconditionally, without reading the
document.

#### Scenario: A declared marker present in the document's bytes answers true
- GIVEN a document entry whose bound revision's bytes contain its declared
  `dataset_marker`
- WHEN the detector runs
- THEN it answers true for that document

#### Scenario: A `None` marker never reads the document
- GIVEN a `documents[N]` entry with `dataset_marker: None`
- WHEN the detector runs for that entry
- THEN it answers false without opening that document's bytes

#### Scenario: No lock catches an engine literal, so construction is the guard
- GIVEN `LockBEngineNeutralityTests` derives its haystack from
  `vocabulary.names`, which does not contain a dataset-marker word
- WHEN a hardcoded `**Dataset:**`-shaped literal is planted directly in the
  engine
- THEN no existing lock fails on it, which is why the marker must be
  profile-supplied rather than relied on a lock to catch

### Requirement: `cmd_verify`'s `with_data` Is Derived From The Declaration, Never Purely From Disk

`cmd_verify` MUST derive `with_data` from the dataset detector's answer for
the document bound to that run, replacing its present
`(target / name / "Data").is_dir()` self-fulfilling read. `expected_dirs`'s
existing shape (`f"{name}/{d}"`, presence-only) is unchanged; only the
source of the `with_data` flag changes for `verify`.

#### Scenario: `missingDirs` newly contains a `Data/`
- GIVEN a target whose bound document declares a dataset and whose
  `{name}/Data/` is absent
- WHEN `cmd_verify` runs
- THEN `missingDirs` contains `{name}/Data`, and `structure_ok` is false —
  captured as a real case, not asserted

#### Scenario: The same target with `Data/` present clears the demand
- GIVEN the identical bound document and target, with `{name}/Data/` created
- WHEN `cmd_verify` runs
- THEN `missingDirs` is empty for that entry — the first control

#### Scenario: An empty `Data/` satisfies the demand
- GIVEN `{name}/Data/` exists but holds no files
- WHEN `cmd_verify` runs
- THEN `missingDirs` does not contain `{name}/Data` — presence only, matching
  `Notebooks/`, `Results/`, `Models/`; judging the data's correctness is out
  of scope

#### Scenario: A document declaring no dataset changes nothing
- GIVEN a document entry with `dataset_marker: None`
- WHEN `cmd_verify` runs
- THEN `with_data` and `missingDirs` for that entry are byte-identical to
  this capability's absence

### Requirement: The Demand Holds The `standing` Stage Through The Existing Mechanism

A `Data/` gap reported in `missingDirs` MUST feed `structure_ok` exactly as
the other three product categories already do, and MUST hold this skill's
`OBJECTIVE_FLOW`'s `standing` stage's `behindWhen` through that same
existing mechanism. No new gate is introduced for this category.

#### Scenario: A missing declared `Data/` holds `standing`
- GIVEN a bound document declaring a dataset and no `{name}/Data/`
- WHEN `standing`'s `behindWhen` is evaluated
- THEN it reports not-yet-behind, through `structure_ok` alone

### Requirement: No New Refusal Code Is Introduced

This capability MUST add zero entries to `reachable_refusal_codes`'s derived
roster. `verify` reports the gap; it never refuses for it.

#### Scenario: The roster is unchanged, asserted not assumed
- GIVEN `reachable_refusal_codes()` before and after this capability
- WHEN compared
- THEN the roster is identical

### Requirement: The Reaching Configuration Ships As A Fixture Before The Shipped Marker Does

A fixture profile declaring a `dataset_marker` MUST exist and prove every
branch above before `experimental-implementation`'s own `documents[0]`
declares its real marker. Declaring the real marker before the detector is
proven against a fixture is indistinguishable from a fixture written to
pass — this project's own prior defect at smaller scale.

#### Scenario: The fixture proves the detector before the shipped marker lands
- GIVEN the fixture profile and its corpus
- WHEN the detector, threading, and `missingDirs` scenarios above all pass
  against the fixture
- THEN only afterward may `documents[0]`'s real marker be declared

### Requirement: Zero Bare `"Data"` Literals Remain Outside `PRODUCT_DIRS`/`PRODUCT_DATA`

Every bare `"Data"` string literal in `classify`, `build_plan`, and
`cmd_verify` MUST be replaced by `PRODUCT_DATA`, completing F5's class
(previously applied only in `expected_dirs`), with zero sealed-digest
movement, since `PRODUCT_DATA == "Data"`.

#### Scenario: The identity refactor leaves every digest unchanged
- GIVEN the seal captured before this replacement
- WHEN the three remaining literals are replaced by `PRODUCT_DATA` and the
  seal re-runs
- THEN every digest is byte-identical

## Boundary (explicitly not built here)

Whether the declared dataset is present, correct, or the same one as a
prior revision is `experimental-deliberation`'s preservation question,
already answered by its `dataset` atom. This capability answers presence of
`Data/` only, never the dataset's identity or correctness.
