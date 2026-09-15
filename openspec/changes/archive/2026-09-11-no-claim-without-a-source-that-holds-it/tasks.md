# Tasks: No Claim Without a Source That Holds It

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~1400-1700 across 3 commits (WU1 ~700-850, WU2 ~250-350, WU3 ~450-550) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | WU1 → WU2 → WU3 (the proposal's 3 sequential work-unit commits) |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 | Evidence record/span/store + guidance classifier + `urllib` resolution client, wired into `paper_cli.py` | PR 1 | `.venv/bin/python -m unittest tests.test_paper_evidence -v` | `paper_cli.py resolve --identifier <doi> --role resolution` with the raising `OPENER` installed (no live network) | Revert `paper_evidence.py`, `paper_resolve.py`, their verbs, `.mcp.json`, `papersmith.yaml` additions; unrelated verbs untouched |
| 2 | `refs.bib` built only from cached resolved metadata + reciprocal checks | PR 2 | `.venv/bin/python -m unittest tests.test_paper_evidence -v` (bib cases) | `paper_cli.py bib build` against a fixture metadata cache | Revert `paper_bib.py` and its verb; WU1 store untouched |
| 3 | Verdict accounting, regime-dispatched placement, bounded 3-round loop | PR 3 | `.venv/bin/python -m unittest tests.test_paper_citation -v` | `paper_cli.py validate --block <id>` against a headered fixture `.md` | Revert `paper_validate.py` and its verb; WU1/WU2 untouched, `substitute` never reached on exhaustion |

## Phase 1: Foundation

- [x] 1.1 Confirm `reachable_paper_refusal_codes()` / `unreadable_paper_refusal_sites()` in `tests/test_paper_writing.py` glob `scripts/*.py` (sibling change's widening, not a literal module tuple) before adding any new module. Confirmed: the derivation walks `(CLI, *paper_cli_imported_modules())`, deriving imported modules from `paper_cli.py`'s own `ast.Import` nodes — no directory scan, no literal tuple. No change needed to the derivation itself.
- [x] 1.2 Add `VERDICTS = ("holds", "does-not-hold", "insufficient")` and `validate_verdict()` to `paper_vocabulary.py` (evidence-set Req 4; citation-validation Req 1).
- [x] 1.3 Add `paper_writing.roles` (discovery/resolution/full-text → connector) and `contact` to `papersmith.yaml` (literature-search Req 1, 4).
- [x] 1.4 Create `.mcp.json` naming discovery connectors agent-side only (literature-search Req 3); no resolution credential in it.

## Phase 2: Work Unit 1 — Evidence Channel

- [x] 2.1 RED `tests/test_paper_evidence.py`: `Verdict.holds`/`does_not_hold` require `span` positionally; no public string-taking constructor exists (evidence-set Req 4; design Decision 2).
- [x] 2.2 GREEN: `EvidenceSpan` (frozen, built only via `EvidenceSpan.locate(md_path, quote)`, byte-search, `SPAN_NOT_IN_SOURCE`) and `Verdict` in `paper_evidence.py`.
- [x] 2.3 RED: adversarial-pairing fixture — one `.md` returns `holds` for claim A and `does-not-hold` for claim B from the same bytes (design Decision 7a).
- [x] 2.4 RED: a span authored to look right but not byte-identical to its quote raises `SPAN_NOT_IN_SOURCE` (design Decision 7b).
- [x] 2.5 RED: one fixture is a verbatim excerpt of a pre-existing repository document, not authored for this test; state its domain-independence limit in-file (design Decision 7c).
- [x] 2.6 GREEN: `EvidenceRecord` + JSONL store at `paper/.paper-writing/evidence/<block-id>.jsonl` (evidence-set Req 3).
- [x] 2.7 GREEN: `classify_guidance_child(path)` → `evidence | style | ambiguous`, deriving section ids from `sections/` at runtime, never a literal list (evidence-set Req 2).
- [x] 2.8 Test: fixtures build their own `guidance/<id>/` tree with an in-test manifest; no test reads the repository's real `guidance/` or any `.papersmith-evidence.json` outside a temp fixture. (The earlier draft of this task also asserted the real `guidance/` tree holds only `.gitkeep`; measured false on this disk — it is gitignored working state that varies per operator machine, so that specific assertion was dropped rather than asserted against an unguaranteed premise.)
- [x] 2.9 RED: mutation m1 — patch the transport guard to `return {}`; the `RESOLVER_UNREACHABLE` + non-zero-exit test must go red via `_run_against_mutant` (literature-search Req 6).
- [x] 2.10 GREEN: `paper_resolve.py` — module-level `OPENER` seam, OpenAlex/Crossref/arXiv endpoints, one retry on transport/429/5xx only, `RESOLVER_UNREACHABLE`/`IDENTIFIER_UNRESOLVED`/`RESOLVER_ROLE_EMPTY`/`DISCOVERY_UNAVAILABLE` (literature-search Req 4, 6).
- [x] 2.11 Test: `mailto` sourced from `contact` in config, never hardcoded; resolution path holds no API key for any connector (literature-search Req 4).
- [x] 2.12 Wire `resolve` verb into `paper_cli.py`: `COMMANDS`, `_COMMANDS`, `REFUSAL_CLASSIFICATION`.
- [x] 2.13 Test: new codes from `paper_evidence.py`/`paper_resolve.py` are reachable via the widened derivation and classified; measured-count assertion updated 45 → 54, never skipped.
- [x] 2.14 Update `SKILL.md`: verb table gains `resolve`; the offline claim is no longer universal.

## Phase 3: Work Unit 2 — Sourced Bibliography

- [x] 3.1 RED: a hand-composed entry (no cached `metadata_digest` blob) refuses `ENTRY_UNSOURCED` with the `OPENER` never installed — proves no network needed (sourced-bibliography Req 1).
- [x] 3.2 GREEN: `paper_bib.py` — sole producer `entry_from_record(paper_dir, record)`; no function/flag accepts caller-composed entry text; `refs.bib` rebuilt whole and sorted, never appended (design Decision 4).
- [x] 3.3 RED then GREEN: `CITE_WITHOUT_ENTRY` and `ENTRY_WITHOUT_CITE` fire independently, from two separate fixtures (sourced-bibliography Req 2).
- [x] 3.4 Wire `bib build` verb into `paper_cli.py` (nested subparser: `bib` → `build`); extend `REFUSAL_CLASSIFICATION`.
- [x] 3.5 Test: roster reachability/classification re-run, measured count updated 54 → 57.

## Phase 4: Work Unit 3 — Citation Validation and Placement

- [x] 4.1 RED: build a record set containing `insufficient`/`does-not-hold`; assert `satisfied` excludes both — mutation m2 (widen the set to include `insufficient`) must turn this red via `_run_against_mutant` (citation-validation Req 1; design Decision 5).
- [x] 4.2 GREEN: `paper_validate.py` — `satisfied = {r.claim for r in records if r.verdict == HOLDS}`, no per-verdict branch.
- [x] 4.3 RED: mutation m3 — `Verdict.holds` accepting `span=None` must turn the spanless-verdict test red (citation-validation Req 2). (Target reused: WU1's own `test_holds_with_none_span_refuses`, since `Verdict` lives in `paper_evidence.py` from WU1 — the mutation table spans both test files, not one per work unit.)
- [x] 4.4 RED: plant a false citation — a claim paired with a source that does not support it executes to `does-not-hold`, AND the opposite pole (a genuinely-holding citation) executes to `holds` in the same run.
- [x] 4.5 RED then GREEN: 3-round bounded loop; on round-3 exhaustion raise `EVIDENCE_EXHAUSTED` naming every unsupported claim verbatim, and assert `paper_block.substitute` is never called (citation-validation Req 3).
- [x] 4.6 GREEN: placement dispatch table on `citations` regime — `discovery` end-of-sentence + noun-phrase prohibition, `resolution` anywhere including a noun phrase, `none` refuses any citation; no section/block id in code (citation-placement Req 1-3).
- [x] 4.7 Test: the same mid-sentence citation position fails under `discovery` and passes under `resolution`, attached to its object, in one fixture pair (citation-placement Req 1 scenario).
- [x] 4.8 Test: a `sections/*.md` fixture with no front matter refuses `CONTRACT_HEADER_ABSENT`, never a defaulted regime. (The real shipped `sections/*.md` now carry headers from a sibling change landing since design.md was written — this task builds its own unheadered fixture rather than asserting anything about the real tree's current state.)
- [x] 4.9 Wire `validate` verb into `paper_cli.py`; extend `REFUSAL_CLASSIFICATION`.
- [x] 4.10 Test: final roster pass across all five new/modified modules — nothing reachable unclassified, nothing classified unreachable (`RefusalRosterTests`, measured count 57 → 65).

## Phase 5: Cleanup

- [x] 5.1 Update `SKILL.md`'s refusal-roster paragraph and verb table for `bib build` / `validate`.
- [x] 5.2 Run `_shared/tools/check_citations.py` against this tasks artifact (deferred from drafting per design.md's own note: "this executor has no shell tool"; run here during `sdd-apply`). One flagged citation: `SKILL.md` read as an attempted `class:` symbol lookup and reported "no such class defined" — a false positive (`SKILL.md` is a backticked filename, not a class), not a broken citation. No other citation in `tasks.md` failed to resolve.

## Phase 6: Corrective batch — verify-report.md's 3 CRITICAL findings

`sdd-verify` (id 1661) found 32/35 scenarios compliant, 0 functional defects, but
FAILed on the strict rule that a spec scenario needs a *named, executing* test,
not static inspection. All three gaps are in `literature-search`, all describe
behaviour deliberately absent from this CLI.

- [x] 6.1 Test: no source file in the skill's `scripts/` references an MCP
  config — scans every `.py` file under `SKILL_SCRIPTS` (via glob, not a
  hand-picked list) for `.mcp.json`/`mcpServers`, closing "Discovery issues an
  open search" / "Discovery candidate reaches resolution".
- [x] 6.2 Test: `paper_resolve.py` defines no free-text query-construction
  function — derived via `inspect` over the module's own public surface
  (name or parameter containing "query"/"search"), closing the same two
  scenarios' mechanism gap.
- [x] 6.3 Test: `"consensus"` is not among `paper_resolve.RESOLVERS`,
  `paper_resolve.ROLES`, or `paper_resolve._ENDPOINT_BUILDERS` — closing
  "Consensus cannot supply a verdict".
- [x] 6.4 Mutation-proved all three: added `"consensus"` to `RESOLVERS`
  (6.3 fails), added a `build_search_query(query)` function (6.2 fails),
  appended an `.mcp.json`-referencing string to `paper_resolve.py` (6.1
  fails) — each mutant reverted, zero production diff. `LiteratureSearchAbsenceTests`
  in `tests/test_paper_evidence.py`, commit `bc592f7`.

No production code touched (WARNING and 2 SUGGESTIONS from verify-report.md
stay open, out of this batch's scope). Full mandated test command re-run
green: `npm test` 559/559, `.venv/bin/python -m unittest discover -s tests -p
'test_*.py'` 3160 tests OK (6 skipped), `npm run typecheck` clean.
