# Proposal: The Skill Writes the Declaration It Demands

## Intent

This is not a missing feature. It is a rule of this repository being broken by a
file the skill itself demands.

The rule, the one that produced `bind`: **a decision about the paper is made by
USING the skill** — never by an agent editing a file, never in a conversation
held to unblock something.

A source root's revision-naming rule is such a decision: it says how `experiments/`
names its revisions, and the corpus reads it back as authority. It lives in
`<root>/.paper-writing.json`. `paper_declarations.read_revisions_marker` is its
only reader. **Nothing in the skill writes it.** Measured: every write pattern
grepped against both marker kinds across `scripts/` returns zero hits. The file
exists because an agent created it with a file-writing tool, outside the skill
entirely — the exact act Decision I of the archived predecessor ruled out, one
layer below where it ruled it out.

| | `bind` | the marker |
|---|---|---|
| recorded by | a verb of the skill | a file written outside it |
| validated | at the moment of the decision | only when something later reads it |
| protected | region digest, refuses a hand edit, no `--adopt` | nothing |
| surfaced in `plan` | yes | not at all |

The same change that shipped the marker recorded its shape and never added the
writer — precisely the shape of defect that change existed to close, repeated
inside itself. Two call sites (`paper_declarations._resolve_bind_document`,
`paper_graph.resolve_section_index`) turn an absent marker into
`SOURCE_REVISIONS_UNDECLARED` with byte-identical text, and neither names a
command, because none exists to name. A lock with no key.

`guidance/`'s own `class` marker has the **identical** gap, and its schema
(`_MARKER_ALLOWED_KEYS = ("class",)`) carries no digest field at all. **The owner
ruled it enters this change.** Fixing one marker kind and leaving the other would
put the defect and its repair inside a single skill.

## Scope

### In Scope

Four pieces, for **both** marker kinds, none optional:

- **SHOW.** A root's declaration state appears in the read-only position report
  beside `guidance/`'s classification, which is already there. A session with no
  memory learns where the paper stands without hitting a wall first.
- **ASK.** `SOURCE_REVISIONS_UNDECLARED` names the exact command that answers it
  and reads the root from disk to say what it currently sees — the way `bind`'s
  own refusal names candidate lineages and their section titles. The refusal is
  the question. **Both raise sites, or neither**: they carry byte-identical text
  today, and enriching one reintroduces a drift this project has already hit.
- **VALIDATE at the moment of writing.** The declared prefix and digit count are
  checked against the files actually under the root as the declaration is
  recorded — not three steps later, in a different command, under an unrelated
  message.
- **SEAL.** An edit made outside the skill must not read as a decision.

Plus: `guidance/`'s `class` marker gets the same four, per the owner's ruling;
`SKILL.md` **and** `references/usage.md` (a doc fix that stops at `SKILL.md` is
half a fix); the roster re-measured after the code lands.

### Out of Scope

- **The `INGESTED` root.** `dataset`→`evidence` resolves by identity and
  structurally bypasses `read_revisions_marker`; it has no revisions rule to
  declare. It is in scope only for the `guidance/` class marker above.
- **The 48-hit leaked-name audit** across three sibling skills. Measured,
  owner-acknowledged, separate work.
- Deleting or migrating any existing marker's meaning; widening either grammar
  beyond what sealing requires.
- Any post-change refusal-roster count. Roster is **154** today, by direct count
  of `REFUSAL_CLASSIFICATION`. The count after this lands is measured, never
  forecast, and appears in no artifact until it is.

## Capabilities

### New Capabilities

- `source-declaration-authoring`: a marker's declaration is written by a verb of
  the skill, validated against disk at the moment of writing, sealed against an
  unaware edit, and reported by the read-only position verb. Covers both marker
  kinds; owns the writer, the write-time validation, the seal's exact strength,
  and the reported-versus-refused split for absent and malformed state.

### Modified Capabilities

- `source-section-binding`: `SOURCE_REVISIONS_UNDECLARED` must name the answering
  command and what it read from disk, at **both** raise sites; the marker grammar
  gains whatever the seal requires (see the fork — under option 2 this reduces to
  the marker becoming a regenerable materialization).
- `guidance-registry`: the `class` marker gains a writer, write-time validation
  against the closed `CLASSES` vocabulary, and a seal; `unclassified` stays a
  reported state and a malformed marker keeps refusing.
