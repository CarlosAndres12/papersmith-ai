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
TESTS_DIR = Path(__file__).resolve().parent
if str(TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(TESTS_DIR))

os.environ.setdefault(
    "IMPLEMENTATION_DOMAIN_PROFILE",
    str(FORGE / ".claude/skills/proposal-implementation/impl_profile.py"))

from seal import harness as seal_harness  # noqa: E402  (path set above)
from pair import corpus as pair_corpus  # noqa: E402  (path set above)
import impl_position  # noqa: E402  (path set by seal_harness's own import)

#: Cut 3 corrective apply (verify FAIL, CRITICAL finding): the real CLI
#: entry point, the same one every subprocess case in this suite already
#: runs against -- needed directly (not only through `seal_harness.run_case`)
#: by the stateful lifecycle classes below, whose whole point is ledger
#: state accumulated ACROSS several real subprocess calls against the same
#: target, something the single-command golden-digest mechanism cannot
#: represent (`seal_harness.run_case` gives every case a fresh scratch
#: target).
CLI = FORGE / ".claude/skills/proposal-implementation/scripts/implementation_cli.py"

CASES_PATH = TESTS_DIR / "pair" / "cases.json"
DIGESTS_PATH = TESTS_DIR / "pair" / "digests.json"
#: Re-verify (Cut 3, second correction) WARNING 2: the spec's own named
#: escape valve for "a branch that cannot be captured as a byte-exact
#: golden" (`tests/seal/unsealed.json`'s pattern), replicated here for this
#: corpus so the set of exempt cases is a declared, enforced membership --
#: never a silent absence.
UNSEALED_PATH = TESTS_DIR / "pair" / "unsealed.json"
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


def _load_unsealed() -> dict:
    return json.loads(UNSEALED_PATH.read_text(encoding="utf-8"))


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


class PairCorpusMembershipTests(unittest.TestCase):
    """Re-verify (Cut 3, second correction) WARNING 2: `tests/seal/unsealed.
    json`'s own escape valve for "a branch that cannot be captured as a
    byte-exact golden" (its own `SealMembershipTests`), mirrored here for
    `tests/pair/`. Both of this corpus's two existing cases already have
    goldens (proven above), so the correct membership today is the empty
    set -- asserted, not merely absent, so a case added later with neither
    a golden nor a declared reason is caught instead of silently dropping
    through."""

    #: A literal, not derived -- growing this requires editing the test,
    #: the same deliberate friction `tests/seal/unsealed.json`'s own
    #: `SealMembershipTests.EXPECTED_UNSEALED` uses.
    EXPECTED_UNSEALED = frozenset()

    def test_every_pair_case_is_either_sealed_or_declared_unsealed(self):
        cases = {case["id"] for case in _load_cases()}
        digests = set(_load_digests())
        unsealed = set(_load_unsealed())
        self.assertEqual(digests | unsealed, cases)
        self.assertEqual(digests & unsealed, set())

    def test_the_unsealed_set_is_exactly_its_declared_membership(self):
        self.assertEqual(frozenset(_load_unsealed()), self.EXPECTED_UNSEALED)

    def test_every_unsealed_entry_states_a_reason(self):
        for case_id, reason in _load_unsealed().items():
            with self.subTest(case=case_id):
                self.assertIsInstance(reason, str)
                self.assertGreaterEqual(len(reason), 20)


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


class AuthorizationBindingKeysPresenceBranchTests(unittest.TestCase):
    """Corrective apply, Cut 3 (verify FAIL, CRITICAL finding), instruction
    2: a DIRECT proof of `_authorization_binding_keys`'s presence-gated
    branch -- independent of the full gate/offer subprocess machinery in
    `TwoDocumentLifecycleTests` below, which also reaches it (via a real
    minted token's own `gate_binding` re-derivation) but depends on git,
    job folders and a file-based capacity adapter. This class needs none
    of that: `_authorization_binding_keys` is a pure function over
    whatever mapping it is handed, so its presence branch is provable with
    no subprocess at all -- reusing `seal_harness.impl`, the identical
    already-imported engine module every other file in this suite reads,
    never a second import of it."""

    def test_documentrevisions_present_grows_the_ninth_key(self):
        base = dict.fromkeys(seal_harness.impl._AUTHORIZATION_BINDING_KEYS, None)
        binding = {**base, "documentRevisions": [
            {"label": "experiments", "revision": "r1.md", "sha256": None}]}
        keys = seal_harness.impl._authorization_binding_keys(binding)
        self.assertIn("documentRevisions", keys)
        self.assertEqual(len(keys), 9)

    def test_documentrevisions_absent_stays_at_eight_keys(self):
        binding = dict.fromkeys(seal_harness.impl._AUTHORIZATION_BINDING_KEYS, None)
        keys = seal_harness.impl._authorization_binding_keys(binding)
        self.assertNotIn("documentRevisions", keys)
        self.assertEqual(len(keys), 8)
        self.assertEqual(set(keys), set(seal_harness.impl._AUTHORIZATION_BINDING_KEYS))


class DiscoverDocumentRevisionTests(unittest.TestCase):
    """`each-document-names-its-own-revision`, D1 / design.md's Testing
    Strategy ("Unit | discover_document_revision | marker-owned /
    hand-authored / tie / empty / ambiguous, each its own case"). A pure
    filesystem read, driven directly by `IMPLEMENTATION_PROPOSALS_1` --
    the identical override `ExtraDocumentFidelityStatusTests`
    (test_proposal_implementation.py) already uses for the sibling
    per-document function one call site over -- so no subprocess is
    needed to exercise it. The ambiguous-family case is proven separately,
    end to end through a real subprocess refusal
    (`TwoDocumentAmbiguousFamilyRefusesTests`, Phase 3), since that one
    needs the refusal's own code and detail, not only this function's
    `families` field.
    """

    def _root(self) -> Path:
        root = Path(tempfile.mkdtemp(prefix="discover-doc-"))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        previous = os.environ.get("IMPLEMENTATION_PROPOSALS_1")
        os.environ["IMPLEMENTATION_PROPOSALS_1"] = str(root)

        def restore():
            if previous is None:
                os.environ.pop("IMPLEMENTATION_PROPOSALS_1", None)
            else:
                os.environ["IMPLEMENTATION_PROPOSALS_1"] = previous
        self.addCleanup(restore)
        return root

    def test_an_empty_root_answers_no_revision(self):
        self._root()
        result = seal_harness.impl.discover_document_revision(1)
        self.assertIsNone(result["revision"])
        self.assertEqual(result["families"], [])
        self.assertEqual(result["tied"], [])

    def test_a_hand_authored_root_picks_the_digit_tuple_max(self):
        root = self._root()
        (root / "draft-1.md").write_text("one", encoding="utf-8")
        (root / "draft-2.md").write_text("two", encoding="utf-8")
        result = seal_harness.impl.discover_document_revision(1)
        self.assertEqual(result["revision"], "draft-2.md")
        self.assertFalse(result["markerOwned"])
        self.assertEqual(result["tied"], [])

    def test_a_real_tie_on_the_digit_tuple_is_reported(self):
        root = self._root()
        (root / "draft-1.md").write_text("a", encoding="utf-8")
        (root / "draft-01.md").write_text("b", encoding="utf-8")
        result = seal_harness.impl.discover_document_revision(1)
        self.assertEqual(sorted(result["tied"]), ["draft-01.md", "draft-1.md"])

    def test_a_marker_owned_root_excludes_unmarked_candidates(self):
        root = self._root()
        (root / "draft-1.md").write_text("plain, unmarked", encoding="utf-8")
        (root / "draft-2.md").write_bytes(
            seal_harness.impl.MANAGED_ARTIFACT_MARKER + b"managed\n")
        result = seal_harness.impl.discover_document_revision(1)
        self.assertEqual(result["revision"], "draft-2.md")
        self.assertTrue(result["markerOwned"])
        self.assertEqual(result["nonManaged"], ["draft-1.md"])

    def test_not_a_directory_answers_the_identical_empty_shape(self):
        os.environ["IMPLEMENTATION_PROPOSALS_1"] = str(
            Path(tempfile.mkdtemp(prefix="discover-doc-missing-")) / "absent")
        self.addCleanup(os.environ.pop, "IMPLEMENTATION_PROPOSALS_1", None)
        result = seal_harness.impl.discover_document_revision(1)
        self.assertEqual(
            result,
            {"revision": None, "markerOwned": False, "nonManaged": [],
             "tied": [], "families": []})


