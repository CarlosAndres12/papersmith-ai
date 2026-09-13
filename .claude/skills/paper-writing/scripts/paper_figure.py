"""paper_figure: diagram source/manifest layout, the two-way manifest
cross-check, the data-figure boundary's source-side stop (stop A), and the
per-figure-id repair-budget ledger.

Owns no subprocess of its own — that is `paper_latex.py`'s exclusive
privilege (design.md, "three skill-local modules, none of them in
`_core/`"); this module calls `paper_latex.compile()` and interprets its
`CompileResult`.

An ordinary repairable compile failure (exit != 0, a diagnostic explains
it, the package is not simply absent, and the budget is not yet exhausted)
is reported as a successful CLI call (`"status": "ok"`) carrying
`"verdict": "failure"` and the diagnostics — spending a budget attempt is
the ordinary cost of the authoring loop, not a guard blocking anything.
Only these become `Refused` (exit 2): the toolchain/log/package absences,
`DIAGRAM_PLOTS_DATA`, `MANIFEST_SOURCE_MISMATCH`, `LATEX_OUTCOME_UNEXPLAINED`,
and `REPAIR_BUDGET_SPENT` once the fifth repairable attempt is requested.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_latex  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

#: Four repairable `latexmk` compiles per figure id (proposal.md, "A repair
#: budget of four compiles per figure id"). Keyed to the id ALONE — every
#: attempt for this id counts against the same ledger regardless of the
#: source digest at the time, which is the whole point of
#: `REPAIR_BUDGET_SPENT`'s "editing the source between attempts MUST NOT
#: reset the count" (`authored-diagram` spec). The operator's bound, never
#: an agent's to widen.
REPAIR_BUDGET = 4

#: Stop A, source side of the data-figure boundary (design.md, "the
#: data-figure boundary is two stops, and neither subsumes the other").
_PLOTTING_PACKAGES = ("pgfplots", "pgfplotstable")
_USEPACKAGE_RE = re.compile(r"\\usepackage(?:\[[^\]]*\])?\{([^}]*)\}")
_AXIS_ENV_RE = re.compile(r"\\begin\{axis\}")
_EXTERNAL_READ_PATTERNS: tuple[re.Pattern, ...] = (
    re.compile(r"\\addplot\s+table"),
    re.compile(r"\\pgfplotstableread"),
    re.compile(r"\\csvreader"),
)
_INPUT_ESCAPE_RE = re.compile(r"\\(?:input|include)\{([^}]+)\}")
_COORDINATES_BLOCK_RE = re.compile(r"coordinates\s*\{([^}]*)\}", re.DOTALL)
_NUMERIC_PAIR_RE = re.compile(r"\(\s*-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?\s*\)")
#: More than this many numeric pairs in one `coordinates{...}` block reads
#: as an embedded data series rather than a small illustrative sketch (a
#: handful of points placing boxes on a canvas is normal TikZ; a series
#: this long is a plotted result).
_COORDINATE_SERIES_THRESHOLD = 4

#: A node this manifest/source cross-check recognizes: a comment marker
#: `% node: <label>` the diagram author places beside each declared
#: component. This skill parses no real TikZ grammar — the marker is this
#: skill's own, deliberately simple grammar for "what this source declares
#: as a component," analogous to how `paper_block.py` never parses LaTeX
#: either and instead reads its own marker comments.
_NODE_MARKER_RE = re.compile(r"%\s*node:\s*(\S+)")


def figure_paths(paper_dir: Path, figure_id: str) -> dict:
    """Every path one figure id resolves to (`authored-diagram` spec,
    `Requirement: Source Layout`)."""
    figures_dir = paper_dir / "Figures"
    scratch_dir = paper_dir / ".paper-writing" / "figures" / figure_id
    return {
        "tex": figures_dir / f"{figure_id}.tex",
        "manifest": figures_dir / f"{figure_id}.diagram.json",
        "pdf": figures_dir / f"{figure_id}.pdf",
        "scratch": scratch_dir,
        "ledger": scratch_dir / "ledger.json",
    }


def read_manifest(paths: dict) -> dict:
    """Refuses `DIAGRAM_SOURCE_ABSENT` when `<id>.diagram.json` names no
    matching `<id>.tex` (`authored-diagram` spec, `Scenario: Manifest
    without source refuses`)."""
    if not paths["tex"].is_file():
        raise Refused("DIAGRAM_SOURCE_ABSENT", f"{paths['tex']} does not exist for this manifest")
    return json.loads(paths["manifest"].read_text(encoding="utf-8"))


def _tex_nodes(tex_text: str) -> set:
    return set(_NODE_MARKER_RE.findall(tex_text))


def cross_check_manifest(manifest: dict, tex_text: str) -> None:
    """Both directions (`diagram-obligation` spec, `Requirement: Manifest
    Crossed With Source, Both Directions`): a declared label absent from
    the source, or a node in the source absent from the manifest, refuses
    `MANIFEST_SOURCE_MISMATCH` naming the label(s) and the direction."""
    declared = set(manifest.get("components", []))
    present = _tex_nodes(tex_text)
    missing_in_source = sorted(declared - present)
    if missing_in_source:
        raise Refused(
            "MANIFEST_SOURCE_MISMATCH",
            f"declared in the manifest, absent from the source: {missing_in_source}",
        )
    missing_in_manifest = sorted(present - declared)
    if missing_in_manifest:
        raise Refused(
            "MANIFEST_SOURCE_MISMATCH",
            f"present in the source, undeclared in the manifest: {missing_in_manifest}",
        )


def _resolves_inside_figures(target: str) -> bool:
    if target.startswith("/"):
        return False
    return ".." not in Path(target).parts


def scan_data_boundary(tex_text: str) -> None:
    """Stop A: refuses `DIAGRAM_PLOTS_DATA` on a plotting package, a
    `\\begin{axis}`, an external table read, an `\\input`/`\\include`
    escaping `paper/Figures/`, or an embedded coordinate series over the
    threshold (`authored-diagram` spec, `Requirement: Data-Figure
    Boundary`)."""
    for usepackage_match in _USEPACKAGE_RE.finditer(tex_text):
        packages = {name.strip() for name in usepackage_match.group(1).split(",")}
        for plotting_package in _PLOTTING_PACKAGES:
            if plotting_package in packages:
                raise Refused("DIAGRAM_PLOTS_DATA", f"loads plotting package {plotting_package!r}")
    if _AXIS_ENV_RE.search(tex_text):
        raise Refused("DIAGRAM_PLOTS_DATA", "declares a pgfplots \\begin{axis} environment")
    for pattern in _EXTERNAL_READ_PATTERNS:
        if pattern.search(tex_text):
            raise Refused("DIAGRAM_PLOTS_DATA", f"reads an external table via {pattern.pattern!r}")
    for input_match in _INPUT_ESCAPE_RE.finditer(tex_text):
        target = input_match.group(1)
        if not _resolves_inside_figures(target):
            raise Refused(
                "DIAGRAM_PLOTS_DATA", f"\\input/\\include escapes paper/Figures/: {target!r}",
            )
    for series_match in _COORDINATES_BLOCK_RE.finditer(tex_text):
        pairs = _NUMERIC_PAIR_RE.findall(series_match.group(1))
        if len(pairs) > _COORDINATE_SERIES_THRESHOLD:
            raise Refused(
                "DIAGRAM_PLOTS_DATA", f"embeds a {len(pairs)}-point coordinate series",
            )


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _atomic_replace(path: Path, data: bytes) -> None:
    directory = path.parent
    fd, tmp_name = tempfile.mkstemp(dir=str(directory), prefix=path.name + ".")
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def _read_ledger(ledger_path: Path) -> dict:
    if not ledger_path.is_file():
        return {"attempts": []}
    return json.loads(ledger_path.read_text(encoding="utf-8"))


def _write_ledger(ledger_path: Path, ledger: dict) -> None:
    ledger_path.parent.mkdir(parents=True, exist_ok=True)
    _atomic_replace(ledger_path, json.dumps(ledger, indent=2).encode("utf-8"))


def acknowledge_reset(paths: dict, figure_id: str) -> dict:
    """The only exit from a spent ledger: an explicit operator
    acknowledgement (`authored-diagram` spec, `Scenario: Acknowledgement
    clears the ledger`). Deleting the ledger file IS the acknowledgement,
    made explicit rather than pretended-secure (design.md, "nothing under
    `paper/` is tamper-proof")."""
    if paths["ledger"].is_file():
        paths["ledger"].unlink()
    return {"figureId": figure_id, "ledgerReset": True}


def _package_diagnostic(diagnostics: tuple) -> object | None:
    for diagnostic in diagnostics:
        if diagnostic.kind == "package":
            return diagnostic
    return None


def render(paper_dir: Path, figure_id: str, *, path: str | None = None) -> dict:
    """The whole `render` pipeline for one figure id: layout resolution,
    the manifest cross-check, stop A, the compile, and the budget ledger.

    Refuses (never spends budget): `DIAGRAM_SOURCE_ABSENT`,
    `MANIFEST_SOURCE_MISMATCH`, `DIAGRAM_PLOTS_DATA` (all pre-compile),
    `LATEX_TOOLCHAIN_ABSENT`, `LATEX_LOG_ABSENT`, `LATEX_OUTCOME_UNEXPLAINED`,
    `LATEX_PACKAGE_ABSENT` (a missing `.sty` "cannot be fixed by redrawing",
    `authored-diagram` spec, `Requirement: Package Absence Spends Nothing`).
    Refuses, spending the fifth attempt: `REPAIR_BUDGET_SPENT`. Returns a
    plain dict (never `Refused`) for a clean success OR an ordinary
    repairable failure within budget — the latter IS the loop's ordinary
    cost, not a guard blocking anything (module docstring).
    """
    paths = figure_paths(paper_dir, figure_id)
    manifest = read_manifest(paths)
    tex_text = paths["tex"].read_text(encoding="utf-8")
    cross_check_manifest(manifest, tex_text)
    scan_data_boundary(tex_text)

    source_digest = _digest(tex_text)
    ledger = _read_ledger(paths["ledger"])
    attempts = list(ledger.get("attempts", []))

    # The budget is checked BEFORE spawning another compile -- a spent
    # ledger refuses without wasting a fifth `latexmk` call, which is the
    # whole point of a REPAIR budget (`authored-diagram` spec, `Requirement:
    # Repair Budget Ledger`). Keyed to the id alone: `attempts` above is
    # NEVER filtered by `source_digest`, so editing the source between
    # attempts cannot reset the count (`DiagramMutationProofTests`,
    # "budget keyed to (id, sourceDigest) instead of id").
    if len(attempts) >= REPAIR_BUDGET:
        raise Refused(
            "REPAIR_BUDGET_SPENT",
            "budget of "
            f"{REPAIR_BUDGET} compiles spent for {figure_id!r}; "
            f"diagnostics={[a['diagnostics'] for a in attempts]} "
            f"digests={[a['sourceDigest'] for a in attempts]}",
        )

    result = paper_latex.compile(paths["tex"].parent, figure_id, paths["scratch"], path=path)

    if result.verdict == "unexplained":
        raise Refused(
            "LATEX_OUTCOME_UNEXPLAINED",
            f"exit={result.exit_code} pdfWritten={result.pdf_written} "
            f"diagnostics={len(result.diagnostics)} unrecognizedLines={result.unrecognized_lines} "
            f"log={result.log_path}",
        )

    if result.verdict == "success":
        pdf_bytes = (paths["scratch"] / f"{figure_id}.pdf").read_bytes()
        paths["pdf"].parent.mkdir(parents=True, exist_ok=True)
        paths["pdf"].write_bytes(pdf_bytes)
        return {
            "figureId": figure_id, "pdf": str(paths["pdf"]), "verdict": "success",
            "ledgerCreated": bool(attempts), "attemptsUsed": len(attempts),
        }

    # result.verdict == "failure": a repairable outcome, or a package
    # absence that spends nothing.
    package_diag = _package_diagnostic(result.diagnostics)
    if package_diag is not None:
        raise Refused(
            "LATEX_PACKAGE_ABSENT",
            f"{package_diag.message}; the budget is unchanged at {len(attempts)}/{REPAIR_BUDGET}",
        )

    attempts.append({
        "sourceDigest": source_digest,
        "diagnostics": [d.message for d in result.diagnostics],
        "at": datetime.now(timezone.utc).isoformat(),
    })
    _write_ledger(paths["ledger"], {"attempts": attempts})
    return {
        "figureId": figure_id, "verdict": "failure", "attemptsUsed": len(attempts),
        "budgetRemaining": REPAIR_BUDGET - len(attempts),
        "diagnostics": [d.message for d in result.diagnostics],
    }


def place_figure(paper_dir: Path, figure_id: str, pdf_source: Path, provenance_source: Path) -> dict:
    """Placing a measured figure — compiles nothing, requires provenance
    naming the run that produced it (`authored-diagram` spec, `Requirement:
    Data-Figure Boundary`: "Placing a measured figure MUST use a separate
    verb that compiles nothing and requires provenance naming the run that
    produced it"). Entirely outside the compile path: no `latexmk` call, no
    ledger, no stop-A scan — the diagram-authoring loop and the
    measured-figure path never share a code path (proposal.md's own
    "Two independent stops" risk mitigation).

    Reuses `DIAGRAM_SOURCE_ABSENT` for a missing `--pdf`/`--provenance`
    source or a provenance record that names no run: the same code already
    means "the named diagram artifact this call needs is absent," and this
    is the placement path's own instance of exactly that condition — never
    a second code for one condition (design.md's own convention, `Refusal
    codes and their classification`).
    """
    if not pdf_source.is_file():
        raise Refused("DIAGRAM_SOURCE_ABSENT", f"{pdf_source} does not exist")
    if not provenance_source.is_file():
        raise Refused("DIAGRAM_SOURCE_ABSENT", f"{provenance_source} does not exist")
    provenance = json.loads(provenance_source.read_text(encoding="utf-8"))
    if not provenance.get("run"):
        raise Refused(
            "DIAGRAM_SOURCE_ABSENT", f"{provenance_source} names no 'run' the figure came from"
        )

    paths = figure_paths(paper_dir, figure_id)
    paths["pdf"].parent.mkdir(parents=True, exist_ok=True)
    paths["pdf"].write_bytes(pdf_source.read_bytes())
    provenance_dest = paths["pdf"].with_suffix(".provenance.json")
    provenance_dest.write_text(json.dumps(provenance, indent=2), encoding="utf-8")
    return {"figureId": figure_id, "pdf": str(paths["pdf"]), "provenance": str(provenance_dest)}
