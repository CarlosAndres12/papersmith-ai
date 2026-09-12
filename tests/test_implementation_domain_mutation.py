"""Cut 2 (`the-domain-crosses-the-seam`), design.md D8: mutation proof,
both directions, per leaf.

**Removal** is already proven for all sixteen leaves by
`test_implementation_profile.py`'s `DomainFieldLeafRefusalTests` -- each
raises `IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE` naming its own leaf. This
file is the OTHER half: **change**. A real, reverted mutation moves the
digest D1 predicted -- or, where measurement disagrees with prediction, the
digest actually measured, recorded honestly (design.md's own warning: Cut 1
shipped a false git-rename prediction, and this cut's own predictions are
claims apply must measure, never facts to cite).

**Never a monkeypatch** (the scar Cut 1 recorded and this cut carries
forward): every seal case is a real subprocess, so patching
`impl_domain_profile.PROFILE` or any engine attribute in-process has ZERO
effect on it. Every mutation here is a REAL file on disk -- a scratch copy
of `impl_profile.py`, with `kit.root`/`cli.path`/`documents.directory`'s
own base kept anchored to the real skill directory so only the ONE leaf
under test differs from the shipped profile -- reached by a REAL
`IMPLEMENTATION_DOMAIN_PROFILE` environment override on a REAL subprocess.
The shipped `impl_profile.py` is never edited by this file.

**Anchor discipline** (design.md D8): before every mutation, the real
source's occurrence count for the OLD spelling is asserted to be exactly 1
(so the substitution is unambiguous) and the NEW spelling to be absent; the
scratch copy is then asserted 0/1. An anchor that matched is not a mutation
that ran.

**Measured, not assumed.** Seven of the fourteen change-tested leaves below
did NOT move any of the 28 sealed cases against these particular fixtures,
despite a mover predicted in design.md D1. Each is recorded here as an
explicit ZERO-MOVER: its removal-refusal (above) and its lock coverage
(`test_implementation_domain_lock.py`) are its whole defence, per design.md
D8's own instruction -- never papered over, never hunted for a test that
would have moved it.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
import unittest
from pathlib import Path

FORGE = Path(__file__).resolve().parents[1]
ENGINE_DIR = FORGE / ".claude/skills/_core/implementation/engine"
REAL_PROFILE = FORGE / ".claude/skills/proposal-implementation/impl_profile.py"
CASES_PATH = FORGE / "tests/seal/cases.json"

os.environ.setdefault("IMPLEMENTATION_DOMAIN_PROFILE", str(REAL_PROFILE))

import sys  # noqa: E402
if str(ENGINE_DIR) not in sys.path:
    sys.path.insert(0, str(ENGINE_DIR))
import implementation_engine as impl  # noqa: E402

_TESTS_DIR = Path(__file__).resolve().parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))
from seal import corpus as seal_corpus  # noqa: E402  (path set above)
from seal import harness as seal_harness  # noqa: E402

REAL_PROFILE_SRC = REAL_PROFILE.read_text(encoding="utf-8")
CASES = json.loads(CASES_PATH.read_text(encoding="utf-8"))

#: A case whose output is measured (during apply) to be non-deterministic
#: EVEN WITH ZERO CHANGES -- a fresh unmutated run's digest already
#: disagrees with the committed golden for this one id. Excluded from
#: every comparison below; recorded, not silently dropped. `propose`
#: composes `mintOrdinal`/timing-adjacent state the corpus's own
#: `IMPLEMENTATION_PROPOSALS`-free construction does not pin identically
#: run to run. Pre-existing to this cut -- no field mutation here touches
#: anything `propose` reads.
NON_DETERMINISTIC_CASE_IDS = frozenset({"propose"})

#: Leaf -> (old literal substring, new literal substring), each chosen to
#: occur EXACTLY ONCE in the real `impl_profile.py` (asserted below) so the
#: substitution is unambiguous -- the anchor discipline itself.
MUTATIONS: dict[str, tuple[str, str]] = {
    "provenance.claim_key": ('"claim_key": "equations",', '"claim_key": "claims",'),
    "provenance.authored_init_sentence": (
        '"Each module declares the sections and equations it implements in\\n"',
        '"Each module names what it establishes in\\n"'),
    "findings.locus_key": ('"locus_key": "equations",', '"locus_key": "loci",'),
    "findings.remedy_locus_key": (
        '"remedy_locus_key": "remedy_equations",', '"remedy_locus_key": "remedy_loci",'),
    "findings.notation_keys": ('"locus": "equations",', '"locus": "loci",'),
    "findings.citation_pattern": (
        r'r"Ecs?\.?\s*\(?(\d+)\)?|Eq\.?\s*\(?(\d+)\)?|Ecuaciones?\s*\((\d+)\)"',
        r'r"NOMATCHPATTERN_\d+"'),
    "vocabulary.subject_singular": (
        '"subject_singular": "equation",', '"subject_singular": "claim",'),
    "vocabulary.subject_plural": (
        '"subject_plural": "equations",', '"subject_plural": "claims",'),
    "vocabulary.subject_singular_es": (
        '"subject_singular_es": "ecuación",', '"subject_singular_es": "afirmación",'),
    "vocabulary.subject_plural_es": (
        '"subject_plural_es": "ecuaciones",', '"subject_plural_es": "afirmaciones",'),
    "vocabulary.subject_collective": (
        '"subject_collective": "mathematics",', '"subject_collective": "claims",'),
    "vocabulary.subject_collective_es": (
        '"subject_collective_es": "matemática",', '"subject_collective_es": "afirmación",'),
    "vocabulary.artifact_noun": ('"artifact_noun": "formulation",', '"artifact_noun": "method",'),
    "documents.label": ('"label": "proposal",', '"label": "document",'),
    # `new` is filled in per-test-run with the real sibling path (a fresh
    # `tempfile.mkdtemp()`, so it exists -- M3 requires absolute, not
    # existence, but an existing one keeps this mutation from ALSO
    # exercising the "documents.directory absent" path, which is not what
    # this leaf's mutation is proving).
    "documents.directory": ('"directory": _FORGE_ROOT / "proposals",', None),
}

#: Measured (this apply session, real subprocess runs, every one of the 28
#: sealed case ids compared): the case ids that actually moved for each
#: leaf, `NON_DETERMINISTIC_CASE_IDS` already excluded. An empty tuple is a
#: recorded zero-mover.
MEASURED_MOVERS: dict[str, tuple[str, ...]] = {
    "provenance.claim_key": ("probe", "verify-a", "verify-b", "verify-t"),
    "provenance.authored_init_sentence": (),  # ZERO-MOVER (see module docstring)
    "findings.locus_key": ("handoff-e1", "verify-a", "verify-b"),
    "findings.remedy_locus_key": ("handoff-e1", "verify-a", "verify-b"),
    "findings.notation_keys": ("handoff-e1", "verify-a", "verify-b"),
    # Re-measured, Cut 3 slice C (`the-second-document-verified-on-its-own-
    # terms`, design.md D3): this leaf's mutated value
    # (`r"NOMATCHPATTERN_\d+"`) has ZERO capturing groups. Before C1's
    # resolver-side group-count validation this was a genuine zero-mover
    # (a pattern that never matches still resolves; it just cites nothing).
    # C1 now refuses `IMPLEMENTATION_DOMAIN_PROFILE_INVALID_CITATION_PATTERN`
    # at import for ANY resolved `citation_pattern` without exactly three
    # groups, so every command that needs the profile to resolve at all
    # now fails the same way -- every sealed case except the one already
    # excluded as non-deterministic moves.
    "findings.citation_pattern": (
        "admit-e0", "admit-e1", "apply", "close-e0", "close-e1", "compose",
        "defect", "discuss", "gate-e0", "gate-e1", "handoff-e0", "handoff-e1",
        "materialize", "name", "offer-e0", "offer-e1", "plan-a", "plan-b",
        "position-e0", "position-e1", "probe", "settle", "step", "verify-a",
        "verify-b", "verify-t", "walk"),
    "vocabulary.subject_singular": ("compose",),
    "vocabulary.subject_plural": (),  # ZERO-MOVER
    "vocabulary.subject_singular_es": ("handoff-e1",),
    "vocabulary.subject_plural_es": ("handoff-e1",),
    "vocabulary.subject_collective": (),  # ZERO-MOVER
    "vocabulary.subject_collective_es": (),  # ZERO-MOVER
    "vocabulary.artifact_noun": (),  # ZERO-MOVER
    "documents.label": (),  # ZERO-MOVER
    "documents.directory": ("admit-e0", "close-e0", "gate-e0", "offer-e0", "position-e0"),
}


#: Captured ONCE, at import time, before this module ever reassigns
#: `seal_harness.build_env` -- the wrapper below calls THIS reference, never
#: the module attribute (which becomes the wrapper itself once assigned;
#: calling through the attribute would recurse into itself forever).
_ORIGINAL_BUILD_ENV = seal_harness.build_env


def _build_env_with_profile_override(profile_path):
    """`seal_harness.build_env`'s own `ALLOWED_ENV_KEYS` deliberately does
    NOT pass `IMPLEMENTATION_DOMAIN_PROFILE` through (design.md D2: the
    seal always exercises the skill's OWN real profile via the launcher's
    `setdefault`). This wraps the real `build_env` to add exactly that one
    key when a mutation is under test -- a real env var reaching a real
    subprocess, never a monkeypatch of an engine or profile attribute."""
    def _wrapped(case, roots):
        env = _ORIGINAL_BUILD_ENV(case, roots)
        env["IMPLEMENTATION_DOMAIN_PROFILE"] = str(profile_path)
        return env
    return _wrapped


def _run_all_cases_under(profile_path, roots, scratch_root) -> dict[str, dict]:
    seal_harness.build_env = _build_env_with_profile_override(profile_path)
    try:
        results = {}
        for case in CASES:
            result = seal_harness.run_case(case, roots, scratch_root=scratch_root)
            results[case["id"]] = seal_harness.digest_result(result)
        return results
    finally:
        seal_harness.build_env = _ORIGINAL_BUILD_ENV


def _write_scratch_profile(tmp_dir: Path, mutated_src: str) -> Path:
    """A scratch copy of `impl_profile.py` -- `_SKILL` re-anchored to the
    REAL skill directory (this file computes `kit.root`/`cli.path`/
    `documents.directory` from its own location, and a copy elsewhere
    would otherwise point those at the scratch directory instead)."""
    real_skill_dir = REAL_PROFILE.resolve().parent
    anchored = mutated_src.replace(
        "_SKILL = Path(__file__).resolve().parent",
        f"_SKILL = Path({str(real_skill_dir)!r})")
    scratch_profile = tmp_dir / "impl_profile.py"
    scratch_profile.write_text(anchored, encoding="utf-8")
    return scratch_profile


class PerLeafChangeMutationTests(unittest.TestCase):
    """D8's change proof, one subtest per leaf: anchor discipline, a real
    scratch mutation, a real subprocess seal run over all 28 cases, and an
    assertion that ONLY the measured movers (never any other case) moved."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls._corpus_root = Path(cls._tmp.name) / "corpus"
        cls._roots = seal_corpus.build(cls._corpus_root)
        cls._scratch_root = FORGE / "implementations" / f"_domain_mutation_test_{os.getpid()}"
        cls._scratch_root.mkdir(parents=True, exist_ok=True)
        cls._baseline = _run_all_cases_under(REAL_PROFILE, cls._roots, cls._scratch_root)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._scratch_root, ignore_errors=True)
        cls._tmp.cleanup()

    def test_every_leaf_moves_exactly_its_measured_case_set(self):
        for leaf, (old, new) in MUTATIONS.items():
            with self.subTest(leaf=leaf):
                if leaf == "documents.directory":
                    sibling = Path(tempfile.mkdtemp(prefix="mutation-sibling-proposals-"))
                    self.addCleanup(shutil.rmtree, sibling, ignore_errors=True)
                    new = f'"directory": Path({str(sibling)!r}),'

                # Anchor discipline (design.md D8): the real source carries
                # the old spelling exactly once and the new spelling not at
                # all, BEFORE any mutation.
                real_src = REAL_PROFILE.read_text(encoding="utf-8")
                self.assertEqual(
                    real_src.count(old), 1,
                    f"{leaf}: expected the OLD spelling exactly once in the real "
                    f"impl_profile.py, found {real_src.count(old)} -- an ambiguous "
                    "anchor is not a mutation that can run unambiguously")
                self.assertEqual(
                    real_src.count(new), 0,
                    f"{leaf}: the NEW spelling already appears in the real "
                    "impl_profile.py before any mutation -- anchor invalid")

                mutated_src = real_src.replace(old, new, 1)

                with tempfile.TemporaryDirectory() as scratch_dir:
                    scratch_profile = _write_scratch_profile(
                        Path(scratch_dir), mutated_src)
                    scratch_src = scratch_profile.read_text(encoding="utf-8")
                    # Anchor discipline, the mutated side: 0 old / 1 new.
                    self.assertEqual(scratch_src.count(old), 0)
                    self.assertEqual(scratch_src.count(new), 1)

                    mutated_results = _run_all_cases_under(
                        scratch_profile, self.__class__._roots,
                        self.__class__._scratch_root)

                moved = sorted(
                    cid for cid in mutated_results
                    if cid not in NON_DETERMINISTIC_CASE_IDS
                    and mutated_results[cid] != self.__class__._baseline[cid])
                expected = sorted(MEASURED_MOVERS[leaf])
                self.assertEqual(
                    moved, expected,
                    f"{leaf}: measured movers changed since apply-time measurement "
                    f"-- expected {expected}, got {moved}. If this is a genuine, "
                    "understood change, MEASURED_MOVERS must be updated with the "
                    "new measurement, never assumed")


