# Transposition Fidelity Specification

## Purpose

A block whose contract declares `mode: transposition` must carry its bound
source section into the paper's own style — never copy it. Nothing enforced
that until now: `paper_leak.check_tripwire` exists to prove style did not
leak content, and has exactly one call site gated on the style channel; it
never reached a source-section binding, so a redactor could paste a bound
section's own bytes into a draft and `write` would write it.

This capability adds `SOURCE_SECTION_VERBATIM`, a SIBLING of the style
tripwire — its own refusal code, its own self-calibrated threshold, reusing
the same shipped measurement primitives (`overlap_against_set`,
`tripwire_spans`) rather than widening `check_tripwire` itself, so the two
domains' thresholds stay tunable apart and the shipped style check's own
bytes never move because of this capability.

**The threshold has no independent-paper precedent to inherit.** The shipped
eight-token tripwire is calibrated against an INDEPENDENT published paper's
prose, where any shared clause is already suspicious. A bound source section
is the SAME author's own earlier text about the same work, where reusing
terms, quantities, and formal statements at a far higher baseline is
ordinary. This capability therefore self-calibrates per block, per section,
against the one text already known to be legitimate: the block's own
contract prose.

**The limit, stated rather than implied away.** No real `document` binding
exists on disk in this repository today — the archived predecessor removed
every transcribed binding, and every bindable entry is `undecided`. Every
end-to-end scenario below is necessarily synthetic: exercised through
`bind`-recorded fixtures, never a real source document. The falsifiers named
below become executable only once a real binding exists, and that obligation
is recorded, not deferred silently.

## Requirements

### Requirement: The Verbatim Check Is A Sibling, Never An Extension Of The Style Tripwire

