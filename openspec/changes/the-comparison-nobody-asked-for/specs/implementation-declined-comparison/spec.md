# implementation-declined-comparison Specification

## Purpose

When the second flow proposes a comparison and the person answers "not now",
that answer MUST be remembered: the same offer MUST NOT re-fire on every
pass while nothing has changed, and it MUST re-fire by itself the moment the
situation that was declined stops being the situation on offer. This
capability covers the stable question text keyed on sorted baseline names,
the settled-decline outcome, the reported decline date, last-event-wins
reopening, the stability rule, and the one expected re-fire this change's
own baseline-finder fix causes on landing.

A declined comparison is also not a dead end — and the follow-up is
precisely neither of the two things it could be mistaken for. The target's
own apparatus already runs the method against a rival to decide which wins;
the follow-up offers that identical apparatus with a single arm: the method
alone, on real data, at small scale, judged against the prediction,
statistical unit, metric, and direction already declared in `premises`, for
the document already declared in `revision` — the proposal's own acid test,
run without a rival. It is **not** more verification (the invariant tests
already prove the formulas in the abstract, with no data) and it is **not**
a comparison (there is no rival arm, and no winner is decided). `premises`
gives the yardstick's *form* — unit, metric, direction — but not its
*calibration*: with no rival to be better than, the reference figure is the
one the declared document itself reports, so the offer's draft asks the
person for that figure and names which `revision` to read it from, rather
than the engine ever parsing a number out of prose.

Once the comparison is declined, the flow MUST NOT terminate while the
acid-test decision remains open — it reports the acid-test offer as the
next question. Only once both decisions are settled does the flow report a
fully terminal outcome, each recorded the same persistence-and-stability way
the comparison decline itself is. Accepting either offer opens a discussion
carried out entirely inside this same skill and session — no bridge to
another skill. Accepting the acid test specifically MUST NEVER create the
benchmark package or run the harness stage: a single-arm run is not a
comparison, and naming it one would reintroduce this change's own defect
wearing the opposite mask.

**Budget note.** This spec exceeds 650 words for the same reason as its
sibling `implementation-comparison-deferral`: the owner's directive requires
full coverage and no regression, and the migration-adjacent one-time re-fire
must be specified as correct behaviour or it will be mistaken for a defect
the first time anyone observes it. The acid-test follow-up adds two
non-negotiable requirements of its own — nothing may materialize before an
offer is accepted, and even once accepted, nothing benchmark-named may ever
be created — for the identical reason this whole change exists.

## Requirements

### Requirement: A Declined Comparison Is Persisted As A Bare Discuss Event

A decline MUST be persisted as a `discuss` ledger event — no `settle` entry,
no `AGREED.md` checkbox, no Results artifact, and no new ledger event kind.
Declining alone MUST NOT create any comparison machinery. Declining the
comparison, by itself, MUST NOT be reported as a fully terminal outcome:
the flow's next reported step MUST be the acid-test offer, specified in full
by the requirements below. A fully terminal outcome — nothing further
published — is reported only once the acid-test decision is settled too
(see "Declining The Comparison Opens The Acid-Test Offer" below).

#### Scenario: Declining records a discuss event and nothing else
- GIVEN the second flow offers a comparison and the person answers "not now"
- WHEN the answer is persisted
- THEN a `discuss` event is recorded, no `AGREED.md` entry is written, and no
  Results artifact is created

#### Scenario: Probe reports the acid-test offer, not a bare terminal outcome
- GIVEN the discuss event above exists, nothing else has changed, and the
  acid-test decision has never been asked
- WHEN `probe` runs again
- THEN it reports the acid-test offer as the next step, and builds no
  comparison machinery

### Requirement: The Decline Question Text Is Constructed In Exactly One Place, Keyed On Sorted Baseline Names

The question-text constructor MUST embed the target, the method name, and
the **sorted** baseline names — the exact output of `previous_implementations()`
at the moment of asking — and MUST NEVER embed a count of them. Exactly one
call site in the codebase MUST construct this text.

#### Scenario: Different baseline sets produce different question text
- GIVEN two targets with different sets of prior work on disk
- WHEN the decline question is constructed for each
- THEN the two question texts differ

#### Scenario: The question text never contains a bare count
- GIVEN any target with baseline names
- WHEN the question text is constructed
- THEN it contains the sorted names themselves, and no numeral standing in
  for how many there are

#### Scenario: A single construction site is enforced
- GIVEN the codebase after this change
- WHEN a test enumerates callers that build this exact question text
- THEN exactly one call site is found

