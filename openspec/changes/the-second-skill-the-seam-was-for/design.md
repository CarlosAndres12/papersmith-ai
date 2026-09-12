# Design: The second skill the seam was for — slice A

**Scope: change A only** — `experimental-implementation` on disk with a
**single** declared document. B (`Data/` per product folder), C (the claim
vocabulary scalar→pair) and D (cross-document agreement, the successor
composer, Flow B to a submission) are named as follow-ons and designed
nowhere below.

## Technical Approach

A adds a second **host** to the shared implementation engine and changes the
engine by **zero bytes**. Everything new is a profile, a launcher, a doctrine,
two agents and tests. The bar — `proposal-implementation` untouched, all 28
sealed digests byte-identical, `npm test` 595/595, Python `OK (skipped=6)` with
`Ran` grown — is met structurally: the engine is not edited, so it cannot move,
and the sibling's profile is not edited, so its digests cannot move. Everything
below that could move a digest is therefore a *test-side* decision, and each is
ruled on by name.

## Measurements that change the proposal's shape

Every symbol here was grepped this session, by name, never by line.

**M1 — `test_every_declared_name_really_is_that_domain_speaking` is vacuous for
every profile, not only for a namespace word.** It searches
`entry["source"]` — the profile file's whole text — which *contains the
`names` list literal itself*. Any name written as a literal is found in its own
declaration. The sibling's seven words pass for that reason too. So nothing the
second profile declares can make this check non-vacuous; the check must change
(D6). The TS original (`proposal-deliberation-domain-profile-lock.test.mjs`,
`every declared name really is that domain speaking`) has the same shape and
the same hole.

**M2 — `citation_pattern` must expose exactly three groups, and nothing
validates it.** `_impact_class` reads
`match.group(1) or match.group(2) or match.group(3)`. A two-group pattern
raises `IndexError` inside `finding_impact`; a four-group pattern silently
drops the fourth. `impl_domain_profile._resolve()` checks presence only.

**M3 — the kit is ~99% general, so A ships none.** `\b(equation|ecuaci…|
mathematic…|formulation)\b` occurs on **18 lines across 9 files** of the
~2,000-line `proposal-implementation/assets/` tree. Copying 2,000 lines to
change 18 is the duplication the operator refused for the CLI, one directory
over. Consequence, stated rather than discovered: commands that read a kit
asset are not available in this domain under A.

**M4 — the launcher can be byte-identical, all 24 lines.** Every value in
`scripts/implementation_cli.py` is derived from `Path(__file__).resolve()`
(`_HERE.parents[1] / "impl_profile.py"`, `_HERE.parents[2] / "_core" /
"implementation" / "engine"`). A byte-for-byte copy placed in the new skill
resolves to the new skill's own profile. That is Cut 1's design property made
visible.

**M5 — `tests/seal/harness.py` lives inside `tests/seal/`.** The bar
`git diff --exit-code tests/seal/` exits 0 therefore forbids adding a
`cli_invocation` parameter to `run_case`, which was the obvious move. D7 takes
the pair suite's existing wrapper idiom instead.

**M6 — the doctrine, priced.** The deliberation precedent re-authored a *full
parallel* doctrine: `experimental-deliberation/SKILL.md` **383** vs
`proposal-deliberation/SKILL.md` **322**, and `references/usage.md` **424** vs
**305** — both larger, not thinner. Mirrored here (2,854 + 2,264) that is
**~6,100 lines for A's doctrine alone**, against a `review_budget_lines: 1400`
and a whole-proposal estimate of 3,850–6,250. D8 rules against mirroring.

**M7 — `ENTRANCE_CLAIMS` contains `"the implementation skill"`.** The new
north declares no `entrances`, so `declared_entrances` returns `[]` and
`test_an_agent_never_claims_an_entrance_its_skill_does_not_declare` holds both
new agents to all five phrases. This check exists *because*
`experimental-publish` was written from `deliberation-publish` as a template —
the exact thing A does twice.

## Architecture Decisions

### D1 — The declared document is the **experiments** document

