# Design: The Tripwire Reaches The Section That Feeds It

## Technical Approach

Three shipped things are joined, and one shipped defect is corrected first.

1. `paper_style.strip_math` stops letting a `$$…$$` body through as prose — a correction to a
   guard that is already live, measured before it lands.
2. `paper_cli._resolve_write_gate` stops discarding the corpus it already assembles with
   `enforce_bindings=True`; a new `paper_source_span.py` turns each resolved
   `(fact, lineage, title)` triple into the bound section's own bytes; `BlockContract` gains
   `source_sections`.
3. `paper_leak` gains a SIBLING of `check_tripwire` — `check_source_section_verbatim` — wired
   into `paper_write.write_block`, refusing `SOURCE_SECTION_VERBATIM`.

The sibling adds no measurement machinery: the floor is `paper_leak.overlap_against_set`
(shipped) and the hit scan is `paper_leak.tripwire_spans` (shipped, and whose own docstring
already declares it "a pure measurement — never refuses on its own"). Only the threshold and the
refusal are new.

## Architecture Decisions

### A — The `$$` fence exclusion, its blast radius, and its slice

`_MATH_DISPLAY_RE` is substituted before `_MATH_INLINE_RE` in `strip_math`, so the fix is one
alternative added to the display pattern, which already carries `re.DOTALL`:

```python
_MATH_DISPLAY_RE = re.compile(
    r"\$\$.*?\$\$|\\\[.*?\\\]|\\begin\{(equation|align|gather|math)\*?\}.*?\\end\{\1\*?\}",
    re.DOTALL,
)
```

The new alternative carries no group, so `\1` still names the environment group; `_MATH_INLINE_RE`
is untouched, and an unpaired `$$` surviving the display pass still loses only its delimiters.

**The class, not the instance.** `paper_bindings._strip_math` carries the identical defect and
feeds `STRUCTURAL_CARRIES_CLAIM` through `_has_numeral`/`_has_comparative`/`_named_external_object`
— a display equation inside a structural sentence leaks its digits today. The same alternative
lands there in the same slice. The two implementations are NOT merged (`paper_bindings` is a
module-level import of `paper_write`; pulling `paper_style` in would drag `paper_evidence` and
`paper_guidance` behind it and break the local-import discipline `paper_leak` exists under).
Drift is held instead by a DERIVED sweep test: every module under `scripts/` exposing a callable
named `strip_math` or `_strip_math` is collected by introspection — never a two-item list — and
each must exclude a `$$` fence.

**Measurement M1 — the gate, and it runs on `main` before the regex moves.** For every ordered
pair `(styled, sample)` drawn from a committed fixture corpus of invented markdown
(`tests/fixtures/math_fence_corpus/`: a `$$` fence, an inline `$…$`, a `\[…\]`, a
`\begin{equation}`, an unpaired `$`, and plain prose), M1 records
`len(paper_style.normalize_tokens(styled))` and
`len(paper_leak.tripwire_spans(styled, [sample]))` and
`paper_leak.overlap_against_set(styled, [sample])`. The delta report names every pair whose
tripwire hit count changed and every file whose normalized token count changed.

| Gate condition | How it is satisfied |
|---|---|
| Blast radius is measured, not forecast | `openspec/changes/<this change>/math-fence-blast-radius.md` carries M1's before-table (run on an otherwise-unmodified tree) and after-table, both produced by executing M1 |
| No number in that file is authored | Every figure is copied from a run; the file states the command that produced it |
| The ambient half does not decide the gate | M1 is additionally run over whatever document-sourced `.md` this checkout happens to hold, recorded in the same file and explicitly marked `ambient, not asserted` — a fresh clone holds none, and an assertion over ambient counts is a machine-dependence defect this suite has already paid for once |

**It ships as the FIRST slice — this overrules the proposal's ordering**, which put the wiring
first. Two reasons: the before-table is only honest against a tree that is otherwise `main`, and
the threshold in Decision C is computed over the SAME normalization, so calibrating it before the
fence exclusion lands would calibrate it against equation bodies counted as prose.

