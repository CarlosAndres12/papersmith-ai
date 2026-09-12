# Design: Each Document Names Its Own Revision

> **Size note.** Over the 800-word budget, on the precedent Cut 3 set and the
> brief repeats: *mechanics concrete enough that apply invents nothing*. A
> derivation rule, a refusal with a classification, a fixture reshape that must
> redden without editing an assertion, and a five-member derived set do not
> compress without becoming a design apply has to re-derive.

## Technical Approach

`revision` stops being **one name against N roots** and becomes **one name per
document**. Index 0 keeps taking its name from `--revision`, byte-identically.
Every index beyond it **discovers** its own name inside its own root, under the
convention that root's own contents express — the operator's option B.

The carriers do not move. `_extra_document_revisions` already builds
`{label, revision, sha256}` **per index**; it simply fills every `revision` slot
with the same string. This change fills it with the right one. Nothing about the
key set changes, which is what keeps the whole cut contained.

## Measurements from this phase (every symbol grepped, none inherited)

### M1 — `proposals_root` already takes an index

The brief's reading is right about `revision_discovery` (it calls
`proposals_root()` bare) but `proposals_root(index: int = 0)` has been indexed
since Cut 3. Per-document discovery needs **no new root accessor** — only a seed
rule and a call-site argument.

### M2 — the one-name write is a single literal

Inside `_extra_document_revisions`'s loop, `"revision": revision`. That literal
is the defect at the carrier. `_admissibility_extra_documents` and
`_position_extra_documents` both copy `entry["revision"]` from it, so fixing the
loop fixes all three producers at once.

### M3 — the containment claim HOLDS, verified three ways (not inherited)

1. `_AUTHORIZATION_BINDING_KEYS` is a literal 8-tuple ending `proposalDigest`.
   This change does not touch it.
2. `_authorization_binding_keys` contributes the 9th key on **presence**
   (`if "documentRevisions" in record_or_binding`), never on a null.
3. **No record in any clone can carry `documentRevisions` at all.** Every site
   that writes it is gated on `len(DOCUMENTS) > 1`, and the only shipping
   profile — `proposal-implementation/impl_profile.py` — declares a
   one-entry `documents` list. The two-document profile lives under
   `tests/fixtures/two_documents/`, outside `discover_profiles()`'s
   `.claude/skills/*/impl_profile.py` glob.

So this change alters a **value**, inside a **key that exists on no disk
anywhere**. No committed record re-digests; no minted token in any clone is
invalidated. The claim is confirmed, and the 8-tuple stays literal.

### M4 — `position_state`'s `extra_sources` is a parameter nothing passes

Nine call sites (`cmd_probe`, `cmd_discuss`, `cmd_settle`, `cmd_gate`,
`cmd_offer`, `cmd_close` ×2, `cmd_step`, `cmd_verify`). **None passes
`extra_sources`.** So `_bound_to(revision, None, entry_sha)` returns `"unknown"`
for every document beyond 0, always, and C1's multi branch can never report
`current` or `stale`. Cut 3's re-verify mutation only proved `boundTo` is a
*dict*. This is "the rule that nothing calls", and it is a member of the derived
set the proposal did not have.

### M5 — `--revision`'s help text becomes false

Registered for eight commands; its help says admit/handoff/position/gate/offer/
close *"discover nothing"*. Per-document discovery makes six of them discover for
documents 1..N. Prose that outlived its mechanism, in argparse. `rg 'help'
tests/seal/cases.json` → **0 matches**, so correcting it should move no digest —
a claim apply must re-measure, not repeat.

### M6 — two readers of one carrier pair it two different ways

`position_state`'s multi branch keys the header's `documents` list **by label**
(`header_documents = {entry.get("label"): entry ...}`). `admissibility_record`'s
extra-document loop pairs **by position** (`enumerate(extra, start=1)`) and never
reads `entry["label"]` at all. Under one shared name the two agree by accident.
Under per-document names, adding, removing or reordering a document silently
compares document 1's recorded sha against document 2's file.

## Architecture Decisions

### D1 — Document N's name comes from the DIRECTORY, not from the profile

**Choice.** Seedless discovery inside `proposals_root(index)`, deriving the
family from that directory's own eligible contents.

