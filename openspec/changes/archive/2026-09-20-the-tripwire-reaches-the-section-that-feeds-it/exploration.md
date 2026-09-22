# Exploration: the tripwire reaches the section that feeds it

Measured 2026-09-20 against `main`. Read-only pass.

## Current state

**The tripwire's real reach.** `paper_leak.check_tripwire` has exactly one call
site — `paper_write.write_block` — gated on `contract.style_set`, which is
populated only from `guidance/` folders classed `style-reference`. It never
reaches evidence-bound sentences and never reaches the source-section bindings
that just shipped. The evidence audit checks binding STRUCTURE only, never
textual overlap. So a redactor can paste a source document's section verbatim
into the paper and nothing notices.

**Which blocks are in transposition mode — derived, confirmed.**
`paper_contract.resolve_mode` is fully derived: a block-level declaration wins,
the section-level one is the default, and an absent mode refuses at `write`.
Measured over the shipped corpus: six of ten sections declare
`mode: transposition`, four declare `argument`, and there are zero block-level
overrides today.

**No real bindings exist yet.** The archived change removed all nine
transcribed `document` bindings from the contracts; every bindable entry is
`undecided`. Only `bind`-recorded fixtures can exercise this end to end.

**Where the comparison would get its bytes — the path exists and is wired to
nothing.** `BlockRecord.source_bindings` → `FACT_SOURCE_ROOT[fact]` →
`source_root_status` → `resolve_lineage`/`resolve_ingested_document` → a file
path → `segment_markdown` → byte offsets → slice. Every hop is shipped and
tested. But it runs only inside `paper_graph._verify_source_section_bindings`
and the result is discarded: `paper_cli._resolve_write_gate` assembles the
corpus with `enforce_bindings=True` and returns `None`, so `cmd_write`'s
`BlockContract` never receives the resolved bindings. Closing that wiring gap
is the concrete prerequisite, and it lives in editable files.

## A shipped defect this exploration uncovered, with blast radius beyond this change

`paper_style.strip_math` does not exclude `$$...$$` display-math fences. Its
inline pattern matches the first two adjacent `$` as an empty span, so the
fences vanish and **the entire equation body survives as ordinary prose**.
Verified by executing it: an equation between `$$` fences comes out intact,
with only its delimiters removed.

The one real document-sourced file in this repository uses `$$` fences 136
times and the delimiters `strip_math` actually handles once.

This is not confined to the change being explored. The SHIPPED style tripwire
runs on stripped text too, so an equation quoted from a style-reference paper
already counts toward its eight-token overlap today. **Fixing it is a
prerequisite here and a correction to an existing guard, and its blast radius
must be measured before it is changed.**

## The threshold is not obviously transferable

The shipped spec justifies eight tokens as the point above which a shared run
stops being legitimate academic idiom — calibrated against an INDEPENDENT
published paper's prose. A source document is the same author's own earlier
text about the same work, where reusing terms, quantities and formal statements
is legitimate at a far higher baseline.

Inheriting "eight" unchanged is an assumption, not a result. Design must
justify or replace it, and must not port the three-draft register proof, which
has no natural unstyled control for a same-author document.

## The opposite failure, out of scope but real

Nothing verifies that a transposition block asserts only what its bound section
actually carries. Content verification against a located span exists today only
for citations. This is a genuine separate gap — record it, do not fold it in.

## Approaches

1. **Extend `check_tripwire` in place.** DRY, but overloads a function whose
   own spec fixes it to style semantics.
2. **A sibling function reusing the span machinery, under a new refusal code.**
   Keeps the two domains' thresholds tunable apart and leaves the shipped
   check untouched. **Recommended.**
3. **Per-sentence, inside the evidence binding.** Wrong shape: verbatim copy is
   a passage property that spans sentence boundaries.

## Recommendation

Approach 2, behind two prerequisites the owner must rule rather than inherit:
widen the math exclusion for `$$` fences and measure what that changes about
the shipped guard; and justify or replace the eight-token threshold for a
same-author source. Close the wiring gap as its own reviewable slice first.

## Refusal roster

Measured **144**, live. Any post-change number is a forecast and must never be
written into an artifact — measure after the code lands.

## Risks

- Every test path is synthetic; no real bindings exist on disk.
- The math-fence fix reaches further than this feature and may move the shipped
  style tripwire's own behaviour.
- Threshold soundness has no obvious right answer.
- `paper_graph.py` is being changed by a concurrent change, so resolution logic
  may have to be reached rather than duplicated — reconcile at design time.

## Files another change is being planned against — do not propose edits

`paper_graph.py`.
