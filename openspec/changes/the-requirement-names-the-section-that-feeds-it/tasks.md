# Tasks: The Requirement Names the Section That Feeds It

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~470 (U1+U2 ≈ 300, U3 ≈ 170) |
| 400-line budget risk | Medium |
| Chained PRs recommended | Yes |
| Suggested split | PR 1: Phase 1+2 (U1+U2, ~300) → PR 2: Phase 3+4 (DP+U3, ~170) |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending — ask the operator |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: Medium

Six refusal codes total, not four: `SECTION_NOT_IN_SOURCE`, `SECTION_TITLE_AMBIGUOUS`,
`SECTION_BINDING_ABSENT`, `SOURCE_LINEAGE_UNRESOLVED`, `SOURCE_REVISIONS_UNDECLARED`,
`MALFORMED_SOURCE_MARKER`. The last two, and the disjoint-key cross-check against
`guidance/`'s marker, are folded into Unit 2 (Phase 2) below; the line estimate is
unchanged from design.md, which already priced the marker reader in.

### Suggested Work Units

| Unit | Goal | PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 (U1) | `document` entry shape, inert | PR 1 | `.venv/bin/python -m unittest tests.test_paper_contract` | N/A — additive, no corpus edit yet | revert `paper_contract.py`/`paper_graph.py` diffs |
| 2 (U2) | Marker + lineage resolver + existence/ambiguity, inert without U3 | PR 1 | `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions` | N/A — no binding demanded yet | revert `paper_declarations.py`/`paper_graph.py` diffs |
| 3 (DP) | Owner rules on unanchorable entries | — | N/A — human decision | N/A | reversible; nothing lands until ruled |
| 4 (U3) | Obligation unconditional, corpus transcribed, `write` wired for all six codes | PR 2 | full suite (both, see 4.12) | `.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py write <bound-block-id>` | `git revert` U3's single commit |

## Phase 1 — U1: Entry shape, inert

- [ ] 1.1 RED: add failing tests in `tests/test_paper_contract.py` for `section-contract` scenarios "A document binding parses", "A malformed document binding refuses", "A document binding on a declaration entry refuses".
- [ ] 1.2 Add `_REQUIREMENT_OPTIONAL = ("document",)`, `_DOCUMENT_REQUIRED = ("lineage","section")` to `.claude/skills/paper-writing/scripts/paper_contract.py`; refuse `MALFORMED_HEADER` per 1.1; reject `document` on `requires_declarations` entries.
- [ ] 1.3 Add `requirement_documents()` accessor to `.claude/skills/paper-writing/scripts/paper_contract.py`.
- [ ] 1.4 Add `BlockRecord.source_bindings: tuple = ()` to `.claude/skills/paper-writing/scripts/paper_graph.py`; confirm every existing construction site stays green.
- [ ] 1.5 Add bindable-fact derivation (sole test: key of `FACT_SOURCE_ROOT`) to `.claude/skills/paper-writing/scripts/paper_declarations.py`. Mutation: extend `FACT_SOURCE_ROOT` with a sixth root in a test fixture; assert bindable with zero engine edit.
- [ ] 1.6 Run `.venv/bin/python -m unittest tests.test_paper_contract`; confirm 1.1 now green and the shipped corpus still assembles byte-identically.

## Phase 2 — U2: Resolution, inert without U3

**Marker grammar — `MALFORMED_SOURCE_MARKER`**

- [ ] 2.1 RED: add failing marker-grammar tests in `tests/test_paper_writing.py` for `MALFORMED_SOURCE_MARKER` (non-UTF-8, non-JSON, non-object, missing `revisions`, missing `revision_prefix`/`ordinal_digits`, unknown key at either level, wrong-typed value).
- [ ] 2.2 Add `read_revisions_marker()` to `.claude/skills/paper-writing/scripts/paper_declarations.py`; refuse `MALFORMED_SOURCE_MARKER` naming the offending file and key, per 2.1.
- [ ] 2.3 Mutation: add a sixth key to a fixture marker; separately flip `ordinal_digits` to a string; confirm both refuse `MALFORMED_SOURCE_MARKER`.

**Disjoint-key cross-check with `guidance/`'s own marker (both directions)**

