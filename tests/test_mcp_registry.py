"""Capability-roster drift: the MCP surface stays deliberate, never partial."""

from __future__ import annotations

import argparse
import ast
from pathlib import Path

from papersmith.cli import build_parser
from papersmith.mcp import registry
from papersmith.mcp.server import catalog

REPO_ROOT = Path(__file__).resolve().parents[1]
PAPER_CLI = REPO_ROOT / "skills" / "paper-writing" / "scripts" / "paper_cli.py"


def _paper_cli_commands() -> tuple[str, ...]:
    tree = ast.parse(PAPER_CLI.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            getattr(target, "id", None) == "COMMANDS" for target in node.targets
        ):
            return tuple(ast.literal_eval(node.value))
    raise AssertionError("paper_cli.COMMANDS was not found")


def _cli_commands() -> tuple[str, ...]:
    parser = build_parser()
    action = next(
        candidate
        for candidate in parser._actions
        if isinstance(candidate, argparse._SubParsersAction)
    )
    return tuple(action.choices)


def test_registry_labels_match_the_real_paper_cli_roster() -> None:
    assert registry.PAPER_VERBS == _paper_cli_commands()


def test_registry_labels_match_the_real_cli_roster() -> None:
    assert set(registry.CLI_COMMANDS) == set(_cli_commands())


def test_every_paper_verb_has_a_disposition() -> None:
    assert set(registry.PAPER_DISPOSITIONS) == set(registry.PAPER_VERBS)


def test_every_cli_command_has_a_disposition() -> None:
    assert set(registry.CLI_DISPOSITIONS) == set(registry.CLI_COMMANDS)


def test_dispositions_use_only_the_declared_vocabulary() -> None:
    allowed = {"exposed", "deferred", "out"}
    assert set(registry.PAPER_DISPOSITIONS.values()) <= allowed
    assert set(registry.CLI_DISPOSITIONS.values()) <= allowed


def test_the_server_host_is_declared_out_not_exposed() -> None:
    assert registry.CLI_DISPOSITIONS["mcp"] == "out"
    assert not any(spec.verb == "mcp" for spec in registry.TOOLS)


def test_exposed_paper_tools_are_exactly_the_exposed_dispositions() -> None:
    exposed_tools = {spec.verb for spec in registry.TOOLS if spec.surface == "paper"}
    exposed_declared = {
        verb for verb, state in registry.PAPER_DISPOSITIONS.items() if state == "exposed"
    }
    assert exposed_tools == exposed_declared


def test_every_tool_name_is_namespaced_and_unique() -> None:
    names = [spec.name for spec in registry.TOOLS]
    assert len(names) == len(set(names))
    assert all(name.startswith("papersmith.") for name in names)


def test_every_input_schema_is_a_closed_object() -> None:
    for spec in registry.TOOLS:
        schema = spec.input_schema
        assert schema["type"] == "object", spec.name
        assert schema["additionalProperties"] is False, spec.name
        for required in schema.get("required", []):
            assert required in schema["properties"], spec.name


def test_every_tool_declares_all_four_annotation_hints() -> None:
    for spec in registry.TOOLS:
        for hint in ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"):
            assert isinstance(spec.annotations[hint], bool), (spec.name, hint)


def test_read_only_and_destructive_are_never_both_true() -> None:
    for spec in registry.TOOLS:
        if spec.annotations["readOnlyHint"]:
            assert spec.annotations["destructiveHint"] is False, spec.name


def test_target_check_is_open_world_despite_being_read_only() -> None:
    spec = registry.TOOLS_BY_NAME["papersmith.target_check"]
    assert spec.annotations["readOnlyHint"] is True
    assert spec.annotations["openWorldHint"] is True


def test_paper_validate_is_not_exposed_as_read_only() -> None:
    # C1: `validate` appends evidence and can substitute the block body.
    assert "papersmith.paper_validate" not in registry.TOOLS_BY_NAME
    assert registry.PAPER_DISPOSITIONS["validate"] == "deferred"


def test_paper_observe_is_exposed_read_only() -> None:
    spec = registry.TOOLS_BY_NAME["papersmith.paper_observe"]
    assert spec.annotations["readOnlyHint"] is True
    assert registry.PAPER_DISPOSITIONS["observe"] == "exposed"


def test_every_deferred_verb_is_named_never_silently_dropped() -> None:
    deferred = {
        verb for verb, state in registry.PAPER_DISPOSITIONS.items() if state == "deferred"
    } | {
        command
        for command, state in registry.CLI_DISPOSITIONS.items()
        if state == "deferred"
    }
    assert {"resolve", "render", "validate", "write", "substitute"} <= deferred
    assert {"deliberate", "implement", "run", "remote"} <= deferred


def test_catalog_tools_match_the_registry_order() -> None:
    assert [tool["name"] for tool in catalog()["tools"]] == [
        spec.name for spec in registry.TOOLS
    ]
