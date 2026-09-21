# Design: The Skill Writes the Declaration It Demands

## Technical Approach

The marker stays exactly where Decision A of `the-requirement-names-the-section-that-feeds-it`
put it — beside the directory it describes — and gains a **verb that writes it**, a **write-time
validation against that directory's real files**, a **seal read back by the same reader every
gating verb already goes through**, and a **line in the position report**. Both marker kinds
(`revisions` and `class`) share one file name, one seal convention, one writer root and one
strength statement; they keep their own disjoint key sets and their own kind-specific refusals,
which is the split `paper_region.py` already uses for its two region kinds.

    mark revisions ─┐                                    ┌─▶ read_revisions_marker ─┐
                    ├─▶ validate vs disk ─▶ paper_marker ─┤   (seal verified here)  ├─▶ write / bind / separate
    mark class     ─┘         (write-time)   .write()     └─▶ _classify ────────────┘        plan
                                                               (seal verified here)

Nothing about the marker's location, its two grammars, or `describe_binding_candidates` changes.
What changes is that a human answering `SOURCE_REVISIONS_UNDECLARED` now has a command to run,
that command checks its answer against the files it is about, and the result is visible in `plan`
before anyone hits a wall.

**Measured on this checkout before designing** (invariant 8 — nothing inherited):
`compute_plan` returns `{guidance, declarations, provenance[, sectionGuidance]}` and no verb
renders `Corpus.source_roots` at all, so the predecessor's ticked item 2.14 is false as written;
both raise sites of `SOURCE_REVISIONS_UNDECLARED` carry byte-identical text; both readers refuse
an unknown key (`read_revisions_marker` at top level *and* nested, `_classify` at top level);
`paper_declarations` imports `paper_guidance` (line 94), not the reverse; four markers exist on
this checkout — one revisions marker, three class markers — every one of them unsealed, and every
one of them untracked (`.gitignore` ignores `proposals/*`, `guidance/*/*` and `paper/*` alike).

## Architecture Decisions

### A — The declaration stays beside its root; the seal is a new key inside the marker (the fork, ruled)

| Option | For | Against | Decision |
|---|---|---|---|
| **1. Beside the root**, `<root>/.paper-writing.json` gains a self-referential digest key | Root scoping survives; one reader, one file, one lifecycle per directory; no signature grows a `paper_dir` | A second digest convention; a revert strands sealed markers the older reader refuses as malformed | **Chosen** |
| **2. A fifth `declarations`-region record kind**, marker demoted to a materialization | Reuses a proven seal and a proven hand-edit guard | Import cycle; a repo-scoped fact behind a per-paper file; one hand edit darkens every root at once | Rejected |

Four reasons, in decreasing force. A reader who disagrees should attack the first — it is the only
one that is structural rather than doctrinal.

1. **Option 2 creates an import cycle for the class marker.** `paper_declarations` imports
   `paper_guidance` today. Making the class declaration a `declarations`-region record means
   `paper_guidance._classify` must read that region, i.e. import `paper_declarations` — a cycle.
   The escapes are threading a `paper_dir` through `_classify`/`read_registry`/`classify_source_md`
   and every caller, or extracting a fourth module to hold the region reader. Both are larger than
   the seal they buy, and the second is option 1's shared module wearing a disguise.
2. **A root is classified before a paper exists.** `guidance/` folders are classified for
   ingestion and `proposals/`/`experiments/` are populated by other skills entirely; `read_bindings`
   already documents that `paper/` may legitimately not be scaffolded yet. Under option 2 a
   correct marker sitting right beside its own content would read as undeclared until somebody
   scaffolds a paper. The declaration would disappear when the paper does — the exact scope
   objection archived Decision A used to reject `papersmith.yaml`, and it lands harder here
   because the marker is already on disk and already right.
3. **Blast radius.** Option 2 puts every root's rule behind one `DECLARATIONS_HAND_EDITED`, so one
   unaware edit anywhere in the region darkens every root at once. Option 1 fails per directory.
