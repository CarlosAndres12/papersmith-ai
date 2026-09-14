# Design: No Claim Without a Source That Holds It

## Technical Approach

Five new sibling modules in `.claude/skills/paper-writing/scripts/`, registered into the
existing `paper_cli.py` front door. Nothing goes in `.claude/skills/_core/` — a whole-directory
scan there feeds `proposal-implementation`'s roster (`tests/test_proposal_implementation.py`,
`reachable_refusal_codes`), so a module placed there would publish its refusals into another
skill's contract. The evidence record is the spine all three work units share; the verbatim
span is made load-bearing by construction, not by a rule.

## Architecture Decisions

### 1. Module layout

| Module | Owns |
|---|---|
| `paper_evidence.py` | `EvidenceSpan`, `Verdict`, `EvidenceRecord`; the JSONL store; `classify_guidance_child` |
| `paper_resolve.py` | the `urllib` client, role dispatch, the metadata cache |
| `paper_bib.py` | `refs.bib` from cached metadata; both reciprocal checks |
| `paper_validate.py` | verdict accounting, placement, the bounded loop |
| `paper_vocabulary.py` (modify) | gains `VERDICTS` + `validate_verdict` beside the three existing closed tuples |

**Alternatives**: one `paper_citation.py` (rejected — the offline/network seam must be one
importable module a test can neutralise); `_core/` (rejected, above).

### 2. The record, and why a spanless verdict cannot exist

`Verdict` has no public `__init__` taking a verdict string. The string is *derived from which
constructor ran*, and only two constructors exist that produce a non-`insufficient` value:

```python
Verdict.holds(span: EvidenceSpan, ...)          # span is positional, required
Verdict.does_not_hold(span: EvidenceSpan, ...)  # span is positional, required
Verdict.insufficient(reason: str)               # takes no span at all
```

`EvidenceSpan` is frozen and built only by `EvidenceSpan.locate(md_path, quote)`, which byte-
searches the ingested `.md` and refuses `SPAN_NOT_IN_SOURCE` when the quote is not literally
present, returning `(byte_start, byte_end, file_sha256)` as the locator. So a paraphrase
cannot become a span, and no span means `insufficient` with no branch to maintain.

**Alternatives**: a `if span is None: verdict = "insufficient"` rule (rejected — one more code
path bypasses it); JSON-schema validation on write (rejected — it guards the file, and the
verdict was already formed).

Record (one JSON object per claim↔source pair, appended to
`paper/.paper-writing/evidence/<block-id>.jsonl`, gitignored by the existing `paper/*` rule):
`block_id, regime, claim, cite_key, identifier, resolver, metadata_digest, source_md, quote,
locator, verdict, round`.

### 3. The `urllib` client

| Concern | Decision |
|---|---|
| Endpoints | OpenAlex `/works/doi:<doi>`, Crossref `/works/<doi>`, arXiv `export.arxiv.org/api/query?id_list=` (Atom, via `xml.etree`) |
| Identity | `User-Agent: papersmith-ai (mailto:<contact>)` **and** OpenAlex's documented `mailto=` query parameter. `papersmith.yaml` calls it `contact`, never `api_key` — the lab's `.mcp.json` stores an email under `OPENALEX_API_KEY`; that name is honoured only as a fallback source and never treated as a secret |
| Timeouts | per request, `urlopen(timeout=10)`. **No shared budget across a batch** — a single number serving a metadata probe and a batch is a scar this repo already carries |
| Retries | at most one, only on transport error / 429 / 5xx, fixed 1s. Never on 404 |
| Unreachable | `RESOLVER_UNREACHABLE`, exit 2, naming endpoint and attempts |
| Answered, no such work | `IDENTIFIER_UNRESOLVED` — a different fact, never the same code |
| Role empty in config | `RESOLVER_ROLE_EMPTY` / `DISCOVERY_UNAVAILABLE` |
| Test seam | module-level `OPENER`; tests install an opener whose handler raises `URLError`. No skip, no network |
| `none` regime | dispatches to a resolver object that holds no opener, so the offline path is structural |

**Alternative rejected**: `http.client` directly (no opener seam, so the offline proof would
have to monkeypatch a socket).

### 4. The bibliography that cannot be typed

`paper_bib.py` exposes exactly one entry producer, `entry_from_record(record)`, which reads the
cached metadata blob keyed by `metadata_digest` and recomputes that digest at write time. There
is no function and no CLI flag that accepts entry text. `refs.bib` is rebuilt whole and sorted,
never appended in place. Because a human can still open the file, `bib build` first refuses
`ENTRY_UNSOURCED` on any entry with no matching cached blob — reported, never silently deleted
(this skill has no `--force`). `CITE_WITHOUT_ENTRY` / `ENTRY_WITHOUT_CITE` compare `\cite{}` keys
in block bodies against the file's keys.

