"""Cut 1 (`the-engine-leaves-its-skill`): the domain-profile resolver the
moved engine fails closed without, and the launcher's own promise that it
exposes none of the engine's attributes.

Mirrors `.claude/skills/_core/deliberation/engine/domain-profile.ts`'s own
resolver-property tests, ported to the shape design.md D3 settles on for
Python: `IMPLEMENTATION_DOMAIN_PROFILE`, six named refusal codes,
`ImplementationProfileError(RuntimeError)` -- never `Refused`/`NameRefused`,
because `reachable_refusal_codes()` (`tests/test_proposal_implementation.py`)
walks every `*.py` under `_core/implementation/` for exactly those two
constructors and pins `len(...) == 112`; six `Refused`s in a core module
would move that unrelated pin.

Phase 1 (RED first, tasks.md): at the moment this file is first run, neither
`impl_domain_profile.py` nor the launcher's own `??=`-style default exist yet
-- every test below is expected to fail on collection/execution, not pass.
"""

from __future__ import annotations

import contextlib
import copy
import importlib.util
import itertools
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Mapping

FORGE = Path(__file__).resolve().parents[1]
RESOLVER = FORGE / ".claude/skills/_core/implementation/impl_domain_profile.py"
LAUNCHER = FORGE / ".claude/skills/proposal-implementation/scripts/implementation_cli.py"

_ENV_VAR = "IMPLEMENTATION_DOMAIN_PROFILE"

#: A minimal, syntactically complete `objective` literal for fixture
#: profiles that are not themselves testing `objective`'s own validation --
#: real content is irrelevant to those tests, only completeness is, and this
#: keeps every unrelated refusal-code fixture from tripping the (now
#: required) `objective` check before it ever reaches the code under test.
_VALID_OBJECTIVE_SRC = (
    "{'purpose': 'p', 'arrival': 'a', 'humanStops': ['h'], "
    "'stages': [{'stage': 's', 'establishes': 'e', 'behindWhen': 'b'}]}")

def _cut2_fields_src(tmp_dir: Path) -> str:
    """Cut 2 (`the-domain-crosses-the-seam`, design.md D1) grew the
    resolver's required-leaf set past Cut 1's `kit`/`cli`/`objective`. This
    is that growth as a literal source fragment, spliced into every
    hand-written Cut-1 fixture below that is testing `kit`/`cli`/`objective`
    specifically and would otherwise trip `..._INCOMPLETE` on an unrelated
    missing Cut-2 leaf before ever reaching the behaviour under test."""
    documents_dir = tmp_dir / "proposals"
    return (
        "'provenance': {'claim_key': 'equations', "
        "'authored_init_sentence': 'x'}, "
        "'findings': {'locus_key': 'equations', "
        "'remedy_locus_key': 'remedy_equations', "
        "'notation_keys': {'locus': 'equations', "
        "'remedyLocus': 'remedyEquations', 'unknown': 'unknownEquations'}, "
        "'citation_pattern': 'x'}, "
        "'vocabulary': {'subject_singular': 'equation', "
        "'subject_plural': 'equations', 'subject_singular_es': 'ecuación', "
        "'subject_plural_es': 'ecuaciones', "
        "'subject_collective': 'mathematics', "
        "'subject_collective_es': 'matemática', "
        "'artifact_noun': 'formulation', "
        "'names': ['equation', 'equations', 'ecuación', 'ecuaciones', "
        "'mathematics', 'matemática', 'formulation']}, "
        f"'documents': {{'directory': Path({str(documents_dir)!r}), "
        "'label': 'proposal'}")


_counter = itertools.count()


@contextlib.contextmanager
def _env(value):
    """Sets or removes `IMPLEMENTATION_DOMAIN_PROFILE` for the block, then
    restores whatever this process had before -- never `patch.dict`, which
    cannot express "absent" as cleanly as an explicit pop/restore pair."""
    had = _ENV_VAR in os.environ
    original = os.environ.get(_ENV_VAR)
    if value is None:
        os.environ.pop(_ENV_VAR, None)
    else:
        os.environ[_ENV_VAR] = value
    try:
        yield
    finally:
        if had:
            os.environ[_ENV_VAR] = original
        else:
            os.environ.pop(_ENV_VAR, None)


