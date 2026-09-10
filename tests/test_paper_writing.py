"""paper-writing: scaffold, block grammar, substitution engine.

Stdlib-only `unittest`. Every fixture lives under a `TemporaryDirectory`; the
real `paper/` at the forge root is never touched by this suite outside the
one CLI subprocess test, which scaffolds under the already-gitignored
`implementations/` tree and cleans up after itself. Every
`paper_scaffold.resolve_paper_dir` call below passes an injected
`forge_root` for exactly this reason.
"""
from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
import uuid
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = FORGE_ROOT / ".claude" / "skills" / "paper-writing" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
import paper_scaffold  # noqa: E402
import paper_block  # noqa: E402
import paper_cli  # noqa: E402

sys.path.insert(0, str(FORGE_ROOT / ".claude" / "skills" / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

CLI = SKILL_SCRIPTS / "paper_cli.py"
CORE_IMPLEMENTATION = FORGE_ROOT / ".claude" / "skills" / "_core" / "implementation"


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


class TexUndecodableTests(unittest.TestCase):
    """block-substitution spec: a `main.tex` that cannot even be decoded to
    locate marker lines refuses rather than being reasoned about as source."""

    def test_undecodable_bytes_refuse_tex_undecodable(self) -> None:
        data = b"\xff\xfe not valid utf-8 \x80\x81"

        with self.assertRaises(Refused) as ctx:
            paper_block.parse(data)

        self.assertEqual(ctx.exception.code, "TEX_UNDECODABLE")


class BlockIdShapeTests(unittest.TestCase):
    """design step 1: `--block <id>` shape, checked before it is ever used
    to look anything up."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"

    def test_malformed_block_id_refuses_on_substitute(self) -> None:
        _write_fixture(self.paper_dir, _marker_pair("a", b"body\n"))

        with self.assertRaises(Refused) as ctx:
            paper_block.substitute(self.paper_dir, "not a valid id!", new_body=b"x\n")

        self.assertEqual(ctx.exception.code, "BLOCK_ID_MALFORMED")

    def test_malformed_block_id_refuses_on_open(self) -> None:
        _write_fixture(self.paper_dir, b"")

        with self.assertRaises(Refused) as ctx:
            paper_block.open_block(self.paper_dir, "bad id", at_end=True)

        self.assertEqual(ctx.exception.code, "BLOCK_ID_MALFORMED")


class ResolveMainTexTests(unittest.TestCase):
    """`open`, `status`, `substitute` never create `paper/` themselves —
    only `scaffold` does — so each refuses cleanly when it is missing."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"

    def test_substitute_on_absent_paper_dir_refuses_paper_absent(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_block.substitute(self.paper_dir, "a", new_body=b"x\n")

        self.assertEqual(ctx.exception.code, "PAPER_ABSENT")

    def test_substitute_when_paper_is_a_file_refuses_paper_not_a_directory(self) -> None:
        self.paper_dir.parent.mkdir(parents=True, exist_ok=True)
        self.paper_dir.write_bytes(b"not a directory")

        with self.assertRaises(Refused) as ctx:
            paper_block.substitute(self.paper_dir, "a", new_body=b"x\n")

        self.assertEqual(ctx.exception.code, "PAPER_NOT_A_DIRECTORY")

    def test_status_on_missing_main_tex_refuses_paper_absent(self) -> None:
        self.paper_dir.mkdir(parents=True)

        with self.assertRaises(Refused) as ctx:
            paper_block.read_status(self.paper_dir)

        self.assertEqual(ctx.exception.code, "PAPER_ABSENT")


class OpenBlockTests(unittest.TestCase):
    """block-substitution spec: `open` installs an empty pair, never
    content."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"

    def _fixture(self) -> bytes:
        return (
            b"\\documentclass{article}\n\\begin{document}\n\n"
            + _marker_pair("a", b"Body A.\n")
            + b"\n\\end{document}\n"
        )

    def test_open_after_anchor_inserts_empty_pair_and_leaves_prefix_unchanged(self) -> None:
        fixture = self._fixture()
        _write_fixture(self.paper_dir, fixture)
        anchor_end = fixture.index(b"%% paper-writing block a end") + len(
            b"%% paper-writing block a end\n"
        )

        paper_block.open_block(self.paper_dir, "b", after="a")

        post = (self.paper_dir / "main.tex").read_bytes()
        self.assertEqual(post[:anchor_end], fixture[:anchor_end])
        empty_digest = hashlib.sha256(b"").hexdigest()
        self.assertIn(
            f"%% paper-writing block b begin sha256={empty_digest}\n"
            "%% paper-writing block b end\n".encode("ascii"),
            post,
        )
        parsed = paper_block.parse(post)
        self.assertEqual(set(parsed.order), {"a", "b"})

    def test_open_on_existing_id_refuses_block_duplicated(self) -> None:
        fixture = self._fixture()
        _write_fixture(self.paper_dir, fixture)

        with self.assertRaises(Refused) as ctx:
            paper_block.open_block(self.paper_dir, "a", at_end=True)

        self.assertEqual(ctx.exception.code, "BLOCK_DUPLICATED")
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), fixture)

    def test_open_after_missing_anchor_refuses_anchor_absent(self) -> None:
        fixture = self._fixture()
        _write_fixture(self.paper_dir, fixture)

        with self.assertRaises(Refused) as ctx:
            paper_block.open_block(self.paper_dir, "b", after="missing")

        self.assertEqual(ctx.exception.code, "ANCHOR_ABSENT")
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), fixture)

    def test_open_at_end_never_inserts_a_blank_line(self) -> None:
        fixture = (b"Preamble line.\n" + _marker_pair("a", b"Body.\n")).rstrip(b"\n")
        _write_fixture(self.paper_dir, fixture)

        paper_block.open_block(self.paper_dir, "b", at_end=True)

        post = (self.paper_dir / "main.tex").read_bytes()
        added = post[len(fixture):]
        # Exactly one newline completes the unterminated last line — never a
        # blank line, which would be two in a row.
        self.assertTrue(added.startswith(b"\n%% paper-writing block b begin"))
        self.assertFalse(added.startswith(b"\n\n"))


class CLIWiringTests(unittest.TestCase):
    """CLI wiring for `open`, `status`, `substitute` — exercised as real
    subprocesses against `paper_cli.py`. `paper_cli.py` always resolves
    `--paper` against the REAL repository root (there is no injection point
    through the CLI, unlike `paper_scaffold.resolve_paper_dir`'s own
    `forge_root` kwarg), so — like
    `ScaffoldTests.test_cli_scaffold_verb_runs_and_emits_json` — every
    fixture here lives under the already-gitignored `implementations/` tree
    and is removed afterward, never under a system temp directory outside
    the repository, which `PAPER_OUTSIDE_REPOSITORY` would correctly refuse."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        test_root = FORGE_ROOT / "implementations" / f".paper-writing-cli-wiring-{os.getpid()}-{uuid.uuid4().hex[:8]}"
        self.addCleanup(shutil.rmtree, test_root, ignore_errors=True)
        self.paper_dir = test_root / "paper"

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            capture_output=True, text=True, timeout=30,
        )

    def _scaffold(self) -> None:
        proc = self._run("scaffold", "--paper", str(self.paper_dir))
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_status_reports_the_block_table_without_writing(self) -> None:
        self._scaffold()
        (self.paper_dir / "main.tex").write_bytes(_marker_pair("intro", b"Intro body.\n"))
        before = (self.paper_dir / "main.tex").read_bytes()

        proc = self._run("status", "--paper", str(self.paper_dir))

        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "ok")
        ids = {b["id"] for b in payload["blocks"]}
        self.assertEqual(ids, {"intro"})
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), before)

    def test_open_then_substitute_round_trip(self) -> None:
        self._scaffold()

        proc = self._run("open", "--paper", str(self.paper_dir), "--block", "intro", "--at-end")
        self.assertEqual(proc.returncode, 0, proc.stderr)

        body_path = Path(self._tmp.name) / "body.txt"
        body_path.write_bytes(b"New introduction.\n")
        proc = self._run(
            "substitute", "--paper", str(self.paper_dir),
            "--block", "intro", "--body", str(body_path),
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["rendering"], "unproven")
        final = (self.paper_dir / "main.tex").read_bytes()
        self.assertIn(b"New introduction.\n", final)

    def test_substitute_body_from_stdin_dash(self) -> None:
        self._scaffold()
        self._run("open", "--paper", str(self.paper_dir), "--block", "intro", "--at-end")

        proc = subprocess.run(
            [sys.executable, str(CLI), "substitute", "--paper", str(self.paper_dir),
             "--block", "intro", "--body", "-"],
            input="From stdin.\n", capture_output=True, text=True, timeout=30,
        )

        self.assertEqual(proc.returncode, 0, proc.stderr)
        final = (self.paper_dir / "main.tex").read_bytes()
        self.assertIn(b"From stdin.\n", final)

    def test_substitute_with_neither_body_nor_adopt_refuses_substitute_mode_required(self) -> None:
        self._scaffold()
        self._run("open", "--paper", str(self.paper_dir), "--block", "intro", "--at-end")

        proc = self._run("substitute", "--paper", str(self.paper_dir), "--block", "intro")

        self.assertEqual(proc.returncode, 2, proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["code"], "SUBSTITUTE_MODE_REQUIRED")

    def test_substitute_with_body_and_adopt_together_refuses_adopt_body_conflict(self) -> None:
        self._scaffold()
        self._run("open", "--paper", str(self.paper_dir), "--block", "intro", "--at-end")
        body_path = Path(self._tmp.name) / "body.txt"
        body_path.write_bytes(b"x\n")

        proc = self._run(
            "substitute", "--paper", str(self.paper_dir), "--block", "intro",
            "--body", str(body_path), "--adopt",
        )

        self.assertEqual(proc.returncode, 2, proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["code"], "ADOPT_BODY_CONFLICT")

    def test_open_with_neither_position_refuses_open_position_required(self) -> None:
        self._scaffold()

        proc = self._run("open", "--paper", str(self.paper_dir), "--block", "intro")

        self.assertEqual(proc.returncode, 2, proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["code"], "OPEN_POSITION_REQUIRED")

    def test_open_with_both_positions_refuses_open_position_conflict(self) -> None:
        self._scaffold()

        proc = self._run(
            "open", "--paper", str(self.paper_dir), "--block", "intro",
            "--after", "nope", "--at-end",
        )

        self.assertEqual(proc.returncode, 2, proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["code"], "OPEN_POSITION_CONFLICT")


