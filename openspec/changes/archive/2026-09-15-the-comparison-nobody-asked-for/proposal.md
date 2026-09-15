# Proposal: the-comparison-nobody-asked-for

**Phase**: propose · **Artifact store**: hybrid (Engram `sdd/the-comparison-nobody-asked-for/proposal`)
**Upstream**: `openspec/changes/the-comparison-nobody-asked-for/exploration.md`
**Subject**: `.claude/skills/proposal-implementation` and the shared engine
`.claude/skills/_core/implementation/engine/implementation_engine.py`

> **Size note.** The `sdd-propose` skill sets a 450-word default budget. The owner's
> binding scope directive for this change enumerates seven required contents,
> including a non-technical walkthrough. That explicit contract overrides the
> default budget. Every section below is required by it.
>
> **Revision 2.** Incorporates the owner's answers to the three proposal-round
> questions: the gap count is derived rather than transcribed (Q1); a declined
> comparison reports its date (Q2); and the offer re-fires on its own when the
> set of things to compare against changes (Q3). `exploration.md` has been
> patched with this phase's two corrections, so the two documents agree.

## Intent

The skill implements a mathematical proposal in plain numerical code, proves it
against the paper, and stops. It never converts to a trainable backend and never
runs a benchmark on its own. That division is correct and is **not** in question.

Two things around it are wrong.

**The comparison machinery is built before anyone asks for a comparison.** The
first flow's scaffold stage unconditionally creates a benchmark package next to
the method's own package. Nobody has proposed a comparison at that point. Worse,
the flow then makes itself dependent on what it prematurely created: the
declaration it asks the user for is written *into* that benchmark package, and
the notebook the first flow executes imports its stamping module *from* that
benchmark package. So the premature creation cannot simply be deleted — two
things the first flow genuinely needs are living inside it.

**A declined comparison leaves no trace.** When the second flow finally does
propose the benchmark run and the person answers "not now", nothing anywhere
records that answer. The next time anyone asks what to do next, the same offer
fires again, unchanged, forever.

There is a third consequence that follows from the first. Because the skill's own
benchmark package is a directory under `src/` that the baseline finder does not
exclude, **every scaffolded target appears to already have a baseline** — the one
the skill just created for itself. The state that exists precisely to say "there
is nothing here to compare against" is therefore structurally unreachable.

## How the flow works after this change

*This section names no file, no function, and no refusal code. It is the whole
behaviour, for a reader who has never seen this codebase.*

**The first pass.** Somebody hands the assistant a mathematical proposal and asks
for an implementation. The assistant builds the method in plain numerical code,
writes tests that prove each formula behaves the way the paper says it does, runs
them, and stops. It builds nothing for measuring the method against a competitor,
because nobody has asked for a measurement. What exists on disk at the end of
this pass is the method, its tests, the declaration of what revision of the paper
it was built against, and the small piece that lets the verification notebook
stamp what it proved.

**What the flow recommends next.** When somebody asks "what now?", the flow reads
what is actually on disk and names the single most useful next thing. If the
method is not yet in a form a machine can train, it says so and asks for that
conversion first. If there is genuinely nothing on disk to compare the method
against, it says exactly that and stops — it does not invent a competitor, and it
does not count its own scaffolding as one.

**When the comparison is proposed.** Only once a trainable version exists *and*
there is real prior work on disk to measure against does the flow put the
question to the person: should we run this comparison? It costs machine time, so
it is asked, never assumed.

**On acceptance.** The person says yes. *Only then* does the comparison machinery
come into existence — the code that runs both sides, the code that decides which
one won, and the notebook that reports the outcome. The comparison then runs and
the result is reported.

**On refusal.** The person says not now. That answer is recorded as an answered
question against the exact wording that was asked, and that wording names the
prior work the comparison would have been against. The flow reports that the
comparison stands declined **and on what date it was declined**, then stops
there. Nothing is built.

**The pass after a refusal.** Asking "what now?" again does not re-open the
settled question. The flow reports the same declined state, with the same date,
so somebody returning weeks later can tell at a glance whether this was decided
yesterday or in March. Nobody is asked the same question twice while nothing has
changed.

