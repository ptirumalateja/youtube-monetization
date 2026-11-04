# Toolkit setup

Cloud sessions start fresh, so run `bash tools/setup/install.sh` at the start of a session that needs these tools (about 2 minutes; the first earshot install pulls torch from PyPI, about 5 more).

Last cloud retest: 4 Nov 2026, after `*.youtube.com`, `*.googlevideo.com` and `*.hf.co` were allowed.

| asked for | installed | what works in the cloud |
|---|---|---|
| hyperframes | heygen-com/hyperframes (npm `hyperframes`) | renders fine; jsdelivr is allowed, so `hf-gsap.sh` is only needed if it gets blocked again |
| yt-alb | yt-dlp (`yt-dlp[default]`, includes the JS challenge solver) | **fails**: the proxy now lets youtube.com and googlevideo.com through, but YouTube itself blocks the cloud IP. Default/mweb/android_vr clients get `HTTP Error 403: Forbidden` on the video stream; tv/ios/web_safari get `Sign in to confirm you're not a bot`. Use the Mac, or pass `--cookies` from a signed-in browser |
| wishper | Whisper via faster-whisper, base.en model from a GitHub mirror | `transcribe.py audio.mp3 --json words.json` gives word timings; HuggingFace downloads now work too (tested `Systran/faster-whisper-tiny.en`, 75 MB) |
| openverse | WordPress/openverse API, `openverse.py` (stdlib) | search works (200 with the script's own User-Agent). `--get` mostly fails: audio files live on cdn.freesound.org (`403 Forbidden`), images on live.staticflickr.com (not allowed by the proxy). The script now skips a failed file instead of crashing |
| realsfx | vibe-motion/sound (Freesound search/download skill) | **fails**: freesound.org and cdn.freesound.org answer an empty `403 Forbidden` to every request (curl too, with or without a User-Agent); www.freesound.org is not allowed by the proxy. Works on the Mac |
| earshot | Leonxlnx/earshot (agent ears: describe, match, SFX bank, kits) | everything works: `describe` and `match` fetch their CLAP models from HuggingFace on first use (~30 s on CPU); offline commands (`measure`, `sfx`, `kit`, `forge`) too |

Other notes
- download.pytorch.org is blocked, so the script falls back to the PyPI torch wheel (bigger, includes CUDA libs, works).
- YouTube from the cloud needs `--js-runtimes node` (node is installed; deno is not).
- Don't spoof a browser User-Agent to get past a 403; it is a block, not a header problem.
