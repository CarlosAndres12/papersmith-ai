# Proposal: The Seal Before The Cut

## Intent

`proposal-implementation`'s 17,100-line CLI will be extracted into a profile-driven
shared engine across three later cuts. **Nothing may cut until preservation can be
proven, and today it cannot be.**

Seam measurement §C (`openspec/changes/_measurements/experimental-implementation-seam-measurement.md`):

> The existing suites cannot prove preservation. `npm test` (595) is entirely the Node
> deliberation side. The Python suite (2,783) is dominated by DERIVATION tests that read
> their expectations off the code's own literals … Every one goes green across a refactor
> that moves the code and its derived expectation together. **They prove internal
> consistency. They do not prove preservation.**

The operator's binding constraint: *"todo lo que hagas no puede afectar lo que ya
funciona en la skill hermana."* Byte-for-byte, as `proposal-deliberation/SKILL.md:301`
defines it: *"Untouched content is byte-identical … a guarantee the engine enforces
**structurally, not a courtesy**."* Every non-interference claim here is proven by a
command whose output is pasted, never asserted.

This change builds the instrument. **It moves no code toward the extraction and cuts
nothing.**

## Scope

### In Scope

1. **The seal.** All **20** subcommands (verified: 20 `cmd_*` functions, 20 `COMMANDS`
   entries) run against a fixed fixture corpus; stdout **bytes** and exit status captured
   and digested. A later cut re-runs and requires byte-identical stdout and identical exit
   status.
2. **The corpus, exercising by construction** (§C.3): all 14 provenance schema sites
   (target with `__provenance__` and populated `arms`); all 14 findings sites (populated
   `tests/findings.py` with `remedy_block`, `adoption`, `uses`, `introduces`); the 5
   hardcoded-path refusals **both with and without `IMPLEMENTATION_PROPOSALS` set**;
   `Data/` present and absent; a marker-owned and a hand-authored revision family; a tie.
3. **Normalization** (§C.4), or the seal is noise: `_now_iso8601()`, absolute
   `str(target)`, `CLI_INVOCATION` (contains `sys.executable`), `--session` ids, git
   commit shas, `source_digest`/`suite_digest`.
4. **F3 — the one sanctioned behaviour change.** Five refusal messages spell
   `FORGE_ROOT / 'proposals'` while the read went through `proposals_root()`, which
   honours `IMPLEMENTATION_PROPOSALS` (verified at lines 7535, 10362, 12982, 13509,
   13683; `proposals_root()` at 4402; `cmd_handoff` omits the path and is correct). All
   five move to `proposals_root()`.
5. **F5.** `expected_dirs` spells `"Data"` as a bare literal beside `PRODUCT_DIRS`
   (verified, line 2502) — the exact second-literal defect the comment at 113-119 argues
   against for `PRODUCT_NOTEBOOKS = PRODUCT_DIRS[0]`. Introduce `PRODUCT_DATA =
   PRODUCT_DIRS[1]` with the same comment.

### Out of Scope

Not proposed, not listed as future work:

- Cut 1 (file move, per-skill launcher), Cut 2 (the 167 lines), Cut 3 (scalar→pair on the
  24 `revisionSha256` sites).
- Any rename of `proposalDigest` or the F1 campaign-proposal identifiers — they are
  written into minted authorization tokens in committed ledgers that travel in clones.