4. **Subject.** A directory's own reading rule is a property of that directory. Decision A ruled
   this once; nothing measured since contradicts it.

**The honest cost, and why it is bounded.** Option 1 does add a second digest convention. It is
confined to one module (Decision B), and the two conventions describe two genuinely different
containers: a whole file of canonical JSON, and a `%% `-prefixed span inside a LaTeX document.
One module owns each, and neither is spelled twice. The rollback edge is real and is ruled in
Decision K — it costs one command per declared root, run before the revert, not a hand edit.

### B — One shared seal convention, in one new module: `scripts/paper_marker.py`

`paper_marker.py` owns the seal and nothing else: the key name, the canonical-bytes rule, the
digest, the shape check, the atomic write, and the strength statement. It imports stdlib and
`impl_refusals` only, so both marker modules can import it with no cycle in either direction.

It follows `paper_region.py`'s own split verbatim: **the shared module never raises the consumer's
refusal.** `paper_region` computes `current_digest` and leaves `DECLARATIONS_HAND_EDITED` /
`PROVENANCE_HAND_EDITED` to its two consumers; `paper_marker` computes `computed_seal` and leaves
`SOURCE_DECLARATION_HAND_EDITED` / `GUIDANCE_DECLARATION_HAND_EDITED` to its two. The alternative
— one shared `MARKER_HAND_EDITED` code — was rejected because it would collapse a distinction the
roster already draws between the two marker kinds' malformed codes.

    SEAL_KEY = "seal_sha256"                  # one literal, both grammars admit it from here
    canonical_bytes(obj)  -> json.dumps(indent=2, sort_keys=True, ensure_ascii=False) + b"\n"
    computed_seal(obj)    -> sha256(canonical_bytes(obj without SEAL_KEY)).hexdigest()

`sort_keys=True` is load-bearing for the same reason `paper_region.serialize_body` documents: without
it the same declaration serializes differently between runs and every second `plan` reports a
phantom hand edit.

`_atomic_replace` is copied a fourth time rather than imported from `paper_declarations` (which
would be the cycle again). `paper_block.py`, `paper_contract.py` and `paper_declarations.py`
already each carry their own copy with a docstring saying so; this one says the same.

### C — The seal is verified in the READER, never in the report

`read_revisions_marker` and `_classify` each gain six lines: shape-check the seal key, and compare
it against `computed_seal` when present. Nothing else in the skill checks a seal.

This is the whole of invariant 4 ("a guard wired only to a read-only verb is wired to nothing").
Those two readers are already on every gating path — `write` reaches them through
`resolve_section_index`, `bind` through `_resolve_bind_document`, `validate --source-md` through
`classify_source_md`, `separate` through the corpus. Putting the check in `plan` instead would
have produced a guard nine measured instances in this repository have already produced: visible,
green, and wired to nothing. `plan` inherits the refusal for free, which is the correct direction.

**An unsealed marker is a reported state, never a refusal.** Four markers on this checkout are
unsealed; sealing is what this change introduces, so demanding it would make the change break the
repository at the moment it lands. `declared-unsealed` is a first-class value of the report
vocabulary, exactly as `unclassified` and `undeclared` are.

### D — The verb is one new root, `mark`, with two modes

| Option | Tradeoff | Decision |
|---|---|---|
| One new root, `mark`, with `revisions` and `class` sub-modes (the `bib build` nesting precedent, already in this file) | Both modes write the same file name, with the same seal, in the same act — one subject, one root, one place `SKILL.md` describes | **Chosen** |
| Two roots (`declare-source`, `declare-guidance`) | Two roots for one act; the second exists only because the owner's both-kinds ruling arrived after the first was named | Rejected |
| A fifth mode of `declare` | `declare`'s four modes all write `paper/main.tex`'s `declarations` region; this writes a file beside a directory on disk — a different subject, which is precisely why `bind` got its own root | Rejected |