### Requirement: The Offer Re-Fires Exactly When The Baseline Name Set Materially Changes

Once a comparison is declined, the offer MUST re-fire only when the sorted
set of baseline names changes — new prior work appearing, or existing prior
work disappearing. It MUST NOT re-fire because of re-running the test suite,
editing the method's own modules, or re-rendering a report.

#### Scenario: New prior work re-fires the offer
- GIVEN a decline recorded against a given baseline name set
- WHEN a new baseline package appears on disk, changing that set
- THEN the offer re-fires: the new question text is unanswered, and probe
  reports it rather than the settled decline

#### Scenario: Removed prior work re-fires the offer
- GIVEN the same decline, with the baseline set instead losing a member
- WHEN probe evaluates the new, smaller set
- THEN the offer re-fires for the same reason: the question text changed

#### Scenario: Re-running the suite leaves the decision settled
- GIVEN the same decline and an unchanged baseline set
- WHEN the test suite is re-run
- THEN the comparison decision is still reported as settled-declined; the
  offer does not re-fire

#### Scenario: Editing method modules leaves the decision settled
- GIVEN the same decline and an unchanged baseline set
- WHEN a method module is edited
- THEN the comparison decision is still reported as settled-declined

#### Scenario: Re-rendering a report leaves the decision settled
- GIVEN the same decline and an unchanged baseline set
- WHEN a report is re-rendered
- THEN the comparison decision is still reported as settled-declined

### Requirement: The Declined Report Names The Decline Date, Read From The Ledger Event

The declined report MUST name the date the comparison was declined, read
from the bucket/ledger event's own `at` field — never transcribed by hand
and never supplied by `_answered_discussions`, which returns question text
only and cannot carry a date.

#### Scenario: The reported date matches the ledger event
- GIVEN a discuss event recording a decline with a given `at` value
- WHEN the declined report is produced
- THEN the date shown matches that event's `at` field exactly

#### Scenario: A stale report is distinguishable from a fresh one
- GIVEN a decline recorded weeks ago and no material change since
- WHEN the declined report is produced today
- THEN it names the original decline date, not today's date

### Requirement: Ledger Append Order Decides Ties; The Decline Date Is Display-Only, Never An Ordering Key

`at` is second-granularity and can tie between two events on the same
question text. `_discussion_buckets` MUST decide which event is authoritative
by ledger append order, never by comparing `at` values. The decline date
shown in a report MUST remain purely informational and MUST NOT be used to
decide which of two same-second events wins.

#### Scenario: Two same-second events on identical text resolve by append order
- GIVEN two discuss events on the exact same question text, recorded within
  the same second, with different answers
- WHEN the bucket is resolved
- THEN the event that was appended later to the ledger is authoritative,
  regardless of any `at`-value comparison

#### Scenario: The displayed date does not change which answer is authoritative
- GIVEN the tie above
- WHEN the declined (or accepted) report is produced
- THEN the authoritative answer is the later-appended one, and the date shown
  is informational only — swapping which same-second event carries the
  earlier or later `at` value does not change the outcome

### Requirement: Answering The Same Question Again Reopens The Comparison With No Separate Reopening Step

Re-running `discuss` on the identical question text with an accepting answer
MUST make the comparison live again, proceeding exactly as if it had been
accepted the first time. No dedicated reopening code path is introduced.

#### Scenario: A changed answer flips the bucket
- GIVEN a prior decline recorded against a stable question text
- WHEN the identical question text is answered again with acceptance
- THEN the bucket's last event wins, and probe proceeds toward the
  comparison as though it had never been declined

### Requirement: The Baseline-Finder Fix Causes Exactly One Expected Re-Fire On Landing, Not A Defect

