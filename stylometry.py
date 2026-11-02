"""
Signal two: the style signal. Measures the text as text, without understanding it.

Direction convention: each measure is first turned into a "human-ness" value
from 0 to 1 (higher = more human-like). style_signal() averages them and flips
the result, so the final score is 0-1 where HIGHER = MORE LIKELY AI, the same
direction as detector.model_signal.

Blind spot: it cannot read. Typos, broken-up sentences or a pasted quotation
change the shape without changing the substance, and it is unreliable on short text.
"""

import re
import statistics


def sentences(text: str) -> list[str]:
    """Split into sentences. Rough and good enough — given to you."""
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p for p in parts if p.strip()]


def words(text: str) -> list[str]:
    """Split into lowercase words, punctuation stripped. Given to you."""
    return re.findall(r"[a-z0-9']+", text.lower())


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _scale(value: float, low: float, high: float) -> float:
    """Map value onto 0-1 so that low -> 0.0 and high -> 1.0, clamped."""
    return _clamp01((value - low) / (high - low))


# ── The three measures ───────────────────────────────────────────────────────

def sentence_length_spread(text: str) -> float:
    """
    Coefficient of variation of sentence length (stdev / mean, in words).
    Higher = lumpier = more human-like. Roughly 0.2 (even) to 0.8 (varied).
    One sentence (or none) has no spread, so it returns 0.0, which reads as
    "perfectly even" and leans AI-like. That is a decision, not a fact.
    """
    lengths = [len(words(s)) for s in sentences(text)]
    lengths = [n for n in lengths if n > 0]
    if len(lengths) < 2:
        return 0.0
    mean = statistics.mean(lengths)
    return statistics.stdev(lengths) / mean if mean else 0.0


def type_token_ratio(text: str) -> float:
    """
    Unique words over total words, measured on the first 100 words only so that
    long and short texts are comparable. Higher = more varied vocabulary = more
    human-like. Between 0 and 1.
    """
    w = words(text)[:100]
    if not w:
        return 0.0
    return len(set(w)) / len(w)


def punctuation_density(text: str) -> float:
    """
    Non-terminal punctuation marks per word: commas, semicolons, colons, dashes,
    parentheses, quotes, ! and ?. Full stops are ignored because every writer
    uses them. Higher = more varied punctuation = more human-like.
    """
    w = words(text)
    if not w:
        return 0.0
    marks = re.findall(r"[,;:()\"!?\u2014\u2013-]", text)
    return len(marks) / len(w)


# ── Combining them ───────────────────────────────────────────────────────────

def style_signal(text: str) -> float:
    """
    The style signal as a 0-1 score. Higher = more likely AI.

    Each measure is scaled onto 0-1 as "human-ness", then averaged with equal
    weights, then flipped:

        spread:       0.2 -> 0 (even),   0.7 -> 1 (lumpy)
        vocabulary:   0.5 -> 0 (repeats), 0.85 -> 1 (varied)
        punctuation:  0.03 -> 0 (sparse), 0.15 -> 1 (varied)
    """
    human_spread = _scale(sentence_length_spread(text), 0.2, 0.7)
    human_vocab = _scale(type_token_ratio(text), 0.5, 0.85)
    human_punct = _scale(punctuation_density(text), 0.03, 0.15)

    human_score = (human_spread + human_vocab + human_punct) / 3
    return round(1.0 - human_score, 4)


if __name__ == "__main__":
    import sys

    text = " ".join(sys.argv[1:]) or (
        "The system works well. It handles most cases correctly and provides "
        "good results. Users generally find it easy to use and understand."
    )

    print(f"{len(sentences(text))} sentences, {len(words(text))} words\n")
    print(f"sentence_length_spread   {sentence_length_spread(text):.3f}")
    print(f"type_token_ratio         {type_token_ratio(text):.3f}")
    print(f"punctuation_density      {punctuation_density(text):.3f}")
    print(f"style_signal             {style_signal(text)}   (higher = more likely AI)")