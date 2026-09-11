# Design: Only the Block Changes

## Technical Approach

A stdlib-only, fail-closed CLI in the shape of `implementation_cli.py` and `remote_cli.py`:
one JSON object on stdout, exit 0 = ran, exit 2 = a guard refused. Three modules under
`.claude/skills/paper-writing/scripts/`: `paper_cli.py` (front door, argparse, refusal
classification), `paper_block.py` (marker grammar, locate, substitute, invariant),
`paper_scaffold.py` (the `paper/` tree). All file I/O binary.

This design is written against the spec's **The Safety Net Has No Git Behind It**. `main.tex`
is never tracked: `paper/*` is gitignored, `!paper/.gitkeep` alone travels, by the policy this
repository already applies to `proposals/` and `experiments/`. Nothing below is reasoned about
as if a commit history could recover a bad write.

## Architecture Decisions

### Decision: nothing goes into `_core/` in this phase

| Option | Tradeoff | Decision |
|---|---|---|
| New `_core/paperblock/` now | Right home *if* a second **skill** ever imports it; six later phases are one skill, so it buys nothing yet | Rejected |
| Add modules to `_core/implementation/` | `reachable_refusal_codes` (`tests/test_proposal_implementation.py`) takes **every** `.py` in that directory whole and demands each refusal be classified in `GATING_REFUSALS`. Paper codes would land in another skill's roster | Rejected — measured coupling |
| Own modules; import only `Refused` | `impl_refusals.py` defines and raises nothing, so it contributes no roster entry. One exception class forge-wide | **Chosen** |

`impl_position.splice`/`write_spliced`/`digest_bytes` are the same *shape*, not reusable code:
`splice`'s `block is None` branch pads with `\n\n`, which in LaTeX is the paragraph break this
change exists to prevent, and `write_spliced` hardcodes `POSITION_HOLDER_MOVED`. The forge
already carries both precedents — share a constant (`tests/forge_vocabulary.py`), copy a helper
with a fidelity test (`CopiedHelperFidelityTests`). **Revisit trigger**: the first second skill
to need block shapes; extraction is mechanical because the module holds no state.

### Decision: the pre-image is the only recovery, and its depth is tested

Because `main.tex` is untracked, the one-deep pre-image is not a convenience beneath a git
safety line — there is no line beneath it. Two consequences the implementation must carry:

- `scaffold` writes `paper/.gitkeep`, or the folder does not travel.
- The `paper/*` rule already covers `paper/.paper-writing/`, so the proposal's separate ignore
  line for it is redundant and is not added.

One level is sufficient **for this phase's scope** and its limit is asserted by a test, not left
to be discovered: after two successive writes, the pre-image holds the second write's predecessor
and nothing older is recoverable anywhere. Multi-step undo is a future capability, not an
extension of this mechanism — a deeper history is a ledger, and this skill has none.

### Decision: forge root by path arithmetic, never `git rev-parse`

`PAPER_OUTSIDE_REPOSITORY` resolves from `Path(__file__).resolve().parents[3]`. No subprocess,
works in a worktree, and keeps the whole engine free of shell. `--paper` and `--body` are
`.resolve()`d and required to stay under that root.

### Decision: sibling-skill SKILL.md length over `skill-creator`'s 180–450 token target

The in-repo precedents are thousands of lines and the task requires a sibling. Per the
sdd-design rule, the existing pattern wins; the deviation is recorded here.

## The substitution algorithm, and the name of each failure

