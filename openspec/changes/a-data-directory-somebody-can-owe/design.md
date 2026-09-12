# Design: A `Data/` directory somebody can owe — Slice B

> **Budget note.** Over the 800-word default, on the precedent Slice C's own
> design records, and for the reason this change's brief states: *mechanics
> concrete enough that apply invents nothing*. Three of the items below are
> corrections to inherited counts, and a correction that does not carry its
> measurement is just another inherited count.

## Technical Approach

`with_data` stops being derived from the repository's own contents and starts
being derived from **what the bound document says**, at both producers, without
either producer losing the derivation it already has.

Four properties hold the sibling's bar structurally, not by care:

1. **A `None` marker is never read.** The detector short-circuits on the leaf
   before it opens anything. Every profile on disk after B1 declares `None`, so
   no document is opened and both producers take today's exact branch.
2. **`plan` consults a document only when `--revision` is given.** No discovery,
   ever, at `plan`. Absent the flag, `build_plan`'s new disjunct and its new key
   are both structurally unreachable.
3. **The declaration is a disjunct, never a replacement.** `cmd_verify` becomes
   `declared or is_dir()`; `build_plan` becomes `declared or <its two existing
   disjuncts>`. Nothing that demands a `Data/` today stops demanding one.
4. **The shipped marker is the last write of the change.** B1 proves the
   detector against a planted configuration in the sibling's own 28-case
   harness; B2 declares.

## Measurements from this phase — every symbol grepped by name, none inherited

### M1 — `--revision` reaches **nine** commands, through **two** registrations

`main()` registers it once for `{verify, admit, handoff, probe, position, gate,
offer, close}` — eight — and **again, separately, for `walk`**. The proposal's
"registered for exactly eight commands" describes the first registration, not
the flag. `settle` records in a comment why it has none: *"a flag it ignores
would be a promise this file does not keep."* That comment decides D3 below.

### M2 — `cmd_verify` computes `with_data` ~95 lines before it has a revision

Order in `cmd_verify` today, by symbol: `with_data` → `missing_dirs` →
`structure_ok` → the module loop (`module_claims_by_index`) →
`resolve_benchmark_declaration` → `revision_discovery` → `revision = args.revision
or discovered`. So the declaration is not available where `with_data` is
computed. **`missing_dirs` is read in exactly two places** (`structure_ok`, and
`structure.missingDirs` in the output dict) and **`structure_ok` in exactly one**
(`structure.status`). Both readers sit below the revision block. The reorder is
therefore three statements moved down, not a restructure — D5.

### M3 — the two guards, and why one is a wall and the other is blind

- `CoreNamesNoDomainTests` scans `CORE.glob("*.py")` — **non-recursive**, so the
  eleven flat `_core/implementation/*.py` files, never `engine/`. It fails on a
  **case-sensitive substring** of any of `Notebooks`, `Data`, `Results`,
  `Models`, `src`, `tests`, `tools`. Measured this phase: those eleven files
  contain **zero** occurrences of any of the seven. That is a live wall, not a
  theoretical one — a docstring in `impl_domain_profile.py` saying "the `Data/`
  folder" reddens it.
- `LockBEngineNeutralityTests` builds its needles from `vocabulary.names`. No
  profile declares `Dataset`, and none should. **A hardcoded `**Dataset:**` in
  the engine is invisible to it.** D7 is the answer.

### M4 — a lock phrased over the word `dataset` is red at HEAD

`classify` already returns the reason string `"dataset"` for `DATA_EXT`. Any
guard of the shape "the engine never says dataset" fails today. The lock must be
over the **declared marker value**, never the English word — D7.

### M5 — F5's remaining class: 3 sites, 4 occurrences; the rest of the class is 22

Bare `Data` literals outside `PRODUCT_DIRS`: `classify` (1), `build_plan` (2 in
one expression), `cmd_verify` (1). B touches the last two sites. Measured for
scope honesty: `Notebooks`/`Results`/`Models` literals appear on **22** further
lines. The zero-literal lock in D6 is scoped to `Data` deliberately; the 22 are a
named follow-up, not a silent omission.

