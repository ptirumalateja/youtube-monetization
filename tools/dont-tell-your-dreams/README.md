# Don't Tell Your Dreams (Slow Light Dark)

15.0 s, 1080x1920, 30 fps. Copy: `publish-copy/dont-tell-your-dreams.md`. This is a shot-for-shot restaging of a reference reel the owner supplied, in the Silence Is Distance (v8) look. It is Canvas 2D, in a 720x1280 design space: a navy gradient with a warm wash and motes, a glossy ledge floor, glowing cream stickmen with ink faces, and a gold star. A first pass in the 3D Slow Light Dark look was dropped for this one, because the reference is 2D and this look matches its poses and faces far more closely. Every cut, beat and caption time in `timeline.json` was measured frame by frame from the reference. The song is "Don't Tell Your Dreams" by LOVIXX & STOSLIV. It is not in git and is not in the upload file: add it from the platform's music library.

```
cd tools/dont-tell-your-dreams && npm install                    # three@0.170.0 (playwright comes from the global install)
for w in 0 1 2 3; do OUT=/path/to/render SUB=3 node render.cjs frames $w 4 & done   # 450 frames (about 9 min)
OUT=/path/to/render W=360 H=640 SUB=1 node render.cjs stills      # the review times in timeline.json
python3 compose.py /path/to/render /path/to/deliver [song.mp3]    # _music-ready (silent, upload) [+ _song-preview, sync check only]
```

**Shots:**

| Time (s) | Shot | What happens |
|---|---|---|
| 0–2.17 | A | Wide. He holds the star among four smiling friends. A knife appears behind R1's back at 0.6. He turns and offers the star to L1. |
| 2.17–4.97 | B | Closer. R1 turns angry at 2.9 and L1 at 3.25. R1's hand reaches for the star from 3.6. |
| 4.97–5.9 | C | He shows L1 the star again. At 5.2 his face turns worried, the star dims, and he pulls it back. |
| 5.9–7.63 | D | Push in. He hugs the star, scared, with angry faces over him, knives, and speed lines. |
| 7.63–11.27 | E | Close-up. Scared; eyes closed at 8.0 as the star sinks into his chest; eyes open, determined, at 9.47; arms down from 9.8; push in from 10.5. |
| 11.27–15 | F | Wide. He steps forward and the friends shrink back. At 12.97 the light bursts from his chest. They cartwheel out and land flat with dazed X eyes; their knives fly and land. |

**Code notes:**
- `scene.js` uses a front-view rig in world px: the hero is 860 tall at s = 1.
- Arms are 2-bone IK to a hand target. A hand-placed elbow is used for the hug.
- The camera per shot is `{cx, z, fy}`.
- The blast rotates and moves the whole skeleton about the hip.
- The lyrics, the speed lines and the white flash are drawn in the same canvas.
