"""no-claim-without-a-source-that-holds-it: WU1 (the evidence channel) and
WU2 (the bibliography that was never typed).

Same shape `tests/test_paper_contract.py` and `tests/test_paper_writing.py`
already use: every fixture lives under a `TemporaryDirectory`, `setUp`
installs a raising `OPENER` module-wide so an accidental live network call
fails loudly instead of passing slowly, and the mutation tests reuse
`_run_against_mutant` from `tests/paper_mutation.py`.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
import urllib.error
import urllib.request
from pathlib import Path

FORGE_ROOT = Path(__file__).resolve().parents[1]
SKILL_SCRIPTS = FORGE_ROOT / ".claude" / "skills" / "paper-writing" / "scripts"
SECTIONS_DIR = FORGE_ROOT / "sections"
sys.path.insert(0, str(SKILL_SCRIPTS))
import paper_cli  # noqa: E402
import paper_evidence  # noqa: E402
import paper_resolve  # noqa: E402
import paper_scaffold  # noqa: E402

sys.path.insert(0, str(FORGE_ROOT / ".claude" / "skills" / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paper_mutation import _run_against_mutant  # noqa: E402


class _RaisingOpener:
    """The module-level `OPENER` seam (`design.md`, Decision 3, Test seam):
    every request this fakes raises `URLError` with no socket ever touched,
    proving the offline refusal path with zero live network access."""

    def open(self, request, timeout=None):  # noqa: A003 -- mirrors OpenerDirector.open
        raise urllib.error.URLError("test seam: network is not reachable")


class _AnsweringOpener:
    """Returns a fixed byte payload for any request -- used to prove the
    guard is NOT firing when the transport genuinely answers."""

    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def open(self, request, timeout=None):
        return _FakeResponse(self._payload)


class _FakeResponse:
    def __init__(self, payload: bytes) -> None:
        self._payload = payload

    def read(self) -> bytes:
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class _NotFoundOpener:
    def open(self, request, timeout=None):
        raise urllib.error.HTTPError(request.full_url, 404, "Not Found", {}, None)


def _config(resolution=("openalex",), discovery=(), contact="") -> dict:
    return {
        "paper_writing": {
            "contact": contact,
            "roles": {
                "discovery": list(discovery),
                "resolution": list(resolution),
                "full-text": [],
            },
        }
    }


class VerdictConstructionTests(unittest.TestCase):
    """design.md Decision 2: `Verdict` has no public string-taking
    constructor; `.holds`/`.does_not_hold` require a real span
    positionally, and only `.insufficient` can be built without one."""

    def test_holds_requires_a_span_positionally(self) -> None:
        with self.assertRaises(TypeError):
            paper_evidence.Verdict.holds()  # type: ignore[call-arg]

    def test_does_not_hold_requires_a_span_positionally(self) -> None:
        with self.assertRaises(TypeError):
            paper_evidence.Verdict.does_not_hold()  # type: ignore[call-arg]

    def test_no_public_string_taking_constructor_exists(self) -> None:
        with self.assertRaises(TypeError):
            paper_evidence.Verdict(value="holds", span=None, reason=None)

    def test_holds_with_none_span_refuses(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_evidence.Verdict.holds(None)
        self.assertEqual(ctx.exception.code, "VERDICT_SPAN_REQUIRED")

    def test_insufficient_needs_no_span(self) -> None:
        verdict = paper_evidence.Verdict.insufficient("no source located")
        self.assertEqual(verdict.value, "insufficient")
        self.assertIsNone(verdict.span)


class EvidenceSpanTests(unittest.TestCase):
    """`EvidenceSpan.locate` byte-searches the ingested `.md`; a quote not
    literally present refuses `SPAN_NOT_IN_SOURCE` rather than becoming a
    span (`evidence-set`, Requirement: A Spanless Record Is Insufficient By
    Construction)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)

    def test_locate_finds_the_verbatim_quote(self) -> None:
        source = self.root / "ingested.md"
        source.write_text("The estimator converges under bounded variance.\n", encoding="utf-8")
        span = paper_evidence.EvidenceSpan.locate(source, "converges under bounded variance")
        self.assertEqual(span.byte_start, source.read_bytes().find(b"converges under bounded variance"))
        self.assertEqual(span.byte_end - span.byte_start, len("converges under bounded variance"))
        self.assertTrue(span.file_sha256)

    def test_a_paraphrase_refuses_span_not_in_source(self) -> None:
        source = self.root / "ingested.md"
        source.write_text("The estimator converges under bounded variance.\n", encoding="utf-8")
        with self.assertRaises(Refused) as ctx:
            paper_evidence.EvidenceSpan.locate(source, "the estimator always converges")
        self.assertEqual(ctx.exception.code, "SPAN_NOT_IN_SOURCE")

    def test_a_span_authored_to_look_right_but_not_byte_identical_refuses(self) -> None:
        # One character off from a real sentence in the source -- looks
        # right to a human skim, is not byte-identical (design.md, Decision
        # 7b: "a fixture and a span authored together still have to agree
        # byte-for-byte or SPAN_NOT_IN_SOURCE fires").
        source = self.root / "ingested.md"
        source.write_text("The dataset contains 4,096 labeled examples.\n", encoding="utf-8")
        near_miss = "The dataset contains 4,095 labeled examples."
        self.assertNotIn(near_miss, source.read_text(encoding="utf-8"))
        with self.assertRaises(Refused) as ctx:
            paper_evidence.EvidenceSpan.locate(source, near_miss)
        self.assertEqual(ctx.exception.code, "SPAN_NOT_IN_SOURCE")

    def test_empty_quote_refuses(self) -> None:
        source = self.root / "ingested.md"
        source.write_text("non-empty content\n", encoding="utf-8")
        with self.assertRaises(Refused) as ctx:
            paper_evidence.EvidenceSpan.locate(source, "")
        self.assertEqual(ctx.exception.code, "SPAN_NOT_IN_SOURCE")

    def test_domain_independent_fixture_a_pre_existing_repository_document(self) -> None:
        # design.md, Decision 7c / Testing Strategy leg 3: one fixture
        # nobody wrote for this test -- a verbatim excerpt of a repository
        # document that predates the validator. README.md is prose about
        # this repository's own tooling, not a science paper: it proves
        # independence of AUTHORSHIP (this quote was not shaped to pass),
        # never independence of DOMAIN. That limit is stated here, not
        # silently assumed.
        readme = FORGE_ROOT / "README.md"
        self.assertTrue(readme.is_file(), "README.md must exist for this fixture to mean anything")
        quote = "Una forja de papers: ingiere PDFs de referencia a Markdown de alta fidelidad y"
        span = paper_evidence.EvidenceSpan.locate(readme, quote)
        self.assertEqual(span.quote, quote)


