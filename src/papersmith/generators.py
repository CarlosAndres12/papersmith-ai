"""Deterministic runtime-document generators.

Claude's ``.claude/agents`` directory is the workspace SSOT. The generated
entrypoints only route each runtime to that SSOT and the workspace skills; they
intentionally do not fork agent instructions between harnesses.
"""

from __future__ import annotations

import ast
import warnings as _warnings
from pathlib import Path
from typing import Any

from .core.config import load_papersmith_yaml, load_workspace_config
from .errors import UserError
from .render import render_package_template

ALL_TOOLS = ("claude", "opencode", "pi", "antigravity")

#: Each runtime's *static* entrypoints. Used to answer "is this a known runtime?"
#: and, for a runtime a workspace does not declare, to name that runtime's
#: surplus static files in ``audit``. It is deliberately not a complete
#: rendered-path list and cannot become one: the dynamic
#: ``.opencode/commands/<name>.md`` and ``.claude/commands/<name>.md`` files are
#: one per discovered skill. :func:`render_files` is the single authority for
#: the path set.
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


def _is_dir(path: Path) -> bool:
    """``Path.is_dir`` treating an unstatable path as absent.

    ``Path.is_dir`` re-raises anything but ENOENT/ENOTDIR, so an unsearchable
    directory (EACCES) would escape the fail-soft contract of the collectors
    that call this.
    """
    try:
        return path.is_dir()
    except OSError:
        return False


def is_regular_file(path: Path) -> bool:
    """True when ``path`` is a regular file the framework may read.

    Two distinct hazards fold into ``False``. ``Path.is_file`` re-raises every
    errno but ENOENT/ENOTDIR/EBADF/ELOOP, so on CPython 3.11-3.13 an unsearchable
    directory (EACCES) would escape; and a non-regular but openable path — a FIFO,
    or a symlink to a character device — would make a subsequent read block
    forever. Both are "there is nothing to read here", not an error.

    This is the gate every managed-path read must pass before it opens a file.
    """
    try:
        return path.is_file()
    except OSError:
        return False


def collect_agents(workspace: Path) -> list[dict[str, str]]:
    """Read only agent names/descriptions from the canonical front matter.

    Fail-soft by contract, like :func:`collect_commands`: this runs inside every
    rendered-context derivation, so a damaged or unreadable agent file must not
    break ``status`` or ``audit``. Such a file is reported by name with an empty
    description instead of raising.
    """
    agents: list[dict[str, str]] = []
    agent_dir = workspace / ".claude" / "agents"
    if not _is_dir(agent_dir):
        return agents
    try:
        candidates = sorted(agent_dir.glob("*.md"))
    except OSError:
        return agents
    for path in candidates:
        if not is_regular_file(path):
            agents.append({"name": path.stem, "description": ""})
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            agents.append({"name": path.stem, "description": ""})
            continue
        lines = text.splitlines()
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


COMMAND_TOOLS = ("opencode", "claude")


def derive_command_description(source: str) -> str:
    """Collapse whitespace, then keep the first sentence.

    Command front matter wants a terse single-line description, while skill
    front matter carries a long ``Trigger: ...`` paragraph. This is the single
    definition of that source-to-derived transform: the emitted value and every
    assertion use it, never the raw multi-sentence source.
    """
    normalized = " ".join(source.split())
    for index, char in enumerate(normalized):
        if char in ".!?":
            following = normalized[index + 1:index + 2]
            if not following or following.isspace():
                return normalized[: index + 1]
    return normalized