### M6 — `tests/experiments_seal/`'s fingerprint is the file's own sha256

`CORPUS_FINGERPRINT_SOURCE = Path(__file__)`. Editing `corpus.py` at all moves
`__corpus_fingerprint__`, whether or not one case digest changes. That movement
is mechanical and must be separated from case movement before anything is
accepted — D9.

### M7 — the sibling's seal corpus already carries line-leading headings

`tests/seal/corpus.py`'s revision text has lines beginning `## 1`, `## 2`,
`## 3`. This is what makes the leaf a **measured mover** in the existing 28-case
harness rather than a zero-mover — D8's mutation.

## Architecture Decisions

### D1 — The leaf is a literal line-leading marker, required per `documents[N]`, nullable

**Choice.** `documents[N].dataset_marker`: a string, or `None`. Required key on
every entry — it joins the per-entry walk beside `directory` and `label`,
appended after them so existing `..._INCOMPLETE` message ordering is unchanged.

| Option | Consequence |
|---|---|
| A callable | Un-renderable in `profile_values_text`, un-validatable in shape, and the kit crossing the seam. Rejected |
| A regex | Precedent exists (`citation_pattern`) but buys nothing: the question is presence, not extraction. It would need its own compile tier and hands a host arbitrary backtracking over document bytes. Rejected |
| **A literal marker** | One `str`/`None` leaf. Renders into `values_text`. Mutation-proven by changing one quoted literal |

**It is NOT a member of `_DOCUMENT_VOCABULARY_LEAVES`.** Adding it there would
drag the existing all-or-nothing rule over it and force every entry of every
profile to declare a full five-leaf overlay — a behavioural change B does not
want. Its own required-key check, its own tier.

**Matching rule:** a line whose text, after `lstrip()`, **starts with** the
marker, matched case-sensitively, anywhere in the resolved revision's text.
Rejected: a bare substring test. A document that discusses its own format —
"every protocol needs a `**Dataset:**` line" — would satisfy a substring test
while declaring nothing, which is this project's own "a guard searching for a
literal declared in it" scar, one level up.

### D2 — Every declared document is consulted, or-folded

The demand is true when **any** declared document whose revision resolves
carries its own marker. Document 0's name is the seed; every index beyond it
discovers its own, through `document_revision_names` — Slice C's machinery,
unedited.

**Rationale.** Ruling 1 places the leaf per document. If only index 0 were ever
read, the per-document placement would be decoration — the unprovable-field
shape eight changes have been removing. Or-folding is also the operator's own
rule: a repository owes a `Data/` if the method it is bound to needs one.

### D3 — `--revision` is registered on `plan` alone; `apply` and `materialize` inherit the binding from the approved plan

This **contradicts the brief's "three parser registrations"**, and the argument
is M1's comment on `settle`.

`cmd_apply` and `_materialize_plan_gate` both already load the approved plan
before calling `build_plan`. They read the seed **out of the plan's own
conditional key** (D4) and pass it. So the three call sites agree *by
construction* rather than by operator discipline — an operator who ran `plan
--revision X` and then a bare `apply` cannot produce `PLAN_STALE`, which is the
failure mode the proposal's top risk names.

| Option | Consequence |
|---|---|
| Flag on all three | An `apply --revision Y` against a plan approved at `X` can only contradict the approval. A flag whose every non-default use is a defect |
| Flag on none; discover at `plan` | `plan` runs on a bare clone; discovery there makes its answer depend on a directory the operator did not name. Also breaks property 2 |
| **Flag on `plan`; seed carried in the plan** | One registration (the eight-name set becomes nine; ten commands carry the flag). The name comes from the approval; the **bytes are re-read**, so a marker deleted since approval still moves `createDirs` and still refuses `PLAN_STALE` |

