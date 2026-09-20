# Proposal: The Tripwire Reaches The Section That Feeds It

## Intent

A block whose contract declares `mode: transposition` must carry its source
section into the paper's own style — not copy it. Nothing enforces that.

Measured 2026-09-20: `paper_leak.check_tripwire` has exactly ONE call site
(`paper_write.write_block`, line 195), gated on `contract.style_set`, which is
populated only from `guidance/` folders classed `style-reference`. It never
reaches a source-section binding. A redactor can paste a bound section verbatim
and `write` writes it.

What makes this newly possible: `source-section-binding` shipped, so the skill
now knows which section of which document feeds each block. There is finally a
concrete thing to compare a draft against.

## Scope

### In Scope
- Close the wiring gap: `paper_cli._resolve_write_gate` already assembles the
  corpus with `enforce_bindings=True` and returns `None`; `cmd_write`'s
  `BlockContract` never receives the resolved bindings. Its own slice, first.
- A sibling check in `paper_leak.py` (never an extension of `check_tripwire`),
  refusing `SOURCE_SECTION_VERBATIM` inside `write_block`.
- Fix `paper_style.strip_math` for `$$...$$` display fences, with its blast
  radius on the SHIPPED style tripwire measured before the fix lands.
- Settle the threshold for a same-author source, rather than inherit eight.
- A pre-apply neutrality audit gate (Invariant 1).

### Out of Scope
- **Verifying that a transposition block asserts only what its bound section
  carries.** Content verification against a located span exists today only for
  citations. A separate, real gap — named here, not folded in.
- Editing `paper_graph.py` (concurrent change lands first).
- Any post-change refusal-roster count. Measured live today: **144**.

## Capabilities

### New Capabilities
- `transposition-fidelity`: a transposition draft must not reproduce its bound
  source section's prose verbatim; the check derives its subjects from the
  contract on disk and refuses inside `write`.

### Modified Capabilities
- `style-leak-detection`: normalization must exclude `$$...$$` display fences.
  This corrects a live guard, not only the new one.
- `evidence-bound-drafting`: `Requirement: Structural Sentences Are Typed` —
  its normalization carries the identical `$$` defect through
  `paper_bindings._strip_math`, which feeds the shipped
  `STRUCTURAL_CARRIES_CLAIM` guard.

**Corrected after design (2026-09-20).** An earlier draft of this proposal said
the `Redactor Input Contract`'s "exactly four inputs" would gain the resolved
bound source sections. The design never routes them there and was right not to:
`write_block` is a pure judge over an already-drafted envelope, and this skill
hands the redactor nothing — the orchestrating agent assembles its inputs and
delegates. The guard does not depend on how the redactor obtained its text;
copying is copying whatever its provenance.

**Open question, recorded rather than silently dropped.** Where a transposition
block's redactor obtains the prose it must transpose is unresolved. Today it
arrives by hand, which means the skill cannot know what the redactor was shown
— it can only judge what came back. That is a real gap in the shuttle, not in
this guard, and it belongs to whoever widens `packet`. Note that `packet`'s
shipped boundary — heading outlines, never reference prose — is about a STYLE
reference whose content must not leak in, and does not transfer to a source
document the block is contracted to carry.

## Approach

Exploration's Approach 2. A sibling function reusing the span machinery, under
its own refusal code, so the two domains' thresholds stay tunable apart and the
shipped check is untouched. Lazily imported exactly as `check_tripwire` is, so
`paper_write.py` stays importable without it.

**How a transposition block is identified.** From `paper_contract.resolve_mode`
against `paper_vocabulary`'s own mode value — the same derivation `write`
already performs for `MODE_ABSENT`. No block id, no section title, no list.

**Where the bytes come from.** `BlockRecord.source_bindings` →
`FACT_SOURCE_ROOT` → resolved revision → `paper_guidance.segment_markdown`
byte offsets → slice. Every hop is shipped and tested. The concurrent change
to `paper_graph.py` lands first; design reconciles with its result rather than
duplicating resolution, and the slicing helper lives outside that file.

**Where it fires.** In `write_block`, after contract-audit clears and before
`substitute`, beside the style tripwire. A guard wired only to a read-only verb
is wired to nothing — nine measured instances here.

### The three items, by name

**1. `strip_math` and its blast radius.** `_MATH_INLINE_RE` matches the first
two adjacent `$` as an empty span, the fences vanish, and the whole equation
body survives as prose. Verified by executing it. The one real
document-sourced file here uses `$$` 136 times and the delimiters `strip_math`
handles once. Because the shipped tripwire normalizes the same way, a quoted
equation already counts toward its eight-token overlap **today**. The fix is a
prerequisite AND a correction. Its effect on the shipped guard MUST be measured
and recorded before the fix lands, never after.

