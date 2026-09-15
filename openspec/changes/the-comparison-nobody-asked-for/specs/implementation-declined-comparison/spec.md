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

The acid test is a real run on real data and spends machine time, exactly
like the comparison — so, like the comparison, it MUST be able to go to a
remote worker, and the offer MUST say so rather than leave that reachable
only by accident. Where it runs is decided in its own dedicated section of
the draft, deciding neither option, and the offer states what each option
costs without ever inventing a number the forge cannot know.

**A decision already taken can change, and the flow has to see it.** Two
gaps in the lifecycle this capability governs are closed here. First: today,
a person who accepts a decision but has not yet built it is left reporting
a settled decline forever — the flow re-offers only when the situation
materially changes, never when the person simply changes their mind before
building anything. Answering again, through a closed token, MUST reopen the
decision on the strength of that answer alone. Second: once an acid test
and a comparison can each exist on their own, a person may want to move
from one to the other. That transition is asymmetric — adding a rival arm
is not the same operation as recognizing that a rival-inclusive run already
measured what a single-arm run would have asked — and in neither direction
does it delete anything a run already produced.

**Budget note.** This spec exceeds 650 words for the same reason as its
sibling `implementation-comparison-deferral`: the owner's directive requires
full coverage and no regression, and the migration-adjacent one-time re-fire
must be specified as correct behaviour or it will be mistaken for a defect
the first time anyone observes it. The acid-test follow-up adds three
non-negotiable requirements of its own — nothing may materialize before an
offer is accepted, nothing benchmark-named may ever be created even once
accepted, and that prohibition must hold across both placements it may now
run under. The reopening and transition requirements add a fourth: no
completed run's evidence may ever be deleted merely because the question
being asked of the target changed — for the identical reason this whole
change exists.

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

### Requirement: A Declined Decision Reopens On Its Own Answer Alone, Never On Waiting For Structure To Exist

Either standing decision — the comparison's or the acid test's — MAY be
changed after a decline by answering it again through a **closed `yes`/`no`
token**, never free text: the same discipline this codebase already applies
elsewhere (a closed binary answer, refused as an unrecognized token when it
is anything else). Answering `yes` MUST reopen the decision by the strength
of that answer alone — it MUST NOT continue to be reported as declined
merely because the corresponding structure (the benchmark package, or the
wired acid test) has not yet been built. Answering `no` again MUST leave it
declined. No dedicated reopening code path is introduced beyond reading the
answer.

#### Scenario: Accepting reopens the decision before anything is built
- GIVEN a prior decline recorded against either standing decision
- WHEN that same decision is answered `yes` again
- THEN the flow reports it as accepted immediately, with nothing yet built

#### Scenario: An accepted-but-unbuilt decision is never reported as declined
- GIVEN the decision above was answered `yes` and nothing has been built
- WHEN `probe` runs
- THEN it does not report that decision as declined; the reported decision
  state reflects the acceptance, not silence about the contradiction

#### Scenario: Declining again leaves it declined
- GIVEN the same decision
- WHEN it is answered `no` again
- THEN it remains declined

#### Scenario: An answer outside the closed domain is refused, never interpreted
- GIVEN an attempt to change either decision with anything other than the
  two closed tokens
- WHEN it is submitted
- THEN the engine refuses it as an unrecognized token; it never attempts to
  interpret the text's meaning

### Requirement: A Repair Whose Own Precondition Reads The Benchmark Declaration Does Not Preempt An Unoffered Comparison

Any repair override whose own precondition reads the benchmark declaration
MUST exclude a target whose declaration is entirely absent when that target
has never even been offered a comparison. The three-way
comparison/acid-test/settled branch MUST be evaluated after every other
repair override, so that a genuinely owed repair always outranks an
unresolved or settled decision — and, symmetrically, a target that has never
been offered a comparison is never mistaken for one whose report disagrees
with a run that was never made.

#### Scenario: A never-offered target reports the comparison offer, not a report-reading repair
- GIVEN a target whose benchmark declaration is entirely absent and which
  has never been offered a comparison
- WHEN `probe` runs
- THEN it reports the comparison offer; it does not report a repair whose
  own precondition assumes a report exists to disagree with a run

