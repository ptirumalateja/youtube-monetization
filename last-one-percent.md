# Wireman: Last 1% (reel)

Slow Light wireman series. 24.5 s, 1080x1920, 30 fps, no voiceover, no music (a clean drop at 16.4 s is left for the music you add in Instagram / YouTube), loops.
Picked from Teja's shortlist (last 1% / crowd that follows / bridge by bridge) because the battery is a countdown everyone has felt, so it holds attention by itself. The wall was dropped.

- Source: `tools/last-one-percent/` (`index.html` scene with `window.renderAt(t, samples)`, `render.js`, `shot.js`, `times.js`, `compose.py`, `mix.py`)
- Final files (project files, not in git): `final-reels/last-one-percent.mp4` (with sound design), `final-reels/last-one-percent_music-ready.mp4` (silent, add your track), `final-reels/last-one-percent_contact_2fps.jpg`

## 1. Concept

One idea: **we will run across a whole city for a charger that was lying next to us the whole time.**

A wireman made of glowing wire sits on a bench on a rainy evening street. His battery chirps: 1%. Far down the street a charging post glows gold. He sprints for it, trailing his own cable with a plug on the end. Every few seconds the battery drops a notch and the street goes darker with him: windows and lamps click off in waves, his glow fades and flickers. He hurdles a barrier, leaps a puddle, slows to a drag, reaches the post at 0.01% and plugs his own tail in. Drop: the light rushes back down the whole street.

