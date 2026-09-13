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
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = FORGE_ROOT / ".claude" / "skills" / "paper-writing" / "scripts"
SECTIONS_DIR = FORGE_ROOT / "sections"
sys.path.insert(0, str(SKILL_SCRIPTS))
import paper_vocabulary  # noqa: E402
import paper_contract  # noqa: E402
import paper_graph  # noqa: E402
import paper_readiness  # noqa: E402

sys.path.insert(0, str(FORGE_ROOT / ".claude" / "skills" / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

# The forge's vocabulary floor, defined in one place beside the suites --
# the same import shape `tests/test_skill_audit.py` and
# `tests/test_proposal_implementation.py` already use.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import forge_vocabulary  # noqa: E402


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
#:
#: `02-experimental-setup.md`, `04-limitations.md` and `05-related-work.md`
#: later received one operator-authored sentence each (the missing
#: `mode`-bearing sentence a corrective batch added), a legitimate,
#: intentional prose edit -- their three digests below were re-captured
#: after that edit and no longer equal the header-migration-era value.
#: `08-abstract.md` received one further operator-authored sentence (a
#: `mode.source.quote` unambiguous to a human reader, repointing `mode`
#: away from the pre-existing "whole argument at one-fiftieth scale"
#: sentence, which stays in the body as ordinary prose) -- its digest below
#: was re-captured after that edit too. The other six are untouched since
#: the original migration and keep their original digest.
PRE_MIGRATION_BODY_DIGESTS: dict[str, str] = {
    "01-materials-and-methods.md": "ca424309f46389e79155d58d36245e4160db77aaf837b48a2b585d1e0e628a89"[:64],
    "02-experimental-setup.md": "c4465b7f1a371e1b8ee2315e4032cff0a6e8bf76ac4c0a8903a90635c8f7888f"[:64],
    "03-results-and-discussion.md": "e48277cdcc415b5641a72d7a473bc7900dc1bd882a84afc1f7b6c89e1b5b39f0"[:64],
    "04-limitations.md": "1e78bf579fcc41399b7bf47981197afe419ce2c657f5d0a3fdad79ac1404931b"[:64],
    "05-related-work.md": "d4d10c2da38e6c576c6305bd0c37879c81bfb5806670f3c2dc9bc851a19483b4"[:64],
    "06-introduction.md": "0f6c3b6bfe13206470ed22d88a953f96e86b81bd56445b0c2e40d1ee1354cbff"[:64],
    "07-conclusions.md": "a855ee2a68b66328562317274049d9f78108457644089b3125ea6b51a76ae84b"[:64],
    "08-abstract.md": "2e5ef7501bccafc785be3aa7fa640dbcf62add3e7e5bc345fa1be21f34a20b66"[:64],
    "09-title-and-keywords.md": "7f44428e530a0209152366e83a7c7e23c52cfc41efe1bc9689eb813c3c44b297"[:64],
    "10-back-matter.md": "8965bd1e429556163077e4350c1a57d4d4d06f3852fa7b6b117236bdc61be2ff"[:64],
}


class ShippedHeaderDigestTests(unittest.TestCase):
    """`section-contract` spec: Byte-Clean Header Insertion. The mechanism
    that performed the insertion (`paper_contract.install_header`) has since
    been deleted (zero-production-caller corrective: its one-shot migration
    over the ten shipped contracts already completed, and nothing promises
    an ongoing "create a new section contract" workflow anywhere in
    `SKILL.md`, a published spec, or a registered agent). This test stands
    alone as the regression check on the corpus's own result, against the
    digests this change's own author captured from `git show HEAD:` at the
    commit before the insertion ran (`PRE_MIGRATION_BODY_DIGESTS` above) --
    `HEAD` itself is never read here, precisely because by the time this
    suite runs again `HEAD` already carries the header and comparing
    against it would prove only that the file equals itself."""

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


def _write_section(directory: Path, filename: str, header: dict, body: bytes = b"Prose.\n") -> None:
    (directory / filename).write_bytes(_header_bytes(header) + body)


def _block(block_id: str, *, facts=(), declarations=(), citations="none", after=None) -> dict:
    entry = {
        "id": block_id,
        "requires_facts": list(facts),
        "requires_declarations": list(declarations),
        "citations": citations,
    }
    if after is not None:
        entry["after"] = after
    return entry


def _quote_source(file: str, quote: str) -> dict:
    return {"file": file, "quote": quote}


def _quote_in_body(file_path: Path, quote: str) -> bool:
    """Thin pass-through to the PRODUCTION lock, `paper_contract.quote_in_body`
    -- kept here, rather than deleted, only because most of this file's
    callers pass a file PATH while the production function (called from
    both `paper_contract.parse` and `paper_graph.assemble_corpus`, which
    read bodies off two different disk shapes) takes body BYTES directly.
    No algorithm lives in this file any more: a second copy of the
    whitespace-collapse/emphasis-strip logic, next to the one now load-
    bearing in production, is exactly the "two enforcement paths that can
    disagree" risk this corrective was written to close (defect 1). Note
    this now runs `paper_contract.parse` on `file_path`, which since this
    same corrective also refuses `SPAN_NOT_IN_SOURCE` if THAT file's own
    `mode` transcription is dishonest -- never an issue for the real,
    honestly-transcribed corpus this helper is used against."""
    _header, body = paper_contract.parse(file_path.read_bytes())
    return paper_contract.quote_in_body(body, quote)


class GraphTests(unittest.TestCase):
    """`section-contract` spec: flat id namespace, `after` transcription and
    resolution, the exactly-two literal cross-section edges, and the
    position-derived third edge the orchestrator settled at apply time
    (`specs/section-contract/spec.md`'s Implementation note)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.sections_dir = Path(self._tmp.name) / "sections"
        self.sections_dir.mkdir()

    # --- flat id namespace -------------------------------------------------

    def test_a_block_id_colliding_with_a_section_id_refuses_id_collision(self) -> None:
        _write_section(self.sections_dir, "01-a.md", {
            "section": "a", "position": 1, "blocks": [_block("only")],
        })
        _write_section(self.sections_dir, "02-b.md", {
            "section": "b", "position": 2, "blocks": [_block("a")],  # collides with section "a"
        })

        with self.assertRaises(Refused) as ctx:
            paper_graph.assemble_corpus(self.sections_dir)

        self.assertEqual(ctx.exception.code, "ID_COLLISION")
        self.assertIn("a", ctx.exception.detail)

    def test_disjoint_ids_across_sections_assemble_cleanly(self) -> None:
        _write_section(self.sections_dir, "01-a.md", {
            "section": "a", "position": 1, "blocks": [_block("only")],
        })
        _write_section(self.sections_dir, "02-b.md", {
            "section": "b", "position": 2, "blocks": [_block("only")],  # same raw id, different section: fine
        })

        corpus = paper_graph.assemble_corpus(self.sections_dir)

        self.assertEqual(set(corpus.blocks), {"a.only", "b.only"})

    # --- after: section target expands to every block ----------------------

    def test_after_naming_a_section_expands_to_every_block_of_it(self) -> None:
        _write_section(self.sections_dir, "01-a.md", {
            "section": "a", "position": 1,
            "blocks": [_block("first"), _block("second")],
        })
        _write_section(self.sections_dir, "02-b.md", {
            "section": "b", "position": 2,
            "after": [{"target": "a", "source": _quote_source("sections/01-a.md", "Prose.")}],
            "blocks": [_block("only")],
        })

        corpus = paper_graph.assemble_corpus(self.sections_dir)
        edge_set = paper_graph.collect_edges(corpus)

        pairs = {(before, after) for before, after, _source in edge_set.edges}
        self.assertIn(("a.first", "b.only"), pairs)
        self.assertIn(("a.second", "b.only"), pairs)

    # --- after: an absent target is reported, never refused ----------------

    def test_dangling_after_target_is_reported_never_refused(self) -> None:
        _write_section(self.sections_dir, "01-a.md", {
            "section": "a", "position": 1,
            "after": [{"target": "nonexistent", "source": _quote_source("sections/01-a.md", "x")}],
            "blocks": [_block("only")],
        })

        corpus = paper_graph.assemble_corpus(self.sections_dir)
        edge_set = paper_graph.collect_edges(corpus)  # must not raise

        self.assertIn("nonexistent", edge_set.dangling)

    # --- transcription lock: real corpus ------------------------------------

    def _real_corpus(self):
        return paper_graph.assemble_corpus(SECTIONS_DIR)

    def test_the_real_corpus_assembles_cleanly_under_the_production_transcription_lock(self) -> None:
        """This corrective's own requirement: moving the transcription lock
        off the test suite and into `paper_contract.parse` (`mode`) and
        `paper_graph.assemble_corpus` (`after`) must refuse NONE of the ten
        shipped contracts or their real `after` edges -- both checks run as
        a side effect of the one call below (`assemble_corpus` parses every
        file, which enforces `mode`; it then enforces `after` itself). A
        refusal here would mean the operator's own prose is wrong, to be
        reported back, never patched around by loosening this check."""
        corpus = paper_graph.assemble_corpus(SECTIONS_DIR)  # must not raise
        self.assertEqual(len(corpus.sections), 10, "expected exactly the ten shipped sections")

    def test_every_transcribed_afters_quote_is_a_substring_of_its_named_file(self) -> None:
        # Reads the parsed BODY only, via `paper_contract.parse`'s own
        # header/body split -- never the raw file text. A whole-file read is
        # vacuous for any edge whose `source.file` is the SAME file as the
        # header that transcribes it (`introduction.block-3` -> `related-
        # work`, sourced in its own `06-introduction.md`): that header's own
        # JSON always re-serializes `quote` verbatim, so a substring check
        # against the raw bytes finds it there regardless of what the prose
        # says. Checking the body only closes that hole -- proven by
        # `test_a_fabricated_quote_on_a_self_referential_edge_fails_the_lock`
        # below, which replays this exact check with a prose-absent quote on
        # that exact edge and confirms it now fails.
        corpus = self._real_corpus()

        checked = 0
        for section_id, header in corpus.sections.items():
            entries = list(header.after)
            for raw_block in header.blocks:
                entries += raw_block["after"]
            for entry in entries:
                source = entry["source"]
                self.assertTrue(
                    _quote_in_body(FORGE_ROOT / source["file"], source["quote"]),
                    f"{section_id}: quote not found verbatim (whitespace-collapsed) in "
                    f"{source['file']}'s prose body",
                )
                checked += 1

        self.assertGreater(checked, 0, "no transcribed after entries were found to check")

    def test_a_fabricated_quote_on_a_self_referential_edge_fails_the_lock(self) -> None:
        """Reproduces the verifier's own falsification exactly, on a temp
        copy -- never the tracked file. `introduction.block-3`'s `after`
        names `related-work`, sourced in `06-introduction.md`, the SAME file
        as its own holder section: self-sourced, the one shape (of the two
        shipped literal edges) that made the OLD, whole-file-reading lock
        vacuous, because that file's header always re-serializes whatever
        `quote` it holds. Substitute a prose-absent quote into ONLY the
        header field (the body is untouched) and confirm: the OLD shape
        (raw-whole-file substring) still reports it found -- the exact hole
        -- while the body-only check above correctly reports it absent.
        A fix proven only by "the old test still passes" would prove
        nothing, since that test passed while broken."""
        real_path = SECTIONS_DIR / "06-introduction.md"
        header, body = paper_contract.parse(real_path.read_bytes())
        self.assertEqual(header.section, "introduction")

        fabricated_quote = "Purple elephants never write in Related Work order at all."
        body_text = " ".join(body.decode("utf-8").split())
        self.assertNotIn(
            fabricated_quote, body_text,
            "fixture assumption: the fabrication is absent from the real prose",
        )

        def _tamper(raw_block: dict) -> dict:
            if raw_block["id"] != "block-3":
                return raw_block
            tampered = dict(raw_block)
            tampered["after"] = [
                {**entry, "source": {**entry["source"], "quote": fabricated_quote}}
                for entry in raw_block["after"]
            ]
            return tampered

        tampered_header = {
            "section": header.section,
            "position": header.position,
            "after": header.after,
            "blocks": [_tamper(raw_block) for raw_block in header.blocks],
        }
        tampered_bytes = _header_bytes(tampered_header) + body

        # OLD lock shape: raw-whole-file substring check. It finds the
        # fabrication -- not in the prose, but in the header's own JSON,
        # which the tamper just wrote into that same file. This is exactly
        # the vacuity `verify-report.md`'s Finding W1 proved.
        raw_text = " ".join(tampered_bytes.decode("utf-8").split())
        self.assertIn(
            fabricated_quote, raw_text,
            "fixture assumption: the tampered header still re-serializes the fabrication verbatim",
        )

        # NEW lock shape (this corrective's fix, defect 1): drive the REAL
        # production entrypoint, `paper_graph.assemble_corpus`, on a temp
        # copy of the WHOLE shipped corpus (never the tracked file) with
        # only `06-introduction.md` swapped for the tampered bytes -- the
        # rest of the corpus stays real so `related-work`, this edge's own
        # `target`, still resolves exactly as it does in the real
        # repository. A single-file fixture would make that target
        # dangling and this corrective's own narrowing (dangling targets
        # are not quote-checked) would silently skip the exact case this
        # test exists to prove.
        with tempfile.TemporaryDirectory() as tmp:
            temp_sections = Path(tmp) / "sections"
            temp_sections.mkdir()
            for path in SECTIONS_DIR.glob("*.md"):
                (temp_sections / path.name).write_bytes(path.read_bytes())
            (temp_sections / "06-introduction.md").write_bytes(tampered_bytes)

            with self.assertRaises(Refused) as ctx:
                paper_graph.assemble_corpus(temp_sections)

        self.assertEqual(ctx.exception.code, "SPAN_NOT_IN_SOURCE")
        self.assertIn("06-introduction.md", ctx.exception.detail)
        self.assertIn("Purple elephants", ctx.exception.detail)

    # --- exactly two literal cross-section edges, derived not hand-listed --

    def test_the_shipped_corpus_has_exactly_two_literal_cross_section_after_edges(self) -> None:
        corpus = self._real_corpus()

        cross_section = set()
        for section_id, header in corpus.sections.items():
            for entry in header.after:
                if entry["target"] != section_id and entry["target"] in corpus.sections:
                    cross_section.add((section_id, entry["target"]))
            for raw_block in header.blocks:
                for entry in raw_block["after"]:
                    if entry["target"] != section_id and entry["target"] in corpus.sections:
                        cross_section.add((f"{section_id}.{raw_block['id']}", entry["target"]))

        self.assertEqual(
            cross_section,
            {("abstract", "conclusions"), ("introduction.block-3", "related-work")},
        )

    # --- the position-derived third edge (orchestrator settlement) ---------

    def test_title_and_keywords_position_derived_edge_targets_exactly_the_seven_body_sections(self) -> None:
        corpus = self._real_corpus()

        body_sections = {
            sid for sid, header in corpus.sections.items()
            if corpus.sections["abstract"].position < header.position < corpus.sections["back-matter"].position
        }

        self.assertEqual(
            body_sections,
            {
                "introduction", "related-work", "materials-and-methods",
                "experimental-setup", "results-and-discussion", "limitations",
                "conclusions",
            },
        )

        edge_set = paper_graph.collect_edges(corpus)
        pairs = {(before, after) for before, after, _source in edge_set.edges}
        tk_blocks = corpus.order_by_section["title-and-keywords"]
        for section_id in body_sections:
            for target_qualified in corpus.order_by_section[section_id]:
                for tk_qualified in tk_blocks:
                    self.assertIn((target_qualified, tk_qualified), pairs)

    def test_position_derived_edge_is_computed_from_looked_up_positions_not_a_hardcoded_integer(self) -> None:
        # Re-derive the same corpus with abstract's position changed (still
        # a valid, internally consistent renumbering) and confirm the body
        # set moves with it -- proof the computation reads `position` via
        # section id lookups rather than a baked-in `2`/`10` pair.
        with tempfile.TemporaryDirectory() as tmp:
            alt_dir = Path(tmp) / "sections"
            alt_dir.mkdir()
            _write_section(alt_dir, "01-title-and-keywords.md", {
                "section": "title-and-keywords", "position": 1, "blocks": [_block("only")],
            })
            _write_section(alt_dir, "02-abstract.md", {
                "section": "abstract", "position": 3, "blocks": [_block("only")],  # moved from 2 to 3
            })
            _write_section(alt_dir, "03-middle.md", {
                "section": "middle", "position": 4, "blocks": [_block("only")],
            })
            _write_section(alt_dir, "04-back-matter.md", {
                "section": "back-matter", "position": 5, "blocks": [_block("only")],
            })

            corpus = paper_graph.assemble_corpus(alt_dir)
            edge_set = paper_graph.collect_edges(corpus)
            pairs = {(before, after) for before, after, _source in edge_set.edges}

            self.assertIn(("middle.only", "title-and-keywords.only"), pairs)


class ModeTranscriptionTests(unittest.TestCase):
    """`section-contract` spec, `Requirement: Closed Mode Vocabulary And
    Transcription`: a `mode` MUST be admitted only where the contract's own
    prose states it, "mirroring the transcription discipline already
    required of `after` edges" -- the discipline `GraphTests` above already
    proves for `after` via `_quote_in_body` (body-only, never the raw
    file). Before this corrective, `test_paper_writing.py`'s
    `test_shipped_contracts_declaring_mode_resolve_it_at_every_block`
    checked `mode`'s SHAPE and `source["file"]`, but never `source["quote"]`
    against real prose -- this class closes that gap, the CRITICAL a
    corrective re-verify found."""

    def _real_corpus(self):
        return paper_graph.assemble_corpus(SECTIONS_DIR)

    def _declared_modes(self, corpus=None):
        """Derived from the corpus, never a hand-listed set of section ids:
        every section's own `header.mode` (all ten shipped sections declare
        one as of the `02`/`04`/`05` corrective) plus every block's own
        `mode` (none in the shipped corpus today, but the walk is generic --
        a future block-level declaration is picked up without touching this
        test). `corpus` defaults to the real shipped one; a caller may pass a
        synthetic corpus to exercise the None-skipping branch without
        depending on any real section ever leaving `mode` undeclared."""
        corpus = corpus if corpus is not None else self._real_corpus()
        entries = []
        for section_id, header in corpus.sections.items():
            if header.mode is not None:
                entries.append((section_id, header.mode))
            for raw_block in header.blocks:
                block_mode = raw_block.get("mode")
                if block_mode is not None:
                    entries.append((f"{section_id}.{raw_block['id']}", block_mode))
        return entries

    def test_every_declared_modes_quote_is_a_substring_of_its_named_file(self) -> None:
        entries = self._declared_modes()

        for owner, mode in entries:
            source = mode["source"]
            self.assertTrue(
                _quote_in_body(FORGE_ROOT / source["file"], source["quote"]),
                f"{owner}: mode quote not found verbatim (whitespace-collapsed, "
                f"markdown-emphasis-stripped) in {source['file']}'s prose body",
            )

        # Golden count, not a hand-listed set of section ids: the walk above
        # is generic over the whole corpus; this pins it to the ten modes
        # this build has actually declared, one per shipped section -- the
        # same "exactly N, derived not hand-listed" style `GraphTests`
        # already uses for the two literal cross-section `after` edges.
        # Grew from seven to ten when `02-experimental-setup.md`,
        # `04-limitations.md` and `05-related-work.md` each received their
        # operator-authored mode-bearing sentence; the count is read off the
        # real corpus walk above, never edited by hand to match.
        self.assertEqual(len(entries), 10, "expected exactly the ten declared modes")

    def test_undeclared_sections_are_absent_not_silently_passing(self) -> None:
        """Every shipped section now declares a `mode`
        (`test_every_declared_modes_quote_is_a_substring_of_its_named_file`'s
        golden count of ten), so this class exercises the None-skipping
        branch of the walk on a synthetic corpus instead of leaning on a
        real section that happens to leave `mode` undeclared -- the walk
        must still skip an undeclared section entirely rather than ever
        counting the absence as a checked-and-passed entry."""
        with tempfile.TemporaryDirectory() as tmp:
            sections_dir = Path(tmp)
            declared_header = {
                "section": "with-mode", "position": 1,
                "mode": {
                    "value": "argument",
                    "source": {"file": "with-mode.md", "quote": "This section argues."},
                },
                "blocks": [{
                    "id": "b1", "requires_facts": [], "requires_declarations": [],
                    "citations": "none",
                }],
            }
            undeclared_header = {
                "section": "without-mode", "position": 2,
                "blocks": [{
                    "id": "b2", "requires_facts": [], "requires_declarations": [],
                    "citations": "none",
                }],
            }
            (sections_dir / "with-mode.md").write_bytes(
                b"---\n" + json.dumps(declared_header).encode("utf-8") + b"\n---\nThis section argues.\n"
            )
            (sections_dir / "without-mode.md").write_bytes(
                b"---\n" + json.dumps(undeclared_header).encode("utf-8") + b"\n---\nNo mode sentence here.\n"
            )

            corpus = paper_graph.assemble_corpus(sections_dir)
            self.assertIsNone(corpus.sections["without-mode"].mode)

            owners = {owner for owner, _mode in self._declared_modes(corpus=corpus)}
            self.assertIn("with-mode", owners)
            self.assertNotIn("without-mode", owners)

    def test_a_fabricated_mode_quote_on_a_self_sourced_entry_fails_the_lock(self) -> None:
        """Same falsification `GraphTests` already runs for `after`
        (`test_a_fabricated_quote_on_a_self_referential_edge_fails_the_lock`),
        replayed for `mode` -- the exact CRITICAL this corrective closes.
        `introduction`'s own `mode` is self-sourced (`source.file` is
        `06-introduction.md`, the same file as the header holding it): the
        one shape that makes a whole-file raw substring check vacuous, since
        that file's header JSON always re-serializes whatever `quote` the
        `mode` entry holds, verbatim."""
        real_path = SECTIONS_DIR / "06-introduction.md"
        header, body = paper_contract.parse(real_path.read_bytes())
        self.assertEqual(header.section, "introduction")
        self.assertIsNotNone(header.mode)
        self.assertEqual(header.mode["source"]["file"], "sections/06-introduction.md")

        fabricated_quote = "Purple elephants narrate every argumentative function in reverse."
        body_text = " ".join(body.decode("utf-8").split())
        self.assertNotIn(
            fabricated_quote, body_text,
            "fixture assumption: the fabrication is absent from the real prose",
        )

        tampered_header = {
            "section": header.section,
            "position": header.position,
            "after": header.after,
            "mode": {
                "value": header.mode["value"],
                "source": {**header.mode["source"], "quote": fabricated_quote},
            },
            "blocks": [dict(raw_block) for raw_block in header.blocks],
        }
        tampered_bytes = _header_bytes(tampered_header) + body

        with tempfile.TemporaryDirectory() as tmp:
            tampered_path = Path(tmp) / "06-introduction.md"
            tampered_path.write_bytes(tampered_bytes)

            # OLD lock shape: raw-whole-file substring check. It finds the
            # fabrication -- not in the prose, but in the header's own JSON,
            # which the tamper just wrote into that same file.
            raw_text = " ".join(tampered_path.read_text(encoding="utf-8").split())
            self.assertIn(
                fabricated_quote, raw_text,
                "fixture assumption: the tampered header still re-serializes the fabrication verbatim",
            )

            # NEW lock shape (this corrective's fix, defect 1): the REAL
            # production entrypoint -- `paper_contract.parse` itself, not a
            # test-only helper reporting a bare `False` -- refuses on its
            # own, before this header is ever handed back to any caller
            # (`paper_graph.assemble_corpus`, `write`, `render`, `place`,
            # every CLI verb that reads a section contract).
            with self.assertRaises(Refused) as ctx:
                paper_contract.parse(tampered_path.read_bytes())

        self.assertEqual(ctx.exception.code, "SPAN_NOT_IN_SOURCE")
        self.assertIn("introduction", ctx.exception.detail)
        self.assertIn("Purple elephants", ctx.exception.detail)

    def test_a_paraphrased_quote_and_an_unrelated_sentence_both_still_fail(self) -> None:
        """The trap named in this corrective's own brief: normalizing
        markdown emphasis (`**bold**`/`*italic*`) must never become a fuzzy
        or similarity match. Feed the lock a genuine paraphrase of
        `06-introduction.md`'s own prose (same meaning, different words) and
        a genuinely unrelated sentence, and confirm both still fail -- proof
        the normalization only strips literal `*` characters, never blurs
        word content."""
        real_path = SECTIONS_DIR / "06-introduction.md"

        paraphrase = "Six persuasive roles, always in the same sequence, spread over 7 to 13 paragraphs."
        unrelated = "The dataset was collected across three clinical sites over eighteen months."

        self.assertFalse(_quote_in_body(real_path, paraphrase), "a paraphrase must not pass the lock")
        self.assertFalse(_quote_in_body(real_path, unrelated), "an unrelated sentence must not pass the lock")

    def test_the_shipped_introduction_mode_quote_passes_only_once_emphasis_is_stripped(self) -> None:
        """Direct proof of the fix, isolated from the corpus walk above:
        `06-introduction.md`'s real, unedited `mode.source.quote` is an
        honest, word-for-word transcription of the real prose -- the ONLY
        reason the old whitespace-collapse-only lock rejected it is that the
        prose wraps two of those words in `**bold**` markup, decoration a
        JSON quote field was never meant to have to spell out."""
        real_path = SECTIONS_DIR / "06-introduction.md"
        header, _body = paper_contract.parse(real_path.read_bytes())
        quote = header.mode["source"]["quote"]

        self.assertTrue(_quote_in_body(real_path, quote))


class EmphasisStripTests(unittest.TestCase):
    """Defect 2: the emphasis strip must be PAIR-aware, never a bare-
    character removal. Two properties, each its own test rather than one
    combined assertion, so either can fail independently and name exactly
    which property broke."""

    def test_a_bold_pair_still_matches_once_stripped(self) -> None:
        """The property the strip exists for in the first place: a
        `**bold**` pair must still match a quote written without the
        markup -- this is why `06-introduction.md` needed no prose edit
        when its own mode quote was first transcribed."""
        body = b"This sentence carries **bold words** inside it.\n"
        self.assertTrue(paper_contract.quote_in_body(body, "bold words"))

    def test_an_unpaired_asterisk_inside_a_word_does_not_falsely_match(self) -> None:
        """The exact hole named in this corrective's brief: `func*tions`
        (one bare `*`, no closing partner anywhere in the text) must NOT
        match a quote written `functions` -- a single stray delimiter is
        not a pair, so nothing strips it, and the literal `*` survives
        into the comparison, correctly breaking the match."""
        body = b"This sentence carries func*tions inside it.\n"
        self.assertFalse(paper_contract.quote_in_body(body, "functions"))


class OrderTests(unittest.TestCase):
    """`writing-readiness` spec: the derived writing order, and its
    distinctness from both filename order and rendering (`position`)
    order."""

    def test_order_is_deterministic_across_repeated_derivations(self) -> None:
        corpus_1 = paper_graph.assemble_corpus(SECTIONS_DIR)
        edges_1 = paper_graph.collect_edges(corpus_1)
        order_1 = paper_graph.derive_order(corpus_1, edges_1)

        corpus_2 = paper_graph.assemble_corpus(SECTIONS_DIR)
        edges_2 = paper_graph.collect_edges(corpus_2)
        order_2 = paper_graph.derive_order(corpus_2, edges_2)

        self.assertEqual(order_1, order_2)

    def test_rendering_order_differs_from_filename_order(self) -> None:
        corpus = paper_graph.assemble_corpus(SECTIONS_DIR)
        # Rendering order: by `position` -- introduction (3) before
        # related-work (4), even though the filenames sort the other way
        # (06-introduction.md > 05-related-work.md).
        self.assertLess(corpus.sections["introduction"].position, corpus.sections["related-work"].position)
        filenames = sorted(p.name for p in SECTIONS_DIR.glob("*.md"))
        intro_filename_index = filenames.index("06-introduction.md")
        rw_filename_index = filenames.index("05-related-work.md")
        self.assertGreater(intro_filename_index, rw_filename_index)  # filename order disagrees

    def test_related_work_precedes_introduction_block_3_and_follows_blocks_1_2_4(self) -> None:
        corpus = paper_graph.assemble_corpus(SECTIONS_DIR)
        edges = paper_graph.collect_edges(corpus)
        order = paper_graph.derive_order(corpus, edges)
        index = {qid: i for i, qid in enumerate(order)}

        for rw_block in corpus.order_by_section["related-work"]:
            self.assertLess(index["introduction.block-1"], index[rw_block])
            self.assertLess(index["introduction.block-2"], index[rw_block])
            self.assertLess(index["introduction.block-4"], index[rw_block])
            self.assertLess(index[rw_block], index["introduction.block-3"])

    def test_back_matter_renders_last_while_its_writing_order_place_is_graph_derived_not_fact_derived(self) -> None:
        """`writing-readiness` spec, Requirement: Derived Writing Order,
        Scenario "Position reports rendering order separately from writing
        order". Back matter is the discriminating case: every one of its
        blocks requires zero facts, so a writing-order deriver that (wrongly)
        used readiness/fact-satisfaction as its ordering signal would place
        every back-matter block FIRST, ahead of anything still waiting on a
        fact -- back matter renders LAST (the highest `position` in the
        shipped corpus). This test pins both halves down: `position` is read
        directly off the header as a value separate from the derived order
        (rendering order), and the derived order does not place a
        zero-missing-facts block ahead of fact-blocked ones (writing order is
        graph-derived, not readiness-derived) -- back matter carries no
        `after` edge of its own, transcribed or position-derived, so nothing
        in the graph names it either."""
        corpus = paper_graph.assemble_corpus(SECTIONS_DIR)

        # Rendering order: back matter's own `position` is the maximum among
        # every shipped section -- a fact read straight off the header,
        # computed nowhere near the graph.
        self.assertEqual(
            corpus.sections["back-matter"].position,
            max(header.position for header in corpus.sections.values()),
        )

        # Back matter carries no `after` edge anywhere -- section-level or
        # block-level -- so nothing transcribed constrains its place, and it
        # is not `title-and-keywords` (the one section that receives a
        # position-derived edge). Its place in the writing order is decided
        # only by the (absent) `after` edges naming it, never by `position`.
        bm_header = corpus.sections["back-matter"]
        self.assertEqual(bm_header.after, [])
        for raw_block in bm_header.blocks:
            self.assertEqual(raw_block["after"], [])

        # Readiness: every back-matter block requires zero facts, so a
        # (wrong) fact-only ordering signal would rank every one of them
        # ahead of any block still waiting on a fact.
        readiness = paper_readiness.compute_readiness(
            corpus, satisfied_facts=set(), satisfied_declarations=set()
        )
        bm_qualified_ids = {r["block"] for r in readiness if r["block"].startswith("back-matter.")}
        self.assertTrue(bm_qualified_ids, "fixture assumption: back matter ships at least one block")
        for entry in readiness:
            if entry["block"] in bm_qualified_ids:
                self.assertEqual(entry["missing_facts"], [])

        fact_blocked_qualified_ids = {r["block"] for r in readiness if r["missing_facts"]}
        self.assertTrue(
            fact_blocked_qualified_ids,
            "fixture assumption: at least one shipped block still needs a fact",
        )

        # Writing order: derived from the graph. If readiness/fact-count
        # decided placement, every zero-missing-facts back-matter block would
        # land before every still-fact-blocked block above. It does not --
        # the graph, not readiness, decides.
        edges = paper_graph.collect_edges(corpus)
        order = paper_graph.derive_order(corpus, edges)
        index = {qid: i for i, qid in enumerate(order)}

        for bm_qid in bm_qualified_ids:
            for fact_blocked_qid in fact_blocked_qualified_ids:
                self.assertGreater(
                    index[bm_qid], index[fact_blocked_qid],
                    f"{bm_qid} (zero missing facts) landed before {fact_blocked_qid} (still fact-blocked) "
                    "in the writing order -- readiness, not the graph, appears to be deciding placement",
                )

    def test_a_two_block_mutual_after_cycle_refuses_order_cycle_naming_both(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sections_dir = Path(tmp) / "sections"
            sections_dir.mkdir()
            _write_section(sections_dir, "01-a.md", {
                "section": "a", "position": 1,
                "blocks": [_block(
                    "x", after=[{"target": "b.y", "source": _quote_source("sections/01-a.md", "Prose.")}]
                )],
            })
            _write_section(sections_dir, "02-b.md", {
                "section": "b", "position": 2,
                "blocks": [_block(
                    "y", after=[{"target": "a.x", "source": _quote_source("sections/02-b.md", "Prose.")}]
                )],
            })

            corpus = paper_graph.assemble_corpus(sections_dir)
            edges = paper_graph.collect_edges(corpus)

            with self.assertRaises(Refused) as ctx:
                paper_graph.derive_order(corpus, edges)

            self.assertEqual(ctx.exception.code, "ORDER_CYCLE")
            self.assertIn("a.x", ctx.exception.detail)
            self.assertIn("b.y", ctx.exception.detail)

    def test_acyclic_synthetic_corpus_orders_without_refusing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            sections_dir = Path(tmp) / "sections"
            sections_dir.mkdir()
            _write_section(sections_dir, "01-a.md", {
                "section": "a", "position": 1, "blocks": [_block("only")],
            })
            _write_section(sections_dir, "02-b.md", {
                "section": "b", "position": 2,
                "after": [{"target": "a", "source": _quote_source("sections/01-a.md", "Prose.")}],
                "blocks": [_block("only")],
            })

            corpus = paper_graph.assemble_corpus(sections_dir)
            edges = paper_graph.collect_edges(corpus)
            order = paper_graph.derive_order(corpus, edges)

            self.assertLess(order.index("a.only"), order.index("b.only"))


class ReadinessTests(unittest.TestCase):
    """`writing-readiness` spec: per-block `writable`/`blocked`, and the
    case a facts-only check gets wrong."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.sections_dir = Path(self._tmp.name) / "sections"
        self.sections_dir.mkdir()

    def test_a_block_with_every_requirement_satisfied_is_writable(self) -> None:
        _write_section(self.sections_dir, "01-a.md", {
            "section": "a", "position": 1,
            "blocks": [_block("only", facts=["dataset"])],
        })
        corpus = paper_graph.assemble_corpus(self.sections_dir)

        report = paper_readiness.compute_readiness(corpus, satisfied_facts={"dataset"}, satisfied_declarations=set())

        entry = next(r for r in report if r["block"] == "a.only")
        self.assertEqual(entry["status"], "writable")
        self.assertEqual(entry["missing_facts"], [])
        self.assertEqual(entry["missing_declarations"], [])

    def test_a_block_blocked_only_by_a_declaration_is_not_writable(self) -> None:
        _write_section(self.sections_dir, "01-a.md", {
            "section": "a", "position": 1,
            "blocks": [_block("only", facts=["dataset"], declarations=["repository-url"])],
        })
        corpus = paper_graph.assemble_corpus(self.sections_dir)

        report = paper_readiness.compute_readiness(
            corpus, satisfied_facts={"dataset"}, satisfied_declarations=set()
        )

        entry = next(r for r in report if r["block"] == "a.only")
        self.assertEqual(entry["status"], "blocked")
        self.assertEqual(entry["missing_facts"], [])
        self.assertEqual(entry["missing_declarations"], ["repository-url"])

    def test_back_matter_reports_zero_missing_facts_and_its_declarations_missing(self) -> None:
        corpus = paper_graph.assemble_corpus(SECTIONS_DIR)

        report = paper_readiness.compute_readiness(corpus, satisfied_facts=set(), satisfied_declarations=set())

        bm_entries = [r for r in report if r["block"].startswith("back-matter.")]
        self.assertGreater(len(bm_entries), 0)
        for entry in bm_entries:
            self.assertEqual(entry["missing_facts"], [])
            if entry["missing_declarations"]:
                self.assertEqual(entry["status"], "blocked")


