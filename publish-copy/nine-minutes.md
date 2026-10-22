# Nine Minutes (CAR-T vs cancer)

| | |
|---|---|
| Status | v1 final (with the "cancer cell" hook); v2 paused as untested WIP |
| Upload file | `final-reels/nine-minutes.mp4` |
| Length | 22 s |
| Voice | None (wordless; the voiceover was dropped) |
| Copy taken from | `nine-minutes-reel.md` on branch `claude/project-thread-mbrzok` |

## Version notes

- On-screen hook from frame 0: "WATCH THIS CANCER CELL / DIE IN 9 MINUTES." with the chip "CANCER CELL (LEUKEMIA, A BLOOD CANCER)".

## Publish copy

**YouTube title:** What a CAR-T cell does to cancer in 9 minutes

**Alt titles:** "A living drug vs a leukemia cell" / "Watch a cancer cell self-destruct"

**Description:**
> A CAR-T cell is a patient's own T cell, given a new receptor in a lab so it can recognise a marker on cancer cells (here, CD19 on a leukemia cell). In a lab-dish study, one CAR-T cell locked on to its target within about 3 minutes, and the cancer cell began apoptotic blebbing (self-destructing) about 9 minutes after first contact.
>
> This is a 3D illustration, not microscopy footage. Shapes and colours are artistic and not to scale; timings are from one cell pair in a lab dish.
>
> Source: Lee M. et al., "Deep-learning-based three-dimensional label-free tracking and analysis of immunological synapses of CAR-T cells", eLife 2020;9:e49023. https://elifesciences.org/articles/49023
>
> Sound: original, synthesised for this video.
>
> #CART #Cancer #Immunotherapy #Leukemia #Biology #Science #Shorts

**Instagram / Facebook caption:**
> Nine minutes. That's how long it took one CAR-T cell to make a leukemia cell self-destruct in a lab dish. 🧬
> A CAR-T cell is your own T cell, rebuilt to hunt one marker (CD19).
> 3D illustration, not to scale. Timings: Lee et al., eLife 2020. Original sound.
> #CART #Immunotherapy #Cancer #Science

**Pinned comment idea:** "The 9 minutes is from one cell pair in a lab dish (eLife 2020). Real treatment involves millions of these cells, and each kill can look different."

Upload checklist: AI/synthetic content label ON (it is a rendered illustration); not medical advice; no claims about cure rates.

## Facts and sources

Primary source (the study the reference video comes from):
Lee M, Lee Y-H, Song J, Kim G, Jo YJ, Min HS, Kim CH, Park YK. "Deep-learning-based three-dimensional label-free tracking and analysis of immunological synapses of CAR-T cells." *eLife* 2020;9:e49023. https://elifesciences.org/articles/49023

| Claim on screen | What the paper says | Status |
|---|---|---|
| Dies in about 9 minutes | CAR-T cells "induced apoptotic blebbing on the target cells about 9 min after the initial contact" (Results) | Verified |
| Synapse "stable within ~3 min" | Synapse area reached half maximum within 40 s and "reached a steady-state within only 3 min" (K562-CD19, Fig. 8b) | Verified |
| CD19 is the marker | CART19: anti-CD19 scFv (FMC63), CD8a hinge/TM, 4-1BB, CD3ζ; targets were K562 cells transduced with human CD19; CD19-negative K562 did not form a stable synapse | Verified |
| "Leukemia cell" | K562 is a human chronic myelogenous leukemia cell line | Verified (cell line identity) |
| Toxic granules delivered at the synapse | The paper tracks lytic granules "coalescing into the IS" | Verified (wording kept general: no perforin/granzyme claim on screen) |
| "The patient's own T cell, given a new receptor in a lab" | Standard description of autologous CAR-T therapy; the study used T cells engineered with a lentiviral CAR construct | General knowledge; phrased generically |
| Apoptosis / self-destructs | Apoptotic blebbing is a hallmark of apoptosis (programmed cell death) | Verified |

Accuracy guardrails used:
- The 9 minutes is one observation in a lab dish (one effector-target pair, label-free holotomography). The end card says so. Do not claim every CAR-T kill takes 9 minutes, or that this happens in a patient on this clock.
- The video is an illustration: shapes, colours, receptor counts and granule counts are artistic. Tagged "ILLUSTRATION · NOT TO SCALE · TIME-LAPSE".
- No treatment claims, cure claims or survival statistics.
