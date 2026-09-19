# Tasks: The Requirement Names the Sentence That Demands It

## Work-Unit Table

| # | Unit | Touches | New refusals | Est. lines | Budget risk (vs 1200) | Depends on | Status |
|---|------|---------|---------------|-----------|------------------------|------------|--------|
| U1 | Schema + validators + derived accessor — gate INERT | `paper_contract.py`, `paper_graph.py` (`BlockRecord` ctor), `paper_cli.py:1455`, `tests/test_paper_writing.py` | None (`MALFORMED_HEADER` gains a new failure surface, no new code) | ~190 | Low | — | [x] |
| U2 | Transcribe the anchorable, report the rest — gate still INERT | `sections/*.md` (10, headers only), `openspec/changes/the-requirement-names-the-sentence-that-demands-it/unanchored-requirements.md` | None | ~330 | Low | U1 | [x] |
| DP | Operator ruling — **blocking** | `unanchored-requirements.md` (operator writes the ruling into it) | N/A | 0 | N/A (no code) | U2 | [ ] |
| U3 | Apply ruling; gate LIVE unconditional; fixtures; roster re-derive — atomic | `paper_contract.py`, `paper_graph.py`, `sections/*.md` (per ruling), `tests/test_paper_contract.py`, `tests/test_paper_writing.py`, `tests/test_paper_decisions.py`, `tests/test_paper_figure.py`, `specs/section-contract/spec.md`, `SKILL.md` | None (`SPAN_NOT_IN_SOURCE` reachable on this field; `MALFORMED_HEADER` on bare string) | ~700 | Medium–High | DP | [ ] |