- [ ] 2.4 RED: add a failing test asserting the source-root reader (`read_revisions_marker()`) refuses a `guidance/`-shaped marker (`{"class": "style-reference"}`), naming `revisions` as missing — `MALFORMED_SOURCE_MARKER`.
- [ ] 2.5 RED: add a test asserting `.claude/skills/paper-writing/scripts/paper_guidance.py`'s existing `resolve_guidance_dir` reader refuses a source-root-shaped marker (`{"revisions": {...}}`) as an unknown key — `MALFORMED_GUIDANCE_MARKER`. This is a regression proof: `_MARKER_ALLOWED_KEYS = ("class",)` already excludes `revisions`, so no production edit is expected here — only the test is new.
- [ ] 2.6 Run 2.4 and 2.5 green; confirm neither reader was widened to accept the other's key set (each refuses loudly on the other's shape, per `source-section-binding`'s disjoint-key requirement).

**Marker-driven resolution, no literal — generality**

- [ ] 2.7 RED: add a failing test asserting a marker declaring `{"revisions": {"revision_prefix": "v", "ordinal_digits": 3}}` resolves lineage `lineage` to `lineage-v007.md` — the marker's own declared values drive resolution, never a literal.
- [ ] 2.8 Confirm `resolve_lineage()` (2.14 below) composes its regex only from the marker's declared `revision_prefix`/`ordinal_digits`; `rg` under `.claude/skills/paper-writing/scripts/` confirms no revision-pattern literal governs resolution.

**Undeclared marker — `SOURCE_REVISIONS_UNDECLARED`**

- [ ] 2.9 RED: add a failing test asserting a document-rooted root (contains `*.md`) carrying no `.paper-writing.json` marker refuses `SOURCE_REVISIONS_UNDECLARED` naming the root.
- [ ] 2.10 RED: add a failing test distinguishing the two outcomes: a document-rooted root that HAD a marker, now deleted, MUST refuse `SOURCE_REVISIONS_UNDECLARED` — it MUST NOT degrade to the `unmeasured` report, which is reserved only for a root that is not document-rooted at all (e.g. `experiments/` holding only `.gitkeep`).
- [ ] 2.11 Wire `SOURCE_REVISIONS_UNDECLARED` into `source_root_status()`/`_verify_source_section_bindings()` (`paper_declarations.py`/`paper_graph.py`): document-rooted + no marker refuses; only a non-document-rooted root reports `unmeasured`; these two outcomes are never collapsible.
- [ ] 2.12 Mutation (design.md Testing Strategy): delete `proposals/.paper-writing.json` in the fixture root; confirm `SOURCE_REVISIONS_UNDECLARED` fires and the outcome is never `unmeasured`.

**Unmeasured-root report**

- [ ] 2.13 RED: add failing `source_root_status()` tests (document-rooted; root holding only `.gitkeep`; root absent) for the `unmeasured` report.
- [ ] 2.14 Add `source_root_status(base, root_name)` to `paper_declarations.py`; add `Corpus.source_roots: dict` to `.claude/skills/paper-writing/scripts/paper_graph.py`, echoed by every corpus-reading verb.

**Lineage resolution — `SOURCE_LINEAGE_UNRESOLVED`**

- [ ] 2.15 RED: add failing `resolve_lineage()` tests — max ordinal, gap-tolerant, zero-candidate foreign lineage refuses, tie between two ordinal spellings refuses naming both candidates.
- [ ] 2.16 Add `resolve_lineage(root, lineage, marker)` to `paper_declarations.py`; refuse `SOURCE_LINEAGE_UNRESOLVED` naming the lineage, the root, and every candidate found on zero or >1 matches.
- [ ] 2.17 Mutation: rename the newest fixture revision to a foreign lineage (zero case); add `research-concept-r021.md` beside `research-concept-r21.md` (tie case); confirm both refuse, naming both candidates on the tie.

**Section existence/ambiguity — `SECTION_NOT_IN_SOURCE` / `SECTION_TITLE_AMBIGUOUS`**

