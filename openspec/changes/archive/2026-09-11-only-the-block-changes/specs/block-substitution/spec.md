# Block Substitution Specification

## Purpose

Delimits, locates, replaces and refuses over named blocks inside
`paper/main.tex`, byte-for-byte, and exposes `open`, `substitute`, `status`
as CLI verbs. Block ids are opaque strings here — shape only, no
semantics; their grammar and ordering belong to a sibling change.

## Requirements

### Requirement: Marker Grammar

A block is delimited by two LaTeX-comment marker lines:

```
%% paper-writing block <id> begin sha256=<hex>
<body>
%% paper-writing block <id> end
```

`<id>` MUST match `[A-Za-z0-9._-]+` (shape only). `<hex>` MUST be a
lowercase 64-character sha256 hex digest. A line matching the marker
prefix (`%% paper-writing block`) that does not match this exact grammar
MUST refuse `MARKER_MALFORMED` (work-state), naming the offending line.

#### Scenario: Well-formed pair parses

- GIVEN `main.tex` contains a begin marker for `intro` with a valid digest
  and a matching end marker
- WHEN `status` runs
- THEN block `intro` is reported with its digest

#### Scenario: Malformed marker line refuses

- GIVEN a line `%% paper-writing block intro begin` with no `sha256=`
- WHEN any block command runs
- THEN it refuses `MARKER_MALFORMED` naming the line

### Requirement: Block Region Is Marker-Line-Bounded

The block's byte region MUST start at the first byte of the begin-marker
line and end at the last byte of the end-marker line's own line
terminator. No byte before the begin marker's first byte or after the end
marker's terminator belongs to the region.

#### Scenario: Region excludes the preceding newline

- GIVEN a preceding line ending in its own newline, immediately followed
  by a begin marker
- WHEN the region is computed
- THEN the newline that ends the preceding line is outside the region

### Requirement: open Installs an Empty Pair, Never Creates Content

`open <id> --after <anchor-id> | --at-end` MUST insert an empty begin/end
pair for `<id>` at the named position. Ordering is caller business, never
the engine's. `open` MUST refuse `BLOCK_DUPLICATED` (work-state) if
`<id>` already has a pair, and `ANCHOR_ABSENT` (invocation-defect) if
`--after <anchor-id>` names an id with no existing pair.

#### Scenario: Open after an anchor

- GIVEN block `a` exists and `b` does not
- WHEN `open b --after a` runs
- THEN an empty pair for `b` appears immediately after `a`'s end marker,
  and every byte before the insertion point is unchanged

#### Scenario: Anchor missing

- GIVEN no block named `missing` exists
- WHEN `open b --after missing` runs
- THEN it refuses `ANCHOR_ABSENT` and writes nothing

### Requirement: substitute Never Creates

`substitute <id> <body>` MUST refuse `BLOCK_ABSENT` (work-state) when no
pair for `<id>` exists. It MUST NOT create one. The first write to a new
block is always `open` then `substitute`, so rewrite has exactly one code
path.

#### Scenario: Substitute on a missing block

- GIVEN no block named `results` exists
- WHEN `substitute results <body>` runs
- THEN it refuses `BLOCK_ABSENT` and writes nothing

### Requirement: Substitution Body May Not Carry a Marker

The system MUST refuse `CONTENT_CARRIES_MARKER` (invocation-defect) when
the supplied replacement body contains a line matching the marker prefix.

#### Scenario: Body contains a marker-shaped line

- GIVEN a replacement body containing a line starting
  `%% paper-writing block`
- WHEN `substitute` runs
- THEN it refuses `CONTENT_CARRIES_MARKER` and writes nothing

### Requirement: The Byte-Identity Invariant

After a successful `substitute` or `open`, every byte of `main.tex`
outside the affected block's region (or insertion point) MUST be
identical to the pre-write bytes. A candidate that would violate this
MUST NOT reach disk — checked on candidate bytes in memory before any
write.

#### Scenario: Only the named block changes

- GIVEN `main.tex` with blocks `a` and `b` plus surrounding prose
- WHEN `substitute a <new body>` runs
- THEN every byte outside `a`'s region — preamble, block `b`, trailing
  content — is byte-for-byte identical to before

#### Scenario: A violating candidate never reaches disk

