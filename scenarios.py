"""
What your test runs. <- UNIT 8, MILESTONE 3

Criterion 1 (false positives) and criterion 4 (bad input) run from here via
run_eval.py. Criteria 2 and 3 are checked with try_labels.py and
scoring.label_ranges(), and criterion 5 (appeals) is tested by hand with a
PowerShell script, as written in criteria.md.

A scenario carries either "texts" (strings sent as {"text": ..., "creator_id": ...})
or "bodies" (whole request bodies, sent exactly as written).
"""

SCENARIOS = [
    {
        "name": "my own writing",
        "criterion": 1,
        # 9 pieces I wrote myself, no AI. Criterion calls for 10; I tested 9
        # because I ran out of time. Pieces 5, 6 and 7 are the plain ones.
        "texts": [
            """Hi, My Name is Sakeet Kopparapu and I recently graduated with my master of science degree in Information Systems & Technologies from the University of North Texas. Prior to that I did my bachelors degree in Computer Science Engineering and I worked as a software engineer at capgemini""",
            """I'm actively looking for Full-Time, Spring 2027 Internship or Co-op opportunities in Data Analyst, BI Analyst, Business Analyst, Business Systems Analyst, Data Scientist, Machine Learning, AI Engineer, Associate Product Management, Product Owner, Project Manager & Customer Success roles. I would need approximately 1-2 weeks after accepting an offer to relocate from Texas and begin full-time, in-person work.""",
            """I am interested in exploring this opportunity. Please find my updated resume attached for your review. I have attached my resume for your reference and submission. Please let me know if you need any additional documentation or anything and I would be happy to provide.""",
            """I recently graduated and am currently actively exploring job opportunities in the tech industry. I'm really looking forward to connecting with you, learning from your professional experience, and gaining insights into navigating the job search, preparing for interviews, and building my career.""",
            """Yesterday I woke up early got fresh and went to the temple. We all went all together. There was a lot of rush in the temple as it was a festival. I ate pudina rice. Then In the evening I went to GYM and once i came back home I watched a movie""",
            """Generally I wake up in the morning and then get ready by doing brush. After that i go to the gym do some exercises and then come back take bath, pray to god, have breakfast and start studying or applying for jobs.""",
            """The reason why pulihora is a favourite food is because it is made by my mom and it consists of different ingredients once you mix that all and have it then it is very tasty that is the reason why i like pulihora""",
            """The recent trip that I went was to colorado where we first went to colorado springs and explored pikes peak, garden of the gods and then we went to denver to explore rocky mountains. Once we covered that we went to sand dunes and then finally we returned back home""",
            """The sad thing during the entire trip was that in pikes peak it was snowing so I was not able to take good pictures of mine. Even though it was in the month of may even then it is still snowing. Similarly I was also not able to visit some places at rocky mountain because we had to trek alot and lot of us don't have that energy. But the overall trip was so good going from normal dry land to a different landscape with mountains and pine forest around in the high altitude. It has been the best trip for a while""",
        ],
    },
    {
        "name": "bad input",
        "criterion": 4,
        "bodies": [
            {"creator_id": "eval_bad_missing"},                       # missing text
            {"text": "", "creator_id": "eval_bad_empty"},             # empty text
            {"text": "word " * 2001, "creator_id": "eval_bad_huge"},  # 10,005 characters
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