#### Scenario: The three-way branch is evaluated last among the overrides
- GIVEN a target with both an owed repair and an unresolved or settled
  comparison decision
- WHEN `probe` runs
- THEN the owed repair is reported first; the comparison/acid-test/settled
  branch is reached only once every other repair override's own
  precondition is false

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

### Requirement: The Acid-Test Draft Names Placement As Its Own Section, Deciding Neither Option

Where the acid test runs MUST be its own draft section — never folded into
the scale section, and never buried inside a question the draft asks
without a section of its own. It MUST name `local` and `remote` with the
consequence of each, and MUST decide neither: a run whose placement is
undeclared cannot be routed once the flow leaves rehearsal scale, so a
default here would be exactly the choice the walk already refuses to make
silently. Placement and scale are independent declarations answering
different questions — scale answers how big, placement answers where — and
MUST NOT be conflated on the strength of a coincidence: one repository's own
declared rung ladder happens to spell a scale point `"remote"`, and that
target-authored word names a scale, never a placement.

#### Scenario: The draft names both placements without choosing
- GIVEN the acid-test offer's published draft
- WHEN its placement section is inspected
- THEN both `local` and `remote` are named, each with its own consequence,
  and neither is selected

#### Scenario: An undeclared placement is never defaulted
- GIVEN the acid-test draft as accepted and wired
- WHEN its `placement` entry is inspected
- THEN it carries exactly what the person chose; a test that would go red on
  a silently-introduced default catches one if added

#### Scenario: A target's own scale-rung name does not read as a placement
- GIVEN a target whose own declared rung ladder happens to name a rung
  `"remote"`
- WHEN the acid-test draft's placement section and scale section are
  compared
- THEN the two remain distinct: the rung name is read only as a point on
  the scale, never as a placement decision

### Requirement: The Acid-Test Draft Proposes The Job Name And Asks For The Service, Never Guessing Either

Within the placement section, the draft MUST propose a job name — derived
mechanically from the step's own name, costing the person nothing to accept
— because a remote step whose job names nothing cannot be routed either.
The draft MUST NOT propose or guess a service: it MUST be asked of the
person, because the engine may not name a service it has not been told
(reducing any known service to a count is the extent of what it may do with
one) and cannot discover one either. Any accelerator, environment, or budget
knob the remote path accepts MUST be named as available and answered by the
person, never chosen by the draft.

#### Scenario: A job name is proposed, not left for the person to invent
- GIVEN the acid-test draft's placement section
- WHEN it is inspected
- THEN a job name derived from the step's own name is already proposed

#### Scenario: The service is asked, never guessed
- GIVEN the same section
- WHEN it is inspected
- THEN no service name is proposed or invented; the person is asked to
  supply one

#### Scenario: Remote knobs are named as available, not pre-selected
- GIVEN a remote placement's accelerator, environment, or budget knobs
- WHEN the draft is inspected
- THEN they are listed as available for the person to answer, and none is
  pre-selected by the draft

### Requirement: The Acid-Test Offer States Cost's Shape, Never Its Magnitude

The offer MUST state, in its published question: that the acid test is a
real run on real data and spends machine time — the fact separating it from
the invariant tests, which spend none; that a local run occupies the
machine for its duration; that a remote run spends metered quota on a
service account; that the scale on offer is the small one named in the
draft's scale section, and accepting it is not accepting a larger campaign,
which is a different decision; and that declining later costs nothing to
unwind, because no comparison-named structure was ever created. The offer
MUST carry the proposed scale's axes, derived from the declaration. It MUST
NOT state a duration, a quota figure, or a service name: the engine cannot
know how long a run takes or what quota it costs, and this repository has
already lived through the failure of a forge-invented figure — a weekly
quota number that once lived in a comment nothing read and did not match
reality. A number the offer invented would be that same defect with a fresh
timestamp.

#### Scenario: The offer states each placement's cost
- GIVEN the acid-test offer's published question
- WHEN it is inspected
- THEN it names machine-time spending, local's machine occupancy, and
  remote's metered-quota cost