- GIVEN a substitution whose candidate bytes would alter a byte outside
  the target region
- WHEN the in-memory check runs before write
- THEN no write occurs and the prior `main.tex` on disk is unchanged

### Requirement: Independent Byte-Identity Verification

Verification MUST re-read the written file from disk, strip every block
region by re-parsing markers, and compare that projection against the
same projection of the pre-image — a computation independent of the
substitution's own `prefix + new + suffix` construction, so it can fail.
Each mutation below MUST make its corresponding guard test fail (red):

- **M1**: shifting the region start one byte earlier, consuming the
  preceding newline, MUST fail the byte-identity guard.
- **M2**: opening `main.tex` in text mode against a CRLF fixture MUST
  fail the byte-identity guard (CRLF outside the block rewritten to LF).
- **M3**: skipping the digest comparison MUST fail the hand-edit guard (a
  hand-edited block is silently accepted instead of refused).

#### Scenario: M1 is caught

- GIVEN the region-start computation is mutated one byte earlier
- WHEN independent verification runs
- THEN the byte-identity test fails

#### Scenario: M2 is caught

- GIVEN a CRLF fixture and a text-mode open of `main.tex`
- WHEN substitution and verification run
- THEN the byte-identity test fails because CRLF outside the block was
  rewritten to LF

#### Scenario: M3 is caught

- GIVEN the digest comparison is skipped
- WHEN a hand-edited block is substituted over
- THEN the test asserting `BLOCK_HAND_EDITED` fires and fails

### Requirement: Binary I/O Only

All reads and writes of `main.tex` MUST use binary mode end to end. The
system MUST NOT open the file in text mode at any point.

#### Scenario: CRLF fixture round-trips untouched

- GIVEN `main.tex` uses CRLF line endings throughout, including inside a
  mid-paragraph block
- WHEN `substitute` replaces one block's body
- THEN every CRLF byte pair outside the substituted region is unchanged,
  byte for byte

### Requirement: Hand Edit Is Detected, Not Overwritten

The begin marker's `sha256=` MUST equal the digest of the on-disk body as
this engine last wrote it. A mismatch MUST refuse `BLOCK_HAND_EDITED`
(work-state), naming both the expected and the found digest. The only
exit is `--adopt`, which accepts the on-disk body as the new baseline and
rewrites the digest without altering the body. No `--force` exit exists:
nothing here ever discards the human's on-disk text in favor of an
incoming replacement.

#### Scenario: Hand edit refuses

- GIVEN a block whose on-disk body was edited outside this engine
- WHEN `substitute` targets that block
- THEN it refuses `BLOCK_HAND_EDITED` naming both digests, and writes
  nothing

#### Scenario: --adopt clears it

- GIVEN the same hand-edited block
- WHEN `--adopt` runs against it
- THEN the digest updates to match the on-disk body, the body itself is
  untouched, and a later `substitute` no longer refuses

### Requirement: Refusal Roster

Every refusal MUST use `Refused(code, detail)` and be classified
invocation-defect or work-state:

| Code | Condition | Class |
|---|---|---|
| `PAPER_ABSENT` | `paper/` does not exist | work-state |
| `PAPER_NOT_A_DIRECTORY` | `paper/` exists as a non-directory | work-state |
| `PAPER_OUTSIDE_REPOSITORY` | `--paper` resolves outside the repo root | invocation-defect |
| `TEX_UNDECODABLE` | `main.tex` bytes cannot be decoded to locate marker lines | work-state |
| `BLOCK_ABSENT` | `substitute` targets an id with no pair | work-state |
| `BLOCK_DUPLICATED` | two begin (or two end) markers share one id | work-state |
| `BLOCK_UNPAIRED` | a begin marker has no matching end (or the reverse) | work-state |
| `BLOCK_NESTED` | a begin marker appears before its predecessor's matching end | work-state |
| `MARKER_MALFORMED` | a marker-prefixed line fails the exact grammar | work-state |
| `BLOCK_HAND_EDITED` | on-disk digest mismatches the recorded one | work-state |
| `CONTENT_CARRIES_MARKER` | supplied body contains a marker-shaped line | invocation-defect |
| `ANCHOR_ABSENT` | `--after <id>` names an id with no pair | invocation-defect |
| `BLOCK_ID_MALFORMED` | a supplied block id fails the exact id grammar | invocation-defect |
| `OPEN_POSITION_REQUIRED` | `open` runs with no position flag | invocation-defect |
| `OPEN_POSITION_CONFLICT` | `open` runs with more than one position flag | invocation-defect |
| `SUBSTITUTE_MODE_REQUIRED` | `substitute` runs with no body source | invocation-defect |
| `ADOPT_BODY_CONFLICT` | `substitute` supplies a body alongside `--adopt` | invocation-defect |
| `NOTHING_TO_ADOPT` | `--adopt` runs against a block whose on-disk digest already matches the recorded one | invocation-defect |
| `SUBSTITUTION_NOT_LOCAL` | a write would alter bytes outside the target block | work-state |
| `TEX_MOVED` | `main.tex` changed identity between read and write | work-state |

