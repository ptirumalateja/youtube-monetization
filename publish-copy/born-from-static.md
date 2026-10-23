# Born From Static (how AI art is made)

| | |
|---|---|
| Status | Final (v1), delivered 23 Oct 2026, awaiting Teja's review. Made for the "AI Art" topic that Facebook's creator assistant flagged as popular with Teja's followers. |
| Upload file | `final-reels/born-from-static_master.mp4` for YouTube (share: `born-from-static.mp4`, with sound design) or `final-reels/born-from-static_music-ready.mp4` (silent, add platform music; drop on 9.0 s) |
| Length | 15 s, loops |
| Voice | None (wordless, on-screen text only) |
| Copy taken from | `final-reels/born-from-static.md` (project files); source in `tools/born-from-static/` |

## Publish copy

**YouTube title:** AI art starts as pure static 📺 Watch a picture appear in 50 steps #AIArt
**Alt title (A/B):** AI doesn't draw. It deletes noise.

**YouTube description:**
> Most AI image generators (Stable Diffusion, Flux, DALL·E, Imagen) never "draw" anything. They start from random static and remove a little noise at each step, until only a picture is left. The prompt decides what the model "sees" in the noise.
> How did they learn that? By training on billions of images that were buried in noise step by step, and learning to undo it.
>
> The painting in this video was made with code for this explainer, and the noise is drawn in pixels so you can see it. Real models such as Stable Diffusion do the same thing in a compressed "latent" space and usually take 20 to 50 steps.
> Sound design: original, made for this video.
>
> #AIArt #AI #StableDiffusion #Midjourney #DigitalArt #Shorts #SlowLight

**Tags:** AI art, how AI art works, diffusion model, Stable Diffusion, Midjourney, DALL-E, AI image generator, generative AI, text to image, AI explained, digital art, machine learning

**Instagram / Facebook caption:**
> AI doesn't paint. It starts with pure static and deletes noise, 50 times, until a picture is left. 📺➡️🪐
> It learned this by burying billions of images in noise and practising how to get them back.
> Follow @slowlight for stories worth slowing down for.
> #aiart #ai #stablediffusion #midjourney #digitalart #generativeai #reels

**Facebook tags (Tags field, no #):** AI art, AI, artificial intelligence, AI image generator, diffusion model, Stable Diffusion, Midjourney, DALL-E, generative AI, text to image, digital art, AI explained, machine learning, tech, science, art, Slow Light

**Pinned comment:** At which step did you first see the planet? 👀 (I saw it around step 20.)

**Upload checklist:** use `born-from-static.mp4` (or the music-ready file with an airy, building track whose drop hits 9.0 s). Turn the AI/synthetic label on (computer-generated visuals). Cover frame: the clean painting with "UNTIL ONLY A PICTURE IS LEFT." (about 9.5 s), or the half-noisy planet at about 5.5 s.

## Facts and sources

| On screen | Status | Source |
|---|---|---|
| "AI ART STARTS AS PURE STATIC." | Verified for diffusion and flow models, which power most popular generators | Diffusion models generate by starting from Gaussian noise and denoising step by step (Ho, Jain, Abbeel, "Denoising Diffusion Probabilistic Models", 2020, https://arxiv.org/abs/2006.11239). Stable Diffusion is a latent diffusion model (Rombach et al., 2022, https://arxiv.org/abs/2112.10752); DALL·E 2/3 and Imagen use diffusion; Flux is a rectified-flow model that also starts from noise. Not every image AI works this way (some are autoregressive), so the caption says "AI art", not "every AI". |
| "IT DOESN'T DRAW." / "IT DELETES NOISE. STEP BY STEP." | Verified (simplified) | Each sampling step predicts the noise in the current image and removes part of it (DDPM paper above). "Draw" is the everyday sense: no strokes are placed. |
| "STEP 00/50" counter, 50 steps | Illustration of a typical setting | Common samplers use about 20 to 50 steps (DDIM, Song et al. 2020, https://arxiv.org/abs/2010.02502, showed 50 steps work well; 50 was an early Stable Diffusion default). |
| Picture appears coarse first, details last | Verified (simplified) | Noise hides fine detail first, so denoising settles large shapes before fine texture. The reel exaggerates this a little with a blur on early steps so it reads on a phone. |
| "IT LEARNED THIS BY BURYING BILLIONS OF IMAGES IN NOISE." / "TRAINING: +NOISE" | Verified | Training adds noise to real images at random strengths and teaches the model to predict that noise (DDPM paper). Stable Diffusion v1 was trained on subsets of LAION-2B-en, about 2.3 billion image-text pairs (model card, https://huggingface.co/CompVis/stable-diffusion-v1-4). |
| The painting and the prompt box | Made for this video | The painting is procedural (numpy), not the output of an AI model; the prompt box shows the kind of prompt that would describe it. The noise is drawn in pixel space; real latent diffusion denoises a smaller latent and decodes it at the end. |