| Alternative | Why not |
|---|---|
| A `stem`/`revisionPattern` field on `documents[i]` in `impl_profile.py` | `revision_discovery`'s own docstring is the standing doctrine: *"nothing here may know a naming convention"*, and *"teaching this side the other's naming rule would be a third copy of a convention that already has two."* A profile field is a **fourth** spelling, in the reader, that nothing can hold to `experimental-deliberation/profile.ts`'s `artifact` block. Drift would be silent |
| Seeded from the carrier (position header, `admissibility.json`) | The ruling's own rejection: nothing is bound on a first invocation, and a stale carrier would pin the family forever |
| One shared matcher across every root | The defect being fixed |

**Mechanism — `discover_document_revision(index)`**, reusing
`revision_discovery`'s arithmetic rather than copying it:

1. `root = proposals_root(index)`; not a directory → the same `empty` shape
   `revision_discovery` already returns.
2. Candidates: files under `sorted(root.iterdir())` whose name contains a digit
   run.
3. **Marker filter first**, `revision_discovery`'s existing rule verbatim: if any
   candidate `is_managed_artifact`, the directory is marker-owned and only marked
   candidates are eligible; the rest are reported in `nonManaged`.
4. Family key per eligible candidate: the digit-elided skeleton
   (`re.sub(r"\d+", …, name)`) — the same elision `revision_discovery` performs
   on its seed, applied to the candidates instead.
5. Exactly one family key → that family; pick by the same digit-tuple `max`, with
   `tied` reported identically.
6. More than one family key → **ambiguous**. Two conventions in one directory is
   not a choice this side may make (D3).

**Why the asymmetry with document 0 is forced, not chosen.** Document 0 has a
seed because the target's own bench declaration and module provenance carry a
revision name. Nothing in the target ever names document N's revision. The
seedless path therefore fires **only for `index > 0`** — which is also what keeps
`revision_discovery(None)`'s document-0 answer (`empty`) byte-identical, and with
it `fidelity.latestRevision`/`markerOwned`/`nonManagedCandidates` in the 28
sealed digests.

### D2 — `revision_source(revision, index)` stays a dumb reader

**Choice.** It means exactly *"read the file NAMED `revision` from document
`index`'s root."* It performs no discovery, so the defect cannot return inside
it. The docstring's claim — *"a revision is the pair of files that name shares
across `DOCUMENTS[0]`'s and `DOCUMENTS[1]`'s roots"* — is deleted, and replaced
by: the argument names **one** document's file; which name belongs to which index
is the caller's question, answered by `document_revision_names`.

**Rejected:** re-resolving internally for `index > 0`. A file reader that does
directory I/O, at thirteen call sites, answering differently on two calls in one
command.

**The resolver, memoized per process:**

```python
_DOCUMENT_NAME_CACHE: dict[tuple, tuple[str | None, ...]] = {}

def document_revision_names(revision: str | None) -> tuple[str | None, ...]:
    """One name per declared document. Index 0 is `revision`, exactly as
    given. Every index beyond it is DISCOVERED in its own root (D1)."""
```

Memoized because **two calls in one command must agree**: `cmd_gate` resolves the
pair twice (its inline `gate_binding`, then `_authorization_binding`), and a file
landing between them would make the binding disagree with itself and the mint and
the re-derivation diverge. Consistency, not speed.

**The cache key is `(revision, *[str(proposals_root(i)) for i in
range(len(DOCUMENTS))])`, never `revision` alone**, and this is not a detail:
every existing in-process test that re-points `IMPLEMENTATION_PROPOSALS` between
calls would otherwise read a stale answer. `functools` is **not** imported in the
engine today; a plain module-level dict keeps the import roster untouched and
lets the key carry the roots, which `lru_cache` on the bare argument cannot.

### D3 — The refusal: `DOCUMENT_REVISION_UNREADABLE`, WORK_STATE, inside `_extra_document_revisions`

**One code, not three.** Precedent: document 0's `REVISION_UNREADABLE` already
covers "no such file" and "unreadable file" under one code, because the
consumer's question is the same. The `detail` names the index, the label, the
directory, and which of the three causes fired: no family found, ambiguous
families (naming both), or a discovered name that would not read.