`documents[0] = {"directory": _FORGE_ROOT / "experiments", "label":
"experiments"}`.

| Option | Consequence |
|---|---|
| `documents[0]` = `proposals/`, label `proposal` | The profile becomes the sibling's vocabulary byte for byte; no leaf is mutation-provable as *this* domain's; the skill has no path to the document it exists for |
| **`documents[0]` = `experiments/`, label `experiments`** | Every vocabulary leaf carries this domain's own value; C adds the mathematical proposal as `documents[1]` |

Answers the proposal's Q4: the label word is `experiments`; the *index* is 0
here, and C's second entry is the mathematical document. `experiments/` holds
only `.gitkeep` — existence is not required (`_resolve`'s absolute-only tier).

### D2 — The profile: 19 leaves, 2 of them structurally identical

`_REQUIRED_NESTED` (2) + `_REQUIRED_PRESENCE` (14) = the 16 validated leaves,
plus `objective` and `documents[0]`'s two.

| Leaf | Engine reader | This skill's value |
|---|---|---|
| `kit.root` | `SKILL_ROOT` | **structurally identical** (`_SKILL`) |
| `cli.path` | `CLI_PATH` → `CLI_INVOCATION` | **structurally identical** (`_SKILL / "scripts" / …`) |
| `objective` | `OBJECTIVE_FLOW`, stamped into every refusal; read by `test_agents.py` | own north (D3) |
| `provenance.claim_key` | `CLAIM_KEY` | `"experiments"` |
| `provenance.authored_init_sentence` | `AUTHORED_INIT_SENTENCE` | own sentence naming `sections` and `experiments` |
| `findings.locus_key` | `LOCUS_KEY` | `"experiments"` |
| `findings.remedy_locus_key` | `REMEDY_LOCUS_KEY` | `"remedy_experiments"` |
| `findings.notation_keys` | `NOTATION_KEYS` | `experiments` / `remedyExperiments` / `unknownExperiments` |
| `findings.citation_pattern` | `CITATION_RE` | `(Exp. N)` bilingual, **exactly three groups** (M2) |
| `vocabulary.subject_*` ×6, `artifact_noun` | `SUBJECT_*`, `ARTIFACT_NOUN` | experiment/experiments/experimento/experimentos/experimentation/experimentación/`protocol` |
| `vocabulary.names` | both neutrality locks | D6 |
| `documents[0].directory` / `.label` | `DOCUMENTS_DIRECTORY`, `DOCUMENTS_LABEL`, `proposals_root()` | D1 |

Rule carried forward from Cut 2 and from this project's scars: **a leaf earns
its place by being read and by being mutation-provable.** No leaf is added
here that the engine does not already read; a leaf whose value would be
byte-identical to the sibling's is a leaf that is not domain-specific, and
`authored_init_sentence` is the only near-miss — it differs by its subject
word and is kept for that reason, not for symmetry.

### D3 — `OBJECTIVE_FLOW`, its own north, in `impl_profile.py`, and no `profile.ts`

`test_agents.py::_python_objective` walks `(SKILLS / skill).rglob("*.py")` and
`ast.literal_eval`s a **module-level `OBJECTIVE_FLOW` assignment**, so the
north must physically live in the skill's own tree as a literal (never a call,
never a derived expression). `declared_objective` **raises** when a skill
declares both a Python north and a `profile.ts`, so this skill ships no
`profile.ts` at all.

