"""paper_objective: this skill's declared north.

Module-level `OBJECTIVE_FLOW`, read by `tests/test_agents.py` via
`ast.literal_eval` — pure literals only, no function calls, no imports of
anything this dict's own values depend on (design.md's own constraint,
`insumos-observer cannot decide, by schema and by capability`: "the seal
that forces extra scope").

Wording is this change's own to make (design.md's Open Question: "the
seal requires them to exist, not what they say"). `paper-writing`'s own
verbs stop at `declare`; `cite`, `write`, `render` and `verify` are named,
honest future stages — SKILL.md's own "Not shipped yet, on purpose"
section already says so for `write`, and this dict does not pretend
otherwise.
"""
from __future__ import annotations

OBJECTIVE_FLOW = {
    "purpose": (
        "carry paper/ from an empty scaffold to a rendered document whose "
        "every block, decision and citation is recorded and checkable, "
        "never assumed"
    ),
    "stages": [
        {
            "stage": "scaffold",
            "establishes": (
                "paper/main.tex, refs.bib, Figures/ and .gitkeep exist, "
                "idempotently, no hand edit ever overwritten"
            ),
            "behindWhen": (
                "`scaffold` has not been run yet, or any block/region verb "
                "still refuses PAPER_ABSENT"
            ),
        },
        {
            "stage": "plan",
            "establishes": (
                "every guidance/ folder's class, every declaration/fact's "
                "fill state, and every written block's provenance state "
                "are visible in one read-only report"
            ),
            "behindWhen": (
                "`plan` has not been run since the last `declare`, "
                "`--reopen` or `substitute --contract`"
            ),
        },
        {
            "stage": "declare",
            "establishes": (
                "every block's requires_facts and requires_declarations "
                "names a fixed record, so `readiness` reports it writable"
            ),
            "behindWhen": (
                "`plan` reports any block `blocked`, naming its still-"
                "missing facts or declarations"
            ),
        },
        {
            "stage": "cite",
            "establishes": (
                "every block whose citations regime is discovery or "
                "resolution carries the citations that regime demands"
            ),
            "behindWhen": (
                "no verb in this skill produces or checks a citation yet "
                "-- a later capability, not built"
            ),
        },
        {
            "stage": "write",
            "establishes": (
                "every writable block, in the order `order` derives, "
                "carries a substituted body"
            ),
            "behindWhen": (
                "`order`'s output is not yet fed into `open`/`substitute` "
                "automatically (SKILL.md, \"Not shipped yet, on purpose\")"
            ),
        },
        {
            "stage": "render",
            "establishes": (
                "the document compiles and its rendering is proven, not "
                "merely reported \"unproven\""
            ),
            "behindWhen": (
                "this skill has no LaTeX toolchain; every successful "
                "`substitute` still reports \"rendering\": \"unproven\""
            ),
        },
        {
            "stage": "verify",
            "establishes": (
                "the rendered document is checked against every declared "
                "requirement one last time before it leaves this "
                "repository"
            ),
            "behindWhen": "no verb performs this check yet",
        },
    ],
    "arrival": (
        "a rendered, decision-complete document: every block substituted, "
        "every declaration and fact fixed, every required citation "
        "resolved, and nothing asserted that a run did not check"
    ),
    "humanStops": [
        "declaring an operator-supplied value (declare --declaration <id>) "
        "is always a human decision, never inferred from evidence",
        "deciding when a drifted or unprovenanced block is acceptable to "
        "submit anyway",
    ],
}
