# Proposal: Only the Block Changes

## Intent

The `paper-writing` skill writes a paper section by section into one `main.tex`. Unlike this repo's deliberation skills it publishes no successor revision, so a bad write is unrecoverable: hours of accepted prose are destroyed by one wrong offset, and nothing announces it. Phase 1 builds the substitution unit everything else rests on — replace exactly one named block, leave every other byte of the file identical, and refuse by name when the document does not permit the write.

## Scope

### In Scope

- `paper/` scaffold: exactly `main.tex`, `refs.bib`, `Figures/`. Created when absent, never overwritten when present (idempotent; a second run leaves bytes identical).
- Block delimiting inside `main.tex` and the byte-for-byte substitution engine.
- Named refusals for every way the document can fail to admit a write.
- The first CLI slice: `scaffold`, `open`, `substitute` (plus `status` of the block table).
- The proof: independent byte-identity check, plus the mutations that make it fire.

### Out of Scope

- Parsing `sections/*.md`, the fact chain, readiness, declarations, agents, MCP, citations, figures. Block ids are **opaque strings** here; their grammar belongs to `the-contract-is-data-not-code`.

## Capabilities

### New Capabilities
- `paper-scaffold`: creating and re-entering the `paper/` directory without clobbering.
- `block-substitution`: delimiting, locating, replacing and refusing over blocks in `main.tex`. The CLI is the surface of both.

### Modified Capabilities
- None.

## Approach

**Delimiters are LaTeX comments carrying a digest.** A block is the byte range from the start of its begin-marker line through the end of its end-marker line:

```
%% paper-writing block <id> begin sha256=<hex>
<body>
%% paper-writing block <id> end
```

Comments are chosen because they are invisible in the PDF, legal *mid-paragraph* — a comment line consumes its own newline, so it adds neither space nor paragraph break, which the one-paragraph abstract's seven slots require — and because they keep the document self-describing. Rejected: a sidecar offsets index (a second source of truth that any human keystroke invalidates) and `\begin{}` environments (they change what is rendered and cannot sit inside a paragraph).

**Hand edits are detected, not overwritten.** The digest is of the body as this engine last wrote it. A mismatch is `BLOCK_HAND_EDITED`, cleared only by an explicit `--adopt`, mirroring `materialize --adopt`.

**Substitution never creates.** A missing pair is `BLOCK_ABSENT`; `open` installs an empty pair at a caller-named position (`--after <id>` or `--at-end`) — ordering is contract business, never the engine's. First write is `open` then `substitute`, so rewrite has exactly one code path.

**All I/O is binary.** Never text mode: universal newlines would rewrite every CRLF in the file and break the invariant silently.

**Refusals** follow `Refused(code, detail)` and are classified invocation-defect vs work-state, per `implementation_cli`: `PAPER_ABSENT`, `PAPER_NOT_A_DIRECTORY`, `TEX_UNDECODABLE`, `BLOCK_ABSENT`, `BLOCK_DUPLICATED`, `BLOCK_UNPAIRED`, `BLOCK_NESTED`, `MARKER_MALFORMED`, `BLOCK_HAND_EDITED`, `CONTENT_CARRIES_MARKER`, `ANCHOR_ABSENT`, `PAPER_OUTSIDE_REPOSITORY`.

**The safety net is three layers, each doing what only it can do.** (1) The invariant is checked on candidate bytes *in memory*; a violating substitution never reaches disk — not writing is stronger than recovering. (2) Same-directory temp + `os.replace`, so an interrupted process never leaves a torn `main.tex`. (3) A one-deep pre-image at `paper/.paper-writing/main.tex.prev` (gitignored), because git cannot help mid-session and a clean-worktree requirement would make section-by-section writing unusable — the worktree state is reported, never demanded.

**The proof, and the mutation.** The check re-parses the written file from scratch, strips every block region, and compares that projection against the same projection of the pre-image — a different computation from `prefix + new + suffix`, so it can go red. Three mutations must make it red: (M1) start the region one byte earlier, consuming the preceding newline; (M2) open `main.tex` in text mode against a CRLF fixture; (M3) skip the digest comparison. Red-first, per `strict_tdd`.

## Affected Areas

| Area | Impact | Description |
|---|---|---|
| `.claude/skills/paper-writing/SKILL.md` | New | Skill body, sibling of the two precedents |
| `.claude/skills/paper-writing/scripts/paper_cli.py` | New | Fail-closed front door, stdlib only, python3.12 |
| `tests/test_paper_writing_*.py` | New | Python `unittest`, forge-side |
| `.gitignore` | Modified | Ignore `paper/.paper-writing/` |
| `paper/` | New | User data; tracked |

## Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| Byte identity holds and the document stops compiling | Med | The suite proves bytes, never rendering. Declare it unproven; markers never sit adjacent to a blank line the engine did not already own |
| The identity check computed the same way as the substitution — a green that cannot go red | Med | Independent re-derivation by re-parsing; M1–M3 recorded as executed, not asserted |
| Text-mode I/O rewrites CRLF across the whole file | Med | Binary I/O everywhere; a CRLF fixture is a first-class test |
| A hand edit made weeks ago surfaces only at the next write | Med | Refusal names the expected and found digest; pre-image kept |
| Id grammar leaks in from the parallel contract change | Low | Shape-only validation (`[A-Za-z0-9._-]+`), no semantics |
| `paper/` location undecided (see question round) | Med | CLI takes `--paper <dir>`; only the default is at stake |

## Rollback Plan

`git rm -r .claude/skills/paper-writing tests/test_paper_writing_*.py` and revert the `.gitignore` line. `paper/` is untouched by rollback and remains a valid LaTeX document — markers are comments, so the paper survives the skill's removal. That property is the format's main defence.

## Dependencies

- None. Stdlib only, no LaTeX toolchain required to test.

## Success Criteria

- [ ] `scaffold` run twice leaves the tree byte-identical the second time.
- [ ] A substitution on a CRLF fixture with a mid-paragraph block leaves every byte outside the region identical, proven by independent re-derivation.
- [ ] M1, M2 and M3 each turn a named test red; the run is recorded, not claimed.
- [ ] Every refusal code above is reachable from the CLI, proven by a roster test derived from the code rather than hand-listed.

## Proposal question round

Answering these sharpens the proposal; skipping them accepts the assumption beside each.

1. **Where does `paper/` live?** Assumed: the forge repository root, beside `sections/`. `implementations/` is gitignored, and a paper no clone receives is a paper nobody can review. Correct this if the paper belongs to the target repository.
2. **When the engine finds a hand edit, whose text wins by default?** Assumed: neither — it refuses, and `--adopt` is the human saying "take mine as the new baseline". Is a `--force` that discards the human's text ever wanted?
3. **May `open` place a block anywhere the caller names, or only append?** Assumed: `--after <id>` and `--at-end`, both caller-supplied. Phase 2 will supply contract order.
4. **Is one level of undo enough?** Assumed: yes, plus git. A deeper history is a ledger, and this skill has none.
