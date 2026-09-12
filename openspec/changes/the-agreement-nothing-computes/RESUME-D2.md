# Resume point — Phase D2, paused mid-phase

**Paused**: 2026-09-12, deliberately, at a clean worktree. Not a failure.
**HEAD at pause**: `f07e786` — `git status --porcelain` empty, verified at the pause.

## Why the pause is safe here

Every unit D2 finished is a commit. Nothing was in flight: the pause was taken
between a committed unit and the next command, not during an edit. The resume
point is the task list, not an agent's memory.

## What landed — nine commits, `2f70434`..`f07e786`

| Commit | Unit |
|---|---|
| `2f70434` | RED: `cross_citation`'s required, nullable tier |
| `6c0796d` | resolve `documents[N].cross_citation` |
| `3212aa2` | declare `cross_citation` on every shipped and fixture document |
| `7525a27` | the sibling's X4 scratch fixture declares `cross_citation` |
| `28d92ed` | RED: `crossing_state`'s four-membership unit matrix |
| `22f742d` | `crossing_state`, `checkReferenceIntegrity` one document over |
| `9b01534` | the second corpus's own crossing axis |
| `c4dc0f5` | `[claims:N]` must never join `cites()`, and the form documented |
| `f07e786` | RED: Z6 — `crossing_state`'s declared must read the target's locator |

## What is NOT done

- **`tasks.md` Phase 2 check-offs: zero of 15.** The code landed; the artifact
  was not updated. D1 did its check-off in a later `docs(...)` commit, so this
  is the same ordering, interrupted before that commit — **not** evidence that
  the units are missing. Re-derive each `[x]` from the commits above rather
  than trusting this note.
- **Task 2.7a** — `tests/seal/`'s 28 digests asserted byte-identical *across the
  sibling edit specifically*, as its own check, never folded into the phase-end bar.
- **The phase gate, none of it run**: both seals, `npm test`, the full Python
  suite, the measured diff size, the refusal pin, and the command proving
  `reference-experimental.ts` byte-unchanged.

The agent's own next action at the moment of the pause was to run the full
suite as a single instance. That run costs ~616s on this machine (measured at
D1), which is why the pause was taken before it rather than during it.

## How to resume

Launch `sdd-apply` scoped to **Phase 2 only**, with the D2 brief, plus:

1. Re-derive which 2.x tasks the nine commits already satisfy — **measure, do
   not trust this table.** Six inherited counts have been measured false in
   this change alone.
2. Finish the remaining 2.x units, then the phase gate.
3. `strict_tdd` still holds: RED committed, then GREEN committed. D1 deviated
   here and it was recorded; D2's commits above show the contract restored
   (`2f70434`, `28d92ed`, `f07e786` are RED commits in their own right).

## Bars unchanged

`tests/seal/` 28 digests (29 keys) byte-identical · `tests/experiments_seal/`
27 case digests, any mover **named before regenerating** · `npm test` 595/595 ·
Python `Ran >= 3014`, `OK (skipped=6)` — **`skipped=6` must not move**.
