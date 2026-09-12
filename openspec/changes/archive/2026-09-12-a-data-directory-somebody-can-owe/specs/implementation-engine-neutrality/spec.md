# Delta for implementation-engine-neutrality

**Budget note.** This delta exceeds 650 words because the MODIFIED workflow
requires copying the entire pre-existing requirement block — including its
full measured-movers table — before editing it; a partial copy would lose
rows at archive time.

## MODIFIED Requirements

### Requirement: Ten Domain-Specific Profile Fields Are The Whole Vocabulary Surface

Each field MUST be a validated resolver leaf, named in
`IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` by its dotted (or indexed) path, and MUST move only its
own named sealed digest(s) when changed. A field satisfying neither MUST NOT exist.

| Field | Read by | Digest(s) moved — MEASURED |
|---|---|---|
| `provenance.claim_key` | 14 provenance sites; kit lock | `probe`, `verify-a`, `verify-b`, `verify-t` |
| `provenance.authored_init_sentence` | `authored_package_init` | **none — zero-mover** |
| `findings.locus_key` | `cmd_admit` field loop, impact | `handoff-e1`, `verify-a`, `verify-b` |
| `findings.remedy_locus_key` | same loop, `cmd_handoff` | `handoff-e1`, `verify-a`, `verify-b` |
| `findings.notation_keys` | `handoff`/report payloads | `handoff-e1`, `verify-a`, `verify-b` |
| `findings.citation_pattern` | `CITATION_RE` | **none — zero-mover** |
| `vocabulary.subject_singular` | refusal builders | `compose` |
| `vocabulary.subject_plural` | refusal builders | **none — zero-mover** |
| `vocabulary.subject_singular_es` | Spanish refusal builders | `handoff-e1` |
| `vocabulary.subject_plural_es` | Spanish refusal builders | `handoff-e1` |
| `vocabulary.subject_collective` | refusal builders | **none — zero-mover** |
| `vocabulary.subject_collective_es` | Spanish refusal builders | **none — zero-mover** |
| `vocabulary.artifact_noun` | `authored_package_init` | **none — zero-mover** |
| `vocabulary.names` | both locks below, nothing else | lock goes red |
| `documents[i].directory` | `proposals_root()`, 5 refusals, validated per index | index 0: `admit-e0`, `close-e0`, `gate-e0`, `offer-e0`, `position-e0` — unchanged from the measured set |
| `documents[i].label` | `undeclared_arms_note` only, validated per index | **none — zero-mover**, any index |
| `documents[i].dataset_marker` | the dataset detector; `cmd_verify`'s `with_data`; `plan`'s conditional document-name key | measured only after real subprocess verification, never forecast — entered here as a passing scenario's exact result, mirroring this table's own correction history below |

**This table was corrected after verification and is now the measured truth, not a
prediction.** Its first version was written from design.md's forecast and diverged
from `MEASURED_MOVERS` in at least six rows. The most consequential: it claimed
`documents.label` moves "the same 5 refusals" as `documents.directory`. It does
not. `DOCUMENTS_LABEL` is read at exactly ONE call site (`undeclared_arms_note`,
inside `ARMS_UNDECLARED_CONSEQUENCE`'s `.format()`), gated on `declaration.get(
"arms")` being falsy AND at least one module declaring `sections` — a condition
**none of the 28 sealed cases hits**.

**Seven of the fifteen pre-existing leaves are zero-movers**, and that is a
recorded state, not a gap to hunt a stronger test for. A zero-mover is still read
— its removal raises `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming its exact
dotted (or indexed) leaf — it is simply not observable in the sealed stdout of
these particular fixtures. The removal-refusal plus the two neutrality locks are
its whole instrument, and saying so is the honest outcome. `documents[i]
.dataset_marker`'s own zero-mover-or-real-mover status MUST be measured, not
assumed, before this row's third column is treated as final — repeating that
measurement discipline is this table's own established correction pattern, not a
new one invented for this leaf.

Verification established this was **not a harness artifact**. A positive control
ran first: mutating `provenance.claim_key`, a known real mover, reproduced apply's
recorded set byte for byte, proving the profile genuinely reaches the seal's child
process. Only then were three zero-movers re-tested, and all three held.

Under `len(documents) > 1`, each entry is validated and refused by its own
index: removing `documents[1].directory` MUST raise
`IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming `documents[1].directory`
exactly, never the bare `documents.directory`. The identical rule now applies
to `documents[1].dataset_marker`.
(Previously: the table held fifteen leaves, with no `dataset_marker` row; a
`documents[N]` entry could omit any dataset declaration silently, since no
leaf named it as required.)

#### Scenario: A missing leaf refuses by its own dotted name
- GIVEN a profile omitting `findings.remedy_locus_key`
- WHEN the resolver validates it
- THEN it raises `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming that exact leaf

#### Scenario: Changing one field moves only its named digest
- GIVEN the sealed 28-case corpus
- WHEN `provenance.claim_key` changes and the seal re-runs
- THEN only `probe`, `verify-a`, `verify-b` and `verify-t` move -- the measured set, never `handoff` -- and the other 24 are byte-identical

#### Scenario: A second document's missing leaf refuses by its indexed name
- GIVEN a two-document fixture profile with `documents[1].directory` omitted
- WHEN the resolver validates it
- THEN it raises `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming
  `documents[1].directory`, not `documents.directory`

#### Scenario: A missing `dataset_marker` refuses by its indexed name
- GIVEN a `documents[N]` entry omitting `dataset_marker`
- WHEN the resolver validates the profile
- THEN it raises `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming
  `documents[N].dataset_marker` exactly, and `documents[N].dataset_marker`
  set to `None` passes with no refusal

## ADDED Requirements

### Requirement: A New Core File Naming A `PRODUCT_DIRS` Member Stays Reachable By `CoreNamesNoDomainTests`

`CoreNamesNoDomainTests` scans `CORE.glob("*.py")` non-recursively and fails
any core-level file whose text names a `PRODUCT_DIRS`/`SOURCE_ROOTS` member.
Any new file this capability adds that names `PRODUCT_DATA` or `"Data"`
MUST live under `_core/implementation/engine/`, which that non-recursive
glob does not reach, or MUST be added to the existing engine module rather
than a new flat `_core/implementation/*.py` file.

#### Scenario: A flat detector file reddens the guard
- GIVEN a hypothetical detector module placed directly under
  `_core/implementation/`, naming `PRODUCT_DATA`
- WHEN `CoreNamesNoDomainTests` runs
- THEN it fails, naming that file

#### Scenario: The same code under `engine/` does not
- GIVEN the identical detector code added to
  `_core/implementation/engine/implementation_engine.py` instead
- WHEN `CoreNamesNoDomainTests` runs
- THEN it passes, unaffected
