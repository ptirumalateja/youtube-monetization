# Series: "India's Deep-Time Story" (3 Shorts)

Your four topics combine into one three-part series:

| Ep | Title | Built from your topics |
|---|---|---|
| 1 | **The top of Everest was once the bottom of an ocean** | "Why did India move so fast?" and "What happened when India hit Asia" |
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

## Episode 1: "The top of Everest was once the bottom of an ocean"

**Length:** about 42 s · 9:16 · no still images

### Fact base

- The summit rock of Everest is marine limestone (the Qomolangma Formation) with fossils of sea creatures such as crinoids and trilobites.
- India separated from Madagascar about 90 Ma, after leaving the rest of Gondwana earlier.
- India's peak speed was about 15–20 cm/yr (roughly 80–50 Ma). Typical plates move 2–5 cm/yr, and fingernails grow about 3–4 cm/yr.
- **Why so fast?** There are competing explanations, so present them as "scientists think":
  - India's lithosphere was unusually thin, about 100 km (Kumar et al., 2007, *Nature*).
  - It was pulled by two subduction zones at once (Jagoutz et al., 2015, *Nature Geoscience*).
  - It got a push from the Réunion plume head (Cande & Stegman, 2011, *Nature*).
- The collision began about 50–55 Ma.
- India still converges with Asia at about 4–5 cm/yr, and the Himalayas are still rising by millimetres per year.

### Narration

> The top of Mount Everest... was once the bottom of an ocean.
>
> Because about 90 million years ago, India wasn't part of Asia.
> It was a giant island... drifting north.
>
> And it was fast.
> Most continents move about as fast as your fingernails grow.
> India moved up to five times faster.
>
> Why? Scientists think its plate was unusually thin...
> and it was being dragged north by two subduction zones at once.
>
> Then, around 50 million years ago... it hit Asia.
>
> The ocean floor between them was crushed... folded...
> and pushed into the sky.
>
> That's the Himalayas.
>
> And India never stopped pushing.
> Which means Everest... is still rising.

(About 105 words. The last shot returns to the summit to loop back to line 1.)

### Shot list

**Layer key:** `AI` = AI video generation · `GLOBE` = GPlates/Blender data render

| # | Time | Line | Layer | Shot | SFX |
|---|---|---|---|---|---|
| 1 | 0–3 | "The top of Mount Everest…" | AI | **HOOK, frame 0 already moving:** a fast aerial rush up the final ridge of Everest at sunrise, with wind-blown snow plumes, cresting the summit | Howling wind, whoosh |
| 2 | 3–5 | "…the bottom of an ocean." | AI | Macro of grey summit limestone, frost blowing away to reveal a fossil sea lily. A match-cut dissolve turns the rock into the same fossil alive and swaying on an ancient seafloor | Wind fades into deep underwater ambience |
| 3 | 5–9 | "…India wasn't part of Asia. It was a giant island…" | GLOBE | Photoreal globe at about 90 Ma. Slow push in on India, alone in a vast ocean, with clouds drifting | Low ocean drone |
| 4 | 9–12 | "And it was fast." | GLOBE | Time-lapse: India streaks north across the ocean, with a faint glowing motion trail behind it. Speed it up hard | Rising whoosh, bass swell |
| 5 | 12–17 | "…fingernails… five times faster." | AI and GLOBE | Split screen: a fingernail growing in time-lapse on top, India racing on the globe below | Ticking clock |
| 6 | 17–23 | "…unusually thin… two subduction zones…" | AI | Cutaway cross-section of Earth's crust. A thin plate slides over glowing orange mantle, with two dark trenches ahead pulling it down like a conveyor | Deep grinding, magma rumble |
| 7 | 23–26 | "…around 50 million years ago… it hit Asia." | GLOBE | India makes contact with Asia. **Freeze the music for a beat on contact** | Silence, then a massive low impact boom |
| 8 | 26–31 | "…crushed… folded… pushed into the sky." | AI | Ground-level time-lapse: layered seafloor rock buckles, folds and rises into jagged peaks, water draining off, dust and clouds forming | Rock cracking and rumbling, building |
| 9 | 31–34 | "That's the Himalayas." | AI | Epic aerial reveal of the Himalayan range at golden hour, with the camera pulling up and back | Music hits full, wind |
| 10 | 34–38 | "And India never stopped pushing." | GLOBE | Today's globe, with India pressed into Asia and a subtle glowing arrow of pressure pushing north | Low pulse |
| 11 | 38–42 | "…Everest… is still rising." | AI | Slow push toward Everest's summit with snow plume blowing. The final frame matches shot 1's framing so the loop is seamless | Wind, cut to silence on the last word |

### AI prompt suffix (every AI shot)

*Photoreal, cinematic, 9:16, natural lighting, documentary style, no text, no captions, no maps, no logos, no watermark.*

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
