# Why can't you tickle yourself? (Format B pilot, frozen plan v1)

Format B editorial explainer, see `slow-light-design-playbook.md` section 11 for the look, layout numbers, colour semantics and pipeline. Look is **style B** (approved); style frames in `tools/tickle/styleframes/`. About 32 s, 1080x1920, voiceover-led, loops.

## Idea and honest science

- Hook: you can't tickle yourself.
- Mechanism (simplified): when you move, the brain sends the movement command and an internal **copy** (efference copy). A forward model (the **cerebellum**) uses the copy to **predict** the touch. The predicted touch is subtracted from the real signal, so self-touch is **dampened, not zero**. A touch you did not generate has no copy and no prediction, so it arrives as full surprise.
- Visual metaphor: the **shadow is the brain's prediction** and always arrives before the hand. Someone else's hand has **no shadow**.
- Claims to verify before publishing (do not put a citation in the video): Blakemore, Wolpert and Frith 1998 (central cancellation of self-produced tickle sensation). Tag the reel "simplified illustration".
- Do not say "impossible" in the copy; say "dampened", "less surprise, less tickle".

## Colour use for this reel

Teal = prediction (shadow edge, copy signal). Gold = the real thing that moves (hand path, command). Red = accent only (reticle, chip, graph step line, spike, rim light). Graph: gold smooth line = hand movement; red step line = felt tickle.

## Voiceover script v1 (about 75 words, 2.4 w/s)

| # | Line | Time (s, target) | Caption card (chip word in brackets) |
|---|---|---|---|
| 1 | "You can't tickle yourself." | 0.0-2.4 | YOU CAN'T [TICKLE] YOURSELF. |
| 2 | "Your brain knows what you're about to do... before you do it." | 2.4-7.0 | YOUR BRAIN [KNOWS] FIRST |
| 3 | "When you move, it sends the command... and a copy." | 7.0-11.0 | [COMMAND] + [COPY] |
| 4 | "The copy predicts the touch." | 11.0-13.5 | THE COPY [PREDICTS] |
| 5 | "Predicted touch? Dampened." | 13.5-16.0 | PREDICTED = [DAMPENED] |
| 6 | "Less surprise. Less tickle." | 16.0-18.5 | LESS SURPRISE. LESS [TICKLE]. |
| 7 | "Someone else's hand? No copy. No prediction." | 18.5-24.0 | NO COPY. NO [PREDICTION]. |
| 8 | "Your brain can't be surprised by itself." | 24.0-28.0 | [SURPRISED] BY ITSELF? |
| 9 | "Your brain already knows." (loop line) | 28.0-32.0 | YOUR BRAIN ALREADY [KNOWS]. |

Voice versions: A = owner's voice, tightened (pitch-preserving stretch, trimmed pauses); B = commanding ElevenLabs voice (one generation, only with the owner's OK). Timings above are targets; final caption timing comes from each recording.

## Shot table

| Time | Shot | Graph / clock | Sound |
|---|---|---|---|
| 0.0-2.4 | Hook frame as in style B: hand rises from lower-left, shadow already at the reticle. Echo trails. Caption typed by 1.9 s. | Gold curve starts; red flat. Clock ticks. | Frame-0 soft tap + low pulse; voice line 1. |
| 2.4-7.0 | Split screen: left "YOUR HAND" shadow ahead; right same move, shadow ahead again. Pan-in on the gap between shadow and hand. | Red stays flat. | Voice only + bed; small tick on chip. |
| 7.0-11.0 | Mechanism: line-art arm draws on stroke by stroke; a flat brain in the corner with the **cerebellum** lit teal; gold command pulse down the arm, teal copy pulse to the cerebellum. | Gold line steps up on the pulse. | Pulse ping (gold), softer teal chime (copy). |
| 11.0-16.0 | Copy predicts the touch: teal prediction ripple meets the gold real ripple on the skin plane and they cancel. HOLD marker. | Red stays flat: "dampened". | Self-touch sound low-passed and quiet. |
| 16.0-18.5 | Hand tries different spots (palm, forearm, cheek icon). Shadow ahead every time. | Red flat. | Ticks only. |
| 18.5-23.0 | "Someone else's hand?" a second hand approaches from behind. **No shadow.** Slow push, held breath. | Red flat -> held. | Sound ducks to near silence (held breath) from about 22.2 s. |
| 23.0-24.2 | **Reveal.** The other hand lands; impact starburst + 2-frame punch (within exposure limits). | Red line **spikes**. | The one sized hit, bright and wide. |
| 24.2-28.0 | Hold on the spike, then return to the original wall; shadow waiting. | Spike decays to flat. | Tail, bed returns. |
| 28.0-32.0 | Match to frame 0: shadow already at the reticle, hand rising. End line typed once. Loop. | Gold curve restarts. | Loop-link tone into frame 0. |

## Sound cue sheet (synthesised + CC0, no Higgsfield SFX)

- Voice-led mix target about -15 LUFS, true peak checked after AAC.
- New sound family (do not reuse Night Sky or Ladder palettes): soft filtered-noise brush for touch, a low pulse (body 90-400 Hz) for command/HOLD, a teal glassy chime on a root that is not 106 Hz for prediction, risers kept minimal.
- Idea that proves the science by ear: expected touch is low-passed and quiet; the surprise touch is bright, wide, full.
- Licence: synthesised needs none; any Freesound file must be CC0 or CC BY with credit and "changes were made"; update `audio-attribution.md` and `tickle-publish-copy.md` when added.

## Build plan

1. Timeline JSON (script, card timings, shot keys) + renderer based on `tools/tickle/styleframes/` (SVG layers in headless Chromium, frame by frame, PNG to ffmpeg).
2. Hand art: compare refined vector against a Qwen-seeded illustration (restart the pod only for this, stop it after). Cut-outs with masks.
3. Voice A and B; derive caption timings from each.
4. Numpy mix; composite; QA (playbook section 7 + 11.6).
5. Publish copy: `tickle-publish-copy.md` (title, caption, hashtags, credits, "simplified illustration" note, AI label).

## Open items

- Hook A/B for overlay-only testing: A "YOU CAN'T TICKLE YOURSELF." / B "YOUR BRAIN KNOWS FIRST."
- Final fonts (system Liberation fonts are placeholders): confirm OFL licences before publishing.
- Verify the science claims and any numbers before the voice is recorded.
