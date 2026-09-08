# Deliberation Structural Entries Specification

## Purpose

Structural documents contain more than headings, paragraphs, and math. A
Markdown table or a figure placeholder must be resolvable as its own locus,
not absorbed into the paragraph or section that contains it.

## Requirements

### Requirement: `table` and `figure_placeholder` are first-class leaf entries

`EntryType` MUST include `table` and `figure_placeholder`. `buildStructuralIndex`
MUST recognize GFM tables and declared figure placeholders as entries of these
types, and `target-resolver.ts`'s leaf list MUST include both. This change is
additive: no existing entry type, span, or resolution changes.

#### Scenario: A GFM table resolves as its own locus

- GIVEN a managed document containing a GFM table nested inside a section
- WHEN `RESOLVE_TARGET` is asked to resolve a query naming that table
- THEN it resolves to a `table` entry whose byte span is exactly the table
- AND NOT to the enclosing `paragraph` or `section` entry

#### Scenario: A figure placeholder resolves as its own locus

- GIVEN a document containing a declared figure placeholder block
- WHEN `RESOLVE_TARGET` is asked to resolve a query naming it
- THEN it resolves to a `figure_placeholder` entry, not to a `paragraph`

#### Scenario: Documents without tables are unaffected

- GIVEN a document with headings, paragraphs, and math entries but no tables
  or figure placeholders
- WHEN the structural index is rebuilt after this change
- THEN it is byte-identical to the pre-change structural index

#### Scenario: Ambiguity between a table and its enclosing section still refuses correctly

- GIVEN a document with two tables under one heading and an under-specified
  query
- WHEN `RESOLVE_TARGET` is asked to resolve the ambiguous query
- THEN it refuses with the existing ambiguity-gate behavior, now able to list
  both `table` candidates by their own identity instead of one collapsed
  `paragraph`

## Acceptance Criteria

- Existing math-domain structural index snapshots are unchanged (additive
  guarantee proven by regression, not by inspection).
- A fixture document with at least one real GFM table and one real figure
  placeholder demonstrates the new resolution; a fixture with none demonstrates
  the additive no-op.