#### Scenario: Duplicated id

- GIVEN two begin markers both named `intro`
- WHEN any block command runs
- THEN it refuses `BLOCK_DUPLICATED` naming both line locations

#### Scenario: Nested blocks

- GIVEN a begin marker for `a` followed by a begin marker for `b` before
  `a`'s end marker
- WHEN any block command runs
- THEN it refuses `BLOCK_NESTED`

#### Scenario: Unpaired marker

- GIVEN a begin marker for `a` with no end marker anywhere after it
- WHEN any block command runs
- THEN it refuses `BLOCK_UNPAIRED`

### Requirement: status Reports the Block Table

`status` MUST list every parsed block id, its digest and its region,
without writing to `main.tex`.

#### Scenario: Status on a well-formed file

- GIVEN two well-formed blocks
- WHEN `status` runs
- THEN both ids, their digests and their line ranges are reported and
  `main.tex` is unchanged

### Requirement: The Safety Net Has No Git Behind It

`main.tex` is never tracked by git — `paper/*` is gitignored except
`.gitkeep` (see `paper-scaffold`), by the same policy this repository
already applies to `proposals/` and `experiments/`. No layer below may be
specified or reasoned about as if a commit history could recover a bad
write; none exists. The net is exactly three layers, and each MUST be
read for what it alone catches:

1. **The byte-identity invariant, checked on candidate bytes in memory
   before any write** (see above) is the PRIMARY and load-bearing
   defense, not a belt-and-braces addition to a deeper history layer that
   does not exist. It structurally prevents a write that would corrupt
   content outside the target block's region from ever reaching disk.
   This is the only one of the three with no depth limit: refusing to
   write has no "how many steps back" question.
2. **Atomic same-directory temp file + `os.replace`** catches an
   interrupted process, nothing else: it guarantees `main.tex` is always
   either fully the pre-write or fully the post-write content, never torn.
   It says nothing about whether the post-write content is correct.
3. **A one-deep pre-image** at `paper/.paper-writing/main.tex.prev`
   (gitignored) is the ONLY recovery path once bytes have already reached
   disk — the one case layer 1 cannot reach, because layer 1 only rejects
   region-boundary violations, never a correctly-scoped write whose
   content the caller did not actually want (a wrong body, or an
   `--adopt` taken by mistake). It recovers exactly the state immediately
   before the most recent write; a later successful write overwrites it,
   so anything earlier than one step back has no recovery path anywhere
   in this system.

One level MUST be treated as sufficient for this phase and MUST NOT be
silently exceeded: it exists to reverse the single most recent write, not
to serve as a content history. Multi-step undo, if ever needed, is a new
capability — not an extension of this pre-image — and is out of this
phase's scope.

#### Scenario: Interrupted write leaves no torn file

- GIVEN a write is interrupted before `os.replace` completes
- WHEN `main.tex` is read afterward
- THEN it holds either the pre-write or the post-write content in full,
  never a mix of both

#### Scenario: Pre-image is kept

- GIVEN a successful substitution
- WHEN `paper/.paper-writing/main.tex.prev` is read afterward
- THEN it holds exactly the bytes `main.tex` had immediately before that
  substitution

#### Scenario: Only the immediately-prior state is recoverable

- GIVEN two successive successful substitutions, the second following the
  first
- WHEN `paper/.paper-writing/main.tex.prev` is read after the second
- THEN it holds the state immediately before the second substitution
  only; the state before the first substitution is not recoverable
  through this mechanism or through git, because neither retains it
