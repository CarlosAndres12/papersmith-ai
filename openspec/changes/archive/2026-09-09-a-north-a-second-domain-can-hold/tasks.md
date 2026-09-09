# Tasks: A north a second domain can hold

## Review Workload Forecast

| Field | Value |
|---|---|
| Estimated changed lines | ~950 of 1400 session budget (design) |
| 400-line budget risk | High — design's 2-slice split still puts Unit A at ~640 lines |
| Chained PRs recommended | Yes |
| Suggested split | 4 units, stacked, each under 400 (correction below) |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

**Correction to design's 2-slice plan**: design proposes A(~640)/B(~310); A alone exceeds
the 400-line PR guard. Split A along its own stated sub-dependencies (parametrize →
experimental north → guard layers) into 3 units; B unchanged as unit 4.

### Suggested Work Units

| Unit | Goal | PR | Focused test | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 | `objective` field + REQUIRED + nested validation; `cli.mjs` reads `DOMAIN.objective`; `proposal-deliberation/profile.ts` byte-identical; generalized flow test | 1 | `npm test -- proposal-deliberation-objective-flow` | `node .claude/skills/proposal-deliberation/cli.mjs status` | revert `domain-profile.ts`, `cli.mjs`, `proposal-deliberation/profile.ts`, the flow test |
| 2 | `experimental-deliberation/profile.ts` north; its `SKILL.md` objective section + line-55 reword | 2 (base=1) | `npm test -- experimental-deliberation-domain-profile` | `node .claude/skills/experimental-deliberation/cli.mjs status` | revert `experimental-deliberation/profile.ts`, `SKILL.md` |
| 3 | C-1/C-2/C-3 lock generalization; 3 core rewordings; equation-residue pin | 3 (base=2) | `npm test -- proposal-deliberation-domain-profile-lock` | N/A — static scan, no process | revert lock test + the 3 reworded files |
| 4 | seal rewrite, discipline test, `stretch:` on 5 agents, 2 new agents | 4 (base=3) | `.venv/bin/python -m unittest tests.test_agents` | N/A — pytest-only, no subprocess (Decision A rejects one) | revert `test_agents.py` + 7 agent files |

## Phase 0: Measurements (block later phases)

- [x] 0.1 Read `implementation-build`/`implementation-walk`'s bound skill north (via `Skill:` path) to confirm they end at stages `audit`/`rehearsal`; record exact stage names for task 4.4.
- [x] 0.2 Recount the `equation` residue with an occurrence-accurate command (`rg -o`, not line-count — a same-line multi-match undercounts, e.g. measured 105 by line vs 126 by occurrence on this repo) and the sorted file list; pin both in task 3.6.

## Phase 1: Parametrize (Unit 1)

- [x] 1.1 RED: extend `domain-profile.ts`'s profile-loader test for `objective` missing/incomplete (`purpose`/`stages`/`arrival`/`humanStops`) → `DELIBERATION_DOMAIN_PROFILE_INCOMPLETE` naming `objective.<field>` (Req: content is profile-supplied).
- [x] 1.2 GREEN: add `objective` type + nested `OBJECTIVE_REQUIRED` validation to `domain-profile.ts`.
- [x] 1.3 `proposal-deliberation/profile.ts`: declare today's exact `purpose`/`stages`/`arrival` text, byte-identical.
- [x] 1.4 `cli.mjs`: delete `OBJECTIVE_FLOW`; read `DOMAIN.objective` at `runStatus` + both catch handlers.
- [x] 1.5 Correct `proposal-deliberation/SKILL.md`'s reach claim (STATUS + 2 error paths only, not every refusal).
- [x] 1.6 Generalize `proposal-deliberation-objective-flow.test.mjs`: derive stages/order from loaded profile; keep error-path count (2), STATUS placement; add whitespace-normalized `arrival` equality (new).
- [x] 1.7 Mutation-prove M1a–M1c (design table): delete `objective:`, delete only `arrival:`, empty `stages:` — assert each names the right missing field, restore, re-baseline.
- [x] 1.8 Mutation-prove M2a–M2c: rename a stage, swap stage order, drop `objective` from one profile (pinned pair-count 2→1) — each must fail the right assertion.

