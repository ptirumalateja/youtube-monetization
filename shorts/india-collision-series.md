# Series: "India's Deep-Time Story" (3 Shorts)

Your four topics combine into one three-part series:

| Ep | Title | Built from your topics |
|---|---|---|
| 1 | **India is about to crash into Asia** | "Why did India move so fast?" and "What happened when India hit Asia" |
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

**Length:** about 38 s (under 40) · 9:16 · no still images · **Hook type:** anticipation (hook B), with voiceover from frame 0

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

### Narration

> India is about to crash into Asia...
> moving five times faster than most continents.
>
> When it hits, the ocean floor in between ends up on top of Mount Everest.
>
> 90 million years ago, India broke free and raced north.
> Most continents move as fast as your fingernails grow. India moved up to 20 centimetres a year.
>
> Scientists think its plate was unusually thin... and two subduction zones were dragging it north.
>
> Around 50 million years ago, India's leading edge — now buried beneath Tibet — hit Asia.
>
> The ocean floor was crushed... folded... and pushed into the sky.
>
> That's why Everest's summit is full of ancient sea creatures.
>
> And India is still pushing. Everest is still rising.

(About 100 words, about 38 s. Voice starts on frame 0, over the moving globe. There's no title card or text-only screen: the on-screen text on shot 1 does the job a title would. The last line cuts straight back to shot 1, so the video loops: "...still rising" → "India is about to crash into Asia".)

### Shot list

**Layer key:**
- `GLOBE`: Blender globe driven by GPlates plate data
- `DESIGN`: Blender designed visualisation
- `STOCK`: real stock footage (Pexels/Pixabay, free licence)
- `AI`: Wan clip made with the look-test recipe (full-quality start frame, no speed LoRA, graded with grain)

| # | Time | Line | Layer | Shot | Text on screen | SFX |
|---|---|---|---|---|---|---|
| 1 | 0–3 | "India is about to crash into Asia…" | GLOBE | **HOOK, frame 0 already moving:** India is mid-ocean (about 70 Ma), racing north toward Asia with a faint motion trail. The camera is low and close, with Asia looming at the top of frame. A year counter in the corner rolls down: "70,000,000 years ago…" | **India is about to hit Asia** | Deep rumble rising, ticking |
| 2 | 3–6 | "…five times faster than most continents." | GLOBE | Faster push alongside India, with the trail stretching and clouds whipping past | **5× faster** | Whoosh, bass swell |
| 3 | 6–10 | "When it hits… on top of Mount Everest." | STOCK/AI | A quick teaser of the Everest summit ridge with blowing spindrift, then a macro of summit rock with a fossil sea lily | — | Wind, then sudden quiet |
| 4 | 10–14 | "90 million years ago, India broke free…" | GLOBE | Rewind: the counter jumps back to 90 Ma. India tears away from Madagascar, with a thin glowing seam opening between them | **90 million years ago** | Rewind sweep, a crack |
| 5 | 14–19 | "…fingernails… 20 centimetres a year." | STOCK + GLOBE | Split screen: a fingernail time-lapse (stock) on top, India racing on the globe below | **~4 cm/yr vs 20 cm/yr** | Ticking clock |
| 6 | 19–25 | "…unusually thin… two subduction zones…" | DESIGN | Clean designed cutaway of Earth's interior. A thin plate glides over a glowing mantle, with two trenches ahead pulling it down like conveyor belts. Museum-quality look, not fake footage | — | Deep grinding |
| 7 | 25–29 | "…around 50 million years ago… India's leading edge… hit Asia." | GLOBE | The gap closes along the real data path (50 → 35 Ma). A thin glowing line along India's northern edge marks the buried leading edge. **Freeze the music for a beat on contact** | **50 million years ago** | Silence, then a massive low impact boom |
| 8 | 29–34 | "…crushed… folded… pushed into the sky." | DESIGN | Designed cross-section: ocean-floor rock layers (with fossil shells visible in them) fold and rise into peaks | — | Rock cracking, rising rumble |
| 9 | 34–38 | "…summit of Everest… ancient sea creatures." | STOCK | Real drone footage of the Himalayas or Everest at golden hour, then a cut back to the fossil macro from shot 3 | — | Music hits full, wind |
| 10 | 38–41 | "And India is still pushing into Asia…" | GLOBE | Today's globe, with India pressed into Asia and a soft pressure glow pushing north | **Still moving: ~4 cm/yr** | Low pulse |
| 11 | 41–45 | "…so Everest is still rising." | AI | The Everest summit ridge with a snow plume blowing (the look-test shot). On the last word, **hard cut to shot 1** so the loop is seamless | — | Wind, cut to silence |

### Sourcing notes

- **Stock:** search Pexels/Pixabay for "Everest drone", "Himalaya aerial" and "fingernail time lapse". Check each clip's licence and keep the links.
- **Fossil macro (shots 3 and 9):** AI with the look-test recipe, or a stock photo of a crinoid fossil animated with a slow push in the edit.
- **Globe (shots 1, 2, 4, 7 and 10):** one Blender scene rendered at different times and camera positions. Credit line: *"Plate reconstruction: Müller et al. (2019), EarthByte / GPlates."*

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
