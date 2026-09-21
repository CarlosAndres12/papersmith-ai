# Delta for Source Section Binding

## MODIFIED Requirements

### Requirement: A Document-Rooted Source With No Marker Refuses

A root is **document-rooted** when it resolves to a directory under the
source base that contains at least one `*.md` file — a property computed on
disk, never keyed by a fact id. A document-rooted root that carries no
`<root>/.paper-writing.json` marker MUST refuse `SOURCE_REVISIONS_UNDECLARED`
naming the root. A document-rooted root MUST NOT degrade to the `unmeasured`
report for a missing marker: deleting a marker MUST NOT silently switch the
existence guard off. The refusal's detail MUST name the exact `mark
revisions` invocation that answers it and what is read under the root at the
moment of refusal — every `*.md` file currently there. Both raise sites of
this refusal (`paper_declarations._resolve_bind_document` and
`paper_graph.resolve_section_index`) MUST produce byte-identical detail text
for the same root and disk state, built from one shared detail builder so
the two sites cannot drift independently.

(Previously: the refusal named only the root, with no answering command and
no read of the root's current contents; the two raise sites carried
byte-identical text by coincidence of a copied string, not by a shared
builder.)

#### Scenario: A document-rooted root without a marker refuses

- GIVEN `proposals/` holding one or more `*.md` files and no
  `.paper-writing.json` marker
- WHEN a binding under `proposals` is resolved
- THEN it refuses `SOURCE_REVISIONS_UNDECLARED` naming `proposals`, the
  files currently under it, and the `mark revisions --root proposals ...`
  invocation that answers it

#### Scenario: Deleting the marker does not degrade to unmeasured

- GIVEN `proposals/` already document-rooted and marked, with a binding that
  resolves cleanly
- WHEN the marker file is deleted and the same binding is resolved again
- THEN it refuses `SOURCE_REVISIONS_UNDECLARED`, never a silent `unmeasured`
  report — an unmeasured report is reserved for a root that is not
  document-rooted at all

#### Scenario: Both raise sites produce byte-identical detail

- GIVEN the same undeclared root reached once through `bind` and once
  through `write`
- WHEN each raises `SOURCE_REVISIONS_UNDECLARED`
- THEN the two refusal details are byte-identical

#### Scenario: Mutation — inlining a literal message at one raise site is caught

- GIVEN one raise site's call to the shared detail builder replaced with an
  inline literal string
- WHEN the byte-identity test runs
- THEN it fails red

### Requirement: The Marker Grammar Is Validated, And Disjoint From `guidance/`'s

A `<root>/.paper-writing.json` marker MUST parse as UTF-8 JSON holding
exactly one top-level key, `revisions`, an object holding `revision_prefix`
(string) and `ordinal_digits` (integer), both required, and MAY additionally
hold `seal_sha256` (a 64-character lowercase hex string) at the top level. No
other key is admitted at either level. Content that is not valid UTF-8, not
valid JSON, not an object, missing either required `revisions` key, carrying
an unknown key at either level, carrying a wrong-typed value for any key, or
carrying a `seal_sha256` that is not a 64-hex string MUST refuse
`MALFORMED_SOURCE_MARKER` naming the offending file and the missing,
unknown, or wrong-typed key. When `seal_sha256` is present and shape-valid,
the reader MUST compare it against the digest computed over the marker's own
canonical bytes (excluding that key); a mismatch MUST refuse
`SOURCE_DECLARATION_HAND_EDITED`, naming the file, the recorded digest, and
the computed digest, with no `--adopt` escape. When `seal_sha256` is absent,
the marker is accepted exactly as before sealing existed. The source-root
marker reader MUST NOT accept `guidance/`'s own `class` key, and the
`guidance/` marker reader MUST NOT accept `revisions`: the two markers share
a filename but carry disjoint key sets, and each reader refuses loudly on
the other's shape rather than silently reusing it.

(Previously: the `revisions` object admitted exactly `revision_prefix` and
`ordinal_digits`, with no optional key and no seal verification.)

#### Scenario: A valid unsealed marker parses

- GIVEN `proposals/.paper-writing.json` holding `{"revisions":
  {"revision_prefix": "r", "ordinal_digits": 2}}`
- WHEN the marker is read
- THEN it parses with no refusal

#### Scenario: A valid sealed marker parses

- GIVEN the same marker with a `seal_sha256` key whose value matches the
  digest computed over the rest of its own bytes
- WHEN the marker is read
- THEN it parses with no refusal

#### Scenario: A non-JSON marker refuses

- GIVEN a `.paper-writing.json` file whose content is not valid JSON
- WHEN the marker is read
- THEN it refuses `MALFORMED_SOURCE_MARKER` naming the file

#### Scenario: A marker missing a required key refuses

- GIVEN a marker's `revisions` object carrying `revision_prefix` but no
  `ordinal_digits`
- WHEN the marker is read
- THEN it refuses `MALFORMED_SOURCE_MARKER` naming `ordinal_digits`

#### Scenario: A marker carrying an unknown key refuses

- GIVEN a marker's `revisions` object carrying a third key beside
  `revision_prefix` and `ordinal_digits`
- WHEN the marker is read
- THEN it refuses `MALFORMED_SOURCE_MARKER` naming the unknown key

#### Scenario: A marker with a wrong-typed value refuses

- GIVEN a marker declaring `ordinal_digits: "2"` (a string, not an integer)
- WHEN the marker is read
- THEN it refuses `MALFORMED_SOURCE_MARKER` naming `ordinal_digits`

#### Scenario: A malformed seal shape refuses as malformed, not as hand-edited

- GIVEN a marker whose `seal_sha256` value is not a 64-hex string
- WHEN the marker is read
- THEN it refuses `MALFORMED_SOURCE_MARKER` naming `seal_sha256`

#### Scenario: A mismatched seal refuses, with no adopt escape

- GIVEN a sealed marker whose recorded `seal_sha256` does not match the
  digest computed over its own current bytes
- WHEN the marker is read through `write`, a gating verb
- THEN it refuses `SOURCE_DECLARATION_HAND_EDITED`, naming the file, the
  recorded digest, and the computed digest — re-recording through `mark
  revisions` is the only exit

#### Scenario: The source-root reader refuses a `guidance/`-shaped marker

- GIVEN a `.paper-writing.json` under a source root carrying `{"class":
  "style-reference"}` — `guidance/`'s own shape — instead of `revisions`
- WHEN the source-root marker is read
- THEN it refuses `MALFORMED_SOURCE_MARKER` naming `revisions` as missing,
  rather than silently accepting `class`

#### Scenario: The marker's declared prefix and digits drive resolution, never a literal

- GIVEN a marker declaring `{"revisions": {"revision_prefix": "v",
  "ordinal_digits": 3}}` and a root holding `lineage-v007.md`
- WHEN lineage `lineage` is resolved
- THEN it resolves to `lineage-v007.md`, off the marker's own declared
  prefix and digit count — proving no revision-pattern literal governs
  resolution
