# Measurement M1 — The `$$` Display-Fence Blast Radius

Executed, not authored. Every number below is copied verbatim from a real
run of `tests/math_fence_blast_radius.py`; no figure in this file was typed
by hand.

Command:

```
.venv/bin/python tests/math_fence_blast_radius.py
```

## Before table — run on an otherwise-unmodified tree

Captured before `paper_style.py`'s or `paper_bindings.py`'s `_MATH_DISPLAY_RE`
was touched (`git status` on both files was clean at capture time).

```
=== M1 over the committed fixture corpus (asserted) ===
Token counts (len(normalize_tokens(file))):
  bracket_display.md: 24
  display_fence.md: 51
  equation_environment.md: 22
  inline_math.md: 32
  plain_prose.md: 42
  unpaired_dollar.md: 29

Pair measurements (styled, sample) -> hits=len(tripwire_spans) overlap=overlap_against_set:
  (bracket_display.md, bracket_display.md) -> hits=1 overlap=24
  (bracket_display.md, display_fence.md) -> hits=0 overlap=2
  (bracket_display.md, equation_environment.md) -> hits=0 overlap=4
  (bracket_display.md, inline_math.md) -> hits=0 overlap=4
  (bracket_display.md, plain_prose.md) -> hits=0 overlap=2
  (bracket_display.md, unpaired_dollar.md) -> hits=0 overlap=2
  (display_fence.md, bracket_display.md) -> hits=0 overlap=2
  (display_fence.md, display_fence.md) -> hits=1 overlap=51
  (display_fence.md, equation_environment.md) -> hits=0 overlap=2
  (display_fence.md, inline_math.md) -> hits=0 overlap=2
  (display_fence.md, plain_prose.md) -> hits=1 overlap=14
  (display_fence.md, unpaired_dollar.md) -> hits=0 overlap=2
  (equation_environment.md, bracket_display.md) -> hits=0 overlap=4
  (equation_environment.md, display_fence.md) -> hits=0 overlap=2
  (equation_environment.md, equation_environment.md) -> hits=1 overlap=22
  (equation_environment.md, inline_math.md) -> hits=0 overlap=2
  (equation_environment.md, plain_prose.md) -> hits=0 overlap=2
  (equation_environment.md, unpaired_dollar.md) -> hits=0 overlap=2
  (inline_math.md, bracket_display.md) -> hits=0 overlap=4
  (inline_math.md, display_fence.md) -> hits=0 overlap=2
  (inline_math.md, equation_environment.md) -> hits=0 overlap=2
  (inline_math.md, inline_math.md) -> hits=1 overlap=32
  (inline_math.md, plain_prose.md) -> hits=0 overlap=2
  (inline_math.md, unpaired_dollar.md) -> hits=0 overlap=2
  (plain_prose.md, bracket_display.md) -> hits=0 overlap=2
  (plain_prose.md, display_fence.md) -> hits=1 overlap=14
  (plain_prose.md, equation_environment.md) -> hits=0 overlap=2
  (plain_prose.md, inline_math.md) -> hits=0 overlap=2
  (plain_prose.md, plain_prose.md) -> hits=1 overlap=42
  (plain_prose.md, unpaired_dollar.md) -> hits=0 overlap=2
  (unpaired_dollar.md, bracket_display.md) -> hits=0 overlap=2
  (unpaired_dollar.md, display_fence.md) -> hits=0 overlap=2
  (unpaired_dollar.md, equation_environment.md) -> hits=0 overlap=2
  (unpaired_dollar.md, inline_math.md) -> hits=0 overlap=2
  (unpaired_dollar.md, plain_prose.md) -> hits=0 overlap=2
  (unpaired_dollar.md, unpaired_dollar.md) -> hits=1 overlap=29

=== M1 over ambient document-sourced .md (NOT asserted -- a fresh clone holds none) ===
  (39 ambient files found; token counts only -- the pairwise tripwire/overlap scan is skipped here as computationally infeasible over real documents of this size, stated rather than silently forecast)
Token counts (len(normalize_tokens(file))):
  .atl/skill-registry.md: 1720
  .pytest_cache/README.md: 48
  .review/PENDIENTES.md: 1141
  README.md: 29303
  backup/proposals/2026-08-02T16-51-28Z/matematica_propuesta_CREDA.md: 2324
  backup/proposals/2026-09-16T22-12-13Z/proposals/research-concept-r21.md: 7285
  backup/proposals/2026-09-16T23-03-49Z/proposals/research-concept-r21.md: 7459
  guidance/data-paper/s41597-026-06758-7/s41597-026-06758-7.md: 8639
  guidance/paper-guide/Li_2026_Prog._Biomed._Eng._8_022013/Li_2026_Prog._Biomed._Eng._8_022013.md: 6572
  guidance/paper-guide/brainsci-16-00363/brainsci-16-00363.md: 10547
  guidance/reference-papers/computation-13-00116-v2/computation-13-00116-v2.md: 11861
  guidance/reference-papers/computation-14-00002-v3/computation-14-00002-v3.md: 14868
  guidance/reference-papers/computers-13-00176-v2-1/computers-13-00176-v2-1.md: 7585
  guidance/reference-papers/computers-15-00428/computers-15-00428.md: 13648
  guidance/reference-papers/mathematics-13-02602/mathematics-13-02602.md: 13135
  implementations/Domain_Adaptation/.pytest_cache/README.md: 48
  implementations/Domain_Adaptation/MIL-CREDA/AGREED.md: 11480
  implementations/Domain_Adaptation/README.md: 457
  proposals/research-concept-r01.md: 2328
  proposals/research-concept-r02.md: 2328
  proposals/research-concept-r03.md: 1701
  proposals/research-concept-r04.md: 2935
  proposals/research-concept-r05.md: 2342
  proposals/research-concept-r06.md: 3166
  proposals/research-concept-r07.md: 3253
  proposals/research-concept-r08.md: 4926
  proposals/research-concept-r09.md: 5094
  proposals/research-concept-r10.md: 5213
  proposals/research-concept-r11.md: 5377
  proposals/research-concept-r12.md: 5626
  proposals/research-concept-r13.md: 5696
  proposals/research-concept-r14.md: 5717
  proposals/research-concept-r15.md: 5775
  proposals/research-concept-r16.md: 5773
  proposals/research-concept-r17.md: 6111
  proposals/research-concept-r18.md: 6129
  proposals/research-concept-r19.md: 6137
  proposals/research-concept-r20.md: 7293
  proposals/research-concept-r21.md: 7471
```