Twist: the camera cranes up and the street turns out to be the screen of a phone lying on a nightstand. The phone is at 1%. Its charging cable lies 3 cm from the port. "THE CHARGER WAS RIGHT THERE." The screen dims (the phone's own low-battery chirp), the street inside restarts with him back on the bench at 1%, and the camera dives back into the screen: frame 0.

- **Hook (0-0.6 s):** "1% LEFT." typed over the low-battery chirp; the wireman is already moving (slumped, then startled).
- **Countdown:** BATTERY 1.00% to 0.01%, asserted to only go down (`compose.py`); a red battery icon floats over his head and blinks once it is under 0.5%.
- **Beats:** the world dims at 4.6, 7.2, 9.8, 12.4 and 14.4 s (light level 1.0 to 0.21, never black).
- **Held breath:** 15.9-16.4 s, near silence, plug inches from the socket.
- **Drop:** 16.4 s plug in, surge, relight wave, CHARGING chip. **Cut your music's drop to 16.4 s.**
- **Twist:** 17.8 s the street becomes the phone screen; 20.3-22.4 s end line.
- **Loop:** the last frame is the screen filling the frame with the street at time 0, so it matches frame 0 exactly.

## 2. Look (Teja: dark but not too dark, dreary but not eerie, instantly relatable)

- **Street:** blue-hour rainy evening, warm amber windows and shop fronts (shelves inside, mullions), sodium street lamps with pools on the wet pavement and long reflections on the road, light drizzle streaks. Sky is navy with a warm city glow on the horizon. Even at the darkest beat the hemisphere light and sky keep the street readable.
- **Wireman:** the stickman rig as cool glowing wire (pale blue-white emissive tubes), with a wire tail and a plug. His glow tracks the battery: bright at the start, dim and flickering near 0, a capped flare after the plug.
- **Target:** a dark charging post with a gold rim, a gold lightning bolt and a gold ring socket, visible down the street from the first stride (target first).
- **Bedroom:** cozy, warm bedside lamp on low, walnut nightstand, mug, book, bed and pillow, blue moonlight. White cable lying right next to the phone.
- **Palette:** navy and charcoal, cream text, gold and teal accents, red only for the battery.

## 3. Shot plan

| Time (s) | Shot | Counter / text |
|---|---|---|
| 0.0-1.5 | Front, slow push. Slumped on the bench under a lamp; chirp; he startles and stands. | "1% LEFT." (by 0.6 s), 1.00% |
| 1.5-2.4 | He turns to the street; the charger pings gold far away; camera swings behind him. | |
| 2.4-15.3 | One continuous tracking camera behind-left (street and target ahead), side-on for the hurdle (about 6.7 s), low over the puddle (about 9.1 s). Lights die at each beat. He slows from 12.4 s. | 0.95% to 0.03% |
| 15.3-16.4 | Close 3/4: he grabs his tail, holds the plug to the socket. Held breath. | 0.01% |
| 16.4 | Plug in: sparks, flare, lamps relight down the street in a wave. | CHARGING |
| 16.4-17.8 | Pull back and crane up, looking back down the relit street. | |
| 17.8-20.6 | The street is a phone screen: pull back from top-down to the phone on the nightstand, status bar red "1%", cable 3 cm short of the port. | |
| 20.6-22.6 | Slow drift; status battery blinks. | "THE CHARGER WAS / RIGHT THERE." |
| 22.6-24.5 | Screen dims and the street inside restarts at the bench; dive back into the screen to fill. | (loop) |

## 4. Facts

No numbers are claimed beyond the joke itself. The phone, the cable gap (3 cm) and the 1% are fiction, and nothing names a real brand or person.

## 5. Sound ("battery and rain", new family, all synthesised in `mix.py`, no samples, no credits)

Rain, drips and low city hum under the street, muffled through the window in the bedroom. Low-battery chirp on frame 0 (and from the real phone at 22.1 s). At each beat: a lower chirp, a power-down sweep and lamp clunks. Wet footsteps from the hero's real foot contacts (`times.js`), softer as he drags. Whoosh and landing for the hurdle, splash for the puddle. A rising pulse and riser from 12.4 s, held breath 15.9-16.4 s, then the drop: plug clack, surge (sub plus pitch sweep), and an ascending tink for every lamp as it relights. Whoosh into the phone, a bell on the end line, a rise into the loop.

The music-ready copy has no audio at all, so a licensed track from the Instagram or YouTube library can go on top; align its drop to 16.4 s.

## 6. Pipeline (rebuild)

```
cd tools/last-one-percent
npm i --no-save three@0.170.0 playwright-core@1.56.1
python3 -m http.server 8821 &
node shot.js 540 960 /tmp/shots 8821 0 3.5 6.6 9.3 16.0 17.6 20.5 23.5     # stills
node times.js 8821 timing.json                                             # head positions, battery, foot contacts
for i in 0 1 2 3; do node render.js 1080 1920 /tmp/frames 8821 $i 4 & done # 735 frames, native 1080x1920
python3 mix.py timing.json mix.wav
python3 compose.py /tmp/frames timing.json mix.wav last-one-percent.mp4
python3 compose.py /tmp/frames timing.json - last-one-percent_music-ready.mp4
```

Render: three.js r0.170, headless Chromium + SwiftShader, Unreal bloom (0.5, capped spike at the plug), ACES tone mapping, 3 motion-blur sub-frames (5 in the sprint, the plug flare and the phone moves). The phone screen is the street composer rendered to a half-float target and shown on the screen mesh, so it is tone-mapped once and the switch at 17.8 s is pixel-matched.

## 7. Publish copy

**YouTube Shorts title:** He Ran Across the City at 1% #shorts

**YouTube description:**
> 1% left. He sees a charger at the end of the street and runs for it.
> Every few seconds the world gets darker with him.
> Watch to the end. 🔌
>
> A Slow Light wireman short. Visuals and sound made by Slow Light.
>
> #battery #lowbattery #relatable #stickman #animation #shorts

**Instagram / Facebook caption:**
> POV: 1% and the charger is across the city 🔋
> (the cable was right there)
> #lowbattery #relatable #stickman #animation #reels

**Pinned comment:** What's the lowest % you've ever let your phone get to?

**Upload settings:** 9:16, made with AI/synthetic media label on, add music from the platform library (drop at 16.4 s).

## 8. QA

Final render, 22 Oct 2026:

- `final-reels/last-one-percent.mp4`: 1080x1920, 30 fps, H.264 CRF 18 + AAC 256k, 24.5 s, 23.1 MB (under the 30 MB chat limit). `final-reels/last-one-percent_music-ready.mp4`: same picture, no audio, 22.3 MB. Contact sheet: `final-reels/last-one-percent_contact_2fps.jpg`.
- Frame 0 is moving (slump, then startle) with the chirp on frame 0; hook fully typed by 0.6 s.
- Battery counter 1.00% to 0.01% asserted to only go down in `compose.py`; typed text never uses a negative slice.
- No white or beige frames: the plug flare is capped (bloom spike 0.2) and the bedroom is lit by a low warm lamp. Darkest street beat still shows windows, lamps and sky.
- Text stays above the bottom 18% (counter at y 1400-1550).
- Audio after AAC: -15.0 LUFS integrated, true peak -3.2 dBTP (soft-clip + limiter in `compose.py`; the plug transient was the overshoot). Held breath 15.9-16.4 s; one big hit on the drop at 16.4 s.
- Loop: the last frame is the phone screen filling the frame with the street at time 0; mean pixel difference to frame 0 is about 6/255 (the camera push is still moving, as intended).
- Soft spots for a v2: the battery icon over his head is small in the wide sprint shots; the street inside the phone during the reveal is a wide shot where the wireman is too small to see.

## 9. v2 polish pass (22 Oct 2026, from Teja's review)

Files: `final-reels/last-one-percent_v2.mp4` (sound), `final-reels/last-one-percent_v2_music-ready.mp4` (silent), `final-reels/last-one-percent_v2_contact_2fps.jpg`. v1 files are kept.

- **Hook:** "1% LEFT." is fully on screen from frame 0 with a red warning flash at the screen edges; the startle is sharper (jolt off the bench).
- **Chase:** about 2 s shorter. Camera now cuts the monotony with a push-in, a side-on hurdle, a front-facing shot looking back at the lamps dying, a low puddle leap and a close-side stumble. Glowing wet footprints fade behind him.
- **Desperation:** at 10.8 s he trips, drops to one knee, gets up and drags to the charger.
- **Blackout:** each lamp goes out in sequence as he passes it (flicker, then dead); the rest go out one by one before 12 s; windows are near dark from 12 s. Only the sky, the charger and his fading glow remain.
- **Plug-in (now 14.4 s):** wide close-up from the front-side so the plug is seen entering the socket, a tiny spark, a charge pulse travelling up his tail, then a gold pulse racing back down the kerb as the lamps relight. Bloom is capped (no white-out).
- **Reveal (from 16.4 s):** the street becomes the phone, then a side-on macro shows the phone's port and speaker holes, the connector stopping short of the port, with contact shadows from a warm lamp key. Caption lands at 19.8 s.
- **Loop:** the HUD (1% LEFT. and 1.00%) fades back in over the last 0.4 s so the seam has no pop.
- **Sound:** cable drag, per-lamp clicks, stumble thud and breaths, near-silent held breath before the plug, one big hit on the plug-in, then the epic sound is cut dead at the phone and a tiny dry tick plays at the connector (19.6 s). **Music: put the drop at 14.4 s.** Audio -14.5 LUFS, true peak -3.1 dBTP.
