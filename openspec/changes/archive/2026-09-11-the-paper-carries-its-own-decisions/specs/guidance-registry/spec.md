# Guidance Registry Specification

## Purpose

Classifies each folder under `guidance/` as `style-reference` or `evidence`
by reading a per-folder marker, never by reading the folder's name. A folder
carrying no marker MUST be reported `unclassified` — including every folder
on a fresh clone, where no marker files exist yet. This is designed
behavior, not a default and not a fault.

## Requirements

### Requirement: Per-Folder Marker File

Each `guidance/<folder>/` MAY carry a marker file at
`guidance/<folder>/.paper-writing.json`, holding a JSON object with exactly
one mandatory key, `class`, drawn from the closed vocabulary
`style-reference`, `evidence`. A marker whose `class` value falls outside
this vocabulary MUST refuse `UNKNOWN_GUIDANCE_CLASS` (work-state), naming
the offending value and the folder. A marker that is not a JSON object, or
carries any key other than `class`, MUST refuse `MALFORMED_GUIDANCE_MARKER`
(work-state).

#### Scenario: A valid marker classifies its folder

- GIVEN `guidance/prior-papers/.paper-writing.json` holds `{"class":
  "evidence"}`
- WHEN the registry is read
- THEN `guidance/prior-papers` is reported class `evidence`

#### Scenario: An out-of-vocabulary class refuses

- GIVEN a marker holding `{"class": "reference-material"}`
- WHEN the registry is read
- THEN it refuses `UNKNOWN_GUIDANCE_CLASS` naming `reference-material` and
  the folder

### Requirement: An Unmarked Folder Is Reported Unclassified, Never Guessed

A folder under `guidance/` carrying no `.paper-writing.json` MUST be
reported `unclassified`. The registry MUST NOT infer a class from the
folder's name, from any substring match against a known or prior folder
name, or from any other folder's marker. Nothing about a name may ever
imply `style-reference` or `evidence`.

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

### Requirement: The Registry Reads No Hardcoded Folder Path

The registry MUST enumerate `guidance/*` from disk and read each folder's
own marker; it MUST NOT reference any specific folder name as a constant
anywhere in its own source. `_core/deliberation/engine/proposal-workspace.ts`
hardcoding `GUIDE_DIRECTORY = "guidance/paper-guide"` is the anti-pattern
this requirement exists to keep out of this registry — named as precedent,
not repaired here.

#### Scenario: Two arbitrarily named folders both classify correctly

- GIVEN two folders under `guidance/`, named neither `paper-guide` nor
  matching any name used elsewhere in this skill or its tests, each
  carrying a valid marker with a different declared class
- WHEN the registry is read
- THEN each reports exactly the class its own marker declares, proving no
  name drove the result

## Acceptance Criteria

- A marker's `class` is validated against the closed two-value vocabulary;
  an out-of-vocabulary value refuses and never silently degrades to
  `unclassified`.
- Absence of a marker is the only path to `unclassified`; a malformed
  marker refuses instead of falling through to `unclassified`.
- Mutation proof: defaulting an unclassified folder to `style-reference`
  (rather than reporting `unclassified`) MUST make the fresh-clone scenario
  above fail red.
- No test or source scan may pass while any folder-name literal decides a
  class; the two-arbitrary-folders scenario is the executed proof.
