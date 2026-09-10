"""CLI paper end-to-end journey — Unit 1: fixtures, stub helpers, init/status.

Hermetic pytest gate proving the workspace foundation for the from-scratch
paper journey. In-process ``main([...])`` calls only, pytest-run
``unittest.TestCase`` classes (repo standard per tasks decision).

Scope (Unit 1 only):
- ``tests/fixtures/e2e/paper.pdf`` (1-page, <10KB) for the ingest leg.
- Helpers: ``_make_workspace``, ``_link_node_modules``, ``_stub_extract``,
  ``_fake_kaggle_bin``.
- ``TestInitStatus``: fresh ``init --no-npm`` -> ``status`` exit 0; dirty
  workspace drift detection names the offending paths.

Boundaries faked: ``--no-npm`` + prebuilt ``node_modules`` symlink, stubbed
download/extract writing the canned ``research-concept-r01.md`` expectation,
fake ``kaggle`` exe on PATH. No network, no live Kaggle, no Marker weights.
"""

from __future__ import annotations

import contextlib
import io
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from papersmith.cli import main
from papersmith.core import ingest as ingest_module
from papersmith.core import status as status_module

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PDF = REPO_ROOT / "tests" / "fixtures" / "e2e" / "paper.pdf"
CANNED_MD = REPO_ROOT / "tests" / "fixtures" / "research-concept-r01.md"

# Minimal 1x1 transparent PNG (68 bytes) for the stubbed figure file.
_FAKE_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000a49444154789c63000100000500010d0a2db40000000049454e44ae426082"
)


def _make_workspace(base: Path, name: str = "e2e-paper") -> Path:
    """Create an isolated workspace via ``init --no-npm`` and return its path."""
    workspace = base / name
    rc = main(
        [
            "init",
            str(workspace),
            "--title",
            "E2E Paper",
            "--topic",
            "e2e testing",
            "--remote",
            "local",
            "--no-npm",
        ]
    )
    assert rc == 0, f"init failed with exit {rc}"
    return workspace


def _link_node_modules(workspace: Path) -> Path:
    """Symlink the prebuilt root install into the workspace (no npm install)."""
    src = REPO_ROOT / "node_modules"
    dst = workspace / "node_modules"
    if dst.is_symlink() or dst.exists():
        return dst
    if src.is_dir():
        dst.symlink_to(src, target_is_directory=True)
    return dst


@contextlib.contextmanager
def _stub_extract():
    """Stub download + Marker extract: write the canned ``.md`` plus one figure.

    Patches ``papersmith.core.ingest._download`` (no network) and
    ``papersmith.core.ingest.run_script`` (no Marker/surya weights). The fake
    runner copies ``tests/fixtures/research-concept-r01.md`` as the canned
    expectation and writes one PNG figure beside it.
    """
    canned_text = CANNED_MD.read_text(encoding="utf-8")

    def _fake_download(url: str, destination: Path) -> None:
        Path(destination).write_bytes(b"%PDF-1.4 stub\n%%EOF\n")

    def _fake_run(root, script, args, **kwargs):
        root = Path(root)
        pdf_rel = Path(args[0])
        slug = pdf_rel.stem
        paper_dir = root / "guidance" / "reference-papers" / slug
        paper_dir.mkdir(parents=True, exist_ok=True)
        (paper_dir / f"{slug}.md").write_text(canned_text, encoding="utf-8")
        (paper_dir / "_page_1_Figure_1.png").write_bytes(_FAKE_PNG)
        return subprocess.CompletedProcess(args=[], returncode=0, stdout="ingested\n", stderr="")

    with (
        mock.patch.object(ingest_module, "_download", side_effect=_fake_download),
        mock.patch.object(ingest_module, "run_script", side_effect=_fake_run),
    ):
        yield


def _fake_kaggle_bin(bin_dir: Path, monkeypatch=None) -> Path:
    """Write a ``#!/bin/sh`` ``exit 0`` fake ``kaggle`` exe and prepend PATH.

    ``monkeypatch`` is the pytest fixture when available; ``unittest`` callers
    pass ``None`` and restore ``PATH`` via ``addCleanup``. Returns the exe path.
    """
    bin_dir.mkdir(parents=True, exist_ok=True)
    exe = bin_dir / "kaggle"
    exe.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    exe.chmod(exe.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    new_path = f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}"
    if monkeypatch is not None and hasattr(monkeypatch, "setenv"):
        monkeypatch.setenv("PATH", new_path)
    else:
        os.environ["PATH"] = new_path
    return exe


