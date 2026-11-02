"""
Signal three: the cue signal. Counts formulaic transition phrases that
generated prose leans on. Higher = more likely AI (same direction as the others).
Blind spot: formal human writing (reports, essays) uses these phrases too, and
anyone can evade it by avoiding the list.
"""
import re
import stylometry

CUES = [
    "furthermore", "moreover", "additionally", "in conclusion", "therefore",
    "it is important to note", "it is essential", "plays a crucial role",
    "in today's", "significantly", "leverage", "foster", "overall",
    "various", "ensure", "crucial", "essential",
]


def cue_signal(text: str) -> float:
    lowered = text.lower()
    hits = sum(len(re.findall(r"\b" + re.escape(c) + r"\b", lowered)) for c in CUES)
    n_sentences = max(1, len(stylometry.sentences(text)))
    density = hits / n_sentences          # cue phrases per sentence
    return round(min(1.0, density / 0.8), 4)   # 0.8 per sentence or more = 1.0


if __name__ == "__main__":
    import sys
    t = " ".join(sys.argv[1:]) or "Furthermore, it is important to note that this is essential."
    print(f"cue_signal {cue_signal(t)}   (higher = more likely AI)")