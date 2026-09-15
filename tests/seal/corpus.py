"""The seal's fixture corpus, committed as code and built fresh per run.

`build(root)` writes every fixture byte from the module-level constants below
into `root`, `git init`s each target with pinned identity and pinned
`GIT_AUTHOR_DATE`/`GIT_COMMITTER_DATE`, and returns a `Roots` naming every
path a case's argv or the harness itself needs.

Three git targets, one proposals directory, one plan template:

- `fixture_a` — package `Seal`, `Seal/Data/` present, findings covering
  `remedy_block`, one adopted `adoption`, `uses`, and `introduces` (all four,
  design.md D3's coverage requirement), declared family `seal-1.md` (marker-
  owned, matches proposals `P`'s `seal-1.md`/`seal-2.md`).
- `fixture_b` — `fixture_a` with `Seal/Data/` absent, otherwise byte-
  identical. **Load-bearing for F5** (design.md D3/D8): `expected_dirs`'s
  `or with_data` short-circuit makes `fixture_a` structurally blind to a
  wrong `PRODUCT_DATA`; only `fixture_b` can see it move `missingDirs`.
- `fixture_t` — case 14 only. `__benchmark__` undeclared; the one module's
  own `__provenance__` declares family `draft-1.md`, matching proposals
  `P`'s hand-authored, unmarked `draft-1.md`/`draft-01.md` tie.
  `verify`'s `discovery`/`tied`/`markerOwned` fields derive SOLELY from the
  target's own declared revision, never from `--revision` (measured during
  apply, 2026-09-11): `fixture_t` is a genuinely separate target because
  case 12's marker-owned family and case 14's hand-authored, tied family
  cannot coexist as one target's declared state.
- `proposals` (`P`) — `seal-1.md`/`seal-2.md` (both `MANAGED_ARTIFACT_MARKER`-
  prefixed), `draft-1.md`/`draft-01.md` (unmarked, one family, one digit key
  — the tie).
- `plan_template` — the four path-independent `build_plan()` fields
  (`renames`/`moves`/`createDirs`/`referenceUpdates`, all empty for both
  `fixture_a` and `fixture_b`); the harness injects `"target"` per case.
"""

from __future__ import annotations

import dataclasses
import os
import subprocess
from pathlib import Path

#: Pinned so the corpus's own git commits are byte-reproducible across
#: capture runs without needing N5 at all for the corpus's OWN shas — N5
#: stays belt-and-braces (design.md D4).
_GIT_AUTHOR_DATE = "2026-01-01T00:00:00"
_GIT_COMMITTER_DATE = "2026-01-01T00:00:00"
_GIT_IDENTITY_NAME = "seal-corpus"
_GIT_IDENTITY_EMAIL = "seal-corpus@example.invalid"

#: The marker the deliberation skill's own store writes; read here the exact
#: same way `implementation_cli.MANAGED_ARTIFACT_MARKER` reads it back — a
#: leading prefix, byte for byte (design.md's proposal.md citation).
_MANAGED_ARTIFACT_MARKER = b"<!-- proposal-workspace:artifact:v1 -->\n"

#: The revision text both `fixture_a`/`fixture_b`'s package and `P`'s
#: `seal-1.md`/`seal-2.md` files carry. Three sections, three tagged
#: equations (`1.1`, `2.1`, `3.1`), one notation marker (`E[x]`), one
#: already-adopted replacement text (`g = h + k`) — everything the four
#: findings below cite.
REVISION_TEXT = (
    "## 1\n"
    "\n"
    "$$\n"
    "a = b \\tag{1.1}\n"
    "$$\n"
    "\n"
    "## 2\n"
    "\n"
    "$$\n"
    "c = d \\tag{2.1}\n"
    "$$\n"
    "\n"
    "## 3\n"
    "\n"
    "$$\n"
    "e = f \\tag{3.1}\n"
    "$$\n"
    "\n"
    "Throughout, the estimator is written E[x].\n"
    "\n"
    "The corrected form now reads g = h + k.\n"
)

