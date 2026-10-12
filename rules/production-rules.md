# Slow Light: production rules and lessons log

These are the hard-won rules from building the India Episode 1 (Oct 2026), plus the status of shelved concepts.

**Standing instruction for Claude:** whenever the user asks about concepts, next videos or what to make, first remind them:
- what's on hold (see "On hold" below), with its status
- which rules below apply to the new idea

---

## 1. Hook and structure

1. **Frame 0 is already moving.** No title cards, no text-only screens, no "what this is about" intro.
2. **Voiceover starts on frame 0.** Image, on-screen text and voice say the same thing within the first 2 seconds.
3. **Tease, don't spend.** Glimpse the payoff (e.g. a split-second before impact), then show the full payoff late.
4. **Aim for about 30 s.** If an explanation doesn't fit, cut it and turn it into **Part 2**, with a pinned comment like *"Want to know WHY…? Part 2 👇"*.
5. **The ending must be a revelation** that makes viewers reconsider what they saw, not a repeat of the opening visuals. Then hard-cut back to frame 0 so the video loops.
6. **Time jumps must be explicit.** If chronology moves backward (a rewind), the viewer must clearly see that it's a rewind. Reversed footage alone confused people.

## 2. Visual rules

1. **If a camera could have filmed it, it must look filmed** (real stock footage, or calm AI motion graded to match). **If no camera could have filmed it, it must look designed** (Blender or graphics), never fake-filmed.
2. **Never let an AI model draw map or continent shapes.** Outlines come from data: plate model silhouettes are saved in `shorts/assets/`.
3. **AI video only for atmospheric motion:** dust, water, clouds, light, camera drift. Never ask it to move or reshape land; it morphs, and morphing looks "sickening".
4. **Transformations** (e.g. rock folding) only via **first- and last-frame pairs** (E1 → E2) made as edits of the same image. Even then, check that the middle frames show cause and effect, not just warping.
5. **No cut-out compositing for physical events.** A cut-out sliding over a photo reads as a sticker or tabletop slab. A collision needs a real scene where the contact is visible.
6. **One visual language per episode.** Cuts between sections need a bridge: matching camera direction, lighting and motion. A new rendering style mid-video feels like a different video.
7. **No unexplained graphics.** Rings, glows or arrows must obviously mean something, or they look like render artifacts.
8. **Kill AI tells:** smoke-like plumes on summits, impossible footprints, lava where there's no volcano, over-glossy "AI poster" colours. Start frames use camera-style prompts (35 mm, natural muted colour, grain), not "epic, dramatic".
9. **Polish only after the core action works.** Order: geometry/position → deformation → atmosphere → sound.

## 3. Accuracy

1. **No modern political maps** for ancient landmasses. They are inaccurate and politically sensitive (borders, Kashmir).
2. **Nothing that forms later appears earlier:** no Himalayas or Ganges plain before the collision, no Antarctic or Greenland ice before ~34 Ma.
3. **Every on-screen number** (years, distances, speeds) must come from the **same model and the same definition**, and the timestamps must match the labels.
4. **Present debated science as "scientists think".** Don't invent shapes that aren't known (e.g. Greater India's outline).

## 4. Process and checks

1. **Test the cheapest version first.** Run fast-mode or local tests before full-quality renders.
2. **Inspect motion, not just the final frame.** Check the first, middle and last frames with measurements (e.g. the gap to the coast).
3. **Sound design improves impact but cannot fix visual continuity.**
4. Don't keep iterating the same prompt on a failed approach. Change the method.

## 5. Tools, voice and costs (the user is credit-limited)

- **Voice:** ElevenLabs `eleven_v3`, voice "Teja Clone V3" (`hnvKSWZUzB30Og1MMmAl`).
  - One take, check it, then fix single lines only if needed.
  - About 450 credits per 30 s.
- **Sound effects:** ElevenLabs `eleven_text_to_sound_v2`, about 17 credits each. **Music:** `eleven_music_v2`, about 900 credits.
  - Reuse what's already in the library before generating more.
  - **Ask before spending.**
- **Higgsfield:** don't use without asking (limited credits).
- **Free stock footage first** (Pexels / Pixabay) for anything filmable.
- **RunPod:**
  - Create pods only on demand (A5000 for Blender, A40 for heavy ComfyUI) and terminate them when done.
  - Storage volume `slowlight-100` (CA-MTL-1) costs about $14/month.
  - Keep the account balance topped up, or the volume is at risk.

---

## On hold

### India Episode 1: "India is about to crash into Asia"

**Status: ON HOLD (2026-10-12). Not publishable yet; we will come back to it.**

**What exists:**
- **Script and voiceover:** 30 s v3 voiceover (`india_ep1_vo_v3.mp3`). The script is in `shorts/india-collision-series.md`.
- **Plate-data globe pipeline** (`tools/globe/`) and renders: racing hook, Madagascar breakaway, collision with leading-edge glow, today.
- **Fold shot:** Wan first-and-last-frame (E1 → E2).
- **Assets:** India silhouettes at 55 and 70 Ma (`shorts/assets/india/`) and the ChatGPT painted assets (A2, India #1, E1, E2).
- **Edits:** the edit v2 script (`tools/edit/edit_ep1_v2.py`), plus the ElevenLabs sound effects and music in the session scratchpad. Re-download them if they're lost.

**Verdict on edit v2** (the user and ChatGPT agree): better structure, but it's a collection of explainer visuals, not one gripping story.
1. **0–15 s:** the globe lacks progression. India reads as a raised cut-out, the compositions repeat, and the white rings look like artifacts.
2. **16–19 s:** the cross-section feels like a different video (different lighting, perspective and visual language), with no bridge from the moving continent.
3. **20–25 s:** the Everest plume looks artificial or volcanic. It's the weakest section, and the text does more work than the image.
4. **26–29 s:** the ending repeats the opening's globe look, so there's no final revelation.
5. **Chronology and labels:** the rewind must be explicit, and all distance counters must be checked against the same plate model and definition.

**Plan when resumed** (an editorial pass, not more AI generations):
1. Keep the strongest globe footage and tighten the opening.
2. Remove or redesign the rings.
3. Add a deliberate rewind transition.
4. Keep plate motion in Blender.
5. **Make the collision the visual climax** with a bridge (approach → contact → compression → mountains) using matching camera direction and light.
6. Replace the Everest plume shot with a natural mountain reveal (stock).
7. End on a purposeful present-day revelation shot.
8. The proper fix for the approach is a **Blender scene**:
   - India and Asia meshes from the plate data, flush in a continuous ocean
   - Asia fixed
   - a stable high-oblique camera
   - a three-frame position check first

   Estimated at about 8–10 hours of work. It can be reused for Episodes 2 and 3.

**Also queued in this series:**
- Ep 2: "What if India had no Himalayas?"
- Ep 3: "When the asteroid hit, India was already on fire"
- Part 2: "Why was India moving so fast?"
