# Transposition Grounding Specification

## Purpose

A block whose contract declares `mode: transposition` must assert only what
its bound source section carries. Five judge stages already run inside
`write_block`, and the only one that reads a bound section's bytes —
`SOURCE_SECTION_VERBATIM` — is a **copying** measurement: it refuses a draft
that repeats too much of the section, and stays silent about a draft that
paraphrases freely while asserting something the section never states. The
further a draft drifts from the truth, the quieter that check gets.

This capability adds a fourth sibling, `paper_grounding`, that judges
**containment** instead of copying: a subject sentence — a `fact:`-bound
sentence in a transposition block whose fact also carries a bound section —
must be supported by that section's own bytes. An agent proposes a
per-sentence verdict; the guard re-derives both the sentences and the
sections itself and reconciles the account against them in both directions.
A verdict the guard cannot re-ground is never trusted.

**Ordering dependency, named rather than assumed.** This capability holds a
drafted sentence to a section's bytes on the presumption that the drafter
was actually shown that section. Applied before the redactor receives its
bound section, this guard would demand fidelity to bytes the drafter never
saw and would refuse a competent draft. The requirements below assume that
seam is already closed.

This checks containment, never correctness — whether the section itself is
true is out of scope, and so is copying, which stays `SOURCE_SECTION_VERBATIM`'s.

## Requirements

### Requirement: The Subject Set Is An Intersection Derived From Bytes, Never A List

A subject is a `fact:`-bound sentence segmented from the draft whose fact id
also names a section in the block's own bound sections. The guard MUST
derive this set as the intersection of two independently produced sets — the
draft's own segmented bindings and the block's resolved bound sections —
computed fresh on every run. No block id, section title, document filename,
or lineage literal MUST decide subject membership.

#### Scenario: A licensed fact with a bound section is a subject

- GIVEN a transposition block with a `fact:`-bound sentence whose fact names
  a section the block resolves as bound
- WHEN the guard derives the subject set
- THEN that sentence is a subject

#### Scenario: An evidence-bound sentence is never a subject

- GIVEN a sentence bound `evidence:` rather than `fact:`, in the same block
- WHEN the guard derives the subject set
- THEN that sentence is never a subject, regardless of any section bound to
  the block

#### Scenario: A structural sentence is never a subject

- GIVEN a sentence classified `structural` by the block's own bindings
- WHEN the guard derives the subject set
- THEN that sentence is never a subject

#### Scenario: A fact-bound sentence whose fact carries no bound section is never a subject

- GIVEN a `fact:`-bound sentence whose fact has no document-rooted bound
  section resolved for the block
- WHEN the guard derives the subject set
- THEN that sentence is never a subject, and no refusal is raised for it

#### Scenario: An argument-mode block has no subjects

- GIVEN a block whose contract resolves `mode: argument`, with an otherwise
  identical `fact:` binding and bound section
- WHEN the guard runs
- THEN the subject set is empty and no grounding refusal is possible for
  that block

### Requirement: An Absent Account Refuses, Distinct From A Missing Verdict

When the subject set is non-empty and no grounding account was supplied, the
guard MUST refuse `GROUNDING_ACCOUNT_ABSENT`, naming the block and the
subject count — never letting the absence fall through to
`GROUNDING_VERDICT_MISSING` on the first subject, which would name one
sentence when the real fault is that no account ran at all.

#### Scenario: No account, subjects exist

- GIVEN a block with one or more subject sentences and no grounding account
- WHEN the guard runs
- THEN it refuses `GROUNDING_ACCOUNT_ABSENT`, naming the block and the
  subject count, and raises no `GROUNDING_VERDICT_MISSING`

#### Scenario: No account, no subjects

- GIVEN a block with an empty subject set and no grounding account
- WHEN the guard runs
- THEN no grounding refusal is raised

#### Scenario: Mutation — the absent-account refusal is reachable

- GIVEN the absent-account check removed, so an absent account is treated as
  if it were simply empty
- WHEN the "no account, subjects exist" scenario above is run against the
  mutant
- THEN that scenario goes red, proving `GROUNDING_ACCOUNT_ABSENT` is
  reachable under an unmutated implementation

### Requirement: The Account Is Reconciled Against Independently Re-Derived Bytes, In Both Directions

The guard MUST NOT trust the account's own list of sentences or its own copy
of a section's text. It MUST re-derive the subject sentences from the
draft's own segmentation and the section bytes from the block's own resolved
bindings, then reconcile the account against those re-derived values in
both directions: every account entry must name a sentence the guard itself
segmented, and every subject sentence must have an account entry.