#: `tests/findings.py`'s content: four findings, `ast.literal_eval`-able
#: (`read_findings` parses statically, never imports). Covers, per
#: design.md D3's Corpus Coverage requirement: `remedy_block` (`inline-fix`,
#: `structural-notation`), one ADOPTED `adoption` (`adopted-tag`), `uses`
#: (all four), `introduces` (`structural-notation`, non-empty — the coverage
#: requirement's own `≥1 item with non-empty introduces`).
#:
#: Verified live against the real CLI during apply (`handoff --revision
#: seal-2.md`): `settleInline=[inline-fix]`, `deferToOwnSession=
#: [structural-notation, unreadable-marker]`, `alreadyAdopted=[adopted-tag]`
#: — all three of inline/deferred/settled non-empty, the exact shape
#: `test_findings_reach_the_output` requires.
FINDINGS_SOURCE = '''FINDINGS = [
    {
        "id": "adopted-tag",
        "kind": "inconsistency",
        "status": "measured",
        "rate": "always",
        "statement": "Section 1's identity omits a correction term.",
        "remedy": "Replace a = b with the corrected identity.",
        "equations": ["1.1"],
        "remedy_equations": ["1.1"],
        "uses": ["E[x]"],
        "introduces": [],
        "adoption": {"absent": "UNPATCHED_ARTIFACT_MARKER_1",
                      "expect": ["g = h + k"]},
        "remedy_block": "$$\\ng = h + k \\\\tag{1.1}\\n$$",
        "becomes_invariant": "identity_one_holds",
    },
    {
        "id": "inline-fix",
        "kind": "gap",
        "status": "measured",
        "rate": "always",
        "statement": "Section 2's identity is written without its correction.",
        "remedy": "Replace c = d with the corrected form.",
        "equations": ["2.1"],
        "remedy_equations": ["2.1"],
        "uses": ["E[x]"],
        "introduces": [],
        "adoption": {"absent": "c = d", "expect": ["c = D_corrected"]},
        "remedy_block": "$$\\nc = D_corrected \\\\tag{2.1}\\n$$",
    },
    {
        "id": "structural-notation",
        "kind": "gap",
        "status": "measured",
        "rate": "always",
        "statement": "Section 3's identity needs a new operator this document has never defined.",
        "remedy": "Introduce a new operator and rewrite the identity in terms of it.",
        "equations": ["3.1"],
        "remedy_equations": ["3.1"],
        "uses": ["E[x]"],
        "introduces": ["Theta-op"],
        "adoption": {"absent": "e = f", "expect": ["e = Theta-op"]},
        "remedy_block": "$$\\ne = Thetaop \\\\tag{3.1}\\n$$",
    },
    {
        "id": "unreadable-marker",
        "kind": "inconsistency",
        "status": "measured",
        "rate": "sometimes",
        "statement": "The identity for a = b may already have changed in a way this cannot read.",
        "remedy": "Confirm by hand whether the identity still needs correcting.",
        "equations": ["1.1"],
        "remedy_equations": [],
        "uses": ["E[x]"],
        "introduces": [],
        "adoption": {"absent": "NEVER_PRESENT_MARKER_4", "expect": ["NEVER_MATCHES_EITHER"]},
    },
]
'''

#: `src/Seal/kernels.py`'s `__provenance__`, shared by `fixture_a`/`fixture_b`.
#: Declares family `seal-1.md` only as a FALLBACK precedent; the `__benchmark__`
#: declaration below is what `fixture_a`/`fixture_b`'s `verify` actually
#: discovers against (`resolve_benchmark_declaration`'s declared revision
#: takes priority — see `cmd_verify`'s own docstring).
_MODULE_SOURCE = (
    '__provenance__ = {\n'
    '    "revision": "seal-1.md", "sections": ["1", "2", "3"],\n'
    '    "equations": ["1.1", "2.1", "3.1"], "invariants": ["identity_one_holds"],\n'
    '}\n\n\n'
    'def identity():\n'
    '    return True\n'
)

