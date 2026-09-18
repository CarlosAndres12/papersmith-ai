# Design: The Phases Are Derived, Not Remembered

## Technical Approach

Nothing is carried. Every dependency is a quote-anchored `after` edge inside a contract header, re-read and re-verified on every call; every phase is recomputed from those edges; both skeleton decisions are recomputed from the block ids opened in `main.tex`. The one genuinely new algorithm is wave grouping. Everything else is normalization plus transcription over machinery that already exists — `paper_contract.quote_in_body`, `paper_graph._resolve_target`, `paper_block.open_block`, `paper_style.resolve_style_set`, `paper_leak`'s tripwire.

The comparison the repository never made — header half vs prose half — lands in exactly one place: `paper_graph.assemble_corpus` already holds every header AND every prose body in the same call (`bodies`, built for `_verify_after_transcription`). A sibling `_verify_internal_chain` reads both from that same dict, costing zero extra disk passes.

## Architecture Decisions

### D1 — The name→id mapping lives in the row, or nowhere

**Choice.** Normalization rewrites each `## Inputs` table into `### External inputs` (dependency = a fact id) and `### Internal chain` (dependency = another block). Both tables' cells OPEN with the qualified id in backticks; the prose name survives as a gloss after an em dash: `` `introduction.block-4b` — what each contribution introduces ``. The reader consumes the leading backticked token and never reads the gloss. `_verify_internal_chain` refuses `CHAIN_ROW_UNRESOLVED` when that token is not a key of `corpus.blocks`, and `CHAIN_ROW_UNBACKED` when the row's dependency block has no `after` edge on the subject block. An unmapped row cannot be dropped silently — that silent drop is the failure this change exists to close.

| Option | Tradeoff | Decision |
|---|---|---|
| Qualified id in the row itself | Same vocabulary `after.target`, `order`, `open --block` already speak; one source | **Chosen** |
| A `name_map` object in the header | A second unanchored copy that drifts from the prose — the two-halves defect, reintroduced | Rejected |
| Fuzzy prose matching of names to ids | Silently drops an edge; unfalsifiable; precisely the failure mode above | Rejected |
| A separate `sections/_mapping.md` | A third file nothing else reads, tracked by nobody | Rejected |

**Composite parts (settled decision 5).** `5 partial` and `5 complete` are glosses on `introduction.block-5`. **`4a` and `4b` are NOT glosses** — the contract's own extent line ("Two physical paragraphs, 120-180 words in total") makes them two blocks, `introduction.block-4a` and `introduction.block-4b`, because their parts fall on opposite sides of `block-2` and one node manufactures an `ORDER_CYCLE` the writing order does not have. The union rule applies only where every part sits on the same side of every sibling. Several rows may carry the same id; their dependency sets UNION, so the node lands in the wave where its last input arrives. A composite sub-name never appears as an id anywhere.

**Rows whose subject is not a block** ("How many blocks Assessment has", "Whether the acronym appears", "The correct reading of an ambiguous equation") are structural decisions, not blocks. Normalization moves them out of both tables into ordinary prose under a `### Structural decisions` heading; they carry no id and generate no edge. A row left in a table without a resolvable id refuses.

### D2 — Waves beside `derive_order`, over one shared graph construction

**Choice.** Extract `_build_graph(corpus, edge_set) -> (successors, indegree)` from `derive_order`; `derive_waves(corpus, edge_set) -> list[list[str]]` reuses it, `_sort_key` for intra-wave ordering, and `_extract_minimal_cycle` + the existing `ORDER_CYCLE` code for termination. No second cycle extractor, no second sort key, no new refusal.

Invariants a test must hold:

1. `set(chain(*waves)) == set(corpus.blocks) == set(derive_order(...))`.
2. For every edge `(before, after)`: `wave_of(before) < wave_of(after)`.
3. Each wave is sorted by `_sort_key`; wave membership never depends on dict iteration or filename.
4. A cycle refuses `ORDER_CYCLE` with the identical detail string `derive_order` produces.
5. Flattened waves are **not** asserted equal to `derive_order`'s sequence — the min-heap holds nodes from several frontiers at once, so the two orders legitimately differ. Asserting sequence equality would be a false lock.

### D3 — `readiness` gains a basis; a new `phases` verb owns "what can I write now"

`cmd_readiness` never resolves `paper_dir`, so a bare call returns a plausible, stale answer. Both halves are kept, neither is allowed to be silent:

| Invocation | Behaviour |
|---|---|
| `readiness --paper <dir>` | Satisfied sets read from the `declarations` region (`paper_declarations.read_satisfied`, reusing `_read_declarations`/`_verify_not_hand_edited`/`_body_or_default` — no second region reader). `--fact`/`--declaration` union on top, each labelled `"source": "supposed"`. |
| `readiness --fact … --declaration …` (no `--paper`) | The hypothetical what-if preserved intact; payload carries `"basis": "supposed-only"`. |
| `readiness` with neither | Refuses `READINESS_BASIS_REQUIRED` (invocation-defect). The stale-number path is removed, not defaulted. |

