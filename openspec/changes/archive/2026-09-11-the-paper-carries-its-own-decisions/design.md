# Design: The Paper Carries Its Own Decisions

## Technical Approach

Four new stdlib-only modules beside Phase 1's and Phase 2's, one shared region
parser, two new `paper_cli.py` verbs, and one agent whose inability to decide is a
capability grant rather than an instruction. Phase 2's `paper_readiness` computes
readiness *given* satisfied sets and has no source for them; the declarations
region becomes that source. That is the join this change exists to make.

## Architecture Decisions

### Decision: Module layout — four siblings, nothing in `_core/`

| Option | Tradeoff | Verdict |
|---|---|---|
| Shared region parser in `.claude/skills/_core/` | `test_implementation_core.py::test_no_core_file_names_a_product_directory_or_source_root` globs `_core/implementation/*.py` wholesale, and `reachable_paper_refusal_codes`'s docstring turns on `impl_refusals.py` raising no `Refused` of its own. A `Refused` in `_core` enters the sibling skill's roster, which neither skill owns | **Rejected** |
| One module for all three capabilities | Fewer files; but the region parser has two consumers with different lifecycles, and one file makes the guidance registry drag in the region grammar | Rejected |
| Four modules in `.claude/skills/paper-writing/scripts/` | More files; each independently importable | **Chosen** |

`paper_region.py` (one grammar, both kinds), `paper_guidance.py`,
`paper_declarations.py`, `paper_provenance.py`. `paper_cli.py` and
`paper_block.py` modified. Phase 2 is mid-apply in `paper_cli.py` — `paper_vocabulary.py`
and `paper_contract.py` are on disk, the CLI's four verbs are not yet its six. That file
is the merge surface; `paper_graph.py` and `paper_readiness.py` are still pending.

### Decision: The digest covers the region body, and a mismatch never heals itself

| Option | Tradeoff | Verdict |
|---|---|---|
| Digest the whole file | Every Phase 1 `substitute` invalidates both regions. Structurally unusable | Rejected |
| No digest, trust the file | `paper/*` is gitignored (`.gitignore:78`) and this is the one area Phase 1 declares undigested. There would be **no** integrity here at all | Rejected |
| Digest the region's own body bytes | Same mental model as Phase 1's block digest | **Chosen** |

A mismatch refuses `DECLARATIONS_HAND_EDITED` / `PROVENANCE_HAND_EDITED` (work-state),
writes nothing, and `plan` reports it. **There is no `--adopt` here**, and that is a
deliberate departure from Phase 1. Phase 1 adopts because the block body is prose the
human owns; a declarations record is a decision the machine reads back as authority, and
adopting one would launder an unreviewed edit into "what was decided". Cost: the operator
must re-run `declare`. Accepted.

### Decision: Two grammars coexist by mutual non-prefix, pinned in both directions

Sentinels: `%% paper-writing declarations begin sha256=<hex>` … `end`, likewise
`provenance`. Neither starts with `MARKER_PREFIX = b"%% paper-writing block"`
(verified in `paper_block.py`), and Phase 1's `scan_markers` `continue`s on any line
that does not — so both regions are prose to Phase 1. Our parser anchors on the **full
kind token**, never on `%% paper-writing `, so it cannot read a block marker either.

**The `<kind>` token sits in slot 2** — the same whitespace-delimited slot Phase 1's
literal `block` occupies (`%%`, `paper-writing`, `<kind>`).

| Option | Tradeoff | Verdict |
|---|---|---|
| Slot 2, sibling of `block` | Maximum surface similarity — a human skimming sees three near-identical comment families. But disjointness reduces to *one token comparison at a fixed index*, which is what makes the lock derivable instead of hand-written | **Chosen** |
| Fuse into token 1 (`%% paper-writing-declarations`) | Deliberately dissimilar for human eyes; but it leaves the family, and it is still one narrowing away from being swallowed identically. Trades a machine-checkable property for an ergonomics guess | Rejected |
| Kind after `begin` (`%% paper-writing region begin declarations`) | Introduces a third literal and moves the kind *out* of the sentinel, so a mistyped kind still parses as a region | Rejected |

`DisjointGrammarTests` holds this five ways, four of them derived from
`paper_block.MARKER_PREFIX` and `paper_region.KINDS` rather than written out:

