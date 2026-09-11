"""Normalize nondeterministic bytes out of captured stdout before digesting.

Six sources, per proposal.md/design.md D4 — `_now_iso8601()`, absolute
`str(target)`, `CLI_INVOCATION`, `--session` ids, git shas,
`source_digest`/`suite_digest` — four erased (N1, N2, N3, N5), two PINNED
instead (N4 `--session`, N6 content digests): erasing them would blind the
seal to exactly the thing it exists to catch (design.md D4's own table).

`NORMALIZERS` is an ORDERED tuple, and the order is load-bearing:
`shlex.quote(sys.executable)`'s own absolute path resolves under
`FORGE_ROOT` in this repo (the venv lives at `<repo>/.venv/bin/python3`), so
N2 rewriting the forge prefix first would mangle N3's exact-match target
before N3 ever runs. N3 must run before N2.
"""

from __future__ import annotations

import dataclasses
import re
import shlex
import sys
from pathlib import Path


@dataclasses.dataclass(frozen=True)
class Roots:
    """The four known absolute roots N2 replaces, longest-first. `target` is
    the CURRENT case's own resolved scratch copy — a fresh value per case,
    never the corpus's master fixture path."""

    target: Path
    corpus: Path
    forge: Path
    proposals: Path


#: N3 `cli_invocation` — the interpreter token ONLY, never the whole
#: `CLI_INVOCATION` value. **Design correction, applied before capture,
#: 2026-09-11**: the original shape erased `str(CLI_PATH)` along with the
#: interpreter, which would hide Cut 1's single silent failure mode
#: (`CLI_PATH` resolving to the engine instead of the launcher — measurement
#: §C). Narrowed so `str(CLI_PATH)` survives into N2's `<FORGE>/...`
#: rewrite, where `test_the_sealed_cli_path_names_the_launcher` pins it
#: directly (the same idiom N4 uses for `--session`).
def n3_cli_invocation(text: str, roots: Roots) -> str:
    interpreter_token = shlex.quote(sys.executable or "python3")
    return text.replace(interpreter_token, "<PYTHON>")


#: N2 `absolute_roots` — exact substring replacement, longest-first, of the
#: four known roots. Longest-first so a `target` path that happens to sit
#: under `corpus` (it does — every fixture and every case's scratch copy
#: lives under the corpus's own tmp root) is replaced by its own, more
#: specific placeholder before the shorter `corpus` replacement would
#: otherwise eat part of it.
def n2_absolute_roots(text: str, roots: Roots) -> str:
    replacements = [
        (str(roots.target), "<TARGET>"),
        (str(roots.proposals), "<PROPOSALS>"),
        (str(roots.corpus), "<CORPUS>"),
        (str(roots.forge), "<FORGE>"),
    ]
    replacements.sort(key=lambda pair: len(pair[0]), reverse=True)
    for needle, placeholder in replacements:
        if needle:
            text = text.replace(needle, placeholder)
    return text


#: N1 `iso8601_timestamps` — every `_now_iso8601()` stamp this CLI ever
#: writes is `YYYY-MM-DDTHH:MM:SSZ` (UTC, no microseconds, no offset).
_ISO8601_RE = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")


def n1_iso8601_timestamps(text: str, roots: Roots) -> str:
    return _ISO8601_RE.sub("<TS>", text)


#: N5 `git_shas` — exactly 40 hex characters, word-bounded so a 64-hex
#: `sha256` (`fileSha256`, `revisionSha256`, `digest`, ...) is never
#: partially matched inside a longer hex run. Belt-and-braces: the corpus
#: already commits under pinned identity and pinned dates, so its OWN shas
#: are already reproducible without this — this is for any OTHER 40-hex
#: value the CLI happens to echo (a real git sha read from a target).
_GIT_SHA_RE = re.compile(r"\b[0-9a-f]{40}\b")


def n5_git_shas(text: str, roots: Roots) -> str:
    return _GIT_SHA_RE.sub("<GITSHA>", text)


#: Order pinned by `test_normalizer_order_is_pinned`: N3 before N2 (see
#: module docstring). N1 and N5 target disjoint character classes from N2's
#: placeholders and from each other, so their relative order does not
#: matter — kept last for readability, not for correctness.
NORMALIZERS: tuple = (n3_cli_invocation, n2_absolute_roots, n1_iso8601_timestamps,
                      n5_git_shas)


def normalize(text: str, roots: Roots) -> str:
    """Fold `NORMALIZERS` left to right over `text`."""
    for normalizer in NORMALIZERS:
        text = normalizer(text, roots)
    return text
