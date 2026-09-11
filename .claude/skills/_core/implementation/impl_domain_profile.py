"""The contract a Cut-1 implementation domain fills in, and the resolver
that finds it.

The moved engine (`_core/implementation/engine/implementation_engine.py`)
serves no domain of its own: it resolves its host from
`IMPLEMENTATION_DOMAIN_PROFILE` and refuses to start without one, mirroring
`.claude/skills/_core/deliberation/engine/domain-profile.ts`'s resolver
properties exactly -- no default, fails closed at import, absolute path
required, nested required-key validation, path values validated, named
refusal codes.

`ImplementationProfileError(RuntimeError)`, never `Refused`/`NameRefused`
(design.md D3, three independent reasons):

1. The TS precedent throws a plain `Error`, not the engine's own domain
   refusal type.
2. The engine's JSON error renderer lives inside a module that has not
   finished importing when this resolves, and a second, duplicated renderer
   here is new surface for a state the launcher never produces.
3. Collateral: `reachable_refusal_codes()`, part of this suite's own
   coverage lock, walks every `*.py` under `_core/implementation/` for
   `Refused`/`NameRefused` constructions and pins its derived count at a
   fixed number. Six `Refused`s in a core module would move that unrelated
   pin -- a behavioural-delta-adjacent edit to a guard this change does not
   touch. A distinctly-named exception is invisible to that walk.

Cut-1 field set (design.md D3, amended 2026-09-11 -- operator ruling on task
7.5's non-interference finding): `kit.root` (the engine's `SKILL_ROOT`, 19
reader lines), `cli.path` (the engine's `CLI_PATH` -> `CLI_INVOCATION`), and
`objective` (the engine's `OBJECTIVE_FLOW` -- stamped into every refusal AND
discovered by the suite's cross-skill north lock (`test_agents.py`), which
walks a skill's OWN directory tree for a literal `OBJECTIVE_FLOW` assignment).
Nothing else -- a profile field nothing reads cannot be mutation-proven, and
an unprovable field is the shape of a false guard; `objective` earns its
place by that exact rule, now that it is read twice from outside the engine.
"""
from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from typing import Any, Mapping

#: The variable a launcher sets (`setdefault`, so an explicit override wins)
#: and this resolver reads. No default: a default would have to name one
#: domain, which is exactly the coupling this file exists to remove.
_ENV_VAR = "IMPLEMENTATION_DOMAIN_PROFILE"

#: `(section, key)` pairs the profile must declare, nested. Named this way
#: so an incomplete `kit: {}`-shaped profile is refused by its actual
#: missing LEAF (`kit.root`), never by the top-level key alone -- the
#: `artifact: {}` lesson `domain-profile.ts` already learned once. Path-
#: valued only: each pair below is also walked by the UNSAFE_PATH check,
#: which treats every value here as a filesystem path. `objective`'s own
#: leaves are validated separately (`_OBJECTIVE_REQUIRED`), since none of
#: them is a path.
_REQUIRED_NESTED: tuple[tuple[str, str], ...] = (("kit", "root"), ("cli", "path"))

#: `domain-profile.ts`'s own `OBJECTIVE_REQUIRED` mirrored exactly: the four
#: top-level keys a declared north must carry.
_OBJECTIVE_REQUIRED: tuple[str, ...] = ("purpose", "stages", "arrival", "humanStops")

#: What every element of `objective.stages` must carry. `stages: []` would
#: pass a bare presence check vacuously -- a north with no stages is not a
#: north -- so this is checked as its own shape, exactly as `domain-
#: profile.ts`'s `stagesIncomplete` does.
_STAGE_REQUIRED: tuple[str, ...] = ("stage", "establishes", "behindWhen")


class ImplementationProfileError(RuntimeError):
    """The engine has no domain profile it can start with.

    Deliberately not `Refused`/`NameRefused` -- see the module docstring's
    three reasons. Every message below leads with its own named code so a
    caller can classify the refusal from `str(error)` alone, exactly as the
    engine's own `Refused.code` lets a JSON reader classify a refusal.
    """


def _load_profile_module(path: Path, configured: str):
    """One fresh, uncached load of the host-declared profile file.

    `spec_from_file_location` returning `None` (an unrecognised location)
    and the module's own top-level code raising are both refused under the
    same `UNREADABLE` code -- the caller only ever gets a working profile
    or a named reason it does not have one, never a raw traceback from a
    file it does not own.
    """
    spec = importlib.util.spec_from_file_location(
        "impl_domain_profile_host", path)
    if spec is None or spec.loader is None:
        raise ImplementationProfileError(
            f"IMPLEMENTATION_DOMAIN_PROFILE_UNREADABLE: {configured} could "
            "not be loaded as a module.")
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    except ImplementationProfileError:
        raise
    except Exception as exc:  # the host's own file is malformed
        raise ImplementationProfileError(
            f"IMPLEMENTATION_DOMAIN_PROFILE_UNREADABLE: {configured} raised "
            f"{type(exc).__name__}: {exc}") from exc
    return module