- `paper-declarations`: **conditional on the fork below.** Modified only if design
  rules the declaration is a fifth `declarations`-region record kind.

## Approach

**The verb's shape follows `bind`, not `declare`.** `bind` got its own root rather
than becoming a fifth mode of `declare`, because `declare`'s four modes all write
the same subject — the paper's own facts and declarations, in `paper/main.tex`'s
`declarations` region. A source root's revision rule is a different subject: it is
a property of the corpus on disk, true before `paper/` exists and after it is
archived. So this change adds its own root too, and that holds whichever way the
fork below is ruled: where the record LANDS is design's question; what the verb's
subject IS is already decided by what it declares.

**ASK reuses shipped code.** `describe_binding_candidates` already carries a
"no marker yet — list every `*.md` by its own filename stem" fallback, built for
exactly this condition. The enriched refusal calls it rather than growing a second
lister.

**Absence reports, malformed refuses.** No new philosophy is needed: `guidance/`'s
classification already shows `unclassified` for an unfilled folder while a
malformed marker propagates a refusal straight through `plan` today. The new
source-root report mirrors that split exactly.

**This CLI never invokes an agent.** No `subprocess`. It refuses and names the
next action.

**Which roots need a declaration is derived**, from the shipped root map and each
root's own kind, never from a list of names.

## Sealing — stated at its real strength

The existing region digest has **no secret**. Anyone who reproduces the
canonical-JSON-plus-`%% `-prefix convention can hand-edit a region and recompute a
matching digest. `DECLARATIONS_HAND_EDITED` protects against an **unaware** edit —
never a determined one.

Whatever this change adds MUST be described at exactly that strength, in the spec,
in the code's own docstrings, and in the refusal's own wording. Promising more
than the mechanism delivers is worse than the gap it closes: it converts a known
hole into a believed guarantee.

## The fork — named here, ruled by design

Where the written declaration lives. Genuinely undecided.

| Option | For | Against |
|---|---|---|
| **1. Beside the root** — a verb validates and writes `<root>/.paper-writing.json`, adding a self-referential digest the schema does not have today | Preserves root scoping: a root's rule is true before `paper/` exists and after it is archived, and a gitignored root carries its own rule | Introduces a **second digest convention** alongside `paper_region.py`'s, and widens a closed marker grammar that today refuses every unknown key |
| **2. A fifth `declarations`-region record kind** — the marker demoted to a regenerable materialization, a mismatch refusing | Reuses proven sealing, the proven hand-edit guard, and one convention | Couples a **repo-scoped** fact to a **per-paper** file's lifecycle — the exact objection the archived Decision A used to reject `papersmith.yaml` |

One input design should weigh that neither exploration nor this proposal settles:
under option 1 the marker grammar gains a key, so a revert leaves sealed markers on
disk that the reverted reader refuses as `MALFORMED_SOURCE_MARKER` — an unknown
key is a refusal in both readers today. Option 2 has no such rollback edge,
because the marker's own bytes never change shape. That is a rollback-cost
argument, not a decision; design rules it.

## A prior claim measured false — recorded, not smoothed over

The archived `2026-09-20-the-requirement-names-the-section-that-feeds-it` carries,
in `design.md`'s Decision B and File Changes table and in `tasks.md` item **2.14,
marked `[x]`**, the claim that `Corpus.source_roots` is "echoed by every
corpus-reading verb".

Measured by running them: the field exists on the `Corpus`, and `plan`, `phases`
and `contract` surface it in **none** of the three. It is consumed internally by
`compute_separation`, `cmd_bind` and `paper_source_span`, and never rendered as an
operator-visible field. Half the task shipped; the whole task was ticked. It
passed verify and archive because the field exists and every test consuming it
passes — nobody ran the three verbs and read the output.

**So the SHOW piece is not new work. It finishes work already recorded as
finished.** This is the third artifact in one session found claiming something the
code does not do, and the third found by a later change going to lean on it rather
than by its own verification. A proposal that presented SHOW as new work would
hide a defect in the record.

## Worked example — invented names throughout

An invented checkout. `<base>/experiments/` holds `field-survey-r07.md`,
`field-survey-r08.md`, `widget-calibration-notes.md` and no marker.