#: `src/Seal_Benchmark/__init__.py`'s content for `fixture_a`/`fixture_b`:
#: `__benchmark__` (populated `arms`, declared family `seal-1.md`) beside
#: `__steps__` — both top-level literals live in the same file, per
#: `BENCHMARK_DECLARATION`/`STEPS_DECLARATION` (design.md's own citations).
_BENCHMARK_INIT_SOURCE = (
    "__benchmark__ = {\n"
    "    'revision': 'seal-1.md',\n"
    "    'premises': {},\n"
    "    'arms': {'floor': {'sections': ['1']}, 'full': {'sections': ['1', '2', '3']}},\n"
    "    'search': {},\n"
    "    'report': {},\n"
    "    'distribution': {},\n"
    "    'entry': {'module': 'Seal_Benchmark.steps', 'function': 'run'},\n"
    "}\n"
    "__steps__ = {\n"
    "    'measure': {'module': 'Seal_Benchmark.steps', 'function': 'run'},\n"
    "}\n"
)

_STEPS_MODULE_SOURCE = "def run(*a, **k):\n    return {}\n"

_AGREED_SOURCE = "# Agreed\n\n## Ladder\n\n- [ ] First measurable claim.\n"

#: `fixture_t`'s own module: no `__benchmark__` at all, so `cmd_verify`'s
#: `family` derivation falls back to this module's OWN declared revision —
#: `draft-1.md`, matching `P`'s hand-authored, unmarked tie family.
_TIE_MODULE_SOURCE = (
    '__provenance__ = {\n'
    '    "revision": "draft-1.md", "sections": ["1", "2", "3"],\n'
    '    "equations": ["1.1", "2.1", "3.1"], "invariants": [],\n'
    '}\n'
)


@dataclasses.dataclass(frozen=True)
class Roots:
    """Every path a case's argv or the harness needs, once `build()` runs."""

    root: Path
    fixture_a: Path
    fixture_b: Path
    fixture_t: Path
    proposals: Path
    #: The four path-independent `build_plan()` fields. `"target"` is
    #: injected per case by the harness (`seal_capture.py`), never
    #: statically committed — the exact-string match in
    #: `_materialize_plan_gate`/`cmd_apply` would only ever match one
    #: specific scratch copy's path.
    plan_template: dict


def _git_env() -> dict:
    env = dict(os.environ)
    env["GIT_AUTHOR_NAME"] = env["GIT_COMMITTER_NAME"] = _GIT_IDENTITY_NAME
    env["GIT_AUTHOR_EMAIL"] = env["GIT_COMMITTER_EMAIL"] = _GIT_IDENTITY_EMAIL
    env["GIT_AUTHOR_DATE"] = env["GIT_COMMITTER_DATE"] = _GIT_AUTHOR_DATE
    # Never let an operator's global/system git config reshape a commit this
    # corpus depends on being byte-fixed.
    env["GIT_CONFIG_GLOBAL"] = env["GIT_CONFIG_SYSTEM"] = "/dev/null"
    return env


def _git_commit(target: Path) -> None:
    env = _git_env()
    subprocess.run(["git", "init", "-q", str(target)], check=True, capture_output=True)
    subprocess.run(["git", "add", "-A"], cwd=target, env=env, check=True,
                   capture_output=True)
    subprocess.run(["git", "commit", "-q", "-m", "initial"], cwd=target, env=env,
                   check=True, capture_output=True)


def _write_common_package(target: Path, *, module_source: str,
                          benchmark_init_source: str, findings_source: str,
                          with_data: bool) -> None:
    (target / "src" / "Seal").mkdir(parents=True)
    (target / "src" / "Seal_Benchmark").mkdir(parents=True)
    (target / "tests").mkdir(parents=True)
    (target / "Seal" / "Notebooks").mkdir(parents=True)
    (target / "Seal" / "Results").mkdir(parents=True)
    (target / "Seal" / "Models").mkdir(parents=True)
    if with_data:
        (target / "Seal" / "Data").mkdir(parents=True)

    (target / "src" / "Seal" / "__init__.py").write_text("__all__ = []\n", encoding="utf-8")
    (target / "src" / "Seal" / "kernels.py").write_text(module_source, encoding="utf-8")
    (target / "src" / "Seal_Benchmark" / "__init__.py").write_text(
        benchmark_init_source, encoding="utf-8")
    (target / "src" / "Seal_Benchmark" / "steps.py").write_text(
        _STEPS_MODULE_SOURCE, encoding="utf-8")
    (target / "tests" / "findings.py").write_text(findings_source, encoding="utf-8")
    (target / "tests" / "__init__.py").write_text("", encoding="utf-8")
    (target / "Seal" / "AGREED.md").write_text(_AGREED_SOURCE, encoding="utf-8")


