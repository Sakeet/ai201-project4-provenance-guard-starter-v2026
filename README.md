# Provenance Guard

A small backend service a writing site could plug into. Text comes in. What comes back is a guess, a confidence number, a plain-English label the reader would see, and a way for the writer to appeal.

How to run it: see [RUNNING.md](RUNNING.md).

---

## Stretch features (declared before building)

1. **A third signal** (`cues.py`): counts formulaic transition phrases ("furthermore", "in conclusion", "it is important to note"). I will write down how the three signals are weighted.
2. **`GET /content/<id>`**: returns one item's current status.
3. **A verified-human path** (`POST /verify`): a writer earns a credential through an extra step, and it shows on their work.

---

## What This Does

1. A request arrives at `POST /submit` with JSON `text` and an optional `creator_id` (defaults to "unknown").
2. Validation: `text` must be a non-empty string, otherwise the service returns a 400 `bad_request`. Rejected input writes no log entry.
3. Signal one (`detector.py`, gpt2 running locally) produces `model_score`. Text under 3 tokens returns a 400, and a model that can't load returns a 503.
4. Signal two (`stylometry.py`) produces `style_score` from the shape of the text.
5. `scoring.py::combine_signals` merges the two scores and the word count into one combined score.
6. `scoring.py::score_to_label` turns the combined score into a guess (ai / human / unsure) and the plain-English label.
7. A `content_id` is generated and the decision (all three scores, guess, label, status "decided") is appended to `logs/audit.jsonl`, then the JSON is returned.

`POST /appeal` takes a `content_id` and the writer's reasoning, checks the ID exists (404 if not, 400 if fields are missing), and appends a second log entry with status `under_review`. The log is append-only, so the original decision stays in place and the appeal sits after it. There is no automatic re-checking.

`confidence` in the response is the distance of the combined score from the uncertain middle: `abs(combined - 0.5) * 2` (0 = no idea, 1 = certain).

---

## Signals and Scoring

### Signal one — the model signal

**What it measures:** Perplexity under gpt2, meaning how predictable the text is to a language model, squashed onto 0-1 (higher = more likely AI).

**Why that might differ between human and AI writing:** A language model writes by picking likely next words, so AI text tends to be easy for a model to predict. Human writing wanders more, with odd word choices and abrupt turns.

**What it can't see:** Authorship. It only sees predictability, so plain writing with common words in short sentences scores machine-like. My tests confirmed this: an ordinary human paragraph about a grandmother's button tin scored 0.7128, close to my AI samples (0.7368 and 0.7533). The reverse also happens: ornate prose with rare words can score as human, so AI text with unusual vocabulary can slip through.

### Signal two — the style signal

**What it measures:** Three surface statistics: sentence-length spread (stdev divided by mean), type-token ratio on the first 100 words, and non-terminal punctuation per word. Each is scaled to a 0-1 "human-ness" value, the three are averaged with equal weights, and the result is flipped so higher = more likely AI. The scaling ranges are my own starting guesses (spread 0.2-0.7, vocabulary 0.5-0.85, punctuation 0.03-0.15) and I did not tune them.

**Why that might differ between human and AI writing:** AI text tends toward even, mid-length sentences and a narrower vocabulary. Human writing is lumpier.

**What it can't see:** Meaning. Anything that changes the shape without changing the substance moves it: typos, split sentences, a pasted quotation. It is also noisy on short text. In my tests it never rose above about 0.47 on any text, human or AI, so it separates the two classes only weakly.

### The combining rule

**The rule:** A weighted average, with guards. "High-confidence AI" needs a very high combined score AND both signals leaning AI. "High-confidence human" needs a low combined score AND both signals leaning human. Text under 40 words can never be confident either way. Everything else is "unsure".

**The numbers:** Weights 0.6 model / 0.4 style. AI: combined >= 0.85 and both signals >= 0.6. Human: combined <= 0.30 and both signals <= 0.5. Minimum 40 words. All of these are in `config.py`.

**Where it lives:** `scoring.py::combine_signals` (numbers in `config.py`)

**A case where my two signals split, and what my rule does with it:** My clearly-AI sample scored model 0.7544 but style 0.459, so the average is about 0.64 and it lands in "unsure". The reverse split also happens: `human_b` scored model 0.5227 and style 0.0009 (combined 0.314). The style signal read it as very human, but the model signal sat above 0.5, so the agreement guard keeps it out of "human". This is deliberate: when the signals disagree the rule says "unsure", because a wrong accusation costs a writer more than a missed detection costs the site.