def _fresh_resolver_load(env_value):
    """One fresh, uncached `exec_module` of the resolver under a controlled
    env -- the resolver validates and raises at IMPORT time (module-level
    `PROFILE = _resolve()`), so this either returns a live module or lets
    the resolver's own exception propagate to the caller."""
    name = f"impl_domain_profile_probe_{next(_counter)}"
    spec = importlib.util.spec_from_file_location(name, RESOLVER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        with _env(env_value):
            spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


class ProfileResolverRefusalTests(unittest.TestCase):
    """The six named refusal codes (design.md D3), each proven by one
    mutation of the profile-resolution inputs -- never asserted by shape
    alone. In-process, fresh `importlib` per case, exactly `CoreNamesNoDomain
    Tests._cli_module()`'s own pattern."""

    def _profile_file(self, tmp_dir: Path, body: str) -> Path:
        profile_file = tmp_dir / "impl_profile.py"
        profile_file.write_text(body, encoding="utf-8")
        return profile_file

    def _tmp_dir(self) -> Path:
        tmp_dir = Path(tempfile.mkdtemp(prefix="impl-profile-refusal-"))
        self.addCleanup(shutil.rmtree, tmp_dir, ignore_errors=True)
        return tmp_dir

    def test_unset_refuses_required(self):
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(None)
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_REQUIRED", str(ctx.exception))

    def test_empty_string_refuses_required(self):
        """Empty is not merely falsy-and-ignored -- it is refused under the
        same code as unset, never silently treated as "no override"."""
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load("")
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_REQUIRED", str(ctx.exception))

    def test_relative_path_refuses_not_absolute(self):
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load("relative/impl_profile.py")
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_NOT_ABSOLUTE", str(ctx.exception))

    def test_absent_file_refuses_unreadable(self):
        tmp_dir = self._tmp_dir()
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(tmp_dir / "does-not-exist.py"))
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_UNREADABLE", str(ctx.exception))

    def test_a_file_that_raises_on_exec_refuses_unreadable(self):
        """`spec_from_file_location` succeeding is not the same as the
        module executing cleanly -- a profile file that itself raises must
        be caught and re-raised under the resolver's own named code, never
        left as the profile file's raw exception."""
        tmp_dir = self._tmp_dir()
        profile_file = self._profile_file(
            tmp_dir, "raise RuntimeError('the profile file itself is broken')\n")
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_UNREADABLE", str(ctx.exception))

    def test_no_profile_export_refuses_invalid(self):
        tmp_dir = self._tmp_dir()
        profile_file = self._profile_file(tmp_dir, "NOT_PROFILE = 1\n")
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_INVALID", str(ctx.exception))

    def test_a_non_mapping_profile_refuses_invalid(self):
        tmp_dir = self._tmp_dir()
        profile_file = self._profile_file(tmp_dir, "PROFILE = ['not', 'a', 'mapping']\n")
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_INVALID", str(ctx.exception))

    def test_a_missing_nested_key_refuses_incomplete_and_names_it(self):
        """The `artifact: {}` lesson (design.md D3): a present-but-empty
        `kit` must be named by its missing LEAF, `kit.root`, never by the
        top-level key alone -- a top-level-only check passes this
        vacuously."""
        tmp_dir = self._tmp_dir()
        real_cli = str(LAUNCHER)
        profile_file = self._profile_file(
            tmp_dir,
            "from pathlib import Path\n"
            "PROFILE = {'kit': {}, "
            f"'cli': {{'path': Path({real_cli!r})}}, "
            f"'objective': {_VALID_OBJECTIVE_SRC}}}\n")
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        message = str(ctx.exception)
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE", message)
        self.assertIn("kit.root", message)
        self.assertNotIn("'kit'", message, "must name the leaf, not the section")

    def test_a_top_level_only_key_still_refuses_incomplete(self):
        tmp_dir = self._tmp_dir()
        profile_file = self._profile_file(tmp_dir, "PROFILE = {}\n")
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        message = str(ctx.exception)
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE", message)
        self.assertIn("kit.root", message)
        self.assertIn("cli.path", message)
        self.assertIn("objective", message)

    def test_a_relative_kit_root_refuses_unsafe_path(self):
        tmp_dir = self._tmp_dir()
        real_cli = str(LAUNCHER)
        profile_file = self._profile_file(
            tmp_dir,
            "from pathlib import Path\n"
            "PROFILE = {'kit': {'root': Path('relative/kit/root')}, "
            f"'cli': {{'path': Path({real_cli!r})}}, "
            f"'objective': {_VALID_OBJECTIVE_SRC}, "
            f"{_cut2_fields_src(tmp_dir)}}}\n")
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        message = str(ctx.exception)
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_UNSAFE_PATH", message)
        self.assertIn("kit.root", message)

    def test_a_nonexistent_absolute_kit_root_refuses_unsafe_path(self):
        """Absolute alone is not safe -- today this scatters into 19
        unrelated missing-asset failures under the 19 `SKILL_ROOT` readers;
        validating it here turns that into one named refusal (design.md
        D3)."""
        tmp_dir = self._tmp_dir()
        real_cli = str(LAUNCHER)
        missing = tmp_dir / "does-not-exist-either"
        profile_file = self._profile_file(
            tmp_dir,
            "from pathlib import Path\n"
            f"PROFILE = {{'kit': {{'root': Path({str(missing)!r})}}, "
            f"'cli': {{'path': Path({real_cli!r})}}, "
            f"'objective': {_VALID_OBJECTIVE_SRC}, "
            f"{_cut2_fields_src(tmp_dir)}}}\n")
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        message = str(ctx.exception)
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_UNSAFE_PATH", message)
        self.assertIn("kit.root", message)

    def test_a_valid_profile_resolves_cleanly(self):
        """The positive control every refusal test above is a mutation OF:
        a complete, absolute, existing profile loads with no error and
        exposes `PROFILE` as a mapping carrying exactly what was declared."""
        tmp_dir = self._tmp_dir()
        real_cli = str(LAUNCHER)
        profile_file = self._profile_file(
            tmp_dir,
            "from pathlib import Path\n"
            f"PROFILE = {{'kit': {{'root': Path({str(tmp_dir)!r})}}, "
            f"'cli': {{'path': Path({real_cli!r})}}, "
            f"'objective': {_VALID_OBJECTIVE_SRC}, "
            f"{_cut2_fields_src(tmp_dir)}}}\n")
        module = _fresh_resolver_load(str(profile_file))
        self.assertEqual(Path(module.PROFILE["kit"]["root"]), tmp_dir)
        self.assertEqual(Path(module.PROFILE["cli"]["path"]), LAUNCHER)
        self.assertEqual(module.PROFILE["objective"]["purpose"], "p")


