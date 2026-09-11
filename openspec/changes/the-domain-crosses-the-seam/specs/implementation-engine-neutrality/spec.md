# Delta for implementation-engine-neutrality

## ADDED Requirements

### Requirement: Ten Domain-Specific Profile Fields Are The Whole Vocabulary Surface

Each field MUST be a validated resolver leaf, named in
`IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` by its dotted path, and MUST move only its
own named sealed digest(s) when changed. A field satisfying neither MUST NOT exist.

| Field | Read by | Digest(s) moved |
|---|---|---|
| `provenance.claim_key` | 14 provenance sites; kit lock | `verify`, `handoff` |
| `provenance.authored_init_sentence` | `authored_package_init` | `materialize` |
| `findings.locus_key` | `cmd_admit` field loop, impact | `admit` |
| `findings.remedy_locus_key` | same loop, `cmd_handoff` | `admit`, `handoff` |
| `findings.notation_keys` | `handoff`/report payloads | `handoff` |
| `vocabulary.subject_singular`/`_plural` | Spanish refusal builders | `handoff` |
| `vocabulary.artifact_noun` | `authored_package_init` | `materialize` |
| `vocabulary.names` | both locks below, nothing else | lock goes red |
| `documents.directory` | `proposals_root()`, 5 refusals | the 5 path refusals |
| `documents.label` | same 5 refusals | the same |

#### Scenario: A missing leaf refuses by its own dotted name
- GIVEN a profile omitting `findings.remedy_locus_key`
- WHEN the resolver validates it
- THEN it raises `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming that exact leaf

#### Scenario: Changing one field moves only its named digest
- GIVEN the sealed 28-case corpus
- WHEN `provenance.claim_key` changes and the seal re-runs
- THEN only `verify` and `handoff` digests move; the other 26 are byte-identical

### Requirement: The Coarse Provenance Key Stays Shared, Never Profile-Supplied

`"sections"` MUST stay a hardcoded literal in the engine and every kit asset. The
profile MUST NOT expose a coarse-key field. `unreached_mathematics` MUST cross
`__provenance__["sections"]` against `__benchmark__["arms"][x]["sections"]` using that
literal on both sides.

#### Scenario: The join reads the literal on both sides, unaffected by an unread key
- GIVEN a profile declaring an extra, unread `provenance.drift_unit_key`
- WHEN `unreached_mathematics` computes the join
- THEN both sides still read the literal `"sections"`, and the join is unaffected

### Requirement: §B1 Fields Excluded For A Recorded Reason Are Not Present

| Field | Reason |
|---|---|
| `provenance.drift_unit_key` | it IS the coarse key; removed by the B2 ruling |
| `provenance.revision_key` | shape (scalar->pair) is Cut 3 |
| `document_reader.drift_units` | no Cut-2 reader |
| `documents.marker` | F6; a fifth spelling worsens the coupling |
| `cli_invocation` | rejected at Cut 1: profile supplies the path only |

#### Scenario: None of the five keys is in the resolver's validated set
- GIVEN the resolver's required-leaf table after Cut 2
- WHEN it is inspected
- THEN none of the five keys above appears in it

### Requirement: The Campaign-Proposal Exclusion List Is Enforced By A Test

A test MUST assert `proposalDigest`, `GATE_PROPOSAL_*`, `_proposal_digest`,
`_verify_gate_proposal`, `_gate_proposal_question`, `_verify_optional_election`,
`cmd_propose`, `_authorization_binding`, `_verify_gate_authorization`,
`_campaign_identity`, `_load_remote_execution_*` remain unrenamed by this cut.

#### Scenario: A rename to any excluded symbol is caught
- GIVEN a hypothetical edit renaming `proposalDigest`
- WHEN the exclusion test runs
- THEN it fails, naming the symbol; unmodified, the test passes

### Requirement: The Kit Template's Provenance Keys Agree With The Profile

`assets/kit/src/module.py`'s `"equations"` key MUST equal `PROFILE.provenance.claim_key`;
its `"sections"` key MUST equal the shared literal.

#### Scenario: Divergence is caught
- GIVEN the kit template edited to a different `"equations"` value
- WHEN the lock runs
- THEN it fails, naming the divergent key; reverted, it passes

### Requirement: The Engine Spells No Declared Domain Word

A neutrality lock MUST fail when any `vocabulary.names` word appears anywhere — code,
string, comment, or docstring — under `_core/implementation/engine/`.

#### Scenario: A planted word reddens it, reverting restores green
- GIVEN a `vocabulary.names` word planted anywhere in `engine/`, including a comment
- WHEN the lock runs
- THEN it fails, naming the file and word; reverting the plant restores green

### Requirement: A Python Mirror Discovers Profiles By Globbing, Not Hardcoding

The Python domain-profile lock MUST discover profiles by globbing `*/impl_profile.py`,
mirroring `discoverProfiles` in `tests/proposal-deliberation-domain-profile-lock.test.mjs`.

#### Scenario: A third skill is held without editing the lock
- GIVEN a hypothetical third skill's `impl_profile.py` declaring empty `vocabulary.names`
- WHEN the lock runs
- THEN it fails on that skill with zero edits to the lock file itself

## MODIFIED Requirements

### Requirement: Engine Refuses To Start Without A Domain Profile

The engine MUST fail closed, with a named refusal, when `IMPLEMENTATION_DOMAIN_PROFILE`
is unset, non-absolute, or resolves to a module missing a required field — now including
the ten Cut-2 domain fields alongside Cut 1's `kit.root`, `cli.path`, `objective`. It
MUST NOT default to any domain.
(Previously: validated only `kit.root`, `cli.path`, `objective`.)

#### Scenario: Unset variable refuses
- GIVEN `IMPLEMENTATION_DOMAIN_PROFILE` is unset
- WHEN the engine is imported
- THEN it raises a named refusal before any command runs

#### Scenario: Malformed profile refuses
- GIVEN the variable is relative, or the module omits a required field
- WHEN the engine loads it
- THEN it raises a refusal named for that exact case

#### Scenario: A missing Cut-2 leaf refuses by its own dotted name
- GIVEN a profile carrying Cut 1's three fields but omitting `vocabulary.artifact_noun`
- WHEN the engine loads it
- THEN it raises `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming that leaf
