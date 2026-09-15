# Design: The Seal Before The Cut

> **Size note.** This design exceeds the usual 800-word budget deliberately. The
> operator's brief requires the five F3 messages *exact, not described*, and one named
> mutation *per normalizer*. A shortened design here is a design apply has to invent.

## Technical Approach

`main()` writes every result — success and refusal alike — as
`json.dump(payload, sys.stdout, indent=2)` followed by `"\n"`, returning `0` or `2`
(verified at the tail of `implementation_cli.py`). So the sealed surface is well-defined:
**stdout bytes plus exit status, per case**. The seal is a committed roster of invocation
cases, a deterministic corpus built from committed code, an ordered normalizer chain, and
committed digest goldens. A cut re-runs the roster and must reproduce every digest.

Two entry points, one mechanism:

- `tests/seal_capture.py` — **capture** (regeneration). Runs each case **twice**, refuses
  to write anything if any pair disagrees. Not matched by `unittest discover`'s `test*.py`
  pattern, so it never runs in the suite. Precedent: `tests/forge_vocabulary.py` is
  already a non-`test_*` module inside `tests/`.
- `tests/test_implementation_seal.py` — **comparison** (recurring). Runs each case
  **once** and compares against the goldens. This is the guard.

## Architecture Decisions

### D1 — Where the harness lives and how it stays cheap

**Choice**: comparison lives in `tests/test_implementation_seal.py`, inside the normal
`unittest discover -s tests` run. Capture is a separate module invoked by hand.

**Alternatives rejected**: (a) env-var gate — a skipped test and a switched-off guard look
identical, and it would move the `skipped=6` baseline; (b) fully standalone script — a
seal nobody runs is not a seal; (c) capture-twice on every suite run — doubles the
recurring cost for a property only capture needs.

**Cost budget**: 29 cases × 1 subprocess ≈ 0.4 s each ≈ 12 s, plus one corpus build and 29
`copytree`s of a small tree. **Ceiling: the new file adds ≤ 60 s to `unittest discover`.**
Apply MUST measure the delta (`time` the discover run before and after) and paste it. If
it exceeds 60 s, the fix is fewer *duplicate* cases, never fewer covered commands.

**Zero new skips.** `skipped=6` is part of the non-interference evidence.

### D2 — How the 20 subcommands are invoked

**Choice**: real subprocess, argv built as
`shlex.split(impl.CLI_INVOCATION) + case_argv`.

