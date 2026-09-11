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
import inspect
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
SECTIONS_DIR = FORGE_ROOT / "sections"
sys.path.insert(0, str(SKILL_SCRIPTS))
import paper_scaffold  # noqa: E402
import paper_block  # noqa: E402
import paper_cli  # noqa: E402
import paper_contract  # noqa: E402
import paper_vocabulary  # noqa: E402
import paper_bindings  # noqa: E402
import paper_audit  # noqa: E402
import paper_write  # noqa: E402
import paper_style  # noqa: E402
import paper_leak  # noqa: E402

sys.path.insert(0, str(FORGE_ROOT / ".claude" / "skills" / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

sys.path.insert(0, str(FORGE_ROOT / "tests"))
from paper_mutation import _run_against_mutant  # noqa: E402

CLI = SKILL_SCRIPTS / "paper_cli.py"
CORE_IMPLEMENTATION = FORGE_ROOT / ".claude" / "skills" / "_core" / "implementation"


#: Guarded, module-scoped `subprocess.Popen` monitor
#: (`writing-orchestration` spec, `Requirement: No Live Agent Invocation In
#: Tests`). Installed at IMPORT time, before any test in this module (or,
#: under `python -m unittest discover`, any test collected alongside it)
#: runs -- passive observation only, never blocking, so it cannot break an
#: unrelated suite's own legitimate subprocess use (`git`, `sys.executable`
#: running this skill's own CLI, etc). `paper-writing` never ships a code
#: path that spawns an agent binary (`design.md`, Decision D2: "No
#: agent-invoking code path exists"), so the list this accumulates is
#: asserted empty by `ZZLiveAgentGuardTests` below.
_AGENT_BINARY_NAMES = ("claude", "gemini", "codex", "pi", "claude-code")
_live_agent_launches: list[list[str]] = []
_real_popen_init = subprocess.Popen.__init__


def _guarded_popen_init(self, args, *a, **kw):
    argv = args if isinstance(args, (list, tuple)) else [args]
    head = Path(str(argv[0])).name if argv else ""
    if head in _AGENT_BINARY_NAMES:
        _live_agent_launches.append([str(x) for x in argv])
    return _real_popen_init(self, args, *a, **kw)


subprocess.Popen.__init__ = _guarded_popen_init


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


# =====================================================================
# the-writer-may-assert-only-what-it-was-given -- Work Unit 1
# =====================================================================


class ModeWideningTests(unittest.TestCase):
    """`section-contract` spec delta: `mode` joins `_TOP_LEVEL_OPTIONAL`/
    `_BLOCK_OPTIONAL`."""

    def _header(self, *, section_mode=None, block_mode=None) -> dict:
        header = {
            "section": "demo", "position": 1,
            "blocks": [{
                "id": "b1", "requires_facts": [], "requires_declarations": [],
                "citations": "none",
            }],
        }
        if section_mode is not None:
            header["mode"] = section_mode
        if block_mode is not None:
            header["blocks"][0]["mode"] = block_mode
        return header

    def _mode_obj(self, value: str) -> dict:
        return {"value": value, "source": {"file": "demo.md", "quote": "some prose"}}

    def test_a_valid_mode_value_parses(self) -> None:
        header = paper_contract.parse_header(self._header(block_mode=self._mode_obj("transposition")))
        self.assertEqual(header.blocks[0]["mode"]["value"], "transposition")

    def test_an_invalid_mode_value_refuses_unknown_mode(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_contract.parse_header(self._header(block_mode=self._mode_obj("exposition")))
        self.assertEqual(ctx.exception.code, "UNKNOWN_MODE")
        self.assertIn("exposition", ctx.exception.detail)

    def test_a_block_inherits_the_section_level_mode(self) -> None:
        header = paper_contract.parse_header(self._header(section_mode=self._mode_obj("argument")))
        resolved = paper_contract.resolve_mode(header, header.blocks[0])
        self.assertEqual(resolved["value"], "argument")

    def test_a_blocks_own_mode_overrides_the_section_level_default(self) -> None:
        header = paper_contract.parse_header(self._header(
            section_mode=self._mode_obj("argument"), block_mode=self._mode_obj("transposition"),
        ))
        resolved = paper_contract.resolve_mode(header, header.blocks[0])
        self.assertEqual(resolved["value"], "transposition")

    def test_neither_level_declaring_mode_resolves_to_none(self) -> None:
        header = paper_contract.parse_header(self._header())
        self.assertIsNone(paper_contract.resolve_mode(header, header.blocks[0]))

    def test_all_ten_shipped_contracts_still_parse_with_no_mode_declared(self) -> None:
        # `Headers Written Before mode Existed`: sections/*.md ship with no
        # `mode` key yet, and that absence is schema-valid, not a
        # violation -- `write`'s own readiness stage is what refuses on it
        # (`WritingPipelineTests.test_no_mode_resolved_refuses_mode_absent`
        # below), never this reader.
        for path in sorted(SECTIONS_DIR.glob("*.md")):
            header, _body = paper_contract.parse(path.read_bytes())
            self.assertIsNone(header.mode, path.name)
            for block in header.blocks:
                self.assertIsNone(paper_contract.resolve_mode(header, block), (path.name, block["id"]))


class RedactorInputContractTests(unittest.TestCase):
    """`evidence-bound-drafting` spec, `Requirement: Redactor Input
    Contract`."""

    def test_empty_style_set_is_a_valid_input(self) -> None:
        redactor_input = paper_bindings.RedactorInput(
            contract_prose="Some contract prose.", evidence_set=(), mode="transposition", style_set=(),
        )
        self.assertEqual(redactor_input.style_set, ())
        self.assertEqual(redactor_input.contract_prose, "Some contract prose.")


class BindingMapTests(unittest.TestCase):
    """`evidence-bound-drafting` spec, `Requirement: Binding Map
    Production`, `Requirement: Draft-Versus-Map Reconciliation`,
    `Requirement: Binding Resolution`."""

    def test_every_binding_entry_names_one_of_the_three_kinds(self) -> None:
        for raw, expected in (
            ("evidence:E1", ("evidence", "E1")),
            ("fact:results", ("fact", "results")),
            ("structural", ("structural", None)),
        ):
            with self.subTest(raw=raw):
                self.assertEqual(paper_bindings.parse_binding(raw), expected)

    def test_an_unbound_sentence_refuses(self) -> None:
        latex = "First sentence. Second sentence."
        bindings = [{"sentence": "First sentence.", "binding": "structural"}]
        with self.assertRaises(Refused) as ctx:
            paper_bindings.reconcile(latex, bindings)
        self.assertEqual(ctx.exception.code, "UNBOUND_SENTENCE")
        self.assertIn("Second sentence.", ctx.exception.detail)

    def test_an_orphaned_binding_refuses(self) -> None:
        latex = "Only sentence here."
        bindings = [
            {"sentence": "Only sentence here.", "binding": "structural"},
            {"sentence": "Nothing drafted matches this.", "binding": "structural"},
        ]
        with self.assertRaises(Refused) as ctx:
            paper_bindings.reconcile(latex, bindings)
        self.assertEqual(ctx.exception.code, "BINDING_ORPHANED")
        self.assertIn("Nothing drafted matches this.", ctx.exception.detail)

    def test_an_unknown_evidence_id_refuses(self) -> None:
        bindings = [paper_bindings.Binding(sentence="s", kind="evidence", ref="E9")]
        with self.assertRaises(Refused) as ctx:
            paper_bindings.resolve_bindings(bindings, evidence_ids=set(), licensed_facts=set())
        self.assertEqual(ctx.exception.code, "EVIDENCE_ID_UNKNOWN")
        self.assertIn("E9", ctx.exception.detail)

    def test_an_unlicensed_fact_id_refuses(self) -> None:
        bindings = [paper_bindings.Binding(sentence="s", kind="fact", ref="results")]
        with self.assertRaises(Refused) as ctx:
            paper_bindings.resolve_bindings(bindings, evidence_ids=set(), licensed_facts=set())
        self.assertEqual(ctx.exception.code, "FACT_NOT_LICENSED")
        self.assertIn("results", ctx.exception.detail)

    def test_licensed_ids_resolve_without_refusing(self) -> None:
        bindings = [
            paper_bindings.Binding(sentence="s1", kind="evidence", ref="E1"),
            paper_bindings.Binding(sentence="s2", kind="fact", ref="results"),
        ]
        paper_bindings.resolve_bindings(bindings, evidence_ids={"E1"}, licensed_facts={"results"})


class StructuralTypingTests(unittest.TestCase):
    """`evidence-bound-drafting` spec, `Requirement: Structural Sentences
    Are Typed` (`design.md`, Decision D3)."""

    def test_a_numeral_inside_a_structural_sentence_refuses(self) -> None:
        bindings = [paper_bindings.Binding(sentence="We report 42% accuracy.", kind="structural", ref=None)]
        with self.assertRaises(Refused) as ctx:
            paper_bindings.type_structural(bindings, contract_prose="")
        self.assertEqual(ctx.exception.code, "STRUCTURAL_CARRIES_CLAIM")

    def test_a_plain_structural_sentence_passes(self) -> None:
        bindings = [
            paper_bindings.Binding(sentence="This paragraph closes the section.", kind="structural", ref=None)
        ]
        paper_bindings.type_structural(bindings, contract_prose="")

    def test_a_cite_command_inside_structural_refuses(self) -> None:
        bindings = [
            paper_bindings.Binding(
                sentence="See the prior work \\cite{smith2020}.", kind="structural", ref=None
            )
        ]
        with self.assertRaises(Refused) as ctx:
            paper_bindings.type_structural(bindings, contract_prose="")
        self.assertEqual(ctx.exception.code, "STRUCTURAL_CARRIES_CLAIM")

    def test_a_comparative_inside_structural_refuses(self) -> None:
        bindings = [
            paper_bindings.Binding(
                sentence="This method is faster than the baseline.", kind="structural", ref=None
            )
        ]
        with self.assertRaises(Refused) as ctx:
            paper_bindings.type_structural(bindings, contract_prose="")
        self.assertEqual(ctx.exception.code, "STRUCTURAL_CARRIES_CLAIM")

    def test_a_named_external_object_absent_from_contract_prose_refuses(self) -> None:
        bindings = [
            paper_bindings.Binding(
                sentence="This closes the discussion of Transformer.", kind="structural", ref=None
            )
        ]
        with self.assertRaises(Refused) as ctx:
            paper_bindings.type_structural(bindings, contract_prose="No mention of that architecture here.")
        self.assertEqual(ctx.exception.code, "STRUCTURAL_CARRIES_CLAIM")

    def test_a_named_object_present_verbatim_in_contract_prose_passes(self) -> None:
        bindings = [
            paper_bindings.Binding(
                sentence="This closes the discussion of Transformer.", kind="structural", ref=None
            )
        ]
        paper_bindings.type_structural(bindings, contract_prose="This section discusses Transformer at length.")


class ModeAdmissibilityTests(unittest.TestCase):
    """`evidence-bound-drafting` spec, `Requirement: Mode-Admissible
    Bindings`."""

    def test_transposition_rejects_a_discovery_binding(self) -> None:
        bindings = [paper_bindings.Binding(sentence="s", kind="evidence", ref="D1")]
        evidence_by_id = {"D1": {"id": "D1", "regime": "discovery"}}
        with self.assertRaises(Refused) as ctx:
            paper_bindings.check_mode_admissibility(bindings, "transposition", evidence_by_id)
        self.assertEqual(ctx.exception.code, "MODE_VIOLATION")
        self.assertIn("D1", ctx.exception.detail)

    def test_argument_admits_the_same_discovery_binding(self) -> None:
        bindings = [paper_bindings.Binding(sentence="s", kind="evidence", ref="D1")]
        evidence_by_id = {"D1": {"id": "D1", "regime": "discovery"}}
        paper_bindings.check_mode_admissibility(bindings, "argument", evidence_by_id)

    def test_both_modes_admit_resolution_class_evidence(self) -> None:
        bindings = [paper_bindings.Binding(sentence="s", kind="evidence", ref="R1")]
        evidence_by_id = {"R1": {"id": "R1", "regime": "resolution"}}
        paper_bindings.check_mode_admissibility(bindings, "transposition", evidence_by_id)
        paper_bindings.check_mode_admissibility(bindings, "argument", evidence_by_id)


_SAMPLE_DISQUALIFIER = "A symbol used without being declared."


def _contract_body(bullets: list) -> str:
    lines = ["# Demo Contract", "", "Some prose.", "", "## Disqualifiers"]
    lines += [f"- {bullet}" for bullet in bullets]
    return "\n".join(lines) + "\n"


class ContractAuditTests(unittest.TestCase):
    """`contract-audit` spec."""

    def test_bullet_text_reaches_the_audit_unchanged(self) -> None:
        bullets = paper_audit.extract_disqualifiers(_contract_body([_SAMPLE_DISQUALIFIER]))
        self.assertEqual(bullets, [_SAMPLE_DISQUALIFIER])

    def test_a_firing_disqualifier_quotes_its_span(self) -> None:
        body = _contract_body([_SAMPLE_DISQUALIFIER])
        draft = "A symbol X appears with no declaration."
        verdicts = [
            {"bullet": _SAMPLE_DISQUALIFIER, "verdict": "fires",
             "span": "symbol X appears with no declaration"}
        ]
        result = paper_audit.audit(body, draft, verdicts)
        self.assertTrue(result["blocks"])
        self.assertEqual(result["fired"][0]["span"], "symbol X appears with no declaration")

    def test_clear_and_firing_coexist_in_one_run(self) -> None:
        second = "A dataset described here and left unreferenced."
        body = _contract_body([_SAMPLE_DISQUALIFIER, second])
        draft = "A symbol X appears with no declaration."
        verdicts = [
            {"bullet": _SAMPLE_DISQUALIFIER, "verdict": "fires",
             "span": "symbol X appears with no declaration"},
            {"bullet": second, "verdict": "clear"},
        ]
        result = paper_audit.audit(body, draft, verdicts)
        by_bullet = {entry["bullet"]: entry["verdict"] for entry in result["verdicts"]}
        self.assertEqual(by_bullet[_SAMPLE_DISQUALIFIER], "fires")
        self.assertEqual(by_bullet[second], "clear")

    def test_an_all_undecidable_audit_does_not_block(self) -> None:
        second = "A dataset described here and left unreferenced."
        body = _contract_body([_SAMPLE_DISQUALIFIER, second])
        verdicts = [
            {"bullet": _SAMPLE_DISQUALIFIER, "verdict": "undecidable"},
            {"bullet": second, "verdict": "undecidable"},
        ]
        result = paper_audit.audit(body, "draft text", verdicts)
        self.assertFalse(result["blocks"])
        self.assertEqual({entry["verdict"] for entry in result["verdicts"]}, {"undecidable"})

    def test_one_firing_bullet_blocks_regardless_of_undecidables(self) -> None:
        second, third = "second bullet text.", "third bullet text."
        body = _contract_body([_SAMPLE_DISQUALIFIER, second, third])
        draft = "The offending clause appears here."
        verdicts = [
            {"bullet": _SAMPLE_DISQUALIFIER, "verdict": "fires",
             "span": "The offending clause appears here"},
            {"bullet": second, "verdict": "undecidable"},
            {"bullet": third, "verdict": "undecidable"},
        ]
        result = paper_audit.audit(body, draft, verdicts)
        self.assertTrue(result["blocks"])
        self.assertEqual(result["fired"][0]["bullet"], _SAMPLE_DISQUALIFIER)

    def test_a_fires_verdict_with_no_span_downgrades_to_undecidable(self) -> None:
        body = _contract_body([_SAMPLE_DISQUALIFIER])
        verdicts = [{"bullet": _SAMPLE_DISQUALIFIER, "verdict": "fires", "span": ""}]
        result = paper_audit.audit(body, "draft text", verdicts)
        self.assertFalse(result["blocks"])
        self.assertEqual(result["verdicts"][0]["verdict"], "undecidable")

    def test_a_fires_verdict_whose_span_is_not_in_the_draft_downgrades(self) -> None:
        body = _contract_body([_SAMPLE_DISQUALIFIER])
        verdicts = [{"bullet": _SAMPLE_DISQUALIFIER, "verdict": "fires", "span": "not present anywhere"}]
        result = paper_audit.audit(body, "draft text entirely unrelated", verdicts)
        self.assertFalse(result["blocks"])
        self.assertEqual(result["verdicts"][0]["verdict"], "undecidable")

    def test_a_contract_missing_the_heading_refuses(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_audit.extract_disqualifiers(
                "# Demo\n\nNo disqualifiers section here.\n", source_name="demo.md"
            )
        self.assertEqual(ctx.exception.code, "DISQUALIFIERS_ABSENT")
        self.assertIn("demo.md", ctx.exception.detail)

    def test_all_ten_shipped_contracts_carry_the_heading(self) -> None:
        for path in sorted(SECTIONS_DIR.glob("*.md")):
            _header, body = paper_contract.parse(path.read_bytes())
            bullets = paper_audit.extract_disqualifiers(body.decode("utf-8"), source_name=path.name)
            self.assertGreater(len(bullets), 0, path.name)

    def test_a_verdict_naming_an_unknown_bullet_refuses(self) -> None:
        verdicts = [{"bullet": "not a real bullet", "verdict": "clear"}]
        with self.assertRaises(Refused) as ctx:
            paper_audit.reconcile_verdicts([_SAMPLE_DISQUALIFIER], verdicts, "draft")
        self.assertEqual(ctx.exception.code, "VERDICT_BULLET_UNKNOWN")

    def test_a_missing_verdict_for_a_real_bullet_refuses(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_audit.reconcile_verdicts([_SAMPLE_DISQUALIFIER], [], "draft")
        self.assertEqual(ctx.exception.code, "VERDICT_MISSING")


def _write_contract(
    *, block_id="mm-proposal", citations_regime="resolution", mode="transposition",
    requires_facts=(), evidence_set=(), disqualifiers=(_SAMPLE_DISQUALIFIER,),
) -> "paper_write.BlockContract":
    return paper_write.BlockContract(
        block_id=block_id,
        contract_prose=_contract_body(list(disqualifiers)),
        contract_source="demo.md",
        citations_regime=citations_regime,
        mode=mode,
        requires_facts=tuple(requires_facts),
        evidence_set=tuple(evidence_set),
    )


_CLEAN_DRAFT = {
    "latex": "This paragraph closes the section.",
    "bindings": [{"sentence": "This paragraph closes the section.", "binding": "structural"}],
}
_CLEAN_AUDIT = {"verdicts": [{"bullet": _SAMPLE_DISQUALIFIER, "verdict": "clear"}]}
_FIRING_AUDIT = {
    "verdicts": [
        {"bullet": _SAMPLE_DISQUALIFIER, "verdict": "fires", "span": "This paragraph closes the section"}
    ]
}


class WritingPipelineTests(unittest.TestCase):
    """`writing-orchestration` spec. This is one of the two decisive proofs
    for this change (per the orchestrator's launch context): the claim
    "an assertion outside the evidence set never reaches main.tex" is
    exercised here end to end, not merely asserted."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"
        _write_fixture(self.paper_dir, _marker_pair("mm-proposal", b"Old body.\n"))

    def test_a_clean_pipeline_writes_the_block(self) -> None:
        contract = _write_contract(citations_regime="none", evidence_set=())
        result = paper_write.write_block(self.paper_dir, contract, _CLEAN_DRAFT, _CLEAN_AUDIT)
        self.assertEqual(result["status"], "written")
        final = (self.paper_dir / "main.tex").read_bytes()
        self.assertIn(b"This paragraph closes the section.", final)

    def test_no_mode_resolved_refuses_mode_absent(self) -> None:
        contract = _write_contract(citations_regime="none", mode=None)
        with self.assertRaises(Refused) as ctx:
            paper_write.write_block(self.paper_dir, contract, _CLEAN_DRAFT, _CLEAN_AUDIT)
        self.assertEqual(ctx.exception.code, "MODE_ABSENT")

    def test_a_citing_block_with_no_evidence_set_refuses_evidence_set_required(self) -> None:
        contract = _write_contract(citations_regime="resolution", evidence_set=())
        with self.assertRaises(Refused) as ctx:
            paper_write.write_block(self.paper_dir, contract, _CLEAN_DRAFT, _CLEAN_AUDIT)
        self.assertEqual(ctx.exception.code, "EVIDENCE_SET_REQUIRED")
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), _marker_pair("mm-proposal", b"Old body.\n"))

    def test_a_none_regime_block_with_no_evidence_writes_with_no_refusal(self) -> None:
        contract = _write_contract(citations_regime="none", evidence_set=())
        result = paper_write.write_block(self.paper_dir, contract, _CLEAN_DRAFT, _CLEAN_AUDIT)
        self.assertEqual(result["status"], "written")

    def test_an_assertion_outside_the_evidence_set_never_reaches_main_tex(self) -> None:
        """The decisive proof: give the writer an evidence set, then draft a
        binding naming an id outside it -- and confirm main.tex never
        changes."""
        contract = _write_contract(
            citations_regime="resolution", evidence_set=({"id": "E1", "regime": "resolution"},),
        )
        draft = {
            "latex": "This closes on the recorded evidence. This asserts an outside claim.",
            "bindings": [
                {"sentence": "This closes on the recorded evidence.", "binding": "evidence:E1"},
                {"sentence": "This asserts an outside claim.", "binding": "evidence:E9"},
            ],
        }
        pre = (self.paper_dir / "main.tex").read_bytes()
        with self.assertRaises(Refused) as ctx:
            paper_write.write_block(self.paper_dir, contract, draft, _CLEAN_AUDIT)
        self.assertEqual(ctx.exception.code, "EVIDENCE_ID_UNKNOWN")
        self.assertIn("E9", ctx.exception.detail)
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), pre)

    def test_a_failing_evidence_audit_stops_before_contract_audit_runs(self) -> None:
        contract = _write_contract(citations_regime="none", evidence_set=())
        bad_draft = {
            "latex": "First sentence. Second sentence.",
            "bindings": [{"sentence": "First sentence.", "binding": "structural"}],
        }
        with unittest.mock.patch("paper_audit.audit") as mocked_audit:
            with self.assertRaises(Refused) as ctx:
                paper_write.write_block(self.paper_dir, contract, bad_draft, _CLEAN_AUDIT)
        self.assertEqual(ctx.exception.code, "UNBOUND_SENTENCE")
        mocked_audit.assert_not_called()
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), _marker_pair("mm-proposal", b"Old body.\n"))

    def test_one_bounded_redraft_reports_fired_bullets_as_feedback(self) -> None:
        contract = _write_contract(citations_regime="none", evidence_set=())
        result = paper_write.write_block(self.paper_dir, contract, _CLEAN_DRAFT, _FIRING_AUDIT)
        self.assertEqual(result["status"], "audit-fired")
        self.assertEqual(result["attempt"], 1)
        self.assertEqual(result["fired"][0]["bullet"], _SAMPLE_DISQUALIFIER)
        self.assertEqual(result["fired"][0]["span"], "This paragraph closes the section")
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), _marker_pair("mm-proposal", b"Old body.\n"))

    def test_the_second_attempt_is_audited_with_the_same_inputs(self) -> None:
        contract = _write_contract(citations_regime="none", evidence_set=())
        paper_write.write_block(self.paper_dir, contract, _CLEAN_DRAFT, _FIRING_AUDIT)
        # Same contract/evidence/mode -- the ledger recognizes this as
        # attempt 2 against the SAME key, exactly what "the re-draft's
        # input includes ... the same contract, evidence set, and mode as
        # the first attempt" requires.
        key_before = paper_write._attempt_key(contract)
        ledger = paper_write._read_ledger(self.paper_dir, "mm-proposal")
        self.assertEqual(ledger["key"], key_before)
        self.assertEqual(ledger["attempts"], 1)

    def test_two_failing_audits_leave_main_tex_unchanged_and_refuse_audit_exhausted(self) -> None:
        contract = _write_contract(citations_regime="none", evidence_set=())
        pre = (self.paper_dir / "main.tex").read_bytes()
        paper_write.write_block(self.paper_dir, contract, _CLEAN_DRAFT, _FIRING_AUDIT)
        with self.assertRaises(Refused) as ctx:
            paper_write.write_block(self.paper_dir, contract, _CLEAN_DRAFT, _FIRING_AUDIT)
        self.assertEqual(ctx.exception.code, "AUDIT_EXHAUSTED")
        self.assertIn(_SAMPLE_DISQUALIFIER, ctx.exception.detail)
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), pre)

    def test_a_changed_input_starts_a_fresh_attempt_budget(self) -> None:
        contract = _write_contract(citations_regime="none", evidence_set=())
        paper_write.write_block(self.paper_dir, contract, _CLEAN_DRAFT, _FIRING_AUDIT)
        different_contract = _write_contract(citations_regime="none", evidence_set=(), mode="argument")
        result = paper_write.write_block(self.paper_dir, different_contract, _CLEAN_DRAFT, _FIRING_AUDIT)
        self.assertEqual(result["status"], "audit-fired")
        self.assertEqual(result["attempt"], 1)


class StyleChannelReportingTests(unittest.TestCase):
    """Ruling 2 (orchestrator, this change): an all-`noEquivalent` style set
    reports `unmeasured`, it does not pass."""

    def test_empty_style_set_reports_unmeasured(self) -> None:
        result = paper_write.style_channel_report([], None, None)
        self.assertEqual(result["status"], "unmeasured")

    def test_nonempty_style_set_reports_measured(self) -> None:
        recorded = [{"reference": "paperA", "span": "x"}]
        result = paper_write.style_channel_report(recorded, {"pass": True}, {"pass": True})
        self.assertEqual(result["status"], "measured")


# =====================================================================
# Ruling 1 -- the no-subprocess seam, with exactly one named exception
# =====================================================================

#: The one file this skill will ever let import `subprocess`, for
#: `latexmk` (`a-diagram-that-compiles-or-says-why`, not yet landed; the
#: orchestrator's Ruling 1 for this change). Named here, not empty, so this
#: scan already tolerates it the moment that sibling's file appears on
#: disk. Pinned to `len(...) == 1` below: a SECOND name requires
#: hand-editing that literal in a diff someone reads.
SUBPROCESS_EXCEPTIONS: tuple = ("paper_latex.py",)


def _forbidden_process_names_in(source_path: Path) -> list:
    tree = ast.parse(source_path.read_text(encoding="utf-8"))
    found: list = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in ("subprocess", "multiprocessing"):
                    found.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module in ("subprocess", "multiprocessing"):
            found.append(node.module)
        elif (isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name)
                and node.value.id == "os"):
            if node.attr in ("system", "popen") or node.attr.startswith("exec"):
                found.append(f"os.{node.attr}")
    return found


def scan_forbidden_process_imports(scripts_dir: Path) -> dict:
    """`design.md`, Decision D2 / Threat Matrix "Process integration":
    forbids `subprocess`, `os.system`, `os.popen`, `os.exec*`,
    `multiprocessing` across every `scripts/*.py` except
    `SUBPROCESS_EXCEPTIONS`."""
    violations: dict = {}
    for path in sorted(scripts_dir.glob("*.py")):
        if path.name in SUBPROCESS_EXCEPTIONS:
            continue
        found = _forbidden_process_names_in(path)
        if found:
            violations[path.name] = found
    return violations


class NoSubprocessScanTests(unittest.TestCase):

    def test_exception_list_has_exactly_one_entry(self) -> None:
        self.assertEqual(len(SUBPROCESS_EXCEPTIONS), 1)
        self.assertEqual(SUBPROCESS_EXCEPTIONS, ("paper_latex.py",))

    def test_no_shipped_script_imports_a_forbidden_process_primitive(self) -> None:
        self.assertEqual(scan_forbidden_process_imports(SKILL_SCRIPTS), {})

    def test_a_planted_subprocess_import_is_caught(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            (tmp_dir / "evil.py").write_text("import subprocess\n", encoding="utf-8")
            violations = scan_forbidden_process_imports(tmp_dir)
        self.assertIn("evil.py", violations)
        self.assertIn("subprocess", violations["evil.py"])

    def test_the_exception_named_file_is_tolerated_when_present(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_dir = Path(tmp)
            (tmp_dir / "paper_latex.py").write_text("import subprocess\n", encoding="utf-8")
            violations = scan_forbidden_process_imports(tmp_dir)
        self.assertEqual(violations, {})


class ModuleCompletenessTests(unittest.TestCase):
    """tasks.md 1.12 -- the highest-value task in this change: `{stems of
    scripts/*.py}` must equal `paper_cli.py`'s own module-level import set,
    so a module nobody imports cannot ship unclassified. RED was proven by
    hand during implementation: a sixth, unimported module planted under
    `scripts/` made this equality fail; removed once proven, since a
    permanent planted file would corrupt this skill's own roster for every
    other suite that scans `scripts/*.py`."""

    def test_every_script_on_disk_is_imported_at_module_level_by_paper_cli(self) -> None:
        on_disk = {path.stem for path in SKILL_SCRIPTS.glob("*.py")}
        imported = {module.stem for module in paper_cli_imported_modules()} | {"paper_cli"}
        self.assertEqual(on_disk, imported)


class ZZLiveAgentGuardTests(unittest.TestCase):
    """`writing-orchestration` spec, `Requirement: No Live Agent Invocation
    In Tests`. Named `ZZ...` so it sorts alphabetically last among this
    module's own test classes (`unittest.TestLoader` iterates `dir(module)`,
    which is sorted) -- every subprocess-launching test class defined above
    (`ScaffoldTests`, `CLIWiringTests`, `MutationProofTests`,
    `WriterMutationProofTests`) has therefore already run by the time this
    assertion executes. The monitor itself (top of this file) is installed
    at import time, so it also covers any subprocess launched by another
    test module collected alongside this one under `python -m unittest
    discover`, for as long as this module stays imported."""

    def test_no_agent_binary_launched_by_any_subprocess_this_run_has_made_so_far(self) -> None:
        self.assertEqual(_live_agent_launches, [])


# =====================================================================
# the-writer-may-assert-only-what-it-was-given -- Work Unit 2
# =====================================================================


class StyleChannelTests(unittest.TestCase):
    """`style-channel` spec."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.guidance_dir = Path(self._tmp.name) / "guidance"

    def _make_reference(self, name: str) -> Path:
        folder = self.guidance_dir / name
        folder.mkdir(parents=True)
        (folder / ".paper-writing.json").write_text(
            json.dumps({"class": "style-reference"}), encoding="utf-8"
        )
        return folder

    def test_a_style_reference_resolves_its_equivalent_block(self) -> None:
        folder = self._make_reference("paperA")
        md = folder / "paperA.md"
        md.write_text("Intro text. The equivalent block reads exactly like this, whole.\n", encoding="utf-8")
        proposals = [{
            "reference": "paperA", "source_md": str(md),
            "span": "The equivalent block reads exactly like this, whole.",
        }]
        recorded, no_equivalent = paper_style.resolve_style_set(self.guidance_dir, proposals)
        self.assertEqual(no_equivalent, [])
        self.assertEqual(len(recorded), 1)
        self.assertEqual(recorded[0]["reference"], "paperA")

    def test_a_resolved_block_is_passed_intact_never_truncated(self) -> None:
        folder = self._make_reference("paperA")
        whole = "Sentence one. Sentence two. Sentence three."
        md = folder / "paperA.md"
        md.write_text(whole, encoding="utf-8")
        proposals = [{"reference": "paperA", "source_md": str(md), "span": whole}]
        recorded, _no_equivalent = paper_style.resolve_style_set(self.guidance_dir, proposals)
        self.assertEqual(recorded[0]["span"], whole)

    def test_r_contains_exactly_the_shown_samples(self) -> None:
        folder_a = self._make_reference("paperA")
        folder_b = self._make_reference("paperB")
        md_a = folder_a / "paperA.md"
        md_a.write_text("Block A body.", encoding="utf-8")
        md_b = folder_b / "paperB.md"
        md_b.write_text("Block B body.", encoding="utf-8")
        proposals = [
            {"reference": "paperA", "source_md": str(md_a), "span": "Block A body."},
            {"reference": "paperB", "source_md": str(md_b), "span": "Block B body."},
        ]
        recorded, no_equivalent = paper_style.resolve_style_set(self.guidance_dir, proposals)
        self.assertEqual(no_equivalent, [])
        self.assertEqual({entry["reference"] for entry in recorded}, {"paperA", "paperB"})
        self.assertEqual({entry["span"] for entry in recorded}, {"Block A body.", "Block B body."})

    def test_a_proposed_span_not_byte_present_refuses_span_not_in_source(self) -> None:
        folder = self._make_reference("paperA")
        md = folder / "paperA.md"
        md.write_text("Real content only.", encoding="utf-8")
        proposals = [{"reference": "paperA", "source_md": str(md), "span": "Fabricated content."}]
        with self.assertRaises(Refused) as ctx:
            paper_style.resolve_style_set(self.guidance_dir, proposals)
        self.assertEqual(ctx.exception.code, "SPAN_NOT_IN_SOURCE")

    def test_no_equivalent_degrades_to_the_empty_style_set(self) -> None:
        self._make_reference("paperA")
        recorded, no_equivalent = paper_style.resolve_style_set(
            self.guidance_dir, [{"reference": "paperA", "noEquivalent": True}],
        )
        self.assertEqual(recorded, [])
        self.assertEqual(no_equivalent, ["paperA"])

    def test_zero_style_references_is_the_empty_style_set(self) -> None:
        recorded, no_equivalent = paper_style.resolve_style_set(self.guidance_dir, [])
        self.assertEqual(recorded, [])
        self.assertEqual(no_equivalent, [])


class StyleLeakDetectionTests(unittest.TestCase):
    """`style-leak-detection` spec. This is the second of the two decisive
    proofs for this change: write one block three times -- two unstyled,
    one styled -- and check both inequalities for real."""

    def test_register_distance_rises_with_style_reported_with_its_control(self) -> None:
        unstyled_a = "The system computes the objective. It reports the result plainly."
        unstyled_b = "The method evaluates the loss. It states the outcome directly."
        styled = (
            "Verily, the apparatus doth compute yon objective most curiously! Behold, it "
            "proclaimeth the result unto thee, exceedingly and most plainly indeed, forsooth!"
        )
        result = paper_leak.register_distance_holds(styled, unstyled_a, unstyled_b)
        self.assertIn("d_S_AB", result)
        self.assertIn("d_AB", result)
        self.assertGreater(result["d_S_AB"], result["d_AB"])
        self.assertTrue(result["pass"], result)

    def test_dropping_the_ab_control_fails_construction(self) -> None:
        with self.assertRaises(TypeError):
            paper_leak.register_distance_holds("styled text", "unstyled a text")

    def test_overlap_stays_at_the_chance_floor_passes(self) -> None:
        samples = [{"reference": "paperA", "span": "the quick brown fox jumps over the lazy dog today"}]
        unstyled_a = "an unrelated sentence about something else entirely today"
        unstyled_b = "a different unrelated sentence about another topic today"
        styled = "yet another styled sentence sharing almost nothing with the sample"
        result = paper_leak.relative_overlap_holds(styled, unstyled_a, unstyled_b, samples)
        self.assertTrue(result["pass"], result)

    def test_styled_overlap_exceeding_both_baselines_fails(self) -> None:
        samples = [{"reference": "paperA", "span": "the quick brown fox jumps over the lazy dog today"}]
        unstyled_a = "completely unrelated text about nothing shared here at all"
        unstyled_b = "another unrelated sentence sharing nothing with the sample text"
        styled = "the quick brown fox jumps over the lazy dog today, verbatim and whole"
        result = paper_leak.relative_overlap_holds(styled, unstyled_a, unstyled_b, samples)
        self.assertFalse(result["pass"], result)
        self.assertGreater(result["overlap_S"], max(result["overlap_A"], result["overlap_B"]))

    def test_relative_overlap_holds_signature_carries_no_threshold(self) -> None:
        sig = inspect.signature(paper_leak.relative_overlap_holds)
        self.assertEqual(list(sig.parameters), ["styled", "unstyled_a", "unstyled_b", "samples"])
        for name in sig.parameters:
            self.assertNotIn("threshold", name.lower())
            self.assertNotIn("min_token", name.lower())

    def test_a_near_verbatim_lifted_sentence_refuses_style_overlap(self) -> None:
        samples = [{"reference": "paperA", "span": "one two three four five six seven eight nine"}]
        styled = "prefix text one two three four five six seven eight nine suffix text"
        with self.assertRaises(Refused) as ctx:
            paper_leak.check_tripwire(styled, samples)
        self.assertEqual(ctx.exception.code, "STYLE_OVERLAP")
        self.assertIn("paperA", ctx.exception.detail)

    def test_shared_math_notation_does_not_trip_the_tripwire(self) -> None:
        shared_math = r"\(\alpha \beta \gamma \delta \epsilon \zeta \eta \theta \iota\)"
        samples = [{"reference": "paperA", "span": f"Some prose. {shared_math} More prose."}]
        styled = f"Different prose entirely. {shared_math} Also different."
        hits = paper_leak.tripwire_spans(styled, samples)
        self.assertEqual(hits, [])

    def test_overlap_ignores_text_in_the_reference_file_outside_r(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ref_file = Path(tmp) / "reference.md"
            ref_file.write_text(
                "Recorded content only here today. UNRECORDED SECRET one two three four "
                "five six seven eight",
                encoding="utf-8",
            )
            samples = [{
                "reference": "paperA", "source_md": str(ref_file),
                "span": "Recorded content only here today.",
            }]
            styled = "UNRECORDED SECRET one two three four five six seven eight"
            self.assertEqual(paper_leak.overlap_against_set(styled, samples), 0)
            self.assertEqual(paper_leak.tripwire_spans(styled, samples), [])


class WriterMutationProofTests(unittest.TestCase):
    """`tasks.md` 1.11/2.3/2.5 -- the seven mutations named in the
    proposal, executed for real against the five new modules, mirroring
    `MutationProofTests` above."""

    def _assert_guard_failed_under_mutation(self, proc: subprocess.CompletedProcess) -> None:
        output = proc.stdout + proc.stderr
        self.assertIn("MUTANT_IMPORTED_OK", output, output)
        self.assertNotEqual(proc.returncode, 0, output)

    def test_mutation_1_dropped_reconciliation_fails_the_unbound_sentence_guard(self) -> None:
        proc = _run_against_mutant(
            "if sentence not in by_sentence:",
            "if False:",
            "tests.test_paper_writing.BindingMapTests.test_an_unbound_sentence_refuses",
            source_path=SKILL_SCRIPTS / "paper_bindings.py",
        )
        self._assert_guard_failed_under_mutation(proc)

    def test_mutation_2_never_firing_fails_the_one_firing_bullet_blocks_guard(self) -> None:
        proc = _run_against_mutant(
            'fired = [entry for entry in reconciled if entry["verdict"] == "fires"]',
            "fired = []",
            "tests.test_paper_writing.ContractAuditTests"
            ".test_one_firing_bullet_blocks_regardless_of_undecidables",
            source_path=SKILL_SCRIPTS / "paper_audit.py",
        )
        self._assert_guard_failed_under_mutation(proc)

    def test_mutation_3_substituting_on_exhausted_audit_fails_the_exhaustion_guard(self) -> None:
        proc = _run_against_mutant(
            "if attempt >= 2:",
            "if attempt >= 99:",
            "tests.test_paper_writing.WritingPipelineTests"
            ".test_two_failing_audits_leave_main_tex_unchanged_and_refuse_audit_exhausted",
            source_path=SKILL_SCRIPTS / "paper_write.py",
        )
        self._assert_guard_failed_under_mutation(proc)

    def test_mutation_4_a_hardcoded_bullet_fails_the_verbatim_extraction_guard(self) -> None:
        proc = _run_against_mutant(
            "    return bullets",
            '    bullets.append("HARDCODED BULLET THAT WAS NEVER IN THE CONTRACT")\n    return bullets',
            "tests.test_paper_writing.ContractAuditTests.test_bullet_text_reaches_the_audit_unchanged",
            source_path=SKILL_SCRIPTS / "paper_audit.py",
        )
        self._assert_guard_failed_under_mutation(proc)

    def test_mutation_5_absent_heading_as_zero_disqualifiers_fails_the_guard(self) -> None:
        proc = _run_against_mutant(
            "        raise Refused(\n"
            '            "DISQUALIFIERS_ABSENT", f"{source_name}: no \'## Disqualifiers\' heading"\n'
            "        )",
            "        return []",
            "tests.test_paper_writing.ContractAuditTests.test_a_contract_missing_the_heading_refuses",
            source_path=SKILL_SCRIPTS / "paper_audit.py",
        )
        self._assert_guard_failed_under_mutation(proc)

    def test_mutation_6_optional_ab_control_fails_the_typeerror_guard(self) -> None:
        proc = _run_against_mutant(
            "def register_distance_holds(styled: str, unstyled_a: str, unstyled_b: str) -> dict:",
            'def register_distance_holds(styled: str, unstyled_a: str, unstyled_b: str = "") -> dict:',
            "tests.test_paper_writing.StyleLeakDetectionTests.test_dropping_the_ab_control_fails_construction",
            source_path=SKILL_SCRIPTS / "paper_leak.py",
        )
        self._assert_guard_failed_under_mutation(proc)

    def test_mutation_7_reading_the_reference_file_fails_the_recorded_set_guard(self) -> None:
        proc = _run_against_mutant(
            'return max(_longest_run(tokens, paper_style.normalize_tokens(sample["span"])) '
            "for sample in samples)",
            "return max(_longest_run(tokens, paper_style.normalize_tokens("
            'Path(sample["source_md"]).read_text(encoding="utf-8"))) for sample in samples)',
            "tests.test_paper_writing.StyleLeakDetectionTests"
            ".test_overlap_ignores_text_in_the_reference_file_outside_r",
            source_path=SKILL_SCRIPTS / "paper_leak.py",
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
    roster, scoped here to `paper_cli.py` and whatever it imports
    (`paper_cli_imported_modules()`)."""
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


def paper_cli_imported_modules() -> list[Path]:
    """Every module `paper_cli.py` imports at module level via a plain
    `import X` (never `from X import Y`, which is how it reaches
    `impl_refusals.Refused` and contributes no roster entry of its own by
    design), resolved to a `.py` file inside this skill's own scripts
    directory.

    Derived from `paper_cli.py`'s own imports rather than a hand-listed
    tuple or a directory scan. A hand-listed tuple goes stale silently the
    moment a new script is added and wired in -- measured: this skill's own
    `paper_contract.py` and `paper_graph.py` were added and every refusal in
    them went unrostered with no test going red, because nothing re-derived
    the tuple. A directory scan is the OTHER wrong shape: it would claim a
    sibling change's own modules the moment they land beside these, which is
    exactly the whole-directory-scan pattern `.claude/skills/_core/` is
    forbidden from reproducing (measured elsewhere in this repository, where
    a different skill's roster derivation does scan a whole directory and is
    the reason nothing of this skill's may live under `_core/`). Importing
    is the correct reachability boundary either way: a module the front door
    never imports raises nothing a user can reach through it.
    """
    tree = ast.parse(CLI.read_text(encoding="utf-8"))
    modules = []
    for node in tree.body:
        if not isinstance(node, ast.Import):
            continue
        for alias in node.names:
            candidate = SKILL_SCRIPTS / f"{alias.name}.py"
            if candidate.is_file():
                modules.append(candidate)
    return modules


def unreadable_paper_refusal_sites() -> set[tuple[str, str]]:
    sites = set()
    for source in (CLI, *paper_cli_imported_modules()):
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
    `paper_cli.py` itself), UNIONED with a whole-module scan of every module
    `paper_cli.py` itself imports (`paper_cli_imported_modules()` above) —
    this skill's own helper modules, playing the role
    `_core/implementation/*.py` plays for the sibling skill, and widening by
    itself the moment a verb is actually wired rather than needing a second,
    hand-maintained tuple kept in sync with the first. `impl_refusals.py`
    contributes nothing: it raises no `Refused` of its own (design.md's `Own
    modules; import only Refused` decision) — the whole point of that choice
    being that this skill's roster and the sibling skill's roster never
    share an entry neither owns.
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
    for source in paper_cli_imported_modules():
        module = ast.parse(source.read_text(encoding="utf-8"))
        codes |= _codes_from_sites(_refusal_sites(module, "<module>"),
                                    _module_code_constants(module))
    return codes


class RefusalRosterTests(unittest.TestCase):
    """Every refusal reachable from a `paper_cli.py` command is classified,
    and nothing is classified that no command can reach — the lock
    `GatingRefusalRosterTests` holds `implementation_cli.py` to, derived
    rather than hand-listed so a new `Refused` anywhere in `paper_cli.py` or
    any module it imports goes red here until somebody classifies it."""

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
        """No refusal in `paper_cli.py` or any module it imports raises a
        code this walk cannot read as a string literal — asserted rather
        than assumed, so a future dynamic code site is looked at by a human
        instead of silently widening to a module's constants."""
        self.assertEqual(unreadable_paper_refusal_sites(), set())

    def test_the_derivation_finds_the_measured_count(self) -> None:
        """Sanity check on the derivation itself: a change that adds,
        removes or renames a refusal anywhere reachable should move this
        number, never a typo in the walk above. Moved from 21 to 30 when
        `the-contract-is-data-not-code` appended `contract`/`readiness`/
        `order` and `paper_cli.py` started importing `paper_vocabulary.py`,
        `paper_contract.py` and `paper_graph.py` — 3 (`UNKNOWN_FACT`,
        `UNKNOWN_DECLARATION`, `UNKNOWN_CITATIONS_REGIME`) + 4
        (`MALFORMED_HEADER`, `HEADER_PRESENT`, `BODY_MUTATED`,
        `SECTIONS_OUTSIDE_REPOSITORY`) + 2 (`ID_COLLISION`, `ORDER_CYCLE`).
        Moved from 30 to 36 in Slice A of `the-paper-carries-its-own-decisions`,
        which imports `paper_region.py` (`REGION_MALFORMED`,
        `REGION_DUPLICATED`, `REGION_UNPAIRED`) and `paper_guidance.py`
        (`GUIDANCE_OUTSIDE_REPOSITORY`, `UNKNOWN_GUIDANCE_CLASS`,
        `MALFORMED_GUIDANCE_MARKER`) at module level ahead of either
        module's own verb wiring (tasks.md, 1.10) — six new codes, reachable
        and classified the moment the import lands. Moved from 36 to 41 in
        Slice B, which wires `declare`: `DECLARATION_FIXED` and
        `DECLARATIONS_HAND_EDITED` from `paper_declarations.py`, plus
        `DECLARE_MODE_REQUIRED`, `DECLARE_MODE_CONFLICT`,
        `DECLARE_VALUE_REQUIRED` from `cmd_declare`'s own mode selection in
        this file — `UNKNOWN_DECLARATION`/`UNKNOWN_FACT` are reused
        verbatim from Phase 2 and add nothing new to the set. Moved from 41
        to 43 in Slice C1, which adds `CONTRACT_UNREADABLE` (raised
        directly inside `paper_block.substitute`, already-imported) and
        `PROVENANCE_HAND_EDITED` (from the newly-imported
        `paper_provenance.py`). Moved from 43 to 45 in Slice C2, which adds
        `NOT_AN_OBSERVABLE_FACT` and `EVIDENCE_CONFLATED` from
        `paper_declarations.validate_observation_report` -- reachable
        through the whole-module scan even though no `cmd_*` root calls it
        directly, the same shape that already applies to every other
        module-level refusal here. `plan`'s own wiring adds no new code:
        every refusal `compute_plan`/`cmd_plan` can raise was already
        classified by an earlier slice. `paper_objective.py` raises none of
        its own, matching `paper_readiness.py`'s own precedent. Moved from
        45 to 54 in WU1 of `no-claim-without-a-source-that-holds-it`, which
        adds `UNKNOWN_VERDICT` (`paper_vocabulary.py`, already-imported
        module) and wires `resolve` -- `paper_cli.py` starts importing
        `paper_evidence.py` (`SPAN_NOT_IN_SOURCE`, `VERDICT_SPAN_REQUIRED`)
        and `paper_resolve.py` (`PAPERSMITH_CONFIG_UNREADABLE`,
        `UNKNOWN_ROLE`, `DISCOVERY_UNAVAILABLE`, `RESOLVER_ROLE_EMPTY`,
        `RESOLVER_UNREACHABLE`, `IDENTIFIER_UNRESOLVED`) -- 1 + 2 + 6 = 9
        new codes. Moved from 54 to 57 in WU2, which wires `bib build`:
        `paper_bib.py` adds `ENTRY_UNSOURCED`, `CITE_WITHOUT_ENTRY`,
        `ENTRY_WITHOUT_CITE`. Moved from 57 to 65 in WU3, which wires
        `validate`: `paper_validate.py` adds `EVIDENCE_EXHAUSTED`,
        `CITATION_MULTI_CLAIM_SENTENCE`, `CITATION_NOUN_PHRASE`,
        `CITATION_NOT_AT_SENTENCE_END`, `CITATION_DETACHED_FROM_OBJECT`,
        `CITATION_UNDER_NONE_REGIME`, `CONTRACT_HEADER_ABSENT`, plus
        `cmd_validate`'s own `VALIDATE_VERDICT_REQUIRED` in this file -- 7 + 1
        = 8 new codes. Moved from 65 to 79 in `the-writer-may-assert-only-
        what-it-was-given`: `paper_contract.py`'s `mode` widening adds
        `UNKNOWN_MODE` (1); WU1 wires `write` and starts importing
        `paper_bindings.py` (`UNBOUND_SENTENCE`, `BINDING_ORPHANED`,
        `EVIDENCE_ID_UNKNOWN`, `FACT_NOT_LICENSED`,
        `STRUCTURAL_CARRIES_CLAIM`, `MODE_VIOLATION` -- 6),
        `paper_audit.py` (`DISQUALIFIERS_ABSENT`, `VERDICT_MISSING`,
        `VERDICT_BULLET_UNKNOWN` -- 3) and `paper_write.py`
        (`MODE_ABSENT`, `EVIDENCE_SET_REQUIRED`, `AUDIT_EXHAUSTED` -- 3);
        WU2 starts importing `paper_leak.py` (`STYLE_OVERLAP` -- 1) and
        `paper_style.py` (raises none of its own, reusing
        `SPAN_NOT_IN_SOURCE`) -- 1 + 6 + 3 + 3 + 1 = 14 new codes."""
        self.assertEqual(len(reachable_paper_refusal_codes()), 79)


if __name__ == "__main__":
    unittest.main()