class DocumentRevisionNamesMemoTests(unittest.TestCase):
    """design.md D2: the memo's cache key carries `(revision, *roots)`,
    never `revision` alone. Re-pointing `IMPLEMENTATION_PROPOSALS_1`
    between two calls in the same process, with the SAME `revision`
    argument both times, must change the second call's answer -- a bare-
    argument cache (e.g. a naive `functools.lru_cache`) would instead
    return the first call's now-stale answer."""

    def test_repointing_the_root_between_two_calls_changes_the_answer(self):
        # `document_revision_names` loops `range(1, len(DOCUMENTS))`, and
        # this test process's own `IMPLEMENTATION_DOMAIN_PROFILE` (set at
        # module import, above) declares exactly one document -- the real
        # skill's shipped profile every other file in this suite shares.
        # `DOCUMENTS` is reassigned here, in-process, to a genuine
        # two-entry list purely so the memo's OWN loop runs a second
        # iteration; this never touches a subprocess (which always reads
        # its own environment's real profile), so the recorded scar
        # ("monkeypatching a module attribute has ZERO effect on a
        # subprocess") does not apply -- nothing here is reached by one.
        impl = seal_harness.impl
        original_documents = impl.DOCUMENTS
        original_cache = dict(impl._DOCUMENT_NAME_CACHE)
        impl._DOCUMENT_NAME_CACHE.clear()
        impl.DOCUMENTS = [
            {"directory": original_documents[0]["directory"], "label": "proposal"},
            {"directory": Path("/nonexistent/memo-doc1"), "label": "experiments"},
        ]

        def restore():
            impl.DOCUMENTS = original_documents
            impl._DOCUMENT_NAME_CACHE.clear()
            impl._DOCUMENT_NAME_CACHE.update(original_cache)
        self.addCleanup(restore)

        root_a = Path(tempfile.mkdtemp(prefix="memo-root-a-"))
        self.addCleanup(shutil.rmtree, root_a, ignore_errors=True)
        (root_a / "draft-1.md").write_text("a", encoding="utf-8")

        root_b = Path(tempfile.mkdtemp(prefix="memo-root-b-"))
        self.addCleanup(shutil.rmtree, root_b, ignore_errors=True)
        (root_b / "draft-9.md").write_text("b", encoding="utf-8")

        previous = os.environ.get("IMPLEMENTATION_PROPOSALS_1")

        def restore_env():
            if previous is None:
                os.environ.pop("IMPLEMENTATION_PROPOSALS_1", None)
            else:
                os.environ["IMPLEMENTATION_PROPOSALS_1"] = previous
        self.addCleanup(restore_env)

        os.environ["IMPLEMENTATION_PROPOSALS_1"] = str(root_a)
        first = impl.document_revision_names("r1.md")

        os.environ["IMPLEMENTATION_PROPOSALS_1"] = str(root_b)
        second = impl.document_revision_names("r1.md")

        self.assertEqual(first[1], "draft-1.md")
        self.assertEqual(second[1], "draft-9.md")
        self.assertNotEqual(
            first[1], second[1],
            "the SAME revision argument against two different roots must "
            "resolve to two different document-1 names -- a cache keyed "
            "on revision alone would instead serve the first root's "
            "now-stale answer")


