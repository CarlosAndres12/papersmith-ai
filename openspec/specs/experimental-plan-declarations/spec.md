# Experimental Plan Declarations Specification

## Purpose

An `experimental-deliberation` document plans work that has not happened. A
reader — and a reviewer — must be able to check, from the bytes alone, what
data the plan runs on and what statistical procedure will decide its result.
Today both are doctrine only, asked for in `SKILL.md` prose and decided by
nothing in `preservation-experimental.ts`. This capability makes both
hard-blocking canonical-form rules, at the same severity as the four rules
`violations()` already enforces (`report-table-fabricated-value`,
`url-without-verification-marker`, `baseline-missing-repository-url`,
`baseline-missing-venue-year`), reached the same way: through
`profile.preservation.violations`, on every `CREATE_INITIAL_REVISION` and
every successor accept, before any write.

## Requirements

### Requirement: A document declares exactly one dataset

The system MUST refuse to publish, as v1 or as any successor, an
`experimental-deliberation` document that does not carry exactly one
`**Dataset:** …` line, matched anywhere in the document's bytes (no named
section or boundary machinery), using the same bold-label shape
`**Success criterion:**` already uses. Zero occurrences and two or more
occurrences MUST both be refused as violations of the canonical form — a hard
block that no acknowledgment clears, exactly like the four existing
`violations()` rules. Two occurrences are an ambiguity about which dataset the
plan uses, and the engine MUST NOT resolve that ambiguity by picking one line
silently.

#### Scenario: A single dataset line is accepted

- GIVEN a candidate whose bytes contain exactly one `**Dataset:** …` line and
  otherwise satisfies the canonical form
- WHEN `violations()` runs against it
- THEN the result contains no violation naming the dataset rule

#### Scenario: A missing dataset line is refused

- GIVEN a candidate whose bytes contain zero `**Dataset:** …` lines
- WHEN `violations()` runs against it
- THEN the result contains a violation naming the missing-dataset rule and the
  violation's line MUST be present
- AND `CREATE_INITIAL_REVISION` for that candidate returns `status: 'blocked'`
  and writes nothing

#### Scenario: Two dataset lines are refused, not de-duplicated

- GIVEN a candidate whose bytes contain two distinct `**Dataset:** …` lines
- WHEN `violations()` runs against it
- THEN the result contains a violation naming the duplicate-dataset rule,
  naming both lines or the second occurrence
- AND the engine does not select either line as authoritative

#### Scenario: v1 is checked, not only successors

- GIVEN an idea and source fragments that compose into v1 content missing a
  `**Dataset:** …` line
- WHEN `CREATE_INITIAL_REVISION` runs
- THEN it returns `status: 'blocked'` with code
  `INITIAL_REVISION_CANONICAL_FORM_VIOLATION`, naming the dataset rule
- AND no revision file is written

### Requirement: A declared dataset is a preservation atom

`extractAtoms` MUST recognize a new atom kind, `dataset`, extracted from the
same `**Dataset:** …` line the violation rule matches, keyed by its collapsed
text (matching the existing atoms' keying-by-text convention, not by a
digest). The atom is presence-based, like the other five kinds: it exists or
it does not, never counted. Its purpose is distinct from the hard block above
— the hard block guarantees a dataset line exists in every published version;
the atom guarantees a silent swap between two versions surfaces as a loss the
author must acknowledge by id before publishing, because a different dataset
invalidates everything the `validated` stage searched.

#### Scenario: A dataset atom is extracted from a compliant document

- GIVEN a document containing one `**Dataset:** ImageNet-R, 2021 split` line
- WHEN `extractAtoms` runs
- THEN the returned map contains one entry of kind `dataset` whose text is
  the collapsed dataset line

#### Scenario: Changing the dataset between two versions is a reportable loss

- GIVEN a published revision declaring `**Dataset:** Office-Home`
- WHEN a successor candidate replaces it with `**Dataset:** DomainNet` and
  nothing else changes about that atom
- THEN the preview reports the `Office-Home` dataset atom as lost in
  `preservationDelta`
- AND accept is refused with the removals-not-acknowledged code unless the
  lost id is echoed in `acknowledgedRemovals`

#### Scenario: Rewording the dataset line without changing its meaning is not a loss

- GIVEN a published revision declaring a dataset line
- WHEN a successor candidate repeats the identical collapsed dataset text
  elsewhere in the document, unchanged
- THEN no dataset atom is reported lost, matching the presence-based
  atom contract already proven for the other five kinds

### Requirement: A document declares exactly one adequate validation scheme

The system MUST refuse to publish, as v1 or as any successor, an
`experimental-deliberation` document that does not carry exactly one
`**Validation scheme:** …` line (same bold-label shape, matched anywhere in
the bytes) whose text names a statistical test, seeds, and repetitions, and is
not reducible to a denylisted placeholder (`tbd`, `n/a`, `pending`) or to a
non-test output (`p-value`, `significance`). This is a hard block only — the
validation scheme takes no atom. There is no closed vocabulary of test names;
a legitimate test never seen before MUST be accepted as long as seeds and
repetitions are also present and no denylisted term stands in for the test
name.

#### Scenario: A complete validation scheme is accepted

- GIVEN a candidate containing `**Validation scheme:** paired t-test, 5
  seeds, 10 repetitions per condition`
- WHEN `violations()` runs against it
- THEN the result contains no violation naming the validation-scheme rule

#### Scenario: A novel, legitimate test name is accepted without a vocabulary update

