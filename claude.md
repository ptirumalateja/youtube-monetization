# STANDING RULES FOR ALL SLOW LIGHT WORK (read first)

1. **Before doing any video, sound or publishing work, read `slow-light-design-playbook.md` in full.** It is the source of truth for design decisions, camera grammar (Scale Ladder orbiting log-zoom; Night Sky single-axis tunnel), depth/parallax/motion, exposure, palette, info-layer sizes, sound design, QA checklist, lessons log and backlog. Then read the per-reel spec (`night-sky-v8-spec.md`, `scale-ladder-reel.md`, `tickle-reel.md`) and the publish copy for the reel you touch. The playbook has two formats: **Format A** (cinematic 3D light-and-scale reels, wordless) and **Format B** (editorial motion-graphic explainers with voiceover, playbook section 11). Rules 2 and 4 below that say "wordless, no voiceover" apply to Format A only; Format B follows playbook section 11.
2. **Rules that always apply** (details in the playbook): **Higgsfield is only for ElevenLabs audio generation; for anything else (image generation, video generation, upscaling, SFX, mixing, assembly) ask the user first. Do those in Claude (local three.js/PIL/numpy/ffmpeg) or on RunPod (Qwen/Wan/SeedVR2) only;** never repeat a visual across reels; wordless, no voiceover; labelled "thought experiment / not to scale"; loops; palette charcoal/navy, cream text, gold/teal, red only for markers; counters must be monotonic; the viewer must be able to decode every transition.
3. **Audio licences:** CC0, or CC BY with an explicit credit and "changes were made". Never CC BY-NC. Per-file credit lines are in `audio-attribution.md`; update it and the reel's `*-publish-copy.md` whenever a sound is added or swapped.
4. **Audio files:** committed Freesound files are in `tools/sfxlib/` (mix scripts expect `../sfxlib/`). Files not in git (Uppbeat braams, unknown-licence files) and the Google Drive file ids are described in `tools/sfxlib/README.md` and `tools/sfxlib/drive_ids.txt`. Look in the user's Google Drive (Drive connector) before asking them to re-upload.
5. **Past reasoning is not in git.** The playbook records decisions and lessons, not the back-and-forth. If something seems undecided, check the playbook's decision log and the `*-spec.md` files; if still unclear, ask the user rather than redoing a frozen decision (the user has said "no redo's": frozen plans stay frozen).
6. Rendered videos, frames and overlay movs are not in git (scratchpad only). Rebuild them from `tools/` using the playbook's pipeline section.
7. **Format B (editorial graphic explainers, e.g. `tickle-reel.md`):** voiceover-led, 25-40 s, flat vector look with cinematic lighting (the approved "style B": rim-lit cut-outs, teal-edged shadow, grain, vignette), captions with a red keyword chip, step-line graph, clock, reticles. Built in code (`tools/tickle/`: HTML/SVG rendered by headless Chromium, timeline-driven) with AI plates only where needed. Full rules, layout numbers and colour semantics are in playbook section 11. Do not copy the reference pigeon video's artwork or its watermark.
8. **Credit budget (owner is credit-limited):** no paid generation without asking first. In particular **no Higgsfield SFX or any Higgsfield generation except ElevenLabs voiceover the owner has approved**. Sound is numpy-synthesised or CC0/CC BY files from Freesound (the owner downloads them; Freesound needs a login). Use RunPod only when a task really needs it, **stop the pod as soon as generation is done**, and say what a restart costs ($0.59/hr on the A40 pod).
9. **Voice:** Format B voiceover is tried in two versions (the owner's voice, tightened; and a more commanding ElevenLabs voice) from the same timeline, then compared. Caption timings come from the finished audio, so each version gets its own timing file.

The rest of this file is the separate Abhimanyu-story project instructions.

---

# Slow Light — Abhimanyu Short Production + Claude Code / RunPod Instructions

## 1. Project

**Channel:** Slow Light  
**Tagline:** Stories worth slowing down for.  
**Format:** Cinematic, story-driven 45–60 sec Shorts/Reels for YouTube, Instagram and Facebook.  
**Current story:** Abhimanyu and the Cakravyuha from the Mahabharata.

### Creative Standard

This must NOT look like generic AI mythology content.

Target:

- Serious
- Cinematic
- Emotionally gripping
- Grounded ancient-Indian visual language
- Restrained rather than fantasy-heavy
- Consistent character identity
- Original visual storytelling
- Strong first 2–5 seconds
- Every shot must have a narrative purpose

Do not casually present epic/traditional narratives as proven modern history. Distinguish the epic text from later popular retellings when relevant.

---

# 2. Story Concept

## Core Hook

> He knew how to get in.  
> He didn't know how to get out.

## Second Question

> So why did the Pandavas send Abhimanyu?

## Real Twist

> Because everyone who promised to follow him was stopped outside.

## Deeper Emotional Payoff

> He was never supposed to be alone.

The viewer should initially think this is a story about Abhimanyu not knowing how to escape.

The reveal is that the real tragedy was that the support promised to him never reached him.

---

# 3. Source / Story Accuracy

The research basis used for the script includes the BORI Critical Edition of the Drona Parva.

Key points:

- Yudhishthira says the Pandavas do not know how to break the Cakravyuha and identifies Abhimanyu, Arjuna, Krishna and Pradyumna as capable of entering it.
- Abhimanyu says his father taught him to breach the formation, but he does not know how to make his way back out.
- Arjuna is away fighting the Samsaptakas.
- Drona forms the Cakravyuha.
- Abhimanyu enters.
- Jayadratha prevents the other Pandavas from following him.
- Abhimanyu is eventually isolated and killed after his weapons and chariot are destroyed.
- The popular story that Abhimanyu learned the entire Cakravyuha technique in the womb while Subhadra fell asleep should NOT be treated as the primary textual account.
- Do not state that Abhimanyu was exactly 16 unless a specific source is being used to support that claim.

### Visual Interpretation

The Cakravyuha should look like a coordinated ancient military formation.

It should NOT look like:

- magical energy
- a glowing supernatural circle
- fantasy machinery
- a video-game formation

---

# 4. Master Audio Transcript

## Duration: ~60.84 seconds

This is the current master narration.

**Do not rewrite this unless explicitly instructed.**

> He knew how to get in.
>
> He didn't know how to get out.
>
> So why did the Pandavas send Abhimanyu into the Cakravyuha?
>
> Because on that day... Arjuna was away.
>
> And Drona had formed a battle array the Pandavas struggled to break.
>
> Abhimanyu knew how to breach it.
>
> But he admitted... he didn't know how to escape.
>
> Still, Yudhishthira told him to break the formation...
> and promised the others would follow.
>
> Abhimanyu charged.
>
> He broke through.
>
> Then the opening closed.
>
> Jayadratha stopped the Pandavas from following.
>
> Abhimanyu was alone.
>
> His bow was destroyed.
>
> His chariot was wrecked.
>
> His sword was gone.
>
> So he picked up a chariot wheel...
> and kept fighting.
>
> But that was the tragedy.
>
> He was never supposed to be alone.

### Narration Rules

- Current ElevenLabs cloned voice is approved.
- Approximate duration: 60.84 sec.
- Narration is the master timeline.
- Do not rewrite narration merely to fit generated video.
- Natural pauses take precedence over rigid visual timestamps.
- No AI-generated dialogue.
- No text baked into generated clips.
- No automatic captions/subtitles inside generated clips.

---

# 5. Master Storyboard

## 00:00–00:04

**Audio:**

> He knew how to get in.

**Visual:**

Close-up of Abhimanyu.

Young South Asian warrior.

Golden sunset battlefield.

Dust and banners.

**Camera:**

Slow push-in.

---

## 00:04–00:08

**Audio:**

> He didn't know how to get out.

**Visual:**

Reveal the enormous Cakravyuha behind him.

**Camera:**

Slow pull-back / reveal.

Formation subtly shifts as an organized military formation.

---

## 00:08–00:12

**Audio:**

> So why did the Pandavas send Abhimanyu into the Cakravyuha?

**Visual:**

Abhimanyu facing the Pandava commanders.

**Camera:**

Slow lateral movement.

---

## 00:12–00:16

**Audio:**

> Because on that day... Arjuna was away.

**Visual:**

Arjuna leaving toward another battlefield.

**Camera:**

Rear/silhouette tracking shot.

---

## 00:16–00:20

**Audio:**

> And Drona had formed a battle array the Pandavas struggled to break.

**Visual:**

Drona and the enormous formation.

**Camera:**

Slow push.

---

## 00:20–00:24

**Audio:**

> Abhimanyu knew how to breach it.

**Visual:**

Close-up of Abhimanyu preparing his bow and studying the formation.

---

## 00:24–00:28

**Audio:**

> But he admitted... he didn't know how to escape.

**Visual:**

Close-up.

Brief hesitation followed by determination.

---

## 00:28–00:32

**Audio:**

> Still, Yudhishthira told him to break the formation...

**Visual:**

Yudhishthira speaks and gestures toward the formation.

---

## 00:32–00:36

**Audio:**

> and promised the others would follow.

**Visual:**

Pandavas prepare behind Abhimanyu.

End on Abhimanyu.

---

## 00:36–00:40

**Audio:**

> Abhimanyu charged.

**Visual:**

Dynamic chariot charge.

Horses.

Dust.

Banners.

**Motion:**

Faster, energetic tracking.

---

## 00:40–00:44

**Audio:**

> He broke through.

**Visual:**

Chariot breaks through the first layer.

**Motion:**

Fast forward movement.

---

## 00:44–00:48

**Audio:**

> Then the opening closed.

**Visual:**

High/wide view.

The opening closes.

Abhimanyu becomes isolated.

**Motion:**

Dramatically slow down.

---

## 00:48–00:52

**Audio:**

> Jayadratha stopped the Pandavas from following.

**Visual:**

Jayadratha blocks the Pandava advance.

**Camera:**

Slow push.

---

## 00:52–00:56

**Audio:**

> Abhimanyu was alone. His bow was destroyed. His chariot was wrecked. His sword was gone.

**Visual:**

Rapid sequence showing:

- bow destroyed
- chariot disabled
- sword lost

No graphic gore.

---

## 00:56–01:00.84

**Audio:**

> So he picked up a chariot wheel... and kept fighting. But that was the tragedy. He was never supposed to be alone.

**Visual:**

Abhimanyu raises a chariot wheel and advances.

Then transition into a wide sunset battlefield composition.

**Ending feeling:**

Heroic tragedy.

Scale.

Isolation.

Dust.

Sunset.

---

# 6. Visual Style Bible

## Overall Style

High-end cinematic Indian epic / historical drama.

Use:

- Grounded ancient Indian battlefield
- Realistic South Asian faces
- Ancient Indian clothing
- Historically inspired armor
- Bows
- Chariots
- Muted bronze
- Deep blue
- Dusty earth tones
- Warm sunset
- Atmospheric haze
- Dust and smoke
- Subtle camera movement
- Painterly photorealistic finish

## Avoid

- Marvel superhero aesthetic
- Fantasy armor
- Glowing eyes
- Magical energy
- Excessive gold CGI
- Cartoon
- Anime
- Modern objects
- Excessive camera shake
- Graphic gore
- Text
- Captions
- Subtitles
- Logos
- Watermarks
- Random costume changes
- Character morphing
- Identity changes

---

# 7. Abhimanyu Character Continuity

The same Abhimanyu must remain consistent across all shots.

Reference characteristics:

- Young South Asian warrior
- Dark curly hair
- Warrior tilak
- Bronze/gold armor
- Blue drape/sash
- Ancient Indian warrior styling
- Bow
- Quiver
- Realistic human proportions
- Cinematic realistic face

### Reference Image

Current reference image on RunPod:

`/workspace/runpod-slim/ComfyUI/input/slowlight/abhimanyu_test.png`

### Critical Continuity Rules

The following must remain consistent unless a shot intentionally starts from a new reference pose:

- Face
- Identity
- Head orientation
- Body orientation
- Torso
- Shoulders
- Arms
- Hands
- Bow
- Bow hand
- Armor
- Blue drape
- Hairstyle

---

# 8. RunPod Environment

## Pod

`comfyui-rtx-a6000`

## Device

`bbab976d9a06`

## GPU

NVIDIA RTX A6000

~48 GB VRAM

## ComfyUI

`/workspace/runpod-slim/ComfyUI`

## Port

`8188`

ComfyUI is already running locally.

---

# 9. Installed Wan Models

Already installed:

```text
wan2.2_ti2v_5B_fp16.safetensors
umt5_xxl_fp8_e4m3fn_scaled.safetensors
wan2.2_vae.safetensors
```

> **Update (Oct 2026):** that list is the old Abhimanyu pod. The network volume `bvufz93jst` (`slowlight-100`, CA-MTL-1) now holds: Qwen Image Edit 2511 fp8 + Lightning 4-step LoRA, **Wan 2.2 I2V 14B** (high/low noise fp8) + lightx2v 4-step LoRAs, UMT5-XXL, Qwen 2.5 VL 7B, Wan 2.1 VAE, Qwen VAE, SeedVR2 3B + VAE. Pods are created from the REST API (`runpod/comfyui:1.3.3-comfyuiv0.30.0-cuda12.8`, A40 or RTX A6000, volume mounted at `/workspace`, ports 8188/8080/8888/22) and must be stopped after use. Qwen Image Edit edits an existing image; it does not generate from nothing, so seed it with a reference or a blank plate.
