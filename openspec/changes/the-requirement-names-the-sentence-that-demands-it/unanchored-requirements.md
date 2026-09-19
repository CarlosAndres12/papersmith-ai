# Unanchored Requirements — Operator Ruling Needed (DP)

U2 transcribed 47 of the 51 `requires_facts` / `requires_declarations` entries
across the ten `sections/*.md` contracts — every entry for which a literal,
`quote_in_body`-passing sentence exists somewhere in the corpus. The 4 entries
below have **no** literal anchor that unambiguously backs that specific
block's need for that specific value, and were left as bare strings
(U1's shape layer still accepts them; the gate stays inert). This confirms
design.md's Open Questions list of 2 confirmed + 2 borderline entries — the
full read found no additional unanchored entry and no fewer.

Every field below is derived from the corpus, not asserted. The operator
rules on each row, per DP.1 in `tasks.md`: **"spurious — remove from
header"** or **"contract omission — author the missing sentence into that
contract's prose, then transcribe normally."** Do not infer the ruling from
this table; it only assembles the evidence.

## Ruling

_(Operator: write your ruling for each row in the "Ruling" column below.
Leave blank until DP.1 is complete — U3 may not start before every row is
ruled.)_

| # | Block | Field | Value | Ruling |
|---|---|---|---|---|
| 1 | `experimental-setup.es-assessment` | `requires_facts` | `experimental-design` | _(pending)_ |
| 2 | `experimental-setup.es-assessment` | `requires_facts` | `gap` | _(pending)_ |
| 3 | `experimental-setup.es-assessment` | `requires_facts` | `dataset` | _(pending)_ |
| 4 | `title-and-keywords.keywords` | `requires_facts` | `contributions` | _(pending)_ |

---

## 1. `experimental-setup.es-assessment` — `requires_facts: experimental-design`

**Contract file**: `sections/02-experimental-setup.md`

**Reading A — spurious**: the value is not mentioned anywhere in the file;
nothing ties `es-assessment` to the experimental design as a fact input.

**Reading B — contract omission**: `es-assessment` is literally the design
of the experiment (the file's own subsection title is "Assessment and Method
Comparison is the design of the comparison"), so the requirement is real —
the sentence stating it was simply never written.

**Evidence**:

- **Does the value appear anywhere in the file's body at all?** No. `rg
  "experimental.design|experimental design"` against
  `sections/02-experimental-setup.md` matches only the raw JSON string
  `"experimental-design"` inside the header list itself — zero occurrences in
  the prose body.
- **The block's own `### External inputs` rows, verbatim**:

  | Input | Unblocks |
  |---|---|
  | The **dataset** — when this section owns it | `es-dataset` |
  | Which **property** each contribution claims — if it was promised, this is where its instrument is named | `es-assessment` |
  | The **competing methods** — the baseline list settled in the state of the art | `es-assessment` |
  | The **axes** — what the comparison is swept over | `es-assessment` |
  | The **purpose-built corpus** — that no standard reference measures what is claimed | `es-assessment` |
  | The **implementation** of the experiments and its configuration — what actually ran | `es-training-details` |

  None of these rows name `experimental-design`.
- **Which other blocks anchor the same value, and where**: `experimental-design`
  is anchored (with a literal quote) for `limitations.lim-validation-items`
  (`sections/04-limitations.md`, "The experimental design — what was fixed
  instead of searched, what was tested at a single point"), `introduction.block-5`
  (`sections/06-introduction.md`, "The experimental design — scenarios,
  comparisons, criteria, complementary analyses"), and `abstract.slot-5`
  (`sections/08-abstract.md`, "The experimental design"). The fact is a real,
  well-anchored vocabulary item elsewhere — only this block's use of it is
  unbacked.
- **Is it already an `### Internal chain` row?** No. `es-assessment`'s only
  Internal chain row is the dataset one (see item 3 below); nothing chains
  it to an experimental-design source.
- **Block `optional`**: `false` (not marked optional in the header — this is
  a required block).
- **Blocks whose readiness changes if deleted**: only `es-assessment` itself.
  No other block's `requires_facts`/`requires_declarations`, `after` edge, or
  Internal chain row references `es-assessment`'s own requirement list, so
  removing this entry narrows `es-assessment`'s own `missing_facts` /
  `declined_facts` set (currently `experimental-design` shows as a declined
  fact in `phases`) and changes nothing downstream.

---

## 2. `experimental-setup.es-assessment` — `requires_facts: gap`

**Contract file**: `sections/02-experimental-setup.md`

**Reading A — spurious**: the gap is a `related-work`/`introduction` concept
(closing the state-of-the-art argument); nothing in `es-assessment`'s own
text argues from the gap.

**Reading B — contract omission**: the comparison design (which methods,
which axes) is arguably shaped by what the gap says nobody else resolved —
the sentence connecting them was never written.

**Evidence**:

- **Does the value appear anywhere in the file's body at all?** No. `rg
  "\bgap\b"` against `sections/02-experimental-setup.md` matches only the
  raw JSON string `"gap"` inside the header list — zero occurrences in the
  prose body.
- **The block's own `### External inputs` rows, verbatim**: identical table
  to item 1 above (same block, `es-assessment`). None of the five rows names
  a gap.
- **Which other blocks anchor the same value, and where**: `gap` is anchored
  for `related-work.rw-closing` (`sections/05-related-work.md`, "The gap,
  which is also stated in the introduction and must agree"). This is the
  fact's only other declared use in the whole corpus.
- **Is it already an `### Internal chain` row?** No.
- **Block `optional`**: `false`.
- **Blocks whose readiness changes if deleted**: only `es-assessment` itself,
  for the same reason as item 1 (nothing downstream reads this block's
  requirement list).

---

## 3. `experimental-setup.es-assessment` — `requires_facts: dataset` (borderline)

**Contract file**: `sections/02-experimental-setup.md`

**Reading A — spurious**: this duplicates the ordering the header's own
`after` edge already encodes (`es-assessment` → `es-dataset`); the block
does not need a second, independent "dataset exists" gate on top of that
DAG edge and its own Internal chain row.

**Reading B — contract omission**: the Internal chain quote below is a real
justification for *why* `es-assessment` needs the dataset fact (it must
draw the "which data enter" panel of its closing diagram) — it is simply
never restated as its own standalone sentence separate from the `after`
edge's ordering claim, which is why reusing it reads as circular rather than
as independent backing.

**Evidence**:

- **Does the value appear anywhere in the file's body at all?** Yes,
  repeatedly — but only as part of `es-dataset`'s own External Input row,
  the Internal chain row below, structural-decision prose, and generic
  usages of the word "dataset(s)" elsewhere in the file (lines 104, 116,
  228, 253, 259–260 of `sections/02-experimental-setup.md`). None of these
  is a sentence written to justify `es-assessment` needing the `dataset`
  fact independently of the `es-dataset` ordering dependency it already
  declares.
- **The block's own `### External inputs` rows, verbatim**: identical table
  to item 1 above. The only dataset-related row is "The **dataset** — when
  this section owns it | `es-dataset`" — it unblocks `es-dataset`, not
  `es-assessment`.
- **Which other blocks anchor the same value, and where**: `dataset` is
  anchored for `materials-and-methods.mm-dataset`
  (`sections/01-materials-and-methods.md`), `experimental-setup.es-dataset`
  (`sections/02-experimental-setup.md`, same file), `introduction.block-1`
  (`sections/06-introduction.md`), and `abstract.slot-1`
  (`sections/08-abstract.md`) — all with their own dedicated External Input
  rows.
- **Is it already an `### Internal chain` row?** **Yes** — this is exactly
  the duplication design.md flags. The file's Internal chain table carries:

  | Block | Depends on |
  |---|---|
  | `experimental-setup.es-assessment` — the closing diagram's "which data enter" panel | `experimental-setup.es-dataset` — the dataset block, when this section owns it |

  This is the same relationship already carried by `es-assessment`'s header
  `after` edge to `experimental-setup.es-dataset`, whose own quote reads:
  *"Its one dependency that is NOT internal is the data it must show
  entering, which live in `es-dataset` when the dataset belongs to this
  section"* — a real, `quote_in_body`-passing sentence, but one that already
  backs the `after` ordering edge, not (independently) this `requires_facts`
  entry.
- **Block `optional`**: `false`.
- **Blocks whose readiness changes if deleted**: only `es-assessment` itself
  — removing the `dataset` fact requirement does not touch the `after` edge
  to `es-dataset`, so `es-assessment` still cannot be written before
  `es-dataset` in the assembled order; it would only stop separately gating
  on the global `dataset` fact being declared.

---

## 4. `title-and-keywords.keywords` — `requires_facts: contributions` (borderline)

**Contract file**: `sections/09-title-and-keywords.md`

**Reading A — spurious**: `keywords` already carries an `after` edge to
`title-and-keywords.title`, and `title` itself requires `contributions`;
`keywords` inherits the dependency transitively through ordering and does
not need its own independent `contributions` gate.

**Reading B — contract omission**: keywords are themselves drawn from the
contributions (the file states "Ordered broadest to most specific: the task
or domain first, then the property, then the machinery" and "The property
in its searchable form" as one of three keyword kinds) — the sentence
tying that content requirement to the `contributions` fact specifically was
never written.

**Evidence**:

- **Does the value appear anywhere in the file's body at all?** Yes, but
  only in `title`'s own External Input row and in unrelated prose about the
  title's property-adjective slot (lines 77 and 84 of
  `sections/09-title-and-keywords.md`, e.g. "The property the contribution
  adds — and it comes first"). None of these sentences is about `keywords`.
- **The block's own `### External inputs` rows, verbatim**:

  | Input | Unblocks |
  |---|---|
  | The **contributions**, already defined — the title selects among them | `title` |
  | The **keyword-bounds** and **classification-line** — the target journal's requirements | `keywords` |

  The only row naming `contributions` unblocks `title`, not `keywords`.
- **Which other blocks anchor the same value, and where**: `contributions`
  is anchored for `title-and-keywords.title` (this same file, the row
  above), `experimental-setup.es-assessment`, `results-and-discussion.rd-contribution-blocks`,
  `related-work.rw-synthesis-artefact`, `introduction.block-2`,
  `conclusions.concl-block-1`, and `abstract.slot-2` (the last two cross-file
  via `sections/06-introduction.md` and `sections/07-conclusions.md`
  respectively). It is one of the best-anchored facts in the corpus —
  everywhere except this one block.
- **Is it already an `### Internal chain` row?** Not for `contributions`
  specifically. `keywords`'s only Internal chain row is: `title-and-keywords.keywords`
  — "the property in its searchable form, the noun form of what the title
  carries as an adjective" — depends on `title-and-keywords.title` — "the
  property adjective the title opens on". The candidate reuse here is the
  `keywords` → `title` `after` edge's own quote, *"The title carries the
  adjective; the keyword carries the noun"* — a real, `quote_in_body`-passing
  sentence, but one written to justify the **ordering** (keywords drafted
  after title), not an independent `contributions` fact requirement for
  `keywords` itself. Reusing it would be citing the same evidence twice for
  two different claims.
- **Block `optional`**: `false`.
- **Blocks whose readiness changes if deleted**: only `keywords` itself.
  Nothing depends on `keywords` (it is the terminal block of wave 5, per
  `paper_cli.py phases`), so removing this requirement only drops
  `contributions` from `keywords`'s own `missing_facts` list, leaving
  `keyword-bounds` and `classification-line` as its remaining gates.

---

## Summary

- **Transcribed**: 47 of 51 requirements now carry `{value, source: {file, quote}}`.
- **Unanchored (this file)**: 4 — exactly the 2 confirmed + 2 borderline
  groups design.md's Open Questions section named. No additional unanchored
  entry was found in the full read of all 51 requirements across all 10
  section contracts, and none of the expected 4 turned out to have a hidden
  anchor.
- **U3 blocking condition**: every row's "Ruling" cell above must be filled
  before U3 (`tasks.md` DP.1) may begin.
