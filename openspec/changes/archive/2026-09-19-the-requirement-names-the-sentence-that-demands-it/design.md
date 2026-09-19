# Design: The Requirement Names the Sentence That Demands It

## Technical Approach

One storage shape, one derivation point, one verifier. A `requires_facts` /
`requires_declarations` entry becomes `{value, source:{file,quote}}` — `after`'s
list-of-objects precedent. `paper_contract._parse_block` normalizes every entry
through a single function and keeps the objects under the **existing key**; the
plain id list is never stored, only derived at read time through one accessor.
The quote check lives in `paper_graph` alone, mirroring
`_verify_after_transcription`, and reuses `paper_contract.quote_in_body`.

## Architecture Decisions

### D1 — Two representations, or one plus an accessor (question A)

| Option | Drift | Call sites | Verdict |
|---|---|---|---|
| Plain list + sibling rich key in the parsed dict | two lists at rest; re-serialization derives the sibling from the plain list and silently loses provenance | 0 | **Rejected** — this is the defect class the change exists to close |
| Rich list under `requires_facts` + `paper_contract.requirement_values()` accessor | impossible: nothing plain is stored | 2 | **Chosen** |

The single point is `_normalize_requirement_entry` inside `_parse_block`. The
plain tuple exists only as a transient at two construction sites:
`paper_graph.py:162-163` (`BlockRecord`) and `paper_cli.py:1455`
(`BlockContract`). Both route through `requirement_values`. A second path is
made unreachable by an AST test over `scripts/*.py`: no module outside
`paper_contract` may subscript `["requires_facts"]` / `["requires_declarations"]`
on a parsed block dict except through that accessor. The seven value-consumers
downstream of `BlockRecord` are untouched, as the proposal requires.

**Consequence to record:** `paper_cli.py:432` (`contract --file`) emits
`header.blocks` verbatim, so that command's `requires_facts` becomes a list of
objects. That is an observable output change and needs a spec scenario.

### D2 — Which validator runs where (question B)

