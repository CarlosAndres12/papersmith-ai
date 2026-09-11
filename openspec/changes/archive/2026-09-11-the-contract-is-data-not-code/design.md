# Design: The Contract Is Data, Not Code

## Technical Approach

A stdlib-only, fail-closed reader over `sections/*.md`, in `implementation_cli.py`'s shape:
one JSON object on stdout, exit 0 = ran, exit 2 = a guard refused. The header is parsed;
the prose below it is read as bytes and never decoded for meaning. Five modules under
`.claude/skills/paper-writing/scripts/`, layered so a later phase can import the
vocabulary without importing the reader. Implements `specs/section-contract` and
`specs/writing-readiness`.

## Architecture Decisions

### Decision: no `_core/`; the seam is inside the skill

| Option | Tradeoff | Decision |
|---|---|---|
| New `_core/contract/` now | `_core/` is a **cross-skill** seam — `LaunchAvailableNoUpwardImportsTests` forbids it importing caller-side modules at all. The six later consumers are six phases of *one* skill, which share code by sharing a directory | Rejected; trigger below |
| Add to `_core/implementation/` | Measured coupling: `reachable_refusal_codes` (`tests/test_proposal_implementation.py`, docstring at its definition) takes **every `*.py` under `_core/implementation/` whole** and demands each refusal be classified in `GATING_REFUSALS`. Paper codes would land in another skill's roster | Rejected |
| Skill-local modules; import only `Refused` | `impl_refusals.py` defines and raises nothing, so it contributes no roster entry. One exception class forge-wide | **Chosen** |

**Revisit trigger**: a second *skill* needing the fact vocabulary or the sort. Extraction is
mechanical — `paper_vocabulary.py` and `paper_graph.py` hold no state and no I/O.

Internal layering, which is the seam the six later phases actually consume:

| Module | Holds | Why separate |
|---|---|---|
| `paper_vocabulary.py` | the three closed tuples (facts, declarations, citation regimes) and nothing else | a consumer that only needs the vocabulary must not drag in the reader; this is the one declaration every roster derives from |
| `paper_contract.py` | front-matter grammar, schema validation, `install_header` | the only module that touches disk bytes |
| `paper_graph.py` | corpus assembly, id namespace, edge resolution, sort, cycle report | pure functions over parsed records — the half a later phase reuses whole |
| `paper_readiness.py` | per-block readiness given satisfied sets | separable because readiness and order are two questions, and back matter proves they differ |
| `paper_cli.py` | front door, refusal classification, JSON | shared with `only-the-block-changes` (below) |

### Decision: the header is JSON inside a `---` front-matter fence

| Option | Tradeoff | Decision |
|---|---|---|
| PyYAML | It *is* in `requirements.txt`, but that file declares the **forge's own** venv, not what a shipped script may assume; and YAML's implicit typing silently coerces (`no`→False, a bare id that looks numeric→int) | Rejected |
| Hand-parsed YAML subset | Every subset is a second undocumented grammar. Nesting — a list of maps whose values are lists — is exactly where subsets parse *partially*, which the spec forbids by name | Rejected |
| stdlib `tomllib` | Comments, but 3.11+ only (this repo already died under 3.9), and `blocks` becomes verbose arrays-of-tables | Rejected |
| **JSON inside `---` … `---`** | `json.loads` is all-or-nothing **by construction**, so "never parses partially" is structural rather than a rule someone must maintain; `JSONDecodeError` gives line and column for one `MALFORMED_HEADER`. JSON is a YAML 1.2 subset, so the fence is *also* valid YAML front matter and editors highlight it. Cost: no comments, and quotes/commas to hand-edit | **Chosen** |

Cost mitigated, not waved away: `contract show --file` re-emits a canonical header the user
can paste, and `MALFORMED_HEADER` carries line/column rather than "invalid".

### Decision: one flat id namespace; `after` admits section **and** block ids