**Alternatives rejected**: (a) in-process `impl.main(argv)` under `redirect_stdout` — fast,
but it bypasses the process boundary, and Cut 1's single silent failure mode (per
measurement §C) is `CLI_PATH`/`SKILL_ROOT` resolving to the engine rather than the
launcher. A seal blind to that is blind to the exact thing it exists to catch.
(b) `[sys.executable, str(CLI)]` — this is the *repaired* shape
`PublishedCommandsRunVerbatimTests` documents as the original defect. Sourcing argv from
`CLI_INVOCATION` reuses the existing mechanism instead of inventing a second one, and it
is also **why the interpreter portion of `CLI_INVOCATION` must be normalized out** (it is
echoed inside published `resolve.command` values in refusal payloads) — narrowly, not the
whole value. `str(CLI_PATH)` must survive normalization: a `CLI_PATH` that resolves to the
wrong file after Cut 1 (measurement §C's single silent failure mode for that cut) is
exactly the failure this seal exists to catch, and it can only be observable if the sealed
bytes still name the file. See D4 N3.

**Environment is constructed, never inherited.** The child env is an explicit dict:
`PATH`, `HOME`, plus `PYTHONHASHSEED=0`, `PYTHONDONTWRITEBYTECODE=1`, `LC_ALL=C.UTF-8`,
`TZ=UTC`, `NO_COLOR=1`, `COLUMNS=80`, `GIT_CONFIG_GLOBAL=/dev/null`,
`GIT_CONFIG_SYSTEM=/dev/null`, and `IMPLEMENTATION_PROPOSALS` only when the case says so.
Inheriting `os.environ` would let an operator's stray `IMPLEMENTATION_*` silently reshape
every digest. A test asserts the env builder emits no key outside that allow-list.

### D3 — The corpus: committed as code, built per run

**Choice**: `tests/seal/corpus.py` writes every fixture byte from module-level string
constants into a per-run temp root, then `git init`s with pinned identity and pinned
`GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`. Each case gets its own `copytree` scratch copy, so
writing commands (`apply`, `materialize`, `position`, `settle`, `defect`) are contained
and repeatable.

**Alternatives rejected**: a committed fixture tree — a target must be a git repository, and
a nested `.git` cannot be committed. A per-run *ad hoc* build — the corpus would drift
between capture and comparison.

**Anti-trim guard**: `digests.json` stores `sha256(corpus.py source bytes)`.
`test_corpus_fingerprint_matches` goes red the moment anyone edits the corpus without
recapturing. This is what stops the corpus being trimmed silently under time pressure.

**Fixture trees**

| Id | What it is | What it is for |
|---|---|---|
| `A` | `sealbox/` target, package `Seal`: `src/Seal/__init__.py` with `__provenance__` and populated `arms`; `src/Seal_Benchmark/__init__.py` with `__steps__`; `tests/findings.py` with four findings covering `remedy_block`, `adoption` (one adopted), `uses`, `introduces`; `Seal/{Notebooks,Data,Results,Models}`; `AGREED.md`; git-committed | the 14 provenance sites and the 14 findings sites |
| `B` | `A` with `Seal/Data/` **absent** | `Data/` absent leg |
| `P` | proposals dir: `seal-1.md`, `seal-2.md` (both prefixed `MANAGED_ARTIFACT_MARKER`), `draft-1.md` + `draft-01.md` (no marker) | marker-owned family, hand-authored family, and the **tie** — `draft-1`/`draft-01` are one family and one digit key, `revision_discovery` reports them in `tied` |
| `plan.json` | a committed approved plan | feeds `apply` and `materialize --stage` |

**Env states**: `E0` = `IMPLEMENTATION_PROPOSALS` unset; `E1` = set to `P`.

**Case roster** (`tests/seal/cases.json`, 29 cases, all 20 commands):

| # | Command | Fixture | Env | Purpose |
|---|---|---|---|---|
| 1 | `name` | — | E0 | no-repository command |
| 2 | `walk` | A | E1 | |
| 3 | `plan` | A | E1 | |
| 4 | `plan` | B | E1 | `Data/` absent |
| 5 | `apply` | A | E1 | writing command, contained copy |
| 6 | `admit` | A | E1 | provenance + findings, success leg |
| 7 | **`admit`** | A | **E0** | **F3 site 1 refusal** |
| 8 | `handoff` | A | E1 | findings routing |
| 9 | `handoff` | A | E0 | the correct precedent (no path in message) |
| 10 | `compose` | A | E1 | sealed, otherwise untouched (M1 not decided here) |
| 11 | `probe` | A | E1 | |
| 12 | `verify` | A | E1 | discovery: `markerOwned` true |
| 13 | `verify` | B | E1 | `structure.missingDirs` differs from #12 |
| 14 | `verify` | A | E1 `--revision draft-1.md` | hand-authored family + `tied` non-empty |
| 15 | `position` | A | E1 `--sequence` | |
| 16 | **`position`** | A | **E0** | **F3 site 2 refusal** |
| 17 | `discuss` | A | E1 | |
| 18 | `propose` | A | E1 | |
| 19 | `gate` | A | E1 | refuses, no authorization minted |
| 20 | **`gate`** | A | **E0** | **F3 site 3 refusal** |
| 21 | `offer` | A | E1 | |
| 22 | **`offer`** | A | **E0** | **F3 site 4 refusal** |
| 23 | `close` | A | E1 | |
| 24 | **`close`** | A | **E0** | **F3 site 5 refusal** |
| 25 | `step` | A | E1 | refuses `INTERPRETER_ABSENT` — no `.venv`, so no suite runs |
| 26 | `settle` | A | E1 | |
| 27 | `defect` | A | E1 | `--file` a forge-owned file |
| 28 | `materialize` | A | E1 | |
| 29 | `env` | A | E1 `--python /nonexistent/python` | refuses **before** building a venv |

Cases 25 and 29 are deliberately pinned at their bounded legs: `step` runs a suite and
`env` builds a venv, and either would put minutes into every suite run.

**Coverage is asserted over the captured output, not over the fixture.** A fixture
inspected for shape can be satisfied by an empty file; an output is not.

- `test_provenance_reaches_the_output`: case 6/12 normalized output carries ≥1 module with
  a non-empty equation list and ≥1 arm.
- `test_findings_reach_the_output`: case 8 has **all three** of `inline`, `deferred`,
  `settled` non-empty (which requires `remedy_block`, `remedy_equations` and an adopted
  `adoption` to be live), and ≥1 item with non-empty `introduces`.
- `test_case_13_is_the_instrument_that_would_catch_a_botched_f5`: **replaces the original
  `test_data_absence_is_visible`, whose claim was measured FALSE during apply, 2026-09-11,
  before any capture ran** — record kept rather than deleted, per this repo's own
  discipline that a corrected claim is worth more beside its refutation than a clean one.

  **The original claim, and why it is false.** "case 12 and case 13 digests differ, and
  case 13's output names a missing `Data` directory" — measured: build fixture A (`Data/`
  present) and fixture B (`Data/` absent), otherwise byte-identical, run `verify` against
  both. `json.loads(a.stdout) == json.loads(b.stdout)` is **`True`** — the two payloads
  are completely identical, not merely `missingDirs`. `rg 'PRODUCT_DIRS\[1\]|"Data"'` over
  the whole 17,100-line CLI returns exactly three hits: the tuple definition (111),
  `expected_dirs`'s own self-fulfilling filter (2502), and the one
  `with_data = (target / name / "Data").is_dir()` computation (14249) that feeds it — no
  other command or field reads `Data` at all. This is measurement finding B4, confirmed to
  reach the *entire* `verify` payload today, and B4/F4 (threading `--revision` through
  `plan`, which would make `with_data` non-self-fulfilling) is explicitly Out of Scope.

  **What case 13 actually proves, instead.** It is not there to show a missing `Data/`
  *today* — it is the only case in the corpus where a botched F5 becomes visible at all.
  `expected_dirs`'s filter is `d != PRODUCT_DATA or with_data`: when `with_data` is
  `True` (fixture A), that `or` makes the condition trivially true for every `d`,
  regardless of what `PRODUCT_DATA` is bound to — fixture A's `expected_dirs` output is
  **invariant to a wrong `PRODUCT_DATA`**. Only when `with_data` is `False` (fixture B)
  does `PRODUCT_DATA`'s value actually decide which one directory is excluded from the
  expected list, and excluding the wrong one leaves the genuinely-absent `Data/` IN the
  expected list, moving `missingDirs`. Measured with `PRODUCT_DIRS[2]` ("Results")
  substituted for the correct `PRODUCT_DIRS[1]` ("Data"):

  ```
  with_data=False   (fixture B, Data/ ABSENT)
    correct PRODUCT_DATA: ['M/Notebooks', 'M/Results', 'M/Models']
    botched PRODUCT_DATA: ['M/Notebooks', 'M/Data',    'M/Models']
    DIFFER: True            <- case 13 sees it

  with_data=True    (fixture A, Data/ PRESENT)
    correct PRODUCT_DATA: ['M/Notebooks', 'M/Data', 'M/Results', 'M/Models']
    botched PRODUCT_DATA: ['M/Notebooks', 'M/Data', 'M/Results', 'M/Models']
    DIFFER: False            <- fixture A is blind to it
  ```

  So **keep both fixtures**; dropping case 13 would leave F5 an edit no instrument in this
  change could check, the precise opposite of its stated purpose as "the seal's first live
  customer" (D8). The corrected test asserts what is actually true today —
  `test_corpus_provably_exercises_data_present_and_absent` (a construction-level check:
  fixture A's `Seal/Data/` exists on disk, fixture B's does not — satisfying spec.md's
  literal "provably exercise ... reached by at least one case" wording) — and D8 carries
  the mutation that proves case 13's instrument value: see below.
