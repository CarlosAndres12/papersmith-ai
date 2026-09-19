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
import re
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

#: `contract-input-partition` spec, `Requirement: Two-Heading Partition`.
#: Exact heading lines every contract's prose body must carry — checked by
#: `_verify_input_partition` below, never by a filename or a header field.
_EXTERNAL_INPUTS_HEADING = "### External inputs"
_INTERNAL_CHAIN_HEADING = "### Internal chain"

#: `internal-chain-edges` spec / `contract-input-partition` spec,
#: `Requirement: Internal-Chain Rows Name Qualified Block Ids`. A normalized
#: row's own cell OPENS with a backticked qualified id (design.md, D1: "The
#: reader consumes the leading backticked token and never reads the
#: gloss") — this is the only thing `_chain_row_id` below reads.
_CHAIN_ROW_ANCHOR_RE = re.compile(r"`([^`]+)`")
_CHAIN_ROW_SEPARATOR_RE = re.compile(r"^[-:\s]+$")

#: tasks.md 4.8b-4.8i: the PROSE -> HEADER direction no other check covers.
#: `_UNIT_PARENT_RE` matches the numbered-block heading convention six of
#: ten contracts use (`01`, `02`, `05`, `06`, `07`, `08`); the other four
#: name blocks by content (`## Funding`, `## The closing`, `## Keywords`)
#: and never match this pattern at all — the per-section gate tasks.md
#: 4.8i asks for falls out of the pattern itself, never a second flag.
#: `_UNIT_CHILD_RE` matches a `###` sub-heading naming a sub-unit
#: (`Paragraph 4a`, never `### What is cited here`, which carries no unit
#: word and is correctly ignored).
_UNIT_PARENT_RE = re.compile(r"^#{2}\s+(?:Block|Slot|Subsection)\s+(\d+)\b")
_UNIT_CHILD_RE = re.compile(r"^#{3}\s+(?:Paragraph|Block|Slot|Subsection|Part)\s+(\d+[A-Za-z]*)\b")
_ANY_TOP_HEADING_RE = re.compile(r"^#{1,2}\s")

