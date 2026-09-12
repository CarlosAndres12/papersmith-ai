# Design: The second document, verified on its own terms — Slice C

> **Budget note.** Over the 800-word default, on the precedent Cut 3's
> amendment set and this change's own proposal repeats: *mechanics concrete
> enough that apply invents nothing*. A scope derivation, an overlay tier with
> an all-or-nothing rule, a fold whose red must be structural, and a lock that
> counts one English word in engine prose do not compress without becoming a
> design apply has to re-derive.

## Technical Approach

The claim vocabulary stops being **one value per profile** and becomes **one
value per document**, and `cmd_verify`'s fidelity fold stops passing four shared
lists to every index and starts deriving them **inside each document's own claim
scope**.

Three properties hold the bar structurally rather than by assertion:

1. **Overlay, never replace.** A `documents[N]` entry declaring none of the five
   leaves inherits all five from `provenance.*`/`findings.*`. Every profile on
   disk today declares none, so every one resolves to the identical values.
2. **Every new fold branch is gated on `len(DOCUMENTS) > 1`.** The sibling's
   profile declares one document, so the new arithmetic is *structurally
   unreachable* for the 28 sealed digests — the same protection Cut 3's amendment
   used for `DOCUMENT_REVISION_UNREADABLE`, not a re-measurement.
3. **The declaration is the last act.** `documents[1]` lands only after the fold
   that reads it is green against a fixture the shipped fold cannot pass.

## Measurements from this phase — every symbol grepped by name, none inherited

### M1 — the proposal's 26/32 reproduce exactly, and decompose further

At HEAD, word-boundary over `implementation_engine.py`:

| Symbol | Definition line | Reader lines | Total |
|---|---:|---:|---:|
| `CLAIM_KEY` | 1 | 4 | **5** |
| `LOCUS_KEY` | 1 | 4 | **5** |
| `REMEDY_LOCUS_KEY` | 1 | 10 | **11** |
| `NOTATION_KEYS` | 1 | 8 | **9** |
| `CITATION_RE` | 1 | 1 | **2** |
| | **5** | **27** | **32 symbol-line hits** |

**26 distinct lines**, exactly as the proposal reported — confirmed, not
inherited. The decomposition it did not carry: **5 of those 26 are the module-
level definitions; only 21 are reader lines.** `CITATION_PATTERN`'s own
definition is a 27th line, excluded because `CITATION_PATTERN` is not one of the
five symbols. Apply threads **21** lines, not 26, and must re-derive both numbers
before quoting either.

### M2 — Q1 confirmed against disk, not against a record

`.claude/skills/experimental-implementation/impl_profile.py` declares
`documents[0] = {"directory": _FORGE_ROOT / "experiments", "label":
"experiments"}` with `provenance.claim_key = "experiments"` and
`findings.locus_key = "experiments"`. The proposal could not read this file; this
phase could. **C adds the mathematical proposal as `documents[1]`.** No further
ruling is open.

### M3 — the lock that C can move with a comment, and the one it cannot

`L1_EXPECTED_COUNT = L1_BASELINE_AT_S0 (97) − L1_DELIBERATE_SHRINK (1) = 96`,
counting `\bproposal\b` case-insensitively across `_engine_files()`, which is
`ENGINE_DIR.rglob("*.py")` with `ENGINE_DIR = _core/implementation/engine`.
`L1_EXPECTED_FILES = ["implementation_engine.py"]`.

Two consequences, both actionable:

- **`impl_domain_profile.py` is OUTSIDE that scan** (one directory up). C1's
  resolver work cannot move L1 — structurally, not by care.
- **C2/C2b can move it with a single comment.** Document 1 *is* the mathematical
  proposal, so the natural word to write in the new engine prose is the exact
  word this lock counts. D9 rules on it.

### M4 — the refusal roster's pin, and why C1 is invisible to it

`reachable_refusal_codes()` is pinned at **114** and walks for `Refused`/
`NameRefused` constructions. C1's new refusals are `ImplementationProfileError`
— invisible to that walk, by the reason the resolver's own module docstring
already records. C2 adds no refusal at all (`verify` reads; it does not gate).
**Predicted: the pin does not move. A claim apply must measure.**

### M5 — which digest files move, and which cannot

- `tests/seal/digests.json`: `__corpus_fingerprint__` + **28** case entries
  (29 keys) — counted, not inherited. The profile behind it declares one
  document. **Structurally immune.**
- `tests/pair/cases.json`: both sealed cases run `name`, **not** `verify`. So
  `tests/pair/digests.json` is predicted **unmoved** by C1/C2 even though the
  fixture profile behind it is two-document. A claim apply must measure.
