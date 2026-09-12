"""Change `the-second-skill-the-seam-was-for`, slice A1: this skill's own
profile resolves through the SAME shared resolver
(`_core/implementation/impl_domain_profile.py`) the sibling
(`proposal-implementation`) already proves generically. This file proves the
SECOND host, not the resolver again -- one refusal case per validated leaf
(mirroring `tests/test_implementation_profile.py`'s
`DomainFieldLeafRefusalTests`, structurally, never a shared import), the
launcher's byte-equality to the sibling's (design.md D4/M4, mutation X3),
and the citation pattern's exactly-three-group shape (task 1.4, M2).
"""

from __future__ import annotations

import copy
import importlib.util
import itertools
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Mapping

FORGE = Path(__file__).resolve().parents[1]
SKILL_DIR = FORGE / ".claude" / "skills" / "experimental-implementation"
PROFILE_FILE = SKILL_DIR / "impl_profile.py"
LAUNCHER = SKILL_DIR / "scripts" / "implementation_cli.py"
SIBLING_LAUNCHER = (
    FORGE / ".claude" / "skills" / "proposal-implementation" / "scripts"
    / "implementation_cli.py")
RESOLVER = FORGE / ".claude/skills/_core/implementation/impl_domain_profile.py"

_counter = itertools.count()


def _load_module(path: Path, prefix: str):
    """A fresh, uncached load -- never the plain `import` statement, which
    would share `sys.modules` state with every other test file that has
    already imported the same-named module under a different profile."""
    name = f"{prefix}_{next(_counter)}"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


def _real_profile() -> Mapping:
    return _load_module(PROFILE_FILE, "experimental_impl_profile_probe").PROFILE


def _resolve_with(profile_file: Path):
    """A fresh, uncached load of the RESOLVER under a controlled env --
    the resolver validates and raises at import time."""
    import os
    import contextlib

    @contextlib.contextmanager
    def _env(value):
        had = "IMPLEMENTATION_DOMAIN_PROFILE" in os.environ
        original = os.environ.get("IMPLEMENTATION_DOMAIN_PROFILE")
        os.environ["IMPLEMENTATION_DOMAIN_PROFILE"] = value
        try:
            yield
        finally:
            if had:
                os.environ["IMPLEMENTATION_DOMAIN_PROFILE"] = original
            else:
                os.environ.pop("IMPLEMENTATION_DOMAIN_PROFILE", None)

    name = f"experimental_impl_resolver_probe_{next(_counter)}"
    spec = importlib.util.spec_from_file_location(name, RESOLVER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        with _env(str(profile_file)):
            spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


def _to_source(value) -> str:
    if isinstance(value, Mapping):
        items = ", ".join(f"{k!r}: {_to_source(v)}" for k, v in value.items())
        return "{" + items + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_to_source(v) for v in value) + "]"
    if isinstance(value, Path):
        return f"Path({str(value)!r})"
    return repr(value)


#: The sixteen validated leaves this skill's profile must declare (design.md
#: D2), named the same way `test_implementation_profile.py::_CUT2_LEAVES`
#: names them, `documents[0].*` indexed rather than flat (Cut 3, D4).
_LEAVES: tuple[str, ...] = (
    "kit.root",
    "cli.path",
    "provenance.claim_key",
    "provenance.authored_init_sentence",
    "findings.locus_key",
    "findings.remedy_locus_key",
    "findings.notation_keys",
    "findings.citation_pattern",
    "vocabulary.subject_singular",
    "vocabulary.subject_plural",
    "vocabulary.subject_singular_es",
    "vocabulary.subject_plural_es",
    "vocabulary.subject_collective",
    "vocabulary.subject_collective_es",
    "vocabulary.artifact_noun",
    "vocabulary.names",
    "documents[0].directory",
    "documents[0].label",
)

_INDEXED_LEAF_RE = re.compile(r"^documents\[(\d+)\]\.(directory|label)$")


def _without_leaf(profile: dict, dotted: str) -> dict:
    clone = copy.deepcopy(profile)
    indexed = _INDEXED_LEAF_RE.match(dotted)
    if indexed:
        index, key = int(indexed.group(1)), indexed.group(2)
        del clone["documents"][index][key]
        return clone
    section, key = dotted.split(".", 1)
    del clone[section][key]
    return clone


class LeafRefusalTests(unittest.TestCase):
    """Mutation X1 (design.md): delete each of the sixteen validated leaves
    one at a time -- the resolver refuses `..._INCOMPLETE` naming exactly
    that leaf, never its section alone."""

    def _tmp_dir(self) -> Path:
        tmp_dir = Path(tempfile.mkdtemp(prefix="experimental-impl-leaf-"))
        self.addCleanup(__import__("shutil").rmtree, tmp_dir, ignore_errors=True)
        return tmp_dir

    def test_each_validated_leaf_refuses_incomplete_and_names_itself(self):
        full = dict(_real_profile())
        for dotted in _LEAVES:
            with self.subTest(leaf=dotted):
                tmp_dir = self._tmp_dir()
                incomplete = _without_leaf(full, dotted)
                profile_file = tmp_dir / "impl_profile.py"
                profile_file.write_text(
                    "from pathlib import Path\n"
                    f"PROFILE = {_to_source(incomplete)}\n",
                    encoding="utf-8")
                with self.assertRaises(RuntimeError) as ctx:
                    _resolve_with(profile_file)
                message = str(ctx.exception)
                self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE", message)
                self.assertIn(dotted, message)

    def test_the_real_profile_resolves_cleanly(self):
        """The positive control every refusal case above is a mutation OF."""
        module = _resolve_with(PROFILE_FILE)
        self.assertEqual(module.PROFILE["provenance"]["claim_key"], "experiments")
        self.assertEqual(module.PROFILE["documents"][0]["label"], "experiments")


class CitationPatternGroupCountTests(unittest.TestCase):
    """Task 1.4 (M2, design.md): `_impact_class` reads `match.group(1) or
    match.group(2) or match.group(3)` -- a two-group pattern raises
    `IndexError`, a four-group pattern silently drops the fourth. Scoped to
    THIS profile's own pattern only; validating `_resolve()`/`_impact_class`
    itself is out of scope (D2/M2, deferred to change C per design.md Q3)."""

    def test_this_profiles_citation_pattern_compiles_to_exactly_three_groups(self):
        pattern = _real_profile()["findings"]["citation_pattern"]
        compiled = re.compile(pattern)
        self.assertEqual(compiled.groups, 3)


class LauncherByteEqualityTests(unittest.TestCase):
    """Design.md D4/M4: a byte-for-byte copy of the sibling's launcher --
    not a symlink, not an import. Mutation X3: flip one byte, confirm this
    test fails, restore."""

    def test_the_launcher_is_byte_identical_to_the_siblings(self):
        self.assertEqual(
            LAUNCHER.read_bytes(), SIBLING_LAUNCHER.read_bytes(),
            "the launcher must be a byte-for-byte copy of the sibling's own "
            "launcher (design.md D4): every value in it is derived from "
            "Path(__file__).resolve(), so a byte-identical copy placed here "
            "resolves to THIS skill's own profile")


if __name__ == "__main__":
    unittest.main()
