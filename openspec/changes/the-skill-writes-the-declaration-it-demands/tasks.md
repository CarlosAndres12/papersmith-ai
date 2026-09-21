# Tasks: The Skill Writes The Declaration It Demands

## Sizing — measured, not averaged

The proposal estimated **~1550 engine lines**. The design estimated **~700** and
explained the gap (Decision B: one shared seal module + six lines per reader, not two
sealing implementations; four extractions move existing lines rather than adding them).

Read against this checkout, function by function, before writing this file:
`paper_declarations.read_revisions_marker` (70 lines total, ~17 docstring / ~52 logic),
`resolve_lineage` (42 lines, ~19/~22), `_ingested_root_status` (53 lines, ~22/~29),
`paper_guidance._classify` (37 lines, ~10/~27), `paper_cli.cmd_bind` (34 lines, ~25/~8),
`paper_cli.compute_plan` (63 lines, ~33/~29), and `paper_region.py`'s own seal precedent
(`serialize_body` + `current_digest` + `_atomic_replace`, ~55 lines together — the exact
shape `paper_marker.py` mirrors per Decision B).

Bottom-up by function, at this codebase's own measured docstring density:

| Module | New/changed engine lines | Basis |
|---|---|---|
| `scripts/paper_marker.py` (new) | ~135 | `SEAL_KEY`+`SEAL_STRENGTH` (~8), `canonical_bytes` (~10), `computed_seal` (~10), `is_sealed` (~6), `seal_shape_error` (~20), `write` (~25), `_atomic_replace` copy (~22), module header (~15, quotes `SEAL_STRENGTH`) |
| `scripts/paper_declarations.py` | ~185 | `declarable_source_roots` (~12), `declaration_state` incl. seal split (~28+10), `_validate_revisions_obj`/`_revision_pattern` extractions net (~28), `_unmarked_candidates` (~10), `declare_revisions` (~60), `source_revisions_undeclared_detail` (~30), seal check in `read_revisions_marker` (~8) |
| `scripts/paper_guidance.py` | ~80 | key/import (~2), `_validate_class_obj` extraction net (~15), seal check in `_classify` (~8), `declare_class` (~52) — folder membership, class membership, pre-write `EVIDENCE_ROOT_AMBIGUOUS`, round-trip, write |
| `scripts/paper_graph.py` | ~5 | raise site 2 calls the shared detail builder — a net-neutral swap, not an addition |
| `scripts/paper_cli.py` | ~105 | `cmd_mark_revisions`/`cmd_mark_class` (~32), two argparse subparsers under one `mark` root (~35), `compute_plan`'s `sourceRoots` + widened `guidance` (~30), five `REFUSAL_CLASSIFICATION` entries (~5) |

**Total: ~500-650 engine lines, called at ~600.** This lands near design's ~700 and
confirms design's own diagnosis of the proposal's double-count: a real, shared
`paper_marker.py` costs ~135 lines once, against the ~600 the proposal implicitly
priced for two independent sealing implementations (U2+U3, ~300 apiece) — the ~450-line
gap Decision B named is real, measured here at the function level, not asserted. No
part of this measurement suggests the design missed work; the extractions
(`_validate_revisions_obj`, `_revision_pattern`, `_unmarked_candidates`,
`_validate_class_obj`) are net-neutral moves of existing logic, exactly as Decision B
says, and every new refusal-raising function in the table above has a real, load-bearing
docstring at this repository's own density — none of the ~600 is padding.

Against the owner's **1600-engine-line budget** (code under
`.claude/skills/paper-writing/scripts/` only — tests, mutation proofs, fixtures and
openspec documents excluded, per the owner's own repeated ruling): **~600 of 1600, Low
risk**, with headroom even if per-function docstrings run heavier than measured above.

## Review Workload Forecast

Engine and test lines are forecast **separately per unit** — a combined total hides the
split the owner has ruled on four times.

