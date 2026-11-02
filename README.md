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
5. Signal three (`cues.py`, stretch) produces `cue_score` from formulaic transition phrases.
6. `scoring.py::combine_signals` merges the three scores and the word count into one combined score.
7. `scoring.py::score_to_label` turns the combined score into a guess (ai / human / unsure) and the plain-English label.
8. A `content_id` is generated and the decision (all scores, guess, label, status "decided", verified_human) is appended to `logs/audit.jsonl`, then the JSON is returned.

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

### Signal three — the cue signal (stretch)

**What it measures:** Formulaic transition phrases per sentence ("furthermore", "moreover", "in conclusion", "it is important to note", "plays a crucial role", and similar). 0.8 or more cue phrases per sentence scores 1.0 (higher = more likely AI).

**Why that might differ between human and AI writing:** Generated prose leans on stock connectives. My casual human texts used almost none.

**What it can't see:** Anything outside a fixed phrase list. Formal human writing (reports, essays) uses these phrases too, and anyone can evade it by avoiding the list. In my tests it read exactly 0.0 on every human text and 1.0 on both AI samples, which says more about how formulaic my AI samples are than about real-world accuracy.

### The combining rule

**The rule:** A weighted average, with guards. "High-confidence AI" needs a very high combined score AND the signals agreeing (all signals at or above 0.6 with two signals; at least two of three with three signals). "High-confidence human" needs a low combined score AND every signal at or below 0.5. Text under 40 words can never be confident either way. Everything else is "unsure".

**The numbers:** Two signals: 0.6 model / 0.4 style. Three signals (used by `/submit`): 0.45 model / 0.30 style / 0.25 cue. AI: combined >= 0.85. Human: combined <= 0.30. Agreement bars: 0.6 (AI) and 0.5 (human). Minimum 40 words. All of these are in `config.py`.

**How the three signals are weighted (stretch note):** The model signal keeps the largest weight (0.45) because it is the only one that reads the text through a language model. The style signal gets 0.30 because it was the weakest separator in my tests (it never exceeded about 0.47). The cue signal gets 0.25 because it is the easiest to evade and reads only 0 or 1 on my samples, so I did not let it dominate. I chose these before running the three-signal test and did not tune them afterwards.

**Where it lives:** `scoring.py::combine_signals` (numbers in `config.py`)

**A case where my signals split, and what my rule does with it:** My clearly-AI sample scored model 0.7544 but style 0.459, so it lands in "unsure". The reverse split also happens: `human_b` scored model 0.5227 and style 0.0009 (combined 0.31). The style signal read it as very human, but the model signal sat above 0.5, so the agreement guard keeps it out of "human". This is deliberate: when signals disagree the rule says "unsure", because a wrong accusation costs a writer more than a missed detection costs the site.

**What the third signal changed (9 test texts, three signals):**

| Text | Words | Model | Style | Cue | Combined | Label |
|---|---|---|---|---|---|---|
| ai_try | 58 | 0.7533 | 0.4365 | 1.0 | 0.7199 | unsure |
| ai_a | 53 | 0.7368 | 0.345 | 1.0 | 0.6851 | unsure |
| human_try | 77 | 0.351 | 0.2563 | 0.0 | 0.2348 | human |
| human_a | 57 | 0.4999 | 0.0075 | 0.0 | 0.2272 | human |
| human_b | 53 | 0.5227 | 0.0009 | 0.0 | 0.31 | unsure |
| human_c | 54 | 0.4989 | 0.0566 | 0.0 | 0.2415 | human |
| human_d | 82 | 0.6557 | 0.3353 | 0.0 | 0.3957 | unsure |
| human_e | 81 | 0.7128 | 0.4712 | 0.0 | 0.4621 | unsure |
| human_f | 80 | 0.5997 | 0.4622 | 0.0 | 0.4085 | unsure |

With two signals only "unsure" was ever produced, and plain human texts scored 0.53-0.62 combined (`human_e` 0.6162). With the cue signal, plain human texts dropped by 0.13-0.15 (`human_e` to 0.4621) and the human label became reachable.

