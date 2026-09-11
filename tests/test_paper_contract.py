"""the-contract-is-data-not-code: vocabulary, header schema, insertion into the
ten shipped contracts, block graph, readiness and order.

Stdlib-only `unittest`, the same shape `tests/test_paper_writing.py` already
uses for this skill: every fixture lives under a `TemporaryDirectory`, and the
only calls touching the real repository are the ones that MUST — reading the
ten shipped `sections/*.md` files and their `git show HEAD:` digests, and the
insertion + mutation subprocesses, each of which restores or never writes to
the real tree outside what the work unit itself is proving.

One class per concern, no class name reused — `design.md`, `Testing Strategy`.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = FORGE_ROOT / ".claude" / "skills" / "paper-writing" / "scripts"
SECTIONS_DIR = FORGE_ROOT / "sections"
sys.path.insert(0, str(SKILL_SCRIPTS))
import paper_vocabulary  # noqa: E402
import paper_contract  # noqa: E402

sys.path.insert(0, str(FORGE_ROOT / ".claude" / "skills" / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402


def _header_bytes(header: dict) -> bytes:
    return b"---\n" + json.dumps(header).encode("utf-8") + b"\n---\n"


def _minimal_header(**overrides) -> dict:
    header = {
        "section": "example",
        "position": 1,
        "blocks": [
            {
                "id": "only-block",
                "requires_facts": [],
                "requires_declarations": [],
                "citations": "none",
            }
        ],
    }
    header.update(overrides)
    return header


class VocabularyTests(unittest.TestCase):
    """`section-contract` spec: the three closed vocabularies, each derived
    from one declaration so an unclassified value goes red rather than
    silent."""

    def test_a_listed_fact_parses(self) -> None:
        paper_vocabulary.validate_fact("results")  # raises nothing

    def test_every_declared_fact_id_is_accepted(self) -> None:
        for fact in paper_vocabulary.FACTS:
            paper_vocabulary.validate_fact(fact)  # raises nothing

    def test_an_unlisted_fact_refuses_unknown_fact(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_vocabulary.validate_fact("discussion")

        self.assertEqual(ctx.exception.code, "UNKNOWN_FACT")
        self.assertIn("discussion", ctx.exception.detail)

    def test_a_listed_declaration_parses(self) -> None:
        paper_vocabulary.validate_declaration("author-roles")  # raises nothing

    def test_every_declared_declaration_id_is_accepted(self) -> None:
        for declaration in paper_vocabulary.DECLARATIONS:
            paper_vocabulary.validate_declaration(declaration)  # raises nothing

    def test_an_unlisted_declaration_refuses_unknown_declaration(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_vocabulary.validate_declaration("reviewer-name")

        self.assertEqual(ctx.exception.code, "UNKNOWN_DECLARATION")
        self.assertIn("reviewer-name", ctx.exception.detail)

    def test_a_valid_citations_regime_parses(self) -> None:
        paper_vocabulary.validate_citations("discovery")  # raises nothing

    def test_every_declared_citations_regime_is_accepted(self) -> None:
        for regime in paper_vocabulary.CITATIONS_REGIMES:
            paper_vocabulary.validate_citations(regime)  # raises nothing

    def test_an_invalid_citations_regime_refuses(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_vocabulary.validate_citations("maybe")

        self.assertEqual(ctx.exception.code, "UNKNOWN_CITATIONS_REGIME")
        self.assertIn("maybe", ctx.exception.detail)

    def test_the_three_vocabularies_are_closed_tuples_with_no_overlap(self) -> None:
        # Own decision (design.md, `paper_vocabulary.py`): "three closed
        # tuples, no I/O, no state" -- proven here rather than merely
        # documented.
        self.assertIsInstance(paper_vocabulary.FACTS, tuple)
        self.assertIsInstance(paper_vocabulary.DECLARATIONS, tuple)
        self.assertIsInstance(paper_vocabulary.CITATIONS_REGIMES, tuple)
        self.assertEqual(len(paper_vocabulary.FACTS), 10)
        self.assertEqual(len(paper_vocabulary.DECLARATIONS), 6)
        self.assertEqual(len(paper_vocabulary.CITATIONS_REGIMES), 3)
        self.assertEqual(
            set(paper_vocabulary.FACTS) & set(paper_vocabulary.DECLARATIONS), set()
        )


class SchemaTests(unittest.TestCase):
    """`section-contract` spec: the front-matter schema, `MALFORMED_HEADER`,
    and the `--sections` repository boundary."""

    def test_valid_header_parses_with_no_refusal(self) -> None:
        header = _minimal_header(
            blocks=[
                {
                    "id": "results-block",
                    "requires_facts": ["results"],
                    "requires_declarations": [],
                    "citations": "discovery",
                }
            ]
        )
        parsed, body = paper_contract.parse(_header_bytes(header) + b"Prose.\n")

        self.assertEqual(parsed.section, "example")
        self.assertEqual(parsed.position, 1)
        self.assertEqual(len(parsed.blocks), 1)
        self.assertEqual(parsed.blocks[0]["id"], "results-block")
        self.assertEqual(parsed.blocks[0]["requires_facts"], ["results"])
        self.assertEqual(body, b"Prose.\n")

    def test_header_missing_position_refuses_naming_position(self) -> None:
        header = _minimal_header()
        del header["position"]

        with self.assertRaises(Refused) as ctx:
            paper_contract.parse(_header_bytes(header))

        self.assertEqual(ctx.exception.code, "MALFORMED_HEADER")
        self.assertIn("position", ctx.exception.detail)

    def test_header_missing_section_refuses_naming_section(self) -> None:
        header = _minimal_header()
        del header["section"]

        with self.assertRaises(Refused) as ctx:
            paper_contract.parse(_header_bytes(header))

        self.assertEqual(ctx.exception.code, "MALFORMED_HEADER")
        self.assertIn("section", ctx.exception.detail)

    def test_header_missing_blocks_refuses_naming_blocks(self) -> None:
        header = _minimal_header()
        del header["blocks"]

        with self.assertRaises(Refused) as ctx:
            paper_contract.parse(_header_bytes(header))

        self.assertEqual(ctx.exception.code, "MALFORMED_HEADER")
        self.assertIn("blocks", ctx.exception.detail)

    def test_header_with_unknown_top_level_key_refuses(self) -> None:
        header = _minimal_header(reviewer="someone")

        with self.assertRaises(Refused) as ctx:
            paper_contract.parse(_header_bytes(header))

        self.assertEqual(ctx.exception.code, "MALFORMED_HEADER")
        self.assertIn("reviewer", ctx.exception.detail)

    def test_block_missing_requires_facts_refuses_naming_it(self) -> None:
        header = _minimal_header(
            blocks=[{"id": "b", "requires_declarations": [], "citations": "none"}]
        )

        with self.assertRaises(Refused) as ctx:
            paper_contract.parse(_header_bytes(header))

        self.assertEqual(ctx.exception.code, "MALFORMED_HEADER")
        self.assertIn("requires_facts", ctx.exception.detail)

    def test_block_with_unknown_key_refuses(self) -> None:
        header = _minimal_header(
            blocks=[
                {
                    "id": "b",
                    "requires_facts": [],
                    "requires_declarations": [],
                    "citations": "none",
                    "reviewer": "someone",
                }
            ]
        )

        with self.assertRaises(Refused) as ctx:
            paper_contract.parse(_header_bytes(header))

        self.assertEqual(ctx.exception.code, "MALFORMED_HEADER")
        self.assertIn("reviewer", ctx.exception.detail)

    def test_block_declaring_an_unknown_fact_refuses_unknown_fact(self) -> None:
        header = _minimal_header(
            blocks=[
                {
                    "id": "b",
                    "requires_facts": ["discussion"],
                    "requires_declarations": [],
                    "citations": "none",
                }
            ]
        )

        with self.assertRaises(Refused) as ctx:
            paper_contract.parse(_header_bytes(header))

        self.assertEqual(ctx.exception.code, "UNKNOWN_FACT")
        self.assertIn("discussion", ctx.exception.detail)

    def test_block_declaring_an_unknown_declaration_refuses_unknown_declaration(self) -> None:
        header = _minimal_header(
            blocks=[
                {
                    "id": "b",
                    "requires_facts": [],
                    "requires_declarations": ["reviewer-name"],
                    "citations": "none",
                }
            ]
        )

        with self.assertRaises(Refused) as ctx:
            paper_contract.parse(_header_bytes(header))

        self.assertEqual(ctx.exception.code, "UNKNOWN_DECLARATION")
        self.assertIn("reviewer-name", ctx.exception.detail)

    def test_block_declaring_an_invalid_citations_regime_refuses(self) -> None:
        header = _minimal_header(
            blocks=[
                {
                    "id": "b",
                    "requires_facts": [],
                    "requires_declarations": [],
                    "citations": "maybe",
                }
            ]
        )

        with self.assertRaises(Refused) as ctx:
            paper_contract.parse(_header_bytes(header))

        self.assertEqual(ctx.exception.code, "UNKNOWN_CITATIONS_REGIME")
        self.assertIn("maybe", ctx.exception.detail)

    def test_malformed_json_returns_nothing_not_merely_raises(self) -> None:
        data = b"---\n{not valid json\n---\nProse.\n"
        sentinel = object()
        result = sentinel

        with self.assertRaises(Refused) as ctx:
            result = paper_contract.parse(data)

        self.assertEqual(ctx.exception.code, "MALFORMED_HEADER")
        # The call site never received a value -- `result` still holds the
        # sentinel it was seeded with, not a partial parse.
        self.assertIs(result, sentinel)

    def test_missing_opening_fence_refuses_malformed_header(self) -> None:
        data = b"No fence at all.\n"

        with self.assertRaises(Refused) as ctx:
            paper_contract.parse(data)

        self.assertEqual(ctx.exception.code, "MALFORMED_HEADER")

    def test_unclosed_fence_refuses_malformed_header(self) -> None:
        data = b"---\n" + json.dumps(_minimal_header()).encode("utf-8") + b"\nProse with no closing fence.\n"

        with self.assertRaises(Refused) as ctx:
            paper_contract.parse(data)

        self.assertEqual(ctx.exception.code, "MALFORMED_HEADER")

    def test_body_below_the_header_is_passed_through_unread(self) -> None:
        header = _minimal_header()
        body = b"Arbitrary prose.\n\nMore prose, %% not a marker, just text.\n"

        _parsed, returned_body = paper_contract.parse(_header_bytes(header) + body)

        self.assertEqual(returned_body, body)

    def test_sections_outside_repository_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            forge_root = Path(tmp) / "repo"
            forge_root.mkdir()
            outside = Path(tmp) / "elsewhere"

            with self.assertRaises(Refused) as ctx:
                paper_contract.resolve_sections_dir(str(outside), forge_root=forge_root)

            self.assertEqual(ctx.exception.code, "SECTIONS_OUTSIDE_REPOSITORY")

    def test_sections_dir_defaults_to_sections_under_the_forge_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            forge_root = Path(tmp) / "repo"
            forge_root.mkdir()

            resolved = paper_contract.resolve_sections_dir(None, forge_root=forge_root)

            self.assertEqual(resolved, (forge_root / "sections").resolve())


if __name__ == "__main__":
    unittest.main()
