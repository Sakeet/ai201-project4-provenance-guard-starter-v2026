"""
Turning two numbers into one, and one number into something a person can read.
← YOU BUILD THIS IN MILESTONES 4 AND 5

Two functions live here, and both are stubs.

`combine_signals` is where your false-positive decision from Milestone 1
actually gets made. Everything above it — the labels, the appeal path — is
downstream of a number this function produced.

`score_to_label` is where you stop writing for a machine and start writing for
a person. A score of 0.62 means nothing to a writer.

⚠️ Your README's **Signals and Scoring** section has to name the file and
function holding your combining rule. The grader checks your code against what
you claim, so that line should read `scoring.py::combine_signals`.
"""

import config

def combine_signals(model_score: float, style_score: float, word_count: int = 999,
                    cue_score: float | None = None) -> float:
    """
    Two signals: 0.6/0.4 weighted average. Three signals: 0.45/0.30/0.25.
    Guards: AI needs the signals to agree (all of them with two signals, at
    least two of three with three signals); human needs every signal <= 0.5;
    text under MIN_WORDS can never be confident either way.
    """
    # UNIT 8 STRETCH (second improvement): a cue score of 0 means "no cue
    # phrases found", not evidence of a human. Counting it at weight 0.25 capped
    # every cue-free text at 0.75 (so "ai" was unreachable) and dragged EV05
    # into "human". With no cue phrases, fall back to the two-signal weights.
    if cue_score == 0:
        cue_score = None

    if cue_score is None:
        scores = [model_score, style_score]
        score = (config.WEIGHT_MODEL_SIGNAL * model_score
                 + config.WEIGHT_STYLE_SIGNAL * style_score)
        votes_needed = 2
    else:
        scores = [model_score, style_score, cue_score]
        score = (config.WEIGHT3_MODEL * model_score
                 + config.WEIGHT3_STYLE * style_score
                 + config.WEIGHT3_CUE * cue_score)
        votes_needed = 2

    just_below_ai = config.AI_THRESHOLD - 0.01
    just_above_human = config.HUMAN_THRESHOLD + 0.01

    ai_votes = sum(1 for s in scores if s >= config.AI_AGREE_MIN)
    if cue_score is None:
        votes_needed = len(scores)
    if score >= config.AI_THRESHOLD and ai_votes < votes_needed:
        score = just_below_ai
    if score <= config.HUMAN_THRESHOLD and max(scores) > config.HUMAN_AGREE_MAX:
        score = just_above_human
    if word_count < config.MIN_WORDS:
        score = min(max(score, just_above_human), just_below_ai)

    return round(score, 4)

def score_to_label(score: float) -> tuple[str, str]:
    """
    Turn a score into a guess and the text a reader actually sees.
    ← TODO (Milestone 5)

    Returns:
        (guess, label_text) — where `guess` is a short machine-readable string
        like "ai" / "human" / "unsure", and `label_text` is the full sentence
        shown to a person.

    ⚠️ Write the label text for someone who has never heard the word
    "threshold".

        ✗ "human, 0.81 confidence"
        ✓ "We think this was probably written by a person."

    All three labels have to be **reachable**. If no score can produce one of
    them, your ranges have a gap — and Milestone 5 asks you to submit text that
    produces each one, which is how you'd find out.

    The hardest one to write is "unsure". It has to admit uncertainty without
    sounding like an accusation, because the person reading it may well have
    written every word themselves. Your breakout asks your group what they'd
    think if they got it on their own work. That question is the whole
    milestone.
    """
    if score >= config.AI_THRESHOLD:
        return "ai", (
            "Our tools think this may have been written with the help of AI, "
            "but they can be wrong, especially with plain or simple writing. "
            "If you wrote it yourself, you can appeal and your work will be "
            "marked as under review."
        )
    if score <= config.HUMAN_THRESHOLD:
        return "human", "We think this was most likely written by a person."
    return "unsure", (
        "Our tools aren't perfect, and we couldn't tell whether this was "
        "written by a person or with AI. We're not drawing any conclusion "
        "about you or your work, and you don't need to do anything."
    )


def label_ranges() -> list[tuple[str, str]]:
    """
    The score range each label covers. Your README needs these beside the
    label text — given to you so the numbers can't drift apart from config.py.
    """
    return [
        ("high-confidence human", f"0.00 – {config.HUMAN_THRESHOLD:.2f}"),
        ("unsure", f"{config.HUMAN_THRESHOLD:.2f} – {config.AI_THRESHOLD:.2f}"),
        ("high-confidence AI", f"{config.AI_THRESHOLD:.2f} – 1.00"),
    ]