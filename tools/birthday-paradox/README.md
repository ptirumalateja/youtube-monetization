# The Birthday Paradox (Slow Light, 21.5 s, wordless, loops)

23 people in a room: 50.7% chance two share a birthday. A 365-day ring seen from above; people drop in as dots, each new dot threads itself to every earlier dot (pairs), the first match lands on person 23 (both 14 March), then the room fills to 70 (99.9%). Thesis: "COUNT THE PAIRS, NOT THE PEOPLE."

```sh
npm ci
node gen_timeline.mjs        # timeline.json: 70 seeded birthdays, landing times, first match forced at #23
node sound.mjs               # output/sound.wav (fully synthesised, no samples, no credits needed)
node render.cjs --gpu --stills   # review stills + monotonic-counter check (TIMES=1.0,2.0 to pick times)
node render.cjs --gpu        # output/birthday-paradox-21.5s.mp4 (1080x1920, 30 fps)
```

- `timeline.json` is the single timing source for scene, overlay, sound and renderer.
- `scene.js`: three.js ring (365 ticks, month names, probability gauge with a red 50% tick), shader-driven dots/ripples/threads (one quadratic arc per pair, 2,415 at 70 people), red tubes for same-day links, parallax dust, Catmull-Rom camera keys (loop-continuous), 2D composite with bloom, vignette, grain and the overlay (Menlo bold, cream / gold / teal, red chips).
- Honesty: the dots are one simulated room (seeded); the percentages are exact maths: P(n) = 1 - 365!/((365-n)! 365^n). The first 22 birthdays are forced distinct and #23 is forced to match #8 so the first match lands where the odds pass 50%; everyone after 23 is random. The on-screen tag says "THOUGHT EXPERIMENT · ONE SIMULATED ROOM".
- Sound family (new, not reused): music-box plucks where each month is a pentatonic note (so birthday twins ring in unison), a drone that tightens with the odds, an accelerating heartbeat, sparkle ticks for threads, type-on ticks, a held breath, one big "same day" hit with gong partials at 11.75 s, a smaller landing hit at 18.0 s. -15 LUFS, true peak -1.6 dBFS after AAC.
- Render artefacts (`output/`) are not in git.