class AdversarialPairingTests(unittest.TestCase):
    """design.md, Testing Strategy leg 1: the SAME bytes must be able to
    produce `holds` for one claim and `does-not-hold` for another -- proving
    the mechanism does not silently collapse every verdict to one pole. An
    author who shaped the source to satisfy the matcher would make the
    `does-not-hold` claim pass too; it does not, because the verdict is the
    caller's own judgment against a real, located span, never derived from
    the quote's mere presence."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.source = Path(self._tmp.name) / "ingested.md"
        self.source.write_text(
            "The proposed estimator achieves a 12% reduction in test error "
            "on the benchmark suite. The baseline model was not evaluated "
            "on out-of-distribution inputs in this study.\n",
            encoding="utf-8",
        )

    def test_claim_a_holds_from_its_own_verbatim_span(self) -> None:
        span = paper_evidence.EvidenceSpan.locate(
            self.source, "achieves a 12% reduction in test error"
        )
        verdict = paper_evidence.Verdict.holds(span)
        self.assertEqual(verdict.value, "holds")
        self.assertEqual(verdict.span.source_md, str(self.source))

    def test_claim_b_does_not_hold_from_a_real_but_unsupporting_span(self) -> None:
        # The claim under test: "the baseline WAS evaluated on
        # out-of-distribution inputs" -- the located span is real (it is in
        # the file, byte for byte) but it says the opposite, so the caller
        # (standing in for the agent's own judgment) records does-not-hold.
        span = paper_evidence.EvidenceSpan.locate(
            self.source, "was not evaluated on out-of-distribution inputs"
        )
        verdict = paper_evidence.Verdict.does_not_hold(span)
        self.assertEqual(verdict.value, "does-not-hold")
        self.assertIsNotNone(verdict.span)


class EvidenceRecordStoreTests(unittest.TestCase):
    """`evidence-set`, Requirement: The Claim<->Source Record Shape, and the
    JSONL store at `paper/.paper-writing/evidence/<block-id>.jsonl`."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.paper_dir = Path(self._tmp.name) / "paper"
        self.paper_dir.mkdir()
        self.source = Path(self._tmp.name) / "quote.md"
        self.source.write_text("Training used 30 random seeds per configuration.\n", encoding="utf-8")

    def test_a_complete_record_round_trips_through_the_store(self) -> None:
        span = paper_evidence.EvidenceSpan.locate(self.source, "30 random seeds per configuration")
        verdict = paper_evidence.Verdict.holds(span)
        record = paper_evidence.EvidenceRecord.from_verdict(
            block_id="results.main-claim", regime="discovery", claim="30 seeds were used",
            cite_key="smith2024", identifier="10.1/example", resolver="openalex",
            metadata_digest="abc123", verdict=verdict, round=1,
        )
        paper_evidence.append_record(self.paper_dir, record)
        stored = paper_evidence.read_records(self.paper_dir, "results.main-claim")
        self.assertEqual(len(stored), 1)
        self.assertEqual(stored[0]["verdict"], "holds")
        self.assertEqual(stored[0]["quote"], "30 random seeds per configuration")
        self.assertTrue(stored[0]["locator"]["file_sha256"])
        self.assertEqual(stored[0]["claim"], "30 seeds were used")

    def test_a_spanless_record_carries_empty_span_fields(self) -> None:
        verdict = paper_evidence.Verdict.insufficient("no candidate source found")
        record = paper_evidence.EvidenceRecord.from_verdict(
            block_id="results.main-claim", regime="none", claim="unsupported claim",
            cite_key="", identifier="", resolver="", metadata_digest="",
            verdict=verdict, round=1,
        )
        self.assertEqual(record.source_md, "")
        self.assertEqual(record.quote, "")
        self.assertEqual(record.locator, {})

    def test_reading_an_unwritten_block_returns_empty(self) -> None:
        self.assertEqual(paper_evidence.read_records(self.paper_dir, "never-written"), [])

    def test_multiple_appends_accumulate_in_order(self) -> None:
        for round_number in (1, 2):
            verdict = paper_evidence.Verdict.insufficient(f"round {round_number}")
            record = paper_evidence.EvidenceRecord.from_verdict(
                block_id="b", regime="none", claim="c", cite_key="", identifier="",
                resolver="", metadata_digest="", verdict=verdict, round=round_number,
            )
            paper_evidence.append_record(self.paper_dir, record)
        stored = paper_evidence.read_records(self.paper_dir, "b")
        self.assertEqual([r["round"] for r in stored], [1, 2])


