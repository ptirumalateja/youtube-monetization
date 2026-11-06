"""python3 tighten.py TAG  -> TAG_tight.wav + TAG_tight_timeline.json: pauses capped (longer caps before dramatic beats), key times remapped"""
import json, sys, subprocess, numpy as np, soundfile as sf
tag = sys.argv[1]; SR = 48000
a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", f"{tag}.mp3", "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32).reshape(-1, 2)
keys = json.load(open(f"{tag}_timeline.json"))["keys"]
hop = int(0.01 * SR); e = np.sqrt((a.mean(1)[:len(a) // hop * hop].reshape(-1, hop) ** 2).mean(1)); sil = 20 * np.log10(e + 1e-9) < -40
CAP, DRAMA = 0.28, {"then": 0.75, "vaultb": 0.45, "weeks": 0.55, "was": 0.5, "would": 0.6, "still": 0.55}
runs = []; i = 0
while i < len(sil):
    if sil[i]:
        j = i
        while j < len(sil) and sil[j]: j += 1
        runs.append((i * 0.01, j * 0.01)); i = j
    else: i += 1
segs = []; t_out = 0.0; last = 0.0; mapping = []
def cap_for(t_end):
    for k, c in DRAMA.items():
        if abs(keys.get(k, -9) - t_end) < 0.35: return c
    return CAP
for s0, s1 in runs:
    if s0 < 0.05 or s1 - s0 <= CAP: continue
    c = cap_for(s1); keep = min(s1 - s0, c)
    cut0, cut1 = s0 + keep * 0.5, s1 - keep * 0.5
    segs.append((last, cut0)); mapping.append((last, t_out)); t_out += cut0 - last; last = cut1
segs.append((last, len(a) / SR)); mapping.append((last, t_out))
f = int(0.008 * SR); out = []
for s0, s1 in segs:
    c = a[int(s0 * SR):int(s1 * SR)].copy(); c[:f] *= np.linspace(0, 1, f)[:, None]; c[-f:] *= np.linspace(1, 0, f)[:, None]; out.append(c)
out = np.concatenate(out); sf.write(f"{tag}_tight.wav", out, SR)
def remap(t):
    src, dst = mapping[0]
    for s, d in mapping:
        if s <= t: src, dst = s, d
    return dst + max(0, t - src)
nk = {k: round(remap(v), 3) for k, v in keys.items()}; nk["end"] = round(len(out) / SR - 0.05, 3)
json.dump(dict(keys=nk), open(f"{tag}_tight_timeline.json", "w"), indent=1)
print(tag, "dur", round(len(a) / SR, 1), "->", round(len(out) / SR, 1))
