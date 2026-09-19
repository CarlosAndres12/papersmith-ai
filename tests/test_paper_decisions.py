"""paper-writing: region grammar, guidance registry, declarations,
provenance — the paper's own decisions.

A second, independent suite from `tests/test_paper_writing.py` on purpose
(design.md, `File Changes`: "a second class of the same name loses tests
silently"). Stdlib-only `unittest`, same fixture discipline: every fixture
lives under a `TemporaryDirectory`, and every `paper_scaffold.resolve_paper_dir`
/ `paper_guidance.resolve_guidance_dir` call passes an injected `forge_root`
so the real repository tree is never touched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parent.parent
SKILL_SCRIPTS = FORGE_ROOT / ".claude" / "skills" / "paper-writing" / "scripts"
CLI = SKILL_SCRIPTS / "paper_cli.py"
sys.path.insert(0, str(SKILL_SCRIPTS))
import paper_block  # noqa: E402
import paper_region  # noqa: E402
import paper_guidance  # noqa: E402
import paper_scaffold  # noqa: E402
import paper_vocabulary  # noqa: E402
import paper_graph  # noqa: E402
import paper_declarations  # noqa: E402
import paper_provenance  # noqa: E402
import paper_couplings  # noqa: E402
import paper_coupling_evidence  # noqa: E402
import paper_cli  # noqa: E402

sys.path.insert(0, str(FORGE_ROOT / ".claude" / "skills" / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

sys.path.insert(0, str(FORGE_ROOT / "tests"))
from paper_mutation import _run_against_mutant  # noqa: E402

AGENTS_DIR = FORGE_ROOT / ".claude" / "agents"


def _assert_guard_failed_under_mutation(case: unittest.TestCase, proc) -> None:
    """Shared two-part assertion every mutation-proof test in this suite
    uses: `MUTANT_IMPORTED_OK` proves the mutant module actually loaded and
    `unittest` actually ran the named test against it, and a non-zero exit
    proves the guard genuinely failed rather than the process crashing on
    import before the test ever ran."""
    output = proc.stdout + proc.stderr
    case.assertIn("MUTANT_IMPORTED_OK", output, output)
    case.assertNotEqual(proc.returncode, 0, output)


def _marker_pair(block_id: str, body: bytes) -> bytes:
    digest = hashlib.sha256(body).hexdigest()
    return (
        f"%% paper-writing block {block_id} begin sha256={digest}\n".encode("ascii")
        + body
        + f"%% paper-writing block {block_id} end\n".encode("ascii")
    )


class DisjointGrammarTests(unittest.TestCase):
    """`design.md`, `Two grammars coexist by mutual non-prefix, pinned in
    both directions`. Five checks, four derived from
    `paper_block.MARKER_PREFIX` and `paper_region.KINDS` rather than
    written out by hand."""

    def test_marker_prefix_has_exactly_three_tokens(self) -> None:
        self.assertEqual(
            len(paper_block.MARKER_PREFIX.split()), 3,
            "a narrowing of MARKER_PREFIX to 'block' status alone (dropping "
            "a token) changes the slot this test derives everything else "
            "from",
        )

    def test_marker_prefix_slot_two_is_block(self) -> None:
        self.assertEqual(paper_block.MARKER_PREFIX.split()[2], b"block")

    def test_block_is_not_a_region_kind_and_no_kind_prefixes_another(self) -> None:
        block_token = paper_block.MARKER_PREFIX.split()[2]
        encoded_kinds = [kind.encode("ascii") for kind in paper_region.KINDS]
        self.assertNotIn(block_token, encoded_kinds)
        candidates = encoded_kinds + [block_token]
        for i, left in enumerate(candidates):
            for j, right in enumerate(candidates):
                if i == j:
                    continue
                self.assertFalse(
                    right.startswith(left),
                    f"{right!r} is a prefix of {left!r}; the two grammars would "
                    "collide under Phase 1's own startswith() check",
                )

    def test_marker_prefix_is_pinned_exactly(self) -> None:
        self.assertEqual(
            paper_block.MARKER_PREFIX, b"%% paper-writing block",
            "MARKER_PREFIX is pinned exactly, trailing space included, "
            "deliberately brittle: a legitimate Phase 1 edit to this "
            "constant is EXPECTED to redden this test, on purpose -- it "
            "is not a bug in this test and must not be loosened to admit "
            "the change silently. A narrowing to 'b\"%% paper-writing "
            "block \"' (trailing space) would split identically and "
            "silently disarm Phase 1's own MARKER_MALFORMED detection.",
        )

    def test_regions_only_file_reports_zero_blocks_and_two_regions(self) -> None:
        declarations_bytes, _digest = paper_region.build_region_bytes(
            "declarations", {"generation": 0, "records": []}
        )
        provenance_bytes, _digest2 = paper_region.build_region_bytes(
            "provenance", {"records": []}
        )
        data = declarations_bytes + provenance_bytes

        result = paper_block.status(data)
        self.assertEqual(result["blocks"], [])

        self.assertIsNotNone(paper_region.find_region(data, "declarations"))
        self.assertIsNotNone(paper_region.find_region(data, "provenance"))

    def test_one_block_plus_both_regions_are_seen_by_their_own_parser_only(self) -> None:
        body = b"prose\n"
        data = _marker_pair("intro", body)
        declarations_bytes, _digest = paper_region.build_region_bytes(
            "declarations", {"generation": 0, "records": []}
        )
        provenance_bytes, _digest2 = paper_region.build_region_bytes(
            "provenance", {"records": []}
        )
        data = data + declarations_bytes + provenance_bytes

        result = paper_block.status(data)
        self.assertEqual(len(result["blocks"]), 1)
        self.assertEqual(result["blocks"][0]["id"], "intro")

        self.assertIsNotNone(paper_region.find_region(data, "declarations"))
        self.assertIsNotNone(paper_region.find_region(data, "provenance"))


class RegionGrammarMutationTests(unittest.TestCase):
    """Mutation 1 (design.md): renaming our sentinel's slot 2 to `block`
    proves `DisjointGrammarTests`'s behavioural scenario can fire."""

    def test_mutation_1_renaming_the_sentinel_to_block_breaks_the_regions_only_scenario(
        self,
    ) -> None:
        proc = _run_against_mutant(
            'begin_line = f"%% paper-writing {kind} begin sha256={digest}\\n".encode("ascii")',
            'begin_line = f"%% paper-writing block begin sha256={digest}\\n".encode("ascii")',
            "tests.test_paper_decisions.DisjointGrammarTests"
            ".test_regions_only_file_reports_zero_blocks_and_two_regions",
            source_path=SKILL_SCRIPTS / "paper_region.py",
        )
        _assert_guard_failed_under_mutation(self, proc)


class RegionParsingTests(unittest.TestCase):
    """Grammar-level refusals: `REGION_MALFORMED`, `REGION_DUPLICATED`,
    `REGION_UNPAIRED`, and the round-trip through `serialize_body` /
    `deserialize_body` / digesting."""

    def test_absent_region_returns_none(self) -> None:
        self.assertIsNone(paper_region.find_region(b"nothing here\n", "declarations"))
        self.assertIsNone(paper_region.read_region(b"nothing here\n", "declarations"))

    def test_malformed_marker_line_refuses(self) -> None:
        data = b"%% paper-writing declarations begins sha256=deadbeef\n"
        with self.assertRaises(Refused) as ctx:
            paper_region.find_region(data, "declarations")
        self.assertEqual(ctx.exception.code, "REGION_MALFORMED")

    def test_duplicated_begin_marker_refuses(self) -> None:
        region_bytes, _digest = paper_region.build_region_bytes(
            "declarations", {"generation": 0, "records": []}
        )
        begin_line = region_bytes.splitlines(keepends=True)[0]
        data = begin_line + region_bytes
        with self.assertRaises(Refused) as ctx:
            paper_region.find_region(data, "declarations")
        self.assertEqual(ctx.exception.code, "REGION_DUPLICATED")

    def test_unpaired_begin_marker_refuses(self) -> None:
        region_bytes, digest = paper_region.build_region_bytes(
            "declarations", {"generation": 0, "records": []}
        )
        begin_only = region_bytes.split(b"%% paper-writing declarations end\n")[0]
        with self.assertRaises(Refused) as ctx:
            paper_region.find_region(begin_only, "declarations")
        self.assertEqual(ctx.exception.code, "REGION_UNPAIRED")

    def test_round_trip_preserves_body_and_verifies_digest(self) -> None:
        body_obj = {"generation": 3, "records": [{"kind": "declaration", "id": "x"}]}
        region_bytes, digest = paper_region.build_region_bytes("declarations", body_obj)
        record = paper_region.read_region(region_bytes, "declarations")
        self.assertEqual(record["body"], body_obj)
        self.assertEqual(record["digest"], digest)
        self.assertEqual(paper_region.current_digest(record["body_bytes"]), digest)

    def test_canonical_serialization_is_key_order_independent(self) -> None:
        first = paper_region.serialize_body({"b": 1, "a": 2})
        second = paper_region.serialize_body({"a": 2, "b": 1})
        self.assertEqual(first, second)

    def test_replace_or_append_appends_when_absent(self) -> None:
        region_bytes, _digest = paper_region.build_region_bytes(
            "declarations", {"generation": 0, "records": []}
        )
        result = paper_region.replace_or_append(b"prose\n", "declarations", region_bytes, None)
        self.assertTrue(result.startswith(b"prose\n"))
        self.assertTrue(result.endswith(region_bytes))

    def test_replace_or_append_replaces_existing_span_exactly(self) -> None:
        first_bytes, _digest = paper_region.build_region_bytes(
            "declarations", {"generation": 0, "records": []}
        )
        data = b"before\n" + first_bytes + b"after\n"
        existing = paper_region.find_region(data, "declarations")
        second_bytes, _digest2 = paper_region.build_region_bytes(
            "declarations", {"generation": 1, "records": []}
        )
        replaced = paper_region.replace_or_append(data, "declarations", second_bytes, existing)
        self.assertEqual(replaced, b"before\n" + second_bytes + b"after\n")


