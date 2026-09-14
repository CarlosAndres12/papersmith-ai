# Delta for experimental-implementation-skill

## ADDED Requirements

### Requirement: `documents[0]` Declares Its Real Dataset Marker, Landed Last

`experimental-implementation`'s `documents[0]` (the experiments document)
MUST declare a real `dataset_marker` value, added only after
`implementation-data-demandability`'s detector, threading, and `missingDirs`
scenarios are already proven green against a fixture profile the shipped
engine could not otherwise pass. `documents[1]` (the mathematical proposal)
MUST declare `dataset_marker: None` permanently — the mathematical domain
binds to no dataset, and this is a recorded decision, never a silent
omission.

#### Scenario: The real marker lands after the fixture proves the mechanism
- GIVEN the fixture profile's dataset scenarios all pass
- WHEN `documents[0]`'s real `dataset_marker` is declared
- THEN it is this capability's last write to `impl_profile.py`

#### Scenario: `documents[1]` never owes a dataset
- GIVEN `documents[1]`'s `dataset_marker: None` declaration
- WHEN the dataset detector runs for `documents[1]`
- THEN it answers false unconditionally, and `documents[1]`'s `Data/` is
  never demanded

### Requirement: `SKILL.md` States The Dataset-Declared `Data/` Demand, Per Product Folder

`SKILL.md` MUST state that a document declaring a dataset makes `{name}/Data/`
demanded for that product folder, that the demand is presence-only, and that
it is scoped per product folder — never to the repository as a whole —
because a run binds to one method via `--name` and a later paper may move to
a different area entirely.

#### Scenario: The stated demand matches the enforced behavior
- GIVEN `SKILL.md`'s updated text
- WHEN compared against `cmd_verify`'s actual `with_data` derivation and
  `expected_dirs`'s per-`{name}` shape
- THEN the stated demand (presence-only, per product folder) matches what is
  enforced, with no claim the engine does not also do
