# Proposal: No Claim Without a Source That Holds It

## Intent

**Problem.** A writer with no evidence channel invents citations, and invents them
*well* — correct authors, plausible year, well-formed key — which is what makes the
failure survive review. Phases 1 and 2 gave the skill a place to write and a contract
saying what each block owes; neither gives it one sourced fact.

**Why now.** Phase 4 is the writer. Build it before the channel it draws from and the
channel becomes a retrofit onto prose already written.

**Success.** Every cited sentence traces to a verbatim span of an ingested source, and a
citation whose source does not support it is *rejected by execution*, not by review.

## The governing rule

Search comes first, always. What varies is the **query**, and the contract's `citations`
field selects it. The skill reads the regime; it must not know it. No section id, block
id, density number or placement rule may appear in skill code.

| Regime | Query | Cites | Placement |
|---|---|---|---|
| `discovery` | open search by topic | claims about the field | end of the sentence it supports |
| `resolution` | targeted lookup, named object | objects (estimators, baselines, datasets) | attached to the object, wherever it sits |
| `none` | none | nothing | n/a |

**Placement dispatches on regime.** `sections/01-materials-and-methods.md`: *"The citation
attaches to the object it credits, wherever that object sits in the sentence. This differs
from the introduction, where the citation supports a claim and therefore closes the
sentence."* End-of-sentence is the `discovery` rule (`05-related-work.md` Citations;
`06-introduction.md` conventions). One universal rule would reject every correct methods
citation.

**The noun-phrase prohibition is `discovery`-only.** Only `05` and `06` state it. Under
`resolution` a noun-phrase citation *is* attaching to the object it credits; applying the
prohibition there would fight the methods contract.

## Scope

### In Scope

- **Connector roles, not names.** `papersmith.yaml` maps `discovery` / `resolution` /
  `full-text` to connectors. Adding one is a config edit, never a code edit.
- **The split by role** (below): discovery agent-side, resolution CLI-side.
- **Named refusals.** `DISCOVERY_UNAVAILABLE`, `RESOLVER_UNREACHABLE`. An unreachable
  endpoint and an empty result set are different facts and never share a code. A `none`
  block stays writable with zero connectors reachable.
- **Ingestion routing, `paper-ingestion` unchanged.** Evidence PDFs land in
  `guidance/<section-id>/`; its `source_base: guidance` discovery already promotes any
  child holding a loose PDF to a source root. No parallel pipeline.
- **The evidence set.** Per claim↔source pair: claim text, citation key, resolved DOI +
  resolver + metadata digest, **and a verbatim quoted span of the ingested `.md` with its
  locator**. Without the span the verdict is an unfalsifiable opinion; with it, a
  measurement anyone can re-check.
- **`paper/refs.bib` built from resolved metadata**, each entry carrying provenance. No
  entry is ever typed. Plus `CITE_WITHOUT_ENTRY` / `ENTRY_WITHOUT_CITE`.
- **The validator.** `holds` / `does-not-hold` / `insufficient`. `insufficient` means the
  ingested text cannot decide — never a soft `holds`. It fails the citation and consumes
  an iteration exactly as `does-not-hold` does.
- **Regime-dependent placement**, the `discovery` noun-phrase rule, one sentence / one
  attributed claim.
- **The loop: three search rounds per block.** On exhaustion, `EVIDENCE_EXHAUSTED` reports
  the block **un-citable, naming the specific claims that found no support**, and the block
  **is not written**. A half-cited block written anyway is the failure this phase exists to
  prevent.

### Out of Scope

The writer itself, the declarations gate, the style channel and its `guidance/` registry,
figures, LaTeX rendering, `main.tex`, and the `citations` front-matter field (owned by
`the-contract-is-data-not-code`).

## Approach — the fork, decided

MCP servers are agent-side; the skill's CLI is stdlib-only. **Split by role.**

- **Discovery → the agent's MCP.** A hallucinated candidate dies at resolution anyway, so
  the weaker provenance costs nothing. The connector set stays the operator's `.mcp.json`
  configuration; this change does not fix it.
- **Resolution and metadata → the CLI over stdlib `urllib`**, keyless, against **OpenAlex,
  Crossref and arXiv** — enough to resolve a DOI or arXiv id to metadata. PubMed and
  bioRxiv are not required: this paper family is mathematics and machine learning.

**The tool that writes the `refs.bib` entry is the tool that fetched the bytes.** Hand the
CLI a finished entry and "never hand-typed" degrades from a property to a claim — we would
have replaced a human typing with a model typing.

**This changes the skill's character and the change must own it: the CLI is no longer
offline on that one path.** It stays keyless and stdlib, every call sits behind a role the
config can empty, and an unreachable endpoint is a **named refusal**, never a silent empty
result.

**Consensus is excluded from the verdict path.** A connector answering *does the literature
support X* makes the verdict an external opinion instead of a check against text we
ingested and can quote. The reason generalizes to any future connector proposed for the
verdict path.

## Delivery — one change, three work units

The split is a delivery seam, not a change boundary: all three share one record shape, and
Phase 1 delivered three units inside one change successfully. Three **sequential work-unit
commits**, each carrying its own proof.

| # | Work unit | Ends at |
|---|---|---|
| 1 | the evidence channel | a claim↔source set with verbatim spans exists on disk |
| 2 | the bibliography that was never typed | `refs.bib` sourced; both reciprocal checks green |
| 3 | the citation that holds | a planted false citation rejected by execution |

## Capabilities

### New Capabilities

