# Proposal: The Engine Leaves Its Skill

> **Contingent.** This change MUST NOT start until `the-seal-before-the-cut` has landed
> and the seal is captured. The seal is this change's only proof.

## Intent

`implementation_cli.py` is 17,100 lines of which **167 (0.98%) genuinely name the
mathematical proposal** (seam measurement §A.1). The other 99% is a general engine that
happens to live inside one skill's `scripts/`. A second implementation domain cannot
exist without copying it.

The deliberation side already solved this exact problem: `_core/deliberation/engine/`
plus a **13-line** per-skill `proposal-deliberation/cli.mjs` that names the domain and
hands over. This is **Cut 1 of three** (measurement §B1): the file move and the
launcher, and nothing else. Its whole value is that it is *provable* — every one of the
seal's captured digests must be byte-identical afterwards.

## Precondition — all three, verified, before work starts

- `the-seal-before-the-cut` landed; committed, non-empty seal goldens exist.
- The seal comparison suite is **green** on unchanged code.
- The seal is **mutation-proven**: one byte of one captured output turns it red.

An uncaptured or unproven seal means this change has no instrument and must not begin.

## Scope

### In Scope

1. Move `implementation_cli.py` **verbatim** to
   `.claude/skills/_core/implementation/implementation_engine.py`.
2. A ~15-line launcher at the **unchanged path**
   `.claude/skills/proposal-implementation/scripts/implementation_cli.py`, mirroring
   `cli.mjs`: sets `IMPLEMENTATION_DOMAIN_PROFILE` (`??=` semantics — an explicit
   environment value is a deliberate override and wins), declares its own `__file__` as
   the CLI path, hands over. Every argument and exit code stays the engine's.
3. `_core/implementation/impl_domain_profile.py`: no default, fails closed at import,
   absolute path required, named refusal codes — mirroring `domain-profile.ts`.
   **Cut-1 field set only**: `kit.root` and the CLI path.
4. **Re-point `PublishedCommandsRunVerbatimTests` at the launcher, explicitly.**
5. Re-run the seal through the launcher; require byte-identical stdout and identical
   exit status on every case.

### Out of Scope

Not proposed, not future work here:

- **Cut 2** — the 167 domain lines. They stay exactly where they are, still hardcoded.
- **Cut 3** — scalar→pair on the 24 `revisionSha256` sites.
- The profile's full field set (`documents`, `provenance`, `document_reader`,
  `findings`, `vocabulary`, `objective`, `cli_invocation`).
- Creating `experimental-implementation`.
- Any rename of `proposalDigest`, `GATE_PROPOSAL_*` or the other F1 campaign-proposal
  identifiers — they are written into minted authorization tokens in committed ledgers
  that travel in clones.
- F6, M1 (`compose`), M2, B2's provenance-schema decision.

## Capabilities

### New Capabilities

- `implementation-engine-neutrality`: the engine serves no domain of its own — it
  resolves its host from `IMPLEMENTATION_DOMAIN_PROFILE`, refuses to start without one,
  and sources `kit.root` and its published CLI path from the host rather than from its
  own location.

### Modified Capabilities

- `implementation-cli-seal`: the sealed invocation target must be the **per-skill
  launcher**, not whatever `CLI_INVOCATION` resolves to. The existing `Seal Capture
  Scope` requirement pins the twenty subcommands but not the entry point, and after the
  move those are no longer the same file.

## Approach

### The one silent failure mode (measurement §C)

`CLI_INVOCATION` is built from `CLI_PATH` and `sys.executable`, and is printed into
every published command and into `AGREED.md`. If `CLI_PATH` resolves to the engine,
**published commands still run** — and name a file the reader was never given. Nothing
goes red. The seal chose real-subprocess invocation through `CLI_INVOCATION` precisely
so this is observable; the guard is the explicit re-point in scope item 4.

### The three `__file__`-derived sites

The measurement names two. There is a third, located in the source during this phase:

| Site | Today | After the move | Failure mode |
|---|---|---|---|
| `SKILL_ROOT = Path(__file__).resolve().parents[1]` | the skill dir | `_core/` | **silent** — 17 readers resolve under the wrong root. Must come from `kit.root`; non-optional |
| `CLI_PATH = Path(__file__).resolve()` | the launcher path | the engine path | **silent** — the failure mode above |
| `sys.path.insert(0, …parents[2] / "_core" / "implementation")` | `.claude/skills` | `.claude` | **loud** — `ImportError` at import; must resolve from the engine's own directory |

The third means "verbatim" is exact for 17,097 lines and shaped for three. Everything
else the seal proves neutral.

`FORGE_ROOT` is unaffected: it is `parents[4]` of `_core/implementation/impl_layout.py`,
which does not move.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/_core/implementation/implementation_engine.py` | New | the moved file |
| `.claude/skills/proposal-implementation/scripts/implementation_cli.py` | Replaced | ~15-line launcher, same path |
| `.claude/skills/_core/implementation/impl_domain_profile.py` | New | fail-closed resolver |
| `.claude/skills/proposal-implementation/impl_profile.py` | New | `kit.root`, CLI path |
| `tests/test_proposal_implementation.py` | Modified | `PublishedCommandsRunVerbatimTests` re-pointed |
| `tests/seal/`, `tests/test_implementation_seal.py` | Modified | invocation target pinned to the launcher |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Published commands name the engine; test still passes | **High** | Scope item 4, asserted against the launcher's literal path, with a mutation that reddens |
| `SKILL_ROOT`'s 17 readers silently resolve under `_core/` | High | `kit.root` is mandatory in the Cut-1 profile; the engine has no fallback |
| The seal is relaxed to accommodate a delta | Med | **There is no sanctioned delta.** Any digest movement is a defect, never a new golden |
| The move is done with an edit that matched nothing | Med | Recorded scar: assert anchor counts before and after, paste both |
| `tests/` is being written by a parallel change | Med | Re-locate every symbol by name at apply time; line citations from any artifact are stale |
| `proposal-deliberation` is touched | Low | Nothing in it is written to; both baselines re-run and pasted |

## Rollback Plan

Two reverts, no shared state: `git mv` the engine back and delete the launcher, profile
and resolver; revert the two test re-points. No data, no migration, no committed ledger
touched — the move writes nothing into any target's `.implementation/position.jsonl`.

## Dependencies

- `the-seal-before-the-cut` archived, with green and mutation-proven goldens.
- `.venv/bin/python` (3.12). Bare `python3` here is 3.9 and cannot import these modules.

## Success Criteria

- [ ] Every seal case reproduces its stored digest and exit status **byte-identically**.
      Zero declared delta.
- [ ] `PublishedCommandsRunVerbatimTests` asserts the launcher path, with a named
      mutation (point `CLI_PATH` at the engine) that turns it **red**.
- [ ] The engine refuses to start with `IMPLEMENTATION_DOMAIN_PROFILE` unset, relative,
      or missing `kit.root` — one named refusal per case, each mutation-proven.
- [ ] `SKILL_ROOT`'s readers resolve to the skill directory, asserted at the value.
- [ ] The launcher path is unchanged, so every previously published command still runs.
- [ ] `npm test` and the Python suite hold their baselines; both outputs pasted.

## Proposal Question Round

Four product decisions this proposal assumed. Each is answerable now or deferrable to
design; none blocks writing specs.

1. **Does `kit.root` belong to the profile, or does the launcher pass it?** Assumed:
   profile, mirroring `artifact.directory` in `domain-profile.ts`.
2. **Does the Cut-1 profile carry only `kit.root` + CLI path, or does it declare the
   full field set with everything else unused?** Assumed: minimal. A field nothing reads
   cannot be mutation-proven, and an unprovable field is the shape of a false guard.
3. **Is a Python mirror of the TS domain-profile lock in this cut or Cut 2?** Assumed:
   **Cut 2**, because with no domain words yet moved, the lock would pass vacuously.
4. **Does the `sys.path` site resolve from the engine's own directory, or become a
   profile field?** Assumed: **its own directory**. The core modules are the engine's
   siblings for every host, so making it host-supplied invents a way to get it wrong.
