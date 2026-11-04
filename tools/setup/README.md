# Toolkit setup

Cloud sessions start fresh, so run `bash tools/setup/install.sh` at the start of a session that needs these tools (about 2 minutes).

| asked for | installed | what works in the cloud |
|---|---|---|
| hyperframes | heygen-com/hyperframes (npm `hyperframes`) | renders fine; jsdelivr is allowed since 4 Nov, so `hf-gsap.sh` is only needed if it gets blocked again |
| yt-alb | yt-dlp | still blocked: allowlist has youtube.com but yt-dlp calls www.youtube.com (needs *.youtube.com, *.googlevideo.com) |
| wishper | Whisper via faster-whisper, base.en model from a GitHub mirror | `transcribe.py audio.mp3 --json words.json` gives word timings; HF downloads still fail (weights come from cas-server.xethub.hf.co / *.hf.co, not allowed) |
| openverse | WordPress/openverse API, `openverse.py` (stdlib) | API reachable (curl gets 200) but the script's Python request gets 403 from Openverse; works on the Mac |
| realsfx | vibe-motion/sound (Freesound search/download skill) | freesound.org is reachable but answers 403 Forbidden to the scraper; www.freesound.org is not allowed; works on the Mac |
| earshot | Leonxlnx/earshot (agent ears: describe, measure, SFX bank, kits) | offline commands (`measure`, `sfx`, `kit`, `forge`) work; `describe`/`match` need HF model weights from *.hf.co (blocked) |