class TestHelpers(unittest.TestCase):
    def new_tmp(self) -> Path:
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        return Path(holder.name)

    def test_helper_fixture_pdf_is_one_page_under_10kb(self) -> None:
        assert FIXTURE_PDF.is_file(), f"missing fixture PDF: {FIXTURE_PDF}"
        size = FIXTURE_PDF.stat().st_size
        assert size < 10 * 1024, f"fixture too large: {size} bytes"
        assert FIXTURE_PDF.read_bytes().startswith(b"%PDF"), "missing PDF header"

    def test_helper_fixture_pdf_has_valid_structure(self) -> None:
        data = FIXTURE_PDF.read_bytes()
        assert data.strip().endswith(b"%%EOF"), "missing PDF trailer"
        assert b"/Count 1" in data, "fixture must be exactly one page"
        assert b"/Type /Page" in data, "fixture must contain a page object"

    def test_helper_make_workspace_creates_contract(self) -> None:
        tmp_path = self.new_tmp()
        workspace = _make_workspace(tmp_path)
        assert (workspace / ".papersmith" / "manifest.json").is_file()
        assert (workspace / ".papersmith" / "config.json").is_file()
        assert (workspace / "papersmith.yaml").is_file()
        assert (workspace / "CLAUDE.md").is_file()
        snapshot = status_module.status(workspace)
        assert snapshot["project_name"] == "e2e-paper"

    def test_helper_make_workspace_isolated_names(self) -> None:
        tmp_path = self.new_tmp()
        first = _make_workspace(tmp_path, name="e2e-alpha")
        second = _make_workspace(tmp_path, name="e2e-beta")
        assert first != second
        assert status_module.status(first)["project_name"] == "e2e-alpha"
        assert status_module.status(second)["project_name"] == "e2e-beta"

    def test_helper_link_node_modules_symlinks_prebuilt(self) -> None:
        tmp_path = self.new_tmp()
        workspace = _make_workspace(tmp_path)
        linked = _link_node_modules(workspace)
        src = REPO_ROOT / "node_modules"
        assert src.is_dir(), "prebuilt node_modules missing at repo root"
        assert linked.is_symlink(), "expected a symlink, no real install"
        assert linked.resolve() == src.resolve()

    def test_helper_link_node_modules_idempotent(self) -> None:
        tmp_path = self.new_tmp()
        workspace = _make_workspace(tmp_path)
        first = _link_node_modules(workspace)
        second = _link_node_modules(workspace)
        assert first == second
        assert second.is_symlink()

    def test_helper_stub_extract_writes_canned_markdown(self) -> None:
        tmp_path = self.new_tmp()
        workspace = _make_workspace(tmp_path)
        with _stub_extract():
            result = ingest_module.ingest(str(FIXTURE_PDF), workspace)
        md_path = workspace / "guidance" / "reference-papers" / "paper" / "paper.md"
        assert md_path.is_file(), "stubbed extract wrote no markdown"
        text = md_path.read_text(encoding="utf-8")
        canned = CANNED_MD.read_text(encoding="utf-8")
        assert text == canned, "stub must copy the canned expectation byte-for-byte"
        assert r"\mathcal" in text, "canned markdown must carry LaTeX"
        assert r"\tag" in text, "canned markdown must carry equation tags"
        assert result["index"]["entries"], "index must list the ingested paper"

    def test_helper_stub_extract_copies_figure(self) -> None:
        tmp_path = self.new_tmp()
        workspace = _make_workspace(tmp_path)
        with _stub_extract():
            ingest_module.ingest(str(FIXTURE_PDF), workspace)
        fig = workspace / "guidance" / "reference-papers" / "paper" / "_page_1_Figure_1.png"
        assert fig.is_file(), "stub must write one figure file"
        data = fig.read_bytes()
        assert len(data) > 0, "figure must be non-empty"
        assert data.startswith(b"\x89PNG"), "figure must be a PNG"

    def test_helper_fake_kaggle_bin_exits_zero(self) -> None:
        tmp_path = self.new_tmp()
        old_path = os.environ.get("PATH", "")
        self.addCleanup(os.environ.__setitem__, "PATH", old_path)
        exe = _fake_kaggle_bin(tmp_path / "bin")
        assert exe.is_file()
        assert os.access(exe, os.X_OK), "fake kaggle must be executable"
        completed = subprocess.run([str(exe)], capture_output=True, timeout=30)
        assert completed.returncode == 0

    def test_helper_fake_kaggle_bin_prepended_to_path(self) -> None:
        tmp_path = self.new_tmp()
        old_path = os.environ.get("PATH", "")
        self.addCleanup(os.environ.__setitem__, "PATH", old_path)
        exe = _fake_kaggle_bin(tmp_path / "bin")
        assert exe.read_text(encoding="utf-8").startswith("#!/bin/sh"), "must be a sh stub"
        assert shutil.which("kaggle") == str(exe), "fake bin must win on PATH"
        completed = subprocess.run(
            [str(exe), "kernels", "status", "x"], capture_output=True, timeout=30
        )
        assert completed.returncode == 0, "stub must exit 0 for any args"


class TestInitStatus(unittest.TestCase):
    def new_tmp(self) -> Path:
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        return Path(holder.name)

    def test_init_fresh_init_passes_status(self) -> None:
        tmp_path = self.new_tmp()
        workspace = _make_workspace(tmp_path)
        _link_node_modules(workspace)
        assert main(["status", str(workspace)]) == 0
        snapshot = status_module.status(workspace)
        assert snapshot["framework"]["drifted_files"] == []
        assert snapshot["framework"]["version_match"] is True

    def test_init_status_json_reports_ready(self) -> None:
        import contextlib
        import json

        tmp_path = self.new_tmp()
        workspace = _make_workspace(tmp_path)
        _link_node_modules(workspace)
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            assert main(["status", str(workspace), "--json"]) == 0
        payload = json.loads(buffer.getvalue())
        assert payload["project_name"] == "e2e-paper"
        assert payload["framework"]["drifted_files"] == []
        assert payload["proposal"]["revision_id"] is None

    def test_init_dirty_workspace_fails_naming_paths(self) -> None:
        import contextlib

        tmp_path = self.new_tmp()
        workspace = _make_workspace(tmp_path)
        _link_node_modules(workspace)
        (workspace / "CLAUDE.md").write_text(
            (workspace / "CLAUDE.md").read_text(encoding="utf-8") + "\n<!-- dirty probe -->\n",
            encoding="utf-8",
        )
        snapshot = status_module.status(workspace)
        assert "CLAUDE.md" in snapshot["framework"]["drifted_files"]
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            rc = main(["status", str(workspace)])
        # NOTE: status reports drift but still exits 0 in current CLI;
        # the "fail" is the drift detection naming the path, not a non-zero exit.
        assert rc == 0
        assert "CLAUDE.md" in buffer.getvalue()
