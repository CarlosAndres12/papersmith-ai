---
name: paper-writing
description: "Trigger: create or re-enter the paper/ tree, or write into a named block of paper/main.tex without touching anything else in the file. Stdlib-only, keyless, offline, fail-closed CLI (paper_cli.py) — scaffold, status, open, substitute."
---

# Paper Writing

`paper/main.tex` is edited one named block at a time, byte-for-byte. A block
is delimited by two LaTeX-comment marker lines carrying its id and a sha256
digest of its own body; this engine never rewrites a byte outside the block
it was asked to change, and proves that on every call rather than assuming
it — before a single byte reaches disk.

## What this skill ships today

Four verbs, wired into one front door (`scripts/paper_cli.py`):
`scaffold`, `status`, `open`, `substitute`. Block ids are opaque strings
here — shape only (`[A-Za-z0-9._-]+`), no meaning. Which ids exist, what
each one requires, and where in the document they belong is a sibling
change's business, not this skill's: the engine accepts any shape-valid id
and asks nothing else about it.

**Not shipped yet, on purpose.** This is one of nine planned build phases,
and only the first three landed here: scaffold, the block-substitution
engine, and this CLI wiring. Nothing about sections, an id vocabulary, or
document assembly exists in this skill — do not invent it, and do not read
its absence as a bug.

## Every read starts the same way

Run `status` before touching anything. It lists every block's id, digest and
byte region, and writes nothing:

```bash
.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py status
```

(Every verb accepts `--paper <dir>` to override the default `paper/` at the
repository root; omit it and the default is used.)

## The four verbs

| Verb | What it does | Refuses |
| --- | --- | --- |
| `scaffold` | Creates `paper/main.tex`, `paper/refs.bib`, `paper/Figures/`, `paper/.gitkeep` if absent. Idempotent — a second run never touches an existing byte, hand edits included | `PAPER_OUTSIDE_REPOSITORY`, `PAPER_NOT_A_DIRECTORY`, `SCAFFOLD_ENTRY_WRONG_TYPE` |
| `status` | Read-only block table: id, digest, byte region, per block | `PAPER_ABSENT`, `TEX_UNDECODABLE`, `MARKER_MALFORMED`, `BLOCK_DUPLICATED`, `BLOCK_UNPAIRED`, `BLOCK_NESTED` |
| `open --block <id> (--after <id> \| --at-end)` | Installs an EMPTY begin/end pair at the named position. Never writes content — the first write to a new block is always `open` then `substitute` | adds `BLOCK_DUPLICATED`, `ANCHOR_ABSENT`, `OPEN_POSITION_REQUIRED`, `OPEN_POSITION_CONFLICT` |
| `substitute --block <id> (--body <path\|-> \| --adopt)` | Replaces one block's body, or (`--adopt`) accepts the on-disk body as the new baseline without changing it | adds `BLOCK_ABSENT`, `BLOCK_HAND_EDITED`, `CONTENT_CARRIES_MARKER`, `NOTHING_TO_ADOPT`, `SUBSTITUTE_MODE_REQUIRED`, `ADOPT_BODY_CONFLICT`, `SUBSTITUTION_NOT_LOCAL`, `TEX_MOVED` |

Every JSON reply carries `"status": "ok"` (exit 0) or `"status": "refused",
"code": "<CODE>", "detail": "<why>"` (exit 2). A successful `substitute`
always adds `"rendering": "unproven"` — this engine has no LaTeX toolchain
and makes no claim the document compiles or that the change looks right on
the page. That is a separate, unbuilt capability.

**There is no `--force`.** Nothing here ever discards a human's on-disk text
in favor of an incoming body. The only exit from a hand-edited block is
`--adopt`, which re-baselines the digest and leaves the body untouched.

## Decision Gates

