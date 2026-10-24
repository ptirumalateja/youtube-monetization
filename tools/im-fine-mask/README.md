# I'm Fine (Slow Light Dark, reel 2)

18.5 s, 1080x1920, 30 fps, wordless, ends on a 1 s hold. Copy: `publish-copy/im-fine-mask.md`.
The shared look (palette, rim/dust materials, floor, beam and motes, stickman rig, grade, text layer, compose and the mix
helpers) is copied from the series pilot `tools/chain-never-locked/` so the two reels match.

```
cd tools/im-fine-mask && npm install                          # three@0.170.0 (playwright comes from the global install)
OUT=/path/to/render node render.cjs meta                      # meta.json: timeline + per-frame screen positions
for w in 0 1 2 3; do OUT=/path/to/render node render.cjs frames $w 4 & done   # 555 frames, 3 motion-blur sub-frames (6 on the trucks)
OUT=/path/to/render W=540 H=960 SUB=1 TIMES=0.4,7,11.3,17.9 node render.cjs stills   # quick look stills
python3 overlay.py still IN.jpg T OUT.jpg                     # text layer on one still
python3 mix.py /path/to/render/meta.json /path/to/render/mix.wav   # DUMP=1 prints per-bus levels
python3 compose.py /path/to/render /path/to/deliver           # master (-15 LUFS, under -1 dBTP) + _music-ready (silent)
```

- `timeline.json`: every story time (mask lift, the four trucks, thumbs-up, pats, laugh, call, sit, grip, the two pulls and creaks, crack, gasp, slump, pull-out, lamp flicker, look, the grey one's mask off, clink, loosen, lower, end text, warm-up).
- `scene.js`: pure `renderAt(t)`. Five pools in a row along +x, 3.4 m apart, so only one is in frame; the camera trucks pool to pool through the dark, and the hero switches pool at mid-truck when neither is on screen. Two spot lights are re-used (lamp k uses spot k % 2, live from the arrival at pool k-1 to the arrival at pool k+1). The mask is a porcelain half-ellipsoid with a canvas texture (painted closed eyes, the red smile line also in the emissive map, a hairline crack drawn up to `crackAt(t)`). Night: two hanging lamps; the second flickers on at 12.55 s.
- `overlay.py`: text layer (JetBrains Mono, tracked caps, cream, soft halo; "SLOW LIGHT" watermark at 35%). WORK. FRIENDS. FAMILY. is one small line, each word arriving with its pool.
- `mix.py`: all sound synthesised in numpy (office murmur, distant laughter, phone buzz and tinny voice, breath, footsteps, ceramic creaks, crack, porcelain clink, lamp flicker, drone, final warm chord) plus one CC0 Freesound file from `../sfxlib/` (sleepCircle wind, as room tone).
- Floor mirror: the Reflector stops at z = 1.0 (it showed stray gold streaks in the near floor of the wide night shot).