**Today — true, and a dead end.**

```
$ paper write --block methods.block-b
REFUSED SOURCE_REVISIONS_UNDECLARED
'experiments' is document-rooted but carries no '.paper-writing.json' marker
(exit 2)
```

**Enriched — the refusal is the question, read from disk at that moment.**

```
REFUSED SOURCE_REVISIONS_UNDECLARED
'experiments' is document-rooted but carries no '.paper-writing.json' marker.
Read now under <base>/experiments (3 files):
  field-survey-r07.md
  field-survey-r08.md
  widget-calibration-notes.md
Answer it:
  declare-source --root experiments --revision-prefix <prefix> --ordinal-digits <n>
```

Byte-identical enrichment at **both** raise sites.

**The write, validated against disk at the moment of writing.**

```
$ declare-source --root experiments --revision-prefix r --ordinal-digits 2
{"root": "experiments",
 "revisions": {"revision_prefix": "r", "ordinal_digits": 2},
 "matched": ["field-survey-r07.md", "field-survey-r08.md"],
 "unmatched": ["widget-calibration-notes.md"],
 "sealed": true}
```

**The same write, refused for a wrong value — at the moment of writing, not three
steps later under an unrelated message.**

```
$ declare-source --root experiments --revision-prefix v --ordinal-digits 2
REFUSED SOURCE_DECLARATION_UNMATCHED
'experiments': prefix 'v' with 2 or more ordinal digits matches 0 of the 3 *.md
files under it. Seen: field-survey-r07.md, field-survey-r08.md,
widget-calibration-notes.md
```

**A hand edit to a sealed declaration, on the next read.**

```
REFUSED SOURCE_DECLARATION_HAND_EDITED
<base>/experiments/.paper-writing.json: recorded digest <a>, computed <b>.
Re-record it with declare-source; there is no --adopt.
```

(Self-consistency, not cryptography — see above. The refusal's own wording says so.)

**The position report, showing a root nobody has declared.**

```
$ paper plan
{
  "guidance": {"reference-corpus": "style-reference", "scratch": "unclassified"},
  "sourceRoots": {
    "experiments": {"state": "document-rooted", "documents": 3,
                    "declaration": "undeclared"},
    "proposals":   {"state": "unmeasured", "reason": "no *.md under it",
                    "declaration": "n/a"}
  },
  "declarations": {...}, "provenance": {...}
}
```

`undeclared` is a **reported** state, exactly as `unclassified` is. A malformed
marker still refuses through `plan`, exactly as `guidance/`'s does today.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/paper-writing/scripts/paper_declarations.py` | Modified | The writer, write-time validation, the seal, the enriched refusal at raise site 1 |
| `scripts/paper_guidance.py` | Modified | The same four pieces for the `class` marker; `_MARKER_ALLOWED_KEYS` widened for the seal |
| `scripts/paper_graph.py` | Modified | Raise site 2 of `SOURCE_REVISIONS_UNDECLARED` — enriched identically |
| `scripts/paper_region.py` | Read or Modified | Read under fork option 1; modified under option 2 |
| `scripts/paper_cli.py` | Modified | The new verb's own root, `compute_plan`'s source-root key, new `REFUSAL_CLASSIFICATION` entries |
| `.claude/skills/paper-writing/SKILL.md`, `references/usage.md` | Modified | The loop, in both |
| `tests/test_paper_*.py` | Modified/New | Red-first, one executed mutation per new code, one per enriched raise site |
| `tests/test_proposal_implementation.py` | Gate | Derived-denylist audit before apply |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| The fork is unsettled; sealing cannot be built before it is ruled | High | DP is a blocking unit; no seal code lands before design rules |
| Under option 1, a revert strands sealed markers an older reader refuses as malformed | High | Named as a fork input above; design rules it, and the Rollback Plan below reflects both branches |
| Sealing is described as stronger than it is, in spec, docstring or refusal text | High | The honest strength is stated three times here and is a success criterion; it is a review gate, not a footnote |
| The enriched text is applied to one raise site only | Med | Explicit invariant; a test asserts both messages are byte-identical |
| The forge suite needs deps nothing declares, so a bare interpreter reports environment failures as red | Med | Run both suites in the declared environment: `npm test` **and** the project venv's `unittest discover` |
| This paper's names leak into the forge (breached in the change before last) | Med | Derived-denylist audit as a blocking gate, comments and fixtures included |
| Size: the marker's own predecessor cost ten units and four budget rulings | High | Six units, chained PRs, forecast below |

## Review Workload Forecast

```
Decision needed before apply: Yes
Chained PRs recommended: Yes
400-line budget risk: High     (default budget)
1600-line budget risk: Medium  (owner's budget for this change, engine lines only)
```

Budget is **1600 engine lines** — code under `.claude/skills/paper-writing/scripts/`
only. Tests, mutation proofs, fixtures and openspec documents do not count.

| Unit | Content | Est. engine lines | Green alone |
|---|---|---|---|
| **DP** | Design rules the fork | blocking | — |
| U1 | The source-root writer + write-time validation, its own verb root | ~350 | yes |
| U2 | The seal, per the fork's ruling, for the source-root declaration | ~300 | yes |
| U3 | The `guidance/` `class` marker's writer, validation and seal | ~300 | yes |
| U4 | The enriched refusal at **both** raise sites, reusing `describe_binding_candidates` | ~250 | yes |
| U5 | SHOW: source-root state in the position report — finishing task 2.14 | ~200 | yes |
| U6 | `SKILL.md` + `references/usage.md`, leak audit, roster re-measured | ~150 | yes |

Estimated **~1550 engine lines** — at the ceiling, not under it. **It splits.**
Four chained PRs recommended: PR#1 `U1`, PR#2 `U2+U3` (one sealing convention,
applied twice; splitting them duplicates fixture setup), PR#3 `U4+U5`, PR#4 `U6`,
each targeting the previous branch. U1 is inert without U2.

