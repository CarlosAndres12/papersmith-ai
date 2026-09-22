# Delta for Paper Declarations

## ADDED Requirements

### Requirement: declare Refuses A Produced Fact

`declare` MUST refuse `PRODUCED_FACT_UNDECLARABLE` (work-state) when asked to
record a `fact-resolution` for a fact id that has a producing block
(`fact-production`), naming the fact id and its producing block. Only a fact
resolving to an external source (`FACT_SOURCE_ROOT`) may be recorded through
this region; a produced fact's satisfaction is read from its producer's own
written status, never authored twice.

#### Scenario: Declaring a produced fact refuses

- GIVEN `gap` classified PRODUCED, with `related-work.rw-closing` as its
  producer
- WHEN `declare --fact gap --value ...` is invoked
- THEN it refuses `PRODUCED_FACT_UNDECLARABLE` naming `gap` and
  `related-work.rw-closing`

#### Scenario: Declaring an external fact is unaffected

- GIVEN `formulation`, resolved from `FACT_SOURCE_ROOT`, with no producing
  block
- WHEN `declare --fact formulation --value ...` is invoked
- THEN it records the fact resolution as before, with no refusal

## MODIFIED Requirements

### Requirement: The Declarations Region Is The Single Source Any Reader Consults

Any reader that reports satisfied facts or declarations for a `paper_dir` —
including `readiness` (`writing-readiness`) — MUST derive that state by
parsing this same `declarations` region, never from a separately memorized
or separately persisted copy. A fact whose producer is a block
(`fact-production`) is excluded from this region entirely: its satisfaction
is derived from that producer block's own written status, and this region
never holds — and is never consulted for — a resolution of it.
(Previously: every fact's satisfied state, produced or not, was read from
this region alone, with no carve-out for a fact a block produces.)

#### Scenario: A second reader reads the same region, not a copy

- GIVEN a `declarations` region recording `formulation` as satisfied
- WHEN two independent verbs (`declare --reopen`'s report and `readiness`)
  each need to know whether `formulation` is satisfied
- THEN both derive the same answer from parsing this one region, and
  neither reads a separate cache

#### Scenario: A produced fact's satisfaction bypasses this region

- GIVEN a `declarations` region holding no entry for `gap`, and
  `related-work.rw-closing` (gap's producer) already written
- WHEN a reader asks whether `gap` is satisfied
- THEN it answers satisfied from `rw-closing`'s written status, never by
  finding — or failing to find — an entry for `gap` in this region
