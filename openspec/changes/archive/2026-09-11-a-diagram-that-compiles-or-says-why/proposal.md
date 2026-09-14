# Proposal: A Diagram That Compiles, Or Says Why

## Intent

Three contracts demand an authored diagram and each states what it must contain
(`sections/01`, `02`, `05`). Nothing here can produce one, prove it compiles, or check it
against the contract that demanded it — `substitute` reports `rendering: "unproven"` because no
LaTeX toolchain exists in this repository. Close that, without letting an agent draw a result.

## Scope

### In Scope

- **Sources live in the document tree**: `paper/Figures/<id>.tex` plus `<id>.diagram.json`
  (component labels, encodings, caption); `<id>.pdf` beside them; build scratch under
  `paper/.paper-writing/figures/<id>/`. `paper/*` stays gitignored — a diagram is the user's
  document, not forge content. `main.tex` receives an `\includegraphics` figure through the
  existing `substitute`; no TikZ enters `main.tex`.
- **`render`**: exactly one `latexmk` compile per call, `-file-line-error
  -interaction=nonstopmode`; parses `!` errors and `Overfull \hbox` back to source lines.
- **A repair budget of four compiles per figure id**, held in a ledger that editing the source
  does **not** reset — otherwise the bound is decorative. Spent → `REPAIR_BUDGET_SPENT`, naming
  every distinct diagnostic and every source digest tried; cleared only by an operator's explicit
  acknowledgement. Only repairable diagnostics consume it: a missing `.sty` refuses
  `LATEX_PACKAGE_ABSENT` and spends nothing, because redrawing cannot fix it.
- **Toolchain absence is a named refusal**: `LATEX_TOOLCHAIN_ABSENT`, naming the binary sought
  and the `PATH` searched. Not a degraded mode, not a silent pass.
- **Obligations read, never known**: a per-block `figure:` declaration in the contract front
  matter — `components_from` (the fact whose ordered list the components must equal), `ordered`,
  `excludes` (forbidden element classes), `caption_enumerates`, `caption_decodes`, `mandatory`.
  The skill names no section and no contract.
- **Three checks**: components (missing / extra / misordered against the named fact);
  separation (each diagram's own `excludes`, plus the **intersection** of any two diagrams'
  component sets — a shared box refuses); caption (every component present in order, every
  declared encoding decoded).
- **The manifest is crossed with the source, both directions**: a declared label absent from the
  `.tex`, or a node in the `.tex` absent from the manifest, refuses. A dataset box cannot hide
  from the separation test by going undeclared.
- **The data-figure boundary, enforced twice**: `render` refuses `DIAGRAM_PLOTS_DATA` on a source
  that loads a plotting package, reads an external table, or embeds a coordinate series; and it
  compiles with no reachable path to any results tree. Placing a measured figure is a **separate
  verb that compiles nothing** and requires provenance naming the run that produced it.
- **Mutations executed, never asserted**: drop a component; reorder two; name a dataset in the
  methods diagram; the same label in both diagrams; strip a colour the figure encodes from the
  caption; plot a series; empty `PATH`; spend the budget.

### Out of Scope

Producing data figures; `main.tex`'s preamble and document assembly; `refs.bib`; the seven
contracts that demand no diagram; authoring any real paper's figure content.

## Capabilities

### New Capabilities

- `authored-diagram`: source layout, manifest, `render`, the bounded repair ledger, toolchain and
  package absence, the data-figure boundary and its second verb.
- `diagram-obligation`: obligations read off the contract header — components, order, separation,
  the cross-diagram intersection, the caption rule.

### Modified Capabilities

- `section-contract`: gains the per-block `figure:` field. Owned by the sibling change
  `the-contract-is-data-not-code`, which has **not landed** — `sections/*.md` carries no front
  matter today.

## Approach

Fail-closed stdlib CLI registered into the existing `paper_cli.py` front door, refusal roster
derived from source the way `REFUSAL_CLASSIFICATION` already is. `latexmk` is invoked, never
emulated; its log is the only evidence a compile happened.

### What the precedent gives, and what it does not

`marco-propuestas-ia`'s `proposal/scripts/compile_tikz.py` and its three agents.