PAPER_BLOCK_SOURCE = (SKILL_SCRIPTS / "paper_block.py").read_text(encoding="utf-8")


def _run_against_mutant(anchor: str, replacement: str, dotted_test: str) -> subprocess.CompletedProcess:
    """Copy `paper_block.py` into a fresh, uniquely named temp tree at the
    SAME relative depth the real script lives at (so the module's own
    `parents[2]` resolution still finds `_core/implementation`), patch its
    source with exactly one substitution, and run `dotted_test` against the
    mutant by pre-seeding `sys.modules["paper_block"]` in a bootstrap script
    — so the mutant is used regardless of any `sys.path` manipulation
    `tests/test_paper_writing.py` performs on its own (it inserts the REAL
    scripts directory at position 0 on import, which would otherwise win a
    plain `sys.path` race and silently run every mutation against the
    original file).

    Asserts the anchor matched EXACTLY once and the bytes actually changed
    before running anything: a matched-but-unapplied substitution, or one
    applied to more than one site, is not the mutation this call claims to
    run — and `git diff --stat` cannot catch it either, since the mutant
    lives in a temp directory this repository never tracks.
    """
    occurrences = PAPER_BLOCK_SOURCE.count(anchor)
    if occurrences != 1:
        raise AssertionError(
            f"anchor {anchor!r} matched {occurrences} times in paper_block.py; "
            "expected exactly 1 for the mutation to be well-defined")
    mutated = PAPER_BLOCK_SOURCE.replace(anchor, replacement, 1)
    if mutated == PAPER_BLOCK_SOURCE:
        raise AssertionError("the substitution produced no byte change")

    tmp_root = Path(tempfile.mkdtemp(prefix="paper-writing-mutant-"))
    module_name = f"paper_block_mutant_{uuid.uuid4().hex}"
    try:
        core_dst = tmp_root / "_core" / "implementation"
        core_dst.mkdir(parents=True)
        shutil.copy2(CORE_IMPLEMENTATION / "impl_refusals.py", core_dst / "impl_refusals.py")

        scripts_dst = tmp_root / "paper-writing" / "scripts"
        scripts_dst.mkdir(parents=True)
        mutant_path = scripts_dst / f"{module_name}.py"
        mutant_path.write_text(mutated, encoding="utf-8")

        # A directory created this call, never reused across mutations: no
        # __pycache__ can be stale here. PYTHONDONTWRITEBYTECODE below also
        # stops one from being written during this very run.
        bootstrap = tmp_root / "bootstrap.py"
        bootstrap.write_text(
            "import importlib.util\n"
            "import sys\n"
            "import unittest\n"
            "\n"
            f"spec = importlib.util.spec_from_file_location({module_name!r}, {str(mutant_path)!r})\n"
            "mutant = importlib.util.module_from_spec(spec)\n"
            # Registered under its OWN name too, not only under 'paper_block':
            # @dataclass's field-type resolution reads `sys.modules[cls.__module__]`
            # (== the unique spec name) during `exec_module` itself, and a module
            # missing from sys.modules under its own name makes exec_module crash
            # before a single line of the mutation is ever exercised -- a failure
            # mode indistinguishable from a genuine test failure by exit code
            # alone, which is exactly why this is asserted separately below.
            f"sys.modules[{module_name!r}] = mutant\n"
            "sys.modules['paper_block'] = mutant\n"
            "spec.loader.exec_module(mutant)\n"
            # A marker unittest's own runner never prints, so the caller can
            # tell 'the mutant module failed to even import' (a harness
            # defect) apart from 'unittest ran the named test and it failed'
            # (the actual proof this whole harness exists to produce) --
            # both exit non-zero, and only one of them says anything about
            # the mutation.
            "print('MUTANT_IMPORTED_OK')\n"
            "\n"
            f"program = unittest.main(module=None, argv=['prog', {dotted_test!r}], exit=False)\n"
            "sys.exit(0 if program.result.wasSuccessful() else 1)\n",
            encoding="utf-8",
        )

        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        existing_path = env.get("PYTHONPATH", "")
        env["PYTHONPATH"] = str(FORGE_ROOT) + (os.pathsep + existing_path if existing_path else "")

        return subprocess.run(
            [sys.executable, str(bootstrap)],
            cwd=str(FORGE_ROOT), capture_output=True, text=True, timeout=60, env=env,
        )
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)


