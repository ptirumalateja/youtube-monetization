# They Threw Words. He Built Stairs. (Slow Light Dark)

18 s, 1080x1920, 30 fps, one continuous shot, clean end hold. Copy: `publish-copy/they-threw-words.md`.
Remake of an Instagram reel Teja shared (insult bricks thrown at a stickman who builds a wall). Ours: every word-block becomes a step, he climbs into the lamp, and the red "YOU'LL NEVER MAKE IT" block falls short.
Series look: `storyboards/slow-light-dark/style-sheet.md`. `sld.js` is a copy of `../slow-light-dark-common/sld.js` (the page server only serves this folder).

```
cd tools/words-to-stairs && npm install                        # three@0.170.0 (playwright comes from the global install)
mkdir -p fonts && cp /usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-{SemiBold,Bold}.ttf fonts/   # brick words (OFL, not committed)
OUT=/path/to/render node render.cjs meta                       # meta.json (asserts the placed-block count is monotonic and ends at 9)
for w in 0 1 2 3; do OUT=/path/to/render node render.cjs frames $w 4 & done   # 540 frames, about 25-30 min on 4 CPUs
OUT=/path/to/render W=540 H=960 SUB=1 TIMES=0,5,12.4 node render.cjs stills  # quick look stills
python3 mix.py /path/to/render/mix.wav
python3 compose.py /path/to/render /path/to/deliver            # master (-15 LUFS) + _music-ready (silent)
```

- `timeline.json`: words, catch times, which man throws each block, flight time, the place delay, red block release and landing, look-down / stand-tall, gold payoff, fade-out of the men, and the three text times.
- `scene.js`: the stage (lamp, beam, motes, mirror floor, grade from `sld.js`). Blocks are boxes 0.56 x 0.18 x 0.40 m. Each new one sits on the last one, 0.20 m further along a diagonal heading right and away from camera, so the stair faces the camera and every word stays readable. Each block carries a billboard word while it is in hands or in the air. When it is set down, the word sinks into the front face, which flashes and then stays lit (emissive map from a canvas), and a few gold motes lift off. Flights are ballistic (g = 9.8). Both throwers and the catcher use two-hand IK on the block's grips. The red block is held low by the third man from frame 0 and lands short of the stair with a dust puff.
- `overlay.py`: hook on frame 0, one rehook, and the payoff held to the end, using the shared `sld_text.py` and the watermark.
- `mix.py`: room bed, lamp hum and a rising drone; a recorded whoosh per throw (Tomlija 175183, CC BY 3.0, credit required); synthesised catch slaps, stone placements, ember crackle and footfalls; a held-breath duck, then the red slam (sub_boom + CC0 qubodup 814046 two octaves down) and gravel. No music.
