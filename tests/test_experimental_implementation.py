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
import json
import os
import re
import shutil
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


#: `a-data-directory-somebody-can-owe` (B1). The engine's shared
#: `impl_domain_profile` import is a plain `from impl_domain_profile import
#: PROFILE` (fixed module name), cached process-wide in `sys.modules` --
#: every fresh engine re-import below must `pop` it first, or a later call
#: silently reads an earlier test's already-resolved profile (the exact
#: scar `test_implementation_domain_mutation.py` records for its own
#: mutation harness).
ENGINE_DIR = FORGE / ".claude" / "skills" / "_core" / "implementation" / "engine"


def _engine_with_documents(documents: list[dict]):
    """A fresh engine import whose ONLY difference from the real,
    resolving `experimental-implementation` profile is its `documents`
    list -- every other leaf is untouched, so the resolver's other checks
    stay satisfied and only the detector's own behaviour is exercised."""
    profile = dict(_real_profile())
    profile["documents"] = documents
    tmp_dir = Path(tempfile.mkdtemp(prefix="dataset-marker-detector-"))
    profile_file = tmp_dir / "impl_profile.py"
    profile_file.write_text(
        "from pathlib import Path\n"
        f"PROFILE = {_to_source(profile)}\n",
        encoding="utf-8")

    os.environ["IMPLEMENTATION_DOMAIN_PROFILE"] = str(profile_file)
    sys.modules.pop("impl_domain_profile", None)
    if str(ENGINE_DIR) not in sys.path:
        sys.path.insert(0, str(ENGINE_DIR))
    name = f"experimental_impl_engine_probe_{next(_counter)}"
    spec = importlib.util.spec_from_file_location(
        name, ENGINE_DIR / "implementation_engine.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module, tmp_dir


class DatasetDeclaredDetectorTests(unittest.TestCase):
    """B1 (`a-data-directory-somebody-can-owe`, design.md D1/D2, tasks.md
    Phase 2): the dataset-declared detector, proven directly -- pure
    function, no CLI dispatch, so an in-process fresh-engine import is not
    the "monkeypatch has zero effect on a subprocess" scar (that scar is
    about a DIFFERENT process reading a patched attribute; this is the
    SAME process calling a freshly-imported module's own function)."""

    def _tmp_docs_dir(self) -> Path:
        tmp_dir = Path(tempfile.mkdtemp(prefix="dataset-marker-docs-"))
        self.addCleanup(shutil.rmtree, tmp_dir, ignore_errors=True)
        return tmp_dir

    def test_a_none_marker_never_opens_the_document(self):
        """The revision names a file that does not exist at all -- proving
        only that a missing file does not raise would be true of ANY
        marker (`revision_source` already tolerates absence); the
        property under test is that a `None`-marked entry never attempts
        the read in the first place, proven by a spy on `revision_source`
        itself."""
        docs_dir = self._tmp_docs_dir()
        engine, _ = _engine_with_documents([
            {"directory": docs_dir, "label": "experiments", "dataset_marker": None},
        ])
        calls = []
        original = engine.revision_source

        def _spy(revision, index=0):
            calls.append((revision, index))
            return original(revision, index)

        engine.revision_source = _spy
        self.assertFalse(engine.declares_dataset("does-not-exist.md"))
        self.assertEqual(
            calls, [],
            "a None-marked document must never open a file at all, and this "
            "spy proves revision_source was never called for it")

    def test_a_declared_marker_present_at_line_start_answers_true(self):
        docs_dir = self._tmp_docs_dir()
        (docs_dir / "r1.md").write_text(
            "intro line\n**Dataset:** the corpus\nmore text\n", encoding="utf-8")
        engine, _ = _engine_with_documents([
            {"directory": docs_dir, "label": "experiments",
             "dataset_marker": "**Dataset:**"},
        ])
        self.assertTrue(engine.declares_dataset("r1.md"))

    def test_a_mid_sentence_only_occurrence_answers_false(self):
        """X3's own strength case: `lstrip().startswith(marker)`, never a
        bare substring test -- a document that only DISCUSSES its own
        format ("every protocol needs a **Dataset:** line") must not
        satisfy a substring test while declaring nothing (design.md D1)."""
        docs_dir = self._tmp_docs_dir()
        (docs_dir / "r1.md").write_text(
            "every protocol needs a **Dataset:** line somewhere\n"
            "but this one never puts it first\n", encoding="utf-8")
        engine, _ = _engine_with_documents([
            {"directory": docs_dir, "label": "experiments",
             "dataset_marker": "**Dataset:**"},
        ])
        self.assertFalse(engine.declares_dataset("r1.md"))

    def test_a_marker_with_regex_metacharacters_matches_only_literally(self):
        """Threat-matrix row (host-supplied text matched against file
        bytes): the marker is a literal, never a regex -- a document
        carrying unrelated text a regex interpretation of the marker
        WOULD match must still answer false."""
        docs_dir = self._tmp_docs_dir()
        marker = "Da.*taset:"
        (docs_dir / "r1.md").write_text(
            # A regex built from `marker` would match this line (any char
            # for `.`, zero-or-more `a` for `*`); a literal match must not.
            "Dazzzztaset: this is not the literal marker\n", encoding="utf-8")
        engine, _ = _engine_with_documents([
            {"directory": docs_dir, "label": "experiments",
             "dataset_marker": marker},
        ])
        self.assertFalse(engine.declares_dataset("r1.md"))

        (docs_dir / "r2.md").write_text(f"{marker} literally, at line start\n",
                                        encoding="utf-8")
        self.assertTrue(engine.declares_dataset("r2.md"))

    def test_or_fold_only_index_one_declares_and_the_demand_still_holds(self):
        """Kills "read index 0 always" (design.md D2): index 0 declares
        `None`, index 1 declares a real marker present in ITS OWN
        discovered revision -- the demand must still answer true,
        or-folded across every declared document."""
        doc0_dir = self._tmp_docs_dir()
        (doc0_dir / "r1.md").write_text("no marker here\n", encoding="utf-8")
        doc1_dir = self._tmp_docs_dir()
        (doc1_dir / "only-candidate-9.md").write_text(
            "**Dataset:** declared only here\n", encoding="utf-8")
        engine, _ = _engine_with_documents([
            {"directory": doc0_dir, "label": "experiments", "dataset_marker": None},
            {"directory": doc1_dir, "label": "proposal",
             "dataset_marker": "**Dataset:**"},
        ])
        self.assertTrue(engine.declares_dataset("r1.md"))

    def test_no_revision_at_all_answers_false_and_discovers_nothing(self):
        """Property 2 (design.md): a `None` seed (`plan` with no
        `--revision`) must short-circuit before EVER discovering document
        1's own revision -- proven the same way as the None-marker case,
        by spying on the discovery entry point."""
        doc0_dir = self._tmp_docs_dir()
        doc1_dir = self._tmp_docs_dir()
        (doc1_dir / "candidate-9.md").write_text(
            "**Dataset:** would be found if discovery ran\n", encoding="utf-8")
        engine, _ = _engine_with_documents([
            {"directory": doc0_dir, "label": "experiments", "dataset_marker": None},
            {"directory": doc1_dir, "label": "proposal",
             "dataset_marker": "**Dataset:**"},
        ])
        calls = []
        original = engine.document_revision_names

        def _spy(revision):
            calls.append(revision)
            return original(revision)

        engine.document_revision_names = _spy
        self.assertFalse(engine.declares_dataset(None))
        self.assertEqual(
            calls, [],
            "declares_dataset(None) must never call document_revision_names "
            "at all -- no discovery, ever, absent an explicit revision")


class RevisionThreadingAgreementTests(unittest.TestCase):
    """Phase 3 (design.md D3/D4, tasks.md 3.1-3.3): `--revision` reaches
    all three `build_plan` call sites -- `plan` (the ONLY parser
    registration), `apply` and `materialize`'s own gate (both re-derive
    the seed from the approved plan's own `boundTo` key, never a second
    `--revision` flag). Real subprocesses throughout, against a SCRATCH
    profile declaring a real marker -- never the shipped
    experimental-implementation profile, whose own marker stays `None`
    until B2 (design.md D10)."""

    PACKAGE = "PlanRevision"

    def setUp(self):
        self.docs_dir = Path(tempfile.mkdtemp(prefix="plan-revision-docs-"))
        self.addCleanup(shutil.rmtree, self.docs_dir, ignore_errors=True)
        (self.docs_dir / "r1.md").write_text(
            "**Dataset:** declared here\n", encoding="utf-8")
        self.profile_file = self._write_profile_with_marker(self.docs_dir)

    def _write_profile_with_marker(self, docs_dir: Path) -> Path:
        profile = dict(_real_profile())
        profile["documents"] = [
            {"directory": docs_dir, "label": "experiments",
             "dataset_marker": "**Dataset:**"},
        ]
        tmp_profile_dir = Path(tempfile.mkdtemp(prefix="plan-revision-profile-"))
        self.addCleanup(shutil.rmtree, tmp_profile_dir, ignore_errors=True)
        profile_file = tmp_profile_dir / "impl_profile.py"
        profile_file.write_text(
            "from pathlib import Path\n"
            f"PROFILE = {_to_source(profile)}\n",
            encoding="utf-8")
        return profile_file

    def _env(self, profile_file: Path | None = None) -> dict:
        env = dict(os.environ)
        env["IMPLEMENTATION_DOMAIN_PROFILE"] = str(profile_file or self.profile_file)
        env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "plan-revision-tests"
        env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = (
            "plan-revision-tests@example.invalid")
        return env

    def _box(self, suffix: str) -> Path:
        box = FORGE / "implementations" / f"_plan_revision_{os.getpid()}_{id(self)}{suffix}"
        self.addCleanup(shutil.rmtree, box, ignore_errors=True)
        box.mkdir(parents=True)
        env = self._env()
        subprocess.run(["git", "init", "-q", str(box)], check=True, capture_output=True)
        (box / "src" / self.PACKAGE).mkdir(parents=True)
        (box / "src" / self.PACKAGE / "__init__.py").write_text(
            "__all__ = []\n", encoding="utf-8")
        (box / "tests").mkdir(parents=True)
        subprocess.run(["git", "add", "-A"], cwd=box, env=env, check=True,
                       capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=box, env=env,
                       check=True, capture_output=True)
        return box

    def _run(self, *args: str, profile_file: Path | None = None):
        return subprocess.run(
            [sys.executable, str(LAUNCHER), *args],
            capture_output=True, text=True, cwd=FORGE,
            env=self._env(profile_file))

    def _approved_plan_path(self, plan: dict) -> Path:
        plan_dir = Path(tempfile.mkdtemp(prefix="plan-revision-approved-"))
        self.addCleanup(shutil.rmtree, plan_dir, ignore_errors=True)
        plan_path = plan_dir / "plan.json"
        plan_path.write_text(json.dumps(plan), encoding="utf-8")
        return plan_path

    def test_plan_with_no_revision_opens_no_document_and_stays_byte_identical(self):
        """Property 2 (design.md), reading-at-plan-time threat row:
        absent `--revision`, `plan`'s output must not depend on the
        document at all. Proven by pointing the profile's own document
        root at a NONEXISTENT directory and asserting `plan` still
        succeeds, identically to the same command against the real one --
        a read attempt against a missing directory would surface
        differently were it ever made."""
        missing_root = Path(tempfile.mkdtemp(prefix="plan-revision-missing-")) / "gone"
        self.addCleanup(shutil.rmtree, missing_root.parent, ignore_errors=True)
        missing_docs_profile = self._write_profile_with_marker(missing_root)
        box = self._box("_control")

        with_docs = self._run("plan", "--target", str(box), "--name", self.PACKAGE)
        without_docs = self._run(
            "plan", "--target", str(box), "--name", self.PACKAGE,
            profile_file=missing_docs_profile)

        self.assertEqual(with_docs.returncode, 0, with_docs.stderr)
        self.assertEqual(without_docs.returncode, 0, without_docs.stderr)
        self.assertEqual(with_docs.stdout, without_docs.stdout)
        self.assertNotIn("boundTo", json.loads(with_docs.stdout))

    def test_plan_approve_apply_agree_and_create_dirs_holds_the_declared_data(self):
        box = self._box("_agreement")
        plan_proc = self._run(
            "plan", "--target", str(box), "--name", self.PACKAGE,
            "--revision", "r1.md")
        self.assertEqual(plan_proc.returncode, 0, plan_proc.stderr)
        plan = json.loads(plan_proc.stdout)
        self.assertIn(f"{self.PACKAGE}/Data", plan["createDirs"])
        self.assertEqual(plan["boundTo"]["revision"], "r1.md")

        apply_proc = self._run(
            "apply", "--target", str(box), "--name", self.PACKAGE,
            "--plan", str(self._approved_plan_path(plan)))
        self.assertEqual(apply_proc.returncode, 0, apply_proc.stderr)
        applied = json.loads(apply_proc.stdout)
        self.assertIn(f"{self.PACKAGE}/Data", applied["createdDirs"])

    def test_a_bare_apply_after_plan_revision_cannot_produce_plan_stale(self):
        """D3's own risk: an operator who ran `plan --revision X` and then
        a bare `apply` must not refuse `PLAN_STALE` -- the seed is
        carried in the approved plan's own `boundTo` key, never
        re-typed."""
        box = self._box("_bare_apply")
        plan_proc = self._run(
            "plan", "--target", str(box), "--name", self.PACKAGE,
            "--revision", "r1.md")
        self.assertEqual(plan_proc.returncode, 0, plan_proc.stderr)
        plan = json.loads(plan_proc.stdout)

        apply_proc = self._run(
            "apply", "--target", str(box), "--name", self.PACKAGE,
            "--plan", str(self._approved_plan_path(plan)))
        self.assertEqual(apply_proc.returncode, 0, apply_proc.stderr)
        self.assertNotEqual(
            json.loads(apply_proc.stdout).get("code"), "PLAN_STALE")

    def test_materialize_stage_gate_refuses_plan_stale_on_the_same_drift_apply_would(self):
        """Repeat through `materialize --stage` (tasks.md 3.2):
        `_materialize_plan_gate` alone, proven independent of any
        specific stage's own kit requirement (this domain ships none,
        SKILL.md) -- the marker is removed from the SAME revision file
        after approval, so the gate's own re-derivation of `createDirs`
        disagrees with the approved plan and refuses before any
        stage-specific write."""
        box = self._box("_materialize_gate")
        plan_proc = self._run(
            "plan", "--target", str(box), "--name", self.PACKAGE,
            "--revision", "r1.md")
        self.assertEqual(plan_proc.returncode, 0, plan_proc.stderr)
        plan_path = self._approved_plan_path(json.loads(plan_proc.stdout))

        (self.docs_dir / "r1.md").write_text("no marker anymore\n", encoding="utf-8")

        proc = self._run(
            "materialize", "--target", str(box), "--name", self.PACKAGE,
            "--stage", "scaffold", "--plan", str(plan_path), "--seed", "7")
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        self.assertEqual(json.loads(proc.stdout).get("code"), "PLAN_STALE")

    def test_a_pre_existing_plan_with_no_bound_to_key_still_applies(self):
        """Data-integrity row (design.md): an approved plan.json with no
        `boundTo` key at all (every plan.json on disk before this
        change) still applies --
        `(approved.get("boundTo") or {}).get("revision")` falls back to
        `None`, today's exact branch."""
        box = self._box("_no_bound_to")
        plan_proc = self._run("plan", "--target", str(box), "--name", self.PACKAGE)
        self.assertEqual(plan_proc.returncode, 0, plan_proc.stderr)
        plan = json.loads(plan_proc.stdout)
        self.assertNotIn("boundTo", plan)

        apply_proc = self._run(
            "apply", "--target", str(box), "--name", self.PACKAGE,
            "--plan", str(self._approved_plan_path(plan)))
        self.assertEqual(apply_proc.returncode, 0, apply_proc.stderr)


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


class PublishedCommandsRunVerbatimTests(unittest.TestCase):
    """Task 3.7 (design.md D8): every command string this skill's OWN
    `SKILL.md` publishes must run verbatim through THIS skill's own
    launcher. The sibling's own `PublishedCommandsRunVerbatimTests`
    (`tests/test_proposal_implementation.py`) is bound to `SKILL_ROOT =
    proposal-implementation` and cannot see this file at all -- this is
    the new suite's own, never a shared import."""

    SKILL_MD = SKILL_DIR / "SKILL.md"

    #: Every fenced ```bash block whose first non-blank line begins with
    #: this skill's own launcher path -- a syntactic shape, not a
    #: hand-kept list of which lines to check.
    _FENCE_RE = re.compile(r"```bash\n(.*?)```", re.DOTALL)

    def _published_commands(self) -> list[str]:
        text = self.SKILL_MD.read_text(encoding="utf-8")
        launcher_rel = str(LAUNCHER.relative_to(FORGE))
        commands = []
        for block in self._FENCE_RE.findall(text):
            for line in block.splitlines():
                line = line.strip()
                # `<command>`/`<TARGET>`-shaped placeholders name the usage
                # TEMPLATE, never a concrete runnable line -- skipped here,
                # never silently "run" against a literal `<...>` string.
                if line.startswith(launcher_rel) and "<" not in line:
                    commands.append(line)
        return commands

    def test_the_doctrine_publishes_at_least_one_concrete_command(self):
        self.assertGreater(
            len(self._published_commands()), 0,
            "SKILL.md publishes no concrete, runnable command line -- this "
            "check would otherwise be vacuous")

    def test_every_published_command_runs_verbatim_through_this_launcher(self):
        launcher_rel = str(LAUNCHER.relative_to(FORGE))
        for command in self._published_commands():
            with self.subTest(command=command):
                argv = command[len(launcher_rel):].strip().split()
                proc = subprocess.run(
                    [sys.executable, str(LAUNCHER)] + argv,
                    cwd=str(FORGE), capture_output=True, text=True, timeout=30)
                self.assertEqual(
                    proc.returncode, 0,
                    f"published command {command!r} did not run cleanly "
                    f"through this skill's own launcher: "
                    f"{proc.stdout}{proc.stderr}")


class DoctrineVocabularyLeakTests(unittest.TestCase):
    """Task 3.8: `tests/forge_vocabulary.py::shipped_documents()` scans this
    skill's directory unedited -- proven directly, not assumed -- and the
    doctrine spells none of the denylisted target words."""

    def test_shipped_documents_discovers_this_skills_own_files(self):
        sys.path.insert(0, str(FORGE / "tests"))
        import forge_vocabulary  # noqa: E402  (path set above)
        documents = forge_vocabulary.shipped_documents()
        under_this_skill = [
            path for path in documents
            if SKILL_DIR in path.parents]
        self.assertGreater(
            len(under_this_skill), 0,
            "shipped_documents() discovers no file under this skill's own "
            "directory")

    def test_the_doctrine_spells_no_denylisted_target_word(self):
        sys.path.insert(0, str(FORGE / "tests"))
        import forge_vocabulary  # noqa: E402  (path set above)
        for document in (SKILL_DIR / "SKILL.md",
                         FORGE / ".claude" / "agents" / "experiments-build.md",
                         FORGE / ".claude" / "agents" / "experiments-walk.md",
                         PROFILE_FILE):
            with self.subTest(document=document.name):
                text = document.read_text(encoding="utf-8")
                leaks = forge_vocabulary.leaks_in(text)
                self.assertEqual(leaks, [], f"{document.name} spells {leaks}")


if __name__ == "__main__":
    unittest.main()
