# Someone Knew 4 Days Early (PHP2Shell reel)

Slow Light news reel. 15.0 s, 1080x1920, 30 fps, wordless, loops. Dark red theme (Teja's ask for this reel; it overrides the usual "red only for markers" palette rule).

The reading of "the PHP attacks shaking the world": PHP2Shell (CVE-2026-109618 and CVE-2026-109619), two unauthenticated remote code execution flaws in PHP itself, leaked on 20 Oct 2026, patched 21 Oct, and exploited in the wild, with the first attempt seen on 17 Oct.

## Files

- `prep.py`: builds `data/world.npz` (hex dot-matrix land from Natural Earth 50m land, 2,600 illustrative host points clustered around Natural Earth populated places, spread order from the seed with long jumps). Download the two Natural Earth GeoJSON files into `data/` first (see the docstring); they are not committed.
- `timeline.py`: beat times shared by picture, text and sound.
- `render.py`: numpy/scipy renderer. Tilted map plane under a pinhole camera; land dots, lat/lon grid, scan sweep, host pings (flash, ring, steady flicker), heat glow, parabolic arcs with comet heads, dust above the plane for parallax, hit shockwave, bloom, vignette, grain, chromatic split on hits. 3 motion-blur sub-frames. About 6 s/frame on CPU; `--workers 4` renders 450 frames in about 35 min. Skips frames that exist, so it can resume.
- `text.py`: HUD (PHP2SHELL chip, LIVE, date ticker 17 to 22 Oct, "ILLUSTRATIVE MAP"), typed headlines with glitch characters, counters, "ATTACK #1" target brackets, dark band behind the lower text.
- `sound.py`: fully synthesised mix (no samples, so no licences): drone that thickens with the spread, 1.5 s beacon throb synced to the seed ring, one blip per host lighting up (becomes crackle), arc chirps, typing and counter ticks, glitch stutters, riser, 0.5 s held breath, hits at 0.0, 9.0 (biggest) and 9.65, reverse swell into frame 0.
- `qa.py`: asserts the counters are monotonic.

## Beats

| Time (s) | Picture | Text |
|---|---|---|
| 0.0-2.2 | Close on one red ping with target brackets "ATTACK #1 · 17 OCT 2026", slow push | SOMEONE KNEW / 4 DAYS EARLY. + FIRST ATTACK SEEN 17 OCT / BUG MADE PUBLIC 21 OCT |
| 2.2-3.6 | Snap pull-back, Europe lights up, first arcs leave the seed | THE HOLE IS IN / PHP. |
| 2.7-4.4 | Spread jumps to other continents | 69.3% OF WEBSITES RUN ON IT |
| 5.2-8.5 | Camera pans east, map fills | ATTACKS ARE / SPREADING. + 1,886,612 PHP SERVERS FACING THE INTERNET |
| 8.5-9.0 | Held breath: everything dims | (none) |
| 9.0-11.2 | Biggest hit, shockwave crosses the planet | NO PASSWORD. / ONE REQUEST. + CRITICAL · CVSS 9.2 · REMOTE CODE EXECUTION |
| 11.2-13.0 | Pan west | HIDDEN IN PHP / SINCE 2012. + FIXED: 8.2.35 8.3.36 8.4.27 8.5.12 · UPDATE PHP NOW |
| 13.0-15.0 | Lights drain far to near, camera flies home to the first ping | SO WHO / KNEW? |
| 15.0 | Matches frame 0 (loop) | |

Facts, sources and publish copy: `publish-copy/php2shell-who-knew.md`.

## Build

```
python3 prep.py
python3 render.py OUT/frames --workers 4
python3 sound.py OUT/sound.wav
python3 qa.py
ffmpeg -framerate 30 -i OUT/frames/f_%05d.png -i OUT/sound.wav -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p -c:a aac -b:a 192k -af volume=-1.5dB -shortest -movflags +faststart php2shell-who-knew.mp4
```
