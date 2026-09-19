# Design: A Fact Is Declared Or It Is Produced

## Technical Approach

`produces_facts` joins the header grammar at **both levels** (section and block), the shape `after`
and `mode` already established. Its entry shape is byte-identical to `requires_facts` —
`{value, source:{file, quote}}` — so `paper_contract._normalize_requirement_entry` parses it
unchanged and `paper_graph._verify_requirement_transcription` anchors it by adding one member to
its own `("requires_facts", "requires_declarations")` tuple. One shape, one parser, one verifier.

WHICH facts are produced is never an engine tuple: it is read off the corpus (settled decision 1).
The engine owns only the *declarable* route it already owns —
`paper_declarations.OBSERVABLE_FACTS ∪ STRUCTURAL_FACTS`. Every fact therefore has exactly one
satisfaction route, and the two new corpus invariants are stated against those two sets.

## Architecture Decisions

### A — A produced fact's value is its producer's written block body

| Option | Tradeoff | Decision |
|---|---|---|
| Whole producer body, sliced by `paper_block.parse` marker pairs | The exact slice `paper_coupling_evidence.gather` already builds; no second parser | **Chosen** |
| A located span inside the body | Needs a new sub-grammar and a third transcription discipline | Rejected |
| A separately declared value | Two texts drift; only one is in the paper (operator ruling) | Rejected |

Unwritten producer ⇒ no value, fact unsatisfied, consumer `blocked` **naming the producer**.
Multi-producer facts yield one body *per producer*; nothing is ever concatenated or merged.
No new verb prints the text: the producer's qualified id is the pointer, `main.tex` is the text.

**The one live value consumer**, measured: `related-work.rw-synthesis-artefact`'s
`figure.components_from: "contributions"` resolves through `paper_declarations.read_fact`
(`paper_cli._resolve_expected_components`) — i.e. it demands `declare --fact contributions`, the
very pre-authoring this change refuses. It is repointed at the producer's body, read through a
`\item` extraction promoted from `paper_verify`'s private `_ITEM_RE` to a public
`item_lines(body) -> list[str]` (allowlist still `{"re"}`, still writes nothing), so
`check_contribution_list` and the Components Check share one definition. Both existing codes are
reused verbatim: `COMPONENTS_FACT_UNRESOLVED` (no producer body yet),
`COMPONENTS_FACT_NOT_A_LIST` (body yields no items). Roster unmoved.

### B — Anchoring is the existing requirement-transcription lock

`paper_contract.parse(data: bytes)` holds no path and cannot tell a self-file quote from a
cross-file one; `assemble_corpus` holds every header and every body and already owns exactly this
check for `requires_facts`. `produces_facts` joins that loop — same `quote_in_body`, same
`SPAN_NOT_IN_SOURCE`, no new discipline. Section-level entries are walked alongside block-level
ones, the way `_verify_mode_transcription` already walks both.

`BlockRecord` gains `produces_facts: tuple = ()` — **defaulted**, so every existing construction
site and fixture stays green. `ContractHeader` gains the section-level list the same way.

### C — Ordering is VERIFIED, never derived

| Option | Tradeoff | Decision |
|---|---|---|
| Derive an `after` edge per producer→consumer | Manufactures unanchored edges and can invent an `ORDER_CYCLE` the hand-written corpus does not have | Rejected |
| Refuse unless the producer **reaches** every consumer in `collect_edges`' graph | Every edge stays hand-transcribed and quote-anchored; a cycle can only come from the corpus | **Chosen** |
| Require a *direct* edge | Refuses orderings already guaranteed transitively; 13 corpus edits instead of 5 | Rejected |

The traversal is an iterative DFS over `_build_graph`'s `successors` with a visited set —
**cycle-tolerant by construction**, so a cyclic corpus still refuses `ORDER_CYCLE` at
`derive_order`/`derive_waves` and never hangs or refuses something else here.

Measured on the live corpus: 13 producer→consumer pairs are unbacked today; reachability closes
all 13 with **five** new `after` edges (`related-work` ← `introduction.block-2`;
`experimental-setup.es-assessment` ← `introduction.block-3`; one edge each into
`results-and-discussion` and `conclusions` from `introduction.block-4b`; `conclusions` ←
`limitations`). Each carries its quote and one `### Internal chain` row.

### D — Totality is relative to consumption

A produced-class fact that **some block requires** must have a producer in that same corpus.
A fact nobody requires needs no producer — it is simply absent from this paper, legally.
`skeleton` (structural) and the five observable facts stay declarable and are never produced;
a `produces_facts` entry naming one of them refuses **route ambiguity**. The DECLINED state is
untouched: `experimental-design` is observable, so declining it is unaffected; declining a
*produced* fact is refused by the same guard that refuses declaring one.

