# implementation-cli-seal Specification

## Purpose

A stdout characterization seal for `proposal-implementation`'s CLI. Captures
byte-exact stdout and exit status for all 20 subcommands against a fixed
corpus, proving preservation across the later profile-driven extraction, and
hosts the two sanctioned behaviour changes (F3, F5) under a declared-delta
discipline. Governs the seal only, not the CLI's existing runtime behavior.

## Requirements

### Requirement: Seal Capture Scope

The seal MUST run all 20 subcommands (20 `cmd_*` functions, 20 `COMMANDS`
entries) against a fixed fixture corpus, capturing raw stdout bytes and exit
status, and MUST digest each.

#### Scenario: Every subcommand is captured

- GIVEN the corpus and the 20 registered subcommands
- WHEN capture runs
- THEN each has a digest+exit status, or is in the unsealed set with a reason

#### Scenario: A new subcommand is detected

- GIVEN a 21st subcommand added to `COMMANDS`
- WHEN the coverage check runs
- THEN it fails, naming the uncaptured subcommand

### Requirement: Corpus Coverage By Construction

The corpus MUST provably exercise: all 14 provenance sites; all 14 findings
sites (populated `tests/findings.py`: `remedy_block`, `adoption`, `uses`,
`introduces`); the 5 hardcoded-path refusals with and without
`IMPLEMENTATION_PROPOSALS`; `Data/` present and absent; a marker-owned and a
hand-authored revision family; a tie.

#### Scenario: Coverage is asserted

- GIVEN the corpus
- WHEN a coverage test runs
- THEN it confirms every site above is reached by at least one case

#### Scenario: A dropped case is caught

- GIVEN a corpus case covering one refusal's `IMPLEMENTATION_PROPOSALS` state
  is removed
- WHEN the coverage test runs
- THEN it fails, naming the uncovered site

### Requirement: Normalization Before Digesting

The seal MUST normalize exactly six sources before digesting —
`_now_iso8601()`, absolute `str(target)`, `CLI_INVOCATION`, `--session` ids,
git shas, `source_digest`/`suite_digest` — each with its own named mutation
test.

#### Scenario: A disabled normalizer reddens

- GIVEN one normalizer is switched off
- WHEN capture is compared to its golden
- THEN it fails, distinguishable from a normalizer never written

#### Scenario: Two immediate captures agree

- GIVEN the corpus run twice in succession
- WHEN both are normalized and digested
- THEN digests match; any differing source is unnormalized, not stored

### Requirement: Digests Committed As Generated Goldens

Digests MUST be committed under `tests/`, not `.gitignore`d, so a seal
captured in one session serves a cut in another.

#### Scenario: Digests survive a clean checkout

- GIVEN a fresh clone at the capturing commit
- WHEN the seal comparison runs with no prior local state
- THEN stored digests are present and readable

### Requirement: Unsealed Commands Are Explicit And Exact

A subcommand whose nondeterminism normalization cannot reach MUST be recorded
in an explicit unsealed set with a reason, not stopping the change. That set
MUST be asserted by an exact-membership test.

#### Scenario: An unrecorded addition is caught

- GIVEN a subcommand added to the unsealed set without updating the test
- WHEN the membership test runs
- THEN it fails

#### Scenario: An unrecorded removal is caught

- GIVEN a subcommand goes from unsealed to sealed (digest added) without
  updating the test
- WHEN the membership test runs
- THEN it fails

### Requirement: Seal Is Mutation-Provable

The comparison MUST detect a single-byte change in any captured output.

#### Scenario: One byte breaks the seal

- GIVEN a stored golden for one subcommand
- WHEN one byte of its captured stdout is mutated and compared
- THEN the comparison goes red

### Requirement: F3 Declared-Delta Discipline

The five refusal messages currently spelling `FORGE_ROOT / 'proposals'` MUST
read via `proposals_root()`. This delta MUST be documented, with before/after
text for all five, in `f3-message-delta.md`, which MUST exist before any
digest is captured. It is the only sanctioned pre/post difference.

#### Scenario: The delta predates the capture

- GIVEN `f3-message-delta.md` with all five before/after pairs
- WHEN the seal is captured
- THEN captured messages match the declared "after" text, and the delta
  document predates the digests

#### Scenario: `cmd_handoff` is unaffected

- GIVEN `cmd_handoff` already omits the path
- WHEN the seal is captured
- THEN its output is unchanged by F3

### Requirement: F5 Zero-Delta Identity Refactor

`PRODUCT_DATA = PRODUCT_DIRS[1]` replacing the bare `"Data"` literal in
`expected_dirs` MUST be applied only after capture, and MUST produce zero
seal delta, since `PRODUCT_DIRS[1] == "Data"`.

#### Scenario: F5 leaves every digest unchanged

- GIVEN a seal captured after F3 but before F5
- WHEN F5 is applied and the seal re-captured
- THEN every digest is byte-identical to the pre-F5 capture

### Requirement: Non-Interference With Sibling Suites

The change MUST NOT alter either existing suite's pass/fail outcome beyond
F3's sanctioned delta. `npm test` MUST remain 595/0; the Python suite MUST
remain `Ran 2783 ... OK (skipped=6)`, both re-run and pasted after the change.

#### Scenario: Both baselines hold

- GIVEN the change applied on `a851390`
- WHEN both suites re-run, output redirected to files
- THEN `npm test` shows 595 pass/0 fail and Python shows `Ran 2783` `OK
  (skipped=6)`

#### Scenario: `proposal-deliberation` is untouched

- GIVEN the change is scoped to `proposal-implementation`
- WHEN the change's diff is inspected
- THEN no file under `proposal-deliberation` is modified
