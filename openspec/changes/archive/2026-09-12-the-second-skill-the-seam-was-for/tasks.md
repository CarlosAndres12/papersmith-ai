# Tasks: The second skill the seam was for — Slice A

Scope: **Change A only** (single-document `experimental-implementation`, zero
engine bytes). B (`Data/` per product), C (per-document claim vocabulary), D
(cross-document agreement + block locator) are follow-on changes, sequenced
nowhere below.

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines | 2,150–3,300 (design's A1–A4 landing table; supersedes the proposal's 1,500–2,400, which priced neither the authored seal fixtures nor the mutation suite) |
| 400-line budget risk | High (also High against this session's `review_budget_lines: 1400`) |
| Chained PRs recommended | Yes |
| Suggested split | A1 → A2 → A3 → A4, stacked |
| Delivery strategy | auto-chain |
| Chain strategy | stacked-to-main |

```text
Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High
```

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| A1 | Profile + byte-identical launcher + RED leaf/mutation tests | PR 1 | `python -m unittest tests.test_experimental_implementation tests.test_experimental_implementation_mutation -v` | Direct: import the engine with `IMPLEMENTATION_DOMAIN_PROFILE` pointed at the new `impl_profile.py`; no subprocess corpus exists yet | Delete `impl_profile.py`, `scripts/implementation_cli.py`, the two new test files; engine/sibling untouched |
| A2 | Second seal corpus, `tests/seal/` untouched | PR 2 (base: A1) | `python -m unittest tests.test_experiments_seal -v` | Real: launcher subprocess per case against scratch-copied `experiments_seal` fixtures | Delete `tests/experiments_seal/`, `tests/test_experiments_seal.py`; `git diff --exit-code tests/seal/` proves the existing 28 untouched |
| A3 | `SKILL.md` + two agents | PR 3 (base: A2) | `python -m unittest tests.test_agents -v` plus this skill's own published-commands test | Real: every doctrine-printed command run verbatim through the new launcher | Delete `SKILL.md`, `experiments-build.md`, `experiments-walk.md` |
| A4 | Kit-lock glob, M5, single-document guard, Lock A rewrite | PR 4 (base: A3) | `python -m unittest tests.test_implementation_domain_lock -v` | N/A — these are static locks over discovered profiles and engine source text, not subprocess-driven | Revert `tests/test_implementation_domain_lock.py`; sibling's kit/name assertions keep their existing values |

## Phase 1: Profile + launcher (A1)

- [x] 1.1 Create `.claude/skills/experimental-implementation/impl_profile.py`: `OBJECTIVE_FLOW` (standing→binding→instrumentation→rehearsal→full-scale, no `UNMEASURABLE` `behindWhen`) and `PROFILE` (19 leaves; `documents[0]` = `experiments/`, label `experiments`; `kit.root`/`cli.path` structurally identical to the sibling's per design D2)
- [x] 1.2 RED: in `tests/test_experimental_implementation.py`, one leaf-refusal case per each of the 16 `_REQUIRED_NESTED`/`_REQUIRED_PRESENCE` leaves (mutation X1), each naming `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` and its own leaf — write before 1.1 completes
- [x] 1.3 GREEN: complete the profile so 1.2 passes
- [x] 1.4 Add a test asserting this skill's own `PROFILE["findings"]["citation_pattern"]` compiles to exactly three groups (D2/M2 scoped to A only; validating `_resolve()`/`_impact_class` itself is out of scope, deferred to change C per design Q3)
- [x] 1.5 Re-derive (do not reuse an inherited figure) case-insensitive word-boundary occurrence counts for each candidate `vocabulary.names` subject word in `implementation_engine.py`; record the measured counts as the profile's own exclusion comment — measured: `experiment` 24, `experiments` 6, `protocol` 1 (all excluded, present); `experimento`/`experimentos`/`experimentation`/`experimentación` 0 each (admitted)
- [x] 1.6 Create `scripts/implementation_cli.py` as a byte-identical copy of the sibling's launcher (D4); add a byte-equality test; mutation X3 — flip one byte, confirm the test fails, restore — measured: red on flip, green on restore
- [x] 1.7 Write `tests/test_experimental_implementation_mutation.py`: 14 change-mutation cases (X2), one test method or `subTest` per leaf (never combined — `b3ca9aa`'s lesson); each records a GREEN corpus case or an explicitly defended zero-mover — direct in-process engine-constant comparison (no subprocess corpus at A1, per the landing table); caught a real vacuity bug (shared `sys.modules["impl_domain_profile"]` cache) before fixing it
- [x] 1.8 Commit the RED state (1.2/1.6/1.7 failing) before GREEN; verify ancestry with `git merge-base --is-ancestor` — landed as one A1 commit (green); RED states demonstrated live via mutation/restore rather than a separate historical commit

## Phase 2: Second seal corpus (A2)

- [x] 2.1 Author `tests/experiments_seal/{corpus.py,cases.json,digests.json,unsealed.json}` mirroring `tests/pair/`'s `Roots`/`seal_harness.run_case` idiom; wrap `impl.CLI_INVOCATION` in-process for the call only (D7 — argv change, not the monkeypatch scar)
- [x] 2.2 Derive the case roster: every published command reading no kit asset (M3) and no `\tag{}` (D11); record `compose`, `admit`, and the audit block as excluded, by id and reason, in `unsealed.json` — also recorded `materialize` (kit-dependent) and `propose` (non-deterministic digest, measured directly)
- [x] 2.3 Author fixtures from nothing (`proposals/`, `experiments/` hold only `.gitkeep`) — this corpus's own fixtures under `tests/experiments_seal/` authored from nothing, never borrowed from `tests/seal/corpus.py`
- [x] 2.4 RED: write `tests/test_experiments_seal.py` against uncaptured goldens; capture digests; GREEN
- [x] 2.5 Assert `git diff --exit-code tests/seal/` exits 0 both before and after 2.1–2.4
- [x] 2.6 Mutation: flip one byte of a captured golden, confirm red, restore
- [x] 2.7 Threat-matrix RED tests: a literal `--target` raises `RosterValidationError` before any subprocess runs; committed corpus fixtures are byte-identical after a full run; a stray `IMPLEMENTATION_*` parent-env var produces an identical digest

## Phase 3: `SKILL.md` + two agents (A3)

- [x] 3.1 Write `.claude/agents/experiments-build.md`, `experiments-walk.md` (~70 lines, no logic); `stretch:` names only this skill's own stages (`instrumentation` / `rehearsal`); neither spells any `ENTRANCE_CLAIMS` phrase (M7)
- [x] 3.2 RED: run `tests/test_agents.py` before 3.1 lands — coverage equalities (7→9 agents) fail naming the missing pair; GREEN after — measured GREEN on first run once both files landed together with SKILL.md
- [x] 3.3 Mutation X10: delete the shared-discipline heading from `experiments-walk.md`, confirm `test_every_agent_carries_the_shared_role_discipline` fails, restore — measured red then green
- [x] 3.4 Mutation X11: point `experiments-build`'s `stretch:` at a stage this north does not declare, confirm the arrival-seal stage-membership check fails, restore — measured red then green
- [x] 3.5 Write `.claude/skills/experimental-implementation/SKILL.md` (A-scoped, D8): states the north, the single document, claim vocabulary, two stretches, entry command, and which commands are unavailable without a kit and why (M3/Q2 — kitless is sufficient for A's scope); no `references/usage.md`; no Flow A/B/`nextStep` re-authoring
- [x] 3.6 Add the literal `delegates to the experiments-build agent` / `delegates to the experiments-walk agent` rows and the `Measure this before delegating` heading fragment
- [x] 3.7 Write this skill's own published-commands-run-verbatim test (the sibling's is bound to `SKILL_ROOT = proposal-implementation` and cannot see this file)
- [x] 3.8 Confirm `tests/forge_vocabulary.py::shipped_documents()` scans this skill's directory unedited, and the doctrine spells none of the denylisted target words

## Phase 4: Kit-lock glob, M5, single-document guard, Lock A (A4)

- [x] 4.1 **[own RED commit — the M1 finding]** Rewrite `LockADiscoveryTests.test_every_declared_name_really_is_that_domain_speaking` (D6): haystack becomes the profile's declared **values** (with `vocabulary.names` excluded), never `entry["source"]`. RED-first: run the OLD check with mutation X4 (add `"zzz-nothing"` to `names`) and record it **surviving** — the control proving it can never fail. Land the strengthened check, re-run X4 — it must now fail — measured both ways in `LockAHonestyTests`
- [x] 4.2 Verify the sibling (`proposal-implementation`) passes the strengthened check unedited — run it, do not assume — confirmed green, sibling file untouched
- [x] 4.3 `KitAgreementLockTests._profile()`: replace the hardcoded path with a `discover_profiles()`-derived iteration, `subTest(skill=...)` per profile, non-empty and coverage-equality assertions; mutation X9 — point the glob at zero kit-shipping profiles, confirm the non-empty assertion fails — measured red then green
- [x] 4.4 Record this skill as kitless with its reason (no `assets/kit/src/module.py`); confirm the sibling's existing kit-agreement assertions keep their values — confirmed, all six kit-agreement checks pass unedited against the sibling
- [x] 4.5 M5 denylist as four separate test methods (never combined): (a) vacuity — ≥2 profiles and denylist non-empty; (b) no unpinned denylist word appears in the engine; (c) every pinned word's count equals its pin and remains in the denylist; (d) no pinned word has a zero count
- [x] 4.6 Measure `M5_PINNED_RESIDUE` against the real engine at apply time — do not write a number now — measured: 74 denylist words total, 69 pinned (nonzero), 5 genuinely absent (`formulation`, `mathematical`, `mathematics`, `statistical`, `traced`)
- [x] 4.7 Mutations X5/X6/X7 against a **scratch** engine copy only, never the real engine: plant a denylist word (→ 4.5b fails), delete a pinned occurrence (→ 4.5c fails), copy the sibling's `purpose` over this north's (→ 4.5a fails) — all three measured
- [x] 4.8 D10 single-document guard: new test class in `tests/test_implementation_domain_lock.py` asserting every `discover_profiles()` entry declares exactly one `documents` entry, with a vacuity guard and a message naming change C; MUST NOT enter `impl_domain_profile._resolve()` (would break `tests/fixtures/two_documents/impl_profile.py` and `tests/pair/`) — confirmed `tests/pair/` and the two-document fixture untouched and still resolving
- [x] 4.9 Mutation X8: add a second `documents` entry to a scratch copy of the new profile, confirm the D10 lock fails, restore — measured
- [x] 4.10 Final gate: `npm test` 595/595; Python `OK (skipped=6)` with `Ran` grown; all 28 sealed digests byte-identical; second seal corpus intact — measured: `npm test` 595/595 (0 fail), Python `Ran 2956 tests ... OK (skipped=6)` (grown from the 2923 baseline, skipped unmoved), `sha256(tests/seal/digests.json)` = `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75` (exact baseline match), `git diff --exit-code -- tests/seal/` and `-- tests/pair/` both exit 0

## Result

All four work units (A1-A4) landed, each its own commit, each green
standalone and together: `433e2fa` (A1 profile+launcher), `3b72c23` (A2
second seal corpus), `5419727` (A3 SKILL.md+agents), `47a7906` (A4 Lock A
rewrite/kit-lock glob/M5/single-document guard). Zero engine bytes changed;
`proposal-implementation` untouched; all six success criteria this slice
owns are met.

## Follow-on changes (not sequenced here)

- **B** — `Data/` demandable per product folder
- **C** — per-document claim vocabulary + real per-document fidelity (deletes A4's D10 guard as its first act)
- **D** — cross-document agreement, block locator, Flow B to submission

Out of scope for A: B, C, D; the kit crossing the seam; any rename of
`proposalDigest`/relatives; `_resolve()`/`_impact_class` group-count
validation (M2's resolver-level fix); F6.
