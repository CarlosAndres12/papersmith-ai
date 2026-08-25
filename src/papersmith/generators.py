"""Deterministic runtime-document generators.

Claude's ``.claude/agents`` directory is the workspace SSOT. The generated
entrypoints only route each runtime to that SSOT and the workspace skills; they
intentionally do not fork agent instructions between harnesses.
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from .core.config import load_papersmith_yaml, load_workspace_config
from .errors import UserError
from .render import render_package_template

ALL_TOOLS = ("claude", "opencode", "pi", "antigravity")
TOOL_OUTPUTS = {
    "claude": ("CLAUDE.md",),
    "opencode": ("OPENCODE.md",),
    "pi": ("PI.md", ".pi/gentle-ai/persona.json"),
    "antigravity": (".antigravity/rules.md",),
}


def _frontmatter_value(value: str) -> str:
    value = value.strip()
    if value.startswith('"') or value.startswith("'"):
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError):
            return value.strip("'\"")
        return str(parsed)
    return value


def collect_agents(workspace: Path) -> list[dict[str, str]]:
    """Read only agent names/descriptions from the canonical front matter."""
    agents: list[dict[str, str]] = []
    agent_dir = workspace / ".claude" / "agents"
    if not agent_dir.is_dir():
        return agents
    for path in sorted(agent_dir.glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        if not lines or lines[0].strip() != "---":
            agents.append({"name": path.stem, "description": ""})
            continue
        metadata: dict[str, str] = {}
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = _frontmatter_value(value)
        agents.append({
            "name": metadata.get("name", path.stem),
            "description": metadata.get("description", ""),
        })
    return agents


def _agents_block(workspace: Path) -> str:
    agents = collect_agents(workspace)
    if not agents:
        return "- No specialized agents have been installed yet."
    return "\n".join(
        f"- `{agent['name']}`{(' — ' + agent['description']) if agent['description'] else ''}"
        for agent in agents
    )


def context_for_workspace(workspace: Path) -> dict[str, Any]:
    config = load_workspace_config(workspace)
    yaml = load_papersmith_yaml(workspace)
    version_path = workspace / ".papersmith" / "version"
    try:
        version = version_path.read_text(encoding="utf-8").strip()
    except OSError:
        version = str(yaml.get("version", "1"))
    return {
        "name": yaml.get("name", config["project_name"]),
        "title": yaml.get("title", config["project_name"]),
        "topic": yaml.get("topic", "unspecified"),
        "version": version,
        "tools": ", ".join(config["active_tools"]),
        "agents": _agents_block(workspace),
    }


def _context_with_defaults(context: dict[str, Any]) -> dict[str, Any]:
    result = dict(context)
    result.setdefault("name", "paper-workspace")
    result.setdefault("title", result["name"])
    result.setdefault("topic", "unspecified")
    result.setdefault("version", "0.1.0")
    result.setdefault("tools", ", ".join(ALL_TOOLS))
    result.setdefault("agents", "- No specialized agents have been installed yet.")
    return result


def output_paths(tools: list[str] | tuple[str, ...] = ALL_TOOLS) -> list[str]:
    paths = [".gitignore"]
    for tool in tools:
        paths.extend(TOOL_OUTPUTS[tool])
    return list(dict.fromkeys(paths))


def render_files(workspace: Path, context: dict[str, Any] | None = None,
                 tools: list[str] | tuple[str, ...] = ALL_TOOLS) -> dict[str, str]:
    ctx = _context_with_defaults(context or context_for_workspace(workspace))
    rendered: dict[str, str] = {".gitignore": render_package_template("gitignore.tpl", ctx)}
    templates = {
        "claude": ("CLAUDE.md", "claude.md.tpl"),
        "opencode": ("OPENCODE.md", "opencode.md.tpl"),
        "pi": ("PI.md", "pi.md.tpl"),
        "antigravity": (".antigravity/rules.md", "antigravity-rules.md.tpl"),
    }
    for tool in tools:
        if tool not in TOOL_OUTPUTS:
            raise UserError(f"unsupported runtime generator: {tool}")
        output, template = templates[tool]
        rendered[output] = render_package_template(template, ctx)
        if tool == "pi":
            rendered[".pi/gentle-ai/persona.json"] = render_package_template("persona.json.tpl", ctx)
    return rendered


def apply_generated(workspace: Path, context: dict[str, Any] | None = None,
                    tools: list[str] | tuple[str, ...] = ALL_TOOLS) -> list[str]:
    changed: list[str] = []
    for relpath, content in render_files(workspace, context, tools).items():
        path = workspace / relpath
        encoded = content.encode("utf-8")
        if not path.is_file() or path.read_bytes() != encoded:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded)
            changed.append(relpath)
    return changed


def check_generated(workspace: Path, context: dict[str, Any] | None = None,
                    tools: list[str] | tuple[str, ...] = ALL_TOOLS) -> list[str]:
    drifted: list[str] = []
    for relpath, content in render_files(workspace, context, tools).items():
        path = workspace / relpath
        if not path.is_file() or path.read_bytes() != content.encode("utf-8"):
            drifted.append(relpath)
    return drifted
