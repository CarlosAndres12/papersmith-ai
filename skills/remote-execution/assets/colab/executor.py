#!/usr/bin/env python3
"""The Colab VM-side executor — everything after `launch.py` spawned it.

Runs INSIDE the session's working directory (`/content/.psmith/<session>`
in production; its own resolved directory everywhere else, which is what
lets the forge suite execute it without a VM). It reads the uploaded
`run-config.json` and `runner.ipynb`, executes the notebook with
`nbclient`, and writes the three files the session protocol is built on:

- `runner.executed.ipynb` — the executed notebook, written on the failure
  path too, because a notebook that died halfway is the only record of
  where it died (`runner_invoke.py`'s own doctrine, applied one level up);
- `files.json` — the manifest `fetch()` downloads: the runner's
  working-directory capture (every regular file under this directory,
  minus the protocol's own names and minus `clone/.git`). Never a
  candidate scan, and never the pinned clone's VCS metadata: this is the
  landed capture rule of the parent plan's D12 (judged fix S2-J1, with
  the `.git` fold-in S2-J12);
- `status.json` — LAST, and outside every other try/finally: its presence
  is the run's only completion signal (`exitCode` 0 or non-zero, never
  absent for a run that reached this process).

A crash before `status.json` leaves the run `running` to a poll, which is
exactly what it is: the evidence that completion happened is missing, not
negative, so nothing here ever invents one early.

Nothing here names the service, reads a credential, or knows the CLI
exists: this file's whole world is one directory on one VM. S3's
credential-material deletion hangs beside the `finally` below; this slice
stages no such material, and deleting nothing is the correct S3-prep
behavior.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

CONFIG_FILENAME = "run-config.json"
NOTEBOOK_FILENAME = "runner.ipynb"
EXECUTED_NOTEBOOK_FILENAME = "runner.executed.ipynb"
FILES_FILENAME = "files.json"
STATUS_FILENAME = "status.json"
STDOUT_LOG_FILENAME = "stdout.log"
LAUNCH_FILENAME = "launch.json"
EXECUTOR_FILENAME = "executor.py"
CLONE_DIRNAME = "clone"
VCS_DIRNAME = ".git"
DEFAULT_KERNEL_NAME = "python3"

# The files the PROTOCOL itself owns in the working directory. Subtracted
# from the manifest by name at the TOP level only: a file carrying one of
# these names further down the tree is a product of the run, not a
# protocol payload, and stays in the capture.
PROTOCOL_FILENAMES = frozenset(
    {
        EXECUTOR_FILENAME,
        LAUNCH_FILENAME,
        CONFIG_FILENAME,
        NOTEBOOK_FILENAME,
        STATUS_FILENAME,
        FILES_FILENAME,
        STDOUT_LOG_FILENAME,
    }
)

# This executor's OWN ceiling for one notebook execution — deliberately
# not the CLI's helper budget (`--timeout`'s 600 s class is for short
# in-kernel helpers, never for the payload run this skill exists for): a
# ceiling that kills a real run records a failure the run never had.
# Three hours sits well above the observed run lengths this skill has
# paid for (a 75-minute GPU run is on record) and below Colab's own
# session ceiling.
NOTEBOOK_TIMEOUT_SECONDS = 10800.0

# The whole allowlist of ERROR TEXT kept in `status.json`. Bounded so a
# runaway traceback cannot turn the completion signal into a multi-MB
# file every poll has to read past.
ERROR_MAX_CHARS = 2000


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _write_json(path: Path, payload: object) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def execute_notebook(base: Path) -> None:
    """Execute `runner.ipynb` with its own declared kernel, with the
    kernel's working directory set to `base` — the runner's working
    directory, and deliberately not the notebook's location: a relative
    write is an output, and outputs must land where `fetch()` looks.

    The executed notebook is written in a `finally`, so a run that dies
    halfway still comes back with the cell that killed it. `nbformat`
    and `nbclient` are imported HERE, never at module import: importing
    the module (the forge suite does) must not require a kernel
    installation, and a missing one surfaces as this run's failure with
    the traceback in `status.json["error"]`, not as an import-time crash
    of the whole executor.

    `client_factory`-style injection is deliberately absent: the suite
    drives this function's caller (`run`) with this function replaced,
    which is the same seam one level up.
    """
    import nbformat
    from nbclient import NotebookClient

    notebook_path = base / NOTEBOOK_FILENAME
    notebook = nbformat.read(str(notebook_path), as_version=4)
    kernelspec = (notebook.get("metadata") or {}).get("kernelspec") or {}
    kernel_name = str(kernelspec.get("name") or DEFAULT_KERNEL_NAME)
    client = NotebookClient(
        notebook,
        timeout=NOTEBOOK_TIMEOUT_SECONDS,
        kernel_name=kernel_name,
        resources={"metadata": {"path": str(base)}},
    )
    try:
        client.execute()
    finally:
        nbformat.write(notebook, str(base / EXECUTED_NOTEBOOK_FILENAME))


def manifest_entries(base: Path) -> list[str]:
    """The `files.json` allowlist: every regular file the run left in its
    working directory, minus the protocol's own names and minus the
    pinned clone's VCS metadata, sorted POSIX-relative.

    Two prunes, each a deliberate rule rather than a heuristic:

    - a TOP-LEVEL name in `PROTOCOL_FILENAMES` is protocol, not product;
    - anything under `clone/.git/` is the pinned input's VCS metadata —
      thousands of files that are not produced artifacts and that a
      per-file download would pay for one call at a time.

    Symlinks are skipped, never followed and never listed: a link's
    target is somebody else's file, possibly outside this directory, and
    a manifest that can point outside the session is a manifest that can
    fetch a file this run never made.
    """
    entries: list[str] = []
    for path in base.rglob("*"):
        if path.is_symlink():
            continue
        if not path.is_file():
            continue
        relative = path.relative_to(base)
        parts = relative.parts
        if len(parts) == 1 and parts[0] in PROTOCOL_FILENAMES:
            continue
        if len(parts) >= 2 and parts[0] == CLONE_DIRNAME and parts[1] == VCS_DIRNAME:
            continue
        entries.append(relative.as_posix())
    return sorted(entries)


def run(base: Path) -> int:
    """Execute, then always write the manifest and, last of all, the
    completion signal. The return value is the exit code `status.json`
    carries; the CALLER (`__main__` below) uses it only as its own exit
    code, and the adapter's poll reads `status.json`, never this
    process's exit status — a detached child's exit status is not
    observable to anybody who was not waiting on it, and the CLI process
    that spawned us is long gone.
    """
    errors: list[str] = []
    exit_code = 0
    try:
        execute_notebook(base)
    except BaseException as exc:  # noqa: BLE001 - the signal must survive any failure
        exit_code = 1
        errors.append(f"{type(exc).__name__}: {exc}")

    try:
        _write_json(base / FILES_FILENAME, manifest_entries(base))
    except BaseException as exc:  # noqa: BLE001 - status.json must still land
        errors.append(f"manifest: {type(exc).__name__}: {exc}")

    status: dict[str, object] = {"exitCode": exit_code, "finishedAt": _utc_now()}
    if errors:
        status["error"] = " | ".join(errors)[:ERROR_MAX_CHARS]
    _write_json(base / STATUS_FILENAME, status)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(run(Path(__file__).resolve().parent))
