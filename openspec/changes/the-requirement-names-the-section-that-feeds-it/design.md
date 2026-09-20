# Design: The Requirement Names the Section That Feeds It

## Technical Approach

A requirement entry gains one optional object, `document: {lineage, section}`, parsed by the same
`_normalize_requirement_entry` that already owns `{value, source:{file,quote}}`. Shape is checked in
`paper_contract.parse` under the existing `MALFORMED_HEADER`; **resolution** is checked once per
`assemble_corpus` in a new `_verify_source_section_bindings`, alongside the eleven `_verify_*`
passes already there.

Resolution is three hops, each derived from disk, none from a literal, and hop 2 branches on the
root's own **kind** (U2c ruling adds a third branch — `dataset` is sourced from the ingested
evidence document, never `proposals/`'s mathematics lineage):

    fact ──FACT_SOURCE_ROOT──▶ SourceRoot(name, kind)
         ──kind is REPOSITORY?──▶ unmeasured, always — impl_layout.WORKSPACE, never resolved further
         ──kind is PROSE?──▶ base/name ──▶ root dir
              ──marker──▶ revision regex ──max ordinal──▶ current revision file
         ──kind is INGESTED?──▶ guidance/'s own 'evidence'-classed folder (DERIVED — never a
              folder name literal; more than one such folder refuses EVIDENCE_ROOT_AMBIGUOUS)
              ──lineage IS the document, identity not max-ordinal──▶ <folder>/<lineage>/<lineage>.md
         ──segment_markdown──▶ heading titles ──▶ the bound section

The owner's ruling is the whole point of hop 2: for a `PROSE` root, a binding names the
**lineage**, never `r21`. Publish `r22` and every binding follows it for free; publish an `r22`
that renames the bound heading and `SECTION_NOT_IN_SOURCE` refuses by name. For an `INGESTED`
root, hop 2 has no revision to search at all — a published paper gets no `r22`, so the lineage
**is** the document, and resolution is presence, never an ordinal.

## Architecture Decisions

### A — The revision pattern is declared by a per-root marker file (Question 1, ruled)

| Option | Tradeoff | Decision |
|---|---|---|
| `<root>/.paper-writing.json` marker | The skill's own established precedent for "classify a directory from disk, never from its name"; the declaration sits beside the data it describes, so a gitignored root carries its own rule; absent/malformed are two distinct, already-modelled states | **Chosen** |
| `papersmith.yaml` | Its subject today is connector roles and contact for `paper_resolve.py` — a network-resolver config. A root's naming rule would have to be keyed by directory name in a file that no corpus-assembly path reads, and one missing key would darken every root at once | Rejected |
| The section contract's own header | Ten contracts would each re-declare the same rule, which is the drift this change exists to stop; and it makes the **consumer** declare a property of the **source** it cannot know | Rejected |

Marker name is `.paper-writing.json` — the skill has exactly one marker filename and a second
convention is a second thing to keep in sync. Its key set is disjoint from `guidance/`'s
(`revisions` vs `class`), and each reader refuses unknown keys, so a marker read by the wrong
reader refuses loudly instead of being half-understood.

```json
{ "revisions": { "revision_prefix": "r", "ordinal_digits": 2 } }
```

Both keys required, nothing else admitted. This mirrors `artifact-naming.ts` — which composes
`^${ESCAPED_STEM}-(?:${SEGMENT}-)?${REVISION_PREFIX}\d{2,}\.md$` from `DOMAIN.artifact`, warning in
its own source "never a literal `r`" — and goes one step further: the `{2,}` that TS still hardcodes
in core becomes `ordinal_digits` here. `SEGMENT` (`[a-z0-9]+(?:-[a-z0-9]+)*`), the `-` join and
`.md` stay **core conventions**, exactly as they are in TS, because they are properties of the
skill, not of this paper. The regex is composed per root as
`^{escape(lineage)}-{escape(prefix)}\d{{{digits},}}\.md$`.

