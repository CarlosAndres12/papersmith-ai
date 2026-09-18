# Delta for Paper Declarations

## ADDED Requirements

### Requirement: The Declarations Region Is The Single Source Any Reader Consults

Any reader that reports satisfied facts or declarations for a `paper_dir` —
including `readiness` (`writing-readiness`) — MUST derive that state by
parsing this same `declarations` region, never from a separately memorized
or separately persisted copy. This pins the region as the one canonical
source `writing-readiness`'s declaration-aware behavior reads from.

#### Scenario: A second reader reads the same region, not a copy

- GIVEN a `declarations` region recording `formulation` as satisfied
- WHEN two independent verbs (`declare --reopen`'s report and `readiness`)
  each need to know whether `formulation` is satisfied
- THEN both derive the same answer from parsing this one region, and
  neither reads a separate cache

### Requirement: Skeleton Presence Is Read From Opened Block Ids, Never From A Declaration Record

The two skeleton-startup decisions (`skeleton-startup`) are inferred from
`main.tex`'s opened block ids, not recorded as a `declaration` or
`fact-resolution` in this region. A `declare` call attempting to record
either decision under a declaration or fact id MUST refuse — neither
decision is a member of the six-declaration or ten-fact closed vocabularies
this spec already fixes.

#### Scenario: The skeleton decisions are not declarable

- GIVEN an attempt to `declare` "related-work-present" as a declaration id
- WHEN `declare` validates the id
- THEN it refuses `UNKNOWN_DECLARATION`, because the skeleton decision is
  read from disk, never recorded in this region