class LockAHonestyTests(unittest.TestCase):
    """Task 4.1 (design.md D6, the M1 finding): `LockADiscoveryTests
    .test_every_declared_name_really_is_that_domain_speaking` searched
    `entry["source"]` -- the profile FILE's own text -- which trivially
    contains every literal in its own `names` list, since that list's
    declaration lives in the same file. Mutation X4: plant
    `"zzz-nothing"` into a scratch profile's `names`. Proven BOTH ways,
    the control this strengthening needs: the OLD check (searching the raw
    source) must be shown SURVIVING it first -- never merely asserted --
    and only then must the NEW check (`profile_values_text`, `vocabulary.
    names` excluded) be shown catching it."""

    #: A minimal, self-contained profile SOURCE -- real enough to exercise
    #: both checks, never the shipped file (which this test does not touch).
    _SCRATCH_PROFILE_SRC = (
        "PROFILE = {\n"
        "    'kit': {'root': '/scratch/skill'},\n"
        "    'vocabulary': {\n"
        "        'subject_singular': 'widget',\n"
        "        'names': ['widget', 'zzz-nothing'],\n"
        "    },\n"
        "}\n"
    )

    @staticmethod
    def _old_check(source: str, names: list[str]) -> list[str]:
        """The check as it stood before D6: searches the profile FILE's own
        source text -- the vacuous shape M1 found."""
        lower_source = source.lower()
        return [n for n in names if n.lower() not in lower_source]

    @staticmethod
    def _new_check(profile: dict, names: list[str]) -> list[str]:
        """The strengthened check (design.md D6): searches the profile's
        declared VALUES, `vocabulary.names` itself excluded -- reimplemented
        inline here rather than imported from
        `test_implementation_domain_lock.py`, mirroring
        `LockBHonestyTests`'s own established precedent of duplicating the
        scan rather than importing across test files."""
        parts: list[str] = []

        def walk(value, path):
            if path == ("vocabulary", "names"):
                return
            if isinstance(value, dict):
                for key, val in value.items():
                    walk(val, path + (key,))
            elif isinstance(value, (list, tuple)):
                for item in value:
                    walk(item, path)
            else:
                parts.append(str(value))

        walk(profile, ())
        haystack = " ".join(parts).lower()
        return [n for n in names if n.lower() not in haystack]

    def test_the_old_check_survives_a_planted_name_and_the_new_check_catches_it(self):
        names = ["widget", "zzz-nothing"]
        profile = {
            "kit": {"root": "/scratch/skill"},
            "vocabulary": {"subject_singular": "widget",
                          "names": list(names)},
        }

        # X4: `"zzz-nothing"` is planted into `names` with no other profile
        # leaf carrying it. The OLD check, searching the FILE'S OWN source,
        # finds it trivially -- it is written right there, in the `names`
        # list literal -- and SURVIVES: this is the control proving the
        # strengthening did something, per task 4.1's own acceptance
        # condition.
        old_unused = self._old_check(self._SCRATCH_PROFILE_SRC, names)
        self.assertEqual(
            old_unused, [],
            "the OLD check did not survive the planted name -- the control "
            "is invalid: it should have found 'zzz-nothing' vacuously "
            "present in the file's own source and reported nothing unused")

        # The NEW check, searching declared VALUES with `vocabulary.names`
        # excluded, catches it: "zzz-nothing" is not `subject_singular`'s
        # value, not `kit.root`'s, not anything but its own declaration.
        new_unused = self._new_check(profile, names)
        self.assertEqual(
            new_unused, ["zzz-nothing"],
            "the strengthened check did not catch the planted name -- it "
            "should report 'zzz-nothing' as unused by any OTHER profile "
            "value")


