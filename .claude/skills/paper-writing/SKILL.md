---
name: paper-writing
description: "Trigger: create or re-enter the paper/ tree, write into a named block of paper/main.tex without touching anything else in the file, read what sections/*.md declares about itself (ids, requirements, writing order), record/reopen a declaration or fact resolution and see the paper's overall plan, or resolve a citation's metadata against OpenAlex/Crossref/arXiv. Stdlib-only, keyless, fail-closed CLI (paper_cli.py) — scaffold, status, open, substitute, contract, readiness, order, declare, plan, resolve. Offline except `resolve`, which sits behind a config role that can be emptied."
---

# Paper Writing

`paper/main.tex` is edited one named block at a time, byte-for-byte. A block
is delimited by two LaTeX-comment marker lines carrying its id and a sha256
digest of its own body; this engine never rewrites a byte outside the block
it was asked to change, and proves that on every call rather than assuming
it — before a single byte reaches disk.

## What this skill ships today

Ten verbs, wired into one front door (`scripts/paper_cli.py`):
`scaffold`, `status`, `open`, `substitute` (the block-substitution engine),
`contract`, `readiness`, `order` (the section contract reader —
`the-contract-is-data-not-code`), `declare`, `plan` (the paper's own
decisions — `the-paper-carries-its-own-decisions`), and `resolve` (citation
metadata resolution — `no-claim-without-a-source-that-holds-it`). To the
substitution engine, block ids stay opaque strings — shape only
(`[A-Za-z0-9._-]+`), no meaning. The contract reader is what says which ids
exist, what each requires, and where in the document they belong, entirely
over in `sections/*.md`. `declare`/`plan` are what records the
operator-supplied declarations and fact resolutions those requirements
name, and reports where the paper stands against all of it in one
read-only call — see "The paper's own decisions" below.

**This CLI is no longer offline end to end.** `resolve` is the one path
that reaches the network — keyless, stdlib `urllib` only, against OpenAlex,
Crossref and arXiv, behind a `papersmith.yaml` role the operator can empty.
Every other verb remains exactly as offline as before; `resolve` refuses by
name (`RESOLVER_UNREACHABLE`, `DISCOVERY_UNAVAILABLE`, `RESOLVER_ROLE_EMPTY`)
rather than silently returning an empty result.

**Not shipped yet, on purpose.** Deriving a writing order and substituting a
block by id are two capabilities that exist side by side and are not yet
wired together: `order`'s output (a sequence of `<section>.<block>` ids) is
not fed into `open`/`substitute` automatically, and nothing here assembles
`paper/main.tex` from `sections/` on its own. Do not invent that wiring, and
do not read its absence as a bug — it is a later phase.

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

**Declared gap, narrowed.** The marker digest covers block bodies and, as of
`the-paper-carries-its-own-decisions`, the `declarations`/`provenance`
region bodies too — a hand edit to either region's own bytes refuses
(`DECLARATIONS_HAND_EDITED` / `PROVENANCE_HAND_EDITED`) rather than passing
silently. What remains outside every digest is ordinary prose: text that is
neither inside a block nor inside a region. A hand edit there is still
invisible to every layer above — `status` cannot see it and neither can the
byte-identity invariant, since both compare against the pre-image read in
the same call and carry that edit forward silently. That prose belongs to
the human; this engine never claims it.

## Binary I/O only

Every read and write of `main.tex` is binary, end to end. A universal-
newlines text-mode open would silently flatten every CRLF pair in the file
to LF outside the block being touched — exactly the corruption the
byte-identity invariant exists to catch, and a fixture with real CRLF bytes
(`tests/test_paper_writing.py`, `CRLFTests`) proves it round-trips
untouched.

## What "shape only" means for block ids

`[A-Za-z0-9._-]+`, nothing else. The block-substitution engine (`open`,
`status`, `substitute`) never validates an id against a list of what should
exist, never derives ordering, and never opens anything under `sections/`
itself — that reasoning is entirely the contract reader's, described below,
and the two sides only agree on the shape class, never on meaning. A later
change may join ids with `.` or `-` and the substitution engine needs zero
changes; a `/`-joined id would need a one-character widening of the shape
class there, and nothing more.

## Reading the section contract

Three more verbs, from `the-contract-is-data-not-code`: `contract`,
`readiness`, `order`. Each `sections/*.md` file now opens with a
`---`-fenced JSON header — `section`, `position`, optional `after`, and a
`blocks` list, each block declaring `id`, `requires_facts`,
`requires_declarations`, `citations`. The prose below the header is
unchanged; nothing here reads it for meaning.

