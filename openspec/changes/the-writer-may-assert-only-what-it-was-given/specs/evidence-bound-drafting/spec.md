# Evidence-Bound Drafting Specification

## Purpose

The redactor drafts one contract block from three separated channels —
contract prose (verbatim), an evidence set, and a mode — and MUST assert
nothing outside that evidence set. It proves this by emitting a binding map
alongside the LaTeX, checked against the draft rather than trusted, so an
unbound assertion is *detected*, never merely instructed against.

**The seam, stated so nobody assumes coverage.** This capability detects an
assertion bound to *nothing*. An assertion bound to a real evidence or fact id
whose record does not actually support the claim is Phase 6's validator
(`holds` / `does-not-hold` / `insufficient`), consumed here as an interface
and never re-implemented. Neither capability covers the other's failure mode.

## Requirements

### Requirement: Redactor Input Contract

The redactor MUST receive exactly four inputs for one block: the contract's
prose (verbatim, uninterpreted), the block's evidence set, the block's `mode`,
and its style set (empty is a valid value). It MUST output LaTeX for that one
block plus a binding map, and MUST assert nothing the evidence set does not
license.

#### Scenario: A block drafts with an empty style set

- GIVEN a block's contract prose, evidence set, and mode, and an empty style
  set
- WHEN the redactor drafts the block
- THEN it returns LaTeX and a binding map with no style-channel input consumed

### Requirement: Binding Map Production

The redactor MUST emit, beside the LaTeX, a binding map: every sentence of the
draft mapped to exactly one of `evidence:<record-id>`, `fact:<fact-id>`, or
`structural`.

#### Scenario: Every sentence receives one binding kind

- GIVEN a drafted block
- WHEN its binding map is read
- THEN every entry names exactly one of `evidence:`, `fact:`, or `structural`

### Requirement: Draft-Versus-Map Reconciliation

Sentences MUST be segmented from the emitted LaTeX by the CLI, never trusted
from the redactor's own account. A draft sentence absent from the binding map
MUST refuse `UNBOUND_SENTENCE`. A binding map entry matching no segmented
draft sentence MUST refuse `BINDING_ORPHANED`.

#### Scenario: An unbound sentence refuses

- GIVEN a drafted block whose binding map omits one drafted sentence
- WHEN the CLI segments and reconciles the draft against the map
- THEN it refuses `UNBOUND_SENTENCE` naming that sentence

#### Scenario: An orphaned binding refuses

- GIVEN a binding map entry whose sentence text matches nothing the CLI
  segmented
- WHEN reconciliation runs
- THEN it refuses `BINDING_ORPHANED` naming that entry

### Requirement: Binding Resolution

An `evidence:` binding whose id is absent from the block's evidence set MUST
refuse `EVIDENCE_ID_UNKNOWN`. A `fact:` binding whose id is outside the
block's `requires_facts` MUST refuse `FACT_NOT_LICENSED`.

#### Scenario: An unknown evidence id refuses

- GIVEN a binding `evidence:E9` where `E9` is not in the block's evidence set
- WHEN bindings are resolved
- THEN it refuses `EVIDENCE_ID_UNKNOWN` naming `E9`

#### Scenario: An unlicensed fact id refuses

- GIVEN a binding `fact:results` on a block whose `requires_facts` excludes
  `results`
- WHEN bindings are resolved
- THEN it refuses `FACT_NOT_LICENSED` naming `results`

### Requirement: Structural Sentences Are Typed

A `structural` sentence carrying a numeral, a `\cite` command, a comparative,
or a named external object MUST refuse `STRUCTURAL_CARRIES_CLAIM`. This is
the attack surface of the `structural` classification, closed by detection
rather than by instruction.

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

### Requirement: Mode-Admissible Bindings

A block whose `mode` is `transposition` MUST admit only `fact`, `structural`,
and `resolution`-class evidence bindings. A block whose `mode` is `argument`
MUST additionally admit `discovery`-class evidence bindings. Any binding
outside its mode's admitted set MUST refuse `MODE_VIOLATION`.

#### Scenario: A transposition block rejects a discovery binding

- GIVEN a `transposition`-mode block binding `evidence:D1`, a `discovery`-class
  record
- WHEN mode admissibility is checked
- THEN it refuses `MODE_VIOLATION` naming `D1`

#### Scenario: The same binding passes under argument mode

- GIVEN an `argument`-mode block binding the same `discovery`-class record
  `D1`
- WHEN mode admissibility is checked
- THEN no refusal is raised