class LockBHonestyTests(unittest.TestCase):
    """14.5: plant a declared `vocabulary.names` word anywhere in `engine/`
    (including a comment); Lock B must redden, naming the file and word;
    revert; green. Proven against a SCRATCH COPY of the engine file, never
    the shipped one -- Lock B's own test already proves the shipped file is
    clean (test_implementation_domain_lock.py); this proves the LOCK ITSELF
    is not vacuously green."""

    def test_a_planted_names_word_reddens_lock_b_and_reverting_restores_green(self):
        import re
        real_source = (ENGINE_DIR / "implementation_engine.py").read_text(encoding="utf-8")

        # Before: the real file carries none of the planted word.
        planted_word = "formulation"
        self.assertNotIn(planted_word, real_source.lower())

        with tempfile.TemporaryDirectory() as tmp:
            scratch_engine_dir = Path(tmp) / "engine"
            scratch_engine_dir.mkdir()
            planted_source = real_source + f"\n# a planted {planted_word} comment\n"
            (scratch_engine_dir / "implementation_engine.py").write_text(
                planted_source, encoding="utf-8")

            # Reddens: a Lock-B-shaped scan over the SCRATCH directory finds it.
            leaks_with_plant = []
            for path in sorted(scratch_engine_dir.rglob("*.py")):
                source = path.read_text(encoding="utf-8")
                if re.search(rf"\b{planted_word}\b", source, re.IGNORECASE):
                    leaks_with_plant.append(path.name)
            self.assertEqual(leaks_with_plant, ["implementation_engine.py"])

            # Revert: remove the plant, the scratch copy is clean again.
            (scratch_engine_dir / "implementation_engine.py").write_text(
                real_source, encoding="utf-8")
            leaks_after_revert = []
            for path in sorted(scratch_engine_dir.rglob("*.py")):
                source = path.read_text(encoding="utf-8")
                if re.search(rf"\b{planted_word}\b", source, re.IGNORECASE):
                    leaks_after_revert.append(path.name)
            self.assertEqual(leaks_after_revert, [])


