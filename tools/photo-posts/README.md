# Photo posts (16 Nov 2026)

- `jupiter_still.py OUT.jpg 1080 1350 3` with `JBDIR=tools/jupiter-bodyguard` (branch claude/project-thread-1q4tlb), `JB_TEX=<textures>`, env `JZ=-70 JY=5.8 TY=7.9`. Then `jupiter_comp.py OUT.jpg.npy earth-has-a-bodyguard.png` (bloom, sky lift, text, watermark).
- Sorry still: `tools/sorry-five-letters` (branch claude/project-thread-bcntm0) with `toDataURL('image/png')` and the SLOW LIGHT label moved to design y 1034 (alpha 0.42); `W=2160 H=3840 SUB=4 TIMES=1.1 node render.cjs stills`, crop design y 160-1060, resize to 1080x1350.
- `earth_dot_carousel.py`: run in a folder with frames `f_<t>.png` grabbed from `scale_ladder_3d_v4_A.mp4` at 1.6, 4.2, 10.5, 16.8, 21.6, 25.3 s; crops y 200-1550, lifts the sky, adds n/6 and the swipe cue.

# Lobster (25 Nov 2026), first animal-parables post

- Image: OpenArt GPT Image 2 (text2image, 4:5, 2k, medium, 40 credits), folder "Slow Light photo posts"; prompt in the OpenArt history. A procedural 3D attempt (`lobster/`, `node still.cjs OUT.png W H`) is kept for reference; it read as a toy, so the owner chose OpenArt.
- `lobster_comp.py IN.png OUT.png`: crop to 1080x1350, warm the highlights toward gold, lift shadows to deep teal (no black border), headline in Inter Medium + Lora Italic (`fonts/`, OFL), SLOW LIGHT watermark. Copy: `publish-copy/lobster-photo-post.md`.

# Same Size (25 Nov 2026), corridor illusion

- v1 flat: `same_size_illusion.py OUT.png`.
- v2 3D (the one to post): `cd corridor && QS=mode=corridor node still.cjs C.png 2160 2700 && QS=mode=figure node still.cjs F.png 1200 2400`, then `python3 same_size_3d.py C.png F.png OUT.png`. The figure sprite is pasted twice at the same height (360 px in the post); the far copy is only tinted and rim-lit.
- v3 raw (the one to post): `same_size_sketch.py OUT.png`, a hand-drawn ink sketch on notebook paper (Caveat handwriting in `fonts/`, OFL).

# Pencil vs Pen (25 Nov 2026)

- `pencil_vs_pen.py OUT.png`: notebook page; pencil words rubbed out (eraser strokes, smudge, crumbs), the last line in ballpoint circled in red. Caveat handwriting (`fonts/`, OFL).
