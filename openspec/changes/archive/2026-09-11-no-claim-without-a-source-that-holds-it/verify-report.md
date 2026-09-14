```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:223b2b77f65d0a253ec8f8fab47ee630fd501e8bc2a7dcfc9c005383e3a7c50d
verdict: fail
blockers: 3
critical_findings: 3
requirements: 17/20
scenarios: 32/35
test_command: npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
test_exit_code: 0
test_output_hash: sha256:6f0f86fd2b5e3b382861fbe570e140c83231c82dea0c001eb81c0cfc9fcebd1c
build_command: npm run typecheck
build_exit_code: 0
build_output_hash: sha256:0489b64b1ab5dcef532b46d77ea0fca0aa427390ec93669281021dd89abd1486
```

## Verification Report

**Change**: no-claim-without-a-source-that-holds-it
**Version**: N/A (five brand-new capabilities, no prior spec)
**Mode**: Strict TDD
**Evidence revision**: `sha256:223b2b77f65d0a253ec8f8fab47ee630fd501e8bc2a7dcfc9c005383e3a7c50d` = sha256 of the full git commit hash `f3b3fcf49b00da98901688dfc798f1e63e1f7ae4` — current branch `HEAD` at the time this report's test/build evidence was captured (this change's own last commit is `0ea0e7c0d3b7a726be32d1c67e035284d600606e`; `HEAD` moved three commits past it when a sibling change landed mid-verification, purely additively — see the Concurrency note below).

### Completeness
| Metric | Value |
|--------|-------|
| Tasks total | 35 |
| Tasks complete | 35 |
| Tasks incomplete | 0 |

(Filesystem `tasks.md` is the authoritative source; the count is 35, not the
"33" figure quoted informally in the apply-progress Engram summary — re-counted
directly against `^- \[x\] [0-9]+\.[0-9]+` in this phase rather than inherited.)

### Build & Tests Execution

**Build**: PASS — `npm run typecheck` exits 0, no output (dev dependencies now
installed; this is no longer a pre-existing excuse per the launch brief).

