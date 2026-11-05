import json, os, urllib.request, concurrent.futures as cf
S = {
 "01_hiss": ("Close-up hiss of an Indian cobra, slow and threatening, dry, no reverb", 3),
 "02_scales_coins": ("Snake scales sliding over a pile of metal coins, close microphone", 4),
 "03_iron_door": ("Ancient heavy iron vault door groaning open slowly in a stone corridor", 4),
 "04_bell": ("Single deep temple bell strike in a large stone hall, long decay", 6),
 "05_heartbeat": ("Slow human heartbeat, close and muffled", 6),
 "06_choir_drone": ("Low ominous male choir drone with distant chanting, dark and sacred", 10),
 "07_breath": ("Very close whispered breath in the left ear, eerie", 2),
 "08_boom": ("Massive cinematic boom hit with metallic shing and long dark tail", 4),
}
def go(k):
    t, d = S[k]
    body = json.dumps({"text": t, "duration_seconds": d, "prompt_influence": 0.5}).encode()
    r = urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_192", data=body,
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
    open(os.path.join(os.path.dirname(__file__), k + ".mp3"), "wb").write(urllib.request.urlopen(r, timeout=300).read())
    return k
with cf.ThreadPoolExecutor(4) as ex:
    for k in ex.map(go, S): print("ok", k)
