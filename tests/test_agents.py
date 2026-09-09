"""Every agent is bound to a skill, and every delegating skill to its agents.

The binding is TWO-WAY and both directions are held here, because either one
alone leaves something dead. An agent that names no skill has no rules; a skill
that names no agent has agents nobody invokes -- and an agent nobody invokes is
a file, not a boundary. That second failure already happened once in this
repository and the file was deleted rather than kept.


An agent definition is the one place the purpose reaches a session BEFORE
anything happens: its `description` is the first thing in context on every
invocation. The skill declares the north and every refusal carries it, so it
arrives when you are blocked and when you ask -- and an agent is what makes it
arrive at the start, which is where losing it is cheapest to prevent.

That only holds while the two agree. A description that drifts from the
declared arrival is a north nobody updated, and the agent would open every
session with a destination the skill no longer has. So the arrival is read out
of the skill and asserted in the description rather than proof-read.

Stdlib only, for the same reason `test_suite_collects.py` is: this has to
survive an environment missing everything else.
"""

import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS = ROOT / ".claude" / "agents"
SKILLS = ROOT / ".claude" / "skills"

# Skills that declare no north at all -- neither a Python `OBJECTIVE_FLOW`
# nor a TypeScript `profile.ts` `objective`. Pinned by name, not discovered,
# so removing an entry (or a skill quietly growing a north) changes what the
# seal below expects to check, rather than changing what it silently skips.
NORTHLESS_SKILLS = {"skill-audit"}

# A single-line `arrival: "..."` or `stage: "..."` literal inside a
# TypeScript `objective` block. Anchored to the whole line so a token that
# merely CONTAINS the word `arrival` or `stage` elsewhere in the file (there
# is none today, but nothing guarantees that) cannot be mistaken for the
# declaration.
ARRIVAL_LINE = re.compile(r'^[ \t]*arrival:\s*"([^"]*)"\s*,?\s*$', re.MULTILINE)
STAGE_LINE = re.compile(r'^[ \t]*stage:\s*"([^"]*)"\s*,?\s*$', re.MULTILINE)


def frontmatter(path: Path) -> dict:
    """The agent's own header, parsed without a YAML dependency.

    Three keys, one line each, values optionally quoted. A parser is not what
    this file is for, and pulling in YAML would put it back inside the class of
    things `test_suite_collects.py` exists to detect.
    """
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}
    header = text.split("---\n", 2)[1]
    found = {}
    for line in header.splitlines():
        match = re.match(r'^(\w+):\s*"?(.*?)"?\s*$', line)
        if match:
            found[match.group(1)] = match.group(2)
    return found


def _python_objective(skill: str) -> dict | None:
    """This skill's own `OBJECTIVE_FLOW`, as `{"arrival": str, "stages": [str]}`,
    or None if no Python source under it declares one.

    Read out of the source with `ast` rather than by importing it: importing a
    skill's CLI pulls in whatever it depends on, and this file may not depend
    on anything.
    """
    for script in sorted((SKILLS / skill).rglob("*.py")):
        # `__pycache__` holds `.pyc` under a `.py`-shaped name on some layouts
        # and is never source anyway; a decode error there would fail this file
        # for a reason that has nothing to do with what it checks.
        if "__pycache__" in script.parts:
            continue
        try:
            source = script.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        try:
            tree = ast.parse(source)
        except SyntaxError:
            # A kit template carries `{{TOKEN}}` placeholders and is not valid
            # Python until it is materialized. It is scaffolding, never a place
            # a north is declared, so failing on it would fail this file for a
            # reason that has nothing to do with what it checks.
            continue
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            if "OBJECTIVE_FLOW" not in names:
                continue
            flow = ast.literal_eval(node.value)
            return {
                "arrival": flow.get("arrival"),
                "stages": [stage.get("stage") for stage in flow.get("stages", [])],
            }
    return None