| Verb | What it does | Refuses |
| --- | --- | --- |
| `contract [--file <path>]` | Validates the whole `sections/` corpus (flat id namespace, every `after` target resolved or reported dangling), or shows one file's parsed header with `--file` | `MALFORMED_HEADER`, `UNKNOWN_FACT`, `UNKNOWN_DECLARATION`, `UNKNOWN_CITATIONS_REGIME`, `ID_COLLISION`, `SECTIONS_OUTSIDE_REPOSITORY` |
| `readiness [--fact <id>]... [--declaration <id>]...` | Per-block `writable`/`blocked`, naming every still-missing fact and declaration separately | adds nothing beyond `contract`'s own guards |
| `order` | Derives the writing order from the block graph — `position`, declared block order, and every transcribed `after` edge; never the filename | adds `ORDER_CYCLE` |

`--sections <dir>` overrides the default `sections/` at the repository root
on all three, the same shape `--paper` already has.

**The three closed vocabularies** a header may draw from: ten
`requires_facts` ids (`formulation`, `contributions`, `problem-statement`,
`gap`, `dataset`, `experimental-design`, `implementation`, `results`,
`limitations`, `skeleton`), six `requires_declarations` ids (`author-roles`,
`grant-title`, `grant-code`, `repository-url`, `keyword-bounds`,
`classification-line`), and three `citations` regimes (`discovery`,
`resolution`, `none`). A value outside any of the three refuses
immediately — this is deliberately closed, not a convention.

**The block graph is authoritative; `position` is rendering order, not
writing order.** Two edges are transcribed in the shipped contracts' own
headers (`abstract` after `conclusions`, `introduction`'s `block-3` after
`related-work`), each carrying the exact sentence that states it. A third,
`title-and-keywords` after every section between `abstract` and
`back-matter`, is computed from `position` rather than enumerated — see
`specs/section-contract/spec.md`'s implementation note in
`openspec/changes/the-contract-is-data-not-code/` for why.

