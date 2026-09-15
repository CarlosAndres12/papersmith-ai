# Design: The Domain Crosses the Seam

> **Size note.** Over the 800-word budget, deliberately, for the reason Cut 1's
> `design.md` gave and the brief repeats: *mechanics concrete enough that apply invents
> nothing*. Fifteen profile leaves, forty schema sites, four locks and a per-field landing
> order do not compress into 800 words without becoming a design apply has to re-derive.

## Technical Approach

Every domain-carrying literal in `_core/implementation/engine/implementation_engine.py`
becomes a read off `PROFILE`, supplied by `proposal-implementation/impl_profile.py` as
**the same bytes it is today**. A profile supplying the same literal composes the same
output, so the instrument that judges this cut — `tests/seal/`, 28 digests — must stay
byte-identical. **Any movement is a defect, never a new golden.**

Two runs, never conflated:

| Run | Question | Required answer |
|---|---|---|
| **No-delta run** | did landing this field change any output? | all 28 digests byte-identical, after **each** field |
| **Mutation run** | does the field actually reach the output? | a named digest **moves**, under a real reverted file edit |

Cut 1 used the seal for both and R1's predicted movers turned out not to move. Here they
are separate procedures with separate pass conditions.

## Measurements that change the proposal's shape

Five findings from reading the source in this phase. Each corrects the proposal; none
re-opens B2.

### M1 — the `names` lock reads the engine's whole text, so `CITATION_RE` must move too

`CITATION_RE` is a module-level compiled pattern spelling `Ecuaciones?` and `Ecs?`. It is
read by `finding_impact`, which `cmd_handoff` and `cmd_verify` both call. The proposal's
out-of-scope list names `DISPLAY_BLOCK_RE` and `TAG_RE` (both LaTeX-structural, neither
spells a domain word — confirmed by reading them, which is why the `compose`/M1 boundary
holds). It does **not** name `CITATION_RE`, and an honest `names` list keeps the lock red
while that regex stands.

**`findings.citation_pattern` is added as an eleventh field.** It has a named reader
(`finding_impact`), and a mutation that moves a digest (a pattern matching nothing drops
`citedElsewhere` and can flip `impact.class`). It earns its place by the same rule as the
other ten.

### M2 — the subject vocabulary is bilingual and has three grammatical forms, not two

