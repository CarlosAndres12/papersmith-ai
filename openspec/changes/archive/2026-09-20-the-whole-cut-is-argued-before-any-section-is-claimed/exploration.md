# Exploration: the whole cut is argued before any section is claimed

Measured 2026-09-20 against `main`. Read-only pass.

## Current state

`source-section-binding` (archived 2026-09-20) resolves ONE `(block, fact)`
binding at a time. `document.lineage` resolves to a current revision on disk
through the per-root `.paper-writing.json` marker; `document.section` resolves
one or more headings through `segment_markdown`, each checked for existence and
ambiguity. `bind` records one binding into `paper/main.tex`'s `declarations`
region as a third record kind keyed `{block}::{fact}`. `write` refuses
`SECTION_BINDING_ABSENT` at write time only, naming candidates read fresh from
disk.

`paper_graph._verify_source_section_bindings` (lines 391-496) is strictly
per-binding. A memo caches `{title: count}` per `(root, lineage)` for the whole
corpus assembly — one file read, not one per binding — but every consumer of
that memo is still a single `(qualified_id, fact_id, section_title)` lookup.

**Nothing aggregates the set of all bound titles for a lineage against its full
heading set, and nothing checks whether two different blocks bind the identical
title.** `_verify_input_partition` (lines 499-521) remains exactly two regex
scans for the `### External inputs` / `### Internal chain` headings; no other
partition logic exists anywhere.

## The three defect classes, measured

**orphan** — a section no block claims. Not computed anywhere today.

**overlap** — two blocks claiming the same section. Not computed anywhere.
Note that the shipped `SECTION_TITLE_AMBIGUOUS` is a different thing: it fires
when one title matches two or more HEADINGS inside the source document, never
when two BLOCKS bind the same title. Genuinely new; nothing close exists.

**gap** — a block claims sections 1 and 3 and skips 2. Grounded in shipped
prose, not invented: a section contract's own text reads *"Ordered so that each
subsection uses only symbols the previous ones declared. It is a chain of
notation, not a list of topics."* This is fundamentally a per-binding
contiguity check — does one block's claimed title set skip a title sitting
between two others in document order — computable from `segment_markdown`'s
byte offsets. It does not strictly need the whole cut the way orphan and
overlap do, but belongs in the same review pass.

No fourth class was found implied by the corpus or the shipped specs. The
existing per-title checks are NOT replaced by these three: a separation review
must still raise `SECTION_NOT_IN_SOURCE` and `SECTION_TITLE_AMBIGUOUS`, reusing
the same resolution code, for any proposed title that fails to resolve at all,
before orphan/overlap/gap scoring runs.

## A measured false positive that must be ruled before implementation

`segment_markdown` captures ATX headings at every level 1 through 6
(`^(#{1,6})[ \t]+(.*?)[ \t]*$`). Measured against the live source document:
one level-1 heading — the document's own title, spanning the whole file since
no other level-1 follows — plus five level-2 section headings.

A naive orphan check over every heading `segment_markdown` returns would
therefore flag the document's own title as an unclaimed section. That is
nonsensical and it would fire on the very first real run.

**Which heading levels count as a claimable section is an explicit ruling this
change owes, not an implementation-time improvisation.**

## Precedents for "an agent's product the skill validates"

1. **`observe`** (`compute_observation`): the agent writes a JSON report to an
   arbitrary path; the CLI reads it, validates its shape, then reconciles it
   against a real disk measurement it takes itself, refusing
   `OBSERVATION_DISK_CONFLICT` on disagreement. **It writes nothing, ever,
   whatever the outcome.** This is the closest shape for a separation proposal.
2. **`couplings`**: a hand- or agent-authored JSON record, shape-validated then
   written WHOLE and atomically to an untracked file, never merged with prior
   content.
3. **`write`'s draft/audit shuttle**: the agent writes files; the CLI reads,
   audits, and on success performs the substitution itself. The one shuttle
   where CLI success causes a write to `main.tex`.