class TwoDocumentPositionWriteTests(unittest.TestCase):
    """Corrective apply, Cut 3 (verify FAIL, CRITICAL finding): `cmd_
    position`'s own four `len(DOCUMENTS) > 1` sites (C2), each reached by a
    real subprocess `position` call against a fresh product directory
    under the two-document fixture profile -- absent (no block yet),
    install (a fresh write), then an unchanged refresh. `TwoDocument
    LifecycleTests` below also reaches the WRITE branch once, incidentally,
    through `close`'s own internal refresh call; this class is the direct,
    three-call proof of all four sites C2 itself owns, isolated from the
    rest of the lifecycle."""

    REVISION = "pair-position-r01.md"
    REVISION_1 = "pair-position-plan-v01.md"
    REVISION_TEXT = "## 1\ntexto.\n"
    PACKAGE = "PositionOnly"

    def setUp(self):
        profile_root = Path(tempfile.mkdtemp(prefix="pair-position-profile-"))
        self.addCleanup(shutil.rmtree, profile_root, ignore_errors=True)
        self.profile_roots = pair_corpus.build(profile_root)

        self.doc0 = Path(tempfile.mkdtemp(prefix="pair-position-doc0-"))
        self.addCleanup(shutil.rmtree, self.doc0, ignore_errors=True)
        (self.doc0 / self.REVISION).write_text(self.REVISION_TEXT, encoding="utf-8")

        self.doc1 = Path(tempfile.mkdtemp(prefix="pair-position-doc1-"))
        self.addCleanup(shutil.rmtree, self.doc1, ignore_errors=True)
        (self.doc1 / self.REVISION_1).write_text(
            "Document 1's own position-only text -- a real, independently "
            "readable file at DOCUMENTS[1]'s own directory.\n",
            encoding="utf-8")

        self.box = FORGE / "implementations" / f"_pair_position_{os.getpid()}_{id(self)}"
        self.addCleanup(shutil.rmtree, self.box, ignore_errors=True)
        self.box.mkdir(parents=True)
        env = dict(os.environ)
        env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "pair-position"
        env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = "pair-position@example.invalid"
        subprocess.run(["git", "init", "-q", str(self.box)], check=True, capture_output=True)
        (self.box / self.PACKAGE).mkdir(parents=True)
        # A candidate holder, exactly `tests/seal/corpus.py`'s own fixture
        # placeholder: `_chosen_holder` (used by a fresh `--sequence`
        # install) never invents a checklist file, it only ever picks
        # among candidates `agreements_state` already found -- an empty
        # product dir refuses `POSITION_HOLDER_ABSENT` before the install
        # below ever gets to write anything.
        (self.box / self.PACKAGE / "AGREED.md").write_text(
            "# Agreed\n\n## Ladder\n\n- [ ] First measurable claim.\n",
            encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.box, env=env, check=True,
                       capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=self.box, env=env,
                       check=True, capture_output=True)

    def run_cli(self, *args):
        env = dict(os.environ)
        env["IMPLEMENTATION_DOMAIN_PROFILE"] = str(self.profile_roots.profile_path)
        env["IMPLEMENTATION_PROPOSALS"] = str(self.doc0)
        env["IMPLEMENTATION_PROPOSALS_1"] = str(self.doc1)
        return subprocess.run([sys.executable, str(CLI), *args],
                              capture_output=True, text=True, cwd=FORGE, env=env)

    def _doc1_sha256(self) -> str:
        return hashlib.sha256((self.doc1 / self.REVISION_1).read_bytes()).hexdigest()

    def test_absent_install_then_unchanged_all_carry_the_documents_group(self):
        # L10771 (cmd_position's own "nothing to refresh" branch): no
        # block exists yet, and the additive `documents` key is present
        # even here.
        absent = self.run_cli("position", "--target", str(self.box), "--name",
                              self.PACKAGE, "--revision", self.REVISION,
                              "--session", "s1")
        self.assertEqual(absent.returncode, 0, absent.stdout + absent.stderr)
        absent_result = json.loads(absent.stdout)
        self.assertEqual(absent_result["status"], "absent")
        self.assertIn("documents", absent_result)
        self.assertEqual(
            absent_result["documents"],
            [{"label": "experiments", "revision": self.REVISION_1,
              "revisionSha256": self._doc1_sha256()}])

        # L10836 (header gains the group) / L10946 (ledger event) / L10956
        # (final written return): a fresh INSTALL.
        sequence = json.dumps([{"text": "First step.", "witness": {"kind": "record"}}])
        install = self.run_cli("position", "--target", str(self.box), "--name",
                               self.PACKAGE, "--revision", self.REVISION,
                               "--session", "s1", "--sequence", sequence,
                               "--target-level", "final")
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)
        install_result = json.loads(install.stdout)
        self.assertEqual(install_result["status"], "written")
        self.assertIn("documents", install_result)
        self.assertEqual(
            install_result["documents"],
            [{"label": "experiments", "revision": self.REVISION_1,
              "revisionSha256": self._doc1_sha256()}])
        agreed = (self.box / self.PACKAGE / "AGREED.md").read_text(encoding="utf-8")
        self.assertIn("documents=", agreed)
        ledger = self.box / self.PACKAGE / ".implementation" / "position.jsonl"
        events = [json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(len(events), 1)
        self.assertIn("documents", events[-1])

        # L10923 (the unchanged branch's own additive `documents`
        # comparison): an identical second call finds nothing derived
        # moved, so it must compare the `documents` group too, not only
        # the pre-Cut-3 three scalar fields.
        refresh = self.run_cli("position", "--target", str(self.box), "--name",
                               self.PACKAGE, "--revision", self.REVISION,
                               "--session", "s1", "--target-level", "final")
        self.assertEqual(refresh.returncode, 0, refresh.stdout + refresh.stderr)
        refresh_result = json.loads(refresh.stdout)
        self.assertEqual(refresh_result["status"], "unchanged")
        self.assertIn("documents", refresh_result)
        events_after_refresh = [
            json.loads(line) for line in ledger.read_text(encoding="utf-8").splitlines()]
        self.assertEqual(
            len(events_after_refresh), 1,
            "an unchanged refresh must append no second ledger event")


class DocumentOneBoundToTests(unittest.TestCase):
    """design.md D7 / M4: `boundTo["experiments"]` (`position_state`'s
    multi branch) reports `current`, then `stale` after document 1's own
    file changes -- the value M4 measured as unreachable before
    `extra_sources` was ever wired to a real call site. A real subprocess
    `position --sequence` install records document 1's sha into the
    header's own `documents=` group first (the group must exist before
    `current`/`stale` is even a meaningful question -- see
    `position_state`'s own "never recorded" branch); `probe` then reads
    `current` against the unchanged file, and `stale` after the file's
    own bytes are rewritten underneath it, with no second `position` call
    in between."""

    REVISION = "pair-boundto-r01.md"
    REVISION_1 = "pair-boundto-plan-v01.md"
    REVISION_TEXT = "## 1\ntexto.\n"
    PACKAGE = "BoundToOnly"

    def setUp(self):
        profile_root = Path(tempfile.mkdtemp(prefix="pair-boundto-profile-"))
        self.addCleanup(shutil.rmtree, profile_root, ignore_errors=True)
        self.profile_roots = pair_corpus.build(profile_root)

        self.doc0 = Path(tempfile.mkdtemp(prefix="pair-boundto-doc0-"))
        self.addCleanup(shutil.rmtree, self.doc0, ignore_errors=True)
        (self.doc0 / self.REVISION).write_text(self.REVISION_TEXT, encoding="utf-8")

        self.doc1 = Path(tempfile.mkdtemp(prefix="pair-boundto-doc1-"))
        self.addCleanup(shutil.rmtree, self.doc1, ignore_errors=True)
        (self.doc1 / self.REVISION_1).write_text(
            "Document 1's own bound-to text, version one.\n", encoding="utf-8")

        self.box = FORGE / "implementations" / f"_pair_boundto_{os.getpid()}_{id(self)}"
        self.addCleanup(shutil.rmtree, self.box, ignore_errors=True)
        self.box.mkdir(parents=True)
        env = dict(os.environ)
        env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "pair-boundto"
        env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = "pair-boundto@example.invalid"
        subprocess.run(["git", "init", "-q", str(self.box)], check=True, capture_output=True)
        (self.box / self.PACKAGE).mkdir(parents=True)
        (self.box / self.PACKAGE / "AGREED.md").write_text(
            "# Agreed\n\n## Ladder\n\n- [ ] First measurable claim.\n",
            encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.box, env=env, check=True,
                       capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=self.box, env=env,
                       check=True, capture_output=True)

    def run_cli(self, *args):
        env = dict(os.environ)
        env["IMPLEMENTATION_DOMAIN_PROFILE"] = str(self.profile_roots.profile_path)
        env["IMPLEMENTATION_PROPOSALS"] = str(self.doc0)
        env["IMPLEMENTATION_PROPOSALS_1"] = str(self.doc1)
        return subprocess.run([sys.executable, str(CLI), *args],
                              capture_output=True, text=True, cwd=FORGE, env=env)

    def test_current_then_stale_after_document_one_changes(self):
        sequence = json.dumps([{"text": "First step.", "witness": {"kind": "record"}}])
        install = self.run_cli(
            "position", "--target", str(self.box), "--name", self.PACKAGE,
            "--revision", self.REVISION, "--session", "s1",
            "--sequence", sequence, "--target-level", "final")
        self.assertEqual(install.returncode, 0, install.stdout + install.stderr)

        probe_current = self.run_cli(
            "probe", "--target", str(self.box), "--name", self.PACKAGE,
            "--revision", self.REVISION)
        self.assertEqual(probe_current.returncode, 0,
                         probe_current.stdout + probe_current.stderr)
        bound_to_current = json.loads(probe_current.stdout)["position"]["boundTo"]
        self.assertEqual(bound_to_current["experiments"], "current")

        (self.doc1 / self.REVISION_1).write_text(
            "Document 1's own bound-to text, version TWO -- changed after "
            "the position was recorded.\n", encoding="utf-8")

        probe_stale = self.run_cli(
            "probe", "--target", str(self.box), "--name", self.PACKAGE,
            "--revision", self.REVISION)
        self.assertEqual(probe_stale.returncode, 0,
                         probe_stale.stdout + probe_stale.stderr)
        bound_to_stale = json.loads(probe_stale.stdout)["position"]["boundTo"]
        self.assertEqual(bound_to_stale["experiments"], "stale")


class TwoDocumentAmbiguousFamilyRefusesTests(unittest.TestCase):
    """design.md D3/D5: a declared document beyond document 0 whose own
    directory holds candidates from TWO different revision families is
    ambiguous -- neither this side's convention to pick. A real subprocess
    `position` call (a binding-write site) refuses `DOCUMENT_REVISION_
    UNREADABLE`, exit code 2, with a `detail` naming both families. This
    is the corpus case D5's own mutation test (below) needs: independent
    of, and not satisfiable merely by, fixture data written to pass it --
    document 1's directory here genuinely holds two readable, distinct
    families, so only the refusal itself (never a sha/documents
    assertion) can tell the correct behaviour from the mutated one."""

    REVISION = "pair-ambiguous-r01.md"
    PACKAGE = "AmbiguousOnly"

    def setUp(self):
        profile_root = Path(tempfile.mkdtemp(prefix="pair-ambiguous-profile-"))
        self.addCleanup(shutil.rmtree, profile_root, ignore_errors=True)
        self.profile_roots = pair_corpus.build(profile_root)

        self.doc0 = Path(tempfile.mkdtemp(prefix="pair-ambiguous-doc0-"))
        self.addCleanup(shutil.rmtree, self.doc0, ignore_errors=True)
        (self.doc0 / self.REVISION).write_text("## 1\ntexto.\n", encoding="utf-8")

        self.doc1 = Path(tempfile.mkdtemp(prefix="pair-ambiguous-doc1-"))
        self.addCleanup(shutil.rmtree, self.doc1, ignore_errors=True)
        # Two genuinely different, readable families -- neither a marker,
        # so both are eligible and the family count is real, not a
        # single-candidate accident.
        (self.doc1 / "draft-1.md").write_text("family one", encoding="utf-8")
        (self.doc1 / "final-2.md").write_text("family two", encoding="utf-8")

        self.box = FORGE / "implementations" / f"_pair_ambiguous_{os.getpid()}_{id(self)}"
        self.addCleanup(shutil.rmtree, self.box, ignore_errors=True)
        self.box.mkdir(parents=True)
        env = dict(os.environ)
        env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "pair-ambiguous"
        env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = "pair-ambiguous@example.invalid"
        subprocess.run(["git", "init", "-q", str(self.box)], check=True, capture_output=True)
        (self.box / self.PACKAGE).mkdir(parents=True)
        (self.box / self.PACKAGE / "AGREED.md").write_text(
            "# Agreed\n\n## Ladder\n\n- [ ] First measurable claim.\n",
            encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.box, env=env, check=True,
                       capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=self.box, env=env,
                       check=True, capture_output=True)

    def run_cli(self, *args):
        env = dict(os.environ)
        env["IMPLEMENTATION_DOMAIN_PROFILE"] = str(self.profile_roots.profile_path)
        env["IMPLEMENTATION_PROPOSALS"] = str(self.doc0)
        env["IMPLEMENTATION_PROPOSALS_1"] = str(self.doc1)
        return subprocess.run([sys.executable, str(CLI), *args],
                              capture_output=True, text=True, cwd=FORGE, env=env)

    def test_ambiguous_families_refuse_naming_both(self):
        result = self.run_cli(
            "position", "--target", str(self.box), "--name", self.PACKAGE,
            "--revision", self.REVISION, "--session", "s1")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["code"], "DOCUMENT_REVISION_UNREADABLE")
        self.assertIn("draft-#.md", payload["detail"])
        self.assertIn("final-#.md", payload["detail"])