The proposal's `vocabulary.subject_singular`/`_plural` covers the Spanish deferral prose.
Measured, the engine also spells the subject in **English executable strings**
(`ARMS_UNDECLARED_CONSEQUENCE`: *"an arm reimplements an equation instead of calling it"*;
`cmd_admit`'s verdict reason: *"cites equations absent from the revision"*) and as an
**English mass noun** (`_wiring_first_publication`: *"declares mathematics no arm
reaches"*), plus a Spanish mass noun (`cmd_handoff`'s `remedy-text-missing` reason: *"La
redacción de la matemática es la decisión"*). Seven `vocabulary` leaves, not three. The
count is derived from the sites, not chosen.

### M3 — `documents.directory` cannot join `_REQUIRED_NESTED`

`_REQUIRED_NESTED` is walked twice: once for presence, once by the `…_UNSAFE_PATH` check,
which requires `value.exists()`. `proposals_root()`'s own readers already tolerate an
absent root — `revision_discovery` returns `empty` when `not root.is_dir()`, and
`revision_source` returns `None` when the file is absent. Putting `documents.directory` in
the must-exist tier would refuse **at import** on any clone with no `proposals/`, turning
five reported absences into one fatal refusal: a behavioural delta, and the seal's
`*-e0` cases are exactly the absent-document path.

**`documents.directory` gets its own validation tier**: required, absolute, existence
**not** required. `_REQUIRED_NESTED` keeps its two path-and-exists pairs.

### M4 — the kit agreement is six sites, not two

| Kit file | Site | Half of the agreement |
|---|---|---|
| `assets/kit/src/module.py` | `__provenance__`'s `"sections"` / `"equations"` keys | coarse (shared) + `claim_key` |
| `assets/kit/src/module.py` | the rules docstring naming both keys | prose, same pair |
| `assets/kit/src_benchmark/__init__.py` | the `arms` **commented example** `{"baseline": {"sections": ["3.1"]}}` | the join's other half |
| `assets/kit/tests/findings.py` | the commented `"equations"` / `"remedy_equations"` keys | `locus_key` + `remedy_locus_key` |
| `assets/kit/tests/test_audit.py` | **executable** `finding["remedy_equations"]` | `remedy_locus_key` |
| `assets/kit/nb/verification.ipynb` | **executable** `p['equations']` | `claim_key` |

The `arms` half ships as a **comment**, not as data (`"arms": {}` is the live value) — so
the lock reads file text, not a parsed literal. Two of the six are executable code that
runs inside a target's own interpreter, which is the sharpest reason the agreement needs a
test: a divergence there fails in somebody else's repository, not in this suite.

### M5 — the derived-denylist layer (TS C-3) cannot land at Cut 2

`buildDenylist` in `tests/proposal-deliberation-domain-profile-lock.test.mjs` marks a word
as one domain's subject when **no other profile's north uses it**. With one implementation
profile on disk, the "others" set is empty and every word ≥5 chars in `OBJECTIVE_FLOW`
becomes a denylist entry — including `repository`, `mathematics`, `benchmark`, `revision`.
That is not a stricter lock; it is an unsatisfiable one.

**Deferred, with the reason recorded**, to the day a second implementation profile exists.
Landing it now as a `skipTest` would move the pinned `OK (skipped=6)` baseline, which this
cut is not allowed to move. The **explicit `names` lock** — the one the proposal actually
promised — lands in full.

### M6 — B2 gains a structural argument the ruling did not have

Every domain-word-valued profile leaf enters the lock's scanned value set: the engine may
not spell it. `sections` is spelled by the engine at ten sites and **must be**, because it
is the join's shared word. So a profile-supplied coarse key would be a value the lock
requires absent from a file that requires it present — the lock and the join in direct
contradiction. Option A is not merely preferable; it is the only option under which the
neutrality lock can be green and the join can be sound at the same time. Recorded as
corroboration of the ruling, not as a re-opening of it.

## Architecture Decisions

### D1 — The field set: fifteen leaves, each with its reader and its digest

Located by name at HEAD `ff566fa`. **Digest column is a prediction apply must measure
before asserting** (see "Predictions", below).

| Leaf | Value today | Read by (symbol) | Mutation | Predicted mover |
|---|---|---|---|---|
| `provenance.claim_key` | `"equations"` | `unreached_mathematics`, `benchmark_unfaithfulness`, `wiring_proposal`, `cmd_verify`'s module-row builder; the kit lock | → `"claims"` | `verify-a`, `verify-b`, `verify-t` |
| `provenance.authored_init_sentence` | the two-line `"Each module declares the sections and equations it implements in\n`__provenance__`…"` | `authored_package_init` | alter one word | `materialize` |
| `findings.locus_key` | `"equations"` | `remedy_compatibility`, `cmd_admit`'s verdict loop, `cmd_handoff`'s item builder, `cmd_verify`'s audit block | → `"loci"` | `admit-e1`, `handoff-e1`, `verify-a` |
| `findings.remedy_locus_key` | `"remedy_equations"` | `finding_impact`, `remedy_compatibility`, `cmd_admit`, `cmd_handoff` (incl. `selectedEntryId`), `cmd_verify`'s audit block | → `"remedy_loci"` | `handoff-e1`, `admit-e1`, `verify-a` |
| `findings.notation_keys` | `{"locus": "equations", "remedyLocus": "remedyEquations", "unknown": "unknownEquations"}` | `finding_impact`'s return, `cmd_handoff`'s item, `remedy_compatibility`'s return, `cmd_verify`'s audit block | rename one wire key | `handoff-e1`, `verify-a` |
| `findings.citation_pattern` | `CITATION_RE`'s pattern string (M1) | `finding_impact` | pattern matching nothing | `handoff-e1` |
| `vocabulary.subject_singular` | `"equation"` | `ARMS_UNDECLARED_CONSEQUENCE` | → `"claim"` | `verify-*` where `arms` is empty |
| `vocabulary.subject_plural` | `"equations"` | `cmd_admit`'s verdict reason | → `"claims"` | `admit-e1` |
| `vocabulary.subject_singular_es` | `"ecuación"` | `cmd_handoff`'s `remedy-locus-missing` and `structural-reach` reasons | → `"afirmación"` | `handoff-e1` |
| `vocabulary.subject_plural_es` | `"ecuaciones"` | `cmd_handoff`'s `structural-reach` reason and `ECUACIONES A TOCAR:` prompt line | → `"afirmaciones"` | `handoff-e1` |
| `vocabulary.subject_collective` | `"mathematics"` | `_wiring_first_publication` | → `"claims"` | `probe` |
| `vocabulary.subject_collective_es` | `"matemática"` | `cmd_handoff`'s `remedy-text-missing` reason | → `"afirmación"` | `handoff-e1` |
| `vocabulary.artifact_noun` | `"formulation"` | `authored_package_init`'s `"{name} formulation"` | → `"method"` | `materialize` |
| `vocabulary.names` | the declared word list (D5) | **both locks, nothing else** | drop a word that is in the engine | lock goes red |
| `documents.directory` | `FORGE_ROOT / "proposals"` | `proposals_root()` → `revision_source`, `revision_discovery`, and the 5 refusals | → a sibling directory | `admit-e0`, `handoff-e0`, and the other three refusal cases |
| `documents.label` | `"proposal"` | `ARMS_UNDECLARED_CONSEQUENCE` (*"the sections of a proposal"*); the swept docstrings | → `"document"` | `verify-*` where `arms` is empty |

**`provenance.drift_unit_key` does not exist.** It is the coarse key `sections`, which the
operator's B2 ruling keeps shared. Supplying it is the drift reason 2 forbids, and M6 shows
it would also deadlock the lock. **Four further §B1 fields stay excluded**, reasons carried
forward unchanged from the proposal: `provenance.revision_key` (word is general; shape is
Cut 3), `document_reader.drift_units` (no Cut-2 reader; `revision_sections` reads document
structure), `documents.marker` (F6 — a fifth spelling cannot pull the other four), and
`cli_invocation` (the profile supplies the path; the engine composes). **Do not restore
one.**

### D2 — The 40 schema sites: two consumers, two designs

**Which key is diffed is the whole distinction.** Measured: `sections` participates in set
intersection at `changed_sections`' consumers (`module["stale"]` → `drift_detail`'s
`touchedSections`, and the `arms` join in `cmd_verify`'s benchmark block and
`unreached_mathematics`). `equations` participates in **no** comparison anywhere — it is
carried into output and never crossed. That is what makes the fine key safe to profile and
the coarse key not.

**Provenance side (5 sites) — key is both a read and a wire key.**

| # | Site | Shape |
|---|---|---|
| P1 | `unreached_mathematics` | `module.get(<claim_key>, [])` → output under `<claim_key>` |
| P2 | `benchmark_unfaithfulness`'s module row | `prov.get(<claim_key>, [])` |
| P3 | `wiring_proposal`'s module row | `provenance.get(<claim_key>, [])` |
| P4 | `cmd_verify`'s module row | `prov.get(<claim_key>, [])` → surfaces in `fidelity.modules` |
| P5 | `authored_package_init` | **writer**, D3 |

Rule: the read key and the emitted key are **the same leaf**. Splitting them would let a
target's `__provenance__` be read under one word and reported under another — the exact
silent mismatch this cut exists to remove.

**Findings side (the rest) — read keys and wire keys are separate leaves.**

| # | Site | Leaf |
|---|---|---|
| F1 | `remedy_compatibility`'s `for field in (…)` loop | `locus_key`, `remedy_locus_key` |
| F2 | `remedy_compatibility`'s early-return and final dict | `notation_keys["unknown"]` |
| F3 | `finding_impact`'s `finding.get(…)` | `remedy_locus_key` |
| F4 | `finding_impact`'s returned dict | `notation_keys["locus"]` |
| F5 | `cmd_handoff`'s item builder (two keys) | `locus_key`, `remedy_locus_key` → `notation_keys["locus"]`, `["remedyLocus"]` |
| F6 | `cmd_handoff`'s inline-branch guard and `selectedEntryId` | `remedy_locus_key` |
| F7 | `cmd_handoff`'s `remedy-locus-missing` guard and prompt line | `remedy_locus_key` |
| F8 | `cmd_admit`'s `for field in (…)` verdict loop | `locus_key`, `remedy_locus_key` |
| F9 | `cmd_verify`'s `audit.findings` row (two keys) | same pair, wire side |

Why separate here and joined on the provenance side: the two documents have **different
producers**. `__provenance__` is authored by the engine's own kit template into a module;
`tests/findings.py` is authored by a person against the kit's findings template. They can
legitimately diverge in a future domain, and forcing one leaf would make that
undiscoverable. The `notation_keys` mapping exists because the wire spelling is camelCase
(`remedyEquations`, `unknownEquations`) while the read spelling is snake_case — one leaf
cannot serve both without the engine transliterating, which is a naming convention the
engine must not hold.

### D3 — The writer: one verbatim sentence, not a composition

**Choice.** `provenance.authored_init_sentence` carries the whole two-line sentence
verbatim. `authored_package_init` interpolates it, and `vocabulary.artifact_noun` supplies
the `"{name} formulation"` noun. Bytes identical, so `materialize`'s digest does not move.

| Option | Why not |
|---|---|
| Compose from `claim_key` + the shared coarse key + a template | The engine would hold the sentence's **English grammar** (*"declares the X and Y it implements in"*) and the ordering of the two keys. A domain writing in another language gets a sentence it cannot use, and the engine still spells the connective prose. It also triples the mutation surface for one output |
| Leave the sentence in the engine | The `names` lock reddens on `equations`; the whole point of item 6 |
| Profile-supply the entire `__init__.py` body | Hands `__all__ = []` and the docstring shape — engine structure, not domain — to the host |

**The sentence names the shared coarse key**, and the profile therefore spells `sections` in
prose. That is prose, not the join key, and it is bound by assertion: the kit lock asserts
both `PROFILE["provenance"]["claim_key"]` and the literal coarse key `"sections"` appear in
`authored_init_sentence`. A sentence that stops naming what the schema requires is a
divergence with no other detector.

### D4 — The kit agreement lock

Six assertions over the M4 table, in `tests/test_implementation_domain_lock.py`. **No kit
file is edited.** `verify`'s `kitSource` compares a materialized target file byte-for-byte
against its kit template; editing a template reclassifies files in repositories this change
never opened. (Cut 1 measured `kitSource` as already `null` for the seal fixtures, so the
seal would not even report the damage — a claim apply should re-confirm before relying on
it either way.)

The lock asserts, by reading file text:

1. `module.py`'s `__provenance__` literal declares exactly `{"revision", "sections",
   claim_key, "invariants"}` — `claim_key` present **and** the shared `"sections"` present.
2. `module.py`'s rules docstring names both.
3. `src_benchmark/__init__.py`'s `arms` example spells `"sections"` — the join's other
   half, and the one assertion that would have caught a drifted coarse key.
4. `tests/findings.py`'s commented keys equal `locus_key` and `remedy_locus_key`.
5. `tests/test_audit.py`'s executable subscript equals `remedy_locus_key`.
6. `nb/verification.ipynb`'s executable subscript equals `claim_key`.

Vacuity guard, mirroring the TS lock's own: each assertion first asserts the extracted set
is **non-empty**, so a moved file or a changed comment style fails loudly instead of
passing over nothing.

### D5 — The two neutrality locks

Both in `tests/test_implementation_domain_lock.py`, mirroring
`proposal-deliberation-domain-profile-lock.test.mjs` structurally.

**Lock A — profile discovery, by glob.** `discover_profiles()` walks
`.claude/skills/*/impl_profile.py`, skipping `_core`, and returns each profile's declared
leaves. **It hardcodes no pair.** A third skill is held to the rule the day its
`impl_profile.py` appears, without this file being edited — which is the TS lock's own
stated reason for `discoverProfiles`. Per profile it asserts: at least one profile found;
`names` non-empty (or every check below is vacuous); no declared leaf is blank; every
`names` word appears somewhere in that profile's own source (*"a name no profile value
contains is not this domain naming itself"*).

**Lock B — the engine spells no declared name.** Scans **every** `*.py` under
`_core/implementation/engine/` — whole text, comments and docstrings included, which is why
the 88 comment lines are load-bearing and not cosmetic: an unswept docstring keeps Lock B
red exactly as an unswept string does. Word-boundary, case-insensitive.

`names` is declared **from the measurement's own §A token list**, never from what happens
to pass: `equation`, `equations`, `ecuación`, `ecuaciones`, `mathematics`, `matemática`,
`formulation`. The lock's own failure report is the worklist — including for the four
domain identifiers, which apply renames from what Lock B names rather than from a list
written here that would be stale on arrival. `unreached_mathematics` is the one located by
name in this phase; the wire keys it produces (`unreachedModules`, `armsReached`) carry no
domain word and **do not change**, so no digest moves with the rename.

**`PINNED_RESIDUE`, carried over from the TS precedent.** A word that is both a declared
name and deeply pre-existing engine vocabulary is pinned by **exact occurrence count and
sorted file list**, so it can only shrink deliberately, never be exempted into silence.
Here that is `proposal` — and that pin is D6.

### D6 — The campaign-proposal exclusion, as a test

Three layers, because the pin alone is not enough and the list alone is not enough.

| Layer | Assertion | Catches |
|---|---|---|
| **L1 — the residue pin** | `\bproposal\b` (case-insensitive) occurrence count and sorted file list across `engine/` equal a **measured** baseline | any sweep, including one nobody declared. A rename campaign drops the count and the test is red before the commit |
| **L2 — the named exclusion list** | each of `proposalDigest`, `GATE_PROPOSAL_*`, `_proposal_digest`, `_verify_gate_proposal`, `_gate_proposal_question`, `_verify_optional_election`, `cmd_propose`, `_authorization_binding`, `_verify_gate_authorization`, `_campaign_identity`, `_load_remote_execution_*` still resolves in the engine, spelled exactly | a targeted rename that leaves the total count unchanged (rename one, add one) — which L1 alone cannot see |
| **L3 — the binding invariant** | `"proposalDigest" in impl._AUTHORIZATION_BINDING_KEYS` | the consequence, stated where it lives: every previously minted gate authorization in every target's committed `.implementation/position.jsonl` validates against this exact key |

L1's baseline number is **measured at apply, not written here**. A count in this document
would be a claim apply repeats; a count apply measures is evidence. `rg -c` on this engine
reports line counts, not occurrence counts, and the two diverge on multi-match lines — the
TS pin learned this and pins occurrences.

**Third-sense residue, recorded.** `wiring_proposal` and `_wiring_first_publication` spell
`proposal` in a third sense — a *draft suggestion*, neither the mathematical document nor
the campaign launch. They are in neither the 78 nor the exclusion list. L1 covers them; L2
does not. Apply must not "fix" them into `documents.label` reads: they are not the
document.

### D7 — Landing order, and the rollback boundary of each step

**The rule the proposal's mitigation asks for, stated mechanically: one field, one engine
edit, one seal run. Never batch.** The seal is re-run after every step and must be
byte-identical; any movement attributes to exactly the one field just landed, which is the
entire reason for not batching.

| Step | Work | Seal | Rollback boundary |
|---|---|---|---|
| S0 | Baseline: full Python discover, `npm test`, `sha256(tests/seal/digests.json)`, and the L1 occurrence count. Paste all | 28 green | — |
| S1 | **RED first**: `tests/test_implementation_profile.py` grows one `…_INCOMPLETE` case per new leaf, naming the **leaf** (`findings.locus_key`, not `findings`) | n/a, red by design | — |
| S2 | Resolver: `_REQUIRED_NESTED` grows the non-path leaves; `documents.directory` gets its own absolute-but-need-not-exist tier (M3). Declare all fifteen leaves in `impl_profile.py`. Engine untouched | 28 identical | revert two files |
| S3 | `provenance.claim_key` (P1–P4) | 28 identical | revert S3 |
| S4 | `provenance.authored_init_sentence` + `vocabulary.artifact_noun` (P5, D3) — one step because one output | 28 identical | revert S4 |
| S5 | `findings.locus_key` | 28 identical | revert S5 |
| S6 | `findings.remedy_locus_key` | 28 identical | revert S6 |
| S7 | `findings.notation_keys` | 28 identical | revert S7 |
| S8 | `findings.citation_pattern` (M1) | 28 identical | revert S8 |
| S9 | `documents.directory` + `documents.label` | 28 identical | revert S9 |
| S10 | `vocabulary.*` subject leaves, one per sub-step | 28 identical after each | revert that sub-step |
| S11 | The four identifier renames, driven by Lock B's failure report | 28 identical | revert S11 |
| S12 | The 88 comment/docstring lines | 28 identical (no executable text touched — **assert, do not assume**) | revert S12 |
| S13 | Lock A, Lock B, kit lock (D4), L1/L2/L3 (D6). Declare `names`. Re-assert `reachable_refusal_codes()`'s pin | 28 identical | revert S13 |
| S14 | Proof: per-field mutation runs (D8), anchor counts both directions, `git diff --exit-code tests/seal/` | — | — |

**Ordering rationale.** Provenance before findings before documents before vocabulary,
because their predicted movers are progressively less disjoint: a `verify-*`-only field
landed first isolates cleanly, and by the time several fields share `handoff-e1` the
earlier ones are already proven identical.

**Rollback.** Each S-step is independently revertible; the change as a whole is one revert.
`tests/seal/` is untouched by construction, so the pre-change seal is the post-revert seal.
No migration, no target ledger written, no minted authorization touched.

**The separable slice, and the proposal's apparent contradiction resolved.** The split is
`S0–S9 + D4/D6 locks` / `S10–S13`. PR 1 carries the **kit agreement lock, L1/L2/L3 and Lock
A** — none of which needs the comment sweep. PR 2 carries the vocabulary, the identifier
renames, the comment sweep and **Lock B**, which is the one lock that cannot land before
S12. That is what *"schema + locks / vocabulary + comments + locks, never locks-alone"*
means concretely: each PR lands the locks it can actually keep green.

### D8 — Mutation proof per field

**A field that cannot be mutation-proven must not exist.** Each of the fifteen leaves is
proven **both ways**, per the proposal's success criterion:

1. **Removal** — delete the leaf from `impl_profile.py`; the resolver raises
   `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming **that leaf**, not its section.
   In-process, fresh `importlib` load with a controlled `os.environ`.
2. **Change** — a real, reverted edit to `impl_profile.py`, then a seal run; the digest in
   D1's table **moves**.

**Never a monkeypatch for (2).** Every seal case is a subprocess; patching
`impl_domain_profile.PROFILE` or an engine attribute has **zero effect** on one. Cut 1
recorded this and it holds unchanged here.

**Anchor discipline, both directions.** Before each mutation, read `impl_profile.py` and
assert the anchor count moved `1 → 0` for the old spelling and `0 → 1` for the new; after
the revert, assert `1 / 0` again. An anchor that matched is not a mutation that ran, and
`sd -s` exits 0 having changed nothing.

**Measure the property before strengthening a test.** If a predicted digest does not move,
there are two explanations — a weak instrument or a wrong claim about what the field
reaches. Apply measures which cases move *before* writing the assertion, and **records a
zero-mover explicitly** rather than hunting for a test that would have moved it. Cut 1's R1
is the precedent: the predicted `kitSource` carriers did not move, and saying so was the
correct outcome.

## Data Flow

```
IMPLEMENTATION_DOMAIN_PROFILE ──(setdefault, launcher)──→ impl_profile.py
                                        │
                    impl_domain_profile.py  (15 leaves, fail closed at import)
                                        │
            ┌───────────────────────────┼────────────────────────────┐
    provenance.claim_key        findings.{locus,remedy_locus,      documents.directory
            │                    notation_keys,citation_pattern}       │
            │                            │                    proposals_root()
   read __provenance__            read tests/findings.py          │      │
            │                            │              revision_source  5 refusals
            └──── report-only ───────────┴──→ admit / handoff / verify ──┘
                                                          │
   "sections" (SHARED, never profiled) ──→ changed_sections ∩ arms ──→ the join
                                                          │
                        tests/seal/ ──→ 28 digests ──→ must be byte-identical
```

## File Changes

| File | Action | Description |
|---|---|---|
| `.claude/skills/_core/implementation/engine/implementation_engine.py` | Modify | the 167 lines: 40 schema sites, 25 strings, 4 identifiers, 10 paths, 88 comments |
| `.claude/skills/_core/implementation/impl_domain_profile.py` | Modify | new nested leaves validated **by leaf**; `documents.directory`'s own tier (M3) |
| `.claude/skills/proposal-implementation/impl_profile.py` | Modify | the fifteen leaves of D1 |
| `tests/test_implementation_profile.py` | Modify | one removal + one change mutation per leaf |
| `tests/test_implementation_domain_lock.py` | **New** | Lock A, Lock B, the kit agreement (D4), L1/L2/L3 (D6) |
| `.claude/skills/proposal-implementation/assets/kit/**` | **Unchanged** | asserted against, never edited (D4) |
| `tests/seal/*` | **Unchanged** | `git diff --exit-code tests/seal/` must exit 0 |
| `tests/proposal-deliberation-domain-profile-lock.test.mjs` | **Unchanged** | the sister skill is read for structure, never written |

## Interfaces / Contracts

```python
PROFILE = {
    "kit": {"root": _SKILL},                                    # Cut 1, unchanged
    "cli": {"path": _SKILL / "scripts" / "implementation_cli.py"},  # Cut 1, unchanged
    "objective": OBJECTIVE_FLOW,                                # Cut 1, unchanged
    "provenance": {
        "claim_key": "equations",
        "authored_init_sentence": (
            "Each module declares the sections and equations it implements in\n"
            "`__provenance__`, and every invariant listed there has a matching\n"
            "test under tests/.\n"),
    },
    "findings": {
        "locus_key": "equations",
        "remedy_locus_key": "remedy_equations",
        "notation_keys": {"locus": "equations",
                          "remedyLocus": "remedyEquations",
                          "unknown": "unknownEquations"},
        "citation_pattern": r"Ecs?\.?\s*\(?(\d+)\)?|Eq\.?\s*\(?(\d+)\)?|Ecuaciones?\s*\((\d+)\)",
    },
    "vocabulary": {
        "subject_singular": "equation",      "subject_plural": "equations",
        "subject_singular_es": "ecuación",   "subject_plural_es": "ecuaciones",
        "subject_collective": "mathematics", "subject_collective_es": "matemática",
        "artifact_noun": "formulation",
        "names": ["equation", "equations", "ecuación", "ecuaciones",
                  "mathematics", "matemática", "formulation"],
    },
    "documents": {                       # SINGLE-ENTRY SHAPE ONLY — plural is Cut 3
        "directory": FORGE_ROOT / "proposals",
        "label": "proposal",
    },
}
```

`documents` is a **scalar-shaped section, deliberately**. Making it a list is Cut 3's whole
job, together with `revisionSha256`'s scalar→pair at 24 sites. Nothing here may take that.

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | 15 `…_INCOMPLETE` refusals | fresh `importlib` load, controlled `os.environ`; each names its **leaf** |
| Unit | `documents.directory`'s own tier | a non-existent directory must **import fine**; a relative one must refuse (M3) |
| Unit | Lock A | glob discovery; vacuity guards; names-appear-in-own-source |
| Unit | Lock B | whole-text scan of `engine/*.py`; `PINNED_RESIDUE` = `{proposal}` |
| Unit | kit agreement | six assertions, each with a non-empty extraction guard (D4) |
| Unit | exclusion | L1 pin, L2 named list, L3 binding-key membership (D6) |
| Unit | refusal pin | `reachable_refusal_codes()` re-asserted; moved only if a refusal was genuinely added, and the new number recorded |
| Integration | the seal | 28 byte-identical **after each S-step**, not only at the end |
| Mutation | per leaf | real reverted edit + anchor counts both directions; predicted digest moves |
| Mutation | Lock B honesty | plant a declared `names` word in `engine/`; the lock must **redden**; revert; green |
| Mutation | kit lock honesty | change `module.py`'s `"equations"` key in a scratch copy; the lock must redden |
| Non-interference | sister skill | `npm test` **595/595** and Python `OK (skipped=6)` pasted before and after. `proposal-deliberation/` and `_core/deliberation/` are **not written to** |

**Baseline semantics, stated because they are asymmetric.** `npm test` must read **595/595
exactly** — a moved number there is the sister-skill bar failing. Python's `Ran 2849`
**will grow** (new tests are the point); what must not move is `OK` and `skipped=6`. A new
skip is a baseline delta and is refused (M5's reason for not landing C-3).

## Threat Matrix

| Row | Applicable | Behaviour / RED test |
|---|---|---|
| Subprocess invocation | **Yes (inherited)** | the seal's 28 cases; `shell=False`, list argv, unchanged |
| Environment-variable routing | **Yes** | `IMPLEMENTATION_DOMAIN_PROFILE` (unchanged), `IMPLEMENTATION_PROPOSALS` (now reached through `documents.directory`); the override must still win, RED per refusal |
| Filesystem writes | **Yes (bounded)** | `authored_package_init` writes profile-supplied prose into a target's `src/<Package>/__init__.py`. Bounded by D3: one sentence, not the file |
| Path traversal via profile | **Yes** | `documents.directory` must be absolute; existence **not** required (M3), because absence is already a reported state |
| Executable-file classification | N/A | no file mode changes; no new entry point |
| Routing / shell commands | N/A | no command surface changes; `COMMANDS` is untouched |
| VCS / PR automation | N/A | no VCS surface |
| Network | N/A | none reached |

## What Breaks

**Producers** (located by name, not assumed):

- `implementation_engine.py`'s 40 schema sites, 25 strings, 4 identifiers, 10 paths, 88
  comments — the change itself.
- `impl_domain_profile._REQUIRED_NESTED` — grows; its `…_UNSAFE_PATH` walk must **not**
  grow with it (M3).
- `reachable_refusal_codes()`'s pinned count — unchanged unless a refusal is genuinely
  added. Asserted either way.
- `tests/test_proposal_implementation.py` — any test naming a renamed identifier
  (`unreached_mathematics`) goes red; loud, and the rename is driven by Lock B's report.
- `tests/proposal-deliberation-domain-profile-lock.test.mjs` — **not touched.** The Python
  mirror is a new file; editing the TS lock would put the sister skill inside this cut's
  blast radius, which the bar forbids.

**Products** — records already written under the old shape:

- Targets' `src/<Package>/*.py` `__provenance__` dicts spelling `"equations"`: **valid,
  and valid only because `claim_key` supplies the same literal.** This is the row that
  matters. A domain that ever supplied a different word would put every previously authored
  module in that domain out of domain, silently — read under a key nothing writes, reported
  as `[]`. Recorded here so Cut 3 and any future domain inherit it as a constraint, not a
  discovery.
- Targets' `tests/findings.py` findings spelling `equations`/`remedy_equations`: same, via
  `locus_key`/`remedy_locus_key`.
- Targets' `__benchmark__["arms"][x]["sections"]`: **untouched** — the coarse key stays
  shared. Exactly what the B2 ruling protects.
- Targets' already-authored `src/<Package>/__init__.py` carrying the old sentence:
  **untouched.** `authored_package_init` writes at materialize time and nothing re-reads
  that sentence — no verifier parses it. Confirmed by reading its only call site.
- Targets' committed `.implementation/position.jsonl` minted gate authorizations:
  **untouched.** No binding key is a schema key, and `proposalDigest` is not renamed (D6).
- Targets' `admissibility.json` rulings: **untouched.** `cmd_admit`'s verdict prose is
  recomposed from the same literals, so previously written verdicts stay readable and no
  re-ruling is implied.
- `tests/seal/digests.json`: **must stay valid.** That is the success criterion.
- Archived reports carrying `source_digest`/`suite_digest`: **untouched** — no digest input
  changes.
- Materialized kit files in existing targets, judged by `kitSource`: **untouched**, because
  no kit file is edited (D4).

## Migration / Rollout

No migration. Rollout is D7's S0–S14; S1 before S2 is the red-first discipline, and no
S-step may be merged with its neighbour.

## Predictions apply must measure, not repeat

Cut 1 shipped a false prediction about git rename detection. These are claims of the same
kind — each is an instruction to measure, never a fact to cite:

- [ ] Every **Predicted mover** in D1. Measure which case ids move under each mutation
      *before* writing the assertion. A leaf with **no** mover is recorded as having no
      seal instrument, with its removal-refusal and its lock coverage named as its whole
      defence — never papered over.
- [ ] L1's occurrence count and file list (D6). Measured at S0, pinned at S13. `rg -c`
      counts lines, not occurrences.
- [ ] The 88/25/4/10 sub-counts from §A. They are the measurement's, taken at `a851390`,
      and the engine has moved since (Cut 1, F3). Re-derive from Lock B's failure report.
- [ ] That S12's comment sweep touches **no executable text**. Assert by seal run, not by
      inspection.
- [ ] That `kitSource` is blind to a kit-template edit for the seal fixtures (D4). Cut 1
      measured it `null` for these fixtures; that is a reason not to rely on the seal here,
      not a licence to edit the kit.

## Open Questions

- [x] `provenance.drift_unit_key` → **does not exist** (B2 ruling; M6 corroborates).
- [x] The four excluded §B1 fields → **stay excluded**, reasons carried forward (D1).
- [x] How the authored sentence moves → **verbatim, one leaf** (D3).
- [x] The kit agreement → **a lock over six sites, zero kit edits** (D4/M4).
- [x] The campaign-proposal exclusion → **three test layers**, not a discipline (D6).
- [x] The separable slice → schema+locks / vocabulary+comments+locks, with each PR landing
      the locks it can keep green (D7).
- [x] `CITATION_RE` → **`findings.citation_pattern`**, an eleventh field (M1).
- [x] The derived-denylist lock (TS C-3) → **deferred**, with its degeneracy measured (M5).
- [ ] **`compose` / M1 is an OPEN OPERATOR DECISION and this design does not take it.**
      Whether composition becomes a profile-supplied callable or `compose` stays the one
      per-skill command. `DISPLAY_BLOCK_RE` and `TAG_RE` spell no domain word, so Lock B
      does not force the question — which is why it can stay open.
- [ ] **M2's tension, recorded unresolved.** Moving `cmd_handoff`'s hardcoded Spanish into
      `vocabulary` is correct for the extraction **and** hardens a doctrine violation
      (`SKILL.md`: *"Speak the language the user is speaking"*) into a contract shape.
      Translating it here would be a behavioural delta the seal must refuse. Recorded, not
      fixed.

## Citations Checked

Every symbol below was located **by name** in the source during this phase, never inherited
by line: `unreached_mathematics` (and its *"the join nothing else in the flow crosses"*
docstring), `benchmark_unfaithfulness`, `wiring_proposal`, `undeclared_arms_note`,
`ARMS_UNDECLARED_CONSEQUENCE`, `authored_package_init`, `proposals_root`,
`IMPLEMENTATION_PROPOSALS`, `revision_source`, `revision_discovery`,
`MANAGED_ARTIFACT_MARKER`, `CITATION_RE`, `finding_impact`, `adoption_state`,
`remedy_compatibility`, `cmd_admit`, `cmd_handoff`, `cmd_compose`,
`_wiring_first_publication`, `_AUTHORIZATION_BINDING_KEYS`, `changed_sections`'s consumers
in `cmd_verify`, `KIT_SEAL`, `impl_domain_profile._REQUIRED_NESTED` /
`_OBJECTIVE_REQUIRED` / `_STAGE_REQUIRED` / `ImplementationProfileError`,
`impl_profile.PROFILE` and `OBJECTIVE_FLOW`, the kit's `src/module.py`,
`src_benchmark/__init__.py`, `tests/findings.py`, `tests/test_audit.py` and
`nb/verification.ipynb`, `tests/seal/cases.json`'s 29 case ids, and
`tests/proposal-deliberation-domain-profile-lock.test.mjs`'s `discoverProfiles`,
`buildDenylist`, `PINNED_RESIDUE`, `EQUATION_RESIDUE` and `PROPOSAL_RESIDUE`.

**One inherited citation corrected.** The archive
`openspec/changes/archive/2026-09-11-the-engine-leaves-its-skill/` holds `proposal.md`,
`design.md`, `tasks.md` and `verify-report.md` — **no `archive-report.md`**. Cut 1's
mechanics were read from `design.md`. **F3 is confirmed closed at HEAD**: all five refusals
spell `proposals_root()`, so there is no Cut-2 delta there.
