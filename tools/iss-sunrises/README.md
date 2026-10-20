# 16 Sunrises a Day (ISS free fall)

Plan and facts: `/iss-sunrises-spec.md`. Publish copy: `/iss-sunrises-publish-copy.md`.

- `index.html`: three.js scene and in-page overlay. `window.renderAt(t)` returns a JPEG frame (motion-blurred 3D plus text). Procedural Earth with raymarched atmosphere, a procedural ISS, the orbit, and Newton's cannon arcs integrated with inverse-square gravity.
- `render.mjs`: headless Chrome (Metal GPU) renderer. `node render.mjs stills <dir> 0 1.5 ...`, `node render.mjs video <base.mp4>`, `node render.mjs events events.json` (sunrise and cue times for the score).
- `synth.mjs`: original synthesised score from `events.json`. `node synth.mjs events.json mix_raw.wav`.
- `mux.sh base.mp4 mix_raw.wav out.mp4`: two-pass loudnorm (-15 LUFS, TP -1.5), AAC, then prints loudness and true peak after encoding.
- `dbg.mjs`: evaluates an expression in the page (camera and station debug).

`node_modules` is a symlink to `../sleep-paralysis/node_modules` (three 0.170, playwright-core 1.56). If that is missing, run `npm i three@0.170.0 playwright-core@1.56.1` here. The full render takes about 22 minutes on the Mac.