class ObjectiveProfileFieldTests(unittest.TestCase):
    """The Cut-1 field set's third member (operator ruling, task 7.5):
    `objective`, validated exactly as `domain-profile.ts`'s own
    `OBJECTIVE_REQUIRED`/`stagesIncomplete` pair -- top-level presence,
    nested required-key completeness, and `stages: []` ruled out
    separately, since a bare-presence check alone would pass it
    vacuously."""

    def _profile_file(self, tmp_dir: Path, body: str) -> Path:
        profile_file = tmp_dir / "impl_profile.py"
        profile_file.write_text(body, encoding="utf-8")
        return profile_file

    def _tmp_dir(self) -> Path:
        tmp_dir = Path(tempfile.mkdtemp(prefix="impl-profile-objective-"))
        self.addCleanup(shutil.rmtree, tmp_dir, ignore_errors=True)
        return tmp_dir

    def _kit_cli(self, tmp_dir: Path) -> str:
        real_cli = str(LAUNCHER)
        return (f"'kit': {{'root': {str(tmp_dir)!r}}}, "
               f"'cli': {{'path': Path({real_cli!r})}}, "
               f"{_cut2_fields_src(tmp_dir)}")

    def test_a_missing_objective_refuses_incomplete_and_names_it(self):
        tmp_dir = self._tmp_dir()
        profile_file = self._profile_file(
            tmp_dir,
            "from pathlib import Path\n"
            f"PROFILE = {{{self._kit_cli(tmp_dir)}}}\n")
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        message = str(ctx.exception)
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE", message)
        self.assertIn("objective", message)

    def test_a_missing_objective_leaf_refuses_incomplete_and_names_it(self):
        """The `artifact: {}` lesson, applied to `objective` too: a
        present-but-incomplete `objective` is named by its missing LEAF."""
        tmp_dir = self._tmp_dir()
        profile_file = self._profile_file(
            tmp_dir,
            "from pathlib import Path\n"
            f"PROFILE = {{{self._kit_cli(tmp_dir)}, "
            "'objective': {'purpose': 'p', 'arrival': 'a', "
            "'stages': [{'stage': 's', 'establishes': 'e', "
            "'behindWhen': 'b'}]}}\n")  # humanStops omitted
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        message = str(ctx.exception)
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE", message)
        self.assertIn("objective.humanStops", message)

    def test_empty_stages_refuses_incomplete(self):
        """`stages: []` passes a bare presence check vacuously -- a north
        with no stages is not a north (domain-profile.ts's own
        `stagesIncomplete` lesson, mirrored exactly)."""
        tmp_dir = self._tmp_dir()
        profile_file = self._profile_file(
            tmp_dir,
            "from pathlib import Path\n"
            f"PROFILE = {{{self._kit_cli(tmp_dir)}, "
            "'objective': {'purpose': 'p', 'arrival': 'a', "
            "'humanStops': ['h'], 'stages': []}}\n")
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        message = str(ctx.exception)
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE", message)
        self.assertIn("objective.stages", message)

    def test_a_stage_missing_a_required_key_refuses_incomplete(self):
        tmp_dir = self._tmp_dir()
        profile_file = self._profile_file(
            tmp_dir,
            "from pathlib import Path\n"
            f"PROFILE = {{{self._kit_cli(tmp_dir)}, "
            "'objective': {'purpose': 'p', 'arrival': 'a', "
            "'humanStops': ['h'], "
            "'stages': [{'stage': 's', 'establishes': 'e'}]}}\n")  # no behindWhen
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        message = str(ctx.exception)
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE", message)
        self.assertIn("objective.stages", message)

    def test_a_complete_objective_resolves_cleanly(self):
        tmp_dir = self._tmp_dir()
        profile_file = self._profile_file(
            tmp_dir,
            "from pathlib import Path\n"
            f"PROFILE = {{{self._kit_cli(tmp_dir)}, "
            f"'objective': {_VALID_OBJECTIVE_SRC}}}\n")
        module = _fresh_resolver_load(str(profile_file))
        self.assertEqual(module.PROFILE["objective"]["purpose"], "p")
        self.assertEqual(len(module.PROFILE["objective"]["stages"]), 1)


