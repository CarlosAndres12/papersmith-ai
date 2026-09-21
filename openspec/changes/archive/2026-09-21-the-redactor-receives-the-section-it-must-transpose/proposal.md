# Proposal: The Redactor Receives The Section It Must Transpose

## Intent

`transposition-fidelity/spec.md:5-8` requires a `mode: transposition` block to
carry its bound source section into the paper's own style — never copy it. The
skill demands the restatement and ships no way to hand over the thing being
restated. That is this repository's first-named failure class, and its third
occurrence here.

Re-measured 2026-09-21 against disk, not inherited from exploration:

| where | what is there |
|---|---|
| `.claude/agents/redactor.md:15-24` | four inputs, then "You never open a file yourself to find a fifth input". No bound section anywhere. |
| `paper_cli.py:2052-2113` (`assemble_packet`) | returns `{block, section, contract, references}`; `references` are heading OUTLINES. No `paper_dir` parameter exists. |
| `paper_bindings.py:39-44` (`RedactorInput`) | `@dataclass(frozen=True)`, exactly four fields. The four-input rule is code, not only prose. |
| `paper_source_span.py:27-77` (`resolve_bound_sections`) | already resolves the section's `text`. Shipped, tested, called only by `write`. |

The machine opens that section exactly once — inside `write`, after the draft
exists, to distrust it. Never to supply it.

## Scope

### In Scope

- Widen `assemble_packet`: add `paper_dir`, assemble the corpus with the
  default `enforce_bindings=False`, call the shipped `resolve_bound_sections`,
  emit a fifth key `source_sections`.
- Widen `paper_bindings.RedactorInput` with a fifth `source_sections` field,
  mirroring `BlockContract.source_sections`' existing shape.
- Edit the two shipped requirements named below, by delta spec.
- Rewrite `.claude/agents/redactor.md`'s input paragraph so its count is true
  again **without** weakening its prohibition.
