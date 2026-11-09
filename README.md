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
2. Validation: `text` must be a non-empty string, otherwise the service returns a 400 `bad_request`. Rejected input writes no log entry. *(Changed in Unit 8: rejections are now logged with `audit.log_rejection`.)*
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

**Moment 3 (Unit 8)**

- *What I asked for:* Step-by-step help running Unit 8 (Windows commands, the attack run, scenarios, the appeal test script) and help writing up my results.
- *What came back:* Commands and scripts, multiple-choice options for each verdict rule and diagnosis (the method the assignment suggests: possible causes at different stages), and README formatting and wording built from my choices.
- *What I changed or decided myself:* I chose my own verdict rules and picked each cause from the evidence, and decided which malformed inputs count as writing. I wrote my own test pieces and left out my LinkedIn About section because I'd written it with AI help, so it wasn't valid human writing for criterion 1.

---

<!-- ═══════════════════════ UNIT 8 — THE TEST (to be filled next unit) ═══════════════════════ -->

## Rate Limiting

Limits: **10 per minute, 200 per day**, per `creator_id` (falls back to IP address when there's no usable creator_id). Set in `config.py`, applied with `@limiter.limit(...)` on `app.py::submit`.

- **10/minute:** a real writer submits a piece, maybe fixes a typo and resubmits, so a few requests a minute at most. 10 never gets in their way.
- **200/day:** a script trying to learn my thresholds needs hundreds or thousands of variations. 200 a day cuts it off long before it can map where my labels change.
- **Known weakness:** counts live in memory (`memory://`), so a server restart resets every count, and two copies of the service wouldn't share limits.

Flood test (`python run_attacks.py --flood 15`, saved in `results/flood_2026-11-04_1934.md`):

```
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

## Attack Run — Before

Full results: `results/attack_run_2026-11-07_2058_before.md` (56 attacks, 1 auto-marked BROKE).

**My verdict rules:**
- **Evasion:** BROKE only if labeled human. "Unsure" = HELD because my unsure label says "we couldn't tell", so it does not vouch for the text and the attacker did not get passed as human.
- **False positive:** BROKE only if labeled AI. "Unsure" = HELD because my unsure label says "we're not drawing any conclusion about you or your work", so no writer is accused. I count "unsure" the same way in both families: a neutral outcome where neither side wins.
- **Prompt injection:** BROKE only if I can show the instruction caused the result, because my signals measure predictability and text statistics and do not follow instructions, so a result that happens to match is not proof.
- **Malformed:** BROKE if a 5xx, or a 200 verdict on input that isn't writing, because a score on junk is meaningless and gets logged as a real decision. The right answer is a 400.
- **Flood:** HELD if 429s started at my limit.

| Family | Attacks | Held | Broke | Which broke |
|---|---|---|---|---|
| evasion | 10 | 9 | 1 | EV05 (labeled human) |
| false_positive | 8 | 8 | 0 | none |
| prompt_injection | 6 | 6 | 0 | none proven (PI02 labeled human, cause untested) |
| malformed | 20 | 16 | 4 | RQ07 (500 crash), MF03, MF04, MF06 (control characters, punctuation, emoji scored as writing) |
| flood_same_creator | 12 | 12 | 0 | none: requests 11 and 12 got 429 at my limit of 10 |
| **Total** | **56** | **51** | **5** | |

MF05, MF07 and MF08 are real text, so they're HELD under my malformed rule. MF08 (60,000 characters) is over my own 10,000-character limit, so it counts against criterion 4 instead.

**Worst outcome:** EV05. It was AI text after a heavy human editing pass, and my service told readers it was "most likely written by a person." That's the one label that vouches for a text, and it was wrong.

**Not tested:** I didn't re-run PI02 with the instruction removed, so I can't show whether the instruction caused its "human" label.

### Audit log extract (10 entries, including one 429 rejection)

Pulled from `results/audit_extract.json` into `results/readme_log_entries.json`.

```json
[
    {
        "combined_score":  0.2267,
        "content_id":  "c_f11752ba947c",
        "creator_id":  "attacker_EV05",
        "cue_score":  0.0,
        "guess":  "human",
        "label":  "We think this was most likely written by a person.",
        "model_score":  0.3212,
        "status":  "decided",
        "style_score":  0.2738,
        "timestamp":  "2026-11-08T02:58:22+00:00",
        "verified_human":  false
    },
    {
        "combined_score":  0.7018,
        "content_id":  "c_16033342a0f3",
        "creator_id":  "attacker_EV10",
        "cue_score":  0.0,
        "guess":  "unsure",
        "label":  "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
        "model_score":  0.9792,
        "status":  "decided",
        "style_score":  0.8707,
        "timestamp":  "2026-11-08T02:58:24+00:00",
        "verified_human":  false
    },
    {
        "combined_score":  0.573,
        "content_id":  "c_63db83c3081c",
        "creator_id":  "attacker_FP03",
        "cue_score":  0.0,
        "guess":  "unsure",
        "label":  "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
        "model_score":  0.8051,
        "status":  "decided",
        "style_score":  0.7023,
        "timestamp":  "2026-11-08T02:58:25+00:00",
        "verified_human":  false
    },
    {
        "combined_score":  0.5935,
        "content_id":  "c_c98291a18727",
        "creator_id":  "attacker_FP07",
        "cue_score":  0.0,
        "guess":  "unsure",
        "label":  "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
        "model_score":  0.8816,
        "status":  "decided",
        "style_score":  0.6558,
        "timestamp":  "2026-11-08T02:58:26+00:00",
        "verified_human":  false
    },
    {
        "combined_score":  0.1896,
        "content_id":  "c_1369bbb817e2",
        "creator_id":  "attacker_PI02",
        "cue_score":  0.0,
        "guess":  "human",
        "label":  "We think this was most likely written by a person.",
        "model_score":  0.2044,
        "status":  "decided",
        "style_score":  0.3253,
        "timestamp":  "2026-11-08T02:58:26+00:00",
        "verified_human":  false
    },
    {
        "combined_score":  0.3338,
        "content_id":  "c_3d0037c0a81b",
        "creator_id":  "attacker_PI05",
        "cue_score":  0.0,
        "guess":  "unsure",
        "label":  "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
        "model_score":  0.6401,
        "status":  "decided",
        "style_score":  0.1524,
        "timestamp":  "2026-11-08T02:58:27+00:00",
        "verified_human":  false
    },
    {
        "combined_score":  0.31,
        "content_id":  "c_8fb7a66409a9",
        "creator_id":  "attacker_MF03",
        "cue_score":  0.0,
        "guess":  "unsure",
        "label":  "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
        "model_score":  0.0,
        "status":  "decided",
        "style_score":  0.6667,
        "timestamp":  "2026-11-08T02:58:27+00:00",
        "verified_human":  false
    },
    {
        "combined_score":  0.7486,
        "content_id":  "c_e67ef18e160b",
        "creator_id":  "attacker_MF06",
        "cue_score":  0.0,
        "guess":  "unsure",
        "label":  "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
        "model_score":  0.9969,
        "status":  "decided",
        "style_score":  1.0,
        "timestamp":  "2026-11-08T02:58:29+00:00",
        "verified_human":  false
    },
    {
        "combined_score":  0.6416,
        "content_id":  "c_c5686f8b3fe6",
        "creator_id":  "attacker_MF08",
        "cue_score":  0.0,
        "guess":  "unsure",
        "label":  "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
        "model_score":  0.9876,
        "status":  "decided",
        "style_score":  0.6574,
        "timestamp":  "2026-11-08T02:58:31+00:00",
        "verified_human":  false
    },
    {
        "creator_id":  "attacker_flood",
        "event":  "rejected",
        "limit":  "10 per 1 minute",
        "reason":  "rate_limited",
        "status":  "rejected",
        "timestamp":  "2026-11-08T02:58:32+00:00"
    }
]
```

RQ07 (body is a JSON array) crashed with a 500 and is **absent from the log**. The crash happened before any logging code ran, so this attack left no trace. In the log it looks the same as a request that never happened.

## Run Log and Verdicts

- Criteria 1 and 4: `run_eval.py --label before` → `results/run_2026-11-09_0012_before.md`
- Criteria 2 and 3: `python try_labels.py` (3 runs) and `scoring.label_ranges()`
- Criterion 5: tested by hand with a PowerShell script (submit, then appeal, 3 trials)

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. My writing labeled AI | ≤ 1 of 10 | 0/9 | 0/9 | 0/9 | MET (on 9 pieces) |
| 2. Score spread (mean AI − mean human) | ≥ 0.30 | 0.445 | 0.445 | 0.445 | MET |
| 3. All three labels reachable | 3 of 3 | 2/3 (no "ai") | 2/3 | 2/3 | MISSED |
| 4. Bad input → 400, no log entry | 3 of 3 | 2/3 | 2/3 | 2/3 | MISSED |
| 5. Appeals → under_review, unknown → 404 | 5/5 + 404 | 5/5 + 404 | 5/5 + 404 | 5/5 + 404 | MET |

**Notes:**
- **Criterion 1:** tested 9 of my own pieces, not 10 (ran out of time). All 9 came back "unsure" in every trial.
- **Criterion 2:** AI mean 0.7025 (ai_try 0.7199, ai_a 0.6851); human mean 0.2573 (human_try 0.2348, human_a 0.2272, human_b 0.31). Identical in all 3 runs. My criterion says 3 AI samples, but `try_labels.py` has only 2.
- **Criterion 3:** `label_ranges()` = human 0.00–0.30, unsure 0.30–0.85, AI 0.85–1.00, so there are no gaps. But no real submission reached "ai". The highest combined score anywhere was 0.7486, from MF06 (emoji only). The highest from real AI-style text was EV10 at 0.7018, even with model 0.9792 and style 0.8707.
- **Criterion 4:** missing and empty text → 400. The 10,005-character text → 200, scored "unsure".
- **Criterion 5:** `Trial 1/2/3 : 5/5 under_review, unknown id -> 404`.

### Diagnoses (stage + mechanism)

- **Criterion 3:** Stage: the combining rule. Mechanism: the three-signal weights are 0.45 model + 0.30 style + 0.25 cue. When a text has no cue phrases (cue = 0), the highest possible combined score is 0.45 + 0.30 = 0.75, below the 0.85 AI threshold. EV10 had model 0.9792 and style 0.8707 but cue 0, so it scored 0.7018 and stayed "unsure". The AI label can only be reached by text that also uses my fixed list of transition phrases.
- **Criterion 4:** Stage: the route. Mechanism: `submit()` checks that `text` is a non-empty string but never checks its length, so the 10,005-character text went straight to the signals and was scored. Also, my criterion says "no log entry", but Milestone 1 of Unit 8 required me to log rejections with `audit.log_rejection`, so that half of the criterion now conflicts with a required feature. Missing and empty text return 400 but now write a rejection entry.
- **RQ07 crash:** Stage: the route. Mechanism: the first line of `submit()` is `payload = request.get_json(silent=True) or {}`. A JSON array parses fine and a non-empty list is truthy, so `or {}` doesn't replace it. The next line calls `payload.get("text")` on a list, which raises `AttributeError` and returns a 500.
- **EV05 and PI02 labeled human:** Stage: the combining rule. Mechanism: neither text used cue phrases, so cue = 0 at weight 0.25 counts as evidence of "human" and pulls the combined score down. EV05: 0.45×0.3212 + 0.30×0.2738 + 0.25×0 = 0.2267 (human). With my old two-signal weights (0.6/0.4) it would have scored 0.302, which is "unsure". PI02 (model 0.2044, style 0.3253) scores about 0.25 under either weighting, so for PI02 the low signal scores themselves are also part of the cause.
- **Pattern across misses:** two root causes, not five separate failures. (1) **The route doesn't validate input:** RQ07's crash, criterion 4's long text, and junk inputs getting scored. (2) **A cue score of 0 at weight 0.25 distorts the combining rule:** it caps every cue-free text at 0.75, so "ai" is unreachable (criterion 3), and it drags borderline AI text down into "human" (EV05).

## The Improvement

**What I changed (one change):** input validation at the start of `app.py::submit()`. The body must be a JSON object, and `text` must be 10,000 characters or fewer. Rejections return 400 and are logged.

**Why:** my diagnosis put RQ07's crash and criterion 4's miss in the route. Neither was a signal problem; the route passed input to the signals that it should have refused.

### Before vs after

| | Before | After |
|---|---|---|
| RQ07 (JSON array body) | 500 crash, not logged | 400, logged as `body_not_object` |
| MF08 (60,000 chars) | 200, scored | 400, logged as `text_too_long` |
| Criterion 4 (bad input) | 2/3, 2/3, 2/3 | 3/3, 3/3, 3/3 return 400 (but each now writes a rejection entry) |
| Attacks broke (evasion / FP / injection / malformed / flood) | 1 / 0 / 0 / 4 / 0 | 1 / 0 / 0 / 3 / 0 (auto-marked BROKE: 1 → 0) |
| Criterion 1 (my writing labeled AI) | 0/9, 0/9, 0/9 | 0/9, 0/9, 0/9 (unchanged) |
| Criteria 2, 3, 5 | MET / MISSED / MET | not re-run: the fix only touches the route, and these don't depend on it (`try_labels.py` calls the scoring code directly) |

Full results: `results/attack_run_2026-11-09_0107_after.md` and `results/run_2026-11-09_0108_after.md`.

**Did it help?** Yes, for what it targeted: the crash is gone (RQ07 now gets a clean 400 and is logged instead of leaving no trace), and all three bad inputs in criterion 4 now return 400. It didn't change any signal or label, so evasion, false positives and injection came out exactly the same. Criterion 4 is still MISSED on its "no log entry" part, because rejections are logged by design in Unit 8.

**What it didn't fix:** emoji, control characters and right-to-left text are under 10,000 characters and are still JSON objects, so they still get scored. "ai" is still unreachable. Criterion 4's "no log entry" part still conflicts with logging rejections.

## What's Still Broken

- **"ai" label unreachable (criterion 3):** I'd change how the cue signal combines, for example falling back to the two-signal weights when cue = 0 instead of counting 0 as human evidence. I stopped because that's a second change to the scoring, and it could push real writers toward the AI label, so it needs its own before/after measurement.
- **EV05 labeled human:** the same fix would have moved it to "unsure" (0.302 under two-signal weights). Not done for the same reason.
- **PI02 labeled human:** I'd re-run it with the instruction removed to show whether the instruction caused the label. I ran out of time.
- **Junk input still scored (emoji, control characters, punctuation):** I'd reject text with too few real words, before the signals see it. Not done, to keep to one change.
- **Criterion 4's "no log entry":** this conflicts with the Unit 8 requirement to log rejections. I'd revise the criterion to "returns 400 and logs a rejection, never a decision", but it was written before the requirement existed.
- **Criterion 1 tested 9 of 10 pieces:** I ran out of time.

**The trade I'd make in production:** I'd lean toward fewer wrong accusations and keep the wide unsure band, because a wrong accusation costs a real writer far more than a missed detection costs the site. The cost of that choice falls on the site and its readers, who will sometimes see AI text labeled "unsure" or even "human", like EV05.
