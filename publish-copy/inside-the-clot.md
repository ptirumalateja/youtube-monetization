# Inside the Clot (heart attack)

| | |
|---|---|
| Status | v3 in final-reels; v4 encoded but not published (paused) |
| Upload file | `final-reels/inside-the-clot.mp4` (v3) |
| Length | 24.9 s |
| Voice | AI voice (stand-in Kokoro TTS in v3; Teja's ElevenLabs take in the unpublished v4) |
| Copy taken from | `final-reels/inside-the-clot.md` |

## Version notes

- The copy below was written for the wordless v2. v3 adds a crowd opening and a voiceover from frame 0, so turn the AI/synthetic label on for the voice as well as the visuals.
- v4 (paused by Teja) switches the hook to a worldwide WHO figure. If v4 is published, the "Every 40 seconds, someone in the US" lines here must change to match.
- v3 voiceover script: "Every forty seconds, someone in the US has a heart attack. It starts inside an artery, decades earlier. Fatty plaque builds in the wall. Then its cap cracks. A clot seals the crack... and the artery. Within twenty to forty minutes, the heart muscle starts to die. The plaque didn't block it. The clot did. Time is muscle. Call emergency services."

## Publish copy

### YouTube Shorts
**Title (pick one):**
1. A heart attack starts with a crack.
2. The plaque didn't block the artery. The clot did.
3. What actually happens inside a heart attack

Recommended: option 1 (matches the hook).

**Description:**
> Every 40 seconds, someone in the US has a heart attack (CDC). This is what happens inside the artery.
>
> Plaque (fat and cholesterol) builds inside the artery wall for decades, often without narrowing it enough to cause symptoms.
> Then its cap cracks. The body treats the crack like a wound: platelets and fibrin build a clot on it, and within minutes the clot can close the artery completely.
> The heart muscle downstream gets no blood. After roughly 20-40 minutes it starts to die, and the damage keeps spreading for hours.
>
> That's why doctors say "time is muscle." Chest pain, pressure, or discomfort that spreads to the arm, jaw or back, shortness of breath, a cold sweat or nausea: call emergency services (911 in the US) right away. Don't drive yourself.
>
> Illustration: not to scale, time compressed. Educational, not medical advice. Visuals are 3D-rendered; all sound is synthesized.
> Sources: CDC Heart Disease Facts; American Heart Association; Falk, Shah & Fuster, Circulation 1995; Reimer & Jennings, Circulation 1977.
>
> Slow Light: stories worth slowing down for.
> #heart #health #science

**Hashtags (first 3 show above the title):** #heart #health #science

**Tags (under 500 characters):**
heart attack, what happens during a heart attack, how a heart attack happens, plaque rupture, blood clot heart, coronary artery, atherosclerosis, myocardial infarction, time is muscle, heart attack symptoms, heart health, cardiology, human body, medical animation, science shorts, health shorts, slow light

**Pinned comment:** Most people think the plaque slowly clogs the artery shut. Usually it's the clot that does it, in minutes. Did you know that? 🫀

### Instagram / Facebook
> A heart attack starts with a crack. 🫀
> Plaque builds in the artery wall for decades. When its cap cracks, a clot seals it, and the artery with it. The muscle downstream starts dying within about 20-40 minutes.
> Time is muscle: chest pain or pressure? Call emergency services right away.
> Illustration, not to scale. Educational, not medical advice. Sources: CDC, American Heart Association.
> #heart #hearthealth #science #humanbody #health #slowlight

### Upload checklist
- Turn on the platform's "altered or synthetic content" label (3D-rendered medical illustration).
- No sound credits needed (all audio synthesized in `mix.py`).
- YouTube may add a health information panel; keep the description sources as written.

## Facts and sources

| On screen / in copy | Fact | Source |
|---|---|---|
| Copy: "Every 40 seconds, someone in the US has a heart attack" | "In the United States, someone has a heart attack every 40 seconds." About 805,000 per year (605,000 first, 200,000 repeat). | CDC, Heart Disease Facts: https://www.cdc.gov/heart-disease/data-research/facts-stats/ (checked 21 Oct 2026) |
| PLAQUE BUILDS FOR DECADES / FAT + CHOLESTEROL INSIDE THE WALL | Atherosclerotic plaque (lipid-rich core under a fibrous cap, inside the artery wall) develops silently over decades, starting as early as young adulthood. | AHA, "Atherosclerosis" patient pages; standard pathology. The AGE 25->55 counter is illustrative, not a statistic. |
| THE CAP CRACKS / THE BODY TREATS IT AS A WOUND / A CLOT SEALS IT | Most heart attacks (type 1 MI) happen when a plaque's fibrous cap ruptures (or its surface erodes); the exposed core triggers platelets and the clotting cascade (fibrin), and the thrombus blocks the artery. | Falk E, Shah PK, Fuster V. "Coronary plaque disruption." Circulation 1995;92:657-671. Fourth Universal Definition of MI (Thygesen et al., Circulation 2018) for "type 1 MI". |
| THE PLAQUE DIDN'T BLOCK IT. THE CLOT DID. | The plaques that rupture are often not severely narrowing beforehand: in pooled angiography studies most culprit lesions had been under 50-70 % stenosis; the sudden occlusion is the thrombus. The reel shows the plaque at about 45 % narrowing and the clot closing the rest. | Falk, Shah, Fuster 1995 (pooled data from Ambrose 1988, Little 1988 and others). Copy says "often", never "always". |
| MUSCLE STARTS TO DIE / FROM ~20-40 MIN, THEN IT SPREADS | Irreversible injury of heart muscle begins after roughly 20-40 minutes of complete blockage and spreads as a wavefront from the inner wall outward and along the territory over the next hours. | Reimer KA, Jennings RB et al. "The wavefront phenomenon of ischemic cell death." Circulation 1977;56:786-794 (and the 1979 follow-up, Lab Invest). The reel simplifies the inner-to-outer wavefront to a spread along the front wall. |
| TIME IS MUSCLE. / CALL EMERGENCY SERVICES. | Call 911 (or local emergency number) at the first signs; don't drive yourself. Guidelines measure first-medical-contact-to-device time, target 90 minutes or less for primary PCI. | AHA, 2013 ACCF/AHA STEMI guideline "Top things to know": https://professional.heart.org/en/science-news/2013-guideline-for-the-management-of-st-elevation-myocardial-infarction/top-things-to-know ; O'Gara PT et al., Circulation 2013;127:e362-e425. |

Verification notes: the CDC and AHA pages were read on 21 Oct 2026. The journal papers (Falk 1995, Reimer 1977, O'Gara 2013) are cited from the published record; their PubMed/PMC pages were behind a browser check from the build machine, so the page numbers above should be spot-checked before quoting them anywhere outside this file. The on-screen wording is deliberately conservative ("~20-40 MIN", "STARTS TO DIE", no claim about how often).

Rules for any recut: never say a blocked artery "always" comes from a crack (erosion exists, and type 2 MI has other causes); never give medical advice beyond "call emergency services"; keep "illustration, not to scale, time compressed"; this is education, not diagnosis.