class KitLockHonestyTests(unittest.TestCase):
    """14.6: change `module.py`'s `"equations"` key in a SCRATCH COPY, not
    the shipped file; the kit lock must redden; discard the scratch copy.
    The shipped kit template is never touched (D4: `verify`'s `kitSource`
    compares a materialized target file byte-for-byte against its kit
    template; editing the template would reclassify files in repositories
    this change never opened)."""

    def test_a_scratch_kit_mutation_reddens_the_agreement_and_the_shipped_file_is_untouched(self):
        real_module_path = (
            FORGE / ".claude/skills/proposal-implementation/assets/kit/src/module.py")
        real_source = real_module_path.read_text(encoding="utf-8")
        self.assertIn('"equations": ["{{EQUATION}}"],', real_source)

        with tempfile.TemporaryDirectory() as tmp:
            scratch_module = Path(tmp) / "module.py"
            mutated = real_source.replace(
                '"equations": ["{{EQUATION}}"],', '"claims": ["{{EQUATION}}"],', 1)
            self.assertNotEqual(mutated, real_source)
            scratch_module.write_text(mutated, encoding="utf-8")

            # The lock's own assertion (kit agreement lock #1), run against the
            # SCRATCH file: the declared key set no longer matches claim_key.
            import re
            match = re.search(r"__provenance__\s*=\s*\{(.*?)\n\}", mutated, re.DOTALL)
            self.assertIsNotNone(match)
            keys = set(re.findall(r'"(\w+)":', match.group(1)))
            claim_key = impl.CLAIM_KEY
            self.assertNotEqual(
                keys, {"revision", "sections", claim_key, "invariants"},
                "the scratch mutation should have reddened the kit agreement")

        # The shipped file was never touched by this test.
        self.assertEqual(
            real_module_path.read_text(encoding="utf-8"), real_source)


