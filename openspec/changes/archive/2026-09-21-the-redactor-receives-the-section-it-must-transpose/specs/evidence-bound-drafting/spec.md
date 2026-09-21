# Delta for Evidence-Bound Drafting

## MODIFIED Requirements

### Requirement: Redactor Input Contract

The redactor MUST receive exactly five inputs for one block: the contract's
prose (verbatim, uninterpreted), the block's evidence set, the block's
`mode`, its style set (empty is a valid value), and its own bound source
sections (empty is a valid value for a non-`transposition` block, for an
unbound block, or when the paper root could not be measured). It MUST output
LaTeX for that one block plus a binding map, and MUST assert nothing the
evidence set does not license. It MUST NOT open any file itself to find a
sixth input — a bound source section reaches it only through this declared
fifth input, never through a direct read.

(Previously: "The redactor MUST receive exactly four inputs..." — no
bound-section input; `RedactorInput` carried four fields.)

#### Scenario: A block drafts with an empty style set

- GIVEN a block's contract prose, evidence set, and mode, and an empty style
  set
- WHEN the redactor drafts the block
- THEN it returns LaTeX and a binding map with no style-channel input
  consumed

#### Scenario: The redactor receives five declared inputs and opens no file for a sixth

- GIVEN a block about to be drafted, with contract prose, evidence set,
  mode, style set, and bound source sections all supplied as declared
  inputs
- WHEN the redactor drafts the block
- THEN it uses only those five inputs, and reads no file itself to locate a
  bound section, a style extract, or any other content

#### Scenario: A non-transposition block drafts with empty source sections

- GIVEN an `argument`-mode block whose other four inputs are supplied
  normally
- WHEN the redactor drafts the block
- THEN its fifth input, source sections, is empty, and drafting proceeds
  exactly as it did before this capability existed

#### Scenario: The fifth input widens visibility, never the verbatim guard

- GIVEN a `transposition`-mode block whose fifth input carries its own
  bound section's resolved text
- WHEN a draft pastes a run from that text exceeding
  `transposition-fidelity`'s own self-calibrated threshold
- THEN `write` still refuses `SOURCE_SECTION_VERBATIM` — this input widens
  what the redactor can see, never what `write` accepts; the guard itself is
  the sibling capability `transposition-fidelity`, unchanged by this input's
  addition