That engine is TypeScript and this CLI may not call it (no `subprocess`, `NoSubprocessScanTests`).
It is mirrored in Python, never invoked.

### B — `implementation`/`results` are unmeasured by a derived property (Question 2, ruled)

The predicate is **document-rooted**: the root name resolves to a directory under the source base
that contains at least one `*.md` file. One property, computed on disk, no fact id anywhere.

| Root | On this checkout | Outcome |
|---|---|---|
| `proposals` | 21 `*.md` | document-rooted — obligation attaches, bindings fully checked |
| `experiments` | only `.gitkeep` | **unmeasured** — reported, no obligation, no refusal |
| `implementation` | not a directory under the base at all | **unmeasured** — same path, same report |

`source_available` is deliberately **not** reused for this: it answers "non-empty", and `.gitkeep`
makes `experiments/` non-empty while carrying nothing to bind to. "Has a prose document" is the
honest question, and it disposes of Question 2 and of the empty-`experiments` risk with the same
line of code. Drop a `.md` into `implementation/` and it becomes bindable with no code change —
correct behaviour, not a carve-out.

**Unmeasured is reported, never silent.** `Corpus` gains `source_roots: dict` naming every root in
`set(FACT_SOURCE_ROOT.values())` with `measured(<n> documents)` or `unmeasured(<reason>)`, echoed by
every corpus-reading verb **and by `write`** — so "the guard is off for this root" is always on
screen. A root that IS document-rooted but carries no marker refuses `SOURCE_REVISIONS_UNDECLARED`;
it never degrades to unmeasured, because deleting a marker must not switch the guard off.

### C — The source base is `sections_dir.parent`, injectable

`assemble_corpus(sections_dir, *, source_base: Path | None = None)`; `None` derives
`sections_dir.parent`. On the real repo that is `FORGE_ROOT`. In a tmp fixture it is the fixture's
own root, which holds no `proposals/`, so every minimal fixture reports unmeasured and stays green
with **zero edits** — the direct mitigation for the proposal's top risk. Defaulting to
`paper_scaffold.FORGE_ROOT` instead would judge every synthetic corpus against the live
`proposals/` and redden the suite at U3. Accepted limitation: a `--sections` pointed at a nested
directory reports its roots unmeasured rather than refusing; the report names the base it looked
under, so the condition is visible rather than inferred.

### D — Current revision: highest ordinal, exactly one

Candidates are the files under the root matching the composed regex. The winner is the **highest
parsed ordinal**. Gaps are irrelevant — `r01…r21` with `r09` deleted still resolves `r21`. A tie can
only arise from two spellings of one ordinal (`r21.md` and `r021.md`); `SOURCE_LINEAGE_UNRESOLVED`
then refuses naming both candidates. The code's subject is therefore "this lineage did not resolve
to **exactly one** revision", covering zero and more-than-one, rather than a seventh code.

### E — Memoization: one read per lineage, per assembly

`_verify_source_section_bindings` collects every distinct `(root, lineage)` the corpus names, then
resolves and segments each **once** into `{title: count}` — a count, so existence and ambiguity fall
out of one structure. Every binding is then a dict lookup. Today that is one file read for the whole
corpus, not one per binding. The memo is a local built per call, never a module-level cache: a
stale cache would be a decision living in the process instead of on disk.

### F — `dataset` is sourced from the ingested evidence document, never `proposals/` (U2c ruling)

`FACT_SOURCE_ROOT["dataset"]` shipped in U1/U2 as `SourceRoot("proposals", PROSE)` — wrong:
`proposals/research-concept-*.md` is mathematics only (kernel foundations, Rényi entropy, the MIL
formulation, local alignment, normalization) and carries no dataset section, and never will. The
owner ruled the real source is the ingested EVIDENCE document under `guidance/` instead.

