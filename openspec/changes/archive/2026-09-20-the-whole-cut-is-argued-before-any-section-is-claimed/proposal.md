# Proposal: The Whole Cut Is Argued Before Any Section Is Claimed

## Intent

`source-section-binding` (archived 2026-09-20) resolves ONE `(block, fact)` binding at a time.
Measured: `paper_graph._verify_source_section_bindings` is strictly per-binding, and its
`{title: count}` memo is consumed only by single-title lookups. **Nothing aggregates the set of all
bound titles for a lineage against that lineage's full heading set, and nothing checks whether two
different blocks bind the identical title.**

Three defects are therefore invisible to a corpus that is entirely valid per binding:

| Class | What passes today | Why it matters |
|---|---|---|
| **orphan** | A section of the source document no block claims | Content the paper silently drops |
| **overlap** | Two blocks binding the identical title | Two blocks drafting the same source prose |
| **gap** | One block claiming sections 1 and 3, skipping 2 | A section contract's own prose demands contiguity: *"Ordered so that each subsection uses only symbols the previous ones declared. It is a chain of notation, not a list of topics."* |

`SECTION_TITLE_AMBIGUOUS` is **not** overlap: it fires when one title matches two HEADINGS, never
when two BLOCKS claim one title. Nothing close to any of the three exists.

Second, nothing forces the cut to be **argued**. Today it accretes one `bind` at a time, each locally
valid, the whole never stated. And the specific failure mode the owner named — *"ojo con
aceptarse"* — is an agent that concedes because the owner said so. Nothing may pass by authority:
not the owner's cut because it is the owner's, not the agent's because it came first, not a
concession because it is agreeable.

## Scope

### In Scope

- A **separation verb** (`separate`, spelling rulable by design) that reads an agent-authored
  proposal file, validates it, scores it, and **writes no binding, ever, whatever the outcome**.
- **The proposal file's shape**: one lineage and the whole cut across every block that reads it —
  `{lineage, assignments: [{block, fact, sections: [title, ...]}, ...]}`, UTF-8 JSON at a path the
  agent chooses, passed as `--proposal <path>`. Unreadable, non-JSON, non-object or shape-invalid
  refuses `SEPARATION_REPORT_UNREADABLE`.
- **Per-title resolution first, reusing shipped code.** Every proposed title runs through the SAME
  existence/ambiguity path `bind` already uses, raising `SECTION_NOT_IN_SOURCE` and
  `SECTION_TITLE_AMBIGUOUS` unchanged, BEFORE orphan/overlap/gap scoring runs. The per-title checks
  are extended, never replaced.