A target that declined a comparison **before** this change lands has a
recorded bucket key built from the pre-fix baseline name set — one that
still includes the target's own `_Benchmark`-suffixed package as if it were
a baseline. After the `_Benchmark`-suffix exclusion lands (in the same
commit as this capability's question-text constructor), the corrected sorted
name set differs from the recorded one. This is a different key, so the
offer MUST re-fire exactly once on the first pass after the change lands.
This is correct behaviour under the stability rule above — the comparison
described by the corrected question is genuinely not the comparison that was
declined — and MUST NOT be treated, reported, or remediated as a defect.

#### Scenario: A pre-change decline re-fires once after landing
- GIVEN a target with a decline recorded before this change, whose bucket key
  embeds the pre-fix baseline set including its own benchmark package
- WHEN probe runs for the first time after this change lands
- THEN it reports the offer as unanswered, not as the settled decline,
  because the corrected sorted name set produces a different question text

#### Scenario: Answering the re-fired offer restores stability
- GIVEN the one-time re-fire above
- WHEN the person answers the re-fired question, either way
- THEN subsequent passes with no further material change report that same
  settled answer, with no second re-fire caused by the same migration event

### Requirement: Declining The Comparison Opens The Acid-Test Offer, Rather Than Ending The Flow

Once the comparison is declined, the flow MUST NOT report a fully terminal
outcome while the acid-test decision remains open. It MUST publish a
question asking whether to run the proposal's acid test — the method
alone, without the rival, on real data, at small scale — judged against
the prediction, statistical unit,
metric, and direction already declared in `premises`. This is the target's
own two-arm apparatus with a single arm; it is neither more verification
(the invariant tests already prove the formulas in the abstract, with no
data) nor a comparison (there is no rival arm, and no winner is decided). A
draft describing how that single-arm run would be carried out MUST be
published beside the question — the same shape the comparison offer itself
uses (`_benchmark_publication`): a published question, a draft beside it,
and the decision left open rather than offered as an enumerated menu. A
single-arm run on real data spends machine time and declares a scale —
this skill's own definition of an experiment — so the question MUST close
with the same standing choice every other experiment-kind offer closes with
(`NEXT_STEP_EXPERIMENT_CHOICE`), not a new spelling of it.

#### Scenario: A fresh decline publishes the acid-test offer, not a bare statement
- GIVEN a comparison was just declined and the acid-test question has never
  been asked
- WHEN `probe` runs
- THEN it publishes the acid-test question and a draft of how the
  single-arm run would be carried out, rather than a flat statement with
  nothing published

#### Scenario: The offer names a single arm, not a second comparison or more proof
- GIVEN the acid-test offer is published
- WHEN its text is inspected
- THEN it names the method alone, on real data, at small scale, judged
  against `premises`' declared prediction — with no rival arm named and no
  language about how much of the proposal is already proved

#### Scenario: The offer is a question, not a menu
- GIVEN the acid-test offer is published
- WHEN its payload is inspected
- THEN the decision is an open question in prose, not an enumerated
  pick-list of choices

#### Scenario: The offer closes with the standing experiment choice
- GIVEN the acid-test offer's published text
- WHEN it is inspected
- THEN it ends with the identical `NEXT_STEP_EXPERIMENT_CHOICE` text every
  other experiment-kind offer ends with

### Requirement: A Stable Question-Text Constructor Decides The Acid-Test Offer, One Spelling, One Bucket

Exactly one constructor MUST produce the acid-test question's text, in the
same family as `_pilot_decision_question` and `_report_findings_question` —
the string IS the bucket key, so a second spelling anywhere opens a second,
never-retiring bucket. Its derivation MUST use the target, the method's
name, the declared `revision`, and a **canonical rendering** of the declared
`premises` mapping: every key currently present in `premises`, rendered in
sorted order, naming none, requiring none, and dropping none. This
rendering MUST NOT parse, require, or refuse on any specific key `premises`
does or does not carry — it is a total projection of whatever mapping is
there, never a validator, and it MUST NOT reopen the standing ruling that
`premises` keeps no reader. Raw, unparsed source bytes MUST NOT be embedded:
the declaration is already parsed into a value by the time any reader
reaches it, and re-slicing the file's own text a second way would be a
second spelling of "read the declaration" — the exact duplication this
capability's declaration reader exists to prevent. A changed `revision` or a
changed `premises` content is what makes a previously-declined acid test
genuinely a different acid test; the constructor MUST NOT embed any
measured, achieved, or countable value that could shift on its own while
neither has changed.

#### Scenario: The same declared state always produces the same question text
- GIVEN the same target, method name, `revision`, and `premises` content,
  asked on two different passes
- WHEN the acid-test question is constructed both times
- THEN the text is identical

#### Scenario: Cosmetic edits to the declaration's own source do not move the key
- GIVEN `premises` is re-indented, its quote style is changed, a long line is
  reflowed, or a trailing comma is added or removed, with no change to any
  key or value
- WHEN the acid-test question is constructed before and after
- THEN the text is identical, because only the parsed, sorted value is
  embedded, never the source bytes

#### Scenario: The canonical rendering names no key and refuses nothing
- GIVEN a `premises` mapping carrying unexpected keys, missing the four the
  kit's own comment suggests, or bound to a value that is not a mapping at
  all
- WHEN the acid-test question is constructed
- THEN a rendering is produced in every case; none of these shapes is
  refused, and none is treated as more or less valid than another

#### Scenario: A single construction site is enforced
- GIVEN the codebase after this change
- WHEN a test enumerates callers that build this exact question text
- THEN exactly one call site is found

### Requirement: The Acid-Test Offer Re-Fires Exactly When The Declared Revision Or The Declared Criterion Changes

A declined acid-test answer MUST be persisted the same way the comparison
decline itself is persisted — a bare `discuss` event, last-event-wins. The
offer MUST re-fire only when `revision` is edited to name a different
document, or `premises`' declared content changes to a different criterion.
It MUST NOT re-fire because of re-running the test suite, editing method
modules that leave the declaration untouched, re-rendering a report,
cosmetic edits to the declaration's own source formatting that leave its
parsed value unchanged, or the comparison offer separately changing state.

#### Scenario: A declined acid test stays settled
- GIVEN the acid-test offer was declined and neither `revision` nor
  `premises` has changed
- WHEN `probe` runs again
- THEN it reports the acid test as settled-declined, not as a re-asked
  question

#### Scenario: Editing the declared revision re-fires the offer
- GIVEN the acid-test offer was declined against a given `revision`
- WHEN `revision` is edited to name a different document
- THEN the offer re-fires: the new question text is unanswered, and probe
  reports it rather than the settled decline

#### Scenario: Editing the declared criterion re-fires the offer
- GIVEN the acid-test offer was declined against given `premises` content
- WHEN `premises` is edited to a different criterion
- THEN the offer re-fires: the new question text is unanswered, and probe
  reports it rather than the settled decline

#### Scenario: Unrelated activity does not re-open it
- GIVEN the same declined acid test, with `revision` and `premises`
  unchanged
- WHEN the suite is re-run, a method module unrelated to the declaration is
  edited, the declaration's own source is reformatted with no value change,
  or a report is re-rendered
- THEN the acid-test decision remains settled

#### Scenario: A stable key persists across a re-fire-and-redecline of the comparison itself
- GIVEN an acid test was declined, the comparison later re-fires because its
  own baseline set changed, and the comparison is declined again, with
  `revision` and `premises` unchanged throughout
- WHEN the acid-test offer is reached again
- THEN the question text is identical to before (derived from `revision`
  and `premises`, not from the comparison's baseline set), so the prior
  acid-test answer applies again without a fresh question being asked — the
  same one-spelling discipline that governs every other constructor in this
  family

### Requirement: The Acid Test Is Judged By A Yardstick Whose Form Is Declared And Whose Calibration Is Asked

`premises` gives the prediction's statistical unit, metric, and direction —
the yardstick's form — but not a threshold, and with a single arm there is
no rival to be better than. The reference figure MUST be asked from the
person, never parsed by the engine out of any document's prose, and the
question MUST name which declared `revision` the person should read that
figure from.

#### Scenario: The draft asks for the reference figure and names its source
- GIVEN the acid-test offer's published draft
- WHEN it is inspected
- THEN it asks the person for the reference figure and names the `revision`
  it should be read from, rather than stating a number itself

#### Scenario: The engine never extracts a number from prose
- GIVEN any document text associated with the declared `revision`
- WHEN the acid-test offer or its draft is constructed
- THEN no figure is parsed out of that prose; the reference figure is
  supplied only by the person, in response to being asked

### Requirement: An Accepted Acid Test Writes Only Into The Method's Own Surfaces, Never Into Benchmark-Named Structure

Accepting the acid test MUST NEVER create `src/<Package>_Benchmark/` and
MUST NEVER write any destination belonging to the harness stage — not the
benchmark declaration, not its entry module, not its verdict module, not
its harness notebook. A single-arm run of the method against its own
declared prediction is not a benchmark, and naming it one would reintroduce
this change's own defect wearing the opposite mask. What an accepted acid
test MAY write to is exactly: the method's own package declaration (a flow,
record, or scale entry describing the run), the method's own modules, its
own tests, its own notebooks, and a record under the product folder at a
path that does not borrow the comparison's name. Every other existing
package under `src/` is read-only to it.

#### Scenario: No benchmark package exists after an accepted, wired, and run acid test
- GIVEN the acid test is accepted, wired, and run
- WHEN `src/` is inspected afterward
- THEN no `<Package>_Benchmark` directory exists anywhere under it

#### Scenario: No harness destination is written
- GIVEN the same accepted, wired, and run acid test
- WHEN the harness destination list is checked against what was written
- THEN none of it was written by the acid test, and the harness stage's own
  gap count is unchanged by the acid test's activity

#### Scenario: The record's path does not borrow the comparison's name
- GIVEN the acid test's own record entry
- WHEN its path is inspected
- THEN it lives under the product folder without naming or nesting under
  anything that reads as the comparison package

### Requirement: Guidance Offered While Wiring An Acid Test Names The Method's Own Package, Never The Benchmark Package

Any example or guidance shown to a person wiring an acid test — for where
its own flow-declaration entry points, and for where its own record lands —
MUST name the method's own package and a path that does not borrow the
comparison's name. Guidance that models these after the comparison package
would teach exactly the habit the structural prohibition above forbids.

#### Scenario: Flow-declaration guidance names the method's own package
- GIVEN guidance or an example shown while wiring an acid test's own
  flow-declaration entry
- WHEN its example module path is inspected
- THEN it names the method's own package, never a `_Benchmark`-suffixed one

#### Scenario: Record-path guidance does not borrow the comparison's name
- GIVEN guidance or an example shown for where the acid test's record lands
- WHEN its example path is inspected
- THEN it does not read as naming or nesting under the comparison

### Requirement: An Accepted Acid Test Is Discussed Entirely Within This Skill And Session

Answering "yes" to the acid-test offer MUST lead the single-arm run to be
discussed inside this same skill and this same session, using the discuss/
agreement machinery this skill already uses for its other offers. The system
MUST NOT direct the person to another skill, and MUST NOT introduce a
dependency on one. What gets agreed is settled through the same agreement
mechanism this skill already uses to settle other accepted experiment-kind
offers — no new agreement mechanism is introduced.

#### Scenario: Acceptance stays inside this skill
- GIVEN the person answers "yes" to the acid-test offer
- WHEN the single-arm run is discussed
- THEN every command and artifact involved belongs to this skill; no output
  names another skill as the place to continue

#### Scenario: Agreement uses the existing mechanism
- GIVEN a specific acid-test run is agreed
- WHEN that agreement is recorded
- THEN it is recorded through the same mechanism this skill already uses to
  settle other accepted experiment-kind offers

### Requirement: The Acid Test Materializes Nothing Up Front

Neither asking the acid-test question nor the person agreeing to discuss it
MUST create any file, script, or notebook the single-arm run would need.
Whatever it needs MUST appear only once a specific run is agreed — exactly
the discipline this whole change exists to establish for the comparison
offer itself; specifying it otherwise here would reintroduce the defect
this change removes, one rung later.

#### Scenario: Asking the question creates nothing
- GIVEN the acid-test offer has just been published
- WHEN `src/` is inspected
- THEN nothing has been added beyond what already existed

#### Scenario: Agreeing to discuss creates nothing yet
- GIVEN the person has answered "yes" and the discussion has begun, with no
  specific run agreed yet
- WHEN `src/` is inspected
- THEN nothing has been added

#### Scenario: Only agreement on a specific run materializes anything
- GIVEN a specific acid-test run has just been agreed
- WHEN materialization runs
- THEN only then does whatever that specific run needs appear

### Requirement: Introducing The Acid-Test Follow-Up Does Not Reorder Or Shadow Any Other Ladder State

Adding the acid-test offer to the ladder — and deferring a fully terminal
outcome until both the comparison and the acid-test decisions are settled —
MUST NOT change the position, precondition, or output of
`nothing-to-compare`, `already-benchmarked`, `benchmark`, or any other
pre-existing `PROBE_NEXT_STEPS` entry that predates this change. A genuinely
owed repair (for example, a step the target's own declared flow has not yet
finished) MUST continue to outrank a declined-but-unresolved comparison —
the follow-up MUST NOT hide work the flow already agreed to.

#### Scenario: Existing states are unaffected by the acid-test follow-up
- GIVEN `PROBE_NEXT_STEPS` after the acid-test follow-up is added
- WHEN `nothing-to-compare`, `already-benchmarked`, and `benchmark` are each
  exercised under their own precondition
- THEN each fires exactly as before, unaffected by the new behaviour

#### Scenario: A genuinely owed repair still outranks the acid-test offer
- GIVEN a target whose comparison was declined and whose own declared flow
  still owes an unfinished step
- WHEN `probe` runs
- THEN it reports the owed repair, not the acid-test offer
