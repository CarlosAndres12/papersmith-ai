# Design: The Whole Cut Is Argued Before Any Section Is Claimed

All examples below use invented names (lineage `field-survey`, revision `field-survey-r07.md`, blocks
`overview.block-a` / `methods.block-b` / `methods.block-c`, section titles `1. Background on widget
metrics` … `5. Open problems`). No block id, section title, document filename, paper id, subject word
or revision-pattern literal of the paper being written appears here, and none may enter
`.claude/skills/` or the forge suite. Fact ids (`formulation`) are the forge's own shipped
vocabulary, not the paper's.

Roster measured **144** live today via `reachable_paper_refusal_codes()`. No post-change count
appears in this document; it is re-derived after the code lands.

## Technical Approach

One new verb, `separate`, shaped on `compute_observation`: read an agent-authored JSON file at a path
the agent chooses, validate its shape, reconcile it against two real disk measurements this process
takes itself (the assembled corpus, and the resolved source document), refuse on disagreement, and
**never record a binding under any outcome**. It records one thing only: the round — the argument,
not the decision.

The pipeline, in fixed order:

    --proposal <path>
      │  1. shape            SEPARATION_REPORT_UNREADABLE
      ▼
    facts ──FACT_SOURCE_ROOT──▶ exactly one SourceRoot   (UNKNOWN_FACT, BINDING_FACT_NOT_BINDABLE)
      │  2. paper_graph.resolve_section_index(source_roots, root, lineage)
      │     (the SHIPPED marker → lineage → segment_markdown chain, extracted, not duplicated)
      ▼
    revision file ──▶ outline ──claimable_sections()──▶ ordered claimable set C
      │  3. per-title resolution, every named title, anchored or not
      │        SECTION_NOT_IN_SOURCE · SECTION_TITLE_AMBIGUOUS · SEPARATION_SECTION_UNCLAIMABLE
      ▼
    assemble_corpus(enforce_bindings=False) ──▶ anchor each (block, fact); unanchored are REPORTED
      │  4. score_cut(C, anchored claims) → (orphan, overlap, gap)
      ▼
    concession?  ──yes──▶ recompute BOTH scores from disk   SEPARATION_ROUND_ABSENT
      │                                                     SEPARATION_CONCESSION_REGRESSED
      ▼  5. record the round (declarations region, kind="separation")
    score > 0 ──▶ SEPARATION_SECTION_OVERLAP | _SECTION_ORPHANED | _NOTATION_GAP, naming every instance
    score = 0 ──▶ exit 0, payload names the exact `bind` invocations the operator must now run

And, by the owner's amendment (Decision I), `bind` now demands that licence rather than merely
offering it: a binding for a measured, document-rooted fact is refused unless a **settled** round for
the document resolved and digested **right now** names that exact `(block, fact)` with that exact
title set. The loop can no longer be walked around.

## Architecture Decisions

### A — Round history is a FOURTH `declarations`-region record kind, keyed by round (Ruling 1)

**Chosen.** `kind="separation"`, `id = separation::{root}::{lineage}::{revision}::round-{n}`,
written through `_set_record` **unchanged** (`value_field="revision"`, with `root`, `lineage`,
`round`, `assignments`, `score` in `extra`). Reader `read_separation_rounds(paper_dir, root, lineage,
revision)` mirrors `read_bindings`: read-only, `{}` before `paper/` is scaffolded, same
`_read_declarations` / `_verify_not_hand_edited` / `_body_or_default` path, same
`DECLARATIONS_HAND_EDITED` guard, no `--adopt`.

| Option | Tradeoff | Decision |
|---|---|---|
| Fourth record kind, per-round id, same region | The archived design rejected a second on-disk **file** — "a second thing to keep in sync, a second hand-edit guard, a second precedent for where a decision lives" — and answered it by making `binding` the **third record kind**. A fourth kind is that same answer, not a reopening of it. A distinct id per round means `_set_record`'s fixed-record refusal never blocks round two | **Chosen** |
| Widen `binding` to hold rounds | Collapses the one distinction this change exists to keep: a binding is a decision, a round is an argument. It would also make `read_bindings` return things nobody bound | Rejected |
| A new untracked file | Repeats an option already rejected with reasons; the region's digest and hand-edit guard would have to be written a second time | Rejected |

Three refinements the exploration's candidate did not carry:

1. **The revision is part of the id.** Two rounds scored against different revisions of the source
   document are two numbers measured in different régimes, and comparing them would be exactly the
   kind of arithmetic this change exists to refuse. Keying by revision makes staleness structurally
   impossible: publish `field-survey-r08.md` mid-negotiation and the next round is round 1 again, and
   a concession naming a round from `r07` refuses `SEPARATION_ROUND_ABSENT` naming both revisions.
   No stale-round code is needed.
