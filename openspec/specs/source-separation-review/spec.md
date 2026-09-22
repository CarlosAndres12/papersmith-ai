# Source Separation Review Specification

## Purpose

`source-section-binding` resolves one `(block, fact)` binding at a time and
never checks the whole cut. This capability adds an advisory verb, `separate`,
shaped on the shipped `observe`: it reads an agent-authored proposal naming
every block's claimed section titles for one lineage, resolves each title
through the same existence/ambiguity checks `bind` already uses, derives the
lineage's own claimable section set from the resolved document's structure,
scores the proposal's orphan/overlap/gap defects against that set, records
the round (the argument), and refuses on any defect or an unsupported
concession. **It writes no binding under any outcome, whatever the score.**
A decision about the paper is made only by using `bind`; `separate` narrows
what `bind` may later accept without ever acting in its place.

## Requirements

### Requirement: The Proposal File Has One Validated Shape

A `separate --proposal <path>` file MUST be UTF-8 JSON, a single object whose
key set is **exactly** `{lineage, assignments}` plus the optional
`concedes_to_round` (an integer). Each `assignments` entry MUST be an object
with exactly `{block, fact, sections}`, where `sections` is a **list** of
unique non-empty strings. A duplicate `(block, fact)` pair across entries is
a shape error. The facts named across the whole file MUST resolve through
**exactly one** source root. Any violation — unreadable, non-UTF-8,
non-JSON, non-object, wrong key set, wrong-shaped assignment, a duplicate
pair, or more than one resolved root — MUST refuse
`SEPARATION_REPORT_UNREADABLE`.

#### Scenario: A well-shaped proposal parses

- GIVEN a proposal naming lineage `field-survey` and assignments for
  `overview.block-a`, `methods.block-b`, `methods.block-c`, each requiring
  `formulation`
- WHEN `separate` reads the file
- THEN it accepts the shape and proceeds to per-title resolution

#### Scenario: An unknown key refuses

- GIVEN a proposal object carrying a third top-level key beside `lineage`
  and `assignments`
- WHEN `separate` reads the file
- THEN it refuses `SEPARATION_REPORT_UNREADABLE` naming the unknown key

#### Scenario: A duplicate `(block, fact)` pair refuses

- GIVEN two assignment entries both naming `methods.block-b` and
  `formulation`
- WHEN `separate` reads the file
- THEN it refuses `SEPARATION_REPORT_UNREADABLE` naming the duplicate pair

#### Scenario: A proposal spanning two source roots refuses

- GIVEN assignments whose named facts resolve through two distinct source
  roots
- WHEN `separate` reads the file
- THEN it refuses `SEPARATION_REPORT_UNREADABLE` naming both roots

### Requirement: Per-Title Resolution Reuses The Existing Checks Before Scoring

Every title named anywhere in the proposal MUST resolve through the same
existence and ambiguity path `bind` already uses, **before** any
orphan/overlap/gap scoring runs. A title matching zero headings in the
resolved revision MUST refuse `SECTION_NOT_IN_SOURCE`. A title matching two
or more headings MUST refuse `SECTION_TITLE_AMBIGUOUS`. These checks are
extended to a whole-cut reviewer, never replaced.

#### Scenario: An unresolvable title refuses before scoring

- GIVEN a proposal naming a title matching no heading in the resolved
  revision, on a cut that would otherwise also carry orphans
- WHEN `separate` runs
- THEN it refuses `SECTION_NOT_IN_SOURCE` naming that title, and orphan/
  overlap/gap scoring never runs

#### Scenario: An ambiguous title refuses before scoring

- GIVEN a proposal naming a title matching two headings in the resolved
  revision
- WHEN `separate` runs
- THEN it refuses `SECTION_TITLE_AMBIGUOUS` naming that title

### Requirement: The Claimable Section Set Is Derived From The Document's Own Structure, Level-Free

