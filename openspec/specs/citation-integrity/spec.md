# Citation Integrity Specification

## Purpose

Two-way comparison of `\cite{...}` keys in `paper/main.tex` against
`refs.bib` entries. Both sides are derived from the document itself — the
only one of the seven checks with no declaration to read.

## Requirements

### Requirement: Classification

MUST classify as `mechanical`, both sides derived from the document, no
declaration anywhere.

#### Scenario: Classification is data, not prose

- GIVEN any completed run
- WHEN check A's entry is read
- THEN it carries `classification: mechanical`

### Requirement: Dangling Citation Is A Hard Failure

Every `\cite{key}` MUST have a matching `refs.bib` entry. A missing key
renders `[?]` in the compiled document and MUST report `fail`.

#### Scenario: M3a — dangling cite fails

- GIVEN `\cite{ghost}` with no `ghost` entry in `refs.bib`
- WHEN check A runs
- THEN it reports `fail` naming `ghost`

### Requirement: Orphan Bib Entry Is Reported, Not Failed

A `refs.bib` entry with no `\cite` referencing it renders nothing, so it
MUST be reported in the payload but MUST NOT flip the check's verdict to
`fail` (resolves proposal question 3: reported, not failed).

#### Scenario: M3b — orphan entry is listed, not failing

- GIVEN a `refs.bib` entry cited by nothing in `main.tex`
- WHEN check A runs
- THEN the orphan is named in the payload and the dangling-cite direction
  still reports `pass`

### Requirement: The Two Directions Are Independently Proven

A mutation firing the dangling-cite direction MUST NOT be read as proof of
the orphan-entry direction, or the reverse; both MUST be exercised by
separate, named mutations.

#### Scenario: Each direction is proven on its own

- GIVEN M3a (dangling cite) and M3b (orphan entry) run as two separate
  mutations against the fixture
- WHEN each runs alone
- THEN M3a flips only the dangling-cite result and M3b flips only the
  orphan listing; neither mutation moves the other's result
