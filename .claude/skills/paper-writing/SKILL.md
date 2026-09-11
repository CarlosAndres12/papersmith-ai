---
name: paper-writing
description: "Trigger: create or re-enter the paper/ tree, write into a named block of paper/main.tex without touching anything else in the file, read what sections/*.md declares about itself (ids, requirements, writing order), record/reopen a declaration or fact resolution and see the paper's overall plan, resolve a citation's metadata against OpenAlex/Crossref/arXiv, rebuild refs.bib from cached resolved metadata, validate a citation's verdict and placement before writing a block, judge an already-drafted, already-audited block against its own evidence set and contract before it ever reaches main.tex, compile a standalone diagram and prove it against the contract's own figure: obligation, or check whether the cross-section couplings (contribution list, chain, the gap, diagram disjointness, future-work/limitations), citation integrity and contract currency still hold. Stdlib-only, keyless, fail-closed CLI (paper_cli.py) — scaffold, status, open, substitute, contract, readiness, order, declare, plan, resolve, bib build, validate, write, render, place, verify. Offline except `resolve`, which sits behind a config role that can be emptied; `render` is the one other path that reaches outside this process, invoking `latexmk` as a child."
---

# Paper Writing

`paper/main.tex` is edited one named block at a time, byte-for-byte. A block
is delimited by two LaTeX-comment marker lines carrying its id and a sha256
digest of its own body; this engine never rewrites a byte outside the block
it was asked to change, and proves that on every call rather than assuming
it — before a single byte reaches disk.

## What this skill ships today

Sixteen verbs, wired into one front door (`scripts/paper_cli.py`):
`scaffold`, `status`, `open`, `substitute` (the block-substitution engine),
`contract`, `readiness`, `order` (the section contract reader —
`the-contract-is-data-not-code`), `declare`, `plan` (the paper's own
decisions — `the-paper-carries-its-own-decisions`), `resolve`,
`bib build`, `validate` (citation resolution, a sourced bibliography, and
the verdict/placement gate — `no-claim-without-a-source-that-holds-it`),
`write` (evidence-bound drafting, contract audit and the style-leak proof —
`the-writer-may-assert-only-what-it-was-given`), `render`/`place` (a
diagram that compiles or says why, the repair-budget ledger, and the
data-figure boundary — `a-diagram-that-compiles-or-says-why`), and `verify`
(read-only coupling verification, citation integrity and contract currency —
`the-couplings-hold-or-they-do-not`). To the substitution engine, block ids
stay opaque strings — shape only (`[A-Za-z0-9._-]+`), no meaning. The
contract reader is what says which ids exist, what each requires, and where
in the document they belong, entirely over in `sections/*.md`.
`declare`/`plan` are what records the operator-supplied declarations and
fact resolutions those requirements name, and reports where the paper
stands against all of it in one read-only call — see "The paper's own
decisions" below.

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

`bib build` rebuilds `paper/refs.bib` WHOLE, sorted, exclusively from
cached resolved metadata — never appended, never hand-typed:

```bash
.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py bib build
```

| Verb | What it does | Refuses |
| --- | --- | --- |
| `bib build` | Rebuilds `refs.bib` from every block's cached, resolved evidence records; checks both `\cite{}`/entry directions | `ENTRY_UNSOURCED`, `CITE_WITHOUT_ENTRY`, `ENTRY_WITHOUT_CITE` |

A hand-typed entry (no `resolver`/`metadata_digest` provenance) refuses
`ENTRY_UNSOURCED` before a single byte of `refs.bib` is rewritten — checked
entirely offline, since the provenance is either cached already or it is not.

`validate` is the single gate: submit one judged verdict for one claim
(the agent's own reading of a located span decides `holds` vs
`does-not-hold`; omitting `--quote`/`--source-md` records `insufficient`),
then check the block's round-bounded satisfaction, and write only when
every claim the block has evidence for holds:

```bash
.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py validate \
    --block intro.claim --claim "the dataset holds 12000 labeled examples" \
    --quote "holds 12,000 labeled examples" --source-md guidance/06-introduction/paper1.md \
    --verdict holds --cite-key smith2024 --body body.tex
```

| Verb | What it does | Refuses |
| --- | --- | --- |
| `validate --block <id> [--claim ... --quote ... --source-md ... --verdict holds\|does-not-hold] [--body <path\|->] [--sentence <json>] [--regime <r> \| --section-md <path>]` | Optionally records one evidence submission, then reports `pending`/`satisfied`/`written`, or refuses on exhaustion | `SPAN_NOT_IN_SOURCE`, `VALIDATE_VERDICT_REQUIRED`, `EVIDENCE_EXHAUSTED`, `CITATION_MULTI_CLAIM_SENTENCE`, `CITATION_NOUN_PHRASE`, `CITATION_NOT_AT_SENTENCE_END`, `CITATION_DETACHED_FROM_OBJECT`, `CITATION_UNDER_NONE_REGIME`, `CONTRACT_HEADER_ABSENT` |

`--section-md <path>` reads `--block`'s `citations` regime straight from an
already-headered `sections/*.md` file, instead of typing `--regime` by
hand; an explicit `--regime` always wins when both are given.

**Three search rounds per block, then exhaustion.** `insufficient` fails a
claim exactly as `does-not-hold` does — never a soft `holds`. On the third
round with claims still unsupported, `validate` refuses
`EVIDENCE_EXHAUSTED` naming every unsupported claim, and
`paper_block.substitute` is never reached: the write sits strictly inside
the all-satisfied branch.

**Placement dispatches on regime, never one universal rule.** Under
`discovery`, a citation must close the sentence it supports and a
noun-phrase citation is prohibited; under `resolution`, a citation attaches
to the object it credits wherever that sits, and a noun-phrase citation is
exactly what that asks for; under `none`, no citation is allowed at all.

**Observing before declaring: the `insumos-observer` agent.** For the five
facts an outside observer can check against evidence (`formulation`,
`dataset`, `experimental-design`, `implementation`, `results`), this skill
delegates to the `insumos-observer` agent — it reports satisfaction and
evidence, never a value, and never calls `declare` itself.

**Measure this before delegating:** confirm `proposals/`, `experiments/`
and the target implementation repository are readable; an agent asked to
observe an unreadable source cannot distinguish "not yet true" from "cannot
be checked."

## The writer may assert only what it was given: `write`

Three channels feed one block's draft: **contract** (the block's own prose,
verbatim), **evidence** (the block's evidence set — resolved, cached
records, never invented), and **style** (whole equivalent blocks from
`style-reference`-classed `guidance/` folders — empty is valid, meaning
"no style channel at all"). Two audits check the result before it ever
reaches `main.tex`: **evidence-bound drafting**, which reconciles a binding
map against the emitted LaTeX so an unbound assertion is *detected*, never
merely instructed against; and **contract audit**, which evaluates the
contract's own `## Disqualifiers` bullets verbatim against the draft. `write`
is the judge that sequences both — **it never drafts and never audits
anything itself.**

```bash
.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py write \
    --section 01-materials-and-methods --block mm-proposal \
    --draft draft.json --audit audit.json --evidence evidence.json
```

| Verb | What it does | Refuses |
| --- | --- | --- |
| `write --section <id> --block <id> --draft <path> --audit <path> [--evidence <path>] [--style <path>] [--guidance <dir>] [--transcript <path>]` | Reconciles an already-drafted, already-audited block against its real contract, evidence set and mode; substitutes on success, reports fired bullets on a first failure, refuses on exhaustion. `--style` records the sampler's account as `R` and runs the eight-token tripwire against the styled draft before `substitute` | `MODE_ABSENT`, `EVIDENCE_SET_REQUIRED`, `UNBOUND_SENTENCE`, `BINDING_ORPHANED`, `EVIDENCE_ID_UNKNOWN`, `FACT_NOT_LICENSED`, `STRUCTURAL_CARRIES_CLAIM`, `MODE_VIOLATION`, `DISQUALIFIERS_ABSENT`, `VERDICT_MISSING`, `VERDICT_BULLET_UNKNOWN`, `AUDIT_EXHAUSTED`, `SPAN_NOT_IN_SOURCE`, `STYLE_OVERLAP` |