This applies `bind`'s test rather than copying its outcome: **same subject, same root; different
subject, different root.** `bind` split from `declare` because the subject differed. `revisions`
and `class` do not differ in subject — same file name, same grammar family, same seal, same act —
so they share a root the way `declare`'s four modes do.

**This supersedes the proposal's illustrative `declare-source` spelling.** That example was written
before the both-kinds ruling had a second mode to name; recording the change here rather than
letting the name drift silently.

    mark revisions --root <name> --revision-prefix <prefix> --ordinal-digits <n> [--unsealed]
    mark class     --folder <name> --class <value> [--guidance <dir>] [--unsealed]

**No operator string is ever joined onto a path.** `--root` is matched against the derived
declarable-root map and the path comes from the matched `SourceRoot`; `--folder` is matched against
`sorted(guidance_dir.iterdir())` and the path comes from the matched entry. Traversal is impossible
by construction, not by sanitizing.

### E — Re-recording is always available; there is no `--adopt`, and there is no stuck state

`mark` always writes. It does not read the existing marker's seal, does not require a `--reopen`,
and has no `--adopt`.

The reason is that a marker's authority does not come from continuity with its previous bytes — it
comes from the write-time validation (Decision F). Re-recording re-validates against the files
that are there now and re-seals, so the new declaration is as trustworthy as the first one was,
whatever happened to the old bytes.

The alternative — refuse an already-declared root and demand an explicit reopen — was rejected
because it recreates this change's own defect one layer up. A detected hand edit would then be
clearable by neither `--adopt` (correctly absent) nor a re-record (blocked), leaving hand-editing
the file as the only exit: a lock with no key, built by the change that exists to remove one.

This does mean anyone can overwrite a sealed declaration by running the verb. That is not a hole
the seal ever claimed to cover (Decision G); running the verb **is** using the skill, and the
values it writes are checked against disk in that moment.

### F — What is validated at write time, per kind — and what deliberately is not

`mark revisions`, in order:

1. `--root` must name a `SourceRootKind.PROSE` root of `FACT_SOURCE_ROOT` — derived, never listed.
   Otherwise `SOURCE_ROOT_UNDECLARABLE`, naming every root that is declarable and each rejected
   root's kind.
2. `--ordinal-digits` must be ≥ 1. Otherwise `MALFORMED_SOURCE_MARKER`, reused verbatim: it is a
   value-shape error on the marker being written, and the reader already owns that code.
3. The declared pattern is composed by the **same** helper `describe_binding_candidates` and
   `resolve_lineage` compose (`_revision_pattern(prefix, digits)`, extracted so the validator and
   the two listers cannot drift) and matched against `sorted(path.glob("*.md"))`. Zero matches
   refuses `SOURCE_DECLARATION_UNMATCHED`, naming the prefix, the digit count, and every `*.md`
   file it saw. A root that is not a directory at all folds into the same code with the status's
   own reason — the same "cover both cases under one code, never a seventh" reasoning Decision D of
   the predecessor used for `SOURCE_LINEAGE_UNRESOLVED`. **Nothing creates the directory.**
4. The candidate object is round-tripped through the reader's own validator before the write, so
   `mark` can never produce a marker `read_revisions_marker` refuses. `read_revisions_marker`'s
   validation body is extracted into `_validate_revisions_obj(obj, label)` and called from both.

`mark class`, in order:

1. `--folder` must be a directory directly under the resolved `guidance/`, enumerated the same way
   `read_registry` enumerates. Otherwise `GUIDANCE_FOLDER_ABSENT`, naming every folder that is
   there. **Nothing creates the folder.**
2. `--class` must be in `CLASSES`. Otherwise `UNKNOWN_GUIDANCE_CLASS`, reused verbatim.
3. Classing a second folder `evidence` while another already carries it refuses
   `EVIDENCE_ROOT_AMBIGUOUS` — reused verbatim from `_ingested_root_status` — **before** the write,
   naming both folders and the exit (re-mark the other folder first). Today that condition is only
   discovered later, by a different verb, under an unrelated message; catching it with the operator
   present is the whole point of this piece.
