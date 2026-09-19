# Skeleton Startup Specification

## Purpose

Two manuscript-structure decisions — whether a Related Work section exists,
and whether the dataset is described in Materials and Methods or in
Experimental Setup — are asked exactly once, at skeleton time, and answered
by opening the corresponding empty block ids in `main.tex`. Every decision
after that is inferred by reading which block ids are open on disk, never
re-asked and never held only in the agent's memory.

## Requirements

### Requirement: Two Questions, Asked Once

Before any skeleton exists (no `%% paper-writing block` marker present in
`main.tex`), the skill MUST ask exactly two blocking questions: whether the
manuscript carries a dedicated Related Work section, and whether the
dataset is described in Materials and Methods or in Experimental Setup.
Once a skeleton exists, the skill MUST NOT ask either question again.

#### Scenario: A fresh paper asks both questions

- GIVEN a `main.tex` carrying no opened blocks
- WHEN scaffolding is requested
- THEN both blocking questions are asked before the skeleton is opened

#### Scenario: An existing skeleton is never re-asked

- GIVEN a `main.tex` already carrying opened block ids for both decisions
- WHEN the skill is invoked again in a fresh process
- THEN neither question is asked

#### Scenario: Flags contradicting the disk state refuse

- GIVEN a `main.tex` already carrying opened block ids for both decisions
- WHEN the skill is invoked again with a flag naming the opposite answer for
  either decision
- THEN it refuses `SKELETON_ALREADY_DECIDED` naming both what disk already
  records and what the flags requested

#### Scenario: A missing answer refuses

- GIVEN no skeleton exists yet
- WHEN the skill is invoked without both `--related-work` and `--dataset-in`
- THEN it refuses `SKELETON_ANSWER_REQUIRED` naming the missing flag

### Requirement: The Skeleton Is The Answer

Opening the skeleton MUST open, empty, every section and block id implied by
the two answers — including `related-work`'s blocks when Related Work is
chosen, and exactly one of `mm-dataset` / `es-dataset` per the placement
answer — using the existing block-open mechanism. No other record of the two
answers is created.

#### Scenario: The skeleton opens the chosen dataset block only

- GIVEN the answers "Related Work: yes" and "dataset: Experimental Setup"
- WHEN the skeleton is built
- THEN `related-work`'s blocks and `es-dataset` are opened, and `mm-dataset`
  is left unopened

### Requirement: Both Decisions Are Re-Derived From Disk, Never Recalled

Any verb needing either decision MUST derive it by reading the current set
of opened block ids from `main.tex`: Related Work is present iff
`related-work`'s blocks are opened; dataset placement is whichever of
`mm-dataset` / `es-dataset` is opened. It MUST NOT read a separately stored
flag, and MUST NOT rely on an earlier answer held only in conversation.
When both `mm-dataset` and `es-dataset` are opened simultaneously, the
inference is ambiguous and MUST refuse `DATASET_PLACEMENT_CONFLICT` naming
both ids.

#### Scenario: A fresh process infers the same decision from disk alone

- GIVEN a `main.tex` carrying `es-dataset` among its opened blocks and no
  other record of the placement answer
- WHEN a new, independent invocation infers dataset placement
- THEN it reports "Experimental Setup" derived solely from the opened block
  ids

#### Scenario: Both dataset blocks open at once refuses

- GIVEN a `main.tex` carrying both `mm-dataset` and `es-dataset` among its
  opened blocks
- WHEN dataset placement is inferred
- THEN it refuses `DATASET_PLACEMENT_CONFLICT` naming both ids

### Requirement: Disk Presence Checks Include Ignored Paths

Every directory or file-presence check this capability performs — the
opened-block-id scan over `main.tex` and any directory listing consulted to
decide whether the skeleton is buildable — MUST enumerate entries without
applying VCS ignore rules. A populated-but-gitignored path MUST NOT be
reported as empty.

#### Scenario: A gitignored, populated directory reports as populated

- GIVEN a directory this capability inspects for presence, matching a
  `.gitignore` pattern and holding files (for example `guidance/` holding
  ingested reference material)
- WHEN the presence check runs
- THEN it reports the directory as populated, not empty
