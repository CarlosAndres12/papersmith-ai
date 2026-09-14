# Delta for implementation-engine-neutrality

## MODIFIED Requirements

### Requirement: The Kit Template's Provenance Keys Agree With The Profile

Each discovered profile's own kit template MUST have its provenance keys checked
against that same skill's own profile — `KitAgreementLockTests` MUST iterate every
profile `discover_profiles()` finds, the way the domain-profile lock already does,
never a single hardcoded skill path. Each skill's check MUST be independent: one
skill's mismatch MUST be reported without masking another skill's, via `subTest` or
separate test methods per skill.
(Previously: `_profile()` returned a single hardcoded `proposal-implementation`
profile; only that one skill's kit was ever checked, so a second skill's kit template
would diverge from its profile with nothing to catch it.)

#### Scenario: Divergence is caught for the discovered skill it belongs to
- GIVEN the kit template edited to a different `"equations"`-equivalent value under
  `experimental-implementation`
- WHEN the lock runs
- THEN it fails, naming that skill and the divergent key; reverted, it passes

#### Scenario: One skill's break does not hide another's
- GIVEN `experimental-implementation`'s kit is broken while `proposal-implementation`'s
  agrees with its own profile
- WHEN the lock runs
- THEN both outcomes are individually visible — the broken skill fails and the
  agreeing skill passes in the same run, neither masked by test-method halting

#### Scenario: A skill declaring no kit template is not silently skipped as a pass
- GIVEN a hypothetical third skill with `impl_profile.py` but no kit template file
- WHEN the lock runs
- THEN it fails naming the missing template, rather than reporting agreement it
  never checked

## ADDED Requirements

### Requirement: The Derived-Denylist Lock Becomes Satisfiable, Not A Permanent Skip

With a second implementation profile on disk, the Python mirror of the TS
`buildDenylist` mechanism (a word is a domain's own subject only when no other
profile's north uses it) MUST run as a real, unskipped assertion. It MUST NOT be
implemented as a `skipTest`, and its landing MUST NOT move the pinned Python
`skipped=6` invariant.

#### Scenario: The lock runs for real once two profiles exist
- GIVEN `experimental-implementation` and `proposal-implementation` both declare an
  `OBJECTIVE_FLOW`
- WHEN the derived-denylist lock runs
- THEN it computes a real denylist from each skill's own north against the other's,
  and asserts rather than skips

#### Scenario: skipped=6 does not move
- GIVEN this lock lands as a passing test
- WHEN the full Python suite runs
- THEN `OK (skipped=6)` holds, and `Ran` grows by the new test, not by a new skip

### Requirement: A Namespace Word's Self-Check Is Not The Leak Proof

The existing check that a declared `vocabulary.names` word appears in its own
profile's source text (`test_every_declared_name_really_is_that_domain_speaking`)
MUST NOT be relied on as evidence that the word is leak-free — a namespace word (for
example, the skill's own directory name) trivially satisfies it by appearing in the
file's own path or docstring, without ever having been used as a real domain value.
The whole-engine text scan (`test_the_engine_spells_no_declared_names_word`) remains
the sole mutation-provable leak guard for any declared name, including a namespace
word.

#### Scenario: The self-check passes trivially for a namespace word
- GIVEN `experimental-implementation` declares its own namespace word in
  `vocabulary.names`, present only in its profile file's own path or docstring
- WHEN the self-check runs
- THEN it passes, and that pass is not treated as proof the word never leaks into
  the engine

#### Scenario: The whole-engine scan is what actually catches a leak
- GIVEN that same namespace word is planted anywhere under
  `_core/implementation/engine/`
- WHEN the whole-engine scan runs
- THEN it fails, naming the file and the word; reverting the plant restores green