This scoping is deliberate. An unconditional totality invariant in `assemble_corpus` is precisely
what broke every raw-header fixture in the previous change; consumption-relative totality fires on
the real corpus and leaves minimal fixtures alone.

### E — Satisfaction and readiness

`paper_readiness.compute_block_readiness` stays pure and keeps its shape: the caller passes
`produced_by: dict[fact, tuple[qualified_id]]`, exactly the pure-input pattern `declined_facts`
and `opened_blocks` already use, and `produced_by=None` reproduces today's behaviour byte for byte.
A produced fact counts satisfied when **every** producer block is in `opened_blocks` — the same
"opened is written" rule the wave gate already uses; provenance currency stays out of it, for the
reason `compute_phases` already recorded (blocking writing on a documentation gap). The result dict
gains `blocked_on_produced` naming the producer, mirroring `declined_facts`/`stale_declines`.

`paper_declarations.set_fact`/`decline_fact` gain `produced_by: tuple = ()` and refuse when it is
non-empty — enforced **in the module**, the precedent `DECLINE_REASON_REQUIRED` set, so no caller
escapes it. `cmd_declare` resolves the corpus and supplies it.

### F — `check_gap` pairs PRODUCERS, not consumers

`_blocks_by_fact`'s existing semantics are **not** touched: `check_chain` does
`zip(block_ids, links)`, so widening that mapping would silently misalign links to blocks.
`Evidence` gains a separate `producers_by_fact`, and only `check_gap` reads it.

