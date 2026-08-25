"""Standalone generator wrappers and drift detection."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from papersmith.core import init as init_module
from papersmith.generators import ALL_TOOLS, check_generated, collect_agents, render_files


ROOT = Path(__file__).resolve().parents[1]


def _workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "paper"
    init_module.initialize(workspace, run_npm=False)
    return workspace


def test_generators_are_clean_after_init(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    assert check_generated(workspace, tools=ALL_TOOLS) == []
    assert set(render_files(workspace, tools=ALL_TOOLS)) == {
        ".gitignore",
        "CLAUDE.md",
        "OPENCODE.md",
        "PI.md",
        ".pi/gentle-ai/persona.json",
        ".antigravity/rules.md",
    }
    agents = collect_agents(workspace)
    assert any(agent["name"] == "paper-ingestion" for agent in agents)


def test_opencode_check_reports_drift_without_mutating(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    output = workspace / "OPENCODE.md"
    original = output.read_bytes()
    output.write_bytes(b"drift\n")
    command = [sys.executable, str(ROOT / "scripts/gen-opencode.py"), "--root", str(workspace), "--check"]
    checked = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert checked.returncode == 3
    assert "OPENCODE.md" in checked.stdout
    assert output.read_bytes() == b"drift\n"

    generated = subprocess.run(command[:-1], cwd=ROOT, capture_output=True, text=True)
    assert generated.returncode == 0, generated.stderr
    assert output.read_bytes() == original


def test_pi_generator_repairs_both_outputs(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    (workspace / "PI.md").write_text("drift", encoding="utf-8")
    (workspace / ".pi/gentle-ai/persona.json").write_text("{}", encoding="utf-8")
    command = [sys.executable, str(ROOT / "scripts/gen-pi.py"), "--root", str(workspace)]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert '"mode": "gentleman"' in (workspace / ".pi/gentle-ai/persona.json").read_text()
    assert "drift" not in (workspace / "PI.md").read_text()


def test_antigravity_check_is_exit_three_on_missing_output(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    (workspace / ".antigravity/rules.md").unlink()
    command = [
        sys.executable, str(ROOT / "scripts/gen-antigravity.py"),
        "--root", str(workspace), "--check",
    ]
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 3
    assert ".antigravity/rules.md" in result.stdout
