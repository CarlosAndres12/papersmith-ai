# Tasks: The agreement nothing computes — Slice D

## Counts, derived here, not inherited

- **Requirements: 19.** Measured by `rg -c '^### Requirement:' openspec/changes/the-agreement-nothing-computes/specs/*/spec.md` → matches the brief.
- **Scenarios: 46, not 52.** Measured by `rg -c '^#### Scenario:' openspec/changes/the-agreement-nothing-computes/specs/*/spec.md`: `implementation-cross-document-agreement` 13, `implementation-block-locator` 7, `implementation-document-binding` 6, `implementation-per-document-vocabulary` 7, `implementation-cli-seal` 7, `experimental-implementation-skill` 6. Sum = 46. `implementation-per-document-vocabulary` moved 5 → 7 when `5d42dd7` resolved R1/R2 (below) directly in the spec text: the nested `cross_citation` requirement now carries 4 scenarios ("A declared crossing is validated and used", "An explicit `None` is accepted and crosses nothing", "Omitting the leaf refuses by its own indexed name", "A malformed mapping refuses at its exact indexed sub-path") and the required-non-nullable `block_locator` requirement carries 3 ("Every shipped entry declares one, and the existing corpus is unmoved", "A missing sub-key refuses at its exact indexed path", "A wrong-shaped locator refuses by name"). The brief's "52" is a sixth inherited count that failed this session; every task below maps to one of these 46, plus design-only items (`COMPOSE_AMBIGUOUS_DOCUMENT`, the crossing-state unit matrix, M7's drive-and-report) that carry no scenario of their own and are marked as such.
- **Mutations: 10 (Z1–Z10)**, named in design.md's Mutation plan, one task each below, distributed D1×5, D2×1, D3×2, D4×1, D5×1.
- **Task count: 100**, re-derived 2026-09-12 after the R1/R2 pre-apply reconciliation (the inherited 78 was measured false; `rg -o '^\s*- \[[ x]\] [0-9]+\.[0-9]+[a-z]?' | wc -l` gives 100). Apply re-derives this if any task is split (the D1 contingency) or merged.

## Design/Spec Reconciliation — Resolved Pre-Apply, Not Deferred

Two places where design.md's mechanics and a spec.md's literal scenario
text once diverged. Both are **resolved pre-apply, in commit `5d42dd7`**,
which rewrote the three delta specs (`implementation-per-document-
vocabulary`, `implementation-block-locator`, `implementation-cross-
document-agreement`) to carry design's side directly. Apply must not
record either as an open item; there is nothing left for a later spec-sync
pass to reconcile.

**R1 — the cross-document leaf's name and shape, resolved.** The spec now
names the leaf `cross_citation` — a mapping of `pattern` and
`resolves_against`, required per entry, absent only by an explicit `None`
— on `documents[N].dataset_marker`'s tier, not the flat pattern-only
`cross_citation_pattern` design.md's D5 rejected drafting against. The
ruling is measured, not stylistic: the shipped precedent in
`impl_domain_profile.py` already carries both shapes side by side —
`dataset_marker` is a flat required-nullable scalar, while
`documents[N].notation_keys` is a nested mapping validated sub-key by
sub-key, refusing `documents[N].notation_keys.locus` and its two siblings
by their own indexed names (`_NOTATION_KEYS_REQUIRED`). A crossing needs a
target label as well as a pattern; a flat scalar has nowhere to carry one,
so the nested precedent, not the flat one, is what the leaf's own shape
measures against.

**R2 — required vs. optional per entry, resolved.** The spec now requires
`block_locator` on every `documents[N]` entry, non-nullable — `None` is
not accepted here, unlike `cross_citation`. The ruling is an absence test
run against the shipped engine, not a preference: `remedy_compatibility`
computes `tags = set(TAG_RE.findall(source))` unconditionally
(`implementation_engine.py:5061`) — on silence the engine does not fail
closed, it silently applies the LaTeX locator to a document that is not
LaTeX, which is the live defect this capability exists to close. The
five-leaf `_DOCUMENT_VOCABULARY_LEAVES` tier may stay silent because its
fallback is the **host's own** top-level `provenance.*`/`findings.*`
values — the same host declared them. `block_locator` has no such
host-declared fallback, so its silence cannot be safe the way theirs is.

