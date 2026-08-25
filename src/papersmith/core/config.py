"""Read and write workspace-owned JSON/YAML configuration."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..errors import UserError
from ..schema import validate_config_json, validate_papersmith_yaml
from ..yamllite import YamlliteError, loads


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_json(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise UserError(f"missing configuration file: {path}") from None
    except (OSError, json.JSONDecodeError) as exc:
        raise UserError(f"corrupted JSON file {path}: {exc}") from None
    if not isinstance(data, dict):
        raise UserError(f"configuration file {path} must contain a JSON object")
    return data


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def load_workspace_config(workspace: Path) -> dict:
    data = read_json(workspace / ".papersmith" / "config.json")
    return validate_config_json(data)


def load_papersmith_yaml(workspace: Path, *, require_compute: bool = True) -> dict:
    path = workspace / "papersmith.yaml"
    try:
        data = loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise UserError(f"missing workspace configuration: {path}") from None
    except (OSError, YamlliteError) as exc:
        raise UserError(f"invalid workspace YAML {path}: {exc}") from None
    return validate_papersmith_yaml(data, require_compute=require_compute)
