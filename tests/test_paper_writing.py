"""paper-writing: scaffold, block grammar, substitution engine.

Stdlib-only `unittest`. Every fixture lives under a `TemporaryDirectory`; the
real `paper/` at the forge root is never touched by this suite outside the
one CLI subprocess test, which scaffolds under the already-gitignored
`implementations/` tree and cleans up after itself. Every
`paper_scaffold.resolve_paper_dir` call below passes an injected
`forge_root` for exactly this reason.
"""
from __future__ import annotations

import argparse
import ast
import dataclasses
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
import paper_coupling_evidence  # noqa: E402
import paper_verify  # noqa: E402
import paper_objective  # noqa: E402
import paper_graph  # noqa: E402
import paper_readiness  # noqa: E402

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

    def test_observe_validates_an_insumos_observer_report_and_writes_nothing(self) -> None:
        """`observe` wires `paper_declarations.validate_observation_report`
        to a real CLI caller -- the same shuttle shape `write --draft
        <path>` already establishes for the redactor's account."""
        self._scaffold()
        report_path = self.paper_dir.parent / "observation_report.json"
        report_path.write_text(json.dumps({
            "formulation": {"satisfied": True, "evidence": [["proposals/x.md", "the model is..."]]},
            "implementation": {"satisfied": True, "evidence": [["repo/code.py", "q1"]]},
            "results": {"satisfied": True, "evidence": [["repo/results.json", "q2"]]},
        }), encoding="utf-8")
        before = report_path.read_bytes()

        proc = self._run("observe", "--report", str(report_path))

        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["validated"])
        self.assertEqual(payload["satisfied"], ["formulation", "implementation", "results"])
        self.assertEqual(report_path.read_bytes(), before)

    def test_observe_refuses_an_id_outside_the_observable_facts(self) -> None:
        self._scaffold()
        report_path = self.paper_dir.parent / "observation_report.json"
        report_path.write_text(json.dumps({
            "contributions": {"satisfied": True, "evidence": [["x", "y"]]},
        }), encoding="utf-8")

        proc = self._run("observe", "--report", str(report_path))

        self.assertEqual(proc.returncode, 2, proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["code"], "NOT_AN_OBSERVABLE_FACT")

    def test_observe_refuses_conflated_implementation_and_results_evidence(self) -> None:
        self._scaffold()
        report_path = self.paper_dir.parent / "observation_report.json"
        report_path.write_text(json.dumps({
            "implementation": {"satisfied": True, "evidence": [["repo/code.py", "q1"]]},
            "results": {"satisfied": True, "evidence": [["repo/code.py", "q2"]]},
        }), encoding="utf-8")

        proc = self._run("observe", "--report", str(report_path))

        self.assertEqual(proc.returncode, 2, proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["code"], "EVIDENCE_CONFLATED")


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

    #: `Headers Written Before mode Existed`: an absent `mode` at both
    #: levels is schema-valid, never a violation -- `write`'s own
    #: readiness stage is what refuses on it
    #: (`WritingPipelineTests.test_no_mode_resolved_refuses_mode_absent`),
    #: never this reader. All ten shipped contracts now carry a quotable
    #: mode-bearing sentence: `02-experimental-setup.md`,
    #: `04-limitations.md` and `05-related-work.md` initially shipped with
    #: none declared, and a later corrective batch authored the missing
    #: sentence for each. The synthetic, no-real-file-required case (neither
    #: level declaring `mode` still parses and resolves to `None`) is
    #: covered above by `test_neither_level_declaring_mode_resolves_to_none`
    #: and, for the corpus-walk's own None-skipping branch, by
    #: `test_paper_contract.ModeTranscriptionTests.
    #: test_undeclared_sections_are_absent_not_silently_passing`.

    def test_shipped_contracts_declaring_mode_resolve_it_at_every_block(self) -> None:
        for path in sorted(SECTIONS_DIR.glob("*.md")):
            header, _body = paper_contract.parse(path.read_bytes())
            self.assertIsNotNone(header.mode, path.name)
            self.assertIn(header.mode["value"], paper_vocabulary.MODES, path.name)
            self.assertEqual(header.mode["source"]["file"], f"sections/{path.name}")
            for block in header.blocks:
                resolved = paper_contract.resolve_mode(header, block)
                self.assertIsNotNone(resolved, (path.name, block["id"]))


class ContractHeaderTests(unittest.TestCase):
    """`a-diagram-that-compiles-or-says-why`, `section-contract` spec
    delta: `figure` joins `_BLOCK_OPTIONAL`, five subkeys required and
    `components_from` optional (tasks.md 3.1/3.2/3.6; `components_from`
    widened to optional by this change's own corrective amendment —
    verify FAIL, CRITICAL finding on `es-assessment`)."""

    _FIGURE = {
        "components_from": "contributions", "ordered": True,
        "excludes": ["dataset", "baseline"], "caption_enumerates": True,
        "caption_decodes": True, "mandatory": True,
    }

    def _header(self, figure=None) -> dict:
        block = {
            "id": "b1", "requires_facts": ["contributions"], "requires_declarations": [],
            "citations": "none",
        }
        if figure is not None:
            block["figure"] = figure
        return {"section": "demo", "position": 1, "blocks": [block]}

    def test_a_valid_figure_object_parses(self) -> None:
        header = paper_contract.parse_header(self._header(figure=self._FIGURE))
        self.assertEqual(header.blocks[0]["figure"], self._FIGURE)

    def test_no_figure_key_resolves_to_none(self) -> None:
        header = paper_contract.parse_header(self._header())
        self.assertIsNone(header.blocks[0]["figure"])

    def test_a_figure_object_missing_a_subkey_refuses_malformed_figure_obligation(self) -> None:
        broken = {k: v for k, v in self._FIGURE.items() if k != "caption_decodes"}
        with self.assertRaises(Refused) as ctx:
            paper_contract.parse_header(self._header(figure=broken))
        self.assertEqual(ctx.exception.code, "MALFORMED_FIGURE_OBLIGATION")
        self.assertIn("caption_decodes", ctx.exception.detail)

    def test_a_figure_object_with_an_unknown_key_refuses_malformed_figure_obligation(self) -> None:
        broken = dict(self._FIGURE, extra_key="nope")
        with self.assertRaises(Refused) as ctx:
            paper_contract.parse_header(self._header(figure=broken))
        self.assertEqual(ctx.exception.code, "MALFORMED_FIGURE_OBLIGATION")

    def test_an_unknown_components_from_fact_refuses_unknown_fact(self) -> None:
        broken = dict(self._FIGURE, components_from="not-a-real-fact")
        with self.assertRaises(Refused) as ctx:
            paper_contract.parse_header(self._header(figure=broken))
        self.assertEqual(ctx.exception.code, "UNKNOWN_FACT")

    def test_a_non_boolean_ordered_refuses_malformed_figure_obligation(self) -> None:
        broken = dict(self._FIGURE, ordered="yes")
        with self.assertRaises(Refused) as ctx:
            paper_contract.parse_header(self._header(figure=broken))
        self.assertEqual(ctx.exception.code, "MALFORMED_FIGURE_OBLIGATION")

    def test_a_non_string_excludes_entry_refuses_malformed_figure_obligation(self) -> None:
        broken = dict(self._FIGURE, excludes=[1, 2])
        with self.assertRaises(Refused) as ctx:
            paper_contract.parse_header(self._header(figure=broken))
        self.assertEqual(ctx.exception.code, "MALFORMED_FIGURE_OBLIGATION")

    def test_a_figure_object_without_components_from_parses(self) -> None:
        """Corrective amendment: `components_from` is optional — a block
        whose diagram is a composite crossing over several categories of
        content, none of which alone is the full expected list (section
        02's closing diagram), declares no `components_from` at all rather
        than being wired to one fact's partial value."""
        without_components_from = {k: v for k, v in self._FIGURE.items() if k != "components_from"}
        header = paper_contract.parse_header(self._header(figure=without_components_from))
        self.assertIsNone(header.blocks[0]["figure"]["components_from"])

    def test_an_explicit_null_components_from_also_resolves_to_none(self) -> None:
        """Same `raw.get(...) is not None` round-trip convention `mode`
        already uses: this parser's own output re-serializes with an
        explicit `"components_from": null`, and re-parsing that MUST mean
        the same thing as the key being absent."""
        with_null = dict(self._FIGURE, components_from=None)
        header = paper_contract.parse_header(self._header(figure=with_null))
        self.assertIsNone(header.blocks[0]["figure"]["components_from"])


def _derive_figure_holders(sections_dir: Path = SECTIONS_DIR) -> list:
    """`[(filename, block_id), ...]` for EVERY block in `sections_dir` that
    declares a `figure:` obligation -- DERIVED by parsing every real
    `sections/*.md` file's own header, never a fixed list of ids typed by
    hand.

    W3 (`a-diagram-that-compiles-or-says-why`'s corrective re-verify,
    WARNING): this class used to hard-code a `_HOLDERS = {...}` dict of
    exactly three known ids. A hand-typed list like that is complete by
    coincidence, not by construction -- it can never notice a NEW
    figure-declaring block added later, because nothing forces whoever adds
    one to also remember to update a dict elsewhere in a different file.
    Module-level (not a class attribute) so a mutated COPY of the corpus
    can also be scanned from `tests/test_paper_figure.py`'s own mutation
    proof, without needing to instantiate this TestCase.

    W3's OWN re-verify (latent WARNING, cousin of the same finding class):
    the first version of this derivation replaced the hand-typed dict with
    a FRESH `dict[str, str]` keyed by `path.name`, assigned INSIDE the loop
    over that file's own blocks -- `holders[path.name] = block["id"]`. A
    second figure-declaring block in the same file silently overwrote the
    first, reopening the exact collapse this function exists to close.
    Nothing in the real corpus exercised it (each of the three real
    figure-declaring contracts holds exactly one such block), so it was
    unreachable, not absent. A list of `(filename, block_id)` pairs cannot
    collapse the same way -- proven by
    `FigureHolderDerivationDoesNotCollapseTests`, which builds a synthetic
    contract with two figure-declaring blocks in one file and confirms both
    survive."""
    holders: list = []
    for path in sorted(sections_dir.glob("*.md")):
        header, _body = paper_contract.parse(path.read_bytes())
        for block in header.blocks:
            if block["figure"] is not None:
                holders.append((path.name, block["id"]))
    return holders


def _assert_proof_classified_blocks_carry_their_derivation(
    sections_dir: Path, holders: list, realism_proof: dict,
) -> None:
    """For every derived `(filename, block_id)` classified `"proof:..."` in
    `realism_proof`, the REAL, on-disk header at `sections_dir` MUST
    currently declare a non-null `figure.components_from` for that block --
    read fresh from disk every call, never assumed from yesterday's shape.

    W3: a `"proof:..."` entry asserts a named test proves this block's
    Components Check is load-bearing; that claim is only true while the
    contract still names a fact for it. `components_from` moved from
    required to optional to close the original CRITICAL (a check silently
    wired to nothing); the cheapest way to reopen the identical hole is for
    a future edit to drop the field from a `"proof:..."`-classified block
    without also reclassifying its entry to `"exempt:<reason>"`. Raises
    `AssertionError` (not a `self.assert*` call) so this same function is
    callable, and its failure observable, from OUTSIDE a `TestCase` --
    `tests/test_paper_figure.py`'s own mutation proof calls this directly
    against a mutated copy and asserts it raises."""
    for filename, block_id in holders:
        entry = realism_proof.get(block_id)
        if entry is None or not entry.startswith("proof:"):
            continue
        header, _body = paper_contract.parse((sections_dir / filename).read_bytes())
        block = next(b for b in header.blocks if b["id"] == block_id)
        figure = block["figure"]
        if figure is None or figure["components_from"] is None:
            raise AssertionError(
                f"{filename}: {block_id} is classified {entry!r} (a load-bearing Components "
                "Check proof), but its real figure.components_from is now None -- either "
                "restore the field or reclassify this entry to 'exempt:<reason>'"
            )


class FigureHolderDerivationDoesNotCollapseTests(unittest.TestCase):
    """`a-diagram-that-compiles-or-says-why`'s re-verify, WARNING (latent):
    `_derive_figure_holders` built its `dict[str, str]` return by assigning
    `holders[path.name] = block["id"]` INSIDE the loop over that file's own
    blocks -- exactly the shape it exists to close (a second figure-
    declaring block in the same contract silently overwrites the first, and
    that block then drops out of every anti-drift check reading this map).
    No real `sections/*.md` file currently holds two such blocks, so this
    was unreachable through the corpus; it is reachable through a
    synthetic contract that names it directly."""

    _FIGURE = {
        "ordered": False, "excludes": [], "caption_enumerates": False,
        "caption_decodes": False, "mandatory": False,
    }

    def _two_figure_block_header(self) -> dict:
        block = {
            "id": None, "requires_facts": [], "requires_declarations": [], "citations": "none",
            "figure": dict(self._FIGURE),
        }
        first = dict(block, id="fig-a")
        second = dict(block, id="fig-b")
        return {"section": "demo", "position": 1, "blocks": [first, second]}

    def test_two_figure_declaring_blocks_in_one_file_both_survive_derivation(self) -> None:
        header_dict = self._two_figure_block_header()
        # Round-trips through the real parser first, matching every other
        # fixture in this module -- a malformed synthetic header would prove
        # nothing about the real collapse.
        paper_contract.parse_header(header_dict)

        file_bytes = b"---\n" + json.dumps(header_dict).encode("utf-8") + b"\n---\nbody\n"
        with tempfile.TemporaryDirectory() as tmp:
            sections_dir = Path(tmp) / "sections"
            sections_dir.mkdir()
            (sections_dir / "two-figures.md").write_bytes(file_bytes)

            holders = _derive_figure_holders(sections_dir)

        holder_block_ids = [block_id for filename, block_id in holders if filename == "two-figures.md"]
        self.assertIn(
            "fig-a", holder_block_ids,
            "fig-a dropped out of the derivation -- the second block overwrote it",
        )
        self.assertIn(
            "fig-b", holder_block_ids,
            "fig-b dropped out of the derivation -- a same-filename collapse lost a block",
        )


