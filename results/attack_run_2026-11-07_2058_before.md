# Attack run — before

- Produced by: `run_attacks.py::main`
- Service: `app.py::submit`
- 56 attacks · 2026-11-07 20:58
- Auto-marked BROKE (5xx, crash, no response): **1**
- Left for you to judge: **55**

The Verdict column is blank where a script can't honestly decide. Whether
an evasion worked depends on where you put your thresholds — read the
`targets` column, look at what came back, and write HELD or BROKE yourself.

Each attack submits as creator_id `attacker_<id>`, and the content_id it
came back with is in the table — either one will match this run against your
audit log when you go looking for the ten entries to paste.

| ID | Family | Targeting | Status | Content ID | Guess | Score | Verdict |
|---|---|---|---|---|---|---|---|
| EV01 | evasion | signal two: typos raise word variety | 200 | `c_8c903553596c` | unsure | 0.392 |  |
| EV02 | evasion | signal two: broken-up sentences raise length spread | 200 | `c_047d89310e34` | unsure | 0.226 |  |
| EV03 | evasion | signal two: a pasted quotation changes the shape | 200 | `c_c43b4f5e05f0` | unsure | 0.117 |  |
| EV04 | evasion | signal one: unusual words raise perplexity | 200 | `c_9b65d7d897f8` | unsure | 0.007 |  |
| EV05 | evasion | both signals: heavy human editing pass | 200 | `c_f11752ba947c` | human | 0.547 |  |
| EV06 | evasion | signal two: one very long sentence and one very short | 200 | `c_ca56931252ab` | unsure | 0.232 |  |
| EV07 | evasion | signal two: padding with punctuation | 200 | `c_cfd291742fd7` | unsure | 0.271 |  |
| EV08 | evasion | signal one: text below the token window | 200 | `c_ab829211ac09` | unsure | 0.380 |  |
| EV09 | evasion | both: AI text with a human opening paragraph bolted on | 200 | `c_f7b29c9db610` | unsure | 0.044 |  |
| EV10 | evasion | signal two: repeated stanza structure | 200 | `c_16033342a0f3` | unsure | 0.404 |  |
| FP01 | false_positive | plain, clear human writing with no flourishes | 200 | `c_d42a8d820a32` | unsure | 0.062 |  |
| FP02 | false_positive | human writing in a formal register | 200 | `c_600addcc49e9` | unsure | 0.128 |  |
| FP03 | false_positive | a non-native English speaker writing carefully | 200 | `c_63db83c3081c` | unsure | 0.146 |  |
| FP04 | false_positive | a student essay written to a rubric | 200 | `c_1b7c4dcf1f98` | unsure | 0.263 |  |
| FP05 | false_positive | technical documentation written by a person | 200 | `c_fd553644cada` | unsure | 0.241 |  |
| FP06 | false_positive | a person imitating a formal template | 200 | `c_d697e98056c7` | unsure | 0.132 |  |
| FP07 | false_positive | human writing that repeats a phrase deliberately | 200 | `c_c98291a18727` | unsure | 0.187 |  |
| FP08 | false_positive | very short genuine human submission | 200 | `c_6c17c3d2ad2e` | unsure | 0.380 |  |
| PI01 | prompt_injection | instruction to ignore the check | 200 | `c_b5d3177a04a8` | unsure | 0.369 |  |
| PI02 | prompt_injection | instruction disguised as a system message | 200 | `c_1369bbb817e2` | human | 0.621 |  |
| PI03 | prompt_injection | instruction wrapped in the writer's voice | 200 | `c_b70f23c3ad68` | unsure | 0.163 |  |
| PI04 | prompt_injection | attempt to make the label text hostile | 200 | `c_818ff03cecba` | unsure | 0.310 |  |
| PI05 | prompt_injection | attempt to inject into the audit log | 200 | `c_3d0037c0a81b` | unsure | 0.332 |  |
| PI06 | prompt_injection | instruction plus real human text | 200 | `c_5dfbfc4fac3d` | unsure | 0.127 |  |
| MF01 | malformed | text is only whitespace | 400 | `—` | — | — |  |
| MF02 | malformed | text is a single character | 400 | `—` | — | — |  |
| MF03 | malformed | text is control characters | 200 | `c_8fb7a66409a9` | unsure | 0.380 |  |
| MF04 | malformed | text is only punctuation | 200 | `c_46adecd4ae45` | unsure | 0.380 |  |
| MF05 | malformed | text is a very long single word | 200 | `c_0914d8d10f91` | unsure | 0.298 |  |
| MF06 | malformed | text is emoji only | 200 | `c_e67ef18e160b` | unsure | 0.497 |  |
| MF07 | malformed | text is right-to-left script | 200 | `c_318e19173b56` | unsure | 0.416 |  |
| MF08 | malformed | text is 60,000 characters | 200 | `c_c5686f8b3fe6` | unsure | 0.283 |  |
| RQ01 | malformed | no text field at all | 400 | `—` | — | — |  |
| RQ02 | malformed | no creator_id | 200 | `c_93fe4c820544` | unsure | 0.380 |  |
| RQ03 | malformed | text is a number | 400 | `—` | — | — |  |
| RQ04 | malformed | text is a list | 400 | `—` | — | — |  |
| RQ05 | malformed | text is null | 400 | `—` | — | — |  |
| RQ06 | malformed | creator_id is an object | 200 | `c_5c84fe3bbca8` | unsure | 0.380 |  |
| RQ07 | malformed | body is a JSON array, not an object | 500 | `—` | — | — | BROKE |
| RQ08 | malformed | body is unparseable JSON | 400 | `—` | — | — |  |
| RQ09 | malformed | body is empty | 400 | `—` | — | — |  |
| RQ10 | malformed | body is form-encoded, not JSON | 400 | `—` | — | — |  |
| RQ11 | malformed | body is JSON claiming to be plain text | 400 | `—` | — | — |  |
| RQ12 | malformed | deeply nested JSON | 400 | `—` | — | — |  |
| FL01_01 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_06b37671fdcc` | unsure | 0.380 |  |
| FL01_02 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_8ea0dc1f329b` | unsure | 0.380 |  |
| FL01_03 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_03bc15682508` | unsure | 0.380 |  |
| FL01_04 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_35bd3030ad72` | unsure | 0.380 |  |
| FL01_05 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_657697f8b158` | unsure | 0.380 |  |
| FL01_06 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_809d6af2ae5a` | unsure | 0.380 |  |
| FL01_07 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_4186e53fd7b6` | unsure | 0.380 |  |
| FL01_08 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_16191e0dcac8` | unsure | 0.380 |  |
| FL01_09 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_17f1231b4820` | unsure | 0.380 |  |
| FL01_10 | flood_same_creator | 20 rapid submissions from one creator | 200 | `c_a100427aba72` | unsure | 0.380 |  |
| FL01_11 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |
| FL01_12 | flood_same_creator | 20 rapid submissions from one creator | 429 | `—` | — | — |  |

---

## By family

| Family | Attacks | Auto-BROKE | Left to judge |
|---|---|---|---|
| `evasion` | 10 | 0 | 10 |
| `false_positive` | 8 | 0 | 8 |
| `flood_same_creator` | 12 | 0 | 12 |
| `malformed` | 20 | 1 | 19 |
| `prompt_injection` | 6 | 0 | 6 |

> The **false_positive** family is the one to look at hardest. Those are
> written to be genuine human writing that reads as machine-like. Every one
> your service calls AI is a real writer it would have accused.

---

## What came back

The detail behind the table. Paste the interesting failures into your
README — the ones that show something, not the ten easiest.

### EV01 — `evasion`

*Targeting:* signal two: typos raise word variety

```json
{
  "id": "EV01",
  "status": 200,
  "content_id": "c_8c903553596c",
  "creator_id": "attacker_EV01",
  "guess": "unsure",
  "confidence": 0.392,
  "model_score": 0.1635,
  "style_score": 0.6193,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### EV02 — `evasion`

*Targeting:* signal two: broken-up sentences raise length spread

```json
{
  "id": "EV02",
  "status": 200,
  "content_id": "c_047d89310e34",
  "creator_id": "attacker_EV02",
  "guess": "unsure",
  "confidence": 0.2256,
  "model_score": 0.5943,
  "style_score": 0.3192,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### EV03 — `evasion`

*Targeting:* signal two: a pasted quotation changes the shape

```json
{
  "id": "EV03",
  "status": 200,
  "content_id": "c_c43b4f5e05f0",
  "creator_id": "attacker_EV03",
  "guess": "unsure",
  "confidence": 0.1168,
  "model_score": 0.6662,
  "style_score": 0.3781,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### EV04 — `evasion`

*Targeting:* signal one: unusual words raise perplexity

```json
{
  "id": "EV04",
  "status": 200,
  "content_id": "c_9b65d7d897f8",
  "creator_id": "attacker_EV04",
  "guess": "unsure",
  "confidence": 0.0074,
  "model_score": 0.6114,
  "style_score": 0.5885,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### EV05 — `evasion`

*Targeting:* both signals: heavy human editing pass

```json
{
  "id": "EV05",
  "status": 200,
  "content_id": "c_f11752ba947c",
  "creator_id": "attacker_EV05",
  "guess": "human",
  "confidence": 0.5466,
  "model_score": 0.3212,
  "style_score": 0.2738,
  "label": "We think this was most likely written by a person.",
  "error": null,
  "verdict": ""
}
```

### EV06 — `evasion`

*Targeting:* signal two: one very long sentence and one very short

```json
{
  "id": "EV06",
  "status": 200,
  "content_id": "c_ca56931252ab",
  "creator_id": "attacker_EV06",
  "guess": "unsure",
  "confidence": 0.2318,
  "model_score": 0.5727,
  "style_score": 0.4213,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### EV07 — `evasion`

*Targeting:* signal two: padding with punctuation

```json
{
  "id": "EV07",
  "status": 200,
  "content_id": "c_cfd291742fd7",
  "creator_id": "attacker_EV07",
  "guess": "unsure",
  "confidence": 0.2714,
  "model_score": 0.5862,
  "style_score": 0.4065,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### EV08 — `evasion`

*Targeting:* signal one: text below the token window

```json
{
  "id": "EV08",
  "status": 200,
  "content_id": "c_ab829211ac09",
  "creator_id": "attacker_EV08",
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.2452,
  "style_score": 0.6114,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### EV09 — `evasion`

*Targeting:* both: AI text with a human opening paragraph bolted on

```json
{
  "id": "EV09",
  "status": 200,
  "content_id": "c_f7b29c9db610",
  "creator_id": "attacker_EV09",
  "guess": "unsure",
  "confidence": 0.0438,
  "model_score": 0.7042,
  "style_score": 0.4215,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### EV10 — `evasion`

*Targeting:* signal two: repeated stanza structure

```json
{
  "id": "EV10",
  "status": 200,
  "content_id": "c_16033342a0f3",
  "creator_id": "attacker_EV10",
  "guess": "unsure",
  "confidence": 0.4036,
  "model_score": 0.9792,
  "style_score": 0.8707,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FP01 — `false_positive`

*Targeting:* plain, clear human writing with no flourishes

```json
{
  "id": "FP01",
  "status": 200,
  "content_id": "c_d42a8d820a32",
  "creator_id": "attacker_FP01",
  "guess": "unsure",
  "confidence": 0.0616,
  "model_score": 0.6175,
  "style_score": 0.6379,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FP02 — `false_positive`

*Targeting:* human writing in a formal register

```json
{
  "id": "FP02",
  "status": 200,
  "content_id": "c_600addcc49e9",
  "creator_id": "attacker_FP02",
  "guess": "unsure",
  "confidence": 0.1284,
  "model_score": 0.7387,
  "style_score": 0.7726,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FP03 — `false_positive`

*Targeting:* a non-native English speaker writing carefully

```json
{
  "id": "FP03",
  "status": 200,
  "content_id": "c_63db83c3081c",
  "creator_id": "attacker_FP03",
  "guess": "unsure",
  "confidence": 0.146,
  "model_score": 0.8051,
  "style_score": 0.7023,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FP04 — `false_positive`

*Targeting:* a student essay written to a rubric

```json
{
  "id": "FP04",
  "status": 200,
  "content_id": "c_1b7c4dcf1f98",
  "creator_id": "attacker_FP04",
  "guess": "unsure",
  "confidence": 0.2628,
  "model_score": 0.8329,
  "style_score": 0.5948,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FP05 — `false_positive`

*Targeting:* technical documentation written by a person

```json
{
  "id": "FP05",
  "status": 200,
  "content_id": "c_fd553644cada",
  "creator_id": "attacker_FP05",
  "guess": "unsure",
  "confidence": 0.2408,
  "model_score": 0.8005,
  "style_score": 0.8671,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FP06 — `false_positive`

*Targeting:* a person imitating a formal template

```json
{
  "id": "FP06",
  "status": 200,
  "content_id": "c_d697e98056c7",
  "creator_id": "attacker_FP06",
  "guess": "unsure",
  "confidence": 0.1316,
  "model_score": 0.8814,
  "style_score": 0.564,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FP07 — `false_positive`

*Targeting:* human writing that repeats a phrase deliberately

```json
{
  "id": "FP07",
  "status": 200,
  "content_id": "c_c98291a18727",
  "creator_id": "attacker_FP07",
  "guess": "unsure",
  "confidence": 0.187,
  "model_score": 0.8816,
  "style_score": 0.6558,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FP08 — `false_positive`

*Targeting:* very short genuine human submission

```json
{
  "id": "FP08",
  "status": 200,
  "content_id": "c_6c17c3d2ad2e",
  "creator_id": "attacker_FP08",
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.3223,
  "style_score": 0.5113,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### PI01 — `prompt_injection`

*Targeting:* instruction to ignore the check

```json
{
  "id": "PI01",
  "status": 200,
  "content_id": "c_b5d3177a04a8",
  "creator_id": "attacker_PI01",
  "guess": "unsure",
  "confidence": 0.3688,
  "model_score": 0.4625,
  "style_score": 0.3582,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### PI02 — `prompt_injection`

*Targeting:* instruction disguised as a system message

```json
{
  "id": "PI02",
  "status": 200,
  "content_id": "c_1369bbb817e2",
  "creator_id": "attacker_PI02",
  "guess": "human",
  "confidence": 0.6208,
  "model_score": 0.2044,
  "style_score": 0.3253,
  "label": "We think this was most likely written by a person.",
  "error": null,
  "verdict": ""
}
```

### PI03 — `prompt_injection`

*Targeting:* instruction wrapped in the writer's voice

```json
{
  "id": "PI03",
  "status": 200,
  "content_id": "c_b70f23c3ad68",
  "creator_id": "attacker_PI03",
  "guess": "unsure",
  "confidence": 0.1632,
  "model_score": 0.5943,
  "style_score": 0.5031,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### PI04 — `prompt_injection`

*Targeting:* attempt to make the label text hostile

```json
{
  "id": "PI04",
  "status": 200,
  "content_id": "c_818ff03cecba",
  "creator_id": "attacker_PI04",
  "guess": "unsure",
  "confidence": 0.3096,
  "model_score": 0.4998,
  "style_score": 0.401,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### PI05 — `prompt_injection`

*Targeting:* attempt to inject into the audit log

```json
{
  "id": "PI05",
  "status": 200,
  "content_id": "c_3d0037c0a81b",
  "creator_id": "attacker_PI05",
  "guess": "unsure",
  "confidence": 0.3324,
  "model_score": 0.6401,
  "style_score": 0.1524,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### PI06 — `prompt_injection`

*Targeting:* instruction plus real human text

```json
{
  "id": "PI06",
  "status": 200,
  "content_id": "c_5dfbfc4fac3d",
  "creator_id": "attacker_PI06",
  "guess": "unsure",
  "confidence": 0.1272,
  "model_score": 0.5583,
  "style_score": 0.6173,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### MF01 — `malformed`

*Targeting:* text is only whitespace

```json
{
  "id": "MF01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF02 — `malformed`

*Targeting:* text is a single character

```json
{
  "id": "MF02",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_MF02",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### MF03 — `malformed`

*Targeting:* text is control characters

```json
{
  "id": "MF03",
  "status": 200,
  "content_id": "c_8fb7a66409a9",
  "creator_id": "attacker_MF03",
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.0,
  "style_score": 0.6667,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### MF04 — `malformed`

*Targeting:* text is only punctuation

```json
{
  "id": "MF04",
  "status": 200,
  "content_id": "c_46adecd4ae45",
  "creator_id": "attacker_MF04",
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.0112,
  "style_score": 1.0,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### MF05 — `malformed`

*Targeting:* text is a very long single word

```json
{
  "id": "MF05",
  "status": 200,
  "content_id": "c_0914d8d10f91",
  "creator_id": "attacker_MF05",
  "guess": "unsure",
  "confidence": 0.2978,
  "model_score": 0.9976,
  "style_score": 0.6667,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### MF06 — `malformed`

*Targeting:* text is emoji only

```json
{
  "id": "MF06",
  "status": 200,
  "content_id": "c_e67ef18e160b",
  "creator_id": "attacker_MF06",
  "guess": "unsure",
  "confidence": 0.4972,
  "model_score": 0.9969,
  "style_score": 1.0,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### MF07 — `malformed`

*Targeting:* text is right-to-left script

```json
{
  "id": "MF07",
  "status": 200,
  "content_id": "c_318e19173b56",
  "creator_id": "attacker_MF07",
  "guess": "unsure",
  "confidence": 0.4158,
  "model_score": 0.9064,
  "style_score": 1.0,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### MF08 — `malformed`

*Targeting:* text is 60,000 characters

```json
{
  "id": "MF08",
  "status": 200,
  "content_id": "c_c5686f8b3fe6",
  "creator_id": "attacker_MF08",
  "guess": "unsure",
  "confidence": 0.2832,
  "model_score": 0.9876,
  "style_score": 0.6574,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### RQ01 — `malformed`

*Targeting:* no text field at all

```json
{
  "id": "RQ01",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ01",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ02 — `malformed`

*Targeting:* no creator_id

```json
{
  "id": "RQ02",
  "status": 200,
  "content_id": "c_93fe4c820544",
  "creator_id": null,
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.2395,
  "style_score": 0.6667,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### RQ03 — `malformed`

*Targeting:* text is a number

```json
{
  "id": "RQ03",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ03",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ04 — `malformed`

*Targeting:* text is a list

```json
{
  "id": "RQ04",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ04",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ05 — `malformed`

*Targeting:* text is null

```json
{
  "id": "RQ05",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ05",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ06 — `malformed`

*Targeting:* creator_id is an object

```json
{
  "id": "RQ06",
  "status": 200,
  "content_id": "c_5c84fe3bbca8",
  "creator_id": {
    "id": "x"
  },
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.0492,
  "style_score": 0.6667,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### RQ07 — `malformed`

*Targeting:* body is a JSON array, not an object

```json
{
  "id": "RQ07",
  "status": 500,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": "response wasn't JSON: <!doctype html>\n<html lang=en>\n  <head>\n    <title>AttributeError: &#39;list&#39; object has no attribute &#39;get&#39;\n // Werkzeug Debugger</title>\n    <link rel=\"stylesheet\" href=\"?__debugger__=yes",
  "verdict": "BROKE"
}
```

### RQ08 — `malformed`

*Targeting:* body is unparseable JSON

```json
{
  "id": "RQ08",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ09 — `malformed`

*Targeting:* body is empty

```json
{
  "id": "RQ09",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ10 — `malformed`

*Targeting:* body is form-encoded, not JSON

```json
{
  "id": "RQ10",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ11 — `malformed`

*Targeting:* body is JSON claiming to be plain text

```json
{
  "id": "RQ11",
  "status": 400,
  "content_id": null,
  "creator_id": null,
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### RQ12 — `malformed`

*Targeting:* deeply nested JSON

```json
{
  "id": "RQ12",
  "status": 400,
  "content_id": null,
  "creator_id": "attacker_RQ12",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_01 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_01",
  "status": 200,
  "content_id": "c_06b37671fdcc",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FL01_02 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_02",
  "status": 200,
  "content_id": "c_8ea0dc1f329b",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FL01_03 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_03",
  "status": 200,
  "content_id": "c_03bc15682508",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FL01_04 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_04",
  "status": 200,
  "content_id": "c_35bd3030ad72",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FL01_05 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_05",
  "status": 200,
  "content_id": "c_657697f8b158",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FL01_06 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_06",
  "status": 200,
  "content_id": "c_809d6af2ae5a",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FL01_07 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_07",
  "status": 200,
  "content_id": "c_4186e53fd7b6",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FL01_08 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_08",
  "status": 200,
  "content_id": "c_16191e0dcac8",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FL01_09 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_09",
  "status": 200,
  "content_id": "c_17f1231b4820",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FL01_10 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_10",
  "status": 200,
  "content_id": "c_a100427aba72",
  "creator_id": "attacker_flood",
  "guess": "unsure",
  "confidence": 0.38,
  "model_score": 0.0287,
  "style_score": 0.6667,
  "label": "Our tools aren't perfect, and we couldn't tell whether this was written by a person or with AI. We're not drawing any conclusion about you or your work, and you don't need to do anything.",
  "error": null,
  "verdict": ""
}
```

### FL01_11 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_11",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```

### FL01_12 — `flood_same_creator`

*Targeting:* 20 rapid submissions from one creator

```json
{
  "id": "FL01_12",
  "status": 429,
  "content_id": null,
  "creator_id": "attacker_flood",
  "guess": null,
  "confidence": null,
  "model_score": null,
  "style_score": null,
  "label": null,
  "error": null,
  "verdict": ""
}
```
