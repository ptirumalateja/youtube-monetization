# The Higher He Got (v1)

- **Video:** `final-reels/the-higher-he-got.mp4` (37.9 MB master, CRF 18) and `the-higher-he-got-share.mp4` (16.3 MB, CRF 23, for chat). Local only, not in git. 18.0 s, 1080x1920, 30 fps, loops, no voiceover.
- **Status:** delivered 21 Oct 2026, built in the cloud from brief #8 of `ref-remakes-plan.md` (the reference MP4 was not used or seen; only its theme, "money changed him", is shared).
- **Build:** `tools/higher-he-got/` (three.js `renderAt(t)` scene, Playwright headless render, PIL overlay, numpy sound). Rebuild steps are at the end.

## Concept
A stickman parable. He and his partner share one bench under a street lamp, holding hands. A coin lands under him, then another, and every coin lifts him a little higher. The pile compounds (it grows exponentially, like money does), the coins pour in faster, and he slowly turns from cream bone to polished gold. Their hands stretch, then part. He looks up at the light and reaches for more. When the pile finally stops he looks down and reaches for her, and the camera flies back: he is a gold speck on top of a 12 m needle of coins, she is a small figure on the bench under the lamp, and the gap between them is where the last line lands.

- Hook (typed by 1.3 s): **EVERY COIN / LIFTED HIM HIGHER.**
- Wide-shot caption: **HE COULD REACH / ANYTHING.**
- End line: **EXCEPT HER.**
- Monotonic counter: **NET WORTH** $0 to $10,000,000 (only ever goes up).
- Loop: the last frame is the frame-0 camera on the bench (her, with the column's base on his seat); frame 0 is the same shot with him back beside her and the first coin landing. "It started with one coin."

How it differs from the reference: a different metaphor (a coin column growing under one half of a shared bench, not two pillars), our own ivory stickman and navy night world, a 3D camera that rides up with him and then flies back for the reveal, the gold transformation, and the counter.

## Shot plan
| Time (s) | Shot | Sound |
|---|---|---|
| 0.0-1.3 | Bench, lamp, city behind. Both sit holding hands (warm glow at the hands). The first coin spirals in and lands under him on frame 0. Hook types. | first clink + low thump, music-box motif and soft chord |
| 1.3-6.3 | Coins arrive faster (1 per second, then several per second); he rises step by step; she leans and stretches up, he leans down; hands hold while both can still reach. He starts turning gold at 3.2 s. | clinks climbing in pitch, motif starts to wobble |
| 6.33 | Their hands part (the exact moment the scene computes the shoulder gap passing two arm-lengths); the hand glow goes out. | a broken minor-second note |
| 6.3-11.2 | Camera rides up with him. Coins pour in from behind in a spiral; he sits upright, looks up at the golden sky, right arm reaching up. The city drops below. | golden pad and rising tones, coin shimmer |
| 11.25-12.0 | The pile stops. Held breath: he looks down and reaches down toward her. | near silence, reverse suck |
| 12.0-14.2 | HIT. Camera flies back about 25 m: the full coin needle, him tiny and haloed at the top, her on the bench under the lamp. | crack + pitch-drop body + gong + sub |
| 13.4-16.2 | Wide hold. Red ring marks her; she raises her arm toward him. HE COULD REACH / ANYTHING., then EXCEPT HER. in the gap between them. | wind at height, three lonely music-box notes in A minor |
| 16.2-17.6 | Camera dives back down to the bench (frame-0 framing). | falling whoosh, soft landing thud |
| 17.6-18.0 | Hold on her and the column's base; reversed note into frame 0. | lamp hum, reversed note |

## Facts and sources
The reel is a parable and makes no factual claim on screen. The numbers in it are internal to the story: 299 coins, 4 cm each, a 12 m column, and a NET WORTH counter tied to the height (so it compounds with the pile). Background reading for the theme, if the copy ever needs it:
- Kraus, Côté and Keltner (2010), "Social class, contextual accuracy, and empathy", *Psychological Science* 21(11): lower-class participants were more accurate at reading others' emotions. Treat as one study, not settled fact.
- Piff et al. (2012), "Higher social class predicts increased unethical behavior", *PNAS* 109(11). Widely cited and debated; do not quote it as proof that money makes people worse.
- Killingsworth, Kahneman and Mellers (2023), "Income and emotional well-being: A conflict resolved", *PNAS* 120(10): for most people happiness keeps rising with income, so the reel's point is about distance from people, not "money makes you sad".

## Sound
Fully synthesised in numpy (`sound.py`), no samples, so no credits are needed. Coin clinks are placed at the scene's real landing times (one per coin) with pitch rising as the stack grows; the parting note is placed at the computed parting time. Measured after AAC: -15.3 LUFS integrated, true peak -1.9 dBFS (the hit's crack got a 2 ms attack and lower gain after the first encode overshot to +0.1 dBFS).

## Publish copy
- **YouTube title:** The Higher He Got, the Less He Could Reach #shorts
- **Description:** Every coin lifted him a little higher. He could reach anything. Except her. A Slow Light parable, made entirely in code (three.js, rendered frame by frame; sound synthesised, no samples). #shorts #stickman #money #relationships #parable #animation
- **Pinned comment:** What would you trade to stay on the bench?
- **Instagram / Facebook caption:** Every coin lifted him higher. He could reach anything. Except her. 🪙 What would you trade to stay on the bench? #stickman #money #love #animation #reels
- **Hashtags:** #shorts #stickman #money #relationships #parable #animation #slowlight
- **Sound credit line:** none needed (all sound synthesised for this reel).

## Playbook check
Hit and motion on frame 0; hook typed by 1.3 s; one idea; one monotonic counter (asserted frame by frame in `render.cjs meta`); held breath before the single biggest hit; red used only for the marker ring; cream text with black stroke in Liberation Mono Bold; text kept out of the bottom 18%; last frame matches frame 0's camera; wordless.

## Rebuild
```
cd tools/higher-he-got && npm install
node render.cjs meta                                   # coin landing times, parting time, screen positions, counter check
for w in 0 1 2 3; do SUB=4 node render.cjs frames $w 4 & done; wait   # 540 frames at 1080x1920 (about 90 min on 4 CPUs, SwiftShader)
python3 sound.py                                       # output/sound.wav, about -15 LUFS
python3 overlay.py the-higher-he-got.mp4               # text layer + mux -> output/the-higher-he-got.mp4
```
Set `CHROME_PATH` if Chromium is not at `/opt/pw-browsers/chromium` (on the Mac: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`).
