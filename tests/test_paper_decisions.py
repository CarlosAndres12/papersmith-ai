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

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
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


_FIXED_CLOCK = "2024-01-01T00:00:00+00:00"


def _block_record(qualified_id: str, *, requires_facts=(), requires_declarations=()):
    """A minimal, real `paper_graph.BlockRecord` — `affected_blocks` only
    ever reads `.requires_facts`/`.requires_declarations`, so the other
    fields are filled with harmless placeholders rather than driven through
    a full `assemble_corpus` disk fixture."""
    return paper_graph.BlockRecord(
        section="synthetic",
        block_id=qualified_id.split(".")[-1],
        qualified_id=qualified_id,
        block_index=0,
        position=1,
        requires_facts=tuple(requires_facts),
        requires_declarations=tuple(requires_declarations),
        citations="none",
        optional=False,
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
            f"---\n{header}\n---\n\nProse body, never read for meaning.\n",
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


if __name__ == "__main__":
    unittest.main()
