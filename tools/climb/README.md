# Build It As You Climb (Slow Light Dark)

Remake of the neuronvisuals "Perfectionist vs Action Taker" ladder reel (Teja, 6 Nov 2026). 13 s, 1080x1920, 30 fps.
Same composition as the reference (two lanes, the ladder grows as he climbs into a light at the top, the perfectionist
is left with one perfect rung), rebuilt in the 30 Friends dark-warm look: gold hatch and beam, ember glints on every
lashing, a plank bundle on his back that runs out at the top, rung counters, his look up at the light, a seamless loop.

    npm install
    mkdir -p fonts && cp /usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-{SemiBold,Bold}.ttf fonts/
    OUT=out node render.cjs meta
    for w in 0 1 2 3; do OUT=out node render.cjs frames $w 4 & done; wait     # ~30 min on 4 CPUs (SUB=3)
    python3 mix.py out/mix.wav
    python3 compose.py out deliveries

- `scene.js`: the scene. Timing lives in `timeline.json` (cycle, buildFrac, pStand/pPlace/pSit, camera keys in CK).
- `overlay.py`: lane labels + RUNGS counters riding over the lanes, then BUILD IT AS YOU CLIMB., then PERFECTIONIST / RUNGS 01.
- `mix.py`: no music. Wood knocks, rope squeaks, footfalls, sanding, a CC0 riser-hit through the hatch, one click.
  ElevenLabs SFX was tried first but the account had a failed payment on 6 Nov, so the foley is the series kit.
