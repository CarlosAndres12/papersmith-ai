# Design: The Requirement Names the Section That Feeds It

## Technical Approach

A requirement entry gains one optional object, `document: {lineage, section}`, parsed by the same
`_normalize_requirement_entry` that already owns `{value, source:{file,quote}}`. Shape is checked in
`paper_contract.parse` under the existing `MALFORMED_HEADER`; **resolution** is checked once per
`assemble_corpus` in a new `_verify_source_section_bindings`, alongside the eleven `_verify_*`
passes already there.

Resolution is three hops, each derived from disk, none from a literal:

    fact ──FACT_SOURCE_ROOT──▶ root name ──base/name──▶ root dir
         ──marker──▶ revision regex ──max ordinal──▶ current revision file
         ──segment_markdown──▶ heading titles ──▶ the bound section

The owner's ruling is the whole point of hop 2: a binding names the **lineage**, never `r21`.
Publish `r22` and every binding follows it for free; publish an `r22` that renames the bound
heading and `SECTION_NOT_IN_SOURCE` refuses by name.

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

## Refusal Codes — six, and why the proposal's four became six

| Code | Condition | Tier |
|---|---|---|
| `SECTION_NOT_IN_SOURCE` | Named title is no heading in the current revision | work-state |
| `SECTION_TITLE_AMBIGUOUS` | Title matches two or more headings | work-state |
| `SECTION_BINDING_ABSENT` | Bindable fact, document-rooted, no `document` half (U3) | work-state |
| `SOURCE_LINEAGE_UNRESOLVED` | Lineage resolves to zero or more than one revision | work-state |
| `SOURCE_REVISIONS_UNDECLARED` | Document-rooted root carries no marker | work-state |
| `MALFORMED_SOURCE_MARKER` | Marker not UTF-8 / not JSON / not an object / unknown or missing key / bad value | work-state |

The last two are an **amendment** the proposal did not forecast: the ruling "the pattern is read
from an on-disk declaration" arrives with a declaration, and a declaration has an absent state and a
malformed state. Folding either into `SOURCE_LINEAGE_UNRESOLVED` would conflate "nobody said how
revisions are named" with "no revision is there". `MALFORMED_SOURCE_MARKER` is qualifier-led, which
the measured roster admits for exactly this family — the three existing `MALFORMED_*` codes are all
shape checks, and so is this. Entry-shape errors reuse `MALFORMED_HEADER`; no new code for them.

Roster is **133 today**; the count after this lands is re-derived with
`reachable_paper_refusal_codes()`, never forecast.

## File Changes

| File | Action | Description |
|---|---|---|
| `scripts/paper_contract.py` | Modify | `_REQUIREMENT_OPTIONAL = ("document",)`, `_DOCUMENT_REQUIRED = ("lineage","section")`, `requirement_documents()` accessor |
| `scripts/paper_declarations.py` | Modify | `source_root_status()`, `read_revisions_marker()`, `resolve_lineage()`, `bindable_facts()` derived off `FACT_SOURCE_ROOT` |
| `scripts/paper_graph.py` | Modify | `BlockRecord.source_bindings: tuple = ()`; `Corpus.source_roots: dict`; `_verify_source_section_bindings`; `source_base` kwarg |
| `scripts/paper_guidance.py` | Read | `read_markdown_outline`/`segment_markdown` reused unchanged |
| `scripts/paper_cli.py` | Modify | Six codes into `REFUSAL_CLASSIFICATION`; `source_roots` in `plan`/`phases`/`contract`; `_resolve_write_gate` returns the corpus so `cmd_write` reports it |
| `proposals/.paper-writing.json` | Create | `{"revisions":{"revision_prefix":"r","ordinal_digits":2}}` |
| `sections/01-*.md`, `sections/02-*.md` | Modify | Bindings transcribed; prose bytes untouched |
| `tests/test_paper_contract.py`, `test_paper_writing.py`, `test_paper_decisions.py` | Modify | Shape, resolution, mutation proofs, synthetic `experiments/` fixture |

## Interfaces

```python
# paper_declarations.py
def source_root_status(base: Path, root_name: str) -> dict:
    """{"state": "document-rooted"|"unmeasured", "path": Path|None,
        "documents": int, "reason": str|None}"""

def resolve_lineage(root: Path, lineage: str, marker: dict) -> Path:
    """The single highest-ordinal revision. Refuses SOURCE_LINEAGE_UNRESOLVED
    on zero candidates and on a tie, naming what it saw."""
```

`BlockRecord.source_bindings` is a tuple of `(fact_id, lineage, section_title)` triples — a tuple,
matching the `produces_facts: tuple = ()` precedent for a frozen dataclass, defaulted so every
existing construction site stays green.

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | Entry shape, marker grammar | Direct `Refused` assertions on synthetic headers and markers |
| Unit | Lineage resolution: max ordinal, gap, tie, foreign lineage, cross-root | Tmp root with fabricated revision files |
| Unit | Document-rooted predicate | Root with only `.gitkeep`, root absent, root with `*.md` |
| Integration | Version bump is free | Fixture adds `…-r22.md` preserving bound titles; assert the corpus assembles **byte-identically untouched** (success criterion 4) |
| Integration | `write` | Existence refusal fires from `cmd_write`, not only from a read-only verb |
| Mutation | All six codes | `tests/paper_mutation.py::_run_against_mutant`, table below |
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
| Derivation, not a list | Add a **sixth** root to `FACT_SOURCE_ROOT` in a fixture and assert it becomes bindable with no engine edit (success criterion 6) |

## Work Units

| Unit | Content | Est. lines | Green alone |
|---|---|---|---|
| U1 | Entry shape + `document` validator, `requirement_documents`, `BlockRecord.source_bindings`, bindable derivation — both shapes accepted, nothing demanded | ~130 | yes |
| U2 | Marker reader, lineage→revision resolver, `source_root_status`, `_verify_source_section_bindings`, `source_roots` report, existence/ambiguity refusals | ~170 | yes (inert without U3) |
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