class FigureObligationTranscriptionTests(unittest.TestCase):
    """design.md, `Open Questions`: "a test asserts each `excludes` entry and
    the `components_from` fact name occur in the holder contract's prose,
    whitespace-normalised." Scoped to the PROSE below the header fence, not
    the JSON header itself -- a components_from/excludes value that only
    ever appeared inside the machine-written header would prove nothing
    about a human having stated it (design.md's own narrower-than-the-
    sibling's scoping note)."""

    @staticmethod
    def _normalize(text: str) -> str:
        return " ".join(text.split())

    def test_every_excludes_entry_and_components_from_occur_in_the_holders_own_prose(self) -> None:
        for filename, block_id in _derive_figure_holders():
            path = SECTIONS_DIR / filename
            header, body = paper_contract.parse(path.read_bytes())
            block = next(b for b in header.blocks if b["id"] == block_id)
            figure = block["figure"]
            self.assertIsNotNone(figure, f"{filename}: {block_id} declares no figure")
            prose = self._normalize(body.decode("utf-8"))
            if figure["components_from"] is not None:
                self.assertIn(
                    self._normalize(figure["components_from"]), prose,
                    f"{filename}: components_from {figure['components_from']!r} not found in prose",
                )
            for excluded in figure["excludes"]:
                self.assertIn(
                    self._normalize(excluded), prose,
                    f"{filename}: excludes entry {excluded!r} not found in prose",
                )

    #: Fixing the CLASS, not just the instance (`a-diagram-that-compiles-
    #: or-says-why`, corrective verify FAIL): a transcription lock that
    #: only checks a word's presence in prose licenses any value that
    #: happens to share that word — measured directly: `components_from:
    #: "dataset"` passed the substring check above while inverting
    #: `paper_obligation.check_components` for `es-assessment` (a
    #: prose-compliant diagram refused, a degenerate one passed). Every
    #: block that declares `figure:` MUST ALSO be named here against either
    #: an EXECUTED realism proof living in `tests/test_paper_figure.py`
    #: (`"proof:<TestClass>.<test_method>"`, resolved against that file's
    #: own AST below so a stale reference fails loudly, not silently) or an
    #: explicit, human-readable exemption reason (`"exempt:<reason>"`) for
    #: a block whose obligation is conditional and never mechanically
    #: checked at all (section 05's table-or-diagram choice; and now
    #: `es-assessment`, whose composite crossing means it correctly
    #: declares no `components_from` at all — see the corrective fix
    #: below).
    _COMPONENTS_REALISM_PROOF = {
        "mm-proposal": "proof:ObligationTests.test_matching_ordered_components_pass",
        "es-assessment": (
            "exempt:components_from removed entirely (corrective fix, verify FAIL CRITICAL): "
            "the closing diagram is a composite crossing over six categories of content that no "
            "single fact's value can equal, so no Components Check is wired to it at all -- there "
            "is no longer a possible verdict to invert. See test_paper_figure.py, "
            "Section02ComponentsCheckOmittedTests and CLIWiringTests."
            "test_real_section_02_es_assessment_no_longer_inverts_the_components_check"
        ),
        "rw-synthesis-artefact": (
            "exempt:mandatory=false, and a table choice leaves no <id>.tex — no component check "
            "is ever reachable for this block (design.md, 'The 05 conditional, expressed in data "
            "rather than a new key'; ObligationTests."
            "test_a_table_choice_for_block_05_carries_no_diagram_obligation)"
        ),
    }

    def test_every_figure_declaring_block_names_a_realism_proof_or_an_exemption(self) -> None:
        figure_test_source = (FORGE_ROOT / "tests" / "test_paper_figure.py").read_text(encoding="utf-8")
        tree = ast.parse(figure_test_source)
        methods_by_class: dict[str, set] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods_by_class[node.name] = {
                    child.name for child in node.body if isinstance(child, ast.FunctionDef)
                }

        for filename, block_id in _derive_figure_holders():
            self.assertIn(
                block_id, self._COMPONENTS_REALISM_PROOF,
                f"{filename}: {block_id} declares figure: but names no realism proof or exemption",
            )
            entry = self._COMPONENTS_REALISM_PROOF[block_id]
            if entry.startswith("proof:"):
                class_name, _, method_name = entry[len("proof:"):].partition(".")
                self.assertIn(
                    class_name, methods_by_class,
                    f"{block_id}: proof names class {class_name!r}, absent from test_paper_figure.py",
                )
                self.assertIn(
                    method_name, methods_by_class[class_name],
                    f"{block_id}: proof names {class_name}.{method_name}, no such test method",
                )
            else:
                self.assertTrue(
                    entry.startswith("exempt:") and len(entry) > len("exempt:"),
                    f"{block_id}: exemption entry must state a non-empty reason: {entry!r}",
                )

    def test_every_proof_classified_block_currently_carries_the_derivation_it_claims(self) -> None:
        """W3 (`a-diagram-that-compiles-or-says-why`'s corrective re-verify,
        WARNING): `components_from` moved from required to optional to
        close the original CRITICAL. Optionality is itself the cheapest way
        to reopen the identical hole by silent omission -- nothing before
        this test locked the REAL, on-disk `mm-proposal` header to keep
        declaring `components_from`; a future edit could drop it and every
        existing test would stay green, because the one existing
        transcription-lock test
        (`test_every_figure_declaring_block_names_a_realism_proof_or_an_
        exemption`) only checks that a NAMED test method still exists in
        `test_paper_figure.py`, never that the real header still matches
        the classification. Proven load-bearing, not merely asserted, by
        `tests/test_paper_figure.py`'s own
        `ComponentsFromDerivationGuardTests` -- it calls the exact function
        this test calls, against a mutated copy of this real file, and
        confirms the guard raises."""
        holders = _derive_figure_holders(SECTIONS_DIR)
        try:
            _assert_proof_classified_blocks_carry_their_derivation(
                SECTIONS_DIR, holders, self._COMPONENTS_REALISM_PROOF,
            )
        except AssertionError as exc:
            self.fail(str(exc))


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

    def test_both_modes_admit_none_regime_evidence(self) -> None:
        # `none` (no external source at all) is strictly more restrictive
        # than `resolution`, so a mode admitting `resolution` must admit
        # `none` too -- a block declaring `citations: "none"` inherits that
        # same regime on its own evidence records.
        bindings = [paper_bindings.Binding(sentence="s", kind="evidence", ref="N1")]
        evidence_by_id = {"N1": {"id": "N1", "regime": "none"}}
        paper_bindings.check_mode_admissibility(bindings, "transposition", evidence_by_id)
        paper_bindings.check_mode_admissibility(bindings, "argument", evidence_by_id)


class CorpusModeCitationsAdmissibilityTests(unittest.TestCase):
    """Derived guard over the real `sections/*.md` corpus, not a
    hand-listed set of block ids or a golden count standing in for
    enforcement: an evidence record's `regime` is inherited from its own
    block's `citations` field (`paper_cli._resolve_regime` ->
    `paper_validate.read_citations_regime`, fallback `"none"`), so every
    block whose contract declares a `citations` regime its own resolved
    `mode` does not admit would produce evidence its own section refuses
    at `write` time. Both sides of the comparison -- which blocks exist,
    each one's resolved mode, each one's declared citations regime -- are
    derived by parsing the corpus itself in this same test, never asserted
    or hand-listed."""

    def _violations(self) -> list[tuple[str, str, str, str]]:
        violations: list[tuple[str, str, str, str]] = []
        for path in sorted(SECTIONS_DIR.glob("*.md")):
            header, _body = paper_contract.parse(path.read_bytes())
            for block in header.blocks:
                mode_obj = paper_contract.resolve_mode(header, block)
                if mode_obj is None:
                    # No mode resolves for this block -- out of scope for
                    # this guard; `write`'s own readiness stage refuses
                    # `MODE_ABSENT` for it, a separate concern.
                    continue
                mode = mode_obj["value"]
                citations = block["citations"]
                admitted = paper_bindings._MODE_ADMITTED_EVIDENCE_REGIMES[mode]
                if citations not in admitted:
                    violations.append((path.name, block["id"], mode, citations))
        return violations

    def test_every_block_own_resolved_mode_admits_its_own_citations_regime(self) -> None:
        violations = self._violations()
        self.assertEqual(
            violations, [],
            f"block(s) whose resolved mode refuses their own declared citations "
            f"regime (section file, block id, mode, citations): {violations}",
        )

    def test_m4_dropping_none_from_transposition_fails_the_corpus_guard(self) -> None:
        # Load-bearing proof, executed rather than asserted: revert
        # `transposition`'s admitted set to the shipped defect (`none`
        # removed) in a real subprocess against a real mutant module, and
        # confirm the corpus guard above genuinely goes red naming real
        # blocks -- not merely that some test somewhere would notice.
        proc = _run_against_mutant(
            '"transposition": frozenset({"none", "resolution"}),',
            '"transposition": frozenset({"resolution"}),',
            "tests.test_paper_writing.CorpusModeCitationsAdmissibilityTests"
            ".test_every_block_own_resolved_mode_admits_its_own_citations_regime",
            source_path=SKILL_SCRIPTS / "paper_bindings.py",
        )
        output = proc.stdout + proc.stderr
        self.assertIn("MUTANT_IMPORTED_OK", output, output)
        self.assertNotEqual(proc.returncode, 0, output)
        # The failure names real corpus blocks, not an empty or generic
        # message -- proving the guard fires on the actual violation shape.
        self.assertIn("08-abstract.md", output, output)
        self.assertIn("transposition", output, output)


#: Maps the number words `SKILL.md` prose is free to use for this count
#: (including the historical "none") to an integer, so the check below
#: reads *whatever the prose currently claims* rather than a hand-picked
#: expectation, and still catches the count going stale in either
#: direction.
_MODE_COUNT_WORDS = {
    "none": 0, "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10,
}

_SKILL_MD_MODE_COUNT_RE = re.compile(
    r"(\w+) of the (\w+) shipped contracts carry `mode`"
)