`boundTo` is **not** added to `cmd_apply`'s four-key comparison. Under this
design `current["boundTo"]` is derived from `approved["boundTo"]`, so comparing
them is a check that cannot fail — the exact shape this project removes.
Accepted and named: a plan whose *document-1 discovery* moved without changing
`createDirs` applies unchanged, because no action it performs differs.

### D4 — One conditional key, emitted only when a document was nameable

```json
"boundTo": {"revision": "dataset-1.md",
            "documents": [{"label": "experiments", "revision": "dataset-1.md",
                           "declaresDataset": true}]}
```

Set after the plan literal, beside `plan["reorganization"]`, and **only when
`revision is not None`**. `plan` with no `--revision` emits byte-identical
stdout — the structural guarantee for `plan-a`/`plan-b` in **both** corpora.

**`cmd_verify` gains no new key.** Its only new observable is
`structure.missingDirs` and, through it, `structure.status`. Any added key would
move the sibling's digests for a reason unrelated to the demand.

### D5 — `cmd_verify`: three statements move down, nothing else

`with_data`, `missing_dirs` and `structure_ok` move below `revision = args.revision
or discovered`. By M2 they have exactly three readers between them and all three
are below that line. Every statement they depend on (`stray`, `stale_refs`,
`unparsable`, the three `*_recorded`) stays where it is. Output key order is
fixed by the final dict literal, so the move is observationally inert.

**Rejected:** extracting a second revision resolver so `with_data` could be
computed in place. That is a second copy of the discovery rule drifting beside
the first — the defect `_impact_class`'s own docstring records.

### D6 — F5's class is finished, and the zero is asserted by a derived lock

Four literal edits (M5), then `ZeroBareDataLiteralTests`: load the engine, take
`PRODUCT_DATA` off the CLI, and assert the engine source contains that string in
quotes **exactly once** — the `PRODUCT_DIRS` tuple. Derived from the CLI, never
restated, so it holds a fifth category the day one appears.

The zero-delta claim is asserted three ways and never inferred: the lock, the 28
sibling digests unchanged at that commit alone, and a full suite run at that sha.

### D7 — The new neutrality lock, and why it lands in B2

`LockCDeclaredMarkerTests`: for every profile `discover_profiles()` finds, for
every non-`None` `documents[N].dataset_marker`, assert the literal appears in no
file under `ENGINE_DIR`. Non-vacuity asserted (`assertGreater(len(markers), 0)`).

It is **vacuous until a shipped profile declares a marker**, so it lands with the
declaration, in B2. B1's protection is not absent, it is different: D8's
`MEASURED_MOVERS` entry is a zero-mover the moment the engine stops reading the
leaf, so an engine that hardcoded a marker fails B1's own harness.

By M4 the lock is over the declared **value**, never the word `dataset`.

### D8 — The mutation that makes the leaf a mover in the sibling's own harness

`MUTATIONS["documents.dataset_marker"] = ('"dataset_marker": None,',
'"dataset_marker": "## 2",')`. By M7 the sibling's corpus revisions carry a
line-leading `## 2`, authored for another purpose entirely, so the mutated leaf
makes the detector answer **true against real document bytes no one wrote for
this guard**.

**Predicted movers: `verify-b` (and `verify-t` if its fixture has no `Data/`).**
A claim apply must measure and record — never a forecast written into
`MEASURED_MOVERS`, per that file's own correction note.

The anchor is exact: `None,` appears once under `dataset_marker` in the
sibling's single-entry `documents` list. Anchor-count both endpoints, 1→0 and
0→1, clear `__pycache__`, and **`pop` `impl_domain_profile` from `sys.modules`**
or every leaf reads as a zero-mover.

### D9 — B2's corpus axis: two documents differing in one line, and zero existing cases move

The corpus authors **two new revisions in document 0's root, outside the
discovered family**: `dataset-0.md` and `dataset-1.md`, byte-identical except
that `dataset-1.md` carries one `**Dataset:** …` line.

`verify`'s family is derived from the bench's declared `trial-1.md`, so
`trial-(\d+)\.md`; neither new file matches, so **no existing case's discovery
changes and no existing revision's bytes change**.

