# Delta for Writing Orchestration

## ADDED Requirements

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