**Tests**: PASS — run twice, fresh the second time after the sibling change
landed on `HEAD`. First run (evidence commit `0ea0e7c`): `npm test` 559/559
pass, 0 fail; `.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`:
3011 tests OK, 6 skipped. Second, current run (`HEAD` = `f3b3fcf`, this
report's evidence of record): `npm test` 559/559 pass, 0 fail (unchanged);
Python discover: **3085 tests OK, 6 skipped** (+74 tests — the sibling
change's own new coverage, not this change's; this change's own 73 tests are
an unchanged subset of that total, confirmed by the isolated re-run below).
Both commands run exactly as mandated; combined exit 0 both times.

Focused re-run for this change's own two new test files, in isolation:
`.venv/bin/python -m unittest tests.test_paper_evidence tests.test_paper_citation -v`
— 73/73 pass in 3.45s, including the three mutation-proof tests (m1, m2, m3)
and the planted-citation proof.

**Concurrency note (updated mid-verification)**: at the start of this phase a
sibling `sdd-apply` was writing uncommitted work for a different change
(`the-writer-may-assert-only-what-it-was-given`) into this same working tree.
That sibling change has since **landed** as three real commits
(`7d8568e`, `a0f6523`, `f3b3fcf`) on top of this change's own last commit
(`0ea0e7c`); branch `HEAD` is now `f3b3fcf`. Re-checked after the landing:
`git diff 0ea0e7c HEAD` on the shared files (`paper_cli.py`,
`paper_vocabulary.py`, `paper_contract.py`, `tests/test_paper_writing.py`)
remains purely additive on top of this change's own contribution — a new
`write` verb and five new modules (`paper_bindings.py`, `paper_audit.py`,
`paper_write.py`, `paper_style.py`, `paper_leak.py`), new refusal codes (roster
now 79, up from this change's own 65 — a clean superset, every one of this
change's 65 codes confirmed still present, none dropped), and new
`MODES`/`COMPARATIVES`/`NUMBER_WORDS` vocabulary. The four modules this change
owns (`paper_evidence.py`, `paper_resolve.py`, `paper_bib.py`,
`paper_validate.py`) and their two test files show **zero diff** against
either `0ea0e7c` or current `HEAD` — byte-identical throughout. This is
expected, not drift, and none of it is this change's concern.

Two pieces of test debris flagged mid-session (an orphaned
`_open_defect_ladder_fixture_<pid>_*.py` under
`.claude/skills/proposal-implementation/scripts/`, and six generated
directories under `implementations/` left by killed runs) were cleaned before
this report was finalized; `implementations/` now holds only its tracked
`.gitkeep`, confirmed directly. The earlier transient `F` from a concurrent,
self-inflicted second invocation of `tests.test_proposal_implementation` (run
by this verify pass alongside the mandated background suite) is attributed to
that now-cleaned debris and/or the same-time collision, not a defect in this
change; a fresh full mandated run (see below) is the evidence of record.

### The proof this change exists for — executed directly, not read

Built an isolated fixture (`implementations/_verify_no_claim/`, removed after
use) independent of the shipped test suite:

1. Scaffolded a paper dir, wrote a source `.md` stating "contains exactly
   4,000 labeled training examples."
2. Planted a **false** citation: claim "the dataset holds 12000 labeled
   examples", `--quote` the verbatim 4,000-example sentence, `--verdict
   does-not-hold`. Recorded via the real CLI (`paper_cli.py validate`).
3. In the **same run**, submitted the **true** pole: claim "the dataset holds
   4000 labeled examples", the same verbatim quote, `--verdict holds`. This
   claim dropped out of `unsupported` immediately — the same source bytes
   produced both verdicts, decided by the human/agent judgment behind
   `--verdict`, never by the matcher.
4. Resubmitted the false claim two more times to reach `round=3`; the third
   submission refused `EVIDENCE_EXHAUSTED` naming the exact unsupported claim
   text, exit 2.
5. Attempted to write the block anyway (`--body`) at that point: refused the
   same `EVIDENCE_EXHAUSTED`, exit 2. `status` afterward showed the block's
   digest still equal to the empty-content digest — **nothing was written**.

This directly satisfies citation-validation's "planted false citation"
scenario, the "genuinely-holding citation in the same run" scenario, and the
"exhaustion blocks the write, naming the claim" scenario, by execution, not
by re-running the shipped test.

**Re-executed a second time, fresh, against current `HEAD` (`f3b3fcf`, after
the sibling change landed)**, with a new isolated fixture and different
numbers (false claim: "the dataset holds 9000 labeled examples"; same
verbatim 4,000-example quote): identical result — the false claim stayed in
`unsupported`, the true pole ("the dataset holds 4000 labeled examples", same
quote, `--verdict holds`) dropped out immediately. Confirms the deliverable
holds after the sibling's commits landed on top, not only at this change's own
last commit.

### Structural guarantees — tried to violate each, at runtime

1. **`Verdict` has no public constructor taking a verdict string.**
   `paper_evidence.Verdict(value="holds", span=None, reason=None)` (bypassing
   `.holds()`/`.does_not_hold()`/`.insufficient()`) raises `TypeError` at
   `__post_init__` — confirmed by direct execution, not by reading the
   `_TOKEN` sentinel and taking its word for it.
2. **`EvidenceSpan` only exists via `.locate()`, which byte-searches the
   ingested source.** A paraphrase ("the dataset has about four thousand
   training samples" — not a verbatim substring of the fixture) raised
   `Refused("SPAN_NOT_IN_SOURCE", ...)` on direct execution.
3. **Satisfaction is one derivation, no per-verdict branch.**
   `paper_validate.satisfied_claims` is exactly
   `{r["claim"] for r in records if r["verdict"] == HOLDS}` — read directly;
   there is no `if verdict == "insufficient"` special case anywhere in
   `finalize_block` or `satisfied_claims`. `insufficient` cannot become a
   soft `holds` because there is no code path that treats it differently
   from `does-not-hold`.
4. **The searched bytes never derive from the claim under test.**
   `EvidenceSpan.locate` reads `md_path.read_bytes()` verbatim and searches
   only for the caller-supplied `quote` — nothing in `paper_evidence.py`
   re-serializes the claim text, the verdict, or any value under test back
   into the searched bytes. Confirmed by reading the full 366-line module;
   the only inputs to the byte search are the quote string and the file's
   own on-disk content.

### A function wired to nothing — swept all four modules

Cross-referenced every top-level public function in `paper_evidence.py`,
`paper_resolve.py`, `paper_bib.py`, `paper_validate.py` against every
non-test caller in the repository, twice: first a word-boundary mention
sweep, then re-run with a stricter pattern requiring an actual call site
(`name(`, excluding the function's own `def` line) — import-reachability and
call-reachability are two separate checks, and a module can be imported (for
a roster derivation, or a lint-suppressed `# noqa: F401`, as this same build's
sibling change does for `paper_style`/`paper_leak`) without any of its
functions ever being called. Re-run a third time against current `HEAD`
(`f3b3fcf`) after the sibling change landed, since the four modules under
verification showed zero diff either way. All three passes agree. Result:

| Function | Production caller |
|---|---|
| `classify_guidance_child` | **none** — disclosed and deliberate (design.md Decision 6: consuming this discriminator into a shared registry is a later change's work) |
| every other public function in all four modules | at least one production caller in `paper_cli.py` or intra-module code |

Exactly one orphan, and it is the one already disclosed in apply-progress —
no new orphan found. `read_citations_regime` (the previously self-caught gap,
fixed in `0ea0e7c`) now has a real caller: `paper_cli._resolve_regime` →
`cmd_validate`, confirmed by reading the call site directly.

### The offline path — driven for real, guard switched off

Wrote a driver script that imports `paper_cli` **in-process**, replaces
`paper_resolve.OPENER` with an object whose `.open()` always raises
`URLError`, then calls `paper_cli.main(["resolve", ...])` — the actual CLI
entrypoint, not a mocked function. Result: `RESOLVER_UNREACHABLE`, exit 2,
printed through the real `main()` JSON error path. This is independent of
the shipped `ResolverMutationProofTests.test_m1` (which mutates the source
in a subprocess to prove the guard is load-bearing rather than merely
present) — both mechanisms agree, and the shipped m1/m3 (and m2 in
`test_paper_citation.py`) mutation-proof tests re-ran green as part of the
73-test focused run above.

Confirmed separately: `paper_validate._validate_none` never calls into
`paper_resolve` at all (no resolver object, no opener, no import even
reached) — a `citations: none` block's placement check is a pure
`sentence.citations` emptiness check, structurally unable to touch the
network regardless of connector state. `ResolverOfflineTests.
test_a_none_regime_block_is_unaffected_by_every_connector_being_unreachable`
(shipped) exercises the same fact.

### `refs.bib` cannot be hand-composed

`paper_bib.entry_from_record` is the sole entry producer; `bib build`'s
CLI parser (`paper_cli.py`'s `p_bib_build`) takes only `--paper` — no flag
anywhere accepts entry text. Direct execution: `paper_bib.build_refs_bib`
given a hand-composed record dict (no `resolver`/`metadata_digest`) with the
network `OPENER` raising refused `ENTRY_UNSOURCED` before any byte was
written — proven entirely offline.

**One hardening gap, SUGGESTION-level, not a spec violation**: the spec's own
wording ("no function and no flag accepts entry text") is satisfied to the
letter, but `paper/.paper-writing/metadata/<digest>.json` (the cache
`entry_from_record` trusts) carries no hand-edit guard analogous to
`BLOCK_HAND_EDITED` — a human could write a JSON blob there by hand with a
self-consistent `metadata_digest` field and reference it via `validate
--metadata-digest`, without ever touching a flag or function that "accepts
entry text." This is a filesystem-level bypass of the intent, not the letter,
of Requirement 1; no scenario in `sourced-bibliography/spec.md` tests for it.

### Reciprocal checks — both directions, independently

Direct execution against `paper_bib.check_reciprocal`: `\cite{ghost2024}`
with no matching entry refused `CITE_WITHOUT_ENTRY`; a `refs.bib` entry never
cited refused `ENTRY_WITHOUT_CITE` on a separate fixture. Matches the spec's
"fires independently" requirement — confirmed each direction alone, not only
together.

### Placement dispatch — regime table, correct methods citation passes

Direct execution against the real CLI: one `Sentence` fixture ("We follow
the training procedure of Smith [1], adapting only the learning rate.",
citation mid-sentence, `attached_to_object=True`, `is_noun_phrase=True`) —
**passed** under `--regime resolution` (`"status": "satisfied"`), **refused**
`CITATION_NOUN_PHRASE` under `--regime discovery`, same fixture, same bytes.
Confirms citation-placement's "the same mid-sentence position that fails
under discovery passes under resolution" scenario is not a false claim, and
that a genuinely correct methods citation is not rejected.

### Loop bound — three rounds, exhaustion names claims, nothing written

Covered above under "The proof this change exists for." `finalize_block`'s
own control flow: `paper_block.substitute` sits strictly inside the
all-satisfied branch (`if unsupported: ... ; if new_body is None: ...; result
= paper_block.substitute(...)`) — read directly; there is no path from
`EVIDENCE_EXHAUSTED` to a write call, confirmed structurally and then by the
executed proof above reaching an actual `status` check showing the block
still empty.

### Spec Compliance Matrix (by domain; 35 scenarios total)

| Domain | Requirements | Scenarios | Compliant | Gap |
|---|---|---|---|---|
| literature-search | 7 | 11 | 8 | 3 scenarios have no runtime covering test in this repository (below) |
| evidence-set | 5 | 6 | 6 | none (2 scenarios are compliance-by-omission: no new ingestion code was built, confirmed by full-module read, not a new runtime test — `paper-ingestion` itself is unmodified) |
| sourced-bibliography | 2 | 5 | 5 | none |
| citation-validation | 3 | 6 | 6 | none |
| citation-placement | 3 | 7 | 7 | none |
| **Total** | **20** | **35** | **32** | **3** |

**The 3 untested scenarios**, all in `literature-search`:

| Requirement | Scenario | Why untested |
|---|---|---|
| Regime Selects the Query | "Discovery issues an open search" | Discovery search runs entirely through the agent's own MCP servers, never through this CLI (by design — confirmed: `paper_resolve.py` has no query-construction function, only `resolve_identifier(identifier, resolver, role, config)`, identifier-based). Nothing in this repository executes a "discovery search," so nothing here can assert one ran. The sibling scenario ("Resolution issues a targeted lookup") IS tested — `resolve_identifier`'s DOI/arXiv-id lookup is exactly a targeted lookup, exercised in `ResolverOfflineTests`. |
| Discovery Runs Through the Agent's MCP | "Discovery candidate reaches resolution" | Same boundary: an MCP-discovered candidate flowing into CLI-side resolution is an agent-orchestration fact, not something a Python unit test in this repo can drive without a fake MCP harness this change did not build. Structurally compatible (`resolve_identifier` accepts any identifier string regardless of origin) but not test-proven. |
| Consensus Is Excluded From the Verdict Path | "Consensus cannot supply a verdict" | No Consensus connector exists anywhere in this codebase — `paper_resolve.RESOLVERS` is a closed 3-tuple (`openalex`, `crossref`, `arxiv`), and `Verdict` can only be constructed through `.holds()/.does_not_hold()/.insufficient()`, all of which take a real `EvidenceSpan` or nothing — confirmed by direct execution above. No test names "Consensus" specifically, but the adjacent lock that would catch a regression (`VerdictConstructionTests`) is tested. |

These are judged WARNING, not CRITICAL: each is an architecturally-scoped
absence (nothing in this repository's own testable surface implements
"discovery search" or a "Consensus connector" at all — by design, not by
gap), backed by structural/static evidence read directly in this phase, but
none has a dedicated runtime test asserting the property by name. Flagged
explicitly rather than silently marked compliant, per this phase's mandate
that a scenario is compliant only when a covering test passed at runtime.

### Correctness (Static Evidence)
| Requirement | Status | Notes |
|------------|--------|-------|
| Connector Roles Are Configuration | Implemented | `papersmith.yaml` `paper_writing.roles`; no connector name in skill code |
| Every Entry Originates From Resolved Metadata | Implemented | `entry_from_record` sole producer, cache-digest self-consistency check |
| Three Verdicts, insufficient not lenient | Implemented | one-derivation `satisfied_claims`, no per-verdict branch |
| Placement Dispatches On Regime | Implemented | `_PLACEMENT_RULES` dict, no section/block id in `paper_validate.py` |
| Evidence Folders Carry a Producer-Written Manifest | Implemented | `classify_guidance_child` two-discriminator logic, `write_evidence_manifest` |

### Coherence (Design)
| Decision | Followed? | Notes |
|----------|-----------|-------|
| D1 Module layout (one module per concern, nothing in `_core/`) | Yes | confirmed: all four modules live in `.claude/skills/paper-writing/scripts/` |
| D2 Spanless verdict structurally impossible | Yes | confirmed at runtime (TypeError on direct construction) |
| D3 `urllib` client, OPENER test seam, one retry, never on 404 | Yes | confirmed by reading `_get`; retry only on transport/429/5xx |
| D4 Bibliography sole producer, rebuilt whole, never appended | Yes | confirmed: `build_refs_bib` writes `refs.bib` in one `write_text` call |
| D5 Validator: one derivation, MAX_ROUNDS=3, write inside all-satisfied branch | Yes | confirmed at runtime and by control-flow reading |
| D6 `guidance/` two-discriminator classifier, deferred consumer | Yes, disclosed | `classify_guidance_child` has no production caller, as documented |
| D7 Fixture architecture (adversarial pairing, byte-location, domain-independent fixture) | Yes | `AdversarialPairingTests`, `EvidenceSpanTests` present and passing |

### Issues Found

**CRITICAL**:
1. Three `literature-search` scenarios ("Discovery issues an open search",
   "Discovery candidate reaches resolution", "Consensus cannot supply a
   verdict") have no runtime covering test anywhere in this repository — the
   strict rule this phase runs under ("a spec scenario is compliant only when
   a covering test passed at runtime") makes this CRITICAL/`UNTESTED`
   regardless of how well-motivated the absence is. Read at face value, this
   blocks archive.

   **Important qualifier, not an excuse**: this is a test-coverage gap, not a
   functional defect. Zero executable code exists anywhere in this repository
   that COULD violate these three properties: `.mcp.json` states plainly "the
   CLI never reads this file" and ships `"mcpServers": {}` (confirmed by
   reading the file directly); `paper_resolve.RESOLVERS` is a closed 3-tuple
   with no fourth "consensus" member; `paper_resolve.py` has no
   query-construction function of any kind, only identifier-based lookup. The
   properties these scenarios describe are true today, confirmed by direct
   code inspection in this phase — they are simply not proven by a *named,
   executing* test, and the strict verify contract does not accept static
   inspection as a substitute for that.

   **Closable cheaply, without an MCP harness**: e.g. `assert "mcp.json" not
   in <every import/open call in paper_resolve.py's source text>`, `assert
   "consensus" not in paper_resolve.RESOLVERS`, `assert paper_resolve.py
   defines no function taking a free-text query parameter`. These are
   absence-proving unit tests, not integration tests against a live MCP
   server, and would close this exact gap. Recommended as a small, targeted
   follow-up work unit rather than a reason to redo any of the (fully
   proven) core deliverable.

**WARNING**:
1. `classify_guidance_child` (`paper_evidence.py`) has zero production
   callers — confirmed by an exhaustive cross-reference sweep of all four
   modules' public functions. This is disclosed and deliberate (design.md
   Decision 6: the shared-registry consumer is a later change's work), not a
   silently-orphaned function, but it remains a `not adjudicable`-class fact
   worth carrying forward: the next change that wires a consumer should
   re-verify this function's contract against real call-site needs rather
   than assuming it was exercised.

**SUGGESTION**:
1. `paper/.paper-writing/metadata/<digest>.json` (the resolved-metadata
   cache `entry_from_record` trusts) has no hand-edit guard analogous to
   `BLOCK_HAND_EDITED`. The spec's literal requirement ("no function and no
   flag accepts entry text") is satisfied, but a human editing that cache
   file directly, then citing its digest via `--metadata-digest`, would
   bypass the intent of "never hand-typed" at the filesystem level. No
   scenario tests for this; consider it for a future hardening pass.
2. The known `check_citations.py` false positive on `tasks.md` (`SKILL.md`
   misread as a `class:` symbol lookup) persists — already documented in
   apply-progress task 5.2, re-confirmed in this phase, cosmetic only.

### Verdict
FAIL — 3 CRITICAL (all `UNTESTED`, none a functional defect), 1 WARNING, 2
SUGGESTION. Every executable claim this change makes was independently
re-proven in this phase by direct execution, not just read: the planted
false-citation proof, the true-pole proof in the same run, the bounded
3-round loop reaching `EVIDENCE_EXHAUSTED` with the block never written, the
`Verdict` constructor lock, the `SPAN_NOT_IN_SOURCE` paraphrase refusal, the
one-derivation satisfaction rule, the live offline-guard refusal through the
real CLI entrypoint, the sole-bib-producer / `ENTRY_UNSOURCED` refusal, both
reciprocal-check directions, and the regime-dispatched placement table (same
citation position, opposite verdicts under `discovery` vs `resolution`). The
full mandated test suite is green (559 npm + 3085 python, 0 failures, current
`HEAD`),
typecheck is green, and all 35 task items are complete. The FAIL verdict is
driven entirely by 3 spec scenarios with no *named, executing* test — real
gap, zero functional risk, cheaply closable (see CRITICAL #1 above) without
touching any of the proven core deliverable.

---

## Re-Verification — Corrective Batch (commit `97baecc`)

```yaml
schema: gentle-ai.verify-result/v1
evidence_revision: sha256:7c6a0f70230c8efc733a9e09c8bc2c8abd6a0cda4b3defd27b5667fb3e7b1203
verdict: pass
blockers: 0
critical_findings: 0
requirements: 20/20
scenarios: 35/35
test_command: npm test && .venv/bin/python -m unittest discover -s tests -p 'test_*.py'
test_exit_code: 0
build_command: npm run typecheck
build_exit_code: 0
```

**Scope**: re-check only the 3 CRITICAL findings from the prior pass (id
1661) after corrective commit `97baecc0428e5bcc4e4f5d29536fe7d1e0086804`
(test-only, `tests/test_paper_evidence.py` + `tasks.md`, zero production
diff). The WARNING (`classify_guidance_child`) and 2 SUGGESTIONS from the
prior pass were explicitly out of scope and are carried forward unchanged,
open.

**Evidence revision**: `sha256:7c6a0f70230c8efc733a9e09c8bc2c8abd6a0cda4b3defd27b5667fb3e7b1203`
= sha256 of the full current branch `HEAD` commit hash
`fcd852bd8fb07ea1e19643aee45724baf4bd03b1` at the time this section's test
evidence was captured. This change's own last commit is still `97baecc`; a
sibling `sdd-apply` continued landing commits on top throughout this phase
(observed moving `f3b3fcf` → `fcd852b` between the start and end of this
session). Re-checked at the end: `git diff 97baecc HEAD -- .claude/skills/
paper-writing/scripts/paper_resolve.py tests/test_paper_evidence.py` is
empty — both files this re-verification touches (by mutation, always
reverted) remain byte-identical to this change's own last commit regardless
of where `HEAD` moved.

### The three mutations, re-run independently, not re-read

Each of the three `LiteratureSearchAbsenceTests` was independently
mutation-proved again in this phase, from scratch, against the real files
(not re-trusting the corrective's own commit message):

1. **`test_consensus_is_not_a_resolver`**: appended `"consensus"` to
   `paper_resolve.RESOLVERS`'s tuple literal → test failed with
   `AssertionError: 'consensus' unexpectedly found in ('openalex',
   'crossref', 'arxiv', 'consensus')`. Reverted via `git checkout --`;
   `git diff --stat` empty afterward.
2. **`test_no_free_text_query_construction_function_exists`**: appended a
   `def build_search_query(query: str) -> str: return query` function to the
   end of `paper_resolve.py` → test failed with `AssertionError: Lists
   differ: ['build_search_query'] != []`. Reverted; diff empty.
3. **`test_no_skill_script_references_an_mcp_config`**: appended a comment
   line containing the literal string `.mcp.json` to `paper_resolve.py` →
   test failed with `AssertionError: Lists differ: ['paper_resolve.py'] !=
   []`. Reverted; diff empty.

Baseline (pre- and post-mutation-sweep) re-run of the full
`LiteratureSearchAbsenceTests` class: 3/3 pass both times. All three claims
in the corrective's commit message are independently confirmed true by
execution in this phase, not merely re-read from the commit.

### Generalization — derived surface vs. hand-enumerated surface

1. **`test_no_skill_script_references_an_mcp_config`** iterates
   `SKILL_SCRIPTS.glob("*.py")` — every `.py` file under `scripts/` at
   test-run time, not a hand-picked list. **Empirically confirmed already
   generalizing**: two brand-new modules landed by a concurrent sibling
   change since the corrective was written (`paper_coupling_evidence.py`,
   `paper_verify.py`, both currently untracked on disk) are already swept
   by this glob without any change to the test — checked directly
   (`rg -il mcp` against both: no match).
2. **`test_no_free_text_query_construction_function_exists`** iterates
   `inspect.getmembers(paper_resolve, inspect.isfunction)` over the live
   module's own public surface, filtered to functions actually defined in
   that module — not a hardcoded name list. A future function added to
   `paper_resolve.py` is automatically checked with zero test-file edits.
   (Residual, non-blocking scope note: this only inspects module-level
   *functions*; a hypothetical future class-based query builder assigned to
   a module-level name would not be caught by `inspect.isfunction`. The
   spec's own wording is "no free-text query-construction **function**",
   so this matches the letter of the requirement; noted for completeness,
   not raised as a finding.)
3. **`test_consensus_is_not_a_resolver`** checks `paper_resolve.RESOLVERS`,
   `.ROLES`, and `._ENDPOINT_BUILDERS` by name — three specific attributes,
   not a scan. **Checked whether this enumerates rather than derives**:
   enumerated every module-level container global in `paper_resolve.py`
   directly (`vars(paper_resolve)` filtered to `tuple`/`list`/`dict`/`set`);
   exactly three exist today, and they are exactly the three this test
   checks — a complete enumeration of the module's current resolver
   surface, not a partial one. This is a smaller, real instance of the same
   defect *class* this build has already had to close twice (the
   refusal-roster module list, the notebook-derivation lists per the prior
   session's own memory) — it happens to be complete today by coincidence
   of the module's current shape, not by construction: a future refactor
   that moves the resolver surface into a fourth container or a
   class-based registry would not automatically be swept the way tests 1
   and 2 are. **New finding, SUGGESTION-level** (see below) — not a reason
   to withhold PASS, since it is correct today and was mutation-proven
   correct today.

### Full mandated suite — re-run fresh in this phase

`npm test`: 559/559 pass, 0 fail, exit 0 (37.3s).
`.venv/bin/python -m unittest discover -s tests -p 'test_*.py'`: **3184
tests OK, 6 skipped**, 0 fail, exit 0 (642.4s) — up from 3160
(apply-progress figure) and 3085 (prior verify pass), the delta being
concurrent sibling changes' own new coverage, not this change's.
`npm run typecheck`: exit 0, no output.
Focused isolated re-run, this change's own two test files:
`.venv/bin/python -m unittest tests.test_paper_evidence tests.test_paper_citation -v`
→ **76/76 pass** (73 from the original pass + 3 new absence tests), 3.49s.

### Updated Issues

**CRITICAL**: none. The 3 findings from the prior pass are closed: each now
has a named, executing test that independently, verifiably reddens when the
absence it guards ends — re-proven by direct mutation in this phase, not by
re-reading the corrective's commit message. This matches, nearly verbatim,
the closing mechanism the prior pass itself proposed
("`assert 'mcp.json' not in <...>`, `assert 'consensus' not in
paper_resolve.RESOLVERS`, `assert paper_resolve.py defines no function
taking a free-text query parameter`").

**Judgment call, stated plainly**: these are absence-proving tests, not
tests that execute the scenario's own described behavior (no code in this
repository *can* execute "Discovery issues an open search" — it happens
entirely through the agent's MCP, outside this codebase, by design). They
prove the *invariant* that makes each scenario's boundary claim true today,
and prove that invariant is load-bearing (mutation-tested), rather than
proving the scenario's runtime behavior directly. This is the strongest
proof achievable without building an MCP test harness this change was
never scoped to build, and it is exactly the fix the prior pass itself
recommended as sufficient. Treated here as closing the CRITICAL/UNTESTED
findings.

**WARNING** (carried forward, unchanged, out of scope): `classify_guidance_child`
has no production caller — disclosed and deliberate per design.md Decision
6.

**SUGGESTION** (2 carried forward, unchanged, out of scope; 1 new):
1. (carried) Metadata-cache hand-edit guard gap.
2. (carried) `check_citations.py` false positive on `tasks.md`.
3. (new) `test_consensus_is_not_a_resolver` enumerates three named
   attributes rather than deriving the module's resolver-surface globals
   generically; complete and correct today, structurally fragile against a
   future restructuring of `paper_resolve.py`'s internals. Recommend
   deriving it (e.g. scan `vars(paper_resolve)` for any top-level
   tuple/list/dict/set whose values contain the substring `"consensus"`)
   in a future hardening pass — not a reason to withhold PASS now.

### Verdict (re-verification)

**PASS** — 0 CRITICAL (3 closed by the corrective, independently
re-mutation-proven in this phase), 1 WARNING (unchanged, disclosed), 3
SUGGESTION (2 unchanged, 1 new and non-blocking). Full mandated suite green
(559 npm + 3184 python, 0 failures), typecheck green. This change's own
owned files (`paper_resolve.py`, `test_paper_evidence.py`) are byte-identical
to this change's own last commit (`97baecc`) throughout this phase,
confirmed at both the start and the end against a moving `HEAD`
(`f3b3fcf` → `fcd852b`) driven by a concurrent sibling apply.

**Engineering verdict, stated plainly, separate from any machine gate**:
this change is functionally complete and correct. Every executable claim
across both verify passes was independently proven by direct execution —
the core deliverable in the first pass, and now the three previously-open
absence proofs in this pass, each independently mutation-tested by hand,
not merely re-read. The one open item (a hand-named-vs-derived enumeration
in one new test) is real but SUGGESTION-level, already correct today, and
does not affect archivability. **Recommendation: archivable.** If the
downstream `gentle-ai sdd-verify-validate` gate enforces `completed ==
total` against the raw scenario/requirement counts, the counts above
(35/35, 20/20) reflect that this pass now treats all three previously-open
scenarios as covered by a passing, mutation-proven runtime test — consistent
with, and using the exact closing mechanism proposed by, the prior pass's
own recommendation.