**Rejected: putting the marker on `trial-2.md`.** It would move `verify-b` for
the right reason and *also* move `probe`, `position-e0/e1`, `gate-e1`,
`offer-e1`, `close-e1` and `handoff-e1` because that file's bytes changed —
confounding "the detector fired" with "the input moved". A measurement that
cannot distinguish those two proves neither.

Four new cases:

| id | fixture | `--revision` | declares | `Trial/Data/` | Expected |
|---|---|---|---|---|---|
| `verify-b-declared` | B | `dataset-1.md` | yes | absent | `missingDirs` **contains `Trial/Data`**, `structure.status: drift` — **the acceptance condition** |
| `verify-a-declared` | A | `dataset-1.md` | yes | present | `missingDirs` empty — control 1 |
| `verify-b-undeclared` | B | `dataset-0.md` | no | absent | `missingDirs` empty; differs from `verify-b-declared` in exactly the marker line in and the `missingDirs` list out — control 2 |
| `plan-b-declared` | B | `dataset-1.md` | yes | absent | `createDirs` contains `Trial/Data`; `boundTo` present |

**Which digests move in B2, per case: none of the existing twenty.** The file
moves by `__corpus_fingerprint__` (M6, mechanical) plus four new entries. This is
a **stricter** bar than C3's six-of-twenty, and it is stated as the acceptance
condition: if any of the existing twenty moves, the cause is found and named
before anything is regenerated.

### D10 — Landing order: the proposal's B1 → B2 is adopted unchanged

Declaring the shipped marker before the detector is proven is the C3 defect at
smaller scale. Adopted, with one strengthening the proposal did not have: **B1's
reaching configuration is not a fixture at all, it is D8's mutation of the
sibling's real profile against the sibling's real corpus.** A fixture written to
satisfy the detector proves nothing; a corpus authored two changes ago for
another purpose cannot have been.

`tests/fixtures/two_documents/impl_profile.py` still gains two `None` lines in
B1, because the leaf is required — a fixture edit, not a reaching configuration.

## Data Flow

```
--revision (plan only)  ─┐
approved["boundTo"]      ├─► seed ──► document_revision_names(seed)
  (apply, materialize)  ─┘                     │  Slice C machinery, unedited
                                               ▼
                     for each index: PROFILE["documents"][N]["dataset_marker"]
                                               │
                        None ──► False (file never opened)   ◄── the sibling's bar
                                               │
                        str  ──► revision_source(name, N)  ── the ONE path join
                                               │            (no second site: D-threat)
                                               ▼
                                   any lstrip().startswith(marker)
                                               │  or-fold over every index (D2)
                                               ▼
                                        declares_dataset
                    ┌──────────────────────────┴──────────────────────┐
                    ▼                                                 ▼
 build_plan: declared or dir_exists_after or moves-derived   cmd_verify: declared or is_dir()
                    │                                                 │
                    ▼                                                 ▼
          plan.createDirs  + plan.boundTo (conditional)      structure.missingDirs
                    │                                                 │
      cmd_apply / _materialize_plan_gate re-derive              structure.status: drift
      from the SAME seed ⇒ no PLAN_STALE                        ⇒ `standing` is behind
```

## File Changes

