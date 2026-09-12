"""This corpus's own thin wrapper over `tests/seal/harness.py`'s generic
machinery (design.md D7): `run_case`/`validate_case`/`digest_result`/
`RosterValidationError` are reused UNEDITED (`tests/seal/harness.py` itself
is never modified -- the bar `git diff --exit-code tests/seal/` holds).

What differs is WHICH launcher a case's argv resolves to.
`seal_harness.run_case` builds `full_argv` from `impl.CLI_INVOCATION` --
`impl` there is `tests/seal/harness.py`'s own `implementation_engine`
import, permanently resolved (by that module's own `os.environ.setdefault`)
against the SIBLING's profile. `cli_invocation()` below temporarily
reassigns that one attribute for the duration of a call -- an argv change,
never a monkeypatch of anything a CHILD process reads (design.md D7): the
child this launches is a real, separate subprocess running THIS skill's own
launcher, and nothing inside an already-running child is touched.
"""

from __future__ import annotations

import contextlib
import sys
from pathlib import Path

FORGE = Path(__file__).resolve().parents[2]
LAUNCHER = (
    FORGE / ".claude" / "skills" / "experimental-implementation" / "scripts"
    / "implementation_cli.py")

_TESTS_DIR = FORGE / "tests"
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))
from seal import harness as seal_harness  # noqa: E402  (path set above)
from seal import corpus as seal_corpus  # noqa: E402  (re-exported below)

#: Re-exported for callers that only need the generic, unedited surface.
run_case = seal_harness.run_case
digest_result = seal_harness.digest_result
validate_case = seal_harness.validate_case
validate_roster = seal_harness.validate_roster
RosterValidationError = seal_harness.RosterValidationError
build_env = seal_harness.build_env
ALLOWED_ENV_KEYS = seal_harness.ALLOWED_ENV_KEYS

_LAUNCHER_INVOCATION = f"{sys.executable} {LAUNCHER}"


@contextlib.contextmanager
def cli_invocation():
    """Wrap `seal_harness.impl.CLI_INVOCATION` for the duration of the
    block -- this skill's own launcher, not the sibling's -- and restore
    the original value on exit, success or failure alike."""
    original = seal_harness.impl.CLI_INVOCATION
    seal_harness.impl.CLI_INVOCATION = _LAUNCHER_INVOCATION
    try:
        yield
    finally:
        seal_harness.impl.CLI_INVOCATION = original


def run_case_here(case: dict, roots, *, scratch_root):
    """`run_case`, wrapped so this corpus's cases run through THIS skill's
    own launcher for the duration of the one call."""
    with cli_invocation():
        return seal_harness.run_case(case, roots, scratch_root=scratch_root)
