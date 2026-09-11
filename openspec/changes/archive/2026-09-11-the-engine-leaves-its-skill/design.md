# Design: The Engine Leaves Its Skill

> **Size note.** Over the usual 800-word budget, deliberately and for the same reason
> `the-seal-before-the-cut/design.md` was: the brief requires seven mechanisms *exact, not
> described*, each with its own failure mode and its own named mutation. A shortened design
> here is a design apply has to invent, and invention is what this cut cannot afford.

## Technical Approach

Move the engine out of the skill, leave a launcher at the unchanged published path, and let
the engine source its host from a profile. The cut's whole value is that the seal can prove
it: **every captured digest byte-identical, zero sanctioned delta.** Any movement is a
defect, never a new golden.

Two measurements taken during this phase change the proposal's shape and are the spine of
what follows.

### M1 — the engine cannot land flat in `_core/implementation/`

`tests/test_implementation_core.py::CoreNamesNoDomainTests::test_no_core_file_names_a_product_directory_or_source_root`
globs `CORE.glob("*.py")` and fails any core file whose text contains a member of
`PRODUCT_DIRS` or `SOURCE_ROOTS`. The engine *defines* `PRODUCT_DIRS = ("Notebooks",
"Data", "Results", "Models")`. Landing it flat turns that guard red, and the only repairs
are to exempt the engine by name — gutting the guard over 17,100 of ~18,000 core lines — or
to weaken it. Both are unacceptable.

The precedent the proposal claims to mirror already answers it: the deliberation engine
lives at `_core/deliberation/engine/`, a **subdirectory**. `glob("*.py")` does not recurse.

**Engine path: `.claude/skills/_core/implementation/engine/implementation_engine.py`.**
The shared modules keep their guard at full strength; the engine is outside it by location,
which is honest — it is not a shared module yet, it is a domain-carrying engine in transit,
and `engine/` is exactly where Cut 2's neutrality lock will attach.

### M2 — "the CLI path" is three different facts, and the move splits them

One constant serves all three today because they are one file. After the move a blanket
re-point in *either* direction is a defect.

| Meaning | Resolves to | Readers measured |
|---|---|---|
| **Published entry point** — what a reader runs, what `CLI_INVOCATION` names, what the seal invokes | the **launcher** | `PublishedCommandsRunVerbatimTests::test_the_prefix_names_a_real_interpreter_and_this_exact_script`, `…::test_the_script_is_not_executable…`, `…::test_a_published_resolution_runs_unrepaired…`, `tests/seal/harness.py` argv |
| **Engine source** — what source-reading guards parse | the **engine** | `reachable_refusal_codes()`'s source list, `test_no_publication_point_still_builds_a_bare_script_name`, `CoreNamesNoDomainTests._cli_module()`, every in-process `import … as impl` |
| **Skill root** — assets beside the launcher | the **skill** (unchanged) | `sys.path.insert(0, str(CLI.parent.parent / "assets/kit/nb"))` — needs **no edit**, because the launcher stays put |

Apply MUST classify every `CLI` / `CLI_SCRIPT` / `_CLI_SCRIPTS` reader into one of these
three before editing it. Deriving the per-site list at apply time is mandatory: `tests/` is
being written concurrently and any line list written here is stale on arrival.

## Architecture Decisions

### D1 — The launcher is a launcher, not an alias

**Choice.** The launcher sets the profile variable, puts the engine on `sys.path`, and
hands over. It does **not** make itself indistinguishable from the engine.

```python
#!/usr/bin/env python3
# This skill's entry point into the shared implementation engine.
#
# The engine under `_core/` serves no domain of its own and refuses to start
# without one, so the only thing this file does is name which domain is asking
# before handing over. Every argument, subcommand and exit code is the engine's.
#
# `setdefault` rather than `=`: an explicit IMPLEMENTATION_DOMAIN_PROFILE in the
# environment is a deliberate override (a test fixture, a sibling domain being
# exercised through this launcher) and must win over the default -- the same
# `??=` semantics `proposal-deliberation/cli.mjs` uses, including for the empty
# string, which stays empty and is refused.
import os
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
os.environ.setdefault("IMPLEMENTATION_DOMAIN_PROFILE",
                      str(_HERE.parents[1] / "impl_profile.py"))
sys.path.insert(0, str(_HERE.parents[2] / "_core" / "implementation" / "engine"))
import implementation_engine as _engine  # noqa: E402  (path set above)

if __name__ == "__main__":
    raise SystemExit(_engine.main())
```

