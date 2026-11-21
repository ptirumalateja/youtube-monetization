# Respect this woman (Slow Light replica)

Faithful replica of Teja's ref (21 Nov 2026): husband digs in the BUSINESS pit, wife holds the FAMILY (+TRUST) boulder, both turn down temptation, he climbs out with the diamond, the boulder shatters. Paper-cut look (cream sky, teal paper ground), beats matched to the ref's 4 fps timing, plus a 2.6 s end card.

- `scene.html`: canvas `renderAt(t)`; silhouette rig (`P` poses, `drawFig`), camera keys `CAM`, dialogue `LINES`.
- `render.js`: `node render.js video /abs/path/out.mp4 30 4` (~1 min) or `node render.js stills dir t...`. Use an absolute output path.
- `events.json`: pickaxe hit times exported from `window.EVENTS`.
- `sfx.py out.wav`: SFX bed (born-rich foley in `sfx/` + synthesized rumble/boom/shatter/pop/chime).
- Mux: `ffmpeg -i silent.mp4 -i sfx.wav -c:v copy -c:a aac -b:a 192k -shortest out.mp4`.