**When the situation changes on its own.** If prior work that did not exist at
the time of the refusal later appears on disk — or work that did exist is removed
— then the comparison on offer is no longer the comparison that was declined. The
question the flow would ask is a different question, so it asks it. The offer
re-fires by itself, without anybody having to remember to re-open it. Silence is
correct only while the situation is genuinely unchanged; re-running the tests,
editing the method, or re-rendering a report change nothing about what would be
compared, and leave the decision settled.

**Changing one's mind.** The person answers that same question again with a
different answer. The most recent answer is the one that counts, so the
comparison becomes live again and the flow proceeds exactly as if it had been
accepted the first time. There is no separate re-opening step to learn, and no
new machinery behind it.

## End state, concretely

**What the first flow leaves on disk.** `src/<Package>/` holds the method's
modules, `__init__.py` — now also carrying the `revision` and `premises`
declaration as a top-level literal — and `report_digest.py`. **No `_Benchmark`
directory exists at all.**

**The scaffold gap count.** Currently at most **thirteen**: eleven unconditional
destinations plus up to two conditional merge anchors. After this change, at most
**twelve**: ten unconditional plus the same two anchors.

> **Correction, now agreed by both documents.** The exploration originally stated
> the new count as "at most eleven: nine unconditional plus two anchors". That is
> arithmetically wrong; `exploration.md` has been patched and the two documents
> now agree. Two files leave the benchmark package, but only **one** leaves the
> scaffold list. `report_digest.py` is *relocated* to
> `src/<Package>/report_digest.py` and remains an unconditional scaffold
> destination, because the first flow's own verification notebook imports it and
> executes inside the first flow. Only `src/<Package>_Benchmark/__init__.py` is
> removed. Eleven − one = **ten** unconditional. Verified by reading
> `scaffold_destinations`, `scaffold_gaps`, and the kit notebook's import line.

**The count is derived, never transcribed.** *(Owner ruling, Q1.)* Twelve is
stated here, once, with its derivation — and it is the last place a
hand-written figure appears. The doctrine prose must not carry the gap count as
a literal. This is the second change in a row to move that number, and a number
written into prose is precisely the class of sentence that outlives its
mechanism, a defect this repository has hit repeatedly. Wherever a count must
appear for a human to read, it is computed from the destination list at read
time. The sweep therefore **removes** the transcribed "thirteen" rather than
replacing it with "twelve": introducing a fresh literal would only reset the
clock on the same defect.

**The harness destinations.** `harness_destinations()` grows from three entries to
**four**, gaining `src/<Package>_Benchmark/__init__.py`. It is already written
only by the second flow's wiring-first rung, behind a real accepted comparison. No
fourth materialization stage is invented.

**The probe ladder.** `PROBE_NEXT_STEPS` gains one new terminal entry,
`"declined"`, with `wiring: False` and `publish: None` — structurally symmetric
with the existing `nothing-to-compare` and `already-benchmarked`. A declined
comparison is persisted as a bare `discuss` event keyed on a stable question-text
constructor; the last event on that text wins.

**The declined report names its date.** *(Owner ruling, Q2.)* A flat terminal
statement is not enough for somebody returning weeks later. The ledger event
already carries an `at` field, so this reads a field that exists rather than
adding one. Two consequences to carry forward:

- `at` is second-granularity and can tie. `_discussion_buckets` documents that
  **ledger append order decides, never a comparison of `at`**. The date is for
  display only; it must never become the ordering key.
- `_answered_discussions` returns question *text* only, so it cannot supply the
  date. The declined report reads the bucket event itself. Whether that is a
  direct `_discussion_buckets` read or a small sibling reader is a design
  question, not a proposal one — but the insufficiency is named here so the
  design phase does not discover it late.

**The offer re-fires when the situation materially changes.** *(Owner ruling,
Q3.)* The decline question-text constructor derives its text from the target, the
name, and **the sorted baseline names** — the exact output of
`previous_implementations()` at decline time — and **never from a count of them**.
Because buckets are keyed by exact trimmed text, new prior work appearing (or
existing prior work being removed) changes the name set, which changes the key,
which leaves the new bucket unanswered, which re-fires the offer by itself. Every
other activity — re-running the suite, editing modules, re-rendering a report —
leaves the key untouched and the decision settled.

