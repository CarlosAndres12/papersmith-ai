# Design: The Redactor Receives The Section It Must Transpose

> **Paths.** Every `paper_*.py` is under `.claude/skills/paper-writing/scripts/`;
> `tests/` and `openspec/` are repository-root relative.
>
> **Re-measured on disk 2026-09-21.** Nothing below is inherited from the
> proposal or the exploration without re-running its measurement. Two claims
> changed under re-measurement and are marked **[corrected]**.

## Technical Approach

`assemble_packet` gains an optional corpus and an optional paper root, resolves
the block's own bound sections through the already-shipped
`paper_source_span.resolve_bound_sections`, and emits them as a flat fifth key
beside a sibling **state** key. `RedactorInput` gains a fifth field carrying the
same tuple. No new resolver, no new refusal code, no second source of section
bytes.

The change is gated on one fact measured at `paper_write.py:236`:
`check_source_section_verbatim` runs only when
`contract.mode == MODE_TRANSPOSITION`. Section bytes handed to any other mode
would sit in front of a drafter under no verbatim guard at all. Every decision
below follows from that.

---

## Architecture Decisions

### D1 — A missing or unreadable paper root reports a NAMED STATE; it never refuses

**Choice.** `packet` reports `source_sections_state.state = "unmeasured"` with a
`reason` that names the way to answer it (`--paper <dir>`, `paper/main.tex`, or
the unmeasured source root). It never raises `PAPER_ABSENT` and adds no code.

**Rejected.** Refusing. **Rationale, from this repository's own precedent, not
taste:**

| evidence | what it rules |
|---|---|
| `paper_declarations.read_bindings:691-696` | returns `{}` for an absent `paper_dir` and says so literally: "this is not `PAPER_ABSENT`'s concern, which is reserved for a verb that actually needs to WRITE `paper/`" |
| `paper_declarations.source_root_status:1726-1730` | an absent root and an empty root both report `unmeasured` — "the SAME report, never a refusal" |
| `paper_write.source_fidelity_report:277-278` | `write` itself, the strictest verb, reports `unmeasured` rather than refusing when no section resolved |
| `compute_plan` (`paper_cli.py:1752-1767`) | reports per-root state on a read-only verb |

`packet` is read-only and writes nothing on any path. A paper that has not
reached `bind` yet is not in error.

**The distinction the caller must be able to draw** — "this block has no bound
section" versus "I could not look" — is carried by a closed four-value
vocabulary, not by an empty list:

| `state` | meaning | `sections` |
|---|---|---|
| `resolved` | every declared/recorded triple produced bytes | non-empty |
| `unbound` | the block names no `(fact, lineage, title)` triple at all — **nothing to look for** | `[]` |
| `unmeasured` | a triple exists and did not resolve — **could not look**; `reason` names the flag/root/verb, `unresolved` names each triple | possibly partial |
| `not-applicable` | mode is not `transposition` (D5) | `[]` |

`unbound` and `unmeasured` are derived by set difference between
`corpus.blocks[qualified_id].source_bindings` (the input) and
`resolve_bound_sections`' return (the output). `resolve_bound_sections` is not
edited: it still skips silently, and `assemble_packet` does the arithmetic its
docstring at `paper_source_span.py:33-35` already demands of a caller
("reported by the caller as `unmeasured`, never silently passed").

**One refusal does become reachable, and it is an invocation defect, not a state
of the world:** `--paper` resolving outside the repository raises the shipped
`PAPER_OUTSIDE_REPOSITORY` (`paper_scaffold.py:42-55`). That boundary is the
same one `write` and `place` already enforce.

### D2 — The corpus is assembled only for a `transposition` block; `ORDER_CYCLE` is not inherited

**Choice.** Inherit the corpus codes **as-is, unnarrowed by classification**,
but assemble the corpus **only when the block's resolved mode is
`transposition`**. An `argument`-mode or mode-less block's `packet` performs
byte-identical work to today and inherits nothing.

**Rejected.** (a) Always assembling — pays the full blast radius for every block
that could never use the result. (b) Catching the 17 codes and converting them
to a reported state — would create a second classification of corpus integrity
that can drift from `write`'s, would hide a real defect behind a read-only
verb, and would license a packet for a draft `write` can never accept, since
`write` refuses on the same corpus anyway.

