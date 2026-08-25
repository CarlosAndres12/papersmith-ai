"""Append-only execution ledger for workspace runs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import utc_timestamp


def path_for(workspace: Path) -> Path:
    return workspace / ".papersmith" / "runs_ledger.jsonl"


def append(workspace: Path, event: dict[str, Any]) -> None:
    path = path_for(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {"timestamp": utc_timestamp(), **event}
    with path.open("a", encoding="utf-8") as output:
        output.write(json.dumps(record, sort_keys=True) + "\n")


def read(workspace: Path) -> list[dict[str, Any]]:
    path = path_for(workspace)
    if not path.is_file():
        return []
    result: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            result.append({"status": "invalid"})
            continue
        if isinstance(value, dict):
            result.append(value)
    return result