### B — The check is a sibling, not an extension of `check_tripwire` (confirmed)

| Option | Tradeoff | Decision |
|---|---|---|
| Sibling `check_source_section_verbatim`, new code, reusing `overlap_against_set` + `tripwire_spans` verbatim | The two thresholds stay tunable apart; the shipped function's bytes do not move, so M1's after-table is the only thing that changes about `STYLE_OVERLAP` | **Chosen** |
| Extend `check_tripwire` with an extra sample source | `style-leak-detection` spec, `Requirement: Overlap Reads Only The Recorded Sample Set`, forbids `STYLE_OVERLAP` comparing against a reference file read directly — which is exactly where the bound section's bytes come from. Extending would break a shipped requirement, not merely overload a function | Rejected |
| Per-sentence, inside `paper_bindings` | Verbatim copy spans sentence boundaries; the shape is wrong | Rejected |

### C — The threshold for a same-author source (ruled)

For each bound section `S_i` of block `B`:

```
floor_i     = overlap_against_set(contract_prose, [S_i])     # shipped, same normalization
threshold_i = max(floor_i, SOURCE_RUN_BACKSTOP)
refuse when longest shared run(draft, S_i) > threshold_i     # strict; equality passes
```

**Why the floor is the contract prose.** It is same-author, same-subject, quote-anchored to that
source, and it is not the draft — the only text in play that already demonstrates how long a run
this author legitimately shares with this section. Eight was calibrated against an INDEPENDENT
paper and does not transfer; the three-draft register proof does not transfer either, because a
same-author document has no unstyled control.

**No upper clamp on the floor, deliberately.** A contract that itself carries a 40-token run from
the source has licensed that run: a draft carrying it is the redactor obeying its contract, which
is `paper_audit`'s subject, not this guard's. The cost is that such a contract makes this guard
inert for that block — so the floor is REPORTED in every `write` envelope (Decision E), never
inferred.

**`SOURCE_RUN_BACKSTOP = 16`, and it is a ruling, not a measurement.** Saying so is the point: a
threshold nobody can argue with is a threshold nobody measured. The argument for 16: the shipped 8
is deliberately sub-clause, because for an independent paper a shared clause is already
suspicious; for the same author's earlier text about the same work a shared clause is ordinary, and
the unit that means "copied" is a sentence. 16 normalized tokens sits at the low end of an academic
sentence. It is set at the permissive end on purpose — a false refusal blocks the paper at `write`,
a false pass still faces contract-audit and a human.

**What would falsify it** (executable the moment three real bindings exist, and recorded as an
obligation in `tasks.md`, not as a hope):

- A transposed draft — same claim, the paper's own register — whose longest shared run with its
  bound section reaches 16. Then 16 is too low.
- A sentence pasted verbatim out of the bound section whose normalized run is under 16 and passes.
  Then 16 is too high.
- Either observation moves ONE named constant in `paper_leak.py`, and nothing else.

### D — A transposition block is identified by derivation, never by a list

`cmd_write` already computes `mode` from `paper_contract.resolve_mode(header, block)` — the same
derivation `MODE_ABSENT` rests on. `paper_vocabulary` gains `MODE_TRANSPOSITION = "transposition"`
and `MODE_ARGUMENT = "argument"`, with `MODES = (MODE_TRANSPOSITION, MODE_ARGUMENT)` — one literal,
one place, and no string literal for a mode enters `paper_write` or `paper_leak`. The guard runs
when `contract.mode == paper_vocabulary.MODE_TRANSPOSITION`. No block id, no section title, no
list.

Scope ruling: `argument`-mode blocks are NOT checked this change. The threshold's whole
justification rests on transposition semantics ("carry the source into the paper's own style"); a
verbatim run inside an argument block is a quotation question. Widening is a follow-up with its own
calibration, named here so it is not mistaken for an oversight.

### E — Where the resolved bindings reach `write`, and it is its own slice