ENGINE = FORGE / ".claude/skills/_core/implementation/engine/implementation_engine.py"

#: design.md D5: the mutation a WEAKER lock survives, so it is the one that
#: proves the refusal is reachable rather than merely present in source.
#: Deleting the `raise` entirely, or falling back to document 0's name,
#: are both caught by the sha assertions alone (the picked file would not
#: even exist under document 0's name in document 1's directory) and prove
#: nothing about THIS refusal specifically. This mutation instead makes
#: `discover_document_revision`'s own ambiguity branch silently pick the
#: first family it found -- a REAL, readable file, with a REAL sha -- so
#: every existing sha/`documents` assertion this suite makes elsewhere
#: keeps passing, and only an assertion on the refusal ITSELF can tell the
#: two behaviours apart.
_AMBIGUITY_OLD = (
    '    if len(families) > 1:\n'
    '        return {**empty, "markerOwned": marker_owned, "nonManaged": non_managed,\n'
    '                "families": sorted(families)}\n'
    '\n'
    '    (members,) = families.values()\n'
)
_AMBIGUITY_MUTATED = (
    '    if len(families) > 1:\n'
    '        pass  # MUTATED (D5): pick the first family instead of refusing\n'
    '\n'
    '    members = next(iter(families.values()))\n'
)


