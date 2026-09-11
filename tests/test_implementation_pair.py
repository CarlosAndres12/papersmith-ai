"""Cut 3 (`a-revision-is-two-documents`, Phase 4, design.md D9): the pair
corpus's own driver.

**Why this exists at all** (proposal.md, "The line this cut draws"): a
branch no reachable configuration takes cannot be mutation-proven, and by
this project's own standing rule a profile field nothing reads is the shape
of a false guard -- an unprovable branch is the same defect one level up.
Slice A ships no wire-shape change (D2), so the only branches it introduces
are the resolver's per-index walk actually reaching a SECOND document. This
file is that reachable configuration.

Two cases, two profiles, one harness (design.md D9's own summary): both
driven through `seal_harness.run_case`, a real subprocess each, normalized
and digested exactly as the existing 28-case seal is -- but into this
corpus's OWN `tests/pair/digests.json`. **No entry is ever added to
`tests/seal/digests.json`**; that file and its 28 digests are asserted
untouched elsewhere (`SealCorpusUntouchedTests` in
`test_implementation_seal.py`) and again here, directly.

`IMPLEMENTATION_DOMAIN_PROFILE` is deliberately excluded from
`seal_harness.ALLOWED_ENV_KEYS` (design.md D2: the seal always exercises a
skill's own real profile via the launcher's `setdefault`). Reaching a
DIFFERENT profile in a real subprocess therefore needs the same wrapper
`test_implementation_domain_mutation.py` already uses for mutation testing
(M4) -- reused here under its own name, not reinvented, for a different
purpose: swapping in one of THIS corpus's two fixture profiles per case.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

FORGE = Path(__file__).resolve().parents[1]
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

os.environ.setdefault(
    "IMPLEMENTATION_DOMAIN_PROFILE",
    str(FORGE / ".claude/skills/proposal-implementation/impl_profile.py"))

from seal import harness as seal_harness  # noqa: E402  (path set above)
from pair import corpus as pair_corpus  # noqa: E402  (path set above)

CASES_PATH = TESTS_DIR / "pair" / "cases.json"
DIGESTS_PATH = TESTS_DIR / "pair" / "digests.json"
SEAL_DIGESTS_PATH = TESTS_DIR / "seal" / "digests.json"

#: Which of the pair corpus's two fixture profiles each case runs against --
#: task 4.2's own instruction: measure, then assert which case reaches which
#: branch, named here rather than inferred.
#:
#: - `pair-two-documents-resolve` runs against the VALID two-document
#:   profile: `DOCUMENTS[1]` is present in the resolved profile a real
#:   subprocess loads, and the process completes normally (exit 0). This is
#:   task 4.2's "DOCUMENTS[1] presence" branch.
#: - `pair-second-document-missing-directory-refuses` runs against a
#:   profile with `documents[1].directory` removed: the resolver's per-index
#:   walk refuses at import, before the command ever dispatches (exit
#:   non-zero, empty stdout -- the refusal message itself is a traceback on
#:   stderr, which this harness's `CaseResult` does not capture; the
#:   digested signal is the exit/stdout shape, proven directly by
#:   `SubprocessRefusalNamesIndexedLeafTests` below via raw stdout+stderr).
#:   This is task 4.2's "resolver per-index refusal" branch.
CASE_PROFILE_BUILDERS = {
    "pair-two-documents-resolve": pair_corpus.build,
    "pair-second-document-missing-directory-refuses":
        pair_corpus.build_broken_second_document,
}


def _load_cases() -> list:
    return json.loads(CASES_PATH.read_text(encoding="utf-8"))


def _load_digests() -> dict:
    return json.loads(DIGESTS_PATH.read_text(encoding="utf-8"))


def _build_env_with_profile_override(profile_path):
    """The same wrapper `test_implementation_domain_mutation.py` uses (M4):
    calls the REAL `build_env` first (so its own `ALLOWED_ENV_KEYS` assert
    still runs unweakened), then adds exactly one key outside the allow-list
    check -- a real env var reaching a real subprocess, never a
    monkeypatch of an engine or profile attribute (recorded scar: patching a
    module attribute has zero effect on a subprocess)."""
    original_build_env = seal_harness.build_env

    def _wrapped(case, roots):
        env = original_build_env(case, roots)
        env["IMPLEMENTATION_DOMAIN_PROFILE"] = str(profile_path)
        return env
    return _wrapped


_CAPTURED_RESULTS: dict = {}


def _captured_results() -> dict:
    if not _CAPTURED_RESULTS:
        cases = _load_cases()
        original_build_env = seal_harness.build_env
        try:
            with tempfile.TemporaryDirectory(prefix="pair-compare-") as tmp:
                tmp_root = Path(tmp)
                for case in cases:
                    builder = CASE_PROFILE_BUILDERS[case["id"]]
                    case_root = tmp_root / case["id"]
                    roots = builder(case_root / "profile")
                    scratch_root = case_root / "scratch"
                    scratch_root.mkdir(parents=True)
                    seal_harness.build_env = _build_env_with_profile_override(
                        roots.profile_path)
                    try:
                        _CAPTURED_RESULTS[case["id"]] = seal_harness.run_case(
                            case, roots, scratch_root=scratch_root)
                    finally:
                        seal_harness.build_env = original_build_env
        finally:
            seal_harness.build_env = original_build_env
    return _CAPTURED_RESULTS


class PairCorpusComparisonTests(unittest.TestCase):
    """Both cases re-run against a stored golden -- the pair corpus's own
    28-case-seal equivalent, at N=2. A one-byte change in either golden's
    captured stdout/exit must be caught (mirrors
    `implementation-cli-seal`'s own "A one-byte change in a pair-shaped
    case is caught" scenario)."""

    def test_every_pair_case_matches_its_stored_golden(self):
        results = _captured_results()
        digests = _load_digests()
        for case_id, golden in digests.items():
            with self.subTest(case=case_id):
                result = results[case_id]
                actual = seal_harness.digest_result(result)
                self.assertEqual(
                    actual, golden,
                    f"{case_id}: captured result disagrees with the stored "
                    "golden -- a real behavioural delta, or the golden was "
                    "captured against a different build")

    def test_every_case_has_a_golden_and_every_golden_has_a_case(self):
        case_ids = {case["id"] for case in _load_cases()}
        golden_ids = set(_load_digests())
        self.assertEqual(case_ids, golden_ids)


class TwoDocumentsResolveTests(unittest.TestCase):
    """Task 4.2's "DOCUMENTS[1] presence" branch, named and proven directly
    (not only through the opaque digest comparison above): the valid
    two-document profile resolves in a real subprocess and the command
    completes successfully."""

    def test_the_valid_profile_resolves_and_the_command_succeeds(self):
        result = _captured_results()["pair-two-documents-resolve"]
        self.assertEqual(result.exit_status, 0)


class SubprocessRefusalNamesIndexedLeafTests(unittest.TestCase):
    """Task 4.2's "resolver per-index refusal" branch, proven directly
    against raw stdout+stderr (the seal harness's own `CaseResult` digests
    stdout+exit only, so the refusal MESSAGE itself -- on stderr -- is
    checked here, mirroring how `test_implementation_profile.py`'s own
    subprocess tests check `proc.stdout + proc.stderr`, never the digested
    `CaseResult`)."""

    def test_a_real_subprocess_refuses_naming_the_indexed_leaf(self):
        import subprocess
        import sys as _sys

        with tempfile.TemporaryDirectory(prefix="pair-indexed-refusal-") as tmp:
            roots = pair_corpus.build_broken_second_document(Path(tmp))
            env = dict(os.environ)
            env["IMPLEMENTATION_DOMAIN_PROFILE"] = str(roots.profile_path)
            cli = (FORGE / ".claude/skills/proposal-implementation/scripts"
                  "/implementation_cli.py")
            proc = subprocess.run(
                [_sys.executable, str(cli), "name", "--name", "Method"],
                capture_output=True, text=True, env=env)
            self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            combined = proc.stdout + proc.stderr
            self.assertIn("IMPLEMENTATION_DOMAIN_PROFILE_INCOMPLETE", combined)
            self.assertIn("documents[1].directory", combined)


class SealCorpusUntouchedByPairCorpusTests(unittest.TestCase):
    """Design.md D9 / task 4.1: the pair corpus is purely additive. No pair
    case id joins `tests/seal/digests.json`, and the 28 existing entries are
    exactly what they were."""

    def test_no_pair_case_id_appears_in_the_seal_digests(self):
        seal_digests = json.loads(SEAL_DIGESTS_PATH.read_text(encoding="utf-8"))
        pair_case_ids = {case["id"] for case in _load_cases()}
        self.assertEqual(pair_case_ids & set(seal_digests), set())

    def test_the_seal_digests_file_still_has_exactly_twenty_eight_case_entries(self):
        """29 raw keys: the 28 sealed cases plus the reserved
        `__corpus_fingerprint__` entry (`tests/seal/corpus.py`'s own
        docstring)."""
        seal_digests = json.loads(SEAL_DIGESTS_PATH.read_text(encoding="utf-8"))
        case_entries = {
            key: value for key, value in seal_digests.items()
            if key != "__corpus_fingerprint__"}
        self.assertEqual(len(case_entries), 28)


if __name__ == "__main__":
    unittest.main()