The settled interface says the block graph is authoritative. With section-only targets that
graph is **empty inside 8 of 10 contracts** — `06` states an internal chain (`### Internal
chain`, 4b partial → 2 → 3) and `08` states another (`## Inputs per slot`, slot 4 → slot 2),
and both say in their own words that their blocks have no order, only a graph. A schema that
cannot transcribe them makes the authoritative graph a claim about nothing.

So: section ids and block ids share **one namespace and must be disjoint** (`ID_COLLISION`).
Block ids are section-qualified for global uniqueness in `main.tex` (`introduction.block-3`),
joined with `.` — shape-valid under the sibling's `[A-Za-z0-9._-]+` at zero cost, and the
sibling's `/` widening is never needed. The reader never *parses* a block id; a block belongs
to whichever contract declares it. An `after` entry naming a section expands to every block
of that section.

**The "exactly three" test is scoped by derivation, not by a hand-list**: it collects `after`
entries whose target resolves to a *different section than the holder* and asserts that set
is the three transcribed cross-section edges. Intra-section entries are a different class and
are not counted by it.

### Decision: every `after` carries a `source`, and the quote is checked against the file

`after` is a list of objects: `{"target": <id>, "source": {"file": <path>, "quote": <text>}}`.
The `file` may be a **different contract than the holder** — measured: the abstract-after-
conclusions edge is stated only in `sections/07-conclusions.md` ("The abstract is written
after this section, because it compresses it"), and `08-abstract.md`'s own prose states no
cross-section edge at all, because the edge constrains the abstract but the sentence lives
with the conclusions.

The anti-invention lock is mechanical: a test asserts each `quote` is a substring of the
named file **after collapsing every whitespace run to one space on both sides**. `sections/`
is hard-wrapped, so a real sentence spans two lines and a naive substring test would report
it absent — normalising both sides is what makes the lock usable rather than a source of
false reds. An invented edge cannot produce a quote that is in the file.

### Decision: `09`'s "the body" is enumerated in the header, not resolved by the reader

**Measured, and it overturns the spec's parenthetical.** The spec resolves this edge "against
the `skeleton` fact's own list of body sections". `skeleton` occurs exactly once in all ten
contracts — `sections/06-introduction.md:47`, an external input unblocking introduction block
6 — and `09`'s own `Inputs` table names three rows, none of them the skeleton or the body. No
contract anywhere partitions sections into body and non-body. That resolution rule has
nothing to stand on.

| Option | Tradeoff | Decision |
|---|---|---|
| Reserved group token `body` | A third vocabulary with exactly one member, and its membership is undefined by any contract | Rejected |
| Derive "body" from a `position` range | A magic constant inside the reader — interpretation moved into code, which is the defect this change exists to remove | Rejected |
| **Enumerate the sections in `09`'s `after`, citing the sentence** | The reading is visible, auditable and user-editable **as data**; the reader interprets nothing. Cost: one declaration holds seven targets, and a user who adds a body section must add it here | **Chosen** |

Governing principle, and the reason this design is coherent: **all interpretation lives in the
header; the reader performs none.**

### Decision: an absent `after` target is reported, never refused

Deleting a contract is in scope and must leave a working skill; `05-related-work` is
optional by its own prose, and two edges point at it. So a *shape-invalid* id refuses
(`BLOCK_ID_MALFORMED` — a defect), while an id that is merely **absent from the corpus**
contributes no edge and lands in `danglingEdges`, published on every readiness run. The
`interpreterMatch: null` idiom: a field the reader receives, never a silence.

### Decision: `position` is reported, never sorted on, and the filename is never read

The filename prefixes (`01`…`10`) are **not** the rendering order — `08-abstract` renders
second, `10-back-matter` last. A test asserts the derived rendering order differs from the
sorted-filename order, which goes red the moment anyone implements `position` by sorting
paths. `position` never contributes an edge to the writing sort.

## The sort, and how ties are broken

Kahn over the block graph, with a min-heap. The key is
`(section.position, block_index_within_section, block_id)` — every component from the header,
none from `dict` iteration, `os.listdir` or the filename. Files are read in sorted-name order
only so a run is reproducible; the name never enters the key. Two mutually unordered blocks
therefore land in rendering order, then declaration order, then lexical order: total, stable,
and a re-run of an unchanged corpus is byte-identical output.

A cycle: Kahn terminates with nodes remaining. `ORDER_CYCLE` refuses and reports the cycle
**itself** — one minimal cycle extracted by DFS over the residual subgraph, as an ordered id
list, each edge carrying the `source` quote that produced it. A user sees which transcribed
sentences disagree, not that "a cycle exists".

## Header insertion into the ten shipped files

Per file, in one process: read bytes → `pre = sha256(bytes)` → refuse `HEADER_PRESENT` if a
fence is already there (this is what makes the operation idempotent and one-shot) → write
`header_bytes + bytes` via temp-in-same-dir + `os.replace` → re-read → assert
`post[:len(header_bytes)] == header_bytes` **and** `sha256(post[len(header_bytes):]) == pre`.
A mismatch restores the original bytes and refuses `BODY_MUTATED`. All I/O binary; `newline`
is never touched, so no line-ending translation can occur.

The ten expected pre-digests in the suite are taken from `git show HEAD:sections/<file>`, not
from the worktree — a second session writing while the test measures would otherwise make a
real mutation look clean.

## The seam with `only-the-block-changes`

| Owned there (shape) | Owned here (meaning) |
|---|---|
| marker grammar, region bounds, lexical id class `[A-Za-z0-9._-]+`, uniqueness, pairing, nesting | which ids exist, what each requires, which section declares it, readiness, order |

The engine accepts any shape-valid id and asks nothing else; it never opens `sections/`. The
contract layer hands ids in and reads `status`'s block table out; it never parses a marker.

**What breaks if either side drifts.** If the engine ever validates an id against the fact
vocabulary, the eleventh-contract mutation stops passing — an invented contract would need a
code change, which is this change's own success criterion inverted. If this change emits an id
outside the lexical class, `BLOCK_ID_MALFORMED` fires in the engine and no substitution is
possible; so id shape is validated **here too**, against a pattern this side owns, and a test
asserts the two patterns accept the same strings without either importing the other.

**Front-door collision, since neither change has landed.** Both create
`.claude/skills/paper-writing/` and both want `paper_cli.py`. Resolution: `paper_cli.py`'s
mutable surface is a **registration list** of `(subcommand, handler, refusal-class)` entries.
Whichever change lands first creates the file with only its own entries; the second appends
its own. The two changes touch disjoint entries and disjoint modules, so either order merges.
Test files stay separate (`tests/test_paper_contract.py`), because two classes sharing a name
in one file silently drops the second — measured in this repository.

## Testing Strategy

Strict TDD: every row RED first. Suite `tests/test_paper_contract.py`, one class per concern,
no class name reused.

| Layer | What | How |
|---|---|---|
| Unit | schema, both vocabularies, citation regime, every refusal | one fixture per code in a `TemporaryDirectory`; a malformed-JSON fixture asserts **nothing** was returned, not merely that it raised |
| Transcription | every `after` carries a `source`; each quote is a whitespace-normalised substring of its named file | derived from the ten headers; goes red on an invented edge |
| Edge set | exactly three **cross-section** `after` declarations | holder-section vs target-section computed, never a hand-list |
| Insertion | ten body digests vs `git show HEAD:` | per file; one changed byte fails |
| Order | determinism (two runs byte-identical), rendering ≠ filename order, RW before intro block 3 and after 1/2/4a | subprocess, twice, compared |
| Cycle | `ORDER_CYCLE` names the participating blocks | two-block fixture, executed |
| Readiness | back matter: zero missing facts, declarations missing; a facts-satisfied/declaration-missing block reports `blocked` | the case a fact-only check gets wrong |
| Roster | every raised code classified invocation-defect or work-state; every work-state code publishes a `resolve` | derived from source in `reachable_refusal_codes`' shape, never hand-listed |
| Mutation A | the eleventh contract | see below — **executed**, recorded as executed |
| Mutation B | `UNKNOWN_FACT` | subprocess against a fixture declaring `discussion`; assert exit 2 and the `code` field. Observed, never asserted from source |

**The eleventh-contract fixture, and why it is not vacuous.** Its novelty is **derived from
the ten, not declared by its author**. A helper computes from the shipped headers the set of
used shapes along two axes — (a) `frozenset(requires_facts)` per block, (b) graph shape:
whether a section carries both a section-level and a block-level `after`, and whether any
block's `after` targets a section whose `position` is *earlier* than its holder's. The test
asserts the fixture's shape tuple is **absent from that set on both axes**. If a later edit to
a shipped contract makes the fixture's combination shipped, the test goes red and the fixture
must move — the anti-vacuity lock is falsifiable rather than a promise. The fixture is then
run through the CLI **as a subprocess** against a temp `sections/` holding the ten copies plus
the eleventh, with the reader's source byte-identical (digest asserted before and after).

## What Breaks — Producers and Products

| Class | Row |
|---|---|
| Producers | **None.** No `.py` anywhere in this repository references `sections/` (verified 2026-09-10, repo-wide). Nothing imports these modules yet |
| Products | `sections/*.md` — the only existing instances of this shape, and all ten are headerless. Each is unreadable to the new reader until this change writes its header; that is the change, not a break. No other consumer exists to invalidate |
| Products | **No `paper/main.tex` and no block ids exist on disk anywhere** (the sibling verified `paper/` absent, 2026-09-10). Naming ids here invalidates zero written instances |
| Products | Superseded reasoning: `ORDER.md` (deliberately deleted) and the third writing order in memory #1531. Both fall out of domain and are **not** repaired here; nothing reads either |
| Products | Forge leak guard: `shipped_documents()` walks `.claude/skills/` only, so headers in `sections/` are outside its reach — but every new file under `.claude/skills/paper-writing/` is scanned. `transfer` is on `FORGE_VOCABULARY_FLOOR` and `09`'s prose uses it; the skill's own doctrine must not quote that sentence |

## Threat Matrix

`N/A` for every row: no routing, no shell, no subprocess in shipped code (the mutation
subprocesses are test-side), no VCS automation, no PR automation, no executable-file
classification, no process integration. The one real boundary — a caller-supplied
`--sections` path — is answered by `.resolve()` under a root derived by path arithmetic
(`Path(__file__).resolve().parents[3]`, never `git rev-parse`) with
`SECTIONS_OUTSIDE_REPOSITORY`, and gets its own RED test. It is not a row of this matrix and
no row is manufactured for it.

## Migration / Rollout

No data migration. Header insertion **is** the migration: one-shot, per file, guarded by
`HEADER_PRESENT` so a second run refuses rather than double-writing. Rollback is `git revert`;
the ten contracts return to headerless prose and nothing reads them.

## Open Questions

- [ ] `specs/section-contract` resolves `09`'s edge "against the `skeleton` fact's own list of
      body sections". Measured above: no contract defines that list. This design enumerates in
      the header instead. The spec sentence should be narrowed to match, or this decision
      overturned — but not left disagreeing.
- [ ] Intra-section `after` entries widen what the header transcribes beyond the proposal's
      literal wording (`after: [<section-id>]`). Accepted here because the alternative empties
      the authoritative block graph inside 8 of 10 contracts; worth confirming at tasks.
- [ ] Artifact exceeds the 800-word sdd-design budget. Six mandated decision areas plus the
      breakage, threat and testing sections do not compress below it without dropping a
      requirement.