**Results against my criteria (honest status):**
- **Label coverage (criterion 3): not met.** Across more than 10 test texts only "unsure" was ever produced. The closest human text reached combined 0.3029, which is 0.0029 over the 0.30 bar. The best AI sample reached 0.6266, far below 0.85, because the style signal tops out near 0.47 and a 0.6/0.4 average can't reach the bar. I did not lower the thresholds to force a label. The fix belongs upstream, in a style signal that rises on AI text.
- **False positives (criterion 1):** None of my 9 human test texts were labeled AI. One caveat: `plain_human` (27 words) scored 0.9024 on the model signal and 0.7838 on the style signal, and was held back only by the 40-word guard, not by the 0.85 bar. Other plain human texts scored 0.53-0.62 combined, so the risk is real, and the high AI bar plus the short-text guard are what protect those writers.
- **Bad input (criterion 4): partly met.** Missing, empty and too-short text return a 400 and write no log entry. The 10000-character limit is not enforced in `app.py` yet.
- **Appeal path (criterion 5):** A valid appeal returned 200 and wrote an `under_review` entry to the log. An unknown `content_id` returned 404 and missing reasoning returned 400.

---

## Label Variants

| Label | Score range | The exact text a reader sees |
|---|---|---|
| high-confidence human | 0.00 - 0.30 | We think this was most likely written by a person. |
| unsure | 0.30 - 0.85 | Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything. |
| high-confidence AI | 0.85 - 1.00 | Our tools think this may have been written with the help of AI, but they can be wrong, especially with plain or simple writing. If you wrote it yourself, you can appeal and your work will be marked as under review. |

**Why I worded the "unsure" one this way:** Most submissions, including real writers' work, land here, so it can't sound like an accusation. It admits the tools' limit first, says no conclusion is being drawn, and ends with "you don't need to do anything" so the writer isn't left wondering what to do next. The AI label says "may have" and mentions plain writing because my own tests showed plain human writing scores machine-like, and it only promises what `/appeal` actually does (marks the work as under review).

---

## Sample Run

**A submission**

```bash
$ curl.exe -X POST http://127.0.0.1:5000/submit -H "Content-Type: application/json" -d '{"text": "I did not sleep. Not properly, anyway. I lay there listening to the boiler tick and thinking about the thing I said at the pub, which was stupid, and which he will absolutely bring up again. So: coffee, and the long way round to work, and a plan. The plan lasted until about ten past nine.", "creator_id": "u4"}'
```

```json
{
  "combined_score": 0.3218,
  "confidence": 0.3564,
  "content_id": "c_84d5f338a110",
  "guess": "unsure",
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "model_score": 0.3934,
  "style_score": 0.2143
}
```

**An appeal**

```bash
$ curl.exe -X POST http://127.0.0.1:5000/appeal -H "Content-Type: application/json" -d '{"content_id": "c_84d5f338a110", "reasoning": "I wrote this myself for my class."}'
```

```json
{
  "content_id": "c_84d5f338a110",
  "message": "Thanks. Your appeal has been recorded and this work is now marked as under review.",
  "status": "under_review"
}
```

**What the log shows afterwards**

```bash
$ curl.exe "http://127.0.0.1:5000/log?limit=3"
```

```json
{
  "count": 3,
  "entries": [
    {
      "content_id": "c_97ef0a0d3c4f",
      "creator_id": "u3",
      "event": "appeal",
      "reasoning": "I wrote this myself for my class.",
      "status": "under_review",
      "timestamp": "2026-11-02T05:38:55+00:00"
    },
    {
      "combined_score": 0.3218,
      "content_id": "c_84d5f338a110",
      "creator_id": "u4",
      "guess": "unsure",
      "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
      "model_score": 0.3934,
      "status": "decided",
      "style_score": 0.2143,
      "timestamp": "2026-11-02T06:06:56+00:00"
    },
    {
      "content_id": "c_84d5f338a110",
      "creator_id": "u4",
      "event": "appeal",
      "reasoning": "I wrote this myself for my class.",
      "status": "under_review",
      "timestamp": "2026-11-02T06:08:51+00:00"
    }
  ]
}
```

---

## How I Used AI

**Moment 1**

- *What I asked for:* Help writing my Milestone 1 notes, including the blind spot for signal one.
- *What came back:* A draft saying signal one's blind spot was polished or formal human writing.
- *What I changed:* After reading the docstring in `detector.py`, I saw that was backwards: the signal rewards common words in short sentences, so plain writers are the ones it flags. I rewrote the blind spot and my false-positive trace (a plain second-language writer), then confirmed it with a measured result (plain human text scoring 0.7128 on the model signal).

**Moment 2**

- *What I asked for:* The `/appeal` route, after pasting my `audit.py` so the function names matched.
- *What came back:* A route that validates input, checks `audit.entries_for`, and calls `audit.log_appeal` using the creator from the original decision.
- *What I changed:* I first pasted it into `audit.py` instead of `app.py`, which overwrote `log_appeal`. I restored `audit.py` with `git checkout`, put the route in `app.py`, and tested the 200, 404 and 400 paths with curl.

---

<!-- ═══════════════════════ UNIT 8 — THE TEST (to be filled next unit) ═══════════════════════ -->

## Rate Limiting

## Attack Run — Before

## Run Log and Verdicts

## The Improvement

## What's Still Broken