**Nothing here writes to `paper/main.tex`.** `order`'s output is a sequence
of block ids (`<section>.<block>`, e.g. `introduction.block-3`) — the same
shape `open`/`substitute` accept as `--block`. Wiring the two together
(open every block in derived order, substitute each as it's written) is a
later capability, not this one.

### Decision Gates (contract, readiness, order)

| Situation | Action |
| --- | --- |
| `contract` reports `danglingEdges` | An `after` target names an id absent from the corpus — not a defect on its own (deleting a contract is in scope), but confirm it is intentional before trusting `order`'s result |
| `order` refuses `ORDER_CYCLE` | Two or more blocks' `after` edges disagree about who comes first; the refusal names every block in the cycle — fix one of the transcribed sentences, it is never resolved by re-running |
| `readiness` reports a block `blocked` with an empty `missing_facts` | The block is waiting on a declaration only (an operator-supplied input like `repository-url`), not on any measurement |
| A header refuses `UNKNOWN_FACT` / `UNKNOWN_DECLARATION` / `UNKNOWN_CITATIONS_REGIME` | The file declares a value outside the closed vocabulary — fix the header, the vocabularies are not extended by editing the reader |

## The paper's own decisions: declarations and provenance

Two more regions live in `main.tex` alongside its blocks, holding JSON
bodies rather than prose — `declarations` and `provenance`. Neither is
readable by Phase 1's block scanner: both markers share the `%% paper-writing
<kind>` lead-in but never the literal token `block` in slot 3, so
`MARKER_PREFIX`'s own `startswith` check skips them (proven in
`tests/test_paper_decisions.py::DisjointGrammarTests`).

`declare` records two kinds of value: a `declaration` (one of the six
operator-input ids — `author-roles`, `grant-title`, `grant-code`,
`repository-url`, `keyword-bounds`, `classification-line`) or a `fact`
resolution (one of the ten fact ids). Recording either fixes it immediately
— a further `declare` on the same id refuses `DECLARATION_FIXED` until
`--reopen <id>` clears exactly that entry.

```bash
.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py declare \
    --declaration repository-url --value https://example.org/repo
.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py declare \
    --reopen repository-url
```

| Verb | What it does | Refuses |
| --- | --- | --- |
| `declare (--declaration <id> \| --fact <id> \| --reopen <id>) [--value <v>]` | Records a declaration or fact resolution, or clears one id's fixed state | `DECLARE_MODE_REQUIRED`, `DECLARE_MODE_CONFLICT`, `DECLARE_VALUE_REQUIRED`, `UNKNOWN_DECLARATION`, `UNKNOWN_FACT`, `DECLARATION_FIXED`, `DECLARATIONS_HAND_EDITED` |

`substitute` also accepts an optional `--contract <path>`: it changes no
byte of what gets written to the block, only records — in the `provenance`
region — the contract file's sha256 digest as read at that exact moment and
the declarations region's current generation. A block substituted without
`--contract` is reported `unprovenanced`, never assumed current.

```bash
.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py substitute \
    --block intro --body body.tex --contract sections/introduction.md
```

`plan` reads all three concerns — guidance classification, declaration/fact
fill state, and provenance state (`current`, `drifted`, `unprovenanced`) —
in one call, and writes nothing anywhere:

```bash
.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py plan
```

| Verb | What it does | Refuses |
| --- | --- | --- |
| `plan [--guidance <dir>] [--sections <dir>]` | Read-only aggregation: guidance classes, declaration/fact fill state, per-block provenance state | `PAPER_ABSENT`, `TEX_UNDECODABLE`, marker/region grammar codes, `GUIDANCE_OUTSIDE_REPOSITORY`, `UNKNOWN_GUIDANCE_CLASS`, `MALFORMED_GUIDANCE_MARKER`, `SECTIONS_OUTSIDE_REPOSITORY`, `MALFORMED_HEADER`, `ID_COLLISION` (no new codes of its own) |

**Reopening a fact or declaration invalidates the blocks that named it.**
`plan` reads the `sections/` corpus (`--sections` overrides it, same shape
as the other three corpus-reading verbs) to derive, per block, whether any
fact or declaration its own contract names was declared or reopened after
that block's own provenance was written — `declare`/`--reopen` both bump
a record's own generation counter; a block whose recorded generation is
now behind is reported `drifted`, the same state name a contract-byte edit
already used. No new state, no new field on-disk carries a literal "stale"
flag — this is a derived read-time property, recomputed on every `plan`
call from `paper_declarations.affected_blocks` (the reopen-scan function)
and the generation each record was last touched at, never from write
order.

**`guidance/` classifies as `style-reference` or `evidence`, from a
per-folder marker only — never a folder's name.** A folder with no
`.paper-writing.json` reports `unclassified`, including every folder on a
fresh clone; that is designed behavior, not a fault.

**No `--adopt` exists for either region.** A hand-edited `declarations` or
`provenance` region refuses (`DECLARATIONS_HAND_EDITED` /
`PROVENANCE_HAND_EDITED`) and writes nothing — unlike a block body, a
region is a decision the machine reads back as authority, and adopting a
hand edit would launder an unreviewed change into "what was decided."

## No claim without a source that holds it: `resolve`

Search comes first, always — but search itself runs through the agent's own
MCP (`discovery` role, `.mcp.json`), never through this CLI. `resolve` is the
CLI-side half: given an identifier and a named connector, it fetches
metadata over stdlib `urllib`, keyless, and caches the result on disk keyed
by its own digest.

```bash
.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py resolve \
    --identifier 10.1000/example --resolver openalex --role resolution
```

| Verb | What it does | Refuses |
| --- | --- | --- |
| `resolve --identifier <id> --resolver {openalex,crossref,arxiv} [--role <role>]` | Resolves one identifier's metadata through one named connector and caches it | `PAPERSMITH_CONFIG_UNREADABLE`, `UNKNOWN_ROLE`, `DISCOVERY_UNAVAILABLE`, `RESOLVER_ROLE_EMPTY`, `RESOLVER_UNREACHABLE`, `IDENTIFIER_UNRESOLVED` |

**Every role can be emptied in `papersmith.yaml`.** An empty `resolution`
role refuses `RESOLVER_ROLE_EMPTY` rather than silently resolving nothing;
an unreachable connector refuses `RESOLVER_UNREACHABLE` with a non-zero
exit, never a silent empty result. `contact` (a courtesy `mailto` for
OpenAlex's polite pool) is read from `papersmith.yaml`, never hardcoded, and
is never a secret — leaving it empty just means requests go out without it.

**No verdict lives in this CLI.** Whether a source's text actually supports
a claim is a judgment the agent makes by reading a located span
(`EvidenceSpan.locate`, `paper_evidence.py`) — this module only ever proves
a span is real, byte for byte; it never decides what the span means.

**Observing before declaring: the `insumos-observer` agent.** For the five
facts an outside observer can check against evidence (`formulation`,
`dataset`, `experimental-design`, `implementation`, `results`), this skill
delegates to the `insumos-observer` agent — it reports satisfaction and
evidence, never a value, and never calls `declare` itself.

**Measure this before delegating:** confirm `proposals/`, `experiments/`
and the target implementation repository are readable; an agent asked to
observe an unreadable source cannot distinguish "not yet true" from "cannot
be checked."

## Refusal roster

Every refusal is `Refused(code, detail)`, classified invocation-defect
(clear it by changing the invocation alone) or work-state (something on
disk needs a human's decision first). The roster is derived from every
module `paper_cli.py` itself imports, by walking their source
(`tests/test_paper_writing.py`, `reachable_paper_refusal_codes` — the same
shape `proposal-implementation`'s own roster derivation uses) and held to
it in both directions: nothing reachable ships unclassified, and nothing
classified here is unreachable. The module list is derived too
(`paper_cli_imported_modules`), from `paper_cli.py`'s own `import`
statements rather than a hand-listed tuple — a hand-listed tuple went stale
silently once, the day this skill grew past its first three scripts, and
every refusal in the two new modules shipped unrostered until a later
change re-derived it. Adding a `Refused` anywhere in a module `paper_cli.py`
imports, without updating `paper_cli.REFUSAL_CLASSIFICATION`, fails that
test on its own — and so does adding a module `paper_cli.py` never imports
but expecting its refusals to be reachable through the front door.