def _reader_source_digest() -> str:
    """sha256 over every `.py` file the reader ships, concatenated in a
    fixed order. Asserted equal before and after a mutation subprocess run
    (design.md's Mutation A: "digest-asserting the reader's own source is
    unchanged before and after") -- a mutation that patched the reader's own
    disk copy instead of exercising it through a fixture would move this."""
    hasher = hashlib.sha256()
    for name in ("paper_vocabulary.py", "paper_contract.py", "paper_graph.py",
                 "paper_readiness.py", "paper_cli.py"):
        hasher.update((SKILL_SCRIPTS / name).read_bytes())
    return hasher.hexdigest()


def _section_graph_shape(corpus, section_id: str) -> tuple:
    """The graph-shape axis `writing-readiness`'s Mutation A anti-vacuity
    check uses: whether `section_id` carries BOTH a section-level and a
    block-level `after`, and whether any of its `after` entries targets a
    section or block positioned EARLIER than the holder itself. Derived
    from the corpus, never hand-asserted."""
    header = corpus.sections[section_id]
    has_section_after = bool(header.after)
    has_block_after = any(block["after"] for block in header.blocks)
    has_both = has_section_after and has_block_after

    def target_position(target_id):
        if target_id in corpus.sections:
            return corpus.sections[target_id].position
        if target_id in corpus.blocks:
            return corpus.blocks[target_id].position
        return None

    entries = list(header.after)
    for block in header.blocks:
        entries += block["after"]

    has_earlier_target = any(
        (pos := target_position(entry["target"])) is not None and pos < header.position
        for entry in entries
    )

    return (has_both, has_earlier_target)


