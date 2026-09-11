# Design: A Revision Is Two Documents

> **Size note.** Over the 800-word budget, deliberately, on the precedent both
> prior cuts set and the brief repeats: *mechanics concrete enough that apply
> invents nothing*. Twenty-four binding sites, a header grammar, a digest whose
> shape travels in other people's clones, and a two-slice landing order do not
> compress into 800 words without becoming a design apply has to re-derive.

## Technical Approach

`documents` becomes a **list**. Every scalar wire field keeps today's exact
shape under `len(documents) == 1`, and a second document enters through
**additive keys that are absent under one**, never by reshaping a key that is
already on disk. Byte-identity is then **structural** — a property of the code's
shape, not a promise a test has to keep re-proving.

Two runs, never conflated (Cut 2's D8, carried forward unchanged):

| Run | Question | Pass condition |
|---|---|---|
| **No-delta** | did this work unit change any output? | 28 digests byte-identical, after **each** unit |
| **Mutation** | does the new branch actually reach the output? | a named digest **moves**, under a real reverted edit reaching a real subprocess |

**The slice seam.** Slice A changes no wire shape at all, so the existing seal
alone proves it. Slice A also ships the **two-document fixture profile and pair
corpus** — the instrument without which every Slice-B branch is a false guard.
A is independently green and independently valuable: a profile that can declare
two documents, refuse by index, and be driven through the seal harness is a
capability on its own, even if B never lands.

## Measurements that change the proposal's shape

Five findings from reading the source in this phase, each located by symbol.

### M1 — `_POSITION_HEADER_RE` does not exist

The proposal, the brief and the measurement all name it. Grepped by name in
`impl_position.py`: **no such symbol**. The real three are `_BLOCK_OPEN_MARKER`
(a loose counting opener), `_BLOCK_OPEN_RE` (the one true opener: `revision`,
`sha256`, `derivedAt`, `session`, `target`, in that order) and
`_LEGACY_BLOCK_OPEN_RE` (the pre-`target=` grammar, matched only under
`allow_legacy=True`). Every downstream artifact must stop repeating the name.
This is the inherited-citation failure mode the shared protocol describes,
caught by grepping instead of trusting.

### M2 — the "8 `revision_source(args.revision)` call sites" is 7, and `verify` is the eighth *command*

Measured by name: **13** `revision_source(` call sites total. Seven read
`args.revision` directly — `cmd_probe` (in its `if args.revision else None`
form), `cmd_handoff`, `cmd_admit`, `cmd_position`, `cmd_gate`, `cmd_offer`,
`cmd_close`. Six take a parameter or a derived name — `remedy_compatibility`,
`admissibility_record`, and four inside `cmd_verify`, which reaches the
resolved `revision` (argument **or** discovered), never `args.revision`. So
there are eight revision-consuming **commands** and seven `args.revision`
sites. **Tasks must re-derive, not repeat either number.**

### M3 — the binding already survived one shape migration, and it was the *easier* kind

`_verify_gate_authorization` carries `GATE_AUTHORIZATION_SUPERSEDED`: a token
minted before `proposalDigest` joined the binding re-digests under a 7-key
shape and is distinguished from a tampered one. Its discriminator is
`"proposalDigest" not in record` — **key absence, never a null value**, with the
reason stated in the comment beside it. That is a *key-set* migration.
Cut 3's is the harder kind: the key stays, its value changes. `revisionSha256`
is present in both shapes, so **no absence test can see it**. D1 is built
around that asymmetry.

### M4 — the mutation instrument already exists, including the `build_env` wrapper

`tests/test_implementation_domain_mutation.py` already holds
`_ORIGINAL_BUILD_ENV` + `_build_env_with_profile_override`, which injects
`IMPLEMENTATION_DOMAIN_PROFILE` into a real subprocess env precisely because
`seal_harness.ALLOWED_ENV_KEYS` excludes it. Cut 3 **reuses** this, it does not
rebuild it. It also already records `NON_DETERMINISTIC_CASE_IDS = {"propose"}`
and a `MEASURED_MOVERS` table in which `documents.directory` moves exactly
`admit-e0`, `close-e0`, `gate-e0`, `offer-e0`, `position-e0`. **That is the
positive control** (D8).

### M5 — `IMPLEMENTATION_PROPOSALS` is one variable for what is becoming N directories

`proposals_root()` returns `Path(os.environ["IMPLEMENTATION_PROPOSALS"])` when
set, else `DOCUMENTS_DIRECTORY`. `seal_harness.build_env` passes exactly that
one key. Under two documents, one variable cannot name two roots. **Decision:
the bare variable keeps overriding document 0 and nothing else** (byte-identical
under one); a second document is overridden by `IMPLEMENTATION_PROPOSALS_1`,
added to `ALLOWED_ENV_KEYS` only in Slice A's pair-corpus work. A generic
`IMPLEMENTATION_PROPOSALS_0` alias is **rejected**: it would be a second
spelling for a variable every existing fixture, every seal case and every
target's own tooling already uses.

## Architecture Decisions

### D1 — The gate authorization binding (lands FIRST in Slice B)

The token is `sha256(json.dumps({**binding, "session":…, "at":…,
"mintOrdinal":…}, sort_keys=True))`, built in `_find_or_mint_authorization` and
re-derived identically in `_verify_gate_authorization`. Three literals spell the
key set: `_AUTHORIZATION_BINDING_KEYS`, `_authorization_binding`'s return, and
`cmd_gate`'s inline `gate_binding`.

**D1a. `revisionSha256` stays a bare 64-char hex string under one document.**
Not a one-element list, not a mapping keyed by label.

**D1b. A second document enters under a new key, `documentRevisions`,
present in the binding only when `len(documents) > 1`.**

| Option | Why not |
|---|---|
| `revisionSha256` becomes a list always | Moves every minted token in every clone. The F1 damage class, for a value |
| `revisionSha256` becomes a list only under two documents | Key set identical, so it passes today's test — but the conditional hides *inside* a key already on disk, and `GATE_AUTHORIZATION_STALE`'s `record[key] != binding[key]` would then compare a string to a list and refuse under the wrong code |
| A composite `sha256(sha_a + sha_b)` | A composite of one is not the bare sha. Moves under one document |
| **Additive key, absent under one (chosen)** | The one-document payload is byte-identical **by construction**, not by assertion |

**D1c. `_AUTHORIZATION_BINDING_KEYS` stays a literal 8-tuple.** This is the
trap. `own_binding = {key: record.get(key) for key in _AUTHORIZATION_BINDING_KEYS}`
iterates that constant; growing it to 9 makes every one-document record
re-digest over a 9th key it never had (`record.get()` → `None`) and **every
token in every clone fails**. The 9th key is contributed by a separate
`_authorization_binding_keys(record_or_binding)` helper returning the base eight
plus `documentRevisions` **only when that key is present in the mapping** —
absence, never null, the exact discriminator M3 shows the file already trusts
and already explains. `CampaignProposalExclusionTests`'s L3
(`assertIn("proposalDigest", module._AUTHORIZATION_BINDING_KEYS)`) therefore
stays green **unedited**, which is the bar the proposal set.

**D1d. The re-derivation test lands before the work it protects**, as its own
`test(...)` commit, in its own file `tests/test_implementation_authorization_binding.py`:

| Test | Assertion |
|---|---|
| `test_committed_token_rederives` | A committed fixture `authorization` event's payload, rebuilt through the production path, digests to a **token committed as a literal in the test** — never recomputed from the fixture on both sides (that is the "green because nothing happened" shape) |
| `test_verify_accepts_the_committed_token` | `_verify_gate_authorization` over the fixture returns the record, does not raise |
| `test_superseded_still_fires` | A 7-key legacy fixture still yields `GATE_AUTHORIZATION_SUPERSEDED`, not `UNKNOWN` — the existing mechanism is not collateral damage |
| **mutation** | Add any 9th key **unconditionally** to the derivation; `test_committed_token_rederives` must redden. Without this, the guard is unproven |

### D2 — The site classes: what lands and seals together

All 24 `revisionSha256` occurrences in the engine, mapped to their enclosing
symbol in this phase. Each class is one work unit = one `test(...)` commit +
one implementation commit + one seal run.

| Class | Enclosing symbols | Sites | Cut 3 shape |
|---|---|---|---|
| **C1 — position read** | `position_state`: its `empty` dict, its `bound_to` comparison against `hashlib.sha256(source…)`, its return dict | 3 | `boundTo` stays `"current"`/`"stale"`/`"unknown"` under one; a per-document mapping appears only under two |
| **C2 — position write & header grammar** | `cmd_position`: its docstring's `(revision, revisionSha256, targetLevel)`, `header`, the `absent` return, the `unchanged` comparison, the `unchanged` return, the `position` ledger event, the `written` return. Plus `impl_position.locate_block` and `render` | 7 (+2 in `impl_position.py`) | D3 |
| **C3 — admissibility** | `cmd_admit`'s `record`; `admissibility_record`'s `record.get("revisionSha256") != current` | 2 | D5 |
| **C4 — authorization binding** | `_AUTHORIZATION_BINDING_KEYS`, `_verify_gate_authorization`'s `STALE` key tuple, `cmd_gate`'s `gate_binding`, `_authorization_binding` | 4 | D1 |
| **C5 — ledger events & command returns** | `cmd_gate`'s `gate` event + return; `cmd_offer`'s `offer` event + return; `cmd_close`'s `prior_close` comparison, its `not_open` return, its `close` event, its `closed` return | 8 | Scalar key unchanged; additive `documentRevisions` only under two |
| **C6 — the non-`revisionSha256` scalars** | `cmd_verify`'s `module["stale"] = bool(revision) and module["revision"] != revision` (over `prov.get("revision")`); `benchmark`'s `built_against = declaration.get("revision")` and `staleRevision`; `admissibility_record`'s returned `revision`; `fidelity.latestRevision`/`revisionSource` | 5 reads | Per-document; scalar emitted under one |
| **C7 — findings routing** | `well_formed`, `finding_impact`, `remedy_compatibility`, `cmd_admit`'s verdict loop | — | D6 |
| **C8 — per-document fidelity** | `cmd_verify`'s four-condition fold `stale or missing_provenance or untested or unreached` | — | D7 |

**Ordering rationale.** C4 first (it is the only class that can damage a
repository this change never opens). Then C3 and C2 — the two classes with
artifacts already on disk. Then C1, C5, C6 — reads and reported output. Then
C7 and C8, which depend on nothing above them. Within Slice B, no two classes
share a commit.

### D3 — The position header: one optional trailing group

`_BLOCK_OPEN_RE` matches `revision=(?P<revision>\S+)` then
`sha256=(?P<sha256>[0-9a-f]{64})` then `derivedAt`, `session`, `target`, in that
exact order. `\S+` cannot hold a space-separated list, and no field may be
reordered.

**Choice.** `revision=`/`sha256=` keep meaning **document 0, exactly as today**.
A trailing, optional group is appended **after** `target=`:
`(?:\s+documents=(?P<documents>\S+))?`, carrying a compact, whitespace-free
encoding of the remaining pairs. Under one document the group never matches,
`render` never emits it, and the header bytes are identical.

| Alternative | Why not |
|---|---|
| `revision=` becomes a delimited list | Every existing block on disk becomes a one-element list read under a new meaning; `\S+` would silently swallow a delimiter a revision name legitimately contains |
| A second full field pair `revision2=`/`sha2562=` | Two spellings for one concept, and N is not 2 forever |
| A separate sidecar file | The header's whole point is that the binding travels **in the document a human reads** |

**`_LEGACY_BLOCK_OPEN_RE` does not grow the group.** It is the frozen pre-PR10
grammar; its only job is making migration reachable.

**New refusal: `POSITION_HEADER_DOCUMENT_COUNT_MISMATCH`.** A header carrying
`documents=` read under a profile declaring one document is refused, never
half-read. This **adds a reachable refusal code** and therefore moves
`reachable_refusal_codes()`'s pinned count. Re-assert the pin and **record the
new number as measured**, per the proposal's own mitigation.

### D4 — Slice A's accessor: the constants keep their spelling

`DOCUMENTS_DIRECTORY` and `DOCUMENTS_LABEL` are module-level constants read
from `PROFILE["documents"]`. Slice A makes `PROFILE["documents"]` a list and
**keeps both constant names spelled identically**, now derived from entry 0:

```python
DOCUMENTS = PROFILE["documents"]          # a list, Cut 3
DOCUMENTS_DIRECTORY = DOCUMENTS[0]["directory"]   # unchanged spelling, unchanged value at len == 1
DOCUMENTS_LABEL = DOCUMENTS[0]["label"]
```

Nothing downstream of those two names changes in Slice A. That is what makes A
a pure zero-delta cut the existing seal alone can prove.

**Resolver.** `_REQUIRED_ABSOLUTE_ONLY`'s single `("documents", "directory")`
pair becomes a per-entry walk emitting `documents[1].directory` — the **indexed
leaf name**, exactly as `_REQUIRED_NESTED`'s comment already argues for
`kit.root` over `kit`. `documents.label` moves from `_REQUIRED_PRESENCE` to the
same per-entry walk, emitting `documents[0].label`. An empty list is refused
`IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming `documents[0]`, mirroring
`stages_incomplete`'s own reason for existing.

**The TS precedent is thinner than assumed.** `domain-profile.ts` declares
`sources: readonly {path, required}[]` and validates it with **top-level
presence only** — no per-entry check at all. So per-index refusal is *stronger*
than the sister side, not a mirror of it. The inherited lesson is the
`artifact: {}` vacuity bug that file records twice, which argues **for** the
per-index walk.

### D5 — `admissibility.json`: dual-shape read, single-shape write per count

It is a **persisted artifact in somebody else's repository**. `cmd_admit` writes
`{"revision": …, "revisionSha256": …, "findings": …}`; `admissibility_record`
compares `record.get("revisionSha256")` to a freshly computed hash.

- Under one document, `cmd_admit` writes **exactly today's three keys** and
  `admissibility_record` reads them exactly as today.
- Under two, an additive `documents` list is written **beside** them, and
  `revision`/`revisionSha256` keep naming document 0.
- `admissibility_record` reads the scalar keys first and falls back to
  `documents` only when a second document is declared **and** the scalar keys
  are absent. A file written in the scalar shape therefore still rules.

**Asserted from a committed fixture written in the scalar shape**, not from one
this change generates. A fixture the change itself produced cannot prove
backward compatibility.

### D6 — Findings routing, the three IN pieces

| Piece | Shape | Gate |
|---|---|---|
| `well_formed` demands `document` | A new refusal branch inside the existing `MALFORMED_FINDINGS` class, naming `FINDINGS[{index}]` exactly as the `id` branch does | **`len(DOCUMENTS) > 1` only.** Unconditional refuses every populated `tests/findings.py` on disk, the seal corpus's own included, and moves `admit-e1`/`handoff-e1`/`verify-a` |
| `finding_impact`'s `impact["class"]` | Today `"local" if local else "structural"`. Becomes a per-document mapping **only under two**; under one it stays that exact string | `len(DOCUMENTS) > 1` |
| `admissibility.json` | D5 | — |

`remedy_compatibility(findings, revision)` and `admissibility_record(target,
revision)` take the documents rather than one revision; both already return a
`status` dict whose keys are unchanged under one document.

**Out, quoted verbatim into tasks:** *"Cut 3 makes the pair representable and
provable. It computes no verdict over it."* No cross-document agreement, and no
word for what `handoff` prints when a finding names both.

### D7 — Per-document fidelity

`cmd_verify` computes `fidelity_status` by folding `stale or missing_provenance
or untested or unreached`, guarded above by `if not revision: "unknown"` and
below by `resolved["status"] == "undeclared"`. The fold becomes a function of
one document, applied N times.

**Under one document, `fidelity` emits today's exact key set and today's exact
values.** Under two, a sibling `fidelityByDocument` list appears **beside**
`fidelity`, and `fidelity.status` reports document 0. No existing key is
renamed, re-nested, or made conditional. `verify-a`, `verify-b` and `verify-t`
are the three most-covered seal cases; a single moved key in this block moves
all three at once.

### D8 — Mutation proof, and the positive control that runs first

**The control runs before anything else in the harness, under
`.venv/bin/python`.** Mutate `documents[0].directory` to a fresh
`tempfile.mkdtemp()` sibling and assert the **exact five** ids
`admit-e0`, `close-e0`, `gate-e0`, `offer-e0`, `position-e0` move, and no other.
That set is already `MEASURED_MOVERS["documents.directory"]`, so the control is
calibrated against a prior measurement rather than invented here. If it does not
reproduce, **every zero-mover reading in that session is void** — the Cut-2
near-miss where system `python3` broke `CLI_INVOCATION` and crashed both sides
identically, reading as "zero movers" for every leaf.

Per class, both directions:

1. **Removal** — drop the leaf from the fixture profile; the resolver refuses
   `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming the **indexed leaf**.
2. **Collapse** — force the branch back to the scalar path in a scratch copy; a
   **named** pair-corpus test reddens.

**Discipline carried forward unchanged.** Never a monkeypatch — every seal case
is a subprocess, so patching `impl_domain_profile.PROFILE` or an engine
attribute has zero effect. Anchor counts asserted both directions before and
after every edit (`1 → 0` old, `0 → 1` new, then back): an anchor that matched
is not a mutation that ran, and `sd -s` exits 0 having changed nothing. For
untracked scratch files `git diff --stat` proves nothing, so the anchor count
**is** the proof. A surviving mutation has two explanations — a weak test or a
wrong claim about what the branch reaches — and apply **measures which** before
strengthening anything, recording a zero-mover explicitly rather than hunting
for a test that would have moved it.

### D9 — The fixture profile and the pair corpus

**Where it lives:** `tests/fixtures/two_documents/impl_profile.py`, written to a
`tempfile` directory at run time by the same `_write_scratch_profile` mechanism
Cut 2 already uses, with `_SKILL` re-anchored to the real skill directory.

**Why that is sanctioned, not a workaround:** `impl_domain_profile._resolve()`'s
own comment records that a *"must live under `FORGE_ROOT`"* rule *"was
considered and rejected"* because it *"would refuse a tmpdir fixture profile,
which is the exact override case `setdefault` exists to serve"*. And
`tests/test_implementation_domain_lock.py`'s `discover_profiles()` globs
`.claude/skills/*/impl_profile.py`, so a fixture under `tests/` is **not** seen
as a third skill and Lock A stays green.

**The pair corpus is additive.** `tests/seal/cases.json`'s 29 case ids and
`tests/seal/digests.json`'s 28 digests are **byte-identical, untouched**. The
pair cases live in their own roster — `tests/pair/cases.json` with its own
goldens — driven by the same `seal_harness.run_case` through
`_build_env_with_profile_override`. Two rosters, two goldens, one harness.
A pair case has **no** entry in `tests/seal/digests.json` and never can.

## Data Flow

```
impl_profile.PROFILE["documents"]  →  [ {directory,label}, {directory,label}, … ]
                                              │
                     impl_domain_profile._resolve()   per-index refusal:
                                              │        documents[1].directory
                                   DOCUMENTS (list)
                     ┌────────────────────────┼──────────────────────────┐
            DOCUMENTS[0] (Slice A)      len(DOCUMENTS) == 1?      DOCUMENTS[1..] (Slice B)
                     │                        │                          │
       DOCUMENTS_DIRECTORY / _LABEL       yes → today's exact bytes   no → additive keys
                     │                        │                          │
         proposals_root() ← IMPLEMENTATION_PROPOSALS      IMPLEMENTATION_PROPOSALS_1
                     │                        │                          │
              revision_source ──→ sha256 ──→ revisionSha256      documentRevisions
                                              │                          │
        ┌──────────────┬────────────┬─────────┴────────┬─────────────────┘
   position header  admissibility  authorization    fidelity / findings
        │                │              │                 │
   tests/seal/ (28, byte-identical) ─── tests/pair/ (new goldens, additive)
```

## File Changes

| File | Action | Description |
|---|---|---|
| `.claude/skills/proposal-implementation/impl_profile.py` | Modify | **A.** `documents` becomes a one-entry list |
| `.claude/skills/_core/implementation/impl_domain_profile.py` | Modify | **A.** per-index validation tier; indexed leaf names |
| `.claude/skills/_core/implementation/engine/implementation_engine.py` | Modify | **A.** `DOCUMENTS` + the two constants re-derived. **B.** classes C1–C8 |
| `.claude/skills/_core/implementation/impl_position.py` | Modify | **B/C2.** the optional `documents=` group in `_BLOCK_OPEN_RE`, `render`, `locate_block` |
| `tests/fixtures/two_documents/impl_profile.py` | **New** | **A.** the fixture profile (D9) |
| `tests/pair/cases.json`, `tests/pair/digests.json` | **New** | **A.** the pair corpus and its own goldens (D9) |
| `tests/fixtures/authorization/position.jsonl` | **New** | **B.** the committed pre-change token (D1d) |
| `tests/fixtures/admissibility/scalar.json` | **New** | **B.** an `admissibility.json` in the scalar shape (D5) |
| `tests/fixtures/position/scalar_header.md` | **New** | **B.** an `AGREED.md`-style block in the scalar header shape (D3) |
| `tests/test_implementation_authorization_binding.py` | **New** | **B.** D1d, lands first |
| `tests/test_implementation_domain_mutation.py` | Modify | the positive control (D8); per-class mutations |
| `tests/test_implementation_profile.py` | Modify | indexed-leaf removal refusals |
| `tests/seal/harness.py` | Modify | **A.** `IMPLEMENTATION_PROPOSALS_1` joins `ALLOWED_ENV_KEYS` (M5) |
| `tests/seal/cases.json`, `tests/seal/digests.json`, `tests/seal/corpus.py` | **Unchanged** | `git diff --exit-code tests/seal/` must exit 0 |
| `tests/test_implementation_domain_lock.py` | **Unchanged** | `CampaignProposalExclusionTests` must not be edited |
| `.claude/skills/proposal-deliberation/**`, `_core/deliberation/**` | **Unchanged** | read for structure, never written |

## Interfaces / Contracts

```python
# impl_profile.py — one entry, so every byte the engine emits is unchanged
"documents": [
    {"directory": _FORGE_ROOT / "proposals", "label": "proposal"},
],

# the fixture profile — two entries, so every pair branch is reachable
"documents": [
    {"directory": _FIXTURE_ROOT / "proposals", "label": "proposal"},
    {"directory": _FIXTURE_ROOT / "experiments", "label": "experiments"},
],
```

```python
# the authorization binding — 8 keys under one document, byte-identical
{"jobName", "commit", "entrypoint", "units", "rung",
 "revisionSha256", "positionStatus", "proposalDigest"}
# under two, and ONLY under two, a 9th is present:
"documentRevisions": [{"label": ..., "revision": ..., "sha256": ...}, ...]
```

```
<!-- position revision=R sha256=<64hex> derivedAt=D session=S target=T -->
<!-- position revision=R sha256=<64hex> derivedAt=D session=S target=T documents=<compact> -->
```

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | indexed-leaf refusals | fresh `importlib` load, controlled `os.environ`; each names `documents[N].<leaf>` |
| Unit | empty `documents: []` | refused `INCOMPLETE` naming `documents[0]`, never passing vacuously |
| Unit | token re-derivation | committed fixture + committed literal digest (D1d) |
| Unit | scalar-shape `admissibility.json` | still rules under one document, from a committed fixture (D5) |
| Unit | scalar-shape position header | still parses; a `documents=` header under one document refuses (D3) |
| Unit | `well_formed` conditionality | a `document`-less finding **passes** under one, **refuses** under two |
| Integration | the seal | 28 byte-identical **after each work unit**, not only at the end |
| Integration | the pair corpus | every pair branch named, with the case id that reaches it |
| Mutation | positive control | the five `documents.directory` movers, **first**, under `.venv/bin/python` (D8) |
| Mutation | per class | collapse-to-scalar reddens a named pair test; anchor counts both directions |
| Mutation | binding guard | an unconditional 9th key reddens `test_committed_token_rederives` |
| Non-interference | sister skill | `npm test` **595/595**; `.venv/bin/python -m unittest discover -s tests` **OK, `skipped=6`** (`Ran` free to grow). Pasted before and after |

**Commit granularity.** Every work unit is **two commits**: a `test(...)` commit
carrying only the failing test(s), then the implementation. **The RED commit
must be individually checkoutable with the test red at that sha**, verified by
checkout, not by claim. This closes the traceability gap Cut 2 recorded; it
costs roughly double the commit count and **zero** changed lines.

## Threat Matrix

| Row | Applicable | Behaviour / RED test |
|---|---|---|
| Subprocess invocation | **Yes (inherited)** | seal + pair cases; `shell=False`, list argv, unchanged |
| Environment-variable routing | **Yes** | `IMPLEMENTATION_PROPOSALS` keeps overriding document 0 only; `IMPLEMENTATION_PROPOSALS_1` is new and allow-listed (M5). RED per refusal |
| Path traversal via profile | **Yes** | every `documents[N].directory` absolute; existence **not** required, per entry, keeping M3's tier reasoning intact per index |
| Data integrity of persisted records | **Yes — the headline row** | minted tokens, `admissibility.json`, position headers, `close`/`authorization` ledger events. D1d, D5, D3 |
| Executable-file classification | N/A | no file mode changes, no new entry point |
| Routing / shell commands | N/A | `COMMANDS` untouched; no new subcommand (a 21st would redden the seal's coverage check) |
| VCS / PR automation | N/A | no VCS surface |
| Network | N/A | none reached |

## What Breaks

**Producers** (located by name):

- The 24 engine `revisionSha256` sites, mapped to classes C1–C5 in D2.
- `impl_position._BLOCK_OPEN_RE`, `render`, `locate_block` — M1's real names.
- `impl_domain_profile._REQUIRED_ABSOLUTE_ONLY` and `_REQUIRED_PRESENCE`'s
  `("documents", "label")` pair — both move to the per-entry walk.
- `reachable_refusal_codes()`'s pinned count — **moves**, by exactly the
  refusals genuinely added (D3's is one). Re-asserted and re-recorded.
- `seal_harness.ALLOWED_ENV_KEYS` — grows by one key.
- `tests/test_implementation_domain_lock.py` — **not touched.**
  `CampaignProposalExclusionTests` L3 stays green because D1c keeps the tuple
  at eight literal members.

**Products** — records already written under the old shape:

- **Minted gate authorizations in every target's committed
  `.implementation/position.jsonl`: valid, and valid only because D1a/D1c keep
  the payload byte-identical.** The row that matters. A ledger travels in
  clones; this repository cannot enumerate the clones.
- **Prior `close` events**: `cmd_close`'s `prior_close` lookup compares
  `e.get("revisionSha256") == revision_sha256` against events already on disk.
  A changed value shape makes every prior close non-matching and closes a
  second time. Untouched under one document; asserted, not assumed.
- **Prior `authorization` events**: `_find_or_mint_authorization`'s reuse lookup
  is `all(e.get(key) == value for key, value in binding.items())`. A 9th key in
  `binding` under one document would make every existing unconsumed token
  invisible and re-mint. D1b prevents it structurally.
- **Targets' `tests/admissibility.json`**: valid, by D5's dual-shape read,
  proven from a committed scalar-shape fixture.
- **Targets' `AGREED.md`-style position headers**: valid, by D3's optional
  trailing group. The legacy opener stays frozen.
- **Targets' `__provenance__["revision"]` and `__benchmark__["revision"]`**:
  **untouched.** Both stay scalar reads on disk; C6 changes only what the engine
  compares them **against**.
- **`tests/seal/digests.json`**: must stay valid. That is the success criterion.
- **Archived reports carrying `source_digest`/`suite_digest`**: **untouched** —
  no digest input changes.
- **`propose`'s campaign-proposal digest**: unsealed already and
  non-deterministic already (`tests/seal/unsealed.json`); nothing here touches
  what it reads. Stated so it is not later read as a regression.

## Migration / Rollout

No data migration. Nothing already written is rewritten, by construction.

**Slice A** — A0 baseline (both suites + `sha256(tests/seal/digests.json)`,
pasted) → A1 RED: indexed-leaf refusals → A2 resolver per-entry walk +
`impl_profile.py` one-entry list + `DOCUMENTS` accessor (seal: 28 identical) →
A3 fixture profile + `IMPLEMENTATION_PROPOSALS_1` (seal: 28 identical) → A4 pair
corpus + its own goldens (seal: 28 identical) → A5 the positive control (D8).

**Slice B** — B1 **D1d, RED then green, before anything else** → B2 C4 → B3 C3
→ B4 C2 → B5 C1 → B6 C5 → B7 C6 → B8 C7 → B9 C8 → B10 proof: every per-class
mutation, `git diff --exit-code tests/seal/`, both suites pasted.

Seal after **every** step. Any movement attributes to exactly the one unit just
landed — which is the entire reason for not batching.

**Rollback.** Per unit, then per slice. `tests/seal/` is untouched by
construction, so the pre-change seal is the post-revert seal. **One asymmetry,
carried forward from the proposal:** once a second skill exists and has minted an
authorization under a two-document profile, reverting D1 strands that token. No
`proposal-implementation` ledger can hold one, so reverting before that skill
exists is clean.

## Predictions apply must measure, not repeat

Cut 1 shipped a false prediction about git rename detection and predicted digest
movers that did not move. Everything below is an instruction to measure.

- [ ] That the five `documents.directory` movers reproduce as the positive
      control. If they do not, **stop**; every zero-mover reading that session is
      void.
- [ ] That a real minted `authorization` event exists to copy into
      `tests/fixtures/authorization/`, or that one can be minted once with a
      pinned `session`/`at`/`mintOrdinal` and committed.
- [ ] `reachable_refusal_codes()`'s new count. Measured after D3, never
      predicted here.
- [ ] That Slice A moves **zero** digests. Claimed structurally by D4; proven
      only by the seal run.
- [ ] Which pair-corpus case reaches each new branch. Measure, then assert —
      never assert, then hunt for a case.
- [ ] That `well_formed`'s conditional leaves `admit-e1`, `handoff-e1` and
      `verify-a` identical. It is the branch most likely to move a digest.

## Open Questions

- [x] The gate binding's shape → **additive key, absent under one; the tuple
      stays 8 literal members** (D1).
- [x] The position header → **one optional trailing group after `target=`**,
      legacy opener frozen (D3).
- [x] `admissibility.json` → **dual-shape read, proven from a committed scalar
      fixture** (D5).
- [x] Where the fixture profile lives → **`tests/fixtures/two_documents/`,
      written to a tmpdir at run time; sanctioned by the resolver's own comment**
      (D9).
- [x] How the pair corpus relates to the 28 → **its own roster and its own
      goldens; the 28 are byte-identical and untouched** (D9).
- [x] The second document's directory override → **`IMPLEMENTATION_PROPOSALS_1`;
      the bare variable keeps meaning document 0** (M5).
- [ ] **`compose` / M1 remains an OPEN OPERATOR DECISION and this design does
      not take it.** An experiments document has neither `$$` nor `\tag{}`;
      `DISPLAY_BLOCK_RE` and `TAG_RE` are untouched here.
- [ ] **M2** — `cmd_handoff`'s hardcoded Spanish. Still recorded unresolved.
- [ ] **M5 (Cut 2's)** — the derived-denylist lock. Still deferred; a `skipTest`
      would move the pinned `skipped=6`.
- [ ] The `implementation-cli-seal` spec's `Ran 2849` pin is stale. Restate as
      **`skipped=6` with `Ran` free to grow** — the invariant that actually held
      across three cuts. A spec-level correction, recorded, not applied silently.

## Citations Checked

Located **by name** in the source during this phase, never inherited by line:
`revisionSha256` (24 occurrences in `implementation_engine.py`, 2 in
`impl_position.py`), `_AUTHORIZATION_BINDING_KEYS` and its eight members,
`_authorization_binding`, `_find_or_mint_authorization` (and its `mintOrdinal`
payload), `_verify_gate_authorization` (and `GATE_AUTHORIZATION_SUPERSEDED`'s
`"proposalDigest" not in record` discriminator), `_verify_gate_proposal`,
`cmd_gate`'s `gate_binding`, `position_state`, `cmd_position`, `cmd_close`'s
`prior_close`, `cmd_offer`, `cmd_admit`, `admissibility_record`, `well_formed`,
`read_findings`, `finding_impact`, `remedy_compatibility`, `adoption_state`,
`revision_source`, `revision_discovery`, `proposals_root`, `cmd_verify`'s
`fidelity_status` fold and `module["stale"]`, `prov.get("revision")`,
`declaration.get("revision")`, `impl_position.locate_block` / `render` /
`_BLOCK_OPEN_RE` / `_LEGACY_BLOCK_OPEN_RE` / `_BLOCK_OPEN_MARKER`,
`impl_domain_profile._REQUIRED_NESTED` / `_REQUIRED_PRESENCE` /
`_REQUIRED_ABSOLUTE_ONLY` / `_OBJECTIVE_REQUIRED` / `ImplementationProfileError`
and `_resolve()`'s tmpdir comment, `impl_profile.PROFILE`'s `documents` block,
`CLAIM_KEY` / `LOCUS_KEY` / `REMEDY_LOCUS_KEY` / `NOTATION_KEYS` /
`DOCUMENTS_DIRECTORY` / `DOCUMENTS_LABEL`, `seal_harness.build_env` and
`ALLOWED_ENV_KEYS`, `tests/seal/cases.json`'s 29 case ids,
`tests/seal/unsealed.json`'s single `propose` entry,
`test_implementation_domain_mutation.py`'s `MEASURED_MOVERS`,
`NON_DETERMINISTIC_CASE_IDS`, `_ORIGINAL_BUILD_ENV` and
`_build_env_with_profile_override`,
`test_implementation_domain_lock.py`'s `discover_profiles` and
`CampaignProposalExclusionTests`, and `domain-profile.ts`'s `sources` /
`REQUIRED` / `ARTIFACT_REQUIRED`.

**Two inherited citations did not hold and are corrected above.**
`_POSITION_HEADER_RE` **does not exist** anywhere in `impl_position.py` (M1) —
it reached this phase from the proposal, the brief and the measurement alike.
The "8 `revision_source(args.revision)` call sites" count is **7** (M2); there
are 13 `revision_source(` call sites in total and eight revision-consuming
commands, `cmd_verify` reaching it through the resolved `revision` rather than
`args.revision`. Both numbers were re-derived here and neither should be
repeated without re-measuring. The measurement's F4 claim about `--revision`
being *"registered for eight commands"* is **not repeated anywhere in this
document**; F4 is out of scope regardless.
