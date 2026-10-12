# Series: "India's Deep-Time Story" (3 Shorts)

Your four topics combine into one three-part series:

| Ep | Title | Built from your topics |
|---|---|---|
| 1 | **India is about to crash into Asia** | "What happened when India hit Asia" ("Why so fast?" becomes Part 2) |
| 2 | **What if India had no Himalayas?** | "What if India had no Himalayas?" |
| 3 | **When the asteroid hit, India was already on fire** | "The asteroid that changed everything" (Chicxulub and the Deccan Traps, both about 66 million years ago) |

Three linked episodes do better than three separate one-off videos. "Part 2" in the title brings people back, and the algorithm learns what the channel is about.

---

## The visual problem (read first)

**AI video models cannot draw accurate continents.** If you ask one to "show India moving toward Asia", it will invent coastlines. Indian viewers will spot a wrong-shaped India immediately, and the comments will be about that instead of the story.

**Solution: a two-layer approach.**

1. **Accurate layer (the plate-movement shots):** a 3D globe animated from real plate-reconstruction data.
   - **GPlates** is free and open source (gplates.org). Use it with the **EarthByte** plate models (Müller et al.) to get India's position from about 120 Ma to today.
   - Export the coastlines and plate polygons for each time step, then render them in Blender on a photoreal globe. NASA Blue Marble textures and NASA/ETOPO elevation data are public domain.
   - Add atmosphere glow, cloud layers and a slow orbiting camera. That's the "state-of-the-art" look: real data, rendered cinematically.
   - **Check the licence of any paleo-map imagery you don't create yourself.** Ron Blakey's Deep Time Maps are commercially licensed, and Scotese PALEOMAP has its own terms.
2. **Cinematic layer (everything else):** AI-generated video for the shots that don't need map accuracy, such as the Everest summit, fossils in rock, an ocean floor crumpling, mountains rising and an aerial flyover.

**Rule: never let an AI model draw the outline of India.**

---

## Episode 1: "India is about to crash into Asia"

**Length:** about 30 s · 9:16 · no still images · voiceover from frame 0
**Structure:** tease → rewind → story → payoff → loop

### Visual rule

- **If a camera could have filmed it, it should look filmed.** Use real stock footage, or AI shots of calm natural motion graded to match.
- **If no camera could have filmed it, it should look designed.** Use Blender visualisations, never AI pretending to be footage.

### Fact base

- The summit rock of Everest is marine limestone (the Qomolangma Formation) with fossils of sea creatures such as crinoids and trilobites.
- India separated from Madagascar about 90 Ma, after leaving the rest of Gondwana earlier.
- India's peak speed was about 15–20 cm/yr (roughly 80–50 Ma). Typical plates move 2–5 cm/yr, and fingernails grow about 3–4 cm/yr. "Up to five times faster than most continents" is therefore safe.
- **Why so fast?** There are competing explanations, so present them as "scientists think":
  - India's lithosphere was unusually thin, about 100 km (Kumar et al., 2007, *Nature*).
  - It was pulled by two subduction zones at once (Jagoutz et al., 2015, *Nature Geoscience*).
  - It got a push from the Réunion plume head (Cande & Stegman, 2011, *Nature*).
- The collision began about 50–55 Ma.
- In the Müller et al. (2019) plate model, India's visible landmass only reaches Asia around 40–35 Ma. The first contact was India's northern margin ("Greater India"), now underthrust beneath Tibet, and its size is debated. Hence the wording "India's leading edge… hit Asia". Never draw an invented Greater India outline.
- India still converges with Asia at about 4–5 cm/yr, and the Himalayas are still rising by millimetres per year.

### Narration (about 78 words, about 30 s)

> India is about to crash into Asia... at five times the speed of most continents.
>
> Ninety million years ago...
> it broke away from Madagascar and raced north, up to 20 centimetres a year.
>
> About 50 million years ago, its leading edge hit Asia.
>
> The ocean floor between them was crushed... and pushed into the sky.
>
> That's why the top of Everest is ancient seafloor — full of sea-creature fossils.
>
> And India is still pushing. Everest is still rising.

**Cut from the 38 s version, saved for Part 2:**
- "Why so fast?" (thin plate, two subduction zones).
- The fingernail comparison.

Pin a comment: *"Want to know WHY India was moving so fast? Part 2 👇"*

### Shot list

