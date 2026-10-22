# Stickman: He Moved a Mountain (reel, concept #6 "habit time-lapse")

Slow Light stickman series. 25.0 s, 1080x1920, 30 fps, wordless (no voiceover, no music in the file), loops.
Brief: a wireman does one tiny action every day while the world around him ages, and the last frames reveal what it built. It had to feel different from One Step a Day (`one-step-a-day.md`): a different habit and a sharper reveal.

- Source: `tools/one-hammer/` (`index.html` scene with `window.renderAt(t, samples)`, `render.js`, `shot.js`, `times.js`, `mix.py`, `compose.py`)
- Final file: `final-reels/he-moved-a-mountain.mp4` in the project files (not in git), contact sheet `final-reels/he-moved-a-mountain_contact_2fps.jpg`

## 1. Concept

One idea: **one hammer strike is nothing; 22 years of them is a road through a mountain.** It is a true story. From 1960 to 1982 Dashrath Manjhi cut a path 110 m long, 9.1 m wide and up to 7.7 m deep through a ridge near Gehlaur, Bihar, with a hammer and chisel. People called him a lunatic. His road cut the trip between the Atri and Wazirganj blocks from 55 km to 15 km.

How it differs from One Step a Day:

| | One Step a Day | He Moved a Mountain |
|---|---|---|
| Habit | sets one stone (adds) | strikes one blow (removes) |
| Space | climbs up into the sky | cuts into the rock, walls rise around him |
| Aging | crowd stops laughing, sunrise | the walls behind him weather and green, trees grow on the rim, he stoops and greys |
| Reveal | the stair seen from above | the last wall bursts, dawn floods the cut, then the map: 55 km old road vs 15 km his road; "true story" |
| Loop | a crowd member starts his own stair | the world rewinds 22 years back to the first strike |

- **Hook (0-1.7 s):** first strike on frame 2 with a canyon-sized hit; "ONE MAN. / ONE HAMMER. / ONE MOUNTAIN." typed by 1.7 s over a small figure at the foot of a ridge.
- **Monotonic counters:** red YEAR chip 1960 to 1982 and "M CARVED" 0 to 110, asserted to only go up in `compose.py`.
- **Retention engine:** the viewer cannot see the far side until the break; the counter tells them it is coming; a held breath with light leaking through a crack sets up the payoff.
- **Beat drop:** the last strike and the wall bursting are at **16.60 s (frame 498)**. The sound mix has a near-silent held breath 16.0-16.6 s and the biggest hit at 16.60 s, so any track can be lined up with its drop there.
- **Thesis line:** "HE MOVED A MOUNTAIN." with the "TRUE STORY: DASHRATH MANJHI / GEHLAUR, BIHAR, 1960-1982" tag.

## 2. Look

- **Character:** the series' ivory tube stickman, a wooden hammer and an iron chisel. He ages: the stoop grows, the knees bend, the head drops and the ivory greys.
- **World:** a granite ridge (a heightfield carved live every frame: the cut is 9.1 m wide and follows the front of the work), dusty floor, fresh pale rock at the face that weathers to green-grey behind him over the years, trees on the rim that grow from saplings, a village with growing debris heaps at the mouth, a town on the far side that only exists once it can be seen.
- **Light:** side light for the hook; behind-camera sun during the work, whose shadows sweep across the cut (the time-lapse cue); dusk and night for the last strikes; a low dawn sun straight down the cut on the far side, so the last wall holds the cut in shadow until it breaks.
- **Palette:** charcoal/navy night, warm granite, cream text, gold for his road, red only for the YEAR chip and the old road.

## 3. Shot plan (one continuous camera, no cuts)