def _typescript_objective(skill: str) -> dict | None:
    """This skill's own `<skill>/profile.ts` `objective`, as
    `{"arrival": str, "stages": [str]}`, or None if the skill has no
    `profile.ts` at all.

    Read by an anchored regex over the two single-line literals the shape
    guarantees (see `domain-profile.ts`'s `objective.arrival` comment: "the
    Python seal reads it") -- never by executing TypeScript, since this
    file's whole contract is stdlib-only and must survive an environment
    missing node.

    Fail closed: a `profile.ts` that EXISTS but whose `arrival` or `stages`
    literal does not parse raises rather than returning None, so a change
    that breaks this regex's assumption fails loudly instead of reading as
    "no north declared".
    """
    profile = SKILLS / skill / "profile.ts"
    if not profile.is_file():
        return None
    source = profile.read_text(encoding="utf-8")
    arrival_match = ARRIVAL_LINE.search(source)
    stage_matches = STAGE_LINE.findall(source)
    if arrival_match is None or not stage_matches:
        raise AssertionError(
            f"{skill}/profile.ts exists but its `objective.arrival` and/or "
            f"`objective.stages[].stage` single-line literals could not be "
            f"parsed by the anchored regex -- fix the profile or this "
            f"regex, never read the failure as \"no north declared\"")
    return {"arrival": arrival_match.group(1), "stages": stage_matches}


def declared_objective(skill: str) -> dict | None:
    """This skill's own declared `{"arrival": str, "stages": [str]}`, tried
    in Python first and then TypeScript, or None if neither source declares
    one at all.

    Both present in the same skill is a mistake this raises on rather than
    silently picking a source: one skill, one north.
    """
    python_objective = _python_objective(skill)
    typescript_objective = _typescript_objective(skill)
    if python_objective is not None and typescript_objective is not None:
        raise AssertionError(
            f"{skill} declares OBJECTIVE_FLOW in Python AND an objective in "
            f"profile.ts -- one skill, one north; pick a source of truth")
    return python_objective if python_objective is not None else typescript_objective


def bound_skill(path: Path) -> str:
    """The single skill this agent's body binds to, read by its `Skill:`
    path -- never by the agent's filename, which is the STRETCH's name and
    need not match any skill directory at all (`implementation-walk` is not
    a skill and never will be).

    `test_every_agent_names_a_skill_that_exists` already asserts this
    binding is present and real; this reuses the same regex rather than a
    weaker filename guess.
    """
    body = path.read_text(encoding="utf-8")
    named = re.findall(r"\.claude/skills/([\w-]+)/SKILL\.md", body)
    assert named, f"{path.name} names no skill to load"
    return named[0]