**Classified `WORK_STATE`, not `INVOCATION_DEFECT`** — and this asymmetry with
`REVISION_UNREADABLE` is the price of D1, stated rather than discovered. No
argument the operator can pass clears it; publishing a revision in that directory
does. `GATING_REFUSALS` gains the entry, `refusal_resolution` gains its
publication point, and the SKILL.md/usage.md roster tables gain the row —
`GatingRefusalRosterTests` goes red on any of the three being missed.

**Where it fires: inside `_extra_document_revisions`, and nowhere else.** I
re-derived the consumer set by locating every call to it and to its two
wrappers, then its enclosing `def cmd_*`:

| Consumer | Reached via | Writes? |
|---|---|---|
| `cmd_admit` | `_admissibility_extra_documents` | `tests/admissibility.json` |
| `cmd_position` | `_position_extra_documents`, twice | header + ledger |
| `cmd_gate` | inline `gate_binding`, plus its ledger/return pair | ledger |
| `cmd_offer` | `_authorization_binding`, plus its ledger/return pair | mint + ledger |
| `cmd_close` | `extra_documents`, incl. the `prior_close` comparison | ledger |
| `cmd_verify` | **no call** — its per-document path is `_extra_document_fidelity_status`, which already answers a named `"unknown"` | reads |
| `cmd_probe` | **no call** — reaches documents only through `position_state` | reads |

The proposal's measurement holds. Six writers, zero readers, so the refusal does
not contradict `revision_discovery`'s standing *"reported, never refused; `verify`
is a reader"* stance.

Keeping it inside the helper preserves that helper's existing division of labour
(*"meaningful only when a caller has already confirmed `len(DOCUMENTS) > 1`"*):
every writer inherits the refusal and none can forget it, and under one document
the loop body never executes, so the refusal is **structurally unreachable under
one** — the 28 digests protected by construction, not by assertion.

### D4 — The fixture reshape, and the red it must produce untouched

The real pair is `proposals/research-concept-rNN.md` against
`experiments/experiments-<slug>-vNN.md`. The fixture mirrors the **shape** and
never the names — the forge must stay general, so no publisher literal enters
`tests/`.

| Class | Document 0 | Document 1 |
|---|---|---|
| `TwoDocumentLifecycleTests` | `REVISION = "pair-lifecycle-r01.md"` | `REVISION_1 = "pair-lifecycle-plan-v01.md"` |
| `TwoDocumentPositionWriteTests` | `REVISION = "pair-position-r01.md"` | `REVISION_1 = "pair-position-plan-v01.md"` |

Two stems, two version letters, two roots (the roots already differ — both
classes point `IMPLEMENTATION_PROPOSALS` and `IMPLEMENTATION_PROPOSALS_1` at
separate tmpdirs; the lie was only ever the shared filename).

**Slice 1 edits `setUp` and `_doc1_sha256` only.** In each class: write document
1's file under `self.REVISION_1`, and read it back under `self.REVISION_1` in the
helper. Both are fixture lines. **Every `assert*` statement stays byte-identical**
— checked against the file as it stands, where the document-1 assertions are
`assertEqual(result["documents"], [{"label": …, "revision": self.REVISION,
"revisionSha256": self._doc1_sha256()}])` and the two `verify` assertions, none
of which slice 1 touches.

**Predicted reds — three independent mechanisms** (a claim apply must measure):

1. every `revisionSha256` comparison against `_doc1_sha256()` — the engine
   resolves document 0's name in document 1's root and answers `None`;
2. `assertNotEqual(extra_entry["status"], "unknown")` —
   `_extra_document_fidelity_status` falls through to `"unknown"`;
3. `compatibility["status"] == "ok"` — the document-1 finding's
   `uses: ['independently readable']` no longer resolves.

That red is the control the project keeps asking for: an absence measured with
instruments that could have seen a presence. Slice 2 then edits exactly the
assertions encoding the old semantics (`"revision": self.REVISION` on a
document-1 entry → `self.REVISION_1`) **inside the GREEN commit**, never the RED
one.

**Corpus the new branches need**, or they are guards no configuration can
exercise: a second same-family file in document 1's root (so the digit-tuple
`max` is a real pick, not the only candidate); one case where document 1's files
carry `MANAGED_ARTIFACT_MARKER` as first bytes and one where they do not (both
branches of the marker filter); one empty root; one root holding two different
families.

