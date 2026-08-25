"""Upgrade tests for source synchronization and protected research state."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from papersmith.cli import main
from papersmith.core import config, init as init_module, manifest, upgrade as upgrade_module
from papersmith.errors import UserError


def _workspace(tmp_path: Path) -> Path:
    workspace = tmp_path / "paper"
    init_module.initialize(workspace, run_npm=False)
    return workspace


def test_upgrade_restores_framework_files_and_preserves_research(
    tmp_path: Path,
) -> None:
    workspace = _workspace(tmp_path)
    skill = workspace / "skills/paper-ingestion/SKILL.md"
    original_skill = skill.read_bytes()
    skill.write_bytes(b"user accidentally changed a framework file\n")

    readme = workspace / "README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + "\nResearch note.\n", encoding="utf-8")
    yaml = workspace / "papersmith.yaml"
    original_yaml = yaml.read_bytes()
    yaml.write_bytes(original_yaml + b"\n# user configuration comment\n")
    research = workspace / "guidance/paper-guide/local-note.md"
    research.write_text("local guidance", encoding="utf-8")
    agent = workspace / ".claude/agents/paper-ingestion.md"
    agent.write_text(agent.read_text(encoding="utf-8") + "\nlocal note\n", encoding="utf-8")

    result = upgrade_module.upgrade(workspace)

    assert skill.read_bytes() == original_skill
    assert readme.read_text(encoding="utf-8").endswith("Research note.\n")
    assert yaml.read_bytes() == original_yaml + b"\n# user configuration comment\n"
    assert research.read_text(encoding="utf-8") == "local guidance"
    assert not agent.read_text(encoding="utf-8").endswith("local note\n")
    assert "skills/paper-ingestion/SKILL.md" in result["changed_files"]
    assert "README.md" not in result["changed_files"]
    assert "papersmith.yaml" not in result["changed_files"]
    assert "guidance/paper-guide/local-note.md" not in result["changed_files"]

    stored = json.loads((workspace / ".papersmith/manifest.json").read_text())
    expected = manifest.workspace_framework_files(workspace, Path(__file__).parents[1])
    assert stored["files"] == expected


def test_upgrade_rebuilds_generated_projections(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    generated = workspace / "CLAUDE.md"
    generated.write_text("drift\n", encoding="utf-8")
    result = upgrade_module.upgrade(workspace)
    assert generated.read_text(encoding="utf-8") != "drift\n"
    assert "CLAUDE.md" in result["changed_files"]


def test_upgrade_tools_updates_active_tool_configuration(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    result = upgrade_module.upgrade(workspace, tools=("claude", "pi"))
    assert result["active_tools"] == ["claude", "pi"]
    assert config.load_workspace_config(workspace)["active_tools"] == ["claude", "pi"]
    assert (workspace / "CLAUDE.md").is_file()
    assert (workspace / "PI.md").is_file()


def test_upgrade_refuses_missing_manifest(tmp_path: Path) -> None:
    with pytest.raises(UserError, match="not a papersmith workspace"):
        upgrade_module.upgrade(tmp_path / "not-a-workspace")


def test_upgrade_refuses_corrupted_manifest(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    (workspace / ".papersmith/manifest.json").write_text("not json", encoding="utf-8")
    with pytest.raises(UserError, match="corrupted manifest"):
        upgrade_module.upgrade(workspace)


def test_upgrade_refreshes_version_from_a_new_kit(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    workspace = _workspace(tmp_path)
    kit = tmp_path / "kit-0.2"
    for relpath, content in {
        "skills/paper-ingestion/SKILL.md": "# upgraded skill\n",
        "scripts/setup_env.py": "# upgraded env\n",
        ".claude/agents/paper-ingestion.md": "---\nname: paper-ingestion\ndescription: upgraded\n---\n",
        "package.json": '{"version": "0.2.0"}\n',
        "requirements.txt": "kagglesdk==0.1.37\n",
        "CLAUDE.md": "# kit marker\n",
    }.items():
        path = kit / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    monkeypatch.setenv("PAPERSMITH_KIT_ROOT", str(kit))

    result = upgrade_module.upgrade(workspace)

    assert result["version"] == "0.2.0"
    assert (workspace / ".papersmith/version").read_text() == "0.2.0\n"
    assert (workspace / "skills/paper-ingestion/SKILL.md").read_text() == "# upgraded skill\n"
    stored = json.loads((workspace / ".papersmith/manifest.json").read_text())
    assert stored["version"] == "0.2.0"


def test_force_reports_framework_writes_even_when_content_matches(tmp_path: Path) -> None:
    workspace = _workspace(tmp_path)
    result = upgrade_module.upgrade(workspace, force=True)
    assert "skills/paper-ingestion/SKILL.md" in result["changed_files"]
    assert "package.json" in result["changed_files"]


def test_cli_upgrade_routes_directory_and_flags(tmp_path: Path, capsys) -> None:
    workspace = _workspace(tmp_path)
    assert main(["upgrade", str(workspace), "--tools", "claude,pi", "--force"]) == 0
    output = capsys.readouterr().out
    assert "Upgraded papersmith workspace" in output
    assert config.load_workspace_config(workspace)["active_tools"] == ["claude", "pi"]