class SkillMdModeCountAccuracyTests(unittest.TestCase):
    """`M17`: `SKILL.md`'s `### \\`mode\\`: how a block is licensed to argue`
    section states how many of the shipped `sections/*.md` contracts
    already declare `mode`. That count is prose sitting beside data that
    can be read directly -- the defect class this guard exists for is the
    prose going stale while the corpus moves on, exactly as it did when
    coverage went from 0/10 to 10/10 across `d99ee93`/`9986e11` and the
    sentence was never revisited. Both sides are derived here: the corpus
    side by parsing every `sections/*.md` header for a section-level
    `mode`, the prose side by regexing the live `SKILL.md` text -- neither
    is hand-listed or hardcoded to today's value.
    """

    SKILL_MD = (
        FORGE_ROOT / ".claude" / "skills" / "paper-writing" / "SKILL.md"
    )

    def _real_corpus_count(self) -> tuple[int, int]:
        paths = sorted(SECTIONS_DIR.glob("*.md"))
        with_mode = 0
        for path in paths:
            header, _body = paper_contract.parse(path.read_bytes())
            if header.mode is not None:
                with_mode += 1
        return with_mode, len(paths)

    def _claimed_count(self) -> tuple[int, int]:
        text = self.SKILL_MD.read_text(encoding="utf-8")
        match = _SKILL_MD_MODE_COUNT_RE.search(text)
        self.assertIsNotNone(
            match,
            "SKILL.md no longer states a '<n> of the <n> shipped contracts "
            "carry `mode`' sentence -- update this test's regex to match "
            "wherever that claim now lives before trusting it again.",
        )
        claimed_raw, total_raw = match.group(1), match.group(2)
        for raw in (claimed_raw, total_raw):
            self.assertIn(
                raw.lower(), _MODE_COUNT_WORDS,
                f"unrecognized count word {raw!r} in SKILL.md's mode-count "
                f"sentence -- extend _MODE_COUNT_WORDS to read it.",
            )
        return _MODE_COUNT_WORDS[claimed_raw.lower()], _MODE_COUNT_WORDS[total_raw.lower()]

    def test_skill_md_mode_count_matches_the_real_corpus(self) -> None:
        real_with_mode, real_total = self._real_corpus_count()
        claimed_with_mode, claimed_total = self._claimed_count()
        self.assertEqual(
            (claimed_with_mode, claimed_total), (real_with_mode, real_total),
            f"SKILL.md claims {claimed_with_mode} of {claimed_total} shipped "
            f"contracts carry `mode`, but sections/*.md actually shows "
            f"{real_with_mode} of {real_total} -- the prose drifted from "
            f"the corpus it describes.",
        )


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
    requires_facts=(), evidence_set=(), style_set=(), disqualifiers=(_SAMPLE_DISQUALIFIER,),
) -> "paper_write.BlockContract":
    return paper_write.BlockContract(
        block_id=block_id,
        contract_prose=_contract_body(list(disqualifiers)),
        contract_source="demo.md",
        citations_regime=citations_regime,
        mode=mode,
        requires_facts=tuple(requires_facts),
        evidence_set=tuple(evidence_set),
        style_set=tuple(style_set),
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

    def test_a_styled_draft_lifting_the_sample_refuses_style_overlap(self) -> None:
        """`design.md`'s own Data Flow: `paper_leak.tripwire (styled only)
        -> paper_write ledger` runs inside the real pipeline, not only in a
        standalone proof harness -- `write_block` itself refuses when a
        styled draft shares eight or more normalized tokens with a
        recorded sample, and `main.tex` never changes."""
        sample = {
            "reference": "paperA",
            "span": "The quick brown fox jumps over the lazy dog again today.",
        }
        contract = _write_contract(citations_regime="none", evidence_set=(), style_set=(sample,))
        lifted_draft = {
            "latex": (
                "This closes the section. "
                "The quick brown fox jumps over the lazy dog again today."
            ),
            "bindings": [
                {"sentence": "This closes the section.", "binding": "structural"},
                {
                    "sentence": "The quick brown fox jumps over the lazy dog again today.",
                    "binding": "structural",
                },
            ],
        }
        pre = (self.paper_dir / "main.tex").read_bytes()

        with self.assertRaises(Refused) as ctx:
            paper_write.write_block(self.paper_dir, contract, lifted_draft, _CLEAN_AUDIT)

        self.assertEqual(ctx.exception.code, "STYLE_OVERLAP")
        self.assertIn("paperA", ctx.exception.detail)
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), pre)

    def test_a_styled_draft_with_no_lifted_run_still_writes(self) -> None:
        sample = {
            "reference": "paperA",
            "span": "one two three four five six seven eight nine ten",
        }
        contract = _write_contract(citations_regime="none", evidence_set=(), style_set=(sample,))
        result = paper_write.write_block(self.paper_dir, contract, _CLEAN_DRAFT, _CLEAN_AUDIT)
        self.assertEqual(result["status"], "written")

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

    def test_a_real_write_with_no_style_set_reports_the_style_channel_unmeasured(self) -> None:
        """Ruling 2's own guarantee ('never a silent pass') has no real
        caller unless a genuine `write_block` invocation surfaces it. This
        drives the pipeline end to end -- not `style_channel_report` in
        isolation -- with an empty `style_set`, the only value Work Unit 1
        alone ever produces, and asserts the returned envelope itself
        reports `unmeasured` rather than omitting the field entirely."""
        contract = _write_contract(citations_regime="none", evidence_set=(), style_set=())
        result = paper_write.write_block(self.paper_dir, contract, _CLEAN_DRAFT, _CLEAN_AUDIT)
        self.assertEqual(result["status"], "written")
        self.assertEqual(result["styleChannel"], {"status": "unmeasured"})

    def test_a_real_write_with_a_style_set_reports_the_style_channel_measured(self) -> None:
        sample = {
            "reference": "paperA",
            "span": "one two three four five six seven eight nine ten",
        }
        contract = _write_contract(citations_regime="none", evidence_set=(), style_set=(sample,))
        result = paper_write.write_block(self.paper_dir, contract, _CLEAN_DRAFT, _CLEAN_AUDIT)
        self.assertEqual(result["status"], "written")
        self.assertEqual(result["styleChannel"]["status"], "measured")


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


# =====================================================================
# the-couplings-hold-or-they-do-not
# =====================================================================

#: The three canonical, declared contribution names -- shared by every
#: fixture below so a single ordered comparison exercises coupling 1,
#: coupling 4's methods-diagram reuse, and the chain's own closure check
#: against the same document-bound set.
_COUPLING_CONTRIBUTIONS = ["Adaptive Caching", "Async Prefetch", "Bounded Retry"]

#: The section corpus this capability's own fixture installs -- five files,
#: eight blocks, covering the fact every check derives its block set from
#: (`contributions`, `problem-statement`, `gap`, `limitations`). No
#: `figure:` obligation anywhere: this fixture is deliberately independent
#: of `a-diagram-that-compiles-or-says-why`.
_COUPLING_SECTIONS = {
    "01-introduction.md": {
        "section": "introduction", "position": 1,
        "blocks": [
            {"id": "intro-contrib", "requires_facts": ["contributions"],
             "requires_declarations": [], "citations": "none"},
            {"id": "intro-gap", "requires_facts": ["gap"],
             "requires_declarations": [], "citations": "none"},
        ],
    },
    "02-methods.md": {
        "section": "methods", "position": 2,
        "blocks": [
            {"id": "methods-contrib", "requires_facts": ["contributions"],
             "requires_declarations": [], "citations": "none"},
            {"id": "methods-chain", "requires_facts": ["problem-statement"],
             "requires_declarations": [], "citations": "none"},
        ],
    },
    "03-related-work.md": {
        "section": "related-work", "position": 3,
        "blocks": [
            {"id": "related-work-gap", "requires_facts": ["gap"],
             "requires_declarations": [], "citations": "none"},
        ],
    },
    "04-abstract.md": {
        "section": "abstract", "position": 4,
        "blocks": [
            {"id": "abstract-contrib", "requires_facts": ["contributions"],
             "requires_declarations": [], "citations": "none"},
        ],
    },
    "05-conclusions.md": {
        "section": "conclusions", "position": 5,
        "blocks": [
            {"id": "conclusions-contrib", "requires_facts": ["contributions"],
             "requires_declarations": [], "citations": "none"},
            {"id": "conclusions-future", "requires_facts": ["limitations"],
             "requires_declarations": [], "citations": "discovery"},
        ],
    },
}

#: Every block's body bytes in the fully-declared green fixture -- literal
#: enough that each check's own mechanical extraction (first-occurrence
#: order, role-prefixed chain lines, `\\item`/`Closing:` gap shape,
#: `\\cite{}`) is exercised against real bytes, never a hand-built
#: `Evidence` alone. Order inside `intro-contrib`/`methods-contrib`/
#: `abstract-contrib`/`conclusions-contrib` matches `_COUPLING_CONTRIBUTIONS`
#: exactly, so the unmutated tree is reachable-green on coupling 1.
_COUPLING_BODIES = {
    "intro-contrib": (
        b"This work makes three contributions: Adaptive Caching improves "
        b"hit rates, Async Prefetch reduces stalls, and Bounded Retry "
        b"avoids cascading failures.\n"
    ),
    "intro-gap": (
        b"\\item first study\n\\item second study\n"
        b"Closing: nobody has studied the combination.\n"
    ),
    "methods-contrib": (
        b"Section 3 implements Adaptive Caching first, then Async "
        b"Prefetch, and finally Bounded Retry.\n"
    ),
    "methods-chain": (
        b"Problem: Bounded Retry addresses cascading failures under load.\n"
        b"Contribution: Bounded Retry limits retries safely.\n"
        b"Property: Bounded Retry is measured by retry count.\n"
        b"Instrument: Bounded Retry is captured by the profiler.\n"
        b"Evidence: Bounded Retry reduces failures after deployment.\n"
    ),
    "related-work-gap": (
        b"\\item first study\n\\item second study\n"
        b"Closing: nobody has studied the combination.\n"
    ),
    "abstract-contrib": (
        b"In brief: Adaptive Caching, Async Prefetch, and Bounded Retry "
        b"together cut overhead.\n"
    ),
    "conclusions-contrib": (
        b"We summarize Adaptive Caching, Async Prefetch, and Bounded Retry "
        b"as the paper's contributions.\n"
    ),
    "conclusions-future": (
        b"Future work should extend Bounded Retry \\cite{future2027}.\n"
    ),
}

#: Blocks whose `substitute` call also records provenance -- both point at
#: the SAME contract file (`02-methods.md`), so `contract-currency`'s own
#: "one edit flags a whole section" requirement is directly exercisable: a
#: one-byte edit to that one file must stale BOTH blocks, not only one.
_COUPLING_PROVENANCE_BLOCKS = ("methods-contrib", "methods-chain")


def _write_coupling_sections(sections_dir: Path) -> None:
    """`contract-input-partition` spec, `Requirement: Two-Heading
    Partition`: every assembled contract must carry `### External inputs`
    and `### Internal chain`, or `paper_graph.assemble_corpus` refuses
    `INPUT_PARTITION_ABSENT` -- this fixture's own concern
    (`the-couplings-hold-or-they-do-not`) is unrelated to that partition, so
    both headings are added empty, never populated with invented content."""
    sections_dir.mkdir(parents=True, exist_ok=True)
    for name, header in _COUPLING_SECTIONS.items():
        text = (
            "---\n" + json.dumps(header, indent=2) + "\n---\n\nProse.\n\n"
            "### External inputs\n\nNone.\n\n### Internal chain\n\nNone.\n"
        )
        (sections_dir / name).write_text(text, encoding="utf-8")


def _coupling_record(**overrides) -> dict:
    """The fully-declared green `paper/couplings.json` record. `overrides`
    replaces whole top-level keys (never deep-merged) -- a mutation test
    that wants "the same record, minus one field" builds that dict itself
    from this function's own return value, which is the point: no hidden
    default is mutated in place."""
    record = {
        "facts": {
            "contributions": list(_COUPLING_CONTRIBUTIONS),
            "limitations": ["lim-overhead"],
        },
        "chain": {"links": [{"word": "Bounded Retry"}]},
        "artefacts": {
            "setup_cells": ["cell-alpha", "cell-beta"],
            "results_artefacts": ["cell-alpha"],
        },
        "future_work": {
            "directions": [
                {"id": "extend-retry", "limitation": "lim-overhead", "cite_key": "future2027"},
            ],
        },
        "blocks": {block_id: True for block_id in _COUPLING_BODIES},
    }
    record.update(overrides)
    return record


def _build_coupling_paper(
    paper_dir: Path, sections_dir: Path, *,
    bodies: dict | None = None, record: dict | None = None,
    provenance_blocks=_COUPLING_PROVENANCE_BLOCKS, write_refs_bib: bool = True,
) -> None:
    """Builds a real, on-disk fixture tree through the SAME production
    calls an operator would use (`scaffold`, `open`, `substitute
    --contract`) -- never a hand-assembled `main.tex`, so every marker
    digest and every provenance `contract_sha256` is genuine rather than
    computed by this helper a second, possibly-drifting way."""
    _write_coupling_sections(sections_dir)
    paper_scaffold.scaffold(paper_dir)
    bodies = _COUPLING_BODIES if bodies is None else bodies
    for block_id, body in bodies.items():
        paper_block.open_block(paper_dir, block_id, at_end=True)
        contract = sections_dir / "02-methods.md" if block_id in provenance_blocks else None
        paper_block.substitute(paper_dir, block_id, new_body=body, contract=contract)
    if write_refs_bib:
        (paper_dir / "refs.bib").write_text(
            "@article{future2027,\n  title={Future Work},\n  year={2027}\n}\n",
            encoding="utf-8",
        )
    record = _coupling_record() if record is None else record
    (paper_dir / "couplings.json").write_text(json.dumps(record, indent=2), encoding="utf-8")