| File | Action | Slice | Description |
|---|---|---|---|
| `_core/implementation/impl_domain_profile.py` | Modify | B1 | `documents[N].dataset_marker` required-key tier (D1). **Its prose may not spell `Data`/`tests`/`src`/`tools`/`Notebooks`/`Results`/`Models` (M3)** |
| `_core/implementation/engine/implementation_engine.py` | Modify | B1 | The detector (D1/D2); `build_plan` signature, third disjunct, `boundTo` (D4); `cmd_verify`'s three-statement move and disjunct (D5); `cmd_plan`/`cmd_apply`/`cmd_materialize` threading (D3); one parser name added; F5's four literals (D6) |
| `.claude/skills/proposal-implementation/impl_profile.py` | Modify | B1 | **One line**: `"dataset_marker": None,` |
| `tests/fixtures/two_documents/impl_profile.py` | Modify | B1 | Two `None` lines; invisible to `discover_profiles()` |
| `tests/test_implementation_profile.py` | Modify | B1 | The missing-leaf refusal case, per index |
| `tests/test_implementation_domain_mutation.py` | Modify | B1 | `MUTATIONS` + `MEASURED_MOVERS` entries, **measured** (D8) |
| `tests/test_experimental_implementation.py` | Modify | B1 | Detector unit cases incl. the mid-sentence negative; the `PLAN_STALE` agreement test (real subprocesses: plan → approve → apply) |
| `tests/test_implementation_core.py` | Modify | B1 | `ZeroBareDataLiteralTests` (D6) |
| `.claude/skills/experimental-implementation/impl_profile.py` | Modify | **B2** | `documents[0].dataset_marker` — **last write of the change** |
| `.claude/skills/experimental-implementation/SKILL.md` | Modify | B2 | What `verify` now demands, and the three per-product-folder reasons |
| `tests/experiments_seal/corpus.py`, `cases.json`, `digests.json` | Modify | B2 | D9's two revisions and four cases; digests read per case |
| `tests/test_implementation_domain_lock.py` | Modify | B2 | `LockCDeclaredMarkerTests` (D7) |
| `tests/seal/**`, `proposal-deliberation/**`, `_core/deliberation/**` | **Untouched** | — | the bar: `git diff --exit-code tests/seal/` exits 0 |

## What Breaks — Producers and Products

| Class | Item | Verdict |
|---|---|---|
| Producer | `build_plan` signature | Third parameter, defaulted. **Every caller in tests must be found — only a full uninterrupted suite run catches this class** |
| Producer | `expected_dirs`, `dir_exists_after`, `classify` | Unedited except F5's literal in `classify`; behaviour identical |
| Producer | `_resolve()`'s per-entry walk | Gains one append after `label`; existing message ordering unchanged |
| Producer | `cmd_verify`'s statement order | Three statements move (D5); asserted inert by the seal, never inferred |
| Producer | `_materialize_plan_gate` signature | Unchanged — it reads the seed out of `approved`, which it already parses |
| Producer | `reachable_refusal_codes()`'s roster | **Predicted unmoved**: the new refusal is `ImplementationProfileError`, invisible to that walk, and B adds no `Refused`. Assert, never assume |
| Producer | `LockADiscoveryTests`' haystack | Grows by `"None"`/the marker via `profile_values_text`. Cannot redden — it only widens the haystack. Measure |
| Producer | `L1_EXPECTED_COUNT` (`\bproposal\b` in `engine/`) | **Live hazard**: `boundTo`'s prose is about a document. Engine prose says *the bound document*, never `proposal`. Measure |
| **Product** | `tests/seal/digests.json` (28) | **Untouched**, asserted after **each** slice |
| **Product** | `tests/pair/digests.json` | Predicted unmoved; its cases run `name`. Measure |
| **Product** | `tests/experiments_seal/digests.json` | B1: unmoved. B2: fingerprint + 4 new entries, **zero existing cases** (D9) |
| **Product** | Approved `plan.json` files already on disk | They carry no `boundTo`. `(approved.get("boundTo") or {}).get("revision")` → `None` → today's branch. **Old plans keep applying** |
| **Product** | Targets' `__provenance__`, `position.jsonl`, minted authorizations, `tests/admissibility.json` | **Untouched.** No binding key and no written record shape changes; `_AUTHORIZATION_BINDING_KEYS` and `proposalDigest` are out of scope and unedited |
| **Product** | Managed revisions under `experiments/` | `.gitkeep` only. **None exist** — stated, not left implicit |

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | The leaf's absence | Per index, `..._INCOMPLETE` naming `documents[N].dataset_marker` exactly |
| Unit | `None` never opens a file | The detector is handed a revision whose file does not exist and still returns `False` without raising |
| Unit | Line-leading, not substring | A document carrying the marker **mid-sentence only** must answer `False`. This is the strength case |
| Unit | The or-fold | Two-document fixture: only document 1 declares, and the demand still holds (kills "read index 0 always") |
| Unit | F5's class | `ZeroBareDataLiteralTests` (D6) |
| Integration | The three call sites | Real subprocesses: `plan --revision X` → approve → `apply` exits 0 and `createdDirs` contains the `Data/`; and the same through `materialize --stage` |
| Integration | The demand, end to end | D9's four sealed cases |
| Non-interference | The bar | 28 sibling digests byte-identical **after each slice**; `git diff --exit-code tests/seal/`; `npm test` 595/595; Python `OK (skipped=6)` with `Ran` grown — **`skipped=6` must not move in a ninth change, and no `skipTest` is added** |
| Mutation | X1–X5 below | Anchor-counted both directions, scratch copies only |

