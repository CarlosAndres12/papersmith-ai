# Design: the-comparison-nobody-asked-for

**Phase**: design · **Artifact store**: hybrid (Engram `sdd/the-comparison-nobody-asked-for/design`)
**Upstream**: `proposal.md` (revision 2), `exploration.md` (corrected)
**Subject**: `.claude/skills/_core/implementation/engine/implementation_engine.py` and
`.claude/skills/proposal-implementation`

> **Size note.** The `sdd-design` skill sets an 800-word budget. The owner's two
> binding directives for this change — cover everything, and prove no regression
> consumer by consumer — cannot be satisfied inside it. The same explicit-contract
> override the proposal took applies here. Every section below is required by one
> of those two directives.
>
> **Citations.** Every symbol repeated below was located in the source by name
> during this phase, never inherited on trust. Symbol names, not line numbers:
> `sdd-spec` is editing in parallel and every line citation in every upstream
> document is stale the moment either lands. Four inherited claims were checked
> and failed; they are reported in §1 rather than worked around.

---

## 1. What the proposal got wrong

Four upstream claims did not survive checking. Three of them change the work.

### 1.1 The benchmark package's `__init__.py` is not the benchmark's file

**Claim**: `src/<Package>_Benchmark/__init__.py` carries the benchmark declaration,
so removing it from the scaffold costs only `__benchmark__`.

**Measured**: the kit scaffolds **four independent top-level literals** into that
file (the live target carries a fifth — see below), and three of the four have
nothing to do with a comparison:

| Literal | Resolver | What it governs | Benchmark? |
|---|---|---|---|
| `__benchmark__` | `resolve_benchmark_declaration` | arms, search, report, distribution, entry, revision, premises | yes |
| `__levels__` | `resolve_levels_declaration` | the position rung ladder | **no** |
| `__steps__` | `resolve_steps_declaration` | the declared flow: order, `produces`, `placement`, jobs | **no** |
| `__records__` | `resolve_records_declaration` | named records a `@record:level` witness reaches | **no** |

Each of the three sibling resolvers opens with `bench_root.is_dir()` and returns
`[]`/`{}` when it is absent. Their own docstrings say they are "held apart from
`__benchmark__`" precisely because "a target may declare a step long before it has
answered a single one of `__benchmark__`'s seven blocks, or never answer any of
them at all". They are read by `cmd_probe` (`probe_steps`, `position_state`,
`pilot_completeness_state`, `walk_state`, `flow_acts`, `flow_destination`),
`cmd_verify` and `cmd_step` — every one of them a Flow A command.

**Not theoretical — measured on the live target.**
`implementations/Domain_Adaptation/src/MIL_CREDA_Benchmark/__init__.py` declares
`__levels__ = ["none", "pilot", "remote"]`, a non-empty `__records__` (one entry
with a real path and a full `requiredScale`), and a non-empty `__steps__`. The
target's whole position ladder, record grading and declared flow live in that file
today, beside a `__benchmark__` whose `revision` is `"research-concept-r17.md"`.

**And a fifth literal the kit does not scaffold and nothing reads.** That same file
declares `__environment__` (an `install.requirements` list for a remote worker).
Measured: the string `__environment__` appears **nowhere** under `.claude/` or
`tests/` — no resolver, no constant, no test. It is target-authored, has zero
readers anywhere in the forge, and is invisible to every count in this change.
(Note on method: a repository-wide `rg` misses it because `implementations/` is
git-ignored; it was found by reading the file and confirmed by two scoped greps.)
It is **out of scope** — a pre-existing wired-to-nothing declaration, not this
change's to fix — but the migration in §7 must carry it, or splitting the file
silently drops a declaration its author wrote deliberately.

**Consequence.** Movement 3, as scoped, deletes the only scaffolded home for the
target's own flow declaration. The engine keeps answering (empty is a legal
answer), so nothing goes red — the operator simply has nowhere to write
`__steps__`, and the extensive guidance comments that are the only place the forge
documents those three shapes at the point of use disappear with the file. Writing
the file by hand resurrects exactly the directory this change exists to remove.
That is a silent loss of function, which is the class the owner's second directive
forbids. **Designed for in D2.**

### 1.2 `revision` has two readers, not one

**Claim** (exploration fact 3, repeated by the proposal): "`revision` IS consumed,
but only at engine :15614-15631 as `built_against` feeding `changed_sections` —
benchmark-drift machinery only."

**Measured**: `cmd_verify` reads it **twice**.

- `built_against = declaration.get("revision")` inside the `benchmark` block — the
  drift reader the exploration found; and
- `declared_revision = (resolved["contract"] or {}).get("revision")`, higher up,
  under the comment *"Which revision everything below is measured against … the
  bench's own declared revision first, since that is the binding the check exists
  to age"*. It seeds `family` → `revision_discovery` → `revision`, which drives
  `latestRevision`, `module["stale"]` for every module, `declares_dataset`, and
  through it `structure_ok`'s data-directory branch.

So `revision` is not benchmark-local: it is the revision the whole of `verify` is
measured against. Both readers sit behind `resolved["status"] == "declared"`, which
after Movements 2+3 is **false on every Flow A target** — the blocks that made a
Flow A declaration non-blank are exactly the two being moved, and the package is
gone anyway. Left alone, `verify` on a Flow A target would report
`staleRevision: true` with an empty `changedSections`, and would silently fall back
to module provenance for the revision family. **Designed for in D3.**

### 1.3 The transcribed-count sweep is much larger than the proposal's list, and one of the counts is already wrong

The Q1 ruling (derive, never transcribe) has more surface than the proposal names,
and the defect it predicts has **already happened** on a different count:

- `references/usage.md` says *"Eleven values are possible"*, *"The other three have
  no section"*, *"Nine of the eleven publish `resolve`"*, and *"`null` only at
  `nothing-to-compare` and `already-benchmarked`, the two answers"*. The ladder
  holds **thirteen** values today (`NextStepSectionCoverageTests
  .test_every_value_the_cli_can_return_is_accounted_for` pins all thirteen). Those
  four sentences were stale before this change was proposed.
- `cmd_probe`'s own comment says *"Two of the eleven answers publish nothing"* —
  same defect, in the engine.
- `README.md` documents the `nextStep` ladder as five base rungs plus four blocks
  and is not in the proposal's Affected Areas at all. It also names
  `assets/kit/nb/report_digest.py` and draws `src/<Package>_Benchmark/` in a tree.
- `SKILL.md` says `src/<Package>_Benchmark/__init__.py` *"carries one literal,
  `__benchmark__`"* — false today (see §1.1), before this change touches it.
