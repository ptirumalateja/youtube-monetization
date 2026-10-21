# Stickman: One Step a Day (reel #12)

Slow Light stickman series. 17.5 s, 1080x1920, 30 fps, wordless (no voiceover), loops.
Ref topic: "They laughed until he reached the top" (14 s silhouette stickmen, a crowd laughing at a climber on a labelled tower, lightning ending). We keep only the theme. Everything else is ours: our own character, a floating stone stair in our navy world, a day counter, a sunrise above a cloud deck and a loop where one of the crowd starts his own stair.

- Source: `tools/one-step-a-day/` (`index.html` scene with `window.renderAt(t, samples)`, `render.js`, `shot.js`, `times.js`, `mix.py`, `compose.py`, `sfx/`)
- Final file: `final-reels/one-step-a-day.mp4` in the project files (not in git)

## 1. Concept

One idea: **a single step is too small to notice; a year of them is a building.**

He sets one stone step a day. The crowd laughs at day 1. The stones keep coming, the days blur, the laughter thins out and stops, he climbs through the clouds, and on day 365 he sets the last stone as the sun breaks the horizon. From the top, the stair falls away to a crowd that is now a speck. Then one of them picks up a stone. That frame is frame 0 again, so the reel loops.

- **Hook (0-1.5 s):** "DAY 1. / THEY LAUGHED." typed fast over the first stone thud and a burst of laughter.
- **Monotonic counter:** DAY 1 to 365 (red DAY chip + big number) and the height under it (0.2 M UP to 62 M UP). Both are asserted to only go up in `compose.py`.
- **Paradox beat:** each step is 17 cm, which nobody notices; 365 of them are 62 m, about a 20-storey building.
- **Thesis line:** "ONE STEP A DAY."
- **Loop:** the last frame (a crowd member, now ivory, setting his own first stone) matches frame 0 (our hero setting his first stone), same camera offset and the same pose phase.

## 2. Look

- **Character:** ivory stickman (tube limbs, sphere head, warm emissive so he reads on navy). The crowd is the same rig in slate blue. The one who starts his own stair fades from slate to ivory as he picks up his stone.
- **World:** pre-dawn navy ground and sky, three rings of distant ridges for parallax, faint stars, a patchy cloud deck at 35-40 m with a clear well around the stair, drifting gold motes (world-fixed, camera-wrapped, so they show true parallax).
- **Stone:** pale limestone blocks (30 cm tread, 17 cm rise, 1.15 m wide), slightly irregular; "today's" stone glows faint gold.
- **Light:** cool moonlit key with soft shadows; the Sun rises in the direction he climbs and clears the horizon on the last step (gold, capped bloom, no white-out).
- **Palette:** charcoal/navy, cream text, gold and teal accents, red only for the DAY chip.
- Not a repeat of any earlier reel (no tunnel, rings, galaxy or Earth). Stickman look is shared with the series on purpose; the scenes are new.

## 3. Shot plan (frozen before the build)

| Time (s) | Shot | Counter | Text |
|---|---|---|---|
| 0.0-2.2 | Close, low, side-on. He sets stone 1 on frame 2 (thud), picks up and sets stones 2 and 3. Crowd behind him, laughing, "HA" pops over their heads. Slow push. | DAY 1 to 3 | "DAY 1." / "THEY LAUGHED." (typed by 1.5 s, out by 3.3 s) |
| 2.2-4.2 | Days speed up (3 to 22). Camera rises and pulls back; the stair starts to trail behind him. Laughter thins. | 3 to 22 | |
| 4.2-10.6 | Time-lapse climb: stones appear in front of him dozens a second while he climbs with a stone in his arms. Camera follows from the side and above. Crowd falls away below. Through the cloud deck at about 8-9.5 s. | 22 to 357 | "THEY STOPPED LAUGHING." (6.0-10.0) |
| 10.6-12.0 | Slows down: single stones again (358 to 364), then a held breath: one slow lift of the last stone, close, above the clouds, dawn glow behind. | 358 to 364 | |
| 12.0 | Day 365: last stone down, hero hit, the Sun clears the horizon, counter pulses. | 365, 62 M UP | |
| 12.0-14.1 | Reveal: the camera swings up and over him to look back down the whole stair: him at the top in the sunrise, 365 stones falling away through the clouds to a speck of a crowd. | 365 | "ONE STEP A DAY." (13.45), "365 STEPS x 17 CM = 62 M", "ABOUT A 20-STOREY BUILDING", "THOUGHT EXPERIMENT" |
| 14.1-15.9 | Hold and slow drift on the top-down view. | 365 | text out by 15.9 |
| 15.9-17.0 | Dive home down the stair to the crowd. | | |
| 17.0-17.5 | One of the crowd, now ivory, turned toward the stair, picks up a stone and is about to set his own first step: matches frame 0. | | |

