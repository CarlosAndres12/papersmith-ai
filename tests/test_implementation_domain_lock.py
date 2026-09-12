"""Cut 2 (`the-domain-crosses-the-seam`): the two neutrality locks Cut 1
deferred -- "because with no domain words yet moved it would pass
vacuously" -- plus the kit agreement lock (design.md D4) and the
campaign-proposal exclusion (design.md D6). Python mirror of
`tests/proposal-deliberation-domain-profile-lock.test.mjs`, structurally,
never a shared import: these two files exercise the SAME kind of surface
for different runtimes, and a shared helper module would be one more file
this lock itself would then have to scan and clear.
"""

from __future__ import annotations

import importlib.util
import os
import re
import sys
import unittest
from pathlib import Path
from typing import Any, Mapping

FORGE = Path(__file__).resolve().parents[1]
SKILLS_DIR = FORGE / ".claude" / "skills"
ENGINE_DIR = SKILLS_DIR / "_core" / "implementation" / "engine"
ENGINE_FILE = ENGINE_DIR / "implementation_engine.py"


def _import_engine_module():
    """A fresh, uncached load of the engine itself -- for the ONE test
    (L3) that needs a live attribute off it rather than its source text.
    Sets `IMPLEMENTATION_DOMAIN_PROFILE` to this skill's own profile first
    (mirroring `tests/seal/harness.py`'s `os.environ.setdefault`), since the
    engine fails closed at import without one."""
    os.environ.setdefault(
        "IMPLEMENTATION_DOMAIN_PROFILE",
        str(SKILLS_DIR / "proposal-implementation" / "impl_profile.py"))
    if str(ENGINE_DIR) not in sys.path:
        sys.path.insert(0, str(ENGINE_DIR))
    spec = importlib.util.spec_from_file_location(
        "impl_domain_lock_engine_probe", ENGINE_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_profile_module(path: Path):
    spec = importlib.util.spec_from_file_location(
        f"impl_domain_lock_probe_{path.parent.name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def profile_values_text(profile: Mapping[str, Any]) -> str:
    """Every leaf VALUE `profile` declares, rendered as text, with
    `vocabulary.names` itself excluded (design.md D6, the M1 finding).

    This is the haystack `test_every_declared_name_really_is_that_domain_
    speaking` searches -- never the profile FILE's own source text, which
    trivially contains every literal in its own `names` list no matter what
    it says (M1: the check was vacuous for every profile, not only for a
    namespace word, because `names`'s own declaration is itself part of the
    file it searched). A declared name found here had to equal some OTHER
    leaf's real, engine-read value -- `vocabulary.subject_singular_es`,
    `kit.root`'s own path text, and so on -- which is the property the old
    check only appeared to have.
    """
    parts: list[str] = []

    def walk(value: Any, path: tuple[str, ...]) -> None:
        if path == ("vocabulary", "names"):
            return
        if isinstance(value, Mapping):
            for key, val in value.items():
                walk(val, path + (key,))
        elif isinstance(value, (list, tuple)):
            for item in value:
                walk(item, path)
        else:
            parts.append(str(value))

    walk(profile, ())
    return " ".join(parts)


def discover_profiles() -> list[dict[str, Any]]:
    """Globs `.claude/skills/*/impl_profile.py`, skipping `_core` -- never
    one hardcoded path (design.md D5, mirroring `discoverProfiles` in the
    TS lock). A third skill's `impl_profile.py` is held to the rule the day
    it appears, without this file being edited."""
    profiles = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        if not entry.is_dir() or entry.name == "_core":
            continue
        profile_path = entry / "impl_profile.py"
        if not profile_path.is_file():
            continue
        source = profile_path.read_text(encoding="utf-8")
        module = _load_profile_module(profile_path)
        profile: Mapping[str, Any] = module.PROFILE
        names = list(profile.get("vocabulary", {}).get("names", []))
        profiles.append({
            "skill_name": entry.name, "source": source, "profile": profile,
            "names": names, "values_text": profile_values_text(profile),
        })
    return profiles


def _engine_files() -> list[Path]:
    return sorted(ENGINE_DIR.rglob("*.py"))


def _read_all(paths: list[Path]) -> list[tuple[str, str]]:
    return [(str(path.relative_to(ENGINE_DIR)), path.read_text(encoding="utf-8"))
            for path in paths]


class LockADiscoveryTests(unittest.TestCase):
    """Lock A (design.md D5): profile discovery, by glob. Vacuity guards
    first -- a check that never found a profile would pass every assertion
    below it vacuously."""

    def test_at_least_one_profile_is_discovered(self):
        profiles = discover_profiles()
        self.assertGreaterEqual(
            len(profiles), 1,
            f"expected at least 1 profile under {SKILLS_DIR}/*/impl_profile.py, "
            f"found {len(profiles)}")

    def test_every_profile_declares_a_nonempty_names_list(self):
        for entry in discover_profiles():
            with self.subTest(skill=entry["skill_name"]):
                self.assertGreater(
                    len(entry["names"]), 0,
                    f"{entry['skill_name']} declares no vocabulary.names word, "
                    "so the check below would pass vacuously")

    def test_no_declared_leaf_is_blank(self):
        for entry in discover_profiles():
            with self.subTest(skill=entry["skill_name"]):
                for name in entry["names"]:
                    self.assertNotEqual(name.strip(), "")

    def test_every_declared_name_really_is_that_domain_speaking(self):
        """'a name no profile value contains is not this domain naming
        itself' -- the TS lock's own words, mirrored exactly.

        Rewritten (design.md D6, the M1 finding): the haystack is
        `profile_values_text` -- every leaf VALUE the profile declares,
        `vocabulary.names` itself excluded -- never `entry["source"]`, the
        profile FILE's own text. `entry["source"]` always contains every
        name literally, because the `names` list's own declaration lives in
        that same file; searching it made this check pass for ANY profile,
        which is exactly what `LockAHonestyTests`
        (`tests/test_implementation_domain_mutation.py`) proves by planting
        a name that only the OLD check would have let through.
        """
        for entry in discover_profiles():
            with self.subTest(skill=entry["skill_name"]):
                haystack = entry["values_text"].lower()
                unused = [n for n in entry["names"] if n.lower() not in haystack]
                self.assertEqual(
                    unused, [],
                    f"{entry['skill_name']}: a name no OTHER profile value "
                    "contains is not this domain naming itself")


class LockBEngineNeutralityTests(unittest.TestCase):
    """Lock B (design.md D5): the engine spells no declared domain word --
    scanned as WHOLE TEXT (code, strings, comments, docstrings), which is
    why the comment/docstring sweep (S12) is load-bearing and not
    cosmetic. Word-boundary, case-insensitive."""

    def test_the_whole_engine_directory_is_scanned(self):
        files = _engine_files()
        self.assertGreater(
            len(files), 0, f"expected at least one *.py file under {ENGINE_DIR}")

    def test_the_engine_spells_no_declared_names_word(self):
        profiles = discover_profiles()
        names: set[str] = set()
        for entry in profiles:
            names.update(entry["names"])
        self.assertGreater(len(names), 0, "no names word discovered -- vacuous")
        leaks = []
        for rel, source in _read_all(_engine_files()):
            for name in names:
                if re.search(rf"\b{re.escape(name)}\b", source, re.IGNORECASE):
                    leaks.append(f"{rel} spells {name!r}")
        self.assertEqual(
            leaks, [],
            "the engine must read these off the host-chosen profile, never spell "
            "them: " + "; ".join(leaks))


# --- M5: the derived denylist (TS C-3), now landable ------------------------
#
# Deferred at Cut 2 (`the-domain-crosses-the-seam`): with one implementation
# profile on disk the "others" set is empty and every word >=5 letters in
# `OBJECTIVE_FLOW` becomes a denylist entry -- not a stricter lock, an
# unsatisfiable one. A second profile now exists (this change), so the
# "others" set is non-empty and this lands as a real test, never a
# `skipTest` (a skip would move the pinned `skipped=6`, tasks.md 4.5/13.8).

#: Every ``[A-Za-z]{5,}`` word, case-folded -- the Python mirror of
#: `objectiveWords` in `tests/proposal-deliberation-domain-profile-lock.test.mjs`.
_NORTH_WORD_RE = re.compile(r"[A-Za-z]{5,}")


def north_words(profile: Mapping[str, Any]) -> set[str]:
    """Every word `objectiveWords` (the TS lock) would extract: `purpose`,
    every stage's `establishes`/`behindWhen`, `arrival`, `humanStops` --
    read directly off `profile["objective"]` (the module is already
    imported by `discover_profiles()`; no `extractBlock` regex is needed,
    unlike the TS side, which reads unparsed source text)."""
    objective = profile["objective"]
    texts = [objective.get("purpose", ""), objective.get("arrival", "")]
    texts.extend(objective.get("humanStops", []))
    for stage in objective.get("stages", []):
        texts.append(stage.get("establishes", ""))
        texts.append(stage.get("behindWhen", ""))
    words: set[str] = set()
    for text in texts:
        words.update(match.lower() for match in _NORTH_WORD_RE.findall(text))
    return words


def build_denylist(profiles: list[dict[str, Any]]) -> dict[str, str]:
    """A word appearing in EXACTLY ONE profile's north is that domain's own
    subject matter and may not appear, word-boundary, in the engine. A word
    both norths use is engine vocabulary, never flagged -- the Python
    mirror of `buildDenylist` (TS C-3), never a hand-written list."""
    word_sets = {entry["skill_name"]: north_words(entry["profile"])
                for entry in profiles}
    denylist: dict[str, str] = {}
    for skill_name, words in word_sets.items():
        others: set[str] = set()
        for other_name, other_words in word_sets.items():
            if other_name == skill_name:
                continue
            others.update(other_words)
        for word in words:
            if word not in others:
                denylist[word] = skill_name
    return denylist


#: Measured at apply (task 4.6), never predicted -- real occurrence counts
#: (case-insensitive, word-boundary) of every denylist word that the engine
#: ALREADY spells as pre-existing, load-bearing vocabulary, unrelated to
#: either domain's `vocabulary.names` (which Lock B already holds to zero).
#: Two profiles on disk today: `experimental-implementation` (this change)
#: and `proposal-implementation`. Five denylist words measured genuinely
#: ABSENT from the engine and need no pin at all: `formulation`,
#: `mathematical`, `mathematics`, `statistical`, `traced` -- the first three
#: are also members of `proposal-implementation`'s own `vocabulary.names`,
#: so their zero count is cross-confirmed by Lock B independently. Each
#: entry below may only SHRINK deliberately, never grow silently (test 3);
#: a pin whose word left the denylist is a dead exemption (also test 3); a
#: pin at zero is a defect (test 4).
M5_PINNED_RESIDUE: dict[str, int] = {
    "actually": 75, "admissible": 3, "after": 78, "against": 181,
    "agreed": 23, "answered": 71, "answers": 98, "approved": 25,
    "audit": 15, "before": 223, "benchmark": 91, "beside": 91,
    "carries": 176, "check": 145, "checkable": 3, "claim": 34,
    "command": 263, "commands": 15, "compares": 23, "declaration": 189,
    "destinations": 37, "empty": 111, "established": 4, "experiment": 24,
    "experiments": 6, "implementations": 2, "incomplete": 28,
    "invariant": 22, "isolated": 4, "leave": 9, "leaves": 34, "local": 31,
    "longer": 46, "makes": 43, "materialize": 29, "materialized": 10,
    "measured": 140, "measurement": 43, "module": 171, "named": 164,
    "notebooks": 107, "object": 27, "objects": 19, "pilot": 119,
    "place": 50, "premises": 7, "produces": 44, "rather": 330,
    "readable": 23, "recorded": 75, "refuses": 86, "remedy": 48,
    "remote": 55, "reported": 142, "resolves": 32, "ruled": 8,
    "runnable": 15, "scaffolded": 4, "sitting": 9, "small": 4,
    "something": 67, "stage": 82, "steps": 133, "sweep": 7,
    "validated": 7, "value": 219, "whose": 141, "write": 104, "wrong": 51,
}


class DerivedDenylistTests(unittest.TestCase):
    """M5 (design.md D9), four separate test methods, never one method with
    four asserts (`b3ca9aa`'s lesson: a method halts at its first failing
    assertion)."""

    def test_1_vacuity_at_least_two_profiles_and_a_nonempty_denylist(self):
        profiles = discover_profiles()
        self.assertGreaterEqual(
            len(profiles), 2,
            "expected at least 2 profiles on disk; the denylist needs a "
            "second north to compare against or it is unsatisfiable rather "
            "than strict")
        denylist = build_denylist(profiles)
        self.assertGreater(
            len(denylist), 0,
            "no single-owner north word was derived -- if two profiles' "
            "norths were accidentally IDENTICAL text, every word would be "
            "shared and the denylist would be empty (the same self-check "
            "the TS lock records)")

    def test_2_no_unpinned_denylist_word_appears_in_the_engine(self):
        denylist = build_denylist(discover_profiles())
        leaks = []
        for rel, source in _read_all(_engine_files()):
            for word, owner in denylist.items():
                if word in M5_PINNED_RESIDUE:
                    continue
                if re.search(rf"\b{re.escape(word)}\b", source, re.IGNORECASE):
                    leaks.append(f"{rel} spells {word!r} ({owner}'s own north)")
        self.assertEqual(
            leaks, [],
            "a core engine file spells a word belonging to only one "
            "domain's own north, and it carries no pin: " + "; ".join(leaks))

    def test_3_every_pinned_words_count_equals_its_pin_and_stays_in_the_denylist(self):
        denylist = build_denylist(discover_profiles())
        for word, expected_count in M5_PINNED_RESIDUE.items():
            with self.subTest(word=word):
                self.assertIn(
                    word, denylist,
                    f"{word!r} is pinned but no longer in the derived "
                    "denylist -- a pin for a word that left the denylist "
                    "is a dead exemption")
                count = sum(
                    len(re.findall(rf"\b{re.escape(word)}\b", source, re.IGNORECASE))
                    for _, source in _read_all(_engine_files()))
                self.assertEqual(
                    count, expected_count,
                    f"{word!r}'s occurrence count drifted from its pin "
                    f"({expected_count}) to {count} -- a pin may only shrink "
                    "deliberately, never move silently")

    def test_4_no_pinned_word_has_a_zero_count(self):
        for word, expected_count in M5_PINNED_RESIDUE.items():
            with self.subTest(word=word):
                self.assertGreater(
                    expected_count, 0,
                    f"{word!r} is pinned at zero -- a pin exists to record "
                    "genuine pre-existing residue, and a zero-count pin is "
                    "a dead exemption for a word the engine does not spell")


def _kit_root_for(profile: Mapping[str, Any]) -> Path:
    return Path(profile["kit"]["root"])


def kit_shipping_profiles() -> list[tuple[str, Mapping[str, Any]]]:
    """Task 4.3 (design.md D9): every discovered profile whose own
    `kit.root` actually ships `assets/kit/src/module.py` -- derived, never
    the single hardcoded `proposal-implementation` path this class used to
    carry. A third skill's kit is held to this lock the day it appears,
    without this file being edited (mutation X9: pointing this filter at
    zero kit-shipping profiles must redden the vacuity guard below)."""
    shipping = []
    for entry in discover_profiles():
        kit_root = _kit_root_for(entry["profile"])
        if (kit_root / "assets" / "kit" / "src" / "module.py").is_file():
            shipping.append((entry["skill_name"], entry["profile"]))
    return shipping


class KitAgreementLockTests(unittest.TestCase):
    """D4/D9 (design.md): the kit template's provenance keys agree with the
    profile -- six sites, two of them EXECUTABLE code that runs inside a
    target's own interpreter, which is the sharpest reason this needs a
    test: a divergence there fails in somebody else's repository, not in
    this suite. No kit file is ever edited by this lock or by this cut.

    `_profile()` no longer hardcodes `proposal-implementation`'s path
    (task 4.3): every test method below iterates `kit_shipping_profiles()`,
    `subTest(skill=...)` per profile, against non-empty and coverage-
    equality assertions. This skill (`experimental-implementation`) ships
    no kit (task 4.4, M3) and is correctly ABSENT from that derived set --
    confirmed directly by `test_this_skill_is_recorded_kitless` below,
    never merely assumed."""

    def test_at_least_one_kit_shipping_profile_is_discovered(self):
        """Vacuity guard, first -- every assertion below would pass on an
        empty set otherwise (mutation X9 reddens exactly this)."""
        shipping = kit_shipping_profiles()
        self.assertGreaterEqual(
            len(shipping), 1,
            "expected at least one kit-shipping profile; found none -- "
            "every assertion below would pass vacuously")

    def test_this_skill_is_recorded_kitless(self):
        """Task 4.4: this skill ships no `assets/kit/` at all (M3) and is
        therefore correctly absent from `kit_shipping_profiles()`."""
        shipping_names = {name for name, _ in kit_shipping_profiles()}
        self.assertNotIn("experimental-implementation", shipping_names)
        this_skill_root = SKILLS_DIR / "experimental-implementation"
        self.assertFalse(
            (this_skill_root / "assets" / "kit" / "src" / "module.py").is_file(),
            "experimental-implementation ships assets/kit/src/module.py -- "
            "it is no longer kitless and kit_shipping_profiles() must find it")

    def test_module_py_declares_the_agreed_provenance_keys(self):
        checked = set()
        for skill_name, profile in kit_shipping_profiles():
            with self.subTest(skill=skill_name):
                kit_dir = _kit_root_for(profile) / "assets" / "kit"
                source = (kit_dir / "src" / "module.py").read_text(encoding="utf-8")
                match = re.search(r"__provenance__\s*=\s*\{(.*?)\n\}", source, re.DOTALL)
                self.assertIsNotNone(match, "module.py declares no __provenance__ literal")
                keys = set(re.findall(r'"(\w+)":', match.group(1)))
                self.assertGreater(len(keys), 0, "extraction found no keys -- vacuous")
                claim_key = profile["provenance"]["claim_key"]
                self.assertEqual(keys, {"revision", "sections", claim_key, "invariants"})
                checked.add(skill_name)
        self.assertEqual(checked, {name for name, _ in kit_shipping_profiles()})

    def test_module_py_rules_docstring_names_both_keys(self):
        checked = set()
        for skill_name, profile in kit_shipping_profiles():
            with self.subTest(skill=skill_name):
                kit_dir = _kit_root_for(profile) / "assets" / "kit"
                source = (kit_dir / "src" / "module.py").read_text(encoding="utf-8")
                claim_key = profile["provenance"]["claim_key"]
                self.assertIn(f'`{claim_key}`', source)
                self.assertIn("`sections`", source)
                checked.add(skill_name)
        self.assertEqual(checked, {name for name, _ in kit_shipping_profiles()})

    def test_src_benchmark_arms_example_spells_sections(self):
        checked = set()
        for skill_name, profile in kit_shipping_profiles():
            with self.subTest(skill=skill_name):
                kit_dir = _kit_root_for(profile) / "assets" / "kit"
                source = (kit_dir / "src_benchmark" / "__init__.py").read_text(
                    encoding="utf-8")
                example = re.search(r'#\s*"arms":\s*\{.*?\n(?:\s*#.*\n)*', source)
                self.assertIsNotNone(example, "no commented arms example found -- vacuous")
                self.assertIn("sections", example.group(0))
                checked.add(skill_name)
        self.assertEqual(checked, {name for name, _ in kit_shipping_profiles()})

    def test_findings_py_commented_keys_equal_locus_and_remedy_locus(self):
        checked = set()
        for skill_name, profile in kit_shipping_profiles():
            with self.subTest(skill=skill_name):
                kit_dir = _kit_root_for(profile) / "assets" / "kit"
                source = (kit_dir / "tests" / "findings.py").read_text(encoding="utf-8")
                locus_key = profile["findings"]["locus_key"]
                remedy_locus_key = profile["findings"]["remedy_locus_key"]
                self.assertIn(f'#     "{locus_key}"', source)
                self.assertIn(f'#     "{remedy_locus_key}"', source)
                checked.add(skill_name)
        self.assertEqual(checked, {name for name, _ in kit_shipping_profiles()})

    def test_test_audit_py_executable_subscript_equals_remedy_locus_key(self):
        checked = set()
        for skill_name, profile in kit_shipping_profiles():
            with self.subTest(skill=skill_name):
                kit_dir = _kit_root_for(profile) / "assets" / "kit"
                source = (kit_dir / "tests" / "test_audit.py").read_text(encoding="utf-8")
                remedy_locus_key = profile["findings"]["remedy_locus_key"]
                pattern = rf'finding\["{re.escape(remedy_locus_key)}"\]'
                self.assertRegex(source, pattern)
                checked.add(skill_name)
        self.assertEqual(checked, {name for name, _ in kit_shipping_profiles()})

    def test_verification_notebook_executable_subscript_equals_claim_key(self):
        checked = set()
        for skill_name, profile in kit_shipping_profiles():
            with self.subTest(skill=skill_name):
                kit_dir = _kit_root_for(profile) / "assets" / "kit"
                source = (kit_dir / "nb" / "verification.ipynb").read_text(
                    encoding="utf-8")
                claim_key = profile["provenance"]["claim_key"]
                pattern = rf"p\['{re.escape(claim_key)}'\]"
                self.assertRegex(source, pattern)
                checked.add(skill_name)
        self.assertEqual(checked, {name for name, _ in kit_shipping_profiles()})


# --- D6: the campaign-proposal exclusion, three layers ---------------------
#
# L1's baseline is MEASURED at apply (task 0.4), never written into the
# design. Phase 0.4 measured 97 occurrences of `\bproposal\b`
# (case-insensitive) across `_core/implementation/engine/`, one file
# (`implementation_engine.py`). S9's `documents.label` conversion of
# `ARMS_UNDECLARED_CONSEQUENCE`'s "of a proposal" phrase into a profile read
# (`"of a {document}"`, formatted with `DOCUMENTS_LABEL`) is the ONE
# deliberate, recorded shrink this cut takes: the literal word "proposal"
# no longer appears in that constant's SOURCE TEXT (it is composed at
# runtime instead), dropping the count by exactly 1, to 96. Re-measured
# after landing every S3-S13 field: still 96, still 1 file. Any OTHER
# movement -- a rename campaign, an accidental sweep -- is refused here.
L1_BASELINE_AT_S0 = 97
L1_DELIBERATE_SHRINK = 1  # documents.label's ARMS_UNDECLARED_CONSEQUENCE conversion
L1_EXPECTED_COUNT = L1_BASELINE_AT_S0 - L1_DELIBERATE_SHRINK
L1_EXPECTED_FILES = ["implementation_engine.py"]

#: L2 (design.md D6): each of these must still resolve, spelled exactly --
#: catches a targeted rename that leaves L1's total count unchanged.
CAMPAIGN_PROPOSAL_SYMBOLS = (
    "proposalDigest", "GATE_PROPOSAL_", "_proposal_digest",
    "_verify_gate_proposal", "_gate_proposal_question",
    "_verify_optional_election", "cmd_propose", "_authorization_binding",
    "_verify_gate_authorization", "_campaign_identity",
    "_load_remote_execution_",
)


class CampaignProposalExclusionTests(unittest.TestCase):
    """D6: the pin alone is not enough (a targeted rename could leave the
    count unchanged) and the list alone is not enough (a wholesale
    rewording could drop the count while never touching a listed symbol).
    Three layers together."""

    def test_l1_residue_pin_equals_the_measured_s0_baseline_minus_its_one_recorded_shrink(self):
        source = ENGINE_FILE.read_text(encoding="utf-8")
        count = len(re.findall(r"\bproposal\b", source, re.IGNORECASE))
        files = sorted(
            path.name for path in _engine_files()
            if re.search(r"\bproposal\b", path.read_text(encoding="utf-8"),
                        re.IGNORECASE))
        self.assertEqual(
            count, L1_EXPECTED_COUNT,
            "the \\bproposal\\b occurrence count drifted from the measured S0 "
            f"baseline ({L1_BASELINE_AT_S0}) minus its one recorded, deliberate "
            f"shrink ({L1_DELIBERATE_SHRINK}, documents.label's "
            "ARMS_UNDECLARED_CONSEQUENCE conversion) -- any OTHER movement is a "
            "defect: a rename campaign, or an accidental sweep hitting the "
            "campaign-proposal meaning")
        self.assertEqual(files, L1_EXPECTED_FILES)

    def test_l2_named_exclusion_symbols_each_still_resolve(self):
        source = ENGINE_FILE.read_text(encoding="utf-8")
        missing = [symbol for symbol in CAMPAIGN_PROPOSAL_SYMBOLS
                  if symbol not in source]
        self.assertEqual(
            missing, [],
            f"the following campaign-proposal symbols no longer resolve, spelled "
            f"exactly, in the engine: {missing}")

    def test_l3_proposal_digest_is_still_an_authorization_binding_key(self):
        module = _import_engine_module()
        self.assertIn("proposalDigest", module._AUTHORIZATION_BINDING_KEYS)

    def test_wiring_proposal_third_sense_residue_is_covered_by_l1_not_l2(self):
        """Recorded (design.md D6): `wiring_proposal`/`_wiring_first_publication`
        spell `proposal` in a THIRD sense -- a draft suggestion, neither the
        managed document nor the campaign launch. In neither the L2 list nor
        renamed into `documents.label`; L1's occurrence pin is their only
        instrument, and this test exists so that fact is asserted rather than
        merely narrated."""
        source = ENGINE_FILE.read_text(encoding="utf-8")
        self.assertIn("wiring_proposal", source)
        self.assertNotIn("wiring_proposal", CAMPAIGN_PROPOSAL_SYMBOLS)


# --- M5: the derived-denylist layer (TS C-3) has now landed ----------------
#
# Landed above (`DerivedDenylistTests`, change `the-second-skill-the-seam-
# was-for`, slice A4, design.md D9): a second implementation profile
# (`experimental-implementation`) now exists on disk, so `buildDenylist`'s
# "others" set is non-empty and the lock is satisfiable rather than
# vacuous. This comment previously recorded why it was deferred; it is kept
# here, corrected, as the historical reason the deferral existed at all --
# never a `skipTest`, which would have moved the pinned `OK (skipped=6)`
# baseline this cut is not allowed to move.


# --- D10: the single-document guarantee -------------------------------------
#
# `CLAIM_KEY`/`LOCUS_KEY`/`REMEDY_LOCUS_KEY`/`NOTATION_KEYS`/`CITATION_RE` are
# module-level scalars read from `PROFILE[...]`, and
# `_extra_document_fidelity_status` folds four conditions its own docstring
# calls document-count-invariant. A `documents[1]` declared before change C
# therefore yields a fidelity status that reads green having measured
# nothing -- change C's whole first act is deleting this guard (design.md
# D10). Deliberately a SHIPPED-SURFACE lock, never a `_resolve()` refusal:
# `tests/fixtures/two_documents/impl_profile.py` and the whole `tests/pair/`
# suite depend on a two-document profile still resolving, and refusing
# `len(documents) > 1` inside the resolver would take them down.
# `discover_profiles()` globs `.claude/skills/*/impl_profile.py` only, so
# that fixture under `tests/` stays invisible to this lock, by the same
# reasoning the resolver's own module docstring already records.

class SingleDocumentGuaranteeTests(unittest.TestCase):
    """Task 4.8 (design.md D10). Mutation X8 (task 4.9): add a second
    `documents` entry to a SCRATCH COPY of this skill's own profile,
    confirm this lock fails, restore -- proven inline below, never against
    the shipped profile."""

    def test_every_discovered_profile_declares_exactly_one_document(self):
        profiles = discover_profiles()
        self.assertGreaterEqual(
            len(profiles), 1,
            "expected at least one profile on disk; this check would "
            "otherwise be vacuous")
        for entry in profiles:
            with self.subTest(skill=entry["skill_name"]):
                documents = entry["profile"].get("documents")
                self.assertEqual(
                    isinstance(documents, (list, tuple)) and len(documents), 1,
                    f"{entry['skill_name']} declares "
                    f"{len(documents) if isinstance(documents, (list, tuple)) else 'a non-list'} "
                    "documents entries -- a second entry (documents[1]) "
                    "yields a fidelity status that reads green having "
                    "measured nothing until change C lands its own "
                    "per-document fidelity fold; this guard is change C's "
                    "first deletion")

    def test_x8_a_second_documents_entry_on_a_scratch_copy_fails_this_lock(self):
        """Mutation X8: add a second `documents` entry to a SCRATCH COPY of
        this skill's own profile (never the shipped one), confirm the
        single-document assertion above -- reapplied directly to the
        mutated profile dict -- fails; the shipped profile is untouched."""
        real_entry = next(
            entry for entry in discover_profiles()
            if entry["skill_name"] == "experimental-implementation")
        real_documents = real_entry["profile"]["documents"]
        self.assertEqual(len(real_documents), 1)

        mutated_documents = list(real_documents) + [
            {"directory": Path("/scratch/second-document"), "label": "second"}]
        self.assertEqual(len(mutated_documents), 2)

        # The lock's own assertion, applied directly to the mutated
        # (in-memory only) documents list: it must now fail.
        with self.assertRaises(AssertionError):
            self.assertEqual(
                isinstance(mutated_documents, (list, tuple)) and len(mutated_documents), 1)

        # The shipped profile file itself was never touched.
        shipped_source = (
            SKILLS_DIR / "experimental-implementation" / "impl_profile.py"
        ).read_text(encoding="utf-8")
        self.assertEqual(shipped_source.count('"directory":'), 1)


if __name__ == "__main__":
    unittest.main()
