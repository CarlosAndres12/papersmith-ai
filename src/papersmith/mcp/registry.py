"""The MCP capability catalog.

Every exposed capability projects an existing CLI contract; nothing here is
domain logic. The catalog is the single source of truth for the tool surface,
and it also declares a *disposition* for every verb the CLI registers, so the
roster is total: a verb is exposed, or deferred by name, or declared out.

Adding a tool is a data edit here, never a new code path.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .bridge import ChildPlan, INGEST_TIMEOUT

#: The paper-writing CLI's own verb roster (``paper_cli.COMMANDS``).
PAPER_VERBS: tuple[str, ...] = (
    "scaffold",
    "status",
    "open",
    "substitute",
    "contract",
    "readiness",
    "order",
    "declare",
    "observe",
    "plan",
    "resolve",
    "bib",
    "validate",
    "write",
    "render",
    "place",
    "verify",
)

#: The orchestrator CLI's own command roster (``cli._REGISTRY``).
CLI_COMMANDS: tuple[str, ...] = (
    "init",
    "upgrade",
    "status",
    "ingest",
    "deliberate",
    "implement",
    "run",
    "remote",
    "target",
    "audit",
    "mcp",
)


class ToolRefusal(Exception):
    """A domain refusal decided before any child is spawned."""

    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(code)
        self.code = code
        self.detail = detail


@dataclass(frozen=True)
class Flag:
    """One argument a tool accepts, and how it becomes child argv."""

    name: str
    flag: str
    kind: str = "str"  # str | bool | list | int | enum
    required: bool = False
    choices: tuple[str, ...] | None = None
    path: bool = False
    description: str = ""


@dataclass(frozen=True)
class ToolSpec:
    name: str
    title: str
    description: str
    verb: str
    surface: str  # "cli" | "paper"
    annotations: dict[str, Any]
    input_schema: dict[str, Any]
    build: Callable[[dict[str, Any], Path], ChildPlan]
    precondition: Callable[[dict[str, Any], Path], None] | None = None
    result_json: bool = False

    def as_tool(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "title": self.title,
            "description": self.description,
            "inputSchema": self.input_schema,
            "annotations": dict(self.annotations),
        }


def tool_annotations(
    title: str,
    *,
    read_only: bool,
    destructive: bool,
    open_world: bool,
    idempotent: bool = False,
) -> dict[str, Any]:
    return {
        "title": title,
        "readOnlyHint": read_only,
        "destructiveHint": destructive,
        "idempotentHint": idempotent,
        "openWorldHint": open_world,
    }


def resolve_under(root: Path, raw: str) -> Path:
    """Resolve ``raw`` against ``root`` and refuse anything outside it."""
    candidate = Path(raw).expanduser()
    if not candidate.is_absolute():
        candidate = root / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        raise ToolRefusal(
            "WORKSPACE_ESCAPE", f"{resolved} is outside the bound workspace {root}"
        ) from None
    return resolved


# --------------------------------------------------------------------------- #
# workspace orchestration tools
# --------------------------------------------------------------------------- #


def _build_status(arguments: dict[str, Any], workspace: Path) -> ChildPlan:
    return ChildPlan("cli", ("status", "--json", str(workspace)))


def _build_audit(arguments: dict[str, Any], workspace: Path) -> ChildPlan:
    return ChildPlan("cli", ("audit", str(workspace), "--check-drift"))


def _build_target_list(arguments: dict[str, Any], workspace: Path) -> ChildPlan:
    return ChildPlan("cli", ("target", "list"))


def _build_target_check(arguments: dict[str, Any], workspace: Path) -> ChildPlan:
    tokens = ["target", "check"]
    name = arguments.get("name")
    if name:
        tokens.append(str(name))
    return ChildPlan("cli", tuple(tokens))


def _build_target_set(arguments: dict[str, Any], workspace: Path) -> ChildPlan:
    return ChildPlan("cli", ("target", "set", str(arguments["name"])))


def _refuse_npm(arguments: dict[str, Any], workspace: Path) -> None:
    return None


def _build_init(arguments: dict[str, Any], workspace: Path) -> ChildPlan:
    target = resolve_under(workspace, str(arguments["name"]))
    tokens = [
        "init",
        str(target),
        "--title",
        str(arguments.get("title", "Untitled Paper")),
        "--topic",
        str(arguments.get("topic", "unspecified")),
    ]
    remote = arguments.get("remote")
    if remote:
        tokens.extend(["--remote", str(remote)])
    tools = arguments.get("tools")
    if tools:
        tokens.extend(["--tools", str(tools)])
    if not arguments.get("allow_npm"):
        tokens.append("--no-npm")
    return ChildPlan("cli", tuple(tokens), timeout=600.0)


def _build_upgrade(arguments: dict[str, Any], workspace: Path) -> ChildPlan:
    tokens = ["upgrade", str(workspace)]
    tools = arguments.get("tools")
    if tools:
        tokens.extend(["--tools", str(tools)])
    if arguments.get("force"):
        tokens.append("--force")
    return ChildPlan("cli", tuple(tokens), timeout=600.0)


def _build_ingest(arguments: dict[str, Any], workspace: Path) -> ChildPlan:
    source = str(arguments["source"])
    if not source.startswith(("http://", "https://")):
        source = str(resolve_under(workspace, source))
    tokens = ["ingest", source, str(workspace)]
    if arguments.get("ocr"):
        tokens.append("--ocr")
    return ChildPlan("cli", tuple(tokens), timeout=INGEST_TIMEOUT)


# --------------------------------------------------------------------------- #
# paper-writing tools
# --------------------------------------------------------------------------- #


def _paper_child(
    verb: tuple[str, ...],
    flags: tuple[Flag, ...],
    arguments: dict[str, Any],
    workspace: Path,
    *,
    timeout: float | None = None,
) -> ChildPlan:
    script = workspace / "skills" / "paper-writing" / "scripts" / "paper_cli.py"
    argv = [str(script), *verb]
    for spec in flags:
        value = arguments.get(spec.name)
        if value is None:
            continue
        if spec.kind == "bool":
            if value:
                argv.append(spec.flag)
            continue
        if spec.kind == "list":
            for item in value:
                argv.extend([spec.flag, str(item)])
            continue
        text = str(value)
        if spec.path:
            text = str(resolve_under(workspace, text))
        argv.extend([spec.flag, text])
    return ChildPlan("paper", tuple(argv), timeout=timeout)


def _paper_builder(verb: tuple[str, ...], flags: tuple[Flag, ...]) -> Callable[..., ChildPlan]:
    def build(arguments: dict[str, Any], workspace: Path) -> ChildPlan:
        return _paper_child(verb, flags, arguments, workspace)

    return build


def _schema(flags: tuple[Flag, ...]) -> dict[str, Any]:
    properties: dict[str, Any] = {}
    required: list[str] = []
    for spec in flags:
        if spec.kind == "list":
            properties[spec.name] = {"type": "array", "items": {"type": "string"}}
        elif spec.kind == "bool":
            properties[spec.name] = {"type": "boolean"}
        elif spec.kind == "int":
            properties[spec.name] = {"type": "integer"}
        else:
            properties[spec.name] = {"type": "string"}
        if spec.choices:
            properties[spec.name]["enum"] = list(spec.choices)
        if spec.description:
            properties[spec.name]["description"] = spec.description
        if spec.required:
            required.append(spec.name)
    schema: dict[str, Any] = {
        "type": "object",
        "properties": properties,
        "additionalProperties": False,
    }
    if required:
        schema["required"] = required
    return schema


def _refuse_stdin_body(arguments: dict[str, Any], workspace: Path) -> None:
    if arguments.get("body") == "-":
        raise ToolRefusal(
            "STDIN_NOT_AVAILABLE_OVER_MCP",
            "the bound body must be a file path; '-' would read the JSON-RPC wire",
        )


def _no_args() -> dict[str, Any]:
    return {"type": "object", "properties": {}, "additionalProperties": False}


_PAPER_READONLY = (
    ToolSpec(
        name="papersmith.paper_status",
        title="Paper block table",
        description="Report the paper's block table, read-only.",
        verb="status",
        surface="paper",
        annotations=tool_annotations(
            "Paper block table", read_only=True, destructive=False, open_world=False, idempotent=True
        ),
        input_schema=_schema((Flag("paper", "--paper", path=True),)),
        build=_paper_builder(("status",), (Flag("paper", "--paper", path=True),)),
        result_json=True,
    ),
    ToolSpec(
        name="papersmith.paper_contract",
        title="Section contract",
        description="Validate the section corpus, or show one file's parsed header.",
        verb="contract",
        surface="paper",
        annotations=tool_annotations(
            "Section contract", read_only=True, destructive=False, open_world=False, idempotent=True
        ),
        input_schema=_schema(
            (Flag("sections", "--sections", path=True), Flag("file", "--file", description="one file's parsed header"))
        ),
        build=_paper_builder(
            ("contract",),
            (Flag("sections", "--sections", path=True), Flag("file", "--file")),
        ),
        result_json=True,
    ),
    ToolSpec(
        name="papersmith.paper_readiness",
        title="Per-block readiness",
        description="Per-block writable/blocked given satisfied facts and declarations.",
        verb="readiness",
        surface="paper",
        annotations=tool_annotations(
            "Per-block readiness", read_only=True, destructive=False, open_world=False, idempotent=True
        ),
        input_schema=_schema(
            (
                Flag("sections", "--sections", path=True),
                Flag("fact", "--fact", kind="list"),
                Flag("declaration", "--declaration", kind="list"),
            )
        ),
        build=_paper_builder(
            ("readiness",),
            (
                Flag("sections", "--sections", path=True),
                Flag("fact", "--fact", kind="list"),
                Flag("declaration", "--declaration", kind="list"),
            ),
        ),
        result_json=True,
    ),
    ToolSpec(
        name="papersmith.paper_order",
        title="Writing order",
        description="Derive the writing order from the block graph.",
        verb="order",
        surface="paper",
        annotations=tool_annotations(
            "Writing order", read_only=True, destructive=False, open_world=False, idempotent=True
        ),
        input_schema=_schema((Flag("sections", "--sections", path=True),)),
        build=_paper_builder(("order",), (Flag("sections", "--sections", path=True),)),
        result_json=True,
    ),
    ToolSpec(
        name="papersmith.paper_observe",
        title="Validate observer report",
        description=(
            "Validate an insumos-observer report against the observable-fact schema, read-only. "
            "Never calls declare and never writes anything."
        ),
        verb="observe",
        surface="paper",
        annotations=tool_annotations(
            "Validate observer report", read_only=True, destructive=False, open_world=False, idempotent=True
        ),
        input_schema=_schema(
            (Flag("report", "--report", required=True, path=True, description="observer JSON report"),)
        ),
        build=_paper_builder(("observe",), (Flag("report", "--report", required=True, path=True),)),
        result_json=True,
    ),
    ToolSpec(
        name="papersmith.paper_plan",
        title="Paper plan",
        description="Read-only: guidance classes, declaration/fact fill state, provenance state.",
        verb="plan",
        surface="paper",
        annotations=tool_annotations(
            "Paper plan", read_only=True, destructive=False, open_world=False, idempotent=True
        ),
        input_schema=_schema(
            (
                Flag("paper", "--paper", path=True),
                Flag("guidance", "--guidance", path=True),
                Flag("sections", "--sections", path=True),
            )
        ),
        build=_paper_builder(
            ("plan",),
            (
                Flag("paper", "--paper", path=True),
                Flag("guidance", "--guidance", path=True),
                Flag("sections", "--sections", path=True),
            ),
        ),
        result_json=True,
    ),
    ToolSpec(
        name="papersmith.paper_verify",
        title="Coupling verification",
        description=(
            "Read-only report over the cross-section couplings, citation integrity and "
            "contract currency."
        ),
        verb="verify",
        surface="paper",
        annotations=tool_annotations(
            "Coupling verification", read_only=True, destructive=False, open_world=False, idempotent=True
        ),
        input_schema=_schema(
            (Flag("paper", "--paper", path=True), Flag("sections", "--sections", path=True))
        ),
        build=_paper_builder(
            ("verify",),
            (Flag("paper", "--paper", path=True), Flag("sections", "--sections", path=True)),
        ),
        result_json=True,
    ),
)

_WORKSPACE_TOOLS = (
    ToolSpec(
        name="papersmith.workspace_status",
        title="Workspace status",
        description="Show comprehensive workspace status as machine-readable JSON.",
        verb="status",
        surface="cli",
        annotations=tool_annotations(
            "Workspace status", read_only=True, destructive=False, open_world=False, idempotent=True
        ),
        input_schema=_no_args(),
        build=_build_status,
        result_json=True,
    ),
    ToolSpec(
        name="papersmith.workspace_audit",
        title="Workspace audit",
        description=(
            "Audit workspace structure and consistency; reports generated-file drift as findings "
            "and never repairs it."
        ),
        verb="audit",
        surface="cli",
        annotations=tool_annotations(
            "Workspace audit", read_only=True, destructive=False, open_world=False, idempotent=True
        ),
        input_schema=_no_args(),
        build=_build_audit,
    ),
    ToolSpec(
        name="papersmith.target_list",
        title="List compute targets",
        description="List configured compute targets, marking the active one.",
        verb="target list",
        surface="cli",
        annotations=tool_annotations(
            "List compute targets", read_only=True, destructive=False, open_world=False, idempotent=True
        ),
        input_schema=_no_args(),
        build=_build_target_list,
    ),
    ToolSpec(
        name="papersmith.target_check",
        title="Check target connectivity",
        description=(
            "Test compute-target connectivity. Not hermetic: a remote-ssh target runs ssh "
            "and a kaggle target invokes the accounts helper."
        ),
        verb="target check",
        surface="cli",
        annotations=tool_annotations(
            "Check target connectivity", read_only=True, destructive=False, open_world=True, idempotent=True
        ),
        input_schema=_schema((Flag("name", "--name", description="target name; defaults to the active target"),)),
        build=_build_target_check,
    ),
    ToolSpec(
        name="papersmith.workspace_init",
        title="Initialize workspace",
        description=(
            "Create a standalone paper workspace under the bound root. npm install is skipped "
            "unless allow_npm is explicitly set."
        ),
        verb="init",
        surface="cli",
        annotations=tool_annotations(
            "Initialize workspace", read_only=False, destructive=False, open_world=True
        ),
        input_schema=_schema(
            (
                Flag("name", "name", required=True, description="new directory, under the bound root"),
                Flag("title", "--title"),
                Flag("topic", "--topic"),
                Flag("remote", "--remote", kind="enum", choices=("kaggle", "local", "slurm")),
                Flag("tools", "--tools", description="comma-separated runtimes"),
                Flag("allow_npm", "allow_npm", kind="bool", description="run the best-effort npm install"),
            )
        ),
        build=_build_init,
    ),
    ToolSpec(
        name="papersmith.workspace_upgrade",
        title="Upgrade workspace",
        description=(
            "Synchronize framework files in the workspace, preserving all research artifacts. "
            "force is never a default."
        ),
        verb="upgrade",
        surface="cli",
        annotations=tool_annotations(
            "Upgrade workspace", read_only=False, destructive=True, open_world=False
        ),
        input_schema=_schema(
            (
                Flag("tools", "--tools", description="replace active runtime generators"),
                Flag("force", "--force", kind="bool", description="force framework-file writes"),
            )
        ),
        build=_build_upgrade,
    ),
    ToolSpec(
        name="papersmith.target_set",
        title="Select compute target",
        description=(
            "Persist the default compute target in .papersmith/config.json. Idempotent:false — "
            "each call rewrites the config with a new updated_at."
        ),
        verb="target set",
        surface="cli",
        annotations=tool_annotations(
            "Select compute target", read_only=False, destructive=False, open_world=False
        ),
        input_schema=_schema((Flag("name", "name", required=True, description="configured target name"),)),
        build=_build_target_set,
    ),
    ToolSpec(
        name="papersmith.ingest_add",
        title="Ingest a reference",
        description=(
            "Ingest a PDF or literature URL into the workspace as Markdown plus figure files. "
            "Long-running and open-world; the first run may download model weights."
        ),
        verb="ingest",
        surface="cli",
        annotations=tool_annotations(
            "Ingest a reference", read_only=False, destructive=False, open_world=True
        ),
        input_schema=_schema(
            (
                Flag("source", "source", required=True, description="URL or workspace-relative PDF path"),
                Flag("ocr", "--ocr", kind="bool", description="balanced OCR-oriented extraction mode"),
            )
        ),
        build=_build_ingest,
    ),
)

TOOLS: tuple[ToolSpec, ...] = (*_WORKSPACE_TOOLS, *_PAPER_READONLY)

TOOLS_BY_NAME: dict[str, ToolSpec] = {spec.name: spec for spec in TOOLS}

#: Every CLI command and every paper verb has a declared disposition, so the
#: roster-drift test can prove the surface is deliberate rather than partial.
CLI_DISPOSITIONS: dict[str, str] = {
    "init": "exposed",
    "upgrade": "exposed",
    "status": "exposed",
    "ingest": "exposed",
    "audit": "exposed",
    "target": "exposed",
    "deliberate": "deferred",
    "implement": "deferred",
    "run": "deferred",
    "remote": "deferred",
    # The server host itself: never a tool it exposes.
    "mcp": "out",
}

PAPER_DISPOSITIONS: dict[str, str] = {
    verb: (
        "exposed"
        if verb in {"status", "contract", "readiness", "order", "observe", "plan", "verify"}
        else "deferred"
    )
    for verb in PAPER_VERBS
}
