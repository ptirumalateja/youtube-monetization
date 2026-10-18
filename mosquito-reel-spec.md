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

## Shot plan (31 s)
Grammar: camera pull-back / plunge from the playbook (3.3 A), one hero object per beat, one label per object, monotonic time ladder at the left (rungs NIGHT, WEEK, MONTH, YEAR, DECADE; red marker climbs). Palette: charcoal/navy, cream text, gold/teal accents, red only for markers and chips. Sun/galaxy/ring motifs from earlier reels are not reused.

Layer rule from the India project (rules/production-rules.md, on branch `feature/relaxed-johnson-43xliu`): if a camera could have filmed it, it looks filmed (graded stock); if not, it looks designed (local three.js). AI never draws accurate things.

| Time | Beat | Visual | Layer | Text (cream, red chip for numbers) | Sound |
|---|---|---|---|---|---|
| 0-3 | **Hook, NIGHT 1** | Frame 0: extreme macro of a mosquito landing on skin, already moving. At about 2.2 s it bursts into particles; the whine cuts to silence | Graded stock macro + local particle burst | Hook A "WHAT IF EVERY MOSQUITO DIED TONIGHT?" typed by 1.9 s. Hook B (overlay-only) "TONIGHT, EVERY MOSQUITO DIES." | Wingbeat whine on frame 0 (hit), then sudden silence on the burst |
| 3-7 | **WEEK 1: Arctic** | Fast pull-back from the particles to a summer tundra plain; caribou herd under a dense swarm; the swarm lifts away and the herd spreads out and grazes | Designed 3D (tundra), particles | "WEEK 1" / "ARCTIC SWARMS: GONE" | Whooshes, then calm wind |
| 7-12 | **MONTH 1: the cost** | Plunge to a northern bog: one orchid with a pollinator that never arrives (7-10 s). Then a chocolate pod: "SAFE" chip (10-12 s) | Orchid: designed or graded stock; pod: designed | "MONTH 1" / "ONE ORCHID LOSES ITS POLLINATOR" then "CHOCOLATE? SAFE. MIDGES POLLINATE IT." | Soft ticks; a small chime on "SAFE" |
| 12-12.8 | **Held breath** | Hard cut to black, slow push on Earth at night | Designed | none | Near-silence (about -40 dB) |
| 12.8-19 | **YEAR 1: the biggest reveal** | Earth turns to Africa; red malaria-burden markers wink out one by one; the big number lands | Local three.js globe: lattice-point Earth (not the Scale Ladder Earth, not the India globe) | "YEAR 1" / "610,000 DEATHS A YEAR (2024, WHO)" then "ONE EVERY ~52 SECONDS. MOSTLY CHILDREN UNDER 5." | Biggest hit of the reel on the number (braaam family rule: hit only here), sub wall, then quiet |
| 19-26 | **YEAR 10: the open question** | Same bog/tundra camera as 3-7, ten years on: other insects fill the empty air (new, smaller particle swarms) | Designed, mirrors the Arctic shot | "YEAR 10" / "SOMETHING ELSE MOVES IN." / "BETTER, OR WORSE?" | A different, thinner texture: new insect hum |
| 26-31 | **Loop** | Pull back from Earth to one single mosquito on a leaf; its wings start to buzz; hard cut to frame 0 | Same macro stock as frame 0 | End line "WOULD EARTH BE BETTER WITHOUT THEM?" (typed once, n >= 1) and "THOUGHT EXPERIMENT" tag | Whine rises into frame 0 so the loop is audible |

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

## Build outline (after sign-off)
1. `shot.js`-style test stills of each designed beat; one contact-sheet check.
2. Overlay (PIL stream) with the time ladder, hook A/B, chips and the monotonic assertion.
3. Mix script (numpy buses, side-chain ducking).
4. Composite, loudness and true-peak check, loop check (last frame -> frame 0).
5. Publish copy with a "thought experiment, AI-assisted visuals" label and credits.

## Publishing notes
- Pinned comment idea: "Would you do it? Tell me why." (an open question, not the reference's yes/no poll).
- Do not write "ecosystem collapse" or "malaria would end" in the caption. Source line: "Malaria deaths: WHO World Malaria Report 2025."