This needs no new machinery, and the doctrine already argues for it. Two verified
precedents, to be inherited rather than re-derived:

- `_report_findings_question` embeds the **finding names** for exactly this
  reason, in its own words: *"a finding appearing or clearing IS a change of
  state, and re-asking then is the point."* It explicitly refuses to embed a
  count of rows, because *"rows move ... while the fact the operator is being
  shown ... has not changed."* Baseline names are the direct analogue.
- `_piloted_discuss_entry` is the origin of the stability rule both other
  constructors cite: it derives from each axis's **declared** scale and never
  from `ran`, because the achieved figure *"climbs on every poll while the
  ... decision has not changed"*.

**The baseline finder.** `previous_implementations()` gains a `_Benchmark`-suffix
exclusion, which makes `nothing-to-compare` reachable for a scaffolded target for
the first time.

## Scope

### In scope

1. **Movement 1 — the seal leaves the benchmark package.** Relocate
   `report_digest.py` to `src/<Package>/report_digest.py`; simplify `_here()`'s
   self-location (the `_Benchmark` suffix strip becomes a no-op); update
   `scaffold_destinations`, `scaffold_kit_source`, both `materialize.py` sites,
   and the `verification.ipynb` / `probe.ipynb` import lines.
2. **Movement 2 — the declaration leaves the benchmark package.** Move `revision`
   and `premises` to a new top-level literal in `src/<Package>/__init__.py`.
   Step 9's existence gate (`OBJECT_MAP_NOT_APPROVED` until both are non-blank)
   is **preserved verbatim**; only the destination changes. The kit's
   `src_benchmark/__init__.py` seven-block declaration shrinks to five.
3. **Movement 3 — the first flow stops creating the benchmark package.** Remove
   `src/<Package>_Benchmark/__init__.py` from `scaffold_destinations` and its
   mapping entry from `scaffold_kit_source`; add it to `harness_destinations` and
   `harness_kit_source`. Update the gap-count doctrine everywhere.
4. **Movement 4 — a declined comparison is remembered.** Add a stable
   question-text constructor embedding the **sorted baseline names** (never a
   count), a second `_answered_discussions` call site, the `"declined"` terminal
   entry in `PROBE_NEXT_STEPS`, and a declined report that names the decline
   **date** read from the bucket event's `at` field.
5. **The side finding.** `previous_implementations()` excludes `_Benchmark`-suffixed
   packages, making `nothing-to-compare` reachable. **This lands in the same
   commit as the constructor** (see the migration note below) — the two are not
   separable without leaving a window in which the recorded key is knowably wrong.
6. **Stale-documentation sweep — in-scope work, not commentary.** `SKILL.md`'s
   step 5 table, step 8 prose, the seven-block declaration table, the
   run-the-benchmark Decision Gates row, and the "Conversion, then benchmark"
   paragraph; `references/usage.md`'s worked scaffold-file-list example and its
   `OBJECT_MAP_NOT_APPROVED` refusal-detail row; the sibling
   `experimental-implementation/impl_profile.py`'s `OBJECTIVE_FLOW` "standing"
   stage, which names the same gate in its own words. The sweep also **removes
   every transcribed gap-count literal** rather than updating it, per the Q1
   ruling.
7. **Test triage and update** across `tests/test_proposal_implementation.py` and
   `tests/test_remote_execution.py`.

#### Migration consequence — one expected re-fire, not a defect

Unit 4 ships both the `_Benchmark`-suffix exclusion and the question-text
constructor. On a target that declined a comparison **before** this change lands,
the recorded key embeds the pre-fix baseline set — on the live target,
`['CREDA', 'MIL_CREDA_Benchmark']`. After the exclusion, the set becomes
`['CREDA']`. That is a different key, so the offer **re-fires exactly once** on
the first pass after this change.

This is correct behaviour under the rule the owner chose in Q3, not a regression:
the question genuinely changed, because the comparison it describes is no longer
the same comparison. It is stated here so nobody reports it later as a bug. Both
pieces landing in one commit is what keeps this to a single, explicable re-fire
rather than a sequence of them.

Nothing is deferred. No movement is dropped for size.

### Out of scope

