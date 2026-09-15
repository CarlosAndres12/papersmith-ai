"""paper_graph: corpus assembly, the flat id namespace, `after` edge
resolution, the derived writing order.

Pure functions over parsed `ContractHeader` records once `assemble_corpus`
has read `sections_dir` (design.md, `Internal layering`: "pure functions
over parsed records — the half a later phase reuses whole"). Ordering comes
entirely from `position`, declaration order inside `blocks`, and transcribed
`after` edges — never from a filename. Files are read in sorted-name order
only so a run is reproducible; the name itself never enters any sort key.
"""
from __future__ import annotations

import heapq
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_contract  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

#: Orchestrator-settled deviation from design.md's rejected "enumerate seven
#: targets" option and from the spec's literal "resolve against the
#: skeleton fact" wording (recorded in `specs/section-contract/spec.md`'s
#: Implementation note and in tasks.md's own Notes / Deviations).
#: `skeleton` occurs exactly once across all ten shipped contracts and
#: names no body-section list anywhere, so the literal resolution has
#: nothing to read. `title-and-keywords`'s own sentence ("Every keyword
#: appears in the body") is honoured by COMPUTING "the body" instead of
#: enumerating it: every section whose `position` is strictly between
#: `abstract`'s and `back-matter`'s (positions 3-9 in the shipped corpus) —
#: looked up by section id, never a hardcoded integer or a filename.
_KEYWORD_BODY_HOLDER_SECTION = "title-and-keywords"
_KEYWORD_BODY_LOWER_ANCHOR = "abstract"
_KEYWORD_BODY_UPPER_ANCHOR = "back-matter"


@dataclass(frozen=True)
class BlockRecord:
    """One block, corpus-qualified. `qualified_id` is `<section>.<block id>`
    joined with `.` — the shape `main.tex` block ids take
    (design.md, `Block ids are section-qualified for global uniqueness`)."""

    section: str
    block_id: str
    qualified_id: str
    block_index: int
    position: int
    requires_facts: tuple
    requires_declarations: tuple
    citations: str
    optional: bool


@dataclass(frozen=True)
class Corpus:
    """`sections`: section id -> `ContractHeader`. `blocks`: qualified id ->
    `BlockRecord`. `order_by_section`: section id -> qualified ids in
    declaration order (the order each header's own `blocks` list states)."""

    sections: dict
    blocks: dict
    order_by_section: dict


def assemble_corpus(sections_dir: Path) -> Corpus:
    """Parse every `*.md` under `sections_dir`, sorted by filename for
    reproducibility only. Refuses `ID_COLLISION` (work-state) when a raw
    block id equals any section id anywhere in the corpus — the one flat
    namespace design.md's `one flat id namespace; after admits section and
    block ids` decision requires.

    Also verifies every transcribed `after` edge's own `source.quote`
    against `source.file`'s prose body (`_verify_after_transcription`) —
    the half of the transcription discipline `paper_contract.parse` cannot
    check by itself, because `source.file` may name a DIFFERENT contract
    than the one declaring the edge (the shipped `abstract` -> `conclusions`
    edge is sourced in `sections/07-conclusions.md`, not its own
    `08-abstract.md`). Every file this function reads is already read
    exactly once, in the loop below — this adds no second disk pass.
    """
    sections: dict = {}
    bodies: dict = {}
    for path in sorted(sections_dir.glob("*.md")):
        data = path.read_bytes()
        header, body = paper_contract.parse(data)
        sections[header.section] = header
        bodies[f"{sections_dir.name}/{path.name}"] = body

    section_ids = set(sections)
    blocks: dict = {}
    order_by_section: dict = {}
    for section_id, header in sections.items():
        order_by_section[section_id] = []
        for index, raw_block in enumerate(header.blocks):
            block_id = raw_block["id"]
            if block_id in section_ids:
                raise Refused(
                    "ID_COLLISION",
                    f"block id {block_id!r} in section {section_id!r} collides with a section id",
                )
            qualified_id = f"{section_id}.{block_id}"
            blocks[qualified_id] = BlockRecord(
                section=section_id,
                block_id=block_id,
                qualified_id=qualified_id,
                block_index=index,
                position=header.position,
                requires_facts=tuple(raw_block["requires_facts"]),
                requires_declarations=tuple(raw_block["requires_declarations"]),
                citations=raw_block["citations"],
                optional=raw_block["optional"],
            )
            order_by_section[section_id].append(qualified_id)

    corpus = Corpus(sections=sections, blocks=blocks, order_by_section=order_by_section)
    _verify_after_transcription(corpus, bodies)
    return corpus


