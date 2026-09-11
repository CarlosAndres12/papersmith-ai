"""The stdout characterization seal for `proposal-implementation`'s CLI.

Built across `openspec/changes/the-seal-before-the-cut/`: proposal.md, design.md,
tasks.md. Proves preservation across the later profile-driven extraction
(`the-engine-leaves-its-skill` and its successors) by capturing byte-exact stdout
and exit status for all 20 subcommands against a fixed corpus, and hosts the two
sanctioned behaviour changes (F3, F5) under a declared-delta discipline.

This module is built incrementally, phase by phase, per tasks.md:

- Phase 2 (this section): F3's two permanent anchor/behaviour tests.
- Phase 4: threat-matrix RED tests for the harness itself.
- Phase 5: normalizer mutation proofs (reach + guard pairs).
- Phase 7: the comparison suite, coverage tests, membership tests.
- Phase 8: F5's identity tests and the zero-delta re-comparison.

Governs the seal only, not the CLI's existing runtime behavior — this file adds
no assertion about the CLI's non-F3/F5 behaviour that isn't already covered
elsewhere.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

FORGE = Path(__file__).resolve().parents[1]
CLI = FORGE / ".claude/skills/proposal-implementation/scripts/implementation_cli.py"
sys.path.insert(0, str(CLI.parent))
import implementation_cli as impl  # noqa: E402  (path set above)


class F3AnchorTests(unittest.TestCase):
    """F3 — the five `REVISION_UNREADABLE` refusal sites must read the
    directory the code actually consults (`proposals_root()`), never spell a
    hardcoded `FORGE_ROOT / 'proposals'` the `IMPLEMENTATION_PROPOSALS`
    override silently bypasses (design.md D7, f3-message-delta.md).

    **Anchor discipline** (recorded scar: an anchor that matched is not a
    mutation that ran; `sd -s` can exit 0 and change nothing). This reads the
    SOURCE directly, not a byproduct of the CLI's own behaviour.
    """

    def test_no_refusal_names_a_directory_the_code_never_read(self):
        source = CLI.read_text(encoding="utf-8")
        self.assertEqual(source.count("FORGE_ROOT / 'proposals'"), 0)
        self.assertEqual(source.count("{proposals_root()}"), 5)

    def _box(self):
        box = (FORGE / "implementations"
               / f"_seal_f3_override_{os.getpid()}_{id(self)}")
        self.addCleanup(shutil.rmtree, box, ignore_errors=True)
        box.mkdir(parents=True)
        subprocess.run(["git", "init", "-q", str(box)], check=True,
                       capture_output=True)
        return box

    def test_a_refusal_under_an_override_names_the_override(self):
        """The rendering the message-count assertion above cannot see: run
        `admit` with `IMPLEMENTATION_PROPOSALS` pointed at an empty
        directory and an unreadable `--revision`. The refusal must name
        THAT directory, never `FORGE_ROOT / "proposals"` — the exact bug
        F3 fixes. `proposals_root()` renders byte-identically to the old
        literal only when the override is unset; this is the one case
        where it must not."""
        override = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, override, ignore_errors=True)
        box = self._box()
        env = dict(os.environ)
        env["IMPLEMENTATION_PROPOSALS"] = str(override)
        proc = subprocess.run(
            [sys.executable, str(CLI), "admit", "--target", str(box),
             "--name", "Method", "--revision", "does-not-exist.md"],
            capture_output=True, text=True, cwd=FORGE, env=env)
        self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["code"], "REVISION_UNREADABLE")
        self.assertIn(str(override), payload["detail"])
        self.assertNotIn(str(FORGE / "proposals"), payload["detail"])


if __name__ == "__main__":
    unittest.main()
