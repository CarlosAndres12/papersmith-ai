# Design: A north a second domain can hold

## Technical Approach

The north's *structure* stays in core (shape, `STATUS` placement, the two host error
paths); its *text* moves to `DeliberationDomainProfile.objective`, validated at load
like `artifact`. `cli.mjs` already imports engine modules through jiti; it reads
`DOMAIN.objective` and the `OBJECTIVE_FLOW` literal is deleted. Every guard that
today names one skill is re-derived from whatever profiles exist on disk.

## Architecture Decisions

### Decision A: how the Python seal reads a north that is no longer Python

**Choice.** Two independent repairs, both required:
1. Bind agent→skill by the **body `Skill:` path**, not the agent filename.
   `test_every_agent_names_a_skill_that_exists` already parses and asserts that
   binding; the seal invented a weaker one. This alone takes coverage 1/5 → 5/5.
2. `declared_arrival(skill)` tries the Python `OBJECTIVE_FLOW` (`ast`, unchanged),
   then falls back to an anchored regex over `<skill>/profile.ts` for a
   single-line `arrival: "…"`. Both present in one skill ⇒ raise, never pick.
   Fail closed: a `profile.ts` whose arrival does not parse fails the test.

**Measured, and it changes the seal's own claim.** The property "the description
carries its skill's `arrival`" is **false by design for 2 of 5 agents**:
`implementation-build` ends at "the findings report" (stage `audit`) and
`implementation-walk` "stops at the launch" (stage `rehearsal`). Neither ends at
`proposal-implementation`'s arrival, and forcing it would make two correct
descriptions lie. So each agent declares its end in frontmatter:
`stretch: terminal` (description must contain the skill's `arrival` verbatim) or
`stretch: <stage>` (must be one of that skill's declared stage names). Coverage is
pinned, and skills that declare no north sit in a named `NORTHLESS_SKILLS` map
(`skill-audit`) rather than being silently skipped — `assertGreater(checked, 0)` is
replaced by an equality against the derived expected set.

**Rejected.** *Node subprocess `STATUS`*: ~0.7 s jiti cold start per skill, needs
node/jiti/a project root, and breaks the file's stdlib-only contract — an
environment problem would surface as a false red. *Generated JSON both languages
read*: a product that goes stale and needs its own freshness guard. *Read the
arrival from `SKILL.md` instead*: two links, and if the node link is dropped the
Python half still passes while proving nothing — the "protected half reads as proof
of the whole" failure.

### Decision B: typed refusals do not get the north; the prose gets corrected

**Choice.** Correct the false claim in `proposal-deliberation/SKILL.md` ("Every
refusal the engine raises carries it") and in `deliberation-publish.md` ("Every
error the engine returns carries an `objective` block") to the true one: *`STATUS`
reports it above the inventory, and both of this host's error paths carry it; a
typed refusal returned from the engine does not — run `STATUS` to recover it.* The
existing test already pins exactly those three sites (error-path count `2`, STATUS
placement), so the corrected sentence is the sentence that is measured.

**Rationale.** Attaching is cheap in one place (wrap `run()`'s `tool.execute`
result) but wrong here: it changes **both** domains' response shape inside a change
whose constraint is that `proposal-deliberation` behaves identically; and the host
would have to classify what counts as a refusal (`status:'blocked'` appears in 6
engine files, `'error'`/`blocked:true` elsewhere) — a host-side classifier that
guesses attaches to *some* refusals and leaves the doctrine sentence still false,
but harder to disprove. Attaching per-site is excluded outright: it would require
editing `successor-composite-engine.ts`, which must stay byte-identical. Record
attachment as a deferred item with its own refusal taxonomy.

### Decision C: the domain-subject guard, in three layers, with its limits stated

| Layer | What it checks | Would it have caught the north? |
| --- | --- | --- |
| C-1 absence | no core file contains a `purpose:`/`arrival:`/`behindWhen:` string literal or an `OBJECTIVE_FLOW` object; the north is reached only via `DOMAIN.objective` | **Yes**, regardless of vocabulary |
| C-2 extended lock | discover every `.claude/skills/*/profile.ts`; union `declared`+`names` (core+suite) and `artifact.{directory,stem,sidecarRoot}` (core only) | No — "mathematics" is not a declared value |
| C-3 derived subject words | a word (≥5 chars) used by **exactly one** profile's north is subject matter and may not appear in core; a word both norths use is engine vocabulary | Yes, once the text lives in a profile |

C-3 needs no hand-written denylist because the allowlist is derived from the other
profile. **Its limits, stated:** it needs ≥2 profiles, it cannot see a word both
norths happen to share, and it could not have fired before the text moved.

**Measured consequences that must be handled, not discovered:**
- C-2 extended to the experimental profile turns three core sites red — all real
  leaks: `domain-profile.ts` (two `"experiments"` doc-comment examples),
  `proposal-workspace.ts` (a comment naming the experiments document),
  `initial-revision-creation.ts` (names `experimental-deliberation`'s test file).
  Reword all three.
- The **suite** scan must exclude a profile's `names` when the name equals the
  profile's own skill-directory name: 25 occurrences across 6 node tests are import
  paths, tmpdir prefixes and sidecar-root assertions. `CREDA` (a research subject)
  stays in the suite scan; `experimental-deliberation` (a module namespace) does
  not. Derived, not exempted by hand.
- The lock's hardcoded `docs` list becomes a glob over `.claude/skills/*/SKILL.md`
  and `*/references/usage.md` plus `README.md`.
- C-3 fires on a **pre-existing** residue: `equation` is a core *type name*
  (`display_equation`, `CLEANUP_EQUATION_FORBIDDEN`, `equationLabel`,
  `SAFE_EQUATION_LABEL`) with ~110 occurrences across 15 core files, two of them
  byte-frozen. It is pinned by exact total count **and** the sorted file list, so it
  is visible and can only shrink deliberately — never exempted into silence.

## Interfaces / Contracts

```ts
readonly objective: {
  readonly purpose: string;
  readonly stages: readonly { stage: string; establishes: string; behindWhen: string }[];
  readonly arrival: string;                       // single-line literal: the Python seal reads it
  readonly entrances?: readonly { from: string; arrivesAt: string; note: string }[];
  readonly humanStops: readonly string[];
};
```

`objective` joins `REQUIRED`. A nested `OBJECTIVE_REQUIRED` check (same
`DELIBERATION_DOMAIN_PROFILE_INCOMPLETE` code, naming `objective.<field>`) covers
`purpose`/`stages`/`arrival`/`humanStops`, because `objective: {}` would otherwise
pass vacuously — the exact bug `artifact: {}` already taught this file. `stages`
must be non-empty and every element must carry all three keys. `entrances` is
optional; `arrivesAt` must name a declared stage.

## The generalized objective-flow test

Discovers every `profile.ts` declaring an `objective`, pairs it with its sibling
`SKILL.md`, and pins the pair count at **2** ("a third is a decision"). Per pair, by
text: stage names and order equal between profile and doctrine table; `arrival`
equal after whitespace normalisation (new — today `arrival` text is compared
nowhere); ≥1 stage whose `behindWhen` refuses measurement; ≥1 `humanStops` entry;
each declared entrance's `arrivesAt` is a declared stage, with a global assertion
that ≥1 profile declares an entrance so the check is never vacuous. Core-scoped
tests keep the error-path count (2), the `STATUS` placement, and add C-1.

## Answers to the proposal's four questions

1. **`validated` is a north stage.** "The engine does not enforce it" cannot
   disqualify it — `deliberated` is in the north *because* nothing enforces it. The
   difference is that `validated`'s end is byte-decidable
   (`url-without-verification-marker`, `baseline-missing-repository-url`,
   `baseline-missing-venue-year`), which is why it may be delegated.
   `experimental-deliberation/SKILL.md`'s "not an engine stage" line is reworded, not
   removed.
2. **No `entrances` for the experimental domain.** `proposals/` is a required
   *source* read at v1 render, not a session arriving mid-flow, and no skill hands
   this one a finding. Declaring an entrance nothing produces is a claim with no
   producer.
3. **Fix the seal here.** This is the change that makes the seal unable to read the
   deliberation north at all; shipping it broken would ship a guard that provably
   cannot see the domain being added.
4. **`[verified: YYYY-MM-DD]` is acceptable** with its limit written into the agent's
   own bytes: it bounds the trace, not the truth, so the agent returns the query it
   ran in `did` and the tag is re-measurable.

## The two agents

`experimental-publish` — near-copy of `deliberation-publish` (63 lines). Three
domain-bound lines change: `description` (carries the experimental arrival
verbatim), the `Skill:` path, and "this pair of skills" in *Agreement is not
arrival* — that phrase names the implementation handoff, which this domain does not
have; it becomes what is actually lost here (an agreed experiment that never reaches
a published version). Adds `stretch: terminal`.

`experimental-validation` — owns the external-validation stretch. `stretch:
validated`. Tools `Read, Glob, Grep, WebSearch, WebFetch` (no `Write`: the engine
writes). Both get rows in `experimental-deliberation/SKILL.md` with the exact
`delegates to the \`<agent>\` agent` phrasing and a **Measure this before
delegating** entry, or three existing Python tests go red.

The role discipline is **copied, not extracted** (decision already taken). The new
`test_every_agent_carries_the_shared_role_discipline` asserts a named fragment tuple
in every agent's own bytes — the return-contract heading and its four fields, "never
conclusions", "measured again", "Measure before you assert", and the corrected north
sentence — and asserts the number of files checked equals the number of agent files,
so a skipped agent is a failure rather than a lower number. Overlap with existing
tests is acknowledged: only *Measure before you assert*, the corrected sentence, and
the coverage equality are new.

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `_core/…/engine/domain-profile.ts` | Modify | `objective` type + `REQUIRED` + nested validation; reword two `"experiments"` examples |
| `_core/…/engine/cli.mjs` | Modify | delete `OBJECTIVE_FLOW`; read `DOMAIN.objective` at 3 sites |
| `_core/…/engine/proposal-workspace.ts` | Modify | reword one comment naming the experiments document |
| `_core/…/engine/initial-revision-creation.ts` | Modify | reword one comment naming a skill by directory |
| `proposal-deliberation/profile.ts` | Modify | today's north, byte-identical text |
| `proposal-deliberation/SKILL.md` | Modify | correct the refusal claim; note the north's new home |
| `experimental-deliberation/profile.ts` | Modify | the experimental north |
| `experimental-deliberation/SKILL.md` | Modify | objective-flow section; delegation table; reword line 55 |
| `tests/proposal-deliberation-objective-flow.test.mjs` | Modify | profile-derived; + C-1 |
| `tests/proposal-deliberation-domain-profile-lock.test.mjs` | Modify | all profiles; globbed docs; + C-3 |
| `tests/test_agents.py` | Modify | seal rewrite; discipline test |
| `.claude/agents/*.md` (5) | Modify | add `stretch:` frontmatter |
| `.claude/agents/experimental-{publish,validation}.md` | Create | the two agents |

## What breaks — products as well as producers

| Product | Verdict |
| --- | --- |
| Managed revisions on disk (`proposals/`, `experiments/`) | Untouched — the north is never written into a document. **Apply must verify by grep, not assume.** |
| Sidecar state/receipts | Untouched — receipts record operations, not `STATUS` payloads. Same verification duty. |
| `deliberation-publish.md`'s description | Still valid (the arrival is re-declared byte-identically) but newly *checked* — verify the substring holds. |
| `implementation-{build,walk}.md` descriptions | Newly reachable by the seal and **do not** carry the arrival. Handled by `stretch:`, not by editing them into a falsehood. |

## Mutation plan

Every row: break the line, the anchor count must change, the named test goes red,
restore, count returns, green. An unchanged anchor count means the mutation never
ran. Python mutations clear `__pycache__` first.

| # | Break | Anchor (before → after) | Must go red |
|---|---|---|---|
| M1a | delete `objective:` from the experimental profile | `^\tobjective: {` 1→0 | loader INCOMPLETE names `objective` |
| M1b | delete only `arrival:` | `arrival: "` 1→0 | INCOMPLETE names `objective.arrival` |
| M1c | `stages: []` | `stage: "` 5→0 | INCOMPLETE names `objective.stages` (a weaker top-level-only check survives this) |
| M2a | rename `composed`→`assembled` in one profile | `stage: "composed"` 1→0 | stage-name equality, that pair only |
| M2b | swap two stage objects | index order inverted | stage-order assertion |
| M2c | delete `objective` from one profile | profiles-with-objective 2→1 | pinned pair count — proves the test is not checking one skill |
| M3a | drop the arrival clause from `deliberation-publish.md`'s description | arrival occurrences 1→0 | the seal. **Run against the OLD seal first and record it surviving**, then against the new one and record it dying |
| M3b | set `implementation-walk.md` to `stretch: rehearsl` | `stretch: rehearsal` 1→0 | stage-name membership |
| M3c | remove `skill-audit` from `NORTHLESS_SKILLS` | map length 1→0 | coverage equality |
| M4a | add `experimental_plan_base.md` to a core comment | core occurrences 0→1 | "no file in the shared core names a domain" |
| M4b | add `.experimental-deliberation` to a core comment | 0→1 | artifact-namespace scan — proves the *second* profile is in it |
| M5 | paste an `OBJECTIVE_FLOW` object with a `purpose:` literal into `cli.mjs` | `purpose: '` in core 0→1 | C-1 absence |
| M6a | put `mathematics` in `edit-planner.ts` | 0→1 | C-3, naming file and word |
| M6b | delete one `equation` from a non-frozen core comment | total N→N−1 | the residue pin is live, not decorative |
| M6c | copy one profile's `purpose` over the other's | unique-token set → empty | C-3's own vacuity assertion |
| M7a | delete `## Measure before you assert` from `experimental-publish.md` | heading 7→6 across agents | discipline test |
| M7b | same, in `implementation-walk.md` | 7→6 | proves the test covers agents this change did not author |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file
classification, or process-integration boundary. The seal deliberately *avoids*
introducing a subprocess (Decision A, rejected option 1); the profile loader's
existing `SAFE_ARTIFACT_SEGMENT` path validation is unchanged and `objective` carries
no path.

## Migration / Rollout

No migration. No artifact on disk carries state from this change. Rollback is the
commit range; the north returns to a core const and both skills keep launching.

## Revised review workload

The proposal forecast ~670 lines. Measurement moved it: the seal is a redesign, not
a repair (2 of 5 agents cannot carry an arrival), and C-2 turns four extra files
red.

| Item | Forecast |
|---|---|
| Parametrize + generalized flow test | ~360 |
| Experimental north | ~130 |
| Two agents + SKILL.md rows | ~170 |
| Seal rewrite + `stretch:` on 5 agents + discipline test | ~140 |
| Lock generalization + 4 core rewordings + C-3 | ~150 |
| **Total** | **~950 of 1400** |

Two clean slices if the delivery strategy asks: **A** = profile/core/tests
(core-facing), **B** = agents/seal (needs A's arrival to exist). Sequential chain.

## Open Questions

- [ ] Do `implementation-build`/`implementation-walk` end at exactly `audit` and
      `rehearsal`? Read from `implementation_cli.py`'s `OBJECTIVE_FLOW` and confirm
      at apply — the mapping is inferred from their descriptions, not declared.
- [ ] Exact `equation` residue count and file list — measure at apply and pin.