def _build_fixture_a_or_b(target: Path, *, with_data: bool) -> None:
    _write_common_package(
        target, module_source=_MODULE_SOURCE,
        benchmark_init_source=_BENCHMARK_INIT_SOURCE,
        findings_source=FINDINGS_SOURCE, with_data=with_data)
    _git_commit(target)


def _build_fixture_t(target: Path) -> None:
    """Case 14 only: no `__benchmark__`, one module declaring family
    `draft-1.md`. Minimal on purpose — case 14 exercises `verify`'s
    discovery/tie mechanism alone, nothing else."""
    (target / "src" / "Seal").mkdir(parents=True)
    (target / "src" / "Seal_Benchmark").mkdir(parents=True)
    (target / "tests").mkdir(parents=True)
    (target / "src" / "Seal" / "__init__.py").write_text("__all__ = []\n", encoding="utf-8")
    (target / "src" / "Seal" / "kernels.py").write_text(_TIE_MODULE_SOURCE, encoding="utf-8")
    (target / "src" / "Seal_Benchmark" / "__init__.py").write_text(
        "__all__ = []\n", encoding="utf-8")
    (target / "tests" / "__init__.py").write_text("", encoding="utf-8")
    _git_commit(target)


def _build_proposals(root: Path) -> Path:
    proposals = root / "P"
    proposals.mkdir(parents=True)
    (proposals / "seal-1.md").write_bytes(_MANAGED_ARTIFACT_MARKER + REVISION_TEXT.encode("utf-8"))
    (proposals / "seal-2.md").write_bytes(_MANAGED_ARTIFACT_MARKER + REVISION_TEXT.encode("utf-8"))
    (proposals / "draft-1.md").write_text(REVISION_TEXT, encoding="utf-8")
    (proposals / "draft-01.md").write_text(REVISION_TEXT, encoding="utf-8")
    return proposals


def build(root: Path) -> Roots:
    """Write fixtures `fixture_a`, `fixture_b`, `fixture_t`, `proposals`
    under `root`, `git init` each target, and return every path a case or
    the harness needs. Deterministic given the module-level constants above
    — the only non-fixed byte anywhere is `root` itself, which the harness's
    `<CORPUS>` placeholder (`normalize.py` N2) replaces before digesting."""
    root.mkdir(parents=True, exist_ok=True)

    fixture_a = root / "A"
    fixture_b = root / "B"
    fixture_t = root / "T"
    fixture_a.mkdir(parents=True)
    fixture_b.mkdir(parents=True)
    fixture_t.mkdir(parents=True)

    _build_fixture_a_or_b(fixture_a, with_data=True)
    _build_fixture_a_or_b(fixture_b, with_data=False)
    _build_fixture_t(fixture_t)
    proposals = _build_proposals(root)

    plan_template = {
        "name": "Seal", "renames": [], "moves": [], "createDirs": [],
        "referenceUpdates": [],
    }

    return Roots(root=root, fixture_a=fixture_a, fixture_b=fixture_b,
                fixture_t=fixture_t, proposals=proposals,
                plan_template=plan_template)


#: Digested into `digests.json` under the reserved key
#: `"__corpus_fingerprint__"`. `test_corpus_fingerprint_matches` goes red the
#: moment anyone edits this file without recapturing — design.md D3's
#: anti-trim guard.
CORPUS_FINGERPRINT_SOURCE = Path(__file__)