**Results against my criteria (honest status):**
- **Label coverage (criterion 3): partly met.** The human and unsure labels are reachable. The AI label has not been produced: my best AI sample reached 0.7199 against the 0.85 bar, because the style signal stays under about 0.47. I did not lower the threshold to force it.
- **False positives (criterion 1): no false positives observed.** None of the human texts I tested was labeled AI: 9 human texts with two signals, 7 of them rerun with three signals. Caveat: in the first test `plain_human` (27 words) scored 0.9024 model and 0.7838 style and was held back only by the 40-word guard, not the 0.85 bar.
- **Score spread (criterion 2): met on means, but not cleanly separated.** The mean of the two AI samples (about 0.70) is about 0.38 above the mean of the seven human texts (about 0.33), which meets the 0.3 target. But the lowest AI sample (0.685) is only about 0.22 above the highest human sample (0.462), and the result depends on how formulaic my AI samples are.
- **Bad input (criterion 4): partly met.** Missing, empty and too-short text return a 400 and write no log entry. The 10000-character limit is not enforced in `app.py` yet.
- **Appeal path (criterion 5): met.** A valid appeal returned 200 and wrote an `under_review` entry to the log. An unknown `content_id` returned 404 and missing reasoning returned 400.

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

**A submission** (the first run, before the stretch features)

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
      "content_id": "c_84d5f338a110",
      "creator_id": "u4",
      "event": "appeal",
      "reasoning": "I wrote this myself for my class.",
      "status": "under_review",
      "timestamp": "2026-11-02T06:08:51+00:00"
    },
    {
      "creator_id": "u5",
      "event": "verification",
      "method": "code",
      "status": "verified_human",
      "timestamp": "2026-11-02T06:34:55+00:00"
    },
    {
      "combined_score": 0.2413,
      "content_id": "c_0cf0d28393bf",
      "creator_id": "u5",
      "cue_score": 0.0,
      "guess": "human",
      "label": "We think this was most likely written by a person.",
      "model_score": 0.3934,
      "status": "decided",
      "style_score": 0.2143,
      "timestamp": "2026-11-02T06:35:09+00:00",
      "verified_human": true
    }
  ]
}
```

These are the three newest entries: the appeal on `c_84d5f338a110` (the item submitted earlier), the `u5` verification, and the decision on `c_0cf0d28393bf`, which carries `verified_human: true`.

---

## Stretch: what each feature changed

### Third signal (`cues.py`)

It changed which labels are reachable: the human label now appears (three of my human texts reached it) and plain human writing scores lower. The weighting note and the nine-text table are under Signals and Scoring above. A real submission through the service now returns `cue_score`:

```json
{
  "combined_score": 0.2413,
  "confidence": 0.5174,
  "content_id": "c_0cf0d28393bf",
  "cue_score": 0.0,
  "guess": "human",
  "label": "We think this was most likely written by a person.",
  "model_score": 0.3934,
  "style_score": 0.2143,
  "verified_human": true
}
```

### `GET /content/<id>`

It returns one item's current status from the append-only log: the latest status, the original guess and label, and whether it was appealed.

```bash
$ curl.exe http://127.0.0.1:5000/content/c_0cf0d28393bf
```

```json
{
  "appealed": false,
  "combined_score": 0.2413,
  "content_id": "c_0cf0d28393bf",
  "creator_id": "u5",
  "guess": "human",
  "label": "We think this was most likely written by a person.",
  "status": "decided",
  "verified_human": true
}
```

### Verified-human path (`POST /verify`)

The extra step is presenting a verification code (a stand-in for a real out-of-band check such as an emailed code or ID check). A wrong code is refused with a 403 and writes nothing. A correct code writes a `verification` entry, and every later submission from that `creator_id` carries `verified_human: true`, shown in the `/submit` and `/content/<id>` responses above and in the log. The credential is displayed only: it never changes the score or label.

```bash
$ curl.exe -X POST http://127.0.0.1:5000/verify -H "Content-Type: application/json" -d '{"creator_id": "u5", "code": "wrong"}'
```

```json
{
  "message": "That verification code is not valid."
}
```

(This is the refused response with status 403; the `error` field scrolled off in my terminal.)

```bash
$ curl.exe -X POST http://127.0.0.1:5000/verify -H "Content-Type: application/json" -d '{"creator_id": "u5", "code": "writer-pledge-2026"}'
```

```json
{
  "creator_id": "u5",
  "message": "Verified. Work you submit from now on will show a verified-human credential.",
  "status": "verified_human"
}
```

The `verification` entry it wrote is the middle entry in the log block above, and the `c_0cf0d28393bf` decision after it carries `verified_human: true`.

---

## How I Used AI

**Moment 1**

- *What I asked for:* Help writing my Milestone 1 notes (path, signals, false-positive trace, endpoint shapes).
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