### D5 — The mutation a weaker lock survives

The obvious mutation — delete the `raise` — is caught by the sha assertions
alone, so it proves nothing about the refusal. So is "fall back to document 0's
name", since that name reads nowhere in document 1's root either.

**The mutation to run: two readable families in document 1's root, and the
ambiguity branch mutated from `raise Refused(...)` to "pick the first family."**
The command then succeeds and binds a revision the operator never chose, and
**every sha and `documents` assertion in the lifecycle classes still passes** —
the picked file is readable and its sha is real. Only an assertion on the
refusal itself catches it. That assertion therefore lives in its own class
(`TwoDocumentAmbiguousFamilyRefusesTests`) whose only claims are exit code 2, the
code string `DOCUMENT_REVISION_UNREADABLE`, and a `detail` naming **both**
families — never the exit status alone.

Anchor discipline, unchanged from Cut 3's D8: assert the old spelling's count is
exactly 1 and the new spelling's is 0 **before** the edit, and the reverse
**after**, both directions. An anchor that matched is not a mutation that ran;
`sd -s` exits 0 having changed nothing; for untracked scratch files `git diff
--stat` proves nothing, so the count is the proof. Never a monkeypatch — every
case here is a subprocess. A surviving mutation has two explanations, and apply
measures **which** before strengthening anything.

### D6 — Discovery becomes a staleness input, with no new code

Under Cut 3, `documentRevisions[i].revision` was frozen at argv. Discovered, it
can move between `offer` (mint) and `gate` (consume). `_verify_gate_authorization`
already compares it — `if "documentRevisions" in binding and
record.get("documentRevisions") != binding["documentRevisions"]` →
`GATE_AUTHORIZATION_STALE` — so publishing a new document-1 revision mid-flow
invalidates the token under the **existing** refusal, exactly as a moved `commit`
already does. `cmd_close`'s `prior_close` lookup has the same property, and there
it correctly means a close against a different document-1 revision is a new
close.

**Decision: accept it, name it, assert it. No new code and no new refusal.**
Recorded here because apply must not discover it by colliding with it.

### D7 — Wire `extra_sources` (M4)

Left dead, the entire multi branch of `position_state` is decoration.
`cmd_gate`, `cmd_offer`, `cmd_close` (both calls), `cmd_probe` and `cmd_verify`
pass `[revision_source(names[i], i) for i in range(1, len(DOCUMENTS))]` when a
revision resolved, `None` otherwise. **Rejected:** deleting the parameter — the
shape is right; the defect is that nobody fills it.

**Judged in scope** although it is a Cut-3 residual: `extra_sources` cannot be
filled correctly without the per-document resolver, so it belongs here and could
not have belonged earlier.

### D8 — `admissibility_record` pairs by label (M6)

Its extra-document loop keys the recorded list by `entry["label"]`, the way
`position_state`'s `header_documents` already does, and resolves each entry's own
recorded `revision` rather than the scalar one. One carrier, one pairing rule.

### D9 — What this change does NOT add

**No `--revision-1` per-index pin.** The operator rejected an explicit
per-document argument as the derivation, and shipping one as an "override"
reintroduces exactly *a revision you pass is a revision you asserted* for the
documents this change exists to discover. `--revision` keeps pinning document 0,
unchanged, and the argv surface does not move — which protects the 28 digests
structurally rather than by assertion. The spelling `--revision-<index>` is
**reserved** here so a later change does not invent a different one. Recorded as
an open question, not silently closed.

**`fidelityByDocument` gains `revision` per entry** (additive, under
`len(DOCUMENTS) > 1` only). Today an entry carries `{label, status}` alone, so
once document N's name is discovered independently a reader cannot see which
revision it was measured against — a gap this change creates and must close in
the same slice.

**Out, and why.** `KitAgreementLockTests._profile()`'s hardcoded skill stays
deferred, and the reason is structural rather than preference: `discover_profiles()`
globs `.claude/skills/*/impl_profile.py`, this change adds no profile there, and
the fixture lives under `tests/`. Nothing this change does can make that lock bind
two kits. The `vocabulary.names` collision belongs to the skill, not the engine.

## Data Flow

