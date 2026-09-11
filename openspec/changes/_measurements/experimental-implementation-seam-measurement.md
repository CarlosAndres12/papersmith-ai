# `experimental-implementation` — seam measurement

Subject: `.claude/skills/proposal-implementation/scripts/implementation_cli.py`
(17,100 lines), its shared core, its kit and its two agents. Read-only measurement
taken at HEAD `a851390`. Nothing was repaired.

## 0. Headline

**The CLI is 99.0% domain-free. 167 lines of 17,100 genuinely name the mathematical
proposal.** The extraction is not big. What IS big is a thing no word count can see:
**`revision` is a scalar at 24 binding sites**, and "validate against BOTH documents"
turns every one of them into a pair. That, not vocabulary, is the second blocker
beside the profile seam.

One number in the prior orchestrator measurement is wrong in a way that could do real
damage — see F1.

## A. Classification

### A.1 Per-class line counts

| Class | Lines | Cost to move |
| --- | ---: | --- |
| **general** — no domain token at all | **16,933** (99.02%) | zero |
| domain **schema / data shape** | **40** | **expensive** — the profile supplies a contract, not a string |
| domain word in an **executable string** | 25 | cheap |
| domain word in an **identifier** | 4 | mechanical |
| **hardcoded path** | 10 | cheap |
| domain word in **comment/docstring** | 88 | cheap |
| *subtotal, genuinely domain* | **167** (0.98%) | |
| **false-positive** (campaign proposal — must NOT move) | 78 | **negative** — moving these breaks minted tokens |

309 top-level functions, 129 constants, 0 classes. **265 functions (9,574 lines) carry
no domain token at all.** 32 functions genuinely touch the domain across 4,025 lines,
but only 167 of those lines ARE the touch.

`.claude/skills/_core/implementation/*.py` is **1,343 lines with zero domain-specific
code**. Confirmed: no profile mechanism exists there.

### A.2 Commands

Only **three of twenty** have the document as their purpose: `admit`, `handoff`,
`compose` — **235 lines total**. Six are `mixed` at one to four lines each
(`materialize`, `probe`, `position`, `gate`, `offer`, `close`, `verify`). The rest are
general.

`verify` is 557 lines of which **4** are document-bound.

### A.3 The schema sites

19 lines carry a quoted `"sections"` or `"equations"`; counting `remedy_equations` as
its own key raises the true total to **40**. Two consumers: the provenance side (14
lines) and the findings side (the rest). Plus one writer — `authored_package_init`
(4234) writes "Each module declares the sections and equations it implements" INTO the
target — and the kit's `src_benchmark/__init__.py`, which ships the join's other half
as an asset.

## B. The six items

**B1 — the profile seam.** Sized and shaped. Mirror `_core/deliberation/engine/domain-profile.ts`
(267 lines): one env var, no default, fails closed at import, absolute path required,
nested required-key validation, path segments validated, a `names` list enforced by a
lock, and a byte-identical launcher per skill.

Proposed: `_core/implementation/impl_domain_profile.py` reading `IMPLEMENTATION_DOMAIN_PROFILE`,
loading via `importlib.util.spec_from_file_location` (already imported at line 25).
A profile declares: `documents` (**a list, not a scalar**), `provenance`,
`document_reader`, `findings`, `vocabulary`, `objective` (moves verbatim — already the
exact shape of the TS `objective`), `kit`, `cli_invocation`.

Three cuts, in order: **Cut 1** verbatim file move + per-skill launcher (the only
behavioural reach is `SKILL_ROOT`/`CLI_PATH` resolution). **Cut 2** the 167 lines.
**Cut 3** scalar→pair, gated on `len(documents) == 1` behaving exactly as today.

**B2 — the provenance schema.** NOT decided here; the operator's. Four measured
constraints on any answer: two levels of granularity with different jobs (coarse =
diffed, fine = report-only); the coarse key must be computable from the document's own
text; the coarse key is shared across two files or the join returns `[]`; both are
`ast.literal_eval`-able lists of strings.

