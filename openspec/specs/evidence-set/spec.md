# Evidence Set Specification

## Purpose

The claim↔source record whose load-bearing element is a verbatim quoted span of an
ingested source — the thing that turns a citation verdict from an opinion into a
measurement anyone can re-check. Evidence ingestion routes through `paper-ingestion`
unchanged; no parallel pipeline exists.

## Requirements

### Requirement: Evidence PDFs Route Through Existing Ingestion

Evidence PDFs MUST land under `guidance/<section-id>/`, where `<section-id>` is a
folder name from the contract's section vocabulary. This folder MUST be discovered
by `paper-ingestion`'s existing `source_base: guidance` / `discover_source_roots`
promotion rule (a child folder holding a loose PDF becomes a source root). No new
ingestion pipeline, script, or discovery rule MUST be built.

#### Scenario: A dropped evidence PDF is discovered by existing ingestion

- GIVEN a PDF placed loose in `guidance/05-related-work/`
- WHEN `paper-ingestion`'s discovery runs
- THEN `guidance/05-related-work/` is reported as a pending source root, using the
  unmodified `discover_source_roots` rule

### Requirement: Evidence Folders Carry a Producer-Written Manifest

Every folder under `guidance/<section-id>/` that this capability uses as an evidence
source MUST carry an evidence manifest file, written by this capability, recording at
minimum which papers the folder holds and that the folder is evidence-typed. A style
guidance folder (owned by a different capability) MUST NOT carry this manifest. The
folder name alone (a section id) MUST NOT be treated as sufficient proof of evidence
typing — the manifest is the second, independent discriminator. Consuming this
discriminator into a shared registry belongs to a later change; this requirement
covers only that the manifest exists and is accurate when this capability writes it.

#### Scenario: Evidence folder is manifest-marked

- GIVEN this capability uses `guidance/06-introduction/` as an evidence folder
- WHEN the folder is inspected
- THEN it carries an evidence manifest naming its papers

#### Scenario: A style folder carries no evidence manifest

- GIVEN a `guidance/<section-id>/` folder holding only style material, untouched by
  this capability
- WHEN the folder is inspected
- THEN it carries no evidence manifest

### Requirement: The Claim↔Source Record Shape

Each claim↔source record MUST carry: the claim text, the citation key, the resolved
DOI (or connector-native id) with its resolver name and a metadata digest, and a
verbatim quoted span of the ingested `.md` with a locator (file path and an offset or
anchor identifying where the span sits in that file). This shape MUST be identical
across all three work units of this change.

#### Scenario: A complete record is written

- GIVEN a citation resolved against an ingested source
- WHEN its evidence record is written
- THEN it carries claim text, citation key, resolver, digest, and a verbatim span
  with locator, all non-empty

### Requirement: A Spanless Record Is Insufficient By Construction

The record schema MUST make the verbatim span field mandatory for a record to be
eligible for a `holds` or `does-not-hold` verdict. A record whose span field is
empty or absent MUST be classified `insufficient` before any semantic comparison
against the claim runs — this is a structural property of the record type, not a
judgment call made later by the validator.

#### Scenario: Missing span forces insufficient

- GIVEN a claim↔source record with no verbatim span recorded
- WHEN the record is submitted for a verdict
- THEN the verdict is `insufficient`, returned without evaluating the claim's
  semantic content against anything

### Requirement: The Inherited Operator Stop Is Honored

`paper-ingestion` asks the operator before moving any PDF. This capability MUST NOT
engineer around that stop. When pending evidence PDFs exist, the evidence loop MUST
report them and wait; it MUST NOT ingest unattended.

#### Scenario: Pending PDFs block unattended ingestion

- GIVEN loose PDFs sit in a `guidance/<section-id>/` evidence folder awaiting
  ingestion
- WHEN the evidence loop runs with no operator present
- THEN it reports the pending PDFs and performs no move or conversion