class EvidenceTests(unittest.TestCase):
    """`paper_coupling_evidence.py`: the record grammar, and M6."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"
        self.sections_dir = Path(self._tmp.name) / "sections"

    def test_gather_reads_the_declared_record_and_the_provenance_region(self) -> None:
        _build_coupling_paper(self.paper_dir, self.sections_dir)

        evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

        self.assertEqual(evidence.record["facts"]["contributions"], _COUPLING_CONTRIBUTIONS)
        self.assertIsNotNone(evidence.provenance)
        self.assertEqual(
            {entry["block"] for entry in evidence.provenance["body"]["records"]},
            set(_COUPLING_PROVENANCE_BLOCKS),
        )
        self.assertEqual(evidence.block_bodies["intro-contrib"], _COUPLING_BODIES["intro-contrib"])
        self.assertEqual(
            evidence.blocks_by_fact["contributions"][0],
            ("abstract-contrib", "conclusions-contrib", "intro-contrib", "methods-contrib"),
        )

    def test_gather_without_provenance_reports_it_absent(self) -> None:
        _build_coupling_paper(self.paper_dir, self.sections_dir, provenance_blocks=())

        evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

        self.assertIsNone(evidence.provenance)
        self.assertEqual(evidence.contract_drift, {})

    def test_mutation_6_absent_declaration_record_refuses_and_writes_nothing(self) -> None:
        _build_coupling_paper(self.paper_dir, self.sections_dir)
        (self.paper_dir / "couplings.json").unlink()
        before = (self.paper_dir / "main.tex").read_bytes()

        with self.assertRaises(Refused) as ctx:
            paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

        self.assertEqual(ctx.exception.code, "DECLARATION_RECORD_ABSENT")
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), before)

    def test_mutation_6_empty_declaration_record_refuses(self) -> None:
        _build_coupling_paper(self.paper_dir, self.sections_dir)
        (self.paper_dir / "couplings.json").write_text("{}", encoding="utf-8")

        with self.assertRaises(Refused) as ctx:
            paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

        self.assertEqual(ctx.exception.code, "DECLARATION_RECORD_ABSENT")

    def test_headerless_sections_report_unreadable_never_refuse(self) -> None:
        _build_coupling_paper(self.paper_dir, self.sections_dir)
        (self.sections_dir / "01-introduction.md").write_text("no front matter here\n", encoding="utf-8")

        evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

        self.assertEqual(
            evidence.blocks_by_fact["contributions"], ((), "SECTION_CONTRACTS_UNREADABLE"),
        )

    def test_no_block_requires_an_unused_fact(self) -> None:
        _build_coupling_paper(self.paper_dir, self.sections_dir)

        evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

        self.assertEqual(evidence.blocks_by_fact["dataset"], ((), "NO_BLOCK_REQUIRES_FACT"))


class ReportShapeTests(unittest.TestCase):
    """`paper_verify.py`'s report: the closed roster is one declaration,
    proven both directions, and `unmeasured` is never counted in `holds`."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"
        self.sections_dir = Path(self._tmp.name) / "sections"
        _build_coupling_paper(self.paper_dir, self.sections_dir)
        self.evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

    def test_report_carries_exactly_one_object_per_check_both_directions(self) -> None:
        report = paper_verify.run(self.evidence)

        reported = [entry["check"] for entry in report["checks"]]
        self.assertEqual(reported, list(paper_verify.CHECKS))
        self.assertEqual(set(reported), set(paper_verify.CHECKS))

    def test_buckets_sum_to_the_roster_length_and_unmeasured_excluded_from_holds(self) -> None:
        report = paper_verify.run(self.evidence)

        self.assertEqual(report["holds"] + report["fails"] + report["unmeasured"], len(paper_verify.CHECKS))
        unmeasured_checks = [entry["check"] for entry in report["checks"] if entry["verdict"] == "unmeasured"]
        self.assertNotIn("holds", [entry["verdict"] for entry in report["checks"] if entry["check"] in unmeasured_checks])

    def test_every_unmeasured_reason_used_is_in_the_closed_roster(self) -> None:
        report = paper_verify.run(self.evidence)

        for entry in report["checks"]:
            if entry["verdict"] == "unmeasured":
                self.assertIn(entry["unmeasured_reason"], paper_verify.UNMEASURED_REASONS)
            else:
                self.assertIsNone(entry["unmeasured_reason"])

    def test_gap_check_is_unconditionally_unmeasured_and_all_declared_sides_carry_the_limit(self) -> None:
        report = paper_verify.run(self.evidence)
        by_check = {entry["check"]: entry for entry in report["checks"]}

        self.assertEqual(by_check["gap"]["verdict"], "unmeasured")
        self.assertEqual(by_check["gap"]["unmeasured_reason"], "ASSISTED_READING_REQUIRED")

    def test_two_declared_sides_limit_is_derived_never_hand_listed(self) -> None:
        # None of the seven checks' baseline `sides` are ALL declared
        # (`skill-audit`'s own shape prefers a derived side wherever one is
        # possible), so this is a report-level property of `_entry` itself,
        # proven directly -- never a hand-list of which check ever reaches
        # it, matching design.md's own "a test derives that condition from
        # the report rather than a hand-list".
        all_declared = paper_verify._entry(
            "contribution-list", classification="mechanical", verdict="pass",
            sides=[
                {"name": "a", "source": "declared", "origin": "x"},
                {"name": "b", "source": "declared", "origin": "y"},
            ],
            evidence={}, limits=[], unmeasured_reason=None,
        )
        self.assertIn("TWO_DECLARED_SIDES", all_declared["limits"])

        mixed = paper_verify._entry(
            "contribution-list", classification="mechanical", verdict="pass",
            sides=[
                {"name": "a", "source": "declared", "origin": "x"},
                {"name": "b", "source": "derived", "origin": "y"},
            ],
            evidence={}, limits=[], unmeasured_reason=None,
        )
        self.assertNotIn("TWO_DECLARED_SIDES", mixed["limits"])

        # And the real report: no check's baseline sides are all declared.
        report = paper_verify.run(self.evidence)
        for entry in report["checks"]:
            if entry["sides"] and all(side["source"] == "declared" for side in entry["sides"]):
                self.assertIn("TWO_DECLARED_SIDES", entry["limits"])


class ReadOnlyTests(unittest.TestCase):
    """The three-way proof `verify` never writes: the AST lock, an executed
    content manifest, and M8 -- the manifest test itself, mutated."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"
        self.sections_dir = Path(self._tmp.name) / "sections"

    def _forbidden_write_calls(self, source_path: Path) -> list:
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        forbidden_names = {
            "write_bytes", "write_text", "mkdir", "unlink", "replace", "rename",
        }
        forbidden_modules = {"shutil", "tempfile"}
        hits: list = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in forbidden_modules:
                        hits.append(f"import {alias.name}")
            if isinstance(node, ast.Attribute) and node.attr in forbidden_names:
                hits.append(node.attr)
            if isinstance(node, ast.Attribute) and node.attr in ("substitute", "open_block"):
                if isinstance(node.value, ast.Name) and node.value.id == "paper_block":
                    hits.append(f"paper_block.{node.attr}")
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "open":
                # A bare `open(...)` call -- this module never opens a file
                # directly (Path.read_bytes/read_text are used instead), so
                # any occurrence at all is worth naming.
                hits.append("open(...)")
        return hits

    def test_ast_lock_finds_no_write_operation_in_either_module(self) -> None:
        for name in ("paper_coupling_evidence.py", "paper_verify.py"):
            with self.subTest(module=name):
                self.assertEqual(self._forbidden_write_calls(SKILL_SCRIPTS / name), [])

    #: The only imports `paper_verify.py` has ever needed -- a closed
    #: ALLOWlist, not a hand-picked list of banned function names. The
    #: distinction matters: a denylist of forbidden calls is complete only
    #: by whoever remembered to add to it (this build's own repeated
    #: objection); a default-deny allowlist forecloses the ENTIRE universe
    #: of disk/network/process-capable stdlib modules in one shot --
    #: `pathlib`, `os`, `io`, `shutil`, `tempfile`, `sqlite3`, `socket`,
    #: `subprocess`, `ctypes`, and everything else never named here -- by
    #: construction, not by enumeration. Growing this set is a deliberate,
    #: visible test edit; nothing shrinks it silently.
    _PAPER_VERIFY_ALLOWED_IMPORTS = frozenset({"re"})
    _PAPER_VERIFY_ALLOWED_IMPORT_FROM_MODULES = frozenset({"__future__"})

    def _forbidden_reads(self, source_path: Path) -> list:
        """The read-side half of the disk-access lock. Two constructions,
        neither a hand-picked list of banned function names:

        1. A default-deny IMPORT allowlist (`_PAPER_VERIFY_ALLOWED_IMPORTS`
           / `_..._IMPORT_FROM_MODULES`, above). Any import beyond `re`
           (and `__future__`) is forbidden outright, and so is routing
           around the allowlist via dynamic import (`__import__(...)`,
           `importlib.import_module(...)`).
        2. Every `Evidence` field actually typed `Path`, read live off
           `paper_coupling_evidence.Evidence`'s own dataclass fields via
           `dataclasses.fields` -- never hand-typed here. Today that is
           `paper_dir`/`sections_dir`, kept on the object, per that
           dataclass's own docstring, only so `verify`'s report can name
           where evidence came from -- never so a check could re-open a
           file `gather()` already read. Touching either attribute at all,
           from any expression, is forbidden: a pure check has no
           legitimate reason to reach for either one.

        This is meaningful only for `paper_verify.py` -- `paper_coupling_
        evidence.py`'s entire job is reading, so this exact check would
        flag its own legitimate imports and parameters
        (`test_the_read_lock_would_flag_coupling_evidence_if_misapplied`,
        below proves it, rather than leaving the asymmetry asserted only in
        prose).
        """
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        path_field_names = {
            f.name for f in dataclasses.fields(paper_coupling_evidence.Evidence)
            if f.type == "Path"
        }
        hits: list = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name not in self._PAPER_VERIFY_ALLOWED_IMPORTS:
                        hits.append(f"import {alias.name}")
            if isinstance(node, ast.ImportFrom):
                if node.module not in self._PAPER_VERIFY_ALLOWED_IMPORT_FROM_MODULES:
                    hits.append(f"from {node.module} import ...")
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "__import__":
                    hits.append("__import__(...)")
                if isinstance(func, ast.Attribute) and func.attr == "import_module":
                    hits.append("importlib.import_module(...)")
            if isinstance(node, ast.Attribute) and node.attr in path_field_names:
                hits.append(f"evidence.{node.attr}")
        return hits

    def test_ast_lock_finds_no_disk_read_in_paper_verify(self) -> None:
        self.assertEqual(self._forbidden_reads(SKILL_SCRIPTS / "paper_verify.py"), [])

    def test_the_read_lock_would_flag_coupling_evidence_if_misapplied(self) -> None:
        # Proof the scoping to paper_verify.py alone is doing real work,
        # not silently vacuous: paper_coupling_evidence.py's own legitimate
        # `json`/`sys`/`pathlib` imports and its own `paper_dir`/
        # `sections_dir` parameters would trip this exact lock if it were
        # ever pointed at the reader by mistake -- the two files are
        # asymmetric by measurement, never by omission.
        hits = self._forbidden_reads(SKILL_SCRIPTS / "paper_coupling_evidence.py")
        self.assertTrue(hits, "expected the read lock to flag the reader's own legitimate imports")

    def test_coupling_evidence_legitimate_reads_still_pass(self) -> None:
        # A lock that forbade reads everywhere would break the reader whose
        # entire job is reading -- confirm `gather()` still performs its
        # real disk reads end to end, unaffected by the lock above (which
        # is never applied to this module).
        _build_coupling_paper(self.paper_dir, self.sections_dir)
        evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)
        self.assertEqual(evidence.paper_dir, self.paper_dir)
        self.assertEqual(evidence.sections_dir, self.sections_dir)
        self.assertTrue(evidence.main_tex_bytes)
        self.assertTrue(evidence.record)

    def test_content_manifest_unchanged_by_a_real_verify_run(self) -> None:
        _build_coupling_paper(self.paper_dir, self.sections_dir)

        def _manifest() -> dict:
            return {
                str(path.relative_to(self.paper_dir)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(self.paper_dir.rglob("*")) if path.is_file()
            }

        before = _manifest()
        evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)
        paper_verify.run(evidence)
        after = _manifest()

        self.assertEqual(before, after)

    def test_mutation_8_a_write_in_paper_verify_fails_the_manifest_guard(self) -> None:
        proc = _run_against_mutant(
            "def run(evidence, *, optional_block_ids: frozenset = frozenset()) -> dict:",
            'def run(evidence, *, optional_block_ids: frozenset = frozenset()) -> dict:\n'
            '    import pathlib as _pl\n'
            '    _pl.Path(evidence.paper_dir, "main.tex").write_bytes(b"x")',
            "tests.test_paper_writing.ReadOnlyTests.test_content_manifest_unchanged_by_a_real_verify_run",
            source_path=SKILL_SCRIPTS / "paper_verify.py",
        )
        self.assertNotEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("MUTANT_IMPORTED_OK", proc.stdout)


class CouplingOneTests(unittest.TestCase):
    """Coupling 1 (`coupling-verification` spec, `Requirement: Coupling 1
    — Contribution List Identity`)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"
        self.sections_dir = Path(self._tmp.name) / "sections"
        _build_coupling_paper(self.paper_dir, self.sections_dir)
        self.evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

    def test_unmutated_fixture_holds(self) -> None:
        result = paper_verify.check_contribution_list(self.evidence)
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["evidence"]["mismatched_blocks"], [])
        self.assertEqual(result["evidence"]["absent_from_bytes"], [])

    def test_mutation_1_reordered_names_in_one_block_fails(self) -> None:
        reordered = (
            b"In brief: Async Prefetch, Adaptive Caching, and Bounded Retry "
            b"together cut overhead.\n"
        )
        mutated = dataclasses.replace(
            self.evidence,
            block_bodies={**self.evidence.block_bodies, "abstract-contrib": reordered},
        )

        result = paper_verify.check_contribution_list(mutated)

        self.assertEqual(result["verdict"], "fail")
        self.assertIn("abstract-contrib", result["evidence"]["mismatched_blocks"])

    def test_declared_name_absent_from_block_bytes_fails_distinctly(self) -> None:
        missing_name = b"In brief: Adaptive Caching and Async Prefetch cut overhead.\n"
        mutated = dataclasses.replace(
            self.evidence,
            block_bodies={**self.evidence.block_bodies, "abstract-contrib": missing_name},
        )

        result = paper_verify.check_contribution_list(mutated)

        self.assertEqual(result["verdict"], "fail")
        # The evidence payload names this as an absent-name finding
        # distinctly from a plain order mismatch, even though a block
        # missing a name can never equal the full declared order either
        # (spec, `Requirement: Declared-Name Literal Presence Limit`):
        # both reasons are reported, neither one hides the other.
        self.assertIn(
            {"block": "abstract-contrib", "name": "Bounded Retry"},
            result["evidence"]["absent_from_bytes"],
        )

    def test_an_undeclared_block_reports_unmeasured_not_pass(self) -> None:
        record = _coupling_record()
        del record["blocks"]["abstract-contrib"]
        mutated = dataclasses.replace(self.evidence, record=record)

        result = paper_verify.check_contribution_list(mutated)

        self.assertEqual(result["verdict"], "unmeasured")
        self.assertEqual(result["unmeasured_reason"], "BLOCK_NOT_DECLARED")