- `literature-search`: connector roles, regime dispatch, the agent/CLI split, named refusals.
- `evidence-set`: ingestion routing and the claim↔source record with verbatim locator.
- `sourced-bibliography`: `refs.bib` from resolved metadata, provenance, both reciprocal checks.
- `citation-validation`: the three verdicts and the three-round bounded loop.
- `citation-placement`: regime-dispatched placement and the `discovery` noun-phrase rule.

### Modified Capabilities

None. This change reads `the-contract-is-data-not-code`'s `citations` field and the
block-substitution engine's `open`/`substitute`; it changes neither.

## The proof that matters

| Claim | Proof | Not accepted |
|---|---|---|
| The validator rejects | Plant a citation whose source does not support the claim; assert `does-not-hold` **by execution** | a validator that has never rejected anything |
| It does not reject everything | The opposite pole in the same run: a citation that genuinely holds returns `holds` | one pole |
| `.bib` was not hand-typed | Hand-type a well-formed entry; assert `ENTRY_UNSOURCED`. Needs no network | inspection of the file |
| The offline path refuses | Inject an unroutable transport; assert the named code **and a non-zero exit**; switch the guard off and watch it go red | a test that skips when the network is absent |
| `insufficient` is not lenient | It fails the citation and consumes an iteration, asserted | the docstring saying so |
| Exhaustion writes nothing | Three rounds, then the block is absent and the un-cited claims are named | a flagged half-cited block |
| The skill knows no contract | Rename a section id in `sections/`; the pipeline follows with zero code changed | reading source for absent strings |

Tests consume **fixture `.md` files shaped like `paper-ingestion` output**; this suite never
invokes marker or its venv.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/paper-writing/scripts/` | New | search, evidence, bib, validator modules + CLI verbs |
| `papersmith.yaml` | Modified | connector-role map |
| `.mcp.json` | New | discovery connectors, agent-side |
| `guidance/<section-id>/` | New | evidence PDFs; a `paper-ingestion` source root |
| `paper/refs.bib` | Modified | written from resolved metadata only |
| `tests/` | New | red-first; every proof above executed |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| `guidance/` now holds two kinds of folder — style and evidence — because `source_base: guidance` promotes any child with a loose PDF | High | Two independent discriminators: the folder name is a section id from the contract vocabulary, **and** evidence folders carry a manifest. Name-alone is guessable; manifest-alone is forgeable. The registry consuming both belongs to the style-channel phase |
| The validator becomes an LLM opinion with no falsifiable basis | High | The verdict is against a stored verbatim span, quoted in the result. A verdict citing no span is `insufficient` by construction |
| `paper-ingestion` **asks the operator before moving PDFs** — this loop inherits a human stop mid-flight | Certain | Named, never engineered around. The loop reports pending PDFs and waits; it never ingests unattended |
| Network reaches a repository that is otherwise offline end to end | High | Keyless stdlib only, one path, behind a role the config can empty; `none` blocks provably unaffected, by execution |
| The lab's `.mcp.json` connector set is unread | Medium | Stated as an unverified input and a required `sdd-design` read. Nothing here asserts what it contains |

## Rollback Plan

`git revert` the work unit's commit; units 2 and 3 revert independently of each other.
Nothing consumes the evidence set yet — the writer is Phase 4 — so no consumer breaks.
`guidance/` evidence folders and `paper/refs.bib` are gitignored working state, removed by
hand.

## Dependencies

- `the-contract-is-data-not-code` — the `citations` field. Interface settled, not landed.
- `only-the-block-changes` — `open`/`substitute`, landed.
- `paper-ingestion` as shipped — `source_base: guidance`, one folder per paper, operator
  confirmation before any move.
- **The lab's `.mcp.json` (`github.com/amalvarezme/marco-propuestas-ia`) — unread here, no
  network tool available. A required `sdd-design` read.**

## Success Criteria

- [ ] A planted citation whose source does not support its sentence returns `does-not-hold`,
      observed by execution.
- [ ] A citation that genuinely holds returns `holds` in the same run.
- [ ] Every verdict carries the verbatim span it was decided against.
- [ ] A hand-typed `refs.bib` entry refuses `ENTRY_UNSOURCED`; every shipped entry carries a
      resolver and digest.
- [ ] `CITE_WITHOUT_ENTRY` and `ENTRY_WITHOUT_CITE` each fire on a constructed case.
- [ ] With every connector unreachable, a `discovery` block refuses by name with a non-zero
      exit and a `none` block is still writable — both by execution, neither by skip.
- [ ] A `resolution` citation attached mid-sentence to its object passes placement; the same
      citation fails under `discovery`. A `resolution` noun-phrase citation passes.
- [ ] Three rounds exhausted leaves the block unwritten and names the un-supported claims.
- [ ] `insufficient` consumes an iteration and satisfies no citation, asserted.
- [ ] Renaming a section id in `sections/` moves the evidence folder with zero code changed.
- [ ] Every refusal code is classified and derived from one declaration; an unclassified code
      fails its own test.

## Citations checked

Every quoted contract sentence was read from disk in this phase and is cited by file and
quoted text, never by line number: the placement contrast in
`sections/01-materials-and-methods.md`, the noun-phrase prohibition in `05-related-work.md`
and `06-introduction.md` (and its absence from `01`, confirmed by a repository-wide search
of `sections/`), `source_base: guidance` in `papersmith.yaml`, its promotion rule in
`.claude/skills/paper-ingestion/scripts/extract_pdf.py` (`discover_source_roots`), and the
closed `discovery` | `resolution` | `none` regime in `the-contract-is-data-not-code`'s
`section-contract` spec. `openspec/specs/` holds only `deliberation-*` capabilities, none of
them touched here.
