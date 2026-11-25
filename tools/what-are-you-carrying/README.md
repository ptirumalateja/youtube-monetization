# What Are You Carrying (Slow Light Dark)

17.6 s, 1080x1920, 30 fps (v4: starts at the bottom and climbs to mid-hill before the slip; the end card lands at the top of the frame together with the enlightenment; close-up centred on him). Copy: `publish-copy/what-are-you-carrying.md`. Series look: `storyboards/slow-light-dark/style-sheet.md`.
`sld.js` is the shared kit (umbrella/born-rich version with `vig` and `moteSpan`).

```
cd tools/what-are-you-carrying && npm install
sfx/gen.sh                                               # ElevenLabs sound effects (already committed)
OUT=/path/to/render node render.cjs meta                 # meta.json: stone and label screen positions
for w in 0 1 2 3; do OUT=/path/to/render node render.cjs frames $w 4 & done   # 525 frames
python3 mix.py /path/to/render/meta.json /path/to/render/mix.wav
python3 compose.py /path/to/render /path/to/deliver
```

- Idea from a reference reel the owner shared (25 Nov 2026: a 2D outline figure pushing a boulder up a hill, then
  throwing labelled baggage away, 32 s, silent). Our version: 3D cream figure, a sack of stones instead of a boulder,
  the series gold lamp as the "new life" at the top of a steep hill, side view, 17.5 s, our own words.
- v2 (owner notes): the slip takes him all the way back down to OLD LIFE (3.1-4.35) and he lets go on the flat; a gold flag waves at the top (NEW LIFE); arriving there triggers an enlightenment: slow sunburst of rays behind him, halo, rising gold motes, warm glow on him, the lamp lifts.
- `timeline.json`: slip (3.1-4.35), kneel and sack drop (4.45-5.05), camera push (4.3-5.5), the five throws, stand (10.9),
  walk up (11.7) into the light, bloom (14.7), enlightenment glow (14.75-17.2), end card (17.4).
- `scene.js`: hill = extruded side profile (rise 4.4 m over 5.6 m, plateau), faint cream edge line; lamp high over the
  top leaning down the slope. Small grass tufts (one instanced mesh, gentle sway) along the near edge and over the slope. The sack rides on his back (hands hold the mouth over his shoulders), is set down beside
  him (far side, so it never hides him), shrinks with each stone. Stones: shown in front of his chest (label), wound back
  over the shoulder and thrown; flight and roll down the profile precomputed, so `renderAt(t)` stays pure.
- `overlay.py`: hook TRYING TO REACH / A NEW LIFE... then ...WHILE CARRYING / THE OLD ONE., OLD LIFE / NEW LIFE markers with curved arrows,
  IT'S NOT THE CLIMB. / IT'S THE WEIGHT., red chips on the stones, LET IT GO., end card WHAT ARE YOU / STILL CARRYING?
  All captions below the platform top bar (y >= 270).
- `mix.py`: ElevenLabs foley (strain, heavy steps, slip, sack drop, rummage, throw, long rolls panned away, relieved
  breath, light steps, warm swell, shimmer and flag at the top, boom) over the series bed.