4. Same round-trip through `_validate_class_obj`, extracted from `_classify`.

**Deliberately not validated**: a folder classed `evidence` that holds zero ingested papers is not
refused. `_ingested_root_status` already rules that state an earlier stage and never a fault, and
a write-time check that contradicted it would put two readings of one condition inside one skill.
A class is a judgement about a folder, not a measurement of it; the only disk fact available is
that the folder exists, and that is what is checked.

### G — The seal's strength is a constant, interpolated everywhere, and tested in four places

`paper_marker.SEAL_STRENGTH` holds the one sentence:

> This seal detects an unaware edit. It is self-consistency, not tamper-proofing: the convention
> has no secret, so anyone who reproduces it can edit the file and recompute a matching seal.

Both `*_HAND_EDITED` refusal details interpolate it. `paper_marker`'s module docstring quotes it.
`SKILL.md` and `references/usage.md` carry it. A test derives the expected text from the constant
and asserts it appears in all four — so the honest wording cannot rot in one surface while staying
right in another, and strengthening the claim anywhere is a red test rather than a review miss.

This is the requirement the proposal asked for as "not a footnote", made mechanical. Overstating a
keyless digest converts a known hole into a believed guarantee, which is worse than the hole.

### H — ASK: one detail builder, two raise sites

`paper_declarations.source_revisions_undeclared_detail(status, root) -> str` is the only place the
message exists. `_resolve_bind_document` and `paper_graph.resolve_section_index` both call it.
**Byte-identity becomes structural rather than asserted** — the two sites cannot drift because
there is only one string.

The detail names the root, the marker file name, what it reads under the root *at that moment*, and
the exact `mark revisions` invocation that answers it.

`describe_binding_candidates`'s no-marker branch is the list to reuse, but calling it whole would
segment every heading of every file in order to print none. The `sorted(base_path.glob("*.md"))`
derivation is extracted into `_unmarked_candidates(base_path)` and both call it — one lister, two
callers, provably the same list, no wasted read. Growing a second lister was rejected; calling the
heavier function and discarding most of its work was rejected as reuse in name only.

### I — SHOW: a correction, scoped to `plan`, and the predecessor wording it supersedes

`compute_plan` gains `sourceRoots`, and `guidance`'s values widen from a bare class string to
`{"class": ..., "declaration": ...}`. Measured consumers of the flat shape: two assertions in
`tests/test_paper_decisions.py`, zero in `scripts/`.

One vocabulary, both reports: `"undeclared"` | `"declared-unsealed"` | `"declared-sealed"` |
`"n/a"` (the last for `REPOSITORY`- and `INGESTED`-kind roots, which have no revisions rule).
Absence reports; malformed refuses through `plan` exactly as a malformed guidance marker does
today; a broken seal refuses through `plan` for the same reason, because the check is in the reader.

The source base is `paper_dir.parent`, the identical derivation `_binding_separation_report`
already uses — not a second convention, and not `sections_dir`, which `plan` should not need for a
fact about the corpus.

**This is a correction, and the predecessor's wording is superseded, not quietly dropped.**
`2026-09-20-the-requirement-names-the-section-that-feeds-it` ticked item 2.14 claiming
`Corpus.source_roots` is "echoed by every corpus-reading verb"; measured, no verb renders it.
This design rules that wording over-broad and replaces it: **the position verb reports it.**
`phases` answers which wave is open and `contract` renders the contract; a third rendering of one
derived fact is a third place to keep in sync, and the predecessor's own failure was a claim about
three verbs that nobody ran. A claim about one verb, proven by running it and reading its output,
is worth more than a claim about three that was proven by asserting a field exists.

### J — Which roots need a declaration is derived

    declarable   := {r.name: r for r in FACT_SOURCE_ROOT.values() if r.kind is PROSE}
    reported     := {r.name: … for r in set(FACT_SOURCE_ROOT.values())}
    n/a          := r.kind is not PROSE        # REPOSITORY and INGESTED, by kind, never by name

