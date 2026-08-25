"""Execution-profile, ledger, target, remote, and audit contracts."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from papersmith.bridges import audit as audit_bridge
from papersmith.bridges import remote as remote_bridge
from papersmith.cli import main
from papersmith.core import config, executor, init as init_module, ledger, target
from papersmith.core.exit_codes import DRIFT_ERROR, SUCCESS
from papersmith.errors import UserError


def _workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "paper"
    init_module.initialize(workspace, run_npm=False)
    return workspace


def _write_local_manifest(workspace: Path, *, sharded: bool = False) -> None:
    values = "\n      values: [11, 22]\n      parameter: \"--seed\"" if sharded else ""
    workspace.joinpath("papersmith.yaml").write_text(
        f'''version: "1"
name: "{workspace.name}"
title: "Execution Test"
compute_targets:
  default: "local"
  targets:
    local:
      provider: "local"
execution_profiles:
  smoke:
    target: "local"
    entrypoint: "python -c \\\"print(42)\\\""
    timeout_seconds: 30
    sharding:
      enabled: {str(sharded).lower()}{values}
''',
        encoding="utf-8",
    )


def test_ledger_is_append_only_and_jsonl(tmp_path: Path) -> None:
    ledger.append(tmp_path, {"profile": "smoke", "exit": 0})
    ledger.append(tmp_path, {"profile": "sweep", "exit": 4})
    records = ledger.read(tmp_path)
    assert [record["profile"] for record in records] == ["smoke", "sweep"]
    assert all("timestamp" in record for record in records)
    assert len((tmp_path / ".papersmith/runs_ledger.jsonl").read_text().splitlines()) == 2


def test_local_profile_runs_and_records_success(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    _write_local_manifest(workspace)

    result = executor.run_profile(workspace, "smoke")

    assert result["status"] == "ok"
    assert result["jobs"][0]["exit"] == SUCCESS
    assert ledger.read(workspace)[0]["dry_run"] is False


def test_dry_run_and_shard_selection_are_recorded_without_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = _workspace(tmp_path)
    _write_local_manifest(workspace, sharded=True)
    called = False

    def fail_if_called(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("dry-run dispatched a subprocess")

    monkeypatch.setattr(executor.subprocess, "run", fail_if_called)
    result = executor.run_profile(workspace, "smoke", dry_run=True, shard=1)

    assert called is False
    assert result["status"] == "ok"
    assert result["jobs"][0]["shard_value"] == 22
    assert result["jobs"][0]["command"][-2:] == ["--seed", "22"]
    assert ledger.read(workspace)[0]["dry_run"] is True


def test_profile_rejects_invalid_shard_and_profile(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    _write_local_manifest(workspace, sharded=True)
    with pytest.raises(UserError, match="outside"):
        executor.run_profile(workspace, "smoke", shard=3)
    with pytest.raises(UserError, match="unknown execution profile"):
        executor.run_profile(workspace, "missing", dry_run=True)


def test_target_list_set_and_local_check(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    data = config.load_papersmith_yaml(workspace)
    listed = target.list_targets(workspace)
    assert {item["name"] for item in listed} == set(data["compute_targets"]["targets"])
    selected = target.set_target(workspace, "local-workstation")
    assert selected["provider"] == "local"
    code, result = target.check_target(workspace)
    assert code == SUCCESS
    assert result["reachable"] is True


def test_target_rejects_unknown_name(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    with pytest.raises(UserError, match="unknown compute target"):
        target.set_target(workspace, "does-not-exist")


def test_cli_run_dry_run_and_target_list(tmp_path: Path, capsys) -> None:
    workspace = _workspace(tmp_path)
    _write_local_manifest(workspace)
    assert main(["run", "smoke", "--dry-run", str(workspace)]) == SUCCESS
    output = capsys.readouterr().out
    assert "dry-run" in output
    assert main(["target", "list", str(workspace)]) == SUCCESS
    assert "local: local" in capsys.readouterr().out


def _remote_args(**overrides):
    values = {
        "operation": "push",
        "target": "implementations/paper",
        "entrypoint": "implementations/paper/runner.ipynb",
        "backend": "kaggle",
        "account": "worker-a",
        "job": None,
        "submission_id": None,
        "dest": None,
        "consent": "token",
        "smoke": True,
        "unit": ["seed 1", "seed,2"],
        "force": False,
        "resolve": False,
        "service": None,
        "job_name": None,
        "product": None,
        "commit": None,
        "repo_url": None,
        "repo_ref": None,
        "run_module": None,
        "run_function": None,
        "clone_path": [],
        "regenerate": False,
        "extra": [],
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_remote_push_maps_account_job_and_repeatable_units() -> None:
    command = remote_bridge.command_args(_remote_args())
    assert command[:2] == ["submit", "--target"]
    assert "--worker" in command and "worker-a" in command
    assert command.count("--unit") == 2
    assert "seed,2" in command
    assert "--consent" in command


def test_remote_pack_requires_generator_metadata() -> None:
    with pytest.raises(UserError, match="remote pack requires"):
        remote_bridge.command_args(_remote_args(
            operation="pack", service=None, job_name=None, product=None,
            repo_url=None, repo_ref=None, run_module=None, run_function=None,
        ))


def test_remote_pull_maps_job_to_submission_id() -> None:
    command = remote_bridge.command_args(_remote_args(
        operation="pull", target="target", entrypoint="runner.ipynb",
        backend="kaggle", account=None, job="sub-1", dest="inbox/sub-1",
        unit=[], consent=None, smoke=False,
    ))
    assert command == [
        "fetch", "--target", "target", "--entrypoint", "runner.ipynb",
        "--submission-id", "sub-1", "--dest", "inbox/sub-1", "--backend", "kaggle",
    ]


def test_audit_check_drift_returns_exit_three_without_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = _workspace(tmp_path)
    (workspace / "skills/skill-audit/references/probes/skill-audit.structure.json").write_text("{}")
    monkeypatch.setattr(audit_bridge, "run_script", lambda *args, **kwargs: subprocess.CompletedProcess([], 0, "audit ok\n", ""))
    monkeypatch.setattr(audit_bridge, "check_generated", lambda *args, **kwargs: ["PI.md"])
    result = audit_bridge.execute(workspace, check_drift=True)
    assert result == DRIFT_ERROR