class SealCorpusUntouchedTests(unittest.TestCase):
    """14.7: `git diff --exit-code tests/seal/` exits 0 at the end of this
    phase -- asserted here via the same mechanism, in-process, rather than
    shelling out from inside the suite."""

    def test_the_seal_corpus_directory_has_no_uncommitted_changes(self):
        import subprocess
        proc = subprocess.run(
            ["git", "diff", "--exit-code", "--", "tests/seal/"],
            cwd=str(FORGE), capture_output=True, text=True)
        self.assertEqual(
            proc.returncode, 0,
            f"tests/seal/ has uncommitted changes:\n{proc.stdout}")


import test_implementation_domain_lock as domain_lock  # noqa: E402  (path set above)


class M5MutationTests(unittest.TestCase):
    """Task 4.7 (design.md D9): X5/X6/X7, each against a SCRATCH COPY of
    the engine only -- never the real engine -- the same mechanism
    `test_implementation_domain_mutation.py` already has for its own
    per-leaf change mutations. Reuses `domain_lock.build_denylist`/
    `discover_profiles` directly (both Python, both this same suite --
    unlike `LockBHonestyTests`'s inline duplication, which exists
    specifically to avoid a shared import between the TS lock and this
    one)."""

    @staticmethod
    def _scratch_engine_dir(real_source: str) -> Path:
        tmp = tempfile.mkdtemp(prefix="m5-scratch-engine-")
        scratch_dir = Path(tmp) / "engine"
        scratch_dir.mkdir()
        (scratch_dir / "implementation_engine.py").write_text(
            real_source, encoding="utf-8")
        return scratch_dir

    def test_x5_a_planted_denylist_word_reddens_test_2(self):
        """Plant a denylist word into a scratch engine copy; the scan
        `test_2_no_unpinned_denylist_word_appears_in_the_engine` performs
        must find it, naming the file and word."""
        real_source = (ENGINE_DIR / "implementation_engine.py").read_text(
            encoding="utf-8")
        denylist = domain_lock.build_denylist(domain_lock.discover_profiles())
        # An unpinned word: present in the denylist, absent from
        # `M5_PINNED_RESIDUE` -- one of the five genuinely-absent words.
        unpinned = [w for w in denylist
                   if w not in domain_lock.M5_PINNED_RESIDUE]
        self.assertGreater(len(unpinned), 0, "no unpinned denylist word to plant")
        planted_word = unpinned[0]
        self.assertNotIn(planted_word, real_source.lower())

        with tempfile.TemporaryDirectory() as tmp:
            scratch_dir = Path(tmp) / "engine"
            scratch_dir.mkdir()
            planted_source = real_source + f"\n# a planted {planted_word} comment\n"
            (scratch_dir / "implementation_engine.py").write_text(
                planted_source, encoding="utf-8")

            leaks = []
            for path in sorted(scratch_dir.rglob("*.py")):
                source = path.read_text(encoding="utf-8")
                if re.search(rf"\b{planted_word}\b", source, re.IGNORECASE):
                    leaks.append(path.name)
            self.assertEqual(leaks, ["implementation_engine.py"])

    def test_x6_deleting_a_pinned_occurrence_reddens_test_3(self):
        """Delete one occurrence of a pinned residue word from a scratch
        engine copy; the count `test_3` measures against that scratch copy
        must disagree with the real pin."""
        real_source = (ENGINE_DIR / "implementation_engine.py").read_text(
            encoding="utf-8")
        word = "materialized"
        pinned_count = domain_lock.M5_PINNED_RESIDUE[word]
        real_count = len(re.findall(rf"\b{word}\b", real_source, re.IGNORECASE))
        self.assertEqual(real_count, pinned_count)

        pattern = re.compile(rf"\b{word}\b", re.IGNORECASE)
        mutated_source = pattern.sub("REMOVED", real_source, count=1)
        mutated_count = len(re.findall(rf"\b{word}\b", mutated_source, re.IGNORECASE))
        self.assertEqual(mutated_count, pinned_count - 1)

    def test_x7_copying_the_siblings_purpose_over_this_norths_empties_the_denylist(self):
        """Copy the sibling's `purpose` text over this north's own; the
        vacuity guard (`test_1`) must fail: with both norths sharing the
        SAME purpose text, every word in it becomes common to both and can
        no longer be a single-owner subject word."""
        profiles = domain_lock.discover_profiles()
        by_name = {entry["skill_name"]: entry["profile"] for entry in profiles}
        sibling = by_name["proposal-implementation"]
        this_skill = by_name["experimental-implementation"]

        mutated_this_skill = dict(this_skill)
        mutated_objective = dict(this_skill["objective"])
        mutated_objective["purpose"] = sibling["objective"]["purpose"]
        mutated_this_skill["objective"] = mutated_objective

        mutated_profiles = [
            {"skill_name": "experimental-implementation",
             "profile": mutated_this_skill},
            {"skill_name": "proposal-implementation", "profile": sibling},
        ]
        denylist = domain_lock.build_denylist(mutated_profiles)
        shared_purpose_words = domain_lock.north_words(
            {"objective": {"purpose": sibling["objective"]["purpose"],
                          "arrival": "", "humanStops": [], "stages": []}})
        self.assertTrue(shared_purpose_words, "no >=5-letter word in the shared purpose")
        for word in shared_purpose_words:
            self.assertNotIn(
                word, denylist,
                f"{word!r} is shared between both norths' purpose text now "
                "and must not remain single-owner")


if __name__ == "__main__":
    unittest.main()
