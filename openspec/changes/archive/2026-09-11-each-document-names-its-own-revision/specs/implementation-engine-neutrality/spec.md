# Delta for implementation-engine-neutrality

Text-only citation correction, folded into this change because it is two
lines and belongs to the same "a live spec naming a symbol that does not
exist" defect class this change is already measuring elsewhere. No
requirement behavior changes.

## MODIFIED Requirements

### Requirement: The Coarse Provenance Key Stays Shared, Never Profile-Supplied

`"sections"` MUST stay a hardcoded literal in the engine and every kit asset. The
profile MUST NOT expose a coarse-key field. `unreached_modules` MUST cross
`__provenance__["sections"]` against `__benchmark__["arms"][x]["sections"]` using that
literal on both sides.

(Previously: this requirement's text and its scenario cited
`unreached_mathematics`. Cut 2 renamed the engine symbol to
`unreached_modules`; this spec was not updated to follow. Correction only —
the requirement's behavior is unchanged.)

#### Scenario: The join reads the literal on both sides, unaffected by an unread key
- GIVEN a profile declaring an extra, unread `provenance.drift_unit_key`
- WHEN `unreached_modules` computes the join
- THEN both sides still read the literal `"sections"`, and the join is unaffected