`phases [--phase N]` reports waves 1..N with per-block readiness, `opened`, provenance state, and per-wave `complete|open|gated`; `--phase N` refuses `PHASE_NOT_READY` while any required block of waves 1..N-1 is unwritten. `compute_readiness` gains its second and third callers, closing the one-caller seam.

### D4 — The skeleton is inferred from disk, and the `skeleton` fact is left alone

**Choice.** Pure disk inference over `paper_block.read_status(paper_dir)["blocks"]`, intersected with the corpus:

- `relatedWork` = any opened id in `corpus.order_by_section["related-work"]`.
- `datasetPlacement` = `materials-and-methods` if `materials-and-methods.mm-dataset` is opened, `experimental-setup` if `experimental-setup.es-dataset` is opened, `undecided` if neither, and `DATASET_PLACEMENT_CONFLICT` (work-state) if both — the paper says two things and the skill will not pick one.

The existing `skeleton` fact is **not** used to carry either decision. It stays what it is: the gate `introduction.block-6` requires ("a skeleton exists"). Reusing it as the decision record would store an operator string that can drift from the opened ids — the exact defect this change closes, and the opposite of `paper_provenance.py`'s digest-and-recompute precedent. Two different questions, and only one of them is a fact.

`skeleton --related-work yes|no --dataset-in materials|experimental-setup` asks nothing itself (the orchestrator asks, once) and opens every non-excluded block id through `paper_block.open_block` in `derive_order` order — never a new writer, so the byte-identity invariant is untouched. It skips already-opened ids (idempotent) and refuses `SKELETON_ALREADY_DECIDED` when the flags contradict what is on disk; missing flags refuse `SKELETON_ANSWER_REQUIRED`.

**Disk reporting with ignores included.** `guidance/` is two levels deep: `guidance/<root>/<paper>/<paper>.md`. `read_registry` only enumerates the three roots, so eight ingested papers are invisible to it, and `fd`/`rg` report the tree empty because `.gitignore` carries `guidance/*/*`. New pure `paper_guidance.ingested_papers(guidance_dir)` walks with `Path.iterdir()`, which is gitignore-blind **by construction** — the mechanism, not an instruction — and `plan`/`packet` report `{root: [{folder, markdown}]}`. Measured today: 3 roots, 8 `.md`.

### D5 — The packet carries locators, never reference prose

**Choice.** `packet --section <stem> --block <id>` (read-only) emits one JSON object: the block's own contract prose verbatim (ours, safe), plus per ingested paper a heading OUTLINE — `{title, level, byte_start, byte_end}` — and nothing else. The `style-sampler` agent picks the equivalent heading, reads that span itself, and returns it; `paper_style.resolve_style_set` residency-verifies it into `R`; `paper_leak.check_tripwire` runs in `write` exactly as today. Nothing here replaces those three.

The leak guard is therefore structural: the packet is physically incapable of carrying reference prose, because it carries offsets. Rejected alternative — the packet inlines each extracted section's text — puts an unaudited copy of reference prose in a file the redactor can read without ever passing residency verification or the eight-token tripwire. That is the leak the operator flagged twice, written into the artifact.

**Segmentation, and the appendix it must not swallow.** `segment_markdown(body)` ends a section at the next heading of level **≤ its own** (never "the next heading of the same level" — that rule is what swallowed an appendix here before), and at EOF only when no such heading follows. A paper with no headings reports `"headings": []` with `"reason": "NO_HEADINGS"` — a reported state, like `unclassified`, never a silent empty outline. An unreadable `.md` refuses `GUIDANCE_MARKDOWN_UNREADABLE`.

### D6 — `optional` semantics

| Consumer | Meaning of `optional: true` |
|---|---|
| `derive_order` / `derive_waves` | Nothing. An optional block is an ordinary node; absence is a paper-state question, not a graph question. |
| `compute_readiness` | Adds `"optional"`, and a third status `not-applicable` when the block is optional AND unopened (declaration-backed basis only; under `supposed-only` it stays `writable`/`blocked`). Neither writable nor blocked: the paper excluded it. |
| `paper_verify` | A check whose derived block set is entirely optional-and-unopened reports `unmeasured`, reason `OPTIONAL_BLOCK_ABSENT` — a new `UNMEASURED_REASONS` member, not a refusal, so the roster count is unaffected by this row. |
| `phases` gate | Wave completeness ignores optional-and-unopened blocks. An optional block that IS opened is fully required. |