class SetdefaultOverrideTests(unittest.TestCase):
    """The launcher's own `os.environ.setdefault` (design.md D1): an
    explicit `IMPLEMENTATION_DOMAIN_PROFILE` in the child's environment is a
    deliberate override and must win over the launcher's own default --
    mirroring the `??=` semantics `proposal-deliberation/cli.mjs` uses,
    including for the empty string, which stays empty and is refused
    (`ProfileResolverRefusalTests.test_empty_string_refuses_required`).

    Proven via a real subprocess against a tmpdir fixture profile, never a
    monkeypatch: the launcher's `setdefault` call and the engine's own
    `_resolve()` both run in the CHILD process, invisible to an in-process
    patch of this test's own `os.environ` (recorded scar: monkeypatching a
    module attribute has zero effect on a subprocess).
    """

    def test_an_explicit_override_wins_and_its_own_kit_root_is_what_fails(self):
        """The fixture's `kit.root` is deliberately unsafe (nonexistent), so
        a subprocess that used the launcher's own default would succeed --
        and one that honoured the override fails, naming exactly the
        fixture's own path in its refusal. That the fixture's path appears
        at all is the proof the override reached the child process; that it
        is what fails is the proof it was not silently ignored."""
        fixture_dir = Path(tempfile.mkdtemp(prefix="profile-override-"))
        self.addCleanup(shutil.rmtree, fixture_dir, ignore_errors=True)
        missing_root = fixture_dir / "kit-root-does-not-exist"
        profile_file = fixture_dir / "impl_profile.py"
        profile_file.write_text(
            "from pathlib import Path\n"
            f"PROFILE = {{'kit': {{'root': Path({str(missing_root)!r})}}, "
            f"'cli': {{'path': Path({str(LAUNCHER)!r})}}, "
            f"'objective': {_VALID_OBJECTIVE_SRC}, "
            f"{_cut2_fields_src(fixture_dir)}}}\n",
            encoding="utf-8")

        env = dict(os.environ)
        env[_ENV_VAR] = str(profile_file)
        proc = subprocess.run(
            [sys.executable, str(LAUNCHER), "verify", "--target",
             "/tmp/does-not-matter", "--name", "Method"],
            capture_output=True, text=True, env=env)

        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_UNSAFE_PATH", proc.stderr)
        self.assertIn(str(profile_file), proc.stderr)

    def test_unset_falls_back_to_the_launchers_own_default_and_runs(self):
        """The companion control: with the variable absent from the child's
        environment entirely, the launcher's own `setdefault` supplies the
        skill's own profile and the command dispatches normally -- the
        baseline every other subprocess test in this suite already relies
        on, made explicit here."""
        env = dict(os.environ)
        env.pop(_ENV_VAR, None)
        proc = subprocess.run(
            [sys.executable, str(LAUNCHER), "verify", "--target",
             "/tmp/_implementation_profile_unset_probe_does_not_exist",
             "--name", "Method"],
            capture_output=True, text=True, env=env)
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertNotIn("IMPLEMENTATION_DOMAIN_PROFILE", proc.stdout + proc.stderr)