An ingested paper is **not** a revisioned lineage — it has a stable id and is never superseded by an
`r22` — so U2's "resolve to the highest-ordinal revision" does not apply. A third `SourceRootKind`,
`INGESTED`, names this: for an `INGESTED` root, `document.lineage` names the paper's own id directly,
and resolution is **identity** (`guidance/<evidence-folder>/<lineage>/<lineage>.md` either exists or
it does not), never a marker-driven ordinal search.

**Which `guidance/` folder is the evidence root is DERIVED, never named.** `paper_guidance.
read_registry` (already the mechanism every other `guidance/` consumer uses) classifies each folder
from its own `.paper-writing.json`; whichever folder that registry classes `'evidence'` is the root.
`FACT_SOURCE_ROOT["dataset"].name` is `"evidence"` — a generic word already shared with `paper_
guidance.CLASSES`, never this paper's own folder name (`data-paper` appears nowhere under
`scripts/`). More than one folder classed `'evidence'` refuses `EVIDENCE_ROOT_AMBIGUOUS`, naming
every candidate — picking the first would be exactly the silent guess this change exists to rule
out. Zero folders classed `'evidence'` yet, or an evidence folder holding zero ingested papers, both
report `unmeasured` — the same reading `experiments/` holding only `.gitkeep` already gets: a paper
that has not ingested its evidence document yet is at an earlier stage, never a fault.

`SourceRoot.name` still carries no default and the shape is unchanged — `SourceRoot(name, kind)`,
two fields, `kind` mandatory. The binding entry shape (`document: {lineage, section}`) is also
unchanged: only which root a fact resolves through, and how that root resolves a lineage, differ
per kind.

### G — A binding names one title or a non-empty list of titles (U2d, owner ruling)

