# Acceptance criteria — Provenance Guard

Five criteria that say what "working" means for this service, written in unit 7
**before** you built it.

**All five are yours.** None are given.

An acceptance criterion names a number or something plainly observable. *"The
detector is accurate"* is an opinion — and perfect AI detection isn't possible
anyway, so it's an opinion about something nobody can deliver. *"Of 10 pieces I
wrote myself, at most 1 is labelled high-confidence AI"* is a criterion.

Under each, write a sentence or two on **why that target**. *"I allow at most 1
false positive in 10 because on a writing site a wrong accusation costs more
than a missed detection"* is a real answer.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## Pick numbers you can defend

**Cover at least three of these five areas.** They're prompts, not a form.

| Area | A question it could answer |
|---|---|
| False positives | How often may a human's writing get called AI? |
| Score spread | How far apart should clearly-AI and clearly-human text score? |
| Label coverage | Is every one of your three labels actually reachable? |
| The appeal path | Does an appeal always change status and always get recorded? |
| Bad input | What happens when `text` is missing, empty, or enormous? |

Two things worth knowing before you pick numbers:

- **The expensive mistake is one-sided.** Missing some AI text costs the site a
  little. Accusing a real writer costs that person a lot. A criterion that
  treats both errors as equally bad is describing a system nobody would ship.
- **Unit 8 tests across three trials, and the target has to hold across all
  three.** Your first signal runs a model, so identical input can score
  differently twice. A target of "at most 1 in 10" against trials of 2, 1, 2 is
  a **miss**.

---
## 1. False positives
Of 10 pieces of my own human writing (including at least 3 plain, short-sentence pieces), at most 1 is labeled high-confidence AI, in each of 3 runs.

**Why this target:** A wrong accusation costs the writer far more than a missed detection costs the site, and plain writers have the least room to argue back. I picked 1 because 0 is unrealistic for this kind of detector, but more than 1 would mean too many real writers get accused.

## 2. Score spread
The combined score for clearly-AI text is at least 0.3 higher than for clearly-human text, using 3 AI and 3 human samples, in each of 3 runs.

**Why this target:** A gap of 0.3 leaves room for a real "unsure" band between the two, so all three labels can exist. A smaller gap would make the labels meaningless.

## 3. Label coverage
I can produce each of the three labels with a real submission to /submit, and scoring.label_ranges() shows no gaps between ranges from 0.0 to 1.0.

**Why this target:** An unreachable label means my thresholds are wrong, and "unsure" is the one most likely to be unreachable.

## 4. Bad input
Missing text, empty text, and text over 10000 characters each return a 400 JSON error and write no log entry.

**Why this target:** Long text slows the model and could be used to overload the service, and rejected input should never leave a misleading entry in the log.

## 5. Appeal path
5 of 5 appeals I submit with a valid content_id change the status to under_review and appear in logs/audit.jsonl; an unknown content_id returns a 404.

**Why this target:** An appeal is the writer's only recourse, so it should never fail silently.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 8 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Uncertain cases land in the unsure band

         The system handles uncertain cases well.

         **Why this target:** ...

         > **Revised in unit 8:** Text I judged borderline scores between
         > 0.4 and 0.6 in at least 4 of 5 cases.
         >
         > **Why revised:** "well" gave me nothing to check. I couldn't
         > reach a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "At most 1 of 10 of my own pieces flagged as AI" → "at most 3
            of 10", because 1 of 10 turned out to be hard.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
