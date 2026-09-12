# Tasks: Each Document Names Its Own Revision

> **Budget note.** Over the 530-word guidance, on the precedent this change's
> proposal and design already set. Every threat-matrix row, the five-member
> derived set, D1-D9, and the three predicted reds are mechanics apply must
> not re-derive; compressing them below what design already made concrete
> would move the invention into apply, which is the failure mode this whole
> change exists to close.

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | ~870 (design's own floor; every estimate this session ran over, Cut 3 by 78%) |
| 400-line budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (fixture-red) → PR 2 (per-document resolution) → PR 3 (refusal + spec correction) |
| Delivery strategy | auto-chain |
| Chain strategy | feature-branch-chain |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: feature-branch-chain
400-line budget risk: High

Feature-branch-chain, not stacked-to-main: PR 1's RED state must never land on
main by itself (`tests/test_implementation_pair.py` fails on purpose). PR 2
bases on PR 1's branch, PR 3 bases on PR 2's; only the tracker merges to main.
At ~870 lines against the 1400 budget with every prior estimate under-shooting,
grade PR 2 (~450 lines, the derived set plus D1/D2/D7/D8/D9) as the size risk
to watch first — split it again if measured lines exceed ~500.

### Suggested Work Units

| Unit | Goal | Likely PR | Focused test command | Runtime harness | Rollback boundary |
|------|------|-----------|----------------------|-----------------|-------------------|
| 1 | Fixture reshape reddens the pair suite unassisted | PR 1 | `.venv/bin/python -m unittest tests.test_implementation_pair.TwoDocumentLifecycleTests tests.test_implementation_pair.TwoDocumentPositionWriteTests -v` | Real subprocess pair tests (existing harness) | Revert the RED commit; no carrier/code touched |
| 2 | Per-document resolution turns PR 1's red green | PR 2 | Same command as Unit 1, expect green; then `.venv/bin/python -m unittest discover -s tests` | Real subprocess pair + full suite | Revert to PR 1 tip; `tests/seal/` untouched by construction |
| 3 | The refusal, its roster, and the spec correction | PR 3 | `.venv/bin/python -m unittest tests.test_proposal_implementation.GatingRefusalRosterTests -v` plus the new `TwoDocumentAmbiguousFamilyRefusesTests` | Real subprocess refusal case | Revert to PR 2 tip; no minted token exists under a two-doc profile yet |

## Phase 0: Re-Derive Before Coding

- [ ] 0.1 Re-derive the consumer set of `_extra_document_revisions` (via
      `_admissibility_extra_documents`, `_position_extra_documents`) by
      grepping every caller; do not carry the 5-member list from
      proposal/design unmeasured — confirm `revision_source`,
      `admissibility_record`'s staleness loop, `position_state`'s
      `extra_sources`, and `admissibility_record`'s positional-vs-label
      pairing all resolve to real, currently-uncorrected code.
- [ ] 0.2 Re-confirm M3 (containment): grep `_AUTHORIZATION_BINDING_KEYS`,
      `_authorization_binding_keys`, and every shipping `impl_profile.py`'s
      `documents` list; assert none has `len(documents) > 1` before touching
      any producer.

## Phase 1 (PR 1 — Slice 1: fixture-red)

- [ ] 1.1 test(pair): in `tests/test_implementation_pair.py`, give
      `TwoDocumentLifecycleTests` and `TwoDocumentPositionWriteTests` a
      distinct `REVISION_1` (own stem, own version letter). Edit only
      `setUp` (write document 1's file under `REVISION_1`) and
      `_doc1_sha256` (read it back under `REVISION_1`) in each class —
      no `assert*` line changes.
- [ ] 1.2 Run the pair suite; confirm exactly the three predicted reds (the
      `_doc1_sha256()` comparisons, `assertNotEqual(extra_entry["status"],
      "unknown")`, `compatibility["status"] == "ok"`) and no fourth failure
      in either suite. A fourth is information — name it before continuing,
      do not proceed silently.
- [ ] 1.3 Run `tests/seal/`; confirm all 28 digests byte-identical (the
      fixture edit must not move a document-0-only golden).
- [ ] 1.4 Commit the RED state alone (`test(...)`, no implementation) as
      this slice's deliverable.
- [ ] 1.5 After PR 2 and PR 3 land, verify
      `git merge-base --is-ancestor <slice-1-red-sha> <tip>` exits 0 —
      the RED commit must remain a real, unamended ancestor.

## Phase 2 (PR 2 — Slice 2: per-document resolution)

- [ ] 2.1 Add `discover_document_revision(index)` next to `proposals_root`
      in `implementation_engine.py`: not-a-directory → `revision_discovery`'s
      `empty` shape; marker filter first via `is_managed_artifact`/
      `MANAGED_ARTIFACT_MARKER`; digit-elided family key; one family →
      digit-tuple `max` (`tied` reported); more than one family → ambiguous
      (surfaced as a refusal in Phase 3).
- [ ] 2.2 Add `document_revision_names(revision)` with module-level
      `_DOCUMENT_NAME_CACHE: dict[tuple, tuple[str | None, ...]]`, keyed on
      `(revision, *[str(proposals_root(i)) for i in range(len(DOCUMENTS))])`
      — never `revision` alone.
- [ ] 2.3 Give `revision_source`, `revision_discovery`, `latest_revision`
      the `index: int = 0` parameter; rewrite `revision_source`'s docstring
      to a per-index dumb reader, deleting the shared-name claim; make
      `cmd_verify`'s per-document family seed per-document.
- [ ] 2.4 Rewrite `_extra_document_revisions`'s loop to fill each entry's
      `"revision"` from `document_revision_names(revision)`, resolved via
      `revision_source(names[i], i)` — remove the single shared-string
      literal (M2).
- [ ] 2.5 Wire `extra_sources` (D7) at all nine `position_state` call sites
      M4 names, passing `[revision_source(names[i], i) for i in
      range(1, len(DOCUMENTS))]` when resolved, else `None`.
- [ ] 2.6 Fix `admissibility_record`'s extra-document loop (D8): pair the
      recorded `documents` list by `entry["label"]`, matching
      `position_state`'s `header_documents` pairing, not `enumerate(extra,
      start=1)`.
- [ ] 2.7 Give `_extra_document_fidelity_status`'s `fidelityByDocument`
      entries a `revision` key (D9), additive, under
      `len(DOCUMENTS) > 1` only; update both `sources_by_document`
      constructions (`cmd_admit` near line-adjacent `sources_by_document =
      {DOCUMENTS[0]["label"]: source}`, and `cmd_verify`'s
      `verify_sources_by_document`) to use per-index names.
- [ ] 2.8 test(pair): add corpus cases D4 requires for slice 2's happy
      paths — a second same-family file in document 1's root (real `max`
      pick), one marker-owned root, one non-marker root, one empty root —
      in `tests/pair/corpus.py`/`tests/pair/cases.json`.
- [ ] 2.9 GREEN commit: move the assertions encoding the old shared-name
      semantics (`"revision": self.REVISION` on a document-1 entry →
      `self.REVISION_1`) — never in the RED commit.
- [ ] 2.10 Add the memo mutation test (D2): re-point
      `IMPLEMENTATION_PROPOSALS_1` mid-process between two
      `document_revision_names` calls in the same command; assert the
      second call's answer changes — proves the cache key carries the
      roots, not just `revision`.
- [ ] 2.11 Add the `boundTo` integration test (D7): document 1 reports
      `current`, then `stale` after its own file changes — the value M4
      shows is unreachable before this wiring.
- [ ] 2.12 Run `tests/seal/`; confirm 28 digests byte-identical again.
      Confirm `tests/pair/digests.json`'s two cases are unmoved (predicted,
      not assumed).

## Phase 3 (PR 3 — Slice 3: the refusal + spec correction)

- [ ] 3.1 Add `DOCUMENT_REVISION_UNREADABLE` to `GATING_REFUSALS`, classified
      `WORK_STATE`; raise it inside `_extra_document_revisions` only, `detail`
      naming the index, label, directory, and cause (no family / ambiguous
      families / discovered name unreadable).
- [ ] 3.2 Add the refusal's publication point to `refusal_resolution`.
- [ ] 3.3 Add the roster row to `.claude/skills/proposal-implementation/SKILL.md`
      and `references/usage.md`, alongside the existing `REVISION_UNREADABLE`
      row.
- [ ] 3.4 Measure and update `reachable_refusal_codes()`'s pin in
      `tests/test_proposal_implementation.py` (predicted 113 → 114, exactly
      one; re-measure, do not repeat the number).
- [ ] 3.5 test(pair): add the ambiguous-family corpus case (two families in
      document 1's root) and `TwoDocumentAmbiguousFamilyRefusesTests`,
      asserting exit code 2, `DOCUMENT_REVISION_UNREADABLE`, and a `detail`
      naming both families.
- [ ] 3.6 Add `GatingRefusalRosterTests` coverage for the new code across all
      three roster surfaces (classification, `refusal_resolution`, doc row).
- [ ] 3.7 Mutation test (D5): mutate the ambiguity branch from
      `raise Refused(...)` to "pick the first family" (not the `raise`
      itself — a sha lock survives that). Confirm every sha/`documents`
      assertion in the lifecycle classes still passes and only
      `TwoDocumentAmbiguousFamilyRefusesTests` catches it. Anchor discipline:
      assert old-spelling count is exactly 1 / new is 0 before the edit, and
      the reverse after, both directions.
- [ ] 3.8 Correct `openspec/specs/implementation-engine-neutrality/spec.md`:
      `unreached_mathematics` → `unreached_modules`, both occurrences
      (requirement text and scenario). Confirm `rg unreached_mathematics
      openspec/specs/` returns nothing afterward.
- [ ] 3.9 Run `tests/seal/`; confirm 28 digests byte-identical a third time.

## Phase 4: Non-Interference Verification (after PR 3, before chain merge)

- [ ] 4.1 Run `npm test`; confirm 595/595, unchanged from baseline `4dd91df`.
- [ ] 4.2 Run `.venv/bin/python -m unittest discover -s tests`; confirm
      `OK (skipped=6)` — `skipped=6` must not move, `Ran` may grow. Paste
      before/after counts.
- [ ] 4.3 `git diff --exit-code` against `4dd91df` for `tests/seal/**`,
      `.claude/skills/{proposal,experimental}-deliberation/**`,
      `_core/deliberation/**` — must exit 0.
- [ ] 4.4 Confirm D9's non-additions stayed out: no `--revision-<index>`
      flag, no `KitAgreementLockTests._profile()` change, no
      `proposalDigest`-family rename.
- [ ] 4.5 Run `_shared/tools/check_citations.py` against this tasks.md and
      state the result before apply proceeds.