class MutationTests(unittest.TestCase):
    """`writing-readiness` spec: the two executed mutations that prove the
    reader generalizes with zero code changes -- Requirement: Eleventh
    Contract Enters With No Code Change, and Requirement: A Fact Outside
    the Ten Refuses."""

    def test_mutation_a_the_eleventh_contract_is_novel_and_reads_correctly(self) -> None:
        corpus = paper_graph.assemble_corpus(SECTIONS_DIR)

        used_fact_shapes = {frozenset(block.requires_facts) for block in corpus.blocks.values()}
        used_graph_shapes = {_section_graph_shape(corpus, sid) for sid in corpus.sections}

        eleventh_facts = frozenset({"skeleton", "gap"})
        eleventh_graph_shape = (False, True)  # a block whose `after` targets an EARLIER section

        self.assertNotIn(
            eleventh_facts, used_fact_shapes,
            "the fixture's fact combination is already shipped -- it proves round-tripping, not generality",
        )
        self.assertNotIn(
            eleventh_graph_shape, used_graph_shapes,
            "the fixture's graph shape is already shipped -- it proves round-tripping, not generality",
        )

        test_root = FORGE_ROOT / "implementations" / f".paper-contract-mutation-a-{os.getpid()}-{uuid.uuid4().hex[:8]}"
        self.addCleanup(shutil.rmtree, test_root, ignore_errors=True)
        temp_sections = test_root / "sections"
        temp_sections.mkdir(parents=True)
        for path in SECTIONS_DIR.glob("*.md"):
            (temp_sections / path.name).write_bytes(path.read_bytes())

        eleventh_body = b"This appendix is written after the title is fixed, because its examples quote it.\n"
        _write_section(
            temp_sections, "11-supplementary-notes.md",
            {
                "section": "supplementary-notes", "position": 11,
                "blocks": [_block(
                    "only", facts=["skeleton", "gap"],
                    after=[{
                        "target": "title-and-keywords",
                        "source": {
                            "file": "sections/11-supplementary-notes.md",
                            "quote": "This appendix is written after the title is fixed, because its examples quote it.",
                        },
                    }],
                )],
            },
            body=eleventh_body,
        )

        pre_digest = _reader_source_digest()
        proc = subprocess.run(
            [sys.executable, str(SKILL_SCRIPTS / "paper_cli.py"), "readiness",
             "--sections", str(temp_sections), "--fact", "skeleton", "--fact", "gap"],
            capture_output=True, text=True, timeout=30,
        )
        post_digest = _reader_source_digest()

        self.assertEqual(pre_digest, post_digest, "the reader's own source changed during the mutation run")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        entry = next(b for b in payload["blocks"] if b["block"] == "supplementary-notes.only")
        self.assertEqual(entry["status"], "writable")

    def test_mutation_b_a_fact_outside_the_vocabulary_refuses_on_execution(self) -> None:
        test_root = FORGE_ROOT / "implementations" / f".paper-contract-mutation-b-{os.getpid()}-{uuid.uuid4().hex[:8]}"
        self.addCleanup(shutil.rmtree, test_root, ignore_errors=True)
        sections_dir = test_root / "sections"
        sections_dir.mkdir(parents=True)
        _write_section(sections_dir, "01-bad.md", {
            "section": "bad", "position": 1,
            "blocks": [_block("only", facts=["discussion"])],
        })

        proc = subprocess.run(
            [sys.executable, str(SKILL_SCRIPTS / "paper_cli.py"), "readiness", "--sections", str(sections_dir)],
            capture_output=True, text=True, timeout=30,
        )

        self.assertEqual(proc.returncode, 2, proc.stdout)
        payload = json.loads(proc.stdout)
        self.assertEqual(payload["status"], "refused")
        self.assertEqual(payload["code"], "UNKNOWN_FACT")
        self.assertIn("discussion", payload["detail"])


class VocabularyLeakTests(unittest.TestCase):
    """Forge leak guard: `FORGE_VOCABULARY_FLOOR` must never appear in any
    file this skill ships. `transfer` sits on it and `09-title-and-
    keywords.md`'s own prose uses it ("the work does not transfer beyond
    it") -- that sentence lives in `sections/`, which `shipped_documents()`
    never reaches, but nothing newly written under
    `.claude/skills/paper-writing/` may quote it (design.md, `What
    Breaks`)."""

    def test_no_shipped_paper_writing_document_leaks_the_forge_vocabulary_floor(self) -> None:
        skill_root = FORGE_ROOT / ".claude" / "skills" / "paper-writing"
        documents = forge_vocabulary.shipped_documents(skill_root)
        self.assertGreater(len(documents), 0, "no shipped documents found under paper-writing -- scan is broken")

        leaking = {}
        for document in documents:
            text = document.read_text(encoding="utf-8")
            if document.suffix == ".py":
                text = forge_vocabulary.scannable_suite_text(text)
            hits = forge_vocabulary.leaks_in(text)
            if hits:
                leaking[str(document.relative_to(FORGE_ROOT))] = hits

        self.assertEqual(leaking, {})


if __name__ == "__main__":
    unittest.main()