**The ambient half, marked explicitly.** These 39 files are whatever this
checkout happens to hold today; a fresh clone holds none of them, and no
gate condition in this change depends on any number in this section
(design.md, Decision A gate table, third row). The pairwise tripwire/overlap
scan is skipped here — infeasible at this scale on this machine, stated
rather than silently forecast — so only the cheap, per-file normalized
token count is measured for the ambient half.

## After table — run once 0.6 and 0.8 have landed

Same command, same corpus, run after `paper_style.py`'s and
`paper_bindings.py`'s `_MATH_DISPLAY_RE` both gained the `\$\$.*?\$\$|`
alternative (design.md, Decision A).

```
=== M1 over the committed fixture corpus (asserted) ===
Token counts (len(normalize_tokens(file))):
  bracket_display.md: 24
  display_fence.md: 39
  equation_environment.md: 22
  inline_math.md: 32
  plain_prose.md: 42
  unpaired_dollar.md: 29

Pair measurements (styled, sample) -> hits=len(tripwire_spans) overlap=overlap_against_set:
  (bracket_display.md, bracket_display.md) -> hits=1 overlap=24
  (bracket_display.md, display_fence.md) -> hits=0 overlap=2
  (bracket_display.md, equation_environment.md) -> hits=0 overlap=4
  (bracket_display.md, inline_math.md) -> hits=0 overlap=4
  (bracket_display.md, plain_prose.md) -> hits=0 overlap=2
  (bracket_display.md, unpaired_dollar.md) -> hits=0 overlap=2
  (display_fence.md, bracket_display.md) -> hits=0 overlap=2
  (display_fence.md, display_fence.md) -> hits=1 overlap=39
  (display_fence.md, equation_environment.md) -> hits=0 overlap=2
  (display_fence.md, inline_math.md) -> hits=0 overlap=2
  (display_fence.md, plain_prose.md) -> hits=0 overlap=6
  (display_fence.md, unpaired_dollar.md) -> hits=0 overlap=2
  (equation_environment.md, bracket_display.md) -> hits=0 overlap=4
  (equation_environment.md, display_fence.md) -> hits=0 overlap=2
  (equation_environment.md, equation_environment.md) -> hits=1 overlap=22
  (equation_environment.md, inline_math.md) -> hits=0 overlap=2
  (equation_environment.md, plain_prose.md) -> hits=0 overlap=2
  (equation_environment.md, unpaired_dollar.md) -> hits=0 overlap=2
  (inline_math.md, bracket_display.md) -> hits=0 overlap=4
  (inline_math.md, display_fence.md) -> hits=0 overlap=2
  (inline_math.md, equation_environment.md) -> hits=0 overlap=2
  (inline_math.md, inline_math.md) -> hits=1 overlap=32
  (inline_math.md, plain_prose.md) -> hits=0 overlap=2
  (inline_math.md, unpaired_dollar.md) -> hits=0 overlap=2
  (plain_prose.md, bracket_display.md) -> hits=0 overlap=2
  (plain_prose.md, display_fence.md) -> hits=0 overlap=6
  (plain_prose.md, equation_environment.md) -> hits=0 overlap=2
  (plain_prose.md, inline_math.md) -> hits=0 overlap=2
  (plain_prose.md, plain_prose.md) -> hits=1 overlap=42
  (plain_prose.md, unpaired_dollar.md) -> hits=0 overlap=2
  (unpaired_dollar.md, bracket_display.md) -> hits=0 overlap=2
  (unpaired_dollar.md, display_fence.md) -> hits=0 overlap=2
  (unpaired_dollar.md, equation_environment.md) -> hits=0 overlap=2
  (unpaired_dollar.md, inline_math.md) -> hits=0 overlap=2
  (unpaired_dollar.md, plain_prose.md) -> hits=0 overlap=2
  (unpaired_dollar.md, unpaired_dollar.md) -> hits=1 overlap=29

=== M1 over ambient document-sourced .md (NOT asserted -- a fresh clone holds none) ===
  (39 ambient files found; token counts only -- the pairwise tripwire/overlap scan is skipped here as computationally infeasible over real documents of this size, stated rather than silently forecast)
Token counts (len(normalize_tokens(file))):
  .atl/skill-registry.md: 1720
  .pytest_cache/README.md: 48
  .review/PENDIENTES.md: 1141
  README.md: 29303
  backup/proposals/2026-08-02T16-51-28Z/matematica_propuesta_CREDA.md: 1776
  backup/proposals/2026-09-16T22-12-13Z/proposals/research-concept-r21.md: 6177
  backup/proposals/2026-09-16T23-03-49Z/proposals/research-concept-r21.md: 6351
  guidance/data-paper/s41597-026-06758-7/s41597-026-06758-7.md: 8639
  guidance/paper-guide/Li_2026_Prog._Biomed._Eng._8_022013/Li_2026_Prog._Biomed._Eng._8_022013.md: 6572
  guidance/paper-guide/brainsci-16-00363/brainsci-16-00363.md: 10374
  guidance/reference-papers/computation-13-00116-v2/computation-13-00116-v2.md: 11519
  guidance/reference-papers/computation-14-00002-v3/computation-14-00002-v3.md: 14641
  guidance/reference-papers/computers-13-00176-v2-1/computers-13-00176-v2-1.md: 7365
  guidance/reference-papers/computers-15-00428/computers-15-00428.md: 13426
  guidance/reference-papers/mathematics-13-02602/mathematics-13-02602.md: 12852
  implementations/Domain_Adaptation/.pytest_cache/README.md: 48
  implementations/Domain_Adaptation/MIL-CREDA/AGREED.md: 11480
  implementations/Domain_Adaptation/README.md: 457
  proposals/research-concept-r01.md: 1780
  proposals/research-concept-r02.md: 1780
  proposals/research-concept-r03.md: 1153
  proposals/research-concept-r04.md: 2110
  proposals/research-concept-r05.md: 1589
  proposals/research-concept-r06.md: 2301
  proposals/research-concept-r07.md: 2366
  proposals/research-concept-r08.md: 3935
  proposals/research-concept-r09.md: 4071
  proposals/research-concept-r10.md: 4189
  proposals/research-concept-r11.md: 4352
  proposals/research-concept-r12.md: 4591
  proposals/research-concept-r13.md: 4661
  proposals/research-concept-r14.md: 4682
  proposals/research-concept-r15.md: 4740
  proposals/research-concept-r16.md: 4740
  proposals/research-concept-r17.md: 5058
  proposals/research-concept-r18.md: 5076
  proposals/research-concept-r19.md: 5084
  proposals/research-concept-r20.md: 6185
  proposals/research-concept-r21.md: 6363
```

