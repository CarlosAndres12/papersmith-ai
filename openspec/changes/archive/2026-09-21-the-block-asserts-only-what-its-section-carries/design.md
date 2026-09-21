# Design: The Block Asserts Only What Its Section Carries

Change: `the-block-asserts-only-what-its-section-carries` · Store: hybrid ·
Ceiling: **1600** engine lines under `.claude/skills/`. Every `file:line`
below was re-opened on disk **2026-09-21**, not inherited from the proposal or
the exploration. Three inherited claims were corrected by that re-reading and
are marked **[re-measured]**.

## Technical Approach

A fourth sibling in `write_block`'s judge chain: an agent proposes a per-
sentence support account, `paper_grounding.py` re-derives both sides from
bytes and reconciles, and only a byte-grounded `supported` survives. Shaped on
`paper_audit.py`'s shipped reconciliation (`:56-101`), never extending it.

---

## §1 THE REFUSAL SET — FINAL (read this straight off, spec author)

Four codes. This set is closed; a later phase that wants a fifth reopens
design, it does not amend here. All four are `WORK_STATE`: clearing each
requires acting on the repository (editing the draft, or producing the
account), never re-typing the invocation alone — the definition this file
carries at `paper_cli.py:158-161`. The shape precedent is
`EVIDENCE_SET_REQUIRED`/`VERDICT_MISSING`/`VERDICT_BULLET_UNKNOWN`, all
`WORK_STATE` (`paper_cli.py:393-398`).

| Code | Raised when | Names (the way to answer it) | Class |
|---|---|---|---|
| `GROUNDING_ACCOUNT_ABSENT` | subjects exist and no account was supplied | the block, the subject count, and the exact `write --grounding <path>` operand plus the agent that produces it | `WORK_STATE` |
| `GROUNDING_SENTENCE_UNKNOWN` | an account entry's `sentence` is absent from `write`'s own segmentation | the offending account sentence verbatim | `WORK_STATE` |
| `GROUNDING_VERDICT_MISSING` | a subject sentence has no account entry | the block and the unjudged sentence verbatim | `WORK_STATE` |
| `SECTION_UNSUPPORTED_CLAIM` | a surviving verdict is `unsupported` | block, fact, lineage, section title, resolved `path`, and the sentence | `WORK_STATE` |

Each needs one row in `paper_cli.py`'s module-level import registry
(`:75-107`) — one row for the module, not one per code:

```python
import paper_grounding  # noqa: E402 -- the-block-asserts-only-what-its-section-carries: per-sentence support reconciliation against the bound section's own bytes; for the roster derivation
```

and one `REFUSAL_CLASSIFICATION` entry each (`paper_cli.py:182-554`).

**Every `Refused(...)` first argument is a string literal.**
`_refusal_code_argument` (`tests/test_paper_writing.py:7400-7403`) reads only
`ast.Constant`; a non-literal makes the site `code is None`, which both trips
`test_the_derivation_has_no_unreadable_sites` (`:7564-7569`) and silently
widens the module's whole constant set into the roster
(`_codes_from_sites`, `:7436-7440`). No caller may `raise Refused(exc.code,
...)`.

The pinned roster count (**161** today, `tests/test_paper_writing.py:7942`) is
**re-measured live** against `reachable_paper_refusal_codes()` after the code
lands. Never forecast here.

---

## Architecture Decisions

### D1 — The permissive verdict carries the burden of proof (the inversion)

**Choice.** `supported` MUST cite a span byte-present in that fact's own
`section["text"]`; an empty span, an absent span, or a span found only in a
*different* fact's section downgrades to `undecidable` with the span cleared.
`unsupported` needs no span and refuses.

