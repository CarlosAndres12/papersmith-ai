# Delta for Guidance Registry

## MODIFIED Requirements

### Requirement: Per-Folder Marker File

Each `guidance/<folder>/` MAY carry a marker file at
`guidance/<folder>/.paper-writing.json`, holding a JSON object with a
mandatory `class` key, drawn from the closed vocabulary `style-reference`,
`evidence`, and MAY additionally hold a `seal_sha256` key (a 64-character
lowercase hex string). A marker whose `class` value falls outside this
vocabulary MUST refuse `UNKNOWN_GUIDANCE_CLASS` (work-state), naming the
offending value and the folder. A marker that is not a JSON object, that
carries any key other than `class` and `seal_sha256`, or whose `seal_sha256`
is present but not a 64-hex string, MUST refuse `MALFORMED_GUIDANCE_MARKER`
(work-state). When `seal_sha256` is present and shape-valid, the reader MUST
compare it against the digest computed over the marker's own canonical bytes
(excluding that key); a mismatch MUST refuse
`GUIDANCE_DECLARATION_HAND_EDITED` (work-state), naming the folder, the
recorded digest, and the computed digest, with no `--adopt` escape. When
`seal_sha256` is absent, the marker is accepted exactly as before sealing
existed.

(Previously: the marker admitted exactly one key, `class`, with no optional
key and no seal verification.)

#### Scenario: A valid marker classifies its folder

- GIVEN `guidance/prior-papers/.paper-writing.json` holds `{"class":
  "evidence"}`
- WHEN the registry is read
- THEN `guidance/prior-papers` is reported class `evidence`

#### Scenario: A valid sealed marker classifies its folder

- GIVEN the same marker plus a `seal_sha256` matching the digest computed
  over its own remaining bytes
- WHEN the registry is read
- THEN `guidance/prior-papers` is reported class `evidence`, with no
  refusal

#### Scenario: An out-of-vocabulary class refuses

- GIVEN a marker holding `{"class": "reference-material"}`
- WHEN the registry is read
- THEN it refuses `UNKNOWN_GUIDANCE_CLASS` naming `reference-material` and
  the folder

#### Scenario: A malformed seal shape refuses as malformed, not as hand-edited

- GIVEN a marker whose `seal_sha256` value is not a 64-hex string
- WHEN the registry is read
- THEN it refuses `MALFORMED_GUIDANCE_MARKER` naming `seal_sha256`

#### Scenario: A mismatched seal refuses, with no adopt escape

- GIVEN a sealed marker whose recorded `seal_sha256` does not match the
  digest computed over its own current bytes
- WHEN the marker is read through a gating verb that classifies source
  material (e.g. `validate --source-md`), not through the position report
  alone
- THEN it refuses `GUIDANCE_DECLARATION_HAND_EDITED`, naming the folder, the
  recorded digest, and the computed digest — re-recording through `mark
  class` is the only exit

#### Scenario: Mutation — the seal check is reachable through a gating verb

- GIVEN the seal-comparison line inside `_classify` replaced with a constant
  `True`
- WHEN a test drives a hand-edited sealed marker through a gating verb, not
  through the position report alone
- THEN that test fails red

### Requirement: An Unmarked Folder Is Reported Unclassified, Never Guessed

A folder under `guidance/` carrying no `.paper-writing.json` MUST be
reported `unclassified`. The registry MUST NOT infer a class from the
folder's name, from any substring match against a known or prior folder
name, or from any other folder's marker. Nothing about a name may ever imply
`style-reference` or `evidence`. This absence rule is unaffected by sealing:
`unclassified` remains reachable only by absence of a marker, never as a
fallback for an unsealed one — an unsealed but otherwise valid marker still
classifies its folder normally.

#### Scenario: A fresh clone reports every folder unclassified

- GIVEN a `guidance/` tree with three folders and no `.paper-writing.json`
  files anywhere under it
- WHEN the registry is read
- THEN all three folders are reported `unclassified`, and the read refuses
  nothing

#### Scenario: A folder named like a classified one stays unclassified

- GIVEN `guidance/style-reference-notes/` carries no marker file
- WHEN the registry is read
- THEN it is reported `unclassified` — the string `style-reference` inside
  its own name classifies nothing

#### Scenario: An unsealed but valid marker still classifies, not unclassified

- GIVEN a marker holding `{"class": "evidence"}` with no `seal_sha256` key
- WHEN the registry is read
- THEN the folder is reported class `evidence`, never `unclassified`
