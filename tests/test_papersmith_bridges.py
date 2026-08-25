"""Subprocess bridge contracts and deliberation action aliases."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from papersmith.bridges import deliberation, implementation, node, python as python_bridge
from papersmith.core.exit_codes import EXECUTION_ERROR, SUCCESS, USER_ERROR, map_child_rc
from papersmith.errors import ExecutionError, UserError


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("child", "expected"),
    [(0, SUCCESS), (2, USER_ERROR), (1, EXECUTION_ERROR), (7, EXECUTION_ERROR)],
)
def test_child_exit_code_mapping(child: int, expected: int) -> None:
    assert map_child_rc(child) == expected


def test_interpreter_falls_back_then_selects_project_micromamba(tmp_path: Path) -> None:
    assert python_bridge.interpreter_for(tmp_path, prefer_micromamba=True)[0] != str(
        tmp_path / ".micromamba" / "bin" / "micromamba"
    )
    mamba = tmp_path / ".micromamba/bin/micromamba"
    mamba.parent.mkdir(parents=True)
    mamba.write_text("binary", encoding="utf-8")
    (tmp_path / ".micromamba/envs/papersmith").mkdir(parents=True)
    assert python_bridge.interpreter_for(tmp_path, prefer_micromamba=True) == [
        str(mamba), "run", "-n", "papersmith", "python"
    ]


def test_run_script_forwards_list_argv_and_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    script = tmp_path / "script.py"
    script.write_text("", encoding="utf-8")
    captured: dict[str, object] = {}

    def fake_run(command, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return subprocess.CompletedProcess(command, 0, "ok", "")

    monkeypatch.setattr(python_bridge.subprocess, "run", fake_run)
    result = python_bridge.run_script(tmp_path, script, ["--flag", "value"], env={"PAPER": "1"})
    assert result.returncode == 0
    assert captured["command"][-3:] == [str(script), "--flag", "value"]
    assert captured["kwargs"]["env"]["PAPER"] == "1"
    assert captured["kwargs"]["cwd"] == tmp_path


def test_missing_script_is_a_source_error(tmp_path: Path) -> None:
    with pytest.raises(Exception, match="missing skill script"):
        python_bridge.run_script(tmp_path, "missing.py")


def _implementation_args(**overrides):
    values = {
        "action": "materialize",
        "target": "implementations/paper",
        "name": "Paper",
        "plan": "plan.json",
        "finding": None,
        "entry_text": None,
        "python": None,
        "shards": None,
        "revision": None,
        "extra": [],
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_implementation_aliases_map_to_real_commands() -> None:
    command, args = implementation.command_args(_implementation_args())
    assert command == "apply"
    assert args == ["--target", "implementations/paper", "--name", "Paper", "--plan", "plan.json"]
    command, args = implementation.command_args(_implementation_args(action="benchmark", plan=None))
    assert command == "probe"
    assert "--target" in args and "--name" in args


def test_implementation_validates_required_fields() -> None:
    with pytest.raises(UserError, match="requires --target"):
        implementation.command_args(_implementation_args(target=None))
    with pytest.raises(UserError, match="requires --plan"):
        implementation.command_args(_implementation_args(plan=None))


def _deliberation_args(**overrides):
    values = {
        "request": None,
        "request_file": None,
        "action": "status",
        "instruction": None,
        "revision": None,
        "query": [],
        "selected_entry_id": [],
        "decisions": None,
        "accept": False,
        "acceptance_token": None,
        "withdrawal_operation_id": None,
        "withdrawal_reason": None,
        "prior_conclusion": None,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_deliberation_alias_request_shapes() -> None:
    assert deliberation.build_request(_deliberation_args(action="status")) == {"operation": "STATUS"}
    assert deliberation.build_request(_deliberation_args(
        action="init", instruction="A proposal idea"
    )) == {"operation": "CREATE_INITIAL_REVISION", "instruction": "A proposal idea"}
    assert deliberation.build_request(_deliberation_args(
        action="plan", revision="research-concept-r01.md", query=["Assumptions stationarity"]
    )) == {
        "operation": "RESOLVE_TARGET",
        "sourceFilename": "research-concept-r01.md",
        "query": "Assumptions stationarity",
    }
    assert deliberation.build_request(_deliberation_args(
        action="audit", instruction="audit this"
    )) == {"operation": "MAINTENANCE", "instruction": "audit this"}


def test_raw_deliberation_request_is_not_reshaped() -> None:
    request = {"operation": "STATUS", "sourceFilename": "note.md"}
    args = _deliberation_args(request='{"operation":"STATUS","sourceFilename":"note.md"}', action=None)
    assert deliberation.build_request(args) == request


def test_deliberation_requires_instruction_for_mutating_alias() -> None:
    with pytest.raises(UserError, match="--instruction is required"):
        deliberation.build_request(_deliberation_args(action="init"))


def test_node_missing_is_user_error(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(node, "node_binary", lambda: None)
    with pytest.raises(UserError, match="node is required"):
        node.ensure_node_engine(tmp_path)


@pytest.mark.skipif(
    shutil.which("node") is None or not (ROOT / "node_modules/jiti").is_dir(),
    reason="Node.js and jiti are required for the keyless engine smoke check",
)
def test_deliberation_status_uses_one_json_lines_engine() -> None:
    responses = node.call_engine(ROOT, [{"operation": "STATUS"}], timeout=60)
    assert len(responses) == 1
    assert responses[0]["status"] == "ok"
    assert responses[0]["operation"] == "STATUS"
