"""paper_resolve: stdlib-only `urllib` client for citation resolution and
metadata retrieval against OpenAlex, Crossref and arXiv. Keyless -- OpenAlex's
documented "polite pool" identity is a `mailto` contact, sourced from
`papersmith.yaml`'s `paper_writing.contact`, never a secret and never
hardcoded (`literature-search`, Requirement: Resolution Runs Through the CLI
Over Stdlib `urllib`). At most one retry, fixed 1s, only on transport error /
429 / 5xx, never on 404 (`design.md`, Decision 3).

This is also the one path that makes `paper-writing`'s CLI **not** offline
end to end (`proposal.md`, Approach) -- every call sits behind a role
`papersmith.yaml` can empty, and an unreachable endpoint is a named refusal,
never a silent empty result.

Public surface:

    OPENER                                    -- module-level urllib seam
    load_config(path=None)                    -> dict
    connectors_for_role(config, role)         -> list[str]
    require_role_connectors(config, role)     -> list[str]  (raises RESOLVER_ROLE_EMPTY / DISCOVERY_UNAVAILABLE)
    resolve_identifier(identifier, *, resolver, role, config) -> dict
    cache_metadata(paper_dir, result)         -> dict
    read_cached_metadata(paper_dir, digest)   -> dict | None
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_scaffold  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

#: Test seam (`design.md`, Decision 3, "Test seam"). Every outbound request
#: goes through this exact object; a test installs an opener whose `.open()`
#: raises `urllib.error.URLError` to prove the offline refusal path with no
#: live network call -- and switching it back proves the guard is load-
#: bearing rather than merely present.
OPENER: urllib.request.OpenerDirector = urllib.request.build_opener()

#: The three connectors this CLI can resolve against. Never PubMed or
#: bioRxiv -- this paper family is mathematics and machine learning
#: (`proposal.md`, Approach).
RESOLVERS: tuple[str, ...] = ("openalex", "crossref", "arxiv")

#: The connector roles `papersmith.yaml`'s `paper_writing.roles` maps.
#: `discovery` is read by this module only to validate configuration --
#: the actual discovery search never runs here, it runs through the agent's
#: MCP (`literature-search`, Requirement: Discovery Runs Through the Agent's
#: MCP).
ROLES: tuple[str, ...] = ("discovery", "resolution", "full-text")

_RETRY_DELAY_SECONDS = 1
_TIMEOUT_SECONDS = 10

_CONFIG_PATH = paper_scaffold.FORGE_ROOT / "papersmith.yaml"

_COMMENT_RE = re.compile(r"(?<!['\"])#.*$")


class _Unreachable(Exception):
    """Transport failure, or the retry budget is exhausted."""


class _NoSuchWork(Exception):
    """The endpoint answered, but names no matching work."""


# --- a minimal YAML-subset reader -------------------------------------
#
# `papersmith.yaml` stays readable by a human editor with comments, so this
# is deliberately NOT a general YAML parser (no flow style, no anchors, no
# multi-document streams) -- only what this repository's own config file
# ever uses: nested mappings, scalar strings, and block lists of scalar
# strings, indentation-delimited. `paper-writing` stays stdlib-only
# end to end (`SKILL.md`); pulling in a YAML library for one small,
# self-authored config block would cost the "no third-party dependency"
# property for the whole skill just to read six lines.

def _strip_comment(line: str) -> str:
    return _COMMENT_RE.sub("", line).rstrip()


def _indent(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _scalar(text: str):
    text = text.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in "\"'":
        return text[1:-1]
    return text


def _parse_block(lines: list[str], start: int, indent: int):
    if start < len(lines) and lines[start].lstrip().startswith("- "):
        items = []
        i = start
        while i < len(lines) and _indent(lines[i]) == indent and lines[i].lstrip().startswith("- "):
            items.append(_scalar(lines[i].lstrip()[2:]))
            i += 1
        return items, i

    result: dict = {}
    i = start
    while i < len(lines) and _indent(lines[i]) == indent:
        line = lines[i].strip()
        if ":" not in line:
            raise ValueError(f"expected 'key: value' at: {line!r}")
        key, _, rest = line.partition(":")
        key = key.strip()
        rest = rest.strip()
        if rest == "":
            j = i + 1
            if j < len(lines) and _indent(lines[j]) > indent:
                value, i = _parse_block(lines, j, _indent(lines[j]))
            else:
                value = {}
                i = j
        elif rest == "[]":
            value = []
            i += 1
        else:
            value = _scalar(rest)
            i += 1
        result[key] = value
    return result, i


def parse_yaml_subset(text: str) -> dict:
    """Parses the constrained shape above. Raises `ValueError` on anything
    it does not recognize -- fail closed, never a partial or best-effort
    read of a config file this whole skill trusts."""
    lines = [_strip_comment(raw) for raw in text.splitlines()]
    lines = [ln for ln in lines if ln.strip() != ""]
    if not lines:
        return {}
    value, _ = _parse_block(lines, 0, 0)
    if not isinstance(value, dict):
        raise ValueError("top level of the config must be a mapping")
    return value


def load_config(path: Path | None = None) -> dict:
    """Reads and parses `papersmith.yaml` (or `path`). Refuses
    `PAPERSMITH_CONFIG_UNREADABLE` (work-state) when the file is missing,
    not valid UTF-8, or does not match the constrained shape
    `parse_yaml_subset` understands."""
    target = path if path is not None else _CONFIG_PATH
    if not target.is_file():
        raise Refused("PAPERSMITH_CONFIG_UNREADABLE", f"{target} does not exist")
    try:
        text = target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise Refused("PAPERSMITH_CONFIG_UNREADABLE", f"{target}: not valid utf-8: {exc}")
    try:
        return parse_yaml_subset(text)
    except ValueError as exc:
        raise Refused("PAPERSMITH_CONFIG_UNREADABLE", f"{target}: {exc}")


def connectors_for_role(config: dict, role: str) -> list:
    if role not in ROLES:
        raise Refused("UNKNOWN_ROLE", f"{role!r} is not one of the declared roles {ROLES}")
    roles_cfg = (config.get("paper_writing") or {}).get("roles") or {}
    connectors = roles_cfg.get(role) or []
    return list(connectors) if isinstance(connectors, list) else [connectors]


def require_role_connectors(config: dict, role: str) -> list:
    """Refuses `DISCOVERY_UNAVAILABLE` for an empty `discovery` role, or
    `RESOLVER_ROLE_EMPTY` for an empty `resolution`/`full-text` role -- two
    different facts sharing no code, because "which role is empty" is part
    of what a caller needs to act on (`design.md`, Decision 3)."""
    connectors = connectors_for_role(config, role)
    if connectors:
        return connectors
    if role == "discovery":
        raise Refused("DISCOVERY_UNAVAILABLE", "no connector is configured for the discovery role")
    raise Refused("RESOLVER_ROLE_EMPTY", f"no connector is configured for the {role!r} role")


def _contact(config: dict) -> str:
    contact = (config.get("paper_writing") or {}).get("contact")
    return contact if isinstance(contact, str) else ""


def _user_agent(config: dict) -> str:
    contact = _contact(config)
    return f"papersmith-ai (mailto:{contact})" if contact else "papersmith-ai"


def _get(url: str, *, config: dict) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": _user_agent(config)})
    attempts = 0
    last_error: object = None
    while attempts < 2:
        attempts += 1
        try:
            with OPENER.open(request, timeout=_TIMEOUT_SECONDS) as response:
                return response.read()
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                raise _NoSuchWork(f"{url}: 404")
            if exc.code == 429 or 500 <= exc.code < 600:
                last_error = exc
                if attempts < 2:
                    time.sleep(_RETRY_DELAY_SECONDS)
                    continue
                raise _Unreachable(f"{url}: HTTP {exc.code} after {attempts} attempt(s)")
            raise _NoSuchWork(f"{url}: HTTP {exc.code}")
        except urllib.error.URLError as exc:
            last_error = exc
            if attempts < 2:
                time.sleep(_RETRY_DELAY_SECONDS)
                continue
            raise _Unreachable(f"{url}: {exc.reason} after {attempts} attempt(s)")
    raise _Unreachable(f"{url}: unreachable after {attempts} attempt(s): {last_error}")


def _openalex_url(doi: str, config: dict) -> str:
    base = f"https://api.openalex.org/works/https://doi.org/{doi}"
    contact = _contact(config)
    if contact:
        return base + "?" + urllib.parse.urlencode({"mailto": contact})
    return base


def _crossref_url(doi: str) -> str:
    return f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='')}"


def _arxiv_url(arxiv_id: str) -> str:
    return "http://export.arxiv.org/api/query?" + urllib.parse.urlencode({"id_list": arxiv_id})


def _parse_openalex(raw: bytes) -> dict:
    obj = json.loads(raw)
    return {"title": obj.get("title"), "doi": obj.get("doi"), "year": obj.get("publication_year")}


def _parse_crossref(raw: bytes) -> dict:
    obj = json.loads(raw)
    message = obj.get("message", {})
    titles = message.get("title") or []
    return {"title": titles[0] if titles else None, "doi": message.get("DOI"), "year": None}


def _parse_arxiv(raw: bytes) -> dict:
    namespace = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(raw)
    entry = root.find("atom:entry", namespace)
    if entry is None:
        raise _NoSuchWork("arXiv feed carried no <entry>")
    title_el = entry.find("atom:title", namespace)
    title = title_el.text.strip() if title_el is not None and title_el.text else None
    return {"title": title, "doi": None, "year": None}


_ENDPOINT_BUILDERS = {
    "openalex": lambda identifier, config: (_openalex_url(identifier, config), _parse_openalex),
    "crossref": lambda identifier, config: (_crossref_url(identifier), _parse_crossref),
    "arxiv": lambda identifier, config: (_arxiv_url(identifier), _parse_arxiv),
}


def resolve_identifier(identifier: str, *, resolver: str, role: str, config: dict) -> dict:
    """Resolves one identifier through one named resolver, honoring the
    role's configured connector list.

    Refuses `DISCOVERY_UNAVAILABLE`/`RESOLVER_ROLE_EMPTY` when the role has
    no configured connectors or does not include `resolver`,
    `RESOLVER_UNREACHABLE` (exit 2) when the transport never answers after
    one retry, and `IDENTIFIER_UNRESOLVED` when the endpoint answers but
    names no matching work (`literature-search`, Requirement: Unreachable
    Connectors Refuse By Name).
    """
    connectors = require_role_connectors(config, role)
    if resolver not in connectors or resolver not in _ENDPOINT_BUILDERS:
        raise Refused(
            "RESOLVER_ROLE_EMPTY",
            f"{resolver!r} is not a connector configured for role {role!r} ({connectors})",
        )
    url, parser = _ENDPOINT_BUILDERS[resolver](identifier, config)
    try:
        raw = _get(url, config=config)
    except _Unreachable as exc:
        raise Refused("RESOLVER_UNREACHABLE", str(exc))
    except _NoSuchWork as exc:
        raise Refused("IDENTIFIER_UNRESOLVED", str(exc))
    metadata = parser(raw)
    digest = hashlib.sha256(raw).hexdigest()
    return {
        "identifier": identifier,
        "resolver": resolver,
        "metadata_digest": digest,
        **metadata,
    }


def _metadata_path(paper_dir: Path, metadata_digest: str) -> Path:
    return paper_dir / ".paper-writing" / "metadata" / f"{metadata_digest}.json"


def cache_metadata(paper_dir: Path, result: dict) -> dict:
    """Caches a `resolve_identifier` result keyed by its own
    `metadata_digest` (`design.md`, Decision 4 -- `paper_bib.py`'s entry
    producer looks it back up by this same key)."""
    path = _metadata_path(paper_dir, result["metadata_digest"])
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return {"path": str(path)}


def read_cached_metadata(paper_dir: Path, metadata_digest: str) -> dict | None:
    path = _metadata_path(paper_dir, metadata_digest)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