def yaml_double_quote(value: str) -> str:
    """Emit ``value`` as a double-quoted YAML scalar."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _skill_command(skill_dir: Path) -> tuple[dict[str, str] | None, str | None]:
    """Return ``(entry, None)`` or ``(None, skip_reason)`` — never raises."""
    name = skill_dir.name
    skill_file = skill_dir / "SKILL.md"
    if not is_regular_file(skill_file):
        return None, "missing SKILL.md"
    try:
        lines = skill_file.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return None, "unreadable SKILL.md"
    if not lines or lines[0].strip() != "---":
        return None, "malformed front matter"
    metadata: dict[str, str] = {}
    closed = False
    for line in lines[1:]:
        if line.strip() == "---":
            closed = True
            break
        if ":" in line:
            key, value = line.split(":", 1)
            metadata[key.strip()] = _frontmatter_value(value)
    if not closed:
        return None, "malformed front matter"
    declared = metadata.get("name", "").strip()
    description = metadata.get("description", "").strip()
    if not declared:
        return None, "missing name"
    if declared != name:
        return None, f"name '{declared}' does not match directory '{name}'"
    if not description:
        return None, "missing description"
    return {"name": declared, "description": derive_command_description(description)}, None


def collect_commands(workspace: Path, *,
                     warnings: list[str] | None = None) -> list[dict[str, str]]:
    """Derive one slash command per top-level workspace skill.

    Fail-soft by contract: a skill whose ``SKILL.md`` is missing or whose
    ``name``/``description`` front matter is absent or malformed is skipped with
    a warning, never raised on. ``_``-prefixed directories are engine shelves and
    are skipped silently; nested ``SKILL.md`` files are never command targets.
    """
    commands: list[dict[str, str]] = []
    skills_dir = workspace / "skills"
    if not _is_dir(skills_dir):
        return commands
    try:
        skill_dirs = sorted(skills_dir.iterdir())
    except OSError:
        return commands
    skipped: list[str] = []
    for skill_dir in skill_dirs:
        if not _is_dir(skill_dir) or skill_dir.name.startswith("_"):
            continue
        entry, reason = _skill_command(skill_dir)
        if entry is None:
            skipped.append(f"skipping skill '{skill_dir.name}': {reason}")
            continue
        commands.append(entry)
    if skipped:
        if warnings is not None:
            warnings.extend(skipped)
        else:
            # One aggregated warning: Python's default filter dedupes by
            # (module, line), and every skip is emitted from this one line, so
            # per-skip warns would silently drop all but the first.
            _warnings.warn("\n".join(skipped), UserWarning, stacklevel=2)
    commands.sort(key=lambda item: item["name"])
    return commands


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


def workspace_tools(workspace: Path) -> tuple[str, ...]:
    """The tool set a workspace declares. The only place this is decided.

    Returns the validated ``active_tools`` from ``.papersmith/config.json``.
    Fail-soft by contract: when that file is absent, unreadable, corrupt, or
    missing/malformed in ``active_tools``, this resolver emits exactly one
    aggregated :class:`UserWarning` and falls back to :data:`ALL_TOOLS`. It never
    raises, so a consumer that only needs the declared set always proceeds.

    That guarantee covers this resolver alone. ``status`` and ``audit`` still
    require a valid workspace config and raise ``UserError`` without one, because
    they read it independently of this fallback.
    """
    config_path = workspace / ".papersmith" / "config.json"
    try:
        return tuple(load_workspace_config(workspace)["active_tools"])
    except (UserError, OSError, UnicodeDecodeError) as exc:
        _warnings.warn(
            f"could not read the declared tool set from {config_path} ({exc}); "
            f"assuming all runtimes: {', '.join(ALL_TOOLS)}",
            UserWarning,
            stacklevel=2,
        )
        return ALL_TOOLS


def _context_with_defaults(context: dict[str, Any]) -> dict[str, Any]:
    result = dict(context)
    result.setdefault("name", "paper-workspace")
    result.setdefault("title", result["name"])
    result.setdefault("topic", "unspecified")
    result.setdefault("version", "0.1.0")
    result.setdefault("tools", ", ".join(ALL_TOOLS))
    result.setdefault("agents", "- No specialized agents have been installed yet.")
    return result


def render_files(workspace: Path, context: dict[str, Any] | None = None,
                 tools: list[str] | tuple[str, ...] = ALL_TOOLS, *,
                 warnings: list[str] | None = None) -> dict[str, str]:
    ctx = _context_with_defaults(context or context_for_workspace(workspace))
    rendered: dict[str, str] = {".gitignore": render_package_template("gitignore.tpl", ctx)}
    templates = {
        "claude": ("CLAUDE.md", "claude.md.tpl"),
        "opencode": ("OPENCODE.md", "opencode.md.tpl"),
        "pi": ("PI.md", "pi.md.tpl"),
        "antigravity": (".antigravity/rules.md", "antigravity-rules.md.tpl"),
    }
    commands: list[dict[str, str]] | None = None
    if any(tool in COMMAND_TOOLS for tool in tools):
        commands = collect_commands(workspace, warnings=warnings)
    for tool in tools:
        if tool not in TOOL_OUTPUTS:
            raise UserError(f"unsupported runtime generator: {tool}")
        output, template = templates[tool]
        rendered[output] = render_package_template(template, ctx)
        if tool == "pi":
            rendered[".pi/gentle-ai/persona.json"] = render_package_template("persona.json.tpl", ctx)
        if tool == "opencode":
            rendered["opencode.json"] = render_package_template("opencode.json.tpl", ctx)
            rendered[".opencode/plugins/refuse-offpath-push.js"] = render_package_template(
                "opencode-plugin.js.tpl", ctx)
        if tool in COMMAND_TOOLS and commands:
            prefix = ".opencode/commands" if tool == "opencode" else ".claude/commands"
            for command in commands:
                command_ctx = dict(ctx)
                command_ctx.update({
                    "skill_name": command["name"],
                    "skill_path": f"skills/{command['name']}/SKILL.md",
                    "description_yaml": yaml_double_quote(command["description"]),
                })
                rendered[f"{prefix}/{command['name']}.md"] = render_package_template(
                    "command.md.tpl", command_ctx)
    return rendered


def apply_generated(workspace: Path, context: dict[str, Any] | None = None,
                    tools: list[str] | tuple[str, ...] = ALL_TOOLS, *,
                    warnings: list[str] | None = None) -> list[str]:
    changed: list[str] = []
    for relpath, content in render_files(workspace, context, tools, warnings=warnings).items():
        path = workspace / relpath
        encoded = content.encode("utf-8")
        if not path.is_file() or path.read_bytes() != encoded:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(encoded)
            changed.append(relpath)
    return changed


def check_generated(workspace: Path, context: dict[str, Any] | None = None,
                    tools: list[str] | tuple[str, ...] = ALL_TOOLS, *,
                    warnings: list[str] | None = None) -> list[str]:
    drifted: list[str] = []
    for relpath, content in render_files(workspace, context, tools, warnings=warnings).items():
        path = workspace / relpath
        if not is_regular_file(path) or path.read_bytes() != content.encode("utf-8"):
            drifted.append(relpath)
    return drifted