No root name appears as a literal in any of the three. Adding a sixth root to `FACT_SOURCE_ROOT`
widens the report and the declarable set with no engine edit — held by a fixture test, the same
success criterion the predecessor's Decision B set for bindability.

The `INGESTED` root is `n/a` for `revisions` and fully in scope for `class`, per the owner's
ruling: it resolves by identity and never reaches `read_revisions_marker`, but the folder feeding
it is classified by a marker this change now writes and seals.

### K — Rollback: `--unsealed` is the pre-revert step, not a hand edit

Both readers refuse an unknown key, so a revert would leave every marker this change sealed being
refused as malformed — unreadable, not merely unsealed. The proposal named this and left design two
exits: ship an explicit rollback step, or shape the seal so the older reader still accepts it.

The second exit was examined and rejected: the only shape an unmodified older reader accepts is a
second file (`<root>/.paper-writing.seal`), which buys a free revert at the price of a second
marker filename, a second absence state, and a seal that switches off by deleting a file — against
Decision A's "one marker filename" ruling and against the shipped principle that deleting a file
must not switch a guard off.

So: `mark revisions --unsealed` / `mark class --unsealed` write the declaration in the pre-change
grammar, seal key absent. The documented rollback is *run the verb once per declared root, then
revert* — an operator action taken with the code still present, by the same verb, never an editor.
Its docstring states that its only purpose is that downgrade, and that it removes nothing a
determined editor could not remove anyway (Decision G).

## Refusal Codes — five new, three reused verbatim

| Code | Condition | Tier |
|---|---|---|
| `SOURCE_DECLARATION_UNMATCHED` | `mark revisions`: declared prefix/width matches zero `*.md` under the root, or the root is not a directory | work-state |
| `SOURCE_DECLARATION_HAND_EDITED` | `read_revisions_marker`: sealed marker's recorded seal ≠ computed seal | work-state |
| `GUIDANCE_DECLARATION_HAND_EDITED` | `_classify`: same, for the class marker | work-state |
| `SOURCE_ROOT_UNDECLARABLE` | `mark revisions --root` names a root that is not `PROSE`-kind in `FACT_SOURCE_ROOT` | work-state |
| `GUIDANCE_FOLDER_ABSENT` | `mark class --folder` names no directory directly under the resolved `guidance/` | work-state |

Reused verbatim, no new code: `MALFORMED_SOURCE_MARKER` (a bad seal-key shape, a non-positive
digit width — both shape errors the reader already owns), `MALFORMED_GUIDANCE_MARKER` (same),
`UNKNOWN_GUIDANCE_CLASS`, `EVIDENCE_ROOT_AMBIGUOUS`, `GUIDANCE_OUTSIDE_REPOSITORY`.

Two `*_HAND_EDITED` codes rather than one, per Decision B: the two marker kinds already carry
separate malformed codes, and a shared one would tell an operator less than the file path already
in the detail does not.

The roster is **154** today. The count after this lands is measured with
`reachable_paper_refusal_codes()` after the code exists, and appears in no artifact before then.

## Interfaces