```
--revision NAME ─────────────────────────────► names[0]           (unchanged)
                                                  │
proposals_root(i>0) ─► discover_document_revision(i) ─► names[i]  (D1, seedless)
       │                    marker filter → family key → digit max
       │                              │ 0 families / >1 families / unreadable
       ▼                              ▼
document_revision_names(revision)   DOCUMENT_REVISION_UNREADABLE  (D3, WORK_STATE)
       │  memoized on (revision, *roots)          raised inside
       ▼                                     _extra_document_revisions
revision_source(names[i], i)  ── dumb reader (D2)         │
       │                                                  │  len(DOCUMENTS) > 1
       ├──► _extra_document_revisions ──┬─► _admissibility_extra_documents → admit
       │                                ├─► _position_extra_documents      → position
       │                                └─► documentRevisions   → gate / offer / close
       ├──► position_state(extra_sources=…)   (D7, previously never passed)
       ├──► admissibility_record, by label    (D8)
       └──► _extra_document_fidelity_status + fidelityByDocument[].revision (D9)

len(DOCUMENTS) == 1 → every branch above is structurally unreachable
                    → tests/seal/digests.json, 28, byte-identical
```

## File Changes

| File | Action | Description |
|---|---|---|
| `.claude/skills/_core/implementation/engine/implementation_engine.py` | Modify | `revision_source` (rule + docstring), `revision_discovery` (index), `latest_revision` (index), new `discover_document_revision` + `document_revision_names`, `_extra_document_revisions` (per-name + refusal), `admissibility_record` (D8), `_extra_document_fidelity_status`, `cmd_admit`/`cmd_verify` `sources_by_document`, the six `position_state` calls (D7), `fidelityByDocument` (D9), `GATING_REFUSALS`, `refusal_resolution`, `--revision` help (M5) |
| `tests/test_implementation_pair.py` | Modify | `REVISION`/`REVISION_1` split; new ambiguity, empty-root, marker-owned and tie classes |
| `tests/pair/corpus.py`, `tests/pair/cases.json`, `tests/pair/digests.json`, `tests/pair/unsealed.json` | Modify | new pair cases / unsealed entries with reasons |
| `tests/fixtures/two_documents/impl_profile.py` | Unchanged | already two entries, two directories; the naming lived in the tests |
| `tests/test_proposal_implementation.py` | Modify | the `index=1` fixture writing `r1.md`; `reachable_refusal_codes()` pin |
| `.claude/skills/proposal-implementation/SKILL.md`, `references/usage.md` | Modify | the new refusal's roster row |
| `openspec/specs/implementation-engine-neutrality/spec.md` | Modify | `unreached_mathematics` → `unreached_modules`, two occurrences, text only |
| `tests/seal/**`, `.claude/skills/{proposal,experimental}-deliberation/**`, `_core/deliberation/**` | **Unchanged** | `git diff --exit-code` must exit 0 |

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | `discover_document_revision` | marker-owned / hand-authored / tie / empty / ambiguous, each its own case |
| Unit | `document_revision_names` memo | two calls agree; re-pointing `IMPLEMENTATION_PROPOSALS_1` changes the key and the answer |
| Unit | `admissibility_record` by label | a recorded list in a different order than `DOCUMENTS[1:]` still pairs correctly (D8) |
| Unit | roster | `GATING_REFUSALS` classification, `refusal_resolution` publication, doc row — all three, per `GatingRefusalRosterTests` |
| Integration | the reshaped pair | two stems, two letters, end to end through `position`/`gate`/`offer`/`close`/`admit`/`verify`, real subprocesses |
| Integration | `boundTo` (D7) | document 1 reports `current`, then `stale` after its own file changes — the value M4 shows is unreachable today |
| Integration | the seal | 28 byte-identical **after each slice**, not only at the end |
| Mutation | the refusal | D5's ambiguity mutation; the sha locks must survive it and the refusal class must not |
| Mutation | the resolution | revert `document_revision_names` to return `revision` at every index; the reshaped pair reddens |
| Non-interference | sister skill | `npm test` **595/595**; `.venv/bin/python -m unittest discover -s tests` **OK, `skipped=6`** (`Ran` free to grow). Pasted before and after |

**Commit granularity.** Every work unit is two commits: a `test(...)` commit
carrying only the failing test(s), individually checkoutable with the test red at
that sha, then the implementation. Slice 1 is the exception by design — it is a
RED commit with no implementation, and its red is the deliverable.

