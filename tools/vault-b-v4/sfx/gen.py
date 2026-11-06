import json, os, sys, urllib.request, concurrent.futures as cf
S = {
 "w1_whoosh": ("Fast cinematic whoosh transition, sharp and close, no music", 1.2),
 "w2_stinger": ("Sharp horror stinger hit with metallic screech and a short scream-like string, very loud and sudden", 1.5),
 "w3_big_hiss": ("Huge aggressive cobra hiss, loud and close, threatening, deep and breathy, giant snake", 2.5),
 "w4_strike": ("Giant snake lunging strike at the camera: fast whoosh, loud hiss and a heavy bite snap with a deep impact", 1.8),
 "w5_drip": ("Thick liquid dripping slowly onto a stone floor in a quiet echoing vault", 3),
 "w6_temple": ("Indian temple bell ringing with distant conch shell blow, sacred, reverent reveal", 5),
 "w7_riser": ("Dark cinematic tension riser, building fast, ends abruptly", 4),
 "w8_slither": ("Snakes slithering over a pile of gold coins, coins shifting and clinking, close", 5),
}
def go(k):
    t, d = S[k]
    body = json.dumps({"text": t, "duration_seconds": d, "prompt_influence": 0.55}).encode()
    r = urllib.request.Request("https://api.elevenlabs.io/v1/sound-generation?output_format=mp3_44100_192", data=body,
        headers={"xi-api-key": os.environ["ELEVENLABS_API_KEY"], "Content-Type": "application/json"})
    open(os.path.join(os.path.dirname(os.path.abspath(__file__)), k + ".mp3"), "wb").write(urllib.request.urlopen(r, timeout=300).read()); return k
with cf.ThreadPoolExecutor(4) as ex:
    for k in ex.map(go, S): print("ok", k)