#### Scenario: An account entry naming an unsegmented sentence refuses

- GIVEN a grounding account entry whose `sentence` text does not match any
  sentence the guard segmented from the draft
- WHEN the guard reconciles the account
- THEN it refuses `GROUNDING_SENTENCE_UNKNOWN`, quoting the offending
  account entry verbatim

#### Scenario: A subject sentence absent from the account refuses

- GIVEN a subject sentence with no corresponding entry in the grounding
  account
- WHEN the guard reconciles the account
- THEN it refuses `GROUNDING_VERDICT_MISSING`, naming the block and the
  unjudged sentence verbatim

#### Scenario: Mutation — each direction is independently reachable

- GIVEN either the unknown-sentence check or the missing-verdict check
  disabled, one at a time
- WHEN the corresponding scenario above is run against each mutant in turn
- THEN each scenario goes red only for its own disabled direction, proving
  `GROUNDING_SENTENCE_UNKNOWN` and `GROUNDING_VERDICT_MISSING` are reachable
  independently of one another

### Requirement: The Permissive Verdict Carries The Burden Of Proof

`supported` is the verdict that lets a sentence reach substitution, so
`supported` is the one the guard MUST require to be grounded: its cited span
MUST be byte-present in the re-derived text of the section belonging to that
sentence's own fact. `unsupported` MUST need no span to refuse — demanding a
quoted span for a claim the section never makes would demand proof of a
negative. This inverts `contract-audit`'s shipped asymmetry, where the
*blocking* verdict (`fires`) is the one required to quote a span: here the
verdict that must be grounded is the one that lets the sentence through, not
the one that stops it. Copying that asymmetry unchanged would let an
ungrounded `supported` wave every sentence past, making this guard
ceremonial — green and worthless.

#### Scenario: A supported verdict with a byte-present span passes

- GIVEN a subject sentence whose account entry is `supported` with a span
  that is present verbatim in the sliced text of that sentence's own bound
  section
- WHEN the guard reconciles that entry
- THEN the sentence passes as `supported`, with the span reported

#### Scenario: A supported verdict with an absent span downgrades

- GIVEN a subject sentence whose account entry is `supported` with a span
  that is empty, or not byte-present anywhere in that sentence's own bound
  section text
- WHEN the guard reconciles that entry
- THEN the verdict downgrades to `undecidable`, its span cleared, and no
  refusal is raised for that sentence alone

#### Scenario: A supported verdict grounded in a different fact's section downgrades

- GIVEN a subject sentence bound to fact `calibration-regime`, whose account
  entry is `supported` with a span that is byte-present only in the bound
  section of a different fact
- WHEN the guard reconciles that entry
- THEN the verdict downgrades to `undecidable`, its span cleared

#### Scenario: Mutation — the downgrade is caught only by span reconciliation

- GIVEN the span-presence check on a `supported` verdict removed, so any
  span string is accepted without being re-read from the section's own bytes
- WHEN the absent-span downgrade scenario above is run against the mutant
- THEN that scenario goes red — the ungrounded `supported` verdict now
  wrongly survives, proving byte reconciliation is load-bearing

### Requirement: An Unsupported Claim Refuses

A subject sentence whose account verdict is `unsupported` MUST refuse
`SECTION_UNSUPPORTED_CLAIM`, naming the block, the fact, the lineage, the
section title, and the sentence.

#### Scenario: An unsupported claim is refused with full identification

- GIVEN a subject sentence asserting a claim its account marks `unsupported`
- WHEN the guard reconciles that entry
- THEN it refuses `SECTION_UNSUPPORTED_CLAIM`, naming the block, the fact,
  the lineage, the section title, and the sentence verbatim

#### Scenario: Mutation — the unsupported refusal is reachable

- GIVEN the `unsupported` branch of reconciliation mutated to treat that
  verdict as `undecidable` instead of refusing
- WHEN the unsupported-claim scenario above is run against the mutant
- THEN that scenario goes red, proving `SECTION_UNSUPPORTED_CLAIM` is
  reachable under an unmutated implementation

### Requirement: Undecidable Never Blocks Alone; Downgrades Are Counted Separately From Returned Undecidables

