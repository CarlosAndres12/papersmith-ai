# Contract Currency Specification

## Purpose

Reports whether written blocks still stand against the current whole-file
contract hash, by reading the `%% paper-writing provenance` region that
`the-paper-carries-its-own-decisions` (Phase 3) writes at `substitute`
time. This change defines and reads that interface; it does not write the
record (resolves proposal question 5 — Phase 3 is the owner).

## Requirements

### Requirement: Classification

MUST classify as `out-of-reach today`: no landed phase writes the
provenance record as of this change, so check B ships refusing rather than
silently reporting zero stale blocks.

#### Scenario: Classification is data, not prose

- GIVEN any completed run
- WHEN check B's entry is read
- THEN it carries `classification: out-of-reach today`

### Requirement: An Absent Provenance Record Reports Check B Unmeasured, Not The Run Refused

An absent (or present-but-empty) `%% paper-writing provenance` region MUST
report check `contract-currency` alone `unmeasured`, reason
`CONTRACT_RECORD_ABSENT` — MUST NOT report zero stale blocks, which would
be indistinguishable from a genuinely current paper, and MUST NOT refuse
the whole run: every other check still reports a real verdict, and `verify`
exits `0`.

**Reconciled from this requirement's earlier "refuses ... exits non-zero"
wording** (`sdd-apply`, `the-couplings-hold-or-they-do-not`): design.md's
own decision narrows the proposal's run-level-refusal framing specifically
for this tier of inability, because `the-paper-carries-its-own-decisions`
(the provenance region's own writer) had not landed when this capability's
first checks needed to be reachable, and a run-level refusal here would
have made all seven checks unreportable the moment any paper lacked a
single `--contract` write — contradicting this change's own requirement
that every check be reachable today. `DECLARATION_RECORD_ABSENT` (the
whole declaration record entirely absent, `coupling-verification` spec)
remains the one run-level refusal; this is the narrower, check-scoped tier
beside it.

#### Scenario: M7 — absent record reports check B unmeasured, not the run refused

- GIVEN `paper/main.tex` carries no provenance region
- WHEN `verify` runs
- THEN check B reports `unmeasured`, reason `CONTRACT_RECORD_ABSENT`, no
  stale-block count is reported, `main.tex` is unchanged, every other
  check still reports a real verdict, and `verify` exits `0`

### Requirement: Whole-File Hash Semantics Are Inherited, Not Narrowed

When the provenance region is present, a block's recorded contract sha256
MUST be compared against the current whole-file contract hash. Editing one
block's guidance changes the whole-file hash and MUST flag every block of
that section as stale, not only the edited block — inherited from Phase
3's own accepted over-reporting tradeoff, never narrowed here.

#### Scenario: One edit flags a whole section

- GIVEN a provenance record where two blocks of one section recorded the
  same contract hash, and that section's contract file changes by one byte
- WHEN check B runs
- THEN both blocks are reported stale, not only the edited one

### Requirement: verify Never Writes The Provenance Record

`verify` MUST NOT write, repair, or regenerate the provenance region under
any input, including a refusal path.

#### Scenario: A refusal leaves the record untouched

- GIVEN check B refuses `CONTRACT_RECORD_ABSENT` or reports stale blocks
- WHEN `main.tex` is read afterward
- THEN its bytes are identical to before `verify` ran
