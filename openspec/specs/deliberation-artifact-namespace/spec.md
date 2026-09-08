# Deliberation Artifact Namespace Specification

## Purpose

The deliberation engine must name no domain and no artifact namespace itself.
Every managed-artifact naming decision — stem, revision spelling, directory,
sidecar root, marker — must be declared by the domain profile, not hardcoded
in core. `proposal-deliberation` must keep its exact current behavior because
its profile declares exactly today's values.

## Requirements

### Requirement: Domain profile MUST declare a complete artifact namespace

`DeliberationDomainProfile` MUST require an `artifact` block with `directory`,
`stem`, `revisionPattern`, `revisionLabel`, `sidecarRoot`, and `marker`. Each
field MUST be added to `REQUIRED`. A profile missing any of these fields MUST
fail engine startup with an explicit code; the engine MUST NOT substitute a
default.

#### Scenario: Missing artifact field fails closed

- GIVEN a domain profile module that omits `artifact.marker`
- WHEN the engine loads `DELIBERATION_DOMAIN_PROFILE`
- THEN the engine MUST refuse to start with an explicit missing-field code
- AND MUST NOT substitute a default value for `marker`

#### Scenario: Complete artifact block loads

- GIVEN a profile declaring all six `artifact` fields
- WHEN the engine loads
- THEN startup succeeds and every naming site reads its value from the profile

### Requirement: No literal artifact namespace remains in core

Core MUST NOT contain a hardcoded domain stem, revision spelling, directory
name, sidecar root, marker, or a literal TypeScript type derived from any
specific domain's filename. All fourteen previously hardcoded sites and the
three literal-type sites MUST route through profile-derived builders.

#### Scenario: proposal-deliberation preserved by construction

- GIVEN `.claude/skills/proposal-deliberation/profile.ts` declares
  `directory: "proposals"`, `stem: "research-concept"`, the `rNN` revision
  pattern/label, `sidecarRoot: ".proposal-deliberation"`, and today's marker
- WHEN any core site that previously hardcoded these values runs
- THEN the produced filename, path, and marker are byte-identical to
  pre-change output

#### Scenario: A differently-named profile changes the namespace with no core edit

- GIVEN a profile declaring `stem: "experiments"` and revision label `"v"`
- WHEN a new managed artifact is created
- THEN its filename follows the declared stem and revision label, and no core
  file required modification to produce it

### Requirement: The managed directory and sidecar root are profile-derived

Core MUST route the managed artifact directory and the three sidecar kinds
(`state`, `receipts`, `withdrawn`) through `profile.artifact.directory` and
`profile.artifact.sidecarRoot` rather than the literal `proposals/` and
`.proposal-deliberation/`.

#### Scenario: Sidecar root changes with the profile

- GIVEN a profile declaring `sidecarRoot: ".other-deliberation"`
- WHEN a revision is created
- THEN state/receipts/withdrawn sidecars are written under
  `.other-deliberation/`, never under `.proposal-deliberation/`

### Requirement: The domain lock MUST be able to fail

`tests/proposal-deliberation-domain-profile-lock.test.mjs` MUST scan core
source for every artifact value declared by `proposal-deliberation`'s profile
(stem, directory, sidecar root, revision spelling, marker), in addition to the
four values it scans today. A lock that cannot go red on a reintroduced
literal is indistinguishable from a disabled guard.

#### Scenario: Lock passes on clean core

- GIVEN core contains no literal occurrence of the declared artifact values
  outside `profile.ts`
- WHEN the lock test runs
- THEN it reports zero violations

#### Scenario: Lock goes RED on a reintroduced literal

- GIVEN a core file is mutated to hardcode `"research-concept"` or the `rNN`
  spelling outside the profile
- WHEN the lock test runs
- THEN it MUST fail, naming the offending file and the literal it found

## Acceptance Criteria

- `npm test` and `.venv/bin/python -m unittest discover -s tests` both hold
  their baseline (386/0 and 2718 OK skipped=6) after this slice.
- The extended lock ships in the same work unit as the builder migration and
  is proven to fail on a deliberate mutation before merge.