`separate` MUST derive the lineage's claimable section set by eliminating
**root spans** to a fixed point — a heading whose byte range strictly
contains every other remaining heading's start offset — then taking every
remaining heading at the shallowest remaining level, ordered by byte offset.
No heading-level literal MAY govern this computation. A document with no
headings, or whose remainder is empty after elimination, yields an
**unmeasured** claimable set. A named title resolving to a real heading
**outside** the claimable set — the document's own title, or a subsection —
MUST refuse `SEPARATION_SECTION_UNCLAIMABLE` naming the title and the
claimable set; an unmeasured claimable set MUST refuse the same code naming
the document and the reason, never a silent pass.

#### Scenario: A document's own title is excluded, its sections are claimable

- GIVEN a document with one level-1 title spanning the whole file and five
  level-2 sections
- WHEN the claimable set is derived
- THEN it contains the five level-2 sections and excludes the title

#### Scenario: Three siblings with no wrapping title are all claimable

- GIVEN a document with three level-1 sections and no wrapping title
- WHEN the claimable set is derived
- THEN it contains all three

#### Scenario: Sections nested three levels deep are claimable with no engine edit

- GIVEN a document nesting its real sections at level 3, under a level-2
  wrapper, under a level-1 title
- WHEN the claimable set is derived
- THEN it contains the level-3 headings, reached by iterating root-span
  elimination twice, with no change to the derivation logic

#### Scenario: A headingless document is unmeasured

- GIVEN a resolved revision carrying no ATX headings
- WHEN the claimable set is derived
- THEN it reports unmeasured, and any proposal naming a title against it
  refuses `SEPARATION_SECTION_UNCLAIMABLE` naming the reason

#### Scenario: A title naming the document's own title refuses

- GIVEN a proposal naming the document's own level-1 title as a claimed
  section
- WHEN `separate` runs
- THEN it refuses `SEPARATION_SECTION_UNCLAIMABLE` naming that title and the
  derived claimable set

### Requirement: Orphan, Overlap And Gap Are Scored Over The Claimable Set

Let `C` be the ordered claimable set. For each claimable title `t`: **orphan**
counts titles no anchored block claims; **overlap** counts, per title,
`max(0, k(t) − 1)` where `k(t)` is the number of distinct anchored blocks
claiming it; **gap** counts, per block, claimable titles strictly between
that block's own minimum and maximum claimed title (by document order) that
the block does not claim. **Score = orphan + overlap + gap.** An assignment
whose `(block, fact)` is not a real `requires_facts` entry of the assembled
corpus is **unanchored**: it is reported, never deleted or invented, and its
titles contribute nothing to coverage — they clear no orphan and can create
neither an overlap nor a gap.

#### Scenario: An uncovered title is an orphan

- GIVEN a claimable title no anchored block's assignment names
- WHEN the cut is scored
- THEN it is counted as one orphan, named in the refusal detail

#### Scenario: Two blocks claiming one title score one overlap; three score two

- GIVEN a claimable title claimed by two distinct anchored blocks
- WHEN the cut is scored
- THEN overlap for that title is 1
- GIVEN the same title claimed by three distinct anchored blocks instead
- WHEN the cut is scored
- THEN overlap for that title is 2

#### Scenario: A skipped interior title is a gap

- GIVEN a block claiming titles at document positions 2 and 4, and not
  claiming the claimable title at position 3
- WHEN the cut is scored
- THEN position 3 is counted as one gap for that block

#### Scenario: An unanchored assignment scores nothing

- GIVEN an assignment for a `(block, fact)` pair absent from the assembled
  corpus's `requires_facts`
- WHEN the cut is scored
- THEN its claimed titles clear no orphan, and create no overlap or gap, and
  the assignment is reported as unanchored

### Requirement: One Refusal Names Every Defect, Chosen By Fixed Precedence