`_resolve_write_gate` returns the `Corpus` it already builds (its signature today is `-> None`;
note that the archived predecessor's own File Changes row already claimed it "returns the corpus so
`cmd_write` reports it" — the claim shipped, the return value did not). `cmd_write` then calls
`paper_source_span.resolve_bound_sections(corpus, qualified_id)` and fills
`BlockContract.source_sections`.

Resolution and disk reading stay in the CLI; `write_block` receives plain text, so
`BlockContract`'s own "never touches disk itself" contract holds unchanged.

**Reconciling with the concurrent change — the applier must NOT duplicate.**
`the-whole-cut-is-argued-before-any-section-is-claimed` applies first and its own Affected Areas
row states `paper_graph.py | Modified | Per-title resolution/memo reused by the verb, not
duplicated`. `paper_source_span.py` therefore CALLS that landed per-`(root, lineage)` resolution
and adds only the byte slice. Its requirement of that memo: it must carry
`(revision_path, segment_markdown outline)` — the outline, not just `{title: count}`, since counts
derive from the outline and byte offsets do not derive from counts.

If that extraction has not landed callable when this change applies, the applier **stops and
reports**. It does not re-walk `FACT_SOURCE_ROOT → source_root_status → resolve_lineage /
resolve_ingested_document → segment_markdown` into a second implementation, and it does not edit
`paper_graph.py`. A duplicated hop chain is the defect this repository has already recorded under
"fixed the instance, never swept the class".

## Data Flow

    cmd_write
      └─ _resolve_write_gate ─(enforce_bindings=True)─▶ Corpus ──┐   [WU1: no longer discarded]
                                                                │
      paper_source_span.resolve_bound_sections(corpus, block) ◀──┘
           └─ paper_graph's landed per-(root,lineage) memo ─▶ (path, outline)
                └─ bytes[byte_start:byte_end] ─▶ ({fact, lineage, title, path, text}, …)
                                                          │
      BlockContract(mode=…, contract_prose=…, source_sections=…)
                                                          │
    write_block
      readiness ─▶ evidence-audit ─▶ contract-audit ─▶ [style tripwire] ─▶ [source fidelity] ─▶ substitute
                                                         STYLE_OVERLAP      SOURCE_SECTION_VERBATIM

Placement is deliberate: after contract-audit, before `substitute`, beside the style tripwire, and
AFTER it, so a draft failing both always names `STYLE_OVERLAP` deterministically. The ledger is
written only on the audit-fired branch, so a refusal here burns no judge-cycle attempt.
`_attempt_key` is NOT widened with the bound sections — that would reset every in-flight ledger;
the residual (a new source revision does not reset the attempt ledger) is pre-existing and recorded,
not silently changed.

## Interfaces / Contracts

```python
# paper_source_span.py (new)
def resolve_bound_sections(corpus, qualified_block_id: str) -> tuple:
    """One entry per (fact, lineage, title) triple this block's own
    BlockRecord.source_bindings names, under a MEASURED root:
    {"fact", "lineage", "title", "path", "byte_start", "byte_end", "text"}.
    A block with no bindable measured fact returns () -- reported by the
    caller as unmeasured, never silently passed."""

# paper_leak.py (sibling of check_tripwire, same module, separate threshold)
SOURCE_RUN_BACKSTOP: int = 16

def source_section_floor(contract_prose: str, section_text: str) -> int: ...
def check_source_section_verbatim(draft_latex: str, contract_prose: str, sections) -> dict:
    """Per section: threshold = max(floor, SOURCE_RUN_BACKSTOP); refuses
    SOURCE_SECTION_VERBATIM on the first run strictly exceeding it, naming
    the block's bound fact, the lineage, the section title and the span.
    Returns the per-section report when nothing exceeds."""

# paper_write.BlockContract
source_sections: tuple = ()   # defaulted -- the produces_facts/source_bindings precedent
```

`write_block`'s envelope gains `sourceFidelity`, mirroring `styleChannel`'s shipped
`unmeasured`/`measured` shape exactly rather than inventing a second reporting convention:
`{"status": "unmeasured"}` when the block binds no measured section, otherwise
`{"status": "measured", "sections": [{"lineage", "title", "floor", "threshold", "longest_run"}]}`.
"The guard is off for this block" is always on screen, and the floor that decided is always
readable.

## Refusal Codes

| Code | Condition | Tier |
|---|---|---|
| `SOURCE_SECTION_VERBATIM` | A transposition draft's longest normalized run with a bound section strictly exceeds `max(floor, SOURCE_RUN_BACKSTOP)` | work-state |

Exactly one. Every neighbouring condition already has a home: an unbound bindable fact is
`SECTION_BINDING_ABSENT` at the gate; a title that is not a heading is `SECTION_NOT_IN_SOURCE`; an
unresolvable lineage is `SOURCE_LINEAGE_UNRESOLVED`; an empty or absent bound section is
**reported** `unmeasured`, never refused — a paper at an earlier stage is not a fault, the reading
`source_roots` already established.

The post-change roster is re-measured by executing `reachable_paper_refusal_codes()` after the code
lands. The live figure today is **144**; no post-change count appears anywhere in this design.

## File Changes

| File | Action | Description |
|---|---|---|
| `scripts/paper_style.py` | Modify | `$$…$$` alternative in `_MATH_DISPLAY_RE` |
| `scripts/paper_bindings.py` | Modify | The identical alternative in its own `_MATH_DISPLAY_RE` (class sweep) |
| `scripts/paper_source_span.py` | Create | Triple → bytes; calls the landed memo, slices, never re-resolves |
| `scripts/paper_cli.py` | Modify | `_resolve_write_gate -> Corpus`; `cmd_write` fills `source_sections`; one `REFUSAL_CLASSIFICATION` entry |
| `scripts/paper_write.py` | Modify | `BlockContract.source_sections`; the new stage; `sourceFidelity` in the envelope |
| `scripts/paper_leak.py` | Modify | `SOURCE_RUN_BACKSTOP`, `source_section_floor`, `check_source_section_verbatim` |
| `scripts/paper_vocabulary.py` | Modify | `MODE_TRANSPOSITION`/`MODE_ARGUMENT` named once; `MODES` composed from them |
| `.claude/skills/paper-writing/SKILL.md` | Modify | Roster entry for the new code; the new `write` stage |
| `tests/fixtures/math_fence_corpus/` | Create | Invented markdown, no product name |
| `tests/test_paper_writing.py`, `test_paper_contract.py` | Modify | Red-first units, the eight mutations, the end-to-end `write` session |
| `openspec/changes/<this change>/math-fence-blast-radius.md` | Create | M1 before/after, executed |
| `scripts/paper_graph.py` | **Read only** | The concurrent change owns it — no edit is planned here |

Nothing is deleted.

## Testing Strategy

| Layer | What to test | Approach |
|---|---|---|
| Unit | `$$` body excluded; `\1` still names the environment group | Direct `strip_math` assertions on the fixture corpus |
| Unit | Every `strip_math`/`_strip_math` in `scripts/` excludes a fence | Derived introspection sweep, never a two-item list |
| Unit | `floor` rises with a contract that shares a long run; threshold is `max(floor, backstop)` | Invented contract prose + invented section text |
| Unit | Triple → bytes returns the section's own span | `segment_markdown` offsets against a `bind`-recorded fixture |
| Integration | A verbatim paste refuses at `cmd_write`; a transposed draft passes | Full `bind` → `write` session, invented lineage and titles |
| Integration | An `argument`-mode block with the same binding does not refuse | Same fixture, mode flipped in the contract on disk |
| Integration | A block with no measured binding reports `sourceFidelity: unmeasured` | Minimal fixture corpus, no source base |
| Mutation | Eight mutations below | `tests/paper_mutation.py::_run_against_mutant`, anchor count asserted |
| Generality | No block id, section title, document filename or paper id under `.claude/skills/` or `tests/` | `ForgeVocabularyDerivedGuardTests.derived_denylist` (+ `paper_product_root_words`) — **a gate before apply**, comments, docstrings and fixtures included |
| Roster | Bidirectional, re-measured live | `reachable_paper_refusal_codes()`; `npm test` AND `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` |

**Mutation per claim** — each is a mutation a weaker lock survives:

| Claim | Mutation | Must go red |
|---|---|---|
| `SOURCE_SECTION_VERBATIM` is reachable | `min_tokens=threshold + 1` → `min_tokens=10_000` | the verbatim-paste `write` test |
| The floor is load-bearing | `max(floor, SOURCE_RUN_BACKSTOP)` → `SOURCE_RUN_BACKSTOP` | the high-floor test (a contract-licensed run must pass) |
| The back-stop is load-bearing | `max(floor, SOURCE_RUN_BACKSTOP)` → `floor` | the near-zero-floor test (a 6-token idiom must not refuse) |
| It fires inside `write`, not a read-only verb | the new stage's call line → `pass` | the `cmd_write` end-to-end refusal test |
| The resolved bindings really arrive | `source_sections=bound_sections` → `source_sections=()` | the same end-to-end test |
| Mode is derived, not assumed | `MODE_TRANSPOSITION` → `MODE_ARGUMENT` at the stage guard | the transposition test AND the argument-passes test |
| `$$` exclusion is real | drop the `\$\$.*?\$\$|` alternative in `paper_style` | the display-fence unit |
| The class was swept | drop the same alternative in `paper_bindings` | the derived cross-module sweep |

## Work Units

| Unit | Content | Est. lines | Green alone |
|---|---|---|---|
| **WU0** | M1 harness + fixture corpus, before-table on an unmodified tree, `$$` fix in `paper_style` AND `paper_bindings`, derived sweep, after-table, `style-leak-detection` spec delta | ~250 | yes |
| **WU1** | `_resolve_write_gate -> Corpus`; `paper_source_span.py`; `BlockContract.source_sections`; `cmd_write` wiring; `sourceFidelity` reported as `unmeasured`/resolved, no verdict yet | ~295 | yes |
| **WU2** | `SOURCE_RUN_BACKSTOP`, `source_section_floor`, `check_source_section_verbatim`, the `write_block` stage, `MODE_TRANSPOSITION`, `REFUSAL_CLASSIFICATION`, `SKILL.md`, six of the eight mutations | ~355 | yes |
| **WU3** | Neutrality audit as a gate, roster re-measured live, both suites, the falsification obligation recorded | ~150 | yes |

Estimated total **~1050 changed lines** against the owner-raised **1200** budget.

```
Decision needed before apply: No
Chained PRs recommended: Yes
400-line budget risk: High
```

Against the owner-raised 1200 the risk is Medium; against the default 400 it is High, so the four
slices ship chained: WU0 → WU1 → WU2 → WU3, each targeting its predecessor's branch.

**WU0 is the gate for everything after it.** WU1 may not open until
`math-fence-blast-radius.md` carries both executed tables.

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or
process-integration boundary. Stdlib-only, offline, fail-closed, `Refused(code, detail)`, no
`--force`. No `subprocess` import joins `scripts/`; the AST scan (`NoSubprocessScanTests`) is
unchanged and remains a gate.

## Migration / Rollout

No on-disk format, digest, generation counter or marker grammar changes. An existing
`paper/main.tex` and every `bind`-recorded binding stay readable by the prior revision.
`BlockContract.source_sections` is defaulted, so every existing construction site stays green.
Reverting the branch restores the shipped tripwire's measured prior behaviour, which
`math-fence-blast-radius.md`'s before-table names exactly. Nothing is deleted.

## Open Questions

- [x] None blocking. Three things were ruled here rather than deferred, and all three landed: the
      fence exclusion and its gate (A, WU0), the same-author threshold and its falsifier (C, WU2),
      and where the resolved bindings reach `write` (E, WU1). WU3 re-measured the roster
      (`reachable_paper_refusal_codes()` reports **153**, `SOURCE_SECTION_VERBATIM` present),
      re-ran the generality sweep (empty, scoped to this capability's own surface), and confirmed
      the falsification obligation below is recorded rather than silently waived.
- [ ] Recorded, not folded in, still out of scope after WU3: verifying that a transposition block
      asserts only what its bound section carries; widening the check to `argument` mode;
      `_attempt_key` not resetting on a new source revision. None of the three is silently
      resolved by this change — each remains a named follow-up.