- [ ] 2.18 RED: add failing section existence/ambiguity tests against `segment_markdown` headings of a resolved fixture revision.
- [ ] 2.19 Add `_verify_source_section_bindings()` to `paper_graph.py`, called once per `assemble_corpus`, memoizing one `{title: count}` per distinct `(root, lineage)`; refuse `SECTION_NOT_IN_SOURCE` / `SECTION_TITLE_AMBIGUOUS`.
- [ ] 2.20 Mutation: rename the bound heading in a fixture revision (expect `SECTION_NOT_IN_SOURCE`); duplicate the bound heading (expect `SECTION_TITLE_AMBIGUOUS`).

**Source base and version-bump freedom**

- [ ] 2.21 Add `source_base: Path | None = None` kwarg to `assemble_corpus` (default `sections_dir.parent`); add a synthetic `experiments/`-only-`.gitkeep`-style fixture proving unmeasured with zero edits to any existing minimal fixture.
- [ ] 2.22 Integration test: fixture adds a `…-r22.md` revision preserving a bound title; assert the corpus assembles byte-identically untouched (success criterion 4).
- [ ] 2.23 Run `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions`; confirm green; bindings still optional (U3 not landed).

## Phase 3 — DP: Owner decision point (BLOCKING, before Phase 4)

- [ ] 3.1 Scan every bindable `requires_facts` entry in `sections/01-materials-and-methods.md` and `sections/02-experimental-setup.md` against `proposals/research-concept-r21.md` (read-only); list every entry that cannot be anchored to an exact heading title.
- [ ] 3.2 Report the unanchorable list to the owner. STOP. Do not delete or invent a binding. Wait for an explicit ruling before starting Phase 4.

## Phase 4 — U3: Obligation unconditional, atomic (single commit)

- [ ] 4.1 RED: add a failing test for `SECTION_BINDING_ABSENT` on a bindable entry carrying no `document` half.
- [ ] 4.2 Wire `SECTION_BINDING_ABSENT` unconditionally into `_verify_source_section_bindings()` for every bindable entry.
- [ ] 4.3 Mutation: delete the `document` half from one shipped entry; confirm `SECTION_BINDING_ABSENT` fires.
- [ ] 4.4 Transcribe real bindings into `sections/01-materials-and-methods.md` and `sections/02-experimental-setup.md` per the Phase-3 ruling, prose bytes untouched; distinguish `mm-borrowed-machinery` (section 1) from `mm-proposal` (section 3) against `proposals/research-concept-r21.md` (read-only).
- [ ] 4.5 Create `proposals/.paper-writing.json`: `{"revisions":{"revision_prefix":"r","ordinal_digits":2}}`.
- [ ] 4.6 RED: add failing `write`-gate tests for ALL SIX codes reaching `write` through its own corpus assembly: `SECTION_NOT_IN_SOURCE`, `SECTION_TITLE_AMBIGUOUS`, `SECTION_BINDING_ABSENT`, `SOURCE_LINEAGE_UNRESOLVED`, `SOURCE_REVISIONS_UNDECLARED`, `MALFORMED_SOURCE_MARKER` — each refuses before the draft stage runs, `main.tex` stays byte-identical.
- [ ] 4.7 Wire all six binding/marker refusals into `.claude/skills/paper-writing/scripts/paper_cli.py`'s `_resolve_write_gate` (return the corpus) so `cmd_write` refuses before readiness, per `writing-orchestration`.
- [ ] 4.8 Confirm `write` refuses `SOURCE_REVISIONS_UNDECLARED` specifically: a document-rooted root missing its marker, invoked directly via `write` (never only via `phases`) — the marker codes reach `write` through the same corpus assembly as the binding codes.
- [ ] 4.9 Mutation: wire the guard only into a read-only verb (`phases`), leave `write` unguarded; confirm a direct-`write` test fails for both the binding-code family and the marker-code family, proving the wiring-gap mutation this guard must survive across all six codes.
- [ ] 4.10 Generality check: `rg` under `.claude/skills/paper-writing/scripts/` for any block id, section title, document filename, subject word, or revision-pattern literal of this paper; confirm empty output.
- [ ] 4.11 Re-derive the refusal roster with `reachable_paper_refusal_codes()`; record the measured count. Never write a forecast number into any artifact.
- [ ] 4.12 Run `npm test` AND `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` from the repository root; confirm zero new failures beyond the 6 known pre-existing (`test_skill_audit` × 5, `test_proposal_implementation` × 1).
