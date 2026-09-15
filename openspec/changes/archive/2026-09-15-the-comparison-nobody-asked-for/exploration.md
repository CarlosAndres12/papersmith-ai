# Exploration: the-comparison-nobody-asked-for

**Phase**: explore · **Artifact store**: hybrid (Engram `sdd/the-comparison-nobody-asked-for/explore`, id 1838)
**Subject**: `.claude/skills/proposal-implementation` and the shared engine
`.claude/skills/_core/implementation/engine/implementation_engine.py`

## The problem

Flow A implements a mathematical proposal in numpy, validates it, and stops. It
never converts to PyTorch and never proposes a benchmark run — that division is
correct and is not in question. What is in question is that Flow A brings the
*comparison machinery* into existence before any comparison has been proposed,
and that a declined comparison leaves no trace.

## Verified facts

1. **Flow A creates the benchmark package unconditionally.** `scaffold_destinations()`
   (engine :4255) is **eleven** unconditional files; two of them are
   `src/<Package>_Benchmark/__init__.py` (:4265) and
   `src/<Package>_Benchmark/report_digest.py` (:4270). "Thirteen" is
   `scaffold_gaps()`'s maximum — the eleven plus up to two conditional merge
   anchors (`.gitignore` entries, the pytest anchor). SKILL.md uses "thirteen"
   for the gap-report number consistently; the distinction matters for the work,
   not for the doctrine.
2. **Flow A step 8 populates part of that declaration.** SKILL.md :715-728 asks
   for `revision` and `premises` beside the object-to-module map and writes them
   into the benchmark `__init__.py`; `_stage_objects` (:16460-16511) refuses
   `OBJECT_MAP_NOT_APPROVED` without them.
3. **`premises` is write-only by design, not by oversight.** SKILL.md :1236-1238:
   "nothing downstream validates its content — it is written for a person reading
   a drift report beside changed sections, not for a check to parse." `revision`
   IS consumed, but only at engine :15614-15631 as `built_against` feeding
   `changed_sections` — benchmark-drift machinery only.
4. **`report_digest.py` is Flow A's hostage inside the benchmark package.**
   `assets/kit/nb/verification.ipynb` (the notebook Flow A step 15 executes)
   imports `from {{PKG}}_Benchmark import report_digest`. `probe.ipynb` and
   `benchmark.py` reference the package too, but those are
   `harness_destinations()` (:4396-4405), written only by Flow B's wiring-first
   rung — already correctly gated behind a real comparison. The unconditional
   hostage is only the scaffold-stage pair.
5. **A declined comparison has nowhere to live.** `probe`'s ladder (:3545-3556)
   has five states and none is "declined"; `probe_state()` reads only
   `<Name>/Results/<PROBE_RESULTS>`; `probe` never reads `AGREED.md`.
   `_answered_discussions()` (:12322) does suppress rungs from answered `discuss`
   events, but has exactly one call site gating two questions
   (`_pilot_decision_question`, `_report_findings_question`). Answering "not now"
   to the run-the-benchmark menu (SKILL.md :1011) writes nothing and the rung
   re-fires every pass.
6. **The skill's own benchmark package counts as a baseline.**
   `previous_implementations()` (:3109-3133) excludes only the case-folded own
   package and `IGNORED_DIRS` (`impl_layout.py:19-22`, no `_Benchmark` rule).
   Measured on `implementations/Domain_Adaptation`:
   `previous_implementations(t, "MIL-CREDA")` returns
   `['CREDA', 'MIL_CREDA_Benchmark']`. So `nothing-to-compare` is structurally
   unreachable for any scaffolded target.

## What the archived change decided, and what is being reverted

`openspec/changes/archive/2026-08-20-the-flow-names-what-it-needs/` (F1) decided
two separate things:

- **Where in the flow the ask happens** — Flow A step 8, behind step 7's gate,
  with no renumbering. **This is not reverted.**
- **Where on disk the answer is written** — `src/<Package>_Benchmark/__init__.py`,
  for the stated pragmatic reason that the file already existed and already
  asserted the ask in a comment. **This is what Movement 2 reverts.** The
  archived design never argued that `revision`/`premises` conceptually belong to
  the benchmark; only that reusing a scaffolded file was cheaper than inventing
  one.

## Rulings

**`premises` keeps no reader.** The defect was never the absence of a reader —
the doctrine states its purpose is human context in a drift report, the same
posture `AGREEMENTS.md` checklist items take. The defect is the coupling to the
benchmark package. The step 9 existence gate is preserved verbatim; only the
destination changes.

**Destinations.**
- `revision`/`premises` → a new top-level literal in `src/<Package>/__init__.py`,
  already one of the eleven unconditional scaffold destinations. No new file is
  invented.
- `report_digest.py` → `src/<Package>/report_digest.py`. `_here()`'s
  self-location needs a one-line simplification: `parents[1]` still resolves to
  the repository root at that depth, and `.name.removesuffix("_Benchmark")`
  becomes a no-op. `KIT_SEAL` and `remote_cli.py`'s `_load_source_digest()` both
  hardcode the **kit source** at `assets/kit/nb/report_digest.py` and are
  unaffected; only the destination mapping in `scaffold_kit_source()` changes.

