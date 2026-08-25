"""Ingestion source classification and index/bridge behavior."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from papersmith.core import ingest as ingest_module
from papersmith.core import init as init_module
from papersmith.errors import UserError


ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize(
    ("source", "kind", "url", "slug"),
    [
        (
            "https://arxiv.org/abs/2401.12345",
            "url",
            "https://arxiv.org/pdf/2401.12345.pdf",
            "2401.12345",
        ),
        (
            "https://arxiv.org/pdf/2401.12345.pdf",
            "url",
            "https://arxiv.org/pdf/2401.12345.pdf",
            "2401.12345",
        ),
        (
            "https://example.org/papers/method.pdf?download=1",
            "url",
            "https://example.org/papers/method.pdf?download=1",
            "method",
        ),
        (
            "https://openreview.net/forum?id=abc123",
            "openreview",
            "https://openreview.net/forum?id=abc123",
            "abc123",
        ),
    ],
)
def test_classify_supported_sources(source: str, kind: str, url: str, slug: str) -> None:
    result = ingest_module.classify_source(source)
    assert result == {"kind": kind, "url": url, "slug": slug}


def test_classify_local_pdf(tmp_path: Path) -> None:
    path = tmp_path / "my paper.pdf"
    path.write_bytes(b"pdf")
    assert ingest_module.classify_source(str(path)) == {
        "kind": "file", "url": "", "slug": "my-paper"
    }


def test_classify_rejects_unknown_sources() -> None:
    with pytest.raises(UserError, match="must be a PDF path"):
        ingest_module.classify_source("notes.txt")
    with pytest.raises(UserError, match="must point to a PDF"):
        ingest_module.classify_source("https://example.org/landing-page")


def test_refresh_index_scans_ingested_markdown(tmp_path: Path) -> None:
    workspace = tmp_path / "paper"
    reference = workspace / "guidance/reference-papers/method"
    reference.mkdir(parents=True)
    (reference / "method.md").write_text("# A Reproducible Method\n\nBody.\n", encoding="utf-8")
    (reference / "figure.png").write_bytes(b"image")
    (workspace / "guidance/reference-papers/README.md").parent.mkdir(parents=True, exist_ok=True)
    (workspace / "guidance/reference-papers/README.md").write_text("# References", encoding="utf-8")

    index = ingest_module.refresh_index(workspace)

    assert len(index["entries"]) == 1
    entry = index["entries"][0]
    assert entry["id"] == "method"
    assert entry["title"] == "A Reproducible Method"
    assert entry["path"] == "guidance/reference-papers/method/method.md"
    assert (workspace / "guidance/reference-papers/index.json").is_file()


def test_ingest_delegates_pdf_and_refreshes_index(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    workspace = tmp_path / "paper"
    init_module.initialize(workspace, run_npm=False)
    source = tmp_path / "source.pdf"
    source.write_bytes(b"pdf")
    captured: dict[str, object] = {}

    def fake_run(root, script, args, **kwargs):
        captured["root"] = root
        captured["script"] = script
        captured["args"] = list(args)
        output = workspace / "guidance/reference-papers/source/source.md"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text("# Extracted Source\n", encoding="utf-8")
        return subprocess.CompletedProcess([], 0, "ingested\n", "")

    monkeypatch.setattr(ingest_module, "run_script", fake_run)
    result = ingest_module.ingest(str(source), workspace, ocr=True)

    assert captured["script"] == "skills/paper-ingestion/scripts/extract_pdf.py"
    assert captured["args"] == [
        "guidance/reference-papers/source.pdf", "--mode", "balanced"
    ]
    assert result["index"]["entries"][0]["title"] == "Extracted Source"


def test_extract_pdf_accepts_mode_override_and_rejects_invalid_mode() -> None:
    script = ROOT / "skills/paper-ingestion/scripts/extract_pdf.py"
    valid = subprocess.run(
        [sys.executable, str(script), "--list", "--mode", "balanced"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert valid.returncode == 0, valid.stderr
    invalid = subprocess.run(
        [sys.executable, str(script), "--list", "--mode", "invalid"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert invalid.returncode == 2