class LauncherExposesNoEngineAttributeTests(unittest.TestCase):
    """D1's pin against silent re-aliasing: `sys.modules[__name__] = _engine`
    would make `import implementation_cli as impl` yield the engine's own
    attributes again, invisibly. This asserts the launcher's OWN module
    namespace -- loaded exactly as `CoreNamesNoDomainTests._cli_module()`
    loads the CLI -- carries none of the engine's public surface."""

    @staticmethod
    def _launcher_module():
        spec = importlib.util.spec_from_file_location(
            "impl_launcher_for_alias_pin", LAUNCHER)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        return module

    def test_the_launcher_exposes_no_engine_attribute(self):
        launcher = self._launcher_module()
        for name in ("COMMANDS", "CLI_PATH", "SKILL_ROOT", "main"):
            with self.subTest(attribute=name):
                self.assertFalse(
                    hasattr(launcher, name),
                    f"the launcher module carries {name!r} -- it has been "
                    "aliased to the engine rather than merely handing over "
                    "to it")


#: Cut 2 (`the-domain-crosses-the-seam`): the sixteen dotted leaves design.md
#: D1 names, each a validated resolver leaf. `vocabulary.names` is included
#: here (Phase 1 is RED-first for all sixteen) even though the resolver does
#: not require it until S13 -- design.md D7's own landing order, confirmed
#: by task 2.5: "`vocabulary.names` case stays red until S13".
_CUT2_LEAVES: tuple[str, ...] = (
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
    "documents.directory",
    "documents.label",
)