**A declined comparison is a bare `discuss` event.** `settle`/`AGREED.md` is for
agreed work ticked once code carries it — a decline is a category error there. A
Results artifact is ruled out because `probe` is contractually read-only
(SKILL.md :812) and `probe_state()` already owns that file for a different fact.
`discuss` has two live precedents of exactly this shape and never requires
`settle` to persist an answer. The work is a stable question-text constructor
plus one new terminal `next_step` value, `"declined"`, in `PROBE_NEXT_STEPS`,
symmetric with `nothing-to-compare` and `already-benchmarked`. Reopening costs no
new code: re-running `discuss` on the identical text with a new answer flips the
bucket, last-event-wins.

## End state

After Flow A: `src/<Package>/` holds the modules, `__init__.py` (now also
carrying the declaration), and `report_digest.py`. **No `_Benchmark` directory
exists at all.**

> **Corrected during the propose phase.** This section first said the gap count
> drops to at most eleven and that BOTH removed files fold into
> `harness_destinations()`. That is wrong. `report_digest.py` is **relocated**,
> not removed: Flow A's own `verification.ipynb` imports it and executes inside
> Flow A, so it stays a scaffold destination at a new path. Only
> `src/<Package>_Benchmark/__init__.py` leaves the scaffold list. Eleven minus
> one is **ten** unconditional, so **at most twelve** gaps, not eleven, and
> `harness_destinations()` grows from three entries to **four**, not five. No
> fourth materialization stage is invented either way. `probe`'s
ladder gains a `"declined"` terminal state reported the way
`nothing-to-compare`/`already-benchmarked` are today.

## Dependency order (proven from the code, not assumed)

Movement 3 cannot land alone. Step 9's gate (Movement 2) and step 15's notebook
import (Movement 1) both execute **inside Flow A**, before any Flow B work, so
deferring `_Benchmark` creation without first relocating what those two read
would break Flow A itself. Movement 4 must land too, or a decline re-triggers
materialization every pass.

**Order: 1, 2, 4 in any order among themselves → then 3.**

## Blast radius

| Area | What changes |
|---|---|
| `implementation_engine.py` | `scaffold_destinations`, `scaffold_kit_source`, `_stage_objects`, `resolve_benchmark_declaration`, `KIT_SEAL`'s destination mapping, `PROBE_NEXT_STEPS`, a new `_answered_discussions` caller, `previous_implementations` (add a `_Benchmark`-suffix exclusion) |
| `scripts/materialize.py` | Independently duplicates the scaffold mapping (:67, :76) and must move in lockstep |
| `assets/kit/nb/verification.ipynb`, `probe.ipynb` | Both import `report_digest` from `_Benchmark`; both need the new path |
| `assets/kit/src_benchmark/__init__.py` | The seven-block declaration shrinks to five (`arms`, `search`, `report`, `distribution`, `entry`) |
| `SKILL.md` | Step 5's table, step 8's prose, the seven-block table (:1185-1255), the run-the-benchmark Decision Gates row, "Conversion, then benchmark" |
| `references/usage.md` | The worked scaffold-file-list example, the `OBJECT_MAP_NOT_APPROVED` refusal-detail row |
| `openspec/specs/` | **Not empty — 41 specs.** A keyword sweep finds none governing the scaffold list, the declaration location, the probe ladder or the baseline finder, so the conclusion (nothing to update) survives; the premise as first written did not. |
| `experimental-implementation/impl_profile.py` | Its `OBJECTIVE_FLOW` "standing" stage names the same gate in its own words; ships no kit, so Movements 1-3 are latent there, but the shared-engine description must change |
| `remote-execution` | `jobfolder.py`'s mention is a generic docstring example (no change); `remote_cli.py` and `test_remote_execution.py:2032-2036` reference the kit source (unaffected) |
| Tests | `tests/test_proposal_implementation.py` (392 `_Benchmark` / 28 `report_digest` / 35 `premises`) is the bulk; `tests/test_remote_execution.py` (123 `_Benchmark`, mostly generic job-folder fixtures) needs fixture-vs-contract triage rather than assumption |

## Size and delivery

The strictly narrower archived precedent forecast ~790 lines, so a single change
certainly exceeds the 1400-line review budget. Delivery strategy is
`ask-on-risk`: the answer to size is four chained work units in the dependency
order above, never reduced coverage. Every movement ships; nothing is deferred.

## Risks

- `materialize.py`'s duplicated scaffold mapping is a second site that must move
  in lockstep. Missing it reintroduces exactly the drift class the archived
  change already named.
- The 123 `_Benchmark` hits in `test_remote_execution.py` are untriaged
  fixture-vs-contract. Treat that as a discovery task inside the first unit.
- Adding a `PROBE_NEXT_STEPS` entry moves the sealed 28-case corpus's `probe`
  case digest. `openspec/specs/implementation-engine-neutrality/spec.md` already
  names `probe` as a digest mover for a different field, so regenerating the seal
  is expected mechanical work — but it is work, and the unit that adds the state
  owns it.
- `AGREED.md` / `AGREEMENTS.md` naming drift (SKILL.md :730, :954 say
  "AGREEMENTS.md"; everywhere else says "AGREED.md") sits in the same doctrine
  paragraph Movements 2 and 4 touch. Pre-existing and unrelated; worth one line
  in that commit, reported here rather than expanded into a fifth movement.