class CouplingTwoTests(unittest.TestCase):
    """Coupling 2 (`coupling-verification` spec, `Requirement: Coupling 2
    — Chain Word Identity`)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"
        self.sections_dir = Path(self._tmp.name) / "sections"
        _build_coupling_paper(self.paper_dir, self.sections_dir)
        self.evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

    def test_unmutated_fixture_holds(self) -> None:
        result = paper_verify.check_chain(self.evidence)
        self.assertEqual(result["verdict"], "pass")

    def test_mutation_2_synonym_at_one_link_fails(self) -> None:
        # "Elastic Backoff" is not a substring of "Bounded Retry" -- a
        # synonym, never a paraphrase that would still pass a substring
        # check by accident.
        synonym_body = (
            b"Problem: Bounded Retry addresses cascading failures under load.\n"
            b"Contribution: Elastic Backoff limits retries safely.\n"
            b"Property: Bounded Retry is measured by retry count.\n"
            b"Instrument: Bounded Retry is captured by the profiler.\n"
            b"Evidence: Bounded Retry reduces failures after deployment.\n"
        )
        mutated = dataclasses.replace(
            self.evidence,
            block_bodies={**self.evidence.block_bodies, "methods-chain": synonym_body},
        )

        result = paper_verify.check_chain(mutated)

        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["evidence"]["links"][0]["roles_present"]["contribution"])

    def test_closure_against_an_undeclared_word_fails(self) -> None:
        record = _coupling_record()
        record["chain"] = {"links": [{"word": "Not A Contribution"}]}
        mutated = dataclasses.replace(self.evidence, record=record)

        result = paper_verify.check_chain(mutated)

        self.assertEqual(result["verdict"], "fail")
        self.assertFalse(result["evidence"]["links"][0]["closure"])


class CitationTests(unittest.TestCase):
    """Check A (`citation-integrity` spec)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"
        self.sections_dir = Path(self._tmp.name) / "sections"
        _build_coupling_paper(self.paper_dir, self.sections_dir)
        self.evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

    def test_unmutated_fixture_holds_with_no_dangling_or_orphan(self) -> None:
        result = paper_verify.check_citations(self.evidence)
        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["evidence"]["dangling"], [])
        self.assertEqual(result["evidence"]["orphans"], [])

    def test_mutation_3a_dangling_cite_fails_naming_it(self) -> None:
        mutated = dataclasses.replace(
            self.evidence,
            main_tex_bytes=self.evidence.main_tex_bytes + b"\\cite{ghost}\n",
        )

        result = paper_verify.check_citations(mutated)

        self.assertEqual(result["verdict"], "fail")
        self.assertIn("ghost", result["evidence"]["dangling"])
        # M3a alone must not move the orphan-entry direction.
        self.assertEqual(result["evidence"]["orphans"], [])

    def test_mutation_3b_orphan_entry_is_listed_not_failing(self) -> None:
        mutated = dataclasses.replace(
            self.evidence,
            refs_bib_bytes=self.evidence.refs_bib_bytes
            + b"@article{orphan2028,\n  title={Nobody Cites This},\n  year={2028}\n}\n",
        )

        result = paper_verify.check_citations(mutated)

        # M3b alone must not move the dangling-cite direction.
        self.assertEqual(result["evidence"]["dangling"], [])
        self.assertIn("orphan2028", result["evidence"]["orphans"])
        self.assertEqual(result["verdict"], "pass")


class GapTests(unittest.TestCase):
    """Coupling 3 (`coupling-verification` spec, `Requirement: Coupling 3
    — The Gap Is Assisted`)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"
        self.sections_dir = Path(self._tmp.name) / "sections"
        _build_coupling_paper(self.paper_dir, self.sections_dir)
        self.evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

    def test_unmutated_fixture_is_unconditionally_unmeasured_with_clean_mechanical_subchecks(self) -> None:
        result = paper_verify.check_gap(self.evidence)

        self.assertEqual(result["verdict"], "unmeasured")
        self.assertEqual(result["unmeasured_reason"], "ASSISTED_READING_REQUIRED")
        mechanical = result["evidence"]["mechanical"]
        self.assertTrue(mechanical["both_closings_present"])
        self.assertTrue(mechanical["fronts_equal"])
        self.assertTrue(mechanical["front_counts_equal"])
        self.assertEqual(result["evidence"]["depth_reading"], "unmeasured")

    def test_both_full_texts_and_front_lists_are_published(self) -> None:
        result = paper_verify.check_gap(self.evidence)

        self.assertEqual(
            result["evidence"]["closings"]["intro-gap"], "nobody has studied the combination.",
        )
        self.assertEqual(result["evidence"]["fronts"]["intro-gap"], ["first study", "second study"])

    def test_a_missing_closing_is_a_mechanical_fact_never_a_gate(self) -> None:
        no_closing = b"\\item first study\n\\item second study\n"
        mutated = dataclasses.replace(
            self.evidence,
            block_bodies={**self.evidence.block_bodies, "intro-gap": no_closing},
        )

        result = paper_verify.check_gap(mutated)

        # Still unconditionally unmeasured -- a mechanical failure never
        # promotes or demotes the top-level verdict.
        self.assertEqual(result["verdict"], "unmeasured")
        self.assertFalse(result["evidence"]["mechanical"]["both_closings_present"])

    def test_unequal_front_counts_report_mechanical_fail_still_unmeasured(self) -> None:
        three_items = (
            b"\\item first study\n\\item second study\n\\item third study\n"
            b"Closing: nobody has studied the combination.\n"
        )
        mutated = dataclasses.replace(
            self.evidence,
            block_bodies={**self.evidence.block_bodies, "related-work-gap": three_items},
        )

        result = paper_verify.check_gap(mutated)

        self.assertEqual(result["verdict"], "unmeasured")
        self.assertFalse(result["evidence"]["mechanical"]["front_counts_equal"])
        self.assertFalse(result["evidence"]["mechanical"]["fronts_equal"])


class ArtefactsTests(unittest.TestCase):
    """Coupling 4 (`coupling-verification` spec, `Requirement: Coupling 4
    — Diagram Cell Disjointness`)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"
        self.sections_dir = Path(self._tmp.name) / "sections"
        _build_coupling_paper(self.paper_dir, self.sections_dir)
        self.evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

    def test_unmutated_fixture_holds(self) -> None:
        result = paper_verify.check_artefacts(self.evidence)
        self.assertEqual(result["verdict"], "pass")

    def test_mutation_4a_undeclared_results_cell_fails(self) -> None:
        record = _coupling_record()
        record["artefacts"]["results_artefacts"] = ["cell-alpha", "cell-nowhere"]
        mutated = dataclasses.replace(self.evidence, record=record)

        result = paper_verify.check_artefacts(mutated)

        self.assertEqual(result["verdict"], "fail")
        self.assertIn("cell-nowhere", result["evidence"]["undeclared_results"])

    def test_mutation_4b_a_contribution_added_to_setup_cells_fails_on_intersection(self) -> None:
        record = _coupling_record()
        record["artefacts"]["setup_cells"] = ["cell-alpha", "cell-beta", "Adaptive Caching"]
        mutated = dataclasses.replace(self.evidence, record=record)

        result = paper_verify.check_artefacts(mutated)

        self.assertEqual(result["verdict"], "fail")
        self.assertIn("Adaptive Caching", result["evidence"]["shared_with_methods"])

    def test_artefacts_inherits_contribution_lists_own_unmeasured_status(self) -> None:
        record = _coupling_record()
        del record["blocks"]["abstract-contrib"]
        mutated = dataclasses.replace(self.evidence, record=record)

        result = paper_verify.check_artefacts(mutated)

        self.assertEqual(result["verdict"], "unmeasured")
        self.assertEqual(result["unmeasured_reason"], "BLOCK_NOT_DECLARED")


class FutureWorkTests(unittest.TestCase):
    """Coupling 5 (`coupling-verification` spec, `Requirement: Coupling 5
    — Future Work ⊆ Limitations`)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"
        self.sections_dir = Path(self._tmp.name) / "sections"
        _build_coupling_paper(self.paper_dir, self.sections_dir)
        self.evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

    def test_unmutated_fixture_holds_and_publishes_out_of_reach_subparts(self) -> None:
        result = paper_verify.check_future_work(self.evidence)

        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["evidence"]["relevance"], "out-of-reach")
        self.assertEqual(result["evidence"]["specificity"], "out-of-reach")

    def test_mutation_5_a_direction_answering_no_declared_limitation_fails_totality(self) -> None:
        record = _coupling_record()
        record["future_work"]["directions"] = [
            {"id": "extend-retry", "limitation": "lim-nowhere", "cite_key": "future2027"},
        ]
        mutated = dataclasses.replace(self.evidence, record=record)

        result = paper_verify.check_future_work(mutated)

        self.assertEqual(result["verdict"], "fail")
        self.assertIn("extend-retry", result["evidence"]["unanswered"])

    def test_a_direction_whose_cite_key_never_occurs_in_the_block_fails(self) -> None:
        record = _coupling_record()
        record["future_work"]["directions"] = [
            {"id": "extend-retry", "limitation": "lim-overhead", "cite_key": "nevercited2029"},
        ]
        mutated = dataclasses.replace(self.evidence, record=record)

        result = paper_verify.check_future_work(mutated)

        self.assertEqual(result["verdict"], "fail")
        self.assertIn("extend-retry", result["evidence"]["missing_cite"])


class ContractCurrencyTests(unittest.TestCase):
    """Check B (`contract-currency` spec)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"
        self.sections_dir = Path(self._tmp.name) / "sections"

    def test_unmutated_fixture_holds_with_provenance_present(self) -> None:
        _build_coupling_paper(self.paper_dir, self.sections_dir)
        evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

        result = paper_verify.check_contract_currency(evidence)

        self.assertEqual(result["verdict"], "pass")
        self.assertEqual(result["classification"], "out-of-reach today")

    def test_mutation_7_absent_provenance_region_reports_unmeasured_never_zero_stale(self) -> None:
        _build_coupling_paper(self.paper_dir, self.sections_dir, provenance_blocks=())
        evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

        result = paper_verify.check_contract_currency(evidence)

        self.assertEqual(result["verdict"], "unmeasured")
        self.assertEqual(result["unmeasured_reason"], "CONTRACT_RECORD_ABSENT")
        # Run continues -- every OTHER check still reports a real verdict.
        report = paper_verify.run(evidence)
        by_check = {entry["check"]: entry for entry in report["checks"]}
        self.assertEqual(by_check["contribution-list"]["verdict"], "pass")

    def test_one_byte_edit_to_the_shared_contract_file_flags_both_recorded_blocks_stale(self) -> None:
        _build_coupling_paper(self.paper_dir, self.sections_dir)
        contract_path = self.sections_dir / "02-methods.md"
        contract_path.write_text(contract_path.read_text(encoding="utf-8") + "\nOne more line.\n", encoding="utf-8")
        evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

        result = paper_verify.check_contract_currency(evidence)

        self.assertEqual(result["verdict"], "fail")
        self.assertEqual(
            sorted(result["evidence"]["stale_blocks"]),
            sorted(_COUPLING_PROVENANCE_BLOCKS),
        )


