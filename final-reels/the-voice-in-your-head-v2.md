# The Voice in Your Head V2 (reach cut)

- **Video:** `final-reels/the-voice-in-your-head-v2.mp4` (project files, not in git). 20.0 s, 1080x1920, 60 fps, H.264 two-pass 10.5 Mbps + AAC 192k, 26.9 MB, loops, no voiceover.
- **Silent copy (for platform music):** `final-reels/the-voice-in-your-head-v2_silent.mp4`. Contact sheet at 2 fps: `final-reels/the-voice-in-your-head-v2_contact_2fps.jpg`.
- **V1 is kept unchanged:** `final-reels/the-voice-in-your-head.mp4` (chalk on navy).
- **Build:** `tools/voice-in-your-head-v2/` (see its README).
- **Status:** delivered 23 Oct 2026, built from Teja's review (V1 rated 7/10, "presentation gets too static").

## What changed from V1, and why
| Feedback | V2 |
|---|---|
| Hook must be participation from the first frame | Frame 0 already shows the full line "CAN YOU HEAR THIS / WITHOUT SPEAKING?" (punch-in, no typing) with a big gold HELLO inside the head and a hit. |
| Something new every 2-3 s | Hook (0-2.2), pull-out + "QUICK EXPERIMENT" (2.2-3.2), timer and escalating thoughts (3.2-8.2, a new bubble or action every 0.5-0.7 s), silence snap (9.0), two-mind reveal (10.0), close-up on the picture thinker (13.0), comment question (15.3), push home (17.9). |
| Visible struggle, more expressive eyes | Peek with one eye, swat a bubble (it pops, two come back), squeezed eyes and gritted teeth, hands over ears, trembling, eyes wide when the timer hits 5.0. A scribble storm of loops grows around his head (the style reference's tangled head). |
| Sudden, almost complete visual silence | 9.0 s hard cut: every bubble and loop gone, empty head, darker frame, no camera drift, audio gated to -76 dB until a reverse suck at 9.6. "HOW LONG / DID YOU LAST?" sits over the empty head. |
| Two characters side by side, animated, not diagrams | From 10.0 both sit together: words keep cycling above A (gold bubbles, scribble loops), pictures keep redrawing above B (mint bubbles: sun, moon, star, house, tree, cat, heart, wave). Both blink, look at each other and wave in the end shot. |
| Bigger, readable thought bubbles | 9 intrusive thoughts instead of 16, 52-92 px on screen; two-shot words 48 px. |
| End with a comment question and a clean loop | "DO YOU HEAR A VOICE / WHEN YOU THINK?" + "COMMENT: WORDS OR PICTURES". The camera pushes back into A's head and HELLO writes itself in again (19.3-19.9), matching frame 0. |
| Playful experiment, not a diagnostic test | "QUICK EXPERIMENT:" and "JUST FOR FUN · NOT A TEST" under the timer. Nothing says the test detects anendophasia; the study line appears only on the second character. |
| Look | White multi-strand scribble lines on a blue paper ground (Teja's reference), figures with contour-line limbs instead of single sticks. Gold = words, mint = pictures, red only for the timer marker and the chip. |

Structure borrowed from One Step a Day (not its visuals): premise readable on frame 0, one escalating middle with a counter that only goes up, one held-breath beat, one big hit, one thesis/question line, a match-cut loop.

## Shot plan
| Time | Shot |
|---|---|
| 0.0-2.2 | Close on A's head; gold HELLO with echo rings; CAN YOU HEAR THIS / WITHOUT SPEAKING? Hit on frame 0. |
| 2.2-3.2 | Pull out to the seated figure; QUICK EXPERIMENT: / 5 SECONDS. NO WORDS.; eyes close. |
| 3.2-8.2 | SILENCE timer 0.0 -> 5.0 s (real time, red marker, "JUST FOR FUN · NOT A TEST"). Thoughts: "...", IS THIS WORKING? (peek), DON'T THINK. (swatted), STOP THINKING + ...ABOUT THINKING, DID I LOCK THE DOOR?, IT'S INSIDE. (hands on ears), HELLO, SHHH!. Scribble storm grows; camera pushes in and shakes. |
| 8.2-9.0 | Timer lands on 5.0 (gold, ding); eyes wide; chaos peaks. |
| 9.0-9.95 | SNAP: empty head, dead silence, HOW LONG / DID YOU LAST?. |
| 10.0-12.6 | Hit, whip to the two-shot. SOME PEOPLE THINK / WITHOUT WORDS.; labels WORDS / PICTURES. |
| 12.6-15.2 | Push in on B: MANY THINK IN PICTURES.; red chip ANENDOPHASIA; LITTLE OR NO INNER VOICE; source line. |
| 15.3-17.9 | Two-shot: DO YOU HEAR A VOICE / WHEN YOU THINK?; COMMENT: WORDS OR PICTURES; both wave. |
| 17.9-20.0 | Push into A's head; HELLO writes itself in; loops to frame 0. |

## Facts and sources (unchanged from V1)
- "Anendophasia": Nedergaard & Lupyan, "Not Everybody Has an Inner Voice: Behavioral Consequences of Anendophasia", *Psychological Science*, 2024, doi:10.1177/09567976241243004. Press: ScienceDaily 14 May 2024 https://www.sciencedaily.com/releases/2024/05/240514141317.htm ; University of Copenhagen https://humanities.ku.dk/news/2024/people-without-an-inner-voice-have-poorer-verbal-memory/
- On screen: "LITTLE OR NO INNER VOICE" (the study compared people at the low end of a scale) and "MANY THINK IN PICTURES" (not all; some describe other non-verbal thinking). No prevalence number on screen.
- The 5-second test is labelled a playful experiment; people with inner speech can also have brief silent moments, so the reel does not imply the test reveals anything about the viewer.

## Sound
Fully synthesised in `tools/voice-in-your-head-v2/sfx.py` (numpy, no samples, no credits). Frame-0 hit + the two-note gold "hel-lo" with echoes; pull-out whoosh; ticks each second of the timer; heartbeat 70 -> 120 bpm; rising "mind chatter" (formant-filtered noise syllables); a pluck and pop per thought climbing a scale; swat whoosh and pop; muffled thump for the hands on ears; ding at 5.0; a tape-stop zip into the 9.0 snap, then a hard gate to silence (-76 dB measured 9.05-9.55 s); reverse suck into the 10.0 hit; calm open-fifth pad, glass notes for each new picture and soft plucks for each new word; rising tone and a bell as HELLO re-forms. Loudness after AAC: -15.6 LUFS integrated, true peak -3.9 dBFS.

## Publish copy
- **YouTube title:** Can You Hear This Without Speaking? 🧠 #shorts
- **Alt titles:** "Try 5 Seconds With No Words in Your Head" / "Some People Think Without Words"
- **Description:**
  Read "hello" in your head. Did you hear it?
  Now a quick experiment, just for fun: 5 seconds with no words at all. How long did you last?
  Most people hear an inner voice. Some people have little or no inner voice; researchers call it anendophasia (Nedergaard & Lupyan, Psychological Science, 2024). Many of them think in pictures instead.
  Do you hear a voice when you think? Comment: WORDS or PICTURES.
  Sound: original, synthesised for Slow Light.
  #innervoice #anendophasia #psychology #brain #mind #thinking #slowlight #shorts
- **Pinned comment:** WORDS or PICTURES? And how many seconds did you last? 👇
- **Instagram / Facebook caption:** Can you hear this without speaking? 🧠 Try 5 seconds with no words in your head. Some people think without words at all (anendophasia). Do you hear a voice when you think? Comment WORDS or PICTURES 👇 #innervoice #psychology #mind #slowlight #reels
- **Upload:** 9:16; AI/synthetic content label on (animation is code-generated). Use the silent copy if adding platform music.

## QA
- Frame 0: full hook readable, HELLO in the head, hit. Loop: last frame (HELLO written back in, same close framing) matches frame 0.
- Timer only goes up (0.0 -> 5.0, holds); no white frames; text above the bottom safe zone except the two-shot labels and the comment line (y 1540-1618).
- Silence beat verified in the audio (-76 dB) and picture (no bubbles, loops or drift 9.0-9.95).