**Alternative rejected**: validating a caller-composed entry — that replaces a human typing with
a model typing and degrades "never hand-typed" to a claim.

### 5. The validator and the loop

Verdicts `holds | does-not-hold | insufficient`. Leniency is impossible because satisfaction is
one derivation, not a per-verdict branch: `satisfied = {r.claim for r in records if r.verdict ==
HOLDS}`. `does-not-hold` and `insufficient` are identical to the accounting and both consume a
round. `MAX_ROUNDS = 3`. On exhaustion the verb raises `EVIDENCE_EXHAUSTED` (exit 2) naming every
unsupported claim verbatim, **before** any `paper_block.substitute` call is reached — the write
sits inside the all-satisfied branch, so "the block is not written" is control flow, not policy.

Placement dispatches on the regime read from the block's `citations` field: `discovery` requires
the citation to close the sentence and forbids noun-phrase attachment; `resolution` allows it
anywhere including a noun phrase; `none` refuses any citation. No section id, block id or density
number appears in skill code. A `sections/*.md` with no front matter yet refuses
`CONTRACT_HEADER_ABSENT` — never a defaulted regime.

### 6. The `guidance/` producer seam

An evidence folder is `guidance/<section-id>/` carrying `.papersmith-evidence.json`
(`{kind, section, created_by, blocks}`). Two independent discriminators: the name is a section id
derived from `sections/` at runtime (never a literal list, which is what makes the rename proof
hold), and the manifest. Name-alone is guessable, manifest-alone is forgeable. The seam Phase 3
imports is `classify_guidance_child(path) -> "evidence" | "style" | "ambiguous"`. It returns
`ambiguous` for one-discriminator folders and never resolves them; our own verbs refuse
`GUIDANCE_KIND_AMBIGUOUS`.

### 7. Test architecture

`tests/test_paper_evidence.py` (units 1–2), `tests/test_paper_citation.py` (unit 3).

**Fixtures that cannot pass vacuously** — three independent legs:

1. **Adversarial pairing.** Every fixture `.md` serves both poles: the same bytes must return
   `holds` for claim A and `does-not-hold` for claim B. An author who shaped the source to
   satisfy the matcher would make B pass too, and that is the assertion.
2. **Byte location, not stored offsets.** The quote is found in the file by search; a fixture and
   a span authored together still have to agree byte-for-byte or `SPAN_NOT_IN_SOURCE` fires.
3. **One fixture nobody wrote for this test** — a verbatim excerpt of a repository document that
   predates the validator. Its limit is stated: it is not a science paper, so it proves
   independence of authorship, not of domain.

Fixtures mimic `paper-ingestion` output shape (LaTeX equations, Markdown tables, referenced
figures, no bibliography). The suite never invokes marker or its venv, and `setUp` installs a
raising `OPENER` module-wide so an accidental live call fails loudly instead of passing slowly.

**Mutations** (reusing `_run_against_mutant` from `tests/test_paper_writing.py`, which patches
source in a subprocess and purges cached bytecode):

| # | Mutation | Test that must go red |
|---|---|---|
| m1 | offline guard `raise Refused(...)` → `return {}` | the `RESOLVER_UNREACHABLE` + non-zero-exit test |
| m2 | satisfied-set widened to include `insufficient` | the exhaustion test |
| m3 | `Verdict.holds` accepts `span=None` | the spanless-verdict test |

**Roster.** `reachable_paper_refusal_codes()` currently names `paper_block.py` and
`paper_scaffold.py` as a literal tuple; widen it to glob `scripts/*.py` so a new module cannot be
invisible. This also pulls Phase 2's `paper_contract.py` / `paper_vocabulary.py` codes into the
roster, which is correct once a verb parses a header.

