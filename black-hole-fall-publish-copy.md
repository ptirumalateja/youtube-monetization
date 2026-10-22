# Falling In (black hole hero reel)

18 s, 1080x1920, 30 fps, loops. One subject, one continuous camera move: a slow fall toward a black hole. The only text is a hook line and a closing line. Source: `tools/black-hole-fall/` on branch `claude/project-thread-r728nz`. Frames and intermediate files are not in git.

## Files
- `black-hole-fall.mp4`: share encode with the sound bed
- `black-hole-fall_silent.mp4`: same picture, no audio (so you can lay a trending sound over it)
- `black-hole-fall_master.mp4`: CRF 14 master with sound
- `black-hole-fall_contact_2fps.jpg`: contact sheet, 2 frames per second
- `black-hole-fall_preview-stills.jpg`: first and last frame stills

## Text
| Time | Line |
|---|---|
| 0.0-0.75 s typed, gone by 3.4 s | `YOU'RE FALLING IN.` |
| 13.4-17.1 s | `NOTHING COMES BACK.` |

When the reel loops, the closing line leads straight back into the hook.

## The shot
- The camera falls from 90 to 33 black-hole masses out (45x to 16x the horizon radius). It drifts about 40° around the hole and sinks from 18° to 8° above the disk. The fall speeds up gently and is already moving on frame 0.
- Each pixel's light path is integrated through Schwarzschild spacetime (exact null-geodesic equation, RK4). Because of that, the far side of the disk arches over the top, a second image of the disk wraps under the shadow, stars near the hole smear into rings, and the shadow grows as the camera falls. None of it is drawn by hand.
- The disk is volumetric: turbulent streaked gas that rotates differentially (inner gas faster), with cool dust lanes and Doppler beaming, so the approaching side is brighter and whiter. The palette runs white-gold inside to amber and rust outside.
- The sky has a deep blue-violet galaxy band with dark dust lanes and about four layers of fine stars. Two faint dust layers in the foreground drift outward at the frame edges to give parallax. The grade adds bloom, ACES tone mapping, a navy black lift, a vignette and grain (the grain also dithers away banding).
- Loop: the last 0.8 s dissolves into a pre-roll rendered just before frame 0, so the last frame flows into the first.

## Honest simplifications
- The hole doesn't spin (Schwarzschild). The disk's inner edge sits at 3.4 masses for drama, where a real non-spinning disk would stop at 6.
- The camera is a static observer at each point. It ignores the aberration a truly free-falling camera would see.
- The thin photon ring at the shadow edge gets a small artistic boost on top of the traced disk light.
- Doppler beaming is softened (g^2.6 and compressed) so the dim side still reads.
- The galaxy and dust are procedural, and the scale is not real.

## QA and known soft spots
- I checked frame-to-frame change across all 564 frames: there are no pops or flicker (the mean difference stays flat at about 4/255, which is mostly grain). I saw no banding in the encoded file, and stars smear into smooth arcs, not dotted lines.
- **Soft spot 1:** the strip of disk that crosses in front of the hole is noticeably softer and less detailed than the streaked gold arch above it. That's partly real, since it's seen nearly edge-on, but it's the least crisp part of the frame, especially in the last 4 s.
- **Soft spot 2:** the loop is a 0.8 s dissolve from the close view back to the far view, not a seamless cut. It reads as a breath out, but it's visible.
- **Soft spot 3:** the photon ring is a hairline. It shows on the top edge of the shadow and fades where the front of the disk covers it.
- Sound: -16.9 LUFS integrated, -3.0 dBTP true peak, measured after AAC.

## Sound
`sound.py` synthesises everything, so there are no samples and nothing to credit. It's a deep A drone with slow beating, a breathing space-wind noise bed, drifting glass partials, a soft sub swell on frame 0 and a gentle rise over the last 6 s. The tail crossfades into the head so it loops.

## Publish copy
- **Title:** What falling into a black hole looks like
- **Caption:** You're falling in. Every ray of light in this shot is bent by the black hole's gravity: the glowing arch over the top is the far side of the disk, pulled up and over the hole toward you. Watch it till the end, then watch it again.
- **Tags:** #blackhole #space #astrophysics #interstellar #universe #physics #science #shorts
- Label as AI/synthetic content on upload (computer-generated visualisation).

## Rebuild
```
cd tools/black-hole-fall
gcc -O3 -march=native -ffast-math -fopenmp bh.c -o bh -lm
./render.sh OUT 1080 1920 2 -24 539        # frame f at t = f/30 s; -24..-1 is the loop pre-roll (~40 s/frame on 4 cores)
python3 sound.py bed.wav 18
python3 assemble.py OUT 1080 1920 | ffmpeg -f rawvideo -pix_fmt rgb24 -s 1080x1920 -r 30 -i - -i bed.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart black-hole-fall.mp4
```