| Situation | Action |
| --- | --- |
| `status` reports `BLOCK_HAND_EDITED` | Read the on-disk body before deciding. `--adopt` accepts it as the new baseline; a plain `substitute` still refuses until you do |
| `open` refuses `ANCHOR_ABSENT` | The named `--after <id>` has no pair yet — `status` first, then either open that id or pick `--at-end` |
| `open` refuses `OPEN_POSITION_REQUIRED` / `OPEN_POSITION_CONFLICT` | Exactly one of `--after <id>` / `--at-end` is required, never zero, never both |
| `substitute` refuses `SUBSTITUTE_MODE_REQUIRED` / `ADOPT_BODY_CONFLICT` | Exactly one of `--body <path\|->` / `--adopt`, never zero, never both |
| `substitute` refuses `CONTENT_CARRIES_MARKER` | The replacement body itself contains a line starting `%% paper-writing block` — strip it, this grammar cannot nest |
| `substitute`/`open` refuses `SUBSTITUTION_NOT_LOCAL` | The in-memory candidate would have changed a byte outside the target block; nothing was written. This should never fire from ordinary use — report it as a defect if it does |
| `substitute`/`open` refuses `TEX_MOVED` | Something else wrote to `main.tex` between this call's read and its write. Re-run the command against the current file — never retry blind against stale offsets |
| Any command refuses `PAPER_ABSENT` | Run `scaffold` first |

## The safety net has no git behind it — three layers, read for what each alone catches

`paper/*` is gitignored except `.gitkeep` (`paper-scaffold` writes it), the
same policy this repository already applies to `proposals/` and
`experiments/`. `main.tex` is never tracked, so nothing below assumes a
commit history could recover a bad write — none exists.

1. **The byte-identity invariant**, checked on candidate bytes in memory
   before any write. Primary and load-bearing, not a supplement to a deeper
   history that does not exist — the only layer with no depth limit,
   because refusing to write has no "how many steps back" question. Proven
   by an executed mutation harness (`tests/test_paper_writing.py`,
   `MutationProofTests`), not asserted: a real subprocess patches the
   engine's own source, purges any cached bytecode, and confirms the
   corresponding guard test goes red.
2. **Same-directory temp file + `os.replace`**. Catches an interrupted
   process only: `main.tex` is always fully the pre-write or fully the
   post-write content, never torn. Says nothing about whether the
   post-write content is correct.
3. **A one-deep pre-image** at `paper/.paper-writing/main.tex.prev`. The
   only recovery path once bytes have reached disk — the one case layer 1
   cannot reach, because layer 1 only rejects a region-boundary violation,
   never a correctly-scoped write whose content nobody actually wanted.
   Recovers exactly the state immediately before the most recent write. A
   second successful write overwrites it; anything earlier than one step
   back has no recovery path anywhere in this system.

`BLOCK_HAND_EDITED` sits beside these three, not inside them: it protects a
human's on-disk text from being silently overwritten, which is a different
property from "the write stayed inside its own region."

**Declared gap.** The marker digest covers block bodies only. A hand edit to
prose between blocks is invisible to every layer above — `status` cannot
see it and neither can the byte-identity invariant, since both compare
against the pre-image read in the same call and carry that edit forward
silently. That prose belongs to the human; this engine never claims it.

## Binary I/O only

Every read and write of `main.tex` is binary, end to end. A universal-
newlines text-mode open would silently flatten every CRLF pair in the file
to LF outside the block being touched — exactly the corruption the
byte-identity invariant exists to catch, and a fixture with real CRLF bytes
(`tests/test_paper_writing.py`, `CRLFTests`) proves it round-trips
untouched.

## What "shape only" means for block ids

`[A-Za-z0-9._-]+`, nothing else. This skill never validates an id against a
list of what should exist, never derives ordering, and never opens anything
under `sections/`. A later change may join ids with `.` or `-` and this
engine needs zero changes; a `/`-joined id would need a one-character
widening of the shape class here, and nothing more. What must never
happen from this skill's own side: reasoning about what an id *means*.
That question belongs entirely to whatever composes this engine's `open`
and `substitute` calls.

## Refusal roster

Every refusal is `Refused(code, detail)`, classified invocation-defect
(clear it by changing the invocation alone) or work-state (something on
disk needs a human's decision first). The roster is derived from this
skill's own three scripts by walking their source
(`tests/test_paper_writing.py`, `reachable_paper_refusal_codes` —
the same shape `proposal-implementation`'s own roster derivation uses) and
held to it in both directions: nothing reachable ships unclassified, and
nothing classified here is unreachable. Adding a `Refused` anywhere in
`paper_cli.py`, `paper_block.py` or `paper_scaffold.py` without updating
`paper_cli.REFUSAL_CLASSIFICATION` fails that test on its own.