`document.section` accepts either a single title (the original shape) or a
non-empty list of unique titles. The owner's own reason, read off the
corpus: `sections/01-materials-and-methods.md`'s own prose states Slot 2 is
"One to three subsections, each a body of existing theory the proposal
needs" and Slot 3 is the proposal, "always last" — against `research-
concept-r21`'s five top-level sections that is two sections feeding one
block and three feeding another. A single-section binding cannot express
what the contract already promises, so the shape widens rather than forcing
every source document to be re-split to match the paper's own block count.

The deciding argument: the paper's own block count is fixed by its
contract, not by how many sections the CURRENT revision of a source
document happens to have. `research-concept-r21` has 5 sections; a later
`r22` may have 9. Splitting blocks to track that would make the paper's own
structure follow the source document's section count instead of the other
way around — exactly backwards from what a contract is for. A binding
names as many sections as feed it; the block count never moves because a
source document grew or shrank.

| Option | Tradeoff | Decision |
|---|---|---|
| Widen `section` to accept a string or a non-empty list of unique strings | One shape change, in the one place (`_validate_document_object`) that already owns `document`'s grammar; `paper_contract.requirement_documents` expands a list into one `(fact_id, lineage, title)` triple per title, so `paper_graph._verify_source_section_bindings`'s own per-triple loop needs ZERO changes — existence/ambiguity checks, and their "name the failing title" refusal detail, fall out for free | **Chosen** |
| A new `sections` (plural) key beside `section` | Two keys meaning almost the same thing is exactly the kind of drift `document`'s own shape exists to avoid; every caller would need to check which key is present | Rejected |
| Force every binding into a list (`section: [title]` even for one) | Breaks every already-shipped single-title binding's shape for no benefit; the owner explicitly ruled a single string must stay valid | Rejected |

No new refusal code: an empty list, a list with a repeated title, or a
non-string list entry are all schema-shape errors, so they reuse
`MALFORMED_HEADER` — the same code every other `document`-shape violation
already raises. Roster stays **139** — U2d adds no new code, only widens
an existing key's accepted shape.

## Refusal Codes — seven, and why the proposal's four became seven

| Code | Condition | Tier |
|---|---|---|
| `SECTION_NOT_IN_SOURCE` | Named title is no heading in the current revision | work-state |
| `SECTION_TITLE_AMBIGUOUS` | Title matches two or more headings | work-state |
| `SECTION_BINDING_ABSENT` | Bindable fact, document-rooted, no `document` half (U3) | work-state |
| `SOURCE_LINEAGE_UNRESOLVED` | Lineage resolves to zero or more than one revision/document | work-state |
| `SOURCE_REVISIONS_UNDECLARED` | Document-rooted `PROSE` root carries no marker | work-state |
| `MALFORMED_SOURCE_MARKER` | Marker not UTF-8 / not JSON / not an object / unknown or missing key / bad value | work-state |
| `EVIDENCE_ROOT_AMBIGUOUS` | More than one `guidance/` folder is classed `'evidence'` (U2c) | work-state |

The middle five are an **amendment** the proposal did not forecast: the ruling "the pattern is read
from an on-disk declaration" arrives with a declaration, and a declaration has an absent state and a
malformed state. Folding either into `SOURCE_LINEAGE_UNRESOLVED` would conflate "nobody said how
revisions are named" with "no revision is there". `MALFORMED_SOURCE_MARKER` is qualifier-led, which
the measured roster admits for exactly this family — the three existing `MALFORMED_*` codes are all
shape checks, and so is this. Entry-shape errors reuse `MALFORMED_HEADER`; no new code for them.
`EVIDENCE_ROOT_AMBIGUOUS` is U2c's own amendment (Decision F): `SOURCE_LINEAGE_UNRESOLVED` names a
lineage's own candidates under an ALREADY-IDENTIFIED root, never which root to use in the first
place — the two conditions are disjoint, so folding root selection into lineage resolution would
conflate "which document" with "which root holds documents at all".

Roster is **133 today** (the pre-change baseline, before U1 started); the count after each unit
lands is re-derived with `reachable_paper_refusal_codes()`, never forecast — measured **139** after
U2c, unchanged at **139** after U2d (a shape widening, no new raise site), and **140** after U3
(`SECTION_BINDING_ABSENT`'s own raise site, unconditional from the moment it lands).

## File Changes

| File | Action | Description |
|---|---|---|
| `scripts/paper_contract.py` | Modify | `_REQUIREMENT_OPTIONAL = ("document",)`, `_DOCUMENT_REQUIRED = ("lineage","section")`, `requirement_documents()` accessor |
| `scripts/paper_declarations.py` | Modify | `source_root_status()`, `read_revisions_marker()`, `resolve_lineage()`, `bindable_facts()` derived off `FACT_SOURCE_ROOT`; U2c adds `SourceRootKind.INGESTED`, `_ingested_root_status()`, `resolve_ingested_document()`, and imports `paper_guidance` |
| `scripts/paper_graph.py` | Modify | `BlockRecord.source_bindings: tuple = ()`; `Corpus.source_roots: dict`; `_verify_source_section_bindings`; `source_base` kwarg; U2c adds the per-kind dispatch inside `_verify_source_section_bindings` |
| `scripts/paper_guidance.py` | Read | `read_markdown_outline`/`segment_markdown` reused unchanged; U2c additionally reuses `read_registry`/`ingested_papers`, unchanged |
| `scripts/paper_cli.py` | Modify | Seven codes into `REFUSAL_CLASSIFICATION` (U2c adds `EVIDENCE_ROOT_AMBIGUOUS`); `source_roots` in `plan`/`phases`/`contract`; `_resolve_write_gate` returns the corpus so `cmd_write` reports it |
| `proposals/.paper-writing.json` | Create | `{"revisions":{"revision_prefix":"r","ordinal_digits":2}}` |
| `sections/01-*.md`, `02-*.md`, `04-*.md`, `06-*.md`, `08-*.md` | Modify | Bindings transcribed for every bindable requirement whose root is measured (`formulation`, `dataset`); prose bytes untouched below the header |
| `tests/test_paper_contract.py`, `test_paper_writing.py`, `test_paper_decisions.py` | Modify | Shape, resolution, mutation proofs, synthetic `experiments/` fixture, `SECTION_BINDING_ABSENT` write-gate tests |

## Interfaces

```python
# paper_declarations.py
class SourceRootKind(enum.Enum):
    """PROSE -- read as revisions with headings. REPOSITORY -- measured by
    running it; never bindable to a section, whatever is on disk. INGESTED
    -- a published paper under guidance/, identified by that folder's own
    'evidence' classification; identity-resolved, never a revisioned
    lineage (U2c)."""
    PROSE = "prose"
    REPOSITORY = "repository"
    INGESTED = "ingested"