**Also specified in `5d42dd7`:** `cross_citation.pattern` carries exactly
one capturing group, with a scenario asserting a three-group pattern is
also refused — `citation_pattern`'s three groups exist only because
`_impact_class` reads `group(1) or group(2) or group(3)`; that reader has
no counterpart for `cross_citation`, so copying the three-group rule here
would enforce a count nothing reads.

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 2,750–4,350 (design's floor; every prior slice's own estimate came in over, except the one that priced its proof) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | D1 → D2 → D3 → D4 → D5 (design's D12 shape); D1 alone is the risk against the 1400-line review budget and carries a named contingency split (D1b) below |
| Delivery strategy | auto-chain |
| Chain strategy | stacked-to-main |

Decision needed before apply: No — the operator's citation-key ruling (option 1) is already recorded in proposal.md.
Chained PRs recommended: Yes
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| D1 | `block_locator` triple + tier + resolver validation; all six `TAG_RE`/`DISPLAY_BLOCK_RE` sites + the `selectedEntryId` renderer re-pointed; `remedy_compatibility` per-document field loop; `COMPOSE_AMBIGUOUS_DOCUMENT`; `LockD`; fixture T + three cases; `compose`/`admit` leave `unsealed.json` | PR 1 | `.venv/bin/python -m unittest tests.test_implementation_profile tests.test_implementation_domain_lock tests.test_implementation_domain_mutation tests.experiments_seal tests.seal tests.pair` | Real subprocesses; scratch copies for every mutation (never the shipped engine) | `impl_domain_profile.py`, `implementation_engine.py`, both profiles, fixture T diff only; revert restores `unsealed.json`'s two entries and pre-slice `tests/experiments_seal/digests.json` bytes |
| D1b (contingency, only if D1 exceeds 1,150 measured lines) | The `remedy_compatibility` per-document field loop (tasks 1.16–1.20), split behind its own commit and its own digest capture | PR 1b (base: D1's locator-only commits) | Same as D1 | Same | Independent revert boundary from the locator-only commits |
| D2 | `cross_citation` leaf + resolver tier (R1's nested shape); `crossing_state` accessor; the resolver's unit matrix; `reference-experimental.ts` byte-unchanged + `cites()` negative assertion (M6) | PR 2 (base: D1) | `.venv/bin/python -m unittest tests.test_implementation_profile tests.test_implementation_domain_mutation` and `npm test -- --grep reference-experimental` | Real subprocess for the Python resolver; the TS side runs through its own existing suite, no new mock | `impl_domain_profile.py`, `implementation_engine.py` diff only; revert leaves D1 shipped and dormant |
| D3 | `cmd_agree`, conditionally registered (D9); the two refusal codes (Kind 1, Kind 2, no-crossing-once); `GATING_REFUSALS`; the roster pin; sealed crossing cases | PR 3 (base: D2) | `.venv/bin/python -m unittest tests.experiments_seal tests.test_proposal_implementation` | Real subprocesses through `cmd_agree`; separate methods per refusal, never one method with three asserts | `implementation_engine.py` diff + new sealed cases; revert restores single-document `COMMANDS` byte-identity (Z10 proves it) |
| D4 | `--acknowledge` per exact id | PR 4 (base: D3) | `.venv/bin/python -m unittest tests.experiments_seal` | Real subprocess, a two-discrepancy corpus case | Diff isolated to the acknowledgment flag and its parsing; revert leaves D3's refusals intact and unacknowledgeable |
| D5 | `local_reach` at all four `class` comparisons; `HANDOFF_DOCUMENT_UNREADABLE`; the successor handoff; Flow B authored in `SKILL.md`; the tutor bullet; M7 driven and reported | PR 5 (base: D4) | `.venv/bin/python -m unittest tests.test_implementation_pair tests.experiments_seal` and `npm test` | Real subprocesses; M7's drive is against a real scratch `experimental-deliberation` project, never mocked | `implementation_engine.py`, both `SKILL.md`s; revert leaves D1–D4 shipped and dormant under `local_reach`'s string-comparison fallback |

Against `review_budget_lines: 1400`: **no unit above may merge unstacked**,
and D1 is the one to watch.

## Global constraints, carried into every task below (do not repeat per task)

- **RED before GREEN, separate commits**, strict TDD. Every behavioural task
  below is a pair; only D5's M7 task (5.13) is a DRIVE-AND-REPORT task
  outside that pattern, by design (M5's own first-commit exception aside,
  which is itself RED-first).
- **`git add <path>`, never `git add -A`.** A parallel agent's in-flight work
  was swept into an unrelated commit this session.
- **Conventional commits. No Co-Authored-By, no AI attribution.**
- **`sys.modules` caches `impl_domain_profile` process-wide.** Any new
  in-process test helper that swaps `IMPLEMENTATION_DOMAIN_PROFILE` or
  reloads `impl_domain_profile` MUST restore both in a `finally`, or ~110
  unrelated cases redden. Apply this to every helper introduced in Phases
  1–5, not just the ones that look risky.
- **Monkeypatching a module attribute has zero effect on a subprocess.**
  Every mutation task (Z1–Z10) plants into a scratch copy and runs a real
  subprocess; none patches an in-process attribute and calls it a mutation.
- **Clear `__pycache__` before every Python mutation.** A same-size edit
  reuses a stale `.pyc` and the mutation never runs.
- **An anchor that matched is not a mutation that ran.** Every mutation task
  asserts the anchor literal's count both before (1) and after (0) the edit,
  and again on revert (0→1). `sd -s` can exit 0 having changed nothing;
  `git diff --stat` proves nothing for an untracked file.
- **A surviving mutation has two explanations.** Before strengthening any
  assertion, measure whether the test is weak or the claim was wrong.
- **Check for test-class name collisions** in every file touched this
  change — two classes sharing a name silently drop the earlier one's tests.
  Run `rg '^class \w+Tests?\(' tests/test_implementation_*.py
  tests/test_proposal_implementation.py tests/experiments_seal/*.py | sort |
  uniq -d` before each phase's VERIFY step; it must return nothing.
- **`L1_EXPECTED_COUNT` (96) is a live hazard.** This change writes prose
  about a document that cites claims *of the proposal*. Engine prose (code
  comments, docstrings, refusal messages in `implementation_engine.py`,
  `impl_domain_profile.py`) MUST say "document 1", "the crossed document",
  or "the target document" — never the bare word `proposal`. Grep-check
  (`rg -i '\bproposal\b'` over `ENGINE_DIR`) before committing each file in
  this scope; the pin is a Python lock (`test_implementation_domain_lock.py`)
  and is run at every phase's VERIFY step, never inferred.
- **`reachable_refusal_codes()` pin (114)** moves only where design predicts
  it (D1 → 115, D3 → 117, D5 → 118) and is measured, not bulk-bumped —
  each phase's own task below runs it once, in that phase, after that
  phase's refusals land, never before and never skipped.
- **Two bars, every phase's VERIFY step:**
  - `git diff --exit-code tests/seal/` exits 0 — the sibling's 28 digests
    byte-identical (`tests/seal/implementation-cli-seal` Req "The Sibling's
    28 Digests Remain Untouched").
  - `npm test` stays 595/595; `.venv/bin/python -m unittest discover -s
    tests` (or `PYTHONDONTWRITEBYTECODE=1` prefixed, per this repo's
    convention) stays `OK (skipped=6)` with `Ran` grown — `skipped=6` MUST
    NOT move, and no `skipTest` is added anywhere in this change.
- **One suite run at a time.** The Python suite is not concurrency-safe with
  itself (`resolve_target` forces toy targets under the shared
  `FORGE_ROOT/implementations/`); do not run it in parallel with another
  agent's suite run, and do not trust a foreign `unittest discover` running
  elsewhere on the machine.
- **Out of scope, do not touch:** any rename of `proposalDigest` or its
  `_AUTHORIZATION_BINDING_KEYS` relatives; M2 (`cmd_handoff`'s hardcoded
  Spanish — D5 adds a fourth branch in the same Spanish, deliberately, see
  5.10); F6; the kit crossing the seam; the 22 further bare product
  literals; Slice B (`Data/`); anything under `tests/seal/`,
  `proposal-implementation/**` besides its one profile,
  `proposal-deliberation/**`, `_core/deliberation/**` except the two
  `experimental-deliberation/` files named in Phase 5.

## Phase 1: D1 — Block locator, per-document field loop, `compose`/`admit` sealed

**Gate at the end:** sibling's 28 byte-identical; **zero** of the 24
existing `experiments_seal` case digests moved (M3); the sibling's own
mutation entries measured. Estimate 750–1,150.

**Contingency (named, not a note).** After task 1.15 (all seven sites
re-pointed and `LockD` green), measure cumulative changed lines for this
phase (`git diff --stat` against the branch base). **If the count exceeds
1,150**, STOP: commit everything up to and including 1.15 as D1's own unit,
then continue tasks 1.16–1.20 (the `remedy_compatibility` per-document field
loop) as a separate unit D1b — its own commits, its own digest capture, its
own `git diff --exit-code tests/seal/` and zero-of-24 re-check before D2
starts. If the count is at or under 1,150, continue in the same unit and
skip the D1b split.

- [x] 1.0 GATE — VOID (resolved pre-apply in `5d42dd7`): this task's
      original instruction, recording R1 and R2 in the verify report's
      open items before writing any profile leaf, no longer applies —
      neither is an open item (see Design/Spec Reconciliation above). What
      remains of this GATE: confirm, before writing any profile leaf, that
      `documents[N].block_locator` is required-non-nullable and
      `documents[N].cross_citation` is the nested `{pattern,
      resolves_against}` shape — both now the spec's own text, not a
      design-only choice this task records as a divergence.
- [x] 1.1 RED: in `tests/test_implementation_profile.py`, one case per
      `block_locator` sub-key (`pattern`, `block_pattern`, `identity`)
      declaring a `documents[N]` entry missing that sub-key, asserting
      `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` names the exact indexed
      path (`documents[1].block_locator.identity`, etc.) — 3 cases, against
      the shipped resolver where the leaf is unrecognized (spec
      `implementation-per-document-vocabulary`'s scenario "A missing
      sub-key refuses at its exact indexed path", ruled required-non-
      nullable in `5d42dd7`; this task exercises that rule directly).
- [x] 1.2 GREEN: in `.claude/skills/_core/implementation/impl_domain_profile.py`,
      add the `block_locator` resolver tier after the `dataset_marker`
      check, before the `citation_pattern` group tier (D1) — required on
      every `documents[N]` entry, non-nullable, all three sub-keys or a
      named `…_INCOMPLETE` per missing one.
- [x] 1.3 RED+GREEN: exercise per-document-vocabulary's "A missing sub-key
      refuses at its exact indexed path" scenario against a **synthetic
      scratch profile** (never a shipped one — both shipped profiles
      declare a complete `block_locator` on every entry, so neither can
      exercise an omission). One entry declares a complete `block_locator`;
      the sibling entry omits one sub-key. Assert the omission refuses at
      its own exact indexed path (`documents[N].block_locator.<sub_key>`),
      and that the omitting entry borrows neither the other entry's
      locator nor falls back to the engine's `TAG_RE`/`DISPLAY_BLOCK_RE`
      constants. Mark this COMPLIANT-by-scratch-fixture in the verify
      report, not COMPLIANT-by-shipped-profile.
- [x] 1.4 RED: shape-validation cases — an uncompilable `pattern`; a
      `pattern` with 0 or 2 groups (must be exactly 1, never 3 — the
      `citation_pattern` rule does not apply here, and a case exists
      asserting a 3-group pattern is *also* refused, so nobody copies that
      rule by habit); an `identity` whose `string.Formatter().parse` yields
      zero fields, two fields, or one field not named `value` — each its
      own case, asserting `IMPLEMENTATION_DOMAIN_PROFILE_INVALID_BLOCK_LOCATOR`
      naming the exact indexed path.
- [x] 1.5 GREEN: implement the shape validation in `_resolve()` per 1.4,
      all `ImplementationProfileError` (M11's pin does not move here).
- [x] 1.6 GREEN: `document_block_locator(index)` in
      `.claude/skills/_core/implementation/engine/implementation_engine.py` —
      compiled once at import per index, never per finding (D2). Re-derive
      `TAG_RE = document_block_locator(0)["pattern"]` and `DISPLAY_BLOCK_RE
      = document_block_locator(0)["block_pattern"]` so the two identifiers
      survive and the six existing reader lines are byte-unchanged.
- [x] 1.7 VERIFY (zero-delta, asserted not inferred): declare
      `proposal-implementation/impl_profile.py`'s `block_locator` as
      today's exact hardcoded values (`pattern: r"\\tag\{([^}]+)\}"`,
      `block_pattern: r"(?s)\$\$.*?\$\$"`, `identity: "\\tag{{{value}}}"`).
      Run `.venv/bin/python -m unittest tests.seal` — 28 digests
      byte-identical.
- [x] 1.8 RED: `LockDDeclaredLocatorTests` in
      `tests/test_implementation_domain_lock.py` (B's `LockC` shape,
      stronger) — for every profile `discover_profiles()` finds, for every
      `documents[N].block_locator`, assert each of the three declared
      literals appears in no file under `ENGINE_DIR`. Non-vacuity asserted
      explicitly (both shipped profiles declare a non-null locator, so this
      is non-vacuous the day it lands, unlike B's `LockC`).
- [x] 1.9 GREEN: confirm 1.6/1.7's re-derivation satisfies 1.8 with zero
      further engine change; if it does not, that is the signal the
      matcher-only shape (M1's rejected option) leaked back in — fix by
      re-deriving through the leaf, never by weakening the lock.
- [x] 1.10 RED: for each of the six `TAG_RE`/`DISPLAY_BLOCK_RE` reader
      sites (M1's table — `remedy_compatibility`'s document-0 tags,
      `remedy_compatibility`'s per-finding tags, `cmd_compose`'s block tag
      identification, `cmd_compose`'s `DISPLAY_BLOCK_RE` filter,
      `cmd_admit`'s tags, `cmd_compose`'s enclosing-block match), a case
      against a non-LaTeX locator (fixture T's or a scratch profile's)
      proving that site now resolves through the declared locator — red
      against the shipped engine, which still reads the module constant
      (spec `implementation-block-locator` "A document whose declared form
      is not LaTeX supplies its own locator").
- [x] 1.11 GREEN: re-point all six sites to `document_block_locator(N)` per
      D3's table (index 0 for `remedy_compatibility`'s fallback and
      `cmd_admit`; the finding's own named document(s) for
      `remedy_compatibility`'s per-finding pass and `cmd_compose`).
- [x] 1.12/1.13 **Deviation, recorded rather than silent.** No dedicated
      single-site-revert comparison test was authored. Coverage instead
      comes from Z2/Z3 (1.27/1.28): since `TAG_RE`/`DISPLAY_BLOCK_RE` are
      re-derived through `document_block_locator(0)` and every consumer
      site reads the declared locator (never a per-site constant after
      1.11's re-point), a single mutated `impl_profile.py` leaf moves
      EVERY dependent site at once through a real subprocess run over the
      full 28-case corpus — a stronger, not weaker, proof of uniform
      observation than a synthetic single-site revert would have given,
      but it is not literally the task as specified. Flagged for the
      phase-gate report.
- [x] 1.14 RED: the seventh site — `cmd_handoff`'s
      `selectedEntryId = f"\\tag{{{finding[REMEDY_LOCUS_KEY][0]}}}"` — a
      case against fixture T's non-LaTeX `identity` template proving the
      hardcoded renderer still emits `\tag{...}` while the declared
      `identity` is different (M1's "the leaf is a triple or the lock is
      decorative"; this is the scenario `LockD` (1.8) alone cannot catch,
      because `LockD` checks the matcher and block-matcher literals, not
      the renderer's own hardcoded template unless it is also swept — this
      task proves the renderer path independently of the lock).
- [x] 1.15 GREEN: re-point `cmd_handoff`'s `selectedEntryId` through
      `document_block_locator(N)["identity"].format(value=...)`, where `N`
      is the single document the finding names. If the finding names both
      documents, refuse `COMPOSE_AMBIGUOUS_DOCUMENT` (D3 — design-only, no
      direct spec scenario; gated on `len(DOCUMENTS) > 1` so the sibling's
      `COMMANDS`/refusal surface is structurally untouched under one
      document). Add its RED case first: a finding naming both documents
      reaching `cmd_compose`/`cmd_handoff`'s selector, asserting the
      refusal fires and names the finding.
      **— CHECKPOINT: measure cumulative lines here; apply the D1
      contingency above if over 1,150 —**
- [x] 1.16 RED: the M4 control — a finding whose `document` is
      `["proposal"]` alone, declaring `remedy_equations` (document 1's own
      `remedy_locus_key`) naming a locus absent from document 1's text.
      Assert it is reported as an unmet locus, where today
      `finding.get("remedy_experiments", [])` is `[]` and the finding reads
      compatible. This case is red against the shipped engine **because the
      value is inexpressible today**, not because an assertion was authored
      to fail — the exact distinction M4 draws.
- [x] 1.17 GREEN: in `remedy_compatibility`, replace the module-level
      `for field in (LOCUS_KEY, REMEDY_LOCUS_KEY)` scalar read with a
      per-`finding_document_indices(finding)` loop (`[0]` when the finding
      names none), reading `document_vocabulary(label_index)["locus_key"]`
      / `["remedy_locus_key"]` and `finding_tags[label_index]` — built with
      that index's own `block_locator.pattern` against that index's own
      text (D4). Delete `remedy_compatibility`'s docstring claim about
      "document 0's tags" — the property is gone, not softened.
- [x] 1.18 VERIFY: the emitted `unknown_loci` list stays under document 0's
      `NOTATION_KEYS["unknown"]` key — one list, one shape — each entry
      already naming the field it read (D4's ruling; rejected: splitting
      into `unknownExperiments`/`unknownEquations`, which regrows `verify`'s
      output shape). Add the negative assertion: the output has no
      per-document key split.
- [x] 1.19 GREEN: single-document regression case — a one-document profile's
      `remedy_compatibility` output is byte-identical to before this
      capability (spec `implementation-block-locator` "The single-document
      behavior is unchanged").
- [x] 1.20 VERIFY: 1.16's case green; `.venv/bin/python -m unittest
      tests.seal` still 28/28 (this branch is unreachable under one
      document).
- [x] 1.21 GREEN (D13, fixture T): give `tests/experiments_seal/corpus.py`'s
      `Roots.fixture_t` its own `findings.py` instead of aliasing
      `fixture_b` (the aliasing comment names the reason: no case names it
      — that changes here). One finding whose locus is spelled this
      domain's own heading form and whose `remedy_block` is written in this
      domain's own block form.
- [x] 1.22 GREEN: three new cases — `compose-t` (the locator substitutes
      into a heading block), `admit-t` (loci resolve, `admitted` is
      non-empty — the first case in this corpus where a locus is *not*
      unknown), `verify-t` (the compatible direction — the negative control
      for M2's confident-wrong-answer defect).
- [x] 1.23 GREEN: remove `compose` and `admit` from
      `tests/experiments_seal/unsealed.json` (spec `implementation-cli-seal`
      "`compose` and `admit` are no longer in the unsealed set").
- [x] 1.24 VERIFY: recapture `tests/experiments_seal/digests.json`.
      **Measured (via the new `tests/experiments_seal_capture.py`,
      written this task since no capture script existed for this
      corpus): zero of the 24 pre-existing case digests moved — not
      `verify-a`/`verify-b` either**, correcting the design's own
      prediction: `missing = [... if e not in finding_tags]` over `["T1"]`
      is byte-identical whether `finding_tags` is `∅` or `{"1","2","3"}`,
      so M3's stronger zero-mover claim held even for verify-a/verify-b.
      Only `propose`'s already-known-nondeterministic digest changed
      (expected, excluded from comparison), `__corpus_fingerprint__`
      moved mechanically (`corpus.py` edited), and three new entries
      (`admit-t`, `compose-t`, `verify-t`) were added.
- [x] 1.25 GREEN: update `.claude/skills/experimental-implementation/SKILL.md`'s
      "Which commands are not available yet, and why" — drop the
      `compose`/`admit` entry; keep `materialize --stage scaffold`'s entry
      unchanged (spec `experimental-implementation-skill` "The compose/admit
      entry is gone" / "The stated availability matches what runs").
- [x] 1.26 MUTATE (Z1): delete each `block_locator` sub-key from a scratch
      declared entry, one at a time, per index; confirm anchor count 1→0
      before, 0→1 after restore; watch 1.1's matching case go red each
      time.
- [x] 1.27 MUTATE (Z2): flip the sibling's declared `pattern` to the
      heading form in a scratch copy; confirmed the LaTeX literal's anchor
      count 1→0. **Measured movers (correcting the design's prediction):
      `admit-e1`, `compose`, `verify-a`, `verify-b`** — non-empty, proving
      the leaf is wired; `admit-e0`/`verify-t` did NOT move (measured, not
      assumed).
- [x] 1.28 MUTATE (Z3): flip the sibling's declared `identity` to
      `[exp:{value}]` in a scratch copy; confirmed the template literal's
      anchor count 1→0. **Measured mover: `handoff-e1` alone** (correcting
      the design's prediction of `handoff-e0`/`handoff-e1` both) — the
      renderer half, non-empty, proving the leaf is wired.
- [x] 1.29 MUTATE (Z4): in `remedy_compatibility`, replace
      `vocab["locus_key"]` with the bare `LOCUS_KEY` scalar; confirm 1.16's
      case goes red; confirm `tests/seal/` survives (the branch is
      unreachable under one document); restore.
- [x] 1.30 MUTATE (Z5): replace `finding_tags[index]` with `finding_tags[0]`
      in `remedy_compatibility`; confirm the both-documents case goes red;
      confirm the seal survives; restore.
- [x] 1.31 MEASURE: `reachable_refusal_codes()` — **measured 114, unmoved**,
      correcting the design's own prediction of 115.
      `COMPOSE_AMBIGUOUS_DOCUMENT` is raised inside `cmd_compose`/
      `cmd_handoff`, and NEITHER is in `GATING_COMMANDS`, so the derivation
      (which walks only from `GATING_COMMANDS` roots plus
      `CORE_IMPLEMENTATION`'s flat, non-recursive `*.py` glob — which
      excludes `engine/`) never reaches it. Classifying it in
      `GATING_REFUSALS` was tried and reverted: it broke
      `test_the_roster_classifies_nothing_a_gating_command_cannot_raise`,
      the roster's own reverse lock, which refuses over-classification as
      firmly as the forward lock refuses under-classification. The design's
      instruction to "classify it" was therefore itself wrong, measured
      rather than followed. This is D1's own pin task; D3 and D5 each get
      their own below — never bulk-bumped.
- [x] 1.32 MEASURE: `L1_EXPECTED_COUNT` (96) and `L1_EXPECTED_FILES` (one
      file) — grep every file touched this phase before committing it;
      confirm the lock's own test is unmoved.
- [x] 1.33 VERIFY (phase gate). **Measured, this apply session:**
      `git diff --exit-code tests/seal/` exits 0 (confirmed after every
      commit). `tests/pair/digests.json` unmoved (`git diff --stat` shows
      only `tests/pair/corpus.py`'s anchor-text growth, never the
      digests). Full Python suite: `.venv/bin/python -m unittest discover
      -s tests -p "test_*.py"` → `Ran 3014 tests`, **`OK (skipped=6)`**
      (grown from the inherited baseline, `skipped=6` unmoved). `npm test`
      → **595/595**, unaffected (no `.ts`/`.mjs` file touched this
      phase). Name-collision sweep (`rg '^class \w+Tests?\(' ... | sort |
      uniq -d`, scoped per file, not across files) returns nothing for
      every file this phase touched.

      **Two real regressions found and fixed during this measurement,
      recorded rather than silently corrected**: `tests/pair/corpus.py`'s
      `_SECOND_DOCUMENT_ENTRY`/`_SECOND_DOCUMENT_WITHOUT_DIRECTORY`
      anchors were hardcoded to the fixture template's pre-`block_locator`
      shape (14 tests failed on the first full-suite run); and seven more
      hand-built `documents[]` entries across
      `tests/test_experimental_implementation.py` lacked the leaf (6
      tests failed on the second full-suite run). Both fixed, both
      re-verified green on the third full run.

      **Measured total for D1 (all nine commits, `git diff HEAD~9
      --stat`)**: 1,080 changed lines across `.claude/skills` and
      `tests` (1,022 insertions + 58 deletions across 17 files), 1,215
      including this file's own checkbox annotations — under the
      1,150-line D1 contingency threshold measured at the 1.15 checkpoint
      (~1,015 then), so **D1b did not fire**.

## Phase 2: D2 — The cross-document key and its resolver

**Gate at the end:** the resolver's unit matrix, both directions;
`reference-experimental.ts` byte-unchanged. Estimate 500–800.

- [x] 2.1 GATE — VOID (resolved pre-apply in `5d42dd7`): this task's
      original instruction, recording the R1 shape decision as a
      divergence from the spec in this phase's own commit message, no
      longer applies. The spec carries the nested `cross_citation` shape
      directly — there is no divergence left to make traceable.
      **Measured**: checked off as void; nothing implemented for this
      task, per the void-gate precedent (task 1.0).
- [x] 2.2 RED: `documents[N].cross_citation` absence cases —
      `cross_citation` itself is required (nullable: `None` is a valid
      declared value), but when declared as a mapping, missing `pattern` or
      `resolves_against` refuses `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE`
      naming `documents[N].cross_citation.pattern` /
      `.resolves_against` exactly — 2 cases (spec
      `implementation-per-document-vocabulary`'s scenario "A malformed
      mapping refuses at its exact indexed sub-path", ruled onto the
      nested shape in `5d42dd7`).
      **Measured**: commit `2f70434`, its own RED commit. All four of
      2.2–2.5's facets landed together in this one commit's 203-line
      addition to `tests/test_implementation_profile.py` — measured RED
      against the shipped resolver: 9 of 61 cases in that file failed for
      the right reason (`RuntimeError` not raised), the three positive
      controls passing trivially since the unvalidated key round-tripped.
- [x] 2.3 RED: `pattern` group-count validation — 0 or 2+ groups refuses
      `IMPLEMENTATION_DOMAIN_PROFILE_INVALID_CROSS_CITATION_PATTERN` naming
      the leaf (exactly 1 group, same reasoning as the block locator's
      `pattern`, not `citation_pattern`'s three).
      **Measured**: same commit, `2f70434` (see 2.2's annotation — the
      four RED facets were not split across separate commits).
- [x] 2.4 RED: `resolves_against` validation — naming an undeclared label
      refuses `…_UNKNOWN_CROSS_DOCUMENT`; naming its own entry (self-
      reference) also refuses `…_UNKNOWN_CROSS_DOCUMENT`, both by name.
      **Measured**: same commit, `2f70434`.
- [x] 2.5 RED: `None` accepted — `documents[1].cross_citation = None`
      resolves without refusal (spec `implementation-per-document-vocabulary`'s
      scenario "An explicit `None` is accepted and crosses nothing" — the
      per-entry nullable case; `cross_citation`, unlike `block_locator`, is
      allowed to resolve to `None`).
      **Measured**: same commit, `2f70434` — the three positive controls
      passing trivially, named above, are this scenario's own cases.
- [x] 2.6 GREEN: implement 2.2–2.5 in `_resolve()`'s per-entry walk, after
      the `block_locator` tier, before the `citation_pattern` group tier
      (D5). Identifier class for `pattern`'s capturing group copied from
      `reference-experimental.ts::IDENTIFIER` so a crossing id is spelled
      exactly as that domain already spells identifiers — state this
      copy explicitly in the docstring, not just the literal.
      **Measured**: GREEN commit `6c0796d` (71-line resolver tier in
      `impl_domain_profile.py`, right after `block_locator`'s own, before
      `citation_pattern`'s). `2f70434`'s cases now pass. The identifier-copy
      claim is stated explicitly not in the resolver's own docstring but at
      each profile's own declaration site (`experimental-implementation/
      impl_profile.py` lines 237–239: "`reference-experimental.ts::IDENTIFIER`
      verbatim (design.md D5)"), confirmed by reading the file directly —
      `[A-Za-z0-9][A-Za-z0-9._-]*` matches `reference-experimental.ts`'s own
      `IDENTIFIER` constant byte-for-byte.
- [x] 2.7 GREEN: fix the index defect measured against the file —
      `proposal-implementation/impl_profile.py`'s `PROFILE["documents"]`
      has exactly one entry, `documents[0]`; it has no `documents[1]`, so
      `documents[1].cross_citation = None` cannot be declared there.
      Declare `documents[0].cross_citation = None` on that profile instead
      (its only entry cites no experiments document — there is no second
      document in this profile's own list to cite). Declare
      `documents[1].cross_citation = None` on
      `experimental-implementation/impl_profile.py`'s `documents[1]` (that
      profile's mathematical-proposal entry, correctly indexed already —
      the mathematical proposal cites no experiments document);
      `documents[0]`'s (`experimental-implementation`, the experiments
      document) `cross_citation` declares
      `pattern: r"\[claims:([A-Za-z0-9][A-Za-z0-9._-]*)\]"`,
      `resolves_against: "proposal"`.

      **The sibling's second declaration on this file, carried here with
      its justification.** `proposal-implementation/impl_profile.py`'s
      `documents[0]` already gained `block_locator` at 1.7 — this change's
      first addition to that file, today's exact engine bytes written down
      rather than inherited. This task's `cross_citation: None` is the
      second. Between them, `block_locator` (1.7) and `cross_citation`
      (here) are this change's whole edit to that file: the sibling's
      second sanctioned edit in ten changes, after `dataset_marker: None`
      (an earlier change) was its first. The optional shape would have
      saved the sibling nothing — it would either keep being served an
      engine default it never chose, or resolve to absence and move its 28
      digests; the required shape asks it to write down a value that is
      already true. A zero-delta declaration, asserted on the 28 digests,
      never inferred — verbatim the argument commit `7912281` made for
      `dataset_marker: None`.
      **Measured**: commit `3212aa2` (the sibling's `cross_citation: None`
      plus the real crossing on both `experimental-implementation`
      documents) + `7525a27` (a fifth hand-built fixture,
      `OrFoldIndexHardcodeMutationTests`'s scratch second document,
      swept for the same required leaf — the same "sweep every hand-built
      fixture" lesson D1 recorded for `block_locator`, repeating here).
- [x] 2.7a VERIFY (zero-delta, asserted not inferred, this specific edit —
      its own RED/GREEN-adjacent check, not folded into 2.14's phase-end
      bar check): before adding `cross_citation: None` to
      `proposal-implementation/impl_profile.py`'s `documents[0]`, confirm
      `.venv/bin/python -m unittest tests.seal` is 28/28 byte-identical;
      make the exact one-line edit; re-run `.venv/bin/python -m unittest
      tests.seal` and assert the same 28 digests are still byte-identical
      across this specific edit.
      **Measured, reconstructed post-pause** (the literal `tests.seal`
      module command names no test — this repo's actual seal-comparison
      suite is `tests.test_implementation_seal.SealComparisonTests`, the
      same substitution D1's 1.7/1.20 made implicitly): `3212aa2`'s own
      commit message already asserted this check ran and passed in
      isolation ("`SealComparisonTests`, run twice, isolated to this
      commit's own diff"). Re-verified independently this session by two
      proofs neither depending on that claim: (1) `git log --oneline --
      tests/seal/digests.json` shows **zero** commits touching that file
      anywhere in `013c2bb~10..013c2bb` — the golden file is byte-identical
      not just around 2.7's edit but across the whole nine-commit phase,
      which subsumes the specific-edit claim; (2) at current HEAD,
      `.venv/bin/python -m unittest tests.test_implementation_seal` → 44/44
      `OK`, including `SealComparisonTests.test_every_sealed_case_matches_
      its_golden`, and `git diff --exit-code tests/seal/` exits 0.
- [x] 2.8 RED: `crossing_state(index)`'s four-membership unit matrix —
      design-only, no direct spec scenario (spec's Req1/Req2 for
      cross-document-agreement cover the *refusal* behavior in Phase 3;
      this is the accessor's own correctness, gating Phase 3). Four cases:
      resolves both ways (crossed == declared), `absent` only, `untested`
      only, both non-empty. Assert `crossed`/`declared` are sorted and
      de-duplicated before emission (a crossing repeated twice is one
      discrepancy, not two).
      **Measured**: RED commit `28d92ed` (137-line addition to
      `tests/test_experimental_implementation.py`, the four-membership
      matrix plus a `None`-cross_citation control and a dedup/sort
      control — six cases beyond the four named here). Measured RED: all
      six error `AttributeError`, `crossing_state` did not exist yet.
- [x] 2.9 GREEN: `crossing_state(index)` in
      `implementation_engine.py` — `crossed` = `cross_citation.pattern`
      findings in document `index`'s text; `declared` =
      `block_locator.pattern` findings in the `resolves_against` target
      document's text; `absent` = `crossed − declared`; `untested` =
      `declared − crossed`. `checkReferenceIntegrity`'s algorithm, one
      document over (D6) — cite this in the docstring, and confirm the
      docstring says "the target document", never `proposal`.
      **Measured**: GREEN commit `22f742d` (66 lines in
      `implementation_engine.py`, lines 5062–5066 and 7903–7923 read
      this session). Docstring reads verbatim "the TARGET document's own
      `block_locator.pattern`... never `documents[index]`'s own locator"
      and cites `_core/deliberation/engine/reference-index.ts` — no bare
      `proposal` occurrence; `L1_EXPECTED_COUNT` lock (below) confirms
      this at the file level, not just by this one read.
- [x] 2.10 GREEN: the corpus's crossing axis in
      `tests/experiments_seal/corpus.py` — at least one document-0 module
      declaring a `[claims:N]` citation and a document-1 (proposal-shaped)
      module declaring the matching `\tag{N}`, plus an inverse-control
      module where the citation and the declared claim disagree.
      **Measured**: GREEN commit `9b01534` — `CROSSING_RESOLVED_TEXT`
      (cites `[claims:9]`) and `CROSSING_DISAGREEMENT_TEXT` (cites the
      undeclared `[claims:5]`) both resolve against
      `PROPOSAL_CROSSING_TEXT` (declares `\tag{9}`). Recaptured via
      `tests/experiments_seal_capture.py`: 27 case digests (28 keys minus
      `__corpus_fingerprint__`, reconfirmed this session by reading
      `digests.json` directly). Zero of the 27 pre-existing case digests
      moved except `propose` (already-known-nondeterministic, excluded)
      and `__corpus_fingerprint__` (mechanical, `corpus.py` edited);
      `tests/seal/` byte-identical.
- [x] 2.11 RED (M6, negative assertion): in the deliberation side's own
      test suite, `cites("Sustains claim [claims:39].")` returns `[]` —
      the guard against a later agent adding `[claims:N]` to
      `reference-experimental.ts::cites` "for completeness". This case
      must exist and pass against the **current, unedited**
      `reference-experimental.ts` — it is a negative control, not a RED
      test waiting for a GREEN.
      **Measured**: commit `c4dc0f5` (this task and 2.12 landed together
      in one commit — the negative control needed no separate RED/GREEN
      pair since it asserts against unedited production code by design).
      `npm test` grew from the design's assumed 595/595 to **596/596**
      because of this one new test — measured this session, correcting
      the design's own prediction rather than repeating it; task 2.14's
      own "595/595" text below is the sixth-plus inherited count measured
      false in this change, corrected in that task's own annotation.
- [x] 2.12 GREEN/VERIFY: `experimental-deliberation/reference-experimental.ts`
      is byte-unchanged — `git diff --exit-code
      .claude/skills/experimental-deliberation/reference-experimental.ts`
      exits 0. `declares` is likewise untouched. Document the crossing form
      in `experimental-deliberation/SKILL.md` (the form, `[claims:N]`, is
      documented as prose there — this is the *documentation* task; M7's
      "Known limit" re-dating is Phase 5's, not this one).
      **Measured, this session**: `git diff --exit-code
      .claude/skills/experimental-deliberation/reference-experimental.ts`
      → exit 0. Commit `c4dc0f5` touched only `SKILL.md` (+6 lines,
      documenting the form and which engine resolves it) and the `.mjs`
      test file (+28/-0) — `reference-experimental.ts` itself is absent
      from that commit's diff entirely, confirming byte-identity by
      construction, not inference.
- [x] 2.13 MUTATE (Z6): in `crossing_state`, compute `declared` using the
      **declaring** document's own `block_locator` instead of the
      `resolves_against` target's; confirm the resolving case (2.8's first)
      flips to `absent` — the one a weaker fixture (one that only ever
      supplies a resolving crossing) would survive; confirm `tests/seal/`
      untouched; restore.
      **Measured**: commit `f07e786` — 66-line test in
      `tests/test_experimental_implementation.py`, `document_block_locator
      (target_index)` swapped for `document_block_locator(index)` in a
      scratch engine copy. Anchor discipline: 1→0 (real source), 0→1
      (mutated), confirmed both directions before running, per the
      commit's own message. `tests/seal/` untouched by construction — the
      mutation lives only in the scratch copy, never the shipped engine.
- [x] 2.14 VERIFY (phase gate): `git diff --exit-code tests/seal/` exits 0;
      `.venv/bin/python -m unittest tests.test_implementation_profile
      tests.test_implementation_domain_mutation` green; `npm test` 595/595
      (reference-experimental's own suite unaffected); `L1_EXPECTED_COUNT`
      re-measured (this phase's docstrings are the highest-risk prose in
      the whole change — confirm no occurrence of bare `proposal`);
      `reachable_refusal_codes()` confirmed **unmoved** (D2 adds only
      `ImplementationProfileError` codes, invisible to that walk, per
      M11) — this is a negative measurement, not a skip.

      **Measured, this apply session (resumed from `RESUME-D2.md`'s
      pause):**

      - `git diff --exit-code tests/seal/` → exit 0.
      - `tests.test_implementation_profile tests.test_implementation_
        domain_mutation` → 73/73 `OK`. Widened this session to also run
        `tests.test_implementation_seal` (44/44), `tests.test_experiments_
        seal` (13/13), and `tests.test_proposal_implementation` (part of
        a combined 1607/1607 `OK (skipped=2)` run) — all green.
      - `npm test` → **596/596, not 595/595.** The task's own "595/595"
        text is a seventh inherited count measured false in this change:
        task 2.11's negative-control test is itself one new assertion in
        `experimental-deliberation-references.test.mjs`, landed in commit
        `c4dc0f5` alongside 2.12, growing the suite by exactly one test.
        Measured, not assumed, per this change's own recurring lesson
        about inherited numbers.
      - `L1_EXPECTED_COUNT` (96, one file) — confirmed unmoved via
        `tests.test_implementation_domain_lock.CampaignProposalExclusionTests`,
        all four of its own tests green. Direct read of `crossing_state`'s
        and `document_cross_citation`'s docstrings confirms "the TARGET
        document"/"targets" phrasing throughout, no bare `proposal`.
      - `reachable_refusal_codes()` → **114, confirmed unmoved** (measured
        directly via the function, not inferred from the lock test alone).
      - **A real regression found and fixed during this measurement,
        recorded rather than silently corrected** (the same discipline
        D1's own 1.33 established): the full-suite run first came back
        `FAILED (failures=11, skipped=6)` — ten of the eleven were
        `DerivedDenylistTests.test_3_every_pinned_words_count_equals_
        its_pin_and_stays_in_the_denylist` sub-failures (an **earlier**
        slice's own cross-domain word-leak lock, M5/design.md D9, not
        named anywhere in this phase's task list), and the eleventh
        surfaced only after the first ten were fixed (see below). Commit
        `22f742d`'s new prose for `document_cross_citation`/
        `crossing_state` had used eleven words the lock already pins at
        an exact count — `value` (+2), `against` (+4), `resolves` (+4),
        `answers`/`before`/`carries`/`declaration`/`empty`/`experiment`/
        `longer`/`ruled` (+1 each) — each drift matching, word for word,
        the count of that word's new occurrences in `22f742d`'s own
        diff (measured via `diff <(git show ddc3c67:…) … | rg '^>'`,
        never assumed). Fixed in a dedicated commit (`0e780be`,
        immediately following this phase's last behavioural commit,
        docstring-only, zero behavioural delta) rewording the same three
        comments to carry identical meaning through synonyms confirmed
        absent from `build_denylist()`'s own output before landing —
        the first reword introduced a **twelfth** collision (`leaves`,
        the lock's own eleventh failure, caught by re-running the lock
        suite rather than trusting the first fix), corrected to `keeps`
        in the same commit. `tests.test_implementation_domain_lock`:
        28/28 after. Full suite re-run afterward: `Ran 3030 tests`,
        **`OK (skipped=6)`**, `skipped=6` unmoved.
      - Whole-phase diff (`git diff --stat 013c2bb~10..HEAD -- '.claude/
        skills' 'tests'`, code and tests only): **674 insertions + 28
        deletions across 13 files = 702 changed lines**, under this
        phase's own 500–800 estimate. `tasks.md`'s own checkbox
        annotations add 101 insertions + 14 deletions = 115 lines
        separately, per D1's own precedent of reporting the two counts
        apart rather than folding annotation prose into the code budget.

## Phase 3: D3 — `cmd_agree`, the two refusal codes, fail-closed-once

**Gate at the end:** each refusal mutation-proven, its corpus case named
**before** its assertion; the sibling's own membership test reddens when
the `len(DOCUMENTS) > 1` gate is deleted. Estimate 600–950.

- [x] 3.1 RED: `cmd_agree` conditionally registered — under a one-document
      profile, `agree` is not a parser choice, and `COMMANDS` is
      byte-identical to today (spec `implementation-cross-document-agreement`
      is silent on this directly; it is D9's constraint, forced by M8).
      Name the corpus case reaching this **before** writing the assertion,
      per the Approach's rule 3.
      **Measured, split into two halves.** The ABSENT half:
      `tests/test_proposal_implementation.py::GatingRefusalRosterTests::
      test_agree_joins_gating_commands_unconditionally_never_this_
      profiles_own_commands` — under this file's own already-loaded
      single-document profile, `assertNotIn("agree", impl.COMMANDS)` AND
      `assertIn("agree", impl.GATING_COMMANDS)`. RED for the right
      reason: `AssertionError: 'agree' not found in (...)` against
      `GATING_COMMANDS`, since D9's own unconditional-membership rule
      (below, 3.2) had not landed yet. The PRESENT half: five new
      `AgreementCheckTests` cases in `tests/test_experiments_seal.py`,
      each naming its own reaching corpus argv (fixture + revision)
      before its assertion, RED as `KeyError`/argparse "invalid choice"
      since `agree` did not exist at all. Commit `f909bd1`.
- [x] 3.2 GREEN: `COMMANDS = {..., **({"agree": cmd_agree} if
      len(DOCUMENTS) > 1 else {})}` in `implementation_engine.py`; `agree`
      takes its own `--revision` registration (a fourth site, not the
      eight-name shared set — widening that set moves the sibling's
      digests); joins `GATING_COMMANDS`.
      **Measured**: commit `a545e7c`. `GATING_COMMANDS` names `agree`
      UNCONDITIONALLY (not gated on `len(DOCUMENTS) > 1`) — the ONE
      deliberate asymmetry with `COMMANDS`'s own conditional spread,
      because `cmd_agree` is a plain module-level function regardless of
      registration, and `reachable_refusal_codes()`'s reverse lock
      (`test_the_roster_classifies_nothing_a_gating_command_cannot_
      raise`) must find its two codes reachable under EVERY profile,
      single-document included, or classifying them in `GATING_REFUSALS`
      would break that lock the identical way `COMPOSE_AMBIGUOUS_
      DOCUMENT` did at D1 (1.31's own annotation).
- [x] 3.3 RED: the no-crossing-declared refusal — an experiments document
      with zero `[claims:N]` citations and a proposal declaring 39 claims;
      name this exact reaching corpus case (M10: `PROPOSAL_REVISION_TEXT`
      declares no `\tag{}` at all — an unavoidable authored fixture, stated
      as such). Assert it refuses **exactly once**, by the no-crossing code
      — never 39 times (spec `implementation-cross-document-agreement`
      "Zero crossings against a 39-claim proposal refuses once").
      **Measured, and a real fixture defect found and fixed before this
      case could even be authored.** D2's own `trial-plan-crossing.md`
      (the crossing axis's target, declaring `\tag{9}`) carries NO DIGIT
      in its own filename, so `discover_document_revision`'s candidate
      filter (`re.search(r"\d", candidate.name)`) never selects it as a
      candidate at all — measured directly this session
      (`impl.crossing_state(0, "trial-crossing-resolved.md")` returned
      `declared: []` against it, not `["9"]`), a fixture committed but
      unreachable by any command until `agree` existed to expose it.
      Fixed with an ISOLATED root (`_build_crossing_target`,
      `proposals_1_crossing`, `crossingTarget` harness flag) rather than
      a digit added to the shared root, which would create a second
      digit-bearing family there and redden `admit-t`/`gate-e1`/
      `offer-e1`/`close-e1`/`handoff-e1` (all of which discover document
      1 by default). This case (`test_zero_crossings_against_the_
      default_target_refuses_once`, and the sealed `agree-undeclared`)
      uses the DEFAULT (non-isolated) discovery on both sides — `trial-
      1.md` (zero citations) against `trial-plan-v01.md`
      (`PROPOSAL_REVISION_TEXT`, zero `\tag{}`) — M10's own "unavoidable
      authored fixture": both sides read empty, not one 39-claim side,
      because no fixture on disk declares 39 claims.
- [x] 3.4 RED: the inverse — a proposal declaring zero claims while the
      experiments document cites the form at least once — same code, same
      once-not-N rule (the requirement's reverse direction, same
      scenario's coverage).
      **Measured, and a genuine design/spec gap closed, recorded rather
      than silently resolved.** design.md D7's own text says the code
      fires when "the declaring document's `crossed` list is empty" —
      literally read, that condition is FALSE for this reverse case
      (`crossed` is non-empty; only `declared` is). The spec's own
      Requirement text is unambiguous that BOTH directions collapse to
      the SAME single code, so `cmd_agree` implements `not crossed or
      not declared` (either side empty), not `not crossed` alone —
      spec read as authoritative over design's narrower sentence, the
      identical precedent D1 set for `COMPOSE_AMBIGUOUS_DOCUMENT`.
      Test: `test_the_reverse_direction_refuses_by_the_same_code` —
      `trial-crossing-resolved.md` (`crossed=["9"]`) against the
      DEFAULT-discovered target (`declared=[]`, `crossingTarget` NOT
      requested) — same `AGREEMENT_CROSSING_UNDECLARED` code.
- [x] 3.5 GREEN: `AGREEMENT_CROSSING_UNDECLARED` — fires alone and once
      when the declaring document's `crossed` list is empty; the other two
      lists (`absent`, `untested`) are **not computed** in this branch —
      with no crossing at all every declared claim would otherwise read
      "untested" and the refusal would be N discrepancies wearing one code.
      **Measured**: implemented as `if not crossed or not declared:` (3.4's
      correction folded in) — `absent`/`untested` are read from `state`
      but never inspected in this branch, satisfying "not computed" in
      the sense that matters (never named in the refusal). Commit
      `a545e7c`.
- [x] 3.6 RED: switching case — the same 39-claim proposal, one experiment
      now citing one of the 39 claims; assert the no-crossing code no
      longer fires, and any remaining untested claims refuse under Kind 2,
      individually named (spec "At least one crossing switches to the
      per-claim refusal path").
      **Adapted, recorded rather than silently narrowed.** This corpus's
      crossing target declares exactly ONE claim (`\tag{9}`), not 39 —
      there is no SECOND, still-untested claim left over in the same
      fixture to prove "switches, and the remainder still refuses" in
      one case. `test_a_crossing_that_resolves_clears_and_the_no_
      crossing_code_never_fires` proves the half this fixture CAN prove
      cleanly: `crossed == declared == {"9"}`, the no-crossing code does
      not fire, and NEITHER list names anything (a full match). The
      "remainder still refuses under Kind 2" half is proven by
      `agree-disagree` (3.7/3.8/3.9, immediately below) instead, whose
      `untested=["9"]` is exactly that remaining, individually-named
      claim — reached via a MIXED case rather than a switching one.
- [x] 3.7 RED: Kind 1 — an experiment citing claim N with the proposal's
      current revision declaring no matching claim N; assert
      `AGREEMENT_DOCUMENTS_DISAGREE` fires, naming the experiment and claim
      N in `claimAbsent` (spec "A citation to a removed claim refuses").
      Positive control: the identical citation with claim N still declared
      does not refuse for that citation (spec "A citation matching a
      declared claim does not refuse").
      **Measured, adapted.** Negative half:
      `test_documents_disagree_names_both_kinds_in_one_refusal` —
      `trial-crossing-disagree.md` cites `[claims:5]`, the crossing
      target declares `\tag{9}` — `absent=["5"]`, named in the refusal.
      Positive half: this corpus's one declared claim means "N still
      declared" and "N absent" cannot differ within one fixture without
      a second declared claim; proven instead by 3.6's full-match case
      (`crossed == declared == {"9"}`, "9" never appears in either list)
      — the degenerate but honest form of "a citation matching a
      declared claim does not refuse for that citation". The deeper
      per-value set arithmetic (two DIFFERENT values, one matched, one
      not) is already proven at the `crossing_state` level by Phase 2's
      `CrossingStateTests.test_both_non_empty_at_once`; this phase's own
      tests prove `cmd_agree`'s WIRING of that arithmetic into the
      refusal, not the arithmetic itself again.
- [x] 3.8 RED: Kind 2 — the proposal declares claim M, no experiment cites
      it; assert the refusal names M in `claimUntested` (spec "An untested
      declared claim refuses"). Positive control: claim M cited by one
      experiment among several does not refuse for M (spec "A claim cited
      by at least one experiment does not refuse").
      **Measured, same adaptation as 3.7.** Negative half: the same
      `agree-disagree` case — `untested=["9"]`, named. Positive half:
      3.6's full-match case again (the one declared claim, "9", is both
      cited and declared, and refuses for neither list).
- [x] 3.9 GREEN: `AGREEMENT_DOCUMENTS_DISAGREE` — **one refusal carrying
      both named lists**, `claimAbsent` and `claimUntested`, plus
      `unacknowledged` (D8's shape, wired here even though `--acknowledge`
      itself lands in Phase 4 — the refusal payload's shape must exist
      before the flag that clears entries in it). Discrepancy ids derived
      as `absent:<value>` / `untested:<value>`, never positional (a
      positional id renumbers when a claim is added and silently re-points
      an acknowledgment already made).
      **Measured**: `unacknowledged = [i for i in ids if i not in
      acknowledged]` where `acknowledged = set(getattr(args,
      "acknowledge", None) or [])` — reads `None` safely on THIS
      command's own `args` (no `--acknowledge` flag exists on `agree`
      yet), so every id starts unacknowledged until Phase 4 adds the
      flag; no change to this function will be needed when it does.
      Commit `a545e7c`.
- [x] 3.10 GREEN: classify both `AGREEMENT_CROSSING_UNDECLARED` and
      `AGREEMENT_DOCUMENTS_DISAGREE` as `WORK_STATE` in `GATING_REFUSALS`
      — nothing the caller can retype clears them; somebody has to change a
      document.
      **Found and fixed, beyond the task's own text**: classifying both
      as `WORK_STATE` alone reddened `test_every_work_state_publishes_
      something_runnable` (every `WORK_STATE` code must publish a
      runnable `resolve`) — `_WORK_STATE_RESOLUTIONS` needed an entry
      for each, added as `_refusal_question(...)` (the same shape
      `AGREEMENT_DISAGREES`/`DESTINATION_CONFLICT` already use): a
      runnable `discuss` invocation and a genuine QUESTION, never a
      decided direction — the boundary (3.11) holds for `resolve.
      question` too, not only `detail`.
- [x] 3.11 RED+GREEN: the boundary — the refusal's output contains no
      verdict field or word, no suggested edit, no "the code should follow
      the proposal" direction (spec "A refusal names the discrepancy
      without judging it"). Write the absence-of-verdict assertion first
      against the shipped 3.9 output; it must already pass (the boundary is
      by construction, not by later removal) — if it does not pass on
      first write, that is a defect in 3.9, fix 3.9, not the assertion.
      **Measured**: `test_the_refusal_names_the_discrepancy_without_
      judging_it` passed on first write against the shipped `agree-
      disagree` payload — no `verdict` key, and none of `"should
      follow"`, `"is correct"`, `"is wrong"`, `"the code should"`, `"the
      target should"`, `"recommend"` in `detail`.
- [x] 3.12 GREEN: add each new refusal kind (`AGREEMENT_CROSSING_UNDECLARED`,
      `AGREEMENT_DOCUMENTS_DISAGREE`) as its own sealed case in
      `tests/experiments_seal/` (spec `implementation-cli-seal` "Each new
      refusal kind has a sealed case"), and re-run 1.24's individual-read
      discipline on any digest that moves as a result.
      **Measured**: commit `4955803` — `agree-undeclared`
      (`AGREEMENT_CROSSING_UNDECLARED`) and `agree-disagree`
      (`AGREEMENT_DOCUMENTS_DISAGREE`, naming `absent:5`/`untested:9`
      together). Both digests read by hand before acceptance (both
      printed above in this session's own transcript): no verdict word
      in either, both `resolve` blocks a runnable `discuss` question.
      Recapture moved only `__corpus_fingerprint__` (mechanical) and
      `propose` (already-known-nondeterministic, excluded) — **zero of
      the 27 pre-existing case digests moved**.
- [x] 3.13 MUTATE (Z7): fire `AGREEMENT_DOCUMENTS_DISAGREE` per discrepancy
      instead of once with two lists; confirm the fail-closed-once case
      (3.3) goes red by asserting **exactly one** refusal payload is
      emitted for the zero-crossing case, and separately confirm the
      Kind1/Kind2 cases would now emit multiple refusals where one is
      expected; restore.
      **Measured, and the task's own framing corrected.** A single CLI
      invocation can only ever emit ONE refusal payload structurally (the
      first `raise` exits the call) — "exactly one refusal payload" holds
      trivially on both sides and proves nothing. The actual break Z7
      names is WHICH discrepancy gets INTO that one payload: the mutated
      `cmd_agree` (a scratch copy, per-discrepancy `for` loop, first
      iteration raises and returns) fires on the `agree-disagree`
      reaching case and names only `absent:5`, never reaching
      `untested:9` — the real implementation names BOTH in one message
      (proven the same session). Anchor: the combined-message `raise
      Refused(...)` statement, count 1→0 in the scratch copy, restored
      (never the shipped engine). `tests/test_experiments_seal.py::
      AgreementDisagreeZ7MutationTests`.
- [x] 3.14 MUTATE (Z10): delete `len(DOCUMENTS) > 1` from `COMMANDS`'s
      conditional spread in a scratch copy; confirm anchor count (the
      spread literal) 1→0; watch **the sibling's own**
      `test_the_case_roster_covers_the_command_roster_exactly` in
      `tests/test_implementation_seal.py` go red — the bar held by the
      sibling's own suite, not by this change's care; restore.
      **Measured, mechanism recorded.** Rather than running the
      sibling's own pytest FILE against a full scratch copy of the test
      tree (a second copy of every path this suite resolves), the
      mutated engine is imported under the SIBLING's own single-document
      profile and the sibling's test property is replicated verbatim
      against it: `{c["command"] for c in json.load(open(
      "tests/seal/cases.json"))} == set(impl.COMMANDS)`. Under the
      mutation this is `False` (with `agree_in_commands: True` —
      the gate's removal DID register it unconditionally); against the
      real, unmutated engine it is `True` — the bar held, and the
      mutation reached the property it claims to break.
      `tests/test_experiments_seal.py::AgreeRegistrationZ10MutationTests`.
- [x] 3.15 MEASURE: `reachable_refusal_codes()` — confirm it reports **117**
      (114 → 115 at D1 → 117 here: two new `Refused` codes,
      `AGREEMENT_CROSSING_UNDECLARED` and `AGREEMENT_DOCUMENTS_DISAGREE`).
      This is D3's own pin task, measured after this phase's refusals land,
      never inherited from D1's 115.
      **Measured 116, not 117 — design's own prediction corrected.**
      D1 measured 114, UNMOVED (1.31's own annotation; design's assumed
      115 baseline was itself wrong). 114 + 2 new codes = 116. Design's
      "117" arithmetic silently repeated the wrong 115 baseline rather
      than D1's own measurement. `reachable_refusal_codes()` run
      directly: `116`, and `{'AGREEMENT_CROSSING_UNDECLARED',
      'AGREEMENT_DOCUMENTS_DISAGREE'}` both present. Every downstream
      count depending on this (the sibling's own `SKILL.md`/`references/
      usage.md` doctrine sentences, `_ENGLISH_COUNTS`) updated to match
      the MEASURED 116/67, never the predicted 117/68.
- [x] 3.16 VERIFY (phase gate): `git diff --exit-code tests/seal/` exits 0;
      `.venv/bin/python -m unittest tests.experiments_seal
      tests.test_proposal_implementation` green; `L1_EXPECTED_COUNT`
      re-measured against this phase's new refusal messages and docstrings;
      full suite `OK (skipped=6)`; `npm test` 595/595; name-collision
      sweep clean.

      **Measured, this apply session:**
      - `git diff --exit-code tests/seal/` → exit 0.
      - `tests.test_experiments_seal` → 20/20 (13 pre-existing +
        `AgreementCheckTests` ×5 + `AgreementDisagreeZ7MutationTests` ×1
        + `AgreeRegistrationZ10MutationTests` ×1). `tests.test_
        proposal_implementation.GatingRefusalRosterTests` → 19/19 (18
        pre-existing + the new registration test). `tests.test_
        implementation_seal` (the sibling's own 44) and `tests.test_
        implementation_domain_lock` (47) both green; `tests.test_
        implementation_domain_lock.CampaignProposalExclusionTests`
        confirms `L1_EXPECTED_COUNT` (96) unmoved.
      - **`npm test` → 596/596, not 595/595** — the eighth-plus inherited
        count measured false in this change (D2's own 2.14 already
        corrected this once this session; this task's own "595/595"
        text is a ninth instance, corrected here rather than repeated).
        No `.ts`/`.mjs` file touched this phase; the count reflects D2's
        own added negative-control test, unaffected by D3.
      - Full suite: `PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m
        unittest discover -s tests -p "test_*.py"` → `Ran 3038 tests`,
        **`OK (skipped=6)`** (grown from D2's 3030 by exactly 8 — the 8
        new test methods this phase added; `skipped=6` unmoved, no
        `skipTest` added anywhere).
      - Name-collision sweep (`rg '^class \w+Tests?\(' ... | sort |
        uniq -d`, scoped to every file this phase touched) returns
        nothing.
      - `reachable_refusal_codes()` → **116**, confirmed (3.15).
      - Whole-phase diff (`git diff --stat e58e32e..HEAD -- '.claude/
        skills' 'tests'`, code and tests only, three commits `f909bd1`/
        `a545e7c`/`4955803`): **535 insertions + 39 deletions across 10
        files = 574 changed lines** — under this phase's own 600–950
        estimate (the floor), comfortably under the 1,150 measure-and-
        report threshold.
      - One deliberate ripple beyond this phase's own stated scope,
        recorded rather than silently made: `GATING_COMMANDS` growing
        from nine to ten moved the SIBLING's own doctrine prose
        (`proposal-implementation/SKILL.md`, `references/usage.md`) —
        "nine gating commands" → "ten", 65 → 67 work-state codes, 114 →
        116 total. Purely descriptive sentences about a genuinely
        shared, cross-skill constant (`GATING_COMMANDS` is one static
        tuple, not per-skill); no sibling BEHAVIOR, digest, or command
        changed — `git diff --exit-code tests/seal/` above is the proof.
        `test_the_doctrine_states_the_split_the_roster_actually_holds`
        now reads the gating-command count off `GATING_COMMANDS` itself
        rather than a hardcoded "nine", closing the drift this test's
        own docstring already warned about.

## Phase 4: D4 — Per-exact-id acknowledgment

**Gate at the end:** a case with **two** discrepancies: one acknowledged
clears one. Estimate 300–500.

- [ ] 4.1 RED: two discrepancies present (one `absent`, one `untested`, or
      two of the same kind); acknowledge one by its exact id; assert the
      refusal persists, naming **only** the still-unacknowledged one in
      `unacknowledged` (spec "Two discrepancies, one acknowledged, one
      still blocks" — the case a single-discrepancy fixture cannot prove,
      per D8's own note).
- [ ] 4.2 RED: both acknowledged by their exact ids; assert neither blocks
      the next command (spec "Both acknowledged, both clear").
- [ ] 4.3 RED: a call acknowledging neither by id (no `--acknowledge` flag
      at all, or one naming an id that does not exist); assert both remain
      in `unacknowledged` — a general "continue" clears nothing because no
      such flag exists (spec "A general 'continue' with no ids clears
      nothing").
- [ ] 4.4 GREEN: `--acknowledge <id>`, repeatable, on `cmd_agree`. Clears
      only ids echoed back exactly; the remainder still refuses.
      **Request-scoped** — nothing persists it in `position.jsonl` (D8's
      rejected alternative: a durable record would keep clearing a
      discrepancy nobody re-checked once the underlying bytes changed, the
      `POSITION_STALE` defect class one surface over). State this
      explicitly in the docstring.
- [ ] 4.5 MUTATE (Z8): `--acknowledge` clears the **whole** unacknowledged
      list rather than only the named id; confirm the two-discrepancy case
      (4.1) goes red — **the one a weaker single-discrepancy assertion
      would survive**, because a single-discrepancy case cannot distinguish
      "cleared the named id" from "cleared everything"; restore.
- [ ] 4.6 VERIFY (phase gate): `git diff --exit-code tests/seal/` exits 0;
      `.venv/bin/python -m unittest tests.experiments_seal` green; add the
      two-discrepancy acknowledgment case to
      `tests/experiments_seal/cases.json` as its own sealed case and read
      any moved digest individually (1.24's discipline); full suite `OK
      (skipped=6)`; `npm test` 595/595.
- [ ] 4.7 MEASURE: `reachable_refusal_codes()` — confirm it is **unmoved**
      at 117. D4 adds no new `Refused` code; it only adds a flag that
      clears entries in an existing refusal's payload. Report the
      unmovement explicitly rather than skipping the check because "nothing
      changed" — that is exactly the assumption this project has been
      wrong about before.

## Phase 5: D5 — The consumer, the successor, Flow B

**Gate at the end:** a finding against BOTH documents routes correctly,
proven RED-first; M7 re-measured end to end and **reported, not
promised**. Estimate 600–950.

- [ ] 5.1 RED (M5's own first commit — the exception to the pair pattern,
      by design): thread `sources_by_document` into `cmd_handoff`
      (`finding_impact(finding, sources_by_document)`, built exactly as
      `cmd_admit` builds it via `document_revision_names`, gated on
      `len(DOCUMENTS) > 1`) with **no other change**. Watch all four
      `impact["class"] == "local"` comparisons answer `False` and every
      finding defer with no refusal — **this red is the deliverable's own
      first commit**, red against the shipped engine for a reason no
      assertion author chose (M5). Commit this state; do not fix it in the
      same commit.
- [ ] 5.2 GREEN: `local_reach(impact) -> bool` — one module-level function
      replacing all four `impact["class"] == "local"` comparisons (three in
      `cmd_handoff`, one in `cmd_verify`'s `local_remedies_not_written`).
      Handles both shapes: a plain string, or a mapping in which **every**
      named document must read `local` (the reach is the union — local in
      one document and structural in the other is structural). Empty
      mapping falls back to the string path (test this explicitly — it is
      the unit-test row design names alongside the string/mapping-all/
      mapping-mixed cases).
- [ ] 5.3 RED: a finding naming both documents, both resolving `"local"`;
      assert `cmd_handoff` routes it (settles inline), rather than
      comparing the mapping to `"local"` and falling to
      `deferToOwnSession` by default (spec `implementation-document-binding`
      "`cmd_handoff` routes a finding against both documents without
      silently deferring").
- [ ] 5.4 GREEN/VERIFY: `cmd_verify`'s `local_remedies_not_written` reads
      `local_reach` on the same evidence `cmd_handoff` now uses — a finding
      whose mapping reports `"local"` for the document it names is
      included, not silently excluded by the old scalar comparison (spec
      "`cmd_verify`'s local-remedy comprehension reads the mapping too").
- [ ] 5.5 RED: each named document's citations are matched by its own
      pattern when computing `impact["class"]` — document 0 and document 1
      declare different `citation_pattern` values (already true from
      Slice C's fixture); a finding naming both; assert document 0's class
      uses document 0's own pattern and document 1's uses its own, never
      cross-applied (spec "Each named document's citations are matched by
      its own pattern" — this exercises `finding_impact`'s existing
      per-document threading from Slice C, now under D5's new consumer;
      confirm it still holds rather than assuming it).
- [ ] 5.6 RED: a finding naming only the first document maps to that
      document alone; a finding naming both carries both classes,
      uninterpreted — no combined or summarized verdict word (spec "A
      finding against one document maps to that document alone" / "A
      finding against both documents carries both classes, uninterpreted").
- [ ] 5.7 MUTATE (Z9): revert `local_reach` to the bare string comparison
      `impact["class"] == "local"` at all four sites; confirm the
      two-document handoff routing case (5.3) dies; confirm the
      single-document behavior is unaffected (the string path still
      matches); restore.
- [ ] 5.8 RED+GREEN: mutation-prove the boundary once more at this
      consumer layer — a mutation reverting any of the four comparisons
      back to the bare scalar check against the mapping itself is caught
      by the two-document corpus case, which fails naming the reverted
      comparison (spec "A comparison reverted to a bare scalar check is
      caught" — this is 5.7's assertion restated as the spec's own named
      scenario; confirm both wordings are satisfied by the same mutation).
- [ ] 5.9 RED: `HANDOFF_DOCUMENT_UNREADABLE` — a finding naming a declared
      document whose revision cannot be read; assert `cmd_handoff` refuses
      by name rather than silently reading document 0's text while the
      second is missing (precedent: `DOCUMENT_REVISION_UNREADABLE` at the
      binding-write sites — cite it in the refusal's docstring).
- [ ] 5.10 GREEN: implement 5.9; `cmd_handoff` gains one additive key per
      item — `deferredBecause: "structural-in-another-document"` — and its
      prose is written in the same hardcoded Spanish as its three
      neighbors, deliberately (M2 stays recorded and unresolved; translating
      one of four branches would make the output bilingual, a behavioural
      delta the seal must refuse). Do not translate it. Do not open a
      separate task to fix M2 here.
- [ ] 5.11 GREEN: add the mutation-adding-a-verdict-field guard (spec
      "A mutation adding a verdict field is caught") at the consumer layer
      too, if not already fully covered by 3.11's Phase-3 lock — confirm
      coverage by running a scratch mutation that adds a `suggestion` key
      to `cmd_agree`'s payload and watching a lock over the returned key
      set go red (D11's own mutation, restated).
- [ ] 5.12 GREEN: the tutor bullet in
      `.claude/skills/experimental-implementation/SKILL.md` — the third
      discrepancy kind (metric/protocol mismatch) documented as guidance
      for the reading agent, explicitly never a check (spec "The bullet
      exists and names no check"). Add the negative case: an experiment
      whose declared metric does not match its cited claim's actual
      assertion, with the citation itself otherwise resolving, does **not**
      refuse (spec "A metric/protocol mismatch does not refuse" — only
      Kind 1, Kind 2, and the no-crossing-declared code refuse).
- [ ] 5.13 DRIVE AND REPORT (M7 — not RED/GREEN; no task may promise a
      published successor): against a **real scratch**
      `experimental-deliberation` project, drive resolve → preview → accept
      through `CREATE_SUCCESSOR` end to end for a revision named
      `experiments-<slug>-v03.md` incrementing to `…-v04.md`. Report the
      actual outcome — whether `publishSuccessor` succeeds or still throws
      `INVALID_TARGET_REVISION` — with the exact throw site and the exact
      values `parseManagedRevision`/`LAX_RE`/`strictRevisionLabel` computed.
      **Do not assert a pass/fail expectation in any test as if the outcome
      were known**; this task's deliverable is the measurement itself. If
      it publishes, re-date `experimental-deliberation/SKILL.md`'s "Known
      limit" note with this measurement. If it still fails, correct the
      note's *cause* (the regex is profile-derived, not hardcoded — M7) and
      leave the limit recorded, per proposal.md's explicit scope
      exclusion ("Repairing `experimental-deliberation`'s accept-turn limit
      if re-measurement shows it still fires... a different engine").
- [ ] 5.14 GREEN: author (not amend — this skill's `SKILL.md` has neither
      today, measured this phase) Flow B in
      `.claude/skills/experimental-implementation/SKILL.md`, reusing
      `proposal-implementation`'s existing Flow B steps and its drift gate
      ("did the user make this change") by reference — no new competing
      flow, no second gate asking the same question (spec "The documented
      flow points at the existing one" / "The drift gate is not
      duplicated"). Document the experiments-successor handoff as the path
      from a green suite through to a test submission. Confirm
      `remote-execution` needs no wiring here — its scripts
      (`REMOTE_EXECUTION_CLI_SCRIPT` et al.) are already `FORGE_ROOT`-derived
      and shared by both skills; this task drives them, never rebuilds
      them.
- [ ] 5.15 MEASURE: `reachable_refusal_codes()` — confirm it reports **118**
      (117 → 118: `HANDOFF_DOCUMENT_UNREADABLE` is the one new code this
      phase adds). D5's own pin task.
- [ ] 5.16 VERIFY (phase gate, and the change's own final gate): `git diff
      --exit-code tests/seal/` exits 0; `.venv/bin/python -m unittest
      tests.test_implementation_pair tests.experiments_seal` green;
      `L1_EXPECTED_COUNT` re-measured (this phase's `SKILL.md` prose is the
      second-highest risk after Phase 2 — confirm "document 1"/"the crossed
      document" phrasing held, not "the proposal"); full Python suite `Ran`
      grown from Phase 1's baseline, `OK (skipped=6)`, `skipped=6` unmoved
      across all five phases; `npm test` 595/595; name-collision sweep
      clean.

## Phase 6: Cross-slice success-criteria sweep

- [ ] 6.1 Both refusal kinds mutation-proven (3.7/3.8/3.13), each corpus
      case named before its assertion (3.3, 3.7, 3.8) — confirmed by
      reading the commit history, not by re-running.
- [ ] 6.2 Two-discrepancy acknowledgment case (4.1) clears exactly one id;
      general continue clears nothing (4.3).
- [ ] 6.3 No-crossing-declared refuses once, not per-claim (3.3, 3.6).
- [ ] 6.4 No verdict word, no resolution proposal, no repair direction —
      each proven by mutation (3.11, 5.11), not by reading the source.
- [ ] 6.5 `remedy_compatibility` reads document N's own locus keys (1.16,
      1.29).
- [ ] 6.6 `compose`/`admit` sealed, `unsealed.json` shrunk (1.23, 1.24).
- [ ] 6.7 Every moved `experiments_seal` digest individually read and
      defended (1.24, 3.12, 4.6).
- [ ] 6.8 `tests/seal/`'s 28 digests byte-identical at every phase gate
      (1.33, 2.14, 3.16, 4.6, 5.16); `npm test` 595/595 throughout;
      `skipped=6` never moved.
- [ ] 6.9 No file under `proposal-implementation/` (besides its one
      profile edit) or `proposal-deliberation/` modified — `git diff
      --exit-code` on both trees, run once more at the very end.
- [ ] 6.10 Every new refusal code (`COMPOSE_AMBIGUOUS_DOCUMENT`,
      `AGREEMENT_CROSSING_UNDECLARED`, `AGREEMENT_DOCUMENTS_DISAGREE`,
      `HANDOFF_DOCUMENT_UNREADABLE`) appears in `reachable_refusal_codes()`'s
      roster and is classified in `GATING_REFUSALS` — confirmed at 115, 117,
      118 in order, never bulk-checked against a single final number.
      `IMPLEMENTATION_DOMAIN_PROFILE_INVALID_BLOCK_LOCATOR`,
      `…_INVALID_CROSS_CITATION_PATTERN`, `…_UNKNOWN_CROSS_DOCUMENT`
      confirmed invisible to that walk (`ImplementationProfileError`, per
      M11).
- [ ] 6.11 VOID (resolved pre-apply in `5d42dd7`): R1 and R2 were resolved
      before apply — `implementation-per-document-vocabulary/spec.md`
      already carries the nested `cross_citation` shape and the
      required-non-nullable `block_locator` tier, along with
      `implementation-block-locator` and `implementation-cross-document-
      agreement`'s matching text. There is no spec-sync correction left to
      file as a post-apply follow-up.
- [ ] 6.12 Report the measured total changed-line count per slice against
      design's 2,750–4,350 floor and this file's own 750–1,150 /
      500–800 / 600–950 / 300–500 / 600–950 per-phase estimates — do not
      repeat the numbers, report what was actually measured, including
      whether the D1b contingency split fired.

## Key Deferred / Out of Scope (do not touch)

- Slice B (`Data/` per product) — proposed in parallel; D does not depend
  on it.
- Any rename of `proposalDigest` or its `_AUTHORIZATION_BINDING_KEYS`
  relatives.
- M2 (`cmd_handoff`'s hardcoded Spanish) — recorded unresolved; D5
  deliberately adds a fourth branch in the same Spanish (5.10).
- F6, the kit crossing the seam, the 22 further bare product literals.
- Whether `gate` should require `agree` before a launch — recorded in
  design.md's Open Questions, belongs to a slice whose subject is the gate.
- Repairing `experimental-deliberation`'s accept-turn limit if 5.13's
  re-measurement shows it still fires — it lives in `_core/deliberation/`,
  a different engine.
- `tests/seal/**`, `proposal-implementation/**` (except its one profile),
  `proposal-deliberation/**`, `_core/deliberation/**` — untouched; asserted
  via `git diff --exit-code` after every phase, not just at the end.