```python
# scripts/paper_marker.py  (new; stdlib + impl_refusals only, so both marker modules may import it)
SEAL_KEY = "seal_sha256"
SEAL_STRENGTH: str                       # Decision G -- the one sentence, interpolated everywhere

def canonical_bytes(obj: dict) -> bytes
def computed_seal(obj: dict) -> str      # sha256 over canonical_bytes(obj minus SEAL_KEY)
def is_sealed(obj: dict) -> bool
def seal_shape_error(obj: dict) -> str | None
    """None when SEAL_KEY is absent or a 64-hex string; else the detail the CONSUMER
    raises under its OWN malformed code -- this module never invents a consumer's
    refusal (paper_region.py's own split, verbatim)."""
def write(path: Path, obj: dict, *, sealed: bool = True) -> dict
    """Canonical bytes + seal, atomic same-directory replace. Returns the written object."""


# scripts/paper_declarations.py
def declarable_source_roots() -> dict            # {name: SourceRoot} for PROSE kinds -- derived
def declaration_state(status: dict, root: SourceRoot) -> str
    """'undeclared' | 'declared-unsealed' | 'declared-sealed' | 'n/a'. Malformed and
    broken-seal propagate their reader's refusal -- never a fifth value."""
def declare_revisions(base: Path, root_name: str, prefix: str, digits: int,
                      *, sealed: bool = True) -> dict
    """Decision F. Refuses SOURCE_ROOT_UNDECLARABLE, SOURCE_DECLARATION_UNMATCHED,
    MALFORMED_SOURCE_MARKER. Round-trips through _validate_revisions_obj before writing."""
def source_revisions_undeclared_detail(status: dict, root: SourceRoot) -> str
    """The ONE detail both SOURCE_REVISIONS_UNDECLARED raise sites use (Decision H)."""


# scripts/paper_guidance.py
_MARKER_ALLOWED_KEYS = ("class", paper_marker.SEAL_KEY)   # derived, never re-spelled
def declare_class(guidance_dir: Path, folder: str, value: str, *, sealed: bool = True) -> dict
    """Refuses GUIDANCE_FOLDER_ABSENT, UNKNOWN_GUIDANCE_CLASS, EVIDENCE_ROOT_AMBIGUOUS
    (reused verbatim, BEFORE the write). Never refuses an evidence folder with zero
    ingested papers -- _ingested_root_status already rules that an earlier stage."""
```

Worked shapes, invented names throughout:

```
$ mark revisions --root experiments --revision-prefix v --ordinal-digits 3
{"root": "experiments", "revisions": {"ordinal_digits": 3, "revision_prefix": "v"},
 "matched": ["field-survey-v007.md", "field-survey-v008.md"],
 "unmatched": ["widget-calibration-notes.md"], "sealed": true}

$ plan
{"guidance": {"style-corpus": {"class": "style-reference", "declaration": "declared-sealed"},
              "scratch":      {"class": "unclassified",    "declaration": "undeclared"}},
 "sourceRoots": {"experiments": {"state": "document-rooted", "documents": 3,
                                 "reason": null, "declaration": "declared-sealed"},
                 "proposals":   {"state": "unmeasured", "documents": 0,
                                 "reason": "... holds no '*.md' documents",
                                 "declaration": "undeclared"}},
 "declarations": {...}, "provenance": {...}}
```

## File Changes

