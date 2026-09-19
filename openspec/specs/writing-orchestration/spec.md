# Writing Orchestration Specification

## Purpose

The `write` verb sequences readiness, evidence-bound drafting, and contract
auditing into one pipeline, with exactly one bounded re-draft, and it commits
a block to `main.tex` only when both audits clear. This capability owns the
pipeline's order and its exhaustion path — not the two audits' own rules,
specified elsewhere.

## Requirements

### Requirement: Pipeline Stage Order

`write` MUST run its stages in this order for one block: readiness, gate,
draft, evidence-audit, contract-audit, `substitute --contract`. A stage MUST
NOT start until every earlier stage has cleared.

#### Scenario: A failing evidence-audit stops the pipeline before contract-audit

- GIVEN a draft whose binding map fails evidence-audit (for example
  `UNBOUND_SENTENCE`)
- WHEN `write` runs
- THEN contract-audit never runs and `substitute` is never called

### Requirement: One Bounded Re-Draft

When contract-audit reports at least one `fires` verdict, `write` MUST
attempt exactly one re-draft, carrying the fired bullets and their quoted
spans as explicit feedback to the redactor, and MUST audit the result with
the same auditor and the same inputs. `write` MUST NOT attempt a third draft.

#### Scenario: A second attempt is audited with the same inputs

- GIVEN a first draft whose contract-audit reports `fires` on bullet B
- WHEN `write` re-drafts
- THEN the re-draft's input includes bullet B's quoted span and the same
  contract, evidence set, and mode as the first attempt

### Requirement: Exhaustion Leaves The Block Unwritten

When the re-draft's contract-audit also reports at least one `fires` verdict,
`write` MUST refuse `AUDIT_EXHAUSTED`, naming every bullet that fired on the
second attempt, and MUST NOT call `substitute`. The block MUST remain absent
from `main.tex`.

#### Scenario: Two failing audits leave main.tex unchanged

- GIVEN a block whose first and second drafts both fire the same disqualifier
- WHEN `write` completes its bounded retry
- THEN it refuses `AUDIT_EXHAUSTED` naming the fired bullet, and `main.tex` is
  byte-identical to its state before `write` ran

### Requirement: No Live Agent Invocation In Tests

Every test exercising `write`, the redactor, the contract-auditor, or the
style-sampler MUST run against recorded agent transcripts and fixture
evidence sets. No test MUST spawn a live agent process. A guard test MUST
assert that no subprocess naming an agent binary is launched during the
suite's run.

#### Scenario: The suite runs with zero live agent subprocesses

- GIVEN the full test suite
- WHEN it runs to completion
- THEN the live-agent guard reports zero subprocess launches naming an agent
  binary
### Requirement: Packet Assembly Precedes Draft

Before the `draft` stage runs for a block, `write` MUST assemble that
block's redactor packet (`redactor-packet`) and pass it to the draft stage
alongside the existing evidence set and mode. A draft stage invoked without
an assembled packet MUST NOT proceed.

#### Scenario: The draft stage receives an assembled packet

- GIVEN a block entering the `write` pipeline with at least one
  `style-reference`-classed `guidance/` entry
- WHEN the pipeline reaches the `draft` stage
- THEN the redactor packet was assembled before that stage ran, and the
  draft stage's input includes it

### Requirement: Packet Assembly Shuttles Through Files, Never A Live Process

Packet assembly and every agent shuttle it depends on (`style-sampler`)
MUST exchange data through files read and written by the pipeline itself —
never by invoking `subprocess` or any other live process spawn. This is the
same no-subprocess discipline `NoSubprocessScanTests` already enforces
repository-wide, restated here because packet assembly is new code in this
pipeline.

#### Scenario: The suite's subprocess guard covers packet assembly

- GIVEN the full test suite, including tests exercising packet assembly
- WHEN it runs to completion
- THEN the repository-wide no-subprocess guard reports no `subprocess`
  import anywhere in the packet-assembly code path