class AmbiguousFamilyMutationProvesReachabilityTests(unittest.TestCase):
    """design.md D5: the mutation a weaker lock survives. Real engine
    source, real subprocesses, guaranteed reverted -- never a monkeypatch
    (a recorded scar: patching a module attribute has zero effect on a
    subprocess, and every case exercised here is one).

    Anchor discipline (design.md D8, carried): the old spelling's count is
    asserted exactly 1 and the new spelling's exactly 0 BEFORE the
    substitution, and the reverse AFTER -- both directions, so an anchor
    that merely matched without changing anything cannot pass silently.
    """

    def setUp(self):
        original = ENGINE.read_text(encoding="utf-8")
        self.assertEqual(original.count(_AMBIGUITY_OLD), 1,
                         "the ambiguity branch's anchor moved or was "
                         "duplicated -- the mutation this test runs "
                         "depends on it occurring exactly once")
        self.assertEqual(original.count(_AMBIGUITY_MUTATED), 0,
                         "the mutated spelling already appears in the "
                         "real source before any mutation -- anchor invalid")
        mutated = original.replace(_AMBIGUITY_OLD, _AMBIGUITY_MUTATED, 1)
        self.assertEqual(mutated.count(_AMBIGUITY_OLD), 0)
        self.assertEqual(mutated.count(_AMBIGUITY_MUTATED), 1)
        ENGINE.write_text(mutated, encoding="utf-8")

        def restore():
            ENGINE.write_text(original, encoding="utf-8")
            restored = ENGINE.read_text(encoding="utf-8")
            self.assertEqual(restored, original,
                             "the engine file was not restored byte-identical")
            self.assertEqual(restored.count(_AMBIGUITY_OLD), 1)
            self.assertEqual(restored.count(_AMBIGUITY_MUTATED), 0)
        self.addCleanup(restore)

        # A fresh two-document profile and a genuinely ambiguous document
        # 1 (the identical corpus shape `TwoDocumentAmbiguousFamilyRefuses
        # Tests` uses), plus a genuinely UNAMBIGUOUS one (the identical
        # shape `TwoDocumentPositionWriteTests` uses) -- both real
        # subprocess fixtures, so the mutated engine is exercised by both
        # the branch it changes and the branch it must leave alone.
        profile_root = Path(tempfile.mkdtemp(prefix="pair-d5-profile-"))
        self.addCleanup(shutil.rmtree, profile_root, ignore_errors=True)
        self.profile_roots = pair_corpus.build(profile_root)

        self.REVISION = "pair-d5-r01.md"
        self.REVISION_1 = "pair-d5-plan-v01.md"

        self.doc0 = Path(tempfile.mkdtemp(prefix="pair-d5-doc0-"))
        self.addCleanup(shutil.rmtree, self.doc0, ignore_errors=True)
        (self.doc0 / self.REVISION).write_text("## 1\ntexto.\n", encoding="utf-8")

        self.unambiguous_doc1 = Path(tempfile.mkdtemp(prefix="pair-d5-unambiguous-"))
        self.addCleanup(shutil.rmtree, self.unambiguous_doc1, ignore_errors=True)
        (self.unambiguous_doc1 / self.REVISION_1).write_text(
            "Document 1's own single-family text, unaffected by D5's own "
            "mutation.\n", encoding="utf-8")

        self.ambiguous_doc1 = Path(tempfile.mkdtemp(prefix="pair-d5-ambiguous-"))
        self.addCleanup(shutil.rmtree, self.ambiguous_doc1, ignore_errors=True)
        (self.ambiguous_doc1 / "draft-1.md").write_text("family one", encoding="utf-8")
        (self.ambiguous_doc1 / "final-2.md").write_text("family two", encoding="utf-8")

        self.box = FORGE / "implementations" / f"_pair_d5_{os.getpid()}_{id(self)}"
        self.addCleanup(shutil.rmtree, self.box, ignore_errors=True)
        self.box.mkdir(parents=True)
        env = dict(os.environ)
        env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "pair-d5"
        env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = "pair-d5@example.invalid"
        subprocess.run(["git", "init", "-q", str(self.box)], check=True, capture_output=True)
        (self.box / "PACKAGE").mkdir(parents=True)
        (self.box / "PACKAGE" / "AGREED.md").write_text(
            "# Agreed\n\n## Ladder\n\n- [ ] First measurable claim.\n",
            encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=self.box, env=env, check=True,
                       capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=self.box, env=env,
                       check=True, capture_output=True)

    def run_cli(self, doc1_root, *args):
        env = dict(os.environ)
        env["IMPLEMENTATION_DOMAIN_PROFILE"] = str(self.profile_roots.profile_path)
        env["IMPLEMENTATION_PROPOSALS"] = str(self.doc0)
        env["IMPLEMENTATION_PROPOSALS_1"] = str(doc1_root)
        return subprocess.run([sys.executable, str(CLI), *args],
                              capture_output=True, text=True, cwd=FORGE, env=env)

    def test_the_ambiguous_case_silently_succeeds_under_the_mutation(self):
        # Under the REAL (unmutated) engine, this exact fixture refuses --
        # proven by `TwoDocumentAmbiguousFamilyRefusesTests`. Under the
        # mutation, it must instead succeed, binding a revision the
        # operator never chose, with a REAL sha (the picked file IS
        # readable) -- design.md D5's own prediction, measured here.
        result = self.run_cli(
            self.ambiguous_doc1, "position", "--target", str(self.box),
            "--name", "PACKAGE", "--revision", self.REVISION, "--session", "s1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        entry = payload["documents"][0]
        self.assertIn(entry["revision"], ("draft-1.md", "final-2.md"))
        self.assertIsNotNone(entry["revisionSha256"])
        expected_sha = hashlib.sha256(
            (self.ambiguous_doc1 / entry["revision"]).read_bytes()).hexdigest()
        self.assertEqual(entry["revisionSha256"], expected_sha)

    def test_the_unambiguous_case_is_unaffected_by_the_mutation(self):
        # The mutation touches only the `len(families) > 1` branch; a
        # genuinely single-family document 1 must resolve to the
        # IDENTICAL sha it would without the mutation -- "every sha and
        # `documents` assertion in the lifecycle classes still passes"
        # (design.md D5), proven directly rather than assumed.
        result = self.run_cli(
            self.unambiguous_doc1, "position", "--target", str(self.box),
            "--name", "PACKAGE", "--revision", self.REVISION, "--session", "s1")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        entry = payload["documents"][0]
        expected_sha = hashlib.sha256(
            (self.unambiguous_doc1 / self.REVISION_1).read_bytes()).hexdigest()
        self.assertEqual(entry["revision"], self.REVISION_1)
        self.assertEqual(entry["revisionSha256"], expected_sha)


class TwoDocumentLifecycleTests(unittest.TestCase):
    """Corrective apply, Cut 3 (`a-revision-is-two-documents`, verify FAIL,
    CRITICAL finding): real subprocess cases against the two-document
    fixture profile for `gate`/`offer`/`close`/`admit`/`position`/`verify`
    -- the six commands the verify report named as unreached, plus
    `probe` for C1. Every call below is a genuine child process, never
    in-process `impl.cmd_*` (this suite's own recorded scar:
    monkeypatching a module attribute has zero effect on a subprocess), so
    `IMPLEMENTATION_DOMAIN_PROFILE`/`IMPLEMENTATION_PROPOSALS`/
    `IMPLEMENTATION_PROPOSALS_1` are real child-process environment
    variables -- the same mechanism the pair corpus's own driver
    established (`_build_env_with_profile_override`), extended here to a
    STATEFUL, multi-command flow the single-command golden-digest
    mechanism (`seal_harness.run_case`, a fresh scratch target per case)
    cannot represent: this flow's whole point is ledger state
    (`position.jsonl`, `tests/admissibility.json`) accumulated across
    several real calls against the SAME target.

    The launch-capacity registration below drops a real, pid-scoped module
    into `remote-execution/scripts/adapters/` -- the identical, already-
    sanctioned mechanism `test_remote_execution.py::AdapterEnvironmentTests
    .test_dropping_a_module_into_adapters_becomes_reachable_by_backend_name`
    establishes (a module dropped there becomes reachable by `--backend`/
    a job folder's own declared `service`, with no change to `remote_cli.py`
    itself), reused here rather than reinvented, and removed in
    `addCleanup` regardless of outcome -- never a monkeypatch of `ADAPTER`
    from this test process, which a REAL subprocess `offer`/`gate` call
    could never see.
    """

    REVISION = "pair-lifecycle-r01.md"
    REVISION_1 = "pair-lifecycle-plan-v01.md"
    REVISION_TEXT = (
        "## 1\n\n$$\na = b \\tag{1.1}\n$$\n\n"
        "Throughout, the estimator is written E[x].\n\n"
        "The corrected form now reads g = h + k.\n"
    )
    REVISION_SHA256 = hashlib.sha256(REVISION_TEXT.encode("utf-8")).hexdigest()
    PACKAGE = "Method"
    SERVICE = f"pairlifecycle{os.getpid()}"

    def setUp(self):
        profile_root = Path(tempfile.mkdtemp(prefix="pair-lifecycle-profile-"))
        self.addCleanup(shutil.rmtree, profile_root, ignore_errors=True)
        self.profile_roots = pair_corpus.build(profile_root)

        self.doc0 = Path(tempfile.mkdtemp(prefix="pair-lifecycle-doc0-"))
        self.addCleanup(shutil.rmtree, self.doc0, ignore_errors=True)
        (self.doc0 / self.REVISION).write_text(self.REVISION_TEXT, encoding="utf-8")

        self.doc1 = Path(tempfile.mkdtemp(prefix="pair-lifecycle-doc1-"))
        self.addCleanup(shutil.rmtree, self.doc1, ignore_errors=True)
        (self.doc1 / self.REVISION_1).write_text(
            "Document 1's own text -- a real, independently readable file "
            "at DOCUMENTS[1]'s own directory, never document 0's copy.\n",
            encoding="utf-8")

        self._register_capacity_adapter()
        self.box, self.commit = self._build_box()

    def _doc1_sha256(self) -> str:
        return hashlib.sha256((self.doc1 / self.REVISION_1).read_bytes()).hexdigest()

    def _child_env(self):
        env = dict(os.environ)
        env["IMPLEMENTATION_DOMAIN_PROFILE"] = str(self.profile_roots.profile_path)
        env["IMPLEMENTATION_PROPOSALS"] = str(self.doc0)
        env["IMPLEMENTATION_PROPOSALS_1"] = str(self.doc1)
        return env

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(CLI), *args],
                              capture_output=True, text=True, cwd=FORGE,
                              env=self._child_env())

    def _register_capacity_adapter(self):
        adapters_dir = (FORGE / ".claude" / "skills" / "remote-execution"
                        / "scripts" / "adapters")
        fixture_path = adapters_dir / f"{self.SERVICE}.py"
        fixture_path.write_text(
            "import importlib.util\n"
            "import sys\n"
            "from pathlib import Path\n"
            "\n"
            "def _load_adapter_seam():\n"
            "    module_name = 'remote_execution_adapter'\n"
            "    if module_name in sys.modules:\n"
            "        return sys.modules[module_name]\n"
            "    script = Path(__file__).resolve().parent.parent / 'adapter.py'\n"
            "    spec = importlib.util.spec_from_file_location(module_name, script)\n"
            "    module = importlib.util.module_from_spec(spec)\n"
            "    sys.modules[module_name] = module\n"
            "    spec.loader.exec_module(module)\n"
            "    return module\n"
            "\n"
            "ADAPTER = _load_adapter_seam()\n"
            f"ADAPTER.register_declared_capacity({self.SERVICE!r}, lambda: (1, 1))\n",
            encoding="utf-8")
        self.addCleanup(fixture_path.unlink)
        self.addCleanup(
            lambda: shutil.rmtree(adapters_dir / "__pycache__", ignore_errors=True))

    def _build_box(self):
        box = FORGE / "implementations" / f"_pair_lifecycle_{os.getpid()}_{id(self)}"
        self.addCleanup(shutil.rmtree, box, ignore_errors=True)
        box.mkdir(parents=True)
        env = dict(os.environ)
        env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = "pair-lifecycle"
        env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = "pair-lifecycle@example.invalid"
        subprocess.run(["git", "init", "-q", str(box)], check=True, capture_output=True)

        (box / "src" / self.PACKAGE).mkdir(parents=True)
        (box / "src" / self.PACKAGE / "__init__.py").write_text(
            "__all__ = []\n", encoding="utf-8")
        (box / "src" / self.PACKAGE / "kernels.py").write_text(
            "__provenance__ = {\n"
            f"    'revision': {self.REVISION!r}, 'sections': ['1'],\n"
            "    'equations': ['1.1'], 'invariants': [],\n"
            "}\n", encoding="utf-8")
        (box / "src" / f"{self.PACKAGE}_Benchmark").mkdir(parents=True)
        (box / "src" / f"{self.PACKAGE}_Benchmark" / "__init__.py").write_text(
            "__benchmark__ = {\n"
            f"    'revision': {self.REVISION!r}, 'premises': {{}},\n"
            "    'arms': {'floor': {'sections': ['1']}}, 'search': {},\n"
            "    'report': {}, 'distribution': {},\n"
            "    'entry': {'module': 'Method_Benchmark.steps', 'function': 'run'},\n"
            "}\n"
            "__steps__ = {'measure': {'module': 'Method_Benchmark.steps', "
            "'function': 'run'}}\n",
            encoding="utf-8")
        (box / "src" / f"{self.PACKAGE}_Benchmark" / "steps.py").write_text(
            "def run(*a, **k):\n    return {}\n", encoding="utf-8")
        (box / self.PACKAGE).mkdir(parents=True)
        (box / "tests").mkdir(parents=True)
        (box / "tests" / "findings.py").write_text(
            "FINDINGS = [\n"
            "    {\n"
            "        'id': 'pair-lifecycle-finding',\n"
            "        'kind': 'gap',\n"
            "        'status': 'measured',\n"
            "        'rate': 'always',\n"
            "        'statement': 'The identity needs a correction.',\n"
            "        'remedy': 'Replace a = b with the corrected identity.',\n"
            "        'document': 'proposal',\n"
            "        'equations': ['1.1'],\n"
            "        'remedy_equations': ['1.1'],\n"
            "        'uses': ['E[x]'],\n"
            "        'introduces': [],\n"
            "        'adoption': {'absent': 'a = b', 'expect': ['g = h + k']},\n"
            "        'remedy_block': '$$\\ng = h + k \\\\tag{1.1}\\n$$',\n"
            "    },\n"
            "    {\n"
            "        'id': 'pair-lifecycle-doc1-finding',\n"
            "        'kind': 'gap',\n"
            "        'status': 'measured',\n"
            "        'rate': 'always',\n"
            "        'statement': 'Document 1 declares its own notation, "
            "independent of document 0.',\n"
            "        'remedy': 'No change to document 0; this finding exists "
            "only to prove verify routes its compatibility check to the "
            "document it names.',\n"
            "        'document': 'experiments',\n"
            "        'equations': [],\n"
            "        'remedy_equations': [],\n"
            "        'uses': ['independently readable'],\n"
            "        'introduces': [],\n"
            "    },\n"
            "]\n", encoding="utf-8")

        subprocess.run(["git", "add", "-A"], cwd=box, env=env, check=True,
                       capture_output=True)
        subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=box, env=env,
                       check=True, capture_output=True)
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=box, env=env, check=True,
            capture_output=True, text=True).stdout.strip()

        job_dir = box / "tools" / self.SERVICE / "job1"
        job_dir.mkdir(parents=True)
        run_config = {
            "schemaVersion": 1, "product": self.PACKAGE, "service": self.SERVICE,
            "jobName": "job1", "commit": commit,
            "repo": {"url": "https://example.invalid/repo.git", "ref": "main"},
            "clonePaths": [f"src/{self.PACKAGE}"],
            "run": {"module": f"{self.PACKAGE}.module", "function": "run", "kwargs": {}},
            "runnerTemplate": [
                {"path": "assets/runner_bootstrap.py", "sha256": "0" * 64},
                {"path": "assets/runner_invoke.py", "sha256": "0" * 64},
            ],
        }
        (job_dir / "run-config.json").write_text(json.dumps(run_config), encoding="utf-8")

        smoke_path = box / self.PACKAGE / ".remote-execution" / "smoke.jsonl"
        smoke_path.parent.mkdir(parents=True)
        smoke_event = {"kind": "smokeResult", "ts": "2026-09-11T00:00:00Z",
                        "jobName": "job1", "result": "pass", "commit": commit,
                        "worker": "w1", "missing": []}
        smoke_path.write_text(json.dumps(smoke_event) + "\n", encoding="utf-8")

        header = {"revision": self.REVISION, "revisionSha256": self.REVISION_SHA256,
                  "derivedAt": "2026-09-11T00:00:00Z", "session": "s1", "target": "final"}
        # Ticked, not blank: job1's own smoke.jsonl above records a REAL
        # passing result, so a blank mark here would DISAGREE with what
        # `derive()` measures (a claim and its evidence pointing opposite
        # ways is a disagreement regardless of which direction it points)
        # -- `close` (unlike `gate`) refuses on any such disagreement
        # before it will run at all, so the tick must already match the
        # real, passing smoke result for `close` to succeed below.
        items = [{"ordinal": 1, "mark": "x", "text": "Rehearse the job.",
                  "witness": {"kind": "rehearsal", "operand": "job1"}}]
        (box / self.PACKAGE / "AGREED.md").write_text(
            impl_position.render(header, items), encoding="utf-8")

        return box, commit

    def test_the_full_lifecycle_reaches_every_named_gate(self):
        """One flow, seven real subprocess commands, every one of Slice B's
        `len(DOCUMENTS) > 1` runtime sites this corrective apply set out to
        prove -- named per site in the comments beside each assertion."""

        # C1 (position_state's `multi` branch, L637-654): reached the
        # moment ANY command reads a target that already carries a
        # `<!-- position -->` block under a two-document profile. `probe`
        # is the simplest real reader -- a pure read, no ledger write.
        probe = self.run_cli("probe", "--target", str(self.box), "--name",
                             self.PACKAGE, "--revision", self.REVISION)
        self.assertEqual(probe.returncode, 0, probe.stdout + probe.stderr)
        probe_result = json.loads(probe.stdout)
        bound_to = probe_result["position"]["boundTo"]
        self.assertIsInstance(bound_to, dict)
        self.assertEqual(set(bound_to), {"proposal", "experiments"})

        # `propose` -- gate's own separate proposal precondition, unrelated
        # to `len(DOCUMENTS)` itself but required before a minted token
        # will pass `_verify_gate_proposal` below.
        propose = self.run_cli(
            "propose", "--target", str(self.box), "--name", self.PACKAGE,
            "--session", "s1", "--job", "job1", "--worker", "w1",
            "--rationale", "Campaign proposal for the pair lifecycle.")
        self.assertEqual(propose.returncode, 0, propose.stdout + propose.stderr)

        # `offer`: C5's own return/ledger-event sites AND C4's binding
        # growth (`_authorization_binding`'s own `**` spread) -- a REAL
        # launch action minted for job1, via the file-based capacity
        # adapter dropped in `setUp`, never a monkeypatch.
        offer = self.run_cli(
            "offer", "--target", str(self.box), "--name", self.PACKAGE,
            "--revision", self.REVISION, "--session", "s1", "--answer", "yes")
        self.assertEqual(offer.returncode, 0, offer.stdout + offer.stderr)
        offer_result = json.loads(offer.stdout)
        self.assertIn("documentRevisions", offer_result)
        self.assertEqual(
            offer_result["documentRevisions"],
            [{"label": "experiments", "revision": self.REVISION_1,
              "sha256": self._doc1_sha256()}])
        launch = next(a for a in offer_result["actions"] if a["id"] == "launch")
        token = launch["binding"]["authorization"]
        self.assertTrue(token)
        ledger_path = self.box / self.PACKAGE / ".implementation" / "position.jsonl"
        ledger_events = [json.loads(line) for line in
                        ledger_path.read_text(encoding="utf-8").splitlines()]
        offer_event = next(e for e in ledger_events if e["kind"] == "offer")
        self.assertIn("documentRevisions", offer_event)

        # `gate`: consumes the REAL token minted above -- the real success
        # path the 29-case seal corpus can never reach on its own
        # (`gate-e0`/`gate-e1` both refuse before minting anything).
        # `gate_binding`'s own presence-gated `documentRevisions` spread
        # feeds `_verify_gate_authorization`'s `_authorization_binding_
        # keys(record)` call -- C4's verification-side companion to
        # `AuthorizationBindingKeysPresenceBranchTests` above, exercised
        # here with genuinely two-document-shaped data end to end.
        gate = self.run_cli(
            "gate", "--target", str(self.box), "--name", self.PACKAGE,
            "--revision", self.REVISION, "--session", "s1",
            "--job", "job1", "--worker", "w1",
            "--justification", "Rehearsal passed at the pinned commit.",
            "--authorization", token, "--elect", "job1")
        self.assertEqual(gate.returncode, 0, gate.stdout + gate.stderr)
        gate_result = json.loads(gate.stdout)
        self.assertEqual(gate_result["status"], "recorded")
        self.assertIn("documentRevisions", gate_result)
        self.assertEqual(
            gate_result["documentRevisions"],
            [{"label": "experiments", "revision": self.REVISION_1,
              "sha256": self._doc1_sha256()}])
        ledger_events_after_gate = [
            json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
        gate_event = next(e for e in ledger_events_after_gate if e["kind"] == "gate")
        self.assertIn("documentRevisions", gate_event)

        # `close`: also reaches C2's write path a second, independent way
        # -- `close`'s own internal `cmd_position` refresh call finds the
        # hand-authored header from `_build_box` carries no `documents=`
        # group yet (it was written directly by this test, never through
        # `cmd_position`) and writes one now.
        close = self.run_cli(
            "close", "--target", str(self.box), "--name", self.PACKAGE,
            "--revision", self.REVISION, "--session", "s1")
        self.assertEqual(close.returncode, 0, close.stdout + close.stderr)
        close_result = json.loads(close.stdout)
        self.assertEqual(close_result["status"], "closed")
        self.assertIn("documentRevisions", close_result)
        agreed_after_close = (
            self.box / self.PACKAGE / "AGREED.md").read_text(encoding="utf-8")
        self.assertIn("documents=", agreed_after_close)
        ledger_events_after_close = [
            json.loads(line) for line in ledger_path.read_text(encoding="utf-8").splitlines()]
        close_event = next(
            e for e in reversed(ledger_events_after_close) if e["kind"] == "close")
        self.assertIn("documentRevisions", close_event)

        # A second `close`, over the now-unmoved position -- `not_open`,
        # the exact `documentRevisions`-carrying comparison this
        # corrective apply's own launch brief named as the mutation the
        # 29-case seal corpus could never catch (task 11.3's own finding).
        close_again = self.run_cli(
            "close", "--target", str(self.box), "--name", self.PACKAGE,
            "--revision", self.REVISION, "--session", "s1")
        self.assertEqual(
            close_again.returncode, 0, close_again.stdout + close_again.stderr)
        close_again_result = json.loads(close_again.stdout)
        self.assertEqual(close_again_result["status"], "not_open")
        self.assertIn("documentRevisions", close_again_result)

        # `admit`: C3's write path AND C7's `require_document` gate
        # (`read_findings`'s own `well_formed(..., require_document=True)`
        # call) -- the finding declared above carries `document:
        # "proposal"`, so `well_formed` accepts it instead of refusing
        # `MALFORMED_FINDINGS`, and `cmd_admit` writes a real `documents`
        # key into `tests/admissibility.json`.
        admit = self.run_cli(
            "admit", "--target", str(self.box), "--name", self.PACKAGE,
            "--revision", self.REVISION)
        self.assertEqual(admit.returncode, 0, admit.stdout + admit.stderr)
        record = json.loads(
            (self.box / "tests" / "admissibility.json").read_text(encoding="utf-8"))
        self.assertIn("documents", record)
        self.assertEqual(
            record["documents"],
            [{"label": "experiments", "revision": self.REVISION_1,
              "revisionSha256": self._doc1_sha256()}])
        # Re-verify (Cut 3, second correction) WARNING 1: C7's
        # `sources_by_document` construction (L7797) is reached by the
        # subprocess above -- confirmed by the verify session's own
        # mutation, which observed a computed-but-unchecked `"impact":
        # {"class": {"proposal": "local"}}` -- but nothing asserted its
        # OUTPUT. `finding_impact`'s `class` becomes a per-document MAPPING
        # (never the plain string it is under one document) only when this
        # exact site's `sources_by_document` argument is populated, so the
        # type itself -- dict, not str -- is a structural control: turning
        # this site off collapses `class` back to a bare string regardless
        # of either finding's own content.
        impact_class = record["findings"]["pair-lifecycle-finding"]["impact"]["class"]
        self.assertIsInstance(impact_class, dict)
        self.assertEqual(impact_class, {"proposal": "local"})

        # `verify`: C8's fidelity-by-document fold AND `admissibility_
        # record`'s own extra-document staleness read (reached because
        # `admit` above already wrote a record `verify` now reads back).
        verify = self.run_cli(
            "verify", "--target", str(self.box), "--name", self.PACKAGE,
            "--revision", self.REVISION)
        self.assertEqual(verify.returncode, 0, verify.stdout + verify.stderr)
        verify_result = json.loads(verify.stdout)
        fidelity_by_document = verify_result["fidelity"]["fidelityByDocument"]
        self.assertEqual(
            {entry["label"] for entry in fidelity_by_document},
            {"proposal", "experiments"})
        extra_entry = next(
            e for e in fidelity_by_document if e["label"] == "experiments")
        # Document 1's own revision genuinely resolves (a real, readable
        # file at `IMPLEMENTATION_PROPOSALS_1`), so `_extra_document_
        # fidelity_status` never falls back to its `"unknown"` branch here
        # -- proving the function was reached with data that could tell
        # the two branches apart, not merely with an absent revision that
        # would answer `"unknown"` regardless of whether the function ran
        # at all.
        self.assertNotEqual(extra_entry["status"], "unknown")

        # Re-verify (Cut 3, second correction) WARNING 1: C7's sibling site,
        # `cmd_verify`'s `verify_sources_by_document` construction (L14839),
        # reached but likewise unasserted (confirmed identical to L7797 by
        # code+test-file inspection). `pair-lifecycle-doc1-finding` (added
        # to `tests/findings.py` above) names document 1 (`experiments`)
        # and declares `uses: ['independently readable']` -- a phrase
        # present verbatim in document 1's own text and ABSENT from
        # document 0's. `remedy_compatibility` only sees it when THIS
        # site's construction actually routes the check to document 1's
        # text: skip the construction and the finding defaults to document
        # 0's text, where the phrase is missing, and the audit would
        # wrongly report it incompatible -- a genuine control, not a
        # tautology.
        compatibility = verify_result["audit"]["compatibility"]
        self.assertEqual(compatibility["status"], "ok", compatibility)
        self.assertEqual(compatibility["undefinedNotation"], [])


if __name__ == "__main__":
    unittest.main()