| File | Action | Description |
|---|---|---|
| `scripts/paper_marker.py` | Create | The shared seal: key, canonical bytes, digest, shape check, atomic write, `SEAL_STRENGTH` |
| `scripts/paper_declarations.py` | Modify | `declare_revisions`, `declarable_source_roots`, `declaration_state`, `source_revisions_undeclared_detail`; `_validate_revisions_obj`/`_revision_pattern`/`_unmarked_candidates` extracted; seal verified in `read_revisions_marker` |
| `scripts/paper_guidance.py` | Modify | `declare_class`; `_validate_class_obj` extracted; seal verified in `_classify`; `_MARKER_ALLOWED_KEYS` derived from `paper_marker.SEAL_KEY` |
| `scripts/paper_graph.py` | Modify | Raise site 2 calls `source_revisions_undeclared_detail` — the only edit |
| `scripts/paper_cli.py` | Modify | `cmd_mark` + the `mark revisions` / `mark class` subparsers; `compute_plan`'s `sourceRoots` and widened `guidance`; five `REFUSAL_CLASSIFICATION` entries |
| `scripts/paper_region.py` | Read | Unchanged — quoted as the precedent `paper_marker.py` mirrors |
| `SKILL.md`, `references/usage.md` | Modify | The loop (refusal → `mark` → retry), the report's new keys, `SEAL_STRENGTH` verbatim |
| `tests/test_paper_decisions.py`, `test_paper_writing.py` | Modify/New | Red-first per unit; the mutation table below |
| `tests/test_proposal_implementation.py` | Gate | Derived-denylist audit before apply |

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | Seal: canonical bytes, digest stability across runs, shape errors, absent key | Direct assertions on `paper_marker` |
| Unit | Write-time validation, both kinds, every refusal branch | Tmp roots with invented `*.md` and invented folder names |
| Unit | `mark` never writes a marker its own reader refuses | Write, then re-read through the reader, for every accepted input class |
| Integration | The whole loop | `write` refuses → run `mark revisions` → `write` proceeds, one session |
| Integration | SHOW | **Run `plan` and read its output** — never assert a field exists (the exact failure of item 2.14) |
| Integration | Seal reaches a gating verb | `*_HAND_EDITED` proven through `cmd_write` / `validate --source-md`, never only through `plan` (invariant 4) |
| Property | Derivation | A sixth `PROSE` root in a fixture becomes declarable and reported with zero engine edits |
| Property | Honest strength | `SEAL_STRENGTH` appears in the module docstring, both refusal details, `SKILL.md` and `references/usage.md` — derived from the constant |
| Generality | Invariant 1 | Derived-denylist audit over `.claude/skills/` and the suite, comments and fixtures included; `NoSubprocessScanTests` unchanged |
| Roster | Bidirectional | `reachable_paper_refusal_codes()` after the code lands; `npm test` **and** the project venv's `python -m unittest discover -s tests -p 'test_*.py'` |

**Mutation per code** — `tests/paper_mutation.py::_run_against_mutant`, each chosen so a weaker
lock survives it, each asserting its anchor count so a no-op edit cannot pass:

| Code / property | Mutation that proves it reachable |
|---|---|
| `SOURCE_DECLARATION_UNMATCHED` | Replace the zero-match guard's condition with `False`; the wrong-prefix test must go red |
| `SOURCE_DECLARATION_HAND_EDITED` | Replace the seal comparison in `read_revisions_marker` with `False`; the test driving it **through `cmd_write`** must go red |
| `GUIDANCE_DECLARATION_HAND_EDITED` | Same in `_classify`, driven through a gating verb, never through `plan` |
| `SOURCE_ROOT_UNDECLARABLE` | Replace the declarable-membership test with `True`; naming a `REPOSITORY`-kind root must go red, and no marker may appear on disk |
| `GUIDANCE_FOLDER_ABSENT` | Replace the directory test with `True`; naming an absent folder must go red, and no directory may be created |
| `EVIDENCE_ROOT_AMBIGUOUS` at write time | Delete the pre-write uniqueness check; the second-evidence-folder test must go red **and** assert the second marker was not written |
| Byte-identical ASK | Inline a literal message at one of the two raise sites; the equality test must go red |
| Honest strength | Weaken `SEAL_STRENGTH` to drop "not tamper-proofing"; the four-surface test must go red |
| Derivation, not a list | Add a sixth `PROSE` root to `FACT_SOURCE_ROOT` in a fixture; declarability and the report must follow with no engine edit |

## Work Units, and the budget

Engine lines are code under `.claude/skills/paper-writing/scripts/` only, docstrings included at
this codebase's own measured docstring-to-code ratio. Read-based estimate, per function.

| Unit | Content | Est. engine lines | Green alone |
|---|---|---|---|
| **S1** | **SHOW** — `declaration_state`, `compute_plan.sourceRoots`, `guidance` values widened, proven by running `plan`. No fork dependency; closes the false record first | ~110 | yes |
| **S2** | `paper_marker.py`; `mark revisions` + write-time validation + `--unsealed`; the seal verified in `read_revisions_marker`; S1's `declared` splits into `declared-sealed`/`declared-unsealed` **in this same unit** | ~380 | yes |
| **S3** | `mark class` + its write-time validation; the seal verified in `_classify`; `_MARKER_ALLOWED_KEYS` derived | ~135 | yes |
| **S4** | **ASK** — `source_revisions_undeclared_detail`, both raise sites, `_unmarked_candidates` extracted | ~75 | yes |
| **S5** | `SKILL.md` + `references/usage.md`, the four-surface strength test, leak audit, roster re-measured | ~0 (docs + tests) | yes |