class MutationProofTests(unittest.TestCase):
    """Independent byte-identity verification, executed rather than
    asserted in prose. Each mutation below runs against a real subprocess
    and the corresponding guard test's own exit code is read, not guessed
    at.

    Every assertion below is two-part on purpose. `MUTANT_IMPORTED_OK` in
    stdout proves the mutant module actually loaded and `unittest` actually
    ran the named test against it; without that check, a subprocess that
    crashed on import (before the named test ever ran) and a subprocess
    where the guard genuinely failed are the same non-zero exit code, and
    this harness would be proving nothing about the mutation at all — the
    exact failure mode measured once already (`@dataclass` field-type
    resolution needs the mutant registered in `sys.modules` under its own
    `__name__`, not only under `'paper_block'`).
    """

    def _assert_guard_failed_under_mutation(self, proc: subprocess.CompletedProcess) -> None:
        output = proc.stdout + proc.stderr
        self.assertIn("MUTANT_IMPORTED_OK", output, output)
        self.assertNotEqual(proc.returncode, 0, output)

    def test_m1_region_start_one_byte_earlier_fails_the_byte_identity_test(self) -> None:
        # Mutates the WRITE path (`build_candidate`'s own slicing), not the
        # independent verification (`project()`, left untouched). A shift
        # applied symmetrically inside `project()` alone is invisible by
        # construction -- both sides of the comparison would be blind to the
        # exact same swallowed byte, and this was measured, not assumed: an
        # earlier version of this test mutated `project()`'s region list
        # instead and passed green with no guard ever firing. Shifting the
        # boundary actually used to slice `pre` when building the candidate
        # drops one real byte from what reaches disk, which the UNMUTATED,
        # independently re-parsing `project()` then genuinely disagrees
        # about.
        proc = _run_against_mutant(
            'candidate = pre[:begin["start"]] + new_begin_line + written_body + pre[end["start"]:]',
            'candidate = pre[:begin["start"] - 1] + new_begin_line + written_body + pre[end["start"]:]',
            "tests.test_paper_writing.InvariantTests.test_only_the_named_block_changes_three_conjuncts",
        )

        self._assert_guard_failed_under_mutation(proc)

    def test_m2_text_mode_open_against_crlf_fixture_fails_the_byte_identity_test(self) -> None:
        # `newline=None` universal-newlines mode, opened via the builtin
        # `open()` -- matching the CRLFTests fixture's own control assertion
        # exactly, so this exercises the real CRLF-flattening semantics the
        # spec's M2 names, not an unrelated crash from a keyword argument
        # `Path.read_text()` does not accept on this interpreter.
        #
        # For THIS fixture specifically, the guard that actually fires first
        # is `BLOCK_HAND_EDITED`, not `SUBSTITUTION_NOT_LOCAL`: the target
        # block's own body also carries CRLF, so flattening corrupts its
        # on-disk digest before the in-memory byte-identity check ever runs.
        # A fixture whose block body carried no CRLF would instead reach
        # `identity_invariant` and fail there -- both are real guards inside
        # the same safety net (design.md, "Guards that protect but are not
        # net layers"), and either one refusing is the property this test
        # proves: text-mode corruption never reaches disk.
        proc = _run_against_mutant(
            'pre = tex_path.read_bytes()\n    pre_digest = hashlib.sha256(pre).hexdigest()\n\n'
            '    parsed = parse(pre)\n    candidate, written_body = build_candidate(',
            'with open(tex_path, "r", newline=None) as _h:\n'
            '        pre = _h.read().encode("utf-8")\n'
            '    pre_digest = hashlib.sha256(pre).hexdigest()\n\n'
            '    parsed = parse(pre)\n    candidate, written_body = build_candidate(',
            "tests.test_paper_writing.CRLFTests"
            ".test_crlf_block_round_trips_untouched_and_text_mode_would_corrupt_it",
        )

        self._assert_guard_failed_under_mutation(proc)

    def test_m3_skipped_digest_comparison_fails_the_hand_edit_guard(self) -> None:
        proc = _run_against_mutant(
            'if on_disk_digest != begin["digest"]:',
            "if False:",
            "tests.test_paper_writing.BlockCoreTests.test_hand_edited_body_refuses_naming_both_digests",
        )

        self._assert_guard_failed_under_mutation(proc)


