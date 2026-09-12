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

- [x] 0.1 Re-derive the consumer set of `_extra_document_revisions` (via
      `_admissibility_extra_documents`, `_position_extra_documents`) by
      grepping every caller; do not carry the 5-member list from
      proposal/design unmeasured — confirm `revision_source`,
      `admissibility_record`'s staleness loop, `position_state`'s
      `extra_sources`, and `admissibility_record`'s positional-vs-label
      pairing all resolve to real, currently-uncorrected code.

      Measured: `_extra_document_revisions` consumed by
      `_admissibility_extra_documents`, `_position_extra_documents`, and
      directly by `cmd_gate`'s `gate_binding`, `cmd_offer`'s
      `_authorization_binding` (via `documentRevisions`), and `cmd_close`
      (`extra_documents`). `position_state`'s `extra_sources` confirmed
      declared/defaulted/passed-by-none at all 9 call sites (grep:
      cmd_probe, cmd_discuss, cmd_settle, cmd_gate, cmd_offer, cmd_close x2,
      cmd_step, cmd_verify). `admissibility_record`'s extra loop confirmed
      `enumerate(extra, start=1)` positional, never reading `label` — AND a
      second defect one call deeper: it read `revision_source(revision,
      index)` using the SCALAR (document 0's) `revision`, not a per-document
      name. Both fixed together (D8).
- [x] 0.2 Re-confirm M3 (containment): grep `_AUTHORIZATION_BINDING_KEYS`,
      `_authorization_binding_keys`, and every shipping `impl_profile.py`'s
      `documents` list; assert none has `len(documents) > 1` before touching
      any producer.

      Measured: `_AUTHORIZATION_BINDING_KEYS` is an untouched literal
      8-tuple; the only shipping profile (`proposal-implementation/
      impl_profile.py`) declares one `documents` entry. Confirmed holding.

## Phase 1 (PR 1 — Slice 1: fixture-red)

- [x] 1.1 test(pair): in `tests/test_implementation_pair.py`, give
      `TwoDocumentLifecycleTests` and `TwoDocumentPositionWriteTests` a
      distinct `REVISION_1` (own stem, own version letter). Edit only
      `setUp` (write document 1's file under `REVISION_1`) and
      `_doc1_sha256` (read it back under `REVISION_1`) in each class —
      no `assert*` line changes.
- [x] 1.2 Run the pair suite; confirm exactly the three predicted reds (the
      `_doc1_sha256()` comparisons, `assertNotEqual(extra_entry["status"],
      "unknown")`, `compatibility["status"] == "ok"`) and no fourth failure
      in either suite. A fourth is information — name it before continuing,
      do not proceed silently.

      Measured: running the exact command named in Suggested Work Units,
      both test methods FAIL, and each halts at the FIRST assertion its own
      body reaches (red #1, the sha comparison) — Python's `assertEqual`
      raises immediately, so the method never reaches its own later `extra_
      entry["status"]`/`compatibility["status"]` lines in the same run.
      Verified independently (standalone probe, not persisted, using the
      identical fixture and both real findings): `extra_entry["status"]`
      does read `"unknown"` (red #2, confirmed). `compatibility["status"]`
      does NOT merely read a non-"ok" value as red #3's own assertion
      implies — `cmd_verify` CRASHES with an unhandled `TypeError` inside
      `remedy_compatibility` (`"\n".join(texts)` over a list containing
      `None`), because a finding named document 1 while its source resolved
      to `None`. Named as the fourth per this task's own instruction. Never
      reached by the committed suite (which halts earlier), so it is NOT a
      fourth failure IN the RED commit; it is a genuine, orthogonal,
      pre-existing crash this fixture reshape exposed for the first time.
      Fixed as a minimal, scoped correction in Phase 2 (filter `None` out of
      `texts` before joining) — outside D1–D9, documented as its own finding.
- [x] 1.3 Run `tests/seal/`; confirm all 28 digests byte-identical (the
      fixture edit must not move a document-0-only golden).
- [x] 1.4 Commit the RED state alone (`test(...)`, no implementation) as
      this slice's deliverable. — `bec4d12`
- [ ] 1.5 After PR 2 and PR 3 land, verify
      `git merge-base --is-ancestor <slice-1-red-sha> <tip>` exits 0 —
      the RED commit must remain a real, unamended ancestor.

## Phase 2 (PR 2 — Slice 2: per-document resolution)

- [x] 2.1 Add `discover_document_revision(index)` next to `proposals_root`
      in `implementation_engine.py`: not-a-directory → `revision_discovery`'s
      `empty` shape; marker filter first via `is_managed_artifact`/
      `MANAGED_ARTIFACT_MARKER`; digit-elided family key; one family →
      digit-tuple `max` (`tied` reported); more than one family → ambiguous
      (surfaced as a refusal in Phase 3).
- [x] 2.2 Add `document_revision_names(revision)` with module-level
      `_DOCUMENT_NAME_CACHE: dict[tuple, tuple[str | None, ...]]`, keyed on
      `(revision, *[str(proposals_root(i)) for i in range(len(DOCUMENTS))])`
      — never `revision` alone.
- [x] 2.3 Give `revision_source`, `revision_discovery`, `latest_revision`
      the `index: int = 0` parameter; rewrite `revision_source`'s docstring
      to a per-index dumb reader, deleting the shared-name claim; make
      `cmd_verify`'s per-document family seed per-document.

      `revision_discovery`/`latest_revision` now accept `index` (default 0,
      byte-identical); `cmd_verify` computes `document_names =
      document_revision_names(revision)` once and hands each index's own
      name to `_extra_document_fidelity_status`/`fidelityByDocument`, never
      document 0's `revision` read into another index's directory.
- [x] 2.4 Rewrite `_extra_document_revisions`'s loop to fill each entry's
      `"revision"` from `document_revision_names(revision)`, resolved via
      `revision_source(names[i], i)` — remove the single shared-string
      literal (M2).
- [x] 2.5 Wire `extra_sources` (D7) at all nine `position_state` call sites
      M4 names, passing `[revision_source(names[i], i) for i in
      range(1, len(DOCUMENTS))]` when resolved, else `None`.

      Added `_document_extra_sources(revision)` helper, used at all nine
      sites (6 where a revision can resolve: cmd_probe, cmd_gate, cmd_offer,
      cmd_close x2, cmd_verify; 3 where revision is always `None` by design
      — cmd_discuss, cmd_settle, cmd_step — wired for uniformity, provably
      inert). Extra finding closed in the same slice: `position_state`'s
      multi branch could not distinguish "never recorded" from "recorded,
      now mismatched" for an extra document (both read `block_sha256=None`
      into `_bound_to`) — unreachable before `extra_sources` carried a real
      value, and would have wrongly reported `"stale"` (blocking a launch)
      for a document simply never yet written into the header. Fixed:
      `entry is None` now reads `"unknown"` directly, never `_bound_to`.
- [x] 2.6 Fix `admissibility_record`'s extra-document loop (D8): pair the
      recorded `documents` list by `entry["label"]`, matching
      `position_state`'s `header_documents` pairing, not `enumerate(extra,
      start=1)`.
- [x] 2.7 Give `_extra_document_fidelity_status`'s `fidelityByDocument`
      entries a `revision` key (D9), additive, under
      `len(DOCUMENTS) > 1` only; update both `sources_by_document`
      constructions (`cmd_admit` near line-adjacent `sources_by_document =
      {DOCUMENTS[0]["label"]: source}`, and `cmd_verify`'s
      `verify_sources_by_document`) to use per-index names.
- [x] 2.8 test(pair): add corpus cases D4 requires for slice 2's happy
      paths — a second same-family file in document 1's root (real `max`
      pick), one marker-owned root, one non-marker root, one empty root —
      in `tests/pair/corpus.py`/`tests/pair/cases.json`.

      Deviation, stated rather than silently taken: implemented as direct
      unit tests (`DiscoverDocumentRevisionTests` in
      `tests/test_implementation_pair.py`) against
      `discover_document_revision` via `IMPLEMENTATION_PROPOSALS_1`
      overrides, not as new `tests/pair/cases.json` golden-digest entries.
      `cases.json`'s existing two cases drive the `name` command, which
      never reads a revision at all — extending its golden-digest machinery
      to cover file-content-shaped scenarios would invent a new digested
      command shape the design does not otherwise need. A direct unit test
      is the identical style `ExtraDocumentFidelityStatusTests`
      (`test_proposal_implementation.py`) already established for the
      sibling per-document function one call site over, and is what design
      md's own Testing Strategy table names ("Unit | discover_document_
      revision | marker-owned / hand-authored / tie / empty / ambiguous").
      Covers: empty root, hand-authored max-pick, a real tie, marker-owned
      (with a non-marker candidate correctly excluded). The ambiguous case
      lands in Phase 3, proven end to end through the real refusal instead.
- [x] 2.9 GREEN commit: move the assertions encoding the old shared-name
      semantics (`"revision": self.REVISION` on a document-1 entry →
      `self.REVISION_1`) — never in the RED commit.
- [x] 2.10 Add the memo mutation test (D2): re-point
      `IMPLEMENTATION_PROPOSALS_1` mid-process between two
      `document_revision_names` calls in the same command; assert the
      second call's answer changes — proves the cache key carries the
      roots, not just `revision`.

      `DocumentRevisionNamesMemoTests`. This process's own
      `IMPLEMENTATION_DOMAIN_PROFILE` declares one document, so `DOCUMENTS`
      is reassigned in-process (never reaching a subprocess) purely to give
      the memo's own loop a second index to resolve; confirmed: same
      `revision` argument, two different roots, two different answers.
- [x] 2.11 Add the `boundTo` integration test (D7): document 1 reports
      `current`, then `stale` after its own file changes — the value M4
      shows is unreachable before this wiring.

      `DocumentOneBoundToTests`, real subprocess: `position --sequence`
      install records document 1's sha, `probe` reads `current`, document
      1's file is rewritten, `probe` again reads `stale`.
- [x] 2.12 Run `tests/seal/`; confirm 28 digests byte-identical again.
      Confirm `tests/pair/digests.json`'s two cases are unmoved (predicted,
      not assumed).

      Confirmed both: `tests/seal/digests.json` sha256
      `011300df7daf001055fa30d895aeaac27a680e2abcc239a027b5c30169dc6f75`,
      byte-identical. `tests/pair/digests.json`'s two cases pass unmoved
      (`PairCorpusComparisonTests`, unchanged).

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