### The shuttle procedure — this CLI never invokes an agent

No module under `scripts/` imports `subprocess`, `os.system`, `os.popen`,
`os.exec*`, or `multiprocessing` (an AST scan asserts it, with exactly one
named, currently-unused exception reserved for a sibling skill's own
`latexmk` integration — see `tests/test_paper_writing.py`,
`NoSubprocessScanTests`). `write` cannot run unattended, by construction:

1. The orchestrating agent (you) assembles the four redactor inputs and
   delegates to the `redactor` agent, which returns
   `{"latex": ..., "bindings": [...]}`. Write that JSON to a file.
2. The orchestrating agent also delegates to the `contract-auditor` agent
   and writes its JSON verdict envelope to a second file.
3. Run `write --draft <path> --audit <path>`. On `"status": "written"` the
   block is done. On `"status": "audit-fired"`, hand the returned `fired`
   bullets and spans back to the redactor as explicit feedback and re-draft
   **exactly once** — a third submission under the same contract/evidence/
   mode refuses `AUDIT_EXHAUSTED`.

**Measure this before delegating (redactor/contract-auditor):** confirm the
contract's own `sections/*.md` file and its evidence set are both already
readable; an agent asked to draft or audit against a source it cannot read
cannot distinguish "nothing to cite" from "cannot be checked."

The style channel follows the same shuttle shape: the orchestrating agent
delegates to the `style-sampler` agent per `style-reference`-classed
`guidance/` folder, and its verified, recorded account becomes `R` — the
only material any later overlap check may compare a styled draft against.
An all-`noEquivalent` style set reports the style channel `unmeasured`
(`paper_write.style_channel_report`), not a silent pass: an unmeasured
register/overlap check proves nothing about whether style leaked.

**Measure this before delegating (style-sampler):** confirm the guidance
registry has already classed at least one folder `style-reference`; an
agent asked to sample against a registry that classes nothing cannot
distinguish "no style channel wanted" from "nothing to sample yet."

### `mode`: how a block is licensed to argue

`sections/*.md` headers may now declare a `mode` — `transposition` or
`argument` — at section level (the default) or block level (overriding
it), transcribed from the contract's own prose exactly like an `after`
edge (`{"value": ..., "source": {"file", "quote"}}`). A header declaring
neither is schema-valid — none of the ten shipped contracts carry `mode`
yet — but `write` refuses `MODE_ABSENT` rather than assuming one for any
block it resolves to `None`.

`transposition` admits only `fact`/`structural`/`resolution`-class
evidence bindings — a block reporting an existing result. `argument`
additionally admits `discovery`-class evidence — a block making a claim
about the field. Binding a `discovery`-class record under `transposition`
refuses `MODE_VIOLATION`.

### The style-leak proof: register rises, overlap does not

Style must not carry content. Proven, not asserted, by drafting one block
three times against identical contract, evidence and mode — twice with an
empty style set (`A`, `B`) and once with the real one (`S`) — then checking
two measurements:

- **Register distance**, `d(S,{A,B})`, must exceed `d(A,B)` — the A/B
  control is a required argument to `paper_leak.register_distance_holds`,
  never optional, so the control cannot be silently dropped.
- **N-gram overlap**, `overlap(S,R) <= max(overlap(A,R), overlap(B,R))` —
  self-calibrating against whatever chance floor two unstyled drafts
  already share, with `paper_leak.relative_overlap_holds` taking no
  threshold parameter at all.