REFUSAL_CONSTRUCTORS = ("Refused",)
REFUSAL_CODE_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+$")


def _refusal_code_argument(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _refusal_sites(node, owner: str) -> list[tuple[str, str | None]]:
    """Every refusal constructed anywhere under `node`, as `(owner, code)` —
    the same shape `test_proposal_implementation.py` uses for its own
    roster, scoped here to this skill's three files."""
    sites: list[tuple[str, str | None]] = []
    for child in ast.iter_child_nodes(node):
        if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
            sites += _refusal_sites(child, child.name)
            continue
        if (isinstance(child, ast.Call) and isinstance(child.func, ast.Name)
                and child.func.id in REFUSAL_CONSTRUCTORS):
            sites.append(
                (owner, _refusal_code_argument(child.args[0]) if child.args else None))
        sites += _refusal_sites(child, owner)
    return sites


def _module_code_constants(tree) -> set[str]:
    constants = set()
    for statement in tree.body:
        if not isinstance(statement, (ast.Assign, ast.AnnAssign)) or statement.value is None:
            continue
        for node in ast.walk(statement.value):
            if (isinstance(node, ast.Constant) and isinstance(node.value, str)
                    and REFUSAL_CODE_RE.match(node.value)):
                constants.add(node.value)
    return constants


def _codes_from_sites(sites, constants: set[str]) -> set[str]:
    codes = {code for _, code in sites if code is not None}
    if any(code is None for _, code in sites):
        codes |= constants
    return codes


def unreadable_paper_refusal_sites() -> set[tuple[str, str]]:
    sites = set()
    for source in (CLI, SKILL_SCRIPTS / "paper_block.py", SKILL_SCRIPTS / "paper_scaffold.py"):
        tree = ast.parse(source.read_text(encoding="utf-8"))
        sites |= {(source.name, owner)
                  for owner, code in _refusal_sites(tree, "<module>")
                  if code is None}
    return sites


def reachable_paper_refusal_codes() -> set[str]:
    """Every refusal code a `paper_cli.py` command can raise, derived from
    source — never hand-listed. The same shape as
    `test_proposal_implementation.reachable_refusal_codes`: a closure from
    `paper_cli.py`'s `cmd_*` roots (following calls into helpers defined in
    `paper_cli.py` itself), UNIONED with a whole-module scan of
    `paper_block.py` and `paper_scaffold.py` — this skill's own helper
    modules, playing the role `_core/implementation/*.py` plays for the
    sibling skill. `impl_refusals.py` contributes nothing: it raises no
    `Refused` of its own (design.md's `Own modules; import only Refused`
    decision) — the whole point of that choice being that this skill's
    roster and the sibling skill's roster never share an entry neither owns.
    """
    tree = ast.parse(CLI.read_text(encoding="utf-8"))
    definitions = {node.name: node for node in tree.body
                   if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    roots = [f"cmd_{command}" for command in paper_cli.COMMANDS]
    for root in roots:
        if root not in definitions:
            raise AssertionError(f"paper_cli.py defines no {root}")
    constants = _module_code_constants(tree)
    codes: set[str] = set()
    seen: set[str] = set()
    frontier = list(roots)
    while frontier:
        name = frontier.pop()
        if name in seen:
            continue
        seen.add(name)
        definition = definitions[name]
        codes |= _codes_from_sites(_refusal_sites(definition, name), constants)
        frontier += [node.id for node in ast.walk(definition)
                     if isinstance(node, ast.Name)
                     and isinstance(node.ctx, ast.Load)
                     and node.id in definitions]
    for source in (SKILL_SCRIPTS / "paper_block.py", SKILL_SCRIPTS / "paper_scaffold.py"):
        module = ast.parse(source.read_text(encoding="utf-8"))
        codes |= _codes_from_sites(_refusal_sites(module, "<module>"),
                                    _module_code_constants(module))
    return codes


class RefusalRosterTests(unittest.TestCase):
    """Every refusal reachable from a `paper_cli.py` command is classified,
    and nothing is classified that no command can reach — the lock
    `GatingRefusalRosterTests` holds `implementation_cli.py` to, derived
    rather than hand-listed so a new `Refused` anywhere in this skill's
    three files goes red here until somebody classifies it."""

    def test_every_reachable_refusal_is_classified(self) -> None:
        missing = sorted(reachable_paper_refusal_codes() - set(paper_cli.REFUSAL_CLASSIFICATION))
        self.assertEqual(
            missing, [],
            "these codes are reachable and the roster classifies none of them; a "
            "refusal nobody decided about is the defect this roster exists to make "
            "impossible")

    def test_the_roster_classifies_nothing_unreachable(self) -> None:
        extra = sorted(set(paper_cli.REFUSAL_CLASSIFICATION) - reachable_paper_refusal_codes())
        self.assertEqual(
            extra, [],
            "the roster classifies these and no command can reach them")

    def test_every_classification_is_invocation_defect_or_work_state(self) -> None:
        allowed = {paper_cli.INVOCATION_DEFECT, paper_cli.WORK_STATE}
        bad = {code: cls for code, cls in paper_cli.REFUSAL_CLASSIFICATION.items()
               if cls not in allowed}
        self.assertEqual(bad, {})

    def test_the_derivation_has_no_unreadable_sites(self) -> None:
        """No refusal in this skill's three files raises a code this walk
        cannot read as a string literal — asserted rather than assumed, so a
        future dynamic code site is looked at by a human instead of silently
        widening to a module's constants."""
        self.assertEqual(unreadable_paper_refusal_sites(), set())

    def test_the_derivation_finds_the_measured_count(self) -> None:
        """Sanity check on the derivation itself: a change that adds,
        removes or renames a refusal anywhere reachable should move this
        number, never a typo in the walk above."""
        self.assertEqual(len(reachable_paper_refusal_codes()), 21)


if __name__ == "__main__":
    unittest.main()
