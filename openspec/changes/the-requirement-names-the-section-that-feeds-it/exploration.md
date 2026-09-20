# Exploration: the requirement names the section that feeds it

Measured 2026-09-19 against `main` at `33b30b2`. Read-only pass; nothing
below was changed by the exploration itself.

## Scope ruling

The owner scoped this change to **pieces 1 and 2 only** (section-granular
sourcing, and naming the section rather than numbering it). The separation
loop (piece 3), transposition enforcement (piece 4) and their generality
acceptance (piece 5) are deferred to their own changes, because piece 3
cannot be built before a block can name a section at all.

## Piece 1 — section-granular sourcing is absent, and today's `source` is self-referential

`requires_facts` / `requires_declarations` / `produces_facts` entries are
`{value, source: {file, quote}}` (`paper_contract.py:104-110`).
`paper_graph._verify_requirement_transcription` (`paper_graph.py:258-280`)
checks `source.quote` against `source.file`'s own prose — and in every
shipped contract `source.file` is **the contract file itself** (e.g.
`sections/06-introduction.md`), never `proposals/research-concept-r21.md`
or an `experiments/*.md` file.

The existing lock therefore proves "this block's contract prose really asks
for this fact". It does not prove, and has never proved, "which part of the
real source document backs it".

`paper_declarations.FACT_SOURCE_ROOT` (`paper_declarations.py:641-647`)
maps five facts to root directory *names* only — `formulation` and
`dataset` to `proposals`, `experimental-design` to `experiments`,
`implementation` and `results` to `implementation`. It is used exactly
once, to check a root is non-empty; it never names a file, a section, or a
byte range.

## Piece 2 — the segmenter exists but is wired elsewhere; no staleness detection exists

`segment_markdown` (`paper_guidance.py:231-280`) already returns
`{title, level, byte_start, byte_end}`, with the "a shallower heading
swallows the appendix" fix already applied. It is called only from
`packet`'s `guidance/`-folder reference-outline assembly, never over
`proposals/` or `experiments/`.

No digest or mtime mechanism watches those roots. `paper_provenance.py`
hashes only `sections/*.md`. `proposals/*` and `experiments/*` are fully
gitignored (only `.gitkeep` tracked), so no git history exists for them
either. The closest precedent, `EvidenceSpan.locate`'s `file_sha256`
(`paper_evidence.py:78-107`), is write-only: a whole-tree grep shows it is
never re-read for comparison, so even that pattern does not detect an
in-place rewrite today.

This matters here specifically: a source document in this repository has
already been rewritten in place under the same revision name.

## Corrections to the premises this exploration was given

Two framings handed to the exploration were wrong and are recorded here so
no later phase rebuilds on them.

1. **The `introduction.block-4` split was not a fact-root straddle.**
   `sections/06-introduction.md`'s own "Structural decisions" (lines
   264-270) documents it as `ORDER_CYCLE` avoidance: block 2 depends on
   `4b`, and `4a` depends on block 2, so collapsing them into one node
   manufactures a cycle. That `4b` requires facts from two roots
   (`formulation` + `results`) is ordinary multi-fact composition, legal
   everywhere else too (`block-5` does the same). This must not be cited as
   a straddle precedent.

2. **`_verify_input_partition` covers none of this.**
   `paper_graph.py:196-218` is a two-line regex check confirming that the
   `### External inputs` / `### Internal chain` headings exist in a
   contract's prose. It has no notion of a source document at all.

## Piece 5 — generality, confirmed on disk

Both `sections/01-materials-and-methods.md` and
`sections/02-experimental-setup.md` declare `mode: transposition` at
section level. The document-sourced facts are exactly `FACT_SOURCE_ROOT`'s
keys; the four PRODUCED facts plus `skeleton` have no document root and
must be excluded by construction, not by a list.

Caveat carried forward: `experiments/` is empty except `.gitkeep` in this
checkout, so generality over that root can only be exercised against a
synthetic fixture. `proposals/` holds 21 distinct revision files
(`r01`–`r21`), not one file edited across revisions.

## Refusal roster, measured

`paper_cli.REFUSAL_CLASSIFICATION` holds exactly **133** codes. Naming is
dominantly SUBJECT_PREDICATE (`BLOCK_DUPLICATED`, `ORDER_CYCLE`); **12
exceptions (~9%)** lead with a qualifier — the 8 `UNKNOWN_*` codes, 3
`MALFORMED_*` codes, and `NOT_AN_OBSERVABLE_FACT` — all of them
closed-vocabulary membership checks. A new code here should follow the
dominant pattern (`SECTION_NOT_IN_SOURCE`, never an `UNKNOWN_*` shape)
unless it is itself a membership check.

## Affected areas

`paper_contract.py`, `paper_graph.py`, `paper_guidance.py`,
`paper_declarations.py`, `paper_cli.py`; the pilot contracts
`sections/01-materials-and-methods.md` and
`sections/02-experimental-setup.md`; `tests/test_paper_writing.py`,
`tests/test_paper_contract.py`, `tests/test_paper_decisions.py`.

## Sizing

Comparable precedent `a-fact-is-declared-or-it-is-produced`: 6 new codes,
5→8 Kahn waves, 5 spec domains touched. This change estimated at ~300-500
changed lines, against a 400-line review budget under `ask-on-risk`.

## Open decision this change must settle by name

`proposals/` and `experiments/` carry no digest today. This change must
either close that staleness gap or defer it explicitly by name — it must
not leave the question unasked, because a section binding that silently
re-points after an in-place rewrite is the exact failure the naming
requirement exists to prevent.