**Alternative rejected.** Copy `contract-audit`'s asymmetry literally —
`contract-audit/spec.md:30-32` ("A `fires` verdict MUST quote the offending
span"), `contract-auditor.md:32-34`, `paper_audit.py:88-91` — where the
*blocking* verdict is the grounded one.

**Rationale.** The unifying rule under both is: *the verdict that moves the
outcome away from the safe default must be grounded in bytes the code can
re-read.* In `contract-audit` that verdict is `fires`. Here it is
`supported`, because `supported` is what lets a sentence reach `substitute`.
Copied naively, an ungrounded `supported` waves everything past and the guard
becomes ceremonial, green and worthless — "a guard that cannot fire".
`unsupported` needs no span because *absence cannot be quoted*: demanding a
span for a claim the section never makes is demanding proof of a negative. It
is also fail-closed and loud — it names the fact, lineage, title and resolved
`path`, so the operator opens the exact bytes and checks.

### D2 — `undecidable`: no ratio threshold. A ruling, with its falsifier.

**Choice.** `undecidable` never blocks, alone or in bulk. No ratio, no
constant. Instead the report carries `subjects`, `decided`, `undecidable` and
`downgraded` per block, and `status` is `"measured"` only when `decided > 0`.

**This is a judgement call, not a measurement, and is labelled as one.** A
number cannot be measured today: no real `document`-rooted binding exists on
disk (`transposition-fidelity/spec.md:28-34`), so any ratio would be a picked
constant presented as a calibration — the failure this repository names.
Beyond that, `contract-audit`'s shipped `Requirement: Undecidable Is
Reported, Not Blocking On Its Own` (`spec.md:47`, `paper_audit.py:95-101`)
exists precisely because blocking on the mechanism's own uncertainty trains
the agent to guess, and a guess is what this change refuses.

**What closes the silent half of R1 without a number:** `downgraded` is
counted and reported *separately* from the `undecidable` the agent itself
returned. An agent that honestly abstained and one that minted fake spans are
then distinguishable from the envelope alone, which is what a reviewer needs
and what no ratio would have given.

**Falsifier, written so it can be checked:** over ten or more recorded real
`write` runs against genuine `document`-rooted bindings, if any block reaches
`written` with `downgraded > 0`, or with `subjects > 0` and `decided == 0`,
this ruling is wrong and a blocking rule over `undecidable` must be reopened.
Both conditions are read straight off `sourceGrounding`. This sentence ships
in `SKILL.md` and in the capability spec, so the ruling stays arguable rather
than becoming folklore.

### D3 — The subject set is an intersection, derived twice from bytes

**Choice.**

```python
bound_facts = {section["fact"] for section in contract.source_sections}
subjects = [b for b in bindings if b.kind == "fact" and b.ref in bound_facts]
```

**Confirmed on disk today.** `resolve_bound_sections` emits `"fact": fact_id`
per entry (`paper_source_span.py:68-76`); `Binding.ref` is `fact:<id>`'s own
`ref` group (`paper_bindings.py:75-78`, constructed `:121-124`). Same id
space — `record.source_bindings`' fact ids are keys of
`paper_declarations.FACT_SOURCE_ROOT` (`paper_source_span.py:52`) and the same
ids are licensed through `requires_facts` (`paper_bindings.py:136`).

**Alternatives rejected.** A `block_id → section` map, a hand-kept fact list,
or a section-title match. Each is a literal belonging to a real paper inside a
general forge, and each goes stale silently.

**Consequence, stated:** a licensed `fact:` binding whose fact carries no
bound section is simply not a subject. That is the `document`-half scope
boundary (§Scope), expressed as a set operation rather than a second gate.

### D4 — Thread the bindings; nothing segments the draft twice **[re-measured]**

`_stage_evidence_audit` **already returns `list`** (`paper_write.py:121`,
`return bindings` at `:129`) and has **exactly one caller**
(`paper_write.py:159`), where the value is dropped. The proposal and the
phase brief both call for a "signature change"; there is none. The whole edit
is one call site:

```python
bindings = _stage_evidence_audit(contract, draft)   # was: bare statement
```

Nothing else in the repository calls it (grep, whole tree, today). Re-
segmenting inside `paper_grounding` is rejected: two derivations of the same
thing drift, and this repository has paid for that twice.

### D5 — A third sibling, never a branch in either neighbour

**Choice.** A new module `paper_grounding.py`, lazily imported inside
`write_block` exactly as `paper_leak` is at `paper_write.py:203` and `:237`,
and module-level in `paper_cli.py` for the roster walk — the shipped double
pattern (`paper_cli.py:97`).

**Why not `check_tripwire`.** `paper_leak.py:218-225` records it verbatim:
`style-leak-detection`'s `Requirement: Overlap Reads Only The Recorded Sample
Set` forbids `STYLE_OVERLAP` comparing against a directly-read reference file,
so folding a bound section's bytes in "would break a shipped requirement
rather than merely overload a function."

**Why not `check_source_section_verbatim`.** Different reason, equally hard:
that function computes its answer from three strings alone and returns a
floor/threshold report (`paper_leak.py:246-273`). Grounding takes an *agent
account* as input and refuses on semantics. Merging them would put a
verdict-bearing input inside a function whose entire contract is that it has
none, and would make one code stand for two unrelated failures — which the
roster reads statically and cannot separate. `paper_leak.py` is touched by
this change **not at all**.

### D6 — Where it fires

Inside `write_block`, **after** `check_source_section_verbatim` and **before**
`paper_block.substitute`. Copying is decided before meaning, so a draft
failing both names `SOURCE_SECTION_VERBATIM` deterministically — the same
ordering rule that already puts `STYLE_OVERLAP` first (`SKILL.md:1156-1158`).
Never on a read-only verb.

### D7 — An absent account is a refusal, not an `unmeasured` pass

**Choice.** `--grounding` is `default=None` in argparse (requiring it would
break every `argument`-mode and non-transposition invocation and every shipped
fixture). But when subjects exist and the account is `None`,
`paper_grounding` raises `GROUNDING_ACCOUNT_ABSENT` — derived from the same
intersection, never from a flag check in the CLI.

**Alternative rejected.** Let the absent account fall through to
`GROUNDING_VERDICT_MISSING` on the first subject. It fires correctly but its
message points at one sentence when the real fault is "you never ran the
auditor", and it makes one code stand for two failures — the thing D5 refuses.

**Alternative rejected.** Report `unmeasured` and pass. Then the operator
turns the guard off by omitting a flag.

The `--grounding` operand goes through `_resolve_repo_path`
(`paper_cli.py:2007-2021`), reusing `PAPER_OUTSIDE_REPOSITORY` — never a
second code for the same condition.

### D8 — Report shape mirrors the two shipped reports

`source_grounding_report` mirrors `source_fidelity_report`
(`paper_write.py:262-279`) and `style_channel_report` (`:282-292`): the
absence of a refusal never means a pass.

| Condition | `status` |
|---|---|
| no subjects (empty `source_sections`, or no `fact:` binding joins one) | `"unmeasured"`, `subjects: 0` |
| subjects exist, `decided == 0` | `"unmeasured"`, `subjects: N` |
| `decided > 0` | `"measured"` |

Counts disambiguate the two `unmeasured` cases; no new status vocabulary.

### D9 — The agent file's shipped obligations **[re-measured]**

`tests/test_agents.py` is a live gate, not a style note. The new
`.claude/agents/section-grounding-auditor.md` must carry, in its own bytes:
`name: section-grounding-auditor` matching its stem (`:316`); a non-empty
`tools:` (`:376`); `You begin` / `you end` (`:382-391`); a `## What you
return` section naming `` `did` ``, `` `stoppedAt` ``, `` `state` ``,
`` `owed` `` (`:398-403`); the literals `never conclusions` and `measured
again` (`:410-413`); a `## Measure before you assert` heading and the sentence
`Not every agent's description carries its bound skill's arrival` (`:512-522`)
— the role discipline is **copied, never referenced** (`:496-501`).
`stretch: write` (a real stage, the same one `contract-auditor.md:5` uses).

And `SKILL.md` must contain the literal phrase **``delegates to the
`section-grounding-auditor` agent``** (`:345-351`, `:360-370`) or the agent is
an orphan and the suite goes red; the existing `Measure this before
delegating` line (`SKILL.md:1046`) already satisfies `:415-432`.

---

## Data Flow

```
sections/*.md ─┐
               ├→ _resolve_write_gate → Corpus ─→ resolve_bound_sections ─┐
paper/         ┘                                  (bytes off disk)        │
                                                                          ▼
 draft.json ──→ _stage_evidence_audit ──→ bindings ──────────→  ∩  → subjects
 (redactor)     (segments LaTeX itself)   [D4: now kept]        (D3)    │
                                                                        ▼
 grounding.json ─────────────────────────────────────→ paper_grounding.reconcile
 (agent account: proposes, decides nothing)                             │
                                                    ┌───────────────────┤
                                            refuse (§1)        sourceGrounding
                                                                        │
                                                                paper_block.substitute
```

## Interfaces / Contracts

```python
# paper_write.py — keyword-only, defaulted: every construction site that
# predates this field stays green, the `source_sections: tuple = ()` precedent.
def write_block(paper_dir, contract, draft, audit_account,
                *, grounding_account: dict | None = None) -> dict: ...

# paper_grounding.py
def subjects_for(bindings: list, source_sections: tuple) -> list: ...
def reconcile_support(subjects, account, source_sections, *, block_id) -> list[dict]
    # raises GROUNDING_ACCOUNT_ABSENT, GROUNDING_SENTENCE_UNKNOWN,
    #        GROUNDING_VERDICT_MISSING, SECTION_UNSUPPORTED_CLAIM
def source_grounding_report(subjects, reconciled) -> dict
```

Account envelope (agent → file → `--grounding`):

```json
{"support": [{"sentence": "...", "fact": "...",
              "verdict": "supported|unsupported|undecidable", "span": "..."}]}
```

Reconciled entry: `{"sentence", "fact", "lineage", "title", "verdict",
"span", "downgraded": bool}`. `write` envelope gains `"sourceGrounding"`
beside `"sourceFidelity"` (`paper_write.py:252-259`).

## File Changes

| File | Action | Description |
|---|---|---|
| `.claude/skills/paper-writing/scripts/paper_grounding.py` | Create | Subject derivation, both-direction reconciliation, the four refusals, the report |
| `.claude/agents/section-grounding-auditor.md` | Create | `tools: Read, Glob, Grep`; `stretch: write`; never invoked by code (D9) |
| `openspec/specs/transposition-grounding/spec.md` | Create | The capability, written against §1 |
| `scripts/paper_write.py` | Modify | `:159` keeps the bindings (D4); new stage (D6); `sourceGrounding`; `source_grounding_report` delegated to the new module |
| `scripts/paper_cli.py` | Modify | Import row, `--grounding`, `_resolve_repo_path`, four `REFUSAL_CLASSIFICATION` entries, `write` help row |
| `.claude/skills/paper-writing/SKILL.md` + `references/` | Modify | Roster rows, the delegation phrase (D9), D2's falsifier |
| `scripts/paper_leak.py` | **Untouched** | D5, stated as a boundary |
| `tests/test_paper_writing.py` | Modify | Red-first locks; count re-measured live |
| `tests/paper_mutation.py` | **Untouched** | See below **[re-measured]** |

## Testing Strategy

| Layer | What | How |
|---|---|---|
| Unit | Subject intersection; an `evidence:` binding and a `structural` binding are never subjects; a licensed `fact:` with no bound section is never a subject | direct calls, invented fixture names |
| Unit | Downgrade: `supported` + absent span → `undecidable`, span cleared; `supported` + span from *another* fact's section → `undecidable` | plant the absent span **red-first** |
| Unit | `unmeasured` on `subjects == 0` and on `decided == 0`, counts distinguishing them | report shape |
| Integration | Full `write_block`: refuse, pass-with-span, downgrade; `_stage_evidence_audit` called exactly once | spy/count on the one call site |
| Integration | `argument`-mode block and a block with no `source_sections` reach `substitute` untouched | shipped fixtures unchanged |
| Roster | classification both directions; no unreadable site; count re-measured | shipped `RefusalRosterTests` |
| **Mutation** | one per code, four total | `paper_mutation._run_against_mutant(..., source_path=SKILL_SCRIPTS / "paper_grounding.py")` |

**Mutation anchors.** Each of the four refusals needs a source anchor
occurring **exactly once** in `paper_grounding.py` — `_run_against_mutant`
raises if the count is not 1 (`tests/paper_mutation.py:64-68`). Write the four
guard conditions so no two share a line; that is a design constraint on the
module, not an apply-time accident.

**Stale bytecode is already handled — the harness needs no change
[re-measured].** `_run_against_mutant` creates a fresh `tempfile.mkdtemp` per
call (`:74`), names the mutant module uniquely with a `uuid4` (`:75`), and
sets `PYTHONDONTWRITEBYTECODE=1` (`:139`), with the reason recorded in-line at
`:98-100`. R6's mitigation is shipped, not owed. Apply must not "fix" it.

**Synthetic boundary.** No real `document`-rooted binding exists on disk
(`transposition-fidelity/spec.md:28-34`), so every scenario is a `bind`-
recorded fixture with **invented** names. Verify states that boundary; it is
never implied away.

## Scope — what this change does NOT check

Stated so nobody reads it as closing more than it does:

- **`evidence:`-bound sentences.** Held by `citation-validation`/
  `evidence-set`, shipped apart. Never a subject; asserted by a lock.
- **`structural` sentences.** `paper_bindings.type_structural` already refuses
  `STRUCTURAL_CARRIES_CLAIM`; a survivor asserts nothing to ground.
- **Any `argument`-mode block.** Out exactly as it is out of
  `SOURCE_SECTION_VERBATIM`, by the same `contract.mode` derivation
  (`paper_write.py:236`) — no block id, no list.
- **A `fact:` sentence whose fact has no `document` half.** No bytes to
  compare against; `resolve_bound_sections` already skips it
  (`paper_source_span.py:52-57`). Inventing a stricter gate here is "fixed the
  instance, never swept the class".
- **Whether the section itself is true.** This checks *containment*, not
  correctness.
- **Copying.** Still `SOURCE_SECTION_VERBATIM`'s, untouched.

## The seam with its sibling

`the-redactor-receives-the-section-it-must-transpose` applies **FIRST**. It
widens `assemble_packet`/`RedactorInput` so the redactor is handed the bound
section it must transpose. The seam is `contract.source_sections` — the same
tuple, from the same `resolve_bound_sections` call
(`paper_cli.py:2260`): the sibling routes it *into* the drafter, this change
holds the draft *to* it.

**Hard ordering dependency.** Without the sibling, this guard demands fidelity
to bytes the drafter was never shown, which converts a fidelity guard into a
guessing game and makes `SECTION_UNSUPPORTED_CLAIM` fire on competent drafts.
The sibling's own exploration already scopes this change out by name
(`.../exploration.md:107-112`). Apply blocks on the sibling being landed; it
does not race it.

## Threat Matrix

`N/A` — no routing, shell, subprocess, VCS/PR automation, executable-file
classification, or process-integration boundary. The one new operand
(`--grounding <path>`) is a path-containment boundary already owned by
`_resolve_repo_path` and `PAPER_OUTSIDE_REPOSITORY` (`paper_cli.py:2007-2021`,
whose own docstring cites the shipped threat-matrix row); it introduces no new
code and no new seam. No irrelevant task is manufactured from this.

## Migration / Rollout

Purely additive; four chained slices as the proposal forecasts. No on-disk
state format, digest, marker grammar or envelope key a prior revision reads is
changed — `sourceGrounding` is a **new** key. Slice 1 alone turns a discarded
return value into a used one with no behaviour change. Revert in reverse
order; slice 3 removes the import row, the classification entries and the
roster rows in one commit, so the count locks stay consistent.

## Open Questions

- [ ] None blocking. D2's ruling is deliberately falsifiable rather than
      open: the falsifier ships in `SKILL.md` and in the spec.
