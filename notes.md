# Milestone 1 notes

## 1. The path a submission takes
1. **Request arrives** at POST /submit with JSON `text` and `creator_id`. Adds: the raw input.
2. **Validation.** Checks that `text` is a non-empty string. `creator_id` is optional and defaults to "unknown". Adds: a 400 `bad_request` if text is missing or empty, otherwise a go-ahead.
3. **Signal 1** (detector.py, gpt2 running locally). Adds: `model_score` between 0 and 1. Text too short to score (under 3 tokens) returns a 400, and a model that can't load returns a 503.
4. **content_id created** (`c_` plus 12 hex characters from a uuid). Adds: the unique ID the appeal endpoint will use later.
5. **Signal 2** (stylometry.py, measures the text as text). Adds: `style_score` between 0 and 1. Not built yet (null for now).
6. **Combine** (scoring.py::combine_signals, weights in config.py). Adds: one confidence score and a guess (ai, human, or unsure). Not built yet.
7. **Label** (scoring.py::score_to_label). Adds: the plain-English sentence the reader sees. Not built yet.
8. **Log, then respond.** Writes content_id, creator_id, timestamp, model_score, style_score, combined_score, guess, label and status "decided" to logs/audit.jsonl, then returns JSON.

## 2. The two signals

### Signal 1: detector.py (gpt2, local)
- **Measures:** perplexity, meaning how predictable the text is to a language model. Low perplexity maps to a high AI score (0-1, higher = more likely AI).
- **Why it might differ:** a model writes by picking likely next words, so AI text tends to be easy for a model to predict. Human writing wanders more, with odd word choices and abrupt turns.
- **Blind spot:** predictability is not authorship. Plain writing with common words in short sentences scores machine-like, so non-native English writers, younger writers and anyone writing simply get flagged. The reverse also happens: ornate prose with rare words scores human, so AI text that uses rare words can slip through. It is structural, not a bug I can fix.

### Signal 2: stylometry.py (my build)
- **Measures:** surface statistics of the text: sentence-length spread, unique-word ratio, and punctuation density, combined into one score from 0 to 1 (higher = more AI-like, same direction as signal 1).
- **Why it might differ:** AI text often has more even sentence lengths and steady punctuation, while humans vary more in rhythm and vocabulary.
- **Blind spot:** it can't read meaning at all. A human who writes short, uniform sentences looks "AI-like", and AI text with varied sentences looks human. It is also unreliable on very short text, where the statistics are noisy.

## 3. The false-positive trace
A second-language writer submits their own plainly written paragraph, short sentences and everyday words. Signal 1 gives e.g. 0.8 because the text is very predictable, and signal 2 also reads the even, simple sentences as AI-like, giving e.g. 0.7. Combined is about 0.75, which lands in the high-confidence AI range, so they see a label saying it was probably AI-generated. They can submit an appeal, which sets the status to under_review and logs it. This is the person with the least room to argue back, which is why the AI threshold must be high and signal disagreement should lean toward "unsure". These scores are illustrative. I will test the claim that stylometry also flags plain writing by running a plainly written human paragraph in Milestone 4.

## 4. Endpoint shapes

### POST /submit
- **In:** `{"text": string, "creator_id": string (optional, defaults to "unknown")}`
- **Out (200):** `{"content_id": string, "guess": "ai" | "human" | "unsure", "confidence": number 0-1, "label": string, "model_score": number 0-1, "style_score": number 0-1 or null}`
- **Out (400):** `{"error": "bad_request", "message": string}` for missing or empty text, or text too short to score (detector.py raises ValueError under 3 tokens). No log entry is written for rejected input.
- **Out (503):** `{"error": "detector_unavailable", "message": string}` if the detector model can't be loaded (detector.py raises DetectorUnavailable).

### POST /appeal
- **In:** `{"content_id": string, "reasoning": string}`
- **Out (200):** `{"content_id": string, "status": "under_review", "message": string}`
- **Out (404):** `{"error": string}` if the content_id doesn't exist.
- **Out (400):** `{"error": string}` if reasoning or content_id is missing.

## 5. Combining rule

**Rule (in words):** The combined score is a weighted average of the two signals, with the model signal counting more than the style signal. A submission is only called "high-confidence AI" if the combined score is very high AND both signals independently lean AI. It is only called "high-confidence human" if the combined score is low AND both signals lean human. Everything else is "unsure". If the text is too short for the statistics to mean much, the result can never be high-confidence in either direction.

**Numbers (these go in config.py):**
- Weights: 0.6 model signal, 0.4 style signal
- High-confidence AI: combined >= 0.85 and both signals >= 0.6
- High-confidence human: combined <= 0.30 and both signals <= 0.5
- Unsure: everything else
- Short-text guard: under 40 words, force "unsure"

**Why:** In my test, a plainly written human paragraph scored 0.9024 on the model signal and 0.7838 on the style signal, higher than my clearly-AI text. Both signals agreed on the wrong answer, so averaging alone can't protect that writer. A wrongly accused writer costs far more than a missed AI text (criterion 1), so I accept that some AI text will land in "unsure" rather than risk accusing plain writers. The short-text guard exists because that test paragraph was only 27 words, and the statistics are noisy at that length.

**Known weakness:** Plain human writing that is longer than 40 words can still score above 0.85 on both signals and be accused. The guard only helps short text. I will test a longer plain paragraph to find out how big this problem is.

## Attack verdict rules
- Evasion: BROKE if labeled ___. "unsure" counts as ___ because ___.
- False positive: BROKE if labeled ___. "unsure" counts as ___ because ___.
- Prompt injection: BROKE if ___.
- Malformed: BROKE if 5xx/crash. A 200 with a decision on junk counts as ___ because ___.
- Flood: HELD if 429s began at my limit.