## Rollback Plan

Revert the branch. The verb is a new root; the report key is additive; the
enriched refusal changes message text, never a code.

The one non-free part is the seal, and it depends on the fork. Under option 2
(region record) rollback is clean: the marker's own bytes never change shape, and
`_body_or_default`/`_find_record` iterate `body["records"]` generically by
`(kind, id)`, so an older revision that has never seen the new kind simply never
writes one. Under option 1 (beside the root) a revert must ALSO strip the seal key
from any marker this change wrote, because both readers refuse an unknown key —
design must ship that as an explicit rollback step, or shape the seal so the older
reader still accepts it.

## Dependencies

- Archived `2026-09-20-the-requirement-names-the-section-that-feeds-it` — the
  marker, its grammar, `describe_binding_candidates`, and Decision A's reasoning
  for why the marker sits beside its root.
- Archived `2026-09-20-the-whole-cut-is-argued-before-any-section-is-claimed` —
  `bind`'s precondition, and the "the verb is the act" doctrine this change extends.

## Success Criteria

- [ ] A source root's revision rule can be recorded by USING the skill; no
      file-writing tool is needed to answer `SOURCE_REVISIONS_UNDECLARED`.
- [ ] A `guidance/` folder's class can be recorded the same way.
- [ ] Both `SOURCE_REVISIONS_UNDECLARED` raise sites name the answering command
      and what they read from disk, with byte-identical text — asserted by a test,
      proven by a mutation that changes one of the two.
- [ ] A declaration that matches nothing on disk refuses **at the moment of
      writing**, naming the prefix, the digit count and every file it saw.
- [ ] A hand edit to either sealed declaration refuses on the next read, with no
      `--adopt` — proven by an executed mutation.
- [ ] The seal is described as self-consistency and not as tamper-proofing, in the
      spec, in the docstring, and in the refusal's own wording.
- [ ] The position report names every derived root's declaration state: undeclared
      is reported, malformed refuses — proven by running the verb and reading the
      output, not by asserting a field exists (the exact failure of task 2.14).
- [ ] Which roots need a declaration is derived from the root map and each root's
      kind; adding a sixth root widens the report with no engine edit.
- [ ] No `subprocess` import joins `scripts/`; `NoSubprocessScanTests` unchanged.
- [ ] The derived-denylist audit reports zero leaked product names and zero
      hardcoded product values across `.claude/skills/` and the forge suite,
      comments and fixtures included.
- [ ] Refusal roster re-derived after the code lands, never forecast. It is 154 now.
- [ ] Both suites green: `npm test` and the project venv's
      `python -m unittest discover -s tests -p 'test_*.py'`.