Independent of both: any shared run of **eight or more** normalized tokens
between a styled draft and a sample in `R` refuses `STYLE_OVERLAP` by name
— a tripwire, not the proof; tuning it can never move the guarantee above,
because the guarantee's own function reads no threshold. Both measurements
read `R` alone, never a reference file directly.

## A diagram that compiles, or says why: `render` and `place`

Three more modules, from `a-diagram-that-compiles-or-says-why`:
`paper_latex.py` (the sole holder of `subprocess` in this skill — an AST
scan, `NoSubprocessScanTests`, holds every other script to zero),
`paper_figure.py` (source/manifest layout, stop A, the compile pipeline,
the repair-budget ledger), and `paper_obligation.py` (components,
separation, caption, mandatory — pure functions over the contract's own
`figure:` declaration, never a hardcoded section or block id).

Each diagram id resolves to `paper/Figures/<id>.tex` (standalone TikZ, one
`% node: <label>` comment per component), a sibling `<id>.diagram.json`
manifest (`components`, `encodings`, `caption`), and — once compiled —
`<id>.pdf` beside them. `main.tex` receives the figure only through the
existing `substitute` verb's `\includegraphics`; no TikZ byte ever enters
`main.tex`.

| Verb | What it does | Refuses |
| --- | --- | --- |
| `render --figure-id <id> [--paper <dir>]` | Compiles `<id>.tex` standalone via exactly one `latexmk` call, cross-checks the manifest both directions, and scans stop A before ever spawning the compiler | `DIAGRAM_SOURCE_ABSENT`, `MANIFEST_SOURCE_MISMATCH`, `DIAGRAM_PLOTS_DATA`, `LATEX_TOOLCHAIN_ABSENT`, `LATEX_LOG_ABSENT`, `LATEX_OUTCOME_UNEXPLAINED`, `LATEX_PACKAGE_ABSENT`, `REPAIR_BUDGET_SPENT` |
| `render --figure-id <id> --section <stem> --block <id> [--sections <dir>] [--paper <dir>]` | The same compile, and then the full obligation suite (components — only when the block declares `components_from`, excludes, caption, mandatory, cross-diagram separation) against the block's own `figure:` declaration | adds `MALFORMED_FIGURE_OBLIGATION`, `COMPONENT_MISMATCH`, `COMPONENTS_FACT_UNRESOLVED`, `COMPONENTS_FACT_NOT_A_LIST`, `EXCLUDED_COMPONENT`, `SHARED_COMPONENT`, `CAPTION_INCOMPLETE`, `MANDATORY_DIAGRAM_ABSENT` |
| `render --figure-id <id> --acknowledge-reset [--paper <dir>]` | The explicit operator acknowledgement that clears a spent ledger — compiles nothing, never combined with a compile in the same call | (none beyond `render`'s own) |
| `place --figure-id <id> --pdf <path> --provenance <path> [--paper <dir>]` | Places an already-measured figure's PDF — compiles nothing, requires a provenance record naming the run that produced it | `DIAGRAM_SOURCE_ABSENT` (reused: the named artifact this call needs is absent) |

**A repairable failure is an ordinary outcome, not a refusal.** `render`
returns `"status": "ok"`, `"verdict": "failure"` with the parsed
diagnostics and `attemptsUsed`/`budgetRemaining` for a compile that failed
but is still within its four-attempt budget — spending an attempt is the
loop's ordinary cost. Only the fifth attempt for an id refuses
`REPAIR_BUDGET_SPENT`, naming every distinct diagnostic and source digest
already tried; the budget survives edits between attempts (keyed to the id
alone, never reset by a new digest) and is cleared only by an explicit
operator acknowledgement (deleting the ledger file — `paper/.paper-writing/
figures/<id>/ledger.json` — **is** that acknowledgement, made explicit
rather than pretended-secure). A missing `.sty` refuses
`LATEX_PACKAGE_ABSENT` and spends nothing: redrawing cannot fix an absent
package.

**The data-figure boundary, measured, not assumed.** Stop A
(`paper_figure.scan_data_boundary`) refuses `DIAGRAM_PLOTS_DATA`
pre-compile on a plotting package, a `\begin{axis}`, an external table
read, an `\input`/`\include` escaping `paper/Figures/`, or an embedded
coordinate series over the illustrative threshold. Stop B is the compile's
own sandbox (`cwd` = `paper/Figures/`, `-outdir` = scratch, child env
carrying `openin_any=p`/`openout_any=p`/`shell_escape=f`) — **measured
against a real TeX Live 2026 install, not merely declared**: `shell_escape=f`
genuinely blocks `\write18`, but `openin_any=p` does **not** block a literal
absolute-path `\input{...}` on this engine (an explicit absolute path never
goes through kpathsea's search algorithm at all). Stop A's pre-compile
source scan is therefore the primary, load-bearing defense against that
exact vector — never something resting on the env var alone. Placing a
measured figure is `place`, entirely outside the compile path: no
`latexmk` call, no ledger, no stop-A scan.

**Obligations are read, never known.** A block's `figure:` declaration
(`ordered`, `excludes`, `caption_enumerates`, `caption_decodes`,
`mandatory` — all five required; `components_from` OPTIONAL,
`paper_contract.py`'s `_parse_figure`) is read entirely off the contract;
`paper_obligation.py`'s pure functions (`check_components`,
`check_excluded`, `check_shared_components`, `check_caption`,
`check_mandatory`) check it against a manifest, never against a hardcoded
section or block id. When `components_from` names a fact, the Components
Check's expected list is DERIVED — never operator-supplied — from that
fact's own declared resolution (`declare --fact <id> --value
'["a", "b"]'`, read back through `paper_declarations.read_fact`), refusing
`COMPONENTS_FACT_UNRESOLVED` when the fact was never declared and
`COMPONENTS_FACT_NOT_A_LIST` when its resolution does not parse as a JSON
array of strings. `components_from`'s named fact must equal the FULL
expected list by contract — section 01's methods diagram IS the
contribution list, so `components_from: contributions` alone suffices. A
block whose diagram is a composite crossing over several categories of
content, none of which alone is the full list (section 02's closing
diagram: data, methods, axes, metrics, qualitative instruments, the
repetition unit), declares NO `components_from` at all — the Components
Check simply does not run for it, honestly, rather than being wired to one
fact's partial value and silently inverting (measured directly by
`a-diagram-that-compiles-or-says-why`'s own corrective verify: the prior
`components_from: dataset` reading refused a prose-compliant diagram and
passed a degenerate one). Deleting a `figure:` key removes the whole
obligation with zero code changed. A block whose contract states the
synthesis artefact may be a diagram **or** a table (section 05's block 5)
carries no diagram obligation at all when the operator's choice leaves no
`<id>.tex` — a legal table triggers nothing.

**Drafting the diagram itself delegates to the `diagram-author` agent.**
It authors the `.tex`/`.diagram.json` pair and drives its own `render`
loop up to the repair budget, stopping at `REPAIR_BUDGET_SPENT` or an
unrecoverable refusal for the operator to resolve — it never clears a spent
ledger itself.

**Measure this before delegating (diagram-author):** confirm the block's
`figure:` declaration is already readable (`contract --file <path>`) and,
when it declares a `components_from` fact, that fact is already declared
as a JSON array of strings (`plan` reports it fixed; `declare --fact <id>
--value '["a", "b"]'` if not) — an agent asked to draft a diagram against
an obligation it cannot read cannot distinguish "no components yet" from
"cannot be checked."

## The couplings hold, or they do not: `verify`

Ten contracts state obligations that span two sections. A finished
`paper/main.tex` can satisfy every section alone and still be incoherent
across them — `verify` is a read-only report over seven checks: five
cross-section couplings, citation integrity, and contract currency. It
never writes a byte, under any input, including every refusal path, and it
never repairs anything it finds — `skill-audit`'s own shape, reused here.

```bash
.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py verify
```

| Verb | What it does | Refuses |
| --- | --- | --- |
| `verify [--sections <dir>]` | Read-only report: `contribution-list`, `chain`, `gap`, `artefacts`, `future-work`, `citations`, `contract-currency` | `DECLARATION_RECORD_ABSENT` |

**Three values, never two.** Every check's own `verdict` is `pass`, `fail`
or `unmeasured` — `unmeasured` is never folded into `pass`. Two new modules
carry this: `paper_coupling_evidence.py` (every disk read `verify`
performs — named to avoid colliding with `paper_evidence.py`, the
claim<->source evidence module `no-claim-without-a-source-that-holds-it`
already ships) and `paper_verify.py` (the seven pure checks and the report
they assemble; an AST lock and an executed before/after content manifest
both hold it, and `paper_coupling_evidence.py`, to writing nothing).

**`verify` reads its own declaration record, `paper/couplings.json` —
read-only, untracked like `main.tex` itself, and written by nobody this
skill ships today.** An entirely absent or empty record refuses
`DECLARATION_RECORD_ABSENT` for the whole run: nothing is known about any
coupling, so per-check `unmeasured` across the board would bury the fact
that nothing was checked at all. One block missing its own entry inside an
otherwise-present record is narrower — `unmeasured`, reason
`BLOCK_NOT_DECLARED`, for the couplings that depend on that block only; the
run still proceeds and every other check still reports a real verdict.
Which blocks a check reads is itself derived, never hardcoded or
record-declared: the set is every block whose contract `requires_facts`
names the relevant fact, read through `paper_contract.parse` over
`sections/*.md` headers. An unreadable or headerless corpus reports
`unmeasured`, reason `SECTION_CONTRACTS_UNREADABLE`; a fact no block
requires reports `unmeasured`, reason `NO_BLOCK_REQUIRES_FACT` — never zero
comparisons reported as agreement.

**Contract currency reads the `provenance` region `the-paper-carries-its-
own-decisions` already writes at `substitute --contract` time — `verify`
never writes it.** An absent or empty region reports check `contract-
currency` alone `unmeasured`, reason `CONTRACT_RECORD_ABSENT`, and the run
still exits `0`: every other check still reports. Editing one block's
guidance changes the whole-file contract hash and flags every block of
that section stale, not only the edited one — inherited from that region's
own accepted over-reporting tradeoff, never narrowed here.

**Coupling 3 (the gap) can never read `pass`.** Its own vocabulary is the
single value `unmeasured`, reason `ASSISTED_READING_REQUIRED` — `verify`
never guesses and never gates on "the same thing at different depths."
What it publishes instead: both blocks' closing sentences verbatim with
byte offsets, both front lists with counts, and three mechanical
sub-results (both closings present, fronts equal, front counts equal) as
named booleans — evidence a human can act on without making the reading
themselves.

### Decision Gates (verify)

| Situation | Action |
| --- | --- |
| `verify` refuses `DECLARATION_RECORD_ABSENT` | `paper/couplings.json` is missing or empty — nothing has been declared yet; declare the couplings before running `verify` again |
| A check reports `unmeasured`, reason `BLOCK_NOT_DECLARED` | Only the block(s) that check depends on have no entry in the record; every other check still ran |
| A check reports `unmeasured`, reason `SECTION_CONTRACTS_UNREADABLE` | The `sections/` corpus itself could not be read — `contract`/`order` first, then re-run `verify` |
| Coupling `gap` reports `unmeasured` | This is unconditional, not a defect — read the published closings and front lists yourself; `verify` never closes this one |
| `contract-currency` reports `unmeasured`, reason `CONTRACT_RECORD_ABSENT` | No block was ever written with `--contract`; every other check still reports |

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
