# Design: A Diagram That Compiles, Or Says Why

## Technical Approach

Three skill-local modules under `.claude/skills/paper-writing/scripts/`, registered into the
existing `paper_cli.py` front door in the shape the four landed verbs already use: one JSON
object on stdout, exit 0 = ran, exit 2 = a guard refused before touching disk. `latexmk` is
invoked as a child process and never emulated; its log is the only evidence a compile
happened. Diagram obligations are read off a per-block `figure:` declaration in the contract
front matter — the skill names no section, no fact and no figure.

Verified against source, not inherited: `paper_cli.COMMANDS` / `REFUSAL_CLASSIFICATION`,
`paper_scaffold.resolve_paper_dir` / `FORGE_ROOT` / `_SCAFFOLD_ENTRIES` (`Figures` is already
scaffolded), `paper_contract._BLOCK_ALLOWED` and `paper_vocabulary.validate_fact`,
`reachable_paper_refusal_codes()` and `_run_against_mutant` in `tests/test_paper_writing.py`,
and `AgentBindingTests` in `tests/test_agents.py`. `paper_contract.py` and
`paper_vocabulary.py` are on disk; `sections/*.md` still carry **no** front matter, and
`paper/` holds only `.gitkeep`. Every refusal code below is the one `specs/authored-diagram`,
`specs/diagram-obligation` and `specs/section-contract` name — re-read from those files, not
inherited from the proposal's summary.

## Architecture Decisions

### Decision: three skill-local modules, none of them in `_core/`

