# Vault B v3 "The Door" (no Blender)

Plan: /mnt/project-files/final-reels/vault-b-v3-directors-cut.md

1. `vo/tts.py STABILITY OUT.mp3` – ElevenLabs Eleven v3, BlackvieW voice (library voice works by id; the key cannot add voices). Two takes in vo/.
2. `vo/cut.py` – chief-editor VO cut from the scribe word timestamps (stt_*.json), re-spaced pauses, 1.12x rubberband → vo_cut.wav + vo_timeline.json (~51 s).
3. `sfx/gen.py` – 8 ElevenLabs sound effects. `audio/mix.py` – sound design on the VO timeline, ducking, limiter, -15 LUFS.
4. `work/fetch.py` – Wikimedia Commons downloader (slow: shared IP gets 429; thumbs only via upload.wikimedia.org). Credits in footage/*/credits.json and CREDITS.md.
5. CG shots: `cg_workerA.sh` / `cg_workerB.sh` drive `tools/vault-b/render_anim.cjs` (Three.js, swiftshader, ~5-9 s/frame) → cg/<shot>/f####.jpg.
6. `edit.py` – EDL, grade (warm → cold from Vault B), coin rain, motes, flashes, punches, Cinzel text. `render_all.sh` renders in 4 chunks and muxes.
