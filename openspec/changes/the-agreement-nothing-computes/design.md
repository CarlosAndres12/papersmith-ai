# Design: The agreement nothing computes — Slice D

> **Budget note.** Over the 800-word default, on the precedent Slice B's and
> Slice C's designs each record in their own Purpose, and for the reason this
> change's brief states: *mechanics concrete enough that apply invents nothing*.
> Five of the items below are corrections to inherited counts or inherited
> reach, and a correction that does not carry its own measurement is just
> another inherited count. Two of them reverse a claim the proposal made.

## Technical Approach

Three separate things, in dependency order, and the dependency is the design:

1. **A locus stops being LaTeX and becomes a per-document declaration** — a
   `block_locator` leaf that says how *this* document spells a locus, both for
   reading (`pattern`, `block_pattern`) and for writing (`identity`).
2. **A crossing resolves against that same declaration.** `[claims:39]` in the
   experiments document resolves against whatever `documents[1]`'s own
   `block_locator.pattern` finds — which, for the mathematical proposal, is
   `\tag{39}`. **No second declaration vocabulary is introduced anywhere.**
   This is why the locator lands first, and why it must be per-document.
3. **Agreement is `checkReferenceIntegrity`'s algorithm, one document over.**
   `declared` ∖ `cited` and `cited` ∖ `declared` over two documents instead of
   one. The algorithm is already proven; only the scope is new.

Four properties hold the sibling's bar structurally rather than by care:

- **Every profile declares today's exact values**, so the locator indirection is
  a zero-delta edit against `tests/seal/`'s 28 digests. Asserted, never inferred.
- **Every agreement branch is gated on `len(DOCUMENTS) > 1`** — including the
  new command's own registration, which is why `tests/seal/cases.json` does not
  gain an entry (M8 makes that mandatory, not optional).
- **The crossing form never enters the deliberation's `cites()`** (M6). The core
  is byte-untouched and no citation dangles.
- **The engine refuses and names.** No verdict word, no resolution proposal, no
  repair direction — each mutation-proven, not asserted in prose.

## Measurements from this phase — every symbol grepped by name, none inherited

### M1 — the locator's reach is SIX call sites in FOUR functions, and the fourth is a RENDERER

The proposal counted readers of the compiled `TAG_RE` object. Re-derived by
name at HEAD:

| Site | Function | What it does |
|---|---|---|
| `tags = set(TAG_RE.findall(source))` | `remedy_compatibility` | document 0's loci |
| `finding_tags = set(TAG_RE.findall(finding_source))` | `remedy_compatibility` | the named document's loci |
| `tags = TAG_RE.findall(block)` | `cmd_compose` | the remedy block's own locus |
| `tag in TAG_RE.findall(m.group(0))` | `cmd_compose` | inside the `DISPLAY_BLOCK_RE` filter |
| `tags = set(TAG_RE.findall(source))` | `cmd_admit` | document 0's loci |
| `DISPLAY_BLOCK_RE.finditer(entry)` | `cmd_compose` | the enclosing block |

**And a seventh site the proposal does not carry.** `cmd_handoff` builds
`item["deliberation"]["selectedEntryId"] = f"\\tag{{{finding[REMEDY_LOCUS_KEY][0]}}}"`
— a hardcoded LaTeX **renderer**, never routed through `TAG_RE`. Under this
domain the deliberation's own declaration form is `[exp:E1]`
(`experimental-deliberation/reference-experimental.ts::declares`, kind `tag`),
so a handoff that emits `\tag{E1}` hands the experimental deliberation a
selector its own `declares()` cannot resolve — and item 4's successor path runs
through exactly that selector.

**Consequence for the guard.** A neutrality lock over the declared *matcher*
value would pass while `cmd_handoff` still spells `\tag{`: the matcher literal
is `\\tag\{([^}]+)\}` and the renderer literal is `\tag{`. That is this
project's own "the protected half reads as proof of the whole" scar, one level
up. **The leaf is a triple — `pattern`, `block_pattern`, `identity` — or the
lock is decorative.**

### M2 — defect 1, confirmed against the corpus bytes rather than reasoned about

`tests/experiments_seal/corpus.py::REVISION_TEXT` carries no `\tag{}` at all;
its own docstring says so and names design D11 as the reason.
`FINDINGS_SOURCE` declares `experiments`/`remedy_experiments` of `["T1"]`,
`["T2"]`, `["T3"]` and (on `both-documents-citation`) `["9"]`. So in
`remedy_compatibility`, `tags` is the empty set, every declared locus lands in
`unknown_loci`, and `status` is `"incompatible"` on every `verify` case. Not a
crash — a confident wrong answer, captured in `digests.json`.

### M3 — **the proposal's "the seal MUST move" is measured false for the existing cases**

This is the sharpest correction of the phase, and it reverses an acceptance
condition.

Under the new locator, document 0's `pattern` finds the `## N` headings, so
`tags` becomes `{"1", "2", "3"}` where it was `∅`. But `missing = [e for e in
finding.get(field, []) if e not in finding_tags]` over `["T1"]` is `["T1"]`
under **both** sets, and over `["9"]` is `["9"]` under both. The emitted string
is `f"{finding['id']}.{field}: {missing}"`. **Byte-identical.** The same holds
for `dataset-0.md`/`dataset-1.md`, whose text yields `{"1"}`.

**Predicted: D1 moves ZERO of the 24 existing experiments-seal case digests.**
`__corpus_fingerprint__` moves mechanically because `corpus.py` is edited (M9),
and new entries appear for the new cases. This is B's standard —
**zero of twenty-four**, stricter than C3's six of twenty — and it is stated as
the acceptance condition: if any existing case digest moves, the cause is found
and named before anything is regenerated.

It also means **the locator's observability rests entirely on new
configurations**, not on the existing corpus. That is D1's real risk, and D6
below is the answer.

### M4 — defect 2, and the exact test C was missing

`remedy_compatibility`'s `for field in (LOCUS_KEY, REMEDY_LOCUS_KEY)` reads the
two module-level scalars, which are `document_vocabulary(0)["locus_key"]` /
`["remedy_locus_key"]`. Slice C threaded `sources_by_document` into the
function's *text* selection (`finding_source`, `finding_tags`) and left the
*key* selection scalar.

**Why C's suite could not see it.** C's spec Requirement *"Each named document's
citations are matched by its own pattern"* is discharged by `finding_impact` —
the **representation** path, which returns a `{label: class}` mapping and judges
nothing. `remedy_compatibility` is the **judgement** path (its answer becomes
`compatibility.status`) and it received no per-document assertion at all. The
corpus's fourth finding, `both-documents-citation`, proves the pattern threading
and is silent about the key threading, because its declared fields happen to be
document 0's.