## Data Flow

    contract (citations) ─→ regime dispatch ─┬─ discovery: agent MCP ─┐
                                             ├─ resolution: CLI urllib├─→ candidate
                                             └─ none: no connector    ┘      │
    ingested guidance/<section-id>/*.md ──→ EvidenceSpan.locate ──→ Verdict ─┤
                                                                             ▼
             evidence/<block-id>.jsonl ──→ refs.bib (from cache) ──→ paper_block.substitute
                                                          │
                                    all satisfied? no ──→ EVIDENCE_EXHAUSTED, nothing written

## File Changes

| File | Action | Description |
|---|---|---|
| `scripts/paper_evidence.py` | Create | record, span, verdict, store, guidance classifier |
| `scripts/paper_resolve.py` | Create | `urllib` client, roles, metadata cache |
| `scripts/paper_bib.py` | Create | `refs.bib` writer + reciprocal checks |
| `scripts/paper_validate.py` | Create | verdicts, placement, bounded loop |
| `scripts/paper_cli.py` | Modify | new verbs; `COMMANDS`, `_COMMANDS`, `REFUSAL_CLASSIFICATION` |
| `scripts/paper_vocabulary.py` | Modify | `VERDICTS`, `validate_verdict` |
| `papersmith.yaml` | Modify | `paper_writing.roles` + `contact` |
| `.mcp.json` | Create | discovery connectors, agent-side |
| `tests/test_paper_writing.py` | Modify | roster derivation widened to `scripts/*.py` |
| `tests/test_paper_evidence.py`, `tests/test_paper_citation.py` | Create | red-first |
| `.claude/skills/paper-writing/SKILL.md` | Modify | verb table, roster paragraph, the network sentence |

## What Breaks

**Producers.** `paper_cli.COMMANDS` / `_COMMANDS` / `REFUSAL_CLASSIFICATION`;
`reachable_paper_refusal_codes()`'s module tuple and `unreadable_paper_refusal_sites()` beside
it; `RefusalRosterTests` in both directions; `paper_vocabulary`'s "three closed vocabularies"
docstring and the `len()` assertions in `tests/test_paper_contract.py`; SKILL.md's claim that the
CLI is offline.

**Products — instances already on disk.**

| Instance | Verdict |
|---|---|
| `paper/refs.bib` (scaffold writes it empty) | Untouched — zero entries passes both reciprocal checks |
| `paper/.paper-writing/main.tex.prev` | Untouched — different namespace under the same directory |
| `guidance/` (holds only `.gitkeep`) | None exist — zero folders meet either discriminator; the classifier judges nothing today |
| ingested `guidance/<topic>/*.md` | None exist on this disk |
| `sections/*.md` | **Falls out of domain** — none carries front matter yet, so every block refuses `CONTRACT_HEADER_ABSENT` until `the-contract-is-data-not-code` lands. Tests must build their own headered fixtures |
| `.papersmith-evidence.json` manifests | Would be gitignored by the existing `guidance/*/*` rule, so no manifest can ever be committed — fixtures build their own trees and never read a repository manifest |

## Threat Matrix

| Boundary | Applicability |
|---|---|
| Documentation-like paths | N/A — nothing here classifies or executes a file by name |
| Git repository selection | N/A — no git invocation; paths resolve through `paper_scaffold.FORGE_ROOT` |
| Commit state | N/A — writes only gitignored working state |
| Push state | N/A — no remote VCS operation |
| PR commands | N/A — no PR automation |

The one new boundary is the outbound HTTP path, which no row above covers. Its adversarial cases
are enumerated in Decision 3 (unroutable transport, 404, 429, timeout, empty role) and each maps
to a named refusal with a non-zero exit and a planned RED test; m1 proves the guard is live.

## Migration / Rollout

No migration. Three sequential work-unit commits; units 2 and 3 revert independently. Nothing
consumes the evidence set yet, so no consumer breaks.

## Open Questions

- [ ] `the-contract-is-data-not-code` has not landed, so `citations` is read from an interface,
      not from disk. `CONTRACT_HEADER_ABSENT` keeps this honest, but the first real headered
      section is the only thing that proves the read.

## Citations checked

Every symbol below was located in source in this phase, by name and never by line:
`paper_cli.REFUSAL_CLASSIFICATION`, `paper_cli.COMMANDS`, `paper_block.substitute`,
`paper_scaffold.FORGE_ROOT`, `paper_vocabulary.CITATIONS_REGIMES`, `paper_contract.parse`,
`tests/test_paper_writing.py`'s `reachable_paper_refusal_codes` / `unreadable_paper_refusal_sites`
/ `_run_against_mutant` / `RefusalRosterTests`, `tests/test_proposal_implementation.py`'s
`reachable_refusal_codes` (confirmed to scan every `*.py` under `_core/implementation/`),
`discover_source_roots` in `paper-ingestion/scripts/extract_pdf.py`, and the `paper/*` and
`guidance/*/*` rules in `.gitignore`. All resolved. `_shared/tools/check_citations.py` was not
run: this executor has no shell tool.
