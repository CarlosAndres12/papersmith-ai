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


#: The ten shipped contracts' body digests as committed at HEAD **before**
#: this change (578d117f9008062c08bc3a4bd93f2e7245b4ce9b), when every file
#: was headerless prose end to end. Captured once, by running
#: `git show HEAD:sections/<file> | sha256sum` against that commit -- not
#: re-derived from `HEAD` at test time, which would read the AFTER state
#: post-insertion and make the comparison prove nothing (`HEAD` moves the
#: moment this change is committed; a literal baseline does not). This is
#: the acceptance evidence `specs/section-contract`'s
#: `Requirement: Byte-Clean Header Insertion` asks for, held here so the
#: proof stays meaningful for every run after this change lands, not only
#: the one that performed the insertion.
PRE_MIGRATION_BODY_DIGESTS: dict[str, str] = {
    "01-materials-and-methods.md": "ca424309f46389e79155d58d36245e4160db77aaf837b48a2b585d1e0e628a89"[:64],
    "02-experimental-setup.md": "e65e34db61790c00115dd97db5f14a6e47e2be6e9e061da8a4fccb3e6f6f3fdc"[:64],
    "03-results-and-discussion.md": "e48277cdcc415b5641a72d7a473bc7900dc1bd882a84afc1f7b6c89e1b5b39f0"[:64],
    "04-limitations.md": "a9a7c0ee37c43266a09b798f020117362213452014162504118d7847376a08c8"[:64],
    "05-related-work.md": "5a41968610adeeaf6a407e014cf06a78af935e1773612a3fe85069d14b79060f"[:64],
    "06-introduction.md": "0f6c3b6bfe13206470ed22d88a953f96e86b81bd56445b0c2e40d1ee1354cbff"[:64],
    "07-conclusions.md": "a855ee2a68b66328562317274049d9f78108457644089b3125ea6b51a76ae84b"[:64],
    "08-abstract.md": "8814477108c9121d089fa5738b242ca30093bdd4a16952e38da17eda41857c1a"[:64],
    "09-title-and-keywords.md": "7f44428e530a0209152366e83a7c7e23c52cfc41efe1bc9689eb813c3c44b297"[:64],
    "10-back-matter.md": "8965bd1e429556163077e4350c1a57d4d4d06f3852fa7b6b117236bdc61be2ff"[:64],
}