## Threat Matrix

| Row | Applicable | Behaviour / RED test |
|---|---|---|
| Subprocess invocation | Yes (inherited) | pair + seal cases; `shell=False`, list argv, unchanged |
| Environment-variable routing | Yes | `IMPLEMENTATION_PROPOSALS`/`_1` semantics unchanged; they now also key the D2 memo. RED: re-pointing mid-process changes the answer |
| **Directory enumeration (new)** | **Yes** | Seedless discovery lists document N's root and opens each candidate for a 39-byte marker prefix. Files only; `OSError` → `False` (existing `is_managed_artifact` behaviour); no recursion, no symlink following beyond `is_file()`. RED: a directory with a subdirectory, and one with an unreadable file, both resolve without raising |
| Path traversal via profile | Yes | `documents[N].directory` stays absolute and existence-optional; a non-directory root answers `empty`, never raises |
| Data integrity of persisted records | **Yes — headline** | M3: no record on any disk carries `documentRevisions`. Asserted, not assumed, from the shipping profile's one-entry list |
| Executable-file classification | N/A | no file modes, no new entry point |
| Routing / shell commands | N/A | `COMMANDS` untouched; no new subcommand, no new flag (D9) |
| VCS / PR automation, Network | N/A | none reached |

## What Breaks

**Producers.** `revision_source`'s docstring and signature contract;
`revision_discovery`/`latest_revision` (index); `_extra_document_revisions`'s
`"revision": revision` literal (M2); `admissibility_record`'s positional pairing
(M6); `_extra_document_fidelity_status`; both `sources_by_document`
constructions; `position_state`'s nine call sites (M4); `--revision`'s help text
(M5); `GATING_REFUSALS` + `refusal_resolution` + the SKILL.md/usage.md roster;
`reachable_refusal_codes()`'s pin (**113 → 114** predicted, measure);
`test_implementation_pair.py`'s two `REVISION` constants;
`implementation-engine-neutrality`'s two `unreached_mathematics` citations.

**Products — records already on disk.**

- **Committed `.implementation/position.jsonl` in every clone: untouched.** No
  such record carries `documentRevisions` (M3), so no value this change alters
  exists in one.
- **Minted gate authorization tokens: untouched.** The key set does not move and
  the binding of a one-document record is unchanged.
- **Targets' `tests/admissibility.json`: untouched.** The additive `documents`
  key is written only under two documents; no shipping profile declares two.
- **Targets' `AGREED.md` position headers: untouched.** Same gate for the
  `documents=` group; the scalar `revision=`/`sha256=` fields are document 0's
  and unchanged.
- **`tests/seal/digests.json` (28): must stay byte-identical.** The criterion.
- **`tests/pair/digests.json`:** its two cases drive `name` only, which resolves
  before any revision is read — predicted **unmoved**, a claim apply must measure.
- **Archived reports carrying `source_digest`/`suite_digest`: untouched** — no
  digest input changes.
- **Records written by the fixture during a run: none persist.** Every box is a
  tmpdir removed in `addCleanup`.

## Migration / Rollout

No data migration; by M3 there is nothing of the changed shape to migrate.

**Slice 1 — fixture-red.** `setUp`/`_doc1_sha256` only. Paste the three predicted
reds and confirm **no fourth** test in either suite moved. Seal: 28 identical.
**Slice 2 — per-document resolution.** D1, D2, D7, D8, D9's `fidelityByDocument`
key; the assertions encoding the old semantics move in the GREEN commits. Slice 1
turns green. Seal: 28 identical.
**Slice 3 — the refusal.** D3, its roster row, D5's mutation, plus the live
`unreached_mathematics` correction. Seal: 28 identical.

One change, three chained PRs — adopted. Splitting into separate *changes* is
worse for the reason the proposal gives and I re-confirm: slice 1 alone leaves
the repo red, and slice 3's refusal cannot be mutation-proven without slice 1's
fixture.

**Size — a claim, not a fact.** Slice 1 ~120, slice 2 ~450, slice 3 ~300;
~870 total against the 1,400 budget. Every estimate this session came in over —
Cut 3 by 78% — so read this as the floor. Apply reports measured lines per slice
and does not repeat this number.

