"""paper-writing: scaffold, block grammar, substitution engine.

Stdlib-only `unittest`. Every fixture lives under a `TemporaryDirectory`; the
real `paper/` at the forge root is never touched by this suite outside the
one CLI subprocess test, which scaffolds under the already-gitignored
`implementations/` tree and cleans up after itself. Every
`paper_scaffold.resolve_paper_dir` call below passes an injected
`forge_root` for exactly this reason.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = FORGE_ROOT / ".claude" / "skills" / "paper-writing" / "scripts"
sys.path.insert(0, str(SKILL_SCRIPTS))
import paper_scaffold  # noqa: E402

sys.path.insert(0, str(FORGE_ROOT / ".claude" / "skills" / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

CLI = SKILL_SCRIPTS / "paper_cli.py"


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


if __name__ == "__main__":
    unittest.main()