class AgentBindingTests(unittest.TestCase):

    def agents(self):
        return sorted(AGENTS.glob("*.md")) if AGENTS.is_dir() else []

    def test_there_is_at_least_one_agent(self) -> None:
        self.assertTrue(self.agents(), "no agent definitions to hold")

    def test_every_agent_names_its_own_file(self) -> None:
        for path in self.agents():
            self.assertEqual(frontmatter(path).get("name"), path.stem, path.name)

    def test_every_agent_names_a_skill_that_exists(self) -> None:
        """By its PATH in the body, never by its filename.

        An agent is a STRETCH between two of the operator's gates, so its name
        is the stretch's and not the skill's -- `implementation-walk` is not a
        skill and never will be. Reading the binding out of the body is what
        lets one skill have several agents without any of them being named
        after it.
        """
        for path in self.agents():
            body = path.read_text(encoding="utf-8")
            named = re.findall(r"\.claude/skills/([\w-]+)/SKILL\.md", body)
            self.assertTrue(named, f"{path.name} names no skill to load")
            for skill in named:
                self.assertTrue((SKILLS / skill / "SKILL.md").is_file(),
                                f"{path.name} names {skill}, which does not exist")

    def test_every_agent_a_skill_delegates_to_exists(self) -> None:
        """The other direction. A skill that names an agent it delegates a
        stretch to is what makes that agent reachable at all; without this, a
        renamed or deleted agent leaves a skill pointing at nothing and the
        stretch silently stops being delegated."""
        named = set()
        for skill in sorted(SKILLS.iterdir()):
            doc = skill / "SKILL.md"
            if not doc.is_file():
                continue
            for agent in re.findall(r"delegates to the `([\w-]+)` agent", 
                                    doc.read_text(encoding="utf-8")):
                named.add((skill.name, agent))
        self.assertTrue(named, "no skill delegates a stretch to any agent")
        for skill, agent in sorted(named):
            self.assertTrue((AGENTS / f"{agent}.md").is_file(),
                            f"{skill} delegates to `{agent}`, which does not exist")

    def test_every_agent_is_invoked_by_a_skill(self) -> None:
        """The half the first version of this file did not check, and two
        agents were written without it: it asked only that SOME skill delegate,
        which a single delegation satisfies while every other agent sits
        unreachable. An agent nobody invokes is a file, not a boundary -- the
        exact defect that had one deleted earlier the same day.
        """
        invoked = set()
        for skill in sorted(SKILLS.iterdir()):
            doc = skill / "SKILL.md"
            if doc.is_file():
                invoked.update(re.findall(r"delegates to the `([\w-]+)` agent",
                                          doc.read_text(encoding="utf-8")))
        orphans = sorted(path.stem for path in self.agents()
                         if path.stem not in invoked)
        self.assertEqual(orphans, [],
                         "these agents exist and no skill delegates to them, "
                         "so nothing reaches them")

    def test_every_agent_states_its_tools(self) -> None:
        """An agent that declares none inherits everything, which is the
        capability restriction silently not applied."""
        for path in self.agents():
            self.assertTrue(frontmatter(path).get("tools"), path.name)

    def test_every_agent_names_both_ends_of_its_stretch(self) -> None:
        """An agent whose stretch has no ends is not a stretch, it is a job
        with a title. Two of these were written before the criterion existed
        and had neither."""
        for path in self.agents():
            body = path.read_text(encoding="utf-8")
            # Whitespace-tolerant on purpose: these files are hard-wrapped,
            # so "You\nend" is the same sentence as "You end" and a regex that
            # could not cross a line break failed one of them for its wrapping.
            flat = " ".join(body.split())
            self.assertIn("You begin", flat,
                          f"{path.name} never says where its stretch begins")
            self.assertRegex(flat, r"[Yy]ou end",
                             f"{path.name} never says where its stretch ends")

    def test_every_agent_declares_what_it_returns(self) -> None:
        """A subagent's report is not shown to the operator: it reaches the
        orchestrator, which relays what matters. So it is read twice and
        translated once, and anything the agent leaves out is gone. Without a
        declared shape the orchestrator receives whatever occurred to it."""
        for path in self.agents():
            body = path.read_text(encoding="utf-8")
            self.assertIn("## What you return", body, path.name)
            for field in ("`did`", "`stoppedAt`", "`state`", "`owed`"):
                self.assertIn(field, body,
                              f"{path.name} omits {field} from what it returns")

    def test_what_is_returned_is_measurable_and_not_a_conclusion(self) -> None:
        """The property that makes a report checkable rather than believable.
        "I verified it is correct" cannot be checked by anybody; "I ran X, it
        answered Y, I stopped at Z" can -- and the orchestrator's job is to
        verify against the repository rather than believe."""
        for path in self.agents():
            body = path.read_text(encoding="utf-8")
            self.assertIn("never conclusions", body, path.name)
            self.assertIn("measured again", body, path.name)

    def test_every_delegated_stretch_names_what_to_measure_first(self) -> None:
        """A precondition read before delegating, not discovered inside.

        Each agent also refuses from within when it finds itself before its own
        start, and that is the backstop rather than the rule: discovering it
        there costs a whole round trip to learn something that was measurable
        before leaving.
        """
        delegating = [skill for skill in sorted(SKILLS.iterdir())
                      if (skill / "SKILL.md").is_file()
                      and "delegates to the `" in (skill / "SKILL.md").read_text(
                          encoding="utf-8")]
        self.assertTrue(delegating)
        for skill in delegating:
            doc = (skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("Measure this before delegating", doc,
                          f"{skill.name} delegates a stretch and names no "
                          f"precondition to read first")

    def test_a_description_carries_the_arrival_its_skill_declares(self) -> None:
        """The seal.

        Bound by the body `Skill:` path, never the filename -- the earlier
        version checked `declared_arrival(path.stem)`, which only matches a
        skill directory that happens to share the agent's own name, and
        `paper-ingestion` was the sole agent where that held. Coverage was
        1 of 5 and `assertGreater(checked, 0)` passed on that one survivor.

        The property itself is FALSE for an agent whose stretch stops
        short: `implementation-build` ends at "the findings report", not at
        `proposal-implementation`'s arrival, and forcing it to carry that
        arrival would make a correct description lie. So every agent bound
        to a north-declaring skill must name its own end in frontmatter --
        `stretch: terminal` (its description carries the skill's `arrival`
        verbatim) or `stretch: <stage>` (a stage that skill actually
        declares) -- and coverage is an EQUALITY against the derived set of
        agents bound to a north-declaring skill, not `assertGreater(..., 0)`.
        """
        expected = {path.stem for path in self.agents()
                    if bound_skill(path) not in NORTHLESS_SKILLS}
        if not expected:
            self.skipTest("no agent is bound to a skill that declares a "
                           "north; nothing for this seal to check")

        checked = set()
        for path in self.agents():
            skill = bound_skill(path)
            if skill in NORTHLESS_SKILLS:
                self.assertIsNone(declared_objective(skill),
                                  f"{skill} is listed in NORTHLESS_SKILLS "
                                  f"but declares an objective -- remove it "
                                  f"from the map")
                continue

            objective = declared_objective(skill)
            self.assertIsNotNone(
                objective,
                f"{path.name} is bound to {skill}, which is not in "
                f"NORTHLESS_SKILLS, but declares no OBJECTIVE_FLOW and no "
                f"profile.ts objective")
            checked.add(path.stem)

            stretch = frontmatter(path).get("stretch")
            self.assertTrue(stretch,
                            f"{path.name} is bound to {skill}, which "
                            f"declares a north, but names no `stretch:`")
            description = frontmatter(path).get("description", "")
            if stretch == "terminal":
                self.assertIn(objective["arrival"], description,
                              f"{path.name}'s description does not carry "
                              f"the arrival its own skill declares")
            else:
                self.assertIn(stretch, objective["stages"],
                              f"{path.name} declares `stretch: {stretch}`, "
                              f"which is not one of {skill}'s declared "
                              f"stages {objective['stages']}")

        self.assertEqual(checked, expected,
                         "the seal's coverage drifted from every agent "
                         "bound to a north-declaring skill")

    def test_every_agent_carries_the_shared_role_discipline(self) -> None:
        """The role discipline is COPIED into every agent, never extracted --
        a decision already taken, because a shared fragment could only be
        asserted by REFERENCE, and whether an agent actually loaded it is
        unmeasurable. This asserts the whole named tuple lives in each
        agent's own bytes.

        Most of the tuple overlaps tests already above
        (`test_every_agent_declares_what_it_returns`,
        `test_what_is_returned_is_measurable_and_not_a_conclusion`) and is
        re-asserted here as one named set, not claimed as new. Three items
        are new: the `## Measure before you assert` heading, the corrected
        sentence about which agents carry an arrival at all (the false
        universal claim the seal above used to make silently, by checking
        only one agent), and the coverage equality below.
        """
        fragments = (
            "## What you return",
            "`did`",
            "`stoppedAt`",
            "`state`",
            "`owed`",
            "never conclusions",
            "measured again",
            "## Measure before you assert",
            "Not every agent's description carries its bound skill's arrival",
        )
        agents = self.agents()
        checked = 0
        for path in agents:
            body = path.read_text(encoding="utf-8")
            for fragment in fragments:
                self.assertIn(fragment, body,
                              f"{path.name} is missing the shared role "
                              f"discipline fragment {fragment!r}")
            checked += 1
        self.assertEqual(checked, len(agents),
                         "not every agent file was checked for the shared "
                         "role discipline")