class SourceRoot(NamedTuple):
    """`kind` carries NO default: adding a sixth root cannot silently
    inherit a species. Omitting it is a TypeError at construction."""
    name: str
    kind: SourceRootKind


def source_root_status(base: Path, root: SourceRoot) -> dict:
    """{"state": "document-rooted"|"unmeasured", "path": Path|None,
        "documents": int, "reason": str|None}

    A REPOSITORY-kind root is `unmeasured` BY KIND, before disk is
    consulted at all, and its path is the forge's own canonical
    `impl_layout.WORKSPACE` -- never a name this skill spells itself.
    Amended after U2b: the first cut resolved every root name as a
    directory under `base`, which excluded `implementation`/`results`
    for the accidental reason that no directory bore that name.

    An INGESTED-kind root delegates to `_ingested_root_status(base)`:
    which `guidance/` folder feeds it is DERIVED from `paper_guidance.
    read_registry`'s own classification (reused, never a second reader),
    never from `root.name`. More than one folder classed 'evidence'
    refuses EVIDENCE_ROOT_AMBIGUOUS, naming every candidate. Zero such
    folders, or one holding zero ingested papers, both report
    `unmeasured` -- an earlier stage, never a fault (U2c)."""

def resolve_lineage(root: Path, lineage: str, marker: dict) -> Path:
    """The single highest-ordinal revision. Refuses SOURCE_LINEAGE_UNRESOLVED
    on zero candidates and on a tie, naming what it saw."""

def resolve_ingested_document(evidence_dir: Path, lineage: str) -> Path:
    """The INGESTED-kind counterpart: `document.lineage` names the paper's
    own stable id directly, resolution is PRESENCE of
    `evidence_dir/<lineage>/<lineage>.md` -- identity, never an ordinal
    search. Refuses the SAME SOURCE_LINEAGE_UNRESOLVED on zero or more
    than one matching ingested document (U2c)."""
