import detector, stylometry, scoring

tests = {
    "human_d": "I woke up late again and the whole morning went sideways. The toast burned, the kettle took forever, and I couldn't find my other shoe until I finally looked under the bed. By the time I got out the door it had started to rain, of course, and I'd left my umbrella by the front door. So I walked fast, got soaked anyway, and arrived at work looking like I'd fallen in a pond. Nobody said anything. That was kind of nice.",
    "human_e": "My grandmother used to keep a tin of buttons on the shelf in the hallway. I never knew why she had so many. Whenever I was bored she'd let me tip them out on the carpet and sort them by colour, and I'd spend an entire afternoon doing it, quite happy. I found the tin last week at my mum's house. It still rattles the same way. I sat on the floor and sorted them again, and I didn't tell anyone.",
    "human_f": "We drove to the coast on Saturday because Tom said the weather would be good, and it wasn't. It was grey and windy and the car park was half empty. We ate chips on the sea wall anyway, with our coats zipped up to our chins, and a seagull tried to steal Tom's sausage roll. He shouted at it. I laughed so hard I nearly dropped my cup. It wasn't the day we planned, but I'd honestly go again tomorrow.",
}

for name, text in tests.items():
    m = detector.model_signal(text)
    s = stylometry.style_signal(text)
    w = len(stylometry.words(text))
    c = scoring.combine_signals(m, s, w)
    print(f"{name:>10}  words={w}  model={m}  style={s}  combined={c}  -> {scoring.score_to_label(c)[0]}")