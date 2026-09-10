"""paper-writing: scaffold, block grammar, substitution engine.

Stdlib-only `unittest`. Every fixture lives under a `TemporaryDirectory`; the
real `paper/` at the forge root is never touched by this suite outside the
one CLI subprocess test, which scaffolds under the already-gitignored
`implementations/` tree and cleans up after itself. Every
`paper_scaffold.resolve_paper_dir` call below passes an injected
`forge_root` for exactly this reason.
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
import unittest.mock
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = FORGE_ROOT / ".claude" / "skills" / "paper-writing" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
import paper_scaffold  # noqa: E402
import paper_block  # noqa: E402

sys.path.insert(0, str(FORGE_ROOT / ".claude" / "skills" / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

CLI = SKILL_SCRIPTS / "paper_cli.py"


def _marker_pair(block_id: str, body: bytes) -> bytes:
    """Build a well-formed begin/end pair with the correct digest for
    `body`. Test-only fixture construction — production code never builds a
    pair this way; `open` (a later work unit) is what installs an empty one.
    """
    digest = hashlib.sha256(body).hexdigest()
    return (
        f"%% paper-writing block {block_id} begin sha256={digest}\n".encode("ascii")
        + body
        + f"%% paper-writing block {block_id} end\n".encode("ascii")
    )


def _write_fixture(paper_dir: Path, main_tex: bytes) -> None:
    paper_dir.mkdir(parents=True, exist_ok=True)
    (paper_dir / "main.tex").write_bytes(main_tex)


class ScaffoldTests(unittest.TestCase):
    """`paper-scaffold` spec: create/re-enter `paper/` idempotently."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.forge_root = Path(self._tmp.name) / "repo"
        self.forge_root.mkdir()

    def test_first_run_creates_the_tree(self) -> None:
        paper_dir = paper_scaffold.resolve_paper_dir(None, forge_root=self.forge_root)
        result = paper_scaffold.scaffold(paper_dir)

        self.assertTrue((paper_dir / "main.tex").is_file())
        self.assertTrue((paper_dir / "refs.bib").is_file())
        self.assertTrue((paper_dir / "Figures").is_dir())
        self.assertTrue((paper_dir / ".gitkeep").is_file())
        self.assertEqual(
            sorted(result["created"]),
            sorted(["main.tex", "refs.bib", "Figures", ".gitkeep"]),
        )

    def test_second_run_leaves_hand_edited_bytes_identical(self) -> None:
        paper_dir = paper_scaffold.resolve_paper_dir(None, forge_root=self.forge_root)
        paper_scaffold.scaffold(paper_dir)
        (paper_dir / "main.tex").write_bytes(b"\\documentclass{article}\n% hand-edited\n")
        before = {
            str(p.relative_to(paper_dir)): p.read_bytes()
            for p in sorted(paper_dir.rglob("*")) if p.is_file()
        }

        result = paper_scaffold.scaffold(paper_dir)

        after = {
            str(p.relative_to(paper_dir)): p.read_bytes()
            for p in sorted(paper_dir.rglob("*")) if p.is_file()
        }
        self.assertEqual(before, after)
        self.assertEqual(result["created"], [])

    def test_paper_as_a_file_refuses_and_writes_nothing(self) -> None:
        paper_dir = self.forge_root / "paper"
        paper_dir.write_bytes(b"not a directory")

        with self.assertRaises(Refused) as ctx:
            paper_scaffold.scaffold(paper_dir)

        self.assertEqual(ctx.exception.code, "PAPER_NOT_A_DIRECTORY")
        self.assertEqual(paper_dir.read_bytes(), b"not a directory")

    def test_figures_as_a_file_refuses_and_writes_nothing_else(self) -> None:
        paper_dir = self.forge_root / "paper"
        paper_dir.mkdir()
        (paper_dir / "Figures").write_bytes(b"not a directory")

        with self.assertRaises(Refused) as ctx:
            paper_scaffold.scaffold(paper_dir)

        self.assertEqual(ctx.exception.code, "SCAFFOLD_ENTRY_WRONG_TYPE")
        self.assertIn("Figures", ctx.exception.detail)
        self.assertFalse((paper_dir / "main.tex").exists())
        self.assertFalse((paper_dir / "refs.bib").exists())
        self.assertFalse((paper_dir / ".gitkeep").exists())
        # The wrong-typed entry itself is untouched, not replaced.
        self.assertEqual((paper_dir / "Figures").read_bytes(), b"not a directory")

    def test_paper_outside_repository_refuses(self) -> None:
        outside = Path(self._tmp.name) / "elsewhere"

        with self.assertRaises(Refused) as ctx:
            paper_scaffold.resolve_paper_dir(str(outside), forge_root=self.forge_root)

        self.assertEqual(ctx.exception.code, "PAPER_OUTSIDE_REPOSITORY")

    def test_cli_scaffold_verb_runs_and_emits_json(self) -> None:
        # Real FORGE_ROOT (the CLI's own default), scaffolded under the
        # already-gitignored `implementations/` tree and removed afterward —
        # the one place in this test class allowed to touch the real repo.
        test_root = FORGE_ROOT / "implementations" / f".paper-writing-cli-test-{os.getpid()}"
        self.addCleanup(shutil.rmtree, test_root, ignore_errors=True)
        paper_dir = test_root / "paper"

        proc = subprocess.run(
            [sys.executable, str(CLI), "scaffold", "--paper", str(paper_dir)],
            capture_output=True, text=True, timeout=30,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertTrue((paper_dir / "main.tex").is_file())

    def test_cli_scaffold_outside_repository_refuses_with_exit_2(self) -> None:
        outside = Path(tempfile.gettempdir()) / f"paper-writing-outside-test-{os.getpid()}"
        self.addCleanup(shutil.rmtree, outside, ignore_errors=True)

        proc = subprocess.run(
            [sys.executable, str(CLI), "scaffold", "--paper", str(outside)],
            capture_output=True, text=True, timeout=30,
        )

        self.assertEqual(proc.returncode, 2, proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "refused")
        self.assertEqual(payload["code"], "PAPER_OUTSIDE_REPOSITORY")
        self.assertFalse(outside.exists())


class BlockCoreTests(unittest.TestCase):
    """`block-substitution`: marker grammar, pairing, substitute, hand-edit
    detection and `--adopt`. Exercises `paper_block.py` directly — CLI
    wiring for `open`/`status`/`substitute` is a later work unit."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"

    def _fixture(self) -> bytes:
        return (
            b"\\documentclass{article}\n\\begin{document}\n\n"
            + _marker_pair("abstract", b"One paragraph abstract.\n")
            + b"\nSome prose between blocks.\n\n"
            + _marker_pair("intro", b"Introduction body.\n")
            + b"\n\\end{document}\n"
        )

    def test_well_formed_pair_parses_via_status(self) -> None:
        data = self._fixture()
        result = paper_block.status(data)

        ids = {b["id"]: b for b in result["blocks"]}
        self.assertEqual(set(ids), {"abstract", "intro"})
        self.assertEqual(ids["abstract"]["digest"], hashlib.sha256(b"One paragraph abstract.\n").hexdigest())
        start, end = ids["intro"]["region"]
        self.assertEqual(data[start:end], _marker_pair("intro", b"Introduction body.\n"))

    def test_malformed_marker_line_refuses_naming_the_line(self) -> None:
        data = b"%% paper-writing block intro begin\nbody\n%% paper-writing block intro end\n"

        with self.assertRaises(Refused) as ctx:
            paper_block.status(data)

        self.assertEqual(ctx.exception.code, "MARKER_MALFORMED")
        self.assertIn("intro begin", ctx.exception.detail)

    def test_duplicated_id_refuses(self) -> None:
        data = _marker_pair("intro", b"first\n") + _marker_pair("intro", b"second\n")

        with self.assertRaises(Refused) as ctx:
            paper_block.status(data)

        self.assertEqual(ctx.exception.code, "BLOCK_DUPLICATED")

    def test_unpaired_begin_refuses(self) -> None:
        data = b"%% paper-writing block a begin sha256=" + b"0" * 64 + b"\nbody\n"

        with self.assertRaises(Refused) as ctx:
            paper_block.status(data)

        self.assertEqual(ctx.exception.code, "BLOCK_UNPAIRED")

    def test_nested_begin_refuses(self) -> None:
        digest_a = hashlib.sha256(b"").hexdigest()
        data = (
            f"%% paper-writing block a begin sha256={digest_a}\n".encode("ascii")
            + _marker_pair("b", b"nested body\n")
            + b"%% paper-writing block a end\n"
        )

        with self.assertRaises(Refused) as ctx:
            paper_block.status(data)

        self.assertEqual(ctx.exception.code, "BLOCK_NESTED")

    def test_region_excludes_the_preceding_newline(self) -> None:
        preamble = b"preamble line\n"
        data = preamble + _marker_pair("a", b"body\n")
        parsed = paper_block.parse(data)
        begin, _end = parsed.pairs["a"]
        marker_lead = b"%% paper-writing block a begin"

        self.assertEqual(begin["start"], len(preamble))
        self.assertEqual(data[begin["start"]:begin["start"] + len(marker_lead)], marker_lead)

    def test_substitute_on_absent_block_refuses_and_creates_nothing(self) -> None:
        fixture = self._fixture()
        _write_fixture(self.paper_dir, fixture)

        with self.assertRaises(Refused) as ctx:
            paper_block.substitute(self.paper_dir, "results", new_body=b"New results.\n")

        self.assertEqual(ctx.exception.code, "BLOCK_ABSENT")
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), fixture)
        self.assertFalse((self.paper_dir / ".paper-writing").exists())

    def test_body_carrying_a_marker_line_refuses(self) -> None:
        fixture = self._fixture()
        _write_fixture(self.paper_dir, fixture)
        bad_body = b"Some text.\n%% paper-writing block sneaky begin sha256=" + b"0" * 64 + b"\n"

        with self.assertRaises(Refused) as ctx:
            paper_block.substitute(self.paper_dir, "intro", new_body=bad_body)

        self.assertEqual(ctx.exception.code, "CONTENT_CARRIES_MARKER")
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), fixture)

    def test_hand_edited_body_refuses_naming_both_digests(self) -> None:
        fixture = self._fixture()
        _write_fixture(self.paper_dir, fixture)
        tampered = fixture.replace(b"Introduction body.\n", b"Hand-edited body.\n", 1)
        (self.paper_dir / "main.tex").write_bytes(tampered)
        expected_digest = hashlib.sha256(b"Introduction body.\n").hexdigest()
        found_digest = hashlib.sha256(b"Hand-edited body.\n").hexdigest()

        with self.assertRaises(Refused) as ctx:
            paper_block.substitute(self.paper_dir, "intro", new_body=b"Whatever.\n")

        self.assertEqual(ctx.exception.code, "BLOCK_HAND_EDITED")
        self.assertIn(expected_digest, ctx.exception.detail)
        self.assertIn(found_digest, ctx.exception.detail)
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), tampered)

    def test_adopt_updates_digest_without_touching_body_and_clears_the_refusal(self) -> None:
        fixture = self._fixture()
        _write_fixture(self.paper_dir, fixture)
        tampered = fixture.replace(b"Introduction body.\n", b"Hand-edited body.\n", 1)
        (self.paper_dir / "main.tex").write_bytes(tampered)

        paper_block.substitute(self.paper_dir, "intro", adopt=True)

        post_adopt = (self.paper_dir / "main.tex").read_bytes()
        self.assertIn(b"Hand-edited body.\n", post_adopt)
        parsed = paper_block.parse(post_adopt)
        begin, end = parsed.pairs["intro"]
        on_disk_body = post_adopt[begin["end"]:end["start"]]
        self.assertEqual(on_disk_body, b"Hand-edited body.\n")
        self.assertEqual(begin["digest"], hashlib.sha256(b"Hand-edited body.\n").hexdigest())

        # A later substitute() no longer refuses BLOCK_HAND_EDITED.
        paper_block.substitute(self.paper_dir, "intro", new_body=b"Rewritten after adopt.\n")
        final = (self.paper_dir / "main.tex").read_bytes()
        self.assertIn(b"Rewritten after adopt.\n", final)

    def test_adopt_on_matching_digest_refuses_nothing_to_adopt(self) -> None:
        fixture = self._fixture()
        _write_fixture(self.paper_dir, fixture)

        with self.assertRaises(Refused) as ctx:
            paper_block.substitute(self.paper_dir, "intro", adopt=True)

        self.assertEqual(ctx.exception.code, "NOTHING_TO_ADOPT")
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), fixture)


class InvariantTests(unittest.TestCase):
    """Byte-identity invariant: three conjuncts, so a no-op write cannot
    pass trivially, plus the guard that refuses before any write."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"

    def _fixture(self) -> bytes:
        return (
            b"Preamble.\n\n"
            + _marker_pair("a", b"Body A.\n")
            + b"\nMiddle prose, untouched.\n\n"
            + _marker_pair("b", b"Body B.\n")
            + b"\nTail.\n"
        )

    def test_only_the_named_block_changes_three_conjuncts(self) -> None:
        pre = self._fixture()
        _write_fixture(self.paper_dir, pre)

        paper_block.substitute(self.paper_dir, "a", new_body=b"New body for a.\n")

        # Independent re-read: a fresh `read_bytes()`, not the in-memory
        # candidate this call already held — comparing a value against
        # itself would prove nothing.
        post = (self.paper_dir / "main.tex").read_bytes()

        # Conjunct 1: everything outside block `a`'s region is identical.
        self.assertEqual(paper_block.project(post), paper_block.project(pre))
        # Conjunct 2: something on disk actually changed (rules out a
        # no-op `substitute` silently reporting success).
        self.assertNotEqual(post, pre)
        # Conjunct 3: the substituted block's body is exactly the new body
        # (rules out a change landing at the wrong offset that still
        # happens to leave the outside-region projection equal).
        parsed = paper_block.parse(post)
        begin, end = parsed.pairs["a"]
        self.assertEqual(post[begin["end"]:end["start"]], b"New body for a.\n")
        # Block `b`'s own body and digest are untouched.
        begin_b, end_b = parsed.pairs["b"]
        self.assertEqual(post[begin_b["end"]:end_b["start"]], b"Body B.\n")
        self.assertEqual(begin_b["digest"], hashlib.sha256(b"Body B.\n").hexdigest())

    def test_violating_candidate_refuses_before_any_write(self) -> None:
        pre = self._fixture()
        parsed = paper_block.parse(pre)
        candidate, _written = paper_block.build_candidate(pre, parsed, "a", b"New body.\n", adopt=False)
        # Corrupt one byte outside the target block's region — exactly the
        # violation `identity_invariant` exists to catch before a write.
        corrupted = bytearray(candidate)
        corrupted[0:1] = b"X"
        corrupted = bytes(corrupted)

        with self.assertRaises(Refused) as ctx:
            paper_block.identity_invariant(pre, corrupted)

        self.assertEqual(ctx.exception.code, "SUBSTITUTION_NOT_LOCAL")
        # `identity_invariant` never opens a file — the refusal above is
        # itself the proof no write was attempted for this candidate.

    def test_tex_moved_refuses_when_disk_changes_between_read_and_write(self) -> None:
        pre = self._fixture()
        _write_fixture(self.paper_dir, pre)
        real_read_bytes = Path.read_bytes
        calls = {"n": 0}

        def flaky_read_bytes(self_path):
            calls["n"] += 1
            if calls["n"] == 2:
                # Simulate a second session's edit landing between this
                # call's own initial read and its CAS re-read.
                (self.paper_dir / "main.tex").write_bytes(pre + b"% intruder\n")
            return real_read_bytes(self_path)

        with unittest.mock.patch.object(Path, "read_bytes", flaky_read_bytes):
            with self.assertRaises(Refused) as ctx:
                paper_block.substitute(self.paper_dir, "a", new_body=b"New body.\n")

        self.assertEqual(ctx.exception.code, "TEX_MOVED")


class PreImageTests(unittest.TestCase):
    """The one-deep pre-image: the only recovery path once bytes reach
    disk, and its depth limit proven rather than merely stated."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"

    def _fixture(self) -> bytes:
        return _marker_pair("a", b"Body A.\n")

    def _prev_path(self) -> Path:
        return self.paper_dir / ".paper-writing" / "main.tex.prev"

    def test_pre_image_holds_the_exact_pre_write_bytes(self) -> None:
        pre = self._fixture()
        _write_fixture(self.paper_dir, pre)

        paper_block.substitute(self.paper_dir, "a", new_body=b"First rewrite.\n")

        self.assertEqual(self._prev_path().read_bytes(), pre)

    def test_only_the_immediately_prior_state_is_recoverable(self) -> None:
        first = self._fixture()
        _write_fixture(self.paper_dir, first)

        paper_block.substitute(self.paper_dir, "a", new_body=b"First rewrite.\n")
        second = (self.paper_dir / "main.tex").read_bytes()
        self.assertEqual(self._prev_path().read_bytes(), first)

        paper_block.substitute(self.paper_dir, "a", new_body=b"Second rewrite.\n")

        # After the second write, the pre-image holds only what preceded
        # THAT write — the state before the first write is gone from this
        # mechanism, and nothing else (main.tex is untracked) retains it.
        self.assertEqual(self._prev_path().read_bytes(), second)
        self.assertNotEqual(self._prev_path().read_bytes(), first)

    def test_pre_image_is_written_before_main_tex_is_replaced(self) -> None:
        pre = self._fixture()
        _write_fixture(self.paper_dir, pre)
        real_replace = os.replace
        calls = {"n": 0}

        def flaky_replace(src, dst):
            calls["n"] += 1
            if calls["n"] == 2:
                # The second `os.replace` this call makes is main.tex's own
                # (the first is the pre-image's) — simulate a crash right
                # there, after the pre-image landed and before main.tex did.
                raise OSError("simulated crash between pre-image and main.tex")
            return real_replace(src, dst)

        with unittest.mock.patch("paper_block.os.replace", flaky_replace):
            with self.assertRaises(OSError):
                paper_block.substitute(self.paper_dir, "a", new_body=b"Rewrite.\n")

        # The pre-image landed; main.tex was never touched — the crash left
        # pre-image == main.tex, the harmless case design step 9 declares.
        self.assertEqual(self._prev_path().read_bytes(), pre)
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), pre)


class CRLFTests(unittest.TestCase):
    """Binary I/O only: a CRLF fixture built in code, never committed, and
    a control assertion proving a text-mode open would have corrupted it."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"

    def test_crlf_block_round_trips_untouched_and_text_mode_would_corrupt_it(self) -> None:
        preamble = b"\\documentclass{article}\r\n\\begin{document}\r\n"
        body = b"Mid-paragraph CRLF body.\r\n"
        tail = b"\r\nTrailing prose with CRLF.\r\n\\end{document}\r\n"
        pre = preamble + _marker_pair("mid", body) + tail
        _write_fixture(self.paper_dir, pre)

        paper_block.substitute(self.paper_dir, "mid", new_body=b"Replacement body.\r\n")
        post = (self.paper_dir / "main.tex").read_bytes()

        # Every CRLF outside the substituted region survives byte for byte.
        self.assertTrue(post.startswith(preamble))
        self.assertTrue(post.endswith(tail))
        self.assertEqual(post.count(b"\r\n"), preamble.count(b"\r\n") + 1 + tail.count(b"\r\n"))

        # Control: a text-mode, universal-newlines open of the SAME bytes
        # flattens every CRLF to LF — proving that had production code used
        # text mode instead of binary, this test's own byte-identity
        # assertion above would have failed. Demonstrated on the file this
        # engine actually wrote, not a separate hand-built buffer.
        tex_path = self.paper_dir / "main.tex"
        with open(tex_path, "r", newline=None) as handle:
            text_mode_bytes = handle.read().encode("utf-8")
        self.assertNotEqual(text_mode_bytes, post)
        self.assertIn(b"\r\n", post)
        self.assertNotIn(b"\r\n", text_mode_bytes)


if __name__ == "__main__":
    unittest.main()
