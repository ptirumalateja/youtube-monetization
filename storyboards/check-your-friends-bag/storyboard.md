# Stickman: Check Your Friend's Bag (Invisible Backpack, Part 2)

Slow Light stickman series. 20 s, 1080x1920, 30 fps, wordless (no voiceover, on-screen text only).
Part 1, "The Invisible Backpack" (18 s), ends with the white stickman on top of his 7-step rock staircase, a small lamp on the top step, his empty bag below and the blue crowd looking up. **Part 2 opens on that exact frame.**

- Source: `tools/check-your-friends-bag/` (`index.html` scene with `window.renderAt(t, samples)`, `browser.js`, `render.js`, `shot.js`, `times.js`, `compose.py`, `mix.py`, `sfx/`)
- Final files (not in git): `final-reels/check-your-friends-bag_master.mp4`, silent `check-your-friends-bag_music-ready.mp4`

## 1. Concept

One idea: **reaching the top is not the end; the stairs you built can carry someone else.**

He made it. Then he looks back and sees a friend still bent under a bag almost twice his size. He walks back down his own stairs, doesn't open the friend's bag for him, just taps his shoulder and points at the staircase. The friend opens his own bag and hands over the first rock, ALONE. They set it together as the friend's step 1, then build side by side until both stand at the same height, joined by a bridge made of the last rock, TOO LATE, laid flat.

- **Hook (0-1.8 s):** "YOU MADE IT." then "NOW LOOK BACK." over Part 1's last frame; the wind cuts out and a soft piano comes back. A small "PART 2 · IF YOU SAW PART 1..." tag for 3 s.
- **Monotonic counter:** blue ROCK chip, 1 to 7, one tick per blue step (asserted in `compose.py`).
- **Paradox beat:** success isn't staying on top.
- **Thesis line:** "YOUR STAIRS CAN BECOME / SOMEONE ELSE'S BRIDGE."
- **Series link:** the last frame shows two more blue figures looking up: the next ones still carrying something.

## 2. Shot plan (frozen before the build)

| Time (s) | Shot | Action | Text / sound |
|---|---|---|---|
| 0-0.35 | Part 1 final frame (`CFG.cam0`) | He stands on top, lamp lit | "PART 2 · IF YOU SAW PART 1..." tag; wind stops; piano |
| 0.35-3.0 | Swing to a high angle over his shoulder | He turns and looks down: the blue friend, bent double, staggers under a ghost bag almost twice his size | "YOU MADE IT." (0.15) / "NOW LOOK BACK." (1.25), out by 3.05 |
| 3.0-3.55 | Fast drop to the friend | | drop whoosh |
| 3.35-5.9 | Close, X-ray on (cyan scan, world dims) | The bag glows; inside: NO ONE CARES / ALONE / TOO LATE / TIRED / EVERYONE AHEAD (stacked labels) plus filler rocks; the bag shakes; he drops to his knees at 5.55 | "SOMEONE ELSE IS / STILL CARRYING IT."; breathing, heartbeat, rattles, knee thud |
| 6.0-9.75 | Side tracking, moving toward -x (reversed from Part 1) | He walks DOWN his 7 steps, each flares warm as he leaves it, then walks to his friend | "SUCCESS ISN'T / STAYING ON TOP."; a descending chime per step |
| 10.15-13.6 | Close two-shot from the gap between the stairs (facing the friend) | He kneels, taps the friend's shoulder twice, points at the stairs. The friend takes off his own bag, opens it, lifts ALONE out; they carry it together and set it as blue step 1 (13.4) | "IT'S SHOWING SOMEONE / ELSE HOW TO BUILD."; taps, rustle, **first clink** + chord, ROCK 1 |
| 13.6-17.6 | Wide 3/4 time-lapse | The friend's rocks fly into the white stickman's (Part 1) bag; then step by step he hands one across the gap, the friend sets it and both step up together. Steps 2-7 at 14.85 / 15.3 / 15.75 / 16.2 / 16.62 / 17.05 | ROCK 2..7; "ONE ROCK AT A TIME. / TOGETHER."; rising clinks |
| 17.6-18.3 | Pull-back begins | Both on their top steps; he takes TOO LATE out of his bag; held breath 17.75-18.3 | near silence |
| 18.3 | | Both kneel and lay TOO LATE flat across the gap: a bridge. He drops the empty bag; it lands below next to the friend's | warm hit (clink + impact + D gong + sub), D major |
| 18.3-20.0 | Hero wide, wider than Part 1's last frame | They stand and look forward into the dawn; two blue figures below look up; two empty bags on the ground | "YOUR STAIRS CAN BECOME / SOMEONE ELSE'S BRIDGE." then fade to "PART 2 / slowlighttv"; bell |

