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

**Risk discharged (U3c):** exploration.md's own caveat — "`experiments/` is empty except
`.gitkeep` in this checkout, so generality over that root can only be exercised against a
synthetic fixture" — named a real gap: every full-path test (marker read, lineage resolution,
section existence/ambiguity, the `undecided`/`write` tier boundary) ran only against `proposals`,
the one `PROSE`-kind root this checkout happens to populate. `SecondProseRootGeneralityTests` and
`SecondProseRootWriteGateTests` (`tests/test_paper_writing.py`) now drive the identical full path
against `experiments` — the second `PROSE`-kind root `FACT_SOURCE_ROOT` already declares — using an
invented lineage (`field-log`) and invented section titles, at a marker width (3 digits) that is
deliberately not the live root's own (2). Six mutation runs (marker width, max-ordinal selection,
multi-title masking, the undeclared-marker guard, and the `write`-gate absence check) confirm each
behaviour is reachable on this second root, not merely on the one it was developed against. No
engine edit was needed to make any of this pass — the caveat was a coverage gap, not a defect.

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

### H — `SECTION_BINDING_ABSENT` refuses at `write`, never at assembly (U3b correctness repair)

U3 shipped the obligation as unconditional the instant any verb assembled the corpus — including
every read-only verb (`contract`, `phases`, `plan`). That left exactly two options the moment one
real binding turned out to be genuinely undecided: invent a binding to keep the corpus assemblable,
or leave the whole corpus refusing to assemble at all. Both happened during U3's own apply: two
bindings (`introduction.block-4a`, `abstract.slot-3`) were transcribed on a guess the apply agent
itself flagged low-confidence, specifically because leaving them unbound made `assemble_corpus`
refuse outright. A repair that forces an agent to invent content about the paper being written is a
worse defect than the unconditional-obligation gap it closed.

