# F3 — Declared Message Delta

Written **before** any digest is captured, per design.md D7 and the proposal's
step-1-before-step-3 ordering. This is the only sanctioned pre/post seal difference.

## The change

All five sites are the same one-line substitution, in
`.claude/skills/proposal-implementation/scripts/implementation_cli.py`:

```python
FORGE_ROOT / 'proposals'
```

becomes

```python
proposals_root()
```

`proposals_root()` (defined at line 4402, unchanged by this edit):

```python
def proposals_root() -> Path:
    override = os.environ.get("IMPLEMENTATION_PROPOSALS")
    return Path(override) if override else FORGE_ROOT / "proposals"
```

So the rendered message is **byte-identical when `IMPLEMENTATION_PROPOSALS` is unset**
(`proposals_root()` falls back to the exact same `FORGE_ROOT / "proposals"` value), and
differs only when the override is set — which is the bug this fixes: the five refusal
messages spelled the directory the code never actually reads under an override.

## The five sites, before and after

### Site 1 — `cmd_admit` (currently line 7535)

Before:

```python
    raise Refused("REVISION_UNREADABLE",
                  f"{args.revision!r} is not readable under {FORGE_ROOT / 'proposals'}; "
                  "admissibility cannot be ruled on and no remedy may be measured.")
```

After:

```python
    raise Refused("REVISION_UNREADABLE",
                  f"{args.revision!r} is not readable under {proposals_root()}; "
                  "admissibility cannot be ruled on and no remedy may be measured.")
```

Unchanged continuation: `"admissibility cannot be ruled on and no remedy may be measured."`

### Site 2 — `cmd_position` (currently line 10362)

Before:

```python
        raise Refused(
            "REVISION_UNREADABLE",
            f"{args.revision!r} is not readable under {FORGE_ROOT / 'proposals'}; "
            "the position header cannot be bound to a revision.")
```

After:

```python
        raise Refused(
            "REVISION_UNREADABLE",
            f"{args.revision!r} is not readable under {proposals_root()}; "
            "the position header cannot be bound to a revision.")
```

Unchanged continuation: `"the position header cannot be bound to a revision."`

### Site 3 — `cmd_gate` (currently line 12982)

Before:

```python
        raise Refused(
            "REVISION_UNREADABLE",
            f"{args.revision!r} is not readable under {FORGE_ROOT / 'proposals'}; "
            "a gate cannot be recorded against a revision that cannot be read.")
```

After:

```python
        raise Refused(
            "REVISION_UNREADABLE",
            f"{args.revision!r} is not readable under {proposals_root()}; "
            "a gate cannot be recorded against a revision that cannot be read.")
```

Unchanged continuation: `"a gate cannot be recorded against a revision that cannot be read."`

### Site 4 — `cmd_offer` (currently line 13509)

Before:

```python
        raise Refused(
            "REVISION_UNREADABLE",
            f"{args.revision!r} is not readable under {FORGE_ROOT / 'proposals'}; "
            "offer cannot publish an action set against a revision that "
            "cannot be read.")
```

After:

```python
        raise Refused(
            "REVISION_UNREADABLE",
            f"{args.revision!r} is not readable under {proposals_root()}; "
            "offer cannot publish an action set against a revision that "
            "cannot be read.")
```

Unchanged continuation: `"offer cannot publish an action set against a revision that "`
`"cannot be read."`

### Site 5 — `cmd_close` (currently line 13683)

Before:

```python
        raise Refused(
            "REVISION_UNREADABLE",
            f"{args.revision!r} is not readable under {FORGE_ROOT / 'proposals'}; "
            "close cannot require a position true against a revision that "
            "cannot be read.")
```

After:

```python
        raise Refused(
            "REVISION_UNREADABLE",
            f"{args.revision!r} is not readable under {proposals_root()}; "
            "close cannot require a position true against a revision that "
            "cannot be read.")
```

Unchanged continuation: `"close cannot require a position true against a revision that "`
`"cannot be read."`

## `cmd_handoff` — untouched precedent

`cmd_handoff` (function begins at line 7354) already omits the path entirely from its
refusal message and is the correct precedent this change brings the other five up to.
It is not touched by this change.

## Per-case checkable consequence (design.md D7)

- Seal cases 7, 16, 20, 22, 24 (`E0`, `IMPLEMENTATION_PROPOSALS` unset): **zero delta.**
  Pre-F3 and post-F3 bytes are identical, because `proposals_root()` falls back to the
  exact same `FORGE_ROOT / "proposals"` value the old code spelled directly.
- Seal cases 6, 15, 19, 21, 23 (`E1`): these succeed or refuse for reasons unrelated to
  `REVISION_UNREADABLE`, so they carry no F3 text either way.
- The override rendering (the actual bug fix) is proven by a dedicated behavioural test,
  not a sealed case: `test_a_refusal_under_an_override_names_the_override` runs `admit`
  with `IMPLEMENTATION_PROPOSALS` pointed at an empty directory and asserts the message
  contains that directory, not `FORGE_ROOT / "proposals"`.

## Anchor counts (measured, pasted)

Before this edit:

```
FORGE_ROOT / 'proposals' count: 5
{proposals_root()} count: 0
```

After this edit (recorded once the edit lands, task 2.2):

```
FORGE_ROOT / 'proposals' count: 0
{proposals_root()} count: 5
```