| # | Step | Refuses |
|---|---|---|
| 1 | Resolve `--paper`; `--block` shape `[A-Za-z0-9._-]+` | `PAPER_OUTSIDE_REPOSITORY`, `PAPER_ABSENT`, `PAPER_NOT_A_DIRECTORY`, `BLOCK_ID_MALFORMED` |
| 2 | Read `main.tex` binary → `pre`, `pre_digest`; decode-check to locate marker lines | `TEX_UNDECODABLE` |
| 3 | Scan every marker line, pair them, order them | `MARKER_MALFORMED`, `BLOCK_UNPAIRED`, `BLOCK_DUPLICATED`, `BLOCK_NESTED`, `BLOCK_ABSENT` |
| 4 | Compare body digest against the begin marker's `sha256=` | `BLOCK_HAND_EDITED` — the only exit is the `--adopt` mode, step 4a |
| 5 | Supplied body carries no marker-prefixed line | `CONTENT_CARRIES_MARKER` |
| 6 | Build candidate; rewrite `sha256=` in place — 64 fixed hex chars, so no offset outside the marker line moves | — |
| 7 | **Byte-identity invariant on the candidate, in memory** | `SUBSTITUTION_NOT_LOCAL` |
| 8 | Re-read `main.tex`, compare to `pre_digest` (compare-and-swap precondition) | `TEX_MOVED` |
| 9 | Write the pre-image; then temp-in-same-dir + `os.replace` | — |

**Step 4a — the `--adopt` mode.** `--adopt` does *not* substitute. It rewrites the begin marker's
`sha256=` to match the on-disk body and leaves the body itself untouched, so a later `substitute`
no longer refuses. It therefore forbids `--body` (`ADOPT_BODY_CONFLICT`) and refuses
`NOTHING_TO_ADOPT` when the digest already matches. This is `materialize --adopt`'s exact shape:
a flag that switches the command into a distinct mode, guarded by a conflict refusal
(`MATERIALIZE_MODE_CONFLICT`) and an already-in-that-state refusal (`ALREADY_RECORDED`). Steps
6–9 still run, because the marker line is a byte change like any other and gets the same
invariant, the same precondition and the same atomic commit.

Step 8 precedes step 9 so a stale pre-image is never written. A crash between 9a and 9b leaves
pre-image == `main.tex`, which is harmless.

Step 7's invariant: `project(candidate) == project(pre)`, where `project(x)` **re-parses `x` from
scratch** and concatenates everything outside every block region — a different computation from
`prefix + new + suffix`, which is what lets it go red. It additionally asserts the id list and
order are identical and every *other* block's body and digest are unchanged.

## The safety net — exactly three layers, and no git

| Layer | What it alone catches | What it does not claim |
|---|---|---|
| **1. Byte-identity invariant, on candidate bytes in memory, before any write** | A region-boundary violation — bad bytes never exist on disk. **Primary and load-bearing**, not a supplement to a deeper history that does not exist. The only layer with no depth limit: refusing to write has no "how many steps back" question | Whether a correctly-scoped body is the one the caller wanted |
| **2. Same-directory temp + `os.replace`** | An interrupted process. `main.tex` is always fully pre-write or fully post-write, never torn | Nothing about content correctness. **Not recovery** |
| **3. One-deep pre-image** at `paper/.paper-writing/main.tex.prev` | The one case layer 1 structurally cannot reach: a correctly-scoped write whose content the caller did not want — a wrong body, or an `--adopt` taken by mistake. **The only recovery path once bytes reach disk** | Anything earlier than one step. A later successful write overwrites it, and nothing else in this system or in git retains the older state |

**Guards that protect but are not net layers.** The spec's roster already contains a protective
refusal outside the three (`BLOCK_HAND_EDITED`), so this is the spec's own category, not a fourth
layer smuggled in. `TEX_MOVED` joins it: a compare-and-swap on `pre_digest` immediately before
the write, refusing when the file changed between the read that computed the offsets and the
write that would apply them. It is `impl_position.write_spliced`'s `POSITION_HOLDER_MOVED`
precondition, and it is needed here for a measured reason — a second session editing a document
between two reads is a failure this forge has already recorded.