**2. The threshold is not inherited.** Eight was calibrated against an
INDEPENDENT published paper's prose. A source document is the same author's
earlier text about the same work, where reusing terms, quantities and formal
statements is legitimate at a far higher baseline. The three-draft register
proof does not port: a same-author document has no natural unstyled control.
Proposed replacement — self-calibrate against the block's OWN contract prose,
which is same-author, quote-anchored to that source, and not the draft: refuse
only when the draft's longest shared run with the bound section exceeds the run
that contract prose already legitimately shares with it, with a fixed
back-stop. `sdd-design` owns the back-stop and the floor/literal arbitration;
it does not own the right to inherit eight silently.

**3. The wiring gap is its own reviewable slice, first.** It is a discarded
return value, not new machinery.

### Worked example (invented names — not this paper)

Source `widget-study-r4.md`, section `2. Widget Calibration`, bound to block
`analysis.an-core` (`mode: transposition`).

- **Refused.** The draft's opening pastes the section's own sentence: "the
  calibration constant is fixed at the midpoint of the admissible interval and
  held across every trial." Shared run exceeds the contract-prose floor →
  `SOURCE_SECTION_VERBATIM`, naming the block, the fact, the lineage, the
  section title, and the span.
- **Passes.** "Calibration fixes that constant at the interval's midpoint,
  unchanged across trials." Same claim, the paper's register, shared run below
  the floor.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `scripts/paper_cli.py` | Modified | `_resolve_write_gate` returns the corpus; `cmd_write` fills the new field |
| `scripts/paper_write.py` | Modified | `BlockContract` gains bound sections; new stage in `write_block` |
| `scripts/paper_leak.py` | Modified | Sibling measurement + refusing wrapper |
| `scripts/paper_style.py` | Modified | `$$` display fences excluded |
| `SKILL.md` | Modified | Refusal-roster entry for the new code |
| `tests/` | Modified | Red-first mutation proofs; the before/after math measurement |
| `scripts/paper_graph.py` | Read-only | Concurrent change owns it |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Math fix moves the shipped tripwire's behaviour | High | Measure and record before/after; it is a gate, not a note |
| No real bindings on disk; every path synthetic | High | `bind`-recorded fixtures; state the synthetic boundary in verify |
| Threshold has no obviously right answer | Med | Self-calibrating floor + back-stop; design rules explicitly |
| `paper_graph.py` merge collision | Med | Concurrent change lands first; reconcile, never duplicate |
| Product names leak into the forge | Med | Pre-apply neutrality audit is a gate (Invariant 1) |

## Rollback Plan

Revert the branch. No on-disk state format, digest, or marker grammar changes,
so an existing `paper/main.tex` and every recorded binding stay readable by the
prior revision. The `strip_math` correction reverts with it, restoring the
shipped tripwire's measured prior behaviour. Nothing is deleted.

## Dependencies

- Archived `2026-09-20-the-requirement-names-the-section-that-feeds-it`.
- Concurrent `the-whole-cut-is-argued-before-any-section-is-claimed` applies
  first (`paper_graph.py`).

## Review Workload Forecast

Owner raised the delivery budget to **1200 changed lines** for this change.
Four slices, each independently deliverable: (1) wiring gap ~150; (2)
`strip_math` + blast-radius measurement ~200; (3) sibling check, refusal code,
wiring into `write_block` ~450; (4) neutrality audit, roster re-measure, suites
~200. Estimated total ~1000.

```
Decision needed before apply: No
Chained PRs recommended: Yes
400-line budget risk: High
```

Against the owner-raised 1200-line budget the risk is Medium; against the
default 400 it is High, so the four slices ship chained.

## Success Criteria

- [ ] A draft pasting its bound section verbatim refuses `SOURCE_SECTION_VERBATIM`
      at `write` — proven by an executed mutation, not a read-only verb.
- [ ] A transposed draft of the same section passes.
- [ ] Transposition is derived from the contract on disk; no block id, section
      title, document filename or paper id appears in `.claude/skills/` or its suite.
- [ ] `strip_math` excludes `$$...$$`, and the shipped tripwire's before/after
      behaviour is recorded from a measurement, not forecast.
- [ ] The threshold for a same-author source is justified by a recorded
      measurement, not inherited from eight.
- [ ] `_resolve_write_gate`'s resolved bindings reach `BlockContract`.
- [ ] Roster re-measured live after the code lands; no `subprocess`; no file deleted.
- [ ] Both suites green: `npm test` and `.venv/bin/python -m unittest`.