The launch brief proposed a self-file check inside `paper_contract.parse` and a
cross-file check in `paper_graph`. **Measured evidence contradicts the split:**
`parse(data: bytes)` receives no path and never learns its own filename;
`_verify_mode_transcription` only works because every `mode` is self-sourced by
convention. A requirement quote may legitimately live elsewhere
(`abstract.slot-2`'s quote is in `sections/06-introduction.md`), so a
`parse`-level check would refuse a correct corpus.

**Chosen:** one verifier, `paper_graph._verify_requirement_transcription`,
called from `assemble_corpus` beside its three siblings. It reads the same
`bodies` dict (keyed `<sections_dir.name>/<file>`, matching the shipped
`source.file` values), so the self-file case is simply the case where
`source.file` names the declaring contract — not a second discipline.
`paper_contract` validates **shape only**.

Write is covered: `paper_cli._resolve_write_gate` calls `assemble_corpus`
(line 1105) before `cmd_write`'s single-file parse (line 1421). `contract --file`
stays a single-file diagnostic, exactly as it already is for `after` edges.

### D3 — What "inert" means, and what U3 flips (question C)

A flag or env var is `--force` in disguise and fails open; a gate that skips
`source: null` makes the half-migrated state permanent. Both rejected.

| Unit | Shape layer accepts | Gate |
|---|---|---|
| U1–U2 | bare string → `{value, source: None}`; object → validated `source` | absent — the function and its call do not exist |
| **U3** | object with **required** `source` only | `_verify_requirement_transcription` unconditional |

Inert therefore means *the gate does not exist yet*. U3 flips two things in one
commit: bare-string acceptance is removed, and the verifier is wired. After U3
the half-migrated state is unrepresentable — a bare entry refuses
`MALFORMED_HEADER` at parse, an unbacked quote refuses `SPAN_NOT_IN_SOURCE` at
assembly. **No new refusal code.** `UNKNOWN_FACT` / `UNKNOWN_DECLARATION` keep
firing, now on `entry["value"]`; a non-string `value` refuses
`MALFORMED_HEADER`, mirroring `_validate_mode_object`'s own `mode.value` check.

Round-trip holds throughout: U1's normalizer accepts `source: null` under the
same `raw.get(...) is not None` convention `mode` and `figure` already use, and
U3's parser output always carries a dict, so re-parsing its own output is a
fixed point.

### D4 — The DP report (question D)

Not a CLI verb. `install_header` was deleted as a zero-production-caller
one-shot; a permanent surface for a one-time ruling repeats that mistake. The
report is a change-folder artifact,
`openspec/changes/<change>/unanchored-requirements.md`, one entry per
requirement, all fields derived from the corpus:

| Field | What it lets the operator decide |
|---|---|
| block, field, value, contract file | identity |
| the block's own `### External inputs` rows, verbatim | what the contract *did* write down |
| does the value appear anywhere in that file's body | "never mentioned" vs "mentioned, not for this block" |
| which other blocks anchor the same value, and where | the value is real elsewhere |
| is the dependency already an `### Internal chain` row | the `es-assessment`/`dataset` reading |
| block `optional`; blocks whose readiness changes if deleted | the cost of deleting |

The last two rows are exactly what separates *spurious requirement* from
*contract never wrote it down* without reading the corpus.

### D5 — Fixtures (question E)

Once U3 removes bare-string acceptance, a fixture **cannot** build an unanchored
non-empty header: `parse` refuses it. That is structural, not detected. The
rejected alternative — a static scan asserting every bare fixture entry sits in
a function that also asserts `SPAN_NOT_IN_SOURCE` — is function-scoped, fragile
across shared helpers, and only detects.

Blast radius is narrower than it looks: fixtures declaring **empty** lists (the
large majority) are unaffected, since an empty list anchors nothing. Measured:
**26** non-empty raw-header occurrences across `test_paper_writing.py`,
`test_paper_decisions.py`, `test_paper_contract.py`, `test_paper_figure.py`.
Fixtures constructing `BlockRecord` directly (e.g. `test_paper_decisions.py:773`)
are unaffected either way.

## Data Flow

    sections/*.md ──parse──→ header.blocks[i]["requires_facts"]
                             = [{value, source:{file,quote}}, …]   ← only storage
                                      │
              requirement_values() ───┼─── BlockRecord.requires_facts (tuple)
                                      │         └→ 6 consumers, unchanged
                                      └─── BlockContract.requires_facts (tuple)
    bodies{sections/NN-x.md: bytes} ──→ _verify_requirement_transcription
                                            └→ quote_in_body() → SPAN_NOT_IN_SOURCE

## File Changes

| File | Action | Description |
|---|---|---|
| `.claude/skills/paper-writing/scripts/paper_contract.py` | Modify | `_normalize_requirement_entry`, `requirement_values`, `_parse_block` rewiring; U3 narrows the shape |
| `.claude/skills/paper-writing/scripts/paper_graph.py` | Modify | `_verify_requirement_transcription` + `assemble_corpus` wiring; `BlockRecord` built via the accessor |
| `.claude/skills/paper-writing/scripts/paper_cli.py` | Modify | line 1455 through the accessor; `contract --file` output shape |
| `sections/*.md` (10, repo root) | Modify | headers gain transcribed entries; prose bytes identical |
| `tests/*.py` (repo root, 4 files) | Modify | 26 non-empty raw-header occurrences; new tests |
| `.claude/skills/paper-writing/SKILL.md` | Modify | documents the transcription obligation |

## Interfaces / Contracts

```python
# paper_contract.py — the one normalization point
_REQUIREMENT_REQUIRED = ("value", "source")

def _normalize_requirement_entry(raw, validate, owner: str) -> dict:
    """U1: a bare string normalizes to {"value": raw, "source": None}.
    U3: bare strings are gone; 'source' is required and goes through
    _validate_source, exactly as an `after` entry's does."""

def requirement_values(entries) -> tuple:
    """The ONLY way a caller turns entries into plain ids. Nothing stores
    the result; every caller derives it at the point of use."""
```

## Testing Strategy

This repo proves guards by mutation, and test work is expected to exceed the
code. Mutations run on tmp copies of the corpus, never the shipped files; a
source mutation asserts its own anchor replacement count (a matched anchor is
not a mutation that ran), and `git diff --stat` is not accepted as proof.

| Layer | What to test | Approach |
|---|---|---|
| Unit — shape | bare string (U3), missing `source`, unknown entry key, non-string `value` | `MALFORMED_HEADER` naming the key |
| Unit — vocabulary | `value` outside the closed sets | `UNKNOWN_FACT` / `UNKNOWN_DECLARATION` still fire after the shape change |
| Unit — round-trip | `parse_header(json round-trip of parsed blocks)` is a fixed point | guards the null convention |
| Integration — gate | unbacked quote added to a tmp corpus copy | `SPAN_NOT_IN_SOURCE` |
| Integration — cross-file | quote living in another contract passes; typo'd fails | mirrors `_verify_after_transcription`'s own tests |
| Mutation — unconditional | the `assemble_corpus` call line removed | the unbacked test goes green → red; AST test asserts the call is a direct statement of `assemble_corpus`, not inside `if`/`try` |
| Static — one derivation | no module subscripts the two keys outside the accessor | AST scan over `scripts/*.py` |
| Static — one comparison | the new verifier calls `paper_contract.quote_in_body` and defines no local comparison | AST scan |
| Corpus — equality | `{qid: record.requires_facts}` over the shipped corpus vs a frozen snapshot | U3's rulings appear as an explicit golden diff |
| Roster | `reachable_paper_refusal_codes()` bidirectional | **measured after the code lands; never forecast a number** |
| Leak | no id of this paper under `scripts/` | existing forge-vocabulary guard |

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file
classification, or process-integration boundary. Stdlib-only and
`subprocess`-free is preserved: the static guards use `ast`.

## Migration / Rollout

U1 → U2 → **DP (operator ruling)** → U3. No persisted state, no data migration.

**U2 and U3 MUST NOT share a PR.** Not only arithmetic (combined they sit at the
1200-line ceiling): DP falls between them, and a PR opened before the ruling
exists cannot honour it. Separating them also keeps 47 prose judgements
reviewable on their own and preserves the rollback plan — `git revert` of U3
alone restores the pre-gate corpus and fixtures together and leaves a green
suite. U1 and U2 may share a PR if the operator prefers two PRs total; U1 alone
is the smaller, more reviewable mechanism diff.

## Open Questions

- [ ] DP: the 2 confirmed (`es-assessment` → `experimental-design`, `gap`) and 2
      borderline (`es-assessment` → `dataset`; `keywords` → `contributions`)
      requirements. Operator-only; U3 may not start before the ruling returns.
- [ ] `contract --file`'s changed output shape — confirm no consumer outside the
      test suite reads it (nothing in `scripts/` does).
