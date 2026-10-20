# Slow Light "What If" #4: What if every mosquito died tonight? (31 s, wordless)

Status: APPROVED by the owner (18 Oct 2026). Nothing is built yet. This plan is frozen (no redo's); build once, check frames against the table, then deliver.

Format: 9:16, 1080x1920, 31 s, no voiceover, loops. Visuals + sound design + a few words of on-screen text. Tagged "thought experiment" on screen.
Idea: one wish everyone shares (no more bites), then the consequences nobody thinks about, ending on an open question. The reference video (a 98 s low-poly "what if we killed all mosquitoes") is inspiration for the *question only*. We do not copy its look, its stage UI, its button, its "would you press it" line or its Easter egg.

## Why this version
- Owner approved 30-35 s. 31 s keeps payoff by 15 s (playbook: payoff early, lightning Short lost people in the middle).
- Honest framing: the science says the outcome is debated. We show wins, costs and an open ending. We never claim ecosystem collapse.
- Time jumps are explicit and monotonic: NIGHT 1 -> WEEK 1 -> MONTH 1 -> YEAR 1 -> YEAR 10 on one left-hand time ladder (our existing device, new rungs).

## Fact guardrails (every claim on screen)
Status key: V = checked against a source on 18 Oct 2026; TO CHECK = must be verified before it goes on screen or into copy.

| On screen / said | Fact | Status |
|---|---|---|
| 610,000 malaria deaths a year | WHO World Malaria Report 2025: ~610,000 deaths in 2024, ~282 million cases | V (WHO, GHO page) |
| About 95% in Africa, mostly children under five | Same WHO report and news release (4 Dec 2025) | V |
| "About one death every 52 seconds" | Our arithmetic: 31,536,000 s / 610,000 = 51.7 s. Label "(2024, WHO)". Malaria only, not all mosquito-borne disease | V (arithmetic) |
| Only females bite | Blood is needed for egg development (Missouri Extension) | V |
| "Over 3,500 species; fewer than 100 spread disease" | Britannica ~3,500+; ASU Ask a Biologist: <3% (~90 species) transmit disease | V (say "over 3,500", not 3,700) |
| One bog orchid loses its pollinator | *Platanthera obtusata*: Aedes mosquitoes are the dominant pollinator of this orchid (PNAS 2020, Lahondere, Riffell et al.). Another ecologist calls mosquito pollination "relatively minor" overall, so say "one orchid", never "plants" | V, hedged |
| Chocolate is safe | Cacao is pollinated by *Forcipomyia* midges (Ceratopogonidae), not mosquitoes | V |
| "Something else moves in" / "hiccup" | Entomologist Joe Conlon in Nature 466:432 (2010, Janet Fang feature): ecosystems "will hiccup and then get on with life. Something better or worse would take over." Critics say that is overconfident (new vectors could fill the niche) | V (secondary sources; Nature is paywalled) |
| Arctic swarms and caribou | Biting-insect harassment cuts caribou feeding time and drives herds to windy ridges (Toupin et al. 1996, Rivière George herd: feeding 53% -> 30% of time; Russell & Nixon, Porcupine herd; Fancy 1983). Toupin found the energy-balance effect small, so say "swarms cost them feeding time", never "swarms kill caribou" and no "10,000 bites" number | V, hedged (abstracts only) |
| Wingbeat about 400 Hz | Female Aedes ~400-600 Hz depending on species and temperature | TO CHECK, or leave off screen |
| Dengue and Zika | Only some species carry them; wording is "mosquito-borne disease", not "all mosquitoes" | wording rule |
| "Killed half of all humans who ever lived" | Popular but contested | CUT, do not use |

Never say: "ecosystems collapse", "mosquitoes are useless", "malaria would end" (other vectors and a changed ecology are not modelled here). Say: "scientists disagree", "one expert predicted".

## Revision v2 (18 Oct 2026): storyboard merge
Owner shared a 10-panel ChatGPT storyboard. Decisions: opening = macro mosquito, pull back to reveal the swarm, vanish; middle = storyboard rhythm with balanced facts. The authoritative shot list and Flow prompts are now in `mosquito-flow-prompts.md`; the shot-plan table below is kept as history.
Keeps: the 10-beat rhythm, big stat panel ("~610,000 deaths from malaria in 2024 (WHO)"), the closing question, the final mosquito that loops, text at the top of frame with the subject below, "MOSQUITO" as a red word.
Changes (science and rules):
- **"MILLIONS OF LIVES COULD CHANGE"** is unsourced -> replaced by the WHO stat only.
- **Bird catching nothing / "FOOD WEBS WOULD CHANGE" / "SOME PLANTS DEPEND ON THEM"** overstate the science (predators mostly switch prey; mosquito pollination is minor; the only verified case is one bog orchid) -> hedged wording below.
- **AI-drawn world map** invents shapes (rule: never let AI draw maps) -> the malaria map is designed from `tools/mosquito/land.json` with sub-Saharan markers; the storyboard's worldwide red scatter is not the malaria burden.
- **The pink daisy-like flower** is not the bog orchid -> regenerate (Flow C).
- Red only as chips/markers (palette rule): "MOSQUITO" and "BETTER" become red chips.
- Time ladder dropped (storyboard puts malaria before the nature beats, which would break the monotonic rule); the only time label left is "YEAR 10".
- Wording rules for the nature beats (Nature 2010, Fang feature: predators could switch to other prey): say "some predators lose a meal, most would switch", "food webs might shift", "one orchid depends on them". Never "food webs would change" or "some plants depend on them".

## Revision log
- 18 Oct 2026, owner change: the hook now opens on a mosquito SWARM (under 2 s), the swarm vanishes on a bass impact into silence, smash cut to Earth. The single stock macro mosquito moves to the loop ending. Hook wording changed from "died" to "vanished" (matches the Sun-vanishes thought-experiment tone). All later beats shift +0.5 s; the YEAR 1 reveal now lands at 13.3 s (still before 15 s). No other beat changed.
- Flow clip plan, transitions and prompts: `mosquito-flow-prompts.md`.
- Owner confirmed both Pixabay clips are the same close-up of a mosquito biting skin. Use the longer one (https://pixabay.com/videos/mosquito-insect-pest-nature-274935/). The file is not in Drive yet; I need it uploaded (Drive or chat).

## Shot plan (31 s)
Grammar: camera pull-back / plunge from the playbook (3.3 A), one hero object per beat, one label per object, monotonic time ladder at the left (rungs NIGHT, WEEK, MONTH, YEAR, DECADE; red marker climbs). Palette: charcoal/navy, cream text, gold/teal accents, red only for markers and chips. Sun/galaxy/ring motifs from earlier reels are not reused.

Layer rule from the India project (rules/production-rules.md, on branch `feature/relaxed-johnson-43xliu`): if a camera could have filmed it, it looks filmed (graded stock); if not, it looks designed (local three.js). AI never draws accurate things.

| Time | Beat | Visual | Layer | Text (cream, red chip for numbers) | Sound |
|---|---|---|---|---|---|
| 0-1.2 | **Hook 1: the swarm, NIGHT 1** | Frame 0 is already moving: hundreds of mosquitoes stream toward the camera through dark, humid haze, wingbeats building. Under 2 s of swarm in total, no atmosphere build-up | Designed 3D (local three.js, instanced mosquito silhouettes, motion blur) | "WHAT IF EVERY MOSQUITO" typed fast, subject readable by about 1.1 s | Wingbeat whine on frame 0 (hit), rising tension |
| 1.2-2.0 | **Hook 2: the vanish** | At the bass impact the whole swarm disintegrates at once into a brief particle cloud; absolute silence | Designed 3D particle burst | "VANISHED?" slams in on the impact (full hook: "WHAT IF EVERY MOSQUITO VANISHED?") | Bass impact (second-biggest hit of the reel), whine cuts to absolute silence |
| 2.0-3.5 | **Hook 3: the scale** | Smash cut from empty air to Earth from space; one subtle pulse travels across the planet (pattern interrupt at 2.0 s) | Local three.js lattice-point Earth (same Earth is reused for YEAR 1) | "OVERNIGHT. ALL GONE." | Silence holds, then a soft low pulse with the planet pulse |
| 3.5-7.5 | **WEEK 1: Arctic** | Plunge from Earth down to a summer tundra plain; caribou herd under a dense swarm; the swarm lifts away and the herd spreads out and grazes | Designed 3D (tundra), particles | "WEEK 1" / "ARCTIC SWARMS: GONE" | Plunge whooshes, then calm wind |
| 7.5-12.5 | **MONTH 1: the cost** | Plunge to a northern bog: one orchid with a pollinator that never arrives (7.5-10.5 s). Then a chocolate pod: "SAFE" chip (10.5-12.5 s) | Orchid: designed (or approved stock); pod: designed | "MONTH 1" / "ONE ORCHID LOSES ITS POLLINATOR" then "CHOCOLATE? SAFE. MIDGES POLLINATE IT." | Soft ticks; a small chime on "SAFE" |
| 12.5-13.3 | **Held breath** | Hard cut to black, slow push on Earth at night | Designed | none | Near-silence (about -40 dB) |
| 13.3-19.5 | **YEAR 1: the biggest reveal** | Earth turns to Africa; red malaria-burden markers wink out one by one; the big number lands | Same lattice-point Earth as the hook (not the Scale Ladder Earth, not the India globe) | "YEAR 1" / "610,000 DEATHS A YEAR (2024, WHO)" then "ONE EVERY ~52 SECONDS. MOSTLY CHILDREN UNDER 5." | HERO hit of the reel on the number (must be bigger than the vanish impact), sub wall, then quiet |
| 19.5-26 | **YEAR 10: the open question** | Same tundra/bog camera as WEEK 1, ten years on: other insects fill the empty air (new, smaller particle swarms) | Designed, mirrors the Arctic shot | "YEAR 10" / "SOMETHING ELSE MOVES IN." / "BETTER, OR WORSE?" | A different, thinner texture: new insect hum |
| 26-31 | **Loop** | 26-27.5 s: Earth, end line stays up. 27.5-29.5 s: the single stock macro mosquito biting skin, whine rising. 29.5-31 s: it bursts apart and the particles re-form into the swarm, so the last frame matches frame 0 | Earth + stock macro + particle reform | End line "WOULD EARTH BE BETTER WITHOUT THEM?" (typed once, n >= 1) and "THOUGHT EXPERIMENT" tag | Whine rises into frame 0 so the loop is audible |

Monotonic counter: the ladder only moves forward NIGHT 1 -> WEEK 1 -> MONTH 1 -> YEAR 1 -> YEAR 10. The script asserts this frame by frame (as in overlay8).

## Sound plan
- New sound family, not the Ladder's brass-and-sub and not Night Sky's v4 palette. Wordless, no music bed with drums.
- Hit budget: frame 0 (whine), the burst at about 2.2 s, and the single hero hit on the YEAR 1 number. Nothing else peaks.
- Held-breath silence at 12-12.8 s, then the hero hit.
- Phones: keep sub on the hit bus only, 90 Hz high-pass elsewhere. Target about -15 LUFS; check true peak after AAC.
- Licences: CC0, or CC BY with full credit and "changes were made". Never CC BY-NC. Synthesised whine and ticks are free. Record every file in `audio-attribution.md` and the reel's publish copy.

## What is needed from the owner before building
1. ~~Sign-off on this plan~~ done (approved 18 Oct 2026).
2. Stock clip choice: a macro mosquito landing/biting clip and optionally an orchid clip. I will list Pexels/Pixabay candidates and the licence of each; the owner approves.
3. Permission before any spend: RunPod pod (only if a still must be animated with Wan, atmospheric motion only), ElevenLabs/Higgsfield (not needed for this reel, it is wordless).

## Stock candidates (owner to approve; I could not view or download clips from this container)
Pexels returns 403 to this environment, and no free mosquito *video* turned up on Pexels or Wikimedia Commons in search. Pixabay has two candidates by the same uploader (BlenderTimer / Daniel Roberts), both 3840x2160, 24 fps, MP4, "Free for use under the Pixabay Content License" (free commercial use, attribution not required, not CC0). Pages carry tags "Macro, Skin, Wildlife" but do not say what the mosquito is doing, and show no AI label:
- https://pixabay.com/videos/mosquito-insect-pest-nature-274935/ (about 18 s)
- https://pixabay.com/videos/mosquito-insect-pest-nature-274929/ (about 8 s)
Owner: open both, say which (if either) shows a mosquito landing or biting skin in macro, and download it (or upload it to Drive). Fallback if neither works: the owner searches Pexels/Pixabay/Commons for another clip, or we build the hero mosquito procedurally in three.js (a designed look, no AI).
Rule: record the clip's URL and licence in `audio-attribution.md`-style credits for the reel before posting. Also check any orchid footage the same way (not yet shortlisted).

## Flow (Veo) clip review, 18 Oct 2026
Owner supplied three Google Flow clips (10 s, 1080x1920, 24 fps, each with AI audio that we drop) and the Pixabay macro (`274929.mp4`, 4K, 8.3 s, a mosquito standing on skin with its proboscis in, near-static, warm pink). Drive folder: `1MWLOBcSAru1nLvCojDsi7fS151a1Iia4`.
- **Baked text:** all three Flow clips have AI-drawn captions ("WHAT IF EVERY MOSQUITO VANISHED?", "OVERNIGHT. ALL GONE.", "MILLIONS OF LIVES CHANGE", "BUT NATURE NOTICES", "SOME PLANTS DEPEND ON THEM.", "WOULD EARTH BE BETTER?"). Rule: no text baked into generated clips. Use only text-free windows, or regenerate with "no text, no captions".
- **Watermark:** a 72 px Gemini sparkle at about x 864-936, y 1704-1776 (it appears from about 2.5 s). `delogo=x=852:y=1692:w=96:h=96` removes it cleanly on dark sky and leaves a faint smear on busy backgrounds; it sits in the bottom 10% (platform UI zone). The invisible SynthID mark stays, so keep the AI-assisted label on upload.
- **Clean windows (before delogo):** `vanishes` 0-0.4 s two mosquitoes on skin, 2.9-3.9 s night city with a swarm of glowing dots lifting, 6.0-7.9 s Earth (night-side lights, no overlay), 8.0-9.9 s Arctic water with light ribbons. `earth` 3.0-4.1 s Earth pushing in to Africa, 4.4-4.7 s plunge tunnel, 5.0-6.3 s tundra bog with a mosquito swarm, 9.0-9.9 s red ribbons over the bog. `pollinator` 0-3.3 s mosquito on a white orchid turning to dust, 5.9-6.8 s Earth with a red network, 8.8-9.9 s a single mosquito hovering with blurred wings (best loop ending).
- **Do not use:** `earth` 0-1.3 s (red patches over the Mediterranean and the Sahara are not the malaria burden, which is mainly sub-Saharan Africa; fact rule). The white orchid is a moth orchid, not *Platanthera obtusata*, so the orchid beat needs a caption that says it is illustrative, or a regeneration of a small green-white bog orchid.
- **Unexplained graphics:** the glowing white/red ribbons over the bog and the red network on Earth have no stated meaning (playbook rule: no unexplained graphics). Keep only if the caption or beat explains them, else cut.
- **Look decision pending:** the Flow plates are photoreal dark-navy with warm highlights; the designed lattice Earth in `tools/mosquito/` would clash with them. One visual language per reel: either photoreal Flow plates + designed data overlays, or fully designed three.js + the real macro stock. The Pixabay macro is warm pink and would need a heavy navy/teal grade to sit beside Flow plates.

## Build outline (after sign-off)
1. `shot.js`-style test stills of each designed beat; one contact-sheet check.
2. Overlay (PIL stream) with the time ladder, hook A/B, chips and the monotonic assertion.
3. Mix script (numpy buses, side-chain ducking).
4. Composite, loudness and true-peak check, loop check (last frame -> frame 0).
5. Publish copy with a "thought experiment, AI-assisted visuals" label and credits.

## Publishing notes
- Pinned comment idea: "Would you do it? Tell me why." (an open question, not the reference's yes/no poll).
- Do not write "ecosystem collapse" or "malaria would end" in the caption. Source line: "Malaria deaths: WHO World Malaria Report 2025."

## Opening v7 (owner-approved style of v6, rebuilt natively; 10 s)
v6 was a 512x910 procedural render upscaled 2x (hence soft). v7 redraws everything natively at 1080x1920 in code (tools/mosquito/opening2.html, canvas 2D; render2.js; mix_open.py): sunset marsh with the swarm losing flight and falling, then two continuous camera-move transitions: (1) the camera lifts away from the marsh to orbit as the Earth rises with its rim glow (3.45-4.95 s, motion blur); (2) the Earth dives into Africa and the globe becomes the data panel (6.5-7.45 s). Earth is Natural Earth 110m land (public domain) with procedural city lights. Text: "WHAT IF EVERY MOSQUITO VANISHED TONIGHT?" (script line, Earth), "THE HUMAN COST", counter to 610,000 (WHO 2024), "Malaria took over six hundred thousand lives." Markers are illustrative. Sound is synthesised (no credits).

## Reel v9 (24.77 s): voice-over and retiming
Voice: Higgsfield preset "Fraser" via the ElevenLabs engine (text2speech_v2). Lines: "One species. Paused." | "Six hundred and ten thousand deaths. In twenty twenty-four." (x1.25) | "Transmission interrupted." | "The night goes quiet." | "A food source disappears." | "A pollinator. Forgotten." | "Would you erase them?". Retiming of the v8 frames (build_reel2.py, retime_audio.py): freeze on the empty sky 0.6 s after the swarm falls; Earth section x1.2; slow 1.4 s hold on TRANSMISSION INTERRUPTED (old 12.0-12.3 s rendered slowly); flower section x1.129; final grassland x1.25 (trimmed about 0.9 s overall). Voice ducks the bed by about 4 dB.

## Reel v10 (24.77 s): voice-over v2
User-supplied ElevenLabs take (Max voice, one 23.9 s file, 7 lines from mosquito-reel-voiceover-v2.md). tools/mosquito/retime_audio2.py trims the long pauses inside lines and places each on its beat: 3.9 s (x1.15), 7.2, 11.9 (x1.1), 13.8 (x1.12), 16.6, 19.0, 21.9 (ends 24.1). Same picture as v9; voice ducks the bed as before. AI-voice label still applies.
