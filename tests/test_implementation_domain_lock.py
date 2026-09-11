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
KIT_DIR = SKILLS_DIR / "proposal-implementation" / "assets" / "kit"
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
            "names": names,
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
        itself' -- the TS lock's own words, mirrored exactly."""
        for entry in discover_profiles():
            with self.subTest(skill=entry["skill_name"]):
                lower_source = entry["source"].lower()
                unused = [n for n in entry["names"] if n.lower() not in lower_source]
                self.assertEqual(
                    unused, [],
                    f"{entry['skill_name']}: a name no profile value contains "
                    "is not this domain naming itself")


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


class KitAgreementLockTests(unittest.TestCase):
    """D4 (design.md): the kit template's provenance keys agree with the
    profile -- six sites, two of them EXECUTABLE code that runs inside a
    target's own interpreter, which is the sharpest reason this needs a
    test: a divergence there fails in somebody else's repository, not in
    this suite. No kit file is ever edited by this lock or by this cut."""

    @staticmethod
    def _profile() -> Mapping[str, Any]:
        path = SKILLS_DIR / "proposal-implementation" / "impl_profile.py"
        return _load_profile_module(path).PROFILE

    def test_module_py_declares_the_agreed_provenance_keys(self):
        source = (KIT_DIR / "src" / "module.py").read_text(encoding="utf-8")
        match = re.search(r"__provenance__\s*=\s*\{(.*?)\n\}", source, re.DOTALL)
        self.assertIsNotNone(match, "module.py declares no __provenance__ literal")
        keys = set(re.findall(r'"(\w+)":', match.group(1)))
        self.assertGreater(len(keys), 0, "extraction found no keys -- vacuous")
        claim_key = self._profile()["provenance"]["claim_key"]
        self.assertEqual(keys, {"revision", "sections", claim_key, "invariants"})

    def test_module_py_rules_docstring_names_both_keys(self):
        source = (KIT_DIR / "src" / "module.py").read_text(encoding="utf-8")
        claim_key = self._profile()["provenance"]["claim_key"]
        self.assertIn(f'`{claim_key}`', source)
        self.assertIn("`sections`", source)

    def test_src_benchmark_arms_example_spells_sections(self):
        source = (KIT_DIR / "src_benchmark" / "__init__.py").read_text(
            encoding="utf-8")
        example = re.search(r'#\s*"arms":\s*\{.*?\n(?:\s*#.*\n)*', source)
        self.assertIsNotNone(example, "no commented arms example found -- vacuous")
        self.assertIn("sections", example.group(0))

    def test_findings_py_commented_keys_equal_locus_and_remedy_locus(self):
        source = (KIT_DIR / "tests" / "findings.py").read_text(encoding="utf-8")
        profile = self._profile()
        locus_key = profile["findings"]["locus_key"]
        remedy_locus_key = profile["findings"]["remedy_locus_key"]
        self.assertIn(f'#     "{locus_key}"', source)
        self.assertIn(f'#     "{remedy_locus_key}"', source)

    def test_test_audit_py_executable_subscript_equals_remedy_locus_key(self):
        source = (KIT_DIR / "tests" / "test_audit.py").read_text(encoding="utf-8")
        remedy_locus_key = self._profile()["findings"]["remedy_locus_key"]
        pattern = rf'finding\["{re.escape(remedy_locus_key)}"\]'
        self.assertRegex(source, pattern)

    def test_verification_notebook_executable_subscript_equals_claim_key(self):
        source = (KIT_DIR / "nb" / "verification.ipynb").read_text(encoding="utf-8")
        claim_key = self._profile()["provenance"]["claim_key"]
        pattern = rf"p\['{re.escape(claim_key)}'\]"
        self.assertRegex(source, pattern)


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


# --- M5: the derived-denylist layer (TS C-3) is explicitly deferred --------
#
# `buildDenylist` (the TS lock) marks a word as one domain's subject when NO
# OTHER profile's north uses it. With one implementation profile on disk,
# the "others" set is empty and every word >=5 chars in `OBJECTIVE_FLOW`
# becomes a denylist entry -- not a stricter lock, an unsatisfiable one.
# Deferred to the day a second implementation profile exists. Landing it now
# as a `skipTest` would move the pinned `OK (skipped=6)` baseline this cut
# is not allowed to move -- so there is deliberately no test stub here at
# all, only this recorded reason (design.md M5, tasks.md 13.8).


if __name__ == "__main__":
    unittest.main()