class CouplingVerifyCLITests(unittest.TestCase):
    """`verify` wired into `paper_cli.py` (`block-substitution` spec,
    `Requirement: verify Verb Is Registered And Read-Only`). Real
    subprocess calls against the real `paper_cli.py` resolve `--paper`/
    `--sections` against the REAL repository root
    (`paper_scaffold.FORGE_ROOT`), so -- the same convention
    `ScaffoldTests.test_cli_scaffold_verb_runs_and_emits_json` already
    established -- this fixture lives under the already-gitignored
    `implementations/` tree, never an arbitrary tempdir outside it."""

    def setUp(self) -> None:
        test_root = FORGE_ROOT / "implementations" / f".paper-writing-verify-cli-test-{os.getpid()}"
        self.addCleanup(shutil.rmtree, test_root, ignore_errors=True)
        self.paper_dir = test_root / "paper"
        self.sections_dir = test_root / "sections"
        _build_coupling_paper(self.paper_dir, self.sections_dir)

    def test_a_full_run_leaves_main_tex_untouched_and_exits_zero(self) -> None:
        before = (self.paper_dir / "main.tex").read_bytes()

        proc = subprocess.run(
            [
                sys.executable, str(CLI), "verify",
                "--paper", str(self.paper_dir), "--sections", str(self.sections_dir),
            ],
            capture_output=True, text=True, timeout=30,
        )

        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), before)
        by_check = {entry["check"]: entry for entry in payload["checks"]}
        self.assertEqual(by_check["contribution-list"]["verdict"], "pass")
        self.assertEqual(by_check["gap"]["verdict"], "unmeasured")

    def test_a_refusal_path_also_writes_nothing_and_exits_two(self) -> None:
        (self.paper_dir / "couplings.json").unlink()
        before = (self.paper_dir / "main.tex").read_bytes()

        proc = subprocess.run(
            [
                sys.executable, str(CLI), "verify",
                "--paper", str(self.paper_dir), "--sections", str(self.sections_dir),
            ],
            capture_output=True, text=True, timeout=30,
        )

        self.assertEqual(proc.returncode, 2, proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "refused")
        self.assertEqual(payload["code"], "DECLARATION_RECORD_ABSENT")
        self.assertEqual((self.paper_dir / "main.tex").read_bytes(), before)

    def test_mutation_9_the_roster_walk_reaches_paper_verify_by_source_not_import(self) -> None:
        """M9 (design.md; tasks.md 3.9) proves the roster walk reaches
        `paper_verify.py` -- this skill's THIRD imported module, beyond
        `paper_coupling_evidence.py` -- without M9, widening the walk to a
        new module is an untested claim.

        `_run_against_mutant` (used for M8, above) cannot prove this: it
        loads the mutant through `sys.modules`, but
        `reachable_paper_refusal_codes()` never imports the modules it
        scans -- it reads each one's own bytes directly from
        `SKILL_SCRIPTS / f"{name}.py"` (`paper_cli_imported_modules()`,
        `tests/test_paper_writing.py`), a fixed real path a `sys.modules`
        substitution cannot redirect. So this is proven by hand, on the
        real file, the same way `ModuleCompletenessTests`'s own docstring
        already documents for its own precedent case: a throwaway
        `Refused` was inserted into `paper_verify.py`, `RefusalRosterTests
        .test_every_reachable_refusal_is_classified` was run and observed
        to fail naming the new code, the insertion was removed, and the
        suite was confirmed green again -- verified during this change's
        own implementation, not re-run automatically on every CI pass
        (planting it permanently would corrupt this skill's own roster for
        every other suite scanning `scripts/*.py`, `ModuleCompletenessTests`'
        own reasoning, reused verbatim here).

        This test instead asserts the STATIC precondition M9 depends on:
        `paper_verify.py` is a member of the whole-module scan set at all,
        so a `Refused` added anywhere in it is picked up by construction.
        """
        self.assertIn(SKILL_SCRIPTS / "paper_verify.py", paper_cli_imported_modules())


class CouplingFixtureLeakTests(unittest.TestCase):
    """The forge leak guard, extended to this capability's own fixture
    tree -- `shipped_documents()` never reaches `tests/`, so nothing else
    in this suite scans it (design.md, `What Breaks`: "the fixture tree...
    must carry no target vocabulary")."""

    def test_the_fixture_bodies_and_record_carry_no_forge_vocabulary(self) -> None:
        sys.path.insert(0, str(FORGE_ROOT / "tests"))
        import forge_vocabulary  # noqa: E402

        texts = [json.dumps(_COUPLING_SECTIONS)] + [
            body.decode("utf-8") for body in _COUPLING_BODIES.values()
        ] + [json.dumps(_coupling_record())]
        leaking = {name: forge_vocabulary.leaks_in(text) for name, text in
                   zip(list(_COUPLING_BODIES) + ["sections", "record"], texts)
                   if forge_vocabulary.leaks_in(text)}
        self.assertEqual(leaking, {})


class ZZLiveAgentGuardTests(unittest.TestCase):
    """`writing-orchestration` spec, `Requirement: No Live Agent Invocation
    In Tests`. Named `ZZ...` so it sorts alphabetically last among this
    module's own test classes (`unittest.TestLoader` iterates `dir(module)`,
    which is sorted) -- every subprocess-launching test class defined above
    (`ScaffoldTests`, `CLIWiringTests`, `MutationProofTests`,
    `WriterMutationProofTests`, `ReadOnlyTests`, `CouplingVerifyCLITests`)
    has therefore already run by the time this assertion executes. The monitor itself (top of this file) is installed
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


class ThreeDraftProofSetTests(unittest.TestCase):
    """`style-leak-detection` spec, `Requirement: Three-Draft Proof Set`,
    scenario "A, B, and S share every input but the style channel" --
    flagged CRITICAL UNTESTED by this change's own corrective verify. The
    scenario describes the orchestrating agent's live shuttle procedure
    (three separate redactor calls), which this suite may never spawn
    (Decision D2). What IS achievable, and was missing, is the
    CLI-observable half: that `write_block`, given three contracts sharing
    identical contract prose, evidence set and mode and differing ONLY in
    `style_set`, treats every non-style field identically -- proven against
    the exact mechanism the pipeline itself uses to recognize "the same
    attempt" (`_attempt_key`), and end to end through three real
    `write_block` calls."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base_dir = Path(self._tmp.name)

    def _fresh_paper_dir(self, name: str) -> Path:
        paper_dir = self.base_dir / name
        _write_fixture(paper_dir, _marker_pair("mm-proposal", b"Old body.\n"))
        return paper_dir

    def test_attempt_key_is_identical_across_a_b_and_s(self) -> None:
        """The A/B/S split changes only `style_set`. `_attempt_key` --
        which the one-bounded-re-draft ledger uses to decide whether two
        submissions are "the same attempt" -- reads contract, evidence and
        mode alone, so it must hash identically for all three regardless of
        style."""
        contract_a = _write_contract(citations_regime="none", evidence_set=(), style_set=())
        contract_b = _write_contract(citations_regime="none", evidence_set=(), style_set=())
        contract_s = _write_contract(
            citations_regime="none", evidence_set=(),
            style_set=({"reference": "paperA", "span": "one two three four five six"},),
        )
        key_a = paper_write._attempt_key(contract_a)
        key_b = paper_write._attempt_key(contract_b)
        key_s = paper_write._attempt_key(contract_s)
        self.assertEqual(key_a, key_b)
        self.assertEqual(key_a, key_s)

    def test_a_and_b_and_s_produce_identical_outcomes_but_for_the_style_channel(self) -> None:
        """Three real `write_block` calls, one shared contract shape,
        differing only in `style_set`, each against its own fresh fixture
        (so all three independently reach `substitute`). A and B use the
        SAME draft -- non-style-field identity is exactly what is under
        test, not incidental wording variance a live redactor would
        introduce. S uses a differently-worded but content-equivalent draft
        that shares no eight-token run with its one recorded sample, so the
        tripwire stays silent and S reaches `written` too."""
        contract_a = _write_contract(citations_regime="none", evidence_set=(), style_set=())
        contract_b = _write_contract(citations_regime="none", evidence_set=(), style_set=())
        contract_s = _write_contract(
            citations_regime="none", evidence_set=(),
            style_set=({"reference": "paperA", "span": "one two three four five six"},),
        )
        self.assertEqual(contract_a.contract_prose, contract_b.contract_prose)
        self.assertEqual(contract_a.contract_prose, contract_s.contract_prose)
        self.assertEqual(contract_a.mode, contract_s.mode)
        self.assertEqual(contract_a.evidence_set, contract_s.evidence_set)

        result_a = paper_write.write_block(
            self._fresh_paper_dir("a"), contract_a, _CLEAN_DRAFT, _CLEAN_AUDIT,
        )
        result_b = paper_write.write_block(
            self._fresh_paper_dir("b"), contract_b, _CLEAN_DRAFT, _CLEAN_AUDIT,
        )
        styled_draft = {
            "latex": "This paragraph closes the whole demonstration.",
            "bindings": [
                {"sentence": "This paragraph closes the whole demonstration.", "binding": "structural"},
            ],
        }
        result_s = paper_write.write_block(
            self._fresh_paper_dir("s"), contract_s, styled_draft, _CLEAN_AUDIT,
        )

        for result in (result_a, result_b, result_s):
            self.assertEqual(result["status"], "written")
            self.assertEqual(result["verdicts"], result_a["verdicts"])

        self.assertEqual(result_a["styleChannel"], {"status": "unmeasured"})
        self.assertEqual(result_b["styleChannel"], {"status": "unmeasured"})
        self.assertEqual(result_s["styleChannel"]["status"], "measured")

    def test_mutation_8_style_leaking_into_the_attempt_key_fails_the_identity_guard(self) -> None:
        """Falsifies the guard above: if `_attempt_key` were changed to
        fold `style_set` into its payload, A and S would no longer hash
        identically, and `test_attempt_key_is_identical_across_a_b_and_s`
        must go red -- proving that test can actually fail, not just that
        it currently passes."""
        proc = _run_against_mutant(
            '            "mode": contract.mode,\n        },',
            '            "mode": contract.mode,\n'
            '            "style": [dict(entry) for entry in contract.style_set],\n'
            '        },',
            "tests.test_paper_writing.ThreeDraftProofSetTests"
            ".test_attempt_key_is_identical_across_a_b_and_s",
            source_path=SKILL_SCRIPTS / "paper_write.py",
        )
        output = proc.stdout + proc.stderr
        self.assertIn("MUTANT_IMPORTED_OK", output, output)
        self.assertNotEqual(proc.returncode, 0, output)


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
        `SPAN_NOT_IN_SOURCE`) -- 1 + 6 + 3 + 3 + 1 = 14 new codes. Moved
        from 79 to 93 in `a-diagram-that-compiles-or-says-why`: `paper_cli.py`
        starts importing `paper_latex.py` (raises none of its own -- every
        one of its refusals is reused/named by `paper_figure.py`'s own
        call sites), `paper_figure.py` (`DIAGRAM_SOURCE_ABSENT`,
        `LATEX_TOOLCHAIN_ABSENT`, `LATEX_PACKAGE_ABSENT`,
        `REPAIR_BUDGET_SPENT`, `DIAGRAM_PLOTS_DATA`, `MANIFEST_SOURCE_MISMATCH`,
        `LATEX_LOG_ABSENT`, `LATEX_OUTCOME_UNEXPLAINED` -- 8) and
        `paper_obligation.py` (`COMPONENT_MISMATCH`, `EXCLUDED_COMPONENT`,
        `SHARED_COMPONENT`, `CAPTION_INCOMPLETE`, `MANDATORY_DIAGRAM_ABSENT`
        -- 5), and `paper_contract.py`'s own `_parse_figure` adds
        `MALFORMED_FIGURE_OBLIGATION` (1) to an already-imported module --
        8 + 5 + 1 = 14 new codes. Moved from 93 to 94 in
        `the-couplings-hold-or-they-do-not`: `paper_cli.py` starts importing
        `paper_coupling_evidence.py` (`DECLARATION_RECORD_ABSENT` -- 1) and
        `paper_verify.py` (raises no `Refused` of its own), both ahead of
        `verify`'s own wiring -- the same shape `paper_region.py`/
        `paper_obligation.py` already established, forced this time by
        `ModuleCompletenessTests` rather than chosen: that test holds every
        on-disk script to being imported by `paper_cli.py` the moment it
        exists, so the import could not wait for Work Unit 3 the way
        tasks.md's own 3.7 originally phrased it. Moved from 94 to 96 in
        `a-diagram-that-compiles-or-says-why`'s own corrective amendment
        (verify FAIL, CRITICAL): `_resolve_expected_components`, a new
        helper inside `paper_cli.py` itself, raises `COMPONENTS_FACT_
        UNRESOLVED` and `COMPONENTS_FACT_NOT_A_LIST` -- reachable the
        moment `_check_obligations` calls it, no new module import needed
        since both live in the already-scanned `paper_cli.py`. Moved from
        96 to 95 in the zero-production-caller corrective: `paper_contract.
        install_header` (`HEADER_PRESENT`, `BODY_MUTATED`) is deleted --
        its one-shot migration over the ten shipped contracts already ran
        and nothing promises a "create a new section contract" workflow
        anywhere in SKILL.md, a spec, or a registered agent -- and `observe`
        is wired as `validate_observation_report`'s real caller, adding
        `OBSERVATION_REPORT_UNREADABLE` (this file's own shuttle-file read,
        the same shape `CONTRACT_UNREADABLE` already establishes). Net
        -2 + 1 = -1. `classify_guidance_child` (`paper_evidence.py`) is also
        deleted in the same corrective but raises no `Refused` of its own,
        so it moves this count by zero. Moved from 95 to 96 in the K4
        corrective (`resolve_sections_dir` never checked the resolved
        `--sections` path actually existed, so `contract`/`readiness`/
        `order`/`plan` silently read a typo'd path as a real empty corpus):
        `paper_contract.resolve_sections_dir` gains one new raise site for
        `SECTION_CONTRACTS_UNREADABLE` -- reusing, not inventing, the code
        `paper_verify.UNMEASURED_REASONS` and `paper_coupling_evidence.
        _blocks_by_fact` already carry for "the corpus itself could not be
        read", so the set gains a member without gaining a second name for
        the same condition. Moved from 96 to 97 in `the-phases-are-derived-
        not-remembered`, unit 1: `paper_graph.py` gains
        `_verify_input_partition`, called from `assemble_corpus` (an
        already-imported module), refusing `INPUT_PARTITION_ABSENT` when a
        contract's prose body is missing `### External inputs` or
        `### Internal chain` -- reachable through the whole-module scan the
        moment the new raise site lands, no new import needed. Moved from 97
        to 101 in the same change's unit 4 (`internal-chain-edges`, tasks
        4.1-4.13 / 4.8b-4.8i): `paper_graph.py` gains `_verify_internal_
        chain` (`CHAIN_ROW_UNRESOLVED`, `CHAIN_ROW_UNBACKED` -- every
        `### Internal chain` row transcribes to a real, backed `after`
        edge) and `_verify_block_subunits` (`BLOCK_SUBUNIT_UNDECLARED`,
        `UNIT_HEADING_AMBIGUOUS` -- the PROSE -> HEADER direction no
        existing check covered, the guard the block-4 split proved
        missing), both called from `assemble_corpus` -- an already-imported
        module, so all four land reachable together the moment their raise
        sites exist, measured as one +4 move rather than the tasks
        artifact's own three smaller increments forecast in isolation."""
        self.assertEqual(len(reachable_paper_refusal_codes()), 101)