`SKILL_ROOT` and `CLI_PATH` resolve off **this file**, not off the engine: `_HERE.parents[1]`
is the skill, and `impl_profile.py` computes both from its own location (D3).

**Alternatives rejected.**

| Option | Why rejected |
|---|---|
| `sys.modules[__name__] = _engine` (aliasing) | Seductive — "no test changes needed" — and that is the danger. A launcher indistinguishable from the engine is a launcher **no in-process instrument can tell apart from the engine**, in a change that exists because exactly that confusion is silent. It also is not even transparent: `CoreNamesNoDomainTests._cli_module()` uses `exec_module` and returns its own module object, so aliasing leaves it holding the launcher and raising `AttributeError` on `PRODUCT_DIRS`. It saves none of the edits it appears to save, and it removes the possibility of a test that goes red when an import points at the wrong file |
| `from implementation_engine import *` | Skips underscore names; `impl._cli_command` and `impl._discuss_command` are asserted today |
| `globals().update(vars(engine))` | Read-transparent, mutation-opaque: a test that sets `impl.X` would patch a copy while engine internals still read the engine's own global. 995 `impl.` references in one file is not a surface to gamble on |

**Consequence, accepted deliberately.** `import implementation_cli as impl` no longer
yields engine attributes, so every in-process import route is re-pointed to the engine
(meaning 2). This preserves monkeypatch semantics *exactly* — `impl` is the engine module,
as it effectively is today — and it buys a pin aliasing cannot have:
`test_the_launcher_exposes_no_engine_attribute` asserts the launcher module carries none of
`{COMMANDS, CLI_PATH, SKILL_ROOT, main}`, so nobody reintroduces aliasing silently.

**No delta in argparse output.** `main()` builds `ArgumentParser(prog="implementation_cli",
description=__doc__)` — `prog` is a literal, never `sys.argv[0]`, and `__doc__` is the
engine's own docstring, which moves with the file byte-for-byte. Usage, `--help` and every
parser error are unchanged by construction, independent of which file is the entry point.

### D2 — The three behavioural reaches: three mechanisms, three failure modes, three guards

The proposal names three sites. Each fails a different way, and a single "pass the paths in"
answer would hide that.

| # | Site (located by name at HEAD) | After | Fails | Guard | Named mutation |
|---|---|---|---|---|---|
| R1 | `SKILL_ROOT = Path(__file__).resolve().parents[1]` — **19 reader lines measured** (kit file map, `KIT_SEAL`, `requirements-dev.txt`, two `kitSource` sites) | `SKILL_ROOT = PROFILE["kit"]["root"]` | **Silently.** 19 readers resolve under `engine/`; the two `str(source.relative_to(SKILL_ROOT))` sites would raise `ValueError` instead | (a) resolver refuses an absent/relative/nonexistent `kit.root` at import — turns the absent case loud; (b) value pin: `impl.SKILL_ROOT == FORGE/".claude/skills/proposal-implementation"` as a **literal**, plus `assertNotEqual(impl.SKILL_ROOT, ENGINE.parent)`; (c) seal reachability — see below | Edit `impl_profile.py` so `kit.root` names `…/_core/implementation/engine`; (b) must go red |
| R2 | `CLI_PATH = Path(__file__).resolve()` → `CLI_INVOCATION` (4 reader sites, all message builders) | `CLI_PATH = PROFILE["cli"]["path"]` | **Silently.** Published commands still run and name a file the reader was never given. The test passes and the guarantee is gone | The landed `test_the_sealed_cli_path_names_the_launcher` (sealed bytes) **plus** the re-pointed `PublishedCommandsRunVerbatimTests` (D5) **plus** the new entry-point pin (D6) | D4 |
| R3 | `sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))` | `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))` — the engine's own parent, which **is** the shared core | **Loudly.** `ImportError` at import; nothing runs | Any import of the engine. The whole suite | Restore `parents[2] / "_core" / "implementation"` → `ImportError`, reverted |

**Ordering constraint apply must not discover by colliding with it.** `SKILL_ROOT` is
assigned *above* the `sys.path` insert today, so it cannot read `PROFILE` where it stands.
Delete the line at its current position (nothing between it and the import block reads it —
verified, lines 38–46 are comment) and re-assign it beside `CLI_PATH`, immediately above
`CLI_INVOCATION`, so that constant's position and composition are untouched.

**The engine diff is five lines**: one deletion, one reshaped `sys.path` line, one added
`from impl_domain_profile import PROFILE  # noqa: E402` in the core import block, two
assignments. 17,095 lines verbatim, before the operator ruling below.