class GuidanceRegistryTests(unittest.TestCase):
    """`specs/guidance-registry/spec.md`."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.forge_root = Path(self._tmp.name) / "repo"
        self.forge_root.mkdir()
        self.guidance_dir = self.forge_root / "guidance"

    def _write_marker(self, folder: str, obj) -> None:
        target = self.guidance_dir / folder
        target.mkdir(parents=True, exist_ok=True)
        (target / ".paper-writing.json").write_text(json.dumps(obj), encoding="utf-8")

    def test_fresh_clone_reports_every_folder_unclassified_refuses_nothing(self) -> None:
        for folder in ("paper-guide", "reference-papers", "style-reference-notes"):
            (self.guidance_dir / folder).mkdir(parents=True)

        registry = paper_guidance.read_registry(self.guidance_dir)

        self.assertEqual(
            registry,
            {
                "paper-guide": "unclassified",
                "reference-papers": "unclassified",
                "style-reference-notes": "unclassified",
            },
        )

    def test_folder_named_like_a_class_stays_unclassified(self) -> None:
        (self.guidance_dir / "style-reference-notes").mkdir(parents=True)

        registry = paper_guidance.read_registry(self.guidance_dir)

        self.assertEqual(registry["style-reference-notes"], "unclassified")

    def test_valid_marker_classifies_its_folder(self) -> None:
        self._write_marker("prior-papers", {"class": "evidence"})

        registry = paper_guidance.read_registry(self.guidance_dir)

        self.assertEqual(registry["prior-papers"], "evidence")

    def test_out_of_vocabulary_class_refuses(self) -> None:
        self._write_marker("prior-papers", {"class": "reference-material"})

        with self.assertRaises(Refused) as ctx:
            paper_guidance.read_registry(self.guidance_dir)
        self.assertEqual(ctx.exception.code, "UNKNOWN_GUIDANCE_CLASS")
        self.assertIn("reference-material", ctx.exception.detail)
        self.assertIn("prior-papers", ctx.exception.detail)

    def test_marker_with_extra_key_refuses_malformed(self) -> None:
        self._write_marker("prior-papers", {"class": "evidence", "extra": True})

        with self.assertRaises(Refused) as ctx:
            paper_guidance.read_registry(self.guidance_dir)
        self.assertEqual(ctx.exception.code, "MALFORMED_GUIDANCE_MARKER")

    def test_marker_that_is_not_an_object_refuses_malformed(self) -> None:
        target = self.guidance_dir / "prior-papers"
        target.mkdir(parents=True)
        (target / ".paper-writing.json").write_text("[1, 2]", encoding="utf-8")

        with self.assertRaises(Refused) as ctx:
            paper_guidance.read_registry(self.guidance_dir)
        self.assertEqual(ctx.exception.code, "MALFORMED_GUIDANCE_MARKER")

    def test_guidance_outside_repository_refuses(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_guidance.resolve_guidance_dir("../", forge_root=self.forge_root)
        self.assertEqual(ctx.exception.code, "GUIDANCE_OUTSIDE_REPOSITORY")

    def test_two_arbitrarily_named_folders_each_classify_from_their_own_marker(self) -> None:
        self._write_marker("first-unused-name", {"class": "style-reference"})
        self._write_marker("second-unused-name", {"class": "evidence"})

        registry = paper_guidance.read_registry(self.guidance_dir)

        self.assertEqual(registry["first-unused-name"], "style-reference")
        self.assertEqual(registry["second-unused-name"], "evidence")

    def test_registry_reads_no_hardcoded_folder_name(self) -> None:
        """The registry's own source names no specific `guidance/<folder>`
        anywhere (`specs/guidance-registry/spec.md`, `Requirement: The
        Registry Reads No Hardcoded Folder Path`)."""
        source = (SKILL_SCRIPTS / "paper_guidance.py").read_text(encoding="utf-8")
        for hardcoded in ("paper-guide", "reference-papers"):
            self.assertNotIn(hardcoded, source)


class GuidanceRegistryMutationTests(unittest.TestCase):
    """Mutation 4 (design.md): defaulting an unclassified folder to
    `style-reference` proves the fresh-clone scenario can fire."""

    def test_mutation_4_defaulting_unclassified_to_style_reference_breaks_the_fresh_clone_scenario(
        self,
    ) -> None:
        proc = _run_against_mutant(
            'return "unclassified"',
            'return "style-reference"',
            "tests.test_paper_decisions.GuidanceRegistryTests"
            ".test_fresh_clone_reports_every_folder_unclassified_refuses_nothing",
            source_path=SKILL_SCRIPTS / "paper_guidance.py",
        )
        _assert_guard_failed_under_mutation(self, proc)


class SourceMdClassificationTests(unittest.TestCase):
    """`the-skill-stops-trusting-memory`, item 2/3: `paper_guidance.
    classify_source_md` -- the pure lookup `validate --source-md`'s guard is
    built on."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.forge_root = Path(self._tmp.name) / "repo"
        self.forge_root.mkdir()
        self.guidance_dir = self.forge_root / "guidance"

    def _write_marker(self, folder: str, cls: str) -> Path:
        target = self.guidance_dir / folder
        target.mkdir(parents=True, exist_ok=True)
        (target / ".paper-writing.json").write_text(json.dumps({"class": cls}), encoding="utf-8")
        return target

    def test_a_path_under_a_style_reference_folder_classifies_style_reference(self) -> None:
        folder = self._write_marker("reference-papers", "style-reference")
        paper_dir = folder / "paper1" / "paper1.md"
        paper_dir.parent.mkdir(parents=True)
        paper_dir.write_text("body", encoding="utf-8")

        self.assertEqual(
            paper_guidance.classify_source_md(paper_dir, self.guidance_dir), "style-reference",
        )

    def test_a_path_under_an_evidence_folder_classifies_evidence(self) -> None:
        folder = self._write_marker("data-paper", "evidence")
        paper_dir = folder / "paper1" / "paper1.md"
        paper_dir.parent.mkdir(parents=True)
        paper_dir.write_text("body", encoding="utf-8")

        self.assertEqual(paper_guidance.classify_source_md(paper_dir, self.guidance_dir), "evidence")

    def test_a_path_under_an_unmarked_folder_classifies_unclassified(self) -> None:
        target = self.guidance_dir / "area-benchmark" / "paper1"
        target.mkdir(parents=True)
        md_path = target / "paper1.md"
        md_path.write_text("body", encoding="utf-8")

        self.assertEqual(
            paper_guidance.classify_source_md(md_path, self.guidance_dir), "unclassified",
        )

    def test_a_path_outside_guidance_entirely_classifies_none(self) -> None:
        outside = Path(self._tmp.name) / "elsewhere" / "paper1.md"
        outside.parent.mkdir(parents=True)
        outside.write_text("body", encoding="utf-8")

        self.assertIsNone(paper_guidance.classify_source_md(outside, self.guidance_dir))


class ValidateSourceMdGuardTests(unittest.TestCase):
    """`the-skill-stops-trusting-memory`, item 2/3: `validate --source-md`
    refuses a `style-reference`-classed source and accepts an
    `evidence`-classed one -- the exact scenario measured before this
    change: `validate --block X --quote "<a sentence lifted from a
    style-reference paper>" --source-md guidance/reference-papers/<paper>/
    <paper>.md --verdict holds` used to return `satisfied`.

    Runs under the real, non-injectable `FORGE_ROOT` default, the same
    `implementations/` convention `SkeletonPathContainmentTests`
    (`tests/test_paper_writing.py`) uses, because `cmd_validate` resolves
    both `--paper`/`--guidance` through it."""

    def setUp(self) -> None:
        self.test_root = (
            FORGE_ROOT / "implementations"
            / f".paper-writing-validate-source-md-guard-test-{os.getpid()}-{uuid.uuid4().hex[:8]}"
        )
        self.addCleanup(shutil.rmtree, self.test_root, ignore_errors=True)
        self.paper_dir = self.test_root / "paper"
        paper_scaffold.scaffold(self.paper_dir)
        self.guidance_dir = self.test_root / "guidance"

    def _write_marker(self, folder: str, cls: str) -> Path:
        target = self.guidance_dir / folder
        target.mkdir(parents=True, exist_ok=True)
        (target / ".paper-writing.json").write_text(json.dumps({"class": cls}), encoding="utf-8")
        return target

    def _write_source(self, folder: Path, text: str) -> Path:
        paper_dir = folder / "paper1"
        paper_dir.mkdir(parents=True, exist_ok=True)
        md_path = paper_dir / "paper1.md"
        md_path.write_text(text, encoding="utf-8")
        return md_path

    def _args(self, *, source_md: Path, quote: str) -> argparse.Namespace:
        return argparse.Namespace(
            paper=str(self.paper_dir), block="intro.b1", claim="c1", quote=quote,
            source_md=str(source_md), verdict="holds", reason=None, cite_key=None,
            identifier=None, resolver=None, metadata_digest=None, regime="none",
            section_md=None, round=None, guidance=str(self.guidance_dir), body=None,
            sentence=None,
        )

    def test_a_quote_from_a_style_reference_source_refuses(self) -> None:
        folder = self._write_marker("reference-papers", "style-reference")
        source_md = self._write_source(folder, "An Explainable Framework Integrating Local")

        with self.assertRaises(Refused) as ctx:
            paper_cli.cmd_validate(self._args(
                source_md=source_md, quote="An Explainable Framework Integrating Local",
            ))

        self.assertEqual(ctx.exception.code, "SOURCE_STYLE_REFERENCE")
        self.assertIn(str(source_md), ctx.exception.detail)

    def test_a_quote_from_an_evidence_source_is_accepted(self) -> None:
        folder = self._write_marker("data-paper", "evidence")
        source_md = self._write_source(folder, "scientific data")

        result = paper_cli.cmd_validate(self._args(source_md=source_md, quote="scientific data"))

        self.assertEqual(result["status"], "satisfied")

    def test_a_quote_from_an_unclassified_source_refuses(self) -> None:
        target = self.guidance_dir / "area-benchmark" / "paper1"
        target.mkdir(parents=True)
        source_md = target / "paper1.md"
        source_md.write_text("hello world quote", encoding="utf-8")

        with self.assertRaises(Refused) as ctx:
            paper_cli.cmd_validate(self._args(source_md=source_md, quote="hello world quote"))

        self.assertEqual(ctx.exception.code, "SOURCE_NOT_EVIDENCE")

    def test_a_quote_from_outside_guidance_entirely_is_unaffected_by_this_guard(self) -> None:
        """`classify_source_md` returns `None` for a path outside
        `guidance_dir` altogether -- this guard must not refuse THAT case;
        whatever else may apply to it is out of this gate's scope."""
        outside_dir = self.test_root / "elsewhere"
        outside_dir.mkdir()
        source_md = outside_dir / "paper1.md"
        source_md.write_text("free text", encoding="utf-8")

        result = paper_cli.cmd_validate(self._args(source_md=source_md, quote="free text"))

        self.assertEqual(result["status"], "satisfied")

    def test_no_claim_given_never_reaches_the_guard_and_writes_nothing(self) -> None:
        """The guard lives inside `_build_evidence_record`, called only
        when `--claim` is given -- a bare `validate --block` (status
        check) never touches `guidance_dir` classification at all."""
        args = self._args(source_md=Path("unused.md"), quote="unused")
        args.claim = None

        result = paper_cli.cmd_validate(args)

        self.assertEqual(result["status"], "satisfied")
        self.assertEqual(result["unsupported"], [])


class ValidateSourceMdGuardMutationTests(unittest.TestCase):
    """Proves both new refusal branches are load-bearing, not dead code."""

    def _write_marker(self, guidance_dir: Path, folder: str, cls: str) -> Path:
        target = guidance_dir / folder
        target.mkdir(parents=True, exist_ok=True)
        (target / ".paper-writing.json").write_text(json.dumps({"class": cls}), encoding="utf-8")
        return target

    def test_mutation_dropping_the_style_reference_branch_breaks_the_guard(self) -> None:
        proc = _run_against_mutant(
            'if source_class == "style-reference":\n'
            '        raise Refused(\n'
            '            "SOURCE_STYLE_REFERENCE",\n'
            '            f"{source_md} resolves inside a guidance folder classed '
            "'style-reference'; \"\n"
            '            "style-reference feeds style only, never a quote submitted as evidence",\n'
            '        )',
            'if False:\n'
            '        raise Refused("SOURCE_STYLE_REFERENCE", "unreachable")',
            "tests.test_paper_decisions.ValidateSourceMdGuardTests"
            ".test_a_quote_from_a_style_reference_source_refuses",
            source_path=SKILL_SCRIPTS / "paper_cli.py",
        )
        _assert_guard_failed_under_mutation(self, proc)

    def test_mutation_dropping_the_not_evidence_branch_breaks_the_guard(self) -> None:
        proc = _run_against_mutant(
            'if source_class != "evidence":\n'
            '        raise Refused(\n'
            '            "SOURCE_NOT_EVIDENCE",\n'
            '            f"{source_md} resolves inside a guidance folder classed {source_class!r}, "\n'
            '            "not \'evidence\'; classify the folder before quoting it as evidence",\n'
            '        )',
            'if False:\n'
            '        raise Refused("SOURCE_NOT_EVIDENCE", "unreachable")',
            "tests.test_paper_decisions.ValidateSourceMdGuardTests"
            ".test_a_quote_from_an_unclassified_source_refuses",
            source_path=SKILL_SCRIPTS / "paper_cli.py",
        )
        _assert_guard_failed_under_mutation(self, proc)