Coupling 3 is "the gap is stated in two places and they must agree". The two places are the two
blocks that *state* it. `introduction.block-3`'s own contract says **"The closing is the joint
gap"** and **"this gap and that section's closing gap say the same thing at different depths"** —
block-3 authors the gap, it does not receive it. **Operator ruling (confirmed):** `gap` has TWO
producers, `related-work.rw-closing` (develops it) and `introduction.block-3` (condenses it); both
author it, neither receives it. `experimental-setup.es-assessment` is the single true *consumer*
(it needs the gap's text to justify a purpose-built corpus, via `requires_facts`) and is correctly
excluded from the pair. So the pair derives as *the producers of `gap`* = (`rw-closing`,
`introduction.block-3`), `len(block_ids) != 2` survives untouched, and no literal block id appears
anywhere.

This settles **decision 2** as amended: `introduction.block-3` takes `produces_facts: [gap]`, not
`requires_facts: [gap]`. It also amends `fact-production`'s "Exactly One Producer Per Fact"
requirement (retitled "Every Producer Is Either Sole Or Corroborated"): a fact resolves to more
than one block producer only when an existing coupling-verification check names that exact pair as
the two sides it verifies agree — `gap` and Coupling 3, today the only such pair. Every other
duplicate producer still refuses `FACT_PRODUCER_DUPLICATE`. Corroboration is checked structurally
(does a coupling-verification check name this exact pair?), never by a hand-listed exception list
of fact ids.

A coupling naming a fact nobody produces cannot reach this code: consumption-relative totality
refuses at assembly, and `_blocks_by_fact` already maps a refusing assembly to the existing
`SECTION_CONTRACTS_UNREADABLE`. No new `UNMEASURED_REASONS` member.

## Data Flow

    sections/*.md ──parse──▶ ContractHeader{produces_facts}
          │                        │
          │                  assemble_corpus ──▶ transcription · route exclusivity
          │                        │              totality · production ordering
          ▼                        ▼
    main.tex opened ids ──▶ caller resolves produced_by / satisfied
                                   │
                    ┌──────────────┼───────────────┐
              readiness/phases   declare       verify(gather)
              blocked_on_produced  refuses     producers_by_fact ─▶ check_gap

## File Changes

| File | Action | Description |
|---|---|---|
| `scripts/paper_contract.py` | Modify | `produces_facts` in `_TOP_LEVEL_OPTIONAL`/`_BLOCK_OPTIONAL`, parsed by the existing entry normalizer |
| `scripts/paper_graph.py` | Modify | `BlockRecord.produces_facts`; transcription loop widened; self-reference, duplicate-producer, route-exclusivity, totality and reachability checks |
| `scripts/paper_declarations.py` | Modify | `set_fact`/`decline_fact` refuse a produced fact |
| `scripts/paper_readiness.py` | Modify | `produced_by` input, `blocked_on_produced` output |
| `scripts/paper_cli.py` | Modify | Resolve `produced_by` for `readiness`/`phases`/`declare`; repoint `_resolve_expected_components` |
| `scripts/paper_verify.py` | Modify | `item_lines` made public; `check_gap` reads `producers_by_fact` |
| `scripts/paper_coupling_evidence.py` | Modify | `Evidence.producers_by_fact` |
| `sections/*.md` (7 of 10) | Modify | `produces_facts`, five `after` edges, chain rows, produced-fact rows moved out of `### External inputs` |
| `tests/*.py` | Modify | Red-first mutation proofs; roster bidirectionality |

The `### External inputs` → `### Internal chain` row moves preserve each sentence verbatim, so the
51 live quote anchors survive the move — `quote_in_body` is a whole-body substring check. No new
"row in the right table" checker is added; that would be a third direction and another refusal.

## Refusal Codes — six genuinely new conditions, names NOT invented here

Checked against the live roster first. Reused verbatim: `MALFORMED_HEADER`, `UNKNOWN_FACT`,
`SPAN_NOT_IN_SOURCE`, `ORDER_CYCLE`, `SECTION_CONTRACTS_UNREADABLE`, `COMPONENTS_FACT_UNRESOLVED`,
`COMPONENTS_FACT_NOT_A_LIST`.

| # | Condition | Nearest existing code | Verdict |
|---|---|---|---|
| 1 | A block produces and requires the same fact | none | new |
| 2 | Two *uncorroborated* producer declarations for one fact | none | new |
| 3 | A *required* produced-class fact with no producer | none | new |
| 4 | `produces_facts` names a declarable (observable/structural) fact | `UNKNOWN_FACT` — but the fact IS known | new |
| 5 | A producer does not reach one of its consumers | `CHAIN_ROW_UNBACKED` — its subject is a table row, not a header field | new |
| 6 | `declare --fact`/`--decline` targets a produced fact | `DECLARATION_FIXED` — different condition | new |

Per the parallelism warning, **names are reported, not chosen**: `sdd-spec` and this design must
agree on six subject-first names before `sdd-tasks`. Roster arithmetic is measured with
`reachable_paper_refusal_codes()` from 127, never forecast.

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | Entry shape, route exclusivity, self-reference, duplicate producer | Direct `Refused` assertions on synthetic headers |
| Unit | Reachability over a cyclic graph | A corpus with a real cycle must still refuse `ORDER_CYCLE` at `derive_order` and must not hang here |
| Mutation | Every one of the six refusals | `_run_against_mutant` (`tests/paper_mutation.py`): break the guard, watch the named test go red |
| Mutation | Anchoring | Fabricate a `produces_facts` quote; `SPAN_NOT_IN_SOURCE` must fire |
| Integration | `check_gap` | Assert the published sides are exactly `rw-closing` and `introduction.block-3` against the real corpus |
| Integration | Components Check | With `contributions` never declared and `block-4b` written, the check must resolve; with it unwritten, `COMPONENTS_FACT_UNRESOLVED` |
| Regression | `check_chain`/`check_contribution_list`/`check_future_work` | `blocks_by_fact` unchanged — link/block alignment asserted explicitly |
| Roster | Bidirectional | `reachable_paper_refusal_codes()`; both paper suites green under `unittest` |

Every mutation must be one a weaker lock survives, and the anchor count must be asserted — a
`git diff --stat` does not prove an untracked fixture mutated.

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or
process-integration boundary. Stdlib-only, keyless, fail-closed, `Refused(code, detail)`/exit 2,
no `--force`, no `subprocess` (`paper_latex.py`'s reserved exception is untouched).

## Migration / Rollout

**Unit 2 is atomic and cannot be split.** Totality and production ordering are corpus-wide the
instant a producer exists, so the grammar, the corpus edits and their fixtures land together — the
exact failure the previous change hit when a corpus-wide invariant went unconditional ahead of the
files it judged. Unit 1 (grammar, parser, transcription, self-reference, duplicate, route
exclusivity) is strictly additive and ships green on an unedited corpus, because an absent
`produces_facts` parses to `[]`. Unit 3 (readiness, `declare`, `check_gap`, Components Check)
follows unit 2. Rollback is a branch revert: no region format, digest, or on-disk state changes.

`400-line budget risk: High` for unit 2 (7 section files plus fixtures) — `sdd-tasks` forecasts it.

## Open Questions

None open. Both resolved during reconciliation (`sdd-apply` unit 0, against `tasks.md`):

- **Settled decision 2 amendment** (Decision F): confirmed by operator ruling — `gap` has two
  corroborated producers, `related-work.rw-closing` and `introduction.block-3`;
  `FACT_PRODUCER_DUPLICATE` carries a corroboration carve-out for exactly this kind of pair.
- **Six refusal-code names**: finalized against the measured 127-code roster —
  `FACT_SELF_REQUIRED`, `FACT_PRODUCER_ABSENT`, `PRODUCER_CHAIN_ABSENT`,
  `PRODUCED_FACT_UNDECLARABLE` (all verbatim), `FACT_PRODUCER_DUPLICATE` (kept, redefined to fire
  only on an uncorroborated duplicate), `FACT_ROUTE_AMBIGUOUS` (condition 4, a `produces_facts`
  entry naming a declarable fact).
