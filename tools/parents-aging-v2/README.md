# Parents reel V2: "Your Parents Are Aging While You Are Busy"

A 19 s, 24 fps, 1080x1920 reel, one file for FB, IG and YT. It is built on Teja's V2 brief: one table under one warm lamp, three ages (8, 18, 25), no split screen, then the empty chair and "CALL NOW.". V1 lives in `../parents-aging/`.

- `timeline.json`: every time in the reel (scenes, actions, text, phone pills, calendar, cameras).
- `scene.js`: the three.js scene on the Slow Light Dark kit (`sld.js`, with `setScale` for the growing kid).
- `render.cjs`: headless render (`stills`, `meta`, `frames WORKER N`).
- `overlay.py`: text, calendar tag and phone pills (PIL). `mix.py`: synthesised sound, one ring at 15 s, silence from 16 s.
- `compose.py OUT DELIVER`: writes `parents-19s-v2.mp4` (-15 LUFS) and `parents-19s-v2_music-ready.mp4`.

Render: `npm i`, then `node render.cjs meta OUT`, 4x `node render.cjs frames OUT W 4`, `python3 mix.py OUT`, `python3 compose.py OUT OUT/deliver`. That is about 25 minutes on 4 CPUs.