2. **The round number is derived, never supplied.** `n = max(existing rounds for that id prefix) + 1`.
   The file may not name a round; naming one is a shape error. An agent that could choose `n` could
   renumber over its own history.
3. **No `reopen_separation`.** Deliberately absent. Reopening a round would let an argument be
   rewritten after its successor was scored against it. History is append-only.

**Replay.** If the canonicalized cut is byte-identical to the latest existing round for that id
prefix, nothing is recorded and that round is returned (or re-refused) — a retried invocation must
not inflate the round count.

### B — The claimable set is derived from the document's own structure, level-free (Ruling 2)

**Chosen algorithm** — `paper_separation.claimable_sections(outline) -> dict`, pure, given
`segment_markdown`'s own `{title, level, byte_start, byte_end}` headings:

1. No headings at all (`reason: NO_HEADINGS`) → the claimable set is **unmeasured**.
2. **Eliminate root spans, to a fixed point.** A heading `H` is a root span iff every *other*
   remaining heading's `byte_start` lies strictly inside `[H.byte_start, H.byte_end)` — it contains
   all of them, so it partitions nothing. Drop it and repeat.
3. The **claimable set** is every remaining heading at the **shallowest remaining level**, ordered by
   `byte_start`. Deeper headings are subsections *of* a claimable section, never claimable
   themselves.
4. Empty remainder → **unmeasured**.

No level literal appears anywhere. On a document carrying its own level-1 title plus five level-2
sections, step 2 drops the title (it contains all five) and step 3 yields the five — the measured
false positive never fires. On a document with three level-1 sections and no wrapping title, no
heading contains all others, so the three level-1 headings are claimable. On a document nesting its
real sections at level 3 under a level-2 wrapper under a level-1 title, step 2 iterates twice and the
level-3 headings are claimable, **with no engine edit** — that fixture is the generality proof.

| Option | Tradeoff | Decision |
|---|---|---|
| Root-span elimination + shallowest remaining level | Level-free, computed from the document's own byte spans, identical for two people; handles the wrapper case by iterating | **Chosen** |
| "Shallowest level with two or more headings" | Undefined for a document whose every level occurs once, and a document with two level-1 sections plus a level-1 title would silently claim the title | Rejected |
| Declare the level in `<root>/.paper-writing.json` | The marker's grammar is closed and validated ("both keys required, nothing else admitted"); widening it touches `MALFORMED_SOURCE_MARKER`'s scenarios and every marker on disk, to make a human declare something the document already answers | Rejected |

A title that resolves to a real heading **outside** the claimable set (the document's own title, or a
subsection) refuses **`SEPARATION_SECTION_UNCLAIMABLE`**, naming the title, the derived claimable
level and the claimable set. An **unmeasured** claimable set refuses the same code naming the
document and the reason — reporting it and exiting 0 would let a cut pass because nothing was
measured, which is how a green run comes to mean nothing happened.

### C — There is exactly ONE artifact shape; the counter-proposal is submitted through it (Ruling 3)

The orchestrator's reasoning is **confirmed**, with the refinement that resolves the contradiction
between the proposal's Out of Scope line and its own Risks row: no owner-specific artifact kind is
created. There is one shape — the round proposal — and a counter-proposal is a round submitted
through `separate` like any other, carrying the optional key `concedes_to_round: n` when the
submitter is abandoning round *n* in favour of this cut.

The skill never asks **who** wrote a file and carries no authorship field. It cannot verify
authorship, and a field it cannot verify is an authority claim wearing a schema — precisely what
invariant 3 forbids. A concession is therefore not "the agent accepting the owner"; it is "this cut
replaces round *n*", and the skill answers it with arithmetic it recomputed from disk for both cuts.
The owner's cut is refused on exactly the same terms as the agent's.

The alternative — the counter-proposal stays conversational — is overruled: a concession can only be
verified against something the skill has read, and prose read by an agent and paraphrased into a
file is the agent vouching for the owner, which is the concession-by-authority failure mode this
change exists to close.

### D — The scoring function, defined once

Let `C` be the ordered claimable set (`index(t)` is its position). Let the **anchored** assignments be
those whose `(block, fact)` pair is a real `requires_facts` entry of that block in the assembled
corpus; for each block `b`, `claims(b)` is the union of the claimed titles across all of that
block's anchored assignments.