Camera grammar: one continuous camera, no cuts. Part 1 follows a smoothed track of the hero (offset keys, so it never picks up the stepping bob); part 2 uses absolute keys for the reveal, the hold and the dive. The work clock `C(t)` is a monotone cubic through keys, so stone placements, the counter and the sound all come from one function (`times.js` exports them to `timing.json`).

## 4. Facts and sources

| On screen | Value | Source / check |
|---|---|---|
| One step = 17 cm | 0.17 m rise, 0.30 m tread | Inside every building code range: UK Approved Document K (private stairs: rise 150-220 mm), US IRC R311.7.5.1 (riser max 7 3/4 in = 197 mm). 2R + T = 64 cm fits the classic Blondel comfort rule (about 63 cm). |
| 365 steps x 17 cm = 62 m | 365 x 0.17 = 62.05 m | Arithmetic. |
| About a 20-storey building | 62 m / about 3.1 m per storey = 20 | CTBUH height calculator uses about 3.1 m floor-to-floor for residential. "About" stays on screen. |
| Clouds at 35-40 m | Low cloud and valley fog can sit this low | Stylised; the floating stair itself is the thought experiment, hence the "THOUGHT EXPERIMENT" tag. Heights and step sizes are real scale, so no "not to scale" tag is used. |

Nothing claims a real person or record. The motivational idea (consistency adds up) is framed as arithmetic, not as a statistic.

## 5. Sound ("stone and breath" family, new for this reel)

Built in `mix.py` (numpy buses: stone, tick, crowd, bed, wind, hit, air), synced to the 365 placement times from the scene.

- Every stone he sets down has a sound: real stone thuds while the days are slow; while they fly by the thuds hand over to short ticks whose pitch climbs with the stair, so they blur into a whir.
- Crowd laughter (ElevenLabs) on the first stones, thinning out exactly as the scene's laugh weight does (gone by about 7 s).
- A D drone that opens up as he climbs, and a soft shepard riser that follows the climb.
- Wind that grows with height, with gusts.
- Held breath 11.05-12.0 s: everything drops to a thin rising air swell.
- Hero hit at 12.0 s only: stone thud + ElevenLabs impact + a synth gong (98-785 Hz partials) + a short 50 Hz sub, with reverb and a duck on the bed.
- D major chord under the reveal, a bell when the end line lands, a dive whoosh, then a rising tone into frame 0 (whose opening thud closes the loop).
- Delivery: about -15 LUFS integrated, true peak checked after AAC (see QA).

Audio licences: all sound effects were generated for this reel with the ElevenLabs Sound Effects model (`eleven_text_to_sound_v2`) on Teja's account (flow "Slow Light - One Step a Day SFX"); everything else is synthesised in `mix.py`. No Freesound files and no credit lines are needed. ElevenLabs allows commercial use of generated sound effects on paid plans; confirm the account is on a paid plan before a monetised upload.

## 6. Pipeline (rebuild)

```
cd tools/one-step-a-day
npm i three@0.170.0 playwright-core     # into ./node_modules (or symlink), not committed
python3 -m http.server 8811 &
node shot.js 540 960 /tmp/shots 8811 0 4 8 12.2 14.1 17.45        # stills
node times.js 8811 timing.json                                     # placements + per-frame day counter
for i in 0 1 2 3; do node render.js 1080 1920 /tmp/frames 8811 $i 4 & done   # 525 frames, native 1080x1920
python3 mix.py timing.json /tmp/mix.wav
python3 compose.py /tmp/frames timing.json /tmp/mix.wav one-step-a-day.mp4
```

Render: three.js r0.170, headless Chromium + SwiftShader, PCF soft shadows, Unreal bloom (0.42-0.67), ACES tone mapping, 3 motion-blur sub-frames per frame (5 in the time-lapse, the reveal swing and the dive).

## 7. Publish copy

**YouTube Shorts title:** They Laughed at Step One #shorts

**YouTube description:**
> One stone a day. That's all he did.
> Each step is 17 cm, too small for anyone to notice. After 365 days the stair is 62 metres tall, about a 20-storey building.
> They laughed at day 1. Nobody was laughing at day 365.
>
> A Slow Light thought experiment: real step size, real arithmetic, floating stair.
> Sound effects generated with ElevenLabs; all other sound and visuals made by Slow Light.
>
> #consistency #discipline #motivation #stickman #animation #oneday #selfimprovement #shorts

**Instagram / Facebook caption:**
> They laughed at step one. 🪨
> 17 cm a day x 365 days = 62 m. About 20 floors.
> One step a day.
> #consistency #discipline #stickman #motivation #reels

**Pinned comment:** What's your "one step a day"? Day 1 starts with one stone.

**Upload settings:** 9:16, made with AI/synthetic media label on (synthetic scene and AI-generated sound), no music claimed.

## 8. QA (filled in after the final render)

See the QA notes at the bottom of this file.