class GuidanceIngestedPapersTests(unittest.TestCase):
    """`the-phases-are-derived-not-remembered`, design.md D4; tasks.md
    7.6-7.7. `read_registry` only enumerates ONE level under `guidance/`;
    `ingested_papers` walks the real two-level shape
    (`guidance/<root>/<paper>/<paper>.md`) with `Path.iterdir()`, which is
    gitignore-blind BY CONSTRUCTION -- never `fd`/`rg`, which honour
    `.gitignore` and would report a populated-but-ignored tree empty."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.forge_root = Path(self._tmp.name) / "repo"
        self.forge_root.mkdir()
        self.guidance_dir = self.forge_root / "guidance"

    def _write_paper(self, root: str, folder: str, *, extra_files: tuple = ()) -> None:
        paper_dir = self.guidance_dir / root / folder
        paper_dir.mkdir(parents=True, exist_ok=True)
        (paper_dir / f"{folder}.md").write_text("# Title\n", encoding="utf-8")
        for name in extra_files:
            (paper_dir / name).write_bytes(b"")

    def test_a_gitignored_populated_tree_reports_as_populated_not_empty(self) -> None:
        """tasks.md 7.7: mirrors the real repository's own `.gitignore`
        shape (`guidance/*/*`) so the fixture is not merely synthetic in
        spirit -- an actual ignore pattern matching every path this walk
        must still find. `Path.iterdir()` never consults `.gitignore` at
        all, so this is true regardless; the point of the fixture is to
        make that explicit rather than assumed."""
        self._write_paper("data-paper", "s41597-026-06758-7", extra_files=("_page_0_Picture_2.jpeg",))
        self._write_paper("paper-guide", "brainsci-16-00363")
        self._write_paper("paper-guide", "Li_2026_Prog._Biomed._Eng._8_022013")
        (self.guidance_dir / "area-benchmark").mkdir()
        (self.guidance_dir / ".gitignore").write_text(
            "guidance/*/*\n!guidance/*/.gitkeep\n", encoding="utf-8",
        )

        registry = paper_guidance.ingested_papers(self.guidance_dir)

        self.assertEqual(
            {folder["folder"] for folder in registry["data-paper"]}, {"s41597-026-06758-7"},
        )
        self.assertEqual(
            {folder["folder"] for folder in registry["paper-guide"]},
            {"brainsci-16-00363", "Li_2026_Prog._Biomed._Eng._8_022013"},
        )
        self.assertEqual(registry["area-benchmark"], [])
        total_papers = sum(len(papers) for papers in registry.values())
        self.assertEqual(total_papers, 3)

    def test_a_paper_folder_missing_its_own_named_markdown_is_not_reported(self) -> None:
        (self.guidance_dir / "reference-papers" / "not-a-paper").mkdir(parents=True)

        registry = paper_guidance.ingested_papers(self.guidance_dir)

        self.assertEqual(registry["reference-papers"], [])

    def test_a_non_existent_guidance_dir_reports_an_empty_registry(self) -> None:
        registry = paper_guidance.ingested_papers(self.forge_root / "no-such-guidance")
        self.assertEqual(registry, {})

    def test_against_the_real_shipped_guidance_tree(self) -> None:
        """The real corpus, measured 2026-09-18 (not the tasks artifact's
        own stale forecast of 3 roots): 4 tracked root folders
        (`data-paper`, `paper-guide`, `reference-papers`, `area-benchmark`),
        8 ingested papers total, `area-benchmark` genuinely empty. `guidance/`
        contents are `.gitignore`d (`guidance/*/*`); this reads the real,
        checked-out tree directly, proving the reader is gitignore-blind
        against real ignored bytes, not only a synthetic mirror of the
        pattern."""
        real_guidance_dir = paper_guidance.resolve_guidance_dir(
            None, forge_root=FORGE_ROOT,
        )
        registry = paper_guidance.ingested_papers(real_guidance_dir)

        self.assertEqual(
            set(registry), {"data-paper", "paper-guide", "reference-papers", "area-benchmark"},
        )
        self.assertEqual(registry["area-benchmark"], [])
        self.assertEqual(len(registry["data-paper"]), 1)
        self.assertEqual(len(registry["paper-guide"]), 2)
        self.assertEqual(len(registry["reference-papers"]), 5)
        total_papers = sum(len(papers) for papers in registry.values())
        self.assertEqual(total_papers, 8)


_FIXED_CLOCK = "2024-01-01T00:00:00+00:00"


def _block_record(
    qualified_id: str, *, requires_facts=(), requires_declarations=(), optional=False,
    section="synthetic",
):
    """A minimal, real `paper_graph.BlockRecord` — `affected_blocks` only
    ever reads `.requires_facts`/`.requires_declarations`, so the other
    fields are filled with harmless placeholders rather than driven through
    a full `assemble_corpus` disk fixture. `section` defaults to the same
    placeholder every existing caller already relies on; a caller that
    needs `dataset_placement_candidates` to group by a REAL section name
    (it reads `.section`, never `qualified_id`'s own dotted prefix) passes
    one explicitly."""
    return paper_graph.BlockRecord(
        section=section,
        block_id=qualified_id.split(".")[-1],
        qualified_id=qualified_id,
        block_index=0,
        position=1,
        requires_facts=tuple(requires_facts),
        requires_declarations=tuple(requires_declarations),
        citations="none",
        optional=optional,
    )


class DeclarationsTests(unittest.TestCase):
    """`specs/paper-declarations/spec.md`."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.forge_root = Path(self._tmp.name) / "repo"
        self.forge_root.mkdir()
        self.paper_dir = paper_scaffold.resolve_paper_dir(None, forge_root=self.forge_root)
        paper_scaffold.scaffold(self.paper_dir)

    def _clock(self) -> str:
        return _FIXED_CLOCK

    def test_recording_a_fact_as_a_declaration_refuses_unknown_declaration(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.set_declaration(
                self.paper_dir, "contributions", "x", clock=self._clock
            )
        self.assertEqual(ctx.exception.code, "UNKNOWN_DECLARATION")
        self.assertIn("contributions", ctx.exception.detail)

    def test_recording_a_declaration_as_a_fact_refuses_unknown_fact(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.set_fact(
                self.paper_dir, "repository-url", "x", clock=self._clock
            )
        self.assertEqual(ctx.exception.code, "UNKNOWN_FACT")
        self.assertIn("repository-url", ctx.exception.detail)

    def test_the_partition_is_pairwise_disjoint_and_covers_every_fact(self) -> None:
        self.assertEqual(len(paper_declarations.OBSERVABLE_FACTS), 5)
        self.assertEqual(len(paper_declarations.DERIVED_FACTS), 4)
        self.assertEqual(len(paper_declarations.STRUCTURAL_FACTS), 1)
        union = (
            set(paper_declarations.OBSERVABLE_FACTS)
            | set(paper_declarations.DERIVED_FACTS)
            | set(paper_declarations.STRUCTURAL_FACTS)
        )
        self.assertEqual(union, set(paper_vocabulary.FACTS))
        self.assertTrue(
            set(paper_declarations.OBSERVABLE_FACTS).isdisjoint(paper_declarations.DERIVED_FACTS)
        )
        self.assertTrue(
            set(paper_declarations.OBSERVABLE_FACTS).isdisjoint(paper_declarations.STRUCTURAL_FACTS)
        )
        self.assertTrue(
            set(paper_declarations.DERIVED_FACTS).isdisjoint(paper_declarations.STRUCTURAL_FACTS)
        )

    def test_facts_and_declarations_vocabularies_are_pinned_and_disjoint(self) -> None:
        self.assertEqual(len(paper_vocabulary.FACTS), 10)
        self.assertEqual(len(paper_vocabulary.DECLARATIONS), 6)
        self.assertTrue(set(paper_vocabulary.FACTS).isdisjoint(paper_vocabulary.DECLARATIONS))

    def test_a_fixed_entry_refuses_a_plain_overwrite(self) -> None:
        paper_declarations.set_declaration(
            self.paper_dir, "author-roles", "Alice: writing", clock=self._clock
        )

        with self.assertRaises(Refused) as ctx:
            paper_declarations.set_declaration(
                self.paper_dir, "author-roles", "Bob: writing", clock=self._clock
            )
        self.assertEqual(ctx.exception.code, "DECLARATION_FIXED")

    def test_reopen_then_declare_admits_a_new_value(self) -> None:
        paper_declarations.set_declaration(
            self.paper_dir, "author-roles", "Alice: writing", clock=self._clock
        )
        paper_declarations.reopen(self.paper_dir, "author-roles", clock=self._clock)

        result = paper_declarations.set_declaration(
            self.paper_dir, "author-roles", "Bob: writing", clock=self._clock
        )

        self.assertEqual(result["value"], "Bob: writing")
        tex_path = paper_block.resolve_main_tex(self.paper_dir)
        record = paper_region.read_region(tex_path.read_bytes(), "declarations")
        entry = next(r for r in record["body"]["records"] if r["id"] == "author-roles")
        self.assertEqual(entry["value"], "Bob: writing")
        self.assertTrue(entry["fixed"])

    def test_reopen_narrows_to_exactly_the_naming_blocks(self) -> None:
        corpus = paper_graph.Corpus(
            sections={},
            blocks={
                "a.one": _block_record("a.one", requires_declarations=["repository-url"]),
                "a.two": _block_record("a.two", requires_declarations=["repository-url"]),
                "a.three": _block_record("a.three", requires_declarations=["grant-title"]),
            },
            order_by_section={},
        )

        affected = paper_declarations.affected_blocks(corpus, "repository-url")

        self.assertEqual(affected, {"a.one", "a.two"})

    def test_declarations_hand_edited_refuses_and_writes_nothing(self) -> None:
        paper_declarations.set_declaration(
            self.paper_dir, "author-roles", "Alice: writing", clock=self._clock
        )
        tex_path = paper_block.resolve_main_tex(self.paper_dir)
        pre = tex_path.read_bytes()
        record = paper_region.read_region(pre, "declarations")
        # Corrupt exactly one byte of the region's body -- a hand edit that
        # does not touch the marker lines at all.
        corrupted = (
            pre[: record["begin_start"]]
            + pre[record["begin_start"]:record["end_end"]].replace(b"Alice", b"Alicf", 1)
            + pre[record["end_end"]:]
        )
        tex_path.write_bytes(corrupted)

        with self.assertRaises(Refused) as ctx:
            paper_declarations.set_declaration(
                self.paper_dir, "grant-title", "A Title", clock=self._clock
            )
        self.assertEqual(ctx.exception.code, "DECLARATIONS_HAND_EDITED")

        self.assertEqual(tex_path.read_bytes(), corrupted, "a refused write must leave disk untouched")


class DeclinedFactTests(unittest.TestCase):
    """`a-declined-fact-has-somewhere-to-live`: a fact the operator has
    DECLINED — decided it does not enter the paper for now — is distinct
    from a fact simply not yet measured. Stored through the exact same
    `declarations` region, `set_fact`/`reopen`'s exact same private
    readers/writers, never a second store.

    A decline's `condition` is mandatory (`condition-that-expires`
    extension): a JSON object the skill re-evaluates fresh from disk on
    every `read_declined` call, resolved relative to `paper_dir.parent`
    (the fixture's own `forge_root`). `self.CONDITION` names
    `self.forge_root / "experiments"`, a path that does not exist under
    this fixture by default — `_evaluate_condition` reports a non-existent
    path as holding, matching `decline_fact`'s own docstring ("does not
    exist" is a holding case for `directory-empty-except`)."""

    CONDITION = {"type": "directory-empty-except", "path": "experiments", "ignore": [".gitkeep"]}

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.forge_root = Path(self._tmp.name) / "repo"
        self.forge_root.mkdir()
        self.paper_dir = paper_scaffold.resolve_paper_dir(None, forge_root=self.forge_root)
        paper_scaffold.scaffold(self.paper_dir)

    def _clock(self) -> str:
        return _FIXED_CLOCK

    def test_declining_an_unknown_id_refuses_unknown_fact(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.decline_fact(
                self.paper_dir, "repository-url", "not a fact", self.CONDITION, clock=self._clock,
            )
        self.assertEqual(ctx.exception.code, "UNKNOWN_FACT")
        self.assertIn("repository-url", ctx.exception.detail)

    def test_declining_with_none_reason_refuses_decline_reason_required(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.decline_fact(
                self.paper_dir, "experimental-design", None, self.CONDITION, clock=self._clock,
            )
        self.assertEqual(ctx.exception.code, "DECLINE_REASON_REQUIRED")

    def test_declining_with_empty_reason_refuses_decline_reason_required(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.decline_fact(
                self.paper_dir, "experimental-design", "", self.CONDITION, clock=self._clock,
            )
        self.assertEqual(ctx.exception.code, "DECLINE_REASON_REQUIRED")

    def test_declining_with_whitespace_only_reason_refuses_decline_reason_required(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.decline_fact(
                self.paper_dir, "experimental-design", "   ", self.CONDITION, clock=self._clock,
            )
        self.assertEqual(ctx.exception.code, "DECLINE_REASON_REQUIRED")

    def test_declining_with_no_condition_refuses_condition_required(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.decline_fact(
                self.paper_dir, "experimental-design", "no protocol exists yet", None,
                clock=self._clock,
            )
        self.assertEqual(ctx.exception.code, "CONDITION_REQUIRED")

    def test_declining_with_a_non_object_condition_refuses_condition_malformed(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.decline_fact(
                self.paper_dir, "experimental-design", "no protocol exists yet", "not an object",
                clock=self._clock,
            )
        self.assertEqual(ctx.exception.code, "CONDITION_MALFORMED")

    def test_declining_with_a_condition_missing_type_refuses_unknown_condition_type(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.decline_fact(
                self.paper_dir, "experimental-design", "no protocol exists yet",
                {"path": "experiments"}, clock=self._clock,
            )
        self.assertEqual(ctx.exception.code, "UNKNOWN_CONDITION_TYPE")

    def test_declining_with_an_unknown_condition_type_refuses_unknown_condition_type(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.decline_fact(
                self.paper_dir, "experimental-design", "no protocol exists yet",
                {"type": "file-exists", "path": "x"}, clock=self._clock,
            )
        self.assertEqual(ctx.exception.code, "UNKNOWN_CONDITION_TYPE")

    def test_declining_with_a_condition_missing_path_refuses_condition_malformed(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.decline_fact(
                self.paper_dir, "experimental-design", "no protocol exists yet",
                {"type": "directory-empty-except"}, clock=self._clock,
            )
        self.assertEqual(ctx.exception.code, "CONDITION_MALFORMED")

    def test_declining_with_a_non_list_ignore_refuses_condition_malformed(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.decline_fact(
                self.paper_dir, "experimental-design", "no protocol exists yet",
                {"type": "directory-empty-except", "path": "experiments", "ignore": "x"},
                clock=self._clock,
            )
        self.assertEqual(ctx.exception.code, "CONDITION_MALFORMED")

    def test_declining_with_a_path_outside_the_root_refuses_condition_malformed(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.decline_fact(
                self.paper_dir, "experimental-design", "no protocol exists yet",
                {"type": "directory-empty-except", "path": "../outside"}, clock=self._clock,
            )
        self.assertEqual(ctx.exception.code, "CONDITION_MALFORMED")

    def test_declining_a_fact_is_reflected_in_read_declined(self) -> None:
        paper_declarations.decline_fact(
            self.paper_dir, "experimental-design", "no protocol exists yet", self.CONDITION,
            clock=self._clock,
        )

        declined = paper_declarations.read_declined(self.paper_dir)

        self.assertEqual(set(declined), {"experimental-design"})
        entry = declined["experimental-design"]
        self.assertEqual(entry["reason"], "no protocol exists yet")
        self.assertEqual(entry["condition"], self.CONDITION)
        self.assertTrue(entry["holds"])

    def test_a_declined_fact_is_not_in_read_satisfied(self) -> None:
        paper_declarations.decline_fact(
            self.paper_dir, "experimental-design", "no protocol exists yet", self.CONDITION,
            clock=self._clock,
        )

        satisfied_facts, _satisfied_declarations = paper_declarations.read_satisfied(self.paper_dir)

        self.assertNotIn("experimental-design", satisfied_facts)

    def test_declining_an_already_resolved_fact_refuses_declaration_fixed(self) -> None:
        paper_declarations.set_fact(
            self.paper_dir, "experimental-design", "protocol X", clock=self._clock,
        )

        with self.assertRaises(Refused) as ctx:
            paper_declarations.decline_fact(
                self.paper_dir, "experimental-design", "changed my mind", self.CONDITION,
                clock=self._clock,
            )
        self.assertEqual(ctx.exception.code, "DECLARATION_FIXED")

    def test_resolving_an_already_declined_fact_refuses_declaration_fixed(self) -> None:
        paper_declarations.decline_fact(
            self.paper_dir, "experimental-design", "no protocol exists yet", self.CONDITION,
            clock=self._clock,
        )

        with self.assertRaises(Refused) as ctx:
            paper_declarations.set_fact(
                self.paper_dir, "experimental-design", "protocol X", clock=self._clock,
            )
        self.assertEqual(ctx.exception.code, "DECLARATION_FIXED")

    def test_reopen_then_resolve_round_trips_a_declined_fact(self) -> None:
        paper_declarations.decline_fact(
            self.paper_dir, "experimental-design", "no protocol exists yet", self.CONDITION,
            clock=self._clock,
        )

        paper_declarations.reopen(self.paper_dir, "experimental-design", clock=self._clock)

        self.assertNotIn(
            "experimental-design", paper_declarations.read_declined(self.paper_dir),
        )

        result = paper_declarations.set_fact(
            self.paper_dir, "experimental-design", "protocol X", clock=self._clock,
        )
        self.assertEqual(result["resolution"], "protocol X")
        satisfied_facts, _ = paper_declarations.read_satisfied(self.paper_dir)
        self.assertIn("experimental-design", satisfied_facts)

    def test_read_fact_returns_none_for_a_currently_declined_fact(self) -> None:
        paper_declarations.decline_fact(
            self.paper_dir, "experimental-design", "no protocol exists yet", self.CONDITION,
            clock=self._clock,
        )

        self.assertIsNone(paper_declarations.read_fact(self.paper_dir, "experimental-design"))

    def test_a_lapsed_condition_is_reported_as_not_holding(self) -> None:
        paper_declarations.decline_fact(
            self.paper_dir, "experimental-design", "no protocol exists yet", self.CONDITION,
            clock=self._clock,
        )
        experiments_dir = self.forge_root / "experiments"
        experiments_dir.mkdir(parents=True, exist_ok=True)
        (experiments_dir / "protocol.md").write_text("a real protocol\n", encoding="utf-8")

        declined = paper_declarations.read_declined(self.paper_dir)

        entry = declined["experimental-design"]
        self.assertFalse(entry["holds"])
        self.assertIn("protocol.md", entry["detail"])


class DeclarationsMutationTests(unittest.TestCase):
    """Mutations 2, 5, 6 (design.md)."""

    def test_mutation_2_allowing_overwrite_of_a_fixed_entry_breaks_the_refusal_test(self) -> None:
        proc = _run_against_mutant(
            'if existing is not None and existing.get("fixed"):',
            "if False:",
            "tests.test_paper_decisions.DeclarationsTests.test_a_fixed_entry_refuses_a_plain_overwrite",
            source_path=SKILL_SCRIPTS / "paper_declarations.py",
        )
        _assert_guard_failed_under_mutation(self, proc)

    def test_mutation_5_over_invalidating_every_block_breaks_the_reopen_scope_test(self) -> None:
        proc = _run_against_mutant(
            "return {\n"
            "        qualified_id\n"
            "        for qualified_id, block in corpus.blocks.items()\n"
            "        if target_id in block.requires_facts or target_id in block.requires_declarations\n"
            "    }",
            "return set(corpus.blocks)",
            "tests.test_paper_decisions.DeclarationsTests.test_reopen_narrows_to_exactly_the_naming_blocks",
            source_path=SKILL_SCRIPTS / "paper_declarations.py",
        )
        _assert_guard_failed_under_mutation(self, proc)

    def test_mutation_6_swapping_the_declaration_validator_for_the_fact_one_breaks_the_vocabulary_guard(
        self,
    ) -> None:
        proc = _run_against_mutant(
            "paper_vocabulary.validate_declaration(declaration_id)",
            "paper_vocabulary.validate_fact(declaration_id)",
            "tests.test_paper_decisions.DeclarationsTests"
            ".test_recording_a_fact_as_a_declaration_refuses_unknown_declaration",
            source_path=SKILL_SCRIPTS / "paper_declarations.py",
        )
        _assert_guard_failed_under_mutation(self, proc)

    def test_mutation_8_a_declined_fact_counted_as_satisfied_breaks_the_read_satisfied_guard(
        self,
    ) -> None:
        proc = _run_against_mutant(
            'satisfied_facts = {\n'
            '        entry["id"] for entry in body["records"]\n'
            '        if entry["kind"] == "fact" and entry.get("fixed") and not entry.get("declined")\n'
            '    }',
            'satisfied_facts = {\n'
            '        entry["id"] for entry in body["records"]\n'
            '        if entry["kind"] == "fact" and entry.get("fixed")\n'
            '    }',
            "tests.test_paper_decisions.DeclinedFactTests"
            ".test_a_declined_fact_is_not_in_read_satisfied",
            source_path=SKILL_SCRIPTS / "paper_declarations.py",
        )
        _assert_guard_failed_under_mutation(self, proc)


class SkeletonInferenceTests(unittest.TestCase):
    """`the-phases-are-derived-not-remembered`, design.md D4;
    `specs/skeleton-startup/spec.md`, `Requirement: Both Decisions Are
    Re-Derived From Disk, Never Recalled` (tasks.md 7.2-7.5)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.forge_root = Path(self._tmp.name) / "repo"
        self.forge_root.mkdir()
        self.paper_dir = paper_scaffold.resolve_paper_dir(None, forge_root=self.forge_root)
        paper_scaffold.scaffold(self.paper_dir)
        self.corpus = paper_graph.Corpus(
            sections={},
            blocks={
                "related-work.rw-a": _block_record(
                    "related-work.rw-a", section="related-work",
                ),
                "materials-and-methods.mm-dataset": _block_record(
                    "materials-and-methods.mm-dataset", section="materials-and-methods",
                    requires_facts=["dataset"], optional=True,
                ),
                "experimental-setup.es-dataset": _block_record(
                    "experimental-setup.es-dataset", section="experimental-setup",
                    requires_facts=["dataset"], optional=True,
                ),
            },
            order_by_section={
                "related-work": ["related-work.rw-a"],
                "materials-and-methods": ["materials-and-methods.mm-dataset"],
                "experimental-setup": ["experimental-setup.es-dataset"],
            },
        )

    def test_es_dataset_opened_alone_reports_experimental_setup_from_opened_ids(self) -> None:
        """tasks.md 7.3."""
        paper_block.open_block(self.paper_dir, "experimental-setup.es-dataset", at_end=True)

        decisions = paper_declarations.infer_skeleton_decisions(self.paper_dir, self.corpus)

        self.assertEqual(decisions["datasetPlacement"], "experimental-setup")
        self.assertFalse(decisions["relatedWork"])

    def test_both_dataset_blocks_opened_refuses_dataset_placement_conflict(self) -> None:
        """tasks.md 7.4."""
        paper_block.open_block(self.paper_dir, "materials-and-methods.mm-dataset", at_end=True)
        paper_block.open_block(self.paper_dir, "experimental-setup.es-dataset", at_end=True)

        with self.assertRaises(Refused) as ctx:
            paper_declarations.infer_skeleton_decisions(self.paper_dir, self.corpus)

        self.assertEqual(ctx.exception.code, "DATASET_PLACEMENT_CONFLICT")
        self.assertIn("materials-and-methods.mm-dataset", ctx.exception.detail)
        self.assertIn("experimental-setup.es-dataset", ctx.exception.detail)

    def test_related_work_opened_reports_present(self) -> None:
        paper_block.open_block(self.paper_dir, "related-work.rw-a", at_end=True)

        decisions = paper_declarations.infer_skeleton_decisions(self.paper_dir, self.corpus)

        self.assertTrue(decisions["relatedWork"])
        self.assertEqual(decisions["datasetPlacement"], "undecided")

    def test_a_fresh_process_infers_the_same_decision_from_disk_alone_even_when_the_skeleton_fact_disagrees(
        self,
    ) -> None:
        """`specs/skeleton-startup/spec.md`, `Scenario: A fresh process
        infers the same decision from disk alone` -- and tasks.md 7.5's own
        mutation target: the recorded `skeleton` STRUCTURAL_FACT is set to
        the OPPOSITE placement of what is actually opened on disk. If the
        inference ever read `read_fact(paper_dir, "skeleton")` instead of
        `paper_block.read_status`, it would report the fact's answer
        (`materials-and-methods`), not disk's (`experimental-setup`)."""
        paper_declarations.set_fact(self.paper_dir, "skeleton", "materials-and-methods.mm-dataset")
        paper_block.open_block(self.paper_dir, "experimental-setup.es-dataset", at_end=True)

        decisions = paper_declarations.infer_skeleton_decisions(self.paper_dir, self.corpus)

        self.assertEqual(decisions["datasetPlacement"], "experimental-setup")


class SkeletonInferenceMutationTests(unittest.TestCase):
    """tasks.md 7.5: the inference must read disk, and only disk."""

    def test_mutation_reading_the_skeleton_fact_instead_of_read_status_fails(self) -> None:
        proc = _run_against_mutant(
            '    status = paper_block.read_status(paper_dir)\n'
            '    opened_ids = {block["id"] for block in status["blocks"]} & set(corpus.blocks)',
            '    opened_ids = {read_fact(paper_dir, "skeleton")} & set(corpus.blocks)',
            "tests.test_paper_decisions.SkeletonInferenceTests"
            ".test_a_fresh_process_infers_the_same_decision_from_disk_alone_even_when_the_skeleton_fact_disagrees",
            source_path=SKILL_SCRIPTS / "paper_declarations.py",
        )
        _assert_guard_failed_under_mutation(self, proc)


class DatasetPlacementCandidateDerivationTests(unittest.TestCase):
    """the-skill-stops-trusting-memory, item 1: `paper_declarations.
    MM_DATASET_ID`/`ES_DATASET_ID` are gone. `dataset_placement_candidates`
    derives the same two ids from the corpus's own `requires_facts`/
    `optional` shape instead -- SKILL.md:154-158, "block ids are shape
    only ... never validates an id against a list of what should exist"."""

    def test_against_the_real_shipped_corpus(self) -> None:
        """The real `sections/*.md` corpus is what motivated this change:
        `mm-dataset`/`es-dataset` both carry `requires_facts: ["dataset"]`
        and `optional: true` on disk (measured, not assumed)."""
        corpus = paper_graph.assemble_corpus(FORGE_ROOT / "sections")

        candidates = paper_declarations.dataset_placement_candidates(corpus)

        self.assertEqual(
            candidates,
            {
                "materials-and-methods": "materials-and-methods.mm-dataset",
                "experimental-setup": "experimental-setup.es-dataset",
            },
        )

    def test_a_corpus_with_no_candidate_at_all_refuses_absent(self) -> None:
        """Renaming `mm-dataset`'s `requires_facts` away from `dataset` (the
        exact scenario the task names: 'rename mm-dataset in its contract
        and infer_dataset_placement silently reports undecided forever')
        must now REFUSE, never silently degrade to `undecided`."""
        corpus = paper_graph.Corpus(
            sections={},
            blocks={
                "materials-and-methods.mm-preamble": _block_record(
                    "materials-and-methods.mm-preamble", section="materials-and-methods",
                ),
            },
            order_by_section={"materials-and-methods": ["materials-and-methods.mm-preamble"]},
        )

        with self.assertRaises(Refused) as ctx:
            paper_declarations.dataset_placement_candidates(corpus)

        self.assertEqual(ctx.exception.code, "DATASET_PLACEMENT_CANDIDATE_ABSENT")

    def test_a_section_with_two_candidates_refuses_ambiguous(self) -> None:
        corpus = paper_graph.Corpus(
            sections={},
            blocks={
                "materials-and-methods.mm-dataset": _block_record(
                    "materials-and-methods.mm-dataset", section="materials-and-methods",
                    requires_facts=["dataset"], optional=True,
                ),
                "materials-and-methods.mm-dataset-2": _block_record(
                    "materials-and-methods.mm-dataset-2", section="materials-and-methods",
                    requires_facts=["dataset"], optional=True,
                ),
            },
            order_by_section={
                "materials-and-methods": [
                    "materials-and-methods.mm-dataset", "materials-and-methods.mm-dataset-2",
                ],
            },
        )

        with self.assertRaises(Refused) as ctx:
            paper_declarations.dataset_placement_candidates(corpus)

        self.assertEqual(ctx.exception.code, "DATASET_PLACEMENT_CANDIDATE_AMBIGUOUS")
        self.assertIn("materials-and-methods.mm-dataset", ctx.exception.detail)
        self.assertIn("materials-and-methods.mm-dataset-2", ctx.exception.detail)

    def test_a_candidate_that_is_optional_but_does_not_require_dataset_is_not_a_candidate(
        self,
    ) -> None:
        """`optional` alone is not enough -- the block must also require the
        `dataset` fact. This is exactly the shape the OUT-OF-SCOPE
        `tests/test_paper_writing.py` fixture `_write_skeleton_corpus` used
        to carry (`optional: true`, no `requires_facts`) before this
        change; report note: that fixture needs `requires_facts:
        ["dataset"]` added to its `mm-dataset`/`es-dataset` blocks for
        `SkeletonTests` to keep passing under this derivation."""
        corpus = paper_graph.Corpus(
            sections={},
            blocks={
                "materials-and-methods.mm-dataset": _block_record(
                    "materials-and-methods.mm-dataset", section="materials-and-methods",
                    optional=True,
                ),
            },
            order_by_section={"materials-and-methods": ["materials-and-methods.mm-dataset"]},
        )

        with self.assertRaises(Refused) as ctx:
            paper_declarations.dataset_placement_candidates(corpus)

        self.assertEqual(ctx.exception.code, "DATASET_PLACEMENT_CANDIDATE_ABSENT")

    def test_mutation_dropping_the_optional_check_breaks_the_ambiguous_guard(self) -> None:
        """If `dataset_placement_candidates` ever stopped checking `block.
        optional` (matched on `requires_facts` alone), a section carrying a
        non-optional block that also requires `dataset` would silently
        become a second candidate, and the real shipped corpus -- which has
        several non-optional blocks requiring `dataset` alongside
        `mm-dataset`/`es-dataset`? No: measured, only the two optional ones
        require it. This mutation instead proves the REQUIRES_FACTS check
        is load-bearing: dropping it turns every optional block into a
        candidate, which the real corpus's `related-work`/other optional
        blocks (if any) would trip. To keep this hermetic, exercise it
        against a synthetic ambiguous fixture instead of relying on the
        real corpus's own shape drifting under test."""
        proc = _run_against_mutant(
            'if block.optional and "dataset" in block.requires_facts:',
            'if block.optional:',
            "tests.test_paper_decisions.DatasetPlacementCandidateDerivationTests"
            ".test_a_candidate_that_is_optional_but_does_not_require_dataset_is_not_a_candidate",
            source_path=SKILL_SCRIPTS / "paper_declarations.py",
        )
        _assert_guard_failed_under_mutation(self, proc)


class SkeletonExcludedIdsDerivationTests(unittest.TestCase):
    """`paper_cli._skeleton_excluded_ids` no longer reads `paper_
    declarations.MM_DATASET_ID`/`ES_DATASET_ID` -- it derives the excluded
    candidate from the corpus via `dataset_placement_candidates`."""

    def _corpus(self) -> "paper_graph.Corpus":
        return paper_graph.Corpus(
            sections={},
            blocks={
                "related-work.rw-a": _block_record("related-work.rw-a", section="related-work"),
                "materials-and-methods.mm-dataset": _block_record(
                    "materials-and-methods.mm-dataset", section="materials-and-methods",
                    requires_facts=["dataset"], optional=True,
                ),
                "experimental-setup.es-dataset": _block_record(
                    "experimental-setup.es-dataset", section="experimental-setup",
                    requires_facts=["dataset"], optional=True,
                ),
            },
            order_by_section={
                "related-work": ["related-work.rw-a"],
                "materials-and-methods": ["materials-and-methods.mm-dataset"],
                "experimental-setup": ["experimental-setup.es-dataset"],
            },
        )

    def test_materials_choice_excludes_the_experimental_setup_candidate(self) -> None:
        excluded = paper_cli._skeleton_excluded_ids(
            self._corpus(), related_work=True, dataset_in="materials",
        )

        self.assertEqual(excluded, {"experimental-setup.es-dataset"})

    def test_experimental_setup_choice_excludes_the_materials_candidate(self) -> None:
        excluded = paper_cli._skeleton_excluded_ids(
            self._corpus(), related_work=True, dataset_in="experimental-setup",
        )

        self.assertEqual(excluded, {"materials-and-methods.mm-dataset"})

    def test_a_corpus_with_no_dataset_candidate_at_all_refuses(self) -> None:
        """`build_skeleton`/`_skeleton_excluded_ids` can no longer silently
        open every block when the corpus names no dataset-placement
        candidate at all -- it refuses, naming the absence, exactly like
        `dataset_placement_candidates` itself."""
        corpus = paper_graph.Corpus(
            sections={}, blocks={}, order_by_section={},
        )

        with self.assertRaises(Refused) as ctx:
            paper_cli._skeleton_excluded_ids(corpus, related_work=True, dataset_in="materials")

        self.assertEqual(ctx.exception.code, "DATASET_PLACEMENT_CANDIDATE_ABSENT")


class ProvenanceTests(unittest.TestCase):
    """`specs/contract-provenance/spec.md` + the `block-substitution`
    delta (`specs/block-substitution/spec.md`)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.forge_root = Path(self._tmp.name) / "repo"
        self.forge_root.mkdir()
        self.paper_dir = paper_scaffold.resolve_paper_dir(None, forge_root=self.forge_root)
        paper_scaffold.scaffold(self.paper_dir)
        self.contract_path = Path(self._tmp.name) / "sections" / "intro.md"
        self.contract_path.parent.mkdir(parents=True, exist_ok=True)
        self.contract_path.write_bytes(b"contract v1\n")

    def _clock(self) -> str:
        return _FIXED_CLOCK

    def _open_and_substitute(self, block_id, body, *, contract=None):
        paper_block.open_block(self.paper_dir, block_id, at_end=True)
        return paper_block.substitute(
            self.paper_dir, block_id, new_body=body, contract=contract, clock=self._clock,
        )

    def test_provenanced_write_persists_the_write_time_baseline(self) -> None:
        self._open_and_substitute("intro", b"hello\n", contract=self.contract_path)

        tex_path = paper_block.resolve_main_tex(self.paper_dir)
        record = paper_provenance.read_provenance(tex_path.read_bytes())
        entry = next(r for r in record["body"]["records"] if r["block"] == "intro")
        expected_digest = hashlib.sha256(b"contract v1\n").hexdigest()
        self.assertEqual(entry["contract_sha256"], expected_digest)
        self.assertEqual(entry["generation"], 0)

    def test_provenanced_and_unprovenanced_writes_produce_identical_block_bytes(self) -> None:
        self._open_and_substitute("with-contract", b"same body\n", contract=self.contract_path)
        self._open_and_substitute("without-contract", b"same body\n")

        tex_path = paper_block.resolve_main_tex(self.paper_dir)
        status = paper_block.status(tex_path.read_bytes())
        digest_a = next(b["digest"] for b in status["blocks"] if b["id"] == "with-contract")
        digest_b = next(b["digest"] for b in status["blocks"] if b["id"] == "without-contract")
        self.assertEqual(digest_a, digest_b)

        record = paper_provenance.read_provenance(tex_path.read_bytes())
        provenanced_ids = {r["block"] for r in record["body"]["records"]}
        self.assertIn("with-contract", provenanced_ids)
        self.assertNotIn("without-contract", provenanced_ids)

    def test_unreadable_contract_refuses_before_any_write(self) -> None:
        missing = Path(self._tmp.name) / "sections" / "missing.md"
        paper_block.open_block(self.paper_dir, "intro", at_end=True)
        tex_path = paper_block.resolve_main_tex(self.paper_dir)
        pre = tex_path.read_bytes()

        with self.assertRaises(Refused) as ctx:
            paper_block.substitute(self.paper_dir, "intro", new_body=b"x\n", contract=missing)
        self.assertEqual(ctx.exception.code, "CONTRACT_UNREADABLE")
        self.assertEqual(
            tex_path.read_bytes(), pre, "no block byte and no provenance record on refusal"
        )

    def test_hand_edited_block_still_refuses_even_with_contract(self) -> None:
        self._open_and_substitute("intro", b"hello\n", contract=self.contract_path)
        tex_path = paper_block.resolve_main_tex(self.paper_dir)
        corrupted = tex_path.read_bytes().replace(b"hello", b"hellx", 1)
        tex_path.write_bytes(corrupted)

        with self.assertRaises(Refused) as ctx:
            paper_block.substitute(
                self.paper_dir, "intro", new_body=b"new\n", contract=self.contract_path,
            )
        self.assertEqual(ctx.exception.code, "BLOCK_HAND_EDITED")

    def test_a_block_written_without_contract_is_unprovenanced(self) -> None:
        self._open_and_substitute("methods", b"body\n")
        tex_path = paper_block.resolve_main_tex(self.paper_dir)
        self.assertIsNone(
            paper_provenance.drift(tex_path.read_bytes(), "methods", self.contract_path)
        )

    def test_drift_is_reported_on_a_single_byte_edit_and_block_is_untouched(self) -> None:
        self._open_and_substitute("results", b"body\n", contract=self.contract_path)
        tex_path = paper_block.resolve_main_tex(self.paper_dir)
        before = tex_path.read_bytes()

        self.contract_path.write_bytes(b"contract v2\n")

        self.assertTrue(
            paper_provenance.drift(tex_path.read_bytes(), "results", self.contract_path)
        )
        self.assertEqual(tex_path.read_bytes(), before, "drift detection must never rewrite a block")

    def test_no_drift_when_the_contract_is_unchanged(self) -> None:
        self._open_and_substitute("results", b"body\n", contract=self.contract_path)
        tex_path = paper_block.resolve_main_tex(self.paper_dir)

        self.assertFalse(
            paper_provenance.drift(tex_path.read_bytes(), "results", self.contract_path)
        )

    def test_provenance_hand_edited_refuses_and_writes_nothing(self) -> None:
        self._open_and_substitute("intro", b"hello\n", contract=self.contract_path)
        tex_path = paper_block.resolve_main_tex(self.paper_dir)
        pre = tex_path.read_bytes()
        record = paper_provenance.read_provenance(pre)
        corrupted = (
            pre[: record["begin_start"]]
            + pre[record["begin_start"]:record["end_end"]].replace(b"contract", b"contrbct", 1)
            + pre[record["end_end"]:]
        )
        tex_path.write_bytes(corrupted)

        paper_block.open_block(self.paper_dir, "second", at_end=True)
        with self.assertRaises(Refused) as ctx:
            paper_block.substitute(
                self.paper_dir, "second", new_body=b"x\n", contract=self.contract_path,
            )
        self.assertEqual(ctx.exception.code, "PROVENANCE_HAND_EDITED")


class ProvenanceMutationTests(unittest.TestCase):
    """Mutation 3 (design.md): recomputing the baseline at read time makes
    drift structurally undetectable."""

    def test_mutation_3_recomputing_the_baseline_at_read_time_breaks_drift_detection(self) -> None:
        proc = _run_against_mutant(
            "return current_digest != entry[\"contract_sha256\"]",
            "return current_digest != current_digest",
            "tests.test_paper_decisions.ProvenanceTests"
            ".test_drift_is_reported_on_a_single_byte_edit_and_block_is_untouched",
            source_path=SKILL_SCRIPTS / "paper_provenance.py",
        )
        _assert_guard_failed_under_mutation(self, proc)


class ObservationReportTests(unittest.TestCase):
    """`design.md`, `A fact the agent may observe is a partition, not a
    guideline` — the schema `insumos-observer`'s report is checked against."""

    def test_an_id_outside_the_observable_facts_refuses(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.validate_observation_report(
                {"contributions": {"satisfied": True, "evidence": [["x", "y"]]}}
            )
        self.assertEqual(ctx.exception.code, "NOT_AN_OBSERVABLE_FACT")
        self.assertIn("contributions", ctx.exception.detail)

    def test_implementation_and_results_sharing_one_evidence_path_refuses(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_declarations.validate_observation_report({
                "implementation": {"satisfied": True, "evidence": [["repo/code.py", "q1"]]},
                "results": {"satisfied": True, "evidence": [["repo/code.py", "q2"]]},
            })
        self.assertEqual(ctx.exception.code, "EVIDENCE_CONFLATED")

    def test_distinct_evidence_paths_are_accepted(self) -> None:
        paper_declarations.validate_observation_report({
            "implementation": {"satisfied": True, "evidence": [["repo/code.py", "q1"]]},
            "results": {"satisfied": True, "evidence": [["repo/results.json", "q2"]]},
            "formulation": {"satisfied": False, "evidence": []},
        })  # raises nothing


class ObservationReportMutationTests(unittest.TestCase):
    """Mutation 7 (design.md): accepting one evidence path for both facts
    breaks the conflation guard."""

    def test_mutation_7_accepting_one_shared_path_breaks_the_conflation_guard(self) -> None:
        proc = _run_against_mutant(
            "overlap = implementation_paths & results_paths",
            "overlap = set()",
            "tests.test_paper_decisions.ObservationReportTests"
            ".test_implementation_and_results_sharing_one_evidence_path_refuses",
            source_path=SKILL_SCRIPTS / "paper_declarations.py",
        )
        _assert_guard_failed_under_mutation(self, proc)


class PlanTests(unittest.TestCase):
    """`specs/contract-provenance/spec.md`, `Requirement: plan Aggregates
    Registry, Declarations, and Provenance`."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.forge_root = Path(self._tmp.name) / "repo"
        self.forge_root.mkdir()
        self.paper_dir = paper_scaffold.resolve_paper_dir(None, forge_root=self.forge_root)
        paper_scaffold.scaffold(self.paper_dir)
        self.guidance_dir = self.forge_root / "guidance"
        self.contract_path = Path(self._tmp.name) / "sections" / "intro.md"
        self.contract_path.parent.mkdir(parents=True, exist_ok=True)
        self.contract_path.write_bytes(b"contract v1\n")

    def _clock(self) -> str:
        return _FIXED_CLOCK

    def test_plan_aggregates_all_three_concerns_and_writes_nothing(self) -> None:
        classified = self.guidance_dir / "classified-folder"
        classified.mkdir(parents=True)
        (classified / ".paper-writing.json").write_text(
            json.dumps({"class": "evidence"}), encoding="utf-8",
        )
        (self.guidance_dir / "unclassified-folder").mkdir(parents=True)

        paper_declarations.set_declaration(
            self.paper_dir, "author-roles", "Alice", clock=self._clock,
        )

        paper_block.open_block(self.paper_dir, "current", at_end=True)
        paper_block.substitute(
            self.paper_dir, "current", new_body=b"x\n", contract=self.contract_path,
            clock=self._clock,
        )
        paper_block.open_block(self.paper_dir, "bare", at_end=True)
        paper_block.substitute(self.paper_dir, "bare", new_body=b"y\n")

        tex_path = paper_block.resolve_main_tex(self.paper_dir)
        before = tex_path.read_bytes()

        report = paper_cli.compute_plan(self.paper_dir, guidance_dir=self.guidance_dir)

        self.assertEqual(
            report["guidance"],
            {"classified-folder": "evidence", "unclassified-folder": "unclassified"},
        )
        recorded = next(
            r for r in report["declarations"]["records"] if r["id"] == "author-roles"
        )
        self.assertEqual(recorded["value"], "Alice")
        provenance_by_block = {p["block"]: p["state"] for p in report["provenance"]}
        self.assertEqual(provenance_by_block, {"current": "current", "bare": "unprovenanced"})

        self.assertEqual(tex_path.read_bytes(), before, "plan must never write")

    def test_plan_reports_drift_after_a_contract_edit(self) -> None:
        paper_block.open_block(self.paper_dir, "results", at_end=True)
        paper_block.substitute(
            self.paper_dir, "results", new_body=b"x\n", contract=self.contract_path,
            clock=self._clock,
        )
        self.contract_path.write_bytes(b"contract v2\n")

        report = paper_cli.compute_plan(self.paper_dir, guidance_dir=self.guidance_dir)

        provenance_by_block = {p["block"]: p["state"] for p in report["provenance"]}
        self.assertEqual(provenance_by_block["results"], "drifted")

    def test_one_contract_edit_flags_every_block_sharing_that_contract(self) -> None:
        """`specs/contract-provenance/spec.md`, `Requirement: Whole-File
        Hashing Over-Reports by Design`, `One edit flags every block of the
        section` — two blocks provenanced against the SAME contract file;
        editing one byte of it must drift BOTH, even though only one of the
        two ever reads the other's own guidance text. Under-reporting (a
        real drift going unreported for either block) is the failure this
        guards against; over-reporting both is the accepted, deliberate
        direction the spec names."""
        paper_block.open_block(self.paper_dir, "results-a", at_end=True)
        paper_block.substitute(
            self.paper_dir, "results-a", new_body=b"a\n", contract=self.contract_path,
            clock=self._clock,
        )
        paper_block.open_block(self.paper_dir, "results-b", at_end=True)
        paper_block.substitute(
            self.paper_dir, "results-b", new_body=b"b\n", contract=self.contract_path,
            clock=self._clock,
        )

        self.contract_path.write_bytes(b"contract v2\n")

        report = paper_cli.compute_plan(self.paper_dir, guidance_dir=self.guidance_dir)

        provenance_by_block = {p["block"]: p["state"] for p in report["provenance"]}
        self.assertEqual(provenance_by_block["results-a"], "drifted")
        self.assertEqual(provenance_by_block["results-b"], "drifted")


class InsumosObserverThreatMatrixTests(unittest.TestCase):
    """Threat matrix (design.md): process integration. `insumos-observer`'s
    frontmatter `tools` contains none of Write, Edit, Bash — the capability
    layer that survives non-compliance even if its own body were ever
    edited to suggest otherwise."""

    def test_frontmatter_tools_contains_none_of_write_edit_bash(self) -> None:
        path = AGENTS_DIR / "insumos-observer.md"
        text = path.read_text(encoding="utf-8")
        header = text.split("---\n", 2)[1]
        tools_line = next(line for line in header.splitlines() if line.startswith("tools:"))
        tools = {tool.strip() for tool in tools_line.split(":", 1)[1].split(",")}
        self.assertTrue(tools, "insumos-observer.md declares no tools at all")
        self.assertTrue(
            tools.isdisjoint({"Write", "Edit", "Bash"}),
            f"insumos-observer.md grants {tools & {'Write', 'Edit', 'Bash'}}, "
            "which lets it write a record or invoke declare directly",
        )


class ReopenInvalidatesProvenanceEndToEndTests(unittest.TestCase):
    """`specs/paper-declarations/spec.md`, `Requirement: Reopening
    Invalidates Exactly the Blocks That Named It` — driven through the real
    CLI end to end (`subprocess`, real `main.tex` on disk), the same shape
    the verify FAIL's own manual reproduction used to disprove this
    requirement.

    This is deliberately NOT a test against `paper_declarations.affected_blocks`
    or `paper_cli.compute_plan` called directly with a synthetic corpus —
    that is exactly the shape
    (`DeclarationsTests.test_reopen_narrows_to_exactly_the_naming_blocks`)
    that shipped green while the actual `declare --reopen` -> `plan` chain
    gave zero signal, because nothing outside that one test ever called
    `affected_blocks`. This test drives `scaffold` -> `declare` -> `open`
    -> `substitute --contract` -> `plan` -> `declare --reopen` -> `plan`
    as five real subprocess invocations of `paper_cli.py` and asserts the
    block's reported state changes from `current` to `drifted`.
    """

    def setUp(self) -> None:
        self.test_root = (
            FORGE_ROOT / "implementations"
            / f".paper-writing-cli-reopen-test-{os.getpid()}"
        )
        self.addCleanup(shutil.rmtree, self.test_root, ignore_errors=True)
        self.paper_dir = self.test_root / "paper"
        self.sections_dir = self.test_root / "sections"
        self.sections_dir.mkdir(parents=True)

        header = json.dumps({
            "section": "reopen-e2e",
            "position": 1,
            "blocks": [
                {
                    "id": "needs-repo-url",
                    "requires_facts": [],
                    "requires_declarations": ["repository-url"],
                    "citations": "none",
                }
            ],
        })
        self.contract_path = self.sections_dir / "reopen-e2e.md"
        self.contract_path.write_text(
            f"---\n{header}\n---\n\nProse body, never read for meaning.\n\n"
            "### External inputs\n\n### Internal chain\n",
            encoding="utf-8",
        )

    def _run(self, *args: str):
        proc = subprocess.run(
            [sys.executable, str(CLI), *args],
            capture_output=True, text=True, timeout=30,
        )
        return proc.returncode, json.loads(proc.stdout), proc.stderr

    def _plan_state_for(self, block_id: str) -> str:
        code, payload, stderr = self._run(
            "plan", "--paper", str(self.paper_dir), "--sections", str(self.sections_dir),
        )
        self.assertEqual(code, 0, stderr or payload)
        provenance_by_block = {p["block"]: p["state"] for p in payload["provenance"]}
        return provenance_by_block[block_id]

    def test_reopen_then_plan_stops_reporting_current(self) -> None:
        block_id = "reopen-e2e.needs-repo-url"

        code, payload, stderr = self._run("scaffold", "--paper", str(self.paper_dir))
        self.assertEqual(code, 0, stderr or payload)

        code, payload, stderr = self._run(
            "declare", "--paper", str(self.paper_dir),
            "--declaration", "repository-url", "--value", "https://example.org/repo",
        )
        self.assertEqual(code, 0, stderr or payload)

        code, payload, stderr = self._run(
            "open", "--paper", str(self.paper_dir),
            "--block", block_id, "--at-end",
        )
        self.assertEqual(code, 0, stderr or payload)

        body_path = self.test_root / "body.tex"
        body_path.write_text("some prose\n", encoding="utf-8")
        code, payload, stderr = self._run(
            "substitute", "--paper", str(self.paper_dir),
            "--block", block_id, "--body", str(body_path),
            "--contract", str(self.contract_path),
        )
        self.assertEqual(code, 0, stderr or payload)

        self.assertEqual(
            self._plan_state_for(block_id), "current",
            "sanity check before reopening: a freshly provenanced block "
            "against an unchanged contract must report current",
        )

        code, payload, stderr = self._run(
            "declare", "--paper", str(self.paper_dir), "--reopen", "repository-url",
        )
        self.assertEqual(code, 0, stderr or payload)

        self.assertEqual(
            self._plan_state_for(block_id), "drifted",
            "reopening 'repository-url' -- a declaration this exact block's "
            "own contract names in requires_declarations -- must stop plan "
            "from reporting the block current. This is the end-to-end "
            "chain the verify FAIL's manual reproduction ran to prove "
            "affected_blocks() had no real caller; a synthetic-corpus unit "
            "test on that helper alone is not sufficient evidence this "
            "requirement holds.",
        )


class ReadinessDeclinedFactsTests(unittest.TestCase):
    """`a-declined-fact-has-somewhere-to-live` + its `condition-that-expires`
    extension: the decisive proof that a decline actually changes what
    `readiness`/`phases` report, not merely what `declarations` stores --
    and that a LAPSED decline's condition is surfaced, never silently
    treated as still `declined` and never silently auto-unblocked. Same
    synthetic-contract fixture shape as `tests/test_paper_writing.py`'s
    `ReadinessBasisTests`. Three blocks:

    - `declined-only` requires ONLY the declined fact -> `"declined"` while
      the condition holds, `"blocked"` (with `stale_declines`) once it
      lapses.
    - `declined-plus-live` also requires a live (never declared) fact ->
      a decline must never mask a real gap, so this stays `"blocked"`
      regardless of the decline's own holds/stale state.
    - `declined-plus-declaration` also requires a never-declared
      declaration -> also stays `"blocked"` regardless.

    Driven through BOTH `compute_readiness_report` and `compute_phases`,
    which both compute from the same `paper_readiness.compute_readiness`
    call and must therefore agree.
    """

    REASON = "no experimental protocol exists yet in experiments/"
    CONDITION = {"type": "directory-empty-except", "path": "experiments", "ignore": [".gitkeep"]}

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.forge_root = Path(self._tmp.name) / "repo"
        self.forge_root.mkdir()
        self.paper_dir = paper_scaffold.resolve_paper_dir(None, forge_root=self.forge_root)
        paper_scaffold.scaffold(self.paper_dir)
        self.sections_dir = Path(self._tmp.name) / "sections"
        self.sections_dir.mkdir()
        header = json.dumps({
            "section": "declined-readiness",
            "position": 1,
            "blocks": [
                {
                    "id": "declined-only", "requires_facts": ["experimental-design"],
                    "requires_declarations": [], "citations": "none",
                },
                {
                    "id": "declined-plus-live",
                    "requires_facts": ["experimental-design", "dataset"],
                    "requires_declarations": [], "citations": "none",
                },
                {
                    "id": "declined-plus-declaration",
                    "requires_facts": ["experimental-design"],
                    "requires_declarations": ["repository-url"], "citations": "none",
                },
            ],
        })
        (self.sections_dir / "01-declined-readiness.md").write_text(
            f"---\n{header}\n---\n\nProse.\n\n### External inputs\n\nNone.\n\n"
            "### Internal chain\n\nNone.\n",
            encoding="utf-8",
        )
        paper_declarations.decline_fact(
            self.paper_dir, "experimental-design", self.REASON, self.CONDITION,
        )

    def _lapse_the_condition(self) -> None:
        """Writes a real file into the condition's own named path, so
        `_evaluate_condition` reports the decline's condition as no longer
        holding -- the stale/lapsed state, never touched by `--reopen`."""
        experiments_dir = self.forge_root / "experiments"
        experiments_dir.mkdir(parents=True, exist_ok=True)
        (experiments_dir / "protocol.md").write_text("a real protocol\n", encoding="utf-8")

    def _readiness_block(self, block_id: str) -> dict:
        report = paper_cli.compute_readiness_report(self.sections_dir, paper_dir=self.paper_dir)
        return next(b for b in report["blocks"] if b["block"] == block_id)

    def _phases_block(self, block_id: str) -> dict:
        phases = paper_cli.compute_phases(self.paper_dir, self.sections_dir)
        for wave in phases["waves"]:
            for block in wave["blocks"]:
                if block["block"] == block_id:
                    return block
        raise AssertionError(f"{block_id!r} not found in any wave")

    # --- state 1: the condition holds -----------------------------------

    def test_readiness_reports_declined_only_block_as_declined(self) -> None:
        block = self._readiness_block("declined-readiness.declined-only")
        self.assertEqual(block["status"], "declined")
        self.assertEqual(
            block["declined_facts"],
            [{"fact": "experimental-design", "reason": self.REASON}],
        )
        self.assertEqual(block.get("stale_declines", []), [])

    def test_phases_agrees_declined_only_block_is_declined(self) -> None:
        block = self._phases_block("declined-readiness.declined-only")
        self.assertEqual(block["status"], "declined")
        self.assertEqual(
            block["declined_facts"],
            [{"fact": "experimental-design", "reason": self.REASON}],
        )
        self.assertEqual(block["stale_declines"], [])

    # --- state 2: the condition has lapsed (stale) ----------------------

    def test_readiness_reports_a_lapsed_decline_as_blocked_with_stale_declines(self) -> None:
        self._lapse_the_condition()

        block = self._readiness_block("declined-readiness.declined-only")

        self.assertEqual(
            block["status"], "blocked",
            "a lapsed decline must never still read as declined -- and must "
            "never be silently auto-unblocked into writable either",
        )
        self.assertEqual(block.get("declined_facts", []), [])
        self.assertEqual(len(block["stale_declines"]), 1)
        stale = block["stale_declines"][0]
        self.assertEqual(stale["fact"], "experimental-design")
        self.assertEqual(stale["reason"], self.REASON)
        self.assertEqual(stale["condition"], self.CONDITION)
        self.assertIn("protocol.md", stale["detail"])

    def test_phases_agrees_a_lapsed_decline_is_blocked_with_stale_declines(self) -> None:
        self._lapse_the_condition()

        block = self._phases_block("declined-readiness.declined-only")

        self.assertEqual(block["status"], "blocked")
        self.assertEqual(block["declined_facts"], [])
        self.assertEqual(len(block["stale_declines"]), 1)
        self.assertEqual(block["stale_declines"][0]["fact"], "experimental-design")
        self.assertIn("protocol.md", block["stale_declines"][0]["detail"])

    # --- state 3: mixed / regression -- a decline never masks a real gap,
    # re-verified against the v2 three-bucket logic under BOTH the holding
    # and the lapsed condition, so this cannot regress silently either way

    def test_readiness_reports_declined_plus_live_fact_as_blocked(self) -> None:
        block = self._readiness_block("declined-readiness.declined-plus-live")
        self.assertEqual(block["status"], "blocked")

    def test_readiness_reports_declined_plus_missing_declaration_as_blocked(self) -> None:
        block = self._readiness_block("declined-readiness.declined-plus-declaration")
        self.assertEqual(block["status"], "blocked")

    def test_phases_agrees_declined_plus_live_fact_is_blocked(self) -> None:
        block = self._phases_block("declined-readiness.declined-plus-live")
        self.assertEqual(block["status"], "blocked")

    def test_phases_agrees_declined_plus_missing_declaration_is_blocked(self) -> None:
        block = self._phases_block("declined-readiness.declined-plus-declaration")
        self.assertEqual(block["status"], "blocked")

    def test_readiness_reports_declined_plus_live_fact_as_blocked_even_once_lapsed(self) -> None:
        self._lapse_the_condition()
        block = self._readiness_block("declined-readiness.declined-plus-live")
        self.assertEqual(block["status"], "blocked")

    def test_readiness_reports_declined_plus_missing_declaration_as_blocked_even_once_lapsed(
        self,
    ) -> None:
        self._lapse_the_condition()
        block = self._readiness_block("declined-readiness.declined-plus-declaration")
        self.assertEqual(block["status"], "blocked")


class ReadinessDeclinedFactsMutationTests(unittest.TestCase):
    """The literal 'a mutation that drops the decline-awareness from the
    readiness computation must turn it red' requirement: forcing
    `compute_block_readiness` to always report `"blocked"` for a missing
    fact, even when every missing fact is declined and holding, must
    redden the decisive proof above -- and a mutation that stops
    `read_declined` from re-evaluating the condition at all (treating a
    decline as permanent) must redden the lapsed-case proof."""

    def test_mutation_9_always_blocked_breaks_the_declined_only_readiness_guard(self) -> None:
        proc = _run_against_mutant(
            'status = (\n'
            '            "declined" if (declined_missing and not stale_missing and not live_missing)\n'
            '            else "blocked"\n'
            '        )',
            'status = "blocked"',
            "tests.test_paper_decisions.ReadinessDeclinedFactsTests"
            ".test_readiness_reports_declined_only_block_as_declined",
            source_path=SKILL_SCRIPTS / "paper_readiness.py",
        )
        _assert_guard_failed_under_mutation(self, proc)

    def test_mutation_10_never_re_evaluating_the_condition_breaks_the_lapsed_case_guard(
        self,
    ) -> None:
        proc = _run_against_mutant(
            'holds, detail = _evaluate_condition(root, entry["condition"])',
            'holds, detail = True, "always holds"',
            "tests.test_paper_decisions.ReadinessDeclinedFactsTests"
            ".test_readiness_reports_a_lapsed_decline_as_blocked_with_stale_declines",
            source_path=SKILL_SCRIPTS / "paper_declarations.py",
        )
        _assert_guard_failed_under_mutation(self, proc)


class SourceAvailableTests(unittest.TestCase):
    """`the-skill-stops-trusting-memory`, item 5: `paper_declarations.
    source_available` -- gitignore-blind by construction, unlike `fd`/`rg`
    (both honor `.gitignore` by default, which is exactly what made an
    agent's shell exploration report a populated `implementations/<repo>/`
    and an 8-paper `guidance/` tree both ABSENT/EMPTY in the session that
    produced this fix)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_a_non_existent_root_is_not_available(self) -> None:
        self.assertFalse(paper_declarations.source_available(self.root / "does-not-exist"))

    def test_an_existing_but_empty_root_is_not_available(self) -> None:
        target = self.root / "empty"
        target.mkdir()
        self.assertFalse(paper_declarations.source_available(target))

    def test_a_populated_root_is_available(self) -> None:
        target = self.root / "populated"
        target.mkdir()
        (target / "file.txt").write_text("x", encoding="utf-8")
        self.assertTrue(paper_declarations.source_available(target))

    def test_a_root_hidden_from_git_by_gitignore_is_still_measured_available(self) -> None:
        """The exact defect: a `.gitignore` pattern that empties this tree
        for `fd`/`rg` must NOT empty it for this function -- it never
        shells out, by construction, not by discipline."""
        target = self.root / "gitignored"
        target.mkdir()
        (self.root / ".gitignore").write_text(f"{target.name}/*\n", encoding="utf-8")
        (target / "real-content.py").write_text("print(1)", encoding="utf-8")

        self.assertTrue(paper_declarations.source_available(target))


class ReconcileObservationReportTests(unittest.TestCase):
    """`reconcile_observation_report`: the pure comparison `observe`'s new
    disk-truth gate is built on."""

    def test_an_unsatisfied_fact_with_no_evidence_while_its_root_is_available_disagrees(
        self,
    ) -> None:
        """`implementation` AND `results` both map to the `implementation`
        root (`.claude/agents/insumos-observer.md`); `results` is reported
        satisfied here precisely so only `implementation` disagrees."""
        report = {
            "implementation": {"satisfied": False, "evidence": []},
            "results": {"satisfied": True, "evidence": [["out.log", "q"]]},
        }
        measured = {"implementation": True}

        disagreements = paper_declarations.reconcile_observation_report(report, measured)

        self.assertEqual(len(disagreements), 1)
        self.assertEqual(disagreements[0]["fact"], "implementation")
        self.assertEqual(disagreements[0]["source"], "implementation")

    def test_an_unsatisfied_fact_agrees_when_its_root_is_measurably_unavailable(self) -> None:
        report = {
            "implementation": {"satisfied": False, "evidence": []},
            "results": {"satisfied": False, "evidence": []},
        }
        measured = {"implementation": False}

        self.assertEqual(paper_declarations.reconcile_observation_report(report, measured), [])

    def test_a_satisfied_fact_never_disagrees_regardless_of_measurement(self) -> None:
        report = {
            "implementation": {"satisfied": True, "evidence": [["a", "b"]]},
            "results": {"satisfied": True, "evidence": [["c", "d"]]},
        }
        measured = {"implementation": True}

        self.assertEqual(paper_declarations.reconcile_observation_report(report, measured), [])

    def test_an_unmeasured_root_is_never_reconciled_against(self) -> None:
        """`measured` naming nothing for a fact's own root means that root
        was never checked -- never treated as "measured unavailable"."""
        report = {"implementation": {"satisfied": False, "evidence": []}}

        self.assertEqual(paper_declarations.reconcile_observation_report(report, {}), [])

    def test_an_unsatisfied_fact_that_still_carries_evidence_never_disagrees(self) -> None:
        """`evidence` non-empty but `satisfied` false is a real, honest
        report shape (a partial finding the agent judged insufficient) --
        never flagged, since SOME evidence was actually found."""
        report = {
            "implementation": {"satisfied": False, "evidence": [["partial.py", "q"]]},
            "results": {"satisfied": True, "evidence": [["c", "d"]]},
        }
        measured = {"implementation": True}

        self.assertEqual(paper_declarations.reconcile_observation_report(report, measured), [])

    def test_every_fact_is_named_independently_never_averaged_into_one_verdict(self) -> None:
        report = {
            "formulation": {"satisfied": False, "evidence": []},
            "dataset": {"satisfied": True, "evidence": [["p", "q"]]},
        }
        measured = {"proposals": True}

        disagreements = paper_declarations.reconcile_observation_report(report, measured)

        self.assertEqual([d["fact"] for d in disagreements], ["formulation"])


class ReconcileObservationReportMutationTests(unittest.TestCase):
    def test_mutation_dropping_the_no_evidence_check_over_reports_disagreement(self) -> None:
        """Without the `not evidence` half, a fact reported SATISFIED (with
        real evidence) over an available root would also flag as a
        disagreement -- exactly backwards, since a satisfied report
        AGREES with an available source."""
        proc = _run_against_mutant(
            "if not satisfied and not evidence:",
            "if not satisfied:",
            "tests.test_paper_decisions.ReconcileObservationReportTests"
            ".test_an_unsatisfied_fact_that_still_carries_evidence_never_disagrees",
            source_path=SKILL_SCRIPTS / "paper_declarations.py",
        )
        _assert_guard_failed_under_mutation(self, proc)

    def test_mutation_treating_an_unmeasured_root_as_available_breaks_the_guard(self) -> None:
        proc = _run_against_mutant(
            "if root_name not in measured or not measured[root_name]:",
            "if not measured.get(root_name, True):",
            "tests.test_paper_decisions.ReconcileObservationReportTests"
            ".test_an_unmeasured_root_is_never_reconciled_against",
            source_path=SKILL_SCRIPTS / "paper_declarations.py",
        )
        _assert_guard_failed_under_mutation(self, proc)


class ObserveDiskReconciliationTests(unittest.TestCase):
    """`paper_cli.compute_observation`: `observe`'s own end-to-end
    disk-truth reconciliation, injected paths (no argparse defaulting)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.report_path = self.root / "report.json"

    def _write_report(self, obj) -> None:
        self.report_path.write_text(json.dumps(obj), encoding="utf-8")

    def test_the_measured_defect_scenario_now_refuses(self) -> None:
        """The exact scenario the task names: the orchestrator reported the
        implementation repository ABSENT when it was actually populated,
        four times, because `fd`/`rg` honor `.gitignore`."""
        self._write_report({
            "implementation": {"satisfied": False, "evidence": []},
            "results": {"satisfied": False, "evidence": []},
        })
        implementation_dir = self.root / "implementations" / "Domain_Adaptation"
        implementation_dir.mkdir(parents=True)
        (implementation_dir / "train.py").write_text("print(1)", encoding="utf-8")
        (self.root / ".gitignore").write_text("implementations/*\n", encoding="utf-8")

        with self.assertRaises(Refused) as ctx:
            paper_cli.compute_observation(
                self.report_path, implementation_dir=implementation_dir,
            )

        self.assertEqual(ctx.exception.code, "OBSERVATION_DISK_CONFLICT")
        self.assertIn("implementation", ctx.exception.detail)

    def test_an_honest_absent_report_over_an_empty_root_is_accepted(self) -> None:
        self._write_report({"implementation": {"satisfied": False, "evidence": []}})
        implementation_dir = self.root / "implementations" / "empty-repo"
        implementation_dir.mkdir(parents=True)

        result = paper_cli.compute_observation(self.report_path, implementation_dir=implementation_dir)

        self.assertEqual(result["measured"], {"implementation": False})
        self.assertEqual(result["satisfied"], [])

    def test_no_roots_given_performs_no_reconciliation_at_all(self) -> None:
        """Backward compatible: an `observe` call naming no root reconciles
        against nothing and behaves exactly as before this change."""
        self._write_report({"implementation": {"satisfied": False, "evidence": []}})

        result = paper_cli.compute_observation(self.report_path)

        self.assertEqual(result["measured"], {})

    def test_writes_nothing_including_on_a_disk_conflict_refusal(self) -> None:
        self._write_report({"implementation": {"satisfied": False, "evidence": []}})
        implementation_dir = self.root / "impl"
        implementation_dir.mkdir()
        (implementation_dir / "code.py").write_text("x", encoding="utf-8")
        before = sorted(str(p) for p in self.root.rglob("*"))

        with self.assertRaises(Refused):
            paper_cli.compute_observation(self.report_path, implementation_dir=implementation_dir)

        after = sorted(str(p) for p in self.root.rglob("*"))
        self.assertEqual(before, after)


class ObserveCliTests(unittest.TestCase):
    """`paper_cli.cmd_observe`: the CLI front door, real, non-injectable
    `FORGE_ROOT` defaults for `--proposals`/`--experiments`, path
    containment for all three flags -- same `implementations/` convention
    `SkeletonPathContainmentTests` (`tests/test_paper_writing.py`) uses."""

    def setUp(self) -> None:
        self.test_root = (
            FORGE_ROOT / "implementations"
            / f".paper-writing-observe-cli-test-{os.getpid()}-{uuid.uuid4().hex[:8]}"
        )
        self.addCleanup(shutil.rmtree, self.test_root, ignore_errors=True)
        self.test_root.mkdir(parents=True)

    def _args(self, **overrides) -> argparse.Namespace:
        base = dict(report=None, proposals=None, experiments=None, implementation=None)
        base.update(overrides)
        return argparse.Namespace(**base)

    def _write_report(self, obj) -> Path:
        path = self.test_root / "report.json"
        path.write_text(json.dumps(obj), encoding="utf-8")
        return path

    def test_an_implementation_path_outside_the_repository_refuses_containment(self) -> None:
        report_path = self._write_report({"implementation": {"satisfied": False, "evidence": []}})
        outside = Path(tempfile.gettempdir()) / f"paper-writing-observe-outside-{os.getpid()}"

        with self.assertRaises(Refused) as ctx:
            paper_cli.cmd_observe(self._args(report=str(report_path), implementation=str(outside)))

        self.assertEqual(ctx.exception.code, "PAPER_OUTSIDE_REPOSITORY")

    def test_an_implementation_path_inside_the_repository_reconciles_against_it(self) -> None:
        report_path = self._write_report({"implementation": {"satisfied": False, "evidence": []}})
        implementation_dir = self.test_root / "impl"
        implementation_dir.mkdir()
        (implementation_dir / "main.py").write_text("x", encoding="utf-8")

        with self.assertRaises(Refused) as ctx:
            paper_cli.cmd_observe(
                self._args(report=str(report_path), implementation=str(implementation_dir)),
            )

        self.assertEqual(ctx.exception.code, "OBSERVATION_DISK_CONFLICT")

    def test_omitting_implementation_skips_that_reconciliation(self) -> None:
        report_path = self._write_report({"implementation": {"satisfied": False, "evidence": []}})

        result = paper_cli.cmd_observe(self._args(report=str(report_path)))

        self.assertNotIn("implementation", result["measured"])


class CouplingsShapeValidationTests(unittest.TestCase):
    """`the-skill-stops-trusting-memory`, item 4: `paper_couplings.
    validate_couplings_shape` -- the floor every real `paper_verify.py`
    check reads, checked at WRITE time rather than surfacing later as a
    confusing `unmeasured`."""

    def test_a_non_object_record_refuses(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_couplings.validate_couplings_shape([1, 2, 3])
        self.assertEqual(ctx.exception.code, "COUPLINGS_RECORD_MALFORMED")

    def test_a_record_with_no_blocks_key_refuses(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_couplings.validate_couplings_shape({"facts": {}})
        self.assertEqual(ctx.exception.code, "COUPLINGS_RECORD_MALFORMED")

    def test_a_record_with_an_empty_blocks_object_refuses(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_couplings.validate_couplings_shape({"blocks": {}})
        self.assertEqual(ctx.exception.code, "COUPLINGS_RECORD_MALFORMED")

    def test_a_minimal_valid_record_is_accepted(self) -> None:
        paper_couplings.validate_couplings_shape({"blocks": {"a": {}}})

    def test_contributions_that_is_not_a_list_of_strings_refuses(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_couplings.validate_couplings_shape(
                {"blocks": {"a": {}}, "facts": {"contributions": "not-a-list"}}
            )
        self.assertEqual(ctx.exception.code, "COUPLINGS_RECORD_MALFORMED")

    def test_a_chain_link_missing_word_refuses(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_couplings.validate_couplings_shape(
                {"blocks": {"a": {}}, "chain": {"links": [{"not_word": "x"}]}}
            )
        self.assertEqual(ctx.exception.code, "COUPLINGS_RECORD_MALFORMED")

    def test_artefact_cells_that_are_not_strings_refuse(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_couplings.validate_couplings_shape(
                {"blocks": {"a": {}}, "artefacts": {"setup_cells": [1, 2]}}
            )
        self.assertEqual(ctx.exception.code, "COUPLINGS_RECORD_MALFORMED")

    def test_a_future_work_direction_missing_a_required_key_refuses(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_couplings.validate_couplings_shape(
                {
                    "blocks": {"a": {}},
                    "future_work": {"directions": [{"id": "d1", "limitation": "L1"}]},
                }
            )
        self.assertEqual(ctx.exception.code, "COUPLINGS_RECORD_MALFORMED")

    def test_a_fully_populated_record_is_accepted(self) -> None:
        paper_couplings.validate_couplings_shape({
            "blocks": {"a": {}, "b": {}},
            "facts": {"contributions": ["x", "y"], "limitations": ["L1"]},
            "chain": {"links": [{"word": "x"}]},
            "artefacts": {"setup_cells": ["c1"], "results_artefacts": ["c1"]},
            "future_work": {
                "directions": [{"id": "d1", "limitation": "L1", "cite_key": "smith2024"}],
            },
        })


class CouplingsProducerTests(unittest.TestCase):
    """`couplings` writes `paper/couplings.json` whole, atomically -- the
    producer `verify` never had. `DECLARATION_RECORD_ABSENT` refuses before
    this change; it must stop refusing once `couplings` has written a
    minimally valid record, with no other change to `verify` itself."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.forge_root = Path(self._tmp.name) / "repo"
        self.forge_root.mkdir()
        self.paper_dir = paper_scaffold.resolve_paper_dir(None, forge_root=self.forge_root)
        paper_scaffold.scaffold(self.paper_dir)
        self.sections_dir = Path(self._tmp.name) / "sections"
        self.sections_dir.mkdir()

    def test_write_couplings_creates_the_file_with_the_given_content(self) -> None:
        result = paper_couplings.write_couplings(self.paper_dir, {"blocks": {"intro.b1": {}}})

        path = self.paper_dir / paper_coupling_evidence.COUPLINGS_RECORD_NAME
        self.assertTrue(path.is_file())
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"blocks": {"intro.b1": {}}})
        self.assertEqual(result["blocks"], ["intro.b1"])

    def test_write_couplings_rejects_a_malformed_record_and_writes_nothing(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_couplings.write_couplings(self.paper_dir, {"blocks": {}})

        self.assertEqual(ctx.exception.code, "COUPLINGS_RECORD_MALFORMED")
        self.assertFalse((self.paper_dir / paper_coupling_evidence.COUPLINGS_RECORD_NAME).exists())

    def test_write_couplings_rebuilds_whole_never_merges_with_a_prior_write(self) -> None:
        paper_couplings.write_couplings(self.paper_dir, {"blocks": {"a": {}}, "facts": {"contributions": ["x"]}})

        paper_couplings.write_couplings(self.paper_dir, {"blocks": {"b": {}}})

        path = self.paper_dir / paper_coupling_evidence.COUPLINGS_RECORD_NAME
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"blocks": {"b": {}}})

    def test_verify_refuses_declaration_record_absent_before_couplings_runs(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)
        self.assertEqual(ctx.exception.code, "DECLARATION_RECORD_ABSENT")

    def test_verify_stops_refusing_declaration_record_absent_once_couplings_has_run(self) -> None:
        """The end-to-end proof item 4 exists for: `verify`, a shipped verb
        with seven checks, could not be run at all on a real paper before
        this change. It can now, with zero changes to `verify`/`paper_
        coupling_evidence.py` themselves."""
        paper_couplings.write_couplings(self.paper_dir, {"blocks": {"intro.b1": {}}})

        evidence = paper_coupling_evidence.gather(self.paper_dir, self.sections_dir)

        self.assertEqual(evidence.record, {"blocks": {"intro.b1": {}}})


class CouplingsCliTests(unittest.TestCase):
    """`paper_cli.cmd_couplings`: the `--file <path|->` front door, and its
    own path-containment/JSON-readability refusals."""

    def setUp(self) -> None:
        self.test_root = (
            FORGE_ROOT / "implementations"
            / f".paper-writing-couplings-cli-test-{os.getpid()}-{uuid.uuid4().hex[:8]}"
        )
        self.addCleanup(shutil.rmtree, self.test_root, ignore_errors=True)
        self.paper_dir = self.test_root / "paper"
        paper_scaffold.scaffold(self.paper_dir)

    def _write_input(self, text: str) -> Path:
        path = self.test_root / "couplings-input.json"
        path.write_text(text, encoding="utf-8")
        return path

    def test_a_valid_file_is_written_to_paper_couplings_json(self) -> None:
        input_path = self._write_input(json.dumps({"blocks": {"a": {}}}))
        args = argparse.Namespace(paper=str(self.paper_dir), file=str(input_path))

        result = paper_cli.cmd_couplings(args)

        self.assertEqual(result["blocks"], ["a"])
        written = self.paper_dir / paper_coupling_evidence.COUPLINGS_RECORD_NAME
        self.assertEqual(json.loads(written.read_text(encoding="utf-8")), {"blocks": {"a": {}}})

    def test_invalid_json_refuses_input_unreadable_and_writes_nothing(self) -> None:
        input_path = self._write_input("{not-json")
        args = argparse.Namespace(paper=str(self.paper_dir), file=str(input_path))

        with self.assertRaises(Refused) as ctx:
            paper_cli.cmd_couplings(args)

        self.assertEqual(ctx.exception.code, "COUPLINGS_INPUT_UNREADABLE")
        self.assertFalse((self.paper_dir / paper_coupling_evidence.COUPLINGS_RECORD_NAME).exists())

    def test_a_missing_file_refuses_input_unreadable(self) -> None:
        args = argparse.Namespace(
            paper=str(self.paper_dir), file=str(self.test_root / "does-not-exist.json"),
        )

        with self.assertRaises(Refused) as ctx:
            paper_cli.cmd_couplings(args)

        self.assertEqual(ctx.exception.code, "COUPLINGS_INPUT_UNREADABLE")

    def test_a_file_outside_the_repository_refuses_path_containment(self) -> None:
        outside = Path(tempfile.gettempdir()) / f"paper-writing-couplings-outside-{os.getpid()}.json"
        outside.write_text(json.dumps({"blocks": {"a": {}}}), encoding="utf-8")
        self.addCleanup(outside.unlink, missing_ok=True)
        args = argparse.Namespace(paper=str(self.paper_dir), file=str(outside))

        with self.assertRaises(Refused) as ctx:
            paper_cli.cmd_couplings(args)

        self.assertEqual(ctx.exception.code, "PAPER_OUTSIDE_REPOSITORY")


class CouplingsMutationTests(unittest.TestCase):
    """Proves the write-before-validate ordering and the malformed-shape
    guard are both load-bearing."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.forge_root = Path(self._tmp.name) / "repo"
        self.forge_root.mkdir()
        self.paper_dir = paper_scaffold.resolve_paper_dir(None, forge_root=self.forge_root)
        paper_scaffold.scaffold(self.paper_dir)

    def test_mutation_skipping_validation_before_write_lets_a_malformed_record_through(
        self,
    ) -> None:
        proc = _run_against_mutant(
            "    validate_couplings_shape(record)\n"
            "    path = paper_dir / paper_coupling_evidence.COUPLINGS_RECORD_NAME",
            "    path = paper_dir / paper_coupling_evidence.COUPLINGS_RECORD_NAME",
            "tests.test_paper_decisions.CouplingsProducerTests"
            ".test_write_couplings_rejects_a_malformed_record_and_writes_nothing",
            source_path=SKILL_SCRIPTS / "paper_couplings.py",
        )
        _assert_guard_failed_under_mutation(self, proc)

    def test_mutation_accepting_an_empty_blocks_object_breaks_the_shape_guard(self) -> None:
        proc = _run_against_mutant(
            'if not isinstance(blocks, dict) or not blocks:',
            'if not isinstance(blocks, dict):',
            "tests.test_paper_decisions.CouplingsShapeValidationTests"
            ".test_a_record_with_an_empty_blocks_object_refuses",
            source_path=SKILL_SCRIPTS / "paper_couplings.py",
        )
        _assert_guard_failed_under_mutation(self, proc)


if __name__ == "__main__":
    unittest.main()
