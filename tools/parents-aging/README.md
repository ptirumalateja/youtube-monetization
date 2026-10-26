# Your Parents Are Aging While You Are Busy (Slow Light Dark)

The third reel of the Friends → Salary → Parents trilogy. 19 s master (`timeline.json`) and a 26 s FB cut (`timeline-26s.json`) from the same scene. 1080x1920, 30 fps. Copy: `publish-copy/parents-aging.md`. Look: the 30 Friends to 1 kit (`../slow-light-dark-common`). `sld.js` is a copy of it with one addition: `R.setScale(body, head)`, so a single rig can pose a growing child, Mom (0.93) and Dad.

```
cd tools/parents-aging && npm install
OUT=/path/r19 node render.cjs meta                                  # per-frame AGE / PARENTS (monotonic, gap 30 checked) + call labels
for w in 0 1 2 3; do OUT=/path/r19 node render.cjs frames $w 4 & done  # 570 frames, 3 motion-blur sub-frames (about an hour on 4 CPUs)
python3 mix.py /path/r19/meta.json /path/r19/mix.wav
python3 compose.py /path/r19 /path/deliver                          # parents-aging.mp4 (-15 LUFS, true peak checked) + _music-ready.mp4
# 26 s FB cut: prefix every command with TL=timeline-26s.json (slug parents-aging-26s)
OUT=/tmp/x W=540 H=960 SUB=1 TIMES=0,5.6,8,14.5,18.9 node render.cjs stills   # quick look
```

- `scene.js` (`renderAt(t)` is pure): **shot A** (0 to `cut`): Mom hands the boy the tiffin, he hugs her and grows up in the hug (8 → 18), Dad stands, he walks off into the dark. **Shot B**: hard cut to a wide shot of two lamps, the parents' gold one and his cool one far back over his desk and the Salary Loop's plaid bed. Each entry in `calls` is a gold light crossing the dark (`in` = Mom calls: she lifts the receiver, his phone buzzes; `ans` picks up, `flip` turns the phone face down; `out` = he calls and the red phone rings). The parents grey (hair caps) and stoop, and Dad gets a stick at `stick`. The push-in at `push` ends on the two of them, the covered plates and his pushed-in chair. The lamp narrows onto the red phone at `narrow`, it rings once at `ring`, and Mom's hand goes to it.
- `overlay.py`: the hook (frame 0), AGE / PARENTS counter, call labels over his lamp, the payoff, "CALL NOW.", watermark.
- `mix.py`: synthesised soft piano (thins with the years and stops before the end), birds, the tiffin, footsteps, the lamp click, the receiver clacks, the shimmer of each call, the phone buzz, the bell, the clock, one ring, then `silence` (everything, room tone included, at zero until the end).