**DP's three known inputs** (verbatim from proposal/design, do not re-derive):
1. `experimental-setup.es-assessment` → `experimental-design`, `gap` — zero anchor anywhere in the file (confirmed).
2. `es-assessment` → `dataset` — duplicates an existing `### Internal chain` edge to `es-dataset` (borderline).
3. `title-and-keywords.keywords` → `contributions` — anchored only by reusing its own ordering-edge quote (borderline).

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | U1 ~190 · U2 ~330 · U3 ~700 (per-unit PRs; U3 exceeds the session's 400-line review policy but must stay atomic per design D3) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | U1 → U2 → **DP (blocking)** → U3, each its own PR; U2 and U3 MUST NOT share a PR |
| Delivery strategy | ask-on-risk |
| Chain strategy | pending — recommend feature-branch-chain for U1→U2→U3, with `size:exception` requested on U3 alone (atomicity forecloses further splitting) |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High

### Suggested Work Units

| Unit | Focused test command | Runtime harness | Rollback boundary |
|------|----------------------|------------------|--------------------|
| U1 | `.venv/bin/python -m unittest tests.test_paper_writing.RequirementEntryShapeTests tests.test_paper_writing.RequirementSubscriptSingleDerivationTests -v` | N/A — gate not wired until U3; behavior is unit-test-only | Revert `paper_contract.py`/`paper_graph.py`/`paper_cli.py` hunks and the two new test classes in `tests/test_paper_writing.py`; no data touched |
| U2 | `.venv/bin/python -m unittest tests.test_paper_contract -v` | `.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py contract --file sections/<file>.md` per edited file | `git revert` the header edits and the report file; gate still inert |
| DP | N/A | N/A — operator decision only | N/A |
| U3 | `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` | `.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py order` (assembles the full corpus) | Single `git revert` of the atomic U3 commit restores pre-gate corpus + fixtures together (design Rollback Plan) |

## U1 — Schema + Validators + Derived Accessor

- [x] 1.1 Add `_REQUIREMENT_REQUIRED = ("value", "source")` and `_normalize_requirement_entry(raw, validate, owner)` to `paper_contract.py`: bare string → `{"value": raw, "source": None}`; dict → require `value` (string) and `source` (via existing `_validate_source`); unknown key or non-string `value` refuses `MALFORMED_HEADER`.
- [x] 1.2 Add `requirement_values(entries) -> tuple` to `paper_contract.py` — the single accessor deriving plain ids in declaration order.
- [x] 1.3 Rewire `_parse_block` in `paper_contract.py` to normalize every `requires_facts`/`requires_declarations` entry through 1.1, stored under the existing key.
- [x] 1.4 Update `paper_graph.py:162-163` (`BlockRecord` build) to derive both fields via `requirement_values()`.
- [x] 1.5 Update `paper_cli.py:1455` (`BlockContract` build) to derive via `requirement_values()`.
- [x] 1.6 Add an AST-scan test asserting no module outside `paper_contract` subscripts `["requires_facts"]`/`["requires_declarations"]` on a parsed block dict except through `requirement_values()`, scanning `scripts/*.py` (read-only). Landed in `tests/test_paper_writing.py` (`RequirementSubscriptSingleDerivationTests`) rather than `tests/test_paper_contract.py` — that file is concurrently owned by another agent session; the apply prompt directed new tests to `test_paper_writing.py`.
- [x] 1.7 RED test: bare string → `{"value": raw, "source": None}`, and re-parsing that output is a fixed point. `.venv/bin/python -m unittest tests.test_paper_writing.RequirementEntryShapeTests -v`
- [x] 1.8 RED test: rich object missing `source` → `MALFORMED_HEADER` naming `source`.
- [x] 1.9 RED test: rich object with an unknown key → `MALFORMED_HEADER` naming that key.
- [x] 1.10 RED test: non-string `value` → `MALFORMED_HEADER`, mirroring `_validate_mode_object`.
- [x] 1.11 Confirm `UNKNOWN_FACT`/`UNKNOWN_DECLARATION` still fire, now reading `entry["value"]`.
- [x] 1.12 Full suite green (gate still inert, baseline unaffected): `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'` — run per-suite instead (see apply report): `tests/test_paper_contract.py:166` (`SchemaTests.test_valid_header_parses_with_no_refusal`) is a PRE-EXISTING assertion of the old plain-string shape that this change's design correctly obsoletes (`parsed.blocks[0]["requires_facts"]` is now `[{"value": "results", "source": None}]`, not `["results"]`); left unedited per the same concurrent-ownership instruction as 1.6 and reported as a one-line follow-up rather than fixed here.

## U2 — Transcribe the Anchorable, Report the Rest

- [x] 2.1 For each of the 10 `sections/*.md` contracts, transcribe every `requires_facts`/`requires_declarations` entry that has a literal-substring quote anywhere in the corpus (self-file or cross-file, per D2's `bodies` dict) into `{value, source: {file, quote}}`. Prose bodies stay byte-identical.
- [x] 2.2 For every entry with no textual anchor, do NOT transcribe it. Add it to `openspec/changes/the-requirement-names-the-sentence-that-demands-it/unanchored-requirements.md`, one row per entry, carrying design D4's fields: block/field/value/contract file; the block's own `### External inputs` rows verbatim; whether the value appears anywhere in that file's body; which other blocks anchor the same value and where; whether it is already an `### Internal chain` row; block `optional`; blocks whose readiness changes if deleted.
- [x] 2.3 Confirm the report covers exactly the 3 DP-input groups (4 requirements) named in the Work-Unit Table; flag any additional unanchored entry found during the full read. Grep transcribed quotes against `scripts/` (read-only) for any paper-specific literal (the `MM_DATASET_ID`-class leak) — expect none, since only `sections/*.md` changed.
- [x] 2.4 Full suite still green (U1's shape layer still accepts bare strings for untouched entries): `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`

## DP — Operator Ruling (Blocking)

- [ ] DP.1 Operator reads `unanchored-requirements.md` and rules, per entry: "spurious — remove from header" or "contract omission — author the missing sentence into that contract's prose, then transcribe normally." Recorded in the same file. **U3 tasks below MUST NOT start before this returns.**

## U3 — Gate Unconditional + Fixtures (Atomic)

- [ ] 3.1 Apply the DP ruling to the affected headers in `sections/*.md`: remove "spurious" entries; for "contract omission" entries, author the sentence into that contract's prose and transcribe `{value, source}` normally — exactly as ruled, no executor judgment.
- [ ] 3.2 In `paper_contract.py`, narrow `_normalize_requirement_entry`: remove bare-string acceptance; require `source` on every entry (`MALFORMED_HEADER` naming `source` if absent).
- [ ] 3.3 Add `paper_graph._verify_requirement_transcription(bodies, blocks)` mirroring `_verify_after_transcription`: resolve `source.file` against the `bodies` dict, call `quote_in_body`; refuse `SPAN_NOT_IN_SOURCE` naming block + fact/declaration id on failure.
- [ ] 3.4 Wire the call as a direct statement inside `paper_graph.assemble_corpus` (not inside `if`/`try`), beside the other three transcription verifiers.
- [ ] 3.5 RED test in `tests/test_paper_writing.py`: unbacked quote in a tmp corpus copy → `SPAN_NOT_IN_SOURCE`. `.venv/bin/python -m unittest tests.test_paper_writing -v`
- [ ] 3.6 RED test: cross-file quote (mirrors `abstract.slot-2`/`06-introduction.md`) verifies; typo'd cross-file quote refuses.
- [ ] 3.7 Mutation test: remove the `assemble_corpus` call to `_verify_requirement_transcription` on a tmp copy, assert the 3.5 test goes green→red confirms the assertion count, then restore; AST-assert the call is a direct statement, not inside `if`/`try`.
- [ ] 3.8 Add a corpus-equality golden test in `tests/test_paper_writing.py`: snapshot `{qid: record.requires_facts}` / `.requires_declarations` pre-U3, assert equality post-U3 modulo the explicit DP-ruling diff.
- [ ] 3.9 Update the 26 non-empty raw-header occurrences across `tests/test_paper_writing.py`, `tests/test_paper_decisions.py`, `tests/test_paper_contract.py`, `tests/test_paper_figure.py` to the rich `{value, source}` shape. Empty-list fixtures and `BlockRecord`-constructing fixtures (e.g. `tests/test_paper_decisions.py:773`) are unaffected — do not touch.
- [ ] 3.10 RED test: a fixture rebuilt with a bare string now refuses `MALFORMED_HEADER` at parse (proves the half-migrated state is structurally unrepresentable, not merely detected).
- [ ] 3.11 Update `specs/section-contract/spec.md`: replace the "A bare-id requirement entry still parses" scenario with the narrowed post-U3 behavior (bare string refuses `MALFORMED_HEADER`), per design D3.
- [ ] 3.12 Update `.claude/skills/paper-writing/SKILL.md` documenting the transcription obligation for `requires_facts`/`requires_declarations`.
- [ ] 3.13 Measure `reachable_paper_refusal_codes()` bidirectionally after all code lands; record the observed count — do not forecast it.
- [ ] 3.14 Grep `scripts/` (read-only) for any id of this paper (forge-vocabulary guard) — must return empty.
- [ ] 3.15 Full suite green, all seven paper suites: `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`