**Rollback.** Per unit, then per slice, tip-first. `tests/seal/` is untouched by
construction, so the pre-change seal is the post-revert seal. The one asymmetry:
once a second skill exists and has minted an authorization under a two-document
profile, reverting D1 strands that token. No such skill exists yet, so reverting
before `experimental-implementation` lands is clean.

## Predictions apply must measure, not repeat

- [ ] `reachable_refusal_codes()` moves **113 → 114**, exactly one.
- [ ] `tests/pair/digests.json` is **unmoved** by all three slices.
- [ ] `tests/seal/digests.json` is byte-identical **after each slice**, not only
      at the end.
- [ ] Slice 1 produces **exactly** the three predicted reds. A fourth is
      information, not noise: name it before proceeding.
- [ ] No seal case invokes `--help`, so M5's correction moves no digest.
- [ ] The D2 memo reddens **no** existing in-process test that re-points
      `IMPLEMENTATION_PROPOSALS`/`_1` between calls.
- [ ] D5's ambiguity mutation is **survived** by every sha assertion and caught
      **only** by the refusal class. If a sha assertion also reddens, the
      mutation was not the one designed and the refusal is still unproven.
- [ ] D7's wiring makes document 1's `boundTo` report `current` and then
      `stale` — a value M4 shows is unreachable today.

## Open Questions

- [x] Where document N's name comes from → **the directory's own contents** (D1).
- [x] `revision_source`'s new rule and docstring → **a dumb per-index reader** (D2).
- [x] The refusal's code, class and site → **`DOCUMENT_REVISION_UNREADABLE`,
      `WORK_STATE`, inside `_extra_document_revisions`** (D3).
- [x] How slice 1 reddens without an assertion edit → **`setUp` and one helper**
      (D4).
- [ ] **Should `--revision-<index>` ship as an explicit per-index pin?** D9 says
      no and reserves the spelling. An operator decision, left open rather than
      closed in silence.
- [ ] Disagreement between the two documents stays **reported, never judged** —
      Cut 3's recorded boundary, carried unchanged.
- [ ] M2 and F6, carried.

## Citations Checked

Located **by name** in the source during this phase: `proposals_root`,
`revision_source`, `revision_discovery`, `latest_revision`,
`_extra_document_revisions`, `_admissibility_extra_documents`,
`_position_extra_documents`, `is_managed_artifact`, `MANAGED_ARTIFACT_MARKER`,
`admissibility_record`, `_extra_document_fidelity_status`, `_bound_to`,
`position_state` (and all nine call sites), `_AUTHORIZATION_BINDING_KEYS`,
`_authorization_binding_keys`, `_authorization_binding`,
`_verify_gate_authorization`, `cmd_probe`/`cmd_admit`/`cmd_position`/`cmd_gate`/
`cmd_offer`/`cmd_close`/`cmd_verify`, `remedy_compatibility`, `GATING_REFUSALS`,
`REVISION_UNREADABLE`, `INVOCATION_DEFECT`/`WORK_STATE`,
`reachable_refusal_codes` and `GatingRefusalRosterTests` (both in
`tests/test_proposal_implementation.py`, not in the engine),
`TwoDocumentLifecycleTests`/`TwoDocumentPositionWriteTests` and their `REVISION`
constants, `tests/pair/corpus.py`'s `build`/`build_broken_second_document`,
`tests/fixtures/two_documents/impl_profile.py`'s `documents` list,
`proposal-implementation/impl_profile.py`'s one-entry `documents` list, and both
publishers' `artifact` blocks in `.claude/skills/{proposal,experimental}-deliberation/profile.ts`.

**Inherited citations that did not hold, corrected above:** the brief's
*"`revision_discovery(like)` … calls `proposals_root()` with no argument"* is
right about the call and wrong about the accessor — `proposals_root` has been
indexed since Cut 3 (M1). The proposal's *"anything else the design phase finds"*
list was incomplete in one respect that matters: `position_state`'s
`extra_sources` is declared, defaulted and **passed by nobody** (M4), and
`admissibility_record` pairs by position while `position_state` pairs by label
(M6). Neither reached this phase from any upstream document. The proposal's
containment claim and its refusal-blast-radius measurement were both
re-derived here and both hold (M3, D3).