**Rationale.** The narrowing boundary is *need*, not taste, so it needs no
classification logic and cannot drift. Mode is resolved from the header
`assemble_packet` has already parsed (`paper_contract.resolve_mode`) — no extra
disk read. `compute_phases` (`paper_cli.py:1923`) is the precedent for paying
the cost at all; unlike it, `packet` never calls `collect_edges` or
`derive_waves`, so `ORDER_CYCLE` and `PHASE_NOT_READY` stay unreachable here.

**The corpus is never assembled twice.** `cmd_write` already holds one
(`paper_cli.py:2218`, `enforce_bindings=True`) and passes it in. This is not
merely a cost argument: `cmd_write` resolves `paper_dir` from `args.paper`,
while `assemble_corpus`'s own default derives `sections_dir.parent / "paper"`
(`paper_graph.py:299`). A `packet` call that re-derived its own root would
resolve `write --paper <other>`'s bindings against the wrong paper directory.
The rule is one line: **`assemble_packet` never assembles a corpus it was
handed, and never derives a paper root it was not given.**

### D3 — `RedactorInput.source_sections` is APPENDED fifth, defaulted — measured, not assumed

**Sweep result (`rg 'RedactorInput' --type py`, whole repository).** Exactly
**one** construction site: `tests/test_paper_writing.py:4616`. It is **fully
keyword** (`contract_prose=`, `evidence_set=`, `mode=`, `style_set=`).
**Zero positional calls. Zero production construction sites.**

**[corrected]** `RedactorInput` has no production constructor at all today — it
is a shape contract nothing in `paper_cli.py` builds. The proposal treats it as
"code backing the four-input requirement"; it backs it only through that single
test. That is why the field-count assertion the proposal asks for is not a
nicety: it is the *only* enforcement the shape has.

**Choice.** `source_sections: tuple = ()` appended after `style_set`, exact
`BlockContract.source_sections` precedent (`paper_write.py:51-59`). Safe by
measurement: no positional caller exists to break.

### D4 — The fifth input mirrors `BlockContract.source_sections` EXACTLY

**Choice.** One shape in all three places — packet JSON `source_sections`,
`BlockContract.source_sections`, `RedactorInput.source_sections` — the verbatim
`resolve_bound_sections` entry:
`{"fact", "lineage", "title", "path", "byte_start", "byte_end", "text"}`.

**Rejected.** A narrower projection (`title`/`text` only). Its only argument is
aesthetic, and it would put a second shape between the resolver and the
verbatim check, which reads `fact`, `lineage`, `title` and `text` off that exact
dict (`paper_leak.py:248,261-263`). This repository has paid for twin shapes
twice this week.

**This is why the state lives in a SIBLING key, not an envelope around the
list.** Wrapping `source_sections` in `{"state", "sections"}` inside the packet
would make the packet's shape differ from both dataclasses. `compute_plan`
already ships the pattern: `sourceRoots` sits beside `provenance` as a sibling
status key (`paper_cli.py:1763-1768`). Key names are `source_sections` and
`source_sections_state` in snake_case — the packet's existing keys (`block`,
`section`, `contract`, `references`) and the proposal's worked example are the
tiebreak. `plan`'s camelCase is a pre-existing split in this CLI, noted here so
a later reader does not file it as a defect of this change.

### D5 — Only a `transposition` block's sections are resolved

**Choice.** `mode == "transposition"` resolves. `argument` gets
`not-applicable`. `mode is None` gets `unmeasured` naming the absent `mode`
declaration — `packet` never raises `MODE_ABSENT`; that stays `write`'s
(`paper_write.py:106-111`).

**Rationale, measured.** `paper_write.py:236` gates
`check_source_section_verbatim` on `MODE_TRANSPOSITION`. Widening that check to
`argument` is explicitly out of this change's scope. Therefore handing an
`argument` block its source bytes would put prose in front of the drafter with
**no verbatim guard whatsoever** — the exact hazard this change is otherwise
careful to keep guarded. It would also license an `argument` block, which
`check_mode_admissibility` permits to reach `discovery`-class evidence
(`paper_bindings.py:230-233`), to lift from a document it is under no
obligation to restate.