| Option | Tradeoff | Decision |
|---|---|---|
| Report an undecided binding at read-time (`Corpus.undecided_bindings`, mirroring `source_roots`'s own `unmeasured` report), refuse only when `write` assembles its own corpus (`enforce_bindings=True`) | Every read-only verb keeps working on a corpus that honestly carries an undecided binding; `write` is the one moment drafting a block without knowing its own section would produce a false claim, so it is the only moment that must refuse; no invented binding is ever required just to keep the corpus assemblable | **Chosen** |
| Keep the refusal unconditional at every assembly (U3's shipped behaviour) | Forces an invented binding (or a permanently unassemblable corpus) the moment any entry is genuinely undecided — exactly the defect this repair exists to close | Rejected |
| Drop the obligation entirely, report `undecided` everywhere including `write` | `write` could then draft a block against a fact nobody has told it which section answers, silently producing prose with no traceable source — the whole point of `source-section-binding` | Rejected |

`Corpus.undecided_bindings` is computed once, before `Corpus` itself is constructed (a frozen
dataclass has nowhere to gain a field after the fact) — keyed by qualified block id, then fact id, to
`{"state": "undecided", "root": <root name>}`. `assemble_corpus` gains one keyword-only parameter,
`enforce_bindings: bool = False`; `_verify_source_section_bindings` takes the same flag and raises
`SECTION_BINDING_ABSENT` (naming the SAME block and fact the old unconditional loop would have
named first) only when it is `True`. `paper_cli._resolve_write_gate` — `write`'s own first statement,
already the SAME corpus assembly every other `source-section-binding` code reaches `write` through —
is the ONLY call site in the skill that passes `enforce_bindings=True`. Every other call site
(`cmd_contract`, `compute_phases`, `cmd_plan`, `_resolve_write_gate`'s own read-only siblings) keeps
the default, so a genuinely undecided binding never blocks reading the contract or seeing which wave
is open — it blocks exactly the one act (drafting prose for that block) an undecided binding cannot
honestly support. The raise site itself is unconditional in source (still reachable, still counted by
`reachable_paper_refusal_codes()`); only WHEN it fires changed.

`introduction.block-4a` and `abstract.slot-3`'s invented `document` halves are removed by this
repair: both report `undecided` at read-time and refuse `SECTION_BINDING_ABSENT` at `write`, which is
the truth — nobody has ruled which section of the proposal's own lineage feeds either block, and the
owner rules that, not an apply agent's guess.

### I — No binding is transcribed ahead of `write` asking for it (U3d ruling)

U3's own apply, faced with the unconditional-obligation trap Decision H repairs, transcribed nine
`document` bindings into the shipped section contracts (`sections/01-*.md`, `02-*.md`, `04-*.md`,
`06-*.md`, `08-*.md`) — three of the nine (`mm-borrowed-machinery`, `mm-proposal`,
`lim-proposal-items`) were settled in a conversation about a table, to unblock a repair. The owner
ruled that none of the nine survive, not even those three: a binding decided in conversation is not a
binding decided by using the skill, and the only moment that decision belongs to is `write` asking
for it — the exact machinery U3b's `enforce_bindings`/`undecided_bindings` split already built.

| Option | Tradeoff | Decision |
|---|---|---|
| Remove all nine `document` bindings from `sections/*.md`; the corpus reports every one `undecided` until an operator runs `write` and the skill asks | The shipped contracts return to byte-identical with `main`; `write` still refuses `SECTION_BINDING_ABSENT` for every bindable, measured entry, exactly as Decision H already specifies — nothing about the refusal tier changes, only that NO entry currently satisfies it | **Chosen** |
| Keep the three the owner had already ruled on in conversation, remove only the other six | Preserves the exact defect being closed: a decision taken in conversation, to unblock a repair, is not the same act as the skill asking at `write` and an operator answering it in that moment | Rejected |
| Relocate the nine bindings into a fixture or a new file instead of deleting them | The owner's ruling is that the binding does not exist yet, not that it exists somewhere else; a relocated binding is still a pre-empted `write`-time decision wearing a different path | Rejected |

The corpus's `sections/*.md` now carry zero `document` bindings — `rg` for the proposal's own lineage
and paper id, and for its section titles, returns nothing under `sections/`. `assemble_corpus()`
reports all nine as `undecided` (Decision H's own report shape), and `write` refuses
`SECTION_BINDING_ABSENT` for each until an operator supplies the binding at that moment. No spec or
task artifact in this change claims the corpus carries a transcribed binding; where earlier units'
own tasks described the corpus as holding them, this ruling supersedes that description.

**The suite's own fixture names, and the guard that missed them.** `tests/test_paper_writing.py`,
`test_paper_contract.py` and `test_paper_decisions.py` had used the proposal's own real lineage
name and the ingested paper's own real id as fixture DATA — a document lineage is not a secret, but a
fixture proves a shape and must never borrow a real paper's spelling to do it. Both are now invented
names with no product meaning. `tests.test_proposal_implementation.ForgeVocabularyDerivedGuardTests`
(`derived_denylist`) is the guard meant to catch exactly this, and it did not: it derived its
denylist from `implementations/` alone, so a name living in `proposals/`, `experiments/` or
`guidance/` was invisible to it. `paper_product_root_words` widens the SAME rule to those roots too —
derived from `paper_declarations.FACT_SOURCE_ROOT` and `paper_guidance.read_registry`, never a
hand-listed root or folder name — contributing only the UNDIVIDED compound of a live lineage or
evidence-folder/paper id, never its split parts: splitting was tried first and measured to add
ordinary English nouns (`data`, `paper`, `concept`, `research`) that this forge legitimately uses
everywhere, reporting roughly seventy shipped files as leaking, none of them an actual mention of
either real name. Widening the guard surfaced two further mentions the same way — `paper-writing`'s
own `SKILL.md` used the real evidence-folder name as a "for example" in an illustrative list, and
`test_forge_scaffolding.py` named it in a historical-incident docstring — both repaired the same way,
without touching `experimental-deliberation`'s own `guidance/data-paper` requirement (see Open
Questions: two collisions this ruling does not resolve).

## Refusal Codes — seven, and why the proposal's four became seven

| Code | Condition | Tier |
|---|---|---|
| `SECTION_NOT_IN_SOURCE` | Named title is no heading in the current revision | work-state |
| `SECTION_TITLE_AMBIGUOUS` | Title matches two or more headings | work-state |
| `SECTION_BINDING_ABSENT` | Bindable fact, document-rooted, no `document` half — raised only when `write` assembles its own corpus (U3, refusal tier corrected at `write`-only by U3b, Decision H) | work-state |
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
U2c, unchanged at **139** after U2d (a shape widening, no new raise site), **140** after U3
(`SECTION_BINDING_ABSENT`'s own raise site lands), and unchanged at **140** after U3b (the raise site
is a static AST scan target regardless of the `enforce_bindings` gate around it — this repair changes
WHEN the code fires, never WHETHER it is reachable in source).

## File Changes

| File | Action | Description |
|---|---|---|
| `scripts/paper_contract.py` | Modify | `_REQUIREMENT_OPTIONAL = ("document",)`, `_DOCUMENT_REQUIRED = ("lineage","section")`, `requirement_documents()` accessor |
| `scripts/paper_declarations.py` | Modify | `source_root_status()`, `read_revisions_marker()`, `resolve_lineage()`, `bindable_facts()` derived off `FACT_SOURCE_ROOT`; U2c adds `SourceRootKind.INGESTED`, `_ingested_root_status()`, `resolve_ingested_document()`, and imports `paper_guidance` |
| `scripts/paper_graph.py` | Modify | `BlockRecord.source_bindings: tuple = ()`; `Corpus.source_roots: dict`; `_verify_source_section_bindings`; `source_base` kwarg; U2c adds the per-kind dispatch inside `_verify_source_section_bindings`; U3b adds `Corpus.undecided_bindings: dict`, `_compute_undecided_bindings()`, and `assemble_corpus`'s `enforce_bindings` kwarg |
| `scripts/paper_guidance.py` | Read | `read_markdown_outline`/`segment_markdown` reused unchanged; U2c additionally reuses `read_registry`/`ingested_papers`, unchanged |
| `scripts/paper_cli.py` | Modify | Seven codes into `REFUSAL_CLASSIFICATION` (U2c adds `EVIDENCE_ROOT_AMBIGUOUS`); `source_roots` in `plan`/`phases`/`contract`; `_resolve_write_gate` returns the corpus so `cmd_write` reports it; U3b passes `enforce_bindings=True` from `_resolve_write_gate` only |
| `proposals/.paper-writing.json` | Create | `{"revisions":{"revision_prefix":"r","ordinal_digits":2}}` |
| `sections/01-*.md`, `02-*.md`, `04-*.md`, `06-*.md`, `08-*.md` | Modify, then reverted | U3 transcribed bindings for every bindable, measured requirement; U3b removed two of the nine (`introduction.block-4a`, `abstract.slot-3`); U3d removes the remaining seven, per Decision I's ruling — all five files are byte-identical to `main` again |
| `tests/test_paper_contract.py`, `test_paper_writing.py`, `test_paper_decisions.py` | Modify | Shape, resolution, mutation proofs, synthetic `experiments/` fixture, `SECTION_BINDING_ABSENT` write-gate tests; U3b moves the assembly-time `SECTION_BINDING_ABSENT` test to an `undecided`-report assertion and retargets its mutation proof through `cmd_write`; U3d renames every fixture that had borrowed the proposal's own real lineage/paper-id spelling to an invented one |
| `tests/test_forge_scaffolding.py` | Modify | U3d: a historical-incident docstring naming the real evidence-folder name is genericized; no assertion changed |
| `.claude/skills/paper-writing/SKILL.md` | Modify | U3d: an illustrative folder-name list swaps the real evidence-folder name for an invented one |
| `tests/test_proposal_implementation.py` | Modify | U3d: `ForgeVocabularyDerivedGuardTests` gains `paper_product_root_words()`, widening `derived_denylist()`'s denylist derivation from `implementations/` alone to also cover `proposals/`/`experiments/`/`guidance/`'s evidence folder, contributing only the undivided compound of a live lineage or paper id (Decision I) |

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


# paper_graph.py (U3b)
def assemble_corpus(
    sections_dir: Path, *, source_base: Path | None = None, enforce_bindings: bool = False,
) -> Corpus:
    """`enforce_bindings=False` (every read-only verb's own default): an
    undecided binding is reported in `Corpus.undecided_bindings`, never
    raised. `enforce_bindings=True` (`_resolve_write_gate`'s own call,
    the ONLY one in the skill): the SAME condition raises
    SECTION_BINDING_ABSENT. `Corpus.undecided_bindings` -- qualified
    block id -> {fact_id: {"state": "undecided", "root": str}} -- mirrors
    `source_roots`'s own report shape rather than inventing a second
    reporting convention."""
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
| `SECTION_BINDING_ABSENT` | Delete the `document` half from one shipped entry, invoked through `write` (U3b: the assembly-time raise moved to `write`-only, so the mutation proof must go through `cmd_write`, not `assemble_corpus` in isolation) |
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
| U3b | Correctness repair: an undecided binding reports (`Corpus.undecided_bindings`, mirroring `source_roots`), `SECTION_BINDING_ABSENT` refuses at `write` ONLY (Decision H); removes the two invented bindings (`introduction.block-4a`, `abstract.slot-3`) U3's own apply transcribed under this same pressure | engine-only, well under budget (owner ruling: budget counts engine lines) | yes |
| U3c | Discharges the stated `experiments/` generality risk: the full marker/lineage/section/`undecided`-`write` path proven against a SECOND `PROSE`-kind root, tests-only, zero engine edits | tests-only, well under budget | yes |
| U3d | Owner ruling (Decision I): removes all nine `document` bindings U3/U3b left transcribed in `sections/*.md`, restoring byte-identity with `main`; renames every suite fixture that had borrowed the proposal's own real lineage/paper-id spelling; widens `ForgeVocabularyDerivedGuardTests.derived_denylist` to derive from `proposals/`/`experiments/`/`guidance/` too, not `implementations/` alone | tests + suite-fixture renames, well under budget | yes |

Estimated total **~470 changed lines** against the 400-line budget — above the proposal's ~440
because the marker reader and its two codes were added by the Question-1 ruling.
`400-line budget risk: Medium`. **Two chained PRs recommended**: PR#1 `U1+U2` ≈ 300, PR#2 `U3` ≈ 170
targeting PR#1's branch. U1 and U2 are inert without U3, so PR#1 ships green on the untouched corpus.
U3b is a same-branch correctness repair on top of PR#2, reported and settled per the owner's own
engine-lines-only budget ruling.

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

None inside this change's own scope. Both questions the proposal held open are ruled above:
Decision A (per-root marker) and Decision B (document-rooted predicate). The in-place digest stays
deferred with the owner's reason, additive as a third field on the binding this change ships if
in-place rewrites turn out to recur.

**Two collisions U3d's widened guard found and did not resolve, reported for the owner instead of
fixed here (out of scope/budget for this change):**

- `.claude/skills/experimental-deliberation/profile.ts` hardcodes `const DATA_PAPER =
  "guidance/data-paper"` as a required source, and that skill's own `SKILL.md`/`references/usage.md`
  accurately describe that hardcoded literal. This is the same shape of leak Decision F repaired for
  `paper-writing`'s own `dataset` fact (deriving the evidence root from `guidance/`'s own
  classification instead of a literal) — but applying that repair to a different skill's engine is
  its own change, not a U3d task.
- `.claude/skills/proposal-deliberation/profile.ts` declares `artifact: { directory: "proposals",
  stem: "research-concept", ... }` — the skill's OWN sanctioned single point of per-project
  configuration (its own comment: "This profile is now the only place that names them"), naming this
  repository's actual document stem so the skill can manage it. That is not itself a leak the way a
  transcribed binding was; whether `proposal-deliberation`'s and `proposal-implementation`'s
  extensive worked-example documentation (`references/usage.md`, dozens of lines in each) should stop
  mirroring that same real stem is a separate, pre-existing, already-partially-tracked question about
  those two skills' own doctrine, not this change's `source-section-binding` feature.