- **The three defect computations**, over the claimable heading set of the resolved revision:
  orphan = claimable titles no assignment names; overlap = a title named by two distinct blocks;
  gap = within one block, a claimable title lying between two of that block's own claimed titles in
  document order (from `segment_markdown`'s byte offsets) that the block does not claim.
- **A round record**: each round's cut plus its computed score, persisted so a later round can be
  checked against it. The skill has no session and no memory between invocations.
- **The concession check**: on round *n* > 1, when the agent concedes to the counter-proposal, the
  verb **recomputes both scores itself from disk** and refuses `SEPARATION_CONCESSION_REGRESSED`
  when the conceded cut carries more counted defects than the round being abandoned.
- **Refusal codes**, subject-first: `SEPARATION_REPORT_UNREADABLE`, `SEPARATION_SECTION_ORPHANED`,
  `SEPARATION_SECTION_OVERLAP`, `SEPARATION_NOTATION_GAP`, `SEPARATION_CONCESSION_REGRESSED`,
  `SEPARATION_ROUND_ABSENT`. Roster measured **144** live today via
  `reachable_paper_refusal_codes()`; no post-change count appears anywhere until the code lands.
- **A leaked-name and hardcoded-product-value audit as a blocking gate before apply**, not a
  formality — `ForgeVocabularyDerivedGuardTests`'s derived denylist over every product root.

### Out of Scope

- **The verb never calls `bind`.** See Approach.
- Deleting anything. No file, no record, no requirement is removed by this change.
- `paper_leak.py`, `paper_write.py` — another change is being planned against them.
- Widening `bind`, `reopen_binding`, or the `binding` record kind's fixed-until-reopened semantics.
- A second on-disk store outside `paper/` (rejected with reasons in the archived design).
- Making the owner's counter-proposal a machine artifact — see Risks.

## Capabilities

### New Capabilities

- `source-separation-review`: the whole-cut proposal shape, per-title resolution reuse, the three
  counted defect classes, the round record, the concession check, and the verb's own
  never-writes-a-binding contract.

### Modified Capabilities

- `source-section-binding`: what counts as a **claimable section** becomes explicit and shared
  (today unconstrained — see Decision for design #2). `bind`'s own per-title existence/ambiguity
  behaviour is unchanged.

## Approach

Exploration approach 1. The verb is an **advisory reviewer**, shaped exactly on `observe`
(`compute_observation`): read an agent-authored report, validate its shape, reconcile it against a
real disk measurement the CLI takes itself, refuse on disagreement, **write nothing**. Round history
reuses the existing `declarations`-region machinery — same digest, same `DECLARATIONS_HAND_EDITED`
guard, no `--adopt` — rather than opening the "where does a decision live" question several shipped
units were spent closing.

**Why the separation verb does NOT call `bind`.** A decision about the paper is made by USING the
skill — and `bind` is that use. If a settled separation auto-recorded its assignments, the agent's
own proposal would cause a state write with no separate human act between, and `bind` would stop
being the single unambiguous point where a binding becomes real. A separation would become a second,
implicit path to a recorded binding. That is the exact shape the archived design was written to
avoid.

**What the operator runs after a separation settles.** One `bind --block <id> --fact <id> --lineage
<lineage> --section <title> [--section ...]` per assignment entry. Until then `write` keeps refusing
`SECTION_BINDING_ABSENT`, naming candidates read fresh from disk, exactly as it does today. The
separation is the argument; `bind` is the act.

This CLI never invokes an agent: no `subprocess`, ever. The verb refuses and names the next action.
Where a proposed entry cannot be anchored, it is **reported** for the owner's ruling, never deleted
and never invented.

## Decisions for design — named here, settled there

**1. Where round one lives so round two can be checked.** The skill has no session. Every shipped
`declarations`-region record kind (`fact`, `declaration`, `binding`) is single-valued and
fixed-until-reopened; a negotiation needs at least two rounds readable at once, which "fixed" was
never built for. **Leading candidate:** the same region, digest and hand-edit guard, with a new
record kind giving each round its own id — e.g. `separation::{lineage}::round-{n}` — so the
fixed-record refusal never blocks recording round two after round one, and a reader mirroring
`read_bindings` enumerates rounds in order. Design rules this; the proposer does not.

**2. Which heading levels count as a claimable section.** Measured: `segment_markdown` returns every
ATX heading at levels 1–6 (`^(#{1,6})[ \t]+(.*?)[ \t]*$`). A real source document carries one
level-1 heading — its own title, spanning the whole file — plus its level-2 sections. A naive orphan
check over every returned heading would flag the document's own title as unclaimed, and would
misfire on the very first real run. Design rules what a claimable section is; it is not an
implementation-time improvisation.

## Worked example — invented names throughout

Lineage `field-survey`, current revision `field-survey-r07.md`. Headings: the document's own
level-1 title `Field Survey of Widget Alignment`, then five level-2 sections — `1. Background on
widget metrics`, `2. Alignment estimators`, `3. Proposed alignment objective`, `4. Calibration
procedure`, `5. Open problems`. Blocks: `overview.block-a`, `methods.block-b`, `methods.block-c`,
each requiring `formulation`. Counting is one defect per instance.

**Round 1 — the agent's cut.**

| Block | Claims |
|---|---|
| `overview.block-a` | `1. Background on widget metrics` |
| `methods.block-b` | `2. Alignment estimators`, `4. Calibration procedure` |
| `methods.block-c` | `2. Alignment estimators` |

The skill refuses, naming every defect: `SEPARATION_SECTION_OVERLAP` (`2. Alignment estimators`,
claimed by `methods.block-b` and `methods.block-c`); `SEPARATION_SECTION_ORPHANED` (`3. Proposed
alignment objective`, `5. Open problems`); `SEPARATION_NOTATION_GAP` (`methods.block-b` claims 2 and
4, skipping 3). **Score: 1 overlap + 2 orphans + 1 gap = 4.** Round 1 and its score are recorded.
The skill does not opine on which cut is better; it refuses a cut that breaks the structure.

**Round 2, branch A — the owner's counter-proposal, and an honest concession.**

| Block | Claims |
|---|---|
| `overview.block-a` | `1. Background on widget metrics` |
| `methods.block-b` | `2. Alignment estimators`, `3. Proposed alignment objective` |
| `methods.block-c` | `4. Calibration procedure`, `5. Open problems` |

The agent concedes. The skill validates structure again, recomputes **both** scores itself from disk
— round 1 = 4, conceded cut = 0 — and accepts. The concession is supported by arithmetic the skill
computed, not by who proposed it.

**Round 2, branch B — the same concession, unsupported.** Suppose the counter-proposal had instead
been `overview.block-a` ← `2. Alignment estimators`; `methods.block-b` ← `2. Alignment estimators`,
`5. Open problems`; `methods.block-c` ← `1. Background on widget metrics`. Score: 2 orphans (`3.`,
`4.`) + 1 overlap (`2.`) + 2 gaps (`methods.block-b` skips 3 and 4) = **5**. The agent concedes
anyway. The skill refuses `SEPARATION_CONCESSION_REGRESSED`, naming both cuts and both scores
(4 → 5): a concession to a separation that scores worse on counted defects is refused, whoever
proposed it. The agent's remaining legitimate move is a third cut of its own, scored the same way.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/paper-writing/scripts/paper_separation.py` | New | Claimable set, orphan/overlap/gap, score |
| `scripts/paper_declarations.py` | Modified | Round record kind, its writer and read-only reader |
| `scripts/paper_graph.py` | Modified | Per-title resolution/memo reused by the verb, not duplicated |
| `scripts/paper_cli.py` | Modified | `cmd_separate`, `--proposal`, new `REFUSAL_CLASSIFICATION` entries |
| `scripts/paper_guidance.py` | Read | `segment_markdown` unchanged |
| `.claude/skills/paper-writing/SKILL.md`, `references/usage.md` | Modified | The loop, in both — a doc fix that stops at `SKILL.md` is half a fix |
| `tests/test_paper_*.py` | Modified/New | Red-first, one executed mutation per new code |
| `tests/test_proposal_implementation.py` | Gate | Derived-denylist audit before apply |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| The level-1 title fires a false orphan on the first real run | High | Decision for design #2 is blocking; no orphan code before it is ruled |
| No shipped record kind is shaped like a log | High | Decision for design #1; a per-round id, not widened `binding` semantics |
| Whether the owner's counter-proposal is itself a machine artifact is unresolved, and it changes the second pass's shape | High | Design must rule it before the concession check is built |
| Size: the narrower predecessor cost ten units and four budget rulings | High | Five units, chained PRs, forecast below |
| This paper's names leak into the forge (breached in the change that just closed) | Med | Derived-denylist audit as a blocking gate, comments and fixtures included |
| Defect-count granularity changes which cut wins | Med | Design defines the scoring function once; the worked example's counts follow it |

## Review Workload Forecast

```
Decision needed before apply: Yes
Chained PRs recommended: Yes
400-line budget risk: High   (default budget; owner raised it to 1200 for this change, 2026-09-20)
1200-line budget risk: Medium
```

| Unit | Content | Est. lines | Green alone |
|---|---|---|---|
| **DP** | Design rules both decisions above | blocking | — |
| U1 | Claimable set, orphan/overlap/gap, scoring — pure, no CLI, no persistence | ~250 | yes |
| U2 | Proposal file shape + reader, per-title resolution reuse, `separate` round 1 | ~250 | yes |
| U3 | Round persistence, its reader, `SEPARATION_ROUND_ABSENT` | ~250 | yes |
| U4 | Concession check, `SEPARATION_CONCESSION_REGRESSED`, recomputed from disk | ~250 | yes |
| U5 | `SKILL.md` + `references/usage.md`, leak audit, roster re-measured | ~150 | yes |

Estimated ~1150 changed lines with red-first tests and mutation proofs counted — at the ceiling, not
under it. **Four chained PRs recommended**: PR#1 `U1`, PR#2 `U2`, PR#3 `U3+U4`, PR#4 `U5`, each
targeting the previous branch. U1 is inert without U2; U3 and U4 share fixture setup and split badly.

## Rollback Plan

Revert the branch. The change is additive: a new verb, a new module, a new `declarations`-region
record kind inside the same region schema. `_body_or_default`/`_find_record` iterate
`body["records"]` generically by `(kind, id)`, never by an exhaustive kind list, so an older
revision that has never seen a round record simply never writes one and reads the region unchanged.
No region format, digest or generation-counter change. Nothing is deleted, so nothing is lost.

## Dependencies

- Archived `2026-09-20-the-requirement-names-the-section-that-feeds-it` — `bind`, the
  `binding` record kind, lineage resolution, `segment_markdown` reuse.

## Success Criteria

- [ ] A cut with an orphan, an overlap and a gap refuses naming each one, proven by executed mutations.
- [ ] A concession to a cut scoring worse on counted defects refuses `SEPARATION_CONCESSION_REGRESSED`,
      with both scores recomputed by the skill from disk — proven by a mutation that weakens the check.
- [ ] `separate` records no binding under any outcome; `write` still refuses `SECTION_BINDING_ABSENT`
      until an operator runs `bind` — proven by an end-to-end session.
- [ ] A document's own title never reads as an orphan, per design's claimable-section ruling.
- [ ] Round two is checkable against round one with no process state, only disk.
- [ ] The derived-denylist audit reports zero leaked product names and zero hardcoded product values
      across `.claude/skills/` and the forge suite, comments and fixtures included.
- [ ] Refusal roster re-derived with `reachable_paper_refusal_codes()` after the code lands, never forecast.
- [ ] Both suites green: `npm test` and `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`.
