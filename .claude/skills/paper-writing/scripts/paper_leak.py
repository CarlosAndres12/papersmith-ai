"""paper_leak: the three-draft proof (register distance + n-gram overlap)
and the eight-token tripwire — deliberately separated by signature so
tuning the tripwire can never move the proof (`style-leak-detection` spec;
`design.md`, Decision D6).

`relative_overlap_holds` takes no threshold parameter: `overlap(S,R) <=
max(overlap(A,R), overlap(B,R))` is self-calibrating against whatever chance
floor two unstyled drafts already produce. `register_distance_holds`
requires both unstyled controls positionally — there is no way to compute
`d(S,{A,B})` without also computing `d(A,B)`, so a caller cannot drop the
control and still get a "pass" (mutation 6). Both read `paper_style.
normalize_tokens` for tokenization; math is excluded once, at the source.

Public surface:

    register_distance_holds(styled, unstyled_a, unstyled_b) -> dict
    relative_overlap_holds(styled, unstyled_a, unstyled_b, samples) -> dict
    overlap_against_set(text, samples)          -> int
    tripwire_spans(styled, samples, min_tokens=8) -> list[dict]
    check_tripwire(styled, samples)              -> None  (raises STYLE_OVERLAP)
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import paper_style  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "_core" / "implementation"))
from impl_refusals import Refused  # noqa: E402

#: A closed, small set of function words whose relative frequency, together
#: with sentence-length distribution, makes up the register profile
#: (`style-leak-detection` spec, `Requirement: Register Distance Rises With
#: Style, Measured Against The A/B Control`). Not an attempt at a complete
#: function-word list — a fixed, shared vocabulary both `S` and `{A,B}` are
#: measured against identically.
_FUNCTION_WORDS: tuple[str, ...] = (
    "the", "a", "an", "of", "in", "on", "to", "for", "with", "and", "or",
    "but", "is", "are", "was", "were", "this", "that", "these", "those",
    "which", "as", "by", "at", "from", "it", "its", "be", "been", "we",
    "our", "not", "than", "such", "into", "over", "under", "between",
)

_SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+")


def _sentence_lengths(text: str) -> list[int]:
    sentences = [s for s in _SENTENCE_SPLIT_RE.split(text.strip()) if s.strip()]
    return [len(paper_style.normalize_tokens(sentence)) for sentence in sentences]


def _profile(text: str) -> dict:
    tokens = paper_style.normalize_tokens(text)
    lengths = _sentence_lengths(text)
    mean_length = sum(lengths) / len(lengths) if lengths else 0.0
    total = len(tokens) or 1
    frequencies = {word: tokens.count(word) / total for word in _FUNCTION_WORDS}
    return {"mean_sentence_length": mean_length, "function_word_freq": frequencies}


def _average_profile(profile_a: dict, profile_b: dict) -> dict:
    mean_length = (profile_a["mean_sentence_length"] + profile_b["mean_sentence_length"]) / 2
    frequencies = {
        word: (profile_a["function_word_freq"][word] + profile_b["function_word_freq"][word]) / 2
        for word in _FUNCTION_WORDS
    }
    return {"mean_sentence_length": mean_length, "function_word_freq": frequencies}


def _distance(profile_a: dict, profile_b: dict) -> float:
    total = abs(profile_a["mean_sentence_length"] - profile_b["mean_sentence_length"])
    for word in _FUNCTION_WORDS:
        total += abs(profile_a["function_word_freq"][word] - profile_b["function_word_freq"][word])
    return total


def register_distance_holds(styled: str, unstyled_a: str, unstyled_b: str) -> dict:
    """`d(S,{A,B})` MUST exceed `d(A,B)`; both are reported
    (`style-leak-detection` spec, `Requirement: Register Distance Rises With
    Style, Measured Against The A/B Control`). `unstyled_a`/`unstyled_b` are
    both required positionally — omitting either is a `TypeError`, not a
    silent default (mutation 6: dropping the control must fail
    construction)."""
    profile_s = _profile(styled)
    profile_a = _profile(unstyled_a)
    profile_b = _profile(unstyled_b)
    d_ab = _distance(profile_a, profile_b)
    d_s_ab = _distance(profile_s, _average_profile(profile_a, profile_b))
    return {"d_S_AB": d_s_ab, "d_AB": d_ab, "pass": d_s_ab > d_ab}


def _longest_run(tokens_a: list[str], tokens_b: list[str]) -> int:
    best = 0
    for i in range(len(tokens_a)):
        for j in range(len(tokens_b)):
            run = 0
            while (
                i + run < len(tokens_a) and j + run < len(tokens_b)
                and tokens_a[i + run] == tokens_b[j + run]
            ):
                run += 1
            if run > best:
                best = run
    return best


def overlap_against_set(text: str, samples: list[dict]) -> int:
    """The longest contiguous normalized n-gram `text` shares with ANY
    sample in `samples` (`R`, never a reference file read directly —
    `style-leak-detection` spec, `Requirement: Overlap Reads Only The
    Recorded Sample Set`)."""
    tokens = paper_style.normalize_tokens(text)
    if not samples:
        return 0
    return max(_longest_run(tokens, paper_style.normalize_tokens(sample["span"])) for sample in samples)


def relative_overlap_holds(styled, unstyled_a, unstyled_b, samples) -> dict:
    """`overlap(S,R) <= max(overlap(A,R), overlap(B,R))` — self-calibrating,
    no threshold parameter (`design.md`, Decision D6; `style-leak-detection`
    spec, `Requirement: Overlap Does Not Rise Above The Chance Floor`)."""
    overlap_s = overlap_against_set(styled, samples)
    overlap_a = overlap_against_set(unstyled_a, samples)
    overlap_b = overlap_against_set(unstyled_b, samples)
    return {
        "overlap_S": overlap_s, "overlap_A": overlap_a, "overlap_B": overlap_b,
        "pass": overlap_s <= max(overlap_a, overlap_b),
    }


def tripwire_spans(styled: str, samples: list[dict], *, min_tokens: int = 8) -> list[dict]:
    """Every maximal contiguous run of at least `min_tokens` normalized
    tokens `styled` shares with a sample in `samples`, naming the span and
    the reference it came from. A pure measurement — never refuses on its
    own; `check_tripwire` below is the refusing wrapper (`style-leak-
    detection` spec, `Requirement: The Eight-Token Tripwire`)."""
    styled_tokens = paper_style.normalize_tokens(styled)
    hits: list[dict] = []
    for sample in samples:
        sample_tokens = paper_style.normalize_tokens(sample["span"])
        index = 0
        while index < len(styled_tokens):
            best_length = 0
            for start in range(len(sample_tokens)):
                run = 0
                while (
                    index + run < len(styled_tokens) and start + run < len(sample_tokens)
                    and styled_tokens[index + run] == sample_tokens[start + run]
                ):
                    run += 1
                if run > best_length:
                    best_length = run
            if best_length >= min_tokens:
                hits.append({
                    "reference": sample.get("reference"),
                    "span": " ".join(styled_tokens[index:index + best_length]),
                    "length": best_length,
                })
                index += best_length
            else:
                index += 1
    return hits


def check_tripwire(styled: str, samples: list[dict]) -> None:
    """Refuses `STYLE_OVERLAP`, naming the shared span and the reference it
    came from, when `tripwire_spans` finds at least one hit."""
    hits = tripwire_spans(styled, samples)
    if hits:
        first = hits[0]
        raise Refused(
            "STYLE_OVERLAP",
            f"styled draft shares {first['length']} normalized tokens with reference "
            f"{first['reference']!r}: {first['span']!r}",
        )