Estimated **~700 engine lines** against the owner's 1600. **It does not push past the budget, and
it lands at roughly half the proposal's ~1550.** The difference is not optimism: the proposal
priced U2 and U3 as two sealing implementations (~600 together), and this design writes the seal
once in `paper_marker.py` and spends six lines per reader, while four extractions
(`_validate_revisions_obj`, `_validate_class_obj`, `_revision_pattern`, `_unmarked_candidates`)
move existing lines rather than adding them. The risk runs the other way now: an estimate this far
under its proposal may have missed work. Tasks must re-measure with `git diff --stat` per unit and
report an overrun rather than trimming docstrings to fit.

**S1 ships first, as its own slice.** It closes a false record rather than adding behaviour, it
needs no fork ruling, and showing the gap before closing it is the honest order. Its three-value
vocabulary (`undeclared` | `declared` | `n/a`) widens to four in S2 — the unit that first makes a
sealed marker producible. No report value is ever shippable-but-unreachable, which is the same
defect an unreachable refusal is.

Four chained PRs: PR#1 `S1`, PR#2 `S2`, PR#3 `S3+S4`, PR#4 `S5`, each targeting the previous
branch. `S4` names a command, so it cannot precede `S2`, which builds it.

```
Decision needed before apply: No   (the fork is ruled in Decision A)
Chained PRs recommended: Yes
400-line budget risk: High     (default budget)
1600-line budget risk: Low     (owner's budget for this change, engine lines only)
```

## Threat Matrix

N/A — no routing, shell, subprocess, VCS/PR automation, executable-file classification, or
process-integration boundary. Stdlib-only, keyless, offline, fail-closed, `Refused(code, detail)`
and exit 2, no `--force`, no `--adopt`. No `subprocess` import joins `scripts/`;
`NoSubprocessScanTests` is unchanged. The one adjacent surface is filesystem writes from operator
input, disposed of in Decision D: no operator string is ever joined onto a path, both write targets
come from a derived object, and neither mode creates a directory.

## Migration / Rollout

Nothing deletes or migrates a file. The four unsealed markers on this checkout keep working
untouched and report `declared-unsealed`; sealing happens the next time somebody runs `mark` for
that directory, and never before. An older revision of the code reads an unsealed marker exactly as
it does today.

Rollback is Decision K: `mark … --unsealed` once per sealed root, then revert the branch. The verb
is a new root, the report keys are additive apart from `guidance`'s value widening (two test
assertions, zero engine consumers), and the enriched refusal changes message text, never a code.

## Open Questions

None blocking. Two recorded, deliberately out of scope:

- [ ] Whether `phases` and `contract` should also render declaration state. Decision I rules them
      out for this change and supersedes the predecessor's "every corpus-reading verb" wording; if
      an operator is measured hitting the wall from those two verbs, it is a later change with its
      own evidence.
- [ ] Whether `paper_region.py`'s region digest should adopt `paper_marker`'s strength sentence
      too. Its docstrings are accurate today but never state the limit outright; a wording-only
      change to a shipped module is not this change's subject.

**S5 confirmation (tasks.md 5.14):** both items remain explicitly out of scope, not silently
resolved. `phases`/`contract` still render no declaration state anywhere (confirmed: neither
verb's implementation was touched by any phase of this change, S1 through S5); `paper_region.py`
was read-only throughout, per its own row in `File Changes` above, and carries no
`SEAL_STRENGTH`-derived wording. Both checkboxes stay unchecked on purpose — an open question
resolved by silent omission is exactly what this note exists to rule out.