#: `vocabulary.names` is declared at S13 (design.md D7), not S2 -- so a
#: helper that builds a COMPLETE profile without it is what S2-S12's tests
#: exercise, and one WITH it is what S13 onward exercises.
_CITATION_PATTERN_SRC = (
    r"Ecs?\.?\s*\(?(\d+)\)?|Eq\.?\s*\(?(\d+)\)?|Ecuaciones?\s*\((\d+)\)")


def _cut2_profile(tmp_dir: Path, *, with_names: bool = True) -> dict:
    """The complete Cut-2 field set (design.md's Interfaces/Contracts
    block), built as real Python objects -- never hand-serialized text --
    so removing one leaf for a refusal case is one `del`, not sixteen
    hand-written fixture bodies."""
    profile = {
        "kit": {"root": tmp_dir},
        "cli": {"path": LAUNCHER},
        "objective": {
            "purpose": "p", "arrival": "a", "humanStops": ["h"],
            "stages": [{"stage": "s", "establishes": "e", "behindWhen": "b"}],
        },
        "provenance": {
            "claim_key": "equations",
            "authored_init_sentence": (
                "Each module declares the sections and equations it "
                "implements in\n`__provenance__`, and every invariant "
                "listed there has a matching\ntest under tests/.\n"),
        },
        "findings": {
            "locus_key": "equations",
            "remedy_locus_key": "remedy_equations",
            "notation_keys": {
                "locus": "equations",
                "remedyLocus": "remedyEquations",
                "unknown": "unknownEquations",
            },
            "citation_pattern": _CITATION_PATTERN_SRC,
        },
        "vocabulary": {
            "subject_singular": "equation",
            "subject_plural": "equations",
            "subject_singular_es": "ecuación",
            "subject_plural_es": "ecuaciones",
            "subject_collective": "mathematics",
            "subject_collective_es": "matemática",
            "artifact_noun": "formulation",
        },
        "documents": {
            "directory": tmp_dir / "proposals",
            "label": "proposal",
        },
    }
    if with_names:
        profile["vocabulary"]["names"] = [
            "equation", "equations", "ecuación", "ecuaciones",
            "mathematics", "matemática", "formulation",
        ]
    return profile


def _to_profile_source(value) -> str:
    """Serializes a profile dict back to Python source for a fixture file.
    `Path` gets its own branch (its `repr()` is not directly constructible
    without the same import this fixture already carries); everything else
    -- str, list, nested dict -- goes through the ordinary `repr()`."""
    if isinstance(value, Mapping):
        items = ", ".join(
            f"{key!r}: {_to_profile_source(val)}" for key, val in value.items())
        return "{" + items + "}"
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(_to_profile_source(item) for item in value) + "]"
    if isinstance(value, Path):
        return f"Path({str(value)!r})"
    return repr(value)


def _without_leaf(profile: dict, dotted: str) -> dict:
    clone = copy.deepcopy(profile)
    section, key = dotted.split(".", 1)
    del clone[section][key]
    return clone


def _write_profile(tmp_dir: Path, profile: dict) -> Path:
    profile_file = tmp_dir / "impl_profile.py"
    profile_file.write_text(
        "from pathlib import Path\n"
        f"PROFILE = {_to_profile_source(profile)}\n",
        encoding="utf-8")
    return profile_file