1. `MARKER_PREFIX.split()` has **exactly 3 tokens**. A *narrowing* to
   `%% paper-writing` leaves 2 → red.
2. That split's **slot 2 equals `b"block"`**. Any rename → red.
3. `b"block"` is **not in `KINDS`**, and no kind is a prefix of another → red on collision.
4. **Exact pin** on the whole constant, with a failure message naming the coupling.
   Still needed after 1–3: `b"%% paper-writing block "` (trailing space) splits
   identically while silently disarming Phase 1's `MARKER_MALFORMED` detection. The pin
   is brittle on purpose; the message must say so.
5. **Behavioural, both directions**: a `main.tex` holding only the two regions → `status`
   returns zero blocks and refuses nothing; one real block plus both regions → `status`
   finds exactly 1 block and our parser exactly 2 regions.

Mutation 1 (rename our sentinel's slot 2 to `block`) proves 5 can fire.

### Decision: `insumos-observer` cannot decide, by schema and by capability

Three layers, none of which is an instruction:

| Layer | Mechanism | What it makes impossible |
|---|---|---|
| Capability | `tools: Read, Glob, Grep` — no Write, no Edit, no Bash | It cannot write a record, and cannot invoke `declare` or any CLI |
| Schema | Its return has `satisfied: true\|false` + `evidence: [path, quote]` per fact, and **no field a value could be written into** | It can report a fact unsatisfied; it has nowhere to say what the fact should say |
| Vocabulary | Reports against `paper_vocabulary.FACTS` only; an id outside the ten is a refusal, not a new fact | It cannot invent a requirement |

Rejected: grant Bash and instruct read-only. This repository has already measured a
suite spawning live agents that wrote into `implementations/`. An agent told not to
decide will decide; capability removal is the only enforcement that survives
non-compliance. Also rejected: let it emit a ready-to-paste `declare` command — a
decision with one extra keystroke is still a decision.

**The seal that forces extra scope.** `test_agents.py` requires every agent bound to a
skill outside `NORTHLESS_SKILLS = {"skill-audit"}` to have a `stretch:` and its skill to
declare an `OBJECTIVE_FLOW`. `paper-writing` declares none (grepped — zero matches).

| Option | Tradeoff | Verdict |
|---|---|---|
| Add `paper-writing` to `NORTHLESS_SKILLS` | Weakens a lock to admit our own file, and the test then asserts the skill declares no objective — freezing the build's north out permanently | **Rejected** |
| Declare `OBJECTIVE_FLOW` in a `paper-writing` script; agent takes `stretch: <declared stage>` | Phase 3 must author the build's arrival and stages. Non-terminal stretch keeps the agent honest about ending short, so its description need not carry the arrival | **Chosen** |

`test_agents.py` also requires, as exact bytes: `paper-writing/SKILL.md` containing
`delegates to the `insumos-observer` agent` and `Measure this before delegating`; the
agent body containing `You begin`, `you end`, `## What you return` with `did` /
`stoppedAt` / `state` / `owed`, `never conclusions`, `measured again`,
`## Measure before you assert`, and `Not every agent's description carries its bound
skill's arrival`. These are derived from source, not style advice.

### Decision: Four stacked slices, not three

The proposal's three-way slice puts ~780 authored lines in its last slice. Against the
400-line review budget, slice C splits:

| Slice | Contents | Est. authored lines |
|---|---|---|
| A | `paper_region.py`, `paper_guidance.py`, `DisjointGrammarTests`, mutations 1 + 4 | ~490 |
| B | `paper_declarations.py`, the fact partition, `declare`, immutability, `--reopen`, mutations 2 + 5 + 6 | ~620 |
| C1 | `paper_provenance.py`, `substitute --contract`, drift, mutation 3 | ~420 |
| C2 | `plan`, `validate_observation_report`, `insumos-observer`, `OBJECTIVE_FLOW`, SKILL.md, mutation 7 | ~470 |

`paper_region.py` lands in A with no consumer in its own slice — a real cost, accepted
because it is pure (bytes in, records out), fully testable alone, and it is the one
boundary whose failure would force B and C to be rewritten. Settle it first.

Total forecast ~1900 authored lines against a 1400 budget. **Decision needed before
apply: Yes. Chained PRs recommended: Yes. 400-line budget risk: High.**

### Decision: Mutation harness generalized, in a shared helper module

`_run_against_mutant` in `test_paper_writing.py` is bound to `PAPER_BLOCK_SOURCE` and
copies exactly one module; our mutations target new modules that import siblings.
Generalize into `tests/paper_mutation.py` (precedent: `tests/forge_vocabulary.py` is a
non-test helper under `tests/`), copying the whole `scripts/` directory — excluding
`__pycache__` — at correct relative depth, mutating one named file.

Rejected: cross-suite import from `test_paper_writing.py`, which couples two suites.

Both existing assertions are kept and are load-bearing: **exact anchor count == 1** and
**bytes actually changed** — a matched anchor is not a mutation that executed. Stale
`.pyc` is closed twice: a fresh temp dir per call, `PYTHONDONTWRITEBYTECODE=1`, and no
`__pycache__` copied. `MUTANT_IMPORTED_OK` on stdout separates "mutant failed to import"
from "the guard genuinely failed".

Mutation 6, concretely: in `paper_declarations.py`, replace the declaration-kind
validator call `paper_vocabulary.validate_declaration(...)` with `validate_fact(...)` —
a plausible copy-paste between two record kinds sharing a code path. The guard
(`declare --declaration contributions` must refuse `UNKNOWN_DECLARATION`) goes red.
Standing beside it: `set(FACTS).isdisjoint(DECLARATIONS)`, `len(FACTS) == 10`,
`len(DECLARATIONS) == 6` — pinned, so widening either tuple anywhere goes red here.

### Decision: A fact the agent may observe is a partition, not a guideline

The ten facts split three ways, and the split is the agent's whole boundary:

| Class | Facts | Source |
|---|---|---|
| Observable (5) | `formulation`, `dataset` | `proposals/` — the managed mathematical proposal |
| | `experimental-design` | `experiments/` — the managed experiments document |
| | `implementation`, `results` | the target implementation repository |
| Derived (4) | `contributions`, `problem-statement`, `gap`, `limitations` | the agent reports the **material** these derive from, never the derivation |
| Structural (1) | `skeleton` | a decision, not an observation |

`guidance/` is **not** a fact source; it feeds the registry's style/evidence classes only.

`OBSERVABLE_FACTS` / `DERIVED_FACTS` / `STRUCTURAL_FACTS` live in
`paper_declarations.py`, not in Phase 2's `paper_vocabulary.py` — that module's tuples
are landed code this change depends on and must not widen, and it is the one module
every roster derives from. The partition is held by exact equality against
`paper_vocabulary.FACTS`, so a fact Phase 2 ever adds goes red here until somebody
classifies it. Counts pinned 5 / 4 / 1; pairwise disjointness asserted.

Enforcement, in the same three-layer shape as the tool grant:

| Layer | Mechanism |
|---|---|
| Input | The agent is handed `OBSERVABLE_FACTS` as its subject list and is never given the other five ids. It cannot report on a name it was not given |
| Schema | `validate_observation_report()` refuses `NOT_AN_OBSERVABLE_FACT` for any key outside `OBSERVABLE_FACTS` — detectable even if the agent invents an id |
| Evidence | `implementation` and `results` may **not** be satisfied by the same evidence path; a report citing one file for both refuses `EVIDENCE_CONFLATED` |

That last row is the one the coordinator named: both facts share the target repository,
so a source-root binding cannot separate them. A source file can prove code exists; it
cannot prove the code ran. Requiring distinct evidence is what makes the conflation
visible rather than asked-against. **Mutation 7**: let the validator accept one path for
both → that guard goes red.

### Decision: JSON region bodies, comment-prefixed, canonically serialized

Both bodies are JSON, for the reason `paper_contract.py` already states in its own
docstring: `json.loads` is all-or-nothing, so "never parses partially" is structural
rather than a rule someone maintains. Reusing the house pattern, not inventing a second.

**Every body line carries a `%% ` prefix.** The regions sit in the prose area between
blocks, so an unprefixed JSON blob would be typeset into the document. The parser strips
the prefix per line to reconstruct the JSON.

**The digest covers the raw bytes between the markers, prefixes included** — byte-for-byte
Phase 1's rule, no exception. Rejected: digest the stripped JSON, which would make a
hand edit to the prefixes alone invisible and turn one rule into two.

**Serialization is canonical**: `json.dumps(obj, indent=2, sort_keys=True,
ensure_ascii=False)`, UTF-8, one trailing newline. Without `sort_keys` the same content
digests differently between runs and every second `plan` reports a phantom hand edit.
Timestamps come from an injectable clock so the suite is deterministic.

Declarations region body:

```json
{ "generation": 3,
  "records": [
    {"kind": "declaration", "id": "repository-url", "value": "…",      "fixed": true, "recorded": "<iso8601>"},
    {"kind": "fact",        "id": "dataset",        "resolution": "…", "fixed": true, "recorded": "<iso8601>"}
  ] }
```

The two kinds carry **deliberately different value field names** (`value` vs
`resolution`). A shared field name invites a shared code path, and a shared code path is
exactly how a closed vocabulary gets opened by accident — the risk mutation 6 exists to
catch. Different names force two branches, each validating against its own vocabulary.

Provenance region body:

```json
{ "records": [
    {"block": "intro.motivation", "contract": "sections/introduction.md",
     "contract_sha256": "<hex>", "generation": 3, "written": "<iso8601>"}
  ] }
```

A block absent from `records` is `unprovenanced`. Drift is reported when the recorded
`contract_sha256` differs from the file's current digest, or when the block's contract
names an entry reopened since its recorded `generation` — read from Phase 2's parsed
`requires_facts` / `requires_declarations`, never from write order. `--reopen <id>` bumps
`generation` and clears `fixed` on that entry only.

### Refusal codes and their classification

Eight names arrived from the spec; **two are dropped as duplicates**. `NOT_A_DECLARATION`
and `NOT_A_FACT` describe conditions Phase 2's landed `paper_vocabulary.validate_declaration`
/ `validate_fact` already refuse as `UNKNOWN_DECLARATION` / `UNKNOWN_FACT`, and `declare`
calls those validators directly. Two codes for one condition is the drift this
repository's roster exists to prevent. Behaviour is unchanged — only the name is reused.

| Code | Class |
|---|---|
| `DECLARATIONS_HAND_EDITED`, `PROVENANCE_HAND_EDITED` | `WORK_STATE` |
| `DECLARATION_FIXED` — clearing it is a human's decision to reopen, not a different flag | `WORK_STATE` |
| `CONTRACT_UNREADABLE`, `UNKNOWN_GUIDANCE_CLASS`, `MALFORMED_GUIDANCE_MARKER` | `WORK_STATE` |
| `REGION_MALFORMED`, `REGION_DUPLICATED`, `REGION_UNPAIRED` — twins of Phase 1's marker codes | `WORK_STATE` |
| `GUIDANCE_OUTSIDE_REPOSITORY`, `NOT_AN_OBSERVABLE_FACT`, `EVIDENCE_CONFLATED` | `INVOCATION_DEFECT` |

## Data Flow

    guidance/<f>/.paper-writing.json ──┐
    sections/*.md (paper_contract) ────┼──→ plan ──→ readiness + drift report
    declarations region (paper_region)─┤            (names, never repairs)
    provenance region ─────────────────┘
                    ▲                    ▲
           declare ─┘        substitute --contract

    insumos-observer ──(read-only report)──→ operator ──→ declare

## File Changes

| File | Action | Description |
|---|---|---|
| `scripts/paper_region.py` | Create | One region grammar, both kinds; digest over body |
| `scripts/paper_guidance.py` | Create | Per-folder class registry; `unclassified` reported |
| `scripts/paper_declarations.py` | Create | Two record kinds, fixing, immutability, reopen |
| `scripts/paper_provenance.py` | Create | Contract sha256 + generation per block; drift |
| `scripts/paper_cli.py` | Modify | `plan`, `declare`, `COMMANDS`, `REFUSAL_CLASSIFICATION` |
| `scripts/paper_block.py` | Modify | `substitute(..., contract=None)` keyword-only |
| `.claude/agents/insumos-observer.md` | Create | `stretch: <stage>`, read-only tools |
| `.claude/skills/paper-writing/SKILL.md` | Modify | Verbs, regions, delegation phrase, `OBJECTIVE_FLOW` |
| `tests/paper_mutation.py` | Create | Generalized mutation harness |
| `tests/test_paper_decisions.py` | Create | New suite — a second class of the same name loses tests silently |
| `tests/test_paper_writing.py` | Modify | Roster module tuple; measured count 21 moves per slice |

## What Breaks — Producers and Products

**Producers**: `paper_cli.COMMANDS`, `_COMMANDS`, `build_parser`,
`REFUSAL_CLASSIFICATION`; `reachable_paper_refusal_codes()`'s hardcoded
`(paper_block.py, paper_scaffold.py)` tuple — **not extending it makes the roster
silently under-derive, which is the roster failing open**;
`test_the_derivation_finds_the_measured_count`'s `21`; `test_agents.py`'s seal;
`SKILL.md`'s "only the first three landed" prose and its "Declared gap" paragraph, which
becomes partly false once the regions are digested.

**Products** (instances already on disk):

| Product | Verdict |
|---|---|
| `paper/main.tex` without regions | Falls out of domain — absent region is generation 0, never an error |
| Blocks written before `--contract` | Reported `unprovenanced`; never assumed current |
| `paper/.paper-writing/main.tex.prev` | Untouched; one-deep pre-image shape unchanged |
| `guidance/*/` folders on this disk | All `unclassified` — designed behaviour, stated as such |
| Ledgers/manifests/reports of this shape elsewhere | **None exist** |

## Threat Matrix

| Boundary | Applicable | Behaviour + RED test |
|---|---|---|
| Path resolution / traversal | **Yes** | `--guidance <dir>` resolving outside the repository refuses `GUIDANCE_OUTSIDE_REPOSITORY`, mirroring `paper_contract.resolve_sections_dir`. RED test: a `../` argument refuses |
| Process integration (agent tools) | **Yes** | RED test: `insumos-observer` frontmatter `tools` contains none of Write, Edit, Bash |
| Subprocess | **Yes, tests only** | Mutation harness spawns `sys.executable` with a 60s timeout into a temp tree removed in `finally` |
| Shell commands | N/A | No `shell=True`, no shell anywhere |
| Routing | N/A | One argparse front door; no dynamic dispatch |
| VCS/PR automation | N/A | Keyless, offline, no git invocation |
| Executable-file classification | N/A | No file is classified or executed by these modules |

## Migration / Rollout

No migration. Both regions live only in untracked `paper/main.tex`; `git revert` leaves
inert LaTeX comments. `guidance/<folder>/.paper-writing.json` is untracked and
hand-deletable.

## Open Questions

- [ ] `OBJECTIVE_FLOW`'s `arrival` and stage names are the operator's to word — the seal
      requires them to exist, not what they say. Needs one answer before slice C2.
- [ ] Whether `plan` reports guidance classes and drift in one payload or two. Deferred
      to tasks; it does not constrain any module boundary above.

---

**Budget note**: this exceeds the 800-word design budget. `rules.design.require_tradeoffs`
plus six mandated decisions plus a two-class breakage enumeration do not compress further
without dropping the alternatives that make each decision checkable.

**Citations verified 2026-09-10 by reading source**: `paper_block.MARKER_PREFIX`,
`scan_markers`'s prefix `continue`, `paper_cli.REFUSAL_CLASSIFICATION`, `COMMANDS`,
`paper_vocabulary.FACTS`/`DECLARATIONS`, `paper_contract.resolve_sections_dir`,
`test_agents.NORTHLESS_SKILLS`, `declared_objective`, `test_implementation_core.py`'s
`CORE.glob("*.py")`, `reachable_paper_refusal_codes`'s module tuple and its `21`,
`_run_against_mutant`'s two assertions, `.gitignore:23` and `:78`.

**Corrected from the proposal**, each by reading the file:

- `GUIDE_DIRECTORY` is at `.claude/skills/_core/deliberation/engine/proposal-workspace.ts:49`,
  not the path the proposal cited (one directory level off). The anti-pattern is
  unchanged, and that file's own line 5391 already names the fix it never received —
  which is precisely why this registry must not repeat it.
- `paper_vocabulary.py` and `paper_contract.py` **are already on disk**. Their `FACTS`
  and `DECLARATIONS` tuples are landed code this design reads and depends on, not an
  interface to assume. Only `paper_graph.py`, `paper_readiness.py` and the CLI's Phase 2
  verbs remain pending.
- `insumos-observer` is the first agent of this *build*, not of this repository. Seven
  agents already exist under `.claude/agents/`, and `tests/test_agents.py` enforces their
  contract — which is what surfaced the `OBJECTIVE_FLOW` seal above.