class ObjectiveNorthTests(unittest.TestCase):
    """`paper_objective.OBJECTIVE_FLOW` is the north `tests/test_agents.py`
    reads to gate every paper-writing agent's frontmatter (`stage_conditions()`
    there) -- but that file only ever reads a stage's `behindWhen` to find the
    ONE stage a person's word closes (`UNMEASURABLE`). Nothing anywhere checks
    a MEASURABLE `behindWhen` -- one that names a fact a run can check, not a
    human's future call -- against what `paper_cli.py` actually ships today.
    A stage whose own verbs are already live in the CLI's parser roster,
    while its `behindWhen` still says the capability "does not exist yet", is
    exactly the drift an agent reads and then refuses to run a shipped verb
    over.

    `STAGE_VERBS` is not invented: every verb named for a stage below is
    quoted, together with the one-line help `paper_cli.py`'s own
    `build_parser()` gives it, in this same table this class's docstring and
    D3's own defect report both drew from `paper_cli.py --help`. A stage
    absent from this table is simply not covered by this guard -- it is not
    a claim that stage's own `behindWhen` is trustworthy.
    """

    #: A `behindWhen` phrase asserting the stage's capability is flatly
    #: unbuilt -- as opposed to `write`'s legitimate "not yet fed in
    #: automatically", which names a missing AUTOMATION, not a missing verb,
    #: and must never trip this pattern.
    ABSENT_CLAIM = re.compile(
        r"\bno verb\b|\bhas no\b[^.]*\btoolchain\b|\bdoes not exist yet\b",
        re.IGNORECASE,
    )

    # stage -> the paper_cli.py verb(s) whose presence in its OWN parser
    # roster falsifies a behindWhen claiming that stage's capability is
    # unbuilt. Each verb is the one paper_cli.py --help names for exactly
    # this stage's `establishes` text:
    #   cite    -> resolve ("resolve one identifier's metadata through a
    #              named connector"), bib ("refs.bib management -- never
    #              hand-typed"), validate ("the single gate: submit one
    #              judged verdict ... write on success")
    #   render  -> render ("compile one diagram id standalone ... via
    #              latexmk"), place ("place an already-measured figure's
    #              PDF")
    #   verify  -> verify ("read-only report over the couplings, citation
    #              integrity and contract currency")
    STAGE_VERBS = {
        "scaffold": ("scaffold",),
        "plan": ("plan",),
        "declare": ("declare",),
        "cite": ("resolve", "bib", "validate"),
        "write": ("write",),
        "render": ("render", "place"),
        "verify": ("verify",),
    }

    def shipped_verbs(self) -> set[str]:
        """The verb roster `paper_cli.py`'s own `build_parser()` accepts --
        the same names `--help` prints, read from the live parser rather than
        grepped, so a renamed or removed verb changes this set too."""
        parser = paper_cli.build_parser()
        for action in parser._actions:
            if isinstance(action, argparse._SubParsersAction):
                return set(action.choices.keys())
        raise AssertionError("paper_cli.py's parser declares no subcommands "
                              "-- build_parser()'s shape moved")

    def test_a_measurable_behindwhen_never_claims_a_shipped_verb_is_absent(self) -> None:
        """Cross `OBJECTIVE_FLOW` against the CLI it describes.

        For every stage this class has a verb mapping for: if its own
        `behindWhen` claims the capability does not exist (`ABSENT_CLAIM`),
        every verb `STAGE_VERBS` names for that stage must be MISSING from
        `paper_cli.py`'s actual roster -- otherwise the claim is false today,
        not merely destined to become false later.
        """
        shipped = self.shipped_verbs()
        stages = {stage["stage"]: stage["behindWhen"]
                  for stage in paper_objective.OBJECTIVE_FLOW["stages"]}
        for stage, verbs in self.STAGE_VERBS.items():
            self.assertIn(
                stage, stages,
                f"OBJECTIVE_FLOW no longer declares a {stage!r} stage -- "
                f"update STAGE_VERBS or this test, never assume it still "
                f"applies")
            when = stages[stage]
            if not self.ABSENT_CLAIM.search(when):
                continue
            shipped_for_stage = sorted(set(verbs) & shipped)
            self.assertFalse(
                shipped_for_stage,
                f"{stage!r}'s behindWhen claims its capability does not "
                f"exist ({when!r}), but paper_cli.py's own parser roster "
                f"already ships {shipped_for_stage!r} for it -- the north "
                f"is stale, not the CLI")


def _write_optional_contribution_section(sections_dir: Path, *, optional: bool) -> None:
    """One block, `res-contrib`, requiring the `contributions` fact --
    minimal enough that `check_contribution_list`'s derived block set for
    this corpus is exactly this one block, so "entirely optional-and-
    unopened" is trivially the whole set (`optional-block-semantics` spec,
    tasks.md Work Unit 3, 3.6/3.7)."""
    sections_dir.mkdir(parents=True, exist_ok=True)
    header = {
        "section": "results", "position": 1,
        "blocks": [
            {"id": "res-contrib", "requires_facts": ["contributions"],
             "requires_declarations": [], "citations": "none", "optional": optional},
        ],
    }
    text = (
        "---\n" + json.dumps(header, indent=2) + "\n---\n\nProse.\n\n"
        "### External inputs\n\nNone.\n\n### Internal chain\n\nNone.\n"
    )
    (sections_dir / "01-results.md").write_text(text, encoding="utf-8")


class OptionalVerifyTests(unittest.TestCase):
    """`optional-block-semantics` spec, `Requirement: Verify Excuses An
    Unopened Optional Block` (tasks.md, Work Unit 3, 3.5-3.7). Calls each
    check function directly with an explicit `optional_block_ids` set built
    from a real corpus read -- the wiring of that set into `run()`'s only
    real caller today (`paper_cli.cmd_verify`) is deferred: it needs
    `paper_graph.assemble_corpus`, and neither `paper_cli.py` nor
    `paper_coupling_evidence.py` is in this unit's allowed edit roots. See
    this unit's own notes for exactly why."""

    def _build(self, *, optional: bool, opened: bool):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        paper_dir = Path(tmp.name) / "paper"
        sections_dir = Path(tmp.name) / "sections"
        _write_optional_contribution_section(sections_dir, optional=optional)
        paper_scaffold.scaffold(paper_dir)
        if opened:
            paper_block.open_block(paper_dir, "res-contrib", at_end=True)
        (paper_dir / "couplings.json").write_text(
            json.dumps({"blocks": {"res-contrib": True}, "facts": {"contributions": []}}),
            encoding="utf-8",
        )
        corpus = paper_graph.assemble_corpus(sections_dir)
        optional_ids = frozenset(b.block_id for b in corpus.blocks.values() if b.optional)
        evidence = paper_coupling_evidence.gather(paper_dir, sections_dir)
        return evidence, optional_ids

    def test_unopened_optional_block_reports_unmeasured_optional_block_absent(self) -> None:
        evidence, optional_ids = self._build(optional=True, opened=False)

        entry = paper_verify.check_contribution_list(evidence, optional_block_ids=optional_ids)

        self.assertEqual(entry["verdict"], "unmeasured")
        self.assertEqual(entry["unmeasured_reason"], "OPTIONAL_BLOCK_ABSENT")

    def test_unopened_non_optional_block_never_reports_optional_block_absent(self) -> None:
        evidence, optional_ids = self._build(optional=False, opened=False)

        entry = paper_verify.check_contribution_list(evidence, optional_block_ids=optional_ids)

        self.assertNotEqual(entry["unmeasured_reason"], "OPTIONAL_BLOCK_ABSENT")

    def test_opened_optional_block_is_checked_exactly_like_a_non_optional_opened_block(self) -> None:
        optional_evidence, optional_ids = self._build(optional=True, opened=True)
        plain_evidence, plain_ids = self._build(optional=False, opened=True)

        optional_entry = paper_verify.check_contribution_list(optional_evidence, optional_block_ids=optional_ids)
        plain_entry = paper_verify.check_contribution_list(plain_evidence, optional_block_ids=plain_ids)

        self.assertNotEqual(optional_entry["unmeasured_reason"], "OPTIONAL_BLOCK_ABSENT")
        self.assertEqual(optional_entry["verdict"], plain_entry["verdict"])
        self.assertEqual(optional_entry["unmeasured_reason"], plain_entry["unmeasured_reason"])

    def test_run_default_optional_block_ids_never_changes_behavior(self) -> None:
        """`run()`'s new keyword-only parameter defaults to an empty
        `frozenset()` -- calling it exactly as every existing caller does
        today must report byte-identical results."""
        evidence, _optional_ids = self._build(optional=True, opened=False)

        report = paper_verify.run(evidence)

        by_check = {entry["check"]: entry for entry in report["checks"]}
        self.assertNotEqual(by_check["contribution-list"]["unmeasured_reason"], "OPTIONAL_BLOCK_ABSENT")


class OptionalReadinessTests(unittest.TestCase):
    """`optional-block-semantics` spec, `Requirement: Readiness Reports The
    Optional Flag` (tasks.md, Work Unit 3, 3.1/3.3) and the `not-applicable`
    status half of `Requirement: ...` D6 describes (3.2/3.4) -- the basis
    dispatch itself (`--paper`, `READINESS_BASIS_REQUIRED`) is Work Unit 6's
    job; this class proves the pure function `compute_block_readiness`/
    `compute_readiness` grew, called directly with explicit `opened`/`basis`
    values, never through an invented CLI flag."""

    def test_optional_flag_is_read_verbatim_over_the_shipped_corpus(self) -> None:
        corpus = paper_graph.assemble_corpus(SECTIONS_DIR)

        report = paper_readiness.compute_readiness(corpus, satisfied_facts=set(), satisfied_declarations=set())

        by_block = {entry["block"]: entry for entry in report}
        self.assertTrue(by_block["materials-and-methods.mm-dataset"]["optional"])
        self.assertFalse(by_block["experimental-setup.es-assessment"]["optional"])

    def test_optional_unopened_block_is_not_applicable_under_declaration_backed_basis(self) -> None:
        corpus = paper_graph.assemble_corpus(SECTIONS_DIR)
        block = corpus.blocks["materials-and-methods.mm-dataset"]

        declaration_backed = paper_readiness.compute_block_readiness(
            block, satisfied_facts=set(), satisfied_declarations=set(),
            opened=False, basis="declaration-backed",
        )
        flags_only = paper_readiness.compute_block_readiness(
            block, satisfied_facts=set(), satisfied_declarations=set(),
        )

        self.assertEqual(declaration_backed["status"], "not-applicable")
        self.assertIn(flags_only["status"], ("writable", "blocked"))
        self.assertNotEqual(flags_only["status"], "not-applicable")

    def test_optional_opened_block_is_never_not_applicable(self) -> None:
        """`not-applicable` gates on ABSENCE, never on the `optional`
        declaration alone -- the same discriminating principle
        `optional-block-semantics`'s `paper_verify` requirement states
        explicitly, proven here on the readiness side too."""
        corpus = paper_graph.assemble_corpus(SECTIONS_DIR)
        block = corpus.blocks["materials-and-methods.mm-dataset"]

        opened_and_backed = paper_readiness.compute_block_readiness(
            block, satisfied_facts=set(), satisfied_declarations=set(),
            opened=True, basis="declaration-backed",
        )

        self.assertNotEqual(opened_and_backed["status"], "not-applicable")

    def test_a_non_optional_block_is_never_not_applicable_even_when_unopened(self) -> None:
        corpus = paper_graph.assemble_corpus(SECTIONS_DIR)
        block = corpus.blocks["experimental-setup.es-assessment"]

        report = paper_readiness.compute_block_readiness(
            block, satisfied_facts=set(), satisfied_declarations=set(),
            opened=False, basis="declaration-backed",
        )

        self.assertNotEqual(report["status"], "not-applicable")


# =====================================================================
# `derive_waves` -- Work Unit 5
# =====================================================================

#: `writing-phases` spec / tasks.md Work Unit 5. Every fixture below is
#: SYNTHETIC -- never the live `sections/` tree, whose shape keeps moving
#: under later units. Mirrors `test_paper_contract.py`'s own
#: `_write_section`/`_block`/`_quote_source` shape (`### Internal chain`
#: stays "None": transcribing a chain PROSE row into a graph edge is unit
#: 4's concern, already covered there -- this unit only exercises
#: header-level `after` edges over `_build_graph`/`derive_waves`).
_WAVE_BODY = "Prose.\n\n### External inputs\n\nNone.\n\n### Internal chain\n\nNone.\n"