4. **`bind`**: a third `declarations`-region record kind reusing the same
   digest, hand-edit guard and no-`--adopt` machinery. The archived design
   explicitly REJECTED a second on-disk store — "a second file is a second
   thing to keep in sync, a second hand-edit guard to write" — in favour of a
   third record kind inside the existing region.

## The hardest question: where round one lives so round two can be checked

The skill has no session and no memory between invocations. For it to verify a
concession, something on disk must hold what was proposed on the first pass.

No existing mechanism holds a multi-round, appendable negotiation. Every
`declarations`-region record kind shipped today — `fact`, `declaration`,
`binding` — is single-valued and fixed until reopened. A separation negotiation
needs at least two rounds' mappings, or their computed scores, readable at the
same time, and "fixed" semantics were never built for that.

**Leading candidate, not decided here:** reuse the same region, digest and
hand-edit-guard machinery, but give each round its own record id — for example
`separation::{lineage}::round-{n}` under a new record kind — rather than
widening `binding`'s fixed semantics. Each round is then a distinct id, so the
fixed-record refusal never blocks recording round two after round one. A reader
mirroring `read_bindings` would enumerate the rounds in order.

This is the single largest open architectural question in the change and it
belongs to design, not to this exploration.

## Refusal roster

Measured **144**, live, by executing `reachable_paper_refusal_codes()`. The
exploring agent had no shell and corroborated 144 three ways statically; the
orchestrator re-ran it and confirms.

Proposed, unruled, following the subject-first convention:
`SEPARATION_REPORT_UNREADABLE`, `SEPARATION_SECTION_ORPHANED`,
`SEPARATION_SECTION_OVERLAP`, `SEPARATION_NOTATION_GAP`,
`SEPARATION_CONCESSION_REGRESSED` (the core "never concede because you were
asked" guard), `SEPARATION_ROUND_ABSENT`. Five to seven codes. Any post-change
count is a forecast and must never be written into an artifact — measure after
the code lands.

## Approaches

1. **An advisory separation verb, with round history as a new
   `declarations`-region record kind.** The verb validates a proposal file —
   shape, per-title existence and ambiguity, then orphan/overlap/gap — records
   this round's proposal and score for later comparison, and never calls `bind`
   itself. Matches the `observe` precedent exactly; respects the archived
   rejection of a second on-disk store; keeps `bind` as the single unambiguous
   point where a binding becomes real. Costs the operator one `bind` per
   resolved entry after a separation is settled. **Recommended.**

2. **The same, but a successful final round auto-calls `bind_section` for every
   entry.** One fewer manual step, at the price of breaking the rule that a
   binding is decided by USING `bind` — it would become a side effect of
   another verb, and an agent's own proposal would cause a state write with no
   separate human act between. This is the exact shape the archived design was
   written to avoid.

3. **Round history in a new untracked file.** Simpler code, but it reopens the
   "where does a decision live" question that several shipped units were spent
   closing, and repeats an option already rejected with reasons.

## Risks

- The level-1 title false positive will misfire on the first real orphan check
  unless heading-level scoping is ruled first.
- No shipped record kind is shaped like a log; extending the region machinery
  to a per-round id scheme is untested territory here.
- Size: the narrower `source-section-binding` change cost ten work units and
  needed the owner's budget ruling four separate times. This one is materially
  larger — whole-cut computation, the shuttle, round persistence, concession
  arithmetic, the CLI, and this project's mandatory red-first and mutation
  discipline. Expect chained slices.
- Whether the owner's own counter-proposal is ever a recorded machine artifact,
  or stays conversational, is unresolved and materially changes the shape of
  the second pass.

## Ready for proposal

Yes, carrying two open questions that the proposer must NOT settle silently:
the round-history record shape, and which heading levels count as a claimable
section.

## Files another change is being planned against — do not propose edits

`paper_leak.py`, `paper_write.py`.