class ManifestProducerTests(unittest.TestCase):
    """`evidence-set`, Requirement: Evidence Folders Carry a Producer-
    Written Manifest -- `append_record` marks the guidance folder its span's
    source sits under, the real production caller of `write_evidence_manifest`
    (never a second, test-only write path)."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.paper_dir = self.root / "paper"
        self.paper_dir.mkdir()
        self.guidance_dir = self.root / "guidance"
        self.folder = self.guidance_dir / "06-introduction"
        self.folder.mkdir(parents=True)
        self.source = self.folder / "paper1.md"
        self.source.write_text("A verbatim sentence about the field.\n", encoding="utf-8")

    def test_appending_a_record_with_a_real_span_marks_its_guidance_folder(self) -> None:
        span = paper_evidence.EvidenceSpan.locate(self.source, "verbatim sentence about the field")
        verdict = paper_evidence.Verdict.holds(span)
        record = paper_evidence.EvidenceRecord.from_verdict(
            block_id="intro.claim", regime="discovery", claim="claim text", cite_key="paper1",
            identifier="10.1/x", resolver="openalex", metadata_digest="d", verdict=verdict, round=1,
        )
        paper_evidence.append_record(self.paper_dir, record, guidance_dir=self.guidance_dir)
        manifest_path = self.folder / ".papersmith-evidence.json"
        self.assertTrue(manifest_path.is_file())
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(manifest["kind"], "evidence")
        self.assertEqual(manifest["section"], "06-introduction")
        self.assertIn("paper1", manifest["blocks"])

    def test_an_insufficient_record_marks_nothing(self) -> None:
        verdict = paper_evidence.Verdict.insufficient("nothing located")
        record = paper_evidence.EvidenceRecord.from_verdict(
            block_id="intro.claim", regime="discovery", claim="claim text", cite_key="paper1",
            identifier="", resolver="", metadata_digest="", verdict=verdict, round=1,
        )
        paper_evidence.append_record(self.paper_dir, record, guidance_dir=self.guidance_dir)
        self.assertFalse((self.folder / ".papersmith-evidence.json").exists())

    def test_a_source_outside_guidance_dir_marks_nothing_and_never_refuses(self) -> None:
        outside = self.root / "elsewhere.md"
        outside.write_text("some text\n", encoding="utf-8")
        span = paper_evidence.EvidenceSpan.locate(outside, "some text")
        verdict = paper_evidence.Verdict.holds(span)
        record = paper_evidence.EvidenceRecord.from_verdict(
            block_id="b", regime="none", claim="c", cite_key="k", identifier="",
            resolver="", metadata_digest="", verdict=verdict, round=1,
        )
        result = paper_evidence.append_record(self.paper_dir, record, guidance_dir=self.guidance_dir)
        self.assertNotIn("manifest", result)


class GuidanceClassificationTests(unittest.TestCase):
    """`classify_guidance_child` -- two independent discriminators, derived
    from `sections/*.md` at runtime, never a literal list. Every fixture
    builds its OWN `guidance/` and `sections/` tree under a temp dir; no
    test here ever opens the repository's real `guidance/` tree, which is
    gitignored working state whose contents vary per operator machine and
    must never be assumed empty."""

    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        self.sections_dir = self.root / "sections"
        self.sections_dir.mkdir()
        (self.sections_dir / "06-introduction.md").write_text("stub", encoding="utf-8")
        (self.sections_dir / "05-related-work.md").write_text("stub", encoding="utf-8")
        self.guidance_dir = self.root / "guidance"
        self.guidance_dir.mkdir()

    def test_name_and_manifest_both_present_is_evidence(self) -> None:
        folder = self.guidance_dir / "06-introduction"
        folder.mkdir()
        (folder / ".papersmith-evidence.json").write_text(
            json.dumps({"kind": "evidence", "section": "06-introduction", "created_by": "x", "blocks": []}),
            encoding="utf-8",
        )
        self.assertEqual(
            paper_evidence.classify_guidance_child(folder, sections_dir=self.sections_dir), "evidence"
        )

    def test_neither_present_is_style(self) -> None:
        folder = self.guidance_dir / "some-style-notes"
        folder.mkdir()
        self.assertEqual(
            paper_evidence.classify_guidance_child(folder, sections_dir=self.sections_dir), "style"
        )

    def test_name_only_is_ambiguous(self) -> None:
        folder = self.guidance_dir / "05-related-work"
        folder.mkdir()
        self.assertEqual(
            paper_evidence.classify_guidance_child(folder, sections_dir=self.sections_dir), "ambiguous"
        )

    def test_manifest_only_is_ambiguous(self) -> None:
        folder = self.guidance_dir / "not-a-section-id"
        folder.mkdir()
        (folder / ".papersmith-evidence.json").write_text(
            json.dumps({"kind": "evidence", "section": "not-a-section-id", "created_by": "x", "blocks": []}),
            encoding="utf-8",
        )
        self.assertEqual(
            paper_evidence.classify_guidance_child(folder, sections_dir=self.sections_dir), "ambiguous"
        )

    def test_renaming_a_section_id_moves_the_evidence_folder_with_zero_code_changed(self) -> None:
        # proposal.md, Success Criteria: "Renaming a section id in sections/
        # moves the evidence folder with zero code changed." Prove it: a
        # freshly-renamed section id, unknown to any literal list in this
        # module, is recognized the moment it exists on disk.
        (self.sections_dir / "99-a-brand-new-section.md").write_text("stub", encoding="utf-8")
        folder = self.guidance_dir / "99-a-brand-new-section"
        folder.mkdir()
        (folder / ".papersmith-evidence.json").write_text(
            json.dumps({"kind": "evidence", "section": "99-a-brand-new-section", "created_by": "x", "blocks": []}),
            encoding="utf-8",
        )
        self.assertEqual(
            paper_evidence.classify_guidance_child(folder, sections_dir=self.sections_dir), "evidence"
        )


class ConfigParsingTests(unittest.TestCase):
    """`paper_resolve.parse_yaml_subset` -- the constrained reader that
    keeps `paper-writing` stdlib-only end to end."""

    def test_round_trips_roles_and_contact(self) -> None:
        text = (
            "paper_ingestion:\n"
            "  engine: marker  # a trailing comment\n"
            "  source_roots: []\n"
            "\n"
            "paper_writing:\n"
            "  contact: \"a@b.example\"\n"
            "  roles:\n"
            "    discovery: []\n"
            "    resolution:\n"
            "      - openalex\n"
            "      - crossref\n"
            "    full-text: []\n"
        )
        parsed = paper_resolve.parse_yaml_subset(text)
        self.assertEqual(parsed["paper_writing"]["contact"], "a@b.example")
        self.assertEqual(parsed["paper_writing"]["roles"]["resolution"], ["openalex", "crossref"])
        self.assertEqual(parsed["paper_ingestion"]["engine"], "marker")

    def test_malformed_line_raises_value_error(self) -> None:
        with self.assertRaises(ValueError):
            paper_resolve.parse_yaml_subset("not a mapping line at all")

    def test_load_config_refuses_papersmith_config_unreadable_for_a_missing_file(self) -> None:
        missing = Path(tempfile.mkdtemp()) / "nope.yaml"
        with self.assertRaises(Refused) as ctx:
            paper_resolve.load_config(missing)
        self.assertEqual(ctx.exception.code, "PAPERSMITH_CONFIG_UNREADABLE")

    def test_the_real_papersmith_yaml_declares_the_resolution_role(self) -> None:
        config = paper_resolve.load_config()
        self.assertIn("openalex", config["paper_writing"]["roles"]["resolution"])


class RoleConnectorTests(unittest.TestCase):
    def test_an_empty_discovery_role_refuses_discovery_unavailable(self) -> None:
        config = _config(discovery=())
        with self.assertRaises(Refused) as ctx:
            paper_resolve.require_role_connectors(config, "discovery")
        self.assertEqual(ctx.exception.code, "DISCOVERY_UNAVAILABLE")

    def test_an_empty_resolution_role_refuses_resolver_role_empty(self) -> None:
        config = _config(resolution=())
        with self.assertRaises(Refused) as ctx:
            paper_resolve.require_role_connectors(config, "resolution")
        self.assertEqual(ctx.exception.code, "RESOLVER_ROLE_EMPTY")

    def test_an_unknown_role_refuses(self) -> None:
        with self.assertRaises(Refused) as ctx:
            paper_resolve.connectors_for_role(_config(), "translation")
        self.assertEqual(ctx.exception.code, "UNKNOWN_ROLE")


class ResolverKeylessTests(unittest.TestCase):
    """literature-search, Requirement: Resolution Runs Through the CLI Over
    Stdlib `urllib` -- `mailto` from config, never hardcoded; no API key or
    secret anywhere on this path."""

    def test_mailto_sourced_from_config_contact(self) -> None:
        config = _config(contact="reader@example.org")
        url = paper_resolve._openalex_url("10.1000/example", config)
        self.assertIn("mailto=reader%40example.org", url)

    def test_no_contact_means_no_mailto_parameter(self) -> None:
        config = _config(contact="")
        url = paper_resolve._openalex_url("10.1000/example", config)
        self.assertNotIn("mailto", url)

    def test_resolution_source_holds_no_hardcoded_api_key(self) -> None:
        source = (SKILL_SCRIPTS / "paper_resolve.py").read_text(encoding="utf-8")
        self.assertNotIn("api_key", source.lower())
        self.assertNotIn("Bearer ", source)


class ResolverOfflineTests(unittest.TestCase):
    """`literature-search`, Requirement: Unreachable Connectors Refuse By
    Name -- proven with the raising `OPENER` seam, zero live network."""

    def setUp(self) -> None:
        self._real_opener = paper_resolve.OPENER
        self.addCleanup(self._restore_opener)

    def _restore_opener(self) -> None:
        paper_resolve.OPENER = self._real_opener

    def test_unreachable_resolver_refuses_with_the_named_code(self) -> None:
        paper_resolve.OPENER = _RaisingOpener()
        config = _config()
        with self.assertRaises(Refused) as ctx:
            paper_resolve.resolve_identifier(
                "10.1000/example", resolver="openalex", role="resolution", config=config,
            )
        self.assertEqual(ctx.exception.code, "RESOLVER_UNREACHABLE")

    def test_unreachable_resolver_cli_call_exits_non_zero(self) -> None:
        paper_resolve.OPENER = _RaisingOpener()
        exit_code = paper_cli.main(
            ["resolve", "--identifier", "10.1000/example", "--resolver", "openalex", "--role", "resolution"]
        )
        self.assertEqual(exit_code, 2)

    def test_a_none_regime_block_is_unaffected_by_every_connector_being_unreachable(self) -> None:
        # literature-search, Scenario: A none block is unaffected -- proven
        # here by showing the write path this change touches
        # (paper_scaffold/paper_block, unchanged by this work unit) never
        # even consults paper_resolve, so an unreachable OPENER cannot
        # possibly affect it.
        paper_resolve.OPENER = _RaisingOpener()
        with tempfile.TemporaryDirectory() as tmp:
            paper_dir = Path(tmp) / "paper"
            result = paper_scaffold.scaffold(paper_dir)
            self.assertIn("main.tex", result["created"])

    def test_a_not_found_identifier_refuses_identifier_unresolved(self) -> None:
        paper_resolve.OPENER = _NotFoundOpener()
        config = _config()
        with self.assertRaises(Refused) as ctx:
            paper_resolve.resolve_identifier(
                "10.1000/does-not-exist", resolver="openalex", role="resolution", config=config,
            )
        self.assertEqual(ctx.exception.code, "IDENTIFIER_UNRESOLVED")

    def test_a_reachable_resolver_returns_metadata_and_caches_it(self) -> None:
        payload = json.dumps({"title": "A Paper", "doi": "10.1/x", "publication_year": 2024}).encode()
        paper_resolve.OPENER = _AnsweringOpener(payload)
        config = _config()
        result = paper_resolve.resolve_identifier(
            "10.1/x", resolver="openalex", role="resolution", config=config,
        )
        self.assertEqual(result["title"], "A Paper")
        self.assertTrue(result["metadata_digest"])
        with tempfile.TemporaryDirectory() as tmp:
            paper_dir = Path(tmp) / "paper"
            paper_dir.mkdir()
            paper_resolve.cache_metadata(paper_dir, result)
            cached = paper_resolve.read_cached_metadata(paper_dir, result["metadata_digest"])
            self.assertEqual(cached["title"], "A Paper")


class ResolverMutationProofTests(unittest.TestCase):
    """m1 (design.md, Testing Strategy, Mutations table): the offline guard
    itself must be load-bearing, proven by disabling it and watching the
    corresponding refusal test fail."""

    def test_m1_unreachable_guard_disabled_fails_the_refusal_test(self) -> None:
        proc = _run_against_mutant(
            'raise Refused("RESOLVER_UNREACHABLE", str(exc))',
            'return {"identifier": identifier, "resolver": resolver, "metadata_digest": "",'
            ' "title": None, "doi": None, "year": None}',
            "tests.test_paper_evidence.ResolverOfflineTests.test_unreachable_resolver_refuses_with_the_named_code",
            source_path=SKILL_SCRIPTS / "paper_resolve.py",
        )
        output = proc.stdout + proc.stderr
        self.assertIn("MUTANT_IMPORTED_OK", output, output)
        self.assertNotEqual(proc.returncode, 0, output)


if __name__ == "__main__":
    unittest.main()