| From the precedent | Decision |
|---|---|
| Watch `Overfull \hbox`, map to source line | **Adopt** |
| Bounded retries, then escalate to the user | **Adopt**, bound of four |
| Reset-free bound | **Adapt** — ours is keyed to the figure id, not to a source revision |
| TikZ designer agent | **Adopt**, one thin agent that loads the skill and stops at the escalation |
| Optimizer agent | **Do not take** — the repair loop is the CLI's; an agent is not needed to re-run a compiler |
| Figure reviewer agent | **Do not take** — comparing a component set to a contribution list is a list comparison, and a model asked to judge it can agree with a wrong figure |
| Whole-document compile | **Adapt** — each diagram compiles standalone, so the loop does not wait on an unbuilt preamble |

### A suite that skips proves nothing

Three tiers, none of them conditional:

1. **Log parsing, budget arithmetic, obligations, separation, caption** — against committed
   fixture logs captured from a real `latexmk`. Always run.
2. **Invocation shape** — a stub `latexmk` on an injected `PATH` emits a recorded log, so argv,
   cwd and output paths are proven on a machine with no TeX. Always runs.
3. **Absence** — an emptied `PATH` asserts `LATEX_TOOLCHAIN_ABSENT`. Always runs, on every
   machine, because absence is a behaviour and not a reason to stop testing.

A genuine end-to-end compile against a real distribution is reported **`unmeasured`** where it
did not run — never a pass, the same way `interpreterMatch: null` already means unmeasured.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/paper-writing/scripts/` | New | Diagram render, ledger, obligation checks; new verbs on the existing front door |
| `.claude/skills/paper-writing/SKILL.md` | Modified | Verb table, refusal roster, the data-figure boundary |
| `sections/01`, `02`, `05` | Modified | `figure:` in the front matter of the three blocks that demand one. Prose untouched |
| `.claude/agents/` | New | One thin diagram-authoring agent |
| `tests/test_paper_writing.py` | Modified | Red-first; eight mutations executed |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| `section-contract` has not landed, so there is no front matter to extend | **High** | Sequence after it. Until then `render`'s obligation check refuses a named code rather than guessing which sections carry a diagram |
| `main.tex` is scaffolded empty — no preamble, so `\includegraphics` resolves nowhere | Medium | Standalone compile is independent of it; this change **declares** the one package the assembly phase must load and writes none of it |
| A fixture log written by the same hand that parses it passes vacuously | Medium | Fixtures are captured from a real `latexmk` run and committed as raw bytes, never authored |
| The budget is defeated by an agent that edits between attempts | Medium | The ledger is keyed to the figure id; the "spend the budget" mutation is executed with edits in between |
| A diagram agent renders a chart anyway | Low | Two independent stops: the source refusal, and a compile that cannot reach a results tree |

## Rollback Plan

`git revert` the change commit. The new verbs disappear; `scaffold`/`status`/`open`/`substitute`
are untouched, and the `figure:` keys revert with the contracts. Nothing under `paper/` is
tracked, so no committed artefact is orphaned.

## Dependencies

- `the-contract-is-data-not-code` (front matter) — unlanded.
- `latexmk` and a TeX distribution with TikZ — external, absent here, and refused by name.

## Success Criteria

- [ ] A diagram compiles to `paper/Figures/<id>.pdf` and `status` shows the figure block in `main.tex`.
- [ ] Eight mutations executed, each observed red: component dropped, components reordered, dataset in the methods diagram, label shared across two diagrams, encoding undecoded in the caption, series plotted, `PATH` emptied, budget spent.
- [ ] The budget is spent across four compiles **with source edits between them**, and the fifth refuses.
- [ ] Obligations for all three diagrams come from the contract headers; deleting a `figure:` key removes the obligation with zero code changed.
- [ ] On a machine without TeX the suite runs every test and skips none; the end-to-end compile reports `unmeasured`, never `ok`.

## Proposal question round

Blocked from asking directly (delegated phase). Four questions the answers would change:

1. **Where does the diagram source live** — under gitignored `paper/` as proposed (the document
   is the user's and never published), or in a tracked `figures/` beside `sections/`?
2. **Four attempts** — adopted from the precedent. Higher, lower, or a per-figure override?
3. **`\includegraphics` of a standalone PDF, or TikZ inline in `main.tex`?** Standalone
   decouples from the unbuilt preamble; inline keeps one file but couples the whole document to
   TikZ and puts uncompiled content in the block engine's path.
4. **Does this change wait for `the-contract-is-data-not-code`**, or ship with an interim
   obligation source that the front matter later replaces?