class DomainFieldLeafRefusalTests(unittest.TestCase):
    """Phase 1 (RED first, tasks.md): one `..._INCOMPLETE` case per Cut-2
    leaf, each naming the exact dotted leaf -- never its section alone,
    the same `artifact: {}` lesson `ProfileResolverRefusalTests` already
    proves for Cut 1's three fields. At the moment this class first runs
    (S1), the resolver validates none of these sixteen, so every one of
    them is expected to stay RED (no exception raised) until its own S-step
    lands (S2 onward); `vocabulary.names` specifically stays red through
    S12 and only turns green at S13 (design.md D7)."""

    def _tmp_dir(self) -> Path:
        tmp_dir = Path(tempfile.mkdtemp(prefix="impl-profile-domain-"))
        self.addCleanup(shutil.rmtree, tmp_dir, ignore_errors=True)
        return tmp_dir

    def test_each_cut2_leaf_refuses_incomplete_and_names_itself(self):
        for dotted in _CUT2_LEAVES:
            with self.subTest(leaf=dotted):
                tmp_dir = self._tmp_dir()
                full = _cut2_profile(tmp_dir)
                incomplete = _without_leaf(full, dotted)
                profile_file = _write_profile(tmp_dir, incomplete)
                with self.assertRaises(RuntimeError) as ctx:
                    _fresh_resolver_load(str(profile_file))
                message = str(ctx.exception)
                self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE", message)
                self.assertIn(dotted, message)

    def test_the_complete_cut2_profile_resolves_cleanly(self):
        """The positive control every refusal case above is a mutation OF."""
        tmp_dir = self._tmp_dir()
        full = _cut2_profile(tmp_dir)
        (tmp_dir / "proposals").mkdir()
        profile_file = _write_profile(tmp_dir, full)
        module = _fresh_resolver_load(str(profile_file))
        self.assertEqual(module.PROFILE["provenance"]["claim_key"], "equations")
        self.assertEqual(
            module.PROFILE["findings"]["remedy_locus_key"], "remedy_equations")
        self.assertEqual(module.PROFILE["vocabulary"]["artifact_noun"], "formulation")
        self.assertEqual(module.PROFILE["documents"]["label"], "proposal")


class DocumentsDirectoryOwnTierTests(unittest.TestCase):
    """M3 (design.md): `documents.directory` cannot join `_REQUIRED_NESTED`
    -- that tuple's `..._UNSAFE_PATH` walk requires `.exists()`, and a
    non-existent `documents.directory` (a clone with no `proposals/` yet)
    must import fine. Threat-matrix RED test (Path traversal via profile,
    tasks.md 2.3): relative refuses `UNSAFE_PATH`; non-existent absolute
    imports fine."""

    def _tmp_dir(self) -> Path:
        tmp_dir = Path(tempfile.mkdtemp(prefix="impl-profile-documents-"))
        self.addCleanup(shutil.rmtree, tmp_dir, ignore_errors=True)
        return tmp_dir

    def test_a_relative_documents_directory_refuses_unsafe_path(self):
        tmp_dir = self._tmp_dir()
        full = _cut2_profile(tmp_dir)
        full["documents"]["directory"] = Path("relative/proposals")
        profile_file = _write_profile(tmp_dir, full)
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        message = str(ctx.exception)
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_UNSAFE_PATH", message)
        self.assertIn("documents.directory", message)

    def test_a_nonexistent_absolute_documents_directory_imports_fine(self):
        """The whole point of M3: a clone with no `proposals/` yet must not
        be refused at import -- five reported absences would become one
        fatal refusal, a behavioural delta the seal's `*-e0` cases would
        catch."""
        tmp_dir = self._tmp_dir()
        full = _cut2_profile(tmp_dir)
        self.assertFalse(full["documents"]["directory"].exists())
        profile_file = _write_profile(tmp_dir, full)
        module = _fresh_resolver_load(str(profile_file))
        self.assertFalse(Path(module.PROFILE["documents"]["directory"]).exists())