def _verify_after_transcription(corpus: Corpus, bodies: dict) -> None:
    """Enforces, for every transcribed `after` entry whose OWN `target`
    resolves to something real in this corpus (`_resolve_target` below —
    reused rather than re-derived), the same transcription discipline
    `paper_contract.parse` already enforces for `mode`: the entry's
    `source.quote` must be a literal (whitespace-collapsed, markdown-
    emphasis-stripped) substring of `source.file`'s own prose body —
    `paper_contract.quote_in_body`, the one shared check, never a second
    copy of it.

    Skipped for a DANGLING target on purpose: `design.md`'s own "An
    absent after target is reported, never refused" already treats a
    dangling target as a legitimate, reportable state (deleting a
    contract mid-edit is explicitly in scope) — refusing on the quote of
    an edge that already names nothing would conflate two independent
    failures under one refusal. Every shipped `after` edge resolves, so
    this narrowing costs the real corpus nothing.
    """
    for section_id, header in corpus.sections.items():
        entries = list(header.after)
        for raw_block in header.blocks:
            entries += raw_block["after"]

        for entry in entries:
            if _resolve_target(corpus, entry["target"]) is None:
                continue
            source = entry["source"]
            body = bodies.get(source["file"])
            if body is None or not paper_contract.quote_in_body(body, source["quote"]):
                raise Refused(
                    "SPAN_NOT_IN_SOURCE",
                    f"{section_id}: after-edge quote {source['quote']!r} not found verbatim "
                    f"(whitespace-collapsed, markdown-emphasis-stripped) in "
                    f"{source['file']}'s prose body",
                )


def _resolve_target(corpus: Corpus, target_id: str) -> list | None:
    """A transcribed `after`'s `target` names a section (expands to every
    block of it, in declaration order) or a block (already section-
    qualified: a single-element list). `None` when it resolves to neither —
    the caller records it as a dangling edge rather than refusing
    (design.md, `An absent after target is reported, never refused`)."""
    if target_id in corpus.sections:
        return list(corpus.order_by_section[target_id])
    if target_id in corpus.blocks:
        return [target_id]
    return None


@dataclass
class EdgeSet:
    """`edges`: `(before_qualified_id, after_qualified_id, source)` triples
    -- `before` must be written first. `source` is the transcribing
    `{"file", "quote"}` dict, or `None` for the position-derived edge.
    `dangling`: every `after` target that resolved to nothing."""

    edges: list
    dangling: list


def collect_edges(corpus: Corpus) -> EdgeSet:
    """Every transcribed `after` edge, section- and block-level, plus the
    one position-derived edge (module docstring). This is the FULL edge
    list the topological sort consumes; a caller wanting only the literal,
    header-declared cross-section subset filters this same list by
    holder-section-vs-target-section, never hand-listing it."""
    edges: list = []
    dangling: list = []

    for section_id, header in corpus.sections.items():
        holder_blocks = corpus.order_by_section[section_id]

        for entry in header.after:
            targets = _resolve_target(corpus, entry["target"])
            if targets is None:
                dangling.append(entry["target"])
                continue
            for target_qualified in targets:
                for holder_qualified in holder_blocks:
                    edges.append((target_qualified, holder_qualified, entry["source"]))

        for raw_block, holder_qualified in zip(header.blocks, holder_blocks):
            for entry in raw_block["after"]:
                targets = _resolve_target(corpus, entry["target"])
                if targets is None:
                    dangling.append(entry["target"])
                    continue
                for target_qualified in targets:
                    edges.append((target_qualified, holder_qualified, entry["source"]))

    edges.extend(_position_derived_edges(corpus))

    return EdgeSet(edges=edges, dangling=dangling)