**Amended (2026-09-11, operator ruling on task 7.5's non-interference finding).** Apply's
Phase 7 non-interference run surfaced a regression `tests/test_agents.py`'s cross-skill north
lock: it discovers a skill's declared north (`OBJECTIVE_FLOW`) by walking THAT SKILL'S OWN
directory tree for a literal module-level assignment, and after the move `OBJECTIVE_FLOW`
physically left `proposal-implementation/`'s tree entirely, landing with the engine under
`_core/`. Three closures existed and apply correctly stopped rather than pick one unilaterally
(extending an out-of-scope test file's discovery mechanism; declaring the skill northless,
which is false; re-exposing an engine attribute through the launcher, which breaks D1's own
tested guarantee). The operator ruled a fourth: `objective` becomes the Cut-1 field set's third
member, moved into the profile exactly as `kit.root`/`cli.path` were. **Measured, against the
operator's own 17,039 estimate**: a line-level diff of the final engine against the original
17,106-line file counts 61 original lines touched (not 67), leaving **17,045 lines verbatim**,
not 17,039 — the discrepancy is the comment text apply wrote being a few lines longer than a
minimal edit would be, not a different set of lines moved. Recorded as measured rather than the
estimate repeated. Not 17,095 either way — this is a better description of what Cut 1 should
have been from the start, not a scope creep: the precedent already exists on the deliberation
side (`2026-09-09-a-north-a-second-domain-can-hold`), where
`_core/deliberation/engine/domain-profile.ts` hardcodes no domain's `objective` and each skill's
own `profile.ts` declares its own. See D3's amended field-set table.

**R1's seal instrument is a claim to measure, not to assert.** A surviving mutation has two
explanations — a weak test or a wrong claim about the property — so apply **measures first**:
run R1's mutation, record *which* case digests move, and only then write the assertion
around the measured set. `materialize` (case 28) and the `kitSource` carriers are the
expected movers. **If zero cases move, say so**: R1 then has no seal instrument, guards (a)
and (b) are its whole defence, and that is written down rather than papered over.

### D3 — `IMPLEMENTATION_DOMAIN_PROFILE`, the resolver, and the Cut-1 field set

`_core/implementation/impl_domain_profile.py` mirrors `domain-profile.ts`'s **resolver
properties**: no default, fails closed at import, absolute path required, nested required-key
validation, path values validated, named refusal codes.

```python
# .claude/skills/proposal-implementation/impl_profile.py
from pathlib import Path
_SKILL = Path(__file__).resolve().parent
OBJECTIVE_FLOW = { ... }  # moved verbatim from the engine, 56 lines
PROFILE = {
    "kit": {"root": _SKILL},
    "cli": {"path": _SKILL / "scripts" / "implementation_cli.py"},
    "objective": OBJECTIVE_FLOW,
}
```

The reach that broke when the engine moved is gone; what remains is a reach **inside one
skill directory that moves as a unit**.

**The Cut-1 field set (amended 2026-09-11, operator ruling on task 7.5), and why each field
earns its place by being read.**

| Field | Read by | Earns it |
|---|---|---|
| `kit.root` | the engine's `SKILL_ROOT`, 19 reader lines | **Non-optional.** `SKILL_ROOT` breaks the instant the engine moves, and breaks silently. The engine gets no fallback |
| `cli.path` | `CLI_PATH` → `CLI_INVOCATION` → 4 message builders | Cut 1's single silent failure mode. Also makes the mutation surface **one line in a 25-line file** instead of an edit inside 17,100 lines |
| `objective` | the engine's `OBJECTIVE_FLOW`, stamped into every refusal (`impl_domain_profile.py`'s own docstring cites the exact site) | Read **twice from outside the engine**: by the engine's own refusal payload, and by `tests/test_agents.py`'s cross-skill north lock, which walks THIS SKILL'S OWN directory tree — never the engine's — for a literal `OBJECTIVE_FLOW` assignment. That is also why it must physically live here: a second skill on this same engine needs its OWN north without editing the shared file, exactly the reason `kit.root`/`cli.path` are profile-derived |

**Nothing else.** A profile field nothing reads cannot be mutation-proven, and an unprovable
field is the shape of a false guard.