def _resolve() -> Mapping[str, Any]:
    configured = os.environ.get(_ENV_VAR)
    if not configured:
        raise ImplementationProfileError(
            "IMPLEMENTATION_DOMAIN_PROFILE_REQUIRED: this engine serves no "
            f"domain of its own. Set {_ENV_VAR} to a module exporting "
            "`PROFILE`, or launch through a skill's own "
            "scripts/implementation_cli.py, which sets it.")

    # Absolute, and refused otherwise -- mirroring domain-profile.ts's own
    # reasoning verbatim: a relative path resolves against the working
    # directory, and the engine does not control that. A child process
    # launched with its cwd inside the engine would turn
    # `.claude/skills/.../impl_profile.py` into
    # `<engine>/.claude/skills/.../impl_profile.py` and die on a path
    # nobody wrote. Every launcher that sets this variable already knows an
    # absolute path.
    path = Path(configured)
    if not path.is_absolute():
        raise ImplementationProfileError(
            f"IMPLEMENTATION_DOMAIN_PROFILE_NOT_ABSOLUTE: {configured} is "
            "relative, and a child process's working directory is not the "
            "engine's to assume.")
    if not path.is_file():
        raise ImplementationProfileError(
            f"IMPLEMENTATION_DOMAIN_PROFILE_UNREADABLE: {configured} does "
            "not exist.")

    module = _load_profile_module(path, configured)
    profile = getattr(module, "PROFILE", None)
    if not isinstance(profile, Mapping):
        raise ImplementationProfileError(
            f"IMPLEMENTATION_DOMAIN_PROFILE_INVALID: {configured} exports "
            "no `PROFILE`, or it is not a mapping.")

    missing = []
    for section, key in _REQUIRED_NESTED:
        section_value = profile.get(section)
        if not isinstance(section_value, Mapping) or key not in section_value:
            missing.append(f"{section}.{key}")

    objective = profile.get("objective")
    if not isinstance(objective, Mapping):
        missing.append("objective")
    else:
        for key in _OBJECTIVE_REQUIRED:
            if key not in objective:
                missing.append(f"objective.{key}")
    if missing:
        raise ImplementationProfileError(
            f"IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE: {configured} is "
            f"missing {', '.join(missing)}.")

    # `stages` presence alone (the loop above) does not rule out `stages: []`
    # -- domain-profile.ts's own `stagesIncomplete` lesson. Every element
    # must carry all three `_STAGE_REQUIRED` keys, or a stage this domain
    # declares by name would silently establish nothing and close on no
    # condition at all.
    stages = objective["stages"]
    stages_incomplete = (
        not isinstance(stages, (list, tuple)) or len(stages) == 0
        or any(not isinstance(stage, Mapping)
              or any(key not in stage for key in _STAGE_REQUIRED)
              for stage in stages))
    if stages_incomplete:
        raise ImplementationProfileError(
            f"IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE: {configured} is "
            "missing objective.stages.")

    # `SAFE_ARTIFACT_SEGMENT` in the TS precedent guards SEGMENTS joined
    # under a root; these are whole absolute paths the host names, so that
    # escape is not reachable here. What IS reachable is a `kit.root` that
    # does not exist -- today that scatters into 19 unrelated missing-asset
    # failures across the engine's own readers; validating it here turns
    # them into one named refusal at import (design.md D3). A "must live
    # under FORGE_ROOT" rule was considered and rejected: it would refuse a
    # tmpdir fixture profile, which is the exact override case `setdefault`
    # exists to serve.
    unsafe = []
    for section, key in _REQUIRED_NESTED:
        value = Path(profile[section][key])
        if not value.is_absolute() or not value.exists():
            unsafe.append(f"{section}.{key}")
    if unsafe:
        raise ImplementationProfileError(
            f"IMPLEMENTATION_DOMAIN_PROFILE_UNSAFE_PATH: {configured} "
            f"declares an unsafe {', '.join(unsafe)} (must be absolute and "
            "exist on disk).")

    return profile


#: The profile this process serves, resolved once at import. Chosen by the
#: host, never by the engine -- see the module docstring.
PROFILE: Mapping[str, Any] = _resolve()