def _position_derived_edges(corpus: Corpus) -> list:
    """See module docstring / `_KEYWORD_BODY_*` constants."""
    if (_KEYWORD_BODY_HOLDER_SECTION not in corpus.sections
            or _KEYWORD_BODY_LOWER_ANCHOR not in corpus.sections
            or _KEYWORD_BODY_UPPER_ANCHOR not in corpus.sections):
        return []

    lower = corpus.sections[_KEYWORD_BODY_LOWER_ANCHOR].position
    upper = corpus.sections[_KEYWORD_BODY_UPPER_ANCHOR].position
    holder_blocks = corpus.order_by_section[_KEYWORD_BODY_HOLDER_SECTION]

    edges = []
    for section_id, header in corpus.sections.items():
        if section_id == _KEYWORD_BODY_HOLDER_SECTION:
            continue
        if lower < header.position < upper:
            for target_qualified in corpus.order_by_section[section_id]:
                for holder_qualified in holder_blocks:
                    edges.append((target_qualified, holder_qualified, None))
    return edges


def _sort_key(corpus: Corpus, qualified_id: str) -> tuple:
    """`(section.position, block_index_within_section, block_id)` — every
    component read from the header, none from dict iteration, `os.listdir`
    or the filename (design.md, `The sort, and how ties are broken`)."""
    record = corpus.blocks[qualified_id]
    return (record.position, record.block_index, qualified_id)


def derive_order(corpus: Corpus, edge_set: EdgeSet) -> list:
    """Kahn's algorithm over the block graph, min-heap tie-broken by
    `_sort_key`. Refuses `ORDER_CYCLE` (work-state), naming the
    participating blocks, when Kahn terminates with nodes remaining — a
    minimal cycle extracted by DFS over the residual subgraph.
    """
    successors: dict = {qid: [] for qid in corpus.blocks}
    indegree: dict = {qid: 0 for qid in corpus.blocks}
    for before, after, _source in edge_set.edges:
        successors[before].append(after)
        indegree[after] += 1

    heap = [(_sort_key(corpus, qid), qid) for qid, degree in indegree.items() if degree == 0]
    heapq.heapify(heap)

    remaining_indegree = dict(indegree)
    order: list = []
    while heap:
        _key, qid = heapq.heappop(heap)
        order.append(qid)
        for successor in successors[qid]:
            remaining_indegree[successor] -= 1
            if remaining_indegree[successor] == 0:
                heapq.heappush(heap, (_sort_key(corpus, successor), successor))

    if len(order) != len(corpus.blocks):
        remaining = set(corpus.blocks) - set(order)
        cycle = _extract_minimal_cycle(remaining, successors)
        raise Refused("ORDER_CYCLE", f"a cycle among blocks: {' -> '.join(cycle)}")

    return order


def _extract_minimal_cycle(remaining: set, successors: dict) -> list:
    """DFS over the residual subgraph (`remaining` nodes only) for one
    cycle, reported as an ordered id list. Deterministic: nodes are tried
    in sorted order, so a given residual subgraph always reports the same
    cycle."""
    visiting: set = set()
    visited: set = set()
    path: list = []

    def dfs(node: str):
        visiting.add(node)
        path.append(node)
        for successor in successors[node]:
            if successor not in remaining:
                continue
            if successor in visiting:
                start = path.index(successor)
                return path[start:] + [successor]
            if successor not in visited:
                found = dfs(successor)
                if found is not None:
                    return found
        visiting.discard(node)
        visited.add(node)
        path.pop()
        return None

    for start_node in sorted(remaining):
        if start_node in visited:
            continue
        found = dfs(start_node)
        if found is not None:
            return found
    return sorted(remaining)