A cut carrying defects in more than one class raises exactly **one** code,
chosen by fixed precedence `overlap → orphan → gap`, with a detail naming
**every instance** of **every** class present plus all counted totals
(orphan, overlap, gap, and the sum). A cut with no overlap raises
`SEPARATION_SECTION_ORPHANED` when any orphan exists, naming any gaps too.
A cut with only gaps raises `SEPARATION_NOTATION_GAP`.

#### Scenario: All three classes present raise the overlap code with full detail

- GIVEN the worked-example round 1 (one overlap, two orphans, one gap,
  total 4)
- WHEN `separate` runs
- THEN it refuses `SEPARATION_SECTION_OVERLAP`, naming the overlapping
  title, both orphaned titles, the gapped block and title, and the total 4

#### Scenario: Orphan and gap with no overlap raise the orphan code

- GIVEN a cut with two orphaned titles and one gap and no overlapping title
- WHEN `separate` runs
- THEN it refuses `SEPARATION_SECTION_ORPHANED`, naming the gap too

#### Scenario: Only a gap raises the gap code

- GIVEN a cut whose only defect is one skipped interior title
- WHEN `separate` runs
- THEN it refuses `SEPARATION_NOTATION_GAP` naming that title

### Requirement: Every Structurally-Valid Round Is Recorded, Whatever Its Score

`separate` MUST record every round that passes shape and per-title
resolution, whatever its score — the record is the negotiation's log, not a
verdict. The record's id includes the resolved root, lineage, **resolved
revision**, and a round number **derived** as one more than the highest
existing round for that id prefix; the proposal MUST NOT name its own round
number. Records are **append-only**: there is no reopen for a round. A cut
byte-identical, once canonicalized, to the latest recorded round for that id
prefix records nothing and returns that same round. Recording happens
**after** the concession check and **before** the structural refusal, and
any structural or concession refusal names the recorded round's id. A write
failure (`DECLARATIONS_HAND_EDITED`) wins over any pending refusal. A
regressed concession (see below) is never recorded.

#### Scenario: A round that scores nonzero is still recorded

- GIVEN the worked-example round 1, scoring 4
- WHEN `separate` runs and refuses on structure
- THEN the round is recorded before the refusal, and its id is named in the
  refusal detail

#### Scenario: Round two is checkable with no process state

- GIVEN round 1 recorded by one CLI invocation that has since exited
- WHEN a second, independent CLI invocation submits round 2 conceding to
  round 1
- THEN it reads round 1's record from disk alone and scores the concession
  correctly

#### Scenario: A byte-identical resubmission records nothing new

- GIVEN a round already recorded
- WHEN the identical cut, canonicalized, is submitted again
- THEN no new round is recorded, and the existing round's outcome is
  returned or re-refused unchanged

#### Scenario: A regressed concession leaves no new record

- GIVEN a concession that scores worse than the round it abandons
- WHEN `separate` refuses `SEPARATION_CONCESSION_REGRESSED`
- THEN no round is recorded for that submission, and resubmitting it
  identically refuses the same way with no growth in round count

### Requirement: A Concession Is Verified By Recomputing Both Cuts From Disk, Before The Structural Refusal

When the proposal names `concedes_to_round: n`, `separate` MUST recompute
**both** totals itself from disk — the conceding cut and round `n`'s
recorded assignments — never trusting either round's stored score. If `n`
names no recorded round for this `(root, lineage, revision)`, it MUST refuse
`SEPARATION_ROUND_ABSENT`. If the conceding cut's recomputed total strictly
exceeds round `n`'s recomputed total, it MUST refuse
`SEPARATION_CONCESSION_REGRESSED`, naming both cuts and both totals. An
**equal** total is not a regression and is accepted. The concession check
MUST run **before** the structural refusal, so that a conceding cut whose
recomputed total is still nonzero but not worse continues to the structural
refusal rather than being masked by a passed concession check.

#### Scenario: A concession that reaches zero is accepted