## Phase 2: Experimental North (Unit 2)

- [x] 2.1 RED: extend `experimental-deliberation-domain-profile.test.mjs` for the new `bound → validated → deliberated → composed → published` north (no `entrances`).
- [x] 2.2 GREEN: `experimental-deliberation/profile.ts` declares the north; reword `SKILL.md` line 53's "not an engine stage" line without removing the "validated is not enforced" fact.
- [x] 2.3 Verify `runStatus`/error paths on the experimental CLI emit the experimental stages, not the mathematical ones (spec scenario: "experimental profile declares its own north").

## Phase 3: Guard Layers (Unit 3)

- [x] 3.1 RED: extend `proposal-deliberation-domain-profile-lock.test.mjs` for C-1 (no core file contains `purpose:`/`arrival:`/`behindWhen:` literal or `OBJECTIVE_FLOW`). NOTE: implemented in `proposal-deliberation-objective-flow.test.mjs` instead, per design.md's own File Changes table and prose ("Core-scoped tests keep the error-path count (2), the STATUS placement, and add C-1") — this contradicts this task line's placement; design.md was treated as authoritative per apply instructions. See apply report.
- [x] 3.2 GREEN: add the C-1 absence scan.
- [x] 3.3 RED+GREEN: C-2 — glob every `*/profile.ts`, union `declared`+`names`+`objective` text; glob docs (`*/SKILL.md`, `*/references/usage.md`, `README.md`) instead of the hardcoded list; exclude a profile's `names` value when it equals its own skill-directory name (derived, not hand-exempted).
- [x] 3.4 Reword the 3 real C-2 leaks: `domain-profile.ts` (2 `"experiments"` doc-comment examples), `proposal-workspace.ts` (comment naming the experiments doc), `initial-revision-creation.ts` (comment naming `experimental-deliberation` by directory). Plus 2 additional C-3-driven leaks discovered during measurement (`types.ts`, `target-resolver.ts` — see apply report) and 2 more `mathematics` occurrences design's table did not enumerate (`domain-profile.ts`, `preservation.ts`, `proposal-workspace.ts`).
- [x] 3.5 RED+GREEN: C-3 — derived denylist (word ≥5 chars used by exactly one profile's `objective` text); global vacuity assertion (≥2 profiles). Extended with a measured, generalized residue-pin mechanism (see apply report) covering both `equation` (task 3.6) and `proposal` (newly discovered).
- [x] 3.6 Pin the `equation` residue by exact occurrence count and sorted file list from task 0.2. Re-measured at apply time as 124/10 files (not 126/11) because Phase 1 legitimately deleted `cli.mjs`'s own `OBJECTIVE_FLOW` literal, which spelled "equation" twice — see apply report.
- [x] 3.7 Mutation-prove M4a–M4b, M5 (C-1/C-2), M6a–M6c (C-3, incl. the vacuity self-check) — anchor before/after, named failing assertion, restore. M6c mutated as "copy the whole objective block" rather than "copy just purpose" — see apply report for why the literal task wording did not produce vacuity against this repo's real text.

## Phase 4: Agents + Seal (Unit 4)

- [x] 4.1 RED: `test_agents.py` — bind agent→skill via the already-asserted `Skill:` path (not `path.stem`); rewrite `declared_arrival` to try Python `OBJECTIVE_FLOW` then fall back to an anchored `<skill>/profile.ts` `arrival: "…"` regex, raising if both present, failing if `profile.ts` exists and none parses. Implemented as `declared_objective` (returns arrival + stages) built on `_python_objective`/`_typescript_objective`, plus a new `bound_skill()` helper.
- [x] 4.2 GREEN: replace `assertGreater(checked, 0)` with equality against a derived expected set; add `NORTHLESS_SKILLS = {"skill-audit"}`. Measured coverage 1/5 → 6/7 (audit-report/skill-audit correctly excluded as northless).
- [x] 4.3 Add frontmatter `stretch: terminal` to `deliberation-publish.md`, `paper-ingestion.md`, `audit-report.md` (each description carries its skill's arrival verbatim). NOTE: `audit-report.md` did NOT get `stretch:` — `skill-audit` is northless (no OBJECTIVE_FLOW, no profile.ts), so it has nothing to name; only `deliberation-publish.md`/`paper-ingestion.md` got `stretch: terminal`. Task wording assumed all 3 qualify; measurement showed 2.
- [x] 4.4 Add `stretch: audit` to `implementation-build.md`, `stretch: rehearsal` to `implementation-walk.md` per task 0.1's confirmed mapping.
- [x] 4.5 RED: `test_every_agent_carries_the_shared_role_discipline` — asserts the return-contract heading + 4 fields, "never conclusions", "measured again", "Measure before you assert", and the corrected north sentence in every agent's own bytes; asserts checked count == agent file count.
- [x] 4.6 GREEN: create `.claude/agents/experimental-publish.md` (copy of `deliberation-publish.md`; rewrite `description`, `Skill:` path, and "Agreement is not arrival" for the experimental domain's own loss — no implementation handoff; add `stretch: terminal`).
- [x] 4.7 GREEN: create `.claude/agents/experimental-validation.md` (`stretch: validated`; tools `Read, Glob, Grep, WebSearch, WebFetch`, no `Write`; measures `preservation-experimental.ts::violations` rules `url-without-verification-marker`, `baseline-missing-repository-url`, `baseline-missing-venue-year`).
- [x] 4.8 Add both agents' rows to `experimental-deliberation/SKILL.md`'s delegation table (`delegates to the \`<agent>\` agent` phrasing) + a "Measure this before delegating" entry each.
- [x] 4.9 Mutation-prove M3a (run against the OLD seal first, record it surviving; then the NEW seal, record it dying), M3b, M3c, M7a–M7b. All 5 executed with real anchor counts, cp-aside/restore, and re-baselined green. M7a/M7b run against `experimental-publish.md` (new) and `implementation-walk.md` (pre-existing) respectively, proving the discipline test covers both.

## Phase 5: Full-Suite Verification

- [x] 5.1 `npm test` → 548 pass / 0 fail held (Phase 0–3 baseline; no change from Phase 4).
- [x] 5.2 `.venv/bin/python -m unittest discover -s tests` → Ran 2779, OK (skipped=6) — exactly +1 over the 2778 baseline: the one new `test_every_agent_carries_the_shared_role_discipline` test method (the seal test itself, `test_a_description_carries_the_arrival_its_skill_declares`, was rewritten in place, not added, so it does not change the count).
- [x] 5.3 `npm run typecheck` → exactly the 2 known `smoke-runner.ts` errors, no new ones.
- [x] 5.4 Grep `proposals/`, `experiments/` sidecar output and receipts for any north text — confirmed untouched: `proposals/` holds only `.gitkeep`, `experiments/` does not exist, and no `.proposal-deliberation`/`.experimental-deliberation` sidecar directories exist anywhere in the tree.

## Key Learnings

1. Design's 2-slice PR plan understates risk: its own ~640-line Unit A exceeds the 400-line guard and needed a 4-way split along its stated internal dependencies.
2. `rg` line-count and occurrence-count diverge on multi-match lines (105 vs 126 for "equation" here) — mutation-proof anchors must use occurrence-accurate counts.
3. The seal's own property is false by design for 2 of 5 agents, so the fix is a `stretch:` field, not a stricter parser.
