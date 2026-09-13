# Paper Scaffold Specification

## Purpose

Creates and re-enters the `paper/` directory at the repository root without
clobbering existing content, mirroring how this repository already treats
`proposals/` and `experiments/`: the folder travels, its contents stay home.

## Requirements

### Requirement: Scaffold Creates the Paper Tree

The system MUST create `paper/main.tex`, `paper/refs.bib`, `paper/Figures/`
and `paper/.gitkeep` at the repository root when `paper/` is absent.

#### Scenario: First run creates the tree

- GIVEN no `paper/` directory exists
- WHEN `scaffold` runs
- THEN `paper/main.tex`, `paper/refs.bib`, `paper/Figures/` and
  `paper/.gitkeep` all exist

### Requirement: Scaffold Is Idempotent

The system MUST NOT overwrite any file that already exists under `paper/`.
A second run MUST leave every existing byte unchanged, regardless of what
those bytes are.

#### Scenario: Second run changes nothing

- GIVEN `scaffold` ran once, and `main.tex` was hand-edited afterward
- WHEN `scaffold` runs again
- THEN every file under `paper/` is byte-identical to its state immediately
  before the second run

### Requirement: Scaffold Refuses Outside the Repository

`--paper <dir>` MUST resolve inside the repository root. The system MUST
refuse `PAPER_OUTSIDE_REPOSITORY` (invocation-defect) otherwise, and write
nothing.

#### Scenario: Caller names a directory outside the repo

- GIVEN `--paper ../elsewhere`
- WHEN `scaffold` runs
- THEN it refuses `PAPER_OUTSIDE_REPOSITORY` and writes nothing

### Requirement: Scaffold Refuses a Wrong-Shaped Entry

When `paper/` exists but is not a directory (`PAPER_NOT_A_DIRECTORY`,
work-state), or an expected entry (`main.tex`, `refs.bib`, `Figures/`)
exists as the wrong type — a file where a directory is expected, or the
reverse (`SCAFFOLD_ENTRY_WRONG_TYPE`, work-state) — the system MUST refuse
rather than write through it.

#### Scenario: paper/ is a file

- GIVEN a plain file named `paper` at the repository root
- WHEN `scaffold` runs
- THEN it refuses `PAPER_NOT_A_DIRECTORY` and writes nothing

#### Scenario: Figures exists as a file

- GIVEN `paper/Figures` exists as a regular file, not a directory
- WHEN `scaffold` runs
- THEN it refuses `SCAFFOLD_ENTRY_WRONG_TYPE` naming `Figures`, and writes
  nothing else under `paper/`

### Requirement: Paper Contents Stay Untracked, the Folder Travels

The repository's `.gitignore` MUST declare `paper/*` and `!paper/.gitkeep`.
Only `.gitkeep` is tracked; `main.tex`, `refs.bib` and `Figures/` contents
are local to each clone, never committed by this capability.

#### Scenario: A fresh clone still has the folder

- GIVEN a fresh clone that has never run `scaffold`
- WHEN the repository is checked out
- THEN `paper/.gitkeep` exists and `paper/main.tex` does not exist until
  `scaffold` runs locally
