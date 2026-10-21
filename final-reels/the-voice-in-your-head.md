# The Voice in Your Head (v1)

- **Video:** `final-reels/the-voice-in-your-head.mp4` (project files, not in git). 20.0 s, 1080x1920, 60 fps, H.264 two-pass 10.5 Mbps (27 MB), loops, no voiceover.
- **Status:** delivered 21 Oct 2026. Reel #10 of `ref-remakes-plan.md` (the ref was a 58 s voiced chalk-stickman "say hello in your head / 5 second test" explainer; we kept only the topic).
- **Build:** `tools/voice-in-your-head/` (see its README). Contact sheet at 2 fps: `final-reels/the-voice-in-your-head_contact_2fps.jpg` (project files).

## Concept
A wordless participation reel. The viewer is asked to say "hello" in their head, then to keep their head silent for 5 real seconds while a timer runs. Our stickman tries too: gold thought bubbles keep refilling however hard he tries (he swats one and two more appear, he covers his ears, which cannot work because the voice is inside). Twist: a second stickman beside him has no word bubbles at all, only picture bubbles. "SOME PEOPLE DON'T HAVE ONE." Close: "WHICH ONE ARE YOU?" and a push back into the first head, which loops to the frame-0 "HELLO".

Look: the Slow Light stickman series (ivory chalk figure, thick round strokes) on a deep navy chalkboard with eraser smudges, parallax chalk dust, vignette and fine grain. Colour carries the idea: **gold = the inner voice (words)**, **teal = thinking without words (pictures)**, red only for the timer marker and the ANENDOPHASIA chip. Different from Sleep Paralysis (black and blood red, bedroom) and Shadow Stickman (lamp and wall).

## Shot plan
| Time | Shot |
|---|---|
| 0.0-2.0 | Close on his head. Frame-0 hit: a gold HELLO pops inside the head with echo rings. Hook typed by 1.2 s: SAY "HELLO" IN YOUR HEAD. He smiles. |
| 2.0-3.0 | Snap out to the full figure sitting cross-legged on a cushion. NOW STAY SILENT. / 5 SECONDS. NO WORDS. Eyes close. |
| 3.0-8.0 | SILENCE timer 0.0 -> 5.0 s in real time (only goes up), bar with a red marker. Word bubbles arrive faster and faster: "...", OK. SILENCE., AM I DOING IT? (he peeks), DON'T THINK (he swats it, it pops), STOP THINKING + ...ABOUT THINKING, HELLO again, hands over ears, THAT WON'T WORK, IT'S INSIDE, DID I LOCK THE DOOR?, HUNGRY, SHHH, HOW LONG LEFT?, WORDS WORDS WORDS. |
| 8.0-9.4 | Timer lands on 5.0 (gold, ding). HOW FAR DID YOU GET? He opens his eyes, exhausted, hands drop. |
| 9.4-10.08 | Every bubble pops at once into gold dust; held breath (dim, near silence, reverse suck). |
| 10.08-12.4 | Big hit, whip-pan reveal: a second stickman, calm, head glowing teal, picture bubbles (sun, house, wave, tree, heart, star) and no words. SOME PEOPLE / DON'T HAVE ONE. |
| 12.4-15.3 | Push in on him; red chip ANENDOPHASIA; LITTLE OR NO INNER VOICE. / MANY THINK IN PICTURES. |
| 15.3-17.6 | Two-shot: a small gold HELLO inside the first head, teal pictures above the second. WHICH ONE / ARE YOU? Labels A VOICE / NO VOICE. |
| 17.6-20.0 | Push back into the first head (frame-0 framing, eyes up and right), rising tone; loops into the frame-0 HELLO. |

## Facts and sources
- "Anendophasia" is the term Johanne Nedergaard (University of Copenhagen) and Gary Lupyan (University of Wisconsin-Madison) coined for the lack of an inner voice: "Not Everybody Has an Inner Voice: Behavioral Consequences of Anendophasia", *Psychological Science*, 2024, doi:10.1177/09567976241243004.
  - Press summaries: ScienceDaily (14 May 2024) https://www.sciencedaily.com/releases/2024/05/240514141317.htm ; University of Copenhagen https://humanities.ku.dk/news/2024/people-without-an-inner-voice-have-poorer-verbal-memory/ ; BPS Research Digest https://bps.org.uk/research-digest/silent-inner-world-anendophasia
- People with little or no inner voice report thinking in pictures (translating them into words when they speak) or describe non-verbal thinking; in the study they were worse at remembering similar-sounding words and at judging rhymes from pictures, with no difference on task switching or telling similar figures apart.
- Wording choices: the brief's "SOME PEOPLE NEVER HEAR ONE" became **"SOME PEOPLE DON'T HAVE ONE."** (it matches the study's title) and the chip line says **"LITTLE OR NO INNER VOICE"** because the study compared people at the low end of a scale, not only people with none. "MANY THINK IN PICTURES" rather than "all", since some describe other non-verbal thinking.
- No prevalence number on screen. The researchers' rough estimate in the press (5-10% of people do not experience an inner voice the same way) is an estimate, not a measured prevalence; it can be used in a pinned comment as "researchers estimate", not as a fact.
- No sizes or distances are compressed, so no "not to scale" tag is needed.

## Sound
Fully synthesised in `sfx.py` (numpy only, no samples, no credits). Frame-0 hit + two falling gold bell notes (the "hel-lo") with echoes; snap whoosh; soft clock tick each second of the 5 s; heartbeat speeding from 70 to 112 bpm; rising "mind chatter" made from formant-filtered noise syllables; a gold pluck per bubble climbing a pentatonic scale; swat whoosh and pop; a ding at 5.0; a cascade of pops at 9.4 then held breath and a reverse suck; the big hit at 10.08 (crack, pitch-drop body, gong partials, sub); a calm open-fifth pad and glass notes for every new picture; the gold and teal motifs together on WHICH ONE ARE YOU?; a rising tone into the loop. Mix: -15.2 LUFS integrated, true peak -2.5 dBFS measured after AAC.

## Publish copy
- **YouTube title:** Say "Hello" in Your Head. Now Stay Silent for 5 Seconds. #shorts
- **Alt hook titles:** "Can You Turn Off the Voice in Your Head?" / "Some People Don't Have an Inner Voice"
- **Description:**
  Say "hello" in your head. Did you hear it? Now try 5 seconds with no words at all.
  Most of us can't: the inner voice keeps talking. But some people have little or no inner voice. Researchers call it anendophasia (Nedergaard & Lupyan, Psychological Science, 2024). Many of them think in pictures and turn them into words only when they speak.
  How far did you get? And which one are you?
  Sound: original, synthesised for Slow Light.
  #innervoice #anendophasia #psychology #brain #mindfacts #slowlight
- **Pinned comment:** "How many seconds did you last before a word showed up? 🧠 Mine: 1.6"
- **Instagram / Facebook caption:** Say "hello" in your head. Now stay silent for 5 seconds. How far did you get? Some people don't have an inner voice at all (anendophasia, Psychological Science 2024). Which one are you? 👇 #innervoice #psychology #slowlight
- Upload: AI/synthetic content label on (animation is code-generated).
