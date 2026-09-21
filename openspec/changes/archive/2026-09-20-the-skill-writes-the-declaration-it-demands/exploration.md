# Exploration: the skill writes the declaration it demands

Measured 2026-09-20 against `main`. Read-only pass.

## The defect

A source root's revision-naming rule lives in a per-root marker,
`<root>/.paper-writing.json`. `paper_declarations.read_revisions_marker`
(lines 1407-1476) is its only reader. An absent file yields `None`; a
malformed one refuses `MALFORMED_SOURCE_MARKER`. Two call sites turn the
`None` into `SOURCE_REVISIONS_UNDECLARED` with byte-identical text —
`_resolve_bind_document` and `paper_graph.resolve_section_index`. Neither
names a command, because none exists to name.

**Nothing in the skill writes it.** Every write pattern was grepped against
both marker kinds across `scripts/`: zero hits.

Compare `bind`, which this repository's owner required precisely because a
demand with no way to answer it is a lock with no key:

| | `bind` | the marker |
|---|---|---|
| recorded by | a verb of the skill | a file written outside it |
| validated | at the moment of the decision | only when something later reads it |
| protected | region digest, refuses a hand edit, no `--adopt` | nothing |
| surfaced in `plan` | yes | not at all |

## The same gap in the older sibling, and the owner's ruling

`guidance/`'s own `class` marker — the longer-shipped convention this one
was modelled on — has the **identical** gap. `paper_guidance.read_registry`
and `_classify` only ever read; its schema (`_MARKER_ALLOWED_KEYS =
("class",)`) carries **no digest field at all**. So the pattern's weakness
is systemic, not local to the newer marker.

**The owner ruled it enters this change.** Both marker kinds get the same
treatment; shipping a fix for one while the other keeps the defect would
leave an inconsistency inside one skill.

## Sealing, measured and stated honestly

`declarations` and `provenance` live inside `main.tex` between
`%% paper-writing <kind> begin sha256=<hex> … end` lines; the digest covers
the raw prefixed body bytes and is compared at read time
(`_verify_not_hand_edited`, `DECLARATIONS_HAND_EDITED`, no `--adopt`).

**This is self-consistency, not cryptography.** There is no secret;
anyone reproducing the canonical-JSON plus `%% ` prefix convention can hand
edit and recompute a matching digest. Its real protection is against an
unaware edit, never a determined one.

So: **neither shipped marker convention is sealed against a determined
edit**, and `guidance/`'s has no sealing of any kind. That is a finding
about the shipped design, not only about this change, and the design phase
must not promise more than the existing mechanism delivers.

## A prior claim measured false

`openspec/changes/archive/2026-09-20-the-requirement-names-the-section-that-feeds-it/`
carries, in `design.md`'s File Changes table and in `tasks.md` item **2.14
marked `[x]`**, the claim that `Corpus.source_roots` is "echoed by every
corpus-reading verb".

Measured by running them: the field exists on the `Corpus`, and `plan`,
`phases` and `contract` surface it in **none** of the three. `source_roots`
is consumed internally by `compute_separation`, `cmd_bind` and
`paper_source_span`, and never rendered as an operator-visible field.

Half the task shipped and the whole task was ticked. It passed verify and
archive because the field exists and every test that consumes it passes —
nobody ran the three verbs and read the output.

**So the SHOW piece of this change is not new work: it finishes work that
was recorded as finished.** This is the third artifact in one session found
claiming something the code does not do, and the third found by a later
change going to lean on it rather than by its own verification.

## What `plan` already does, and the precedent it sets

`compute_plan` returns `{guidance, declarations, provenance,
[sectionGuidance]}`. Nothing about source-root state.

`guidance`'s classification IS shown, and `read_registry` calls `_classify`
unguarded per folder — so a malformed guidance marker already propagates a
refusal straight through `plan` today. That is the precedent for the new
source-root check, and it needs no new philosophy: **absence is a reported
state** (mirroring `unclassified`), **malformed refuses**.

## Scope of the roots

`FACT_SOURCE_ROOT` maps `formulation`→`proposals` and
`experimental-design`→`experiments`, both PROSE-kind: both need the
identical fix, no divergence. `dataset`→`evidence` is INGESTED-kind,
resolved by identity, and structurally bypasses `read_revisions_marker` —
out of scope for the revisions rule, in scope for the `guidance` class
marker by the owner's ruling above.

## The fork the design must settle

Where a written declaration lives:

1. **Beside the root.** A new verb validates and writes
   `<root>/.paper-writing.json`, adding a self-referential digest the schema
   does not have today. Preserves root scoping — a root's rule is true
   before `paper/` exists and after it is archived — but introduces a second
   digest convention alongside `paper_region.py`'s.
2. **A fifth `declarations`-region record kind**, with the marker demoted to
   a regenerable materialization and a mismatch refusing. Reuses proven
   sealing with no new convention, but couples a repo-scoped fact to a
   per-paper file's lifecycle — which the archived design explicitly
   rejected when it turned down `papersmith.yaml` for the same reason.

Genuinely undecided. It belongs to design, not here.

## Refusal roster

Measured **154** by direct count of `REFUSAL_CLASSIFICATION`'s entries. No
post-change count may be written into any artifact — measure after the code
lands.

## Affected areas

`paper_declarations.py` (the writer, the enriched refusal, the schema),
`paper_guidance.py` (the same for the class marker, per the owner's
ruling), `paper_graph.py` (the second, duplicated
`SOURCE_REVISIONS_UNDECLARED` raise site — fixing one and not the other
reintroduces a drift this project has already hit), `paper_cli.py` (the new
verb, `plan`'s new report key, new classifications), and the corresponding
tests.

## Risks

- The marker-location fork must be settled by design before tasks.
- Two raise sites duplicate the refusal text; enrich both or neither.
- `describe_binding_candidates` already has a "no marker, list every `*.md`"
  fallback — directly reusable for the enriched refusal, and worth reusing
  rather than writing a second lister.
- Sizing is read-based, not diff-based; confirm at tasks time.