- GIVEN round 1 scoring 4 and a conceding cut scoring 0
- WHEN `separate` runs
- THEN it accepts the concession and exits 0

#### Scenario: A concession that scores worse refuses, naming both totals

- GIVEN round 1 scoring 4 and a conceding cut scoring 5
- WHEN `separate` runs
- THEN it refuses `SEPARATION_CONCESSION_REGRESSED` naming both cuts and
  the totals 4 and 5

#### Scenario: An equal total is accepted, not a regression

- GIVEN round 1 scoring 4 and a conceding cut also scoring 4
- WHEN `separate` runs
- THEN the concession check accepts the tie, and the structural refusal
  still fires next because the total is nonzero

#### Scenario: Conceding to a nonexistent round refuses

- GIVEN a proposal naming `concedes_to_round: 7` with no round 7 recorded
  for this `(root, lineage, revision)`
- WHEN `separate` runs
- THEN it refuses `SEPARATION_ROUND_ABSENT` naming the missing round

#### Scenario: Mutation — a tampered stored score does not change the refusal

- GIVEN round 1's recorded score field overwritten on disk to `0`, its
  recorded `assignments` unchanged
- WHEN a conceding cut scoring 5 is submitted against it
- THEN `separate` recomputes round 1's total from its `assignments` as 4 and
  still refuses `SEPARATION_CONCESSION_REGRESSED` naming 4 and 5

### Requirement: The Verb Never Records A Binding, Under Any Outcome

`separate` MUST write only `separation`-kind records: the set of
`declarations`-region record kinds reachable from its command path MUST be
exactly `{"separation"}`. A settled cut (total 0) MUST exit 0 with a payload
naming the exact `bind` invocation for every assignment; it MUST NOT record
any of them. `write` MUST continue to refuse `SECTION_BINDING_ABSENT` after
a settlement until an operator runs `bind`.

#### Scenario: A settled cut names the bind invocations, and records none of them

- GIVEN a cut scoring 0
- WHEN `separate` runs
- THEN it exits 0, its payload names one `bind` invocation per assignment,
  and no `binding` record exists afterward

#### Scenario: `write` still refuses after a settlement

- GIVEN a settled separation with no `bind` yet run
- WHEN `write` assembles the corpus for a block in that separation
- THEN it refuses `SECTION_BINDING_ABSENT` exactly as it does with no
  separation at all

#### Scenario: Mutation — relabeling the round's record kind is caught

- GIVEN the round writer mutated to persist `kind="binding"` instead of
  `kind="separation"`
- WHEN the settled-separation-then-write end-to-end test runs
- THEN it goes red, because `write` now finds a binding `separate` never
  should have created

### Requirement: This CLI Never Invokes An Agent

`separate`, like every verb in this CLI, MUST NOT import or call
`subprocess`. Every refusal payload MUST name the exact next command an
operator or agent should run.

#### Scenario: No subprocess call exists in the separation path

- GIVEN the module implementing `separate`
- WHEN a static scan checks for `subprocess` imports
- THEN none is found

#### Scenario: A refusal names the next action

- GIVEN any `SEPARATION_*` refusal
- WHEN it is raised
- THEN its detail includes the exact next invocation that would answer it

### Requirement: The Negotiation Carries No Authorship Field

The proposal shape carries no field naming who authored it, and `separate`
MUST score every proposal by the identical arithmetic regardless of origin.
`concedes_to_round` states which round is abandoned, never who is conceding
to whom.

#### Scenario: Two proposals score identically regardless of origin

- GIVEN one proposal representing an agent's cut and another representing
  an owner's counter-proposal, structurally identical
- WHEN each is scored
- THEN both produce the identical total by the identical computation

#### Scenario: An authorship-like key refuses like any other unknown key

- GIVEN a proposal carrying an extra key intended to assert who wrote it
- WHEN `separate` reads the file
- THEN it refuses `SEPARATION_REPORT_UNREADABLE` naming the unknown key,
  with no special handling for its intent