Shape (five stages, a different arrival from the sibling's six):
`standing` → `binding` → `instrumentation` → `rehearsal` → `full-scale`;
arrival = complete runs at the protocol's declared scale with a record
checkable against the experiments revision. Two hard constraints:

* No `behindWhen` may match `UNMEASURABLE`
  (`nothing here measures it|the user said so`). If one does,
  `test_an_unmeasurable_stage_is_never_delegated` obliges **both** agents to
  name the stage and any `stretch: terminal` agent to carry four exact
  disclaimer sentences. A declares no such stage.
* The north's prose feeds M5's denylist (D9), so its wording is fixed
  **before** the residue pin is measured.

### D4 — The launcher: byte-identical, copied, never shared

A byte-for-byte copy of `proposal-implementation/scripts/implementation_cli.py`
(M4). Not a symlink, not an import of the sibling's file: deleting the sibling
must not break this skill, which is the rollback plan's whole claim. What must
**not** be shared is the file; what must **stay** identical is its bytes —
24 lines, zero logic, every path self-anchored. A launcher that needs a
domain-specific line is a launcher doing something the seam forbids, so the
new skill's own suite asserts the two files' bytes are equal, with that
reason recorded.

### D5 — Two agents, `experiments-build` and `experiments-walk`

`experimental-*` already prefixes the *deliberation* domain's agents
(`experimental-publish`, `experimental-validation`), so the new pair takes the
document's own label: `experiments-build.md`, `experiments-walk.md`.

* `experiments-walk` is close to a verbatim copy of `implementation-walk.md`:
  the `Skill:` path and the skill name in the north sentence change, plus
  `stretch: rehearsal` re-pointed at *this* north's `rehearsal`.
* `experiments-build`'s two ends move, and its `stretch:` must name a stage in
  **this** north (`instrumentation`) or
  `test_a_description_carries_the_arrival_its_skill_declares` fails.
* Neither may spell any of the five `ENTRANCE_CLAIMS` phrases (M7).

**On the duplication.** Four near-identical files is not the duplication the
operator refused for the CLI, and the difference is measurable: the CLI was
17,100 lines of *behaviour*; an agent file is ~70 lines of prose with **zero**
logic. The role-discipline block cannot be extracted — that decision is already
recorded, in `test_every_agent_carries_the_shared_role_discipline`'s own
docstring: *"a shared fragment could only be asserted by REFERENCE, and whether
an agent actually loaded it is unmeasurable."* What **is** shared is the
enforcement: every check in `test_agents.py` globs `.claude/agents/*.md`, so
the two new files are held to all eleven checks the day they land, without that
suite being edited. Shared enforcement, copied prose — the inverse of the CLI.

### D6 — The `names` collision: the check is what changes

Declared: `["experimental-implementation"]` — the namespace word, matching
`experimental-deliberation`'s recorded reason — **plus** each subject
vocabulary value measured absent from the engine. The engine spells
`experiment(s)` **30** times, `benchmark(s)` **89**, `baseline(s)` **28**
(case-insensitive, word-boundary; the brief's 88/23/20 were line counts), and
those are general machinery, so they are excluded with the reason written into
the profile exactly as the sibling writes its `proposal` exclusion. Candidates
admitted one word at a time, each only after measuring `\bword\b == 0` in
`implementation_engine.py`.

Per M1, that alone leaves Lock A vacuous. So **Lock A changes**: the haystack
becomes the profile's declared **values** (every string/`Path` leaf rendered as
text) with `vocabulary.names` itself excluded — never the raw source. The
sibling stays green unedited: all seven of its names appear in
`vocabulary.subject_*`/`artifact_noun` values (read, not assumed). The
namespace word qualifies through `str(kit.root)`, and that is the honest
reason it is declarable — the skill directory really is named that. A name
that is neither a subject value nor the skill's own path now fails, which is
the property the old check only appeared to have.

### D7 — A second sealed corpus, `tests/seal/` byte-untouched

`tests/experiments_seal/{corpus.py,cases.json,digests.json,unsealed.json}` plus
`tests/test_experiments_seal.py`, mirroring `tests/pair/`'s precedent
(`Roots` duck-typed against `seal.corpus.Roots`, driven through
`seal_harness.run_case`). Because `run_case` builds argv from
`impl.CLI_INVOCATION`, and `tests/seal/harness.py` may not be edited (M5), the
new suite wraps that attribute in-process for the duration of the call — the
same shape `test_implementation_pair.py::_build_env_with_profile_override`
already uses for `build_env`. **This is not the monkeypatch scar**: it changes
the argv the parent passes, not any state inside the child. The child needs no
`IMPLEMENTATION_DOMAIN_PROFILE`: `build_env` emits an explicit dict without
it, so the new launcher's own `setdefault` is what names the profile — which
makes every case an end-to-end proof of `cli.path` and `kit.root`.

Case roster derivation, not enumeration: every published command whose
execution reads **no kit asset** (M3) and **no `\tag{}`** (D10). Commands
excluded are recorded by id and reason in this corpus's own `unsealed.json`,
the idiom `tests/seal/unsealed.json` already uses for `propose`. Fixtures must
be authored from nothing — `proposals/` and `experiments/` hold only
`.gitkeep`.

### D8 — The doctrine A ships, and the doctrine it does not

Against M6: `experimental-implementation/SKILL.md` states **what differs** —
the north, the single document it binds, its claim vocabulary, the two
stretches with their delegation rows, the entry command, and **which commands
this domain cannot yet run and why**. It does not re-author the sibling's Flow
A/Flow B/`nextStep` routing, and A ships no `references/usage.md`.

This is a **deliberate divergence** from the deliberation precedent, which
re-authored everything. The reason: on that side the doctrine is 322 lines and
the parallel is affordable; here it is 2,854 + 2,264 and ~80% of it documents
one engine's command surface, which is shared by construction. Mark as a
claim: the divergence is a judgement about proportion, not a measurement.

Required by derived checks, so not optional: one
`` delegates to the `experiments-build` agent `` row and one for
`experiments-walk`, plus the literal heading fragment
`Measure this before delegating`. Every command string printed in the doctrine
must run verbatim through **this** skill's launcher — the sibling's
`PublishedCommandsRunVerbatimTests` is bound to `SKILL_ROOT =
proposal-implementation` and will not see this file, so the new suite carries
its own.

### D9 — M5 and the kit lock, both unblocked

**M5 (the derived denylist, TS C-3).** With a second profile on disk the
"others" set is non-empty. Python mirror of `buildDenylist`, reading
`profile["objective"]` directly (the module is already imported by
`discover_profiles()`; no `extractBlock` regex is needed): words of ≥5 letters
drawn from `purpose`, every stage's `establishes`/`behindWhen`, `arrival` and
`humanStops`; a word in exactly one profile's north is that domain's subject
and may not appear, word-boundary, in `_engine_files()`. Four separate test
methods (never one method with four asserts — `b3ca9aa`'s lesson):

1. vacuity — ≥2 profiles discovered **and** the denylist non-empty (the
   identical-norths self-check the TS lock records);
2. no unpinned denylist word appears in the engine;
3. every pinned residue word's occurrence count equals its pin **and is still
   in the denylist** (a pin for a word that left the denylist is a dead
   exemption);
4. no pinned word has a zero count.

`M5_PINNED_RESIDUE: dict[str, int]` is **measured at apply**, never written
from this design — the sibling's north spells `benchmark`, `fidelity`,
`audit`, `notebooks`, `premises` and more, and 421 engine lines carry at least
one such word. The pin is the TS lock's own `EQUATION_RESIDUE`/
`PROPOSAL_RESIDUE` discipline: measured, visible, may only shrink deliberately.

**The kit lock.** `KitAgreementLockTests._profile()` stops hardcoding
`proposal-implementation` and derives from `discover_profiles()`, filtered to
profiles that actually ship a kit (`kit.root / "assets" / "kit" / "src" /
"module.py"` exists), with `subTest(skill=…)` per profile, a non-empty
assertion, and a coverage equality against that derived set. **No `skipTest`**
— a skip would move the pinned `skipped=6`. A ships no kit (M3), so it is
recorded as kitless with its reason; a third skill *with* a kit is held the day
it appears.

### D10 — The single-document guarantee

`CLAIM_KEY`/`LOCUS_KEY`/`REMEDY_LOCUS_KEY`/`NOTATION_KEYS`/`CITATION_RE` are
module-level scalars read from `PROFILE[...]`, and
`_extra_document_fidelity_status` folds four conditions its own docstring calls
*document-count-invariant*. A `documents[1]` declared before C therefore yields
a fidelity status that reads green having measured nothing.

The guard is a **shipped-surface** lock, not a resolver refusal: a new test
class in `tests/test_implementation_domain_lock.py` asserting every profile
`discover_profiles()` finds declares exactly one `documents` entry, with a
vacuity guard and a message naming C. It must **not** go into
`impl_domain_profile._resolve()`: `tests/fixtures/two_documents/impl_profile.py`
and the whole `tests/pair/` suite depend on a two-document profile resolving,
and refusing `len > 1` there would take them down. `discover_profiles()` globs
`.claude/skills/*/impl_profile.py` only, so the fixture under `tests/` stays
invisible to the new lock — by the same reasoning that file already records.

C deletes this test as its first act, and its first RED test is the proposal's
own criterion: document 1's fidelity moves when document 1's text moves and
document 0 is clean.

### D11 — What `compose` needs, mapped but not built

The block locator is **two** regexes with **different** reach, and only one of
them is the composer's:

| Symbol | Read by | Reach |
|---|---|---|
| `TAG_RE` (`\\tag{…}`) | `remedy_compatibility` (2 sites), `cmd_compose` (2 sites), `cmd_admit` (1 site) | **3 functions** — and `remedy_compatibility` is itself read by `cmd_handoff` and `cmd_verify`'s audit block |
| `DISPLAY_BLOCK_RE` (`$$…$$`) | `cmd_compose` only | 1 function |

So D's profile-supplied locator owes **two** operations —
`claim_ids(text) -> [str]` (the `TAG_RE` role, 3 call sites) and
`locate_block(entry, claim_id)` (the `DISPLAY_BLOCK_RE` role, 1 call site).
Parameterising only the composer leaves `admit` and `remedy_compatibility`
reading LaTeX in a domain that has none, where they find **zero** tags and
report success: the same read-green-having-measured-nothing class as D10.
M1 recorded the composer; it did not record the other two. **A builds none of
this** — it excludes `compose`, `admit` and the audit block from the new
domain's available surface (D8) and from its seal roster (D7).

## Data flow

    experiments-{build,walk}.md ──loads──▶ experimental-implementation/SKILL.md
                                                     │
                            scripts/implementation_cli.py (24 bytes-identical lines)
                                       │ setdefault IMPLEMENTATION_DOMAIN_PROFILE
                                       ▼
                     experimental-implementation/impl_profile.py
                          (OBJECTIVE_FLOW + PROFILE, 19 leaves)
                                       │
                     _core/…/impl_domain_profile.py::_resolve()   ← UNCHANGED
                                       ▼
                     _core/…/engine/implementation_engine.py      ← UNCHANGED
                                       │
                  tests/experiments_seal/ (own digests)   tests/seal/ (28, untouched)

## File changes

| File | Action | Description |
|---|---|---|
| `.claude/skills/experimental-implementation/impl_profile.py` | Create | `OBJECTIVE_FLOW` + `PROFILE`, 19 leaves (D2/D3) |
| `.claude/skills/experimental-implementation/scripts/implementation_cli.py` | Create | byte-identical copy (D4) |
| `.claude/skills/experimental-implementation/SKILL.md` | Create | A-scoped doctrine (D8) |
| `.claude/agents/experiments-build.md`, `experiments-walk.md` | Create | ~70 lines each, no logic (D5) |
| `tests/test_experimental_implementation.py` | Create | leaf-refusal cases, launcher byte-equality, doctrine + published-command checks |
| `tests/test_experimental_implementation_mutation.py` | Create | per-leaf change-mutation, mirroring `test_implementation_domain_mutation.py` |
| `tests/experiments_seal/*`, `tests/test_experiments_seal.py` | Create | the second corpus (D7) |
| `tests/test_implementation_domain_lock.py` | Modify | kit-lock glob, M5, single-document guard, Lock A strengthening (D6/D9/D10) |
| `.claude/skills/_core/**`, `proposal-implementation/**`, `proposal-deliberation/**`, `tests/seal/**` | **Untouched** | the bar |

## Landing order — A stacks into four

| Slice | Contents | Forecast | Gate at the end |
|---|---|---|---|
| **A1** | Profile + launcher + RED-first leaf-refusal tests + mutation suite | 900–1,300 | 28 digests identical; `Ran` grown; `skipped=6` |
| **A2** | Second seal corpus + fixtures + `tests/seal/` untouched assertion | 350–600 | `git diff --exit-code tests/seal/` exits 0 |
| **A3** | `SKILL.md` + the two agents | 600–900 | all `test_agents.py` checks green, coverage equalities included |
| **A4** | Kit-lock glob, M5 + residue pin, single-document guard, Lock A | 300–500 | `npm test` 595/595 |
| | | **2,150–3,300** | |

`Decision needed before apply: Yes`. `Chained PRs recommended: Yes`.
`400-line budget risk: High` — and High against the session's own
`review_budget_lines: 1400` too: no single slice above may merge unstacked.
A4 depends only on A1 (the north's text must be final before the denylist is
pinned); A2 and A3 both depend on A1; A2 and A3 are independent of each other.
The proposal's 1,500–2,400 for A is **low** — it did not price the second seal
corpus's authored fixtures or the mutation suite, and the closest real anchor
(the second deliberation skill: 1,536 skill + 1,593 test = **3,129** with zero
engine changes) sits inside the range above.

## Mutation plan

Every row: assert the anchor count before (exactly 1) and after (0/1), break it
on disk, watch the named test die, restore, re-assert. **An anchor that matched
is not a mutation that ran**; `sd -s` can exit 0 and change nothing;
`git diff --stat` proves nothing for an untracked new file, so the anchor count
is the instrument. Clear `__pycache__` before every Python mutation (a
same-size edit reuses a stale `.pyc`). Never mutate the real engine — plant into
a scratch copy, the mechanism `test_implementation_domain_mutation.py` already
has.

| # | Break | Anchor | Must go red |
|---|---|---|---|
| X1 | Delete each of the 16 validated leaves, one at a time | leaf literal 1→0 | `…_INCOMPLETE` naming that exact leaf |
| X2 | Change each leaf's value (14 change-mutations) | old literal 1→0, new 0→1 | a named case of the new corpus, **or** recorded as a zero-mover defended by X1 + the locks — measured, never predicted |
| X3 | Flip one byte in the new launcher | byte equality | launcher byte-equality test (D4) |
| X4 | Add `"zzz-nothing"` to the new profile's `names` | names length N→N+1 | strengthened Lock A **only** — run it against the OLD check first and record it surviving (the control that proves the strengthening did something) |
| X5 | Plant one denylist word into a **scratch** engine copy | scratch occurrences 0→1 | M5 test 2, naming file and word |
| X6 | Delete one pinned residue occurrence from the scratch copy | count N→N−1 | M5 test 3 |
| X7 | Copy the sibling's `purpose` over the new north's | unique-word set → ∅ | M5 test 1 (vacuity) |
| X8 | Add a second `documents` entry to the new profile | `"label":` 1→2 | D10's single-document lock |
| X9 | Point the kit-lock glob at zero kit-shipping profiles | derived set →∅ | the kit lock's non-empty assertion |
| X10 | Delete `## Measure before you assert` from `experiments-walk.md` | heading 9→8 across agents | the shared-discipline test |
| X11 | Set `experiments-build`'s `stretch:` to a stage the new north does not declare | literal 1→0 | the arrival seal's stage-membership branch |

Each mechanism gets its own test method or a `subTest` — a method halts at its
first failing assertion, which `b3ca9aa` fixed in `tests/test_implementation_pair.py`.

## What breaks — producers and products

| Class | Item | Verdict |
|---|---|---|
| Producer | `KitAgreementLockTests._profile()` | Replaced by a derivation; the sibling's six assertions keep their values |
| Producer | `LockADiscoveryTests.test_every_declared_name_really_is_that_domain_speaking` | Rewritten (D6); sibling passes unedited — **verify, do not assume** |
| Producer | `LockBEngineNeutralityTests` | Unedited; its `names` union grows, so the engine is scanned for new words — the reason D6 admits words one at a time |
| Producer | `test_agents.py` | Unedited; its coverage equalities grow from 7 agents to 9 by derivation |
| Producer | `tests/forge_vocabulary.py::shipped_documents()` | Unedited; the new skill is scanned the day its directory appears, by `TargetVocabularyLeakTests` **inside the sibling's suite**. The new doctrine may not spell `ceiling`, `ramp`, `transfer`, `latent`, `kaggle`, `t4`, `creda`, `milcreda` — `transfer` is the live trap in an experiments doctrine |
| **Product** | `tests/seal/digests.json` (28 goldens) | Untouched, and asserted so |
| **Product** | `tests/pair/digests.json` | Untouched — D10's guard is deliberately outside the resolver so this corpus keeps resolving |
| **Product** | `.implementation/position.jsonl` in any target, minted authorizations | Out of domain: no target exists for this skill yet, and nothing in A touches `_AUTHORIZATION_BINDING_KEYS` or `proposalDigest` |
| **Product** | Any managed revision under `proposals/`/`experiments/` | None exist beyond `.gitkeep`; stated rather than left implicit |
| **Product** | `L1_EXPECTED_COUNT = 96` / `L1_EXPECTED_FILES` | Unmoved, because A edits no engine byte — **assert it, do not infer it** |

## Threat matrix

The new seal corpus launches real subprocesses against scratch git repositories.

| Boundary | Applicability | Design response | Planned RED test |
|---|---|---|---|
| Documentation-like paths | N/A — A classifies no file as executable; the kit is not shipped | — | — |
| Git repository selection | **Applicable** — cases run `cwd=impl.FORGE_ROOT` against fixtures copied into a fresh scratch dir | Reuse `validate_case`'s rule that `--target` is the `<TARGET>` placeholder, never a literal path | A case with a literal `--target` raises `RosterValidationError` before any subprocess runs |
| Commit state | **Applicable** — any roster case whose command commits writes inside the scratch copy only | `run_case`'s `copytree` into `tempfile.mkdtemp(dir=scratch_root)`, unchanged | Assert the committed corpus fixtures are byte-identical after a full corpus run |
| Push state | N/A — no case has a remote | — | — |
| PR commands | N/A | — | — |
| Subprocess env | **Applicable** — the child env is an explicit dict | Reuse `build_env` + `ALLOWED_ENV_KEYS` unchanged; add no key; rely on the new launcher's `setdefault` for the profile | A case run with a stray `IMPLEMENTATION_*` in the parent env produces an identical digest |

## Migration / rollout

No migration. A is purely additive on the shipped side; rollback is deleting
`.claude/skills/experimental-implementation/`, the two agent files and the new
test directories, plus reverting one test file. The 28-digest seal is the
existing proof the revert was complete.

## Predictions this design makes — claims apply must measure, not repeat

1. The sibling's seven `names` all appear in non-`names` profile **values**, so
   D6's strengthening leaves it green unedited.
2. `experimental-implementation` occurs **0** times in
   `implementation_engine.py`, so Lock B tolerates the namespace word.
3. A byte-identical launcher copy resolves to the new skill's own profile.
4. Wrapping `impl.CLI_INVOCATION` in-process changes the argv of a real
   subprocess (it is not the monkeypatch scar).
5. The M5 denylist is large and its residue pin is not small; the sizes in the
   landing table assume that.
6. `_impact_class`'s three-group read is a live constraint, not a style rule.

Each is a **claim**, not a fact. Where measurement disagrees, record the
measurement and change the design, exactly as Cut 2 recorded seven zero-movers
it had predicted would move.

## Open questions

- [ ] **Q1 (proposal's own, still open):** the cross-document citation key.
      A does not need it — one document, no crossing. D does.
- [ ] **Q2:** does `plan`/`verify`/`probe` run at all in a kitless skill? The
      roster in D7 is derived by measurement at apply; if the kit-free surface
      turns out to be near-empty, M3's ruling needs revisiting and a fifth
      change ("the kit crosses the seam" — tokenise those 18 lines) becomes A's
      real neighbour.
- [ ] **Q3:** should `impl_domain_profile._resolve()` validate
      `citation_pattern`'s group count (M2)? A asserts it in the new skill's
      own suite instead; the resolver fix belongs with C, which reshapes that
      leaf per document.

## Citations checked

Every symbol named above was resolved in the source **this session, by name,
never by line and never inherited**: `SKILL_ROOT`, `CLI_PATH`,
`CLI_INVOCATION`, `CLAIM_KEY`, `LOCUS_KEY`, `REMEDY_LOCUS_KEY`,
`NOTATION_KEYS`, `CITATION_PATTERN`, `CITATION_RE`, `TAG_RE`,
`DISPLAY_BLOCK_RE`, `DOCUMENTS`, `DOCUMENTS_DIRECTORY`, `DOCUMENTS_LABEL`,
`PRODUCT_DIRS`, `_impact_class`, `finding_impact`, `remedy_compatibility`,
`cmd_compose`, `cmd_admit`, `cmd_verify`, `_extra_document_fidelity_status`,
`_document_extra_sources`, `proposals_root`, `revision_source`,
`discover_document_revision`, `document_revision_names`, `_resolve`,
`_REQUIRED_NESTED`, `_REQUIRED_PRESENCE`, `_OBJECTIVE_REQUIRED`,
`_STAGE_REQUIRED`, `ImplementationProfileError`, `discover_profiles`,
`KitAgreementLockTests._profile`, `LockADiscoveryTests`,
`LockBEngineNeutralityTests`, `L1_EXPECTED_COUNT`, `L1_EXPECTED_FILES`,
`CAMPAIGN_PROPOSAL_SYMBOLS`, `_python_objective`, `_python_flow`,
`declared_objective`, `declared_entrances`, `stage_conditions`, `bound_skill`,
`NORTHLESS_SKILLS`, `ENTRANCE_CLAIMS`, `UNMEASURABLE`,
`seal_harness.run_case`, `build_env`, `ALLOWED_ENV_KEYS`, `validate_case`,
`RosterValidationError`, `_build_env_with_profile_override`, `buildDenylist`,
`objectiveWords`, `selfNamespaceNames`, `PINNED_RESIDUE`,
`shipped_documents`, `FORGE_VOCABULARY_FLOOR`, `FORGE_ROOT`
(`impl_layout.py`). Two inherited counts were re-measured and **corrected**:
the engine's subject-word occurrences are 89/30/28, not the brief's 88/23/20;
and the `names` check's vacuity is total, not limited to a namespace word (M1).

---

## D1 revisited: the ruling that flipped, and the orchestrator error behind it

D1 above ruled `documents[0]` = the **experiments** document. Mid-flight the
operator ruled the opposite — the mathematical proposal — and that ruling was
relayed into the tasks brief and the apply brief **without anyone noticing it
contradicted this design.** That was the orchestrator's error, and it is recorded
here rather than quietly reconciled.

**The apply agent followed this design, not the contradicting brief.** That was
the correct call: the design is the authoritative artifact, and a brief that
contradicts it is a defect in the brief.

**Why the operator's ruling was sound and still yielded the wrong answer.** Their
argument was the dependency direction: the experiments document exists to test
claims from the proposal, so verifying downstream while upstream is broken
measures against a false reference. That reasoning is correct and it now governs
C's ordering.

It reached the wrong conclusion here because the orchestrator framed the choice
as *"which of the two verifications do you want, if you can only have one"*.
**That question was wrong.** The operator was not choosing which to have — the
mathematical verification already exists and keeps running in
`proposal-implementation`. They were choosing what the NEW skill adds.

And the framing omitted this design's own decisive argument: with `proposals/`,
the profile becomes the sibling's vocabulary byte for byte and **no leaf is
mutation-provable as this domain's**. That is the same shape as a profile field
nothing reads — the rule seven cycles have been enforcing — applied sixteen times
at once.

Re-put with both facts, the operator confirmed the experiments document.

**What the operator's concern buys anyway**: nothing is lost. The mathematical
proposal keeps being verified by the sibling skill from the day A lands until C
merges both documents into one invocation. The two run side by side.