- `test_both_revision_families_and_a_tie_are_exercised`: case 12 reports
  `markerOwned: true`; case 14 reports a non-empty `tied`.
- `test_every_f3_site_is_sealed_in_both_env_states`: exact set equality over
  `{admit, position, gate, offer, close} × {E0, E1}`.

### D4 — Normalization, one rule at a time

`tests/seal/normalize.py` — an ordered tuple `NORMALIZERS = (N3, N2, N1, N5)` of named
single-purpose functions. **The order is load-bearing and pinned by
`test_normalizer_order_is_pinned`**: N3's match target is the interpreter token
`shlex.quote(sys.executable or "python3")` only — narrower than the whole
`CLI_INVOCATION` string (see the correction below). In this repo the venv interpreter
itself resolves under `FORGE_ROOT` (`<repo>/.venv/bin/python3`), so if N2 rewrote the
forge prefix first, N3's literal would no longer match. N3 must still run before N2.

**Correction to the original N3 shape (found by the parallel Cut-1 proposal, before
capture).** The first draft of N3 replaced the *entire* `impl.CLI_INVOCATION` value with
`<CLI>`, which erases `str(CLI_PATH)` along with the interpreter. That is exactly the
byte the seal exists to protect: measurement §C names Cut 1's single silent failure mode
as `CLI_PATH` resolving to the engine instead of the launcher, and design D2 chose real
subprocess invocation over in-process specifically so that resolution would be
observable ("an in-process seal is blind to exactly that"). A whole-value N3 erasure
makes the seal blind to the one failure it was built to catch — green regardless of
which file actually ran. **Fixed**: N3 normalizes only the interpreter token, leaving
`str(CLI_PATH)` in the sealed bytes; N2 then turns that absolute path into the stable,
machine-independent `<FORGE>/.claude/skills/proposal-implementation/scripts/implementation_cli.py`.
A wrongly-resolved `CLI_PATH` now changes that substring and moves the digest.

