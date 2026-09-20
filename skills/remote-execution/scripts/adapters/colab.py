#!/usr/bin/env python3
"""The Colab backend adapter — this file's own service is named here and
nowhere above the seam.

Every module above `adapter.py` (`ledger.py`, `packer.py`, `remote_cli.py`)
stays deliberately blind to what backend, if any, is behind a given worker.
This module is where that blindness ends: it is the one place permitted to
say "Colab", to spawn the one child that speaks to it, and to know that
service's own vocabulary well enough to translate it into the seam's.

Structural guarantees, held by what this file's own dependency graph can
even reach — never by convention:

1. This module imports `importlib`, `os`, `re`, `subprocess`, `sys` and
   `pathlib` — nothing else. It names no packaged SDK, and the one thing it
   shells out to is the official `colab` command line
   (`google-colab-cli`), which is the service's own headless client.

2. Colab authentication is the CLI's own business, read by the CLI's own
   child process: it resolves `~/.config/colab-cli/token.json` from the
   `HOME` this adapter forwards, and this module never opens that file,
   never learns a path to it, and never sees a token value. There is no
   `credentials` parameter on this adapter and no `CREDENTIAL_CLI` class
   attribute, so `remote_cli._construct_adapter()` never hands it a
   credential provider at all.

   The CLI's own session STATE file (`~/.config/colab-cli/sessions.json`)
   is credential-grade too, and for a measured reason: it carries a live
   per-session access token beside the session record (spike S0). Nothing
   here reads it, copies it or prints it — every session fact this module
   uses comes from the CLI's own stdout, and the only environment this
   module ever forwards is `PATH` and `HOME`.

3. Every subprocess call is `shell=False` with a list argv, an explicit
   timeout, and that same two-variable environment. A non-zero exit, an
   expired timeout, or output this module cannot honestly read is a
   refusal — `ColabAdapterError`, never a fabricated `Status`, `Submission`
   or `Fetched` the service never confirmed.

Slice status, stated so a refusal is never a mystery: this file owns the
S1 surface (registration, the static worker, `list_active()`, `cancel()`)
and refuses the session lifecycle — `submit()`, `poll()`, `fetch()` —
until implementation slice S2 lands it (uploads, detached launch, the
`/content/.psmith/<session>/` sentinel protocol, downloads, release).

Measured against `google-colab-cli` 0.6.0, live (spike S0; evidence in
`proposals/colab-cli-spike/findings.md`):
    [name] m-... | Hardware: CPU | Variant: DEFAULT          (sessions)
    [psmith-s0] m-... | Hardware: CPU | Variant: DEFAULT | Status: IDLE
    [colab] Session 'x' not found.                            (stop, exit 0)
Run with any Python 3.10+ (stdlib-only):
    python3 -m unittest tests.test_remote_execution
"""
from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
from pathlib import Path