| Unit | Engine lines (measured) | Test lines (est.) | Unit total | Green alone | Depends on |
|---|---|---|---|---|---|
| S1 — SHOW | ~60 | ~90 | ~150 | yes | none |
| S2 — `paper_marker.py` + `mark revisions` | ~280 | ~450 | ~730 | yes | S1 (splits `declared` into sealed/unsealed) |
| S3 — `mark class` | ~105 | ~260 | ~365 | yes | S2 (`paper_marker.py`) |
| S4 — ASK, both raise sites | ~45 | ~140 | ~185 | yes | S2 (names `mark revisions` in the message) |
| S5 — Docs, strength test, roster, both suites | 0 | ~90 | ~90 | yes | S1-S4 landed |
| **Total** | **~490** | **~1030** | **~1520** | | |

Against the **default 400-line review budget** (additions + deletions, tests included):
every unit but S5 exceeds it standalone, so all four ship as chained PRs. Against the
**owner's 1600-engine-line budget** (tests excluded): ~490-600 total, Low risk.

```text
Decision needed before apply: Yes
Chained PRs recommended: Yes
Chain strategy: pending
400-line budget risk: High
```

Delivery strategy is `ask-on-risk` (session preflight): per the guard rule, `ask-on-risk`
always resolves `Decision needed before apply: Yes`, independent of the owner's separate,
already-ruled architectural fork (design.md Decision A — that decision is closed, not
what this line is asking about). The orchestrator asks the user to pick one chain
strategy — stacked-to-main, feature-branch-chain, or size:exception — before `sdd-apply`
opens PR #1.

### Suggested Work Units

| Unit | Goal | PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| S1 | `declaration_state` (3-value), `compute_plan.sourceRoots`, `guidance` widened to `{class, declaration}` — closes the false 2.14 record | PR 1 | `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions` | `.venv/bin/python .claude/skills/paper-writing/scripts/paper_cli.py plan` — run it and read the output | `git revert` PR 1's commit(s); `compute_plan`/`declaration_state` diffs are additive keys, no consumer removed |
| S2 | `scripts/paper_marker.py`; `mark revisions` + write-time validation + `--unsealed`; seal verified in `read_revisions_marker`; `declared` splits sealed/unsealed | PR 2 (base: PR 1) | `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions tests.paper_mutation` | `.claude/skills/paper-writing/scripts/paper_cli.py mark revisions --root experiments --revision-prefix r --ordinal-digits 2`, real worked session | `git revert` PR 2's commit(s); `--unsealed` re-run per declared root before revert (Decision K), documented in S2's own task 2.14 |
| S3 | `mark class` + write-time validation; seal verified in `_classify`; `_MARKER_ALLOWED_KEYS` derived | PR 3 (base: PR 2) | `.venv/bin/python -m unittest tests.test_paper_decisions tests.paper_mutation` | `.claude/skills/paper-writing/scripts/paper_cli.py mark class --folder style-corpus --class style-reference` | `git revert` PR 3's commit(s); `--unsealed` re-run per classed folder before revert |
| S4 | `source_revisions_undeclared_detail`, both raise sites, `_unmarked_candidates` extracted | PR 3 (same branch as S3 — S4 names `mark revisions`, which S2 built; S3 and S4 do not depend on each other) | `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions` | `write` on a fresh block bound to an undeclared root — read the refusal text | `git revert` PR 3's S4 commit(s) independently of S3's; disjoint files (`paper_declarations.py`, `paper_graph.py` vs `paper_guidance.py`) |
| S5 | `SKILL.md` + `references/usage.md`, four-surface strength test, leak-audit re-run, roster re-measured, both suites | PR 4 (base: PR 3) | full suite (both, see 5.x) | N/A — documentation + measurement, no new runtime path | `git revert` PR 4's commit(s); no engine code in this unit |

## Phase 0 — GATE: baseline vocabulary audit (before any code lands)

- [ ] 0.1 Derive the product vocabulary from disk: top-level names under `proposals/`,
      `experiments/`, `implementations/`, `guidance/` (all four gitignored — walk with
      `fd -H -I` / `rg -I -H`, never a bare `fd`/`rg`, or the walk silently sees nothing).
- [ ] 0.2 Sweep that vocabulary across `.claude/skills/paper-writing/` and the forge's own
      suite (`rg -n -i -F <term> ...`). Record the exact commands and their output in the
      apply report. Expect the disclosed **48-hit** cross-skill collision — confirm it
      lands in `experimental-deliberation`/`proposal-deliberation` (sibling skills), not
      inside `paper-writing`'s own surface; owner-acknowledged, out of scope, do not let
      it read as this change's leak.