- F6 (`MANAGED_ARTIFACT_MARKER`'s four spellings). Recorded, not acted on.
- The `compose` question (M1). `compose` is captured by the seal like every other
  command and is otherwise untouched. **That decision must not be taken here.**
- Creating the `experimental-implementation` skill.

## Capabilities

### New Capabilities

- `implementation-cli-seal`: the stdout characterization seal — corpus construction
  obligations, normalization of nondeterministic output, byte-identity and exit-status
  comparison, and the declared-delta discipline that governs any sanctioned change to a
  sealed output.

### Modified Capabilities

- None. No existing spec's requirements change. F3 and F5 touch code that no
  `openspec/specs/` capability currently governs (all eleven are deliberation-side except
  `experimental-plan-declarations`).

## Approach

### The ordering is the design

The tension the operator named — F3 **deliberately changes behaviour** while everything
else must change none — is resolved by *when* each edit lands relative to the capture.

| Step | Action | Seal consequence |
|---|---|---|
| 1 | Write `f3-message-delta.md`: all five messages, expected **before** and **after** text | The delta exists on disk before any digest does |
| 2 | Apply F3 (five sites → `proposals_root()`) | — |
| 3 | **Capture the seal** on post-F3 code | Digests are born already accounting for the declared delta |
| 4 | Apply F5 (`PRODUCT_DATA = PRODUCT_DIRS[1]`) | **Zero delta required.** `PRODUCT_DIRS[1] == "Data"`, so this is an identity refactor and the seal must not move |

Step 1 before step 3 is the whole point: a delta declared after capture is a seal quietly
relaxed to accommodate a change, *which is how a seal stops being one*.

Step 4 after step 3 is a proposal decision, not an operator instruction. F5 applied before
capture would be invisible; applied after, it becomes the seal's **first live customer** —
a real edit to production code, demonstrated byte-neutral by the instrument, before any
cut relies on it.

### Proving non-interference

Baselines at `a851390` — `npm test` = 595 pass / 0 fail; `.venv/bin/python -m unittest
discover -s tests` = Ran 2783, OK (skipped=6). Both re-run at the end and **both outputs
pasted**. `.venv/bin/python` (3.12) is mandatory; bare `python3` is 3.9 and breaks. Both
suites print fixture JSON to stdout *and* stderr, so redirect to files and
`rg 'Ran [0-9]+ test'`.

### strict_tdd

Every guard gets a named mutation that turns a test red. The seal itself is the one that
matters: **change one byte of one captured output and the comparison must go red.** A seal
that cannot fail is precisely the failure this change exists to prevent one level down.
Normalization needs its own mutation — a normalizer switched off must redden, or it is
indistinguishable from an absent one.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/proposal-implementation/scripts/implementation_cli.py` | Modified | 5 refusal messages (F3); `PRODUCT_DATA` constant + `expected_dirs` (F5) |
| `tests/test_implementation_seal.py` | New | Seal comparison, normalization, mutation proofs |
| seal corpus builder + stored digests | New | Fixture corpus per §C.3; digests are generated goldens |
| `openspec/changes/the-seal-before-the-cut/f3-message-delta.md` | New | The declared delta, written before capture |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| An unnormalized nondeterminism source is missed; the seal is flaky and gets disabled | Med | Capture twice in one run and require identical digests before storing; a source that differs across two immediate runs is unnormalized |
| Corpus under-exercises the 14+14 schema sites — exactly where Cut 2 lands | Med | Coverage is a spec obligation, asserted by construction, not by inspection |
| The seal is over-normalized into vacuity | Med | Mutation-prove each normalizer; a seal that survives a one-byte change is not a seal |
| Time: the Python suite is ~480 s and must run at least twice | High | See estimate below; forecast, not discovered late |
| A sealed command is nondeterministic in a way normalization cannot reach | Low | Record it explicitly as unsealed with its reason rather than fabricating a digest |

## Rollback Plan

Three independent reverts, no shared state:

- The seal is additive (new test file + fixtures + digests). Delete the added paths;
  both suites return to their `a851390` baselines.
- F3 is five one-line reverts. `git revert` of the change restores all five strings.
- F5 is one constant plus one comparison; reverting restores the bare `"Data"` literal.

No migration, no data, no committed ledger touched. Nothing in `proposal-deliberation`
is written to at any point.

## Dependencies

- `.venv/bin/python` (3.12) present and working.
- HEAD `a851390` baselines are the reference; a rebase invalidates them and they must be
  re-measured, not re-quoted.

## Success Criteria

- [ ] All 20 subcommands have a stored stdout-bytes digest and exit status.
- [ ] Corpus provably exercises: 14 provenance sites, 14 findings sites, 5 refusals × 2
      `IMPLEMENTATION_PROPOSALS` states, `Data/` present + absent, both revision families,
      a tie.
- [ ] All 6 normalization sources handled, each with a mutation that reddens.
- [ ] **A one-byte change to one captured output turns the seal red**, demonstrated.
- [ ] `f3-message-delta.md` exists with before/after text, dated before the digests.
- [ ] F5 applied after capture produces **zero** seal delta.
- [ ] `npm test` = 595/0 and `Ran 2783 … OK (skipped=6)`, both outputs pasted.

## Delivery Forecast

`delivery_strategy: single-pr`, `review_budget_lines: 1400`. Authored additions are
estimated 400–700 lines (harness, corpus builder, mutation tests) plus ~10 modified lines;
stored digests are generated goldens and excluded from authored count. **Within budget.**

**Time to 18:00 — this is tight and may not fit.** Wall-clock floor: the Python suite is
~480 s and must run at least twice (baseline confirmation + final), ~16 min of pure
waiting, plus `npm test` twice. Remaining phases: spec ~15 min, design ~20 min, tasks
~10 min, apply ~60–90 min under strict TDD, verify ~25 min. That is ~2h10–2h40 against
~2h15 available. It fits **only** if spec and design run in parallel and apply runs as a
single writer with no re-scoping. If a phase overruns, the correct cut is **not** the
corpus coverage — that is where Cut 2 lands. The correct cut is to land steps 1–3 (delta,
F3, seal capture) and defer step 4 (F5) to a follow-up, since F5 is the only item with no
downstream dependency.