Options: (A) profile-supply the fine key only — 9 lines, the sole option under ten;
(B) both — 19 lines, fully neutral, but two domains picking different coarse keys can
never cross-join; (C) collapse to one generic key — **changes existing behaviour**;
(D) keep both literals — the leak the mechanism exists to remove.

**B3 — the experiments-fidelity check.** ~95% reusable verbatim (24 of ~30 `verify`
keys, ~553 of 557 lines). 3 keys need the profile (`fidelity`, `audit`, `prose`).
Genuinely new: a second `fidelity` block, **the agreement BETWEEN the two documents**
(no analogue anywhere in 17,100 lines), and the experiments-successor composer.

**B4 — `Data/` demandable.** Confirmed. Two self-fulfilling producers (3868, 14249).
`verify.structure.missingDirs` can never contain a `Data/`. 2 lines at the decision,
~12 to make the fact reach both, plus the detector — `plan` has no path to any
document and no `--revision` in its parser.

**B5 — the two agents.** Both are ~70-line files carrying no logic. The walk-equivalent
is close to a verbatim copy with two names changed — which is itself the argument that
its text belongs to the shared surface. The build-equivalent's two ends move, and its
`stretch:` value must name a stage in the new skill's own `OBJECTIVE_FLOW` or
`test_agents.py` fails.

**B6 — findings routing.** Four things must exist that do not today: a per-finding
document declaration validated at read time (`well_formed` demands only a non-empty
`id`); every finding-consuming call site taking the document as an argument;
`admissibility.json` keyed by document; and a `handoff` reporting the cross-document
consequence. Plus the part with no analogue — a way to say "this finding is against
BOTH", which today's local/structural binary cannot express.

## C. Proving the extraction changed no behaviour

**The existing suites cannot do this.** `npm test` (595) is entirely the Node
deliberation side. The Python suite (2,783) is dominated by DERIVATION tests that read
expectations off the code's own literals — they go green across a refactor that moves
the code and its derived expectation together. They prove internal consistency, not
preservation.

**The check that would catch it: a stdout characterization seal.** Run all 20
subcommands against a fixed fixture corpus at `a851390`, capture stdout BYTES and exit
status, digest each. After each cut, re-run through the launcher and require
byte-identical stdout and identical exit status.

Corpus must exercise all 14 provenance sites, all 14 findings sites, the 5 hardcoded-path
refusals both with and without `IMPLEMENTATION_PROPOSALS` set, `Data/` present and
absent, a marker-owned and a hand-authored family, and a tie. Normalize `_now_iso8601()`,
absolute paths, `CLI_INVOCATION`, session ids, commit shas.

**The one declared delta:** fixing F3 changes five refusal messages. Declare it BEFORE
taking the seal, or the seal gets quietly relaxed to accommodate it — which is how a
seal stops being one.

Three further checks, none optional: mutation-prove every profile field (remove →
named refusal; change → output moves); a Python mirror of the TS domain-profile lock,
globbing profiles rather than hardcoding a pair; and **re-point
`PublishedCommandsRunVerbatimTests` at the launcher explicitly** — if `CLI_PATH`
resolves to the engine, published commands still run and name a file the reader was
never given. That is Cut 1's single silent failure mode.

No-leakage is already structural: `tests/forge_vocabulary.py::shipped_documents()`
walks every file under `.claude/skills/`, so the new skill is scanned the day its
directory appears.

## Findings — most consequential first