- [ ] 0.3 Confirm `tests.test_proposal_implementation.ForgeVocabularyDerivedGuardTests`
      currently shows only the one known pre-existing failure
      (`test_rule_b_finds_no_target_vocabulary_in_the_forge`, naming the three sibling
      skills) before any production edit — this is the baseline S5's task 5.8 re-checks.

## Phase 1 — S1: SHOW (`declaration_state`, `sourceRoots`, widened `guidance`)

Design.md Decisions I, J. Closes `openspec/changes/archive/2026-09-20-the-requirement-names-the-section-that-feeds-it/tasks.md`
item 2.14 (read-only), ticked `[x]`, claiming `Corpus.source_roots` is "echoed by every
corpus-reading verb" — measured false by running `plan`, `phases`, `contract`.

- [ ] 1.1 RED: add failing tests in `tests/test_paper_decisions.py` for
      `declaration_state(status, root)`: `n/a` for a non-`PROSE` root (by kind, never by
      name — assert against a fixture root whose `kind` is `REPOSITORY`); `undeclared` for
      a `PROSE` root with no marker; `declared` for a `PROSE` root with a valid marker
      (three-value vocabulary only — the sealed/unsealed split is S2's, not this unit's).
- [ ] 1.2 Add `declarable_source_roots()` and `declaration_state(status, root)` to
      `scripts/paper_declarations.py`, derived from `FACT_SOURCE_ROOT`'s own `kind` field
      — no root name appears as a literal in either. Confirm 1.1 green.
- [ ] 1.3 Mutation: extend `FACT_SOURCE_ROOT` with a sixth `PROSE`-kind root in a test
      fixture; assert it is both declarable and reported, with zero engine edit — the
      derivation proof design's Decision J and the spec's "Which Roots And Folders Are
      Declarable Is Derived" scenario both require.
- [ ] 1.4 RED: add a failing integration test in `tests/test_paper_writing.py` asserting
      `compute_plan`'s output carries a `sourceRoots` key, one entry per root in
      `FACT_SOURCE_ROOT`, each naming `state`/`documents`/`reason` (existing) plus
      `declaration` (new) — **assert this by calling `compute_plan` and reading its
      return value**, never by asserting a field exists on an intermediate object (the
      exact failure mode of the false-ticked 2.14).
- [ ] 1.5 Wire `sourceRoots` into `paper_cli.compute_plan`, looping `FACT_SOURCE_ROOT`
      once, calling `paper_declarations.source_root_status`/`declaration_state` per root.
- [ ] 1.6 RED: add a failing test in `tests/test_paper_decisions.py` (or wherever the two
      measured flat-string consumers live) asserting `plan`'s `guidance` entries widen
      from a bare class string to `{"class": ..., "declaration": ...}`.
- [ ] 1.7 Widen `compute_plan`'s `guidance` construction to the object shape; update the
      **two measured consumer assertions** in `tests/test_paper_decisions.py` that
      currently expect the flat string (zero consumers in `scripts/`, per design's
      measurement — confirm that measurement still holds with `rg` before editing).
      Confirm 1.6 green.
- [ ] 1.8 Confirm no new `n/a`-producing root is matched by literal name: `rg` under
      `scripts/paper_declarations.py`/`paper_cli.py` for a `REPOSITORY`/`INGESTED` root
      name used as a string comparison rather than a `.kind` check.
- [ ] 1.9 Generality sweep: `rg` the fixture root name from 1.3 across
      `.claude/skills/paper-writing/scripts/`; zero matches outside the test module.
- [ ] 1.10 Run `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions`;
      confirm green, no new failures beyond the known pre-existing baseline.

## Phase 2 — S2: `paper_marker.py` + `mark revisions` (the seal, ruled by Decision A)

Design.md Decisions A (ruled), B, C, D, E, F, G (partial — the strength constant lands
here; the four-surface test lands in S5), K.

**The shared seal module**

- [ ] 2.1 RED: add failing unit tests in `tests/test_paper_writing.py` (new module-level
      test class) for `paper_marker.canonical_bytes`/`computed_seal`: identical input
      produces an identical digest across two separate calls (canonicalization stability
      — `sort_keys=True` is load-bearing, mirroring `paper_region.serialize_body`'s own
      documented reason); the digest excludes `seal_sha256` itself from its own input.
