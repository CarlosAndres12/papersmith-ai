# Contract Audit Specification

## Purpose

A drafted block passing `evidence-bound-drafting` may still violate rules the
operator wrote in prose. `contract-audit` reads a contract's
`## Disqualifiers` bullets verbatim — zero interpretation in code — against
the draft, and returns a verdict per bullet. This is what makes the ten
contracts enforceable instead of decorative.

## Requirements

### Requirement: Verbatim Disqualifier Extraction

The auditor MUST read a contract's `## Disqualifiers` bullets as literal text
and pass them to the check unmodified. No disqualifier bullet's wording MUST
be hardcoded, special-cased, or paraphrased in code.

#### Scenario: A contract's own bullet text reaches the audit unchanged

- GIVEN a contract's `## Disqualifiers` section with a bullet of arbitrary
  wording
- WHEN the auditor runs
- THEN the exact bullet text is what the audit evaluates against, byte for
  byte

### Requirement: Per-Bullet Verdict With Quoted Span

For each disqualifier bullet, the auditor MUST return exactly one of `fires`,
`clear`, or `undecidable`. A `fires` verdict MUST quote the offending span of
the drafted block. A verdict that cites no span MUST be `undecidable`, never
`fires`.

#### Scenario: A firing disqualifier quotes its span

- GIVEN a drafted block violating one disqualifier bullet
- WHEN the auditor evaluates that bullet
- THEN it returns `fires` with the offending span quoted from the draft

#### Scenario: A clear disqualifier and a firing one coexist in one run

- GIVEN a drafted block where one bullet is violated and a second is not
- WHEN the auditor evaluates both
- THEN the first returns `fires` with its span and the second returns
  `clear`, in the same run

### Requirement: Undecidable Is Reported, Not Blocking On Its Own

`undecidable` means the check could not resolve a verdict for that bullet, not
that the block failed it. Uncertainty about the *work* blocks; uncertainty
about the *check* does not, because a check with no verdict has no authority
to refuse. `undecidable` MUST be reported in the same vocabulary as
`unmeasured`, `unprovenanced`, and `unclassified`. The audit's overall outcome
MUST be decided only by whether any bullet returns `fires`; an audit whose
bullets are all `clear` or `undecidable`, with none `fires`, MUST NOT block.

#### Scenario: An all-undecidable audit does not block

- GIVEN a drafted block where every disqualifier bullet returns `undecidable`
  and none returns `fires`
- WHEN the audit's overall outcome is computed
- THEN the audit does not block, and every `undecidable` verdict is reported
  alongside that outcome

#### Scenario: One firing bullet blocks regardless of other undecidables

- GIVEN a drafted block with one `fires` bullet and two `undecidable` bullets
- WHEN the audit's overall outcome is computed
- THEN the audit blocks, citing the `fires` bullet's quoted span

### Requirement: Absent Disqualifiers Heading Refuses

A contract file with no `## Disqualifiers` heading MUST refuse
`DISQUALIFIERS_ABSENT`. A silently un-audited block is how "enforceable"
quietly becomes "decorative" again.

#### Scenario: A contract missing the heading refuses

- GIVEN a contract file with no `## Disqualifiers` section
- WHEN the auditor is invoked against it
- THEN it refuses `DISQUALIFIERS_ABSENT` naming the contract

#### Scenario: All ten shipped contracts carry the heading

- GIVEN the ten `sections/*.md` contract files as shipped
- WHEN each is checked for a `## Disqualifiers` heading
- THEN all ten carry it and none refuses `DISQUALIFIERS_ABSENT`