### Mutation plan

| # | Break | Anchor | Must go red |
|---|---|---|---|
| X1 | Delete `dataset_marker` from one `documents[N]` | leaf literal 1→0 | `..._INCOMPLETE` naming that exact index |
| X2 | Sibling's `None` → `"## 2"` (D8) | `'"dataset_marker": None,'` 1→0 | `MEASURED_MOVERS`'s measured set, and **only** it |
| X3 | `lstrip().startswith(marker)` → `marker in text` | call 1→0 | the mid-sentence negative — **the one a weaker lock survives**, because every positive fixture has it at line start |
| X4 | In the fold, `dataset_marker(index)` → `dataset_marker(0)` | index read 1→0 | the document-1-only fixture; `tests/seal/` must survive |
| X5 | `cmd_apply` passes `None` instead of the seed from `approved` | `"boundTo"` read 1→0 | the `PLAN_STALE` agreement test; repeat for `_materialize_plan_gate` |

**An anchor that matched is not a mutation that ran.** Confirm the count at both
endpoints; `sd -s` exits 0 having changed nothing; `git diff --stat` proves
nothing for an untracked file and is masked by an adjacent real edit. Clear
`__pycache__` — a same-size edit reuses a stale `.pyc`. Never mutate the shipped
engine; plant into a scratch copy. **A surviving mutation has two explanations**
— measure which before strengthening anything.

## Threat Matrix

| Row | Applicable | Behaviour / RED test |
|---|---|---|
| Path traversal via `--revision` | **Yes — inherited, and B must not widen it** | `revision_source` is the single path join, already reached by eight commands. B adds **no second joining site** and returns only a boolean. RED: the detector is asserted to call `revision_source`, not to build a path |
| Host-supplied text matched against file bytes (**new**) | **Yes** | A literal, not a regex (D1): no compilation, no backtracking, no host-controlled matcher. RED: a marker containing regex metacharacters matches literally and nothing else |
| Reading a document at `plan` time | **Yes** | `plan` opens a document only under an explicit `--revision`; on a bare clone it opens nothing. RED: `plan` with no flag on a target with no documents root exits 0 with byte-identical stdout |
| Subprocess invocation | Yes (inherited) | Seal and pair cases; `shell=False`, list argv, unchanged. No new entry point |
| Routing / new subcommand | **N/A** | `COMMANDS` untouched; one existing flag reaches one more command |
| Data integrity of persisted records | **Yes** | The Products table: old `plan.json` files keep applying; no record shape changes |
| Executable-file classification, VCS/PR automation, Network | N/A | None reached |

## Migration / Rollout

No data migration — by the Products table nothing of the changed shape exists on
any disk, and pre-existing approved plans keep applying by D3's `None` fallback.

