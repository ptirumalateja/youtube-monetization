# Born From Static (AI Art reel)

Slow Light explainer reel, 15.0 s, 1080x1920, 30 fps, wordless, loops. Made for the "AI Art" topic that Facebook's creator assistant flagged as popular with the page's followers.

Idea: AI image generators don't draw; they start from static and delete noise step by step. The reel shows a painting appearing out of static in 50 steps, then buries it in noise again (the training direction), which lands back on frame 0.

## Files

- `paint.py`: the hidden picture, procedural numpy (ringed planet rising over a sea, aurora, lone cloaked figure on a cliff). About 20 s.
- `timeline.py`: beats and the noise schedule shared by picture and sound. Step k is held for 4 frames; log-SNR rises with the step; the forward (training) section ramps log-SNR back down to frame 0's value.
- `render.py`: frames piped into ffmpeg. `x = s*image + sqrt(1-s^2)*noise` with 2x2-pixel static (part colour, part mono), fresh noise each step (each frame in the static and training sections), a blur on early steps so it reads coarse-first, slow push-in, held breath dim, 9.0 s flash. Captions (Liberation Mono Bold, cream with black stroke, typed with a red cursor) and the prompt/step HUD. `--notext` renders the clean plate; `--frame=N` writes test stills.
- `sound.py`: fully synthesised (no samples, no licences). Static hiss that drops with each step, step ticks, typing clicks, "tones from noise" (narrow bands of the hiss at the chord notes), a D major add9 pad that opens as the picture clears, held breath, the big hit at 9.0 s, hiss sweep back into frame 0.

## Beats

| Time (s) | Picture | Text |
|---|---|---|
| 0.0-2.0 | Pure static (a 3.5% hint of the picture), STEP 00/50, prompt types in | AI ART STARTS / AS PURE STATIC. |
| 2.0-8.5 | Steps 1-49: big shapes first, then detail | IT DOESN'T / DRAW. then IT DELETES NOISE. / STEP BY STEP. |
| 8.5-9.0 | Held breath, picture dims, near silence | (none) |
| 9.0-11.6 | STEP 50/50, hit, clean painting | UNTIL ONLY / A PICTURE IS LEFT. |
| 11.6-15.0 | TRAINING: +NOISE, picture is buried again | IT LEARNED THIS / BY BURYING BILLIONS / OF IMAGES IN NOISE. |
| 15.0 | Static again = frame 0 (loop) | |

Facts, sources and publish copy: `publish-copy/born-from-static.md`.

## Build

```
python3 paint.py OUT/painting
python3 render.py OUT/painting.npy OUT/video_text.mp4
python3 render.py OUT/painting.npy OUT/video_notext.mp4 --notext
python3 sound.py OUT/sound.wav
ffmpeg -i OUT/sound.wav -af "loudnorm=I=-15:TP=-2:LRA=11,alimiter=limit=0.79:level=false" OUT/sound_norm.wav
ffmpeg -i OUT/video_text.mp4 -i OUT/sound_norm.wav -c:v libx264 -preset slow -b:v 14M -maxrate 16M -bufsize 28M -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -movflags +faststart born-from-static.mp4
```

Full-frame static is expensive to encode: the share file needs about 14 Mbps to stay clean and under 30 MB; the master is CRF 16.
