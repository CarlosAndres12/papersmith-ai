# Tasks: The Writer May Assert Only What It Was Given

RED/GREEN pairs are combined into one task line to hold the size budget; each
still requires a genuinely failing test first. Mutation and threat-matrix
tasks purge `__pycache__` and assert an exact anchor count **and** a changed
digest, per the proposal's seven mutations and design's threat matrix.

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 1100–1500 (5 new modules + widened contract/vocabulary + CLI wiring + 10 section headers + 3 agent contracts + SKILL.md + tests) |
| Applicable budget | **1400 lines** (project override for this build, not the skill's 400 default) |
| Budget risk | High |
| Chained PRs recommended | Yes |
| Suggested split | PR 1 (writer + contract auditor) → PR 2 (style channel + leak guard) |
| Delivery strategy | ask-on-risk |
| Chain strategy | stacked-to-main |

Decision needed before apply: No
Chained PRs recommended: Yes
Chain strategy: stacked-to-main
400-line budget risk: High

(Splitting into two stacked units is already pre-approved for this build per
the orchestrator's preflight; the guard line above names risk against the
project's 1400-line budget, not the skill's literal 400.)

### Suggested Work Units

| Unit | Goal | PR | Focused test command | Runtime harness | Rollback boundary |
|---|---|---|---|---|---|
| 1 | Evidence-bound drafting + contract audit + `write` pipeline, mode widening, module-completeness lock, no-subprocess/no-live-agent guards | PR 1 | `.venv/bin/python -m unittest tests.test_paper_writing -v` | N/A — no runtime harness exists; the suite exercises recorded transcripts and fixtures only, by design (D2) | Revert `paper_bindings.py`, `paper_audit.py`, `paper_write.py`, the `write` verb, `mode` widening; `sections/*.md` headers stay schema-valid without `mode` per the section-contract delta |
| 2 | Style channel + style-leak detection (register distance, overlap, tripwire) | PR 2 | `.venv/bin/python -m unittest tests.test_paper_writing -v` | N/A — same reason as Unit 1 | Revert `paper_style.py`, `paper_leak.py`, their CLI imports; Unit 1 stands alone with an empty style channel (valid since Unit 1) |

## Sequencing Note

Applies after `the-contract-is-data-not-code` (unit 1 committed `b1d67dc`).
Phases 3 (guidance registry) and 6 (evidence validator) are interfaces, not
code — task against fixtures. Two sites move if either lands differently:
**R's residency verification** (`paper_style`'s span-byte-presence check
depends on Phase 3's ingested-`.md` shape) and **mode admissibility**
(`evidence:`-binding class depends on Phase 6's evidence record exposing
`regime ∈ {discovery, resolution}`).

## Work Unit 1 — Writer + Contract Auditor

- [x] 1.1 `paper_contract.py`/`paper_vocabulary.py`: `mode` joins
  `_TOP_LEVEL_OPTIONAL`/`_BLOCK_OPTIONAL`; factor `_validate_source` out of
  `_validate_after_list`; add `MODES`, `validate_mode`. RED: `UNKNOWN_MODE`,
  section-default-inherits, block-overrides scenarios → GREEN: implement.
- [x] 1.2 `paper_bindings.py`: redactor input contract (4 inputs, empty style
  set valid) + binding map (`evidence:`/`fact:`/`structural`, exactly one
  kind per sentence). RED→GREEN.
- [x] 1.3 `paper_bindings.py`: draft-vs-map reconciliation — CLI segments
  sentences from emitted LaTeX itself, never trusts the redactor's account;
  `UNBOUND_SENTENCE`/`BINDING_ORPHANED`. RED→GREEN.
- [x] 1.4 `paper_bindings.py`: binding resolution —
  `EVIDENCE_ID_UNKNOWN`/`FACT_NOT_LICENSED`. RED→GREEN.
- [x] 1.5 `paper_bindings.py`: structural typing —
  `STRUCTURAL_CARRIES_CLAIM` on numeral/`\cite`/comparative/named-external-
  object (typed rule, not a blocklist — mutation 3 coverage); plain
  structural passes. RED→GREEN.
- [x] 1.6 `paper_bindings.py`: mode admissibility — `MODE_VIOLATION`;
  `transposition` admits `fact`/`structural`/`resolution`-evidence,
  `argument` additionally admits `discovery`-evidence. RED→GREEN.
- [x] 1.7 **Ruling 3 — evidence-regime refusal.** A block whose `citations`
  regime (read from the contract header, never inferred) is not `none` and
  has no evidence set is **refused** (new code, e.g. `EVIDENCE_SET_REQUIRED`)
  in `paper_write.py`'s readiness stage — not reported `unvalidated`; a
  `regime: none` block writes with no evidence and no refusal. RED→GREEN.
- [x] 1.8 `paper_audit.py`: verbatim `## Disqualifiers` extraction (zero
  interpretation in code); per-bullet `fires`/`clear`/`undecidable` with
  quoted span required for `fires` (no span → downgrades to `undecidable`);
  outcome = `any(fires)` alone, so all-`undecidable` reports and does not
  block; `DISQUALIFIERS_ABSENT` when the heading is missing, verified against
  all ten shipped `sections/*.md` carrying it today. RED→GREEN.
- [x] 1.9 `paper_write.py`: pipeline order (readiness → gate → draft →
  evidence-audit → contract-audit → `substitute --contract`); a failing
  evidence-audit stops before contract-audit runs. RED→GREEN.
- [x] 1.10 `paper_write.py`: one bounded re-draft — attempt ledger
  `paper/.paper-writing/attempts/<block>.json` keyed by
  `digest(contract, evidence, mode)`; re-draft carries fired bullets + quoted
  spans as feedback into the same auditor/inputs; `AUDIT_EXHAUSTED` on a
  second `fires`, `main.tex` byte-identical to pre-`write` state. RED→GREEN.
- [x] 1.11 Mutations 1–5 (drop reconciliation; let `undecidable` pass; let
  `write` substitute on exhausted audit; hardcode a disqualifier bullet;
  treat absent heading as zero disqualifiers) executed against
  `paper_bindings`/`paper_audit`/`paper_write`.
- [x] 1.12 **Module-list completeness (highest-value task).** RED: add a
  sixth, unimported module under `scripts/` and watch
  `{stems of scripts/*.py} == paper_cli.py`'s module-level import set` fail.
  GREEN: assert that equality in `test_paper_writing.py`, remove the planted
  module, then import `paper_bindings`/`paper_audit`/`paper_write` at
  `paper_cli.py` module level unconditionally.
- [x] 1.13 Wire `write` (`--draft <path>`, `--audit <path>` JSON envelopes)
  into `paper_cli.py`; extend `REFUSAL_CLASSIFICATION` with Unit 1's new
  codes; move `test_the_derivation_finds_the_measured_count`'s `21` to the
  newly measured count (measured 78 at the WU1 commit, then 79 once WU2's
  `paper_leak.py` import lands).
- [x] 1.14 **Ruling 1 — no-subprocess scan, one named exception.** Per the
  orchestrator's explicit ruling for this change (superseding this task's
  own "empty today" framing): the exception tuple is pinned NOW to exactly
  `("paper_latex.py",)`, not empty, even though that file does not exist
  yet — `assertEqual(len(SUBPROCESS_EXCEPTIONS), 1)` is the literal a
  second entry requires hand-editing. RED: a planted `import subprocess` in
  a throwaway fixture dir is caught; the real `scripts/*.py` tree scans
  clean. GREEN: implemented forbidding `subprocess`/`os.system`/
  `os.popen`/`os.exec*`/`multiprocessing`, as a structural scan living in
  `tests/test_paper_writing.py` (source-scan tooling, not production code —
  `design.md`'s own Testing Strategy classification).
- [x] 1.15 Path containment: `--draft`/`--audit`/`--transcript` all resolve
  through `_resolve_repo_path` in `paper_cli.py`, reusing `FORGE_ROOT`
  containment / `PAPER_OUTSIDE_REPOSITORY` — no new code for the same
  condition.
- [x] 1.16 Live-agent guard: a module-scoped `subprocess.Popen` monitor
  (`ZZLiveAgentGuardTests`, named to sort last so every subprocess-launching
  test class in this module has already run) asserts zero launches naming
  an agent binary; recorded fixture drafts/audits exercise the redactor and
  contract-auditor shapes without ever invoking either as a process.
- [x] 1.17 `.claude/agents/redactor.md`, `.claude/agents/contract-auditor.md`
  landed, carrying this repo's full shared role-discipline report shape
  (`did`/`stoppedAt`/`state`/`owed`, "Measure before you assert") —
  `tests/test_agents.py`'s `AgentBindingTests` enforces this and initially
  caught the gap, fixed same-session. `SKILL.md` updated (three channels,
  `write`, two audits, the shuttle procedure). **Deferred, not done**:
  transcribing `mode` into the ten shipped `sections/*.md` headers. The
  `section-contract` delta's own "Headers Written Before mode Existed"
  requirement makes an absent `mode` schema-valid by design, so this is a
  safe deferral, not a broken contract — `write`'s readiness stage refuses
  `MODE_ABSENT` rather than assuming one, proven by
  `WritingPipelineTests.test_no_mode_resolved_refuses_mode_absent`. Left for
  a follow-up: accurate per-block mode transcription needs a close reading
  of each of the ten contracts' own prose that this batch's scope did not
  budget for.
- [x] 1.18 **Corrective (post-verify CRITICAL).** `mode` was transcribed into
  the seven declaring `sections/*.md` headers, but `_validate_mode_object`
  only ever checked shape, never that `source.quote` is real prose —
  `after` edges had this checked by `GraphTests._quote_in_body`
  (`tests/test_paper_contract.py`), `mode` had it checked nowhere. A
  corrective re-verify found this unenforced and measurably violated:
  `06-introduction.md`'s own quote failed the `after`-edge lock because the
  real prose wraps two of its words in `**bold**` mid-sentence. Fix: extend
  `_quote_in_body` with a closed, enumerated markdown-emphasis strip (the
  literal `*` character — the only emphasis markup this corpus uses),
  applied to both `after` and `mode` so the two disciplines stay one;
  added `ModeTranscriptionTests`, corpus-derived (never a hand-listed
  section-id set), covering all seven declared modes, a self-sourced
  fabrication proof (mirroring the existing `after`-edge one), and a
  paraphrase/unrelated-sentence proof that the normalization never becomes
  a fuzzy match. `06-introduction.md` needed no edit — its quote was
  already an honest transcription; only the markup decoration broke the
  naive substring check. Also fixed `SKILL.md`'s stale `write` example
  (`--section materials-and-methods` crashed uncleanly; the flag wants the
  filename stem, `01-materials-and-methods`) and recorded
  `paper_contract.install_header`'s pre-existing dead caller as an explicit
  follow-up owned by `the-contract-is-data-not-code`, not fixed here.

## Work Unit 2 — Style Channel + Leak Guard

- [x] 2.1 `paper_style.py`: equivalent-block resolution per `style-reference`
  guidance entry; whole-block passing (no excerpt/truncation); residency
  verification (span byte-present at its locator in the ingested `.md`); `R`
  recording; `noEquivalent` per missing reference, degrading to the empty
  style set (valid since Unit 1). RED→GREEN.
- [x] 2.2 **Ruling 2 — empty style set reports `unmeasured`.** RED: an
  all-`noEquivalent` reference set (empty `R`) must report `unmeasured` for
  the style channel, not a silent pass on register distance or overlap.
  GREEN: implemented as `paper_write.style_channel_report`, joining
  `unprovenanced`/`unclassified`/`ambiguous`.
- [x] 2.3 `paper_leak.py`: three-draft proof set (`A`/`B` empty style, `S`
  real style, identical contract/evidence/mode); register distance
  `d(S,{A,B}) > d(A,B)` with `d(A,B)` a required argument (mutation 6 fails
  to construct without it); overlap
  `overlap(S,R) ≤ max(overlap(A,R), overlap(B,R))`, all three reported.
  RED→GREEN.
- [x] 2.4 Eight-token tripwire `STYLE_OVERLAP` (names span + reference), math
  environments excluded; shared normalization (case-fold, collapse
  whitespace, strip LaTeX, exclude math) lives once in `paper_style.py`.
  RED→GREEN. Wired into `write_block` (a follow-up fix, same session) —
  the tripwire now runs against the styled draft before `substitute`
  whenever `--style` is given, not only reachable via import.
- [x] 2.5 `relative_overlap_holds(styled, unstyled_a, unstyled_b, samples)`
  signature test asserting **no threshold parameter**. Mutation 7: overlap
  reads `R` only, never the reference file directly.
- [x] 2.6 Imported `paper_style`/`paper_leak` at `paper_cli.py` module level;
  extended `REFUSAL_CLASSIFICATION`; re-ran task 1.12's completeness
  assertion with all five modules present (re-proven RED/GREEN by hand
  again in this same session); refusal count moved 78 → 79.
- [x] 2.7 `.claude/agents/style-sampler.md` landed with the same shared
  role-discipline shape as 1.17's two agents; `SKILL.md`'s style-channel
  and leak-detection sections finalized, including the `--style`/
  `--guidance` CLI wiring added in the follow-up fix.