- **The demand must ship the way to answer it.** A `transposition` block whose
  packet is assembled without a paper root MUST NOT silently receive an empty
  `source_sections`. It refuses, or reports a named state, and either way NAMES
  the flag that answers it. `resolve_bound_sections`' own docstring already sets
  the precedent ("returned `()` … reported by the caller as `unmeasured`, never
  silently passed"); design rules which of the two, silence is ruled out here.
- A synthetic source document and `bind` round as fixture — invented names.
- Reachability of any new refusal proven by executed mutation
  (`tests/paper_mutation.py`), never asserted.

### Out of Scope

- **Whether the draft asserts only what its section carries.** Not closed by
  this change. It is the parallel sibling `the-block-asserts-only-what-its-
  section-carries`, and the prior change deferred it explicitly
  (`archive/2026-09-20-the-tripwire-reaches-the-section-that-feeds-it/design.md:316-319`).
  Nothing here may read as closing it.
- Widening `SOURCE_SECTION_VERBATIM` to `argument` mode.
- Making `SECTION_BINDING_ABSENT` reachable from `packet` — `enforce_bindings`
  stays `False`.
- Any forecast refusal-roster count. Last measured **153** on 2026-09-20 by that
  change's WU3; re-measured live at verify, never predicted here.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `redactor-packet`: `Requirement: The Packet Carries Contract Prose Plus
  Same-Section Style Extracts` (`spec.md:15-23`) becomes a three-part packet —
  contract prose, style extracts, and the block's own bound source sections —
  and gains the named answer for a transposition block assembled without a
  paper root. The zero-content-from-`guidance/` clause is untouched.
- `evidence-bound-drafting`: `Requirement: Redactor Input Contract`
  (`spec.md:19-25`), whose text is literally "MUST receive exactly four inputs",
  becomes **five**: the fifth is the block's bound source sections, empty being
  a valid value for a non-transposition block.

## Approach

Exploration's recommendation. `packet` already knows the block; it gains the
paper root and asks the shipped resolver. No new resolution path, no second
source of section bytes — the same function `write` uses to judge is the one
that supplies.

**Rejected.** A second verb (same machinery cost, worse process shape). Leaving
the redactor blind and hardening only the post-hoc check (addresses nothing).

### This does not reverse D5

D5's own text
(`archive/2026-09-18-the-phases-are-derived-not-remembered/design.md:65-69`):
"the packet is physically incapable of carrying reference prose, because it
carries offsets. Rejected alternative — the packet inlines each extracted
section's text — puts an unaudited copy of reference prose in a file the
redactor can read without ever passing residency verification or the
eight-token tripwire."

Every clause of D5 names **reference** material: someone else's paper, ingested
under `guidance/` for register, whose content must never leak into a claim.
That is why it may only ever arrive as offsets the `style-sampler` resolves and
`paper_style.resolve_style_set` residency-verifies into `R`.

A bound source section is not that. It is the paper's **own** upstream managed
document, named by the block's own `source_bindings`, which the block is under
explicit contractual obligation to restate. D5 never mentions `source_bindings`
and its rationale does not reach one: there is no third party to leak from, and
the guard against copying it is not absence but `SOURCE_SECTION_VERBATIM`,
shipped 2026-09-20 for exactly this prose.

Stated for the reader six months out who sees only "the packet now carries
prose": D5's boundary is intact. `references` still carry offsets and nothing
else. A separate key carries our own document, under its own guard.

### The redactor's prohibition survives

"You never open a file yourself to find a fifth input" is today a true sentence
guarding a real back door. It must not become false, and it must not be deleted.

It becomes: the redactor is handed **five** declared inputs, and still never
opens a file to find a sixth. The change adds a door, it does not remove the
prohibition on the back door. The redactor still reads nothing it was not
given; what it was given simply now includes the section it was already ordered
to restate.

### The accepted tradeoff, named

`packet` assembling a corpus makes **16** further refusal codes reachable from a
read-only verb (`ID_COLLISION`, `SOURCE_BINDING_CONFLICT`,
`INPUT_PARTITION_ABSENT`, `SPAN_NOT_IN_SOURCE`, `FACT_ROUTE_AMBIGUOUS`,
`FACT_PRODUCER_DUPLICATE`, `FACT_SELF_REQUIRED`, `FACT_PRODUCER_ABSENT`,
`PRODUCER_CHAIN_ABSENT`, `CHAIN_ROW_UNRESOLVED`, `CHAIN_ROW_UNBACKED`,
`BLOCK_SUBUNIT_UNDECLARED`, `UNIT_HEADING_AMBIGUOUS`,
`SOURCE_REVISIONS_UNDECLARED`, `SECTION_NOT_IN_SOURCE`,
`SECTION_TITLE_AMBIGUOUS`). An unrelated section's defect can therefore block
one block's packet.

**This cost is accepted, explicitly, not silently.** `compute_phases`
(`paper_cli.py:1884`, assembling at `:1923`) is a read-only verb already paying
exactly it. The alternative — a narrower corpus entry point — does not exist
(`assemble_corpus` globs the whole `sections_dir`, `paper_graph.py:291`) and
inventing one would create a second assembly path that can drift from the one
`write` enforces. A packet that refuses because the paper is inconsistent is
correct: that paper cannot be drafted from either.

### Worked example (invented names — not this paper)

Source `widget-study-r4.md`, section `2. Widget Calibration`, bound to
`analysis.an-core` (`mode: transposition`). `packet --paper <dir> --section
analysis --block an-core` returns `contract`, `references` (outlines), and
`source_sections: [{fact, lineage, title, path, byte_start, byte_end, text}]`.
Without `--paper`, the same transposition block does not get `[]` — it gets the
flag's name.

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `.claude/skills/paper-writing/scripts/paper_cli.py` | Modified | `assemble_packet` gains `paper_dir`, corpus, fifth key; `cmd_packet` gains the flag |
| `.claude/skills/paper-writing/scripts/paper_bindings.py` | Modified | `RedactorInput` fifth field |
| `.claude/agents/redactor.md` | Modified | Four→five declared inputs; prohibition re-anchored |
| `.claude/skills/paper-writing/SKILL.md` | Modified | Refusal roster + `packet` surface |
| `openspec/specs/redactor-packet`, `openspec/specs/evidence-bound-drafting` | Modified | Delta specs |
| `tests/` | Modified | Synthetic binding fixture; mutation proof; both suites |
| `paper_source_span.py` | Read-only | Called, never edited |

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Corpus-wide refusal contamination on `packet` | High | Accepted above by name, with the `compute_phases` precedent; recorded in the delta spec, not only here |
| Widening a frozen dataclass breaks positional callers | Med | Append after defaulted fields; sweep every construction site; shape test asserts the field count |
| `SOURCE_SECTION_VERBATIM` becomes the primary safeguard, not a backstop | High | Was near-structurally unreachable while the redactor never saw the bytes; design re-reads its threshold under the new load |
| No real binding on disk; every path synthetic | High | `bind`-recorded fixture; the synthetic boundary is stated in verify, not hidden |
| A paper name leaks into `.claude/skills/` | Med | Invented fixture names; pre-apply neutrality audit is a gate |
| Reader concludes D5 was overturned | Med | The distinction is argued in this proposal and must survive into the delta spec |

## Rollback Plan

Revert the branch. No on-disk format, digest, or marker grammar changes;
`packet` is read-only and writes nothing on any path, including refusals. An
existing `paper/main.tex` and every recorded binding stay readable by the prior
revision. Nothing is deleted.

## Dependencies

- Archived `2026-09-20-the-tripwire-reaches-the-section-that-feeds-it`
  (`resolve_bound_sections`, `SOURCE_SECTION_VERBATIM`).
- Parallel sibling `the-block-asserts-only-what-its-section-carries` — disjoint
  scope, no ordering requirement, but both touch the transposition story.

## Review Workload Forecast

Owner accepted `size:exception` up front; engine-line ceiling **1600** under
`.claude/skills/`. Five independently deliverable slices: (1) `assemble_packet`
widening + fifth key ~250; (2) `RedactorInput` fifth field + shape test ~120;
(3) the named answer for a missing paper root + mutation proof ~250; (4)
`redactor.md`, SKILL roster, delta specs ~150; (5) synthetic fixture + both
suites ~300. Estimated ~1070.

```
Decision needed before apply: No
Chained PRs recommended: Yes
400-line budget risk: High
```

## Success Criteria

- [ ] `packet` for a `transposition` block returns its bound section's text,
      resolved through `resolve_bound_sections` and no second path.
- [ ] The same block without a paper root gets a named answer — refusal or
      reported state — that NAMES the flag. Proven by executed mutation in
      `tests/paper_mutation.py`, never asserted.
- [ ] `RedactorInput` carries five fields; a shape test asserts the count, which
      no test does today.
- [ ] `redactor.md` says five inputs and still forbids opening a file to find a
      sixth.
- [ ] Both shipped requirements carry delta specs; neither still reads "exactly
      four inputs".
- [ ] The delta spec records the accepted corpus-contamination tradeoff by name.
- [ ] No paper id, block id, section title, document filename, method or lineage
      name appears anywhere under `.claude/skills/` or its suite.
- [ ] Roster re-measured live after the code lands; no forecast count shipped.
- [ ] Both suites green: `npm test` and
      `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`.