`undecidable` — whether returned directly by the account or produced by a
downgrade — MUST NOT block on its own, in any count. A mechanism that blocks
on its own uncertainty trains the agent to guess. But an agent's honest
`undecidable` and a downgraded, unfounded `supported` MUST remain
distinguishable: the report MUST carry `subjects`, `decided`, `undecidable`
(as returned by the account), and `downgraded` (produced by reconciliation)
as separate counts per block.

No ratio threshold exists between these counts, deliberately: no real
`document`-rooted binding exists on disk to calibrate one against, and a
picked ratio presented as a measurement is the failure this repository
names by name. **Falsifier:** over ten or more recorded real `write` runs
against genuine document-rooted bindings, if any block reaches `written`
with `downgraded > 0`, or with `subjects > 0` and `decided == 0`, this
requirement is wrong and a blocking rule over these counts must be added.

#### Scenario: An all-undecidable-or-downgraded account does not block

- GIVEN a block whose subjects are all either returned `undecidable` or
  downgraded to `undecidable`, with none `unsupported`
- WHEN the guard's overall outcome is computed
- THEN the block is not refused for grounding, and `undecidable` and
  `downgraded` are reported as separate, non-zero counts

#### Scenario: A downgrade is never counted as an agent-returned undecidable

- GIVEN one subject returned `undecidable` directly and a second subject
  returned `supported` with an absent span
- WHEN the report is produced
- THEN `undecidable` counts exactly the first and `downgraded` counts
  exactly the second — the two counts never merge

### Requirement: A Sibling Check, Never An Extension Of The Verbatim Or Leak Checks

This capability MUST be implemented as its own function raising its own
codes, never by widening `check_source_section_verbatim`'s overlap
computation or `check_tripwire`'s recorded sample set. Folding a bound
section's bytes into the style sampler's comparison set would break
`style-leak-detection`'s shipped `Requirement: Overlap Reads Only The
Recorded Sample Set`. Folding an agent's semantic account into the verbatim
check would put a verdict-bearing input inside a function whose contract is
that it computes its answer from three strings alone, and would make one
refusal code stand for two unrelated failures the roster cannot separate.

#### Scenario: A verbatim paste and an unsupported claim are two distinct refusals

- GIVEN a transposition block whose draft both pastes a run from its bound
  section above the verbatim threshold and separately asserts a claim its
  account marks `unsupported`
- WHEN `write` runs both checks
- THEN `SOURCE_SECTION_VERBATIM` and `SECTION_UNSUPPORTED_CLAIM` are
  reported as two independent refusals, neither computed by widening the
  other's function or sample set

### Requirement: The Guard Fires After The Verbatim Check And Before Substitution

The grounding guard MUST run inside `write_block`, after
`check_source_section_verbatim` clears and before `paper_block.substitute`.
A draft failing both the verbatim check and this guard MUST name
`SOURCE_SECTION_VERBATIM` deterministically — copying is decided before
meaning. This guard MUST NOT be wired only into a read-only verb.

#### Scenario: An unsupported claim is refused by an actual write invocation

- GIVEN a transposition block whose draft asserts a claim its account marks
  `unsupported`
- WHEN `write` is invoked directly for that block, never a read-only verb
- THEN it refuses `SECTION_UNSUPPORTED_CLAIM` before `substitute` runs, and
  the paper's output remains unchanged from its pre-`write` state

#### Scenario: A draft failing both checks names the verbatim refusal

- GIVEN a draft that both pastes a verbatim run above threshold and asserts
  an unsupported claim
- WHEN `write` runs
- THEN it refuses `SOURCE_SECTION_VERBATIM`, not `SECTION_UNSUPPORTED_CLAIM`

### Requirement: A Block With No Decided Subject Reports Unmeasured, Never A Silent Pass

A block whose subject set is empty, or whose subjects all resolve with
`decided == 0`, MUST report `sourceGrounding: {"status": "unmeasured",
"subjects": N}` — mirroring `sourceFidelity`'s shipped shape — and MUST NOT
be refused or silently treated as passed for that reason. The two
`unmeasured` cases MUST be distinguished by the reported `subjects` count.

#### Scenario: No subjects reports unmeasured with a zero count

- GIVEN a transposition block with an empty subject set
- WHEN `write` completes
- THEN `sourceGrounding` reports `{"status": "unmeasured", "subjects": 0}`

#### Scenario: Subjects exist but none decided reports unmeasured with a nonzero count

- GIVEN a block whose subjects are all returned `undecidable`
- WHEN `write` completes
- THEN `sourceGrounding` reports `{"status": "unmeasured", "subjects": N}`
  with `N > 0`, distinguishing this case from the empty subject set
