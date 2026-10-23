# Would This Ball Hit the Stumps? (paused WIP)

Three.js scene for the cricket predict-the-outcome reel. Serve this folder with three@0.170.0 in `node_modules/` and render headless like `tools/scale-ladder/render.js` (`window.renderAt(T, nsub)`, `window.info(T)` for overlay positions).

Frozen plan (19 s, loops):
- 0-2.0 hook: camera rides beside the spinning red ball, "YOU HAVE 3 SECONDS."
- 2.0-4.2 whip back to the broadcast camera behind the bowler; off-break pitches outside off, turns sharply, freezes 5 cm before the front pad.
- 4.2-7.4 countdown 3-2-1, "HITTING OR MISSING?"
- 7.4-13.7 batter ghosts out, camera goes plan view then end-on; dotted projected path grows, held breath just short of the stumps.
- 13.7-18.0 reveal: hit in line with off stump, still misses leg stump by about 1 cm; close-up of the gap.
- 18.0-19.0 rewind to frame 0.

Physics (simulated delivery): release 77 km/h from 2.05 m, pitches 3.6 m from the stumps at x=+0.25 m, 6.5 degree turn, impact at z=2.28 m x=+0.099 m (off-stump line), crosses the stumps plane at x=-0.162 m, y=0.54 m. Not yet test-rendered.