#### Scenario: Accepting the small scale is distinguished from accepting a campaign
- GIVEN the same offer
- WHEN it is inspected
- THEN it states that the scale offered is the small one, and that a larger
  run is a separate decision

#### Scenario: The offer never states a number it cannot know
- GIVEN the same offer
- WHEN it is inspected
- THEN it contains no duration, no quota figure, and no service name — only
  the proposed scale's own declared axes

### Requirement: An Empty Declared Rung Ladder Does Not Constrain Placement

An empty `__levels__` and the placement decision are independent. An empty
ladder means the scale is asked for directly and the walk grades the step
walked/not-walked rather than by rung — a reporting difference, not a
capability one. It MUST NOT be read, stated, or implemented as ruling out a
remote placement.

#### Scenario: Remote placement is available with an empty rung ladder
- GIVEN a target whose `__levels__` is empty
- WHEN an acid-test step declares `placement: "remote"`
- THEN it routes exactly as it would with a populated ladder; only the
  grading changes, from by-rung to walked/not-walked

#### Scenario: The draft's placement section says so explicitly
- GIVEN the same empty-ladder target
- WHEN the acid-test draft's placement section is inspected
- THEN it does not read, or let a reader infer, that the empty ladder rules
  out a worker

### Requirement: A Remote Acid-Test Step Reaches A Worker Through The Existing, Unmodified Remote-Execution Path

An acid-test step declaring `placement: "remote"` MUST route through the
same generic step-routing machinery every other declared step already uses,
reaching a generated job folder with no acid-test-specific branch anywhere
in that path. The check that validates a job folder's declared clone paths
against what its entry modules actually import MUST adapt to a single arm's
smaller import surface using the identical check every other step uses,
with no special-cased branch for a single arm. This is a testable, provable
claim, not an assertion of compatibility to be taken on faith.

#### Scenario: A remote acid-test step generates a job folder identically to a comparison step
- GIVEN an acid-test step declaring `placement: "remote"`, a `job`, and a
  `service`
- WHEN it is walked
- THEN it reaches the same generate/rehearse/launch progression a
  comparison step reaches, through machinery this change leaves unmodified

#### Scenario: The clone-path check needs no single-arm branch
- GIVEN the acid test's single arm imports fewer packages than a two-arm
  comparison would
- WHEN its declared clone paths are validated against its entry modules'
  actual imports
- THEN the same check that validates any other step's clone paths applies,
  with no separate code path written for a single arm

#### Scenario: The remote run carries the notebook already chosen, not a second implementation
- GIVEN a remote acid-test job folder
- WHEN it is generated
- THEN it carries the notebook already chosen for this run, never a
  second, remote-only implementation of it

### Requirement: An Accepted Acid Test Writes Only Into The Method's Own Surfaces, Never Into Benchmark-Named Structure

Accepting the acid test MUST NEVER create `src/<Package>_Benchmark/` and
MUST NEVER write any destination belonging to the harness stage — not the
benchmark declaration, not its entry module, not its verdict module, not
its harness notebook. A single-arm run of the method against its own
declared prediction is not a benchmark, and naming it one would reintroduce
this change's own defect wearing the opposite mask. What an accepted acid
test MAY write to is exactly: the method's own package declaration (a flow,
record, or scale entry describing the run), the method's own modules, its
own tests, its own notebooks, a record under the product folder at a path
that does not borrow the comparison's name, and — when placement is
remote — a job folder under this repository's own remote-execution output
root, which is not a member of any materialization stage list and cannot
reach the harness destinations even in principle. Every other existing
package under `src/` is read-only to it. **This prohibition MUST hold
identically whether placement is local or remote** — a remote job folder is
not a back door around it.

#### Scenario: No benchmark package exists after an accepted, wired, and run acid test, placed locally
- GIVEN the acid test is accepted, wired, and run with `placement: "local"`
- WHEN `src/` is inspected afterward
- THEN no `<Package>_Benchmark` directory exists anywhere under it

#### Scenario: No benchmark package exists after an accepted, wired, and run acid test, placed remotely
- GIVEN the acid test is accepted, wired, and run with `placement: "remote"`,
  generating its own job folder
