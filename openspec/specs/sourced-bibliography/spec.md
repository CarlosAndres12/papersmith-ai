# Sourced Bibliography Specification

## Purpose

`paper/refs.bib` built exclusively from resolved metadata, with provenance on every
entry, so "never hand-typed" is a checked property rather than a claim.

## Requirements

### Requirement: Every Entry Originates From Resolved Metadata

Every `refs.bib` entry MUST originate from a CLI resolution result (see
`literature-search`) and MUST carry that result's resolver name and metadata digest
as provenance fields on the entry. An entry with no such provenance MUST refuse
`ENTRY_UNSOURCED`. This check MUST require no network access.

#### Scenario: A resolved entry is accepted

- GIVEN a `refs.bib` entry written from a CLI resolution result carrying resolver
  and digest
- WHEN the entry is validated
- THEN it passes with no refusal

#### Scenario: A hand-typed entry is refused offline

- GIVEN a well-formed `refs.bib` entry typed by hand, carrying no resolver or digest
  field
- WHEN the entry is validated with no network reachable
- THEN it refuses `ENTRY_UNSOURCED`

### Requirement: Reciprocal Citation/Entry Checks

The system MUST check both directions between `paper/main.tex` citation keys and
`refs.bib` entries: a `\cite{key}` with no matching entry MUST refuse
`CITE_WITHOUT_ENTRY`, and a `refs.bib` entry never cited by any `\cite` MUST refuse
`ENTRY_WITHOUT_CITE`. Each check MUST fire independently of the other.

#### Scenario: A cite with no entry is caught

- GIVEN `paper/main.tex` cites `key-x` and `refs.bib` has no entry `key-x`
- WHEN the reciprocal check runs
- THEN it refuses `CITE_WITHOUT_ENTRY` naming `key-x`

#### Scenario: An entry with no cite is caught

- GIVEN `refs.bib` has entry `key-y` and no `\cite{key-y}` exists in `paper/main.tex`
- WHEN the reciprocal check runs
- THEN it refuses `ENTRY_WITHOUT_CITE` naming `key-y`

#### Scenario: A fully reciprocal bibliography passes

- GIVEN every `\cite` has a matching entry and every entry is cited at least once
- WHEN the reciprocal check runs
- THEN it passes both directions with no refusal
