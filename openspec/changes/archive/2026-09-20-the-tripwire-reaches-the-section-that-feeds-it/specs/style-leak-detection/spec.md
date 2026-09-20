# Delta for Style Leak Detection

## MODIFIED Requirements

### Requirement: The Eight-Token Tripwire

Independent of the relative check, any maximal contiguous run of eight or
more normalized tokens shared between `S` and a sample in `R` MUST refuse
`STYLE_OVERLAP`, naming the shared span and the reference it came from.
Normalization case-folds, collapses whitespace, strips LaTeX commands, and
excludes every math environment alike: inline `$...$`, DISPLAY `$$...$$`,
`\[...\]`, and `\begin{equation|align|gather|math}...\end{...}` forms. A
display-fenced equation body MUST NOT survive normalization as ordinary
prose — only its delimiters are ever excluded, never the body inside them,
which is what a display fence means as distinct from an inline one.

Because this exclusion is normalization, and this skill computes
normalization in more than one place, EVERY callable named `strip_math` or
`_strip_math` under `scripts/` MUST exclude a `$$...$$` fence identically.
This MUST be proven by a DERIVED introspection sweep that discovers every
such callable by name — never a hand-maintained list of exactly the two
known today — so a third implementation added later inherits the same
exclusion by construction rather than by someone remembering to update a
list.

(Previously: the display-math pattern carried no `$$...$$` alternative, and
the inline pattern's own first-two-adjacent-`$` match consumed only the
fence's own delimiters, leaving the entire equation body between a `$$`
fence intact as ordinary prose. The shipped tripwire normalizes the same
way, so a quoted display equation already counted toward its eight-token
overlap before this correction. The fix is measured before it lands: its
blast radius against an unmodified tree, and again after, is recorded in
this change's own `math-fence-blast-radius.md`, executed rather than
forecast.)

#### Scenario: A near-verbatim lifted sentence refuses

- GIVEN a styled draft `S` containing a contiguous nine-token run identical
  (after normalization) to a run in a sample in `R`
- WHEN the tripwire check runs
- THEN it refuses `STYLE_OVERLAP` naming the span and the source reference

#### Scenario: Shared math notation does not trip the tripwire

- GIVEN a shared run of tokens that lies entirely inside a math environment
- WHEN the tripwire check runs
- THEN the math environment is excluded from normalization and no refusal is
  raised on that run

#### Scenario: A `$$` display fence is excluded, body and all

- GIVEN a sample in `R` and a styled draft `S` that both contain the
  identical equation body between `$$` fences, with no shared text outside
  those fences
- WHEN the tripwire check runs
- THEN normalization excludes the entire fenced body in both `S` and the
  sample, and no refusal is raised on tokens that existed only inside it

#### Scenario: Mutation — dropping the display-fence alternative is caught

- GIVEN `strip_math`'s display-math pattern with its `$$...$$` alternative
  removed
- WHEN the display-fence scenario above is run against the mutant
- THEN that test goes red — the equation body now survives as prose and
  contributes to the shared run, proving the exclusion is load-bearing

#### Scenario: Mutation — a third normalizer is caught by the derived sweep, never a hand-edited list

- GIVEN a new module under `scripts/` exposing a callable named
  `_strip_math` that omits the `$$...$$` alternative
- WHEN the derived introspection sweep runs
- THEN it discovers that callable by name (never by a list naming only the
  two known implementations) and fails on it, proving membership in the
  sweep is computed, not hand-maintained

### Requirement: Overlap Reads Only The Recorded Sample Set

`STYLE_OVERLAP` and the relative overlap check MUST compare `S` only against
`R`, the sampler's recorded set — never against a reference file read
directly. Reading the reference file instead of `R` measures material the
writer was never shown and MUST NOT be treated as this check. A SIBLING
check comparing a draft against a block's own bound source section (a
different capability, a different refusal code) MUST NOT be implemented by
widening this comparison to accept a directly-read file as a member of `R` —
the two comparisons stay structurally separate specifically so this
requirement is never bent to accommodate a second, unrelated use.

#### Scenario: A reference-file read is not the recorded set

- GIVEN a reference file containing text never included in `R`
- WHEN the overlap check runs
- THEN a match against that unrecorded text MUST NOT be reported as
  `STYLE_OVERLAP` or counted in `overlap(S,R)`

#### Scenario: A bound source section is never folded into `R`

- GIVEN a transposition block's own bound source section, resolved and read
  directly from disk for a separate, sibling check
- WHEN the overlap check (`STYLE_OVERLAP`) runs for that same block
- THEN the bound section's bytes are not added to `R` and play no part in
  `overlap(S,R)` — the sibling check reads them under its own refusal code,
  never this one