```

`BlockRecord.source_bindings` is a tuple of `(fact_id, lineage, section_title)` triples — a tuple,
matching the `produces_facts: tuple = ()` precedent for a frozen dataclass, defaulted so every
existing construction site stays green. A `document.section` naming more than one title (U2d)
contributes one triple PER title, expanded by `paper_contract.requirement_documents` — never a
fourth tuple element and never a nested list inside one triple — so every consumer of
`source_bindings` (`_verify_source_section_bindings`'s per-triple loop, `SECTION_BINDING_ABSENT`'s
own presence check keyed by `fact_id`) stays unchanged by the widening.

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | Entry shape, marker grammar | Direct `Refused` assertions on synthetic headers and markers |
| Unit | Lineage resolution: max ordinal, gap, tie, foreign lineage, cross-root | Tmp root with fabricated revision files |
| Unit | Document-rooted predicate | Root with only `.gitkeep`, root absent, root with `*.md` |
| Integration | Version bump is free | Fixture adds `…-r22.md` preserving bound titles; assert the corpus assembles **byte-identically untouched** (success criterion 4) |
| Integration | `write` | Existence refusal fires from `cmd_write`, not only from a read-only verb |
| Mutation | All seven codes | `tests/paper_mutation.py::_run_against_mutant`, table below |
| Generality | No paper literal, no revision literal | `rg` over `.claude/skills/` for block ids, section titles, document filenames, and a bare revision prefix; `NoSubprocessScanTests` unchanged |
| Roster | Bidirectional | `reachable_paper_refusal_codes()`; `npm test` **and** `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` |

**Mutation per code** — each is a mutation a weaker lock survives, and each asserts its anchor count
so an untracked fixture cannot pass on a no-op edit:

| Code | Mutation that proves it reachable |
|---|---|
| `SECTION_NOT_IN_SOURCE` | Rename the bound heading in the fixture revision; the named `write` test must go red |
| `SECTION_TITLE_AMBIGUOUS` | Duplicate the bound heading; the count-based lookup must refuse, not pick the first |
| `SECTION_BINDING_ABSENT` | Delete the `document` half from one shipped entry |
| `SOURCE_LINEAGE_UNRESOLVED` | Rename the newest revision to a foreign lineage (zero case); add `r021.md` (tie case) |
| `SOURCE_REVISIONS_UNDECLARED` | Delete `proposals/.paper-writing.json` in the fixture root |
| `MALFORMED_SOURCE_MARKER` | Add a sixth key to the marker; flip `ordinal_digits` to a string |
| `EVIDENCE_ROOT_AMBIGUOUS` | Classify two `guidance/` folders `'evidence'`; skip the count guard and the first (alphabetical) match silently wins (U2c) |
| Derivation, not a list | Add a **sixth** root to `FACT_SOURCE_ROOT` in a fixture and assert it becomes bindable with no engine edit (success criterion 6) |

## Work Units

| Unit | Content | Est. lines | Green alone |
|---|---|---|---|
| U1 | Entry shape + `document` validator, `requirement_documents`, `BlockRecord.source_bindings`, bindable derivation — both shapes accepted, nothing demanded | ~130 | yes |
| U2 | Marker reader, lineage→revision resolver, `source_root_status`, `_verify_source_section_bindings`, `source_roots` report, existence/ambiguity refusals | ~170 | yes (inert without U3) |
| U2b | Correctness repair: `implementation`/`results` unmeasured BY KIND (`SourceRootKind.REPOSITORY`), not by an invented directory name | ~295 | yes |
| U2c | Owner ruling: `dataset` sourced from the ingested evidence document (`SourceRootKind.INGESTED`), never `proposals/`'s mathematics lineage | 572+/-52 measured (incl. this doc) | yes |
| U2d | Owner ruling: `document.section` accepts one title or a non-empty list of unique titles (Decision G); `requirement_documents` expands a list into one triple per title | ~90 | yes |
| **DP** | **Owner rules on any entry that cannot be anchored** | **blocking** | — |
| U3 | Transcribe corpus bindings, obligation unconditional (`SECTION_BINDING_ABSENT`), refusal wired at `write`, ship `proposals/.paper-writing.json`, fixtures, roster re-derived | ~170 | yes |

Estimated total **~470 changed lines** against the 400-line budget — above the proposal's ~440
because the marker reader and its two codes were added by the Question-1 ruling.
`400-line budget risk: Medium`. **Two chained PRs recommended**: PR#1 `U1+U2` ≈ 300, PR#2 `U3` ≈ 170
targeting PR#1's branch. U1 and U2 are inert without U3, so PR#1 ships green on the untouched corpus.

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or
process-integration boundary. Stdlib-only, keyless, offline, fail-closed, `Refused(code, detail)`
and exit 2, no `--force`. No `subprocess` import joins `scripts/`; `paper_latex.py`'s reserved
exception is untouched. The TypeScript resolver is mirrored, never called.

## Migration / Rollout

No on-disk state, region format, digest or generation counter changes; an existing `paper/main.tex`
stays readable by the prior revision. U3 is one commit — `git revert` restores the pre-obligation
corpus and fixtures together. The only new on-disk artifact is `proposals/.paper-writing.json`,
which an older revision of the code ignores entirely.

## Open Questions

None. Both questions the proposal held open are ruled above: Decision A (per-root marker) and
Decision B (document-rooted predicate). The in-place digest stays deferred with the owner's reason,
additive as a third field on the binding this change ships if in-place rewrites turn out to recur.