**The test that would have caught it, and which D1 writes:** a finding whose
`document` is `["proposal"]` alone and which declares `remedy_equations` (document
1's own `remedy_locus_key`) naming a locus absent from document 1's text. Today
`finding.get("remedy_experiments", [])` is `[]`, nothing is missing, and the
finding reads **compatible**. That is a green assertion over an absence — the
shape this project has been removing.

**And a third consequence the proposal does not name.** `unknown_loci` is
emitted under `NOTATION_KEYS["unknown"]`, itself a document-0 scalar. Ruling
(D4): the finding's own document decides which keys are **read**; the emitted
list stays under document 0's `unknown` key, one list, one shape, with each
entry naming the field it actually read. Splitting the output key per document
would grow `verify`'s shape by one key per document — the reshape C explicitly
refused.

### M5 — the four `class` comparisons, and why the degradation is **latent, not live**

Located by name: `cmd_handoff` carries three
(`impact["class"] == "local" and finding.get("remedy_block")…`;
`impact["class"] == "local" and not finding.get(REMEDY_LOCUS_KEY)`;
`elif impact["class"] == "local"`), and `cmd_verify` a fourth inside
`local_remedies_not_written`.

**But both call sites pass two arguments.** `cmd_handoff` calls
`finding_impact(finding, source)` and `cmd_verify` calls
`finding_impact(f, source or "")` — neither supplies `sources_by_document`, and
`finding_impact` builds the mapping only when that argument is given AND
non-empty. So **no mapping reaches those four comparisons today**; the silent
fall-through to `deferToOwnSession` is latent.

It becomes live the moment the cross-document consequence is threaded in, which
is precisely what D5 delivers. **The RED test is therefore the deliverable's own
first commit**: thread the mapping, watch all four comparisons answer `False`,
and watch every finding defer with no refusal. That is red against the shipped
engine for a reason no assertion author chose.

### M6 — the crossing form must NOT join the deliberation's `cites()`

`checkReferenceIntegrity` (`_core/deliberation/engine/reference-index.ts`)
computes `resolved: cited.every(value => known.has(value))` where `known` is
`declaredValues(source)` — **the same document's** declarations. Adding
`[claims:N]` to `experimental-deliberation/reference-experimental.ts::cites`
would make every crossing an unresolved reference in its own document and fail
deliberation validation — the exact cost the operator's ruling paid to avoid by
not re-pointing `[tests:X]`.

**So `reference-experimental.ts` is byte-unchanged.** The form is documented in
`experimental-deliberation/SKILL.md` and asserted negative in a test:
`cites("Sustains claim [claims:39].")` returns `[]`. That assertion is the guard
against a later agent adding it "for completeness". `declares` is likewise
untouched.

### M7 — the accept-turn blocker: the recorded cause is not in the source

`experimental-deliberation/SKILL.md`'s *"Known limit: the accept turn does not
publish in this domain"* (measured 2026-09-08) records the cause as
*"`proposal-workspace-adapter.ts` derives the published revision label by
matching the target filename against a hardcoded `-r(\d+)\.md$`, and re-checks
it against `^r\d{2,}$`."* Re-derived by name at HEAD:

| Claim | Measured |
|---|---|
| hardcoded `-r(\d+)\.md$` | **Absent.** `publishSuccessor` computes `targetFilename = nextSuccessorTarget(input.sourceFilename)`, then `parseManagedRevision(targetFilename)?.revision` |
| `parseManagedRevision`'s matcher | `LAX_RE` ← `LAX_SOURCE = ^${ESCAPED_STEM}-(?:(.+)-)?${REVISION_PREFIX}(\d+)\.md$` |
| `REVISION_PREFIX` | `escapeRegExp(DOMAIN.artifact.revisionPattern)` — **profile-derived** |
| this domain's value | `experimental-deliberation/profile.ts`: `revisionPattern: "v"`, `stem: "experiments"` |
| `nextSuccessorTarget` | `parseRevisionIncrement` ← `INCREMENT_SOURCE`, same profile-derived prefix |
| the re-check `^r\d{2,}$` | `strictRevisionLabel`, ← `STRICT_REVISION_LABEL_SOURCE = ^${REVISION_PREFIX}\d{2,}$` → `^v\d{2,}$` here |

For `experiments-<slug>-v03.md`: increment gives `…-v04.md`, LAX gives `v04`,
STRICT accepts `v04`. **Neither literal is hardcoded and both are satisfied.**

**This is not a claim that the accept turn publishes.** No suite was run in this
phase. It is a claim that a dated diagnosis no longer describes the code, and
that **D5 must drive resolve → preview → accept end to end and report what
actually happens** before item 4's outcome is priced or promised. This project
has already been misled in both directions by an undated "pre-existing".

### M8 — a new command in `COMMANDS` breaks the bar, structurally

`tests/test_implementation_seal.py::SealMembershipTests::test_the_case_roster_covers_the_command_roster_exactly`
asserts `{c["command"] for c in tests/seal/cases.json} == set(impl.COMMANDS)`,
and `test_every_case_is_either_sealed_or_declared_unsealed` asserts
`digests | unsealed == cases`. **An unconditionally registered new command
therefore forces an edit to `tests/seal/cases.json` and `tests/seal/digests.json`
— which `git diff --exit-code tests/seal/` refuses.**

That is not an obstacle to route around; it is the design constraint that
selects D9's conditional registration, and it makes the bar mutation-provable:
delete the `len(DOCUMENTS) > 1` gate and the **sibling's own suite** goes red.

### M9 — the two corpora, counted here, not inherited

- `tests/seal/cases.json`: **29** cases. `tests/seal/digests.json`: **29**
  top-level keys = `__corpus_fingerprint__` + **28** case digests. `propose`
  carries no digest (non-deterministic, recorded in `unsealed.json`). The
  proposal's 28 is confirmed; the 29/29 decomposition is new.
- `tests/experiments_seal/cases.json`: **24** cases.
  `tests/experiments_seal/digests.json`: **25** keys = fingerprint + **24**.
  The proposal's "20 cases / 21 keys" was Slice C's reading, before B2 added
  four. **Re-derive again at apply.**
- Five of the 24 are `verify`: `verify-a`, `verify-b`, `verify-a-declared`,
  `verify-b-declared`, `verify-b-undeclared`. `verify-a` and `verify-b` share
  one sha256 (`e7587be7…`, 20743 bytes) — B4's self-fulfilling `with_data`
  erases their only difference. Not D's to fix.
- `CORPUS_FINGERPRINT_SOURCE = Path(__file__)`: **any** edit to `corpus.py`
  moves `__corpus_fingerprint__`, case movement or not. Mechanical; separate it
  from case movement before accepting anything (B's M6, carried).

### M10 — the reaching configurations that already exist, and the one that does not

B's standard, applied before authoring anything:

| Thing to prove | Reaching configuration | Authored? |
|---|---|---|
| The locator's **matcher** half | `tests/seal/corpus.py` already carries `$$ … \tag{1.1} $$` display blocks and `remedy_block`s spelling `\\tag{1.1}` — authored at Cut 1 for an unrelated purpose | **No.** A `MUTATIONS` entry flips the sibling's declared matcher; `compose`, `admit-e0/e1`, `verify-a/b/t` are the predicted movers |
| The locator's **renderer** half | the sibling's findings declare `remedy_block`, so `cmd_handoff`'s `inline` branch is reached and `selectedEntryId` is emitted | **No.** `handoff-e0/e1` are the predicted movers |
| **Fail closed once** (no crossing declared at all) | `tests/experiments_seal/corpus.py::REVISION_TEXT`, authored at Slice A, declares zero crossings | **No** |
| The **two discrepancy kinds** | nothing on disk declares a crossing, and `PROPOSAL_REVISION_TEXT` declares no `\tag{}` at all | **Yes — unavoidable, and said plainly** |
| The **per-document locus key** (M4) | no finding on disk names document 1 alone | **Yes — unavoidable** |

For the two unavoidable ones, the defence is not that the fixture is small but
that **the fixture supplies both directions and the negative one is the
acceptance condition**: a crossing that resolves must produce no discrepancy,
and the inverse control must produce one. A fixture that could only ever
satisfy the guard proves nothing; a fixture carrying its own inverse cannot be
satisfied by a guard that ignores its input.

### M11 — the two locks D must not trip

- `L1_EXPECTED_COUNT = L1_BASELINE_AT_S0 (97) − L1_DELIBERATE_SHRINK (1) = 96`,
  counting `\bproposal\b` case-insensitively over `_engine_files()`;
  `L1_EXPECTED_FILES = ["implementation_engine.py"]`. **D writes engine prose
  about "claims the proposal declares" — a live hazard.** Rule, C's D9 carried:
  engine prose says *document 1*, *the crossed document*, or *the document's
  declared label*. Never `proposal`. Never a silent pin bump.
- `reachable_refusal_codes()` is pinned at **114** and `GATING_REFUSALS` must
  classify every code it reaches. Every new `Refused` moves the pin and needs a
  classification. `ImplementationProfileError` codes are invisible to that walk.

## Architecture Decisions

### D1 — `documents[N].block_locator`: a required triple, never a callable

```python
"block_locator": {
    "pattern":       r"\\tag\{([^}]+)\}",      # one capturing group: the locus value
    "block_pattern": r"(?s)\$\$.*?\$\$",       # the enclosing substitutable block
    "identity":      "\\tag{{{value}}}",       # str.format, exactly one field: {value}
},
```

Required on every `documents[N]` entry, **non-nullable**, joining
`dataset_marker`'s own required tier — appended after it so existing
`..._INCOMPLETE` message ordering is unchanged. **Not** a member of
`_DOCUMENT_VOCABULARY_LEAVES`: dragging the all-or-nothing five over it would
force every entry of every profile into a full overlay, a behavioural change D
does not want (B's D1, same reasoning).

| Option | Consequence |
|---|---|
| A profile-supplied **callable** | Un-renderable in `profile_values_text`, un-validatable in shape, and the kit crossing the seam. Rejected — B's D1 rejected it for the identical reasons |
| Matcher only (the proposal's shape) | `cmd_handoff` keeps spelling `\tag{`, and the neutrality lock passes over half the coupling (M1). Rejected |
| **Matcher + block + renderer** | Every one of the seven sites reads a declared value; the lock is non-vacuous the day it lands |

**Nullable rejected.** Every document has loci; a `None` everywhere would make
the leaf a zero-mover, the unprovable-field shape nine changes have removed.

**The inline `(?s)`.** `DISPLAY_BLOCK_RE` is compiled today with `re.DOTALL`.
The declared value carries the flag inline so the resolver can compile every
pattern flag-free, and so the sibling's declared value is behaviourally
identical to today's. Apply asserts the sibling's 28 digests, never infers.

**Resolver tier** (new, after the `dataset_marker` check, before the
`citation_pattern` group tier): all three sub-keys present or each missing one
is named at its exact indexed path
(`documents[1].block_locator.identity`) under the existing
`IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` accumulator; then
`IMPLEMENTATION_DOMAIN_PROFILE_INVALID_BLOCK_LOCATOR` for: a pattern that does
not compile, a `pattern` whose `.groups` is not exactly **1**, or an `identity`
whose `string.Formatter().parse` yields anything other than exactly one field
named `value`. All `ImplementationProfileError` — M11's pin does not move.

**Group count 1, not 3.** `citation_pattern` requires three because
`_impact_class` reads `group(1) or group(2) or group(3)`. The locator's reader
takes one value. **Copying the three-group rule here would enforce a count
nothing reads** — a validator whose reason does not apply is indistinguishable
from one that works. Named because it is the most likely thing apply gets wrong.

### D2 — the accessor, and which scalars are re-derived

```python
def document_block_locator(index: int) -> dict:
    """Document `index`'s compiled locus matcher, block matcher and identity
    template. Compiled ONCE at import, per index -- never per finding."""

TAG_RE = document_block_locator(0)["pattern"]
DISPLAY_BLOCK_RE = document_block_locator(0)["block_pattern"]
```

Both identifiers survive, re-derived at index 0, so the six existing reader
lines are byte-unchanged — C's D2 precedent exactly, and a zero-delta edit that
must be **asserted** on the sibling's 28, not inferred.

Rejected: deleting `TAG_RE` and rewriting all six sites in one commit. That
conflates "the leaf is read" with "the sites were rewritten correctly", and a
green suite could not tell which half is working.

### D3 — which document each site reads, stated per site

| Site | Locator used | Why |
|---|---|---|
| `remedy_compatibility`, document-0 fallback | index 0 | unchanged meaning |
| `remedy_compatibility`, per finding | the document(s) the finding names | the finding's own scope (D4) |
| `cmd_admit`'s `tags` | index 0 | already document-0 scalar by design; its per-document path is `finding_impact(…, sources_by_document)`, landed by C |
| `cmd_compose` (block + tag) | the **single** document the finding names | composing a replacement requires knowing whose syntax to write |
| `cmd_handoff`'s `selectedEntryId` | the single document the finding names | it is the selector that document's deliberation will resolve |

**A finding naming BOTH documents refuses `COMPOSE_AMBIGUOUS_DOCUMENT`**, gated
on `len(DOCUMENTS) > 1` so the sibling is structurally untouched. Rejected:
silently picking index 0 — that writes LaTeX into an experiments document and
calls it a remedy. Pin 114 → **115** after D1; measure.

### D4 — `remedy_compatibility` per document: keys read per finding, one output shape

```python
for label_index in finding_document_indices(finding):      # [0] when none named
    vocab = document_vocabulary(label_index)
    for field in (vocab["locus_key"], vocab["remedy_locus_key"]):
        missing = [e for e in finding.get(field, []) if e not in finding_tags[label_index]]
```

- `finding_tags` becomes per index, each built with **that index's own**
  `block_locator.pattern` against **that index's own** text.
- The emitted list stays under `NOTATION_KEYS["unknown"]` (document 0's key),
  one list, one shape (M4). Each entry already names its field, so the reader
  can tell `experiments` from `equations` without a key per document.
- A finding naming a label whose source is unreadable keeps C's existing
  behaviour: empty text, empty tag set — unknown, never silently re-checked
  against document 0.

**Rejected:** emitting `unknownExperiments` **and** `unknownEquations`. That
grows `verify`'s output by one key per declared document and moves the reshape
C deliberately refused into a slice that is not about reshaping.

### D5 — `documents[N].cross_citation`: pattern plus an explicit target label

```python
"cross_citation": {
    "pattern":          r"\[claims:([A-Za-z0-9][A-Za-z0-9._-]*)\]",  # one group
    "resolves_against": "proposal",                                   # a declared label
},   # or None -- this document cites no other document
```

Required key, **nullable**: `documents[1].cross_citation = None`, because the
mathematical proposal cites no experiments document. Exactly one capturing
group, same reasoning as D1. The identifier class is copied from
`reference-experimental.ts::IDENTIFIER` so a crossing id is spelled exactly as
that domain already spells identifiers.

| Option for the target | Consequence |
|---|---|
| "the other document" | Unambiguous at two documents, undefined at three. A rule that stops meaning anything the day a third is declared |
| index + 1 | Positional magic; a reordered `documents` list silently re-points every crossing |
| **An explicit `resolves_against` label** | Refused by name (`…_UNKNOWN_CROSS_DOCUMENT`) when it names no declared label, or names its own entry |

**What a crossing resolves against: the target document's own
`block_locator.pattern` findings.** Nothing else. That is the whole reason D1
lands first: `[claims:39]` resolves against `\tag{39}` because `documents[1]`
declares the LaTeX matcher, and **no third vocabulary is introduced**. A
migration cost of zero is not a coincidence here — it follows from reusing the
declaration the target document already makes.

### D6 — the resolver, and it is `checkReferenceIntegrity` one document over

```python
def crossing_state(index: int) -> dict:
    """`{"crossed": [...], "declared": [...], "absent": [...], "untested": [...]}`"""
```

- `crossed` = `cross_citation.pattern` findings in document `index`'s text.
- `declared` = `block_locator.pattern` findings in the target document's text.
- `absent` = `crossed − declared` — **kind 1**: the experiments document tests a
  claim the proposal no longer declares.
- `untested` = `declared − crossed` — **kind 2**: the proposal declares a claim
  no experiment tests.

Two set differences over two lists. Byte-decidable, order-independent, and
neither direction requires reading what either document *means* — which is
exactly why the third kind (D11) is a tutor bullet and never a check.

**Ordering and duplicates.** Both lists are sorted and de-duplicated before
emission, so the refusal's payload is a function of the documents and not of
their reading order. A crossing repeated twice is one discrepancy, not two.

### D7 — the two refusal codes, and why one refusal carries both lists

1. **`AGREEMENT_CROSSING_UNDECLARED`** — the declaring document's `crossed` list
   is empty. Fires **alone and once**, never N times, and the other two lists
   are not computed: with no crossing at all, every declared claim would be
   "untested" and the refusal would be N discrepancies wearing a code. This is
   the operator's fail-closed-once rule, and it is the one refusal with a
   reaching configuration already on disk (M10).
2. **`AGREEMENT_DOCUMENTS_DISAGREE`** — one refusal carrying two named lists,
   `claimAbsent` and `claimUntested`, plus `unacknowledged`.

| Option | Consequence |
|---|---|
| One code per kind | The operator acknowledges ids from one list, re-runs, and is refused by the other. Two turns for one reading |
| **One code, two lists** | The whole disagreement is on screen at once, and one acknowledgment turn can clear ids from either list — the `acknowledgedRemovals` shape |

Both classified `WORK_STATE` in `GATING_REFUSALS`: nothing the caller can retype
clears them; somebody has to change a document. `position`'s own precedent.
Pin 115 → **117**; measure.

**Discrepancy ids are derived, never positional:** `absent:<value>` and
`untested:<value>`. A positional id renumbers when a claim is added and
silently re-points an acknowledgment.

### D8 — acknowledgment: per id, exact, request-scoped

`--acknowledge <id>`, repeatable. Clears **only** ids echoed back exactly; the
remainder still refuses, and the refusal's `unacknowledged` list names it.
A general "continue" clears nothing because no such flag exists.

**Request-scoped, matching `acknowledgedRemovals`** (nothing persists it on the
deliberation side). Rejected: a durable record in `position.jsonl`. That ledger
travels in clones, so an acknowledgment made against bytes that have since
changed would keep clearing a discrepancy nobody re-checked — the
`POSITION_STALE` defect class, one surface over, and this change would be
introducing it rather than refusing it.

### D9 — where the check lives: a new command, registered only under two documents

```python
COMMANDS = {..., "defect": cmd_defect, "materialize": cmd_materialize,
            **({"agree": cmd_agree} if len(DOCUMENTS) > 1 else {})}
```

| Option | Consequence |
|---|---|
| Inside `verify` | `verify` is a reader by standing position ("reported, never refused"). A refusal there breaks a contract seven changes rest on. Rejected, as the proposal assumed |
| Inside `admit` | `admit` refuses `NO_FINDINGS` first, so a repository with no findings could never learn its documents disagree. Agreement is a property of the documents and must be decidable with zero findings. Rejected |
| Unconditional new command | **Forces an edit to `tests/seal/cases.json` and `digests.json`** (M8). Refused by the bar |
| **Conditional new command** | The sibling's `impl.COMMANDS` is unchanged, so `tests/seal/` is untouched — and deleting the gate reddens the **sibling's own** membership test |

`agree` joins `GATING_COMMANDS` (it refuses on the repository's own state and can
stop a session dead — `position`'s stated criterion), so
`reachable_refusal_codes()` can see its codes. It takes **its own**
`--revision` registration, a fourth site, rather than joining the eight-name
set: widening that set would add a flag to the sibling's parser and move its
digests. B's W1 correction set the precedent — `plan` got its own too.

### D10 — the consumer: one accessor, and a refusal about the world rather than the engine

**The shape half.** All four `impact["class"] == "local"` comparisons become one
module-level `local_reach(impact) -> bool`, handling both shapes: a plain
string, or a mapping in which **every** named document must read `local`. The
reach is the union — a remedy that is local in one document and structural in
the other is structural. Proven by mutation: revert `local_reach` to the string
comparison and the two-document handoff case dies.

Rejected: a refusal for a mapping reaching a string comparison. The engine
constructs both shapes itself, so such a refusal fires only on an engine defect
and reads exactly like a guard that works — the shape this project removes.

**The silence half, which is about the world and therefore is a refusal.**
`cmd_handoff` gains `sources_by_document`, built exactly as `cmd_admit` builds
it (`document_revision_names`, gated on `len(DOCUMENTS) > 1`), and refuses
**`HANDOFF_DOCUMENT_UNREADABLE`** when a finding names a declared document whose
revision cannot be read. Today `cmd_handoff` reads document 0 alone and cannot
notice; without this, a finding against both documents routes on document 0's
text while the second is missing, and nothing says so. Precedent:
`DOCUMENT_REVISION_UNREADABLE` at the binding-write sites. Pin 117 → **118**.

`cmd_handoff` gains one additive key per item, `impact.class` already being the
mapping; the new `deferredBecause` value is `structural-in-another-document`,
and **its prose is written in the same hardcoded Spanish as its three
neighbours**. M2 stays recorded and unresolved: translating one of four would
make the output bilingual and is a behavioural delta the seal must refuse.

### D11 — the third kind is a tutor bullet, and the boundary is mutation-proven

*The experiment's metric or protocol does not correspond to what the claim
asserts* goes into `experimental-implementation/SKILL.md` as guidance. Judging
it requires reading both documents; a check that tried would block correct work
and pass broken work.

The boundary — **no verdict word, no resolution proposal, no repair direction** —
is a spec requirement with its own mutation: add a `suggestion` key to
`cmd_agree`'s payload and a lock over the returned key set goes red. Reading the
source is not the proof; `deliberated` having no observable condition is the
standing precedent for why.

### D12 — landing order, and D3 splits

The proposal's four become **five**. D1 grows (M1's renderer, M4's key loop,
D3's ambiguity refusal, fixture T); D3 splits at exactly the seam the proposal
predicted; the consumer, the successor and Flow B stay together because they are
one story and share one gate.

| Slice | Delivers | Gate at the end | Estimate |
|---|---|---|---:|
| **D1** | `block_locator` triple + tier + refusals + accessor (D1/D2); all six `TAG_RE`/`DISPLAY_BLOCK_RE` sites and `selectedEntryId` re-pointed (D3); `remedy_compatibility` per-document keys (D4); `COMPOSE_AMBIGUOUS_DOCUMENT`; `LockD`; fixture T + three new cases; `compose`/`admit` leave `unsealed.json` | Sibling's 28 byte-identical; **zero** of the 24 existing experiments cases moved (M3); the sibling mutation entries measured | 750–1,150 |
| **D2** | `cross_citation` leaf + tier + refusals (D5); `crossing_state` (D6); the corpus's crossing axis; the deliberation-side documentation and the `cites()` negative assertion (M6) | The resolver's unit matrix, both directions; `reference-experimental.ts` byte-unchanged | 500–800 |
| **D3** | `cmd_agree`, conditionally registered (D9); the two refusal codes (D7); `GATING_REFUSALS`; the roster pin | Each refusal mutation-proven, its corpus case named **before** its assertion; the sibling's membership test reddens when the gate is deleted | 600–950 |
| **D4** | `--acknowledge` per exact id (D8) | A case with **two** discrepancies: one acknowledged clears one | 300–500 |
| **D5** | `local_reach` at all four sites; `HANDOFF_DOCUMENT_UNREADABLE`; the cross-document consequence; the successor handoff; **Flow B to a submission**; the tutor bullet; `SKILL.md` | A finding against BOTH routes correctly, RED-first; M7 re-measured end to end and **reported, not promised** | 600–950 |
| | | | **2,750–4,350** |

**Above the proposal's 2,000–3,350, deliberately, and the overage is itemised**:
the locator is a triple with a seventh site (M1); `remedy_compatibility` needs
the output-key ruling and its own control (M4); fixture T is a real third
fixture with its own `findings.py`; the acknowledgment is its own slice; and
**`experimental-implementation/SKILL.md` contains no Flow A and no Flow B at
all** — measured this phase — so "Flow B to a submission" is authored, not
amended. Every estimate this session came in over except the one that priced its
proof (865 against an ~870 floor), so read this as the **floor**. Apply reports
measured lines per slice and does not repeat these numbers.

Against `review_budget_lines: 1400`: **no slice may merge unstacked**, and D1 is
the one to watch — if its measured lines pass 1,150, the `remedy_compatibility`
key loop (D4) splits out behind its own commit and its own digest capture.

```text
Decision needed before apply: Yes
Chained PRs recommended: Yes
400-line budget risk: High
```

### D13 — fixture T, and why it is not a fixture written to satisfy a guard

`tests/seal/harness.py::_fixture_path` already evaluates
`{"A": …, "B": …, "T": roots.fixture_t}` unconditionally, and
`experiments_seal/corpus.py::Roots.fixture_t` is currently **aliased to
`fixture_b` because no case names it** — its own comment says so. That is a free
slot the harness already carries.

D1 makes T a real fixture with **its own `findings.py`**, carrying one finding
whose locus is spelled the way this domain's document actually spells one, and
whose `remedy_block` is written in this domain's own block form. Fixtures A and
B keep `FINDINGS_SOURCE` byte-unchanged, which is what keeps M3's zero-movement
prediction true.

Three new cases, and nothing else: `compose-t` (the locator substitutes into a
heading block), `admit-t` (loci resolve, so `admitted` is non-empty — the first
case in this corpus where a locus is *not* unknown), `verify-t` (the compatible
direction, the negative control for M2's confident wrong answer).

## Data Flow

```
PROFILE["documents"][N]["block_locator"]  ── resolver tier (D1) ──┐
                                                                   ▼
                                         document_block_locator(N) = {pattern,
                                                                      block, identity}
             ┌──────────────┬──────────────┬──────────────┬────────┴────────┐
             ▼              ▼              ▼              ▼                 ▼
   TAG_RE = …(0)   remedy_compatibility  cmd_compose   cmd_admit   cmd_handoff
   DISPLAY_BLOCK   per finding: tags(N)  block+tag(N)  tags(0)     identity(N)
   = …(0)          + keys(N)   (D4)      (D3)                      -> selectedEntryId
                                                                        │
PROFILE["documents"][N]["cross_citation"] ── resolver tier (D5) ──┐     │
                                                                   ▼     │
                          crossed = cross_citation.pattern(text of N)    │
                          declared = block_locator.pattern(text of M)    │
                                       M = resolves_against label        │
                                                │                        │
                                                ▼                        │
                        crossing_state(N) = {crossed, declared,          │
                                             absent, untested}   (D6)    │
                                                │                        │
   crossed == []  ──► AGREEMENT_CROSSING_UNDECLARED, once          (D7)  │
   absent|untested ─► AGREEMENT_DOCUMENTS_DISAGREE + unacknowledged (D7) │
                          ▲                                              │
                   --acknowledge <exact id>  (D8)                        │
                                                                         ▼
                 cmd_handoff: finding_impact(…, sources_by_document)
                              local_reach(impact)  at 4 sites      (D10)
                              -> settleInline | deferToOwnSession
                                        │
                                        ▼   replacementText (cmd_compose)
                          experimental-deliberation: RESOLVE_TARGET
                                    -> CREATE_SUCCESSOR preview -> accept   (M7)

   len(DOCUMENTS) == 1  ──► `agree` is not registered; every branch above
                            unreachable ──► tests/seal/, 28 + 29 keys, untouched
```

## File Changes

| File | Action | Slice | Description |
|---|---|---|---|
| `.claude/skills/_core/implementation/impl_domain_profile.py` | Modify | D1, D2 | `block_locator` required tier + `…_INVALID_BLOCK_LOCATOR`; `cross_citation` tier + `…_INVALID_CROSS_CITATION_PATTERN` + `…_UNKNOWN_CROSS_DOCUMENT`. **Its prose may not spell `Data`/`tests`/`src`/`tools`/`Notebooks`/`Results`/`Models`** (B's M3) |
| `.claude/skills/_core/implementation/engine/implementation_engine.py` | Modify | all | `document_block_locator`; `TAG_RE`/`DISPLAY_BLOCK_RE` re-derived (D2); six sites + `selectedEntryId` (D3); `remedy_compatibility` per-document keys (D4); `crossing_state` (D6); `cmd_agree` + conditional `COMMANDS`/parser + `GATING_COMMANDS` (D9); `local_reach`, `sources_by_document` in `cmd_handoff`, `HANDOFF_DOCUMENT_UNREADABLE` (D10) |
| `.claude/skills/proposal-implementation/impl_profile.py` | Modify | D1, D2 | Today's exact LaTeX values as declared leaves; `cross_citation: None`. **Zero-delta — asserted on 28 digests** |
| `.claude/skills/experimental-implementation/impl_profile.py` | Modify | D1, D2 | `documents[0]`: heading locator + `[claims:…]` crossing → `"proposal"`. `documents[1]`: LaTeX locator, `cross_citation: None` |
| `.claude/skills/experimental-implementation/SKILL.md` | Modify | D1, D5 | `compose`/`admit` leave "not available yet"; the tutor bullet; **Flow B, authored**, through to a test submission |
| `.claude/skills/experimental-deliberation/SKILL.md` | Modify | D2, D5 | The `[claims:N]` form documented; M7's "Known limit" re-measured and re-dated, or removed with its measurement |
| `.claude/skills/experimental-deliberation/reference-experimental.ts` | **Untouched** | — | M6: adding the form to `cites()` dangles every crossing |
| `tests/fixtures/two_documents/impl_profile.py` | Modify | D1, D2 | The two new required leaves; invisible to `discover_profiles()` |
| `tests/experiments_seal/corpus.py`, `cases.json`, `digests.json`, `unsealed.json` | Modify | D1–D4 | Fixture T + its `findings.py` (D13); the crossing axis; new cases; `compose`/`admit` un-excluded |
| `tests/test_implementation_domain_mutation.py` | Modify | D1 | `MUTATIONS` + `MEASURED_MOVERS` for the matcher and the renderer — **measured**, never forecast into the table |
| `tests/test_implementation_domain_lock.py` | Modify | D1 | `LockDDeclaredLocatorTests` (below) |
| `tests/test_implementation_profile.py` | Modify | D1, D2 | The per-sub-key refusal matrix, per index |
| `tests/test_proposal_implementation.py` | Modify | D1, D3, D5 | `reachable_refusal_codes()` pin; per-code classification tests |
| `tests/seal/**`, `proposal-implementation/**` (except its one profile), `proposal-deliberation/**`, `_core/deliberation/**` | **Untouched** | — | the bar: `git diff --exit-code tests/seal/` exits 0 after **each** slice |

**`LockDDeclaredLocatorTests`** (B's `LockC` shape, and stronger): for every
profile `discover_profiles()` finds, for every `documents[N].block_locator`,
assert **each of the three declared literals** appears in no file under
`ENGINE_DIR`. Non-vacuity asserted. It is **non-vacuous the day it lands**,
because both shipped profiles declare a non-null locator — unlike B's `LockC`,
which had to wait for B2. This is the lock M1 says a matcher-only leaf would
have let pass.

## What Breaks — Producers and Products

| Class | Item | Verdict |
|---|---|---|
| Producer | `TAG_RE`, `DISPLAY_BLOCK_RE` | Re-derived through `document_block_locator(0)`; identifiers survive, **values identical — assert, do not infer** |
| Producer | `remedy_compatibility` signature | Unchanged; its internals go per-document. Its docstring's "document 0's tags" claim is **deleted, because the property is gone** |
| Producer | `cmd_compose`, `cmd_admit` | Read declared locators; `cmd_compose` gains one refusal under two documents only |
| Producer | `cmd_handoff` | Gains `sources_by_document`, `local_reach`, one refusal, one `deferredBecause` value. **M2 unresolved and unchanged** |
| Producer | `COMMANDS`, `main()`'s parser loop, `GATING_COMMANDS` | Gain one conditional entry. Under one document, byte-identical iteration |
| Producer | `_resolve()`'s per-entry walk | Two appends after `dataset_marker`; existing message ordering unchanged |
| Producer | `reachable_refusal_codes()` pin (114) | **Predicted 118** across D1/D3/D5. Measure per slice; never a bulk bump |
| Producer | `L1_EXPECTED_COUNT` (96) | **Live hazard** — D writes prose about the proposal document. Engine prose says *document 1*. Measure |
| Producer | `checkReferenceIntegrity`, `declares`, `cites` | **Untouched, and asserted so** (M6) |
| **Product** | `tests/seal/digests.json` (28 digests, 29 keys) | **Untouched**, asserted after **each** slice |
| **Product** | `tests/seal/cases.json` (29 cases) | **Untouched** — D9's conditional registration is what makes that true (M8) |
| **Product** | `tests/pair/digests.json` | Predicted unmoved; its cases run `name`. Measure |
| **Product** | `tests/experiments_seal/digests.json` (24 cases, 25 keys) | **Grows.** Predicted: **zero existing case digests move** (M3); `__corpus_fingerprint__` moves mechanically; new entries per new case |
| **Product** | Targets' committed `__provenance__` | **Untouched.** No provenance schema change; the crossing lives in documents, not in code — the whole reason option 2 was refused |
| **Product** | Targets' `tests/findings.py` on disk | **Untouched.** No finding field is added or renamed; `document` already accepts a list |
| **Product** | Targets' `tests/admissibility.json` | **Untouched shape.** `cmd_admit` writes the same keys; only the loci it judges are read through a declared matcher |
| **Product** | `.implementation/position.jsonl`, minted authorizations | **Untouched.** D8 persists no acknowledgment; `_AUTHORIZATION_BINDING_KEYS` and `proposalDigest` are out of scope and unedited |
| **Product** | Managed revisions under `proposals/` and `experiments/` | Both hold **only `.gitkeep`** in this checkout — verified this phase. **No instance of the crossing form exists anywhere**; every fixture is authored from nothing, and the operator's own `research-concept-r17.md` (39 `\tag{}`s) lives outside this repository and is not retrofitted |
| **Product** | Archived reports carrying `source_digest`/`suite_digest` | Untouched; no digest input changes |

## Testing Strategy

| Layer | What | Approach |
|---|---|---|
| Unit | Locator sub-key absence | Per index, per sub-key, `…_INCOMPLETE` naming `documents[N].block_locator.<key>` exactly |
| Unit | Locator shape | Uncompilable pattern; `pattern` with 0/2 groups; `identity` with zero fields, two fields, or a field not named `value` — each its own case |
| Unit | **Group count 1, asserted as such** | A three-group `block_locator.pattern` is **refused**; the case exists so nobody copies `citation_pattern`'s rule |
| Unit | `cross_citation` | `None` accepted; `resolves_against` naming an undeclared label refused; naming its own entry refused |
| Unit | `crossing_state` | Four memberships asserted directly: resolves both ways; `absent` only; `untested` only; both |
| Unit | `local_reach` | String `local`/`structural`; mapping all-local; mapping mixed → `False`; **empty mapping** → falls back to the string path |
| Integration | The per-document locus key (M4) | A finding naming `["proposal"]` alone with a `remedy_equations` locus absent from document 1 — **red against the shipped engine because the value is inexpressible**, not because an assertion was authored to fail |
| Integration | The refusals | Real subprocesses through `cmd_agree`; separate methods, never one method with three asserts |
| Integration | Acknowledgment | Two discrepancies, one acknowledged: exactly one clears, the other still refuses and is named |
| Integration | The consumer | `cmd_handoff` with `sources_by_document` threaded — the RED commit (M5) |
| Integration | The successor | Drive `experimental-deliberation` resolve → preview → accept against a real scratch project; **report the outcome, promise nothing** (M7) |
| Non-interference | The bar | `git diff --exit-code tests/seal/` after **each** slice; 28 digests byte-identical; `npm test` **595/595**; Python `OK (skipped=6)` with `Ran` grown — **`skipped=6` must not move in a tenth change, and no `skipTest` is added anywhere** |
| Mutation | Z1–Z10 | Anchor-counted both directions, scratch copies only |

### Mutation plan

| # | Break | Anchor | Must go red |
|---|---|---|---|
| Z1 | Delete each `block_locator` sub-key, one at a time, per index | sub-key literal 1→0 | `…_INCOMPLETE` naming that exact indexed path |
| Z2 | Sibling's declared `pattern` → the heading form | the LaTeX literal 1→0 | `MEASURED_MOVERS`' measured set. **Predicted: `compose`, `admit-e0`, `admit-e1`, `verify-a`, `verify-b`, `verify-t`.** If it moves nothing, the leaf is not wired and D1 has proven nothing |
| Z3 | Sibling's declared `identity` → `[exp:{value}]` | the template literal 1→0 | **`handoff-e0`/`handoff-e1`.** The renderer half, against the sibling's own pre-existing `remedy_block`s |
| Z4 | In `remedy_compatibility`, `vocab["locus_key"]` → `LOCUS_KEY` | per-index read 1→0 | M4's document-1 case; `tests/seal/` must survive |
| Z5 | In `remedy_compatibility`, `finding_tags[index]` → `finding_tags[0]` | index read 1→0 | the both-documents case; seal survives |
| Z6 | In `crossing_state`, compute `declared` with the **declaring** document's locator | index literal | the resolving case flips to `absent` — the one a weaker fixture survives |
| Z7 | Fire `AGREEMENT_DOCUMENTS_DISAGREE` per discrepancy instead of once with two lists | refusal-site count 1→2 | the fail-closed-once case, by asserting exactly one refusal payload |
| Z8 | `--acknowledge` clears the whole list rather than the named id | comparison 1→0 | the two-discrepancy case — **the one a weaker assertion survives**, because a single-discrepancy case cannot tell the two apart |
| Z9 | `local_reach` → `impact["class"] == "local"` | accessor call 4→0 | the two-document handoff routing case |
| Z10 | Delete `len(DOCUMENTS) > 1` from `COMMANDS`' conditional | the spread 1→0 | **the sibling's own `test_the_case_roster_covers_the_command_roster_exactly`** — the bar, held by the sibling's suite rather than by care |

**An anchor that matched is not a mutation that ran.** Confirm the count at both
endpoints, 1→0 and 0→1. `sd -s` exits 0 having changed nothing; `git diff --stat`
proves nothing for an untracked file and is masked by an adjacent real edit.
Clear `__pycache__` before every Python mutation — a same-size edit reuses a
stale `.pyc`. Never mutate the shipped engine; plant into a scratch copy, the
mechanism `test_implementation_domain_mutation.py` already has.
**`sys.modules` caches `impl_domain_profile` process-wide**: any in-process
helper restores it **and** `IMPLEMENTATION_DOMAIN_PROFILE` in a `finally`, or
~110 unrelated cases redden. Real subprocesses everywhere else —
**monkeypatching a module attribute has zero effect on a child process.**
**A surviving mutation has two explanations**: measure whether the test is weak
or the claim was wrong before strengthening anything.

**Commit granularity.** Every work unit is two commits: a `test(...)` commit
carrying only the failing test(s), individually checkoutable with the test red
at that sha, then the implementation. D5's first commit is the exception by
design — it threads the mapping and its red is the deliverable (M5).

## Threat Matrix

| Row | Applicable | Behaviour / RED test |
|---|---|---|
| **Regexes from a profile** (three new: `block_locator.pattern`, `.block_pattern`, `cross_citation.pattern`) | **Yes — headline** | Host-supplied text compiled into matchers. Compiled at **resolve** time so a malformed pattern refuses by name instead of raising mid-command; group counts validated there too. No dynamic construction, no user input concatenated. RED: an uncompilable pattern refuses at resolve, not at `remedy_compatibility` |
| **A format template from a profile** (`identity`) | **Yes — new** | `str.format` with exactly one field named `value`, validated by `string.Formatter().parse` at resolve time. Never `eval`, never `%`, never f-string construction. RED: `"{0}"`, `"{}"`, `"{value}{other}"` and `"{}"`-free templates each refuse by name |
| Backtracking on document bytes | **Yes** | Both new matchers run over managed revision text. `block_pattern` keeps the sibling's existing non-greedy `.*?` shape; no nested quantifier is introduced. Stated, and the corpus is the evidence |
| Path traversal via `--revision` | **Yes — inherited, and D must not widen it** | `revision_source` stays the single path join; `cmd_agree` reaches documents only through `document_revision_names`/`revision_source`. RED: `agree` is asserted to call `revision_source`, never to build a path |
| Routing / new subcommand | **Yes — new** | `agree` joins `COMMANDS` **conditionally**, no new flag on any existing command, its own `--revision` registration. RED: under a one-document profile, `agree` is not a parser choice and `COMMANDS` is byte-identical (Z10) |
| Subprocess invocation | Yes (inherited) | Seal and pair cases; `shell=False`, list argv, unchanged. No new entry point |
| Data integrity of persisted records | **Yes** | The Products table: no record shape changes; D8 persists nothing; the only digest file that grows is the new skill's own |
| Executable-file classification, VCS/PR automation, Network | N/A | None reached. `remote-execution` is **driven** through its existing forge-root-derived scripts (`REMOTE_EXECUTION_CLI_SCRIPT` et al. are already shared by both skills), never rebuilt and never edited |

## Migration / Rollout

No data migration — by the Products table, **no instance of the crossing form
exists on any disk**: `proposals/` and `experiments/` hold only `.gitkeep` in
this checkout, verified this phase, and no target's `findings.py` shape changes.

**Rollback**, per unit then per slice, tip-first. `tests/seal/` is untouched by
construction, so the pre-change seal is the post-revert seal — and that is
asserted, not assumed. Restoring `tests/experiments_seal/digests.json`,
`cases.json` and `unsealed.json` is **part of** reverting D1, not an
afterthought: without the `unsealed.json` restore, two commands are documented
available and are not, and a moved golden left behind becomes the new baseline
silently.

Reverting D3–D5 leaves D1/D2 shipped and dormant, which is safe: the locator is
a zero-delta indirection and `cross_citation` is a declared leaf nothing refuses
on yet. **Removing a leaf from `impl_profile.py` alone is not a rollback** —
both new keys are required, and their absence refuses the profile.

## Predictions This Design Makes — Claims Apply Must Measure, Not Repeat

- [ ] The locator's reach is **six `TAG_RE`/`DISPLAY_BLOCK_RE` call sites in
      three functions, plus one renderer in `cmd_handoff`** (M1).
- [ ] `TAG_RE` and `DISPLAY_BLOCK_RE` are byte-behaviour-identical after D2's
      re-derivation; the sibling's 28 digests are identical after **each** slice.
- [ ] `git diff --exit-code tests/seal/` exits 0 after **each** slice, including
      `cases.json` (M8/D9).
- [ ] **D1 moves ZERO of the 24 existing experiments-seal case digests** (M3).
      If any moves, the cause is found and named before regeneration.
- [ ] `__corpus_fingerprint__` moves in every slice that edits `corpus.py`, and
      that movement is separated from case movement before acceptance (M9).
- [ ] Z2 moves `compose`, `admit-e0`, `admit-e1`, `verify-a`, `verify-b`,
      `verify-t` — and Z3 moves `handoff-e0`/`handoff-e1`. **If either moves
      nothing, the leaf is not wired.**
- [ ] `reachable_refusal_codes()` goes 114 → **115** (D1) → **117** (D3) →
      **118** (D5). Measured per slice, never bulk-bumped.
- [ ] `L1_EXPECTED_COUNT` stays **96** and `L1_EXPECTED_FILES` stays one file —
      no new engine prose spells `proposal` (M11).
- [ ] `tests/pair/digests.json` is unmoved by every slice.
- [ ] `skipped=6` does not move; **no `skipTest` is added anywhere**; `npm test`
      stays **595/595**.
- [ ] `experimental-deliberation/reference-experimental.ts` is byte-unchanged,
      and `cites("[claims:39]")` returns `[]` (M6).
- [ ] The M4 control is **red against the shipped engine because the value is
      inexpressible**, not because an assertion was authored to fail.
- [ ] M7's accept turn: **outcome unknown**. Driven end to end in D5 and
      reported with its measurement. The 2026-09-08 note is re-dated or removed
      on the basis of that run, never on the basis of this reading.

**A design prediction about tooling is a claim, not a fact.** Five inherited
counts have failed in this project (`_POSITION_HEADER_RE`; 88/23/20 vs
89/30/28; Slice A's 40 tasks vs 33; `--revision`'s eight commands vs nine; B's
own 30 tasks vs 37), and M1, M3, M5, M7 and M9 correct or sharpen five more.
Every box above is measured at apply and reported with its measurement, never
ticked by repetition.

## Open Questions

- [x] The citation key → **option 1**, ruled by the operator; realised as
      `documents[N].cross_citation` resolving against the target document's own
      `block_locator` (D5/D6). No third vocabulary.
- [x] Is the acknowledgment durable → **request-scoped** (D8), with the durable
      option rejected on a named failure mode, not on convenience.
- [x] Where the check runs → **its own command, conditionally registered**
      (D9), forced by M8 rather than chosen for tidiness.
- [x] Composer or end-to-end successor → **the composer and the handoff are
      D's; the published write is re-measured and reported** (M7/D12).
- [x] Per-document locator → **yes** (D1/D3), and it is what makes the crossing
      resolvable at all.
- [x] Does D3 split → **yes**, into the refusals and the acknowledgment (D12).
- [ ] **Should `gate` require `agree` before a launch?** A cross-document
      disagreement arguably blocks a run. Out of scope and recorded rather than
      silently omitted: it is a launch-blocking change, and it belongs to a
      slice whose subject is the gate.
- [ ] **M2 (`cmd_handoff`'s hardcoded Spanish) stays unresolved**, and D5 adds a
      fourth branch in the same Spanish deliberately (D10). Recorded so the
      consistency is a decision, not a later surprise.
- [ ] **The 22 further bare product literals** and **F6** remain named
      follow-ups, untouched here.
- [ ] **A document declaring `cross_citation: None` participates in no
      crossing**, in either direction. Recorded so "it passed with one document
      silent" is a decision rather than a gap.

## Citations Checked

Located **by name, in the source, this phase, never by line and never
inherited**: `TAG_RE`, `DISPLAY_BLOCK_RE`, `remedy_compatibility`,
`cmd_compose`, `cmd_admit`, `cmd_handoff`, `cmd_verify`, `finding_impact`,
`_impact_class`, `document_citation_re`, `DOCUMENT_CITATION_PATTERNS`,
`DOCUMENT_INDEX_BY_LABEL`, `document_vocabulary`, `CLAIM_KEY`, `LOCUS_KEY`,
`REMEDY_LOCUS_KEY`, `NOTATION_KEYS`, `CITATION_RE`, `CITATION_PATTERN`,
`DOCUMENTS`, `well_formed`, `_valid_document_field`, `read_findings`,
`admissibility_record`, `_admissibility_extra_documents`,
`document_revision_names`, `revision_source`, `proposals_root`,
`adoption_state`, `_local_remedy_discuss_entry`, `COMMANDS`, `main`,
`GATING_COMMANDS`, `GATING_REFUSALS`, `INVOCATION_DEFECT`, `WORK_STATE`,
`Refused`, `reachable_refusal_codes`, `unreadable_refusal_sites`,
`_DOCUMENT_VOCABULARY_LEAVES`, `_NOTATION_KEYS_REQUIRED`, `_REQUIRED_NESTED`,
`_REQUIRED_PRESENCE`, `_resolve`, `ImplementationProfileError`,
`IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE`,
`IMPLEMENTATION_DOMAIN_PROFILE_INVALID_CITATION_PATTERN`,
`L1_BASELINE_AT_S0`, `L1_DELIBERATE_SHRINK`, `L1_EXPECTED_COUNT`,
`L1_EXPECTED_FILES`, `_engine_files`, `ENGINE_DIR`, `MUTATIONS`,
`MEASURED_MOVERS`, `discover_profiles`, `profile_values_text`,
`CORPUS_FINGERPRINT_SOURCE`, `Roots`, `_build_documents`,
`_build_document_one`, `_write_common_package`, `FINDINGS_SOURCE`,
`REVISION_TEXT`, `PROPOSAL_REVISION_TEXT`, `DATASET_DECLARED_TEXT`,
`_fixture_path`, `validate_roster`, `validate_case`, `digest_result`,
`run_case`, `build_env`, `SealMembershipTests`, `NON_DETERMINISTIC_CASE_IDS`,
`checkReferenceIntegrity`, `declaredValues`, `citedValues`,
`buildReferenceIndex`, `declares`, `cites`, `proseReference`,
`parseManagedRevision`, `parseRevisionIncrement`, `strictManagedRevision`,
`strictRevisionLabel`, `LAX_RE`, `LAX_SOURCE`, `STRICT_REVISION_LABEL_SOURCE`,
`INCREMENT_SOURCE`, `REVISION_PREFIX`, `SEGMENT`, `escapeRegExp`,
`nextSuccessorTarget`, `publishSuccessor`, `revisionPattern`, `revisionLabel`,
`REMOTE_EXECUTION_CLI_SCRIPT`, `remote_execution_jobs_state`,
`_discovered_job_folders`.

**Inherited claims re-measured this phase; five corrected or sharpened:**

1. *"`TAG_RE` has three readers, `DISPLAY_BLOCK_RE` one."* **Sharpened and
   extended**: six call sites across three functions, **plus a seventh site that
   is a renderer, not a reader** — `cmd_handoff`'s `selectedEntryId` (M1).
2. *"`tests/experiments_seal/` MUST move for D1; `verify-a`/`verify-b` are
   sealed cases against a locator that matches nothing."* **The premise is
   confirmed and the conclusion is reversed**: the emitted `unknown_loci`
   strings are byte-identical under both locators, so **zero existing case
   digests are predicted to move** (M3).
3. *"Hand those four comparisons a mapping and every one is `False`."*
   **Confirmed, and located as latent**: neither `cmd_handoff` nor `cmd_verify`
   passes `sources_by_document` today, so no mapping reaches them. The RED test
   is the deliverable's own first commit (M5).
4. *"`experimental-deliberation`'s accept turn is blocked by a hardcoded
   `-r(\d+)\.md$`."* **The recorded cause is not in the source**; every matcher
   in the chain derives from `revisionPattern` and all of them accept `v04`
   (M7). Outcome still unmeasured.
5. *"20 experiments-seal cases, 21 top-level keys; 28 sealed digests."*
   **Re-derived: 24 cases / 25 keys** for the experiments corpus (B2 added four)
   and **29 cases / 29 keys = fingerprint + 28 digests** for the sibling's, with
   `propose` carrying no digest (M9).

**A sixth finding, new rather than inherited:** `tests/test_implementation_seal.py`
asserts the sibling's case roster equals `impl.COMMANDS` exactly, so an
unconditionally registered `agree` would have broken the bar on the first
commit (M8). That constraint selected D9, and D9 is mutation-provable through
the sibling's own suite (Z10).

**No test suite was run in this phase**, per the session brief. Every count
above is derived from files read this phase and must be re-derived at apply.