- Count literals also live in engine docstrings: `scaffold_destinations`
  ("eleven"), `scaffold_structure_gaps` ("eleven"), `all_kit_destinations`
  ("Eleven scaffold + three objects + three harness = seventeen"),
  `harness_destinations` ("three"), `_stage_objects` ("scaffold's eleven", "ALL
  SEVEN blocks"), `_declaration_is_blank`/`resolve_benchmark_declaration` and the
  three sibling resolvers ("seven blocks", "seven-block", "eighth shape").

**Designed for in D8**: one derivation rule, applied to every count the change
moves, plus the two counts that were already wrong.

### 1.4 The affected test surface is six files and two sealed corpora, not two

`_Benchmark` appears in `tests/test_proposal_implementation.py` (392),
`tests/test_remote_execution.py` (123), **`tests/seal/corpus.py` (8)**,
**`tests/experiments_seal/corpus.py` (5)**, **`tests/test_experimental_implementation.py` (6)**
and **`tests/test_implementation_pair.py` (5)**; `premises` also appears in
**`tests/test_implementation_domain_lock.py`**. Both `seal/corpus.py` and
`test_implementation_pair.py` hand-build a `src/<X>_Benchmark/__init__.py` fixture
carrying `__benchmark__` (with `revision`/`premises`) **and** `__steps__` — so the
sealed-digest consequence is not "the `probe` case moves". Every sealed case whose
output reads the declaration moves, in **both** corpora. **Designed for in D9.**

---

## 2. Technical approach

One sentence: **the declaration file is split by ownership rather than deleted** —
everything the target declares about *itself* moves into `src/<Package>/__init__.py`
and stays in Flow A; only `__benchmark__`, which declares the *comparison*, follows
the benchmark package into the harness stage — and the probe ladder gains two
rungs keyed on the exact question texts that were asked: one open (`validate`, the
offer to run the method alone against its own stated prediction, with a draft
published beside it) and one terminal (`declined`).

```
                     BEFORE                                  AFTER

  src/<P>/__init__.py      exports, nothing else    exports
                                                  + __implementation__ (revision, premises)
                                                  + __levels__  __steps__  __records__
                                                  + report_digest.py beside it

  src/<P>_Benchmark/       __benchmark__ (7)        __benchmark__ (5: arms, search,
    __init__.py            __levels__               report, distribution, entry)
                           __steps__
                           __records__              written by --stage harness,
                           report_digest.py         only after an accepted comparison
    scaffold stage                                  harness stage
```

Nothing new is invented: the three sibling literals move to a file that is already
an unconditional scaffold destination, the fourth (`__implementation__`) is the
"new top-level literal" the proposal already ruled for, and the harness stage
already exists and already runs behind an accepted comparison.

---

## 3. Architecture decisions

### D1 — `revision`/`premises` become one sibling literal, not two, and not a second `__benchmark__`

| Option | Trade-off | Decision |
|---|---|---|
| A second `__benchmark__` in `src/<P>/__init__.py` | Two files binding one name is the exact "two spellings of one fold" defect `_discussion_buckets` and `ForgeVocabularyDefinitionTests` both exist to refuse | **Rejected** |
| Two bare literals `__revision__` + `__premises__` | Forces `_stage_objects`' gate to be rewritten; the owner ruled it preserved verbatim | **Rejected** |
| One literal `__implementation__ = {"revision": "", "premises": {}}` | Fourth member of the existing `__levels__`/`__steps__`/`__records__` family; the gate's `[block for block in ("revision","premises") if not contract.get(block)]` survives byte-identical against a different resolver | **Chosen** |

Shape mirrors `__benchmark__`'s own machinery one size down:
`IMPLEMENTATION_DECLARATION = "__implementation__"`,
`IMPLEMENTATION_BLOCKS = {"revision": "", "premises": {}}`, and
`resolve_implementation_declaration(target, name)` returning the same
`{status, path, detail, contract}` quadruple with the same
`absent`/`undeclared`/`declared` vocabulary and the same blank-is-undeclared rule
(`_declaration_is_blank` generalized over a blocks mapping rather than taught an
eighth shape — its own docstring forbids the latter). `status` is `"absent"` only
when `src/<P>/` itself is absent, which after the scaffold stage never happens.

**`premises` still has no reader.** Its content stays unvalidated; only its
location changed, exactly as ruled.

### D2 — `__levels__`, `__steps__` and `__records__` move with it

They are Flow A's declarations (§1.1). They travel to `src/<Package>/__init__.py`
and their three resolvers read that root. Implementation detail that matters: the
three resolvers plus `resolve_implementation_declaration` share **one** root seam
(`declaration_root(target, name) -> target / "src" / package_name(name)`), so the
location is written once. `resolve_benchmark_declaration` keeps its own
`bench_root` and is not routed through it — the two roots are genuinely different
questions now, and collapsing them would be the next drift.

**Rejected alternative**: leave the three in the benchmark package and let the
harness stage create them. Rejected because it makes the flow declaration
unavailable until a comparison is accepted, and `probe`'s pilot/walk/position
machinery — all of Flow A — reads it.

**Rejected alternative**: a fifth declaration file. Rejected: the proposal's "no new
file is invented" ruling, and the `src/<Package>/__init__.py` destination already
exists.

### D3 — `verify` reads the revision from the new literal, unconditionally

Both readers found in §1.2 move off `resolve_benchmark_declaration` and onto
`resolve_implementation_declaration`, and the drift half moves **out** of the
`resolved["status"] == "declared"` branch: revision drift is a property of the
implementation, so it must be reported on a target that has no benchmark package
at all. Concretely:

- `declared_revision` ← `resolve_implementation_declaration(...)["contract"]`.
- `built_against`, `changed_sections(...)` and `staleRevision` are computed from
  the same literal and reported in `verify`'s own top-level shape.
- The `benchmark` block keeps `armsReached`/`unreachedModules` and keeps reporting
  `status: "absent"` when there is no benchmark package — which after this change
  is the *normal* pre-acceptance state, so its `absent` note (which today points
  the reader at `structure.scaffoldGaps`) must point at `structure.harnessGaps`
  and must not read as a defect.

This is the single highest-risk edit in the change. It is where "no regression"
is either proven or lost.

### D4 — the probe ladder: `declared` is what routes to `declare-first`, not `absent`

Today `next_step in ("benchmark","piloted") and resolved["status"] in ("absent","undeclared")`
→ `declare-first`. After Movement 3, `"absent"` becomes the ordinary state of every
Flow A target, so that branch would tell every such target to go and fill a file
that deliberately does not exist. The condition narrows to `"undeclared"` only —
the package exists and is blank, which after this change can only follow an
accepted comparison, which is exactly what `declare-first` has always meant.

`"absent"` falls through to the offer (`benchmark`) or, if that offer is already
answered, to `declined` (D5).

### D5 — `declined`: one question text, answered-plus-absent, no free-text parsing

**Decision 5a — the offer's own question is the bucket key.** A decline-specific
question string would mean the operator answers one question and the ladder looks
for a different bucket. So `_benchmark_publication`'s text is produced by a single
new constructor, `_benchmark_offer_question(target, name, baselines)`, and the
ladder's probe calls **that same function**. One construction site, by
construction rather than by discipline — the rule `_pilot_decision_question` and
`_report_findings_question` both state.

Text derives from the target, the name and the **sorted baseline names**, never a
count, inheriting `_report_findings_question`'s stated reason verbatim.
`baselines` is already computed at the top of `cmd_probe` and is threaded into
`facts` rather than recomputed — the discipline `declarationStatus`,
`reportFindings` and `withoutNotebook` already keep in that function.

**Decision 5b — the condition is `answered AND the benchmark package is absent`.**
The engine parses no free text and must not start: nothing in this codebase reads
an answer's prose, and "not now" / "no por ahora" / "later" is not a grammar a
forge should learn. So:

```
next_step == "benchmark"
  and resolved["status"] == "absent"          # nothing was built
  and _benchmark_offer_question(...) in answered
    -> next_step = "declined"
```

Acceptance is expressed by the act the acceptance authorizes —
`materialize --stage harness` — after which the package exists, the condition
falls away by itself, and the ladder proceeds to `declare-first` exactly as it does
today. That is the proposal's "no code path specific to reopening", literally: the
reopening code is the absence of a branch.

This branch is evaluated **before** the `"absent"`-narrowing of D4 and before every
repair override, because a declined comparison must not be told to fix wiring for
a harness that does not exist.

> **Divergence flagged for `sdd-spec`.** The proposal's walkthrough says re-answering
> the same question with acceptance makes the comparison live. Under 5b, answering
> again is recorded but the state stays `declined` until the harness is
> materialized. If the spec's requirement demands the answer alone flip the state,
> the requirement wins and 5b is replaced by an explicit yes/no surface
> (`offer --answer` is the repository's existing closed yes/no mechanism); say so
> and this design adjusts. Free-text parsing is not on the table either way.

**Decision 5c — `declined` is assigned by a bare string literal inside `cmd_probe`.**
Not by a constant, not by a computed value. `NextStepSectionCoverageTests
.all_next_steps()` recovers the ladder's domain by scraping
`next_step\s*=\s*"([a-z0-9-]+)"` out of `cmd_probe`'s own source, and
`NextStepPublicationRosterTests` derives its roster check from that. An indirect
assignment would make the new state invisible to both locks.

**Decision 5d — roster entry.** `"declined": {"kind": NEXT_STEP_TERMINAL,
"drafts": (), "publish": None}` (the key is `wiring: False` until D12 migrates the
roster; `declined` publishes no draft either way), and `declined` joins
`NextStepSectionCoverageTests.NO_SECTION` with its reason written beside the other
three: it is Flow B's own answer to "the person said no", and a section
prescribing steps would invent the work the decline refused.

### D6 — the decline date: a sibling reader over one fold, never an ordering key

| Option | Trade-off | Decision |
|---|---|---|
| Widen `_answered_discussions` to return events | Breaks its live `pilot_undecided` set-membership caller and moves its documented "`_open_discussions`' exact complement" claim, for nothing | **Rejected** |
| Raw `_discussion_buckets` read at the probe site | Puts the trim/last-wins/answered rules in a fourth spelling at a call site — the exact thing `_discussion_buckets`' docstring warns about | **Rejected** |
| Sibling reader over the shared fold | Third reader of one fold, which is the pattern that docstring endorses | **Chosen** |

Shape: `_discussion_buckets` is folded **once** in `cmd_probe` and handed to both
readers, the same "computed once and reused" rule `jobs`, `probe_digest`,
`probe_evidence` and `probe_steps` already keep in that function.
`_answered_discussions` keeps its exact public signature and becomes a thin wrapper
over a pure `_answered_from_buckets(buckets)`; the new
`_answered_event_from(buckets, question) -> dict | None` returns the bucket's last
event when it carries a non-blank answer, and `None` both when the question was
never asked and when its last event is unanswered — silence is never consent.

**The date is display-only.** The `at` field is read off the returned event and
never compared, sorted by, or used to choose between events. Ledger append order
decides, which is `_discussion_buckets`' documented rule and stays entirely inside
that function.

**Where it surfaces.** Terminal steps publish `None`, so there is no `resolve`
sentence to carry a date. `cmd_probe`'s payload gains one reported, never-gating
key with a fixed shape on every call (the "note on every branch" rule
`distribution_state` states):

```python
"comparisonDecision": {
    "state": "declined" | None,   # None whenever the offer stands unanswered
    "at":    "<the bucket event's own `at`, verbatim>",   # display only
    "asked": "<the exact question text that was answered>",
}
```

> **Superseded by D16.** Movement 5 gives the flow a second standing decision, so
> this key is reshaped into `decisions.{comparison,validation}` before it ever
> ships. The fold, the reader and the display-only rule are unchanged.

### D7 — `report_digest.py`: relocation, and `_here()`

`_here()` today returns `package_dir.parents[1], package_dir.name.removesuffix("_Benchmark")`.
At `<repo>/src/<P>_Benchmark/report_digest.py`, `package_dir.parents[1]` is
`<repo>`. At `<repo>/src/<P>/report_digest.py` the depth is **identical** —
`parents[0]` is `<repo>/src`, `parents[1]` is `<repo>`. **Verified by reading, not
assumed.** The suffix strip becomes a no-op and the line simplifies to
`return package_dir.parents[1], package_dir.name`. Three docstring paragraphs in
that file assert the old location and change with it.

`source_digest` covers all of `src/**/*.py` and hashes **the relative path** as well
as the bytes. Relocating the file therefore moves the digest for every target —
see §6, products row P1.

### D8 — every moved count is derived, and the two that were already wrong are removed too

The rule, once: **a count that describes a list is computed from that list at read
time; a count in prose is deleted, not updated.** Applied to every site in §1.3,
including `usage.md`'s already-wrong ladder counts and `cmd_probe`'s own comment.
Where a human genuinely needs a number, the engine's answer carries it
(`scaffold_gaps` already returns the list; `structure_gap_resolutions` already
prints `{missing}`), and prose points at the answer instead of restating it.

Engine docstrings that count a list they sit on top of get the same treatment: the
noun replaces the numeral ("the file paths a `materialize --stage scaffold`
writes", not "the eleven file paths"). This is not cosmetic — `all_kit_destinations`
currently *asserts an arithmetic identity in prose* ("Eleven + three + three =
seventeen") that no test holds and that this change falsifies twice.

### D9 — the lockstep problem: remove the duplication, do not police it

`scripts/materialize.py` does not duplicate a mapping table; it re-implements the
scaffold stage imperatively, at **three** sites, not the two the proposal names:

| Site | What it writes | Touched by |
|---|---|---|
| `package.mkdir` + inline `__init__.py` text | `src/<pkg>/__init__.py` | **Movement 2** — the proposal names neither this site nor this movement's need of it |
| `benchmark_package` + `src_benchmark/__init__.py` copy | `src/<pkg>_Benchmark/__init__.py` | Movement 3 |
| `seal = KIT/"nb"/"report_digest.py"` | `src/<pkg>_Benchmark/report_digest.py` | Movement 1 |

That file already imports `IGNORE_ENTRIES` and `writable_at_scaffold_time` from the
engine, and its own header states the doctrine: *"`writable_at_scaffold_time` used
to be defined twice … a duplicate is exactly how the two could drift without either
copy being wrong on its own."* The design follows that precedent rather than adding
a consistency test: the three sites are replaced by a loop over
`scaffold_destinations(name)` + `scaffold_kit_source(destination, name)` +
`authored_package_init(name)`, imported from the engine. Drift becomes impossible
rather than detectable.

Two properties must be preserved when the loop replaces the three sites: the
`writable_at_scaffold_time` filter on `tests/*.py` (keep it), and the fact that
`materialize.py` accepts a **neutral fixture kit** via its fourth argument (the
loop must resolve kit sources under the passed `KIT`, not under `SKILL_ROOT`, or
the forge's own scaffolding tests start shipping one paper's content).

A test still asserts the two agree — but it now asserts a tautology cheaply
(`materialize.py` writes exactly `scaffold_destinations`), which is the point.

### D10 — where the literals live inside `src/<Package>/__init__.py`, and how drift reads them

`src/<Package>/__init__.py` is the one scaffold destination with **no kit source**:
`scaffold_kit_source` returns `None` for it and `_stage_scaffold` special-cases it
to `authored_package_init(name)`. That property is load-bearing —
`experimental-implementation` ships no `assets/kit/` at all — so it is preserved:
the file stays engine-authored and does **not** become kit-sourced.

`authored_package_init` therefore grows the four literals, prefilled empty, with
their guidance comments, held as a module-level template constant beside it. The
engine's own precedent for exactly this is `_DEFAULT_PYPROJECT`, which states the
reason: *"restated here rather than imported so this file never depends on the
harness for its own production path."* Ordering inside the file: docstring,
`__all__`, then `__implementation__`, `__levels__`, `__steps__`, `__records__` —
declarations after exports, so step 9's `__all__` edits and step 8's declaration
edits do not collide in the same region.

**Why prefilled-empty rather than absent.** `resolve_*`'s blank-is-undeclared
machinery exists because the kit pre-writes the blocks empty; an absent literal
reaches the same `undeclared` verdict by a different path, so the gate is safe
either way — but the comment block naming `prediction`, `statisticalUnit`,
`metric`, `direction` is what SKILL.md step 8 tells the agent to use, and deleting
it would replace a template with an instruction to remember four field names.

**How `SCAFFOLD_DRIFT` reads it.** `_kit_structure_gaps` compares the file's current
sha256 against the receipt's `writtenSha256`. Step 8 writing the declaration, and
step 9 writing `__all__`, are both edits to an already-recorded scaffold
destination — which is precisely what `materialize --authored <path>` exists to
re-seal (`_materialize_authored` rewrites `kind` to `"authored"` and refreshes
`writtenSha256`). **No new drift mechanism is needed, and none is added.** What is
needed is SKILL.md step 8 saying so: today that file is only edited at step 9, so
the instruction exists one step later than it now has to.

---

## 3b. Movement 5 — a declined comparison is not a dead end

**Owner addition, received after the first draft of this design, and re-pinned by
the owner after a first reading of it was wrong.** A declined comparison asks one
further question. No ends it, recorded, and it does not re-fire. Yes is discussed
**in this same skill and this same session**, with the machinery the comparison
offer already uses.

**Not a cross-skill bridge.** Handing off to `experimental-deliberation` was raised
and rejected by the owner. Nothing leaves this skill: no new dependency on another
skill's CLI, documents, assets or state. Every input below is a function this
engine already has.

### D10b — what the validation exercise is (corrected)

> **Revision 3 correction.** Revision 2 read the validation exercise as a *coverage*
> question — "what is declared and not yet proved?" — and built the draft, the
> roster `kind` and the bucket key on top of that reading. The owner rejected that
> framing outright. D11, D12 and D14 below are rebuilt; everything else in revision
> 2 stands. The wrong reading is left named here rather than quietly deleted,
> because the corrected picture is only legible against it.

The live target today runs **two arms** — the method and the prior work — and its
whole apparatus exists to answer *which one wins*.

**The validation exercise is that same apparatus with a single arm**: the method,
on real data, at small scale. The question is no longer which wins. It is **whether
the method does what the proposal said it would do.**

That is why it has no existing name in this skill:

| | asks | against | uses data |
|---|---|---|---|
| the invariant tests | does each formula behave as the document says? | the document, abstractly | **no** |
| the comparison | which of the two wins? | a rival on disk | yes, two arms |
| **the validation** | **does the method do what was claimed?** | **the document's own prediction** | **yes, one arm** |

It is not verification and it is not comparison. It is the proposal put against
reality, alone.

**The yardstick is already written.** `premises` states what kind of prediction the
protocol assumes, over which statistical unit, by which metric, and in which
direction it is judged — the exact shape of a single-arm pass/fail criterion.
Nothing has to be invented. See D17 for the one part of it that is *not* written
and must therefore be asked.

### D11 — `validation_proposal`, rebuilt: a single-arm run, not a coverage report

`wiring_proposal` drafts two arms meeting in one environment. The validation draft
is **that draft minus the rival**, plus the yardstick and a scale. Every input below
is a function this engine already has, and the section that maps onto
`wiring_proposal`'s own half is reused rather than re-derived.

| Draft section | Built from (all existing) | Answers |
|---|---|---|
| `claim` | `__implementation__["premises"]` carried through verbatim, beside its `revision` | what the proposal predicts, over which unit, by which metric, in which direction — the yardstick, already written (D17) |
| `arm` | `wiring_proposal`'s `new` half: the package's modules with their provenance `sections`/`CLAIM_KEY`/`invariants`, and its `needs` (which modules carry the trainable terms, where the backbone enters, what the head predicts over) | what has to be made runnable — **one arm, no rival**. The `baseline` half is dropped; that is the whole difference |
| `data` | `baseline_environment(target, baselines, name)` — backbones, datasets, weights, entry points, acquisition, read statically | where a real setting already exists on disk. Its own docstring's reason transfers exactly: *"the one that already has meaning is the baseline's — it is where its results were obtained"*, and this run is what is there today **without the rival arm** |
| `scale` | the target's own `__levels__`, the lowest rung above the floor; **asked** when `__levels__` is empty | small scale, in the repository's own words — never a number the forge picked |
| `placement` | `__steps__`' own `placement`/`job`/`service` keys, and the knobs `generate-job` accepts | **where it runs** — local or remote, named with both consequences and defaulted to neither (D11a) |
| `evidence` | a proposed `__records__` entry shape: name, path under the product folder, `requiredScale` | where the record lands and what grades it. `@record:level` witnesses already read that shape — **existing machinery, no new artefact** |
| `needs` | asked, never guessed | the reference figure the document reports and the tolerance around it (D14b), what a failure would look like, and the `service` a remote placement would run under (D11a) |

`baselines` is non-empty by construction at this rung — the decline was only
reachable because `previous_implementations` returned something, or the ladder
would have answered `nothing-to-compare` far above. So `data` always has material
to read; it is never an empty section apologising for itself.

`needs` carries `wiring_proposal`'s exact posture, for its exact stated reason:
*"a forge for papers cannot know which models or datasets are reasonable for a
field it has not read, and suggesting from a list would be guessing."* The engine
composes the run; the human calibrates it.

`validation_proposal(target, name, facts)` returns the same
`{status: "draft", instruction, …, needs}` envelope `wiring_proposal` returns, so a
reader who has learnt one draft shape has learnt them both.

**Neutrality.** The question text and the draft use `ARTIFACT_NOUN`, `CLAIM_KEY`
and `SUBJECT_COLLECTIVE` from the profile. Nothing here spells "proposal",
"equation" or "paper" as a literal — `tests/test_implementation_domain_lock.py`
exists precisely to catch that, and `experimental-implementation` shares this
engine.

### D11a — `placement` is its own draft section, and it proposes nothing

> **Owner addition (revision 4).** *"Al igual que en el de benchmark, se debe
> habilitar las opciones de remote, eso es importante."* The acid test is a real run
> that spends machine time, so it must be able to go to a worker — **and the offer
> must say so**, not leave the machinery reachable by accident.

**It is its own section**, not folded into `scale` and not buried in `needs`. Four
reasons, in order of weight:

1. **`flow_acts` BLOCKS on it.** A `__steps__` entry with no `placement` yields
   `ACT_BLOCKED` carrying `PLACEMENT_UNDECLARED_CONSEQUENCE` — *"the flow stops at
   it rather than choosing, and a choice made by default is the one nobody would
   have approved."* A field that halts the walk is not a nicety to nest inside
   another section.
2. **`scale` and `placement` are different declarations.** `scale` answers *how
   big*, `placement` answers *where*. The live target's `__levels__`
   (`["none", "pilot", "remote"]`) happens to spell a placement word as a rung name,
   which is exactly why folding the two would re-create that conflation inside the
   forge instead of leaving it in one repository's vocabulary.
3. **Burying it in `needs` would make it a question with no draft beside it** — the
   opposite of the shape the owner pointed at, where the comparison publishes a
   draft *and* the open question.
4. It is where the remote knobs `generate-job` already accepts get named, so the
   operator meets them at the point of decision rather than discovering them later.

**And it proposes neither option.** The section names `local` and `remote` with the
consequence of each and picks nothing — `flow_acts`' own docstring is the rule:
*"Routing by default is how a campaign measured in days ends up somewhere nobody
chose."* A draft that defaulted the routing would be the defect this engine already
refuses, one layer up.

| Key the section covers | Who answers it | Why |
|---|---|---|
| `placement` | the human | both options named with their cost (D11c); never defaulted |
| `job` | **proposed** by the draft — a folder name derived from the step's own name | `flow_acts` blocks a remote step whose `job` names nothing; the name is mechanical, so proposing it costs the human nothing and unblocks the walk |
| `service` | **asked, never guessed** | the forge's own containment rule: it may read a service name to walk a directory and must reduce it to a count before returning anything, and it cannot discover one either — adapters register lazily, so the registry is empty until somebody names one |
| the accelerator / environment / budget knobs `generate-job` accepts | named as available, answered by the human | naming them is documentation; choosing one would be the forge picking a machine |

### D11b — the remote path needs no new machinery, and that is measured

**Question: does generating a remote job folder differ for a single-arm run?
Answer: no. The work is documentation only.** Evidence, read this phase:

| Mechanism | What it reads | Does it know about arms? |
|---|---|---|
| `flow_acts` | a `__steps__` entry's `placement`, `job`, `service`; then `ACT_GENERATE_JOB` → `ACT_REHEARSE` → `ACT_LAUNCH` by the job folder's own state | **No.** It is generic over any declared step; nothing in it distinguishes a comparison step from any other |
| `jobfolder.generate_job` | `service`, `job_name`, `product`, `repo_url`, `repo_ref`, `clone_paths`, and **either** `run_module`/`run_function` **or** `run_notebook` | **No.** Its whole contract is module-or-notebook; it names no arm, no benchmark package, no comparison |
| `resolve_clone_paths()` | cross-checks declared clone paths **against what the declared entry modules actually import** | **It adapts by itself.** One arm imports fewer packages, so fewer clone paths are required — validated by the identical check, with no single-arm branch |
| `--run-notebook` | exists *"so that what a worker runs can be the notebook the pilot ran, rather than a second implementation of it"* | **It is the acid test's own shape**: D15a says the acid test uses the notebooks already chosen, and this is the flag that carries exactly that |

So a single-arm step produces a job folder identically to a comparison step. **No
change to `remote-execution` is needed and none is proposed** — no blocker was
found there.

**Where the job folder lands, and why D15a is satisfied.**
`jobfolder` builds `<target>/tools/<service>/<job-name>/` (`TOOLS_DIRNAME`). That
path is **outside all three `materialize` stage lists** — it is `remote-execution`'s
own output, not a kit destination — so generating a job folder for an acid test
cannot touch `harness_destinations()` even in principle. `tools/` is added to
D15a's positive domain below.

> **Adjacency, reported and deliberately not designed.** `generate_job` accepts
> `environment_requirements` / `environment_index_url`, and the live target's unread
> `__environment__` literal (§1.1) holds exactly `install.requirements`. That is
> almost certainly its intended consumer, and the acid test's remote path is where a
> future change would wire it. **Out of scope here** — wiring it is a reader for a
> literal this change deliberately does not give one. Named so the next person
> finds it.

### D11c — what the offer must state about cost

The repository's own doctrine is that a choice made without its consequence is not a
decision, and the comparison's gate states its cost before the choice. The acid-test
offer states, in the published question:

- that it is a **real run on real data** and spends machine time — the fact that
  separates it from the invariant tests, which spend none;
- **local**: it occupies this machine for the duration;
- **remote**: it spends **metered quota on a service account**;
- that the scale being offered is the small one named in `scale`, and that a larger
  run is a **different decision** — so accepting this is not accepting the campaign;
- that declining later costs nothing to unwind, because D15a means no
  comparison-named structure was created.

**It states no number, and that is a rule rather than an omission.** The forge
cannot know how long this target's run takes, it may not print a service name, and
this repository already has the failure on record: its one weekly-quota figure lived
in a comment nothing read and did not match reality. A number the forge invented
would be that defect with a fresh timestamp. What the question *does* carry is
derived: the axes of the proposed `requiredScale` and the rung from `scale`, named
as `_search_first_publication` already names its axes with their values. **The cost's
shape is stated; its magnitude is the human's to estimate.**

### D11d — an empty `__levels__` does not constrain placement

**It means the scale is asked. It does not mean the acid test cannot go remote.**
The two are independent declarations, and this was read rather than assumed:

- `flow_acts` takes `placement` from the **step entry**, and consults `levels` only
  for the `_rung_reaches` comparison. Its own fallback line proves the
  independence: with no levels declared it grades by `row["walk"] == "walked"` and
  routes by `placement` exactly as before.
- `resolve_levels_declaration`'s docstring says a step with no `:level` marker is
  two-state and *"never reads this list at all"*.

So with `__levels__` empty: placement is fully available, `job`/`service` behave
identically, and the only difference is that the walk grades the step
walked/not-walked rather than by rung — a **reporting** difference, not a capability
one. The draft's `scale` section asks for the rung; the `placement` section is
unaffected and says so, rather than letting a reader infer that an empty ladder
rules out a worker.

### D12 — roster classification, re-ruled: `experiment`

**I withdraw revision 2's `repair` ruling and agree with `sdd-spec`: the validation
rung is `NEXT_STEP_EXPERIMENT`.** Both of my earlier arguments were artefacts of the
coverage picture and do not survive the correction.

| Argument in revision 2 | Under the corrected picture |
|---|---|
| "It offers no declared scale" | **False.** A single-arm run on real data spends real machine time and declares a scale of its own — the `scale` and `evidence.requiredScale` sections of its own draft. `PROBE_NEXT_STEPS`' own hard rule: *"`search-first` launches a search, which declares a scale of its own and is an experiment by this skill's own hard rule."* A validation run meets that rule on both clauses |
| "`NEXT_STEP_EXPERIMENT_CHOICE` would re-offer the thing just declined" | **False.** That sentence asks about *the declared scale the offer names* — here, the validation run's own small scale, not the declined benchmark's. Accepting this offer **is** entering an experiment, which is precisely where the standing rule says the question belongs |

So: `kind = NEXT_STEP_EXPERIMENT`, choice = `NEXT_STEP_EXPERIMENT_CHOICE`.
`terminal` and `repair` are both refused — it names work, and the work spends
machine time.

**`wiring` still does not apply.** That flag is read for exactly one thing: whether
**`wiring_proposal`'s** draft rides in the payload. The validation draft is a
different draft, and publishing the two-arm trainability draft beside a single-arm
validation question would be a *wrong* draft, which is worse than a missing one.
The `drafts` registry (below) is unchanged by the `kind` re-ruling — the draft a
rung publishes and the kind it is classified as are independent, which is exactly
why the roster carries them as separate keys.

**Renamed: `validate-first` → `validate`.** The `*-first` suffix is the repair
family's convention (`declare-first`, `env-first`, `wiring-first`, `poll-first`,
`pilot-first`, `report-first`, `search-first`); the experiment family are peer
offers named for what they offer (`benchmark`, `piloted`, `search-first`).
`validate` sits beside `benchmark` as what it is: the other offer to run. No
collision — no `nextStep` and no verb in this CLI carries the name today.

**Consequences of the `experiment` classification**, all of which are deliverables
rather than side effects:

- `NextStepPublicationRosterTests.test_the_experiment_steps_are_the_ones_that_spend_machine_time`
  asserts `["benchmark", "piloted", "search-first"]` — becomes four, and its
  docstring ("Three answers reach that point") changes with it.
- `usage.md`'s *"Three answers reach that point — `benchmark`, `piloted` and
  `search-first`"* is another transcribed count this change moves (§1.3's class,
  one more instance).
- `validate` prescribes work, so it needs its own `### nextStep: "validate"`
  section in `SKILL.md` and must **not** join `NO_SECTION`. `declined` still joins
  it.

**How the second draft rides.** The roster's `wiring: bool` becomes
`drafts: tuple[str, ...]` over a `PROBE_DRAFTS = {"wiring": …, "validation": …}`
registry, and `cmd_probe` builds `{d: PROBE_DRAFTS[d](target, name, facts) for d in entry["drafts"]}`.
Rejected alternative: a second boolean beside `wiring`. The roster exists because
*"adding a second literal beside the first would have reproduced that defect one
value later"*, and `STRUCTURE_GAP_STAGES` states the same rule for stages — a third
draft must have one place to be classified, not a third flag. Both builders take
the `publish` signature `(target, name, facts)`, so there is one shape to learn.

**Output shape is preserved.** `cmd_probe`'s public `"wiring"` key is unchanged for
every existing rung; a sibling `"validation"` key is added, both always present and
`None`-valued when not applicable (`distribution_state`'s "note on every branch"
rule). `baselines` is already threaded into `facts`; nothing is recomputed.

### D13 — where it sits, and what it does not shadow

The decline stops being a single state and becomes two settled questions:

```
next_step == "benchmark"  and  benchmark package absent
  ├─ comparison offer UNANSWERED ................... benchmark  (the offer to compare)
  ├─ comparison answered, validation UNANSWERED .... validate   (the offer to run one arm)
  └─ comparison answered, validation answered ...... declined   (terminal, both dates)
```

The owner's own sequence, in his order: comparison offered → declined →
**validation offered** → declined → it ends there, both refusals recorded under the
persistence and re-fire rules already designed. Accepting *either* offer enters
that offer's flow. Nothing materializes until an offer is accepted.

`declined` therefore **keeps** its terminal meaning — both questions settled,
nothing owed — rather than becoming a terminal state with an open question behind
it. That failure mode has a name here: it is exactly why `piloted` is in
`NO_SECTION` (*"its own rule keeps a question open, and an open question is work"*).

**Placement: last among the overrides**, after `report-first`, guarded on
`resolved["status"] == "absent"`. Consequences, both intended:

- It **shadows nothing**, by construction: every other override is an earlier
  `elif`, so any genuinely owed repair — including `pilot-first` and
  `pilot-decisions`, which read the target's own declared flow and have nothing to
  do with the comparison — still outranks it. A declined comparison must not hide
  work the flow already agreed to.
- The risk is one-directional and therefore checkable: something else shadowing
  *it*, leaving a declined target reporting a benchmark-flavoured repair forever.

**Proof obligation (one-directional, enumerated).** With
`resolved["status"] == "absent"`, walk all five remaining overrides and show each
is unreachable: `declare-first` (both branches — the first is closed by D4, the
second reads `report.get("live") == "undeclared"` and is **not** conditioned on the
declaration status, so it must be measured, not assumed), `env-first`,
`wiring-first`, `poll-first`, `search-first`, `report-first`. Any branch that turns
out to be reachable is re-examined, never suppressed. This is a named task, not an
assertion this design makes on trust — the `declare-first` second branch is the one
I could not settle by reading alone.

One consequence of D12's re-ruling that cuts the other way and is worth stating:
`validate` is now an **experiment**, and the repair overrides above it are exactly
the states in which launching a run would be wrong. Placing it last is therefore no
longer only a shadowing argument — it is the same argument `_pilot_first_publication`
makes about not offering a run at a state where nothing has been produced. The
placement was right for a weaker reason and is right for a stronger one.

**Both are bare string literals** in `cmd_probe`, for D5c's reason.
**`validate` prescribes work, so it needs a `### nextStep: "validate"` section in
`SKILL.md`** (`test_every_prescriptive_next_step_has_its_own_section`) and must
**not** join `NO_SECTION`. `declined` still joins it.

### D14 — the validation bucket key, re-derived from the corrected picture

The question to answer is not "what is unproved" (revision 2's error) but **what
makes a prior "no" stale for a single-arm run of the method against the
proposal's own prediction.** A "no" becomes a different question when the run being
offered would be *judged differently* or *judged against a different document*.

| Candidate key material | Verdict |
|---|---|
| **`revision`** — the managed document the implementation is bound to | **Chosen.** The document is the reference the run is checked against. A new revision is a new reference, so it is genuinely a different question. Declared-side: a human writes it at step 8 |
| **`premises`** — prediction, statistical unit, metric, direction, rendered canonically | **Chosen.** This *is* the yardstick. Change what is predicted, over what unit, by which metric, or which way wins, and the run being offered is judged by a different criterion. Declared-side for the same reason |
| The sorted declared invariant ids | **Rejected — retracted from revision 2.** They answer a coverage question the owner rejected. They also move on refactors that change nothing about what the method is claimed to do |
| `untested` / test counts | **Rejected.** Achieved-side; shrinks as tests get written while the decision has not changed (`_piloted_discuss_entry`'s stability rule) |
| The method package's own `source_digest` | **Rejected.** It moves on every edit, a typo included — the "climbs on every poll" failure named one level down. The method changing is not the same as what the method *claims* changing, and only the second makes the offer stale |
| The baseline names | **Rejected** — that is the *comparison's* key, and this run has no rival arm. Independence below |
| Any count of anything | **Rejected** — the family's standing rule |

Key = target + name + `revision` + `premises`. **How `premises` enters the key is
ruled in D14a**, because it is the one place where the stability rule and the
"`premises` keeps no reader" ruling appear to pull against each other.

### D14a — `premises` enters the key as its canonical VALUE, not as raw text

> `sdd-spec` chose raw verbatim text and asked for this to be double-checked. **I
> am asking `sdd-spec` to adjust.** The argument below is not a preference; it turns
> on a fact about where the engine gets `premises` from.

**The decisive fact: by the time the constructor sees `premises`, there is no raw
text.** `resolve_*` obtains the declaration through `read_declaration`, which parses
the literal — every caller in the engine treats the result as a Python object
(`contract.get("revision")`, `declaration.get("arms")`, `arms.items()`). Embedding
"the raw bytes verbatim" would therefore require the engine to go back to the file
and slice the source a *second* way, alongside the parse it already did.

That inverts the conservatism argument. Raw text is not the smaller surface — it is
**new** surface, and it is a second spelling of "read the declaration", which is the
exact defect `resolve_benchmark_declaration` exists to have closed (*"no second, ad
hoc way left to spell 'the declaration'"*). The canonical value uses only what the
resolver already hands over.

**And raw text fails the stability rule on four counts, all of which the parse
already discards for free**: re-indenting, changing quote style, reflowing a long
line, and adding a trailing comma all move the bytes while the declared criterion is
identical. Under a raw-text key the flow re-asks for the acid test after a cosmetic
edit — the coordinator's concern is correct, and it is exactly what
`_report_findings_question` refuses when it rejects a row count and what
`_piloted_discuss_entry` refuses when it derives from `declared` rather than `ran`.
Only **key order** survives parsing, and sorting removes it.

**Does sorting reopen the closed ruling? No — and here is the bright line.**

| | permitted | forbidden |
|---|---|---|
| The engine may know `premises` **is a mapping** | ✅ it already does — `BENCHMARK_BLOCKS` declares its empty value as `{}`, and `_declaration_is_blank` compares against it | |
| The engine may know **which keys a mapping ought to have** | | ❌ that is a schema, and it is the ruling the owner closed |

Canonical rendering sorts **whatever keys are there**. It names no field, requires
none, drops none, and refuses nothing — it is a total function from any mapping to a
string, and a function that cannot say "no" is not a validator. Validation is a
predicate; this is a projection.

**Field-name-aware canonicalization is rejected**, and for three reasons rather than
one:

1. It would teach the engine `prediction` / `statisticalUnit` / `metric` /
   `direction` — four names that today live only in the kit asset and `SKILL.md`,
   never in the engine. `experimental-implementation` shares this engine and
   `tests/test_implementation_domain_lock.py` exists to catch exactly that.
2. It is a de-facto schema: "these four are the ones that matter" is a structural
   claim about the field.
3. **It under-fires, which is the worse failure.** A fifth key added to `premises`
   would change the declared criterion and *not* move the key. A key that fails to
   move when the decision genuinely changed is worse than one that moves when it
   has not.

**Shape.** `premises` is rendered from the parsed value with keys sorted and the
render normalized; a `premises` bound to something that is not a mapping is rendered
as its normalized value, the same silent-rather-than-crashing rule
`resolve_levels_declaration` applies to a non-list `__levels__`. **Rendered inline
and readable, never digested**: the key is question text a human reads in the
ledger, and the family's precedent is that the question *names* the thing — finding
names, step names, `_search_first_publication`'s axes with their values. Sixty-four
hex characters in the middle of a sentence is not a question anybody answers.

**If `sdd-spec` holds raw text, its requirement wins and this adjusts** — but the
adjustment would then owe the source-slicing machinery above, and would owe an
explicit statement that a re-indent re-asks a settled question.

**Independence of the two decisions, stated because it looks like a bug.** If a
baseline appears or disappears, the *comparison* key moves, that bucket goes
unanswered, and the ladder reports `benchmark` — the validation question is simply
not reached, and its own bucket stays answered and stays correct, because neither
the prediction nor the document it is judged against has changed. Declining again
lands straight back on `declined` without re-asking. Intended, not a missed re-fire.

**One constructor, one spelling**, same obligation as D5a:
`_validation_offer_question(target, name, revision, premises)` is called by
`_validate_publication` and by the ladder probe, and a test asserts the two are
byte-identical plus a source scan proving the ladder uses the constructor.

### D14b — `premises` gains a use without gaining a reader

> The owner's ruling that `premises` keeps no reader **stands**. This states its
> exact form, because Movement 5 is the first moment in the skill's life where that
> field has a use at the point of use, and a reader arriving later would otherwise
> read the carry-through as a half-built validator.

| The engine **does** | The engine **does not** |
|---|---|
| carry `premises` through into the draft's `claim` section | validate or interpret it |
| render its parsed value canonically into the bucket key (D14a) | name any field, require any field, or drop any field |
| know it is a mapping — `BENCHMARK_BLOCKS` already says so | know which keys a mapping ought to have |
| keep `_stage_objects`' existing non-blank existence check, unchanged | refuse on its content, ever |

This is exactly the relationship `wiring_proposal` already has with
`__provenance__`: it reads it, hands it back, and judges none of it. **Transport,
not interpretation.**

**Boundary test, and it is the point of the ruling**: a `premises` whose keys are
nonsense, or whose `direction` reads `"sideways"`, produces a draft quoting it and
refuses nothing. That assertion is what stops a future contributor from adding
validation "while they are in there" — which would reopen a closed decision and
expand this change's scope.

**And the one part of the yardstick that is not written.** `premises` gives the
unit, the metric and the direction; it does **not** give a threshold, and with a
single arm there is no rival to be better than. The reference figure is the one the
*document* reports — which is why the draft's `needs` asks for it and names the
`revision` it is bound to, so the human knows which document to read it from. The
engine does not parse a number out of prose, and would be wrong to: `report_state`'s
own `proseNumbers` finding treats a measurement typed into prose as a defect class.
The yardstick's *form* is written; its *calibration* is asked.

### D15 — what an agreed acid test produces, and the one structure it may never create

The owner drew the first consequence himself, and it is also this design's own
consistency test: **inventing a stage here would reintroduce the exact defect this
change removes** — machinery built before anyone asked for it.

#### D15a — INVARIANT: an accepted acid test creates no benchmark-named structure

**Owner's hard constraint, stated positively and negatively.** Accepting the acid
test **must never create `src/<Package>_Benchmark/` and must never run the harness
stage** — not the declaration file, not `benchmark.py`, not `verdict.py`, not
`probe.ipynb`. **No member of `harness_destinations()` may be written by it.** The
harness stage belongs to an accepted *comparison* and to nothing else.

**The reason is naming, and it is the owner's.** A single-arm run of the method
against its own declared prediction is not a benchmark. Putting it under a package
called `_Benchmark` would name it as something it is not — and this change exists to
stop structure appearing for work nobody asked for. Creating comparison-named
structure for a non-comparison is the same defect wearing the opposite mask.

**Positively: the whole domain an accepted acid test may write to.**

| Destination | Already exists because | Written by |
|---|---|---|
| `src/<Package>/__init__.py` — a `__steps__`, `__records__` and/or `__levels__` entry | scaffold stage; D2 put the target's own declarations here | the agent, re-sealed with `materialize --authored` (D10) |
| `src/<Package>/*.py` — the method's own modules | scaffold + objects stages | the agent |
| `tests/*.py` | scaffold + objects stages | the agent |
| `<Name>/Notebooks/verification.ipynb`, and whichever notebooks are chosen for the run | scaffold stage | the agent |
| `<Name>/Results/…` — the record the run produces, at a path that does **not** borrow the comparison's name | the product folder already exists | the run |
| `tools/<service>/<job-name>/` — a job folder, when placement is `remote` | `remote-execution`'s own output root (`TOOLS_DIRNAME`), **outside all three `materialize` stage lists** | `remote_cli generate-job` (D11b) |
| the other packages already in `src/` | they are the prior work already on disk | nothing — read only |

**The invariant is satisfied by construction, not by a guard bolted on**, and that
is a direct dividend of D2: because split-by-ownership already moved `__steps__`,
`__records__` and `__levels__` into `src/<Package>/__init__.py`, the acid test's
entire declaration surface is *in the method's own package*. There is no path from
declaring an acid test to touching the benchmark package.

**Two places that would leak the wrong name if left alone**, both concrete:

- The kit's `__steps__` example names `module: "Example_Method_Benchmark.steps"`,
  and the live target's follows it. An agent reading that example while wiring an
  acid test would create a benchmark-named module for a non-comparison. The example
  and `SKILL.md`'s new `### nextStep: "validate"` section must name the **method's
  own package** for this case.
- `__records__` paths inherit the same habit — the live target's is
  `…/Results/Benchmark/ceilings.json`. The draft's `evidence` section (D11)
  proposes a record path under the product folder that does not borrow the
  comparison's name.

**Test obligation, stronger than the "writes no file" test below.** After answering
the acid-test question and after wiring and running it: no path under
`src/<Package>_Benchmark/` exists, `harness_gaps()` is unchanged, no receipt entry
carries `stage: "harness"`, and no destination written appears in
`harness_destinations(name)`. Asserted against the list rather than against a
literal path, so a future contributor cannot quietly route the acid test through the
harness stage by adding a fourth harness destination.

#### D15b — acceptance itself materializes nothing

- **Acceptance** is the validation bucket carrying a non-blank answer. Nothing
  more, and nothing is materialized by it. This composes with D15a rather than
  replacing it: D15b says *nothing appears on acceptance*, D15a says *what may never
  appear at all*.
- **The run is written into surfaces that already exist**: a `__steps__` entry in
  the package init, which `cmd_step` already executes in isolation under the
  target's own venv; a `__records__` entry naming where its record lands and at
  what scale; a `__levels__` rung naming the small scale it runs at; and
  `<Name>/Notebooks/verification.ipynb`, already scaffolded and already the notebook
  Flow A executes and stamps. **No fourth stage, no new kit asset, no new
  destination, no new `materialize` mode.** The draft's `evidence` and `scale`
  sections (D11) propose exactly these entries, which is why accepting it needs no
  machinery built for it.
- **The evidence shows up in readers that already exist**: `@record:level` grades
  the record it produces, `walk` and `pilotCompleteness` move as the step runs, the
  seal restamps. There is no new state to track, which is why there is no new
  machinery to build.

**The engine records that the question was answered and when — never what the
answer said.** D5b forbids parsing free text, and that holds here too: `state` can
only be `"answered"` or `None`. The prose lives in the ledger, the agent reads it
and speaks it; the engine emits the code, the date and the nouns.

### D16 — `decisions`, replacing D6's `comparisonDecision`

D6's single-decision key is not yet shipped, so it is reshaped rather than
extended. One reported, never-gating key, fixed shape on every `probe` call, both
members always present:

```python
"decisions": {
    "comparison": {"state": "answered" | None, "at": …, "asked": …},
    "validation": {"state": "answered" | None, "at": …, "asked": …},
}
```

`at` is read off the bucket event and is **display only** in both members — never
compared, never sorted by, never a tiebreak. Ledger append order decides, inside
`_discussion_buckets`, unchanged. D6's `_answered_event_from` serves both members;
the single fold stays a single fold.

---

## 3c. Movement 6 — a decision already taken can change

> **Revision 5.** Units 1, 2, 4, 4b and 3 are applied and green
> (`b493151` → `432da9f` → `45eae9d` → `cb965c4` → `330c5f1`). Movement 6 is
> designed against **what the code now is**, per each unit's own reported
> divergences — not against this document's earlier prose. Three corrections from
> those reports are load-bearing below and are stated first.

### D17 — what the shipped code actually does (read before designing)

| Design prose said | The code does | Source |
|---|---|---|
| D13: the three-way branch sits "last among the overrides" | **True today** — but only because Unit 3 moved it there. Unit 4b shipped it **first**, which made `declined` beat every repair unconditionally; Unit 3 corrected it and added an explicit `resolved.status != "absent"` guard on `report-first`, the one repair override that reads the benchmark declaration without being naturally shielded when absent | Unit 3 report, task 3.14 |
| D5b: acceptance = materializing the harness | **Shipped, and proved by a test that a bare re-answer alone does NOT reopen it.** That test is the exact hole Part A now fills | Unit 4 report, task 4.11 |
| D11c/D14b: the published acid-test question carries `scale`'s axes | **It does not.** `_validation_offer_question` has a literal 4-parameter signature; the published question carries fixed cost-shape prose only, and the scale axes live in the draft | Unit 4b report, task 4b.5 |

Movement 6 builds on the code as described in the right-hand column. Where this
document's revision-4 prose disagrees with it, **the code wins** — that is the
lesson Unit 4b learned expensively and Unit 3 acted on.

### D18 — the reopening hole, and why my earlier reasoning was wrong

Today `declined` means: the question was asked, an answer exists, nothing is built.
A person who answers *"yes, let's compare"* and then does not build it — waiting on
quota, away for a month — keeps being reported `declined` forever, because the
bucket counts as answered. **The only exit is building the thing**, and nothing
surfaces the contradiction between the report and their own decision.

I dismissed this in revision 2 on the grounds that the engine does not parse prose.
**That reasoning was false, and the counter-example is in this very skill**:
`cmd_offer` takes `--answer yes|no`, refuses `OFFER_ANSWER_NOT_A_TOKEN` for anything
else, and records the answer as a ledger event — a closed binary domain, machine-read,
with no prose interpreted anywhere. The mechanism I said did not exist has existed
the whole time, one command over.

### D19 — the token goes on `discuss`, not on `offer`

**`cmd_offer` must not be reused, and the reason is in its own docstring.**

| Obstacle | Evidence |
|---|---|
| `offer` events are **deliberately never read back** | *"The appended event is write-only history: once written, no code path under `.claude/skills/**/*.py` ever reads a `kind: "offer"` event's fields back into a later decision."* Reading one back into the ladder would break a stated, deliberate invariant |
| `offer` is bound to a **different question** | Its own text: *"continue the flow as it stands, or change the experiment contract first?"* It carries no question-text field, so two different questions recorded under one kind would have no discriminator — the one-spelling bucket discipline's failure, one layer down |
| `offer` drags in unrelated preconditions | `_require_no_open_defect`, `require_named_product_dir`, a readable `--revision`, job-folder discovery, and **authorization minting**. A decline should not mint a launch authorization |

**Chosen: `discuss` gains an optional closed token.** The prose answer stays in
`answered` (unread by the engine, written for humans); a new `decision` field carries
`yes`/`no`, refusing `DISCUSS_DECISION_NOT_A_TOKEN` for anything else — `cmd_offer`'s
exact refusal shape and exact closed domain, on the surface that already owns these
buckets. Everything Units 4 and 4b shipped is reused unchanged: `_discussion_buckets`,
last-wins, the one-spelling key, `_benchmark_offer_question`,
`_validation_offer_question`, `_answered_event_from`.

**The engine still interprets no free text.** It reads one field whose domain is two
tokens. That is the same act `offer` already performs, and it is not interpretation.

### D20 — reading a bucket with no token: the migration rule

Existing ledgers — the live target's included — hold answered `discuss` events with
no `decision` field. The rule is **absent token reads as `no`**, and that is not a
default chosen for convenience:

- Today the **only reachable meaning** of an answered comparison/acid-test bucket is
  "declined". Units 4 and 4b shipped it, tested it, and there is no way to express
  "yes" at all. Reading a legacy event as `no` preserves exactly what the flow
  already reports for it.
- The alternative — absent token reads as undecided — would re-fire an offer the
  person already declined, on every existing target, on the first pass after this
  lands. That is the silence-becomes-noise failure `_answered_discussions`' own
  docstring refuses in the opposite direction.

So the token **adds the ability to say yes** and changes the meaning of nothing
already written. Products row: no existing ledger event is reinterpreted (P4 holds).

### D21 — `build-first`: one rung for "accepted, not built"

With `decision: "yes"` recorded and nothing built, the ladder must not re-publish the
offer — asking a question already answered is the mirror of the bug being fixed. It
falls through to a new rung.

**One rung, not two**, publishing a branching sentence. The comparison's act
(`materialize --stage harness`) and the acid test's act (declare a `__steps__` entry,
which **D15a forbids routing through the harness stage**) are different, but
`_declare_first_publication` is the precedent for exactly this: one rung assigned from
two conditions, whose publication names which state routed there, with the fact
threaded from the branch rather than recomputed. Two rungs would mean two roster
entries, two SKILL.md sections and twice the corpus churn for one idea.

- `kind`: **`NEXT_STEP_REPAIR`**, `NEXT_STEP_REPAIR_CHOICE`. The decision is made; what
  is owed is the wiring. That is the roster's own definition — *"work whose cost is
  already settled … a run the flow already agreed to"* — and it is why `wiring-first`
  is a repair rather than an experiment. `validate`'s `experiment` classification (D12)
  is unaffected: that rung offers the decision, this one follows it.
- `drafts`: `("wiring",)` when the comparison was accepted, `("validation",)` when the
  acid test was — the draft that tells the person how to build what they agreed to.
- It is **bare-literal assigned** (D5c) and **prescribes work**, so it needs its own
  `### nextStep: "build-first"` section and must not join `NO_SECTION`.
- Placement: inside the same last-among-the-overrides branch Unit 3 established, as a
  fourth arm. **Unit 3's `report-first` guard and branch position are not touched** —
  reordering the chain again is the one thing this unit must not do.

```
comparison bucket / acid-test bucket, benchmark package absent
  ├─ unanswered ..................... benchmark  (the offer to compare)
  ├─ decision "no", acid test open .. validate    (the offer to run one arm)
  ├─ decision "no", both settled .... declined    (terminal, both dates)
  └─ decision "yes", nothing built .. build-first (repair + the matching draft)
```

`decisions.comparison` / `decisions.validation` grow a `decision` member beside
`state`/`at`/`asked`, carrying `"yes"`/`"no"`/`None`. The payload key Units 4 and 4b
shipped keeps its shape and its name.

### D22 — Part B up: test → comparison needs no new machinery

A built acid test, and the person wants the comparison. This **adds** a rival arm; the
question changes from "does it do what it said" to "which wins", and what was measured
does not become wrong — it stops answering the new question.

**The mechanism is D19's token and nothing else.** Re-answer the comparison bucket
with `decision: "yes"` → `build-first` → materialize the harness. The bucket key
already embeds the sorted baseline names, so it is already the right question. No new
rung, no new constructor, no new state. Stated explicitly because the temptation is to
build a "transition" surface for something two existing mechanisms already compose.

### D23 — Part B down: comparison → test discards a question, not work

A built comparison, and the person wants the acid test. Two decisions here, and the
first is the one that matters.

**D23a — the acid-test question must become reachable with a comparison present.**
Today `validate` only fires when the benchmark package is absent, so from
`already-benchmarked` it is unreachable. That is the gap.

**D23b — and what it reports there is not an offer to build.** The owner's own
reasoning: *a comparison already runs the method on that data, so what the acid test
would ask is already measured inside it.* So in this state the rung does **not**
propose a run. It names where the answer already lives — the comparison's own record
and the arm that is the method — and asks whether to change the question being asked
of it. Proposing a second run of a measurement already on disk would spend machine
time to learn something the repository knows, which is this change's own defect class
wearing a third mask.

**D23c — a transition NEVER deletes. It stops asking.** The owner's word was
"limpiar", clarified as removing the rival's arms. The ruling:

| Operation | Verdict |
|---|---|
| Undeclare the rival arm — remove its entry from `__benchmark__["arms"]` | **This is the transition.** It stops the arm being exercised and stops it being reported, which is exactly "stop asking about it" |
| Delete `<Name>/Results/…`, executed notebooks, stamps, ledger events | **Never, and not by the forge at all** |

Three reasons, in order of weight:

1. **Those measurements were paid for with machine time.** This change exists because
   structure appeared for work nobody asked for; **its mirror-image failure is
   destroying structure somebody earned.** A forge that did both would have learned
   nothing.
2. **The forge may not assume recoverability.** The live target happens to be its own
   git repository with zero untracked files, so removals there stay in its history —
   but that is *that target's* property, measured, not a guarantee about any target.
   A destructive act justified by an assumption the forge cannot check is not
   recoverable, it is lucky.
3. **`flow_acts`' own rule**: *"A function that both decided and dispatched would be a
   launch path with no `gate` standing in front of it."* The engine names acts; the
   operator takes them. If a person genuinely wants files gone, that is their act with
   their VCS, and the forge names the consequence without performing it.

**Where the evidence of a run that happened continues to live**, stated because "stop
asking" must not read as "lose": the `<Name>/Results/…` records, the executed notebooks
and their `SOURCES-SHA256` seals, the `__records__` entries that grade them, and the
position ledger. All untouched. An undeclared arm is invisible to `armsReached` and
`unreachedModules`; it is not invisible to anybody reading the Results folder.

**Discussed, never automatic** — same posture as every gate here. The transition is a
`discuss` bucket with its own one-spelling constructor and D19's token.

### D24 — Part C: the anti-leak lock, and a correction to the reported diagnosis

**The reported diagnosis is wrong in its mechanism, and the real one is worse.** The
brief says `derived_denylist()` cannot see the repository's directory name. It already
does: `target_words` runs `words.update(self.split(target.name))` on every directory
under `implementations/`. Three layers were measured this phase:

1. **`split` decomposes the name, and the parts are legitimately forge vocabulary.**
   `WORD_SPLIT_RE` breaks on punctuation and camel-case, so `Domain_Adaptation` becomes
   `{"domain", "adaptation"}` — and **`"adaptation"` is the first entry in
   `FORGE_LEXICON`**, admitted with a stated reason ("ordinary English in doctrine prose
   about an arm with its adaptation switched off"). `derived_denylist` subtracts the
   lexicon, so the parts are removed and **nothing target-specific survives**.
   Decomposition destroyed the only identifying thing about the name: **the
   composition.**
2. **Even in the denylist, the compound would not match.** `leaks()` searches
   `\b{word}\b`, and `_` is a regex word character — so `\bdomain\b` does not match
   inside `Domain_Adaptation`. Only the compound as its own denylist word matches it.
3. **And the scan surface is `.claude/skills/` only** (`SCAN_ROOT = SKILLS_ROOT`), so
   `tests/` is never looked at. That is why 28/28 passes with the mention sitting in
   `tests/test_proposal_implementation.py`.

**The class, stated properly**: *any target whose directory name is a compound of
otherwise-ordinary words is invisible to Rule B* — `Domain_Adaptation`,
`Image_Segmentation`, `Language_Model`. Teaching the walk to "see directory names"
would fix nothing, because it already sees them.

**The fix, therefore, is to derive the compound as a word in its own right, in addition
to its parts.** A compound of admitted words can still identify a target, and each
part's admission into the lexicon was argued on its own merits — arguments that do not
extend to the whole. Layers 2 and 3 are named as separate, smaller deliverables so a
future reader knows which of the three closed.

The instance — the fixture comment Unit 2 added — is removed and reworded to say **"a
live target"**, never which. Zero occurrences under `.claude/`, so the shipped skills
are clean and this is a test-surface fix, not a doctrine leak.

---

## 4. Consumer-by-consumer no-regression table

Every reader, writer and asserter of everything being moved. "Adjusted" rows are
the proof obligation; "untouched" rows are proof that the blast radius stops.

### 4a. `report_digest.py` (Movement 1)

| Consumer | Reads today | After | Class |
|---|---|---|---|
| `scaffold_destinations` | `src/<P>_Benchmark/report_digest.py` | `src/<P>/report_digest.py` | adjusted |
| `scaffold_kit_source` | key `src/<P>_Benchmark/{KIT_SEAL.name}` | key `src/<P>/{KIT_SEAL.name}`; value `KIT_SEAL` unchanged | adjusted |
| `KIT_SEAL` constant | `assets/kit/nb/report_digest.py` | identical — the **kit source** does not move | untouched |
| `remote_cli.py` `_load_source_digest` | the kit source path | identical | untouched |
| `jobfolder.py` | a docstring example naming sibling imports | identical | untouched |
| `verification.ipynb` | `from {{PKG}}_Benchmark import report_digest` | `from {{PKG}} import report_digest` | adjusted |
| `probe.ipynb` | same import | same fix | adjusted |
| `probe.ipynb` `HARNESS = ROOT/"src"/"{{PKG}}_Benchmark"/"benchmark.py"` | harness path | identical — harness stage is correct today | untouched |
| `report_digest._here()` | `parents[1]` + suffix strip | `parents[1]` (same depth, verified) + `package_dir.name` | adjusted |
| `report_digest` module + `source_digest` docstrings | assert the benchmark location three times | rewritten | adjusted |
| `source_digest` coverage | all of `src/**/*.py` | identical set, one member at a new **relative path** | adjusted — see P1 |
| `materialize.py` seal site | writes into `_Benchmark/` | driven by `scaffold_destinations` (D9) | adjusted |
| `scaffold_structure_gaps` / receipt | keyed by destination path | new key; old entry becomes an orphan on live targets — see P2 | adjusted |
| `SKILL.md` step 5 table row | `src/<Package>_Benchmark/report_digest.py` | new path | adjusted |
| `usage.md` worked scaffold-file list | `src/Example_Method_Benchmark/report_digest.py` | new path | adjusted |
| `README.md` kit table + tree | names the kit source (fine) and draws the bench package | tree adjusted | adjusted |
| `tests/test_proposal_implementation.py` | 28 `report_digest` hits | triage + update | adjusted |
| `tests/test_remote_execution.py` | 2 hits, both the kit source | verify, expect untouched | triage |
| `experimental-implementation` | ships no kit; `scaffold_kit_source` resolves to non-existent paths for it today and after | identical | untouched |

### 4b. `revision` / `premises` (Movement 2)

| Consumer | Reads today | After | Class |
|---|---|---|---|
| `_stage_objects` gate | `resolve_benchmark_declaration`, `unwritten = [...("revision","premises")...]` | `resolve_implementation_declaration`, **same two lines**; refusal code, condition and per-block message preserved verbatim; only the path in the sentence changes | adjusted |
| `cmd_verify` `declared_revision` (§1.2) | bench contract | implementation contract, unconditionally | **adjusted — the regression** |
| `cmd_verify` `built_against`/`changedSections`/`staleRevision` | bench contract, inside `status == "declared"` | implementation contract, outside that branch | **adjusted — the regression** |
| `BENCHMARK_BLOCKS` | seven blocks | five; new `IMPLEMENTATION_BLOCKS` holds two | adjusted |
| `_declaration_is_blank` | compares against `BENCHMARK_BLOCKS` | generalized over a blocks mapping; no eighth shape learned | adjusted |
| `resolve_benchmark_declaration` docstring | "seven blocks" ×3 | five, plus the sibling literal named | adjusted |
| `probe`'s `declare-first` rung | `resolved["status"] in ("absent","undeclared")` | `"undeclared"` only (D4) | adjusted |
| `premises` readers | none, by ruling | still none | untouched |
| `_plan_bound_to` / `_materialize_plan_gate` `["revision"]` | the **plan's** `boundTo.revision`, a different fact | identical | untouched |
| `probe_state`'s `recorded.get("revision")` | the **results file's** revision | identical | untouched |
| `assets/kit/src_benchmark/__init__.py` | seven blocks + three sibling literals | five blocks; the three siblings move to `authored_package_init` | adjusted |
| `authored_package_init` | docstring + `__all__` | plus four prefilled-empty literals (D10) | adjusted |
| `materialize.py` package-init site | inline hardcoded text | engine's `authored_package_init` (D9) | adjusted — **not named upstream** |
| `SKILL.md` step 8, step 9, seven-block section, Decision Gates row | the bench path, "seven blocks", "one literal" | new path, five blocks, four literals, plus the `--authored` re-seal instruction (D10) | adjusted |
| `usage.md` `OBJECT_MAP_NOT_APPROVED` row | names the bench path | new path | adjusted |
| `experimental-implementation/impl_profile.py` `OBJECTIVE_FLOW` "standing" stage | describes the gate in its own words | rewritten; behaviour latent (no kit) but the shared-engine gate is real for it | adjusted |
| `tests/test_implementation_domain_lock.py` | 1 `premises` hit | triage | triage |

### 4c. `__levels__` / `__steps__` / `__records__` (consequence of Movement 3 — §1.1)

| Consumer | Reads today | After | Class |
|---|---|---|---|
| `resolve_levels_declaration` | `src/<P>_Benchmark/` | `declaration_root` (D2) | adjusted |
| `resolve_steps_declaration` | same | same | adjusted |
| `resolve_records_declaration` | same | same | adjusted |
| `cmd_probe` `probe_steps` → `position_state`, `pilot_completeness_state`, `walk_state`, `flow_acts`, `flow_destination` | via the resolvers | unchanged call shape, new root | untouched at the call site |
| `cmd_step` (`STEP_MALFORMED`) | `resolve_steps_declaration` | same | untouched at the call site |
| `named_records_state` | `resolve_records_declaration` | same | untouched at the call site |
| `impl_position.level_index` / `_record_scale_level` | the resolved lists | same | untouched |
| kit declaration asset | carries all three with ~150 lines of guidance | guidance travels to `authored_package_init`'s template (D10) | adjusted |
| `tests/seal/corpus.py`, `tests/test_implementation_pair.py` | fixtures write `__steps__` into the bench package | rewritten to the package init | adjusted |

### 4d. The benchmark package itself (Movement 3)

| Consumer | Reads today | After | Class |
|---|---|---|---|
| `scaffold_destinations` | includes `src/<P>_Benchmark/__init__.py` | removed | adjusted |
| `scaffold_kit_source` | maps it to `src_benchmark/__init__.py` | entry removed | adjusted |
| `harness_destinations` | three entries | four, gaining it | adjusted |
| `harness_kit_source` | three entries | four | adjusted |
| `harness_gaps` / `harness_structure_gaps` / `structure_ok` | derived | derived; a Flow A target already has harness gaps today, so `structure_ok` is already `False` there — **no new failure** | untouched in effect |
| `_kit_destination_stage` | derived from the three lists | derived; the path re-classifies scaffold → harness automatically | untouched |
| `all_kit_destinations` | seventeen | same total, redistributed; its prose arithmetic deleted (D8) | adjusted |
| `cmd_verify` `benchmark.status == "absent"` note | points at `structure.scaffoldGaps` | points at `structure.harnessGaps`; must read as a state, not a defect | adjusted |
| `previous_implementations` | no `_Benchmark` rule | `_Benchmark`-suffix exclusion (lands with the constructor, one commit) | adjusted |
| `wiring_proposal`, `benchmark_reach`, `unreached_modules`, `declared_dimension_names`, `report_state`, `search_state`, `distribution_state` | all read `bench_root` or the bench contract | identical — all are behind an accepted comparison already | untouched |
| `materialize.py` benchmark site | writes it at scaffold time | removed (D9) | adjusted |
| `SKILL.md` step 5 table + "Conversion, then benchmark" + Decision Gates | list it as scaffold | harness | adjusted |
| `README.md` ladder + tree | scaffold-time bench package | harness | adjusted — **not named upstream** |

### 4e. The declined state (Movement 4)

| Consumer | Reads today | After | Class |
|---|---|---|---|
| `_benchmark_publication` | a fixed sentence | `_benchmark_offer_question(target, name, baselines)` | adjusted |
| `cmd_probe` `answered` | `_answered_discussions` | `_answered_from_buckets(buckets)` over one fold | adjusted |
| `pilot_undecided` | `_pilot_decision_question(...) not in answered` | identical | untouched |
| `report_unacknowledged` | `_report_findings_question(...) not in answered` | identical | untouched |
| `_discussion_buckets` | two readers | three; the fold, the trim rule and the append-order rule are unchanged | untouched |
| `PROBE_NEXT_STEPS` | thirteen entries, keys `kind`/`wiring`/`publish` | **fifteen** entries (`declined`, `validate`), keys `kind`/**`drafts`**/`publish` (D12) | adjusted |
| `NextStepPublicationRosterTests.test_the_experiment_steps_are_the_ones_that_spend_machine_time` | asserts `["benchmark","piloted","search-first"]` | **four** — `validate` joins; docstring's "Three answers reach that point" changes with it (D12) | adjusted |
| `usage.md` "Three answers reach that point" | a transcribed count | four, or derived (§1.3's class, one more instance) | adjusted |
| `harness_destinations` / `harness_gaps` / the harness stage | written only by an accepted comparison | **identical** — D15a forbids the acid test from reaching any of it, including via a job folder, which lands under `tools/` | untouched, and asserted |
| `flow_acts` / `_step_placement` / `_step_job` / `_step_service` / `ACT_GENERATE_JOB`/`REHEARSE`/`LAUNCH` | route any declared step by its own `placement` | **identical** — generic over `__steps__`; an acid-test step walks the same acts (D11b) | untouched, and asserted |
| `remote-execution` (`remote_cli generate-job`/`submit`, `jobfolder.generate_job`, `resolve_clone_paths`) | module-or-notebook contract, clone paths cross-checked against real imports | **identical, no change proposed** — one arm imports fewer packages and the existing check adapts by itself | untouched, and asserted against an unmodified skill |
| `__environment__` | read by nothing (§1.1) | **still read by nothing** — its likely consumer (`generate_job`'s `environment_requirements`) is named as adjacency, not wired | untouched, deliberately |
| `next_step_publication` | `KeyError` on unrostered | identical | untouched |
| `cmd_probe`'s `proposal = wiring_proposal(...) if ...["wiring"]` | one literal flag | loop over `entry["drafts"]` against `PROBE_DRAFTS` | adjusted |
| `cmd_probe` payload `"wiring"` | the trainability draft or `None` | **identical** for every existing rung; sibling `"validation"` key added | untouched |
| `wiring_proposal` | `(target, name, baselines)` | reached through the `(target, name, facts)` builder signature; `baselines` already in `facts` | adjusted |
| `NextStepSectionCoverageTests.all_next_steps` | scrapes literals from `cmd_probe` | recovers `declined` **and** `validate` only if D5c holds for both | **adjusted — test obligation** |
| `NextStepSectionCoverageTests.NO_SECTION` | three members | four (`declined` joins); **`validate` must NOT** — it prescribes work and needs its own SKILL.md section | adjusted |
| kit `__steps__` example (`…_Benchmark.steps`) and `__records__` path habit | benchmark-named by convention | the acid-test guidance names the **method's own package** and a non-comparison record path (D15a) | adjusted |
| `NextStepPublicationRosterTests.test_exactly_the_two_terminal_steps...` | asserts exactly two | three, renamed | adjusted |
| `NextStepPublicationRosterTests` roster-shape assertions | read `kind`/`publish` | plus `drafts` totality: every entry carries it | adjusted |
| `usage.md` ladder counts | already stale by two (§1.3) | now stale by **four**; derived or deleted | adjusted |
| `cmd_discuss` / `_discuss_command` / `settle` | unchanged surfaces | identical — both a decline and a validation answer are bare `discuss` events and need no `settle` | untouched |
| `experimental-deliberation` (or any sibling skill) | not reached | **still not reached** — Movement 5 adds no cross-skill dependency of any kind | untouched |
| `tests/` kit files, `verification.ipynb`, `__steps__`/`cmd_step` | scaffolded surfaces | identical — D15 writes the exercise into them and materializes nothing | untouched |

---

## 5. File changes

| File | Action | Why |
|---|---|---|
| `_core/implementation/engine/implementation_engine.py` | Modify | `scaffold_destinations`, `scaffold_kit_source`, `harness_destinations`, `harness_kit_source`, `authored_package_init` (+ template constant), `declaration_root`, `resolve_implementation_declaration`, `IMPLEMENTATION_DECLARATION`/`IMPLEMENTATION_BLOCKS`, `BENCHMARK_BLOCKS`, `_declaration_is_blank`, the three sibling resolvers, `_stage_objects`, `cmd_verify` (two revision readers), `cmd_probe` (ladder + one fold + `decisions` + the draft loop), `_benchmark_offer_question`, `_benchmark_publication`, `_answered_from_buckets`, `_answered_event_from`, `PROBE_NEXT_STEPS` (+ `drafts` key), `previous_implementations`, count-bearing docstrings — **and for Movement 5**: `validation_proposal`, `PROBE_DRAFTS`, `_validation_offer_question`, `_validate_publication` |
| `proposal-implementation/scripts/materialize.py` | Modify | three imperative sites → one loop over the engine's own lists (D9) |
| `proposal-implementation/assets/kit/nb/report_digest.py` | Modify | `_here()` one-line simplification + three docstring paragraphs |
| `proposal-implementation/assets/kit/nb/verification.ipynb` | Modify | import line |
| `proposal-implementation/assets/kit/nb/probe.ipynb` | Modify | import line (its `HARNESS` path is untouched) |
| `proposal-implementation/assets/kit/src_benchmark/__init__.py` | Modify | seven blocks → five; the three sibling literals leave |
| `proposal-implementation/SKILL.md` | Modify | step 5 table, step 8 (path + `--authored` re-seal), step 9 gate prose, the seven-block section, Decision Gates, "Conversion, then benchmark", count literals — **and a new `### nextStep: "validate"` section** (D12/D15a: what the acid test is, what it may write to, and that it never creates benchmark-named structure; D11a–d: that it can go to a worker, what placement costs, and that `service` is the operator's to name), the kit `__steps__` example's package name, plus the Flow B prose telling the agent to report both standing decisions and their dates |
| `proposal-implementation/references/usage.md` | Modify | worked scaffold list, `OBJECT_MAP_NOT_APPROVED` row, the ladder counts (already stale by two, now by four), the `resolve`/`null` terminal list, **"Three answers reach that point"** (now four — D12), and the `wiring` → `drafts`/`validation` payload description |
| `README.md` | Modify | **not named upstream** — the `nextStep` ladder and the `src/` tree |
| `experimental-implementation/impl_profile.py` | Modify | `OBJECTIVE_FLOW` "standing" stage |
| `tests/test_proposal_implementation.py` | Modify | bulk |
| `tests/test_remote_execution.py` | Triage → modify | 123 `_Benchmark` hits, fixture-vs-contract |
| `tests/seal/corpus.py` | Modify | fixture writes the declaration; regenerate the seal |
| `tests/experiments_seal/corpus.py` | Modify | second corpus, same reason |
| `tests/test_implementation_pair.py` | Modify | cross-skill fixture writes `__benchmark__` + `__steps__` |
| `tests/test_experimental_implementation.py` | Triage → modify | 6 hits |
| `tests/test_implementation_domain_lock.py` | Triage | 1 `premises` hit |
| No file is deleted | — | `report_digest.py` and the bench `__init__.py` are relocated/re-staged, never removed |

---

## 6. What breaks: producers **and** products

Producers are §4. Products — instances of the old shape already on disk — are the
class that gets forgotten, so each is named with its verdict.

| # | Product | Where it already exists | Verdict |
|---|---|---|---|
| **P1** | **Every stamped report and executed notebook** | `implementations/Domain_Adaptation`, any scaffolded target | **Becomes stale.** `source_digest` hashes each file's path *and* bytes; relocating `report_digest.py` changes a path inside `src/`, so every previously printed `SOURCES-SHA256` stops matching. Expected, mechanical, and it must be announced: the remedy is re-executing the notebooks, never editing a historical stamp. |
| **P2** | **Materialization receipts** (`.implementation/materialization.json`) | every materialized target | **Orphaned entry + one unrecorded destination.** The old `src/<P>_Benchmark/report_digest.py` entry keys a path no list names any more (harmless: `_kit_structure_gaps` iterates destinations, not entries), and the new `src/<P>/report_digest.py` will be written by `materialize --stage scaffold` with a fresh entry. `src/<P>_Benchmark/__init__.py` re-classifies from `scaffold` to `harness` via `_kit_destination_stage`, and its existing receipt entry still matches by path — **no `SCAFFOLD_DRIFT`, no `UNRECORDED_SCAFFOLD`.** Verified against `_kit_structure_gaps`' body. |
| **P3** | **Existing `src/<P>_Benchmark/__init__.py` files** | live target + fixtures | **Falls out of domain, does not become invalid.** It keeps parsing; `revision`/`premises` inside it simply stop being read. See §7. |
| **P4** | **Position ledgers** (`.implementation/position.jsonl`) | live target | **Untouched.** No existing event shape changes. Two new bucket keys can appear (comparison offer, validation offer); buckets are by exact text and never retired, so no historical event is reinterpreted. |
| **P5** | **A pre-existing decline recorded before this change** | live target, if any | **Re-fires exactly once.** The proposal's stated migration consequence, and it is correct under the Q3 rule. Both halves land in one commit so it happens once. The validation question has no pre-existing bucket anywhere, so it simply asks for the first time. |
| **P6** | **Both sealed corpora** | `tests/seal/`, `tests/experiments_seal/` | **Invalidated for more cases than `probe`.** §1.4, now compounded: `PROBE_NEXT_STEPS` gains **two** entries, the roster's `wiring` key becomes `drafts`, and `cmd_probe`'s payload gains `decisions` and `validation`. Regeneration is measured against the regenerated corpus, never assumed. Regenerated in **both** unit 4 and unit 4b — 4 moves the digests and cannot land red waiting for 4b. |
| **P7** | **`probe` results files** (`<Name>/Results/<PROBE_RESULTS>`) | live target | **Untouched.** `probe_state` reads its own `revision` key, a different fact from the declaration's. Verified. |

---

## 7. Migration of the live target

`implementations/Domain_Adaptation` is its own git repository, is already
scaffolded, and carries `revision`/`premises` — plus `__levels__`, `__steps__`,
`__records__` — in `src/MIL_CREDA_Benchmark/__init__.py`. Doing nothing is not an
option: the object-map gate would read the new location, find nothing, and refuse
`OBJECT_MAP_NOT_APPROVED` forever, which the owner explicitly forbade.

| Option | Trade-off | Decision |
|---|---|---|
| Transitional dual read (new location, then old) | Two spellings of one declaration — the exact defect `resolve_benchmark_declaration` was built to close ("no second, ad hoc way left to spell 'the declaration'"). A transitional dual read has no removal date and becomes permanent | **Rejected** |
| A new `materialize --adopt`-shaped migration command | A one-off verb in a CLI whose whole doctrine is that every verb is permanent; `--adopt` already exists and already refuses `ALREADY_RECORDED` for a path with a receipt entry, so it is the wrong tool | **Rejected** |
| **Reported gap + documented manual move, using mechanisms that already exist** | Costs the operator a short, explicit procedure; nothing new is built; the gate keeps refusing loudly until it is done, which is the honest state | **Chosen** |

**Why a reported gap is not "doing nothing".** `resolve_implementation_declaration`
returns `undeclared` with a `detail` naming both the file it looked in and — for
exactly this transition — the fact that the sibling `_Benchmark` package still
binds the blocks. `_stage_objects`' refusal already prints a path; it prints the new
one. The state is loud, specific, and self-describing.

**What the live target's operator does, once:**

1. `materialize --stage scaffold --plan <approved> --seed <seed>` — writes exactly
   `src/MIL_CREDA/report_digest.py` and nothing else.
   `_materialize_scaffold_destinations` subtracts what already exists, so
   `src/MIL_CREDA/__init__.py` is **not** rewritten and no authored content is
   lost. Verified by reading that function.
2. Move four literals by hand from `src/MIL_CREDA_Benchmark/__init__.py` into
   `src/MIL_CREDA/__init__.py`: `revision` (`"research-concept-r17.md"`) and
   `premises` become `__implementation__`; `__levels__`
   (`["none", "pilot", "remote"]`), `__steps__` and `__records__` move verbatim,
   comments and all. **All three are non-empty on this target** — this step is
   where the position ladder, the graded record and the declared flow survive the
   change, not a formality. **`__environment__` moves too** (§1.1): nothing reads
   it, so nothing would report its loss, which is exactly why the procedure has to
   name it. Leave `__benchmark__`'s remaining five blocks where they are — that
   package is now a harness destination and its declaration belongs to it.
3. `materialize --authored src/MIL_CREDA/__init__.py` — re-seals the edited
   scaffold destination. `_materialize_authored` requires an existing receipt entry
   (there is one) and rewrites `writtenSha256`, so `SCAFFOLD_DRIFT` clears.
4. Delete `src/MIL_CREDA_Benchmark/report_digest.py`. Two seals on disk both hash
   into `source_digest`, so leaving it is not a correctness fault — but it is a
   second copy of a file this repository's own doctrine refuses to keep twice.
5. Re-execute the notebooks. P1: the seal moved, so every prior stamp is stale by
   construction. Do not hand-edit a stamp.

**Boundary.** `implementations/Domain_Adaptation` is a separate repository. This
change does not commit into it; the procedure above is documented in `SKILL.md`
and the work unit closes when the documentation and the loud refusal exist, not
when the live target has been migrated.

---

## 8. Testing strategy

| Layer | What | Approach |
|---|---|---|
| Unit | `_here()` at the new depth | assert `parents[1]` equals the repo root for a file at `src/<P>/report_digest.py`; RED first by asserting against the old depth |
| Unit | `resolve_implementation_declaration` | absent / undeclared / blank-is-undeclared / declared, mirroring the existing benchmark-resolver suite |
| Unit | `_stage_objects` gate | same refusal code, same per-block message, same condition, new path — a test that would pass against the old implementation except for the path |
| Unit | single construction (D5a) | `_benchmark_publication`'s question is byte-identical to `_benchmark_offer_question(...)`; plus a source scan of `cmd_probe` proving the ladder calls the constructor rather than a literal |
| Unit | key stability (Q3) | the key moves when a baseline appears and when one is removed; the key does **not** move when the suite is re-run, a module edited, or a report re-rendered |
| Unit | never a count | the question text contains the sorted names and no digit derived from `len(baselines)` |
| Unit | date is display-only | two decline events with **identical** `at` and opposing ledger order; the later one in append order wins regardless of `at` |
| Unit | `decisions` shape | both members present on every `probe` call, `None`-valued rather than absent when a question stands unanswered |
| Unit | `validation_proposal` composes a **run** | on a real scaffolded target it names the method's own modules as the single arm, real data read by `baseline_environment`, a scale taken from the target's own `__levels__`, and quotes `premises` as the yardstick — **a draft the skill cannot compose is a promise, not a mechanism**, so the test asserts non-empty content derived from the tree, never a fixed envelope |
| Unit | the draft has **one** arm | the `baseline`/rival half of `wiring_proposal`'s shape is absent, and the presence of baselines on disk does not add a second arm |
| Unit | acid-test key stability (D14/D14a) | the key moves when `revision` changes and when `premises`' **value** changes; it does **not** move when `premises` is re-indented, re-quoted, reflowed, key-reordered, or given a trailing comma; it does **not** move when a module is edited, a test written, the notebook re-run, the seal changed, or a baseline appears — the last proved explicitly, because it looks like a missed re-fire |
| Unit | key under-fire guard (D14a) | adding a **fifth** key to `premises` **does** move the key — the assertion that rejects field-name-aware canonicalization |
| Unit | `premises` gains no validator (D14b) | a `premises` with nonsense keys, or `direction: "sideways"`, produces a draft quoting it and refuses nothing anywhere in the engine |
| Unit | acid-test single construction | `_validate_publication`'s question is byte-identical to `_validation_offer_question(...)`, plus a source scan proving the ladder calls the constructor |
| Unit | roster totality | every `PROBE_NEXT_STEPS` entry carries `kind`, `drafts`, `publish`; `drafts` names only keys present in `PROBE_DRAFTS`; `validate` carries its own draft and not `wiring`'s |
| Unit | roster kinds | `validate` is `NEXT_STEP_EXPERIMENT` and carries `NEXT_STEP_EXPERIMENT_CHOICE`; the experiment list becomes four |
| Unit | draft/payload isolation | on `validate` the payload's `"wiring"` is `None` and `"validation"` is the draft; on `wiring-first` the reverse — the wrong-draft failure D12 rejects is what this pins |
| Integration | the three-way decline branch | unanswered → `benchmark`; comparison answered → `validate` with a draft; both answered → `declined` with both dates |
| Integration | **nothing materializes on acceptance** (D15b) | answering the acid-test question writes no file, adds no receipt entry, and leaves `scaffold_gaps`/`object_gaps`/`harness_gaps` byte-identical |
| Integration | **no benchmark-named structure, ever** (D15a) | after answering, wiring **and running** the acid test: no path under `src/<Package>_Benchmark/` exists, `harness_gaps()` is unchanged, no receipt entry carries `stage: "harness"`, and no written destination appears in `harness_destinations(name)` — asserted **against the list**, not against a literal path, so a fourth harness destination cannot become a quiet route. **Run once with `placement: "local"` and once with `placement: "remote"`**, so generating a job folder is proved not to be a back door into the harness stage |
| Unit | the offer names placement (D11a) | the published question and draft name both `local` and `remote` with their consequences, propose a `job` name, and **ask** for `service`; the draft picks neither placement — a test that would go red if a default were introduced |
| Unit | the offer states cost, not a number (D11c) | the question names the metered-quota consequence for `remote` and the machine-occupancy one for `local`, carries the proposed scale's axes, and contains **no invented duration, quota figure or service name** |
| Integration | a single-arm step generates a job folder identically (D11b) | an acid-test `__steps__` entry with `placement: "remote"` walks `ACT_GENERATE_JOB` → `ACT_REHEARSE` → `ACT_LAUNCH` through the unmodified `flow_acts`, and `generate_job` accepts it with one arm's clone paths — asserted against `remote-execution` **unchanged**, so the claim "documentation only" is held by a test rather than by this document |
| Unit | empty `__levels__` does not block remote (D11d) | with `__levels__ = []`, a step declaring `placement: "remote"` still routes; only the rung grading falls back to walked/not-walked |
| Integration | no cross-skill reach | the validation path imports, reads and invokes nothing outside this skill and the shared engine — asserted, because "not a bridge" is the owner's ruling and prose cannot hold it |
| Integration | shadow enumeration (D13) | with `status == "absent"`, each of `declare-first` (both branches), `env-first`, `wiring-first`, `poll-first`, `search-first`, `report-first` is shown unreachable; `pilot-first`/`pilot-decisions` are shown to still outrank the pair |
| Unit | neutrality | the validation question and draft spell no domain word; `test_implementation_domain_lock.py` and the `experimental-implementation` pair test both stay green |
| Unit | scaffold/harness membership | `src/<P>_Benchmark/__init__.py` is in `harness_destinations` and not in `scaffold_destinations`; `_kit_destination_stage` answers `"harness"` |
| Unit | derived counts (D8) | `scaffold_gaps` length is computed; a grep-style test asserts no doctrine file states a scaffold-gap count or a ladder count as a numeral |
| Integration | `verify`'s revision readers | on a target with **no** benchmark package: `latestRevision`, `module["stale"]` and `changedSections` still answer from `__implementation__`; RED against today's code |
| Integration | the ladder | `absent` → offer, not `declare-first`; `undeclared` → `declare-first`; answered + absent → `declined`; harness materialized → back to `declare-first` |
| Integration | roster locks | `NextStepSectionCoverageTests` recovers `declined`; it has no SKILL.md section; `NextStepPublicationRosterTests` reports three terminal steps |
| Integration | the two mappings agree (D9) | `materialize.py` writes exactly `scaffold_destinations(name)` |
| E2E | fresh Flow A target | after the scaffold stage **no `_Benchmark` directory exists**, `verification.ipynb` executes and stamps, `previous_implementations` is empty, the flow reports `nothing-to-compare` |
| Seal | both corpora | regenerate, then **read the diff** and account for every moved case — not only `probe` |
| Suites | both | `npm test` **and** the Python unittest suites; this repository has two and one alone has hidden a 13-test regression before |

**Reachability discipline.** Each new refusal/branch is proven reachable by
mutation, not by a passing assertion: invert the guard and watch the test go red.
A refusal that cannot fire reads exactly like a guard.

---

## 9. Threat matrix

**Applicable: no.** This change adds no routing of untrusted input, no shell
command, no subprocess, no VCS/PR automation, no executable-file classification and
no process-integration boundary. `materialize.py` already spawns nothing and gains
nothing; `cmd_probe` remains `kind: "read-only"`; the decline is a ledger append
through the existing `discuss` surface. The one process-adjacent edge —
`materialize.py` resolving kit sources under a caller-supplied kit directory — is
pre-existing and is preserved unchanged (D9), not widened. Recorded as **N/A with a
reason**; no manufactured tasks.

**Movement 5 does not change this, including its remote half.**
`validation_proposal` reads the repository and composes a dict; it executes nothing,
spawns nothing, and reaches no other skill (D15, and the owner's ruling that this is
not a bridge). The exercise itself runs through `pytest`, `cmd_step` and — when
placement is `remote` — `remote_cli generate-job`/`submit`, **all pre-existing
surfaces with their own pre-existing guards, none of which this change touches**
(D11b). `flow_acts` is explicitly pure and issues nothing: *"A function that both
decided and dispatched would be a launch path with no `gate` standing in front of
it."* The acid test names acts; it never takes them.

One row of the matrix is worth marking `Applicable` rather than `N/A` on the
strength of that: **process integration exists here, and it is inherited unchanged.**
The design adds no new subprocess, no new command construction, and no new
argument path — it names, in prose the human reads, commands that already exist and
that the operator runs. The planned check is D11b's integration test, which asserts
the remote walk against an **unmodified** `remote-execution`.

---

## 10. Work units and rollback

Order becomes **1, 2, 4 (any order among themselves) → 4b → 3**, with the scope
corrections carried from §1 and Movement 5 landing as a fifth chained unit.

**Why Movement 5 is its own unit rather than absorbed into unit 4.** It depends on
unit 4 (the constructor family, the terminal state, the single fold) and on unit 2
(`__steps__` living in the package init, which `validation_proposal`'s `surfaces`
section names), and on nothing in unit 3. Folding it into unit 4 would roughly
double that unit past any reading budget; deferring it past unit 3 would leave the
ladder's decline branch half-built across the riskiest unit in the change.

| # | Unit | Scope correction from this design | Rollback |
|---|---|---|---|
| 1 | The seal leaves the benchmark package | `materialize.py` becomes a loop over the engine's lists (D9) rather than two edited sites | Revert restores the old destination. Targets scaffolded in between hold the seal at the new path; recovery is re-running the idempotent scaffold stage, which subtracts what exists and writes the old path back. No data loss — the seal is kit-sourced. Stamps go stale again (P1); re-execute. |
| 2 | The declaration leaves the benchmark package | **grows**: `__levels__`/`__steps__`/`__records__` travel with it (D2), `cmd_verify`'s two revision readers move (D3), `authored_package_init` grows the template (D10), `materialize.py`'s third site (D9) | Revert restores the bench-package read. Targets scaffolded in between carry the literals in the package init; the reverted resolvers read the bench package, find nothing, and the gate refuses loudly — a visible, correct refusal, never a silent pass. Recovery is moving four literals back. |
| 4 | A declined comparison is remembered | Purely additive, plus the `_answered_discussions` wrapper refactor; the `_Benchmark` exclusion stays in this commit | Reverts with no on-disk consequence. One bucket key stops being read; the ledger event stays and is re-read if the unit lands again. |
| 4b | **The acid test** (Movement 5) | new: `validation_proposal` (single-arm run draft, D11) **with its `placement` section** (D11a), `_validation_offer_question` (D14/D14a), `_validate_publication` **stating cost without a number** (D11c), `PROBE_DRAFTS`, the roster's `wiring` → `drafts` migration across every entry, `validate` as a fourth **experiment** (D12) with its own SKILL.md section, the three-way decline branch, `decisions`' second member, the D15a no-benchmark-structure invariant and its local+remote test, the kit `__steps__` example's package name, usage.md's payload + experiment-list counts, both corpora regenerated again. **No change to `remote-execution`** (D11b) | Purely additive over unit 4. Reverting drops one rung and one draft; the decline collapses back to unit 4's two-way branch and stays correct. Any acid-test answer already in a ledger is simply no longer read — buckets are never retired, so it is re-read if the unit lands again. **No on-disk consequence, by D15a+D15b together**: acceptance materialized nothing, and what an accepted acid test did write lives in the method's own package and the product folder, never in benchmark-named structure — so a revert unwinds a rung, never a directory. |
| 3 | The first flow stops creating the benchmark package | **grows**: the `declare-first` condition narrows to `"undeclared"` (D4), `README.md` joins the sweep, the stale ladder counts join the sweep (§1.3), both sealed corpora regenerate (§1.4) | The only unit that changes what exists on disk after Flow A. Reverting restores the bench `__init__.py` to the scaffold list; units 1, 2, 4 and 4b stay correct without it, because the relocated seal and the relocated declaration do not depend on the benchmark package existing. |

**Forecast, restated.** The proposal's ~1930 was already low before this addition —
D2, D3, D9's third site, the README and ladder-count sweep and the second sealed
corpus add material to units 2 and 3. Movement 5 compounds it: unit 4b is a new
engine draft builder with its own test surface, a roster key migration touching
every entry, a new ladder branch, a new SKILL.md section, and a second corpus
regeneration. Order of magnitude, for `sdd-tasks` to replace with a measured
number:

| Unit | Proposal | This design |
|---|---|---|
| 1 — the seal leaves | ~360 | ~400 (D9's loop) |
| 2 — the declaration leaves | ~450 | ~750 (D2 + D3 + D10) |
| 4 — a decline is remembered | ~480 | ~560 (one fold + corpus) |
| 4b — the acid test | — | ~720 (D11 + D11a–d + D12's roster migration + D15a's invariant and test) |
| 3 — the package stops being scaffolded | ~640 | ~800 (D4 + README + counts + both corpora) |
| **Total** | ~1930 | **~3220** |

**Revision 3 moved the composition of unit 4b, not its size** (draft rebuilt, key
re-derived to something simpler; offset by the `experiment` classification's extra
count sites and D15a's invariant test). Net +50.

**Revision 4 adds ~70 to unit 4b, and the number is small for a measured reason.**
The remote capability itself needs **no new machinery** (D11b, evidence-backed), so
what 4b absorbs is: one more draft section (`placement`), the cost sentence in the
published question, the `local`/`remote` split in the integration test, and the
`### nextStep: "validate"` section gaining a remote paragraph. Had `generate-job`
turned out to need a single-arm branch, this would have been a much larger number
and would have argued for splitting 4b; it does not, so it does not.

**Unit 4b remains one unit** at ~720, comfortably inside the 1400-line budget on its
own. `sdd-tasks` owns the final number.

### Revision 5 — Movement 6, forecast honestly rather than optimistically

**What the chain actually measured**, which is the only calibration worth using:

| Unit | Forecast | Actual | Ratio |
|---|---|---|---|
| 4b | ~720 | **~1805** | **2.5×** |
| 3 | ~800 | ~837 | 1.05× |

The difference between them is the whole lesson. Unit 3's work was mostly *new*
surface plus one correction; Unit 4b's ripple ran through **already-shipped tests in
other classes**. Unit 3's own overrun was likewise 446 lines of test file, because one
placement correction touched seven pre-existing tests across two classes plus a class
rewrite. **Test ripple across existing classes is what blows a forecast here, and every
part of Movement 6 has it.**

Part A changes the *meaning* of an answered bucket, which is read by
`DeclinedComparisonTests`, `AcidTestShadowEnumerationTests`,
`DeclareFirstBeforeTheRunTests`, both roster test classes and both sealed corpora —
the exact profile that produced 2.5×. Forecasting it at its "new code" size would
repeat Unit 4b's mistake with the evidence already in hand.

| Part | New surface | Ripple | Forecast |
|---|---|---|---|
| **A** — the token, `build-first`, `decisions.decision` | `discuss --decision`, one refusal code, one rung, one publication, one section | heavy: 4 shipped test classes + roster tests + both corpora | **~1000** |
| **B** — the two transitions | `validate` reachable from `already-benchmarked`, the D23b reporting state, one constructor, the arm-undeclaration doctrine | moderate: `validate`'s own class, the ladder tests, both corpora again | **~700** |
| **C** — the lock | compound-word derivation, the `_`-boundary, the scan surface, one fixture comment | light and self-contained: one test class, no engine change | **~300** |
| | | **Total** | **~2000** |

**Movement 6 must be split. Three units, in this order:**

1. **6c — the lock** (~300). Lands **first** and independently: it touches no engine
   code, no ladder, no corpus, and nothing 6a or 6b will touch. Smallest, fully
   isolated, and it closes a measured leak that is open right now. There is no reason
   to hold it behind two larger units.
2. **6a — a decision can be reopened** (~1000). Depends on nothing but the shipped
   chain. Delivers D19–D21 whole; splitting the token from `build-first` would ship a
   `yes` nobody can act on.
3. **6b — the transitions** (~700). Depends on 6a: D22 *is* 6a's token, and D23's down
   direction records its decision with the same field. Chaining it after 6a is what
   keeps 6b small enough to be one unit.

Each of the three is inside the 1400-line budget on its own; the ~2000 total is not.
**Decision needed before apply: Yes. Chained PRs recommended: Yes. Budget risk: High.**
`sdd-tasks` owns the final numbers — and should treat these as floors rather than
estimates, since every forecast in this chain has been low and none has been high.

Against a 1400-line budget that is **Budget risk: High**, **Chained PRs
recommended: Yes**, **Decision needed before apply: Yes** — answered by five
chained units, never by reduced coverage. `sdd-tasks` owns the final number and may
split unit 2 or 3 further; nothing here authorises dropping a movement to fit.

---

## 11. Open questions

- [ ] **D5b vs `sdd-spec`.** Does the requirement demand that re-answering the offer
      with acceptance flip the state on its own? If yes, D5b is replaced by an
      explicit closed yes/no surface and this design adjusts. The requirement wins.
- [ ] **`__implementation__` as the literal's name.** Neutral and consistent with
      `__levels__`/`__steps__`/`__records__`, but it is the one name in this design
      that is chosen rather than derived. If the spec names it, the spec wins.
- [x] ~~Does any live target already declare `__steps__`?~~ **Measured: yes.** The
      live target declares all three sibling literals with real content, plus an
      unread fifth (§1.1), so §7 step 2 is load-bearing, not formal. Closed.
- [ ] **`declare-first`'s second branch under an absent declaration** (D13). It
      reads `report.get("live") == "undeclared"` and is not conditioned on the
      declaration status, so whether it can shadow the decline/validate pair must
      be measured rather than reasoned. Named as a task; it is the one branch in
      the enumeration I could not settle by reading.
- [x] ~~`repair` vs `experiment` for the validation rung.~~ **Closed: `experiment`.**
      Revision 2's `repair` ruling is withdrawn; I agree with `sdd-spec` (D12). Both
      of my earlier arguments were artefacts of the coverage picture and fail under
      the corrected one — a single-arm run spends machine time and declares a scale
      of its own, which is this skill's own hard definition.
- [x] ~~`validate-first` as the rung's name.~~ **Renamed `validate`**, following the
      experiment family (`benchmark`, `piloted`) rather than the repair family's
      `*-first`. Closed by D12.
- [x] ~~Does the remote path differ for a single-arm run?~~ **Measured: no.**
      `flow_acts`, `jobfolder.generate_job` and `resolve_clone_paths` are all
      generic; one arm imports fewer packages and the existing cross-check adapts by
      itself. No `remote-execution` change proposed, no blocker found there. The
      work is documentation plus one draft section. Closed by D11b.
- [x] ~~Does an empty `__levels__` block remote placement?~~ **No** — placement and
      the rung ladder are independent declarations. Closed by D11d.
- [x] ~~D13's placement prose vs the shipped code.~~ **Closed by Unit 3** (task 3.14):
      the branch now sits last among the overrides, matching D13's original text, with
      an explicit `resolved.status != "absent"` guard on `report-first`. Unit 4b's
      first-position placement was the divergence, and it was corrected rather than
      implemented around. **Movement 6 must not reorder that chain again.**
- [ ] **D5b is superseded by D19, not merely amended.** Unit 4 shipped "acceptance =
      materializing the harness" and proved a bare re-answer does not reopen — which
      is correct for a prose answer and is exactly the hole Part A fills. Once the
      closed token exists, `decision: "yes"` reopens **without** the structure existing
      first. The D5b open question in this list is therefore resolved *by being
      replaced*; `sdd-spec` should confirm that reading rather than treating D5b as
      still live.
- [ ] **Does `validate` become reachable from `already-benchmarked` only, or from any
      state with a benchmark package present?** (D23a.) I designed the narrower one —
      a *current, complete* record is what makes the acid test's question already
      answered. A stale or piloted record is a different case and I did not rule on it.
      Named rather than guessed.
- [ ] **`premises` in the bucket key: I am asking `sdd-spec` to adjust** (D14a).
      Its raw-verbatim-text choice needs source-slicing machinery the engine does
      not have — the resolver hands over a parsed value — and it re-asks a settled
      question after a re-indent. My ruling is the canonical *value*, sorted,
      field-name-agnostic. If `sdd-spec` holds raw text, its requirement wins and
      this adjusts, but the adjustment then owes both consequences explicitly.