**Rollback**, per unit then per slice, tip-first. `tests/seal/` is untouched by
construction, so the pre-change seal is the post-revert seal. Restoring
`tests/experiments_seal/digests.json` is **part of** reverting B2, not an
afterthought: a moved golden left behind survives the rollback silently and
becomes the new baseline. Reverting B2 alone leaves B1 shipped and dormant —
safe, because every profile then declares `None` and no document is opened.
**Removing the marker from `impl_profile.py` alone is not a rollback**: the key
is required, and its absence refuses the profile.

## Size — price the proof

| Slice | Delivers | Gate at the end | Estimate |
|---|---|---|---:|
| **B1** | The leaf + detector + `build_plan`'s third parameter through all three call sites + `boundTo` + `cmd_verify`'s reorder + F5's four literals + one parser name; the sibling's and the fixture's `None`s | 28 sibling digests identical; `experiments_seal` unmoved; the agreement test green; X1–X5 (X3/X4 on unit fixtures) | 340–520 |
| **B2** | The shipped declaration; D9's two revisions and four cases; `LockCDeclaredMarkerTests`; `SKILL.md` | `missingDirs` holds a `Data/` in a captured case, both controls captured, **zero existing cases moved** | 170–280 |
| | | | **510–800** |

Above the proposal's 450–750, deliberately: the proposal did not price D6's
derived lock, D7's lock, or the two-document fixture D2 forces. Every estimate
this session came in over except the one that priced its proof, so read this as
the **floor**. Apply reports measured lines and does not repeat this number.

Against `review_budget_lines: 1400`: both fit; **neither fits the 400-line
default**, so neither may merge unstacked.

```text
Decision needed before apply: Yes
Chained PRs recommended: Yes
400-line budget risk: High
```

## Predictions This Design Makes — Claims Apply Must Measure, Not Repeat

- [ ] `--revision` reaches **nine** commands through **two** registrations; after
      B1 it reaches ten through two (M1).
- [ ] Moving three statements in `cmd_verify` (D5) is observationally inert: 28
      sibling digests and 20 `experiments_seal` digests all identical.
- [ ] `git diff --exit-code tests/seal/` exits 0 after **each** slice.
- [ ] B1 moves **zero** digests in either corpus.
- [ ] B2 moves `__corpus_fingerprint__` and adds four entries; **no existing
      case digest moves**.
- [ ] `reachable_refusal_codes()`'s roster is unchanged.
- [ ] `L1_EXPECTED_COUNT` is unchanged — no new engine prose spells `proposal`.
- [ ] `skipped=6` does not move; no `skipTest` is added anywhere.
- [ ] D8's mutation moves `verify-b` (and possibly `verify-t`) and nothing else.
      **If it moves nothing, the detector is not wired and B1 has proven
      nothing.**
- [ ] `LockADiscoveryTests` stays green with the widened `values_text`.
- [ ] The eleven flat `_core/implementation/*.py` files still contain zero
      occurrences of the seven owned words (M3).

**A design prediction about tooling is a claim, not a fact.** Three inherited
counts have failed in this project, and M1/M5 correct two more. Every box above
is measured at apply and reported with its measurement, never ticked by
repetition.

## Open Questions

- [x] What the leaf holds → **a literal line-leading marker, required, nullable**
      (D1).
- [x] How many parser registrations → **one, on `plan`**; `apply` and
      `materialize` inherit the seed from the approved plan (D3). This
      contradicts the brief's three and is argued, not assumed.
- [x] Which documents are consulted → **all declared, or-folded** (D2).
- [x] How `cmd_verify` gets a revision in time → **three statements move down**
      (D5).
- [x] Which `experiments_seal` cases move → **none of the existing twenty** (D9).
- [ ] **The other 22 bare product literals** (`Notebooks`/`Results`/`Models`,
      M5) are a named follow-up. D6's lock is one line away from covering them;
      widening it here would be scope B did not price.
- [ ] **An empty `Data/` satisfies the demand** (ruling 4), matching the other
      three categories. Recorded so "it passed with an empty folder" is a
      decision, not a later surprise.
- [ ] **No `OBJECTIVE_FLOW` edit.** Ruling 5 holds through the existing
      mechanism: `missing_dirs` → `structure_ok` → `structure.status: "drift"`,
      which is what an agent reads to decide `standing` is behind. **Apply must
      invent no new gate for this category.**