**F1. The `proposal` = 152 count over-states coupling by 78 lines, and acting on it
would break minted authorizations.** 47 code + 31 prose lines spell "proposal" in the
sense of the CAMPAIGN launch proposal, not the mathematical document. Among them
**`proposalDigest`, a member of `_AUTHORIZATION_BINDING_KEYS` (12560-12563)**, written
into minted `gate` authorization tokens inside every target's committed
`.implementation/position.jsonl`. A rename sweep driven by the 152 number would
invalidate every previously minted authorization, in a ledger that travels in clones.
*Resolution is to the measurement, not the code. Any rename must exclude
`proposalDigest`, `GATE_PROPOSAL_*`, `_proposal_digest`, `_verify_gate_proposal`,
`_gate_proposal_question`, `_verify_optional_election`, `cmd_propose`,
`_authorization_binding`, `_verify_gate_authorization`, `_campaign_identity`,
`_load_remote_execution_*`.*

**F2. `revision` is general as a WORD and scalar as a SHAPE — the second blocker.**
`revisionSha256` at **24 sites**; `__provenance__["revision"]`, `__benchmark__["revision"]`
and `admissibility.json.revision` all scalars; the `AGREED.md` position header binds one
revision + one sha; `_AUTHORIZATION_BINDING_KEYS` carries one `revisionSha256`, and a
launch token minted under one document must not validate under another. "Validate
against BOTH" converts every one to a pair. **Invisible to a word count and larger than
the entire vocabulary extraction.**
*Resolution: `documents` a list in the profile; every scalar field's wire shape
conditional on `len(documents) == 1`.*

**F3. Five refusal messages name a directory the code never read.** Lines 7535, 10362,
12982, 13509, 13683 spell `FORGE_ROOT / 'proposals'` while the read went through
`proposals_root()`, which honours `IMPLEMENTATION_PROPOSALS`. Under test — and under any
relocation — the refusal names the wrong place. `cmd_handoff` (7368) got it right.
*Resolution: `proposals_root()` at all five. Declare the message delta before the seal.*

**F4. `plan` has no path to any document**, so `Data/` cannot be demanded there without
a new argument. `--revision` is registered for eight commands and `plan` is not one.
*Resolution: add `--revision`, thread `source` into `build_plan`, and decide explicitly
that an unnameable document leaves `with_data` unchanged rather than refusing, so `plan`
stays runnable on a bare clone.*

**F5. `expected_dirs` spells `"Data"` as a bare literal beside `PRODUCT_DIRS`** (2502)
— the exact second-literal defect the comment at 113-119 argues against.
*Resolution: `PRODUCT_DATA = PRODUCT_DIRS[1]`.*

**F6. `MANAGED_ARTIFACT_MARKER` now has four spellings across two languages.** All four
agree today. It is a defect the day one changes, and the failure is silent.
*Out of scope. Record the coupling; do not act.*

## Findings that touch the skill's stated mentality — the operator's, not mine

**M1. `compose` cannot be mirrored by parameterising a regex.** It is LaTeX end to end:
`DISPLAY_BLOCK_RE = \$\$.*?\$\$` locates the block and `TAG_RE = \\tag\{([^}]+)\}`
identifies it. An experiments document has no display blocks — its profile declares
`(Exp. N)` prose references and "a report table or a figure" as its numbered display.
The FLOW mirrors cleanly; the COMPOSER does not. Is composition a profile-supplied
callable, or is `compose` the one per-skill command? **A mentality decision.** Note that
the deliberation side already solved the identical problem by shipping the domain's own
implementation beside its profile (`preservation-math.ts` / `preservation-experimental.ts`).

**M2. `handoff`'s deferral prose is hardcoded Spanish**, and `SKILL.md:818` forbids
exactly that: *"Speak the language the user is speaking."* Making these profile strings
is cheap and correct for the extraction, but it hardens a doctrine violation into a
contract shape.

**M3. `Data/` may be a smaller requirement than stated.** It is already in `PRODUCT_DIRS`,
already routed by `classify` (nine data extensions), already matched by `REFERENCE_RE`,
already carried by `detect_product_dir`. **The only thing missing is demandability** —
B4's ~12 lines plus a detector, not an architecture extension.