- [ ] 2.2 Create `scripts/paper_marker.py`: `SEAL_KEY`, `SEAL_STRENGTH` (Decision G's exact
      sentence — "detects an unaware edit... self-consistency, not tamper-proofing...
      anyone who reproduces it can... recompute a matching seal"), `canonical_bytes`,
      `computed_seal`, `is_sealed`, `seal_shape_error` (returns the shape-error detail
      string, or `None` — **never raises**, per Decision B: the shared module never raises
      a consumer's refusal), and `write(path, obj, *, sealed=True)` with its own
      `_atomic_replace` (a fourth copy, docstring says so — mirrors `paper_block.py`'s
      exact same-directory temp-file-then-`os.replace` shape). Confirm 2.1 green.
- [ ] 2.3 RED: add failing tests for `seal_shape_error`: `None` when `seal_sha256` is
      absent; `None` when present and a 64-char lowercase hex string; a detail string when
      present but wrong length, wrong charset, or non-string.
- [ ] 2.4 Confirm 2.3 green against 2.2's implementation.

**Write-time validation and the write verb**

- [ ] 2.5 RED: add failing tests in `tests/test_paper_decisions.py` for
      `declare_revisions(base, root_name, prefix, digits, *, sealed=True)`: `--root`
      naming a non-`PROSE` root refuses `SOURCE_ROOT_UNDECLARABLE`, naming every
      declarable root and the rejected root's own kind.
- [ ] 2.6 RED: add a failing test asserting `--ordinal-digits < 1` refuses
      `MALFORMED_SOURCE_MARKER` (reused verbatim — a value-shape error on the marker
      being written).
- [ ] 2.7 RED: add failing tests: a prefix/digit pair matching zero `*.md` under the root
      refuses `SOURCE_DECLARATION_UNMATCHED`, naming the prefix, the digit count, and
      every `*.md` file seen; a root that is not a directory at all folds into the same
      code (Decision F.3). Assert **nothing is written to disk** on this refusal.
- [ ] 2.8 Extract `_revision_pattern(prefix, digits)` out of `resolve_lineage`'s own inline
      regex composition (`scripts/paper_declarations.py`), so `resolve_lineage` and
      `declare_revisions` compose the identical pattern from one function — never two
      that can drift. Confirm `resolve_lineage`'s existing tests stay green untouched.
- [ ] 2.9 Extract `_validate_revisions_obj(obj, label)` out of `read_revisions_marker`'s
      own shape-checking body; `read_revisions_marker` becomes a thin wrapper: read file,
      parse JSON, call `_validate_revisions_obj`. Confirm every existing
      `read_revisions_marker` test in `tests/test_paper_writing.py` stays green unchanged
      — this is a pure extraction, not a behavior change.
- [ ] 2.10 Add `declare_revisions`: build the candidate `{"revisions": {...}}` object,
      glob-match per 2.7, round-trip the candidate through `_validate_revisions_obj`
      before writing (so `mark` can never produce a marker its own reader would refuse),
      then call `paper_marker.write`. Returns `{"root", "revisions", "matched",
      "unmatched", "sealed"}`. Confirm 2.5-2.7 green.
- [ ] 2.11 RED-then-GREEN: add a test asserting a matching declaration records the marker,
      reporting both matched and unmatched files correctly (the spec's "A matching
      declaration is recorded" scenario).
- [ ] 2.12 Add `--unsealed` to `declare_revisions` (already threaded via `sealed: bool`);
      RED-then-GREEN: add a test asserting `mark revisions --unsealed` writes a marker
      with no `seal_sha256` key, and that this marker's shape is IDENTICAL to what the
      pre-change grammar admits (round-trip it through a hand-built pre-seal validator
      inline in the test — the "an older reader accepts it" proof).
- [ ] 2.13 RED-then-GREEN: add a test asserting `mark revisions` always writes, with no
      `--reopen`/`--adopt`, regardless of whether a sealed marker already exists at that
      path or whether its existing seal matches — re-recording a hand-edited marker
      clears the defect (spec: "Re-Recording Always Succeeds; There Is No Stuck State").
- [ ] 2.14 Document `mark revisions --unsealed`'s docstring per Decision K: its only
      purpose is the pre-revert downgrade, and it removes nothing a determined editor
      could not already remove by hand-editing the file (Decision G) — this is the
      rollback boundary named in the Suggested Work Units table above.

**The seal reaches the reader — never the report alone**

- [ ] 2.15 RED: add a failing test asserting `read_revisions_marker` accepts a marker with
      no `seal_sha256` key exactly as before sealing existed (`declared-unsealed`, no
      refusal).
- [ ] 2.16 RED: add a failing test asserting `read_revisions_marker` refuses
      `SOURCE_DECLARATION_HAND_EDITED` when `seal_sha256` is present but does not match
      `paper_marker.computed_seal` of the marker's own remaining bytes — driven through
      `cmd_write` (a gating verb), **not through `plan`**.
- [ ] 2.17 Add the seal check inside `read_revisions_marker` (six lines, per design's own
      count): shape-check via `paper_marker.seal_shape_error` (malformed shape still
      raises `MALFORMED_SOURCE_MARKER`, the reader's own code, never
      `paper_marker`'s), then compare via `computed_seal` when shape-valid. Confirm 2.15
      and 2.16 green.
- [ ] 2.18 Widen `declaration_state` (S1) to a four-value vocabulary: `declared` splits
      into `declared-sealed`/`declared-unsealed` using `paper_marker.is_sealed` plus the
      seal-match result. RED-then-GREEN in `tests/test_paper_decisions.py`.
- [ ] 2.19 **Mutation — reachable through `write`, not only through `plan` (the
      non-negotiable constraint)**: replace the seal-comparison line inside
      `read_revisions_marker` with a constant `True`. The test proving
      `SOURCE_DECLARATION_HAND_EDITED` MUST be driven through `cmd_write`
      (`SourceSectionBindingWriteGateTests`-style) and MUST go red under this mutation. A
      test that only drives the mutation through `plan` does not satisfy this task —
      write it through `cmd_write` explicitly, or a cheaper read-only test will pass this
      task's letter while missing invariant 4 entirely.
- [ ] 2.20 Mutation: replace `declare_revisions`'s zero-match guard condition with
      `False`; the wrong-prefix test (2.7) must go red.
- [ ] 2.21 Mutation: replace the declarable-membership test (`root.kind is
      SourceRootKind.PROSE`) with `True`; naming a `REPOSITORY`-kind root at `--root` must
      go red (2.5), and confirm no marker file appears on disk under that mutation.
- [ ] 2.22 Add `cmd_mark_revisions` and the `mark revisions` argparse subparser (`--root`,
      `--revision-prefix`, `--ordinal-digits`, `--unsealed`) to `scripts/paper_cli.py`,
      nested under one new `mark` root (the `bib build` two-level nesting precedent — read
      `scripts/paper_cli.py`'s existing `bib`-root subparser wiring as the shape to mirror,
      read-only). Add `SOURCE_ROOT_UNDECLARABLE` and `SOURCE_DECLARATION_UNMATCHED` and
      `SOURCE_DECLARATION_HAND_EDITED` to `REFUSAL_CLASSIFICATION` (`work-state` tier).
- [ ] 2.23 RED-then-GREEN integration test: `write` refuses `SOURCE_REVISIONS_UNDECLARED`
      → run `mark revisions` for that root → `write` proceeds, one session, real CLI
      invocation (not calling the Python functions directly) — the "whole loop" proof.
- [ ] 2.24 Purge `__pycache__`/`.pyc` before running the mutation suite (a same-size
      mutation can silently reuse a stale bytecode cache in this repository). Extend
      `tests/paper_mutation.py`'s mutant-sandbox copy list with `paper_marker.py`.
- [ ] 2.25 Generality sweep: `rg` under `.claude/skills/paper-writing/scripts/` for any
      fixture root/folder name this unit's own tests invent; zero matches outside the test
      module.
- [ ] 2.26 Run `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions tests.paper_mutation`;
      re-run any mutation tests touched by 2.8/2.9's extraction to confirm no anchor moved
      (extraction shifts exact-match anchors elsewhere in the suite — this is the whole
      point of re-running the full mutation suite, not only the new tests); confirm green.

## Phase 3 — S3: `mark class` (the `guidance/` marker gets the same four pieces)

Design.md Decision F (guidance half), owner ruling that `guidance/`'s class marker enters
this change identically to the revisions marker.

- [ ] 3.1 RED: add a failing test asserting `paper_guidance._MARKER_ALLOWED_KEYS` is
      derived as `("class", paper_marker.SEAL_KEY)` — never re-spelled as a second
      literal. Import `paper_marker` in `scripts/paper_guidance.py`.
- [ ] 3.2 Extract `_validate_class_obj(obj, label)` out of `_classify`'s own shape-checking
      body; `_classify` becomes a thin wrapper. Confirm every existing `_classify`/
      `read_registry` test stays green unchanged.
- [ ] 3.3 RED: add failing tests for `declare_class(guidance_dir, folder, value, *,
      sealed=True)`: `--folder` naming a directory not directly under `guidance/` refuses
      `GUIDANCE_FOLDER_ABSENT`, naming every folder that is there; assert no directory is
      created.
- [ ] 3.4 RED: add a failing test asserting `--class` outside `CLASSES` refuses
      `UNKNOWN_GUIDANCE_CLASS` (reused verbatim).
- [ ] 3.5 RED: add a failing test asserting classing a second folder `evidence` while
      another already carries that class refuses `EVIDENCE_ROOT_AMBIGUOUS` (reused
      verbatim) **before the write** — assert the second folder's marker file was not
      created on disk (the "pre-write check must assert nothing was written" constraint;
      a message with a side effect is not a refusal).
- [ ] 3.6 Add `declare_class`: enumerate folders under `guidance_dir` the same way
      `read_registry` does, check membership (3.3), check `CLASSES` membership (3.4),
      check evidence-ambiguity (3.5), round-trip through `_validate_class_obj`, call
      `paper_marker.write`. Deliberately does NOT refuse an `evidence` folder holding zero
      ingested papers (`_ingested_root_status` already rules that an earlier stage, not a
      fault — no new check may contradict it). Confirm 3.3-3.5 green.
- [ ] 3.7 RED-then-GREEN: add a test asserting `mark class --unsealed` writes with no
      `seal_sha256` key, shape-identical to the pre-change grammar — mirrors 2.12 for the
      class marker.
- [ ] 3.8 RED: add a failing test asserting `_classify` refuses
      `GUIDANCE_DECLARATION_HAND_EDITED` when `seal_sha256` is present but mismatched —
      driven through a gating verb that classifies source material (`validate
      --source-md`), **never through `plan` alone**.
- [ ] 3.9 Add the seal check inside `_classify` (six lines): `paper_marker.seal_shape_error`
      first (malformed shape raises `MALFORMED_GUIDANCE_MARKER`, `_classify`'s own code),
      then `computed_seal` comparison when shape-valid. Confirm 3.8 green.
- [ ] 3.10 **Mutation — reachable through a gating verb, not only `plan`**: replace the
      seal-comparison line inside `_classify` with a constant `True`; the test proving
      `GUIDANCE_DECLARATION_HAND_EDITED` MUST be driven through `validate --source-md` (or
      an equivalent gating verb) and MUST go red.
- [ ] 3.11 Mutation: replace the directory-membership test in `declare_class` with `True`;
      naming an absent folder at `--folder` must go red (3.3), and confirm no directory is
      created under the mutation.
- [ ] 3.12 Mutation: delete the pre-write `EVIDENCE_ROOT_AMBIGUOUS` uniqueness check;
      confirm the second-evidence-folder test (3.5) goes red **and** its own assertion
      that the second marker was never written also fails under the mutation (proving the
      test actually checks the write-order, not merely the refusal).
- [ ] 3.13 Add `cmd_mark_class` and the `mark class` argparse subparser (`--folder`,
      `--class`, `--guidance`, `--unsealed`) nested under the same `mark` root S2 created.
      Add `GUIDANCE_FOLDER_ABSENT` and `GUIDANCE_DECLARATION_HAND_EDITED` to
      `REFUSAL_CLASSIFICATION` (`work-state` tier).
- [ ] 3.14 Generality sweep: `rg` under `.claude/skills/paper-writing/scripts/` for any
      fixture folder name this unit's own tests invent; zero matches outside the test
      module.
- [ ] 3.15 Run `.venv/bin/python -m unittest tests.test_paper_decisions tests.paper_mutation`;
      confirm green, no new failures.

## Phase 4 — S4: ASK — the enriched refusal, byte-identical at both raise sites

Design.md Decision H. `paper_declarations._resolve_bind_document` (line ~1029) and
`paper_graph.resolve_section_index` (line ~427) — read both directly before editing
(read-only reference: `scripts/paper_declarations.py:1008-1034`,
`scripts/paper_graph.py:427-433`) — carry today's byte-identical text by coincidence of a
copied string, not a shared builder.

- [ ] 4.1 Extract `_unmarked_candidates(base_path) -> list` into
      `scripts/paper_declarations.py`: `sorted(p.name for p in base_path.glob("*.md"))` —
      the SAME derivation `describe_binding_candidates`'s own no-marker branch already
      computes. `describe_binding_candidates` calls it too (one lister, two callers).
      Confirm `describe_binding_candidates`'s existing tests stay green unchanged.
- [ ] 4.2 RED: add a failing test asserting
      `source_revisions_undeclared_detail(status, root)` names the root, the marker
      filename, every `*.md` file currently under the root (via `_unmarked_candidates`),
      and the exact `mark revisions --root <name> --revision-prefix <prefix>
      --ordinal-digits <n>` invocation that answers it.
- [ ] 4.3 Add `source_revisions_undeclared_detail` to `scripts/paper_declarations.py`.
      Confirm 4.2 green.
- [ ] 4.4 Wire `_resolve_bind_document`'s existing `SOURCE_REVISIONS_UNDECLARED` raise to
      call `source_revisions_undeclared_detail` instead of its own inline string.
- [ ] 4.5 Wire `paper_graph.resolve_section_index`'s existing `SOURCE_REVISIONS_UNDECLARED`
      raise to call the same function (`paper_graph` already imports
      `paper_declarations`, per design's measured invariant — confirm the import
      direction with `rg` before wiring; it must not run the other way).
- [ ] 4.6 RED-then-GREEN: add a test asserting both raise sites produce byte-identical
      detail text for the same root and disk state — reached once through `bind`/
      `_resolve_bind_document`'s own path and once through `write`/`resolve_section_index`.
- [ ] 4.7 Mutation: inline a literal message at ONE of the two raise sites (revert the
      call to the shared builder at either site); confirm the byte-identity test (4.6)
      goes red.
- [ ] 4.8 RED-then-GREEN: add a test asserting deleting an existing marker file and
      re-resolving the same binding still refuses `SOURCE_REVISIONS_UNDECLARED` (never a
      silent `unmeasured` degrade — this is `source-section-binding`'s existing, unchanged
      guarantee, checked here because the enriched detail text is new code touching the
      same raise sites).
- [ ] 4.9 Generality sweep: `rg` under `.claude/skills/paper-writing/scripts/` for any
      fixture root/lineage name this unit's own tests invent; zero matches outside the
      test module.
- [ ] 4.10 Run `.venv/bin/python -m unittest tests.test_paper_writing tests.test_paper_decisions`;
      confirm green, no new failures.

## Phase 5 — S5: Docs, honest strength, roster re-measured, both suites

Design.md Decision G (the four-surface test), Migration/Rollout.

- [ ] 5.1 RED: add a failing test that derives the expected `SEAL_STRENGTH` text from
      `paper_marker.SEAL_STRENGTH` itself and asserts its byte-identical presence in: (a)
      `scripts/paper_marker.py`'s own module docstring, (b) `SOURCE_DECLARATION_HAND_EDITED`'s
      refusal detail wording, (c) `GUIDANCE_DECLARATION_HAND_EDITED`'s refusal detail
      wording, (d) `SKILL.md`, (e) `references/usage.md`.
- [ ] 5.2 Confirm `paper_marker.py`'s module docstring quotes `SEAL_STRENGTH` verbatim (if
      2.2 did not already word it exactly). Confirm both `*_HAND_EDITED` refusal details
      (2.17, 3.9) interpolate the constant rather than restating it as a separate literal.
- [ ] 5.3 Update `.claude/skills/paper-writing/SKILL.md`: the loop (refusal → `mark` →
      retry) for both marker kinds, the position report's new `sourceRoots` key and
      widened `guidance` shape, `SEAL_STRENGTH` verbatim, one roster entry per new refusal
      code (`SOURCE_DECLARATION_UNMATCHED`, `SOURCE_DECLARATION_HAND_EDITED`,
      `GUIDANCE_DECLARATION_HAND_EDITED`, `SOURCE_ROOT_UNDECLARABLE`,
      `GUIDANCE_FOLDER_ABSENT`).
- [ ] 5.4 Update `references/usage.md` identically — a doc fix that stops at `SKILL.md`
      is half a fix, per the proposal's own framing.
- [ ] 5.5 Confirm 5.1 green against 5.2-5.4.
- [ ] 5.6 Mutation: weaken `SEAL_STRENGTH` to drop "not tamper-proofing"; confirm 5.1 goes
      red — strengthening the claim anywhere is a red test, never a review miss.
- [ ] 5.7 Confirm `git diff main -- sections/` is empty (never edit any file under
      `sections/`) and that `git diff --summary main` shows zero `delete mode` lines
      anywhere in this change (nothing deletes files).
- [ ] 5.8 Re-run Phase 0's audit (0.1-0.2) against the landed tree: confirm zero NEW leak
      introduced by this change's own code, comments, docstrings, or fixtures across all
      four prior phases; confirm the pre-existing 48-hit collision and the one known
      `ForgeVocabularyDerivedGuardTests` failure are unchanged, not widened.
- [ ] 5.9 Re-derive the refusal roster by EXECUTING
      `tests.test_paper_writing.reachable_paper_refusal_codes()` after all engine code
      from S1-S4 has landed. Record the measured number in the apply report. **Do not
      write a predicted number into any artifact before this task runs** — the live
      figure today is 154.
- [ ] 5.10 Purge `__pycache__`/`.pyc` under `.claude/skills/paper-writing/` and `tests/`
      before the final full-suite run (guards against a stale bytecode cache masking a
      same-size mutation from earlier phases).
- [ ] 5.11 Run `npm test`; confirm 640/640.
- [ ] 5.12 Run the Python suite in chunks, sequentially, never concurrently (a cross-chunk
      race on the shared `implementations/` directory has produced a spurious failure
      twice in this repository): `.venv/bin/python -m unittest discover -s tests -p
      'test_*.py'`, split as the two most recent archived changes' own verify reports
      split it, with `PYTHONPATH=tests` isolated to `test_orphan_sweep.py`'s own chunk.
      Before recording numbers, check for and remove any orphaned
      `implementations/_smokebox_*` directory left by a killed mid-run
      `test_proposal_implementation` invocation, then re-run that chunk clean.
- [ ] 5.13 Confirm the Python suite shows **at most one** known pre-existing failure
      (`test_proposal_implementation.ForgeVocabularyDerivedGuardTests.test_rule_b_finds_no_target_vocabulary_in_the_forge`,
      naming only the three sibling skills). **Any second failure belongs to this change
      and blocks delivery.**
- [ ] 5.14 Update `design.md`'s Open Questions section: confirm both recorded items stay
      explicitly out of scope, not silently resolved by this change.

## Discipline carried forward (non-negotiable, not restated per task above)

- Red first, every guard, every phase — a task without a preceding RED task is
  incomplete, not merely undocumented.
- A mutation is the only proof a guard holds; every mutation task above names the exact
  line/condition it flips and the exact test that must go red.
- Every seal mutation (2.19, 3.10) is driven through a gating verb (`write`, `validate
  --source-md`) — **never through `plan` alone**. A `plan`-only proof satisfies nothing
  here; it is invariant 4's own counter-example, restated as a task rather than a
  footnote.
- Byte-identity (4.6) and honest strength (5.1) are each backed by a test that derives
  its expectation from ONE constant/builder, never a second hand-copied literal, so
  drift is a red test rather than a review miss.
- Purge `.pyc`/`__pycache__` before any mutation run (2.24, 5.10) — a same-size mutation
  reusing a stale bytecode cache in this repository has passed a mutant before.
- The roster is measured, never forecast (5.9) — it runs after all engine code lands, and
  no predicted number enters any artifact before that.
- Nothing deletes files; never edit any file under `sections/` — checked explicitly at 5.7.
- The GATE audit (Phase 0) runs once before any code, and again at 5.8 after all code —
  a disclosed pre-existing 48-hit collision across sibling skills is not this change's to
  fix and must not be allowed to read as new.