class DocumentsDirectoryEnvironmentOverrideTests(unittest.TestCase):
    """Threat-matrix RED test (design.md, Environment-variable routing,
    task 9.2): `IMPLEMENTATION_PROPOSALS` must still win over
    `documents.directory` -- `proposals_root()`'s override check runs
    BEFORE the profile-supplied default, exactly as it did in Cut 1 for the
    hardcoded `FORGE_ROOT / "proposals"`. Proven via a real subprocess
    against a Cut-2-complete fixture profile whose `documents.directory`
    deliberately points somewhere else, never a monkeypatch (recorded
    scar: patching a module attribute has zero effect on a subprocess)."""

    def test_the_env_override_wins_over_documents_directory(self):
        fixture_dir = Path(tempfile.mkdtemp(prefix="documents-directory-override-"))
        self.addCleanup(shutil.rmtree, fixture_dir, ignore_errors=True)
        profile_documents_dir = fixture_dir / "not-the-real-proposals-dir"
        profile_documents_dir.mkdir()
        env_documents_dir = fixture_dir / "the-real-proposals-dir"
        env_documents_dir.mkdir()
        revision_name = "seal-2.md"
        (env_documents_dir / revision_name).write_text(
            "the env-routed revision text\n", encoding="utf-8")
        (profile_documents_dir / revision_name).write_text(
            "the profile-routed revision text (must not be read)\n",
            encoding="utf-8")

        full = _cut2_profile(fixture_dir)
        full["documents"]["directory"] = profile_documents_dir
        profile_file = _write_profile(fixture_dir, full)

        env = dict(os.environ)
        env[_ENV_VAR] = str(profile_file)
        env["IMPLEMENTATION_PROPOSALS"] = str(env_documents_dir)
        proc = subprocess.run(
            [sys.executable, str(LAUNCHER), "admit", "--target",
             "/tmp/does-not-matter-for-this-refusal", "--name", "Method",
             "--revision", revision_name],
            capture_output=True, text=True, env=env)

        # The refusal this hits (target/`src/` absent) fires AFTER
        # `revision_source` reads the bound text -- so a refusal naming
        # anything at all proves the environment-routed file, not the
        # profile-routed one, was read.
        self.assertNotIn(
            "REVISION_UNREADABLE", proc.stdout + proc.stderr,
            "the env override did not win: the revision was reported "
            "unreadable, which only happens if the profile's own "
            "documents.directory was read instead")


class IndexedDocumentsLeafRefusalTests(unittest.TestCase):
    """Cut 3 (`a-revision-is-two-documents`, Phase 1, tasks.md 1.1): `documents`
    becomes a list, validated per index (design.md D4) -- a missing or
    malformed leaf is named by its exact indexed path (`documents[1].directory`),
    never the bare field name. At this commit the resolver has not yet
    changed: `documents` is still validated as a single top-level mapping
    (`_REQUIRED_PRESENCE`'s `("documents", "label")` pair, `_REQUIRED_ABSOLUTE_ONLY`'s
    `("documents", "directory")` pair), so every case below is expected to
    stay RED until Phase 2 lands the per-entry walk."""

    def _tmp_dir(self) -> Path:
        tmp_dir = Path(tempfile.mkdtemp(prefix="impl-profile-documents-list-"))
        self.addCleanup(shutil.rmtree, tmp_dir, ignore_errors=True)
        return tmp_dir

    def _two_document_profile(self, tmp_dir: Path) -> dict:
        full = _cut2_profile(tmp_dir)
        full["documents"] = [
            {"directory": tmp_dir / "documents-0", "label": "label-0"},
            {"directory": tmp_dir / "documents-1", "label": "label-1"},
        ]
        return full

    def test_a_second_documents_missing_directory_refuses_by_indexed_name(self):
        tmp_dir = self._tmp_dir()
        full = self._two_document_profile(tmp_dir)
        del full["documents"][1]["directory"]
        profile_file = _write_profile(tmp_dir, full)
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        message = str(ctx.exception)
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE", message)
        self.assertIn("documents[1].directory", message)

    def test_the_first_documents_missing_label_refuses_by_indexed_name(self):
        tmp_dir = self._tmp_dir()
        full = self._two_document_profile(tmp_dir)
        del full["documents"][0]["label"]
        profile_file = _write_profile(tmp_dir, full)
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        message = str(ctx.exception)
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE", message)
        self.assertIn("documents[0].label", message)

    def test_an_empty_documents_list_refuses_incomplete_naming_index_zero(self):
        tmp_dir = self._tmp_dir()
        full = _cut2_profile(tmp_dir)
        full["documents"] = []
        profile_file = _write_profile(tmp_dir, full)
        with self.assertRaises(RuntimeError) as ctx:
            _fresh_resolver_load(str(profile_file))
        message = str(ctx.exception)
        self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE", message)
        self.assertIn("documents[0]", message)


if __name__ == "__main__":
    unittest.main()