- GIVEN a candidate containing `**Validation scheme:** Friedman test with
  Nemenyi post-hoc, 3 seeds, 20 repetitions`, a test name absent from any
  denylist or fixture the rule was built against
- WHEN `violations()` runs against it
- THEN the result contains no violation naming the validation-scheme rule

#### Scenario: A missing validation-scheme line is refused

- GIVEN a candidate with zero `**Validation scheme:** …` lines
- WHEN `violations()` runs against it
- THEN the result contains a violation naming the missing-validation-scheme
  rule

#### Scenario: A denylisted placeholder is refused even though the line is non-empty

- GIVEN a candidate containing `**Validation scheme:** TBD`
- WHEN `violations()` runs against it
- THEN the result contains a violation naming the validation-scheme rule,
  because the text reduces to a denylisted placeholder

#### Scenario: A non-test output named alone is refused

- GIVEN a candidate containing `**Validation scheme:** p-value`
- WHEN `violations()` runs against it
- THEN the result contains a violation naming the validation-scheme rule,
  because a p-value is an output a test produces, not the test itself, and no
  seeds or repetitions are present either

#### Scenario: A named test without seeds or repetitions is refused

- GIVEN a candidate containing `**Validation scheme:** paired t-test`, naming
  a real test but no seed count and no repetition count
- WHEN `violations()` runs against it
- THEN the result contains a violation naming the validation-scheme rule

#### Scenario: Seeds and repetitions without a named test are refused

- GIVEN a candidate containing `**Validation scheme:** 5 seeds, 10
  repetitions`, naming no statistical test
- WHEN `violations()` runs against it
- THEN the result contains a violation naming the validation-scheme rule

#### Scenario: Two validation-scheme lines are refused

- GIVEN a candidate containing two distinct `**Validation scheme:** …` lines
- WHEN `violations()` runs against it
- THEN the result contains a violation naming the duplicate rule
- AND the engine does not select either line as authoritative

#### Scenario: One line naming more than one test satisfies the cardinality rule

- GIVEN a candidate containing exactly one `**Validation scheme:** paired
  t-test and Wilcoxon signed-rank, 5 seeds, 10 repetitions` line
- WHEN `violations()` runs against it
- THEN the result contains no violation naming the validation-scheme rule,
  because the cardinality rule counts declaration lines, not test names

### Requirement: A URL inside a dataset or validation-scheme line still needs its verification tag

No new rule governs a URL that appears inside a `**Dataset:**` or
`**Validation scheme:**` line. The existing document-wide
`url-without-verification-marker` rule already applies to every external URL
regardless of where it sits.

#### Scenario: An untagged URL inside a dataset line is caught by the existing rule

- GIVEN a candidate containing `**Dataset:** see https://example.org/data-card`
  with no verification tag
- WHEN `violations()` runs against it
- THEN the result contains a violation with rule
  `url-without-verification-marker` naming that line
- AND no new rule name is introduced for this case

### Requirement: The tutor doctrine opens from the dataset and always proposes the validation scheme

`SKILL.md`'s "You are the tutor" bullet list MUST gain two bullets, in the
same voice as the eight existing ones: a bold lead phrase, then the reasoning,
then why the failure matters if the bullet is ignored. One bullet MUST state
that the deliberation always opens from the dataset. One bullet MUST state
that the tutor always proposes and presents the validation scheme to the
user, not merely accepts one the user names unexamined.

#### Scenario: The dataset-opening bullet matches the section's voice

- GIVEN the two new bullets added to the tutor section
- WHEN compared against the eight existing bullets in that list
- THEN each new bullet begins with a bolded lead phrase, states the reasoning,
  and states why skipping it fails, matching the existing bullets' shape

#### Scenario: The validation-scheme bullet is present and distinct from the dataset bullet

- GIVEN the tutor section after this change
- WHEN read for a bullet about the statistical validation scheme
- THEN a bullet distinct from the dataset-opening bullet instructs the tutor
  to propose and present the validation scheme, not merely accept an
  unexamined one

### Requirement: SKILL.md no longer claims v1 content is unvalidated

The section titled "Creating v1, and the gap nothing enforces" MUST be
corrected: it currently states `initial-revision-creation.ts` "contains no
reference to `validateCandidate`, to `violations`, or to preservation," which
is false — that file imports `violations` and runs it against composed v1
before any write. The section's title, its claim, and the "rule ... which
nothing enforces" it derives MUST be replaced with text stating that v1 is
checked by the same canonical-form gate as every successor.

#### Scenario: The corrected section states the true reach of the v1 gate

- GIVEN `SKILL.md` after this change
- WHEN a reader reaches the section previously titled "Creating v1, and the
  gap nothing enforces"
- THEN the section no longer claims `initial-revision-creation.ts` contains
  no reference to `violations` or to preservation
- AND it states that `CREATE_INITIAL_REVISION` runs the same
  `violations()` check as the successor path, before any write

### Requirement: Both rules are proven able to fail

Each rule added under this capability MUST be exercised by at least one test
that a mutation of the rule (deleting it, or weakening its condition) would
turn from passing to failing — a guard that only ever asserts an absence and
can never be observed to fire is not a guard.

#### Scenario: Deleting the dataset rule is caught by its own test suite

- GIVEN the dataset presence rule removed from `violations()`
- WHEN the test asserting a missing-dataset document is refused runs
- THEN that test fails, proving the assertion depends on the rule existing

#### Scenario: Deleting the validation-scheme rule is caught by its own test suite

- GIVEN the validation-scheme rule removed from `violations()`
- WHEN the test asserting a `TBD` validation scheme is refused runs
- THEN that test fails, proving the assertion depends on the rule existing