## Citations Checked

Located **by name, in the source, this phase, never by line and never
inherited**: `PRODUCT_DIRS`, `PRODUCT_DATA`, `PRODUCT_NOTEBOOKS`, `DATA_EXT`,
`NOTEBOOK_EXT`, `MODEL_EXT`, `RESULT_EXT`, `classify`, `expected_dirs`,
`in_place`, `dir_exists_after`, `detect_product_dir`, `build_plan`, `cmd_plan`,
`cmd_apply`, `_materialize_plan_gate`, `cmd_materialize`, `cmd_verify`,
`structure_ok`, `scaffold_gaps`, `present_files`, `resolve_benchmark_declaration`,
`revision_source`, `proposals_root`, `document_revision_names`,
`discover_document_revision`, `revision_discovery`, `latest_revision`,
`document_vocabulary`, `_bound_to`, `DOCUMENTS`, `COMMANDS`, `main`,
`_REQUIRED_NESTED`, `_REQUIRED_PRESENCE`, `_DOCUMENT_VOCABULARY_LEAVES`,
`_NOTATION_KEYS_REQUIRED`, `_resolve`, `ImplementationProfileError`,
`IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE`, `MUTATIONS`, `MEASURED_MOVERS`,
`_write_scratch_profile`, `_build_env_with_profile_override`,
`discover_profiles`, `profile_values_text`, `_engine_files`, `ENGINE_DIR`,
`CORE`, `CoreNamesNoDomainTests`, `LockADiscoveryTests`,
`LockBEngineNeutralityTests`, `CORPUS_FINGERPRINT_SOURCE`,
`_write_common_package`, `_build_documents`, `PLAN_STALE`, `PLAN_MISMATCH`.

**Inherited claims re-measured this phase; three corrected:**

1. *"`--revision` is registered for exactly eight commands."* **Corrected** —
   eight through one shared set, plus `walk` through its own. Nine commands, two
   registrations (M1).
2. *"Three parser registrations."* **Argued down to one** (D3), on `settle`'s own
   recorded reasoning about a flag a command cannot honour.
3. *"Three bare `Data` literals remain."* **Confirmed as three sites, and
   decomposed: four occurrences.** The rest of the class is 22 further lines for
   the other three categories (M5).
4. *`CoreNamesNoDomainTests` is non-recursive and substring-based* — **confirmed
   by measurement**: the eleven flat core files contain zero occurrences of all
   seven owned words (M3).
5. *A guard over the word `dataset`* — **would be red at HEAD**; `classify`
   already returns it as a reason string (M4).

No test suite was run, per this change's brief.


---

## Correction after verify (W1): three registrations, not one

D3's table says *"One registration (the eight-name set becomes nine; ten commands
carry the flag)"*. **The count of commands is right and the mechanism is wrong.**

Measured at HEAD: `add_argument("--revision"` appears at **three** sites. The
eight-name set (`verify`, `admit`, `handoff`, `probe`, `position`, `gate`,
`offer`, `close`) is one; `walk` has always had its own; and B gave **`plan` a
third of its own** rather than widening the set. Ten commands carry the flag,
through three registrations.

D3's *ruling* stands untouched and is what mattered: the flag lands on `plan`
alone, and `cmd_apply` and `_materialize_plan_gate` take the seed from the
approved plan's own `boundTo` key, so the three `build_plan` call sites agree by
construction. Only the sentence describing how the registration was spelled was
wrong.

Worth recording because of the pattern, not the line. This is the **fifth**
inherited count in this project that did not survive being checked:
`_POSITION_HEADER_RE` never existed; the engine's subject words were 89/30/28 and
not 88/23/20; Slice A's tasks were 33 and not 40; `--revision` reached nine
commands and not eight; and this change's own tasks are **37**, not the 30 its
apply report stated. Every one was caught by counting rather than by reading.