- **The `AGREED.md` / `AGREEMENTS.md` naming drift** at two points in `SKILL.md`
  where the doctrine paragraph says "AGREEMENTS.md" while everywhere else says
  "AGREED.md". Pre-existing and unrelated to this change. It sits in the same
  paragraph Movements 2 and 4 touch, so it is worth one line in the commit that
  touches that paragraph — it is explicitly **not** a fifth movement and gets no
  work unit, no spec, and no task.
- Changing *where in the flow* the declaration is asked for. Step 8, behind step
  7's gate, with no renumbering, was decided by the archived change
  `2026-08-20-the-flow-names-what-it-needs` and is **not reverted**. Only the
  on-disk destination changes.
- Giving `premises` a reader. Its content is deliberately unvalidated — it is
  written for a person reading a drift report, not for a check to parse. The
  defect was its location, never its lack of a reader.
- Converting to PyTorch or running benchmarks from the first flow. That division
  is correct and untouched.

## Capabilities

> Researched: `openspec/specs/` holds **41** specs. The exploration's claim that
> it is "empty — nothing to update" is false as stated, but its conclusion holds:
> a keyword sweep across all 41 shows **no existing spec governs** the scaffold
> destination list, the benchmark-declaration location, the probe ladder's
> terminal states, or the baseline finder. Matches in
> `implementation-engine-neutrality`, `implementation-document-binding`,
> `paper-scaffold`, `block-substitution`, and `experimental-implementation-skill`
> are all about unrelated subjects that merely share a word.

### New Capabilities

- `implementation-comparison-deferral`: comparison machinery comes into existence
  only after a comparison is accepted. Covers the scaffold destination list, the
  benchmark-declaration location, the seal's location, the harness destination
  list, and the baseline finder's exclusion of the skill's own benchmark package.
- `implementation-declined-comparison`: a declined comparison is persisted,
  survives the next pass, and re-opens itself when the situation materially
  changes. Covers the stable question text keyed on sorted baseline names, the
  `"declined"` terminal state, the reported decline date, last-event-wins
  reopening, and the stability rule (only a change in what would be compared
  moves the key).

### Modified Capabilities

- None. No existing spec's requirements change.

## Approach

Four work units, chained, each with a clear start, finish, verification, and
rollback.

**Dependency order is proven from the code, not preferred.** Movement 3 cannot
land alone: step 9's existence gate (Movement 2) and step 15's notebook import
(Movement 1) both execute *inside the first flow*, before any second-flow work.
Removing the benchmark package without first relocating what those two read would
break the first flow itself. Movement 4 must land too, or a decline re-triggers
materialization on every pass.

**Order: units 1, 2 and 4 in any order among themselves → then unit 3 last.**

| # | Work unit | Delivers | Forecast (add+del) |
|---|---|---|---|
| 1 | The seal leaves the benchmark package | `report_digest.py` at `src/<Package>/`; both notebooks import the new path; both `materialize.py` sites moved in lockstep; `test_remote_execution.py` fixture-vs-contract triage completed | ~360 |
| 2 | The declaration leaves the benchmark package | `revision`/`premises` as a top-level literal in `src/<Package>/__init__.py`; step 9's gate preserved verbatim; kit declaration seven blocks → five; SKILL.md + usage.md swept | ~450 |
| 4 | A declined comparison is remembered | Question-text constructor keyed on sorted baseline names; second `_answered_discussions` call site; `"declined"` terminal in `PROBE_NEXT_STEPS`; decline date in the report; `previous_implementations` `_Benchmark` exclusion **in the same commit** | ~480 |
| 3 | The first flow stops creating the benchmark package | `_Benchmark/__init__.py` out of scaffold and into harness; every transcribed gap-count literal removed in favour of a derived count; `impl_profile.py` `OBJECTIVE_FLOW` updated; the bulk of the `_Benchmark` test surface | ~640 |
| | **Total** | | **~1930** |

The review budget for this change is 1400 lines and the delivery strategy is
`ask-on-risk`. The forecast exceeds the budget, and the answer to that is the
four chained units above — never reduced coverage. The strictly narrower archived
precedent forecast ~790 lines for a smaller subject, which corroborates this
total.