- **orphan** `= |{ t ∈ C : no anchored block claims t }|` — one per uncovered title.
- **overlap** `= Σ_{t ∈ C} max(0, k(t) − 1)` where `k(t)` is the number of **distinct** anchored
  blocks claiming `t` — the number of claims that must be withdrawn. Two blocks on one title score 1;
  three score 2. (The proposal's "one defect per instance" is ambiguous at k ≥ 3; this is the ruling.)
- **gap** `= Σ_b |{ t ∈ C : min index(claims(b)) < index(t) < max index(claims(b)), t ∉ claims(b) }|`
  — one per skipped title. A block claiming zero or one title contributes 0.
- **score** `= orphan + overlap + gap`. Lower is better. **Settled iff score = 0.**

The worked example reproduces exactly: round 1 = 1 overlap + 2 orphans + 1 gap = 4; branch A = 0;
branch B = 1 overlap + 2 orphans + 2 gaps = 5.

**What makes one cut better than another**: strictly the total. Nothing else is ranked — not
elegance, not order of arrival, not who submitted it. **Equal totals are not a regression**: a
concession that ties is accepted, because the skill measured no structural cost and has no standing
to rank the rest.

**Unanchored assignments are reported, never deleted and never invented** (the proposal's own
ruling), and they **contribute nothing to coverage**: their titles do not clear an orphan and cannot
create an overlap or a gap. Fail-closed — otherwise a cut over fictional blocks would score 0 by
covering everything with nothing.

**The stored score is never authority.** Every round record carries its score for an operator to
read, and the concession check **recomputes both** from disk from the stored `assignments`. Its
mutation proof overwrites a stored score with 0 and asserts the refusal is unchanged.

### E — Refusal precedence, and why the concession check runs first

A cut with defects in several classes raises one code with a detail naming **every** instance of
**every** class plus all four numbers. Precedence is fixed: **overlap → orphan → gap**. Overlap is
two blocks drafting the same prose (a contradiction), orphan is content silently dropped, gap is an
ordering defect inside one block.

The concession check runs **before** the structural refusal. If it ran after, only a score-0 cut
could ever reach it, and `SEPARATION_CONCESSION_REGRESSED` would be a refusal that cannot fire —
a guard that reads as protection and protects nothing. Ordered this way, branch B's conceded cut
(score 5 against round 1's 4) refuses the concession code, naming both cuts and both scores, which
is also the message the agent actually needs first.

### F — When a round is recorded, and when it is not

Every structurally-validated round is recorded **whatever its score** — the record is the
negotiation's log, not a verdict, and round 1 in the worked example must be readable at round 2
precisely because it scored 4. Recording therefore happens after the concession check and **before**
the structural refusal; the refusal's detail names the recorded round id.

A **regressed concession is never recorded**: it was refused, so it never became a round, and
re-submitting it refuses identically forever with no state growth. A write failure
(`DECLARATIONS_HAND_EDITED`) wins over any pending structural refusal.

This is where `separate` departs from `observe`, which writes nothing ever. The departure is exact
and bounded: `separate` writes the **argument** and never the **decision**.

### G — Why `separate` never calls `bind`, in the applier's own terms

An applier under time pressure will want a settled separation to record its own assignments — one
command instead of three. Resist it for a property that is easy to lose and expensive to rebuild: at
any moment you can ask *"which bindings exist?"* and the answer is exactly the set of `bind`
invocations somebody made. One verb, one record kind, one question. If `separate` bound on success,
the recorded set would also contain bindings nobody ever invoked, created as a side effect of the
agent's own file passing arithmetic the agent could also see — the agent would decide the paper's
bindings by writing a file to a path it chose, which is the "decided by editing a file" route
Decisions I and J of the archived design closed.

Second reason, independent of provenance: **score 0 means "no section is dropped, doubled or
skipped". It never means "these are the right sections."** The skill measures structure; the owner
rules content. Auto-binding would promote a structural pass into a content decision.

Held by two tests, not by this paragraph: an AST assertion that the set of `declarations`-region
record kinds reachable from `cmd_separate` is exactly `{"separation"}`, and an end-to-end session in
which a settled separation is followed by `write` still refusing `SECTION_BINDING_ABSENT` until an
operator runs `bind`.

### H — What `separate` is wired to, and what it honestly is not

Invariant 5 (nine measured instances) says a guard wired only to a read-only verb is wired to
nothing. Those nine were checks buried inside `assemble_corpus` that only read-only verbs reached.
This is a different shape: every raise site lives in `cmd_separate`'s own closure and fires whenever
the verb runs, so none of them is unreachable.

The residual this decision originally left open — **nothing forces an agent to run `separate` before
`bind`** — was reported to the owner rather than closed, because widening `bind` sat outside the
approved scope. **The owner has since read that risk and widened the scope on purpose.** It is closed
here by Decision I; this decision's own analysis stands unchanged, and the sibling change applying
second inherits a closed hole rather than an open one.

To leave that reachable rather than duplicable, the marker → lineage → `segment_markdown` chain is
**extracted** from `_verify_source_section_bindings` into a module-level
`paper_graph.resolve_section_index(source_roots, root, lineage) -> (path, counts, outline)`, called
by the existing verifier (behaviour unchanged, memo semantics unchanged) and by `cmd_separate`.
`claimable_sections` stays pure in `paper_separation.py` with no corpus dependency, so a sibling
check can import it without touching `paper_graph`. No edits are planned in `paper_leak.py` or
`paper_write.py`.

### I — `bind` demands a settled round that names this exact claim (owner amendment)

Today the machinery reads:

    the long road   separate → argue → separate → bind
    the shortcut    bind

The loop exists and can be walked around entirely. This decision removes the shortcut. **`bind` is
still the only place a binding becomes real** — a precondition is added to it, nothing is moved into
`separate`, and `separate` still records no binding under any outcome.

**The precondition, exactly.** For a `(block, fact)` whose source root is **measured**, `bind`
refuses unless a recorded separation round exists that satisfies all four of:

1. its id matches `separation::{root}::{lineage}::{revision}::round-{n}` for the root derived from
   `fact`, the `--lineage` given, and the revision **resolved right now** from disk;
2. its recorded `document_digest` equals the sha256 of that document's bytes **read right now**;
3. its recorded score total is `0` — it is a *settled* round, not merely a recorded one;
4. its `assignments` contain an entry naming exactly this `(block, fact)` whose title set is
   **equal** to the set being bound.

| Weaker form | Why it loses |
|---|---|
| "A round exists" | Proves an argument happened near this document, nothing more. Round 1 of the worked example scores 4 and was refused; it is history, not a licence. It would license binding a block the cut never mentioned |
| "A round exists whose structural check passed" | Better — the cut is whole — but still only proves *some* settled cut exists. An operator could bind `methods.block-c` ← `5. Open problems` off a settled round that gave `5. Open problems` to `methods.block-b`, and the recorded bindings would then contradict the only cut anyone argued |
| "A settled round names this `(block, fact)`", titles unchecked | Licenses binding a **subset** or a **superset** of the argued titles. Dropping `3. Proposed alignment objective` from a two-title claim silently reintroduces the orphan the cut existed to eliminate, with a licence that still reads valid | 
| **Set equality on the titles** | The only form under which the recorded bindings, taken together, reconstruct exactly the cut that was argued. **Chosen** |

Set equality, not sequence equality: `sections` is an unordered claim (`score_cut` consumes it as a
set), so demanding list order would refuse a correct binding on a cosmetic difference.

**Checks 1 and 2 are the licence's expiry, and that is intended.** Keying rounds by resolved revision
was already load-bearing (Decision A); it now also means **a new revision voids the licence**. That
is the difference between "somebody argued this once" and "somebody argued this against the document
that is actually there" — publish `field-survey-r08.md` and every binding for that lineage must be
re-argued before it can be recorded again. Check 2 exists because this project has already been bitten
by an **in-place rewrite**: same filename, different bytes. A revision check alone would let a
licence survive a document that was silently rewritten under it. The digest is read from disk at
`bind` time and compared against the digest `separate` recorded; neither number is trusted from a
record alone, and the region's own `DECLARATIONS_HAND_EDITED` guard protects both.

**Both root kinds.** The four checks are expressed over *the resolved document*, never over an
ordinal. For a `PROSE` root the resolution is `resolve_lineage` (highest ordinal); for an `INGESTED`
root it is `resolve_ingested_document` (identity) — both already live in `paper_declarations`. Check 1
therefore holds identically for an ingested paper; it simply never expires *by revision*, because an
ingested document is never superseded by an `r22`. Check 2 is what protects the ingested case: re-ingest
or edit that markdown and the digest moves, so the licence is void exactly as it should be. Neither
kind gets a carve-out and neither path is a special case.

**Where the guard lives.** Inside `paper_declarations.bind_section`, not only in `cmd_bind` — the same
precedent `decline_fact`'s own `DECLINE_REASON_REQUIRED` set, so no caller escapes it by skipping a
CLI-layer check. This is possible without a cycle because every piece it needs (`FACT_SOURCE_ROOT`,
`source_root_status`, `read_revisions_marker`, `resolve_lineage`, `resolve_ingested_document`,
`read_separation_rounds`) already lives in `paper_declarations`; `paper_graph` is never imported and
the corpus is never assembled at `bind` time. `bind_section` gains one keyword-only `source_base`,
and `bind` gains `--sections` with the identical default and help text every sibling subcommand
already carries — `source_base=None` derives that same default and **never** means "skip the check".

**`--reopen` is deliberately unguarded.** Reopening withdraws a claim; it never creates one. A
precondition on withdrawal would trap an operator inside a binding they can no longer argue for.

**An unmeasured root is reported, never silently passed.** The precondition applies exactly where
`SECTION_BINDING_ABSENT` applies — a measured, document-rooted root. When the root is `unmeasured`
there is no document to argue a cut over at all, so `bind` records as it does today and its payload
carries `separation: unmeasured(<reason>)`, the same report shape `source_roots` already uses. Such a
binding is inert by construction (`_verify_source_section_bindings` skips unmeasured roots), so this
is not an escape hatch: it cannot launder a claim, and the reason is on screen rather than inferred.

### J — What the first person to hit this sees

Nothing on disk carries a binding today (Decision I of the archived design removed all nine), so this
breaks no existing state. The first person to reach it is an operator answering `write`'s own
`SECTION_BINDING_ABSENT` with the `bind` invocation that refusal handed them — and getting refused a
second time. The message must therefore do what the rest of this skill does: **name the next action**,
not merely withhold permission.

`BINDING_UNARGUED`'s detail names the block, the fact, the root, the resolved revision, which of the
four checks failed, and the exact `separate --proposal <path>` invocation that answers it, together
with the proposal file's own required shape. Where a settled round exists but disagrees, it names
**both** title sets verbatim — the argued one and the one being bound — so the operator can see
whether to change the binding or argue a new cut. Where the licence expired, it names the revision or
digest the round was scored against and the one on disk now. `SKILL.md` and `references/usage.md`
both carry the two-step loop (`separate` → `bind`) rather than `bind` alone; a doc fix that stops at
`SKILL.md` is half a fix.

## Interfaces / Contracts

The proposal file — UTF-8 JSON, one object, **key set exactly** `{lineage, assignments}` plus the
optional `concedes_to_round` (the marker's own closed-grammar discipline; an unknown, missing or
wrong-typed key refuses `SEPARATION_REPORT_UNREADABLE`):

```json
{
  "lineage": "field-survey",
  "concedes_to_round": 1,
  "assignments": [
    {"block": "overview.block-a", "fact": "formulation",
     "sections": ["1. Background on widget metrics"]},
    {"block": "methods.block-b", "fact": "formulation",
     "sections": ["2. Alignment estimators", "3. Proposed alignment objective"]}
  ]
}
```

`sections` is a **list** of unique non-empty strings — list only, not the string-or-list widening
`document.section` carries, because this key has no shipped single-string history to preserve and one
shape means one validator. A duplicate `(block, fact)` pair across assignments is a shape error. The
named facts must resolve through **exactly one** source root: a file naming two roots is not one
document's cut at all, so it fails the file's own contract (`SEPARATION_REPORT_UNREADABLE` naming
both roots) rather than earning a code of its own.

```python
# paper_separation.py -- pure, no CLI, no persistence, no corpus
def claimable_sections(outline: dict) -> dict:
    """{"state": "measured"|"unmeasured", "level": int|None,
        "titles": tuple, "reason": str|None} -- Decision B, root-span
    elimination to a fixed point, then the shallowest remaining level.
    No heading-level literal anywhere."""

def score_cut(claimable: tuple, claims_by_block: dict) -> dict:
    """{"orphan": [...], "overlap": [...], "gap": [...], "total": int}
    -- Decision D. Every list names instances, so a refusal can name
    every defect rather than the first."""

# paper_declarations.py
def record_separation_round(paper_dir, root, lineage, revision, document_digest,
                            assignments, score, *, clock=paper_region.default_clock) -> dict:
    """Fourth `declarations` record kind, id
    separation::{root}::{lineage}::{revision}::round-{n}, n DERIVED.
    Byte-identical replay of the latest round records nothing.
    `document_digest` is sha256 of the resolved document's bytes at
    scoring time -- Decision I check 2, the in-place-rewrite guard."""

def read_separation_rounds(paper_dir, root, lineage, revision) -> tuple:
    """Read-only, ordered by round. {} before `paper/` is scaffolded,
    mirroring read_bindings."""

def settled_round_licensing(paper_dir, root, lineage, revision, document_digest,
                            qualified_block_id, fact_id, sections) -> dict:
    """Decision I's four checks, as ONE predicate both `bind_section` and
    its tests go through: {"state": "licensed"|"refused"|"unmeasured",
    "round": int|None, "failed_check": str|None, "argued_sections":
    tuple|None, "reason": str|None}. Returns the data the refusal detail
    names, so the message is derived, never composed twice."""

def bind_section(paper_dir, qualified_block_id, fact_id, lineage, sections,
                 *, source_base=None, clock=paper_region.default_clock) -> dict:
    """(amended) Refuses BINDING_UNARGUED before recording, unless the
    fact's own root is `unmeasured` -- then it records and REPORTS
    `separation: unmeasured(...)`. Enforced HERE, not only in `cmd_bind`,
    the same precedent `decline_fact`'s DECLINE_REASON_REQUIRED set. No
    `paper_graph` import: every resolver it needs already lives in this
    module, so no corpus is assembled at bind time."""

# paper_graph.py
def resolve_section_index(source_roots: dict, root, lineage: str):
    """The shipped marker/lineage/segment chain, extracted so a sibling
    check reaches it instead of duplicating it."""

# paper_cli.py
def compute_separation(proposal_path: Path, *, sections_dir, paper_dir, source_base=None) -> dict:
    """`separate`'s own logic on already-resolved paths, the same
    separation compute_observation keeps from cmd_observe."""
```

## Refusal Codes — eight: seven on `separate`, one on `bind`

| Code | Condition | Tier |
|---|---|---|
| `SEPARATION_REPORT_UNREADABLE` | Unreadable, non-UTF-8, non-JSON, non-object, key-set violation, bad assignment shape, duplicate `(block, fact)`, more than one source root | work-state |
| `SEPARATION_SECTION_UNCLAIMABLE` | A named title resolves to a heading outside the claimable set, or the claimable set is unmeasured | work-state |
| `SEPARATION_SECTION_OVERLAP` | A claimable title claimed by two or more distinct anchored blocks | work-state |
| `SEPARATION_SECTION_ORPHANED` | A claimable title no anchored block claims | work-state |
| `SEPARATION_NOTATION_GAP` | A claimable title interior to one block's own claimed range that the block does not claim | work-state |
| `SEPARATION_ROUND_ABSENT` | `concedes_to_round` names a round with no record under this `(root, lineage, revision)` | work-state |
| `SEPARATION_CONCESSION_REGRESSED` | A conceding cut's recomputed total strictly exceeds the recomputed total of the round it abandons | work-state |
| `BINDING_UNARGUED` | `bind`, measured root: no settled round for the resolved revision and digest names this exact `(block, fact)` with this exact title set (Decision I, four checks) | work-state |

**Collision check, run live against `.claude/skills/`**: no `SEPARATION_*` code and no
`BINDING_UNARGUED` exists anywhere today. `BINDING_UNARGUED` joins the shipped `BINDING_*` family on
`bind`'s own subject (`BINDING_FACT_NOT_BINDABLE`, `BINDING_LINEAGE_REQUIRED`,
`BINDING_SECTIONS_REQUIRED`) and is distinct from `paper_bindings.BINDING_ORPHANED`, whose subject is
a draft sentence, not a source-section binding. It is **not** folded into `SEPARATION_ROUND_ABSENT`:
that code's subject is a concession naming a round that does not exist, on `separate`, and its next
action is "submit a fresh round" — a different condition on a different verb with a different answer.

`SEPARATION_SECTION_UNCLAIMABLE` is the seventh — inside the exploration's own "five to seven"
forecast and demanded by Ruling 2: once a claimable set exists, "this heading is real but not
claimable" is a distinct state from `SECTION_NOT_IN_SOURCE` ("no such heading"), and folding it there
would report a heading that exists as missing. Note also that `BINDING_ORPHANED` already ships, with
a different subject (a draft-sentence binding matching no segmented sentence) — the subject-first
`SEPARATION_SECTION_ORPHANED` spelling avoids that collision by construction.

Reused verbatim, adding nothing new: `UNKNOWN_FACT`, `BINDING_FACT_NOT_BINDABLE`,
`SECTION_NOT_IN_SOURCE`, `SECTION_TITLE_AMBIGUOUS`, `SOURCE_LINEAGE_UNRESOLVED`,
`SOURCE_REVISIONS_UNDECLARED`, `MALFORMED_SOURCE_MARKER`, `DECLARATIONS_HAND_EDITED`,
`DECLARATION_FIXED`.

## File Changes

| File | Action | Description |
|---|---|---|
| `.claude/skills/paper-writing/scripts/paper_separation.py` | Create | `claimable_sections`, `score_cut`, document-order indexing — pure |
| `scripts/paper_declarations.py` | Modify | `record_separation_round`, `read_separation_rounds`, `_separation_record_id`, `settled_round_licensing`; `bind_section` gains the Decision I guard and `source_base`; `_set_record` unchanged |
| `scripts/paper_graph.py` | Modify | Extract `resolve_section_index`; `_verify_source_section_bindings` calls it, behaviour unchanged |
| `scripts/paper_cli.py` | Modify | `compute_separation`, `cmd_separate`, `separate` subparser + `COMMANDS`/`_COMMANDS`, eight `REFUSAL_CLASSIFICATION` entries; `bind` gains `--sections` and passes `source_base` |
| `scripts/paper_guidance.py` | Read | `segment_markdown` unchanged |
| `.claude/skills/paper-writing/SKILL.md`, `references/usage.md` | Modify | The negotiation loop in **both** — a doc fix that stops at `SKILL.md` is half a fix |
| `tests/test_paper_separation.py` | Create | Pure-core unit + mutation proofs |
| `tests/test_paper_writing.py`, `test_paper_decisions.py` | Modify | CLI path, round record, concession, e2e, roster re-derived |
| `tests/test_proposal_implementation.py` | Gate | Derived-denylist audit, run before apply and again at the end |

Nothing is deleted. No region format, digest or generation-counter change: `_body_or_default` /
`_find_record` iterate `body["records"]` generically by `(kind, id)`, so a revision that has never
seen a `separation` record reads the region unchanged.

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | `claimable_sections` | Fixtures: title + five siblings; three siblings, no title; level-3 under level-2 under level-1 (generality, zero engine edits); headingless; title-only |
| Unit | `score_cut` | The worked example's three cuts reproduce 4 / 0 / 5 exactly; k=3 overlap scores 2 |
| Unit | Shape | Every admitted/rejected key-set, `sections` grammar, duplicate pair, two-root file |
| Integration | Round 1 → round 2 with **no process state**: two separate CLI invocations, second reads only disk |
| Integration | Concession accepted (4 → 0) and refused (4 → 5), both scores recomputed |
| E2E | Settled separation → `write` still refuses `SECTION_BINDING_ABSENT` → `bind` → `write` proceeds |
| E2E | The shortcut is closed: `bind` with no round at all refuses `BINDING_UNARGUED`; the same `bind` after a settled `separate` succeeds; `--reopen` succeeds in both states |
| Integration | Licence expiry, both root kinds: a new revision published under a `PROSE` root voids it; an in-place rewrite (same filename, different bytes) voids it; the identical digest path voids an `INGESTED` document's licence with no revision involved |
| Integration | Licence scope: a settled round naming a **different** block, a **subset** of the titles, and a **superset** of the titles each refuse, naming both sets |
| Mutation | All eight codes + four property mutations | `tests/paper_mutation.py::_run_against_mutant`, each asserting its anchor count |
| Generality | `rg` over `.claude/skills/` and the suite for product names/values; `NoSubprocessScanTests` extended to the new module |
| Roster | `reachable_paper_refusal_codes()` re-derived after the code lands, never forecast; `npm test` **and** `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` |

**Mutation per code** — each chosen so a weaker lock survives it:

| Code / property | Mutation that proves it reachable |
|---|---|
| `SEPARATION_REPORT_UNREADABLE` | Exact key-set check → subset check; the extra-key fixture must go red |
| `SEPARATION_SECTION_UNCLAIMABLE` | Drop root-span elimination (every heading claimable); the title-claim test AND the "title is not an orphan" test must both go red |
| `SEPARATION_SECTION_ORPHANED` | Orphan set → empty whenever any claim exists; the one-orphan fixture must go red |
| `SEPARATION_SECTION_OVERLAP` | `k − 1` → `min(k, 1)`; the two-block fixture must go red |
| `SEPARATION_NOTATION_GAP` | Interior range `[min, max]` → `[min, min]`; the skip-one fixture must go red |
| `SEPARATION_ROUND_ABSENT` | Missing round → an empty round scoring 0 instead of refusing; the concede-to-nothing test must go red |
| `SEPARATION_CONCESSION_REGRESSED` | `submitted > prior` → `submitted > prior + 1` (survives a test that only checks a large jump); the 4 → 5 fixture must go red |
| Stored score is not authority | Overwrite a round record's stored score with 0; the 4 → 5 refusal must be unchanged |
| `separate` never binds | `kind="separation"` → `kind="binding"` in the round writer; the e2e `SECTION_BINDING_ABSENT` assertion must go red |
| `BINDING_UNARGUED` | Weaken check 4 from set **equality** to "the argued set is non-empty" (a lock that still passes every happy-path test and every no-round-at-all test); the subset-bind and wrong-block fixtures must go red |
| Licence expiry is real | Drop check 2 (digest) from `settled_round_licensing`; the in-place-rewrite fixture — same revision filename, one heading renamed — must go red. Dropping check 1 instead must redden the new-revision fixture |
| The guard is in the module | Call `bind_section` directly, bypassing `cmd_bind` entirely, with no round recorded; it must still refuse — a guard reachable only through the CLI is a guard an applier can route around |
| Claimable level is derived | The level-3-under-level-2-under-level-1 fixture scores identically with no engine edit |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or
process-integration boundary. Stdlib-only, offline, fail-closed, `Refused(code, detail)` and exit 2,
no `--force`, no `--adopt`. This CLI never invokes an agent: no `subprocess` import joins `scripts/`,
held by the shipped AST scan, which the new module joins. The verb refuses and names the next action.

## Work Units, and an honest budget statement

**GATE-0 (before U1):** the derived-denylist leak and hardcoded-product-value audit
(`ForgeVocabularyDerivedGuardTests`) runs green over `.claude/skills/` and the forge suite, comments
and fixtures included. Blocking, and re-run at the end of U5.

| Unit | Content | Est. lines | Green alone |
|---|---|---|---|
| U1 | `paper_separation.py`: `claimable_sections`, `score_cut`, ordering — pure, no CLI, no persistence | ~260 | yes |
| U2 | File shape + reader, single-root derivation, `resolve_section_index` extraction, corpus anchoring, `cmd_separate` round-1 path, four codes wired | ~330 | yes |
| U3 | `separation` record kind, writer, reader, derived numbering, `document_digest`, replay rule, `SEPARATION_ROUND_ABSENT` | ~265 | yes |
| U4 | Concession check, recompute-from-disk, precedence ordering, `SEPARATION_CONCESSION_REGRESSED`, the score-is-not-authority mutation | ~230 | yes |
| U6 | **Owner amendment (Decision I/J)**: `settled_round_licensing`, `bind_section`'s guard + `source_base`, `bind --sections`, `BINDING_UNARGUED` and its detail, expiry and scope fixtures for both root kinds, four mutations, the shortcut-closed e2e | ~220 | yes |
| U5 | `SKILL.md` + `references/usage.md` (the two-step loop), spec deltas, leak audit, roster re-measured, e2e session | ~195 | yes |

**This design is well past the ceiling, and the figure is not rounded down.** Estimated **~1470
changed lines** against the 1200 budget — about **270 over**, where the pre-amendment estimate was
~1250 (~50 over). The amendment itself accounts for ~220 of that: ~85 engine lines and ~135 of
red-first tests, four mutation proofs and the both-root-kinds expiry fixtures this project's
discipline requires for a new precondition on a recording verb.

Two compressible cuts exist, and neither is recommended:

- **Corpus anchoring** (~90 lines): drop it and `separate` argues over blocks it never checked exist,
  scoring a cut of fictional blocks as valid.
- **Decision I check 2, the digest** (~45 lines): drop it and a licence survives an in-place rewrite,
  which is a failure this repository has already lived through.

Neither is absorbed silently; both are named for the owner to rule. `1200-line budget risk: High`.

**Five chained PRs**: PR#1 `U1`, PR#2 `U2`, PR#3 `U3+U4`, PR#4 `U6`, PR#5 `U5`, each targeting the
previous branch. U1 is inert without U2; U3 and U4 share fixture setup and split badly. U6 lands
after U4 because its licence check reads the round record U3 writes and the settled-score semantics
U4 fixes, and it ships before U5 so the documentation describes the loop as it will actually behave.

## Migration / Rollout

No migration. Additive everywhere except one deliberate behaviour change: a new verb, a new module, a
fourth record kind inside the same region schema, one extracted function with unchanged behaviour —
plus Decision I's precondition on `bind`, which **is** a behaviour change and the only one.

**Its blast radius on a paper mid-flight is zero**: `sections/*.md` carries no `document` binding and
`paper/` carries no recorded one (the archived Decision I removed all nine), so no shipped or recorded
state becomes invalid. The change is felt only by the next person to record a binding, and Decision J
specifies exactly what they see. An older revision of the code reading a region that contains
`separation` records ignores them, since `_body_or_default`/`_find_record` iterate by `(kind, id)`.
Revert the branch to roll back; nothing is deleted, so nothing is lost.

## Open Questions
- [ ] This document exceeds the phase skill's 800-word guidance. Deliberate: three rulings, a scoring
      function, seven codes and ten mutation proofs were demanded explicitly, and the project's own
      archived designs run long for the same reason.