def _wave_section(section: str, position: int, block_id: str, *, after=None) -> dict:
    header = {
        "section": section,
        "position": position,
        "blocks": [
            {"id": block_id, "requires_facts": [], "requires_declarations": [], "citations": "none"},
        ],
    }
    if after is not None:
        header["after"] = after
    return header


def _write_wave_section(sections_dir: Path, filename: str, header: dict) -> None:
    sections_dir.mkdir(parents=True, exist_ok=True)
    text = "---\n" + json.dumps(header, indent=2) + "\n---\n\n" + _WAVE_BODY
    (sections_dir / filename).write_text(text, encoding="utf-8")


def _wave_after(target: str, source_file: str) -> dict:
    return {"target": target, "source": {"file": source_file, "quote": "Prose."}}


class WaveTests(unittest.TestCase):
    """`writing-phases` spec, `Requirement: Wave Grouping Is Frontier-
    Based` (tasks.md Work Unit 5, 5.1-5.10). `derive_waves` groups
    `derive_order`'s own graph into Kahn frontiers instead of flattening
    them -- design.md D2's five invariants, each proved independently."""

    def test_zero_edge_corpus_is_one_wave(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sections_dir = Path(tmp) / "sections"
            _write_wave_section(sections_dir, "01-a.md", _wave_section("a", 1, "only"))
            _write_wave_section(sections_dir, "02-b.md", _wave_section("b", 2, "only"))
            _write_wave_section(sections_dir, "03-c.md", _wave_section("c", 3, "only"))

            corpus = paper_graph.assemble_corpus(sections_dir)
            edges = paper_graph.collect_edges(corpus)
            waves = paper_graph.derive_waves(corpus, edges)

            self.assertEqual(len(waves), 1)
            self.assertEqual(set(waves[0]), {"a.only", "b.only", "c.only"})

    def test_a_pure_chain_produces_n_waves_matching_chain_length(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sections_dir = Path(tmp) / "sections"
            _write_wave_section(sections_dir, "01-a.md", _wave_section("a", 1, "only"))
            _write_wave_section(
                sections_dir, "02-b.md",
                _wave_section("b", 2, "only", after=[_wave_after("a", "sections/02-b.md")]),
            )
            _write_wave_section(
                sections_dir, "03-c.md",
                _wave_section("c", 3, "only", after=[_wave_after("b", "sections/03-c.md")]),
            )
            _write_wave_section(
                sections_dir, "04-d.md",
                _wave_section("d", 4, "only", after=[_wave_after("c", "sections/04-d.md")]),
            )

            corpus = paper_graph.assemble_corpus(sections_dir)
            edges = paper_graph.collect_edges(corpus)
            waves = paper_graph.derive_waves(corpus, edges)

            self.assertEqual(
                waves,
                [["a.only"], ["b.only"], ["c.only"], ["d.only"]],
            )

    def test_invariant_1_waves_partition_the_same_node_set_derive_order_returns(self) -> None:
        """Diamond fixture: a; b after a; c after a; d after b and c."""
        with tempfile.TemporaryDirectory() as tmp:
            sections_dir = Path(tmp) / "sections"
            _write_wave_section(sections_dir, "01-a.md", _wave_section("a", 1, "only"))
            _write_wave_section(
                sections_dir, "02-b.md",
                _wave_section("b", 2, "only", after=[_wave_after("a", "sections/02-b.md")]),
            )
            _write_wave_section(
                sections_dir, "03-c.md",
                _wave_section("c", 3, "only", after=[_wave_after("a", "sections/03-c.md")]),
            )
            _write_wave_section(
                sections_dir, "04-d.md",
                _wave_section("d", 4, "only", after=[
                    _wave_after("b", "sections/04-d.md"), _wave_after("c", "sections/04-d.md"),
                ]),
            )

            corpus = paper_graph.assemble_corpus(sections_dir)
            edges = paper_graph.collect_edges(corpus)
            order = paper_graph.derive_order(corpus, edges)
            waves = paper_graph.derive_waves(corpus, edges)

            from itertools import chain
            flattened_set = set(chain.from_iterable(waves))
            self.assertEqual(flattened_set, set(order))
            self.assertEqual(flattened_set, set(corpus.blocks))
            # No block omitted or duplicated across waves.
            self.assertEqual(sum(len(wave) for wave in waves), len(corpus.blocks))
            self.assertEqual(
                waves,
                [["a.only"], ["b.only", "c.only"], ["d.only"]],
            )

    def test_invariant_2_every_edge_crosses_a_wave_boundary(self) -> None:
        """Diamond fixture again, read generically: for every collected
        edge `(before, after)`, `wave_of(before) < wave_of(after)` --
        this is the exact test `_run_against_mutant` below targets."""
        with tempfile.TemporaryDirectory() as tmp:
            sections_dir = Path(tmp) / "sections"
            _write_wave_section(sections_dir, "01-a.md", _wave_section("a", 1, "only"))
            _write_wave_section(
                sections_dir, "02-b.md",
                _wave_section("b", 2, "only", after=[_wave_after("a", "sections/02-b.md")]),
            )
            _write_wave_section(
                sections_dir, "03-c.md",
                _wave_section("c", 3, "only", after=[_wave_after("a", "sections/03-c.md")]),
            )
            _write_wave_section(
                sections_dir, "04-d.md",
                _wave_section("d", 4, "only", after=[
                    _wave_after("b", "sections/04-d.md"), _wave_after("c", "sections/04-d.md"),
                ]),
            )

            corpus = paper_graph.assemble_corpus(sections_dir)
            edges = paper_graph.collect_edges(corpus)
            waves = paper_graph.derive_waves(corpus, edges)

            wave_of = {qid: index for index, wave in enumerate(waves) for qid in wave}
            for before, after, _source in edges.edges:
                self.assertLess(
                    wave_of[before], wave_of[after],
                    f"{before} (wave {wave_of[before]}) does not strictly precede "
                    f"{after} (wave {wave_of[after]})",
                )

    def test_invariant_3_wave_membership_is_independent_of_dict_iteration_order(self) -> None:
        """Waves are sorted by `_sort_key`, never by dict/filename
        iteration -- feed `collect_edges`' own edge list back in reversed
        order and confirm the waves (as sets, and as sorted lists) are
        unchanged."""
        with tempfile.TemporaryDirectory() as tmp:
            sections_dir = Path(tmp) / "sections"
            _write_wave_section(sections_dir, "01-a.md", _wave_section("a", 1, "only"))
            _write_wave_section(
                sections_dir, "02-b.md",
                _wave_section("b", 2, "only", after=[_wave_after("a", "sections/02-b.md")]),
            )
            _write_wave_section(
                sections_dir, "03-c.md",
                _wave_section("c", 3, "only", after=[_wave_after("a", "sections/03-c.md")]),
            )

            corpus = paper_graph.assemble_corpus(sections_dir)
            edges = paper_graph.collect_edges(corpus)
            waves_forward = paper_graph.derive_waves(corpus, edges)

            perturbed = paper_graph.EdgeSet(
                edges=list(reversed(edges.edges)), dangling=list(edges.dangling),
            )
            waves_perturbed = paper_graph.derive_waves(corpus, perturbed)

            self.assertEqual(waves_forward, waves_perturbed)

    def test_invariant_4_a_cycle_refuses_order_cycle_with_derive_orders_own_detail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sections_dir = Path(tmp) / "sections"
            _write_wave_section(
                sections_dir, "01-a.md",
                _wave_section("a", 1, "x", after=[_wave_after("b.y", "sections/01-a.md")]),
            )
            _write_wave_section(
                sections_dir, "02-b.md",
                _wave_section("b", 2, "y", after=[_wave_after("a.x", "sections/02-b.md")]),
            )

            corpus = paper_graph.assemble_corpus(sections_dir)
            edges = paper_graph.collect_edges(corpus)

            with self.assertRaises(Refused) as order_ctx:
                paper_graph.derive_order(corpus, edges)
            with self.assertRaises(Refused) as waves_ctx:
                paper_graph.derive_waves(corpus, edges)

            self.assertEqual(waves_ctx.exception.code, "ORDER_CYCLE")
            self.assertEqual(waves_ctx.exception.detail, order_ctx.exception.detail)
            self.assertIn("a.x", waves_ctx.exception.detail)
            self.assertIn("b.y", waves_ctx.exception.detail)

    def test_invariant_5_flattened_waves_are_not_asserted_equal_to_derive_orders_sequence(self) -> None:
        """The rejected false lock, documented as a negative test
        (design.md D2, invariant 5): `derive_order`'s min-heap can pop a
        node from a LATER frontier ahead of a still-unpopped node from an
        EARLIER one, when the later node's `_sort_key` outranks it --
        legitimate interleaving, not a bug. Fixture: `alpha1` (position 1)
        and `alpha2` (position 10) are both wave 1 (no dependencies); `beta`
        (position 2) depends only on `alpha1`. `derive_order`'s heap pops
        `alpha1`, immediately frees `beta` (position 2), and pops IT before
        `alpha2` (position 10) -- but wave-grouping keeps `alpha2` in wave 1
        (it was ready from the start) and `beta` in wave 2 (it only became
        ready once wave 1 finished), so the two orders diverge."""
        with tempfile.TemporaryDirectory() as tmp:
            sections_dir = Path(tmp) / "sections"
            _write_wave_section(sections_dir, "01-alpha1.md", _wave_section("alpha1", 1, "only"))
            _write_wave_section(
                sections_dir, "02-beta.md",
                _wave_section("beta", 2, "only", after=[_wave_after("alpha1", "sections/02-beta.md")]),
            )
            _write_wave_section(sections_dir, "10-alpha2.md", _wave_section("alpha2", 10, "only"))

            corpus = paper_graph.assemble_corpus(sections_dir)
            edges = paper_graph.collect_edges(corpus)
            order = paper_graph.derive_order(corpus, edges)
            waves = paper_graph.derive_waves(corpus, edges)

            from itertools import chain
            flattened = list(chain.from_iterable(waves))

            # The false lock this test documents as REJECTED:
            self.assertNotEqual(
                flattened, order,
                "flattened waves equalled derive_order's own sequence on a "
                "genuinely multi-frontier fixture -- this fixture no longer "
                "demonstrates legitimate interleaving; strengthen it rather "
                "than assert sequence equality (design.md D2, invariant 5)",
            )
            # What IS true instead: same node set, waves respect dependency order.
            self.assertEqual(set(flattened), set(order))
            self.assertEqual(waves, [["alpha1.only", "alpha2.only"], ["beta.only"]])
            self.assertEqual(order, ["alpha1.only", "beta.only", "alpha2.only"])

    def test_the_real_shipped_corpus_decomposes_with_the_preamble_strictly_after_the_proposal(self) -> None:
        """Regression, not a fixture: `materials-and-methods.mm-proposal`
        must land strictly earlier than `materials-and-methods.mm-preamble`
        -- the single clearest evidence this change works (the preamble no
        longer shares a wave with the block it must name). Wave COUNT and
        exact per-wave sizes are measured, reported below, and deliberately
        NOT hard-asserted here: later units still change this corpus."""
        corpus = paper_graph.assemble_corpus(SECTIONS_DIR)
        edges = paper_graph.collect_edges(corpus)
        order = paper_graph.derive_order(corpus, edges)
        waves = paper_graph.derive_waves(corpus, edges)

        from itertools import chain
        flattened_set = set(chain.from_iterable(waves))
        self.assertEqual(flattened_set, set(order))
        self.assertEqual(flattened_set, set(corpus.blocks))
        self.assertEqual(sum(len(wave) for wave in waves), len(corpus.blocks))

        wave_of = {qid: index for index, wave in enumerate(waves) for qid in wave}
        for before, after, _source in edges.edges:
            self.assertLess(wave_of[before], wave_of[after])

        self.assertLess(
            wave_of["materials-and-methods.mm-proposal"],
            wave_of["materials-and-methods.mm-preamble"],
        )


class WaveMutationProofTests(unittest.TestCase):
    """tasks.md 5.6 / design.md's own mutation table, item 4: `derive_waves`
    appending a newly-ready successor to the CURRENT wave instead of the
    NEXT one must fail `WaveTests.test_invariant_2_every_edge_crosses_a_
    wave_boundary` -- a passing assertion beside an unexercised guard is
    not a mutation that ran."""

    def test_mutation_appending_to_the_current_wave_fails_the_boundary_invariant(self) -> None:
        proc = _run_against_mutant(
            "                if remaining_indegree[successor] == 0:\n"
            "                    next_frontier.append(successor)",
            "                if remaining_indegree[successor] == 0:\n"
            "                    waves[-1].append(successor)",
            "tests.test_paper_writing.WaveTests"
            ".test_invariant_2_every_edge_crosses_a_wave_boundary",
            source_path=SKILL_SCRIPTS / "paper_graph.py",
        )
        output = proc.stdout + proc.stderr
        self.assertIn("MUTANT_IMPORTED_OK", output, output)
        self.assertNotEqual(proc.returncode, 0, output)


if __name__ == "__main__":
    unittest.main()