**Declared gap.** The marker digest covers block *bodies* only. A human edit to prose *between*
blocks is invisible to it, and layer 1 cannot see it either, because layer 1 compares the
candidate against the pre-image read in the same call and so carries that edit forward silently.
Prose outside every block belongs to the human and the engine never claims it. Rejected: a
whole-file sidecar digest — the second source of truth the proposal already rejected.

**Also rejected.** A clean-worktree requirement: meaningless, `main.tex` is untracked.
Write-then-verify-then-rollback: recovering is weaker than not writing, and a crash between the
two leaves the bad file. A multi-step undo ledger: a second state machine, and out of scope by
the spec.

## The seam with `the-contract-is-data-not-code`

| Owned here (shape) | Owned there (meaning) |
|---|---|
| marker grammar, region bounds, lexical id class, uniqueness, pairing, nesting | which ids exist, what each requires, section grouping, order |

The engine accepts any shape-valid id and asks nothing else; `open` places a block only where the
caller names (`--after <id>` or `--at-end`) and never derives a position. The contract layer hands
ids in and reads `status`'s block table out; the engine never opens `sections/`. **If the sibling
lands a compound id grammar**, joining with `.` or `-` needs zero change here; only a `/` join
forces a one-character widening of the lexical class, with the roster test unchanged. What must
never happen: validating an id against the nine-fact vocabulary — that would break the sibling's
own success criterion that an invented eleventh contract enters the plan with no code changed.

## CLI first slice

`scaffold` · `status` (read-only block table) · `open --block <id> (--after <id> | --at-end)` ·
`substitute --block <id> (--body <path|-> | --adopt)`.

The two positional choices on `open` and the two modes on `substitute` are each an argparse
`add_mutually_exclusive_group(required=True)`, matching how `implementation_cli.py` lets argparse
own what argparse can own. There is **no `--force`**: a flag that discarded the human's on-disk
text in favour of an incoming body is exactly the silent overwrite the digest exists to prevent.

| Class | Codes |
|---|---|
| invocation-defect | `PAPER_OUTSIDE_REPOSITORY`, `CONTENT_CARRIES_MARKER`, `ANCHOR_ABSENT`, `BLOCK_ID_MALFORMED`, `ADOPT_BODY_CONFLICT`, `NOTHING_TO_ADOPT` |
| work-state (each publishes a `resolve`) | `PAPER_ABSENT`, `PAPER_NOT_A_DIRECTORY`, `TEX_UNDECODABLE`, `BLOCK_ABSENT`, `BLOCK_DUPLICATED`, `BLOCK_UNPAIRED`, `BLOCK_NESTED`, `MARKER_MALFORMED`, `BLOCK_HAND_EDITED`, `TEX_MOVED`, `SUBSTITUTION_NOT_LOCAL` |

`open` on an id that already has a pair refuses `BLOCK_DUPLICATED`, per the spec — no separate
code. `ANCHOR_ABSENT` is invocation on the `SETTLE_TEXT_ABSENT` reasoning: a different `--after`,
or `--at-end`, clears it. `BLOCK_HAND_EDITED` is work-state on the `GATE_AUTHORIZATION_REQUIRED`
reasoning: naming `--adopt` is not the same as being able to fill it — a human must read their own
edit first and decide whether to keep it.

### Delta the spec should absorb

Five codes this design adds to the spec's twelve-row roster, each with the step that raises it:
`BLOCK_ID_MALFORMED` (step 1), `SUBSTITUTION_NOT_LOCAL` (step 7), `TEX_MOVED` (step 8),
`ADOPT_BODY_CONFLICT` and `NOTHING_TO_ADOPT` (step 4a). Surfaced rather than introduced quietly:
the roster test derives from source, so any code missing from the classification map goes red.

## Answering the three known risks

