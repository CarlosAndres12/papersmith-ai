"""Workspace initialization tests against the real repository kit."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from papersmith.cli import main
from papersmith.core import config, init as init_module, manifest
from papersmith.errors import UserError
from papersmith.yamllite import loads


def test_initialize_creates_the_workspace_contract(tmp_path: Path) -> None:
    workspace = tmp_path / "sparse-ae"
    result = init_module.initialize(
        workspace,
        title="Sparse Autoencoder Audit",
        topic="mechanistic interpretability",
        tools=("claude", "opencode", "pi", "antigravity"),
        remote="kaggle",
        run_npm=False,
    )

    assert result["name"] == "sparse-ae"
    assert result["version"] == "0.1.0"
    assert result["default_target"] == "kaggle-gpu-pool"
    for relpath in (
        ".papersmith/version",
        ".papersmith/manifest.json",
        ".papersmith/config.json",
        ".papersmith/runs_ledger.jsonl",
        ".claude/agents/paper-ingestion.md",
        "skills/paper-ingestion/SKILL.md",
        "skills/proposal-deliberation/engine/cli.mjs",
        "skills/kaggle-accounts/store/.gitignore",
        "guidance/paper-guide",
        "guidance/reference-papers",
        "proposals/drafts",
        "proposals/deliberated",
        "proposals/receipts",
        "implementations",
        "kaggle-inbox",
        "journal/README.md",
        "DECISIONS.md",
        "papersmith.yaml",
        "README.md",
        "CLAUDE.md",
        "OPENCODE.md",
        "PI.md",
        ".pi/gentle-ai/persona.json",
        ".antigravity/rules.md",
        ".gitignore",
    ):
        assert (workspace / relpath).exists(), relpath

    # Credentials are never copied from the kit store.
    assert not (workspace / "skills/kaggle-accounts/store/accounts.json").exists()
    assert "paper-ingestion" in (workspace / "CLAUDE.md").read_text(encoding="utf-8")
    assert "mechanistic interpretability" in (workspace / "OPENCODE.md").read_text(encoding="utf-8")
    assert json.loads((workspace / ".pi/gentle-ai/persona.json").read_text()) == {"mode": "gentleman"}

    yaml = config.load_papersmith_yaml(workspace)
    assert yaml["name"] == "sparse-ae"
    assert yaml["title"] == "Sparse Autoencoder Audit"
    assert yaml["topic"] == "mechanistic interpretability"
    assert yaml["paper_ingestion"]["mode"] == "fast"
    assert yaml["compute_targets"]["default"] == "kaggle-gpu-pool"
    assert set(yaml["execution_profiles"]) == {
        "smoke_and_invariants", "sweep_training", "benchmark_evaluation"
    }

    cfg = config.load_workspace_config(workspace)
    assert cfg["project_name"] == "sparse-ae"
    assert cfg["active_tools"] == ["claude", "opencode", "pi", "antigravity"]
    assert cfg["execution_engine"]["active_compute_target"] == "kaggle-gpu-pool"

    stored_manifest = json.loads((workspace / ".papersmith/manifest.json").read_text())
    assert stored_manifest["kind"] == "workspace"
    assert stored_manifest["version"] == "0.1.0"
    expected = manifest.workspace_framework_files(workspace, Path(__file__).parents[1])
    assert stored_manifest["files"] == expected


@pytest.mark.parametrize(
    ("remote", "target"),
    [
        ("local", "local-workstation"),
        ("kaggle", "kaggle-gpu-pool"),
        ("slurm", "slurm-cluster"),
    ],
)
def test_remote_selects_the_declared_default_target(
    tmp_path: Path, remote: str, target: str
) -> None:
    workspace = tmp_path / remote
    init_module.initialize(workspace, remote=remote, run_npm=False)
    data = config.load_papersmith_yaml(workspace)
    assert data["compute_targets"]["default"] == target
    cfg = config.load_workspace_config(workspace)
    assert cfg["execution_engine"]["active_compute_target"] == target


def test_initialize_rejects_unknown_tools(tmp_path: Path) -> None:
    with pytest.raises(UserError, match="unsupported runtime"):
        init_module.initialize(tmp_path / "paper", tools=("claude", "wat"), run_npm=False)


def test_initialize_rejects_nonempty_destination(tmp_path: Path) -> None:
    workspace = tmp_path / "paper"
    workspace.mkdir()
    (workspace / "notes.md").write_text("keep")
    with pytest.raises(UserError, match="must be empty"):
        init_module.initialize(workspace, run_npm=False)


def test_cli_init_routes_flags_and_prints_summary(tmp_path: Path, capsys) -> None:
    workspace = tmp_path / "cli-paper"
    assert main([
        "init", str(workspace), "--title", "CLI Paper", "--topic", "testing",
        "--tools", "claude,pi", "--remote", "local", "--no-npm",
    ]) == 0
    output = capsys.readouterr().out
    assert "Initialized papersmith workspace" in output
    assert config.load_workspace_config(workspace)["active_tools"] == ["claude", "pi"]


def test_generated_yaml_is_parseable_without_third_party_yaml(tmp_path: Path) -> None:
    workspace = tmp_path / "paper"
    init_module.initialize(workspace, run_npm=False)
    parsed = loads((workspace / "papersmith.yaml").read_text(encoding="utf-8"))
    assert parsed["execution_profiles"]["sweep_training"]["sharding"]["values"] == [
        42, 1337, 2026, 9999
    ]