**Layer key:**
- `GLOBE`: Blender globe driven by plate data (`tools/globe/`)
- `DESIGN`: Blender designed visualisation
- `STOCK`: real stock footage
- `AI`: Wan clip made with the look-test recipe

| # | Time | Narration | Layer | Shot | Text on screen | SFX | Status |
|---|---|---|---|---|---|---|---|
| 1 | 0–4 | "India is about to crash into Asia… five times the speed…" | GLOBE | **HOOK:** the racing globe (80 → 52 Ma) with the year counter. At about 3.5 s, a **4–6 frame flash** of the shot 7 impact, then a hard cut | **India is about to hit Asia** | Rising rumble and ticking; low boom on the flash | ✅ `race_clean.mp4`, flash from `shot7_clean.mp4` |
| 2 | 4–6 | "Ninety million years ago…" | GLOBE | Rewind: shot 1 played backwards at 4× speed, with the counter spinning back to 90,000,000 | **90 million years ago** | Tape-rewind whoosh | ✅ made in the edit from `race_clean.mp4` |
| 3 | 6–11 | "…broke away from Madagascar and raced north…" | GLOBE | India pulls away from Madagascar with a faint wake (92 → 72 Ma) | **20 cm a year** | Deep tearing crack, then a whoosh | ✅ `shot4_clean.mp4` |
| 4 | 11–15 | "About 50 million years ago, its leading edge hit Asia." | GLOBE | The collision, with the leading-edge glow (50 → 35 Ma). **Music freezes on contact** | **50 million years ago** | Silence, then a massive low impact boom | ✅ `shot7_clean.mp4` |
| 5 | 15–20 | "The ocean floor… crushed… pushed into the sky." | DESIGN, then STOCK | Designed cross-section of seafloor layers (with fossils) folding into peaks, cut to a real Himalaya aerial | — | Rock grinding, rising rumble, wind | ⏳ fold shot to build; stock aerial to find |
| 6 | 20–26 | "…top of Everest is ancient seafloor… fossils." | STOCK and AI | Everest summit (stock drone, or the look-test clip), then a fossil close-up in grey limestone | **Everest = ancient seafloor** | Wind, then sudden quiet on the fossil | ⏳ stock to find; fossil close-up to make |
| 7 | 26–30 | "And India is still pushing. Everest is still rising." | GLOBE | Today's globe with the pulsing collision line. On "rising", **hard cut to shot 1** so the video loops | **Still moving: ~4 cm/yr** | Low pulse, cut to silence | ✅ `shot10_clean.mp4` |

### Sourcing notes

- **Stock:** search Pexels/Pixabay for "Everest drone" and "Himalaya aerial". Check each clip's licence and keep the links.
- **Fossil close-up:** use the AI look-test recipe, or a stock photo of a crinoid fossil animated with a slow push in the edit.
- **Credit line:** *"Plate reconstruction: Müller et al. (2019), EarthByte / GPlates. Earth imagery: NASA Blue Marble."*

---

## Episode 2: "What if India had no Himalayas?" (outline)

- **Hook (motion):** the Himalayan range collapsing and sinking into flat plains in time-lapse. *"Delete the Himalayas... and India changes forever."*
- **Beats:**
  - The Himalayas act as a wall. They hold warm, moist monsoon air over India and block freezing air from Central Asia.
  - Climate models suggest that without them, northern India would be much drier and colder in winter. Phrase it as "models suggest"; Boos & Kuang (2010, *Nature*) is the key reference.
  - No glaciers means no Ganga, Indus or Brahmaputra as we know them.
- **Twist ending:** *"The mountains didn't just give India its border... they gave it its rain."*

## Episode 3: "When the asteroid hit, India was already on fire" (outline)

- **Hook:** the asteroid entering the atmosphere above the Gulf of Mexico. Cut to India, already glowing with lava fields.
- **Beats:**
  - About 66 Ma, the Chicxulub asteroid hits.
  - At the same time, the Deccan Traps in India are erupting enormous floods of lava.
  - Scientists still debate how much each contributed to the dinosaur extinction. Most see the asteroid as the main trigger, with the Deccan eruptions possibly adding stress.
- **India angle:** you can still stand on those lava flows today, in the Western Ghats and the Deccan Plateau, for example at Mahabaleshwar and Matheran.
- **Caution:** don't say "India killed the dinosaurs". Say "India may have helped".