| Risk | Response |
|---|---|
| Bytes are not rendering | Every successful write emits `"rendering": "unproven"`. A field the reader receives, not prose nobody reads — the `interpreterMatch: null` idiom |
| A marker beside a blank line splits a paragraph | `status` reports per block `adjacency:{before,after}` ∈ `blank-line`/`text`/`marker`/`file-edge`. Reported, never refused — a between-paragraph block legitimately sits by blank lines. Hard rule: `open` never inserts a blank line it was not asked for |
| A hand edit surfaces weeks later | `status` reports `handEdited:[ids]` read-only, so it surfaces at the next *status*, not the next write. Residual: nothing forces anyone to run it |

## Testing Strategy

| Layer | What | How |
|---|---|---|
| Unit | marker grammar, every refusal | one fixture per code, all built in a `TemporaryDirectory` |
| Integration | CRLF mid-paragraph substitution | fixture written as explicit `b"...\r\n..."` **in code, never committed** — a checked-in CRLF file is normalized by editors and stops being a fixture |
| Identity | `project(pre) == project(post)` **and** `post != pre` **and** the block's body equals the new body | the second and third conjuncts stop a no-op write passing trivially |
| Safety net | pre-image holds the exact pre-write bytes; **after two successive writes it holds only the second's predecessor** | the declared one-deep limit asserted, not discovered |
| `--adopt` | digest updates, body byte-identical, a later `substitute` no longer refuses | proves adopt re-baselines rather than substituting |
| Mutation | M1 region one byte earlier, M2 text-mode open, M3 skip the digest compare | a helper copies the engine to a temp dir, patches it, **asserts the anchor matched exactly once and the bytes changed**, uses a unique module name and purges `__pycache__`, runs the named test in a subprocess, asserts non-zero exit. Recorded as executed |
| Roster | every refusal classified, every work-state code has a `resolve` builder | derived from source in the shape of `reachable_refusal_codes`, never hand-listed |

Stdlib only, so `tests/test_suite_collects.py` keeps covering the new modules for free.

## File Changes

| File | Action | Description |
|---|---|---|
| `.claude/skills/paper-writing/SKILL.md` | Create | Skill body, sibling idiom |
| `.claude/skills/paper-writing/scripts/paper_cli.py` | Create | Front door, refusal classification, JSON |
| `.claude/skills/paper-writing/scripts/paper_block.py` | Create | Grammar, locate, substitute, invariant |
| `.claude/skills/paper-writing/scripts/paper_scaffold.py` | Create | `paper/` tree, idempotent |
| `tests/test_paper_writing.py` | Create | Suite (one class per concern; no duplicate class names) |
| `.gitignore` | Modify | `paper/*`, `!paper/.gitkeep` |
| `paper/.gitkeep` | Create | So the folder travels |

## What Breaks — Producers and Products

| Class | Row |
|---|---|
| Producers | None. New capability; nothing imports these modules yet |
| Products | **No `paper/` exists on disk** (verified, 2026-09-10) — no `main.tex`, no markers, no pre-image. Zero instances of the new shape exist anywhere, so nothing already written becomes invalid |
| Products | `sections/*.md` — untouched by this change; the sibling owns them |
| Products | Forge guards: `tests/forge_vocabulary.py` scans every shipped file. The new SKILL.md and scripts must borrow no target word |

## Threat Matrix

`N/A` for every row: no routing, no shell, no subprocess in shipped code (mutation subprocesses
are test-side), no VCS automation (forge root by path arithmetic, not `git rev-parse`), no PR
automation, no executable-file classification. The one boundary that *is* real — caller-supplied
`--paper`/`--body` paths — is answered by `.resolve()` plus the `PAPER_OUTSIDE_REPOSITORY` guard
and gets its own RED test; it is not one of this matrix's rows and no row is manufactured for it.

## Migration / Rollout

No migration required. `scaffold` is idempotent by construction; a second run leaves the tree
byte-identical.

## Open Questions

- [ ] Artifact exceeds the 800-word sdd-design budget. The six mandated decision areas plus the
      breakage and threat sections do not compress below it without dropping a requirement.