**An `after` edge targeting an absent optional block.** The edge stays in the graph (waves never move), and the GATE treats the absent target as satisfied-by-absence. `introduction.block-3 after related-work` with no Related Work opened: block-3 is writable in its wave. With Related Work opened: it waits. The graph is the contract; the gate is the paper. Only the gate reads disk.

Contract data changes: `es-dataset` added to `02-experimental-setup.md` (`optional: true`, mirroring `mm-dataset`); all five `rw-*` blocks become `optional: true`; `mm-proposal.requires_facts` drops `implementation`.

## Data Flow

    sections/*.md ──parse──▶ ContractHeader + prose body
          │                        │
          │                  _verify_after_transcription   (existing)
          │                  _verify_internal_chain        (new — same bodies dict)
          ▼
    assemble_corpus ──▶ collect_edges ──▶ derive_order   (unchanged, flat)
                                     └──▶ derive_waves   (new)
                                                │
    main.tex ─read_status─▶ opened ids ─────────┤
    declarations region ─read_satisfied─────────┤
    provenance region ──────────────────────────┤
                                                ▼
                                    phases / readiness --paper
                                    skeleton inference (relatedWork, datasetPlacement)

    packet ──▶ contract prose + heading outlines (offsets only)
                  └──▶ style-sampler ──▶ resolve_style_set ──▶ R ──▶ write ──▶ check_tripwire

## File Changes

| File | Action | Description |
|---|---|---|
| `sections/01,02,03,04,05,07,08,09,10-*.md` | Modify | `## Inputs` → `### External inputs` / `### Internal chain` / `### Structural decisions`; ids in every row; `after` edges transcribed; `es-dataset`; `rw-*` optional; `mm-proposal` facts |
| `.../scripts/paper_graph.py` | Modify | `_verify_input_partition`, `_verify_internal_chain`, `_build_graph`, `derive_waves` |
| `.../scripts/paper_readiness.py` | Modify | `optional`, `not-applicable`, satisfied-source labelling |
| `.../scripts/paper_declarations.py` | Modify | `read_satisfied`, skeleton inference helpers (pure, over `read_status` output) |
| `.../scripts/paper_guidance.py` | Modify | `ingested_papers`, `segment_markdown`, `GUIDANCE_MARKDOWN_UNREADABLE` |
| `.../scripts/paper_verify.py` | Modify | `OPTIONAL_BLOCK_ABSENT` reason; optional-aware block sets |
| `.../scripts/paper_cli.py` | Modify | `phases`, `skeleton`, `packet`; `readiness` basis; 8 roster entries; docstring `thirteen` → 20 |
| `.claude/skills/paper-writing/SKILL.md` | Modify | 17 → 20 verbs; `readiness` row; new verb tables and decision gates |
| `.claude/agents/insumos-observer.md`, `style-sampler.md` | Modify | Write-tool/shuttle mismatch; sampler consumes the packet's outline |
| `tests/test_paper*.py` | Modify | Roster count 96 → 104; new scenarios and mutations |

## Interfaces / Contracts

```python
# paper_graph.py
def derive_waves(corpus: Corpus, edge_set: EdgeSet) -> list[list[str]]: ...
def _verify_internal_chain(corpus: Corpus, bodies: dict) -> None:
    """CHAIN_ROW_UNRESOLVED / CHAIN_ROW_UNBACKED. Reads the SAME `bodies`
    dict `_verify_after_transcription` already holds — no second disk pass."""
```

Normalized row shape (parsed by leading backticked token only):

```markdown
### Internal chain
| Block | Depends on |
|---|---|
| `introduction.block-4b` | `introduction.block-2` — read backwards as the deficiency it resolves |
```

New refusal codes, classified for `REFUSAL_CLASSIFICATION` (bidirectional roster; `reachable_paper_refusal_codes()` moves 96 → **105**):

| Code | Class |
|---|---|
| `INPUT_PARTITION_ABSENT` | work-state |
| `CHAIN_ROW_UNRESOLVED` | work-state |
| `CHAIN_ROW_UNBACKED` | work-state |
| `READINESS_BASIS_REQUIRED` | invocation-defect |
| `PHASE_NOT_READY` | work-state |
| `SKELETON_ANSWER_REQUIRED` | invocation-defect |
| `SKELETON_ALREADY_DECIDED` | work-state |
| `DATASET_PLACEMENT_CONFLICT` | work-state |
| `GUIDANCE_MARKDOWN_UNREADABLE` | work-state |

`OPTIONAL_BLOCK_ABSENT` is an `UNMEASURED_REASONS` member, not a `Refused` — it moves no count.

## Testing Strategy

| Layer | What to test | Approach |
|---|---|---|
| Unit | `derive_waves` invariants 1–5 | Fixture corpora: zero edges (one wave), a chain (N waves), a cycle (`ORDER_CYCLE`) |
| Unit | `_verify_internal_chain` both refusals | Header/prose fixtures where the two halves disagree |
| Unit | `optional` in order / readiness / verify | One observable outcome change per consumer, asserted separately — never inferred from a sibling |
| Unit | `segment_markdown` | A fixture whose last section is a deeper-level appendix; the swallow must be red before the fix |
| Integration | `readiness --paper` changes answer after `declare` | Real region write, then re-read |
| Integration | `skeleton` → `phases` round trip | Open the skeleton, then recover both decisions from ids alone, no fact read |
| Read-only | `phases`, `packet`, `readiness` write nothing | Before/after content manifest over `paper_dir`, the `ReadOnlyTests` pattern |
| Mutation | Nine proofs below | `_run_against_mutant`, real subprocess, bytecode purged |

Mutations (break the guard, watch it fire — a passing assertion is not a mutation that ran; assert the anchor count):

1. Edit a transcribed chain quote in a contract → `SPAN_NOT_IN_SOURCE`.
2. Delete the `after` entry backing a chain row → `CHAIN_ROW_UNBACKED`.
3. Replace a row's id with its prose name → `CHAIN_ROW_UNRESOLVED`.
4. `derive_waves` appends to the current wave instead of the next → invariant 2 red.
5. `cmd_readiness` defaults the basis instead of refusing → `READINESS_BASIS_REQUIRED` red.
6. Skeleton inference reads `read_fact("skeleton")` instead of `read_status` → fixture where the two disagree goes red.
7. `packet` inlines span text instead of offsets → "no reference byte in the payload" red.
8. `segment_markdown` ends at the next SAME-level heading → appendix fixture red.
9. `phases`/`packet` write one byte → content-manifest guard red.

Plus the two bidirectional roster tests and the count assertion at `tests/test_paper_writing.py:3614`.

## Threat Matrix

| Row | Applicability |
|---|---|
| Shell / subprocess / process integration | **N/A** — `NoSubprocessScanTests` holds every script but `paper_latex.py` to zero; no new verb invokes an agent, and the hand-shuttle stays the only channel |
| Routing / VCS / PR automation | **N/A** — no verb touches git or a remote |
| Executable-file classification | **N/A** — every new read is Markdown or `main.tex` |
| Path containment | **Applicable** — `phases`, `skeleton`, `packet` take `--paper`/`--sections`/`--guidance`. Reuse `paper_scaffold.resolve_paper_dir`, `paper_contract.resolve_sections_dir`, `paper_guidance.resolve_guidance_dir`, `paper_cli._resolve_repo_path` verbatim; never a new containment check, never a new code for an existing condition. RED test: each new verb refuses `PAPER_OUTSIDE_REPOSITORY` / `SECTIONS_OUTSIDE_REPOSITORY` / `GUIDANCE_OUTSIDE_REPOSITORY` for a `../` operand and writes nothing |
| Write amplification into `main.tex` | **Applicable** — only `skeleton` writes, only through `paper_block.open_block`. RED test: mutating `skeleton` to write `main.tex` directly fails the byte-identity harness |

## Migration / Rollout

No data migration — nothing derived is persisted. Eleven chained PRs; waves are measured only after real edges land:

| # | Unit | Depends on | Budget risk |
|---|---|---|---|
| 1a | Normalize `01`, `02`, `05` | — | Med |
| 1b | Normalize `03`, `04`, `07` | — | Med |
| 1c | Normalize `08`, `09`, `10` (`06` already normalized) | — | Med |
| 2 | `es-dataset`, `rw-*` optional, `mm-proposal` facts | 1a–1c | Low |
| 4 | Chain → `after` transcription + both refusals | 1a–1c, 2 | High |
| 3 | `optional` across order / readiness / verify | 2 | Med |
| 5 | `derive_waves` | 4, 3 | Med |
| 6 | `readiness` basis + `phases` | 5 | Med |
| 7 | `skeleton` + disk inference + `ingested_papers` | 2, 3, 6 | High |
| 8 | `packet` + `segment_markdown` | 7 | Med |
| 9 | SKILL.md / `paper_cli` docstring / agent corrections | all | Low |

Every unit's definition of done includes the bidirectional `REFUSAL_CLASSIFICATION` edit and the roster count move for any code it introduces. `ask-on-risk`: units 4 and 7 need a delivery decision before apply.

## Open Questions

- [ ] Do all five `rw-*` blocks become `optional: true`, or does the whole-section conditionality want a section-level `optional` key? The design assumes block-level (no schema change); a section-level key is cheaper to read but widens `_TOP_LEVEL_ALLOWED`.
- [ ] `phases` completeness reads provenance `current` — a block written without `--contract` is `unprovenanced` forever and would gate its successors. Decide in unit 6 whether `unprovenanced` blocks count as written or hold the wave.