- `tests/experiments_seal/cases.json`: **2** `verify` cases. The moment C3
  declares `documents[1]`, `fidelityByDocument` appears in their stdout and
  **those digests move**. That is deliberate, it belongs to C3, and it is
  regenerated with the diff read — never blind-accepted.

### M6 — the two-document fixture profile cannot discriminate as it stands

`tests/fixtures/two_documents/impl_profile.py` declares
`documents[1].label = "experiments"` and **no vocabulary**. Under D1's fallback
its document 1 inherits `claim_key: "equations"` — so document 1's module scope
would equal document 0's and the fold could not tell them apart. **C2a must give
that fixture a document-1 overlay, or its control fixture is unbuildable.** The
file lives under `tests/`, invisible to `discover_profiles()`, so editing it
moves no shipped digest.

## Architecture Decisions

### D1 — Overlay with whole-entry fallback, and the overlay is all-or-nothing

**Choice.** Five optional leaves on each `documents[N]` entry — `claim_key`,
`locus_key`, `remedy_locus_key`, `notation_keys`, `citation_pattern`. An entry
declaring **none** inherits all five from `provenance.*`/`findings.*`. An entry
declaring **any** must declare **all five**; a partial overlay is refused by name.

| Option | Consequence |
|---|---|
| Replace the top-level leaves | Forces an edit to `proposal-implementation/impl_profile.py`; its 28 digests are then protected only by care. Refused by the bar |
| Overlay, **per-leaf** fallback | A `documents[1]` declaring only `claim_key` silently inherits the experiments domain's `notation_keys`. Worse: deleting one leaf from an overlay is then a **zero-mover** — the exact shape of a guard that cannot fire |
| **Overlay, all-or-nothing per entry** | Deleting any one of five from a declared overlay produces an indexed refusal naming that exact leaf. Success criterion 3 is only reachable this way |