| Rejected field | Why not at Cut 1 |
|---|---|
| `names` (the TS `names` list) | Its TS justification is that a **lock reads it**. Operator ruling 3 puts the Python lock at Cut 2, "because with no domain words yet moved it would pass vacuously". Worse than vacuous: at Cut 1 the engine still carries the 167 domain lines, so an honest `names` makes the lock **red today**, and a green one requires declaring a dishonest list. Deferred to Cut 2, with the reason recorded here rather than left as a silent omission |
| `cli_invocation` (B1's spelling) | The profile supplies the **path**; the engine composes `sys.executable` + `shlex.quote` itself, exactly as `artifact-naming.ts` composes from `artifact.directory`. A field named `cli_invocation` would promise a composed value the profile does not supply |
| `documents`, `provenance`, `document_reader`, `findings`, `vocabulary` | Out of scope; no Cut-1 reader |
| ~~`objective`~~ | **No longer rejected** — see the field-set table above. Originally excluded by the exact rule ("a profile field nothing here reads cannot be mutation-proven") that flipped once `test_agents.py`'s cross-skill discovery started reading it too |

**Refusal codes** — six, each mutation-proven:

| Code | Condition |
|---|---|
| `IMPLEMENTATION_DOMAIN_PROFILE_REQUIRED` | unset or empty |
| `…_NOT_ABSOLUTE` | relative — a child process's cwd is not the engine's to assume (the TS file's own measured reason) |
| `…_UNREADABLE` | file absent, `spec_from_file_location` returns `None`, or exec raises |
| `…_INVALID` | module exports no `PROFILE`, or it is not a mapping |
| `…_INCOMPLETE` | missing key, **named nested**: `kit.root`, not `kit` (and, amended, `objective.stages` not `objective`, `objective.stages: []` not silently accepted). The `artifact: {}` lesson — a top-level check passes vacuously |
| `…_UNSAFE_PATH` | `kit.root` / `cli.path` not absolute, or not present on disk |

`…_UNSAFE_PATH` is where this design diverges from the TS on purpose. `SAFE_ARTIFACT_SEGMENT`
guards *segments joined under a root*; these are whole absolute paths the host names, so the
escape it prevents is not reachable. What **is** reachable is a `kit.root` that does not
exist — today that scatters into 19 unrelated missing-asset failures, and validating it at
import turns them into one named refusal. A "must live under `FORGE_ROOT`" rule was
considered and **rejected**: it would refuse a tmpdir fixture profile, which is the exact
override case `setdefault` exists to serve.

**The resolver raises `ImplementationProfileError(RuntimeError)` at import — never `Refused`.**
Three independent reasons: (1) the TS precedent throws a plain `Error`, not the engine's
domain refusal type; (2) the engine's JSON renderer lives inside a module that has not
finished importing, and a second duplicated renderer is new surface for a state the launcher
never produces; (3) **collateral** — `reachable_refusal_codes()` walks
`CORE_IMPLEMENTATION.glob("*.py")` for `Refused`/`NameRefused` constructions, and
`assertEqual(len(reachable_refusal_codes()), 112)` is pinned. Six `Refused`s in a core module
would move that pin, which is a behavioural-delta-adjacent edit to an unrelated guard. A
distinctly-named exception is invisible to that walk. **Apply asserts the pin still reads 112.**

### D4 — How the seal proves this cut

The seal is landed: 29 cases, real subprocess through `CLI_INVOCATION`, N3 narrowed so
`str(CLI_PATH)` survives into the sealed bytes, `test_the_sealed_cli_path_names_the_launcher`
pinning it, `propose` recorded unsealed (28 sealed).

**Zero bytes of the instrument change.** This is checkable, and it is the strongest
statement of "no sanctioned delta" available:

```
git diff --exit-code tests/seal/cases.json tests/seal/digests.json \
                     tests/seal/corpus.py tests/seal/normalize.py \
                     tests/seal/unsealed.json
```

must exit 0 at the end of the change. `harness.py` changes only its import route (meaning 2),
never its argv source: argv stays `shlex.split(impl.CLI_INVOCATION)`, so what is invoked
remains profile-derived, which is precisely what D6 pins.

**Procedure.**

| Step | Action | Required result |
|---|---|---|
| P0 | Before any edit: run the comparison suite; record `sha256(tests/seal/digests.json)` and the pasted `Ran … OK` | green, 28 sealed |
| P1 | Land the change | — |
| P2 | Re-run the comparison suite | **all 28 digests byte-identical**, every `exit` unchanged, `bytes` unchanged. `digests.json` sha256 identical to P0 |
| P3 | `test_the_sealed_cli_path_names_the_launcher` | green, and its `carriers` list **non-empty** (a vacuous pass over zero carriers is the one way it can lie) |
| P4 | The mutation below | red, both ways |
| P5 | Revert, re-run P2 | byte-identical again |

**P4 — the mutation that proves the instrument still sees.** Point `CLI_PATH` at the engine
and require **both** a moved digest **and** a red pin.

*A real, reverted file edit — never a monkeypatch.* Monkeypatching `impl.CLI_PATH` or
`impl_domain_profile.PROFILE` has **zero effect on a subprocess**, and every seal case is a
subprocess. The edit is one line in `impl_profile.py`:

```python
    "cli": {"path": _SKILL.parents[1] / "_core" / "implementation" / "engine"
                    / "implementation_engine.py"},
```

Assert, by reading the file, that the anchor count moved — `1 → 0` for the launcher
spelling and `0 → 1` for the engine spelling — **before** running anything. An anchor that
matched is not a mutation that ran, and `sd -s` can exit 0 and change nothing. Then:

1. the comparison suite goes **red**, and apply records *which* case ids moved;
2. `test_the_sealed_cli_path_names_the_launcher` goes **red**;
3. `PublishedCommandsRunVerbatimTests::test_the_prefix_names_a_real_interpreter_and_this_exact_script`
   goes **red**;
4. revert; assert the anchor counts back at `1 / 0`; re-run; byte-identical.

Requiring (1) **and** (2) together is the point. A digest that moves with a green pin means
the pin is not watching the path; a red pin with unmoved digests means the seal never
carried the path into its bytes. Either alone is satisfiable by a broken instrument.

### D5 — `PublishedCommandsRunVerbatimTests`, re-pointed by meaning, with its own mutation

This class is meaning 1 **except for one test that is meaning 2**, and the split is where
the defect hides.

| Test | Meaning | After the move |
|---|---|---|
| `test_the_prefix_names_a_real_interpreter_and_this_exact_script` | 1 | `assertEqual(Path(tokens[1]), LAUNCHER)`, **plus** a new `assertNotEqual(Path(tokens[1]), ENGINE)`. The equality alone would still pass against a `CLI` constant someone re-pointed; the inequality names the thing that must not happen |
| `test_the_script_is_not_executable_so_the_interpreter_is_load_bearing` | 1 | unchanged constant; the launcher must ship mode 644. `git mv` preserves the engine's mode; the **new** launcher's mode is asserted, not assumed |
| `test_a_published_resolution_runs_unrepaired_from_another_directory` | 1 | unchanged — it runs `payload["resolve"]["command"]` verbatim, which is `CLI_INVOCATION`-derived and therefore profile-derived |
| `test_no_publication_point_still_builds_a_bare_script_name` | **2** | **must read the ENGINE's source.** Left on `CLI` it reads a 25-line launcher, which trivially contains no `"implementation_cli.py` literal — green, and proving nothing about the 17,100 lines where publication points are actually built |
| `test_every_builder_routes_through_the_one_prefix` | 2 | `impl` is the engine module; correct once the import route is re-pointed |

**The mutation that proves the re-point re-pointed.** A re-point without one is the same
defect one level up.

- *For meaning 1:* the D4 mutation. Pointing `cli.path` at the engine must redden
  `test_the_prefix_names_…`. If it stays green, the test is asserting against a constant
  that moved with it rather than against the published value.
- *For meaning 2:* point `test_no_publication_point_still_builds_a_bare_script_name` back at
  the launcher and show it passes **while the engine carries a planted
  `"implementation_cli.py` literal**. A test that passes over a planted leak is the
  vacuity being ruled out. Revert both.

### D6 — `Seal Capture Scope` starts naming the entry point

Today the requirement pins the twenty subcommands but **not which file is invoked**, so
after the move the seal would silently keep sealing whatever `CLI_INVOCATION` resolves to.

**Amendment** (for `sdd-spec` to write into the `implementation-cli-seal` capability; this
design writes no spec): the `Seal Capture Scope` requirement gains a clause requiring the
sealed invocation target to be the **per-skill published launcher at
`.claude/skills/proposal-implementation/scripts/implementation_cli.py`**, named as a literal,
and requiring a scenario in which an invocation target resolving to the shared engine is
refused.

**How it is proven** — `test_the_seal_invokes_the_published_launcher`, in
`tests/test_implementation_seal.py`: `shlex.split(impl.CLI_INVOCATION)[1] == str(LAUNCHER)`
and `!= str(ENGINE)`, with `LAUNCHER` a pinned literal.

This is **not** a duplicate of `test_the_sealed_cli_path_names_the_launcher`. That one pins
the *bytes the seal digested*; this one pins *the file the harness ran*. They cannot diverge
today because `harness.py` derives argv from the same `CLI_INVOCATION` — and that is exactly
why the requirement must pin it, because the divergence becomes available the moment
`harness.py` is edited, which this change edits.

### D7 — Ordering and rollback

| Step | Work | Suite state | Rollback boundary |
|---|---|---|---|
| S0 | Baseline: comparison suite, `PublishedCommandsRunVerbatimTests`, full Python discover, `npm test`. Paste all. Record `sha256(digests.json)`, `wc -l` of the CLI, the three `Path(__file__).resolve()` anchor counts | green | — |
| S1 | **RED first**: `tests/test_implementation_profile.py` — six refusal codes, `setdefault` override, launcher-exposes-nothing. Fails: modules absent | red by design | — |
| S2 | Create `impl_domain_profile.py` + `impl_profile.py`. Additive; nothing imports them yet | green + S1 green | **B1**: delete two files |
| S3 | **Atomic work unit**: `git mv` engine → `engine/implementation_engine.py`, reshape the five lines, write the launcher. The tree is red *between* the `mv` and the launcher; this is one unit, never a commit boundary | green | **B2**: `git mv` back, delete launcher |
| S4 | Re-point every `CLI`/`CLI_SCRIPT`/import route by meaning (M2). Includes `reachable_refusal_codes()`'s source list → the engine; assert the pin still reads **112** | green | **B3**: revert test edits |
| S5 | Seal entry-point pin (D6); re-pointed published-commands assertions (D5) | green | B3 |
| S6 | Proof: P0–P5, R1/R2/R3 mutations, anchor counts pasted both directions | green | — |

`git mv` and the five-line reshape land in **one commit**. This section originally predicted `git diff -M` would report ~99.97% rename similarity. **Measured on the landed commit, it does not: no rename pairing exists at any threshold**, because the launcher was rewritten at the same published path inside the same commit, which defeats git's rename detection regardless of `-M`. The move is still verbatim -- independently re-derived at **17,045 lines**, exactly 61 original lines touched -- but the evidence for that is the hunk diff and the seal's 28 byte-identical digests, never git's rename heuristic. A prediction about git mechanics
similarity. Apply pastes `git diff -M --numstat`. **`git diff --stat` is not evidence for
the launcher, the profile or the resolver** — they are new files, and a stat proves nothing
about paths git is not yet tracking; their content is asserted by reading them.

`FORGE_ROOT` is unaffected: `parents[4]` of `impl_layout.py`, which does not move.
`test_the_core_resolves_the_repository_root_it_actually_lives_in` stays green, confirmed by
reading it.

**Review budget.** ~440 authored lines (resolver ~90, tests ~300, launcher ~22, profile ~25,
engine 5) plus one rename. Inside the 1400-line budget; single PR.

## Data Flow

```
IMPLEMENTATION_DOMAIN_PROFILE ──(setdefault, launcher)──→ impl_profile.py
                                                               │
      argv, exit codes                    impl_domain_profile.py (validate, fail closed)
  reader ──→ launcher ─────────────────────────→ engine       │
             (unchanged path)                      │  PROFILE["kit"]["root"]  → SKILL_ROOT (19 readers)
                                                   └─ PROFILE["cli"]["path"] → CLI_PATH → CLI_INVOCATION
                                                                                             │
  tests/seal/harness.py ──shlex.split(impl.CLI_INVOCATION)──→ subprocess ──stdout+exit──→ normalize ──→ digest
                                                                                             │
                                                                        must equal tests/seal/digests.json, byte for byte
```

## File Changes

| File | Action | Description |
|---|---|---|
| `.claude/skills/_core/implementation/engine/implementation_engine.py` | Create (`git mv`) | the moved engine; 17,045 verbatim, measured (amended 2026-09-11: `OBJECTIVE_FLOW`'s 56-line literal also crossed the seam, replaced by `OBJECTIVE_FLOW = PROFILE["objective"]`) |
| `.claude/skills/proposal-implementation/scripts/implementation_cli.py` | Replace | the ~22-line launcher, unchanged path, mode 644 |
| `.claude/skills/_core/implementation/impl_domain_profile.py` | Create | fail-closed resolver, six named refusals; amended to validate `objective`'s own required leaves and non-empty `stages` |
| `.claude/skills/proposal-implementation/impl_profile.py` | Create | `kit.root`, `cli.path`, amended: `objective` (the 56-line `OBJECTIVE_FLOW`, moved verbatim) |
| `.claude/skills/proposal-implementation/scripts/materialize.py` | Modify (finding, task 4.1) | its own `from implementation_cli import ...` re-pointed to the engine, mirroring the launcher's profile mechanism — not enumerated in the original File Changes table |
| `tests/test_implementation_profile.py` | Create | resolver refusals, override semantics, launcher pins; amended with `ObjectiveProfileFieldTests` |
| `tests/test_proposal_implementation.py` | Modify | M2 re-points; `reachable_refusal_codes()` source list; D5; `SkillRootValueTests` (R1 guard) |
| `tests/test_implementation_core.py` | Modify | `CLI_SCRIPT` → engine (meaning 2); `_cli_module()` |
| `tests/test_implementation_seal.py` | Modify | import route; D6 entry-point pin (`SealEntryPointTests`) |
| `tests/seal/harness.py` | Modify | import route only; argv source untouched |
| `tests/seal/{cases,digests,unsealed}.json`, `corpus.py`, `normalize.py` | **Unchanged** | `git diff --exit-code` must exit 0 |
| `tests/test_agents.py` | **Unchanged** | zero edits — proof that relocating `objective` into the profile restores its cross-skill discovery without touching the discovery mechanism itself |

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | six refusal codes | in-process fresh `importlib` load with a controlled `os.environ`; one mutation per code |
| Unit | `setdefault` override | **subprocess** with `IMPLEMENTATION_DOMAIN_PROFILE` pointed at a tmpdir fixture; output must reflect the fixture's `kit.root` |
| Unit | `SKILL_ROOT` value (R1) | pinned literal, plus `assertNotEqual(…, ENGINE.parent)` |
| Unit | launcher exposes no engine attribute | guards against silent re-aliasing |
| Unit | refusal pin | `len(reachable_refusal_codes()) == 112` unchanged |
| Integration | the seal | 28 digests byte-identical, exits and byte counts unchanged, `digests.json` sha256 unchanged |
| Integration | entry point (D6) | invoked file is the launcher, is not the engine |
| Mutation | **R2 / D4** | real reverted edit to `impl_profile.py`; **moved digest AND red pin**, both required |
| Mutation | R1 | `kit.root` → engine dir; measure which cases move *before* asserting |
| Mutation | R3 | restore `parents[2]`; `ImportError` |
| Mutation | D5 meaning-2 | planted literal in the engine; launcher-pointed guard passes → vacuity proven |
| Non-interference | sister skill | `npm test` = 595/0 and the Python `Ran …, OK (skipped=6)` pasted before and after. `proposal-deliberation` is not written to |

## Threat Matrix

| Row | Applicable | Behaviour / RED test |
|---|---|---|
| Process integration / entry point | **Yes** | The launcher is the only published entry point; D6 pins it, D4 reddens it |
| Environment-variable routing | **Yes** | `setdefault` semantics; empty string is refused, not defaulted; RED per refusal code |
| Subprocess invocation | **Yes (inherited)** | `shell=False`, list argv, unchanged from the landed harness |
| Executable-file classification | **Yes** | launcher and engine both ship mode 644; asserted, and `git mv` mode preservation checked |
| Filesystem writes | **Yes (bounded)** | a wrong `kit.root` is refused at import rather than reaching the 19 readers |
| Path traversal via profile | **Yes** | absolute + must-exist; the under-`FORGE_ROOT` rule considered and rejected with a reason (D3) |
| VCS / PR automation | N/A | no VCS surface beyond `git mv` |
| Network | N/A | none reached |

## What Breaks

**Producers** (measured, not assumed):

- `implementation_cli.py`'s module identity at the old path: no longer the engine (D1,
  deliberate). Every in-process import route re-pointed by meaning.
- `CoreNamesNoDomainTests` — would go red on a flat move; resolved by the `engine/`
  subdirectory (M1), and `_cli_module()` re-pointed to the engine.
- `reachable_refusal_codes()` — its source list is `(CLI, *CORE_IMPLEMENTATION.glob("*.py"))`;
  after the move `CLI` is the launcher and the engine is one directory down, so **without a
  re-point the roster silently loses every engine refusal**. Self-announcing: the pinned
  `112` goes red. Loud, and asserted anyway.
- `test_no_publication_point_still_builds_a_bare_script_name` — becomes **vacuous** if left
  on `CLI`. D5.
- `.claude/skills/proposal-implementation/SKILL.md`, `references/usage.md`, `README.md`,
  `remote-execution/scripts/remote_cli.py`: all name the **launcher path**, which is
  unchanged. Apply verifies none of them names the engine's old location as a *source*.
- `tests/forge_vocabulary.py::shipped_documents()` walks all of `.claude/skills/` uniformly
  with no path-keyed exemption and no stricter `_core/` rule — read, not assumed. The engine
  stays scanned; the floor words (`kaggle`, `t4`, `ceiling`, `ramp`, `transfer`, `latent`,
  and two proper nouns) are unaffected by a move.

**Products** — records already written under the old shape:

- Targets' committed `.implementation/position.jsonl` minted authorizations: **untouched.**
  No binding key is a path; the move writes nothing into any target.
- Targets' committed `AGREED.md`: **untouched.** All four `CLI_INVOCATION` readers are
  message builders (`_cli_command`, and the `gate` / `step` / `discuss` guidance strings) —
  measured, none is a file writer. And the launcher path is unchanged, so any previously
  pasted or stored command string still runs.
- `tests/seal/digests.json` — the only product this change is judged against: **must stay
  valid.** That is the success criterion, not a side effect.
- Archived reports carrying `source_digest`/`suite_digest`, existing `admissibility.json`
  rulings: **untouched** — no digest input changes.

## Migration / Rollout

No migration. Rollout is D7's S0–S6; the red-first S1 before S2 is the discipline, and S3 is
indivisible.

## Open Questions

- [x] `kit.root` on the profile vs passed by the launcher → **profile** (D3), mirroring
      `artifact.directory`.
- [x] Minimal vs full Cut-1 field set → **minimal**, two fields, each with a named reader (D3).
- [x] Python mirror of the TS domain-profile lock → **Cut 2**; at Cut 1 it is red-or-dishonest,
      which is worse than vacuous (D3).
- [x] The `sys.path` site → **the engine's own parent**, which is the shared core (D2/R3).
- [x] **Not anticipated by the proposal**: the engine cannot land flat in
      `_core/implementation/` — `CoreNamesNoDomainTests` globs that directory and the engine
      declares `PRODUCT_DIRS`. Resolved by mirroring the deliberation precedent's
      `engine/` subdirectory (M1).
- [x] **Not anticipated by the proposal**: "the CLI path" is three facts after the move, not
      one. A blanket re-point in either direction is a defect (M2).
- [x] R1's seal instrument: which case digests a wrong `kit.root` actually moves is
      **measured at apply**, not predicted here. If the answer is none, that is recorded.
      **Measured** (task 6.1, apply, 2026-09-11): exactly ONE of the 28 sealed cases moved —
      `materialize` (exit 1, empty stdout, under a real file mutation re-deriving
      `SKILL_ROOT` from the engine's own `__file__`). The `kitSource` carriers this section
      predicted as additional expected movers (`verify-a`, `verify-b`, and similar) did
      **not** move: those fixtures' target files already do not byte-match the kit's own
      templates, so `kitSource` already reports `null` under the CORRECT root too, making
      them structurally blind to a wrong root for this corpus. Guards (a) the resolver's
      `UNSAFE_PATH`/absent/relative refusals, (b) the `SKILL_ROOT` value pin, and (c) a
      permanent in-process guard reproducing the silent kit-source-lookup failure (never a
      permanent real-file-mutating test — the real-file demonstration is one-time, mirroring
      the F5 zero-delta precedent) are what defends R1's silent failure mode; the seal itself
      defends only the one case measured above.

## Citations Checked

Every symbol was re-located by name in the source during this phase, never inherited by line —
`tests/` is under concurrent edit. `SKILL_ROOT` (definition + **19 reader lines**, not the 17
the brief carried — counted, and the discrepancy is reported rather than repeated),
`CLI_PATH`, `CLI_INVOCATION` (definition + 4 readers), the `sys.path.insert` line,
`PRODUCT_DIRS`, `COMMANDS` (20), `main`'s `prog="implementation_cli"` literal and its
`if __name__ == "__main__"` tail, `PublishedCommandsRunVerbatimTests` and its five methods,
`CoreNamesNoDomainTests.test_no_core_file_names_a_product_directory_or_source_root`,
`CORE_IMPLEMENTATION`, `reachable_refusal_codes` and its pinned `112`,
`LaunchAvailableNoUpwardImportsTests` (scoped to one file, **not** the directory — checked,
because a directory scope would have blocked the move),
`test_the_core_resolves_the_repository_root_it_actually_lives_in`,
`test_the_sealed_cli_path_names_the_launcher`, `tests/seal/harness.py`'s `impl.CLI_INVOCATION`
argv source and its `ALLOWED_ENV_KEYS`, `tests/seal/normalize.py`'s `NORMALIZERS` order,
`impl_layout.FORGE_ROOT`, `forge_vocabulary.shipped_documents`, and
`proposal-deliberation/cli.mjs` (13 lines) against `domain-profile.ts` (267 lines).