## 3. Look

- Shared with Part 1 (values in the `CFG` block at the top of `index.html`; must match `storyboards/invisible-backpack/style-sheet.md`): stickman rig from One Step a Day (ivory hero, slate-blue crowd), floating rock-slab steps (rise 0.38 m, tread 0.50 m, width 0.95 m), lamp, pre-dawn navy world with ridges and stars, fog, fonts, Part 1's last camera.
- New in Part 2: the friend's staircase beside the white one (z = -1.75 m, 0.75 m gap), the friend's oversized ghost bag (0.62 x 1.12 x 0.78 m), the X-ray look (fresnel-rim shell, dim world), the bridge slab.
- **Colour story:** the friend's rocks glow dim amber/rust ("pain", not red: the playbook keeps red for markers) and turn calm blue as they become steps; the white staircase glows warm, the blue one cool; the bridge is half warm, half blue. The ROCK counter chip is blue (the friend's colour).

## 4. Sound ("breath and piano", linked to Part 1)

`mix.py`, numpy buses (piano, breath, heart, sfx, wind, hit, air), synced to `timing.json` exported from the scene.
- Part 1's wind cuts on frame 0; a soft felt-piano (synthesised) comes back and carries the reel.
- The friend's heavy breathing (shaped noise) until he is helped; a heartbeat under the X-ray that speeds up to the collapse and fades once help arrives.
- Bag rattles (stone clicks), a knee thud (ElevenLabs stone thud from One Step a Day).
- One descending chime per white step on the way down; two cloth taps; bag rustle; stone scrape.
- **First clink for the blue friend** at step 1 with a D major chord; the time-lapse clinks climb in pitch.
- Held breath before the bridge; one warm hit (clink + ElevenLabs impact + synth D gong + short sub); a bell under the end card.
- Delivery target about -15 LUFS integrated, true peak checked after AAC.
- If Part 1's final mix uses a specific wind or piano bed, swap it in here so the two parts join seamlessly (see the coordination note).

## 5. Pipeline (rebuild)

```
cd tools/check-your-friends-bag
npm i three@0.170.0 playwright-core          # node_modules not committed
python3 -m http.server 8822 &
node shot.js 540 960 /tmp/shots 8822 0 1.5 4.2 7.2 10.6 13.2 16.4 18.5   # stills
node times.js 8822 timing.json                                           # timeline for overlay + mix
for i in 0 1 2 3; do node render.js 1080 1920 /tmp/frames 8822 $i 4 & done   # 600 frames, native 1080x1920
python3 mix.py timing.json /tmp/mix.wav
python3 compose.py /tmp/frames timing.json /tmp/mix.wav check-your-friends-bag_master.mp4
python3 compose.py /tmp/frames timing.json none check-your-friends-bag_music-ready.mp4
```

## 6. Coordination with Part 1

Part 1 was built in parallel (session `session_017hQP4HA9HgeTnBvpQRwv2Z`). Part 2's v1 uses the One Step a Day rig and look with Part 1's recap as the guide; every value Part 1 owns sits in `CFG`. When Part 1's style sheet lands, update `CFG` (step size, colours, lamp, bag position, `cam0`) and the rock/bag/label builders if Part 1's differ, re-render, and re-check that frame 0 matches Part 1's last frame.
