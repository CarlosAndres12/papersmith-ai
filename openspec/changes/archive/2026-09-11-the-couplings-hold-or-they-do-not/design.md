# Design: The Couplings Hold Or They Do Not

## Technical Approach

`verify` is a pure report over four evidence sources — `paper/main.tex` bytes, `paper/refs.bib`,
one read-only declaration record, and the section contract headers — assembled by exactly one
module and consumed by pure check functions. `skill-audit`'s shape throughout: derive both sides
where a side can be derived, publish the provenance of every side that cannot, report, never
repair. Exit `0` for any verdict; exit `2` only for inability to look.

## Architecture Decisions

### Decision: skill-local modules, an evidence seam, no `_core/`

| Option | Tradeoff | Decision |
|---|---|---|
| `.claude/skills/_core/` | `reachable_refusal_codes` (`tests/test_proposal_implementation.py`) takes every `*.py` under `_core/implementation/` **whole**; paper codes would land in another skill's roster. The same reason `the-contract-is-data-not-code` already rejected it | Rejected |
| One `paper_verify.py` (the proposal's shape) | The read-only proof has to cover check logic and disk access in one file, so the AST lock cannot distinguish "a check touched disk" from "the reader did" | Rejected |
| **`paper_evidence.py` (all I/O) + `paper_verify.py` (pure checks, roster, report)** | One module opens files, and it opens them read-only; every check is a pure function of an evidence object and is testable without a tree | **Chosen** |

`verify` never parses a marker: it calls `paper_block.parse` and slices bodies from the same
bytes, so one grammar exists in one place.

### Decision: every side carries its provenance, and a check with no derived side must say so

The report types each side `derived` (computed from bytes nobody declared) or `declared` (read
from the record). A check whose sides are all `declared` must carry the literal limit
`TWO_DECLARED_SIDES`; a test derives that condition from the report rather than a hand-list.

| Check | Side A | Side B | Derived |
|---|---|---|---|
| 1 `contribution-list` | record `facts.contributions`, ordered (declared) | per block requiring that fact: order of **first literal occurrence** of each name in that block's own bytes | B |
| 2 `chain` | record `chain` links (declared) | token identity per link, plus set closure against the same `facts.contributions` check 1 binds to the document | closure |
| 3 `gap` (assisted) | closing sentence of each gap block, sliced from its bytes | front lists and their counts, sliced from the same bytes | both |
| 4 `artefacts` | record `setup_cells`, `results_artefacts` (declared) | methods-diagram boxes **are** `facts.contributions` by contract 01 — the list check 1 already bound to the document, never declared twice | B |
| 5 `future-work` | record `directions` → limitation ids vs `facts.limitations` (declared, totality) | each direction's citation key must occur as a `\cite` key inside the future-work block's bytes and as an entry in `refs.bib` | key |
| A `citations` | `\cite`-family keys scanned from `main.tex` | `@type{key,` entries scanned from `refs.bib` | both (a dangling cite fails; an orphan entry is published in the payload and never fails the check) |
| B `contract-currency` | per-block hash read from the `provenance` region Phase 3 writes | `sha256` of that block's contract file on disk | both |

**Which blocks a check reads is derived, not hardcoded, and has exactly one source.** No block id
appears in this change's source. The set is every block whose `requires_facts` names the fact,
read from the section headers through `paper_contract.parse` — real code on disk, not a proposal.
A record-declared `block_requirements` fallback was considered and **rejected**: it would give the
check a second declared side and let a paper pass by declaring its own block set. When the corpus
is absent or headerless (it is headerless today; Phase 2 installs the headers), the dependent
checks are `unmeasured`, reason `SECTION_CONTRACTS_UNREADABLE`. An empty derived set is
`unmeasured`, reason `NO_BLOCK_REQUIRES_FACT` — never zero comparisons reported as agreement.

Fact keys in the record are validated with `paper_vocabulary.validate_fact`, so the ten-fact
vocabulary is imported, never restated here.

### Decision: one record, one grammar, and this change writes none of it

| Option | Tradeoff | Decision |
|---|---|---|
| Read Phase 3's `declarations` region | That region's fence grammar is fixed, its **resolution payload shape is not**. Verify would be defining another change's record from downstream | Rejected |
| A third `%% paper-writing` region | Widens a closed grammar Phase 3 owns | Rejected |
| **`paper/couplings.json`, read-only** | Invisible to Phase 1 by construction (not in `main.tex` at all); one grammar inside the line budget; when Phase 3's resolutions land, an adapter maps them into this same shape — the shape is verify's **input contract**, not a storage decision. Cost: untracked, like `main.tex` itself | **Chosen** |

The `provenance` region is different: Phase 3 fixes its fence grammar (`%% paper-writing
provenance begin sha256=<hex>` … `end`), so check B parses it today. The region prefix is
asserted disjoint from the imported `paper_block.MARKER_PREFIX` symbol, never a restated literal,
and `paper_block.status` over the fixture must report zero blocks.

### Decision: the report is a closed roster of objects, never a list of what happened to run

One object per check, always, whatever happened:

```json
{"check": "contribution-list", "classification": "mechanical",
 "verdict": "holds|fails|unmeasured",
 "sides": [{"name": "...", "source": "derived|declared", "origin": "..."}],
 "evidence": {...}, "limits": ["ORDER_FROM_FIRST_OCCURRENCE"],
 "unmeasured_reason": null}
```

`CHECKS` is one declaration; a test asserts the report carries exactly one object per member in
both directions, so an absent check is structurally impossible rather than silently missing.
`UNMEASURED_REASONS` is a second closed roster, derived from source like the refusal roster, with
every member proven reachable by a fixture. Three buckets must sum to `len(CHECKS)`; `clean` is
false whenever `fails + unmeasured > 0`. `unmeasured` is never added to `holds` anywhere — held by
the arithmetic, not by prose.

**Three tiers of inability, and they are architecturally different.**

| Situation | Behaviour | Proven by |
|---|---|---|
| The whole declaration record is absent or empty | **Refuse the run**: `DECLARATION_RECORD_ABSENT`, exit 2. Nothing is known about any coupling; per-check `unmeasured` across the board would bury the fact that nothing was checked at all | M6 |
| One block has no entry (hand-written, `--adopt`ed) | `unmeasured` with `BLOCK_NOT_DECLARED` for the couplings that depend on **that block only**; every other check still produces a real verdict and the run proceeds | fixture, one block stripped |
| The `provenance` region is absent | **Check B alone** is `unmeasured` with `CONTRACT_RECORD_ABSENT`, exit 0 | M7 |

The last row narrows the proposal's wording, which reads as a run-level refusal. Phase 3 writes
that region and has not landed, so a run-level refusal would make all seven checks unreportable
and contradict the proposal's own requirement that every check be reachable today. The observable
M7 demands — never "zero stale blocks", never clean — are unchanged.

### Decision: read-only is proven three ways, and the proof is itself mutated

1. **AST lock** over both new modules: no `open(...)` in a writing mode, no `write_bytes` /
   `write_text` / `mkdir` / `unlink` / `replace` / `rename`, no `shutil`, no `tempfile`, and no
   reference to `paper_block.substitute` / `open_block`.
2. **Executed content manifest**: path → `sha256` over the whole fixture tree before and after a
   real `verify` subprocess, asserted equal. Never `git status` — `paper/*` is gitignored, so a
   porcelain check over it is empty by construction (a trap this repository has already paid for).
3. **M8**: make `paper_verify.py` write one byte, observe the manifest test go red, restore by
   inverse patch and confirm by digest. A guard that has never fired is indistinguishable from one
   switched off.

### Decision: the assisted payload publishes evidence, and its only verdict is `unmeasured`

Coupling 3's return vocabulary is the single value `unmeasured`, reason
`ASSISTED_READING_REQUIRED` — `holds` is structurally absent from it, the same shape as
`skill-audit`'s constant `comparison: not-run`. Nobody closes it: `verify` does not guess, does
not ask, and stores no answer, so there is no resolution field for anyone to fill in and no way
for the output to read as a pass.

What it publishes, so the human reading is cheap: both closing sentences verbatim with their byte
offsets, adjacent; both front lists with counts; and the three mechanical sub-results (both
closings present, fronts equal, count equals the declared problem count) as named booleans with
their own evidence. Failure of any of those three is reported as a mechanical fact inside an
`unmeasured` check — evidence a reader can act on without making the reading. Byte-identity of the
two closings is reported and never changes the verdict: two identical sentences are suspicious,
not agreement.

## Data Flow

    couplings.json ─┐
    main.tex bytes ─┼→ paper_evidence.gather() → Evidence ─→ paper_verify.run() → report
    refs.bib       ─┤        (read-only)                        (pure, 7 checks)
    sections/ hdrs ─┘                                                  │
                                                            paper_cli.cmd_verify → JSON

## File Changes

| File | Action | Description |
|---|---|---|
| `.claude/skills/paper-writing/scripts/paper_evidence.py` | Create | Every disk read; the record grammar; the `provenance` region reader; the `requires_facts` derivation over `paper_contract.parse` |
| `.claude/skills/paper-writing/scripts/paper_verify.py` | Create | `CHECKS`, `UNMEASURED_REASONS`, seven pure checks, report assembly |
| `.claude/skills/paper-writing/scripts/paper_cli.py` | Modify | `verify` verb, `COMMANDS`, new `REFUSAL_CLASSIFICATION` entries |
| `.claude/skills/paper-writing/SKILL.md` | Modify | Fifth verb, the three-value verdict vocabulary, decision gates |
| `tests/test_paper_writing.py` | Modify | Widen the roster walk; new check, report, read-only and mutation classes |
| `tests/fixtures/paper-verify/` | Create | One fully-declared green tree; every red variant is a mutation of it in a temp dir |

## Testing Strategy

| Layer | What | How |
|---|---|---|
| Unit | each check over a hand-built `Evidence` | pure, no tree |
| Report | roster totality both ways; buckets sum; `unmeasured` never in `holds` | derived from `CHECKS` |
| Integration | the green tree: every check `holds` except 3, which is `unmeasured` by construction | subprocess, exit 0 |
| Read-only | AST lock + before/after manifest | subprocess |
| Mutation | M1–M9, executed | see below |

Mutations run in a subprocess with `PYTHONDONTWRITEBYTECODE=1` unconditionally; each asserts the
anchor matched an exact count **and** the file digest moved (a matched anchor is not a mutation
that ran), and restores by inverse patch confirmed by digest. The green tree is proven green
before the first byte is touched. M1–M7 are the proposal's. **M8** (read-only lock, above) and
**M9** — add a `Refused` to `paper_verify.py` and observe the roster test go red — are added here:
without M9, widening the roster walk is an untested claim.

## What Breaks — Producers and Products

| Class | Row |
|---|---|
| Producers | `unreadable_paper_refusal_sites` and `reachable_paper_refusal_codes` (`tests/test_paper_writing.py`) each hand-list this skill's script files, so a new script's refusals are invisible to both — the Move-12 defect this repository has measured four times. **Both walks become derived from `paper_cli.py`'s own module-level imports that resolve to a file under `SKILL_SCRIPTS`**, not a `glob("*.py")`: reachability is what the roster claims, and a module nothing imports is not reachable. Today that derivation returns exactly the current hand-list, so it lands green and only `verify`'s own modules widen it |
| Producers | **Reported, not repaired**: `paper_contract.py` and `paper_vocabulary.py` landed raising `Refused` codes that no roster classifies — neither walk reaches them and no `paper_cli` verb registers them yet. The import-derived walk admits them at the moment Phase 2 wires its verbs, which is when they become reachable. This change classifies none of another change's codes |
| Producers | `RefusalRosterTests.test_the_derivation_finds_the_measured_count` asserts `21`; the two docstrings there say "this skill's three files". Both must move with the walk |
| Producers | `paper_cli.REFUSAL_CLASSIFICATION`, `COMMANDS`, `_COMMANDS`; `SKILL.md`'s verb table and refusal-roster paragraph |
| Producers | The forge leak guard scans every new file under `.claude/skills/`; both new modules and the fixture tree must carry no target vocabulary |
| Products | `paper/` holds only `.gitkeep` — **no `main.tex`, no block, no declaration record and no provenance region exists anywhere on disk** (verified 2026-09-10). Zero written instances are invalidated by any shape named here |
| Products | No `verify` report has ever been produced, so no archived report falls out of domain. Stated, not left implicit |
| Products | `sections/*.md` are read for their contract bytes (check B) and never written |

## Threat Matrix

`N/A` for every row. No routing, no shell, no subprocess in shipped code (mutation subprocesses
are test-side), no VCS or PR automation, no executable-file classification, no process
integration. The one boundary — a caller-supplied `--paper` — is already answered by
`paper_scaffold.resolve_paper_dir` and its `PAPER_OUTSIDE_REPOSITORY` refusal, reused unchanged.

## Migration / Rollout

No migration; nothing on disk holds any shape this change reads. Delivery in three stacked slices
against the 1400-line budget: (a) evidence, record grammar, report shape, roster totality,
read-only lock; (b) checks 1, 2, A; (c) checks 3, 4, 5, B, the CLI verb and `SKILL.md`. Rollback
deletes two modules, one verb and its tests; `verify` writes nothing, so `paper/` is untouched.

## Open Questions

- [ ] The record's owner is still unbuilt. This change defines the read shape and refuses without
      it; Phase 3's adapter is named as follow-up work, not assumed.
- [ ] The section headers are not installed yet, so against the real tree today checks 1, 2, 4 and
      5 report `SECTION_CONTRACTS_UNREADABLE`. Reachable-green lives in the fixture corpus until
      Phase 2's header insertion runs. This is designed behaviour, stated as such.
- [ ] `ORDER_FROM_FIRST_OCCURRENCE` is a real limit: a name mentioned in a block's opening
      sentence orders before its own enumeration. It ships in the payload rather than being
      silently accepted.
- [ ] Artifact exceeds the 800-word design budget. The overage is the seven-check side table and
      the breakage rows; compressing either drops a requirement.

---

**Citations checked**: `paper_block.MARKER_PREFIX`, `paper_block.parse`, `paper_block.status`,
`paper_scaffold.resolve_paper_dir`, `paper_vocabulary.FACTS`, `paper_vocabulary.validate_fact`,
`paper_contract.parse`, `paper_contract.ContractHeader`, `paper_cli.REFUSAL_CLASSIFICATION`,
`paper_cli.COMMANDS`,
`reachable_paper_refusal_codes`, `unreadable_paper_refusal_sites` and
`RefusalRosterTests.test_the_derivation_finds_the_measured_count` were each located in source by
name before being repeated here.
