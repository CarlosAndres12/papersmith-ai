#!/usr/bin/env python3
"""Capture `tests/experiments_seal/`'s own seal -- `tests/seal_capture.py`'s
identical double-run-agreement discipline, mirrored for THIS corpus rather
than shared with it (the two corpora build independent fixture roots and
run through independent launchers, design.md D7). Not matched by `unittest
discover`'s `test*.py` pattern, so it never runs inside the recurring
suite -- invoked by hand
(`.venv/bin/python tests/experiments_seal_capture.py`) only when the roster
or the sealed behaviour has genuinely changed.

On agreement (or on a disagreement confined to `NON_DETERMINISTIC_CASE_IDS`
-- `propose`'s own recorded non-determinism, design.md M9), writes
`tests/experiments_seal/digests.json` (one digest entry per case id, run
A's own capture, plus a reserved `__corpus_fingerprint__` entry) --
`unsealed.json` is maintained by hand, never written here, since it
records commands excluded from the ROSTER entirely, a decision this
script does not make. All-or-nothing: an UNEXPECTED disagreement (any case
not already in `NON_DETERMINISTIC_CASE_IDS`) refuses to write anything at
all.
"""

from __future__ import annotations

import difflib
import hashlib
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

FORGE = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(Path(__file__).resolve().parent))
from experiments_seal import corpus as ec  # noqa: E402  (path set above)
from experiments_seal import harness as eh  # noqa: E402

CASES_PATH = Path(__file__).resolve().parent / "experiments_seal" / "cases.json"
DIGESTS_PATH = Path(__file__).resolve().parent / "experiments_seal" / "digests.json"
UNSEALED_PATH = Path(__file__).resolve().parent / "experiments_seal" / "unsealed.json"

#: `propose` differs from `tests/seal/`'s own convention (design.md M9):
#: it carries a case AND a digest entry, but `test_experiments_seal.py`'s
#: own `NON_DETERMINISTIC_CASE_IDS` excludes it from the byte-exact
#: comparison only -- its golden entry still exists (`test_every_case_id_
#: has_a_golden_entry` requires one for every case id). `materialize`
#: alone is fully excluded by design and carries no case in this corpus's
#: roster at all.
NON_DETERMINISTIC_CASE_IDS = {"propose"}

CORPUS_FINGERPRINT_KEY = "__corpus_fingerprint__"


def _corpus_fingerprint() -> dict:
    source = ec.CORPUS_FINGERPRINT_SOURCE.read_bytes()
    return {"sha256": hashlib.sha256(source).hexdigest()}


def _run_once(cases: list, *, label: str) -> dict:
    with tempfile.TemporaryDirectory(prefix=f"experiments-seal-capture-{label}-") as tmp:
        corpus_root = Path(tmp) / "corpus"
        roots = ec.build(corpus_root)

        scratch_root = (FORGE / "implementations"
                        / f"_experiments_seal_capture_{label}_{os.getpid()}")
        scratch_root.mkdir(parents=True)
        try:
            results = {}
            with eh.cli_invocation():
                for case in cases:
                    result = eh.run_case(case, roots, scratch_root=scratch_root)
                    results[case["id"]] = {
                        "result": result,
                        "digest": eh.digest_result(result),
                    }
            return results
        finally:
            shutil.rmtree(scratch_root, ignore_errors=True)


def capture() -> int:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    eh.validate_roster(cases)

    print(f"Capturing {len(cases)} cases, twice, in two independently-built corpora...")
    run_a = _run_once(cases, label="a")
    run_b = _run_once(cases, label="b")

    unexpected = []
    for case in cases:
        case_id = case["id"]
        if case_id in NON_DETERMINISTIC_CASE_IDS:
            continue
        a, b = run_a[case_id], run_b[case_id]
        if a["digest"] != b["digest"]:
            unexpected.append((case_id, a, b))

    if unexpected:
        print(f"UNEXPECTED DISAGREEMENT on {len(unexpected)} case(s); writing NOTHING.\n",
             file=sys.stderr)
        for case_id, a, b in unexpected:
            print(f"--- case {case_id} ---", file=sys.stderr)
            print(f"  run A: {a['digest']}", file=sys.stderr)
            print(f"  run B: {b['digest']}", file=sys.stderr)
            diff = difflib.unified_diff(
                a["result"].stdout_text.splitlines(keepends=True),
                b["result"].stdout_text.splitlines(keepends=True),
                fromfile=f"{case_id} (run A, normalized)",
                tofile=f"{case_id} (run B, normalized)")
            sys.stderr.writelines(diff)
            print(file=sys.stderr)
        return 1

    # `propose` carries a digest entry too (design.md M9, unlike `tests/
    # seal/`'s own convention) -- its RUN A digest, never compared across
    # the two runs, only excluded from the byte-exact assertion.
    digests = {case_id: run_a[case_id]["digest"] for case_id in run_a}
    digests[CORPUS_FINGERPRINT_KEY] = _corpus_fingerprint()

    DIGESTS_PATH.write_text(json.dumps(digests, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
    unsealed = json.loads(UNSEALED_PATH.read_text(encoding="utf-8"))

    print(f"Captured {len(digests) - 1} case digest(s). Wrote {DIGESTS_PATH} "
         f"({len(unsealed)} recorded excluded from comparison/roster: "
         f"{sorted(unsealed)}).")
    for case_id in sorted(digests):
        if case_id == CORPUS_FINGERPRINT_KEY:
            continue
        print(f"  {case_id}: sha256={digests[case_id]['sha256'][:12]}... "
             f"bytes={digests[case_id]['bytes']} exit={digests[case_id]['exit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(capture())
