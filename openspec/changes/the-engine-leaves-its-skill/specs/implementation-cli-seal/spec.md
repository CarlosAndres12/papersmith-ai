# Delta for implementation-cli-seal

## MODIFIED Requirements

### Requirement: Seal Capture Scope

The seal MUST run all 20 subcommands (20 `cmd_*` functions, 20 `COMMANDS`
entries) against a fixed fixture corpus, invoked through the per-skill
launcher's own entry point — never through the engine module directly, and
never through whichever file `CLI_INVOCATION`/`CLI_PATH` happens to resolve
to internally — capturing raw stdout bytes and exit status, and MUST digest
each.

(Previously: the entry point was implicit in `CLI_INVOCATION`; this
requirement pinned the twenty subcommands but never named the entry point
itself, so a launcher/engine split — introduced by Cut 1 — could silently
seal the wrong file.)

#### Scenario: Every subcommand is captured
- GIVEN the corpus and the 20 registered subcommands
- WHEN capture runs
- THEN each has a digest+exit status, or is in the unsealed set with a reason

#### Scenario: A new subcommand is detected
- GIVEN a 21st subcommand added to `COMMANDS`
- WHEN the coverage check runs
- THEN it fails, naming the uncaptured subcommand

#### Scenario: The sealed entry point is the launcher, not the engine
- GIVEN the engine now lives at
  `_core/implementation/implementation_engine.py`, separate from the
  per-skill launcher
- WHEN the seal invokes any case
- THEN the invoked path is the launcher's literal file, and if `CLI_PATH`
  instead resolved to the engine, the case's digest would move