**Decision needed before apply: Yes** (chained delivery confirmation).
**Chained PRs recommended: Yes.**
**Budget risk: High.**

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `_core/implementation/engine/implementation_engine.py` | Modified | `scaffold_destinations`, `scaffold_kit_source`, `harness_destinations`, `harness_kit_source`, `_stage_objects`, `resolve_benchmark_declaration`, `authored_package_init`, `PROBE_NEXT_STEPS`, `previous_implementations`, a second `_answered_discussions` caller |
| `proposal-implementation/scripts/materialize.py` | Modified | Independently duplicates the scaffold mapping at two points; must move in lockstep |
| `proposal-implementation/assets/kit/nb/verification.ipynb` | Modified | Imports the seal from the benchmark package; needs the new path |
| `proposal-implementation/assets/kit/nb/probe.ipynb` | Modified | Same import, same fix |
| `proposal-implementation/assets/kit/nb/report_digest.py` | Modified | One-line `_here()` simplification. The kit **source** path is unchanged, so `KIT_SEAL` and `remote_cli.py`'s `_load_source_digest()` are unaffected |
| `proposal-implementation/assets/kit/src_benchmark/__init__.py` | Modified | Seven-block declaration shrinks to five |
| `proposal-implementation/SKILL.md` | Modified | Step 5 table, step 8 prose, seven-block table, Decision Gates row, "Conversion, then benchmark" |
| `proposal-implementation/references/usage.md` | Modified | Worked scaffold-file-list example; `OBJECT_MAP_NOT_APPROVED` refusal-detail row |
| `experimental-implementation/impl_profile.py` | Modified | `OBJECTIVE_FLOW`'s "standing" stage describes the shared-engine gate |
| `tests/test_proposal_implementation.py` | Modified | The bulk of the change surface |
| `tests/test_remote_execution.py` | Triage then modified | Mostly generic job-folder fixtures; contract-bearing subset unknown until triaged |
| `openspec/specs/` | New | Two new capability specs |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| `materialize.py`'s duplicated scaffold mapping is missed, reintroducing exactly the drift class the archived change already named | Med | Named as an explicit deliverable of unit 1; both sites move in the same commit; a test asserts the two mappings agree |
| The `_Benchmark` hits in `test_remote_execution.py` are untriaged fixture-vs-contract | High | Triage is a **discovery task inside unit 1**, not an assumption. Unit 1 does not close until every hit is classified |
| `experimental-implementation` ships no kit assets, so Movements 1–3 are latent there even though the mechanism is shared engine code | Med | Its `OBJECTIVE_FLOW` prose still describes the gate and is in scope. Verify no behavioural regression despite zero kit surface |
| Adding a `PROBE_NEXT_STEPS` entry moves the sealed corpus's `probe` case digest | High | Expected and mechanical: the neutrality spec already names `probe` as a digest mover. Regenerate the seal; this is not a requirement change |
| The scaffold gap count appears as a literal number in doctrine prose in several places | Med | Per the Q1 ruling, unit 3 **removes** those literals in favour of a derived count rather than updating them, so the next change to the list cannot strand the prose again |
| A second spelling of the decline question opens a second, never-retiring bucket | Med | One constructor, one spelling — the discipline `_pilot_decision_question` and `_report_findings_question` both state explicitly. A test asserts the single construction site |
| Embedding a baseline *count* instead of names would re-ask on every call | Low | Ruled out by the Q3 precedent and named in scope. Names change only on real state change; counts move independently |
| The decline date becomes an ordering key | Low | `at` is second-granularity and can tie; `_discussion_buckets` fixes append order as the ordering rule. Date is display-only, stated in the end state |
| The one-time re-fire after the `_Benchmark` exclusion is reported as a defect | Med | Stated in the proposal as expected behaviour, with the before/after key on the live target. Both pieces land in one commit so it happens once |
| Correcting "nine/eleven" to "ten/twelve" contradicted an upstream artifact | Resolved | `exploration.md` has been patched; both documents now agree |

## Rollback Plan

Each unit is an independent commit on a chained branch and reverts cleanly on its
own, in reverse dependency order. The two riskiest rollbacks:

- **Unit 3** is the only unit that changes what exists on disk after the first
  flow. Reverting it restores `_Benchmark/__init__.py` to the scaffold list; units
  1, 2 and 4 remain correct and functional without it, because the relocated seal
  and relocated declaration do not depend on the benchmark package existing.
- **Units 1 and 2** relocate files. Reverting either after real targets have been
  scaffolded leaves those targets with files at the new paths. Recovery is
  re-running the materialization stage, which is idempotent by contract; no data
  is lost because both relocated artifacts are kit-sourced, not authored.

Unit 4 is purely additive (one roster entry, one call site, one exclusion) and
reverts with no on-disk consequence.

## Dependencies

- None external. Every affected file is inside this repository.
- Internal ordering only: units 1, 2, 4 → unit 3, as derived above.
- No blocker outside this repository was found. Nothing in this change is
  "not now".

## Success Criteria

- [ ] After the first flow completes on a fresh target, **no `_Benchmark`
      directory exists** anywhere under `src/`.
- [ ] `src/<Package>/__init__.py` carries the `revision` and `premises`
      declaration, and step 9 still refuses `OBJECT_MAP_NOT_APPROVED` when either
      is blank — the same refusal, the same condition, a different file.
- [ ] The first flow's verification notebook executes and stamps successfully
      with the seal at its new path.
- [ ] The scaffold gap report names at most **twelve** entries: ten unconditional
      plus the two conditional merge anchors — and that figure is computed from
      the destination list, never transcribed.
- [ ] **No document states a gap count as a hand-written literal.** Grepping the
      doctrine for the old figure returns nothing, and returns no new figure
      either.
- [ ] `previous_implementations()` on a scaffolded target with no genuine prior
      work returns an empty list, and the flow reports `nothing-to-compare`.
- [ ] Declining the benchmark offer, then immediately asking what to do next,
      reports the `declined` terminal state, **names the date of the decline**,
      and offers nothing.
- [ ] After a decline, re-running the suite and re-rendering a report leave the
      state declined — the bucket key does not move.
- [ ] After a decline, **adding a new baseline package under `src/` re-fires the
      offer by itself**, with no human re-opening step.
- [ ] After a decline, **removing a baseline package also re-fires** — the name
      set changed, so the question changed.
- [ ] The decline question text is constructed in exactly one place, and embeds
      sorted baseline names rather than a count of them.
- [ ] Answering the identical question again with acceptance makes the comparison
      live, with no code path specific to reopening.
- [ ] Accepting the comparison, and only then, materializes the benchmark package
      via the second flow's wiring-first rung.
- [ ] Both scaffold mappings (engine and `materialize.py`) agree, enforced by a
      test rather than by review.
- [ ] Every `_Benchmark` reference in both test files is either updated or
      explicitly classified as a generic fixture.
- [ ] The doctrine prose sweep leaves no document naming the old destinations,
      the old block count, or the old gap count.

## Citation verification

Every symbol this proposal repeats was located in the source by name during this
phase, not inherited on trust: `scaffold_destinations`, `scaffold_gaps`,
`scaffold_kit_source`, `harness_destinations`, `harness_kit_source`,
`previous_implementations`, `_answered_discussions`, `_discussion_buckets`,
`_stage_objects`, `resolve_benchmark_declaration`, `PROBE_NEXT_STEPS`,
`KIT_SEAL`, `_report_findings_question`, `_piloted_discuss_entry`,
`_pilot_decision_question`, the kit notebook's import line, and both
`materialize.py` mapping sites. All resolved.

Two inherited claims did not survive checking and are corrected above: the
post-change gap count (ten/twelve, not nine/eleven — `exploration.md` has since
been patched to agree), and "`openspec/specs/` is empty" (it holds 41 specs; the
conclusion survives, the premise does not).

The Q3 precedents were verified as quoted, not paraphrased on trust.
`_report_findings_question`'s docstring does state that finding names are
embedded because *"a finding appearing or clearing IS a change of state, and
re-asking then is the point"*, and does refuse a row count for the stated reason.
`_piloted_discuss_entry` does document the stability rule the other two
constructors cite. One detail the brief did not mention, found while checking and
carried into the end state: `_answered_discussions` returns question text only,
so it cannot by itself supply the decline date required by Q2.
