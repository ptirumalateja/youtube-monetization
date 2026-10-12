# India Ep 1: visual plan v2 (painted cinematic, 2.5D)

This replaces the orbital-globe look from the rough cut. The script, the 30 s voiceover (`eleven_v3`, Teja Clone V3) and the 12-beat structure stay the same.

## Style

- **Look:** painted cinematic geological epic, i.e. painterly realism. Deep atmospheric blues, warm low sun, volumetric clouds and light shafts.
- **Not this:** cel-shaded anime. It would clash with the realistic Everest and present-day shots and read as a kids' explainer.
- **One look for all 12 beats.** Every image starts from the same style prompt.

## Hard rules for every image

1. 9:16 vertical, at the highest resolution available.
2. **No text, labels, arrows or UI.** All of these are added in the edit.
3. **No lava, no fire, no volcanic glow.** Continental collision is crushing and folding, not eruption.
4. **No Himalayas before the collision.** Asia's southern edge is low land.
5. India uses the same painted texture in every shot. Its outline comes from the plate data (see 2.5D below).

**Style prefix** (paste at the start of every ChatGPT prompt):

> Cinematic hand-painted geological epic, painterly realism, deep atmospheric blues and warm golden low sunlight, volumetric clouds, soft light shafts, high detail, vertical 9:16. No text, no labels, no arrows, no UI, no lava, no fire.

## How each beat is made

| Beat | s | Method | Why |
|---|---|---|---|
| 1 Ancient Earth | 0–2 | **2.5D**: painted ocean plate + India cut-out layer + cloud layers, camera push | India keeps its exact shape; no AI morphing |
| 2 India breaks free | 2–4 | **2.5D**: Madagascar background plate, India layer slides away along its real path, ocean gap opens | Real motion from plate data |
| 3 Faster journey | 4–7 | **2.5D**: India layer moves fast over the ocean plate, cloud parallax, accelerating camera | Speed is felt through parallax |
| 4–5 Approaching / final approach | 7–12.5 | **2.5D**: Asia coast plate grows in size, gap narrows, slow push-in, pause | Builds anticipation |
| 6 Collision | 12.5–14.5 | AI image (no lava) + **Wan**: dust surge and small rock movement only. **Camera jolt added in the edit** | Wan moves only particles, never the land |
| 7–8 Compression, mountains rise | 14.5–21 | **Two images** (flat layers → folded, thickened layers with young ridges) + **Wan first-and-last-frame** | The deformation is defined by the two frames. Test once; fall back to a Blender cross-section if it morphs |
| 9 New landscape / Everest | 21–26 | AI image + gentle Wan motion (clouds, light), or real stock drone footage | Safe motion |
| 10–12 Today | 26–29 | Painted present-day Earth image + slow push, data panel overlay | Calm ending, loops to beat 1 |

### 2.5D compositing

Each 2.5D shot is built from flat layers moved by the camera in Blender. No AI video model is involved:

- an ocean / Earth background plate
- India as a separate painted layer, **masked by India's true outline from the plate model** at each moment
- Asia / Madagascar layers
- 2–3 cloud layers at different depths

India moves along its real path, and parallax plus camera moves give the sense of speed. This is the same technique as cinematic anime backgrounds.

### Data panels (added in the edit, styled to match the ChatGPT storyboard)

- Year label
- Speed panel ("~20 CM / YEAR")
- "Distance to Asia" countdown
- x/y/z axis marker
- Small locator globe
- Thin motion arrows

## Images to generate in ChatGPT

Use the style prefix plus each line below.

| ID | Prompt (after the prefix) |
|---|---|
| **A1** | High oblique aerial view of a vast ancient open ocean from about 2,000 km up; the curve of the Earth on the horizon; a low, flat, distant coastline of a continent along the top edge. The middle and bottom of the frame are empty ocean (an empty stage). No landmass in the centre. |
| **A2** | Same camera and composition as A1, but the continental coastline is much closer and larger, filling the top third. Still low, flat land, **no mountains**. |
| **B** | A large island continent shaped like the Indian subcontinent, seen from directly above, painted lush green and ochre with eroded cliff edges, isolated on a **flat pure green #00FF00 background**, no shadow, no ocean. |
| **C** | High oblique aerial view of the East African coast and Madagascar island on the left; the open ocean to the east (right side) is empty. |
| **D** | Low aerial view of a continental landmass pressing into another: the leading edge crumples, rock layers buckle upward, heavy slow dust rising along the boundary, **no lava, no fire**, only low young ridges, no tall snowy peaks. |
| **E1** | Cutaway cross-section of Earth's crust at a collision zone: flat horizontal layered rock strata with ocean sediment between two continental plates, landscape on top, dramatic side light. |
| **E2** | **Exactly the same camera, composition and lighting as E1**, but the layers are folded, compressed and thickened upward into young mountain ridges on the surface. |
| **F** | The Himalayas at golden hour, a sea of clouds, a vast snowy range. |
| **G** | Present-day Earth from orbit, centred on India and the Himalayas, soft sunrise on the limb. |

**Tip:** generate E1 first, then ask for E2 as an edit of E1 ("same image, but…"), so the two frames line up for the Wan first-and-last-frame transition.
