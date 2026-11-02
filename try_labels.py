import detector, stylometry, scoring, cues

tests = {
    "ai_try": "In today's rapidly evolving digital landscape, it is important to note that effective communication plays a crucial role in organizational success. Furthermore, leveraging innovative strategies can significantly enhance overall productivity and foster collaboration. Additionally, it is essential to consider the various factors that contribute to sustainable growth. Moreover, stakeholders should prioritize continuous improvement to ensure long-term outcomes.",
    "ai_a": "In conclusion, it is important to note that effective time management is essential for success. Furthermore, individuals who prioritize tasks are better positioned to achieve their goals. Additionally, minimizing distractions enhances productivity. Moreover, regular breaks contribute to sustained performance. Therefore, adopting these strategies can significantly improve outcomes in both personal and professional contexts.",
    "human_try": "I didn't sleep. Not properly, anyway. I lay there listening to the boiler tick and thinking about the thing I'd said to Marcus at the pub, which was stupid, and which he will absolutely bring up again. Twice now. So: coffee, and the long way round to work, and a plan. The plan lasted until about ten past nine, when Priya asked how the weekend was and I said fine in the voice that means it wasn't.",
    "human_a": "Okay so, honestly? I have no idea why I kept that couch. It smelled like dog, the left arm was torn, my sister hated it. But every night I sat there anyway, feet up, watching bad reruns until midnight, and somehow it was the best part of my day. Weird, right? Anyway, it's gone now. Miss it.",
    "human_b": "Dad called again - third time this week - and I let it ring. Not proud of that. He just wants to talk about the garden, the neighbours, whether I'm eating properly (I'm not). So I'll ring back tomorrow, probably, after work, when I've got the energy to pretend everything's fine. It mostly is. Mostly.",
    "human_c": "We missed the bus. Of course we did. Marta was still hunting for her keys (they were in the fridge, don't ask) and by the time we got to the corner it was pulling away, brake lights glowing like two tiny angry eyes. So: a long walk, wet shoes, and a very quiet coffee.",
    "human_d": "I woke up late again and the whole morning went sideways. The toast burned, the kettle took forever, and I couldn't find my other shoe until I finally looked under the bed. By the time I got out the door it had started to rain, of course, and I'd left my umbrella by the front door. So I walked fast, got soaked anyway, and arrived at work looking like I'd fallen in a pond. Nobody said anything. That was kind of nice.",
    "human_e": "My grandmother used to keep a tin of buttons on the shelf in the hallway. I never knew why she had so many. Whenever I was bored she'd let me tip them out on the carpet and sort them by colour, and I'd spend an entire afternoon doing it, quite happy. I found the tin last week at my mum's house. It still rattles the same way. I sat on the floor and sorted them again, and I didn't tell anyone.",
    "human_f": "We drove to the coast on Saturday because Tom said the weather would be good, and it wasn't. It was grey and windy and the car park was half empty. We ate chips on the sea wall anyway, with our coats zipped up to our chins, and a seagull tried to steal Tom's sausage roll. He shouted at it. I laughed so hard I nearly dropped my cup. It wasn't the day we planned, but I'd honestly go again tomorrow.",
}

for name, text in tests.items():
    m = detector.model_signal(text)
    s = stylometry.style_signal(text)
    k = cues.cue_signal(text)
    w = len(stylometry.words(text))
    c = scoring.combine_signals(m, s, w, k)
    print(f"{name:>10}  words={w}  model={m}  style={s}  cue={k}  combined={c}  -> {scoring.score_to_label(c)[0]}")