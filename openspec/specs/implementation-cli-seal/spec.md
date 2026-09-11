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
entries) against a fixed fixture corpus, invoked through the per-skill
launcher's own entry point — never through the engine module directly, and
never through whichever file `CLI_INVOCATION`/`CLI_PATH` happens to resolve
to internally — capturing raw stdout bytes and exit status, and MUST digest
each.

(Previously: the entry point was implicit in `CLI_INVOCATION`; this
requirement pinned the twenty subcommands but never named the entry point
itself, so a launcher/engine split — introduced by Cut 1 — could silently
seal the wrong file.)

#### Scenario: Every subcommand is captured

- GIVEN the corpus and the 20 registered subcommands
- WHEN capture runs
- THEN each has a digest+exit status, or is in the unsealed set with a reason

#### Scenario: A new subcommand is detected

- GIVEN a 21st subcommand added to `COMMANDS`
- WHEN the coverage check runs
- THEN it fails, naming the uncaptured subcommand

#### Scenario: The sealed entry point is the launcher, not the engine

- GIVEN the engine now lives at
  `_core/implementation/engine/implementation_engine.py`, separate from the
  per-skill launcher
- WHEN the seal invokes any case
- THEN the invoked path is the launcher's literal file, and if `CLI_PATH`
  instead resolved to the engine, the case's digest would move

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
F3's sanctioned delta. `npm test` MUST remain 595/0. The Python suite's
pinned invariant is `skipped=6` and `OK` (no failures, no errors) — `Ran`'s
total count MAY grow as tests are added by this and later cuts and MUST NOT
be pinned to a fixed number.

(Previously: pinned both `Ran 2849` and `skipped=6`. `Ran` was already stale
at `f4e9960` (`Ran 2874`), so the exact-count pin broke on ordinary test
growth across cuts while `skipped=6` held across all three. This corrects
the spec to the invariant that actually survived measurement.)

#### Scenario: Both baselines hold
- GIVEN the change applied after this capability lands
- WHEN both suites re-run, output redirected to files
- THEN `npm test` shows 595 pass/0 fail and the Python suite shows `OK
  (skipped=6)`, with `Ran` at or above its pre-cut count

#### Scenario: `proposal-deliberation` is untouched
- GIVEN the change is scoped to `proposal-implementation`'s shared engine
- WHEN the change's diff is inspected
- THEN no file under `proposal-deliberation` is modified

#### Scenario: A `skipped` count movement is caught
- GIVEN `skipped=6` is the pinned invariant
- WHEN the Python suite runs after this capability lands
- THEN a `skipped` count other than 6 fails the assertion, distinct from
  `Ran` growing, which is expected and unasserted

## ADDED Requirements

### Requirement: The Two-Document Branch Is Sealed By Its Own Corpus, Separate From The Existing 28

A fixture profile declaring two documents, exercised against a corpus of its
own, MUST capture byte-exact stdout and exit status for every pair-shaped
branch this change introduces, digested and committed the same way as the
existing 28-case corpus. The existing single-document corpus under
`tests/seal/` MUST remain untouched by this addition — `git diff --exit-code
tests/seal/` MUST exit 0 both before and after the two-document corpus is
added.

#### Scenario: The existing 28 digests are unaffected by the new corpus existing
- GIVEN the two-document corpus added alongside `tests/seal/`
- WHEN `git diff --exit-code tests/seal/` runs
- THEN it exits 0 — no existing digest moved

#### Scenario: A pair-shaped branch is captured and digested
- GIVEN the two-document fixture profile and its corpus
- WHEN the two-document seal is captured
- THEN each pair-shaped case has a digest and exit status, or is in an
  explicit unsealed set with a reason

#### Scenario: A one-byte change in a pair-shaped case is caught
- GIVEN a stored two-document golden
- WHEN one byte of its captured stdout is mutated and compared
- THEN the comparison goes red
