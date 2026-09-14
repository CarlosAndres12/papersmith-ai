#!/usr/bin/env python3
"""Capture the seal: run every case in `tests/seal/cases.json` TWICE, in two
independently-built corpora, and refuse to write anything at all if any pair
disagrees (design.md D5). Not matched by `unittest discover`'s `test*.py`
pattern, so it never runs inside the recurring suite — invoked by hand
(`.venv/bin/python tests/seal_capture.py`) only when the roster or the
sealed behaviour has genuinely changed.

On agreement (or on a disagreement confined to `KNOWN_UNSEALED_REASONS` —
D5/D6's own declared-nondeterminism path), writes `tests/seal/digests.json`
(goldens, one entry per SEALED case plus a reserved `__corpus_fingerprint__`
entry) and `tests/seal/unsealed.json` (case id -> reason, today: `{"propose":
...}`) — committed as generated goldens (design.md, spec.md "Digests
Committed As Generated Goldens").

All-or-nothing: a half-written golden set can never exist (design.md D5). An
UNEXPECTED disagreement (any case not already in `KNOWN_UNSEALED_REASONS`)
still refuses to write anything at all.
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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from seal import corpus as seal_corpus  # noqa: E402  (path set above)
from seal import harness as seal_harness  # noqa: E402

CASES_PATH = Path(__file__).resolve().parent / "seal" / "cases.json"
DIGESTS_PATH = Path(__file__).resolve().parent / "seal" / "digests.json"
UNSEALED_PATH = Path(__file__).resolve().parent / "seal" / "unsealed.json"

#: A declared, human-diagnosed nondeterminism (design.md D5/D6) — never
#: auto-detected, never silently grown. Measured during apply, 2026-09-11:
#: `propose`'s own campaign-proposal digest (`cmd_propose`'s `digest` field)
#: is `sha256` over a JSON payload that embeds `_now_iso8601()` (the `at`
#: field) at second precision, so it differs across two immediate runs even
#: with source/session/job/rationale fixed — none of the six normalized
#: sources reach an opaque hash DERIVED FROM, but not textually equal to, a
#: timestamp; N1 only erases the literal ISO8601 string shape. Confirmed by
#: `seal_capture.py`'s own double-run disagreement check: every OTHER
#: byte of `propose`'s output (including `campaign`, `jobs`, `workers`,
#: `rationale`, `proposeOrdinal`) already agreed across the two runs, and
#: the disagreement is isolated to the `digest` field alone. The rejected
#: alternative — a seventh normalizer erasing any `"digest": "<64hex>"`
#: pattern — was not taken because spec.md's Normalization requirement
#: names exactly six sources, and `unsealed.json` is the mechanism the spec
#: itself provides for a source normalization genuinely cannot reach
#: (spec.md "Unsealed Commands Are Explicit And Exact": "MUST be recorded
#: in an explicit unsealed set with a reason, not stopping the change").
KNOWN_UNSEALED_REASONS = {
    "propose": (
        "propose's own campaign-proposal digest (cmd_propose's `digest` "
        "field) is sha256 over a JSON payload that embeds `_now_iso8601()` "
        "(the `at` field) at second precision, so it differs across two "
        "immediate runs even with source/session/job/rationale fixed -- "
        "none of the six normalized sources reach an opaque hash DERIVED "
        "FROM, but not textually equal to, a timestamp. Every other byte "
        "of the output agrees across the two runs; only `digest` moves. "
        "Measured via seal_capture.py's own double-run disagreement "
        "check, 2026-09-11."
    ),
}

#: Reserved key, never a valid case id (case ids are lowercase-hyphenated
#: command names, never dunder-wrapped). Digested into `digests.json` so
#: `test_corpus_fingerprint_matches` goes red the moment `corpus.py` is
#: edited without recapturing (design.md D3's anti-trim guard).
CORPUS_FINGERPRINT_KEY = "__corpus_fingerprint__"


def _corpus_fingerprint() -> dict:
    source = seal_corpus.CORPUS_FINGERPRINT_SOURCE.read_bytes()
    return {"sha256": hashlib.sha256(source).hexdigest()}


def _run_once(cases: list, *, label: str) -> dict:
    """One full pass: a fresh corpus build, one run per case. Returns
    `{case_id: {"result": CaseResult, "digest": {...}}}`.

    The corpus itself (the committed fixtures `copytree` reads FROM) never
    needs to live under `implementations/` -- it is never passed as
    `--target` directly. Every per-case SCRATCH COPY does: `resolve_target`
    refuses `OUTSIDE_WORKSPACE` for anything not under `FORGE_ROOT /
    "implementations"` (`implementations/*` is gitignored, so this never
    touches tracked state).
    """
    with tempfile.TemporaryDirectory(prefix=f"seal-capture-{label}-") as tmp:
        corpus_root = Path(tmp) / "corpus"
        roots = seal_corpus.build(corpus_root)

        scratch_root = (seal_harness.impl.FORGE_ROOT / "implementations"
                        / f"_seal_capture_{label}_{os.getpid()}")
        scratch_root.mkdir(parents=True)
        try:
            results = {}
            for case in cases:
                result = seal_harness.run_case(case, roots, scratch_root=scratch_root)
                results[case["id"]] = {
                    "result": result,
                    "digest": seal_harness.digest_result(result),
                }
            return results
        finally:
            shutil.rmtree(scratch_root, ignore_errors=True)


def capture() -> int:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    seal_harness.validate_roster(cases)

    print(f"Capturing {len(cases)} cases, twice, in two independently-built corpora...")
    run_a = _run_once(cases, label="a")
    run_b = _run_once(cases, label="b")

    known_unsealed, unexpected = [], []
    for case in cases:
        case_id = case["id"]
        a, b = run_a[case_id], run_b[case_id]
        if a["digest"] == b["digest"]:
            continue
        (known_unsealed if case_id in KNOWN_UNSEALED_REASONS else unexpected).append(
            (case_id, a, b))

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

    unsealed_ids = {case_id for case_id, _, _ in known_unsealed}
    digests = {case_id: run_a[case_id]["digest"] for case_id in run_a
              if case_id not in unsealed_ids}
    digests[CORPUS_FINGERPRINT_KEY] = _corpus_fingerprint()

    DIGESTS_PATH.write_text(json.dumps(digests, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
    unsealed = {case_id: KNOWN_UNSEALED_REASONS[case_id] for case_id in sorted(unsealed_ids)}
    UNSEALED_PATH.write_text(json.dumps(unsealed, indent=2, sort_keys=True) + "\n",
                             encoding="utf-8")

    print(f"Captured {len(digests) - 1} sealed case(s). Wrote {DIGESTS_PATH} and "
         f"{UNSEALED_PATH} ({len(unsealed_ids)} unsealed: {sorted(unsealed_ids)}).")
    for case_id in sorted(digests):
        if case_id == CORPUS_FINGERPRINT_KEY:
            continue
        print(f"  {case_id}: sha256={digests[case_id]['sha256'][:12]}... "
             f"bytes={digests[case_id]['bytes']} exit={digests[case_id]['exit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(capture())