## Delta

Computed by comparing the before/after tables above line by line (both
executed, neither hand-authored).

**Fixture corpus (asserted):**

- `display_fence.md`'s own normalized token count: **51 -> 39** (the 12-word
  invented equation body, `alpha x plus beta x squared plus gamma x cubed
  minus delta`, no longer survives normalization).
- Pair `(display_fence.md, plain_prose.md)` and its reverse
  `(plain_prose.md, display_fence.md)`: tripwire hits **1 -> 0**, overlap
  **14 -> 6**. This is the shipped `STYLE_OVERLAP` tripwire's own measured
  behaviour change: before this fix, a styled draft containing this
  equation inside a `$$` fence would have counted as a 14-token overlap
  against a sample repeating the same content as ordinary prose — enough to
  refuse `STYLE_OVERLAP` on math notation alone. After the fix, that
  overlap is entirely the fence's own delimiter tokens on the boundary
  ("$$" contributes nothing to `_TOKEN_RE`, but adjacent shared prose words
  still legitimately overlap at 6, which is correct and unrelated to the
  fence).
- Every other pair among the six fixture files is byte-for-byte unchanged:
  the inline `$…$`, `\[...\]`, `\begin{equation}...\end{equation}`, and
  unpaired-`$` forms were already excluded (or, for the unpaired case,
  never matched at all) before this fix, and remain identically excluded
  after it — the new `$$` alternative changes nothing about them.

**Ambient (NOT asserted, informational only):** every ambient `.md` file
containing at least one `$$` fence shows a token-count drop; files with no
`$$` fence (for example `README.md`, `.atl/skill-registry.md`,
`.review/PENDIENTES.md`, `implementations/Domain_Adaptation/README.md`, and
`.pytest_cache/README.md`) are byte-for-byte unchanged. The largest single
document in this checkout, `proposals/research-concept-r21.md`, drops from
**7471 to 6363** normalized tokens (a 1108-token, ~14.8% reduction) — the
real-world scale of what the shipped tripwire was, until this fix, silently
counting as ordinary prose on every `$$`-fenced equation in that document.
No gate in this change depends on this number; it is recorded only to show
the fix matters in practice, not merely on invented fixtures.