#: A section's own ids carry the heading's number only when the ids
#: THEMSELVES are numbered (`block-1`, `slot-1`, `block-4a`) rather than
#: named by content (`mm-dataset`, `es-assessment`, `rw-closing`).
#: Measured: `01`, `02` and `05` all use the `## Slot|Subsection|Block N`
#: HEADING convention with content-named ids — a numbered heading there is
#: a human ordinal label, not a claim about a specific id, and the
#: parent-heading correspondence `_verify_block_subunits` checks only means
#: something where the ids themselves carry the number (`06`, `07`, `08`).
#: This is the precise gate 4.8i's own heading-pattern criterion widens
#: into once measured against the real corpus — a heading-pattern gate
#: alone would misfire `BLOCK_SUBUNIT_UNDECLARED` on `01`'s own
#: `## Slot 1 — The dataset` (id `mm-dataset`, no numeric suffix at all).
_NUMERIC_ID_SUFFIX_RE = re.compile(r"-\d+[A-Za-z]*$")


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

    Also verifies every `### Internal chain` row transcribes to a real,
    backed `after` edge (`_verify_internal_chain`) and that no prose
    heading announces a sub-unit the header never declared
    (`_verify_block_subunits`) — `section_bodies` (section id -> its own
    body) is built in the SAME loop as `bodies`, from the same read,
    keyed by `header.section` rather than a filename.
    """
    sections: dict = {}
    bodies: dict = {}
    section_bodies: dict = {}
    for path in sorted(sections_dir.glob("*.md")):
        data = path.read_bytes()
        header, body = paper_contract.parse(data)
        sections[header.section] = header
        bodies[f"{sections_dir.name}/{path.name}"] = body
        section_bodies[header.section] = body

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
                requires_facts=paper_contract.requirement_values(raw_block["requires_facts"]),
                requires_declarations=paper_contract.requirement_values(
                    raw_block["requires_declarations"]
                ),
                citations=raw_block["citations"],
                optional=raw_block["optional"],
            )
            order_by_section[section_id].append(qualified_id)

    corpus = Corpus(sections=sections, blocks=blocks, order_by_section=order_by_section)
    _verify_input_partition(corpus, bodies)
    _verify_after_transcription(corpus, bodies)
    _verify_internal_chain(corpus, bodies)
    _verify_block_subunits(corpus, section_bodies)
    return corpus


def _verify_input_partition(corpus: Corpus, bodies: dict) -> None:
    """`contract-input-partition` spec, `Requirement: Two-Heading
    Partition`. Refuses `INPUT_PARTITION_ABSENT` (work-state) naming
    whichever of `### External inputs` / `### Internal chain` is missing
    from a contract's own prose body — reads the SAME `bodies` dict
    `_verify_after_transcription` already holds, so this costs zero extra
    disk passes. `corpus` is accepted for the same signature shape as its
    sibling `_verify_internal_chain` (design.md, Interfaces / Contracts);
    the check itself is purely a body-text scan, no corpus data needed.

    `### Internal chain` is checked first: when a flat, unpartitioned
    contract carries neither heading, naming the internal-chain gap is the
    more actionable report, since that is the half this change exists to
    make explicit and machine-addressable (`specs/contract-input-
    partition/spec.md`'s own "flat, unpartitioned contract" scenario)."""
    for file_key, body in bodies.items():
        text = body.decode("utf-8")
        for heading in (_INTERNAL_CHAIN_HEADING, _EXTERNAL_INPUTS_HEADING):
            if not re.search(rf"(?m)^{re.escape(heading)}\s*$", text):
                raise Refused(
                    "INPUT_PARTITION_ABSENT",
                    f"{file_key}: missing {heading!r} heading in the contract's prose body",
                )


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


def _internal_chain_rows(text: str) -> list:
    """Every data row of a contract's own `### Internal chain` markdown
    table, as `(holder_cell, dependency_cell)` raw text pairs — bounded by
    the next `##`/`###` heading, or EOF when none follows. A contract
    reporting no internal dependencies (`04`/`07`'s own checkable "None —
    ..." prose, no table at all) yields an empty list: nothing for
    `_verify_internal_chain` to check for that file, matching the
    genuinely-empty case `contract-input-partition` already accepts."""
    match = re.search(rf"(?m)^{re.escape(_INTERNAL_CHAIN_HEADING)}\s*$", text)
    if match is None:
        return []
    section_text = text[match.end():]
    next_heading = re.search(r"(?m)^#{2,3}\s", section_text)
    if next_heading is not None:
        section_text = section_text[:next_heading.start()]

    rows = []
    for line in section_text.splitlines():
        line = line.strip()
        if not (line.startswith("|") and line.endswith("|")):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != 2:
            continue
        holder_cell, dependency_cell = cells
        if holder_cell == "Block" and dependency_cell == "Depends on":
            continue  # the table's own header row
        if _CHAIN_ROW_SEPARATOR_RE.match(holder_cell):
            continue  # the `|---|---|` separator row
        rows.append((holder_cell, dependency_cell))
    return rows


def _chain_row_id(cell: str) -> str | None:
    """A row cell's own LEADING backticked token — `_resolve_target`'s
    exact input shape — or `None` when the cell opens on prose instead
    (design.md, D1: "The reader consumes the leading backticked token and
    never reads the gloss")."""
    match = _CHAIN_ROW_ANCHOR_RE.match(cell)
    return match.group(1) if match else None


def _verify_internal_chain(corpus: Corpus, bodies: dict) -> None:
    """`internal-chain-edges` spec, both Requirements; `contract-input-
    partition` spec, `Requirement: Internal-Chain Rows Name Qualified Block
    Ids`. Reads the SAME `bodies` dict `_verify_after_transcription`
    already holds — zero extra disk passes (design.md, Data Flow).

    For every `### Internal chain` row: refuses `CHAIN_ROW_UNRESOLVED`
    (naming the row's own text) when either cell's leading backticked
    token is missing or is not a key of `corpus.blocks`; refuses
    `CHAIN_ROW_UNBACKED` (naming the holder and the dependency) when both
    resolve but no `after` edge backs `(dependency, holder)` in the block
    graph. Reuses `collect_edges` for the live edge set — never a second,
    independent edge derivation that could disagree with the one `order`/
    `readiness`/`derive_waves` actually consume.
    """
    edge_pairs = {(before, after) for before, after, _source in collect_edges(corpus).edges}
    for file_key, body in bodies.items():
        text = body.decode("utf-8")
        for holder_cell, dependency_cell in _internal_chain_rows(text):
            row_text = f"{holder_cell} | {dependency_cell}"
            holder_id = _chain_row_id(holder_cell)
            dependency_id = _chain_row_id(dependency_cell)
            if holder_id is None or holder_id not in corpus.blocks:
                raise Refused(
                    "CHAIN_ROW_UNRESOLVED",
                    f"{file_key}: {row_text!r} names no qualified block id for its subject",
                )
            if dependency_id is None or dependency_id not in corpus.blocks:
                raise Refused(
                    "CHAIN_ROW_UNRESOLVED",
                    f"{file_key}: {row_text!r} names no qualified block id for its dependency",
                )
            if (dependency_id, holder_id) not in edge_pairs:
                raise Refused(
                    "CHAIN_ROW_UNBACKED",
                    f"{file_key}: {holder_id} depends on {dependency_id}, but no "
                    f"'after' edge backs that pair",
                )


def _numbered_block_ids(corpus: Corpus, section_id: str, number: str) -> list:
    """Every declared id in `section_id` whose own local suffix — after the
    last `-` — starts with `number` (`block-4a` and `block-4b` both match
    `number='4'`; `block-1` matches `number='1'` and nothing else does).
    The correspondence a numbered `##`/`###` heading makes with the
    header's OWN declared ids — read from `corpus`, never assumed from the
    heading text alone."""
    matches = []
    for qualified_id in corpus.order_by_section[section_id]:
        suffix = qualified_id.rsplit("-", 1)[-1]
        if re.match(rf"^{re.escape(number)}[A-Za-z]*$", suffix):
            matches.append(qualified_id)
    return matches


def _section_uses_numbered_ids(corpus: Corpus, section_id: str) -> bool:
    """Whether `section_id`'s own declared ids are themselves numbered
    (see `_NUMERIC_ID_SUFFIX_RE`'s own comment for the measured reason
    `01`, `02` and `05` are excluded here even though all three use the
    `## Slot|Subsection|Block N` HEADING convention)."""
    return any(_NUMERIC_ID_SUFFIX_RE.search(qid) for qid in corpus.order_by_section[section_id])


def _verify_block_subunits(corpus: Corpus, section_bodies: dict) -> None:
    """tasks.md, 4.8b-4.8i: the PROSE -> HEADER direction no other check
    covers. Every other refusal this change ships checks TABLE -> GRAPH (a
    chain row naming a block); this is the sibling direction — a heading
    announcing a sub-unit, or claiming a single numbered unit, that the
    front matter does not back with exactly the declared id(s) it implies.

    Scoped BY CONSTRUCTION to sections whose own ids are themselves
    numbered (`_section_uses_numbered_ids`) — `01`, `02`, `05` (numbered
    HEADINGS, content-named ids) and `03`, `04`, `09`, `10` (content-named
    headings too) never enter either branch below; no second per-section
    flag, the gate is measured directly off the declared ids.

    Refuses `BLOCK_SUBUNIT_UNDECLARED` when a numbered heading (parent or
    child) resolves to ZERO declared ids under loose suffix matching (a
    number no id anywhere carries at all), and the new
    `UNIT_HEADING_AMBIGUOUS` when a PARENT heading resolves to MORE THAN
    ONE id — the exact residue `06`'s own block-4 split left behind before
    4.8g's fix, `## Block 4` matching both `block-4a` and `block-4b` under
    loose suffix matching with no children to disambiguate it — UNLESS its
    own heading text already names every one of them in backticks: an
    explicit grouping, not an accident.
    """
    for section_id, body in section_bodies.items():
        if not _section_uses_numbered_ids(corpus, section_id):
            continue
        text = body.decode("utf-8")
        current_parent = None
        for line in text.splitlines():
            parent_match = _UNIT_PARENT_RE.match(line)
            if parent_match:
                number = parent_match.group(1)
                matches = _numbered_block_ids(corpus, section_id, number)
                if not matches:
                    raise Refused(
                        "BLOCK_SUBUNIT_UNDECLARED",
                        f"{section_id}: heading {line.strip()!r} names no declared block id",
                    )
                if len(matches) > 1:
                    local_ids = [qid.split(".", 1)[1] for qid in matches]
                    if not all(f"`{local_id}`" in line for local_id in local_ids):
                        raise Refused(
                            "UNIT_HEADING_AMBIGUOUS",
                            f"{section_id}: heading {line.strip()!r} resolves to "
                            f"{sorted(matches)!r} — name every one in the heading "
                            f"itself to declare it an explicit grouping",
                        )
                current_parent = line
                continue
            if _ANY_TOP_HEADING_RE.match(line):
                current_parent = None
                continue
            child_match = _UNIT_CHILD_RE.match(line)
            if child_match and current_parent is not None:
                identifier = child_match.group(1)
                matches = _numbered_block_ids(corpus, section_id, identifier)
                if not matches:
                    raise Refused(
                        "BLOCK_SUBUNIT_UNDECLARED",
                        f"{section_id}: heading {line.strip()!r} (under "
                        f"{current_parent.strip()!r}) names no declared block id",
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


def _build_graph(corpus: Corpus, edge_set: EdgeSet) -> tuple:
    """`(successors, indegree)` — the adjacency shape both `derive_order`
    (one flattened total order) and `derive_waves` (the same graph's
    successive Kahn frontiers, thrown away by `derive_order`'s own min-heap
    today) sort over. `successors[qid]` lists ids that must be written
    after `qid`; `indegree[qid]` counts unmet `after` dependencies. Pure —
    no mutation of `corpus` or `edge_set`, no disk read."""
    successors: dict = {qid: [] for qid in corpus.blocks}
    indegree: dict = {qid: 0 for qid in corpus.blocks}
    for before, after, _source in edge_set.edges:
        successors[before].append(after)
        indegree[after] += 1
    return successors, indegree


def derive_order(corpus: Corpus, edge_set: EdgeSet) -> list:
    """Kahn's algorithm over the block graph, min-heap tie-broken by
    `_sort_key`. Refuses `ORDER_CYCLE` (work-state), naming the
    participating blocks, when Kahn terminates with nodes remaining — a
    minimal cycle extracted by DFS over the residual subgraph.
    """
    successors, indegree = _build_graph(corpus, edge_set)

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


def derive_waves(corpus: Corpus, edge_set: EdgeSet) -> list:
    """The same block graph `derive_order` flattens, reported instead as
    waves 1..N — every wave the full set of blocks whose in-degree in the
    residual graph reaches zero at that Kahn round, tie-broken WITHIN a
    wave the same way `derive_order` tie-breaks (`_sort_key`). Reuses
    `_build_graph` (design.md D2) — no second graph construction, no
    second sort key. Refuses `ORDER_CYCLE`, the identical detail string
    `derive_order` raises via the same `_extract_minimal_cycle`, when
    nodes remain unassigned once the frontier is exhausted.

    `derive_order`'s own min-heap holds ready nodes from SEVERAL frontiers
    at once (a node from wave 2 can out-rank, by `_sort_key`, a still-
    unpopped node from wave 1), so its flattened sequence legitimately
    interleaves waves. Flattening THIS function's waves is therefore never
    asserted equal to `derive_order`'s sequence — only that both name the
    same node set, and that every edge crosses a wave boundary
    (design.md D2, invariants 1/2/5; `specs/writing-phases/spec.md`).
    """
    successors, indegree = _build_graph(corpus, edge_set)

    remaining_indegree = dict(indegree)
    frontier = sorted(
        (qid for qid, degree in remaining_indegree.items() if degree == 0),
        key=lambda qid: _sort_key(corpus, qid),
    )

    waves: list = []
    written = 0
    while frontier:
        waves.append(frontier)
        written += len(frontier)
        next_frontier: list = []
        for qid in frontier:
            for successor in successors[qid]:
                remaining_indegree[successor] -= 1
                if remaining_indegree[successor] == 0:
                    next_frontier.append(successor)
        frontier = sorted(next_frontier, key=lambda qid: _sort_key(corpus, qid))

    if written != len(corpus.blocks):
        remaining = set(corpus.blocks) - {qid for wave in waves for qid in wave}
        cycle = _extract_minimal_cycle(remaining, successors)
        raise Refused("ORDER_CYCLE", f"a cycle among blocks: {' -> '.join(cycle)}")

    return waves
