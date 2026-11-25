# Slow Light Dark: series style sheet

Pilot: **The Chain Was Never Locked** (`tools/chain-never-locked/`, branch `claude/chain-never-locked`). The owner approved its look on 24 Oct 2026: "lighting, cream hero #EDE6D6, red lock #D83A2E, gold lamp, dust, reflection: all perfect. Don't touch that." Every Slow Light Dark reel matches it.

**Source of truth is the code:** `tools/slow-light-dark-common/` (`sld.js` stage + rig, `sld_text.py`, `sld_sound.py`, `render.cjs`, `demo.js` starter). If this sheet and the code disagree, the code wins. Change a look value only with the owner's OK, and tell the other reel sessions.

## The 3-second test (series rule, added 25 Oct 2026 after viewer feedback on the pilot)
With the sound off, a stranger must be able to say in one sentence what is happening by second 3.
- The on-screen text tells the story literally (pilot v2: "HE TRIED TO BREAK FREE ONCE." / "THEN HE STOPPED TRYING." / "12 YEARS LATER, HE CHECKED THE LOCK." / "IT WAS NEVER LOCKED."). The visuals carry the emotion.
- Objects that carry the meaning are big, bright and clearly framed from frame 1 (pilot v2: the padlock is 2x scale, lit, standing beside his foot). A rewatch hint may stay subtle, but the twist itself must be shown by an action that reads without text (he lifts the lock, the shackle swings open, the chain slides off his ankle).
- Check it on a contact sheet before the full render: stills at about 0.5 s, 2.5 s, the middle, the twist and the ending.

## Format
- 1080x1920, 30 fps, 12-20 s. Seamless loop (last frame = frame 0's framing) or a clean 1 s end hold.
- Wordless, no voiceover. Short on-screen text only. One device per reel, the story lives in the caption.
- Not a copy of @neuronvisuals: no pixel font, no pure-white figures, no copied compositions, **no wings, no flying**.

## World (`createStage`)
| | Value |
|---|---|
| Void | `#07080B` background + FogExp2 0.085 (same colour) |
| Lamp (series signature) | one gold SpotLight `#E8B85A`, intensity 60, decay 1.2, angle 0.35 rad, penumbra 0.85, at (0, 4.6, 0.05) aimed at the floor; 2048 PCF soft shadows |
| Beam | ray-marched cone (half-angle 0.27), gain 0.14, drifting haze noise; hidden from the floor mirror |
| Motes | 1700 points, visible only inside the cone, slow fall + drift |
| Other light | hemisphere `#1c2338`/`#2a2218` 0.1, cool back light `#9aa8c8` 0.1. **No front fill** (it lit the floor blue-grey) |
| Floor | Reflector (1/3 res = soft) 6 mm below a concrete skin `#4a4a50`, roughness 0.74, opacity 0.9 |
| Grade | ACES, bloom 0.45 / 0.6 / 0.88, soft clamp `1-exp(-1.15c)`, vignette 0.62, navy corners `+(0.0006,0.0010,0.0028)` (linear: tiny), grain scaled by luminance |
| Camera | FOV 38. Wide: from (0.06, 0.8, 5.6) looking at (-0.02, 0.5, 0); subjects in the middle third, floor reflection below. Slow push-ins/pull-outs, few cuts, never blur across a cut |
| Motion blur | 3 sub-frames at 1/60 s; 7 sub-frames on jolts; 1/30 s for time-lapse crowds |

## Figures (`createRig`)
- Solid 3D: capsule limbs (cylinders + sphere joints), sphere head radius 0.13, **no face**. Proportions thigh 0.46, shin 0.46, torso 0.56, upper arm 0.31, forearm 0.29.
- Limb thickness: **width 0.44× head diameter** (radius 0.22×). Confirmed by the owner on 24 Oct 2026.
- Hero cream `#EDE6D6`, roughness 0.62, rim 0.16 (`#fff1d8`), self-lift emissive 0.07 so the underside never goes black.
- Others slate `#8A8F98`, rim 0.08 (`#9fb2d6`), no lift: outside the beam they read as soft rim outlines. They **fade 1 → 0 into the void over about 2 s** (`F.setAlpha`), never pop.
- Posture carries all the emotion. Look direction = head lean (`hy`, `tilt`) + upper-body twist (`ty`). Pose library: stand, hunch, crouch, sit (floor, knees up, `handsOnKnees`), slump. Ease everything (smoothstep / quintic), add a jolt bump for impacts, breathing on idle.

## Accent
- Exactly one red story object `#D83A2E`. In wide shots it sits **half in shadow** (emissive 0.05, halo 0.025); it only glows (emissive 0.22, halo 0.16, small red point light) when the camera pushes in to it.
- Gold only for the lamp and a final payoff (pilot: lamp +14% as he looks; a gold glint on the twist object).
- Plant the twist in the first frames for rewatchers (pilot: the shackle is open from frame 0, with a faint catch-light on its free tip).

## Text (`sld_text.py`)
- Top centre, tracked caps, cream, JetBrains Mono SemiBold (OFL), soft dark halo. Hook 46 px / track 9 (two lines); counter 60 px / track 14; end line 50 px / track 9; all at y 262.
- "SLOW LIGHT" watermark, JetBrains Mono Medium 24 px, track 10, y 1548, 35% opacity.
- Counters monotonic (assert per frame). Hook on screen from frame 0.

## Sound (`sld_sound.py`)
- Minimal but heavy. Bed = CC0 wind (sleepCircle 22331) low-passed + the lamp's 120 Hz mains hum (series signature) + a 55 Hz drone that swells toward the twist.
- Foley with a visible cause for every sound (synthesised: iron clank, link rattle, scrape, breath, thud, footsteps, creak).
- Silence as a beat: ~0.25 s full duck right before the twist. The twist is the only big hit: `sub_boom` + CC0 qubodup 814046 read two octaves down. No music bed (at most a few sparse low piano notes).
- High-pass non-hit buses at 75-90 Hz (phones), weight in 90-300 Hz. Master to -15 LUFS with a look-ahead limiter; **measure true peak after AAC** (`master_to_mp4`; pilot: -15.2 LUFS, -1.1 dBTP).
- Licences: ElevenLabs SFX via Higgsfield (Higgsfield currently lists no SFX model, only speech), CC0, or CC BY with credit; never NC. Update `audio-attribution.md`.

## Exports
- `<slug>.mp4` master with sound, and `<slug>_music-ready.mp4` silent; state the hit timestamp.
