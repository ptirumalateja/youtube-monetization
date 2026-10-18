# Handoff: where the work stands (18 Oct 2026)

A new Claude session starts with no memory of the chat. Read this file, then `claude.md` (standing rules), `slow-light-design-playbook.md`, `mosquito-reel-spec.md` and `mosquito-flow-prompts.md`.

## Current project: "What if every mosquito vanished?" Reel (31 s, wordless, loops)
- **Spec and decisions:** `mosquito-reel-spec.md` (approved; fact table with sources; revision log) and `mosquito-flow-prompts.md` (authoritative shot list, Flow clip prompts A-I, review of supplied clips). Owner decisions: opening = macro mosquito, pull back to the swarm, vanish; middle = ChatGPT storyboard rhythm with balanced, sourced facts; no time ladder; red only as chips.
- **Opening (beats 01-02, 0-2.4 s) is built in code**, animated style: `tools/mosquito/opening.html` (three.js r0.170), `shot.js` (stills), `render.js` (frames). Run: `cd tools/mosquito; npm i three@0.170.0 playwright-core@1.56.1 (into a scratch dir, symlink node_modules); python3 -m http.server 8766; node shot.js <playwright-core dir> 540 960 <out> 0.2 0.9 ...; node render.js <dir> 1080 1920 <out> <f0> <f1>` then ffmpeg (30 fps, light `noise`). Latest render: v3 (clearer anatomy). Videos are not in git; re-render takes about 3 min with 4 parallel workers.
- **Still to build, same animated style** (owner has not yet confirmed animated vs photoreal for the whole Reel): Earth + pulse, Arctic tundra herd, malaria data globe (data in `tools/mosquito/land.json`, made by `gen_land.js` from Natural Earth 110m; sub-Saharan markers from WHO), bog orchid, cacao, Year 10 tundra, Earth sunrise + closing question, loop back to the macro mosquito. Then overlay (hook text, chips, stat panel), sound (synthesised whine; hits only at frame 0, the vanish, and the malaria number), composite, loop check, publish copy, audio credits.
- **Owner-supplied clips** are in Google Drive folder `1MWLOBcSAru1nLvCojDsi7fS151a1Iia4` (and subfolder `v2`): Flow clips have baked text and a Gemini sparkle (remove with `delogo=x=852:y=1692:w=96:h=96`); clean windows are listed in `mosquito-flow-prompts.md`. Download with `curl -L "https://drive.usercontent.google.com/download?id=<id>&export=download&confirm=t"`.

## Other projects (see the branches)
- India collision series: branch `origin/feature/relaxed-johnson-43xliu` (`shorts/india-collision-series.md`, `rules/production-rules.md`, `tools/globe/`). Ep 1 is ON HOLD with a written verdict and resume plan.
- Black hole ladder, Time Flies, Tesla, Dreams, tickle, aircraft heat: other `origin/feature/*` branches.

## Compute providers
- RunPod: key in `RUNPOD_API_KEY`; setup recipe in `claude.md` on the India branch (section 8-9). Network volume costs about $14/month, which can exceed GPU cost at low usage.
- Vultr: the owner added `VULTR_API_KEY` to the environment (a new session picks it up; never print it). Findings: A40 48 GB plan `vcg-a40-24c-120g-48vram` about $1.71/hr (lax, lhr, fra, sgp), about 3x RunPod; stopped instances still bill until destroyed; Marketplace app "ComfyUI on Ubuntu 24.04" (id 1243); this sandbox cannot SSH (port 22 blocked), HTTPS 443 works, so use a boot-script-and-upload pattern. First task there: `GET /v2/account` and check whether the $250 trial credit is applied, what it covers (GPU?) and when it expires. Do not deploy anything without asking.
- Cheaper alternatives noted: Vast.ai, TensorDock, Hostinger GPUs (prices unverified, check consoles); cheap object storage instead of a paid volume.

## Standing rules to remember
Higgsfield only for ElevenLabs audio; ask before spending anything. No Gemini/Flow text baked into clips. Never let AI draw maps. Wordless Reels use CC0 or credited CC BY audio. Do not redo frozen plans (the owner changes them deliberately).