class HeaderInsertionTests(unittest.TestCase):
    """`section-contract` spec: Byte-Clean Header Insertion. Two kinds of
    evidence, kept apart on purpose: the mechanism's own byte-identity
    guarantee, proven on synthetic fixtures so it stays evergreen; and the
    real migration's own result, checked against the digests this change's
    own author captured from `git show HEAD:` at the commit before the
    insertion ran (`PRE_MIGRATION_BODY_DIGESTS` above) -- `HEAD` itself is
    never read here, precisely because by the time this suite runs again
    `HEAD` already carries the header and comparing against it would prove
    only that the file equals itself."""

    def test_install_over_a_synthetic_fixture_is_byte_clean(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.md"
            original = b"# Sample\n\nSome prose that must survive untouched.\n"
            path.write_bytes(original)

            result = paper_contract.install_header(
                path, {"section": "sample", "position": 1, "blocks": [
                    {"id": "b", "requires_facts": [], "requires_declarations": [], "citations": "none"}
                ]}
            )

            post = path.read_bytes()
            self.assertTrue(post.startswith(b"---\n"))
            _header, body = paper_contract.parse(post)
            self.assertEqual(body, original)
            self.assertEqual(result["body_digest"], hashlib.sha256(original).hexdigest())

    def test_a_second_install_refuses_header_present_and_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.md"
            path.write_bytes(b"Some prose.\n")
            paper_contract.install_header(
                path, {"section": "sample", "position": 1, "blocks": [
                    {"id": "b", "requires_facts": [], "requires_declarations": [], "citations": "none"}
                ]}
            )
            before = path.read_bytes()

            with self.assertRaises(Refused) as ctx:
                paper_contract.install_header(path, {"section": "sample", "position": 1, "blocks": [
                    {"id": "b", "requires_facts": [], "requires_declarations": [], "citations": "none"}
                ]})

            self.assertEqual(ctx.exception.code, "HEADER_PRESENT")
            self.assertEqual(path.read_bytes(), before)

    def test_forced_body_mutation_restores_original_bytes_and_refuses_body_mutated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.md"
            original = b"Original prose, must survive.\n"
            path.write_bytes(original)
            real_replace = paper_contract.os.replace
            calls = {"n": 0}

            def flaky_replace(src, dst):
                calls["n"] += 1
                if calls["n"] == 1:
                    # The header-insertion write itself: simulate it landing
                    # with a corrupted body byte underneath the new header --
                    # exactly the violation BODY_MUTATED exists to catch.
                    corrupted = Path(src).read_bytes().replace(b"Original", b"MUTATED!")
                    Path(src).write_bytes(corrupted)
                return real_replace(src, dst)

            with unittest.mock.patch("paper_contract.os.replace", flaky_replace):
                with self.assertRaises(Refused) as ctx:
                    paper_contract.install_header(
                        path, {"section": "sample", "position": 1, "blocks": [
                            {"id": "b", "requires_facts": [], "requires_declarations": [], "citations": "none"}
                        ]}
                    )

            self.assertEqual(ctx.exception.code, "BODY_MUTATED")
            self.assertEqual(path.read_bytes(), original)

    def test_the_ten_shipped_contracts_carry_headers_matching_the_pre_migration_body_digests(self) -> None:
        for name, expected_digest in PRE_MIGRATION_BODY_DIGESTS.items():
            path = SECTIONS_DIR / name
            data = path.read_bytes()
            self.assertTrue(data.startswith(b"---\n"), f"{name}: no header installed")
            header, body = paper_contract.parse(data)
            self.assertEqual(
                hashlib.sha256(body).hexdigest(), expected_digest,
                f"{name}: body below the header does not match its pre-migration digest",
            )
            self.assertEqual(header.section, name[3:-3])

    def test_installing_a_header_again_on_a_shipped_contract_refuses_header_present(self) -> None:
        # Real-file idempotency: the migration is one-shot and this is what
        # makes a second run over an already-migrated tree refuse rather
        # than double-write. Exercised on a COPY of the real shipped bytes,
        # never on the real file itself -- a test calling a disk-writing
        # function against a tracked repository file is exactly the
        # incident this rewrite fixes (see git history: an earlier revision
        # of this test used a MALFORMED header directly against the real
        # `01-materials-and-methods.md` and corrupted it, because
        # `install_header` did not validate before writing at the time).
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "01-materials-and-methods.md"
            path.write_bytes((SECTIONS_DIR / "01-materials-and-methods.md").read_bytes())
            before = path.read_bytes()
            self.assertTrue(before.startswith(b"---\n"), "shipped file has no header to be idempotent about")

            with self.assertRaises(Refused) as ctx:
                paper_contract.install_header(
                    path, {"section": "materials-and-methods", "position": 5, "blocks": [
                        {"id": "b", "requires_facts": [], "requires_declarations": [], "citations": "none"}
                    ]}
                )

        self.assertEqual(ctx.exception.code, "HEADER_PRESENT")

    def test_install_header_never_writes_a_header_that_fails_its_own_schema(self) -> None:
        # The exact guard that would have caught the incident above: a
        # malformed header is refused before `path` is ever read or
        # written, on a FRESH synthetic fixture (not the real tree) so the
        # proof stays isolated.
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "sample.md"
            original = b"Untouched prose.\n"
            path.write_bytes(original)

            with self.assertRaises(Refused) as ctx:
                paper_contract.install_header(path, {"section": "x", "position": 1, "blocks": []})

            self.assertEqual(ctx.exception.code, "MALFORMED_HEADER")
            self.assertEqual(path.read_bytes(), original)


if __name__ == "__main__":
    unittest.main()