**Rationale.** The bar ("nothing may affect what already works in the sibling
skill") outranks schema tidiness, and the all-or-nothing rule is what converts
five optional leaves from unprovable decoration into five mutation-provable
facts. A mixed vocabulary reads plausible and is wrong — the failure class this
project has been paying off.

### D2 — The five scalars are derived from the accessor at index 0, not left beside it

```python
def document_vocabulary(index: int) -> dict:
    """Document `index`'s five claim-vocabulary values. An entry declaring
    none of them inherits all five from `provenance.*`/`findings.*` (D1)."""

CLAIM_KEY = document_vocabulary(0)["claim_key"]
LOCUS_KEY = document_vocabulary(0)["locus_key"]
REMEDY_LOCUS_KEY = document_vocabulary(0)["remedy_locus_key"]
NOTATION_KEYS = document_vocabulary(0)["notation_keys"]
CITATION_RE = re.compile(document_vocabulary(0)["citation_pattern"])
```

**Rejected:** keeping the five `PROFILE[...]` reads verbatim as a document-0 fast
path. That is a second copy of the same rule drifting beside the accessor — the
defect `_impact_class`'s own docstring says it was extracted to prevent. With no
overlay declared, the values are byte-identical, so the rewrite is a zero-delta
edit and must be asserted as one.

### D3 — The resolver tier: indexed refusals, and the group count A deferred

Inside `_resolve()`, after the existing `documents[N].directory`/`.label` walk
and before the `UNSAFE_PATH` tiers:

1. **Partial overlay** → `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` listing each
   missing leaf by its exact indexed path (`documents[1].notation_keys`),
   reusing the existing `missing` accumulator so one message names them all.
2. **`notation_keys`** must be a mapping carrying `locus`, `remedyLocus`,
   `unknown` — the three keys the engine reads. A partial mapping is refused
   naming `documents[1].notation_keys.remedyLocus`.
3. **`citation_pattern` group count** (Slice A's Q3/M2, deferred here
   explicitly): every citation pattern — the top-level one **and** every
   overlay's — must compile and expose **exactly three** capturing groups.
   `_impact_class` reads `match.group(1) or match.group(2) or match.group(3)`;
   two groups raise `IndexError` inside `finding_impact` at runtime, four drop
   the fourth in silence. New code
   `IMPLEMENTATION_DOMAIN_PROFILE_INVALID_CITATION_PATTERN`, naming the leaf, the
   declared group count, and the required three. An uncompilable pattern is
   refused under the same code — the caller's question is the same, the
   precedent `REVISION_UNREADABLE` already set.

All three raise `ImplementationProfileError`, so M4's pin does not move.

**Why the group check applies to the top-level pattern too:** it is document 0's
pattern under D1's fallback, and a check that validated only overlays would leave
the one pattern that ships today unvalidated — a guard that cannot fire on the
only configuration that exists.

### D4 — What "its own four conditions" actually means: the claim-key scope

This is the design's real work, and it is a derivation, not a schema change.

**Document N's module scope `M_N`** = the modules whose `__provenance__` declares
a **non-empty list under document N's `claim_key`**. Nothing else. This is the
proposal's Q3 assumption held: derived from the claim key alone, so no target's
committed `__provenance__` changes shape and `read_provenance` is untouched.

| Condition | Per-document derivation | Splits? |
|---|---|---|
| `stale` | modules in `M_N` whose `revision` ≠ `document_names[N]` | **Yes** |
| `untested` | invariants declared **by modules in `M_N`** with no `test_<name>` | **Yes** |
| `unreached` | `unreached_modules(...)` filtered to `M_N`'s module paths | **Yes** |
| `missing_provenance` | unchanged whole-tree list, reported on **every** index | **No — and stated** |
| `benchmark_undeclared` | unchanged (one bench per target) | **No — and stated** |

**Why `missing_provenance` stays shared, written down rather than faked.** A file
with no readable `__provenance__` declares no claims under **any** claim key, so
it is attributable to no document. Assigning it to document 0 would be an
inference the engine is forbidden to make; splitting it would require asking a
file which document it *should* have bound to, which is unanswerable. It is a
defect against every document's binding, and it is reported as one.

**The consequence that must not be discovered by collision (D6):** the
discriminating condition in any control fixture must be one of the **three that
split**. A fixture built on `missing_provenance` produces identical statuses on a
*correct* implementation and would be misread as a defect.

**`stale` works without a provenance schema change** because a module's
`prov["revision"]` is one name, and which document it belongs to is settled by
which root that name resolves in — exactly the property
`revision_source(name, index)` and `discover_document_revision(index)` were built
with in the amendment. A module implementing document 1 records document 1's
family name.

### D5 — Where the fold runs, and what it emits

`_extra_document_fidelity_status`'s signature stops taking four pre-computed
lists and takes `(doc_revision, index, conditions, benchmark_undeclared)`. Its
`document-count-invariant` docstring is **deleted, because the property is gone**
— not softened.

Under `len(DOCUMENTS) > 1` only, `cmd_verify` builds `M_N` for every index from a
side structure computed in its existing module loop (rel path → per-index claim
lists) that is **never emitted**, then folds per index. Under one document the
side structure is not built and the existing inline block runs unedited.

`fidelity.status` becomes `fidelityByDocument[0].status` — one answer computed
once, the restraint `verify_sources_by_document` already keeps.

**The four emitted top-level lists stay whole-tree.** `fidelity.staleModules`,
`missingProvenance`, `invariantsWithoutTest`, `drift`, `benchmark` keep their
present meaning and shape: they are the tree's inventory, and scoping them would
hide a document-1-only stale module from the report entirely. No key is renamed,
re-nested, or made conditional — Cut 3's D7 rule, carried.

**Each `fidelityByDocument[N]` gains `"conditions"`**, additive, under two
documents only:

```json
{"label": "...", "status": "drift", "revision": "...",
 "conditions": {"staleModules": [...], "missingProvenance": [...],
                "invariantsWithoutTest": [...], "unreachedModules": [...]}}
```

**Rationale.** Without it the only observable per document is a four-value status
word, and neither a reader nor a test can see *which* condition fired or whether
the fold read the index at all. A test asserting scoped lists is a strictly
stronger instrument than one asserting an enum. Rejected: emitting counts only —
a count of 1 and a count of 1 for two different modules are indistinguishable.

### D6 — The control fixture, and why its red is structural

Two two-document targets, each with document 0 and document 1 modules declaring
**disjoint** claim keys.

| Case | Document 0 | Document 1 | Expected |
|---|---|---|---|
| **C-fwd** | modules bound to doc-0's current revision | one module bound to an **older doc-1** revision | doc0 `ok`, doc1 `drift` |
| **C-inv** (control) | one module bound to an **older doc-0** revision | modules bound to doc-1's current revision | doc0 `drift`, doc1 `ok` |
| **C-shared** (negative control) | a module with unreadable `__provenance__` | clean | doc0 **==** doc1, both `drift` |

**The red is structural, not asserted.** The shipped engine computes one `stale`
list and feeds it to document 0's inline fold and to every index ≥ 1. **It cannot
emit two different statuses for the two entries at all.** So C-fwd and C-inv are
each red on the shipped engine for a reason no fixture author chose: not because
an assertion was written to fail, but because the value asserted is
inexpressible. A fold that ignores the index cannot pass either, in either
direction.

C-shared is the guard against a later agent "fixing" `missing_provenance` into a
fake per-document split: it asserts the two statuses are **equal**, and it goes
red if anyone makes the shared condition split.

**Three independent mechanisms, three separate test methods** — never one method
with three asserts. A method halts at its first failing assertion, which is why
`test_implementation_pair.py` was already corrected once.

Placement: `tests/test_implementation_pair.py`, beside
`TwoDocumentLifecycleTests` / `TwoDocumentPositionWriteTests` /
`TwoDocumentAmbiguousFamilyRefusesTests`, driven through that file's existing
`_build_env_with_profile_override`. Real subprocesses: **monkeypatching a module
attribute has zero effect on a child process**, and every case here is a child.

### D7 — `CITATION_RE` per document (C2b), and why the leaf forces it

D1 makes `citation_pattern` mandatory in any overlay. A declared leaf nothing
reads cannot be mutation-proven, and an unprovable leaf is the shape of a false
guard — the rule seven cycles have enforced. So the leaf must reach the one place
it is read.

`_impact_class` gains a fourth parameter, the compiled pattern, defaulting to
`CITATION_RE` so its existing call path is byte-unchanged. `finding_impact`
already maps `label → doc_source` through `sources_by_document`; it gains the
label→index map from `DOCUMENTS` and passes `document_citation_re(index)` for
each label. Same for the `NOTATION_KEYS`/`LOCUS_KEY`/`REMEDY_LOCUS_KEY` reader
lines that sit inside a per-document mapping.

**Rejected:** compiling inside `_impact_class` per call. `CITATION_RE` is
compiled once at module level today; recompiling per finding per document is the
kind of quiet cost a reader cannot see. Compile once per index, at import.

### D8 — Ordering: the proposal's argument is adopted, and C2 splits again

**Adopted, with one correction.** Declaring `documents[1]` before the fold reads
it is precisely the defect C exists to fix, and in one merged unit a green suite
cannot distinguish *"the fold reads document 1"* from *"the fixture was written to
pass"*. D10's lock is deleted **last**, as C3's act — never first, as the
proposal's Scope section says in one place and its Approach step 4 correctly
contradicts. **The Approach is right; this design follows it.**

**C2 splits.** C1's all-or-nothing rule (D1) forces `citation_pattern` into every
overlay, and D7 forces that leaf to reach its reader. Fold and reader-threading
are two deliverable units with independent gates:

| Slice | Delivers | Gate at the end | Estimate |
|---|---|---|---:|
| **C1** | Five overlay leaves; `document_vocabulary`; the resolver tier, indexed refusals and the group-count code (D1–D3); the five scalars re-derived at index 0 | 28 digests identical; `tests/pair/` and the two-document fixture resolve unchanged; `git diff --exit-code` on both sibling skill trees | 550–800 |
| **C2a** | The fold: claim-key scope, three scoped conditions, the `conditions` block, the docstring deleted; the fixture profile's document-1 overlay (M6); C-fwd/C-inv/C-shared | The three control cases, red first against the shipped fold | 600–950 |
| **C2b** | The remaining reader lines threaded by index — per-document `CITATION_RE`, notation and locus keys inside per-document mappings (D7) | A finding whose impact class differs per document, proven | 350–550 |
| **C3** | Declare `documents[1]`; delete D10's lock and replace it; regenerate `tests/experiments_seal/` digests; `SKILL.md` | Item 2 measured, not asserted; `tests/seal/` still 28 identical | 350–550 |
| | | | **1,850–2,850** |

**This is above the proposal's 1,400–2,300, deliberately.** The proposal priced
three slices; this prices four, and prices the proof in each: C1's per-leaf
refusal matrix is ten cases before a line of overlay exists, and C2a's corpus is
two two-document targets authored from nothing. Every estimate this session came
in over except one (865 against an ~870 floor), so read this as the **floor**.
Apply reports measured lines per slice and does not repeat this number.

Against `review_budget_lines: 1400`: **no slice above may merge unstacked**, and
C2a is the one to watch.

### D9 — No new engine prose may spell `proposal`

Per M3, `L1_EXPECTED_COUNT = 96` counts `\bproposal\b` in
`_core/implementation/engine/`. Document 1 is the mathematical **proposal**, so
every comment C2/C2b wants to write about it is a live hazard.

**Rule:** engine prose says *document 1*, *the second document*, or *the
document's declared label* — never `proposal`. If a comment genuinely needs the
word, `L1_DELIBERATE_SHRINK`'s sibling (a recorded, deliberate **growth**) is
edited in the same commit with its reason, exactly as the one recorded shrink was.
Never a silent pin bump.

`impl_domain_profile.py` is outside the scan, so C1 is free.

## Data Flow

```
PROFILE["documents"][N]  ─── overlay declared? ──┐
                                                 │ all five, or refused (D1/D3)
PROFILE["provenance"/"findings"]  ── fallback ───┤
                                                 ▼
                                    document_vocabulary(N)
                          ┌──────────────────────┼──────────────────────┐
                          ▼                      ▼                      ▼
              CLAIM_KEY/…  = index 0     document_citation_re(N)   claim_key(N)
              (D2, zero-delta)            │  (D7, C2b)              │
                                          ▼                         ▼
                                  _impact_class(…, re)     M_N = modules whose
                                  finding_impact             prov[claim_key(N)]
                                                             is non-empty  (D4)
                                                                  │
   cmd_verify ── len(DOCUMENTS) > 1 ──────────────────────────────┤
                          │                                        ▼
                          │                  stale_N / untested_N / unreached_N
                          │                  + shared missing_provenance,
                          │                    benchmark_undeclared
                          ▼                                        │
          _extra_document_fidelity_status(doc_revision, N, ─────────┘
                                          conditions, undeclared)
                          │
                          ▼
        fidelityByDocument[N] = {label, status, revision, conditions}   (D5)
        fidelity.status = fidelityByDocument[0].status

   len(DOCUMENTS) == 1 → every branch above unreachable
                       → tests/seal/digests.json, 28, byte-identical
```

## File Changes

| File | Action | Description |
|---|---|---|
| `_core/implementation/impl_domain_profile.py` | Modify | Overlay tier, all-or-nothing rule, indexed refusals, `notation_keys` shape, citation group count (D1/D3). **C1** |
| `_core/implementation/engine/implementation_engine.py` | Modify | `document_vocabulary`; five scalars re-derived (D2); claim-key scope, scoped conditions, `_extra_document_fidelity_status` rewritten and its docstring deleted, `fidelityByDocument[].conditions` (D4/D5); per-index `CITATION_RE`/notation/locus threading at the 21 reader lines (D7). **C2a/C2b** |
| `tests/fixtures/two_documents/impl_profile.py` | Modify | Document-1 overlay (M6). **C2a** |
| `tests/test_implementation_pair.py` | Modify | C-fwd / C-inv / C-shared, three methods (D6). **C2a** |
| `tests/test_implementation_profile.py` | Modify | Overlay refusal matrix, group-count cases. **C1** |
| `.claude/skills/experimental-implementation/impl_profile.py` | Modify | `documents[1]` = the mathematical proposal, with its own five leaves. **C3** |
| `.claude/skills/experimental-implementation/SKILL.md` | Modify | The second document, and what `verify` now answers. **C3** |
| `tests/test_implementation_domain_lock.py` | Modify | `SingleDocumentGuaranteeTests` **deleted**, replaced by a lock proving the per-document read. **C3** |
| `tests/experiments_seal/digests.json`, `cases.json` | Modify | Two-document cases; digests regenerated with the diff read (M5). **C3** |
| `tests/seal/**`, `proposal-implementation/**`, `proposal-deliberation/**`, `experimental-deliberation/**`, `_core/deliberation/**` | **Untouched** | the bar; `git diff --exit-code` must exit 0 |

## Mutation Plan

Every row: confirm the anchor's count **before** (exactly 1) and **after** (0/1),
break it on disk, watch the named test die, restore, re-assert. **An anchor that
matched is not a mutation that ran**; `sd -s` exits 0 having changed nothing;
`git diff --stat` proves nothing until existence is confirmed at both endpoints,
and nothing at all for an untracked file. Clear `__pycache__` before every Python
mutation — **a same-size edit reuses a stale `.pyc`**. Never mutate the real
engine: plant into a scratch copy, the mechanism
`test_implementation_domain_mutation.py` already has. **`sys.modules` caches
`impl_domain_profile` process-wide; the `pop` stays.**

| # | Break | Anchor | Must go red |
|---|---|---|---|
| Y1 | Delete each of the five overlay leaves from a declared overlay, one at a time | leaf literal 1→0 | `…_INCOMPLETE` naming `documents[1].<leaf>` exactly |
| Y2 | Declare a two-group and a four-group `citation_pattern`, top-level and overlay (4 cases) | group count | `…_INVALID_CITATION_PATTERN` naming the leaf and the count |
| Y3 | Change each overlay leaf's value | old literal 1→0, new 0→1 | a named case, **or** recorded as a measured zero-mover with its defence |
| Y4 | In the scope builder, `claim_key(index)` → `CLAIM_KEY` | call-site count | C-fwd **and** C-inv; `tests/seal/` must survive |
| Y5 | In the stale derivation, `document_names[index]` → `revision` | index literal | C-fwd and C-inv; seal survives |
| Y6 | Make `missing_provenance` scope by index | shared-list reference 1→0 | **C-shared** — the only case that catches it |
| Y7 | Revert `fidelityByDocument[N].conditions` to the shared lists | key count | the condition-list assertions, not the status ones |
| Y8 | Add `documents[1]` to the shipped profile **before** C3 | `"directory":` 1→2 | D10's lock (the ordering proof: it must still fire through C1 and C2) |
| Y9 | In `_impact_class`, ignore the passed pattern and use `CITATION_RE` | parameter read 1→0 | C2b's per-document impact-class case |

**A surviving mutation has two explanations.** Apply measures *which* — whether
the test is weak or the claim was wrong — before strengthening anything.

## What Breaks — Producers and Products

| Class | Item | Verdict |
|---|---|---|
| Producer | `_resolve()`'s validation walk | Gains a tier; existing messages unchanged |
| Producer | `CLAIM_KEY`/`LOCUS_KEY`/`REMEDY_LOCUS_KEY`/`NOTATION_KEYS`/`CITATION_RE` definitions | Re-derived through `document_vocabulary(0)`; **values identical — assert, do not infer** |
| Producer | `_extra_document_fidelity_status` signature + docstring | Rewritten; the `document-count-invariant` claim deleted |
| Producer | `_impact_class`, `finding_impact` | Gain a pattern parameter with a default; existing call path unchanged |
| Producer | `unreached_modules` | Unedited — its `CLAIM_KEY` read is an **output key**, not a filter; the filtering happens at the caller |
| Producer | `SingleDocumentGuaranteeTests` | **Deleted in C3**, replaced by a lock proving the per-document read |
| Producer | `L1_EXPECTED_COUNT` / `L1_EXPECTED_FILES` | **Predicted unmoved under D9. C edits engine bytes, so A's structural immunity is gone — assert, never infer** |
| Producer | `reachable_refusal_codes()` pin (114) | Predicted unmoved (M4); measure |
| **Product** | `tests/seal/digests.json` (28) | **Untouched**, and asserted so, after **each** slice |
| **Product** | `tests/pair/digests.json` | Predicted unmoved — both cases run `name`, not `verify` (M5). Measure |
| **Product** | `tests/experiments_seal/digests.json` | **Moves in C3**, deliberately, by `fidelityByDocument` appearing in 2 `verify` cases. Regenerated with the diff read |
| **Product** | Targets' committed `__provenance__` blocks | **Untouched.** D4 derives scope from the claim key alone; no provenance schema change |
| **Product** | Targets' `.implementation/position.jsonl`, minted authorizations, `tests/admissibility.json` | **Untouched.** C changes no binding key and no written record shape; `_AUTHORIZATION_BINDING_KEYS` and `proposalDigest` are out of scope and unedited |
| **Product** | Managed revisions under `proposals/` / `experiments/` | Both hold only `.gitkeep`. **None exist** — stated, not left implicit |
| **Product** | Archived reports carrying `source_digest`/`suite_digest` | Untouched; no digest input changes |

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | Overlay resolution | No overlay → identical values to today, asserted leaf by leaf; full overlay → the overlay's values; partial → refusal naming the exact indexed leaf |
| Unit | Group count | 2-group and 4-group patterns, top-level and overlay, each its own case |
| Unit | Scope builder | A module claiming only doc 0, one claiming only doc 1, one claiming both, one claiming neither — four memberships asserted directly |
| Integration | The fold | C-fwd / C-inv / C-shared, real subprocesses, three separate methods (D6) |
| Integration | Per-document impact class | One finding whose `class` mapping differs by label because the two documents cite with different patterns (D7) |
| Non-interference | The bar | 28 digests byte-identical **after each slice**; `tests/pair/` and the two-document fixture resolve; `git diff --exit-code` on both sibling skill trees; `npm test` **595/595**; Python `OK (skipped=6)` with `Ran` grown — **`skipped=6` must not move**, and no `skipTest` is added anywhere |
| Mutation | Y1–Y9 | Anchor-counted both directions, scratch copies only |

**Commit granularity.** Every work unit is two commits: a `test(...)` commit
carrying only the failing test(s), individually checkoutable with the test red at
that sha, then the implementation. C2a's first commit is the exception by design
— it is a RED commit and its red is the deliverable.

## Threat Matrix

| Row | Applicable | Behaviour / RED test |
|---|---|---|
| Subprocess invocation | Yes (inherited) | Pair and seal cases; `shell=False`, list argv, unchanged. No new entry point |
| Regex from a profile (**new**) | **Yes** | `citation_pattern` is host-supplied text compiled into a matcher. D3 compiles it at resolve time so a malformed pattern refuses by name instead of raising mid-command. No dynamic construction, no user input concatenated. RED: an uncompilable pattern refuses at resolve, not at `finding_impact` |
| Environment-variable routing | Yes | `IMPLEMENTATION_PROPOSALS`/`_1` semantics unchanged; no new variable |
| Path traversal via profile | Yes | `documents[N].directory` tier unchanged — absolute required, existence not |
| Data integrity of persisted records | **Yes — headline** | M5 + the Products table: no record shape changes; the only digest file that moves is the second corpus's, in C3, deliberately |
| Executable-file classification | N/A | No file modes, no new entry point |
| Routing / shell commands | N/A | `COMMANDS` untouched; no new subcommand, no new flag |
| VCS / PR automation, Network | N/A | None reached |

## Migration / Rollout

No data migration — by the Products table there is nothing of the changed shape
on any disk.

**Rollback**, per unit then per slice, tip-first. `tests/seal/` is untouched by
construction, so the pre-change seal is the post-revert seal. **Restoring
`SingleDocumentGuaranteeTests` is part of reverting C3, not an afterthought** —
without it a stray `documents[1]` survives the rollback in silence. Reverting C3
alone leaves C1/C2 shipped and dormant, which is safe: every new branch is gated
on `len(DOCUMENTS) > 1` and no shipped profile then declares two.

## Predictions This Design Makes — Claims Apply Must Measure, Not Repeat

- [ ] The five scalars' values are byte-identical after D2's re-derivation.
- [ ] `tests/seal/digests.json` is byte-identical after **each** slice.
- [ ] `tests/pair/digests.json` is unmoved by C1, C2a and C2b.
- [ ] `L1_EXPECTED_COUNT` stays **96** and `L1_EXPECTED_FILES` stays one file.
- [ ] `reachable_refusal_codes()` stays **114** — C1's refusals are
      `ImplementationProfileError` and C2 adds none.
- [ ] `skipped=6` does not move; no `skipTest` is added.
- [ ] C-fwd and C-inv are **both** red against the shipped fold, and red because
      the two statuses cannot differ — not because an assertion was authored to
      fail. If either is green, the fixture is wrong, not the engine.
- [ ] C-shared is **green** on the shipped engine and stays green after C2a. It
      is the only case that reddens if `missing_provenance` is faked into
      splitting.
- [ ] The engine threads **21** reader lines, not 26 — re-derive both.
- [ ] `tests/experiments_seal/` digests move in C3 and nowhere earlier.

**A design prediction about tooling is a claim, not a fact.** Every box above is
measured at apply and reported with its measurement, never ticked by repetition.

## Open Questions

- [x] Which document A declared → **the experiments document**, confirmed
      against `impl_profile.py` on disk (M2). C adds the mathematical proposal.
- [x] Replace or overlay → **overlay, all-or-nothing per entry** (D1).
- [x] What makes the four conditions per-document → **the claim-key scope**,
      three conditions split and two are stated as shared (D4).
- [x] `citation_pattern` group count → **resolver tier, exactly three, top-level
      and overlay** (D3).
- [x] Does C2 split → **yes, C2a and C2b** (D8).
- [ ] **A document whose revision is simply absent still reports `"unknown"`,
      reported and never refused** — proposal Q4's assumption, carried
      unchanged: `verify` is a reader. Recorded, not silently closed.
- [ ] **Should an overlay be permitted on `documents[0]`?** D2's accessor honours
      one; no profile declares one and nothing forces the question. Left open
      rather than forbidden in silence.
- [ ] Cross-document verdicts, repair-direction inference, per-document revision
      pins: out of scope by intent, unchanged from the proposal.

## Citations Checked

Located **by name, in the source, this phase, never by line and never
inherited**: `CLAIM_KEY`, `LOCUS_KEY`, `REMEDY_LOCUS_KEY`, `NOTATION_KEYS`,
`CITATION_PATTERN`, `CITATION_RE`, `DOCUMENTS`, `DOCUMENTS_DIRECTORY`,
`DOCUMENTS_LABEL`, `SKILL_ROOT`, `CLI_PATH`, `CLI_INVOCATION`, `PRODUCT_DIRS`,
`_impact_class`, `finding_impact`, `_extra_document_fidelity_status`,
`cmd_verify`, `unreached_modules`, `read_provenance`, `proposals_root`,
`revision_source`, `discover_document_revision`, `document_revision_names`,
`_document_extra_sources`, `revision_discovery`, `resolve_benchmark_declaration`,
`changed_sections`, `test_function_names`, `remedy_compatibility`,
`admissibility_record`, `_resolve`, `_REQUIRED_NESTED`, `_REQUIRED_PRESENCE`,
`_OBJECTIVE_REQUIRED`, `_STAGE_REQUIRED`, `ImplementationProfileError`,
`reachable_refusal_codes`, `GATING_REFUSALS`, `L1_BASELINE_AT_S0`,
`L1_DELIBERATE_SHRINK`, `L1_EXPECTED_COUNT`, `L1_EXPECTED_FILES`,
`_engine_files`, `ENGINE_DIR`, `ENGINE_FILE`, `SKILLS_DIR`,
`CAMPAIGN_PROPOSAL_SYMBOLS`, `LockADiscoveryTests`, `LockBEngineNeutralityTests`,
`SingleDocumentGuaranteeTests`, `discover_profiles`, `TwoDocumentsResolveTests`,
`TwoDocumentPositionWriteTests`, `TwoDocumentAmbiguousFamilyRefusesTests`,
`TwoDocumentLifecycleTests`, `_build_env_with_profile_override`.

**Inherited claims re-measured this phase:**

1. The proposal's **26 distinct lines / 32 symbol-line hits** — **confirmed
   exactly**, and decomposed into 5 definition lines and **21 reader lines**, the
   number apply actually threads (M1).
2. The proposal's open **Q1** — **settled against disk**, not against a record:
   `documents[0]` is `experiments/` (M2).
3. The bar's **28 digests** — counted: `tests/seal/digests.json` holds
   `__corpus_fingerprint__` plus 28 case entries (M5).
4. The proposal's Scope line calling D10's deletion *"this change's first act"* —
   **contradicted by its own Approach step 4** and by A's D10, which says C's
   *first RED test* is the criterion. Corrected in D8: the lock is deleted
   **last**. The proposal's Risks table already agrees.
5. The proposal's *"the roster is referenced from the engine but defined outside
   `_core/`"* — located: `reachable_refusal_codes()` in
   `tests/test_proposal_implementation.py`, pinned at 114, walking for
   `Refused`/`NameRefused` only, therefore blind to C1's refusals (M4).

---

## Reconciliation: spec and design do NOT disagree about the fallback

`sdd-spec` flagged the proposal as carrying two competing signals — mandatory
per-index versus optional-with-fallback — and resolved toward optional. D1 above
rules "all-or-nothing". Read quickly those look like a conflict. **They are two
different granularities and both hold:**

| Level | Rule | Source |
| --- | --- | --- |
| **Per entry** | An entry declaring NO vocabulary inherits all five from the top level | spec, and D1's own first sentence |
| **Within a declared entry** | An entry declaring ANY of the five must declare all five | D1 |

The spec's concern is satisfied: `tests/pair/` and
`tests/fixtures/two_documents/impl_profile.py` declare no vocabulary, so they
inherit and keep resolving **unedited by the resolver's rule**.

D1's reason for all-or-nothing is the stronger half and stands: per-leaf fallback
would make deleting one leaf a **zero-mover**, and success criterion 3 — *removed
→ an indexed refusal naming that exact leaf* — is reachable only under
all-or-nothing. A leaf whose deletion changes nothing is the unprovable-field
shape this project has been removing for eight changes.

**One consequence that is NOT the resolver forcing anything**: D1 also records
that `tests/fixtures/two_documents/impl_profile.py` gains a document-1 overlay in
C2a. That is a *fixture-content* need, not a resolver demand — its document 1
currently inherits `claim_key: "equations"`, so without an overlay the two
documents cannot differ and the control is unbuildable. The resolver would have
accepted it unedited.

## A second bar, and it is not the first one relaxed

D1's slicing records that **`tests/experiments_seal/digests.json` WILL move in
C3**, deliberately, regenerated with the diff read.

That is not the standing bar loosening. Eight changes have held *"any digest
movement is a defect, never a new golden"* — and that bar is about
**`tests/seal/`**, the sibling's corpus, which this change must leave
byte-identical. `tests/experiments_seal/` is the NEW skill's own corpus, and when
the new skill's behaviour legitimately changes, its digests are supposed to move.

State both directions, because either confusion is expensive: applying the old
bar to the new corpus would block correct work, and applying the new leniency to
`tests/seal/` would silence the guard six changes were built on.