- WHEN `src/` is inspected afterward
- THEN no `<Package>_Benchmark` directory exists anywhere under it

#### Scenario: No harness destination is written, placed locally
- GIVEN the same accepted, wired, and run acid test, placed locally
- WHEN the harness destination list is checked against what was written
- THEN none of it was written by the acid test, and the harness stage's own
  gap count is unchanged by the acid test's activity

#### Scenario: No harness destination is written, placed remotely
- GIVEN the same accepted, wired, and run acid test, placed remotely
- WHEN the harness destination list is checked against what was written,
  including the contents of its generated job folder
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

### Requirement: Adding A Comparison After An Acid Test Adds A Rival Arm; It Answers A Different Question, Not A Better One

When an acid test has already run and the person also wants a comparison,
the transition MUST be discussed, never automatic, the same discipline
every other gate in this lifecycle already uses. Building the comparison
MUST add a rival arm; it MUST NOT invalidate, overwrite, or require
re-running the acid test's own measurement. The acid test answered whether
the method does what the proposal said; the comparison answers a different
question — which of two arms wins. Gaining an answer to the second question
does not retract the answer already given to the first.

#### Scenario: Wanting a comparison after a run acid test is discussed, not automatic
- GIVEN a target whose acid test has already run
- WHEN the person also wants a comparison
- THEN the transition is discussed before anything is built

#### Scenario: The acid test's own record survives the addition of a rival
- GIVEN the acid test's own record already exists
- WHEN a comparison is subsequently built and run
- THEN the acid test's own record is neither deleted nor overwritten, and it
  continues to answer the question it was run to answer

### Requirement: Treating An Existing Comparison As Also Answering The Acid Test Removes Nothing And Reuses What Already Ran

When a comparison has already run and the person wants the acid test's own
question answered too, no new run is required: a comparison already runs
the method on the same data an acid test would use, so what the acid-test
question asks is already measured inside the comparison's own record. This
transition, too, MUST be discussed, never automatic, and it MUST NOT delete,
diminish, or remove the rival's own arm or its measurements — ceasing to ask
the comparison's question is not the same operation as erasing what the
comparison already measured.

#### Scenario: The acid-test question is answered from the existing comparison record
- GIVEN a target with an already-run comparison
- WHEN the acid-test question is asked afterward
- THEN it is answered from the comparison's own existing record, with no new
  run required

#### Scenario: The rival's arm is not removed by the transition
- GIVEN the same target
- WHEN this transition is discussed and completed
- THEN neither the rival's own arm nor its measurements are removed from
  disk or from the record

### Requirement: A Completed Run's Evidence Is Never Deleted When The Question Being Asked Changes

Ceasing to ask about something and erasing it are different operations, and
this capability MUST NOT conflate them. Neither transition above — test to
comparison, or comparison to test — MUST delete, relocate out of its
recorded location, or overwrite any record or arm's output a prior run
already produced. A transition MAY change which question the flow is
currently asking; it MUST NOT retract evidence that a run already happened
and was paid for in machine time.

#### Scenario: A rival's arm is never erased by a later transition
- GIVEN a comparison whose rival arm has already run
- WHEN the person later asks only about the acid test's own question
- THEN the rival's own recorded output remains exactly where it was,
  untouched

#### Scenario: An acid test's record is never erased by a later comparison
- GIVEN an acid test whose record already exists
- WHEN a comparison is subsequently built
- THEN the acid test's own record remains exactly where it was, untouched

## Boundary (explicitly not built here)

A remote run accepts environment-provisioning input — packages to install
before the run starts. Separately, at least one already-scaffolded target
carries its own top-level declaration of exactly that shape, unread by
anything in the forge (see `implementation-comparison-deferral`'s migration
requirement, which is what carries it forward rather than dropping it).
Wiring that declaration through as the remote path's environment input is
almost certainly what it was meant for, and this capability's remote
placement is where that wiring would eventually live. **It is not built
here.** Doing so would give a reader to a literal this change deliberately
leaves without one, which is its own decision and not a side effect of
adding remote placement. Named so the next person finds it rather than
rediscovering it.
