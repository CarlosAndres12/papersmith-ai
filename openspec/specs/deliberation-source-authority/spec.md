# Deliberation Source Authority Specification

## Purpose

Some domain layers treat a loaded source as a hard ceiling on claims (a data
paper an experiment must not contradict). This capability lets a profile name
such ceiling sources and have contradicting evidence flagged. It MUST be
off by default so `proposal-deliberation`, which declares none, is unaffected.

## Requirements

### Requirement: `sourceAuthority` is off by default

A profile declaring no `sourceAuthority` MUST never raise
`SOURCE_AUTHORITY_CONFLICT`, regardless of candidate content.

#### Scenario: No sourceAuthority declared, never raised

- GIVEN `proposal-deliberation`'s profile declares no `sourceAuthority`
- WHEN any candidate is validated
- THEN `SOURCE_AUTHORITY_CONFLICT` is never raised

### Requirement: A declared ceiling source's contradiction is detected

`profile.sourceAuthority` MUST name which loaded sources act as ceilings. A
candidate whose evidence contradicts a declared ceiling source MUST be
detected and surfaced via `SOURCE_AUTHORITY_CONFLICT`.

**STATUS: whether this refusal blocks publish outright or is a preview-time
advisory the caller may acknowledge is an OPEN product question**, pending
decision. This requirement specifies that the mechanism (detection + explicit
code) MUST exist; it does not fix the severity.

#### Scenario: Contradicting evidence is detected

- GIVEN a profile declares `sourceAuthority` naming a loaded ceiling source
- AND a candidate's evidence contradicts a claim in that source
- WHEN the candidate is validated
- THEN `SOURCE_AUTHORITY_CONFLICT` is raised, identifying the contradicting
  claim and the ceiling source

#### Scenario: Non-contradicting evidence passes

- GIVEN the same declared ceiling source
- AND a candidate whose evidence is consistent with it
- WHEN validated
- THEN `SOURCE_AUTHORITY_CONFLICT` is not raised

### Requirement: The domain-vocabulary literal is removed from intent resolution

`intent-resolver.ts` MUST NOT contain the `'sparse'`/`'dispers'` string
literal as an unconditional core term. If a domain still needs the
equivalent inference, it MUST be declared opt-in via `profile.vocabulary`,
never hardcoded.

#### Scenario: Literal absent from core

- GIVEN `intent-resolver.ts`
- WHEN scanned for the string literals `'sparse'` and `'dispers'`
- THEN neither is present as a core-level unconditional term

#### Scenario: Mathematical profile keeps equivalent behavior if it opts in

- GIVEN `proposal-deliberation`'s profile optionally declares a
  `vocabulary` entry equivalent to today's `requestedEffect` fallback
- WHEN intent resolution runs on matching math content
- THEN the resulting `requestedEffect` is identical to pre-change behavior

#### Scenario: Dropping the literal entirely is also acceptable

- GIVEN no profile declares the equivalent `vocabulary` entry
- WHEN intent resolution runs
- THEN `requestedEffect` is simply absent, which is acceptable because nothing
  downstream reads it except the conceptual plan's `scientificGoal` fallback

## Acceptance Criteria

- A fixture proves `SOURCE_AUTHORITY_CONFLICT` can fire when a profile opts in
  (no-vacuous-pass requirement).
- A fixture proves it never fires for `proposal-deliberation`'s profile.
- The severity decision (hard refusal vs. preview advisory) is recorded as
  pending in `design.md` before slice 4 implementation begins.
