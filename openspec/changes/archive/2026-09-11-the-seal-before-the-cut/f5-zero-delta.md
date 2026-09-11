# F5 — Zero-Delta Record

Written after F5 was applied and re-verified, per design.md D8 instrument 4
("Recorded, not inferred"). F5 lands after capture (`14d97e9`), never before —
the whole point of the ordering discipline.

## The change

Beside `PRODUCT_NOTEBOOKS` (`.claude/skills/proposal-implementation/scripts/implementation_cli.py`):

```python
#: The product category a repository's data lives under, named off `PRODUCT_DIRS`
#: rather than spelled a second time, for the reason `PRODUCT_NOTEBOOKS` above
#: states: a second literal beside the tuple is how the two come to disagree the
#: day a layout changes.
PRODUCT_DATA = PRODUCT_DIRS[1]
```

In `expected_dirs`:

```python
    dirs = [f"{name}/{d}" for d in PRODUCT_DIRS if d != PRODUCT_DATA or with_data]
```

replacing the bare `"Data"` literal. `PRODUCT_DIRS[1] == "Data"`, so this is an
identity refactor: the rendered value is unchanged for every caller.

## Commit shas

- Before F5 (digests captured, F5 not yet applied): `14d97e9aa0ea9f1169286f55dfabe2d8425bfb00`
- After F5: `5c72ba5` (`fix(proposal-implementation): F5 -- PRODUCT_DATA read from the tuple, not spelled twice`)

## Instrument 1 — identity at the constant

```
test_the_data_category_is_read_from_the_tuple ... ok
```

`impl.PRODUCT_DATA == "Data"`, `impl.PRODUCT_DATA is impl.PRODUCT_DIRS[1]`, and
`expected_dirs`'s own source contains no `"Data"` literal.

## Instrument 2 — identity at the function, pinned literals

```
test_expected_dirs_with_data_true_pinned ... ok
test_expected_dirs_with_data_false_pinned ... ok
```

## Instrument 3 — the seal itself, against the EXISTING digests (no recapture)

```
test_the_seal_reproduces_pre_f5_digests_unchanged ... ok
```

Cases 3 (`plan-a`), 4 (`plan-b`), 12 (`verify-a`), 13 (`verify-b`) reproduce
their pre-F5 digests exactly. Confirmed again over the FULL 28-case sealed set
(`SealComparisonTests.test_every_sealed_case_matches_its_golden ... ok`) — no
other case moved either.

## Instrument 4 — the mutation that matters (coordinator decision, 2026-09-11)

Zero-delta alone proves the refactor is an identity. It says nothing about
whether the seal COULD have caught it if it were not one. Measured live,
subprocess level, `PRODUCT_DATA` temporarily bound to `PRODUCT_DIRS[2]`
(`"Results"`, wrong on purpose) via a real file edit, real capture, real
revert — never left mutated on disk:

```
verify-a (case 12) MUTATED digest: {'sha256': 'd3210f7272ec97a0cae95ead82fafab7cd9a466c4762da76af90cc2e83b1c809', 'bytes': 19088, 'exit': 0}
verify-a (case 12) STORED  digest: {'bytes': 19088, 'exit': 0, 'sha256': 'd3210f7272ec97a0cae95ead82fafab7cd9a466c4762da76af90cc2e83b1c809'}
case 12 MOVED: False

verify-b (case 13) MUTATED digest: {'sha256': 'e626b81440fe829cef95caaeafb06584efe46728eac2dd6b4003467b180c39e1', 'bytes': 19111, 'exit': 0}
verify-b (case 13) STORED  digest: {'bytes': 19088, 'exit': 0, 'sha256': 'd3210f7272ec97a0cae95ead82fafab7cd9a466c4762da76af90cc2e83b1c809'}
case 13 MOVED: True
```

Exactly as predicted: fixture A (case 12, `with_data=True`) is structurally
blind to `PRODUCT_DATA` — `expected_dirs`'s `or with_data` short-circuit makes
every branch true regardless of which directory `PRODUCT_DATA` names. Fixture
B (case 13, `with_data=False`) sees the wrong index immediately: 19088 → 19111
bytes, a different sha256. **Case 13 is the seal's only instrument for F5.**

After confirming this, the file was reverted (`PRODUCT_DATA = PRODUCT_DIRS[1]`)
and both `F5IdentityTests` and `SealComparisonTests` re-run green (pasted
above, instrument 3) — the mutation was never committed.

A permanent, safe version of the same proof (in-process, never touching the
file a subprocess would read) lives in
`F5IdentityTests.test_a_wrong_product_data_would_move_case_13_but_not_case_12`:
it reconstructs `expected_dirs`'s own output under the correct and the wrong
`PRODUCT_DATA` and asserts the same asymmetry (case 13's list moves, case 12's
does not) — pure-function evidence for the property this document's
subprocess-level run confirms actually reaches a captured digest.

## RED→GREEN mutation proof (strict_tdd)

Reverting `expected_dirs`'s `PRODUCT_DATA` reference back to the bare `"Data"`
literal turned two tests red:

```
AssertionError: '"Data"' unexpectedly found in 'def expected_dirs(...'
AssertionError: [...] == [...] : case 13 (Data/ absent): a wrong PRODUCT_DATA
  must move the expected-dirs list, ...
```

(The second failure is itself informative: with the literal hardcoded,
monkeypatching `impl.PRODUCT_DATA` has no effect at all — confirming the
constant genuinely drives `expected_dirs`'s behaviour only when the code
reads FROM it.) Restoring `PRODUCT_DATA` made both green again.