Each normalizer gets **two** tests — a reach pair and a guard pair. The reach pair is its
named mutation (delete the normalizer, the pair stops collapsing, red). The guard pair is
the symmetric defence: over-normalization makes the seal vacuous, so each rule must be
shown *not* to eat adjacent real output.

| Id | Rule | Reach mutation (must collapse) | Guard (must stay distinct) |
|---|---|---|---|
| **N1** `iso8601_timestamps` | `\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z` → `<TS>` | two samples differing only in a `_now_iso8601()` stamp | `"2026-09-10"` (bare date) and `"2026-09-11"` remain different |
| **N2** `absolute_roots` | exact substring replacement, longest-first, of the four known roots: scratch target → `<TARGET>`, corpus root → `<CORPUS>`, `str(FORGE_ROOT)` → `<FORGE>`, proposals dir → `<PROPOSALS>` | two samples differing only in the tmpdir name | `src/Seal/__init__.py` and `src/Seal/steps.py` remain different; `/usr/bin/x` is untouched |
| **N3** `cli_invocation` | interpreter token only: `shlex.quote(sys.executable or "python3")` → `<PYTHON>` (NOT the whole `CLI_INVOCATION` value — `str(CLI_PATH)` must survive into N2) | two samples differing only in the interpreter path collapse | `python3 other.py` remains different from `python3 another.py` — the `CLI_PATH` difference must survive both N3 and N2 |
| **N4** `session_identity` | **no substitution — pinned instead.** Every `--session` in `cases.json` is a literal from `{"seal-s1","seal-s2"}`; a test asserts no other value appears | change one case's `--session` literal → its digest moves → red. This proves session identity *reaches* the sealed bytes rather than being erased | — (N4 erases nothing, so it cannot over-normalize) |
| **N5** `git_shas` | `\b[0-9a-f]{40}\b` → `<GITSHA>` (belt-and-braces: the corpus already commits under pinned identity and pinned dates) | two corpora committed at different dates | a 64-hex `sha256` survives (`\b…{40}\b` cannot match inside a 64-run); a second test asserts no golden contains a 7–12 hex short sha |
| **N6** `content_digests` | **deliberately NOT normalized.** `source_digest`, `suite_digest` and `revisionSha256` are content-derived over a byte-fixed corpus, so they are already deterministic. Normalizing them would blind the seal to a change in the digest *algorithm* — exactly what Cut 2/3 can break | build the corpus with one byte flipped in `src/Seal/__init__.py` and assert the case-12 digest **moves**. If anyone later adds a `<DIGEST>` normalizer, the digest stops moving and this test goes red | — |

`_now_iso8601()`, absolute `str(target)`, `CLI_INVOCATION`, `--session` ids, git shas and
`source_digest`/`suite_digest` — all six sources the proposal names are accounted for, two
of them (N4, N6) by *pinned determinism with a mutation* rather than by erasure, with the
reason stated. A normalizer switched off and a normalizer never written produce identical
green output; the reach pairs are what tell them apart.