| Option | Tradeoff | Decision |
|---|---|---|
| `_core/implementation/` | `reachable_refusal_codes` (`tests/test_proposal_implementation.py`) scans that directory **whole** and demands every code be classified in another skill's `GATING_REFUSALS`. Diagram codes would land in a roster that does not own them | Rejected |
| One `paper_figure.py` | Fewest files, but the subprocess and the pure obligation arithmetic end up in one module, and "only one module may import `subprocess`" stops being assertable | Rejected |
| **`paper_latex.py` + `paper_figure.py` + `paper_obligation.py`** | `paper_latex.py` is the sole holder of `subprocess`/`shutil.which` (an AST test over the skill's scripts holds it); `paper_obligation.py` is pure functions over parsed headers and manifests, testable with no `PATH` at all; `paper_figure.py` owns the source layout, the manifest cross-check and the ledger. Cost: three files and one more import edge | **Chosen** |

`reachable_paper_refusal_codes()` hard-lists `(paper_block.py, paper_scaffold.py)`. Adding
modules without extending that tuple leaves their refusals **unrostered while the roster test
stays green** — a task, and its own RED test (assert the derived set contains a code only a new
module raises).

### Decision: the compile's verdict never comes from the parser

`latexmk -norc -g -pdf -interaction=nonstopmode -file-line-error -outdir=<scratch> <id>.tex`,
cwd = `paper/Figures/`, scratch = `paper/.paper-writing/figures/<id>/`, child env carrying
`openin_any=p`, `openout_any=p`, `shell_escape=f`. `-norc` because an `~/.latexmkrc` would make
the invocation machine-dependent; `-g` because latexmk skipping an up-to-date target would hand
back a **previous** run's log while spending budget.

The scratch `.log` is deleted before the spawn; no log after it refuses `LATEX_LOG_ABSENT`.

| Option for an unrecognized log line | Tradeoff | Decision |
|---|---|---|
| Ignore it | A failure the parser cannot name reads as a green run | Rejected |
| Refuse on any unrecognized line | Every ordinary log line is unrecognized; unusable | Rejected |
| **Verdict from three signals, parser only explains** | Exit status, the presence of `<id>.pdf`, and the parsed diagnostics must agree. Disagreement — failed with zero explained diagnostics, or succeeded with errors parsed — refuses `LATEX_OUTCOME_UNEXPLAINED`, carrying the log path, the unexplained tail and `unrecognizedLines: N`. Unrecognized lines are **counted and published**, never dropped | **Chosen** |

`LATEX_OUTCOME_UNEXPLAINED` spends **no** budget and does not retry: a diagnostic nobody can map
to a source line is not a repairable one. Parsed shapes: `-file-line-error`'s
`<file>:<line>: <message>` for `!` errors, and `Overfull \hbox (…) in paragraph at lines A--B`
(and `\vbox`) mapped to A — the precedent's rule.

### Decision: the budget is keyed to the figure id, and the ledger is honest about what it is

`paper/.paper-writing/figures/<id>/ledger.json` records `attempts: [{sourceDigest, diagnostics,
at}]`. Four repairable compiles per **id**; the fifth refuses `REPAIR_BUDGET_SPENT`, naming every
distinct diagnostic and every digest tried. A missing `.sty` refuses `LATEX_PACKAGE_ABSENT` and
spends nothing.

**Divergence from the precedent, recorded as such**: `marco-propuestas-ia`'s `compile_tikz.py`
gives **one** four-attempt limit shared by three diagram types. Ours is per id, because a hard
diagram must not eat another's budget. The bound is the operator's to change and never an
agent's.

| Ledger home | Tradeoff | Decision |
|---|---|---|
| Tracked forge path | Survives `rm`, but puts the user's document state in forge history — and `paper/*` is gitignored precisely because the document is the user's | Rejected |
| **`paper/.paper-writing/figures/<id>/`** | Beside the scratch it describes; deleting it **is** the operator acknowledgement, made explicit rather than pretended-secure. `render` publishes `ledgerCreated: true`, so a reset is visible in the JSON | **Chosen** |

Stated plainly, because the alternative is a false claim: nothing under `paper/` is tamper-proof.
The ledger bounds an honest loop and records a reset; it is not a security boundary.

### Decision: the data-figure boundary is two stops, and neither subsumes the other

| Stop | Mechanism | Catches what the other cannot |
|---|---|---|
| **A — source** (`DIAGRAM_PLOTS_DATA`) | `paper_figure.py` scans the `.tex`: a plotting package (`pgfplots`, `pgfplotstable`, `\begin{axis}`), an external table read (`\addplot table`, `\pgfplotstableread`, `\csvreader`, `\input`/`\include` resolving outside `paper/Figures/`), or an embedded coordinate series (a `coordinates`/`plot` list of numeric pairs over a threshold) | A chart drawn from numbers **pasted into the source**. It touches no file, so every filesystem bound in the world sees a clean compile |
| **B — reachability** | cwd is the figure's own directory, `-outdir` is its scratch, `openin_any=p` forbids the engine reading absolute or `..` paths, `shell_escape=f` forbids shelling out. No path from that compile reaches any results tree | A mechanism stop A never enumerated: a package we did not list, a filename built by a macro, `\write18`. Stop A is a closed list and ages; stop B is a capability bound and does not |

Honest limit: stop A is fully measured here. Stop B's **enforcement** belongs to the TeX engine,
so on a machine with no distribution only its invocation shape (cwd, `-outdir`, the three env
vars) is proven and its behaviour reports `unmeasured`.

Placing a measured figure is a separate verb that compiles nothing and requires provenance
naming the run — out of this change's compile path entirely.

### Decision: obligations are read, and the schema stays exactly the six subkeys the spec closes

`paper_contract._BLOCK_OPTIONAL` gains `"figure"`; a `_parse_figure` validator in the same module
holds it to `components_from`, `ordered`, `excludes`, `caption_enumerates`, `caption_decodes`,
`mandatory` — five required, `components_from` optional (widened by this change's own corrective
amendment below), nothing else admitted, `MALFORMED_FIGURE_OBLIGATION` naming the missing or
unknown key. `components_from`, when present, is validated by `paper_vocabulary.validate_fact`, so
an invented fact refuses `UNKNOWN_FACT` with no second vocabulary. `caption_decodes` is a **boolean**:
*which* encodings exist is a property of the diagram, so the encoding list lives in
`<id>.diagram.json` and the contract only says whether decoding them is owed.

**The separation test is transcribed, not inferred.** Both `01` ("A box appearing in both means
one of the two is wrong") and `02` ("no dataset and no baseline appears in the methods diagram,
and no internal component of the proposal appears in this one") state it, and both list it as a
disqualifier — so the intersection check is a transcription of two contracts that already agree,
not a rule this skill invented.

| Scope of the intersection | Tradeoff | Decision |
|---|---|---|
| A `separation_group` subkey | More precise if two diagrams ever legitimately share a box, but it is a **seventh** subkey in an object the spec closes at six | Rejected; revisit trigger below |
| **Every pair of declared diagrams** | Exactly what the spec requires, and it needs no new key. `SHARED_COMPONENT` names the label and both ids | **Chosen** |

Revisit trigger: a contract that states a shared box is correct. Today none does — both say the
opposite in their own words.

**The `05` conditional, expressed in data rather than a new key.** `05`'s block 5 is "an evolution
figure **or** a comparison table". Its declaration is `mandatory: false`, and the operator's
artefact choice is expressed by **whether a diagram source exists for that block**: a table choice
leaves no `<id>.tex`, so no component, separation or caption check runs and
`MANDATORY_DIAGRAM_ABSENT` cannot fire. A design that demanded a compiled diagram there would
refuse a perfectly legal table. Cost, stated: under `mandatory: false` an operator who *intends* a
diagram and writes none gets silence — which is what `mandatory: false` means.

The manifest is crossed with the `.tex` in **both** directions (`MANIFEST_SOURCE_MISMATCH`): a
declared label absent from the source, or a node in the source absent from the manifest, refuses.
A dataset box cannot hide from the separation test by going undeclared.

**What this design leaves for phase 8, deliberately.** `02` also obliges every results table and
figure to be locatable in its closing diagram. That obligation has one side in section `03`, which
is out of scope here, and `the-couplings-hold-or-they-do-not` already owns it as coupling 4. This
change runs no such check and names no results section. What it owes phase 8 is the *possibility*:
`<id>.diagram.json` is a durable, machine-readable record of every cell the crossing declares, so
the later check reads a manifest instead of parsing TikZ.

### Corrective amendment: `components_from` is optional, and its check is derived, never supplied

`sdd-verify` measured, by direct execution against the real on-disk `es-assessment` obligation,
that the schema above (`components_from` required on every `figure:` object) was uncheckable in
practice: `es-assessment`'s `components_from: dataset` named only the anchor of a six-category
composite crossing, and the wiring an earlier corrective attempt added (`--expected-components`,
an operator-built CLI flag) never cross-checked that flag against the fact `components_from`
claimed to be `_from` — a prose-compliant diagram was refused `COMPONENT_MISMATCH`, a degenerate
dataset-only one passed. Two changes close it, replacing that attempt's docstring-only fix:

1. **`components_from` moves from `_FIGURE_REQUIRED` to `_FIGURE_OPTIONAL`** — the same
   `raw.get(...) is not None` round-trip convention `mode` already uses (an explicit JSON `null`
   means the same as the key being absent). The other five subkeys stay mandatory. When absent,
   `_check_obligations` never calls `check_components` for that block; every other check
   (`check_excluded`, `check_caption`, `check_mandatory`, cross-diagram separation) still runs.
2. **When present, the Components Check's expected list is DERIVED**, never operator-supplied.
   `paper_declarations.read_fact` (new, read-only, reuses the exact private readers `set_fact`/
   `reopen` already call) returns the named fact's currently-fixed `resolution` string; a new
   `paper_cli._resolve_expected_components` helper `json.loads`s it and requires a list of
   strings. Undeclared refuses `COMPONENTS_FACT_UNRESOLVED`; unparsable or non-list refuses
   `COMPONENTS_FACT_NOT_A_LIST`. `--expected-components` (the flag) is removed — a flag that
   exists only to be ignored, or to be trusted without cross-checking the fact it claims to name,
   is the same defect in a different costume.

`sections/02-experimental-setup.md`'s `es-assessment` block now declares no `components_from` at
all: no single fact is its closing diagram's full crossing, and a check wired to one anchor fact
inverted itself. `sections/01`'s methods diagram is unaffected — the contribution list IS its full
component list by contract, so `components_from: contributions` still derives correctly through
`declare --fact contributions --value '[...]'`.

**Independent of `the-couplings-hold-or-they-do-not`'s own coupling 4** (`check_artefacts`, "every
result locatable in this diagram"): re-confirmed by reading, not inherited — that check reads only
`couplings.json`'s own `artefacts.setup_cells`/`results_artefacts` and `facts.contributions`,
never `figure`/`components_from`/`paper_obligation` (grep, zero matches across
`paper_coupling_evidence.py`/`paper_verify.py`). Removing `components_from` from `es-assessment`'s
contract cannot affect it.

### The roster

Twelve codes, ten from the proposal and spec — `DIAGRAM_SOURCE_ABSENT`, `LATEX_TOOLCHAIN_ABSENT`,
`LATEX_PACKAGE_ABSENT`, `REPAIR_BUDGET_SPENT`, `DIAGRAM_PLOTS_DATA`, `MALFORMED_FIGURE_OBLIGATION`,
`COMPONENT_MISMATCH`, `MANIFEST_SOURCE_MISMATCH`, `EXCLUDED_COMPONENT`, `SHARED_COMPONENT`,
`CAPTION_INCOMPLETE`, `MANDATORY_DIAGRAM_ABSENT` — plus two this design introduces for behaviour
the spec described without naming: `LATEX_LOG_ABSENT` and `LATEX_OUTCOME_UNEXPLAINED`. Every one
lands in `REFUSAL_CLASSIFICATION`; none of the spec's is dropped.

### Decision: three test tiers, and the no-skip rule is a test

| Tier | What it proves | How |
|---|---|---|
| 1 — parsing, budget, obligations, separation, caption | the arithmetic and the grammar | committed fixture logs **captured raw** from a real `latexmk`, each beside a `provenance.json` (distribution, version, date, argv) and the `.tex` that produced it; a test asserts every fixture carries a pdfTeX banner matching its provenance, so fabricating one is a deliberate act |
| 2 — invocation shape | argv, cwd, `-outdir`, the three env vars, the output path | an executable stub `latexmk` prepended to `PATH` records its argv/cwd/env to JSON and copies a captured log into `-outdir` |
| 3 — absence | `LATEX_TOOLCHAIN_ABSENT` naming the binary sought and the entries searched | `PATH=""` **with cwd set to an empty temp dir** — `shutil.which` splits `""` into one empty entry, which resolves relative names against cwd, so a naive `PATH=""` can pass for the wrong reason |

Discovery is `shutil.which` through an injectable `path` parameter, and `FileNotFoundError` at
spawn maps to the same code (the binary can vanish between the check and the spawn).

Nothing is conditional. An AST test over the new test module asserts no `skip`/`skipIf`/
`skipUnless` decorator and no `self.skipTest` call exists in it. A real end-to-end compile reports
`unmeasured`, never a pass — the `interpreterMatch: null` idiom.

**Executed mutations** (via `_run_against_mutant`, generalised from its hardcoded
`PAPER_BLOCK_SOURCE` to take a module — a task): component dropped; two reordered; a dataset named
in the methods diagram; one label shared across two diagrams; an encoding
undecoded in the caption; a series plotted; `PATH` emptied; **and the budget keyed to
`(id, sourceDigest)` instead of `id`** — the budget test must run four compiles **with a source
edit between each**, or a reset-on-edit bound looks enforced and is not.

A fixture log authored by the same hand that parses it passes vacuously. Tier 1 therefore cannot
be written on this machine: no `latexmk` exists here. Open question below.

## Data Flow

    figure: (sections/NN.md front matter) ─→ paper_contract.parse ─→ paper_obligation
                                                                          │ components/order/
    paper/Figures/<id>.diagram.json ──┬─→ paper_figure (cross-check) ─────┤ separation/caption
    paper/Figures/<id>.tex ───────────┘         │ stop A                  ↓
                                                ↓                     verdict JSON
                       paper_latex.render ─→ latexmk (cwd=Figures, -outdir=scratch,
                                 │              openin_any=p)  ─→ <id>.pdf ─→ paper/Figures/
                                 └─→ log ─→ parse ─→ diagnostics ─→ ledger.json (4 per id)

## File Changes

| File | Action | Description |
|---|---|---|
| `scripts/paper_latex.py` | Create | Toolchain discovery, the one subprocess, log parsing, the three-signal verdict |
| `scripts/paper_figure.py` | Create | Source/manifest layout, both-direction cross-check, stop A, the ledger |
| `scripts/paper_obligation.py` | Create | Components, order, separation groups, caption — pure functions |
| `scripts/paper_cli.py` | Modify | `render` + the placement verb in `COMMANDS`/`_COMMANDS`, new `REFUSAL_CLASSIFICATION` entries |
| `scripts/paper_contract.py` | Modify | `"figure"` in `_BLOCK_OPTIONAL`; `_parse_figure` |
| `.claude/skills/paper-writing/SKILL.md` | Modify | Verb table, roster, the data boundary, the agent invocation `AgentBindingTests` requires |
| `sections/01`, `02`, `05` | Modify | `figure:` in the front matter of the blocks that demand one; prose untouched |
| `.claude/agents/diagram-author.md` | Create | One thin agent that loads the skill and stops at the escalation |
| `tests/test_paper_figure.py` | Create | Separate file — two classes sharing a name in one file silently drops the second |
| `tests/test_paper_writing.py` | Modify | Roster tuple, `_run_against_mutant` generalisation |

## What Breaks — Producers and Products

| Class | Row |
|---|---|
| Producers | `paper_cli.COMMANDS`, `REFUSAL_CLASSIFICATION`, `reachable_paper_refusal_codes()`'s module tuple, `_run_against_mutant`'s `PAPER_BLOCK_SOURCE`, `paper_contract._BLOCK_ALLOWED`, SKILL.md's verb table and roster paragraph, `AgentBindingTests` (a new agent must be invoked by a skill and name both ends of its stretch) |
| Products | `paper/` holds only `.gitkeep` — **no `main.tex`, no `Figures/`, no `<id>.tex`, no manifest, no ledger exists anywhere on disk.** Zero written instances are invalidated |
| Products | `sections/*.md` carry **no** front matter yet, so no existing header becomes invalid; `figure:` extends a fence the sibling change has still to write |
| Products | No `.pdf`, no captured log fixture and no provenance record exists yet; tier 1 creates its own products |
| Products | Forge leak guard: every new file under `.claude/skills/paper-writing/` is scanned, so the new doctrine must avoid `FORGE_VOCABULARY_FLOOR` words; `sections/` is outside its reach |

## Threat Matrix

| Boundary | Applicability | Design response | Planned RED tests |
|---|---|---|---|
| Documentation-like paths | **Applicable** — a `.tex` is executable input to a TeX engine | Stop A's scan plus `shell_escape=f`/`openin_any=p`; `\input` outside `paper/Figures/` refuses | One per class: plotting package, external read, inline series, `\input` escape |
| Git repository selection | N/A — nothing here invokes git; `paper_scaffold.FORGE_ROOT` is path arithmetic, never `git rev-parse` |  |  |
| Commit state | N/A — `paper/*` is gitignored and this change stages nothing |  |  |
| Push state | N/A — no remote interaction |  |  |
| PR commands | N/A — no PR automation |  |  |
| **Subprocess / cwd authority** (added row) | **Applicable** — first external binary this skill invokes | argv list never a shell string; `-norc`; cwd and `-outdir` both resolved under the caller-supplied `--paper` root, which `resolve_paper_dir` already bounds; absence is `LATEX_TOOLCHAIN_ABSENT`, never a degraded mode | Stub-PATH argv/cwd/env assertion; emptied-`PATH` refusal; `FileNotFoundError`-at-spawn mapping; a `--paper` outside the root refusing |

## Migration / Rollout

No data migration — nothing of this shape exists on disk. Sequenced **after**
`the-contract-is-data-not-code` writes the headers; until then `render`'s obligation check
refuses a named code rather than guessing which sections carry a diagram. Rollback is
`git revert`: the verbs disappear, the four landed ones are untouched, and nothing under `paper/`
is tracked, so no committed artefact is orphaned.

## Open Questions

- [ ] **Tier 1 is blocked on a machine with TeX Live.** The fixture logs must be captured raw
      from a real `latexmk`; this machine has none. Apply either receives the captured logs and
      their provenance records, or stalls at that task. Authoring them here is the one thing this
      design forbids.
- [ ] **The transcription lock is narrower than the sibling's.** `the-contract-is-data-not-code`
      backs every `after` edge with a `source: {file, quote}` checked against the prose. The
      `figure` object is closed at six subkeys, so there is nowhere to put the quote. Scoped here
      to what is mechanically checkable — a test asserts each `excludes` entry and the
      `components_from` fact name occur in the holder contract's prose, whitespace-normalised.
      `ordered` and `mandatory` are booleans no substring can prove, and this design does **not**
      claim they are locked. Either amend the spec to admit a seventh `source` subkey, or accept
      the narrower lock; not both readings at once.
- [ ] `LATEX_LOG_ABSENT` and `LATEX_OUTCOME_UNEXPLAINED` are design-introduced. They belong under
      `authored-diagram`'s Standalone Compile requirement and need a scenario each, or the roster
      carries two codes no spec describes.
- [ ] Artifact exceeds the 800-word sdd-design budget, as the sibling's did. Six mandated
      decision areas plus the breakage, threat and testing sections do not compress below it.