### D6 — `SOURCE_RUN_BACKSTOP = 16` HOLDS unchanged, and this change makes its falsifier runnable for the first time

**Re-read `paper_leak.py:185-199` and `202-212`.** `threshold =
max(source_section_floor(contract_prose, section_text), 16)`. Both terms read
`contract_prose` and `section_text` only. **Neither reads the drafter's access
to either.** The arithmetic is therefore untouched by this change.

What does change is the asymmetry the constant's own comment rests on: "a false
refusal here blocks `write`, while a false pass still faces contract-audit and a
human." The false-pass branch now has a real population behind it.

**Choice: do not move the number.** The comment names exactly two observations
that may move it, and "the redactor can now see the section" is neither.
Changing 16 on an unmeasured intuition would be this repository's own recorded
failure — a number altered without the measurement it declares it needs.

**Falsifiable sentence for a later reader.** *16 holds because
`check_source_section_verbatim`'s threshold is a function of contract prose and
section text alone; the way to falsify that is to paste the fixture's own bound
section verbatim into the fixture's draft and observe whether
`SOURCE_SECTION_VERBATIM` refuses — if it does not, 16 is too high and D6 is
wrong.*

**That is not an opinion; it is a required test.** Apply MUST ship
`test_a_verbatim_paste_of_the_fixture_bound_section_refuses`, driving the new
packet → draft path end to end. A green suite without it leaves D6 asserted
rather than measured. The complementary falsifier ("a genuinely transposed
draft whose longest shared run reaches 16") still needs a real binding and
stays an obligation, not a hope.

---

## Refusal Codes — THE COMPLETE SET THE SPEC IS WRITTEN AGAINST

> This is the authoritative enumeration. Every code this change adds or makes
> newly reachable appears here and nowhere else.

### A. New refusal codes introduced by this change

**Zero.** No `raise Refused(...)` site is added by this change. Every named
answer it introduces is a reported state (D1), not a refusal.

### B. Shipped codes newly reachable from `packet`, for a `transposition` block only

Via `paper_graph.assemble_corpus(..., enforce_bindings=False)` (D2). Seventeen:

| # | code | raise site |
|---|---|---|
| 1 | `ID_COLLISION` | `paper_graph.py:311` |
| 2 | `SOURCE_BINDING_CONFLICT` | `paper_graph.py:221` |
| 3 | `SOURCE_REVISIONS_UNDECLARED` | `paper_graph.py:430` |
| 4 | `SECTION_NOT_IN_SOURCE` | `paper_graph.py:518` |
| 5 | `SECTION_TITLE_AMBIGUOUS` | `paper_graph.py:524` |
| 6 | `INPUT_PARTITION_ABSENT` | `paper_graph.py:550` |
| 7 | `SPAN_NOT_IN_SOURCE` | `paper_graph.py:585,625,638` |
| 8 | `FACT_ROUTE_AMBIGUOUS` | `paper_graph.py:681` |
| 9 | `FACT_PRODUCER_DUPLICATE` | `paper_graph.py:703` |
| 10 | `FACT_SELF_REQUIRED` | `paper_graph.py:718` |
| 11 | `FACT_PRODUCER_ABSENT` | `paper_graph.py:778` |
| 12 | `PRODUCER_CHAIN_ABSENT` | `paper_graph.py:812,888` |
| 13 | `CHAIN_ROW_UNRESOLVED` | `paper_graph.py:961,966` |
| 14 | `CHAIN_ROW_UNBACKED` | `paper_graph.py:971` |
| 15 | `BLOCK_SUBUNIT_UNDECLARED` | `paper_graph.py:1035,1058` |
| 16 | `UNIT_HEADING_AMBIGUOUS` | `paper_graph.py:1042` |
| 17 | **`DECLARATIONS_HAND_EDITED`** | `paper_declarations.py:186` |

**[corrected] — #17 is new to this enumeration.** The exploration and the
proposal both name **16**. `assemble_corpus` calls
`paper_declarations.read_bindings(resolved_paper_dir)` (`paper_graph.py:300`),
which calls `_verify_not_hand_edited` (`paper_declarations.py:707`), which
raises `DECLARATIONS_HAND_EDITED`. A tampered `declarations` region in
`paper/main.tex` therefore blocks a transposition block's packet. The correct
count is **17**, and the delta spec must record 17, not 16.

### C. Shipped codes newly reachable from `packet` on EVERY invocation

| code | raise site | cause |
|---|---|---|
| `PAPER_OUTSIDE_REPOSITORY` | `paper_scaffold.py:52` | `cmd_packet` now resolves `--paper` through `resolve_paper_dir` |

### D. Same codes, widened blast radius (NOT new reachability)

`assemble_corpus` parses every `sections/*.md`, not only the named one. For a
`transposition` block, `MALFORMED_HEADER` and `MALFORMED_FIGURE_OBLIGATION`
(`paper_contract.py`, many sites) can now be raised by an **unrelated** section
file. The spec needs a scenario for this; the code set does not grow.

### E. Codes explicitly NOT inherited — each for a stated reason

| code | why not |
|---|---|
| `SECTION_BINDING_ABSENT` | `enforce_bindings` stays `False`; only `_resolve_write_gate` passes `True` |
| `ORDER_CYCLE` | `packet` calls neither `collect_edges` nor `derive_waves` |
| `PHASE_NOT_READY` | same |
| `MODE_ABSENT` | a mode-less block reports `unmeasured` (D5); refusing stays `write`'s |
| `PAPER_ABSENT` | D1 — reserved for verbs that write `paper/` |
| `SOURCE_SECTION_VERBATIM` | stays a `write`-only check; `packet` compares nothing |

### F. Named states this change introduces (not refusals — the spec must cover these too)

`source_sections_state.state` ∈ `{resolved, unbound, unmeasured, not-applicable}`,
closed vocabulary, `reason` non-null for every value except `resolved`.

---

## Data Flow

```
cmd_packet ──┬─ resolve_sections_dir ──┐
             ├─ resolve_guidance_dir ──┤
             └─ resolve_paper_dir ─────┤   (PAPER_OUTSIDE_REPOSITORY)
                                       v
                             assemble_packet(..., corpus=None, paper_dir=...)
                                       │
                          parse header ──> resolve_mode
                                       │
                  mode != transposition ──> state=not-applicable, sections=[]
                                       │
                  mode == transposition
                                       v
                          assemble_corpus(sections_dir, paper_dir=...)   [B, D]
                                       v
                          resolve_bound_sections(corpus, "sec.block")
                                       v
              set-difference(record.source_bindings, resolved)
                                       v
        {block, section, contract, references, source_sections,
                                   source_sections_state}

cmd_write ── _resolve_write_gate ──> corpus ──┐
                                              └──> assemble_packet(..., corpus=corpus)
                                                     (never re-assembles, never re-derives the root)
```

## File Changes

| File | Action | Description |
|------|--------|-------------|
| `paper_cli.py` | Modify | `assemble_packet` keyword params `corpus`/`paper_dir`, mode gate, resolver call, two new keys; `cmd_packet` resolves `--paper`; `cmd_write` passes its corpus; `--paper` added to `p_packet` (`:3096`) |
| `paper_bindings.py` | Modify | `RedactorInput.source_sections: tuple = ()` appended fifth; module docstring `:14` "four-input" → five |
| `.claude/agents/redactor.md` | Modify | `:15-24` four → five declared inputs; prohibition re-anchored to a sixth |
| `.claude/skills/paper-writing/SKILL.md` | Modify | `packet` surface + refusal roster |
| `openspec/specs/redactor-packet`, `.../evidence-bound-drafting` | Modify | Delta specs, written against section **Refusal Codes** above |
| `tests/test_paper_writing.py` | Modify | Fixture, shape test, state tests, D6 paste test |
| `tests/paper_mutation.py` | Read-only | Called with `source_path=SKILL_SCRIPTS / "paper_cli.py"`; **not edited** |
| `paper_source_span.py`, `paper_leak.py`, `paper_graph.py` | Read-only | Called, never edited |

## Interfaces / Contracts

```python
def assemble_packet(
    sections_dir: Path, guidance_dir: Path, section: str, block_id: str,
    *, corpus=None, paper_dir: Path | None = None,
) -> dict:
    """... returns, additionally:
        "source_sections": [ {fact, lineage, title, path,
                              byte_start, byte_end, text}, ... ]
        "source_sections_state": {
            "state": "resolved" | "unbound" | "unmeasured" | "not-applicable",
            "reason": str | None,
            "unresolved": [ {fact, lineage, title}, ... ],
        }
    Never assembles a corpus it was handed; never derives a paper root it
    was not given.
    """

@dataclass(frozen=True)
class RedactorInput:
    contract_prose: str
    evidence_set: tuple = ()
    mode: str = ""
    style_set: tuple = ()
    source_sections: tuple = ()   # exact BlockContract.source_sections shape
```

The four existing packet keys and their values are unchanged. `references`
still carries offsets only — **D5 of `the-phases-are-derived-not-remembered` is
intact**; `source_sections` carries the paper's own upstream document under
`SOURCE_SECTION_VERBATIM`, not third-party reference prose.

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | `RedactorInput` field count is exactly 5 | `dataclasses.fields()` length assertion — the shape's only enforcement (D3) |
| Unit | state vocabulary is closed and `reason` non-null except `resolved` | assert over all four values |
| Integration | `resolved` / `unbound` / `unmeasured` / `not-applicable` | synthetic `widget-study-r4.md` + `bind` round; invented names only |
| Integration | `cmd_write` assembles the corpus once, and `assemble_packet` uses the one it was handed | assert with a paper root differing from `sections_dir.parent / "paper"` |
| Integration | an unrelated section's `MALFORMED_HEADER` blocks a transposition packet, and does **not** block an `argument` packet | two fixtures, one corrupted sibling file (category D + D2) |
| Integration | **D6** — verbatim paste of the fixture's own bound section refuses `SOURCE_SECTION_VERBATIM` | end to end through the new path; failing means D6 is wrong |
| Mutation | the `unmeasured` state is reachable, not decorative | `_run_against_mutant(anchor, replacement, dotted_test, source_path=SKILL_SCRIPTS / "paper_cli.py")`; break the line that sets `state`/`reason` and assert the pinning test FAILS |
| Roster | measured live after the code lands | never forecast |

**Stale bytecode, measured — the harness already purges it.** `_run_against_mutant`
creates a fresh `tempfile.mkdtemp` tree per call (`tests/paper_mutation.py:74`,
so no `__pycache__` can survive across mutations) **and** sets
`PYTHONDONTWRITEBYTECODE=1` in the child environment (`:139`). It also asserts
the anchor matched exactly once and that the bytes changed (`:64-71`), which is
what catches a same-size no-op substitution. No harness edit is required by this
change; the only obligation on apply is to pass `source_path` explicitly,
because the default is still `paper_block.py` (`:34`).

## Threat Matrix

`N/A — no routing, shell, subprocess, VCS/PR automation, executable-file
classification, or process-integration boundary is introduced.` No script under
`.claude/skills/` imports `subprocess` and this change adds none. The one
subprocess in scope is `tests/paper_mutation.py:143`, pre-existing test
infrastructure this change calls and does not modify.

## Migration / Rollout

No migration. No on-disk format, digest, or marker grammar changes; `packet`
writes nothing on any path including refusals. Rollback is a branch revert; an
existing `paper/main.tex` and every recorded binding stay readable by the prior
revision. Additive keys: an existing consumer reading the four shipped packet
keys is unaffected.

## The seam with the sibling change

`the-block-asserts-only-what-its-section-carries` meets this change at exactly
one place: **`BlockContract.source_sections` / `RedactorInput.source_sections`,
the same tuple, the same shape, produced by the same resolver.** This change
fills that tuple and hands it forward. Whether the draft asserts only what the
tuple carries is read off it by the sibling, and is not designed, implied, or
closed here.

## Open Questions

- [ ] None blocking. Two obligations recorded rather than deferred: the D6
      paste test is required at apply, and the "16 is too low" falsifier still
      needs a real `document` binding that does not exist on disk.
