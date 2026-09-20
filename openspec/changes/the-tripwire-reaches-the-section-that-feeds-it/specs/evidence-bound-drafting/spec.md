# Delta for Evidence-Bound Drafting

## MODIFIED Requirements

### Requirement: Structural Sentences Are Typed

A `structural` sentence carrying a numeral, a `\cite` command, a
comparative, or a named external object MUST refuse
`STRUCTURAL_CARRIES_CLAIM`. This is the attack surface of the `structural`
classification, closed by detection rather than by instruction. A numeral,
comparative, or named external object appearing ONLY inside a math
environment excluded from prose — inline `$...$`, DISPLAY `$$...$$`,
`\[...\]`, or `\begin{equation|align|gather|math}...\end{...}` — MUST NOT
by itself trigger this refusal: a display equation is legitimate structural
apparatus, not an assertion the `structural` classification is hiding, and
the same math-exclusion normalization this skill uses elsewhere governs what
counts as "inside" math here.

(Previously: `paper_bindings._strip_math`'s own display-math pattern carried
no `$$...$$` alternative, so a display-fenced equation body survived typing
as ordinary prose; a structural sentence carrying a display equation with a
numeral — for example an equation number or a displayed constant — could
wrongly refuse `STRUCTURAL_CARRIES_CLAIM` for content that was never an
assertion in prose at all. Corrected by the same alternative and the same
derived cross-module sweep `style-leak-detection` requires of every
`strip_math`/`_strip_math` callable under `scripts/`, since the two
implementations carry the identical pattern and must not drift apart.)

#### Scenario: A numeral inside a structural sentence refuses

- GIVEN a binding-map entry classifying a sentence containing "42%" as
  `structural`
- WHEN structural typing runs
- THEN it refuses `STRUCTURAL_CARRIES_CLAIM` naming that sentence

#### Scenario: A plain structural sentence passes

- GIVEN a structural sentence containing no numeral, `\cite`, comparative, or
  named external object
- WHEN structural typing runs
- THEN no refusal is raised

#### Scenario: A numeral inside a display-math fence does not refuse

- GIVEN a structural sentence whose only numeral appears inside a `$$...$$`
  display fence, with no numeral anywhere else in the sentence
- WHEN structural typing runs
- THEN no `STRUCTURAL_CARRIES_CLAIM` refusal is raised

#### Scenario: Mutation — dropping the display-fence alternative wrongly refuses

- GIVEN `paper_bindings._strip_math`'s display-math pattern with its
  `$$...$$` alternative removed
- WHEN the display-math scenario above is run against the mutant
- THEN that test goes red — the fenced numeral now survives as prose and
  wrongly triggers `STRUCTURAL_CARRIES_CLAIM`, proving the exclusion is
  load-bearing here as well as in the style tripwire, and that the derived
  cross-module sweep (`style-leak-detection`) must cover this file too
