# Don't Tell Your Dreams (Slow Light Dark)

15.0 s, 1080x1920, 30 fps. Copy: `publish-copy/dont-tell-your-dreams.md`. This is a shot-for-shot restaging of a reference reel the owner supplied, in the series look: dark void, one gold lamp, cream stickmen, ink faces, and a gold star as the second light. Every cut, beat and caption time in `timeline.json` was measured frame by frame from the reference. The song is "Don't Tell Your Dreams" by LOVIXX & STOSLIV. It is not in git and is not in the upload file: add it from the platform's music library.

```
cd tools/dont-tell-your-dreams && npm install                    # three@0.170.0 (playwright comes from the global install)
for w in 0 1 2 3; do OUT=/path/to/render node render.cjs frames $w 4 & done   # 450 frames
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
- `sld.js` is the kit file plus two additions: `F.rs` (limb radius) and `F.hs` (head size). The scene sets figure size by scaling the skeleton about the root (`skelS`): the hero is 0.82 with a full-size head and ink hair strands, and the friends are 1.06.
- `overlay.py` draws:
  - The song's four lines at the reference's frames, lower third.
  - The speed lines in shot D.
  - The white burst flash.