def _load_adapter_seam():
    """Path-import `adapter.py`, one directory up from this file, reusing
    an already-loaded copy under `remote_execution_adapter` when one
    exists.

    Same `sys.modules`-reuse technique `kaggle.py` uses, and the same
    correctness reason: a second, separately exec'd copy of `adapter.py`
    would define a second, distinct `Adapter` class with the same name,
    and `isinstance(colab_adapter, ADAPTER.Adapter)` checks made by a
    caller holding the first copy would silently fail against an instance
    built from the second.
    """
    module_name = "remote_execution_adapter"
    if module_name in sys.modules:
        return sys.modules[module_name]
    script = Path(__file__).resolve().parent.parent / "adapter.py"
    spec = importlib.util.spec_from_file_location(module_name, script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


ADAPTER = _load_adapter_seam()


class ColabAdapterError(ADAPTER.AdapterError):
    """A refusal: the service CLI failed, timed out, or answered with
    something this adapter will not guess at.

    Never raised to report a guess — only to report that this adapter
    declined to fabricate an answer the service never actually confirmed.
    """


# The one worker this backend exposes: the operator's own Colab account.
WORKER_ID = "colab"

# The concurrent-job figure this backend claims, and the honest reason it
# is 1 rather than a discovered number: this adapter serializes its work
# on purpose (one named session per submission, one submission in flight
# per account), and the CLI reports no concurrency allowance to read.
# Revise only alongside a measured reason.
COLAB_WORKER_CAPACITY = 1

# Every session this adapter creates carries this name prefix. The CLI
# lists the ACCOUNT's sessions, not this skill's — `list_active()` claims
# only the prefixed ones, so a session some other tooling created can
# never be reported as a submission this adapter issued.
SESSION_NAME_PREFIX = "psmith-"

# The CONTROL-PLANE budget: `sessions` and `stop` are small requests whose
# answer the service produces immediately, so two minutes is already
# generous and failing fast is the correct behaviour. Transfer and
# in-kernel budgets are deliberately separate kinds of number and land
# with the session-lifecycle slice that uses them.
SUBPROCESS_TIMEOUT_SECONDS = 120.0

# The tokens a hand-typed launch would carry without ever routing through
# `remote_cli.py submit`. Read by `hooks/refuse_offpath_push.py`; a second
# service is covered by declaring its own tuple beside its own adapter,
# never by editing the hook. Deliberately absent: `sessions`, `status`,
# `ls` and `stop` are reads or cleanup, not launches.
PUSH_SURFACE: tuple[str, ...] = ("colab new", "colab exec", "colab run", "colab upload")

# The sessions listing's own line shape, measured in spike S0:
#     [name] m-... | Hardware: X | Variant: Y
# A machine whose name the CLI can no longer resolve is rendered `[?]`;
# it is deliberately NOT converted into a submission id below — there is
# no name to address it by.
_SESSION_LINE_RE = re.compile(r"^\[(?P<name>[^\]]+)\]\s+\S+")


def _lifecycle_refusal(action: str) -> ColabAdapterError:
    """The one refusal every not-yet-wired lifecycle operation raises,
    naming the slice that owns it so the gap is a placeholder with an
    owner, never a mystery. Nothing was launched, no session was created.
    """
    return ColabAdapterError(
        f"{action} is not wired yet: the Colab session lifecycle "
        "(new → remote dirs → uploads → detached launch → sentinel polling → "
        "downloads → release) lands with implementation slice S2. This "
        "adapter refuses rather than half-implement it — nothing was "
        "launched and no session was created."
    )


class ColabAdapter(ADAPTER.Adapter):
    """The official `colab` CLI, behind the seam's six operations."""

    def __init__(
        self,
        *,
        colab_executable: str = "colab",
        timeout: float = SUBPROCESS_TIMEOUT_SECONDS,
    ) -> None:
        self._colab_executable = colab_executable
        self._timeout = timeout

    # -- the subprocess boundary ------------------------------------------

    def _env_for(self) -> dict[str, str]:
        """The child's WHOLE environment, from a two-name allowlist:
        `PATH` and `HOME`. Nothing else is ever forwarded.

        `HOME` is load-bearing, not convenience: the CLI authenticates
        ITSELF out of `~/.config/colab-cli/token.json`, and it resolves
        that directory from the child's own `HOME`. This adapter never
        touches that file or its contents — the child is the only party
        that does. A process with no `HOME` is refused here rather than
        passed a child that would fail authentication for a reason no
        caller could read.
        """
        home = os.environ.get("HOME")
        if not home:
            raise ColabAdapterError(
                "HOME is not set in this process's environment; the colab "
                "CLI resolves its own credential file from HOME, and "
                "forwarding a child without one only moves the failure "
                "somewhere harder to read"
            )
        return {"PATH": os.environ.get("PATH", ""), "HOME": home}

    def _run(
        self,
        argv: list[str],
        *,
        timeout: float | None = None,
    ) -> subprocess.CompletedProcess:
        """One subprocess boundary for every child this adapter starts.

        `timeout=None` means `self._timeout`, the control-plane budget.
        A timeout or a missing executable is a refusal, and the refusal
        for a missing executable names the exact install command — this
        skill's `## Environment` section in `SKILL.md` is where a reader
        would look, and the sentence lives here, in the one file this
        skill lets name a service.
        """
        effective_timeout = self._timeout if timeout is None else timeout
        try:
            return subprocess.run(
                argv,
                shell=False,
                capture_output=True,
                text=True,
                timeout=effective_timeout,
                env=self._env_for(),
            )
        except subprocess.TimeoutExpired as exc:
            raise ColabAdapterError(
                f"{argv[0]} timed out after {effective_timeout}s: refusing to "
                "guess at a state this process never confirmed"
            ) from exc
        except OSError as exc:
            remedy = ""
            if argv and argv[0] == self._colab_executable:
                remedy = (
                    f" — this adapter shells out to the {argv[0]!r} command "
                    "line, which arrives with `uv tool install --python 3.14 "
                    'google-colab-cli --with "jupyter-kernel-client<1"`; '
                    "install it and make sure the tool bin directory it "
                    "reports is on PATH"
                )
            raise ColabAdapterError(f"could not run {argv[0]}: {exc}{remedy}") from exc

    # -- the seam's six operations ----------------------------------------

    def workers(self) -> list["ADAPTER.Worker"]:
        """This backend's one worker, stated rather than discovered.

        No subprocess, no network, no credential read: this backend's
        unit of capacity is the operator's single account, its sessions
        are serialized by this adapter, and a `workers()` that dialed the
        service would make `packer`'s own capacity path depend on the
        network for a figure no call could change.
        """
        return [ADAPTER.Worker(id=WORKER_ID, capacity=COLAB_WORKER_CAPACITY)]

    def submit(self, job: "ADAPTER.Job") -> "ADAPTER.Submission":
        raise _lifecycle_refusal("submit")

    def poll(self, submission_id: str) -> "ADAPTER.Status":
        raise _lifecycle_refusal("poll")

    def fetch(self, submission_id: str, into: Path) -> "ADAPTER.Fetched":
        raise _lifecycle_refusal("fetch")

    def cancel(self, submission_id: str) -> None:
        """`colab stop -s <session>`, addressed by the session name the
        submission id carries.

        An already-gone session is a no-op, and the measured reason is
        why this method reads OUTPUT rather than the exit code: stopping
        an unknown session prints `Session 'x' not found.` and exits 0
        (spike S0) — a bare `returncode != 0` check would read that as
        success and a genuine failure as whatever its prose said. No
        caller in the nine-command roster invokes this operation on its
        own initiative (`reconcile` reports orphans, never cancels them);
        it exists for an explicit caller and for tests.
        """
        _worker, sep, session_name = submission_id.partition("/")
        if not sep or not session_name:
            raise ColabAdapterError(
                f"{submission_id!r} is not '<worker>/<session-name>'; "
                "refusing to guess which session to stop"
            )
        argv = [self._colab_executable, "stop", "-s", session_name]
        result = self._run(argv)
        combined = f"{result.stdout}\n{result.stderr}"
        if "not found" in combined.lower():
            return
        if result.returncode != 0:
            raise ColabAdapterError(
                f"stop for {submission_id!r} refused (exit {result.returncode}): "
                f"{result.stderr.strip() or result.stdout.strip()}"
            )

    def list_active(self, worker: str) -> list[str]:
        """Submission ids this adapter issued whose sessions still exist,
        from `colab sessions` (measured shape in this module's docstring).

        Only names carrying this adapter's own prefix are claimed — the
        CLI lists the ACCOUNT's sessions, so a session some other tooling
        created is not this adapter's to report. A `[?]` machine is
        skipped deliberately: the CLI can no longer resolve a name for
        it, and fabricating one would make `reconcile` claim a session
        this skill can neither stop nor fetch.
        """
        result = self._run([self._colab_executable, "sessions"])
        if result.returncode != 0:
            raise ColabAdapterError(
                f"colab sessions refused (exit {result.returncode}): "
                f"{result.stderr.strip() or result.stdout.strip()}"
            )
        active: list[str] = []
        for line in result.stdout.splitlines():
            match = _SESSION_LINE_RE.match(line.strip())
            if match is None:
                continue
            name = match.group("name")
            if name == "?" or not name.startswith(SESSION_NAME_PREFIX):
                continue
            active.append(f"{worker}/{name}")
        return active


ADAPTER.register("colab", ColabAdapter)