| Time (s) | Shot | Counter | Text |
|---|---|---|---|
| 0.0-2.4 | Low, behind and to the right of him at the ridge foot; the ridge rises to a peak on the left. First strike on frame 2, then 0.8, 1.55, 2.3 s. Slow push. | 1960, 0 M | ONE MAN. / ONE HAMMER. / ONE MOUNTAIN. (typed by 1.7, out by 3.4) |
| 2.3-3.8 | Camera rises behind him into the follow position over the cut; strikes speed up. | | |
| 3.8-14.2 | Time-lapse. Strikes blur, the face retreats, the walls rise, the camera lags further and further behind (11 m to 37 m) so the cut behind him grows in frame; sun shadows sweep; rim trees grow; walls weather. | 1960 to 1981, 0 to ~105 M | THEY CALLED HIM MAD. (6.4-9.8) |
| 14.2-15.6 | Dusk. The camera rushes in close behind him at the last wall. | 1981 | |
| 15.0-16.0 | Night: three slow strikes ringing in the dark, crickets. | | |
| 16.0-16.6 | Held breath: one slow raise of the hammer; a thin line of dawn light grows up the wall (the crack). | | |
| **16.6** | **The last strike. The wall bursts outward, dawn floods the cut, debris and dust fly away into the light. (Beat drop.)** | 1982, 110 M (pulse) | |
| 16.6-18.6 | Slow push past him; he lowers the hammer and looks into the light; the town is there. | | 22 YEARS. / ONE HAMMER AND CHISEL. (17.3) |
| 18.6-21.6 | Crane up and back to a high view of the whole ridge: his gold road straight through, the old road (red dashes) round the end of the ridge, village below, town above; three people walk his road. | | HIS ROAD 15 KM / OLD ROAD 55 KM / ROUTES NOT TO SCALE (20.0) |
| 21.6-23.6 | Hold and drift. | | HE MOVED / A MOUNTAIN. + true-story tag (21.7-23.5) |
| 23.6-25.0 | Dive home while the world rewinds 22 years (the cut fills back in, the trees shrink); lands on the frame-0 shot. | hidden | |

World time `tau(t)` equals video time until 23.6 s and then runs back to 0, so frame 750 is frame 0. The cut's progress, the strike clock and both counters come from one set of monotone curves (`times.js` exports them to `timing.json`).

## 4. Facts and sources

| On screen | Value | Source |
|---|---|---|
| 22 years, 1960-1982 | "He completed the work in 22 years (1960-1982)" | Wikipedia, Dashrath Manjhi |
| 110 m carved | 110 m long, 9.1 m wide, 7.7 m deep (the scene uses these dimensions) | Wikipedia, Dashrath Manjhi |
| Hammer and chisel | "using only a hammer and a chisel" | Wikipedia |
| They called him mad | Manjhi: "people called me a lunatic" | Wikipedia |
| 55 km became 15 km | Atri to Wazirganj blocks, Gaya district | Wikipedia |
| Routes not to scale | the map compresses 55 km into one ridge-end detour | tag on screen |

The year counter runs evenly through the 22 years and the metres carved run with it; that pacing is a dramatisation (the real work rate is not documented). The stickman is a tribute, not a likeness. His wife's death (the reason he began) is left out of the reel on purpose; it belongs in the description.

## 5. Sound ("iron and stone", all synthesised in `mix.py`, no third-party files)

- Every strike has a sound: a hammer-on-chisel ping (inharmonic metal partials and a click) and a rock thunk; at time-lapse speed they become a metallic whir that climbs slightly with the years.
- Frame-2 hook strike with a canyon boom (130 to 52 Hz pitch drop).
- Low A drone and a soft shepard riser under the work; wind through the cut with gusts.
- Dusk: a camera rush, then three slow strikes with a long tail, crickets.
- Held breath 16.0-16.6 s: near silence, a creaking crack that grows with the light, a 50 ms vacuum.
- Break at 16.60 s: rock burst, pitch-drop body, sub, debris rattle, with reverb and a duck on the bed. This is the beat drop.
- Dawn birds and a quiet A-major chord under the reveal, kept low so a music track sits on top; a soft shimmer as the routes draw; a struck-stone (lithophone) note under the end line.
- Rewind: the whir played backwards and pitched up, a reverse whoosh and a rising tone into the frame-0 strike (closes the loop).
- No Instagram music is in the file. To add a track: line its drop up with 16.60 s and lower the original audio to about 30-40% in the app.