**N3's pinned companion — `test_the_sealed_cli_path_names_the_launcher`.** Narrowing N3
to the interpreter only is correct only if `str(CLI_PATH)` actually survives, through N2,
into the digested bytes; this test pins that directly, the same idiom N4 uses for
`--session`. After full `normalize()`, every case whose captured stdout embeds
`CLI_INVOCATION`-derived text — the `gate` cases (#19, #20), the `step` case (#25), the
`discuss` case (#17) — contains the literal substring
`<FORGE>/.claude/skills/proposal-implementation/scripts/implementation_cli.py`. Its named
mutation: in the raw (pre-normalization) captured text, substitute a different resolved
path for the launcher's before calling `normalize()` — the assertion must go red. This is
the single most load-bearing mutation in the change: without it, the other normalizer
proofs guard an instrument that cannot see the one thing Cut 1 can silently break.

### D5 — Flakiness defence: capture twice, refuse on disagreement

**Choice**: `seal_capture.py` runs every case twice within one invocation and compares the
**normalized** bytes and exit status. On any disagreement it writes **nothing at all** —
not for that case, not for the run — and exits non-zero, printing the case id and a
unified diff of the two normalized outputs.

**Rejected**: recording the disagreeing case as unsealed. An unsealed entry is a
*reasoned, human-written* exemption; a disagreement is an *unexplained* nondeterminism.
Auto-converting one into the other is the seal quietly relaxing itself to accommodate a
problem — the exact failure the ordering discipline exists to prevent. The human either
adds a normalizer, or writes the reason into `unsealed.json` by hand.

All-or-nothing writing also means a half-written golden set can never exist.

### D6 — The unsealed set and its exact-membership test

`tests/seal/unsealed.json` maps case id → reason (a non-empty string, ≥ 20 chars). It is
expected to be `{}` today.

Three tests, in `test_implementation_seal.py`:

1. `test_every_case_is_either_sealed_or_declared_unsealed`
   `set(digests) | set(unsealed) == set(cases)` **and**
   `set(digests) & set(unsealed) == set()`.
   Adding a case without capturing or exempting it → red (absent from both). Removing a
   case → red (stale key on the other side).
2. `test_the_unsealed_set_is_exactly_its_declared_membership`
   `frozenset(unsealed) == EXPECTED_UNSEALED`, where `EXPECTED_UNSEALED = frozenset()` is a
   literal **in the test file**. Growing the set requires editing the test — deliberate
   friction, so it cannot grow silently.
3. `test_the_case_roster_covers_the_command_roster_exactly`
   `{c["command"] for c in cases} == set(impl.COMMANDS)`. A 21st command with no case → red.
   A deleted command with a stale case → red.

Plus `test_every_unsealed_entry_states_a_reason`.

### D7 — F3: the declared delta, and its exact shape

All five sites are the **same one-line substitution**. Written to
`openspec/changes/the-seal-before-the-cut/f3-message-delta.md` **before** capture.

Before, at `cmd_admit` / `cmd_position` / `cmd_gate` / `cmd_offer` / `cmd_close`
(currently lines 7535, 10362, 12982, 13509, 13683 — re-locate by the string, not the
line):

```python
            f"{args.revision!r} is not readable under {FORGE_ROOT / 'proposals'}; "
```

After, all five:

```python
            f"{args.revision!r} is not readable under {proposals_root()}; "
```

The surrounding second line of each message is **unchanged**:

| Site | Function | Unchanged continuation |
|---|---|---|
| 1 | `cmd_admit` | `"admissibility cannot be ruled on and no remedy may be measured."` |
| 2 | `cmd_position` | `"the position header cannot be bound to a revision."` |
| 3 | `cmd_gate` | `"a gate cannot be recorded against a revision that cannot be read."` |
| 4 | `cmd_offer` | `"offer cannot publish an action set against a revision that "` `"cannot be read."` |
| 5 | `cmd_close` | `"close cannot require a position true against a revision that "` `"cannot be read."` |

Site 1 is written with the `raise Refused("REVISION_UNREADABLE",` argument on the same
line and 22-space continuation indent; sites 2–5 use `raise Refused(` / newline /
`"REVISION_UNREADABLE",` / newline with 12-space indent. Preserve each site's own
indentation; only the `{FORGE_ROOT / 'proposals'}` expression changes.

**The delta's measured shape**: `proposals_root()` is
`Path(override) if override else FORGE_ROOT / "proposals"`. So the rendered message is
**byte-identical when `IMPLEMENTATION_PROPOSALS` is unset**, and differs only under the
override. Declared consequence, checkable per case:

- Cases 7, 16, 20, 22, 24 (E0): **zero delta.** Pre-F3 and post-F3 bytes identical.
- Cases 6, 15, 19, 21, 23 (E1): these succeed or refuse for other reasons, so they carry no
  F3 text. The override rendering is proven by a dedicated behavioural test rather than by
  a sealed case — `test_a_refusal_under_an_override_names_the_override` runs `admit` with
  `IMPLEMENTATION_PROPOSALS` pointed at an empty directory and asserts the message contains
  that directory and not `FORGE_ROOT / "proposals"`.

`cmd_handoff` (function begins at 7354 — the measurement's 7368 is the `raise` line inside
it, not the function) omits the path entirely and is the correct precedent; it is not
touched.

**Anchor discipline** (recorded scar: an anchor that matched is not a mutation that ran;
`sd -s` can exit 0 and change nothing). Apply asserts, by reading the file:
`source.count("FORGE_ROOT / 'proposals'")` is **5 before** and **0 after**;
`source.count("{proposals_root()}")` is **0 before** and **5 after**. Both counts pasted.
The `== 0` half becomes a permanent test,
`test_no_refusal_names_a_directory_the_code_never_read`.

### D8 — F5 after capture, and how the zero is asserted

Introduce, beside `PRODUCT_NOTEBOOKS` (currently line 120):

```python
#: The product category a repository's data lives under, named off `PRODUCT_DIRS`
#: rather than spelled a second time, for the reason `PRODUCT_NOTEBOOKS` above
#: states: a second literal beside the tuple is how the two come to disagree the
#: day a layout changes.
PRODUCT_DATA = PRODUCT_DIRS[1]
```

and in `expected_dirs` (currently line 2502):

```python
    dirs = [f"{name}/{d}" for d in PRODUCT_DIRS if d != PRODUCT_DATA or with_data]
```

**How the zero is asserted — five independent instruments, not one green suite:**

1. **Identity, at the constant**: `test_the_data_category_is_read_from_the_tuple` asserts
   `impl.PRODUCT_DATA == "Data"` and `impl.PRODUCT_DATA is impl.PRODUCT_DIRS[1]`, and
   `assertNotIn(f'"{impl.PRODUCT_DATA}"', inspect.getsource(impl.expected_dirs))` — the
   exact shape of the existing precedent
   `test_the_notebook_category_is_read_from_the_forge_not_written_here`.
2. **Identity, at the function**: `expected_dirs("Seal", with_data=True)` and
   `(…, with_data=False)` compared against **pinned literal lists** written into the test,
   not derived from `PRODUCT_DIRS`. A derived expectation moves with the code (§C's whole
   objection) and would prove nothing.
3. **The seal itself**: cases 4 and 13 (fixture `B`, `Data/` absent) and 3 and 12
   (fixture `A`, present) run the comparison after F5 and must reproduce the pre-F5
   digests **unchanged**. This is the F5 zero-delta claim.
4. **The mutation that matters — pick the lock a weaker one would survive.** Zero-delta
   alone only proves this refactor is an identity; it says nothing about whether the seal
   could have caught it if it were NOT one. Per the D3 correction above, fixture A (`with_data=True`)
   is structurally blind to `PRODUCT_DATA`'s value — the `or with_data` short-circuit makes
   every case run against fixture A invariant to it — so only case 13 (fixture `B`,
   `with_data=False`) can see a wrong index move. `test_a_wrong_product_data_moves_case_13`
   temporarily binds `PRODUCT_DATA = PRODUCT_DIRS[2]` (`"Results"`, or any non-`Data`
   member), re-runs the comparison, and asserts **case 13's digest moves** while (as a
   guard against the mutation accidentally reaching further than intended) case 12's does
   not. Then reverts and re-asserts zero delta. Without this, F5's own coverage cell could
   be dropped from the corpus and nothing in this change would notice.
5. **Recorded, not inferred**: `openspec/changes/the-seal-before-the-cut/f5-zero-delta.md`
   carries the commit sha before F5, the sha after, and the pasted comparison-test output
   from both, plus instrument 4's reach/revert pair. `git diff --stat` is not evidence
   here — the goldens are newly added files, and for untracked or newly-added paths a stat
   proves nothing.

## Data Flow

```
tests/seal/corpus.py ──build──→ tmp corpus (git, pinned dates)
        │                              │
        │                              └──copytree──→ per-case scratch
        │                                                  │
tests/seal/cases.json ──argv──→ shlex.split(CLI_INVOCATION) + argv
                                                   │
                                          subprocess (constructed env)
                                                   │
                                        stdout bytes + exit status
                                                   │
                            normalize.py:  N3 → N2 → N1 → N5   (N4/N6: pinned, not erased)
                                                   │
                    ┌──────────────────────────────┴──────────────────────────────┐
             capture (×2, must agree)                                    compare (×1)
                    │                                                             │
          tests/seal/digests.json  ◀────────────────── sha256 ──────────────────▶ assert
          tests/seal/unsealed.json
```

## File Changes

| File | Action | Description |
|---|---|---|
| `.claude/skills/proposal-implementation/scripts/implementation_cli.py` | Modify | F3: five message lines. F5: `PRODUCT_DATA` + `expected_dirs` |
| `tests/test_implementation_seal.py` | Create | comparison, coverage, membership, normalizer reach/guard pairs, F3 and F5 guards |
| `tests/seal/__init__.py` | Create | package marker |
| `tests/seal/corpus.py` | Create | corpus as committed code |
| `tests/seal/normalize.py` | Create | N1, N2, N3, N5 + ordered `NORMALIZERS` |
| `tests/seal/cases.json` | Create | the 29-case roster |
| `tests/seal/digests.json` | Create | goldens (generated; excluded from authored review count) |
| `tests/seal/unsealed.json` | Create | `{}` today |
| `tests/seal_capture.py` | Create | double capture, refuse-on-disagreement |
| `openspec/changes/the-seal-before-the-cut/f3-message-delta.md` | Create | before capture |
| `openspec/changes/the-seal-before-the-cut/f5-zero-delta.md` | Create | after capture |

## Interfaces

```python
# tests/seal/normalize.py
NORMALIZERS: tuple[Callable[[str, Roots], str], ...]   # order pinned by test
def normalize(text: str, roots: Roots) -> str: ...     # folds NORMALIZERS left to right

# tests/seal/corpus.py
def build(root: Path) -> Roots: ...                    # writes A, B, P, plan.json; git init
CORPUS_FINGERPRINT_SOURCE = Path(__file__)             # digested into digests.json

# case record (cases.json)
{"id": "admit-e0", "command": "admit", "fixture": "A",
 "proposals": false, "argv": ["--target","<TARGET>","--name","Seal",
                              "--revision","seal-2.md"]}
# golden record (digests.json)
{"admit-e0": {"sha256": "...", "bytes": 1234, "exit": 2}}
```

`<TARGET>` and `<PROPOSALS>` in `argv` are substituted with the scratch paths at run time —
the same placeholders N2 produces, so the roster is readable and path-free.

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | each normalizer | reach pair (collapses) + guard pair (stays distinct); D4 table |
| Unit | normalizer order | `NORMALIZERS` identity pinned; N3 before N2 |
| Unit | `CLI_PATH` identity | `test_the_sealed_cli_path_names_the_launcher` — pinned assertion the launcher path survives N3+N2 into the sealed bytes; mutation: a different resolved path → red (the most load-bearing mutation in the change, see D4) |
| Unit | env allow-list | the child env builder emits no key outside the list |
| Unit | F5 identity | pinned literal `expected_dirs` outputs; `PRODUCT_DATA` source guard |
| Unit | F3 anchors | old spelling count `== 0`, permanently |
| Integration | the seal | 29 cases, normalized, digest-compared |
| Integration | coverage | provenance/findings/Data/families/tie asserted over **output** |
| Integration | membership | sealed ∪ unsealed == cases; unsealed == literal; commands == `COMMANDS` |
| Integration | F3 override | refusal under `IMPLEMENTATION_PROPOSALS` names the override |
| Mutation | **the seal itself** | flip one byte of one captured output → comparison red. This is the criterion the change exists for |
| Mutation | corpus | corpus fingerprint mismatch → red |
| Non-interference | sister skill | `npm test` = 595/0; python `Ran 2783+K, OK (skipped=6)`, zero failures, skip count unchanged. Both outputs pasted, never asserted |

## Threat Matrix

| Row | Applicable | Behaviour / RED test |
|---|---|---|
| Subprocess invocation | **Yes** | argv is a list, never a shell string; `shell=False`; no `cwd` inside the forge for writing cases. RED: a case whose argv contains a shell metacharacter is refused by the roster validator |
| Environment inheritance | **Yes** | constructed allow-list env; RED: env builder emits an unexpected key |
| Filesystem writes | **Yes** | every writing command runs against a `copytree` scratch under `tempfile`; RED: a case whose `--target` is not under the scratch root is refused |
| Timeouts / hangs | **Yes** | every `subprocess.run` carries `timeout=120`; a timeout is a hard failure, never an unsealed entry |
| VCS automation | **Yes (bounded)** | `git init`/`add`/`commit` only, inside the scratch corpus, with `GIT_CONFIG_GLOBAL=/dev/null` |
| Executable classification | N/A | the seal classifies nothing; the CLI stays mode 644 |
| Routing / PR automation | N/A | no routing surface |
| Network | N/A | no case reaches the network; `env` is pinned at its refusal leg |

## What Breaks

**Producers** (measured, not assumed):

- Five `Refused("REVISION_UNREADABLE", …)` message strings. **No existing test asserts this
  text** — `rg 'is not readable under'` over `tests/` returns nothing; the eleven
  `REVISION_UNREADABLE` hits all assert the `code`, never the `detail`. F3 breaks no
  existing test.
- `expected_dirs`' comparison expression. Existing callers (`test_proposal_implementation.py:10225`)
  pass `with_data=False` and read the returned list; `PRODUCT_DIRS[1] == "Data"` makes the
  return value identical.
- `unittest discover`'s test count rises by K. The **skip count must stay 6**.

**Products** — records already written under the old shape:

- Minted `gate` authorization tokens inside targets' committed
  `.implementation/position.jsonl`: **untouched.** Neither F3 nor F5 touches
  `_AUTHORIZATION_BINDING_KEYS`, `proposalDigest` or `revisionSha256`; a refusal message is
  never written into a ledger event.
- Existing `admissibility.json` rulings and position blocks: **untouched** — same reason.
- Archived reports carrying `source_digest`/`suite_digest`: **untouched**; F5 does not
  change any digest input, and the seal only reads.
- Previously captured seal digests: **none exist.** This change creates the first ones.

## Migration / Rollout

No migration. Rollout is the proposal's four-step ordering, and step 1 before step 3 is the
whole discipline: write `f3-message-delta.md` → apply F3 → capture → apply F5.

Under the session's time ceiling, execution stops after step 3 (F3 applied, delta declared)
and the capture runs next session with an unrushed corpus. That is an execution decision;
the design is the whole change.

## Open Questions

- [x] The 60 s discover-delta ceiling is a forecast, not a measurement. **Resolved**: the
      new seal file's own isolated cost is `Ran 38 tests in 4.941s`, well inside the
      ceiling; the full-suite wall-clock is dominated by inter-run system-load noise
      (587.935s → 528.710s → 458.560s across three measurements of a growing but still
      noise-dominated suite), never attributable to this file alone. No cases cut.
- [x] Whether `materialize` (case 28) has a bounded, non-destructive leg on a scratch copy,
      or must be pinned at a refusal like `step` and `env`. **Resolved**: measured —
      `materialize --stage scaffold` (with `--plan`/`--seed`) runs instantly and writes
      only inside the scratch target (real kit files, never outside it). Kept at its
      current non-destructive leg; no pin needed.
- [ ] `compose` (M1) is sealed and otherwise untouched. That decision stays out of this
      change.
- [x] **Not anticipated by the original design, resolved during apply**: `propose`'s own
      campaign digest embeds `_now_iso8601()`, so it disagrees across two immediate
      captures even with source/session/job/rationale fixed — none of the six normalized
      sources reach an opaque hash derived from, but not textually equal to, a timestamp.
      Declared unsealed with a reason (D6's own mechanism, spec.md's own provision for
      exactly this), rather than a seventh normalizer (spec.md names exactly six sources).
      28 of 29 cases sealed; see `tests/seal_capture.py`'s `KNOWN_UNSEALED_REASONS`.
- [x] **Not anticipated by the original design, resolved during apply**: case 14
      (`verify --revision draft-1.md`, "hand-authored family + tied") cannot share fixture
      A's declared family with case 12 (`markerOwned true`) — measured: `verify`'s
      `discovery`/`tied`/`markerOwned` fields derive SOLELY from the target's own declared
      revision (`cmd_verify`'s own `family` derivation), never from `--revision`. Gave case
      14 its own fixture, `fixture_t` in `corpus.py`: `__benchmark__` undeclared, one
      module's own `__provenance__` declares family `draft-1.md`, falling back exactly like
      the existing precedent `test_a_directory_nobody_manages_behaves_exactly_as_it_did`.

## Citations Checked

Every symbol below was re-located in the source during this phase, not inherited: the five
`FORGE_ROOT / 'proposals'` sites (5 hits, exactly), `proposals_root()` (4402),
`revision_source` (4423), `cmd_handoff` (**begins 7354**, not 7368 — the measurement cites
the `raise` line), `_now_iso8601` (8272), `CLI_INVOCATION` (108), `PRODUCT_DIRS` (111),
`PRODUCT_NOTEBOOKS` (120), `expected_dirs` (2501-2504), `COMMANDS` (16572, 20 entries),
`main` (16589) and its `json.dump(..., indent=2)` exits, `source_digest` (6237),
`suite_digest` (6317), the tie rule (4486, `draft-1.md` / `draft-01.md`),
`MANAGED_ARTIFACT_MARKER` (4420), `PublishedCommandsRunVerbatimTests`
(`tests/test_proposal_implementation.py:31710`) and the `PRODUCT_NOTEBOOKS` precedent test
(same file, 11891).
