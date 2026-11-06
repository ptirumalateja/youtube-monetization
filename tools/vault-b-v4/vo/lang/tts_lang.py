"""python3 tts_lang.py LANG MODEL [VOICE]  -> LANG.mp3 + LANG_timeline.json (key -> start s, from ElevenLabs character alignment)"""
import json, os, sys, base64, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from scripts import SCRIPTS
lang, model = sys.argv[1], sys.argv[2]; voice = sys.argv[3] if len(sys.argv) > 3 else "tSVwqkJGEKjLklhiN0Nx"  # Viraj
segs = SCRIPTS[lang]; text = "".join(t for _, t in segs)
vs = {"stability": 0.5, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True} if model == "eleven_v3" else \
     {"stability": 0.42, "similarity_boost": 0.8, "style": 0.35, "use_speaker_boost": True, "speed": 1.04}
if model == "eleven_v3": vs = {"stability": 0.5, "similarity_boost": 0.8}
body = json.dumps({"text": text, "model_id": model, "voice_settings": vs, "language_code": lang}).encode()
req = urllib.request.Request(f"https://api.elevenlabs.io/v1/text-to-speech/{voice}/with-timestamps?output_format=mp3_44100_192",
    data=body, headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
r = json.loads(urllib.request.urlopen(req, timeout=300).read())
d = os.path.dirname(os.path.abspath(__file__)); tag = f"{lang}_{model.split('_')[-1]}"
open(f"{d}/{tag}.mp3", "wb").write(base64.b64decode(r["audio_base64"]))
al = r.get("normalized_alignment") or r["alignment"]; chars, st, en = al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]
full = "".join(chars); keys = {}; pos = 0
for k, t in segs:
    i = full.find(t.strip()[:6], pos)
    if i < 0: i = pos
    while i < len(full) and full[i] in " .…": i += 1
    if k: keys[k] = st[min(i, len(st) - 1)]
    pos = i + len(t.strip())
keys["end"] = en[-1]
json.dump(dict(keys=keys, text=text), open(f"{d}/{tag}_timeline.json", "w"), ensure_ascii=False, indent=1)
print(tag, round(en[-1], 2), {k: round(v, 2) for k, v in keys.items()})
