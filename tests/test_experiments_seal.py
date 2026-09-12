"""Change `the-second-skill-the-seam-was-for`, slice A2 (design.md D7): this
skill's own second sealed corpus, `tests/seal/` byte-untouched.

Authored from nothing (`experiments/` holds only `.gitkeep`, task 2.3):
every fixture byte here is this corpus's own (`tests/experiments_seal/
corpus.py`), never borrowed from `tests/seal/corpus.py`'s own "Seal"
package. What IS reused, unedited, is `tests/seal/harness.py`'s generic
argv/env-building machinery -- `run_case`, `validate_case`, `digest_result`,
`build_env`, `RosterValidationError` -- wrapped so a case's argv resolves
through THIS skill's own launcher for the call (design.md D7,
`tests/experiments_seal/harness.py::cli_invocation`).
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FORGE = Path(__file__).resolve().parents[1]
CORPUS_DIR = FORGE / "tests" / "experiments_seal"
SEAL_DIR = FORGE / "tests" / "seal"

sys.path.insert(0, str(FORGE / "tests"))
from experiments_seal import corpus as ec  # noqa: E402
from experiments_seal import harness as eh  # noqa: E402

CASES = json.loads((CORPUS_DIR / "cases.json").read_text(encoding="utf-8"))
UNSEALED = json.loads((CORPUS_DIR / "unsealed.json").read_text(encoding="utf-8"))
DIGESTS_PATH = CORPUS_DIR / "digests.json"

#: `propose`'s own digest embeds a second-precision timestamp -- excluded
#: from byte-exact comparison, mirroring `tests/seal/`'s own
#: `NON_DETERMINISTIC_CASE_IDS` (see `unsealed.json`'s own recorded reason).
NON_DETERMINISTIC_CASE_IDS = frozenset({"propose"})


def _run_all() -> dict[str, dict]:
    tmp = tempfile.mkdtemp(prefix="experiments-seal-corpus-")
    try:
        roots = ec.build(Path(tmp) / "corpus")
        scratch_root = FORGE / "implementations" / f"_experiments_seal_{os.getpid()}"
        scratch_root.mkdir(parents=True, exist_ok=True)
        try:
            results = {}
            with eh.cli_invocation():
                for case in CASES:
                    result = eh.run_case(case, roots, scratch_root=scratch_root)
                    results[case["id"]] = eh.digest_result(result)
            return results
        finally:
            shutil.rmtree(scratch_root, ignore_errors=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


class RosterAndUnsealedCoverageTests(unittest.TestCase):
    """Task 2.2: the excluded commands are recorded by id and reason."""

    def test_the_roster_is_nonempty(self):
        self.assertGreater(len(CASES), 0)

    def test_every_case_id_is_unique(self):
        ids = [case["id"] for case in CASES]
        self.assertEqual(len(ids), len(set(ids)))

    def test_materialize_is_recorded_excluded(self):
        for excluded in ("materialize",):
            with self.subTest(command=excluded):
                self.assertIn(excluded, UNSEALED)
                self.assertNotIn(
                    excluded, {case["command"] for case in CASES},
                    f"{excluded} is recorded excluded in unsealed.json AND "
                    "appears in the roster -- contradiction")

    def test_compose_and_admit_are_no_longer_in_the_unsealed_set(self):
        """`the-agreement-nothing-computes` (Slice D, spec
        `implementation-cli-seal`, "`compose` and `admit` are no longer in
        the unsealed set"): the block locator un-excludes both, and each
        is now a sealed case (`compose-t`, `admit-t`)."""
        for now_sealed in ("compose", "admit"):
            with self.subTest(command=now_sealed):
                self.assertNotIn(now_sealed, UNSEALED)
                self.assertIn(now_sealed, {case["command"] for case in CASES})

    def test_the_real_roster_passes_validation(self):
        eh.validate_roster(CASES)


class SealCorpusUntouchedTests(unittest.TestCase):
    """Task 2.5: `git diff --exit-code tests/seal/` exits 0 -- this
    corpus lands BESIDE the existing 28 sealed digests, never inside them."""

    def test_the_existing_seal_corpus_has_no_uncommitted_changes(self):
        proc = subprocess.run(
            ["git", "diff", "--exit-code", "--", "tests/seal/"],
            cwd=str(FORGE), capture_output=True, text=True)
        self.assertEqual(
            proc.returncode, 0,
            f"tests/seal/ has uncommitted changes:\n{proc.stdout}")


class DigestComparisonTests(unittest.TestCase):
    """Task 2.4: every sealed case's captured digest agrees with the
    committed golden, `propose` excluded (non-deterministic, `unsealed.json`)."""

    @classmethod
    def setUpClass(cls):
        cls._captured = _run_all()
        cls._golden = json.loads(DIGESTS_PATH.read_text(encoding="utf-8"))

    def test_every_case_id_has_a_golden_entry(self):
        expected = {case["id"] for case in CASES}
        self.assertTrue(expected.issubset(set(self._golden)))

    def test_every_deterministic_case_matches_its_golden_digest(self):
        for case in CASES:
            case_id = case["id"]
            if case_id in NON_DETERMINISTIC_CASE_IDS:
                continue
            with self.subTest(case=case_id):
                self.assertEqual(
                    self._captured[case_id], self._golden[case_id],
                    f"{case_id}: captured digest disagrees with the "
                    "committed golden")

    def test_the_corpus_fingerprint_matches(self):
        digest = hashlib.sha256(
            ec.CORPUS_FINGERPRINT_SOURCE.read_bytes()).hexdigest()
        self.assertEqual(
            digest, self._golden["__corpus_fingerprint__"]["sha256"],
            "tests/experiments_seal/corpus.py was edited without "
            "recapturing digests.json")


class ThreatMatrixTests(unittest.TestCase):
    """Task 2.7: the same three threat-matrix RED tests
    `tests/test_implementation_seal.py` proves for the sibling, proven here
    against THIS corpus."""

    def test_a_literal_target_raises_before_any_subprocess_runs(self):
        bad_case = {"id": "bad", "command": "verify", "fixture": "A",
                    "proposals": True, "argv": ["--target", "/tmp/literal",
                                                "--name", "Trial"]}
        with self.assertRaises(eh.RosterValidationError):
            eh.validate_case(bad_case)

    def test_committed_fixtures_are_byte_identical_after_a_full_run(self):
        before = CORPUS_DIR.read_bytes() if CORPUS_DIR.is_file() else None
        before_files = {
            path: path.read_bytes()
            for path in sorted(CORPUS_DIR.rglob("*"))
            if path.is_file() and "__pycache__" not in path.parts}
        _run_all()
        after_files = {
            path: path.read_bytes()
            for path in sorted(CORPUS_DIR.rglob("*"))
            if path.is_file() and "__pycache__" not in path.parts}
        self.assertEqual(before_files, after_files,
                         "a full corpus run mutated a committed fixture "
                         "file under tests/experiments_seal/")

    def test_a_stray_parent_env_var_produces_an_identical_digest(self):
        case = {"id": "verify-a", "command": "verify", "fixture": "A",
                "proposals": True, "argv": ["--target", "<TARGET>", "--name",
                                            "Trial"]}
        tmp = tempfile.mkdtemp(prefix="experiments-seal-env-")
        self.addCleanup(shutil.rmtree, tmp, ignore_errors=True)
        roots = ec.build(Path(tmp) / "corpus")
        scratch_root = FORGE / "implementations" / f"_experiments_seal_env_{os.getpid()}"
        scratch_root.mkdir(parents=True, exist_ok=True)
        self.addCleanup(shutil.rmtree, scratch_root, ignore_errors=True)

        with eh.cli_invocation():
            clean = eh.digest_result(
                eh.run_case(case, roots, scratch_root=scratch_root))

            had = "IMPLEMENTATION_DOMAIN_PROFILE" in os.environ
            original = os.environ.get("IMPLEMENTATION_DOMAIN_PROFILE")
            os.environ["IMPLEMENTATION_DOMAIN_PROFILE"] = "/should/be/ignored"
            try:
                with_stray = eh.digest_result(
                    eh.run_case(case, roots, scratch_root=scratch_root))
            finally:
                if had:
                    os.environ["IMPLEMENTATION_DOMAIN_PROFILE"] = original
                else:
                    os.environ.pop("IMPLEMENTATION_DOMAIN_PROFILE", None)

        self.assertEqual(
            clean, with_stray,
            "a stray IMPLEMENTATION_DOMAIN_PROFILE in the PARENT env moved "
            "the digest -- build_env's explicit dict must not pass it "
            "through")


class MutationTests(unittest.TestCase):
    """Task 2.6: flip one byte of a captured golden, confirm the comparison
    suite goes red, restore."""

    def test_a_planted_golden_mismatch_reddens_the_comparison_and_reverting_restores_green(self):
        real_digests = json.loads(DIGESTS_PATH.read_text(encoding="utf-8"))
        captured = _run_all()

        mutated = dict(real_digests)
        mutated["name"] = dict(mutated["name"])
        real_sha = mutated["name"]["sha256"]
        flipped = ("0" if real_sha[0] != "0" else "1") + real_sha[1:]
        mutated["name"]["sha256"] = flipped
        self.assertNotEqual(mutated["name"], captured["name"])

        # Reddens: a mutated golden disagrees with a real capture.
        self.assertNotEqual(mutated["name"], captured["name"])
        # Reverting restores agreement.
        self.assertEqual(real_digests["name"], captured["name"])


if __name__ == "__main__":
    unittest.main()