## 6. Pipeline (rebuild)

```
cd tools/one-hammer
npm i three@0.170.0 playwright-core     # or symlink an existing node_modules; not committed
pip install numpy pillow scipy
python3 -m http.server 8821 &
node shot.js 540 960 /tmp/shots 8821 0.03 6 12 16.7 20.5 22.5        # stills
node times.js 8821 timing.json                                      # strike times + per-frame year/metres
for i in 0 1 2 3; do node render.js 1080 1920 /tmp/frames 8821 $i 4 & done   # 750 frames, native 1080x1920
python3 mix.py timing.json /tmp/mix.wav
python3 compose.py /tmp/frames timing.json /tmp/mix.wav he-moved-a-mountain.mp4
```

Render: three.js r0.170, headless Chromium + SwiftShader, PCF soft shadows (the shadow box follows him, then grows to 190 m for the wide), Unreal bloom (0.36-0.5), ACES tone mapping, 3 motion-blur sub-frames (5 in the time-lapse, the break, the crane and the dive). The terrain is a 128k-vertex non-uniform grid (0.1 m across the cut) re-carved on the CPU each sub-frame.

## 7. Publish copy

**YouTube Shorts title:** He Hit a Mountain Every Day for 22 Years #shorts

**YouTube description:**
> One man. One hammer. One mountain.
> In 1959 Dashrath Manjhi's wife Falguni Devi was badly hurt in a fall on the ridge outside their village, and she died. The nearest town with a doctor was far away round the ridge. In 1960 he started cutting a path through the ridge with a hammer and chisel. People called him mad. In 1982 he broke through: 110 m long, 9.1 m wide, up to 7.7 m deep. The trip became 15 km.
> They call him the Mountain Man.
>
> A Slow Light tribute: real dimensions, routes not to scale. All visuals and sound made by Slow Light.
>
> #MountainMan #DashrathManjhi #consistency #discipline #stickman #animation #truestory #shorts

**Instagram / Facebook caption:**
> He hit a mountain every day for 22 years. ⛏️
> 110 m of rock. One hammer and chisel. 55 km became 15 km.
> True story: Dashrath Manjhi, Bihar, 1960-1982.
> #mountainman #dashrathmanjhi #consistency #stickman #reels

**Pinned comment:** What would you keep hitting for 22 years?

**Upload settings:** 9:16, AI/synthetic media label on (synthetic scene), no music claimed in the file; if you add a track in Instagram, put its drop at 0:16.6.

## 8. QA (final render, 22 Oct 2026)

- File: `final-reels/he-moved-a-mountain.mp4`, 1080x1920, 30 fps, H.264 CRF 18 + AAC 256k, 25.0 s, 18.6 MB (under the 30 MB chat limit). Contact sheet: `final-reels/he-moved-a-mountain_contact_2fps.jpg`.
- Frame 0 is moving and the first strike lands on frame 2; hook fully typed by 1.7 s.
- YEAR 1960 to 1982 and 0 to 110 M CARVED asserted monotonic frame by frame in `compose.py` (hidden during the rewind); 1982 / 110 M lands on the break frame (498). Typed text never uses a negative slice.
- The counter sits under the hook lines (y 590) so it never covers him; all text stays above the bottom 18%.
- Audio after AAC: -15.7 LUFS integrated, LRA 8.6 LU, true peak -0.9 dBTP. Held breath 16.0-16.6 s; one biggest hit at 16.60 s (the beat drop).
- Loop: the last frame is the frame-0 camera on the ridge foot with the cut filled back in.
- Known soft spots for a v2: the break frames are hazy (low dawn sun straight into the lens); the 3.4-4.4 s rise behind him is soft from motion blur; the town is simple blocks.