`SOURCE_SECTION_VERBATIM` MUST be raised by a dedicated function
(`check_source_section_verbatim`) in the same module as the style tripwire,
never by widening `check_tripwire` itself or by adding a bound section to
its own sample set. `style-leak-detection`'s own `Requirement: Overlap Reads
Only The Recorded Sample Set` forbids `STYLE_OVERLAP` from comparing against
a reference file read directly; a bound section's bytes come from exactly
that kind of direct read, so folding them into `check_tripwire` would break
a shipped requirement rather than merely overload a function. This
capability's own comparison — draft against a resolved section's own bytes —
is not `STYLE_OVERLAP` and does not touch `R`, the style sampler's recorded
set, at all.

#### Scenario: A verbatim source-section paste is a distinct refusal from a style leak

- GIVEN a transposition block whose draft both shares a run with its style
  channel's recorded set `R` above the style tripwire's threshold, and
  separately pastes a run from its own bound section above this
  capability's threshold
- WHEN `write` runs both checks
- THEN `STYLE_OVERLAP` and `SOURCE_SECTION_VERBATIM` are reported as two
  independent refusals, neither one computed by widening the other's
  function or sample set

#### Scenario: The shipped style tripwire's own bytes do not move

- GIVEN `check_tripwire` as shipped before this capability existed
- WHEN this capability's sibling function is added
- THEN `check_tripwire`'s own implementation is unchanged; only a new,
  separate function and refusal code are introduced

### Requirement: The Threshold Self-Calibrates Against The Contract's Own Prose

For each bound section `S_i` of a transposition block `B`, the floor is
`overlap_against_set(contract_prose, [S_i])` — the longest normalized run
`B`'s own contract prose already legitimately shares with `S_i` — computed
with the identical normalization the style tripwire uses. The threshold is
`max(floor_i, SOURCE_RUN_BACKSTOP)`, where `SOURCE_RUN_BACKSTOP = 16`. The
check MUST refuse `SOURCE_SECTION_VERBATIM` when the draft's longest shared
normalized run with `S_i` STRICTLY exceeds `threshold_i`; a run equal to the
threshold MUST pass.

`SOURCE_RUN_BACKSTOP` is a ruling, not a measurement: the shipped eight-token
tripwire is deliberately sub-clause because for an independent paper a
shared clause is already suspicious, while for a same-author source a shared
clause is ordinary and the unit that means "copied" is a sentence — sixteen
normalized tokens sits at the low end of an academic sentence, set at the
permissive end on purpose, because a false refusal here blocks `write` while
a false pass still faces contract-audit and a human.

There is deliberately no upper clamp on the floor: a contract that itself
carries a long run from its own bound section has licensed that run, and a
draft carrying it is the redactor obeying its own contract — a concern for
contract-audit, never this guard.

#### Scenario: A draft pasting its bound section verbatim refuses

- GIVEN block `analysis.an-core`, bound to `widget-study-r4.md`, section
  `2. Widget Calibration`, whose contract prose shares no run with that
  section longer than six normalized tokens
- WHEN the draft's opening sentence reproduces, verbatim, a seventeen-token
  run from that section
- THEN `write` refuses `SOURCE_SECTION_VERBATIM`, naming the block, the bound
  fact, the lineage, the section title, and the offending span

#### Scenario: The same claim in the paper's own register passes

- GIVEN the same block and bound section
- WHEN the draft states the same claim in different words, sharing no
  normalized run with the section longer than six tokens
- THEN no `SOURCE_SECTION_VERBATIM` refusal is raised

#### Scenario: A contract-licensed long run is not refused

- GIVEN a block whose own contract prose already shares a forty-token run
  with its bound section (the floor is forty, above the backstop)
- WHEN the draft reproduces that same forty-token run
- THEN no `SOURCE_SECTION_VERBATIM` refusal is raised — the run is equal to,
  not strictly above, its own threshold

#### Scenario: Mutation — the backstop alone is not enough without the floor

- GIVEN `threshold_i` computed as `max(floor_i, SOURCE_RUN_BACKSTOP)`
  mutated to `SOURCE_RUN_BACKSTOP` alone (the floor discarded)
- WHEN the contract-licensed long-run scenario above is run against the
  mutant
- THEN that test goes red — a contract-licensed forty-token run now
  wrongly refuses under the sixteen-token backstop alone, proving the floor
  is load-bearing

#### Scenario: Mutation — the floor alone is not enough without the backstop

- GIVEN `threshold_i` computed as `max(floor_i, SOURCE_RUN_BACKSTOP)`
  mutated to `floor_i` alone (the backstop discarded)
- WHEN a block whose contract prose shares near nothing with its section
  (floor near zero) drafts a six-token idiom that also appears in the
  section
- THEN a test asserting that idiom does NOT refuse goes red — a near-zero
  floor now wrongly refuses a six-token idiom, proving the backstop is
  load-bearing

#### Scenario: Mutation — the refusal is reachable at all

- GIVEN the check's own comparison mutated so that no run can ever exceed
  its threshold (for example the refusal's own minimum raised far above any
  real draft length)
- WHEN the verbatim-paste scenario above is run against the mutant
- THEN that test goes red, proving `SOURCE_SECTION_VERBATIM` is reachable
  under an unmutated implementation and not merely asserted never to fire

### Requirement: The Floor And Threshold Are Reported, Never Inferred Silently

Every `write` envelope for a transposition block with at least one measured
bound section MUST report, per section, the floor, the threshold, and the
longest observed run — whether or not the check refused. A contract whose
own prose already carries a long run from its bound section makes this
guard inert for that block (Requirement above); that inertness MUST be
visible through the reported floor in the same envelope, never silent and
never left for someone to infer from the absence of a refusal.

#### Scenario: A passing block still reports its own floor

- GIVEN a transposition block whose draft passes with no refusal
- WHEN `write` completes
- THEN the envelope's `sourceFidelity` reports, for that section, the floor,
  the threshold, and the longest observed run — not merely a pass/fail
  verdict

#### Scenario: A contract-licensed high floor is visible, not silent

- GIVEN a block whose own contract prose shares a forty-token run with its
  bound section, making the guard inert for any draft run at or below forty
- WHEN `write` completes for a draft that reproduces that run and passes
- THEN the envelope reports a floor of forty and a threshold of forty for
  that section, so the inertness is readable from the envelope itself,
  never merely inferable from an absent refusal

### Requirement: The Guard Fires Inside `write`, Before Substitution, Never Only From A Read-Only Verb

`check_source_section_verbatim` MUST run inside `write_block`, after
contract-audit clears and before `substitute`, beside the style tripwire and
after it — a draft failing both checks MUST name `STYLE_OVERLAP`
deterministically. A guard wired only into a read-only verb enforces
nothing at the one moment a false claim would otherwise reach `main.tex`;
this repository has already measured nine such instances, and this
capability MUST NOT become a tenth.

#### Scenario: A verbatim paste is refused by an actual `write` invocation

- GIVEN a transposition block bound to a section, drafted with a paste
  exceeding its threshold
- WHEN `write` is invoked directly for that block (never a read-only verb)
- THEN it refuses `SOURCE_SECTION_VERBATIM` before `substitute` runs, and
  `main.tex` remains byte-identical to its pre-`write` state

#### Scenario: Mutation — wiring the guard only into a read-only verb is caught

- GIVEN the guard implemented so that only a read-only verb (for example
  `phases`) calls `check_source_section_verbatim`, and `write_block` itself
  skips it
- WHEN a test drafts the same verbatim-paste block by directly invoking
  `write`, never the read-only verb
- THEN that test fails, since `write` would proceed and write the block
  instead of refusing

#### Scenario: A refusal here burns no judge-cycle attempt

- GIVEN a transposition block whose contract-audit already cleared and whose
  draft then fails this capability's own check
- WHEN `write` refuses `SOURCE_SECTION_VERBATIM`
- THEN the on-disk attempt ledger is not written for that attempt — the
  ledger records only the audit-fired branch, not this refusal

### Requirement: Only A Transposition-Mode Block Is Checked, Mode Derived From The Contract On Disk, Never Listed

Whether a block is checked is decided by `contract.mode ==
paper_vocabulary.MODE_TRANSPOSITION`, where `mode` is resolved by the same
derivation `write` already performs for `MODE_ABSENT`
(`paper_contract.resolve_mode`). No block id, section title, document
filename, or paper id may decide applicability; a hand-maintained list of
"which blocks are transposition" MUST NOT exist anywhere this capability's
own code reads.

`argument`-mode blocks are explicitly OUT OF SCOPE for this capability: the
threshold's whole justification rests on transposition semantics — "carry
the source into the paper's own style" — and a verbatim run inside an
argument block is a quotation question this capability does not decide.
Widening to `argument` mode is a named follow-up, not an oversight.

#### Scenario: A transposition-mode block is checked

- GIVEN a block whose contract resolves `mode: transposition`
- WHEN `write` runs
- THEN `check_source_section_verbatim` runs for that block's bound sections

#### Scenario: An argument-mode block with the identical binding is not checked

- GIVEN the same bound section, but the block's contract resolves
  `mode: argument`
- WHEN `write` runs
- THEN `check_source_section_verbatim` does not run, and no
  `SOURCE_SECTION_VERBATIM` refusal is possible for that block regardless of
  how much of the section the draft reproduces

#### Scenario: Mutation — mode is derived, not assumed

- GIVEN the stage guard's own condition mutated from
  `contract.mode == MODE_TRANSPOSITION` to
  `contract.mode == MODE_ARGUMENT`
- WHEN both the transposition-mode scenario and the argument-mode scenario
  above are run against the mutant
- THEN both go red: the transposition block that should be checked is no
  longer checked, and the argument block that should be exempt is now
  wrongly checked

### Requirement: A Block With No Measured Bound Section Reports Unmeasured, Never Refused

A transposition block whose bindable requirements resolve no measured bound
section (an `undecided` binding, or a source root reported `unmeasured`)
MUST report `sourceFidelity: {"status": "unmeasured"}` in its `write`
envelope — mirroring the style channel's own shipped `unmeasured`/`measured`
shape rather than inventing a second reporting convention. It MUST NOT
refuse for that reason, and it MUST NOT be silently treated as passed: a
paper at an earlier stage, with nothing yet bound to compare against, is not
a fault this capability decides.

#### Scenario: A block with no bound section reports unmeasured

- GIVEN a transposition block whose bindable requirement carries no
  `document` binding at all (reported `undecided` elsewhere)
- WHEN `write` completes for that block
- THEN the envelope's `sourceFidelity` reports `{"status": "unmeasured"}`,
  with no `SOURCE_SECTION_VERBATIM` refusal raised

#### Scenario: Mutation — the resolved bindings must actually reach the check

- GIVEN `BlockContract.source_sections` populated with the resolved bound
  sections for a block, then mutated to always pass `()` regardless of what
  was resolved
- WHEN the verbatim-paste scenario above is run against the mutant
- THEN that test goes red — the envelope now wrongly reports `unmeasured`
  and no refusal fires, proving the resolved bindings must actually arrive
  at the check for it to do anything
