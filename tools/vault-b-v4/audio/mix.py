"""Vault B v4 sound: BlackvieW VO (split after "door." for the strike), the Flow clips' own audio under their shots,
new ElevenLabs SFX (sfx/w*.mp3) + v3 SFX + Freesound CC0. No drone under the open. Reads output/timeline.json from edit.py."""
import json, subprocess, os, numpy as np, soundfile as sf, pyloudnorm as pyln
from scipy.ndimage import maximum_filter1d
R = os.path.dirname(os.path.abspath(__file__)) + "/.."; SR = 48000
V3 = f"{R}/../vault-b-v3/sfx"
def load(p):
    a = np.frombuffer(subprocess.run(["ffmpeg", "-v", "error", "-i", p, "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"], capture_output=True, check=True).stdout, np.float32)
    return a.reshape(-1, 2).astype(np.float64)
TL = json.load(open(f"{R}/output/timeline.json")); w = TL["words"]; DUR = TL["DUR"]
S = {k: load(f"{R}/sfx/{k}.mp3") for k in ["w1_whoosh", "w2_stinger", "w3_big_hiss", "w4_strike", "w5_drip", "w6_temple", "w7_riser", "w8_slither"]}
S.update({k: load(f"{V3}/{k}.mp3") for k in ["01_hiss", "02_scales_coins", "03_iron_door", "04_bell", "05_heartbeat", "06_choir_drone", "07_breath", "08_boom"]})
S["coins"] = load(f"{R}/../vault-b/audio/src/coins-pour-363089.wav"); S["impact"] = load(f"{R}/../vault-b/audio/src/bass-impact-512389.mp3")
FL = {n: load(f"{R}/flow/{n}.mp4") for n in ["blood", "corridor", "carvings", "strike", "strike_floor", "coins", "temple"]}
mix = np.zeros((int(DUR * SR), 2)); bed = np.zeros_like(mix)
def db(x): return 10 ** (x / 20)
def put(buf, clip, t, gain=0, a=0, b=None, fade_in=0.005, fade_out=0.05, pan=0.0):
    c = clip[int(a * SR): int(b * SR) if b else None].copy()
    if len(c) < 4: return
    fi, fo = max(1, min(len(c) // 2, int(fade_in * SR))), max(1, min(len(c) // 2, int(fade_out * SR)))
    c[:fi] *= np.linspace(0, 1, fi)[:, None]; c[-fo:] *= np.linspace(1, 0, fo)[:, None]
    c *= db(gain); c[:, 0] *= min(1, 1 - pan); c[:, 1] *= min(1, 1 + pan)
    s = int(t * SR); e = min(len(buf), s + len(c))
    if 0 <= s < len(buf): buf[s:e] += c[:e - s]

# --- VO: split after "door." and push the rest back by GAP
vo = load(f"{R}/vo/{TL.get('VOICE', 'viraj')}_v2.mp3"); cut = int(TL["CUT"] * SR); f = int(0.03 * SR)
A = vo[:cut].copy(); A[-f:] *= np.linspace(1, 0, f)[:, None]; B = vo[cut:].copy(); B[:f] *= np.linspace(0, 1, f)[:, None]
v = np.zeros_like(mix); v[:len(A)] += A; s0 = int((TL["CUT"] + TL["GAP"]) * SR); v[s0:s0 + len(B)] += B[:len(v) - s0]

# --- Flow clips' own audio under their shots (Teja: it's solid)
for seg in TL["flow"]:
    t0, t1, n = seg["t0"], seg["t1"], seg["clip"]
    if n == "strike_floor":   # align the clip's hiss/lunge with the sped-up picture: src 8.0 lands when the picture reaches 8.0
        t8 = TL["LUNGE_T"] + (8.0 - 7.45) / 1.1; put(mix, FL[n], t0, 0, a=8.0 - (t8 - t0), b=9.9, fade_in=0.02, fade_out=0.1)
    elif seg["flash"]:
        put(mix, FL[n], t0, -3, a=seg["src"], b=seg["src"] + (t1 - t0) + 0.04, fade_in=0.004, fade_out=0.03)
    else:
        put(bed, FL[n], t0 - 0.05, -2, a=max(0, seg["src"] - 0.05), b=seg["src"] + (t1 - t0) * seg["speed"] + 0.1, fade_in=0.06, fade_out=0.12)

# --- 1 hook: stinger, a whoosh/tick on every flash, rising, then the giant cobra on "door"
put(mix, S["w2_stinger"], 0.0, -4, fade_out=0.4)
cuts = TL["HOOK_CUTS"]
for i, c in enumerate(cuts[1:-1]):
    put(mix, S["w1_whoosh"], c - 0.08, -16 + i * 0.9, b=0.5, fade_out=0.15, pan=(-0.4 if i % 2 else 0.4))
    put(mix, S["impact"], c, -24 + i, b=0.4, fade_out=0.2)
put(mix, S["w5_drip"], cuts[5], -10, b=0.6, fade_out=0.2)
put(mix, S["01_hiss"], 0.2, -18, b=2.0, fade_in=0.3, fade_out=0.2)
SA, SE = TL["STRIKE_AT"], TL["STRIKE_END"]
put(mix, S["w3_big_hiss"], SA - 0.05, -3, fade_out=0.4)
t_land = TL["LUNGE_T"] + (8.3 - 7.45) / 1.1
put(mix, S["w4_strike"], t_land - 0.35, -1, fade_out=0.3)
put(mix, S["08_boom"], t_land, -2, fade_out=1.0)
put(mix, S["impact"], t_land, -3, fade_out=0.8)
for buf in (mix, bed):  # hard cut to silence after the strike
    a, b = int(SE * SR), int((w["beneath"] - 0.1) * SR); buf[a:b] *= np.r_[np.linspace(1, 0, int(0.04 * SR)), np.zeros(b - a - int(0.04 * SR))][:, None]
# --- 2 temple name: bell + conch
put(mix, S["w6_temple"], w["beneath"] - 0.15, -6, fade_out=1.2)
# --- 3 five vaults open: iron groan, gentle choir from here only
put(mix, S["03_iron_door"], w["six"] - 0.05, -8, fade_out=0.8)
put(bed, S["06_choir_drone"], w["in2011"] - 0.3, -20, b=8.0, fade_in=1.5, fade_out=1.5)
# --- 4 treasure: coin shimmer + impact per item, slither under the cobra shots
for i, k in enumerate(["gold", "eighteen", "sacks", "crowns", "diamonds"]):
    put(mix, S["coins"], w[k] - 0.05, -17 + i * 1.2, a=6.0 + i * 0.4, b=6.9 + i * 0.4, fade_out=0.4)
    put(mix, S["impact"], w[k] - 0.03, -19 + i * 1.2, b=1.0, fade_out=0.5)
put(mix, S["w8_slither"], w["eighteen"] - 0.1, -14, b=4.6, fade_in=0.2, fade_out=0.4, pan=0.3)
put(mix, S["coins"], w["lakh"] - 0.35, -10, a=5.6, b=8.2, fade_in=0.2, fade_out=0.6)
put(mix, S["impact"], w["lakh"] - 0.05, -7, fade_out=1.4)
put(mix, S["w3_big_hiss"], w["rupees"] + 0.1, -14, fade_out=0.4)
# --- 5 THEN: riser into silence, one heartbeat, boom on "Vault B"
gap0 = w["then"] - 0.45
put(mix, S["w7_riser"], gap0 - 2.6, -16, b=2.6, fade_in=1.0, fade_out=0.05)
for buf in (mix, bed):
    a = int(gap0 * SR); buf[a - int(0.05 * SR):a] *= np.linspace(1, 0, int(0.05 * SR))[:, None]; buf[a:int(w["then"] * SR)] = 0
beat = S["05_heartbeat"][:int(0.75 * SR)]
put(mix, beat, w["then"] - 0.25, -4)
put(mix, S["08_boom"], w["vaultb"] - 0.03, -5, fade_out=1.8)
for k in ["handle", "lock", "keyhole"]:
    put(mix, S["03_iron_door"], w[k] - 0.05, -14, a=0.55, b=1.4, fade_out=0.3)
    put(mix, S["impact"], w[k] - 0.02, -14, b=0.8, fade_out=0.4)
put(mix, S["07_breath"], w["keyhole_end"] + 0.05, -8, pan=-0.85, fade_out=0.3)
# --- 6 cobras / Naga Bandham: hiss, choir low
put(mix, S["w3_big_hiss"], w["cobras"] + 0.9, -12, fade_out=0.6)
put(mix, S["w2_stinger"], w["naga"] - 0.1, -9, fade_out=0.6)
put(bed, S["06_choir_drone"], w["legend"] - 0.3, -16, a=2.0, b=8.4, fade_in=0.8, fade_out=0.6)
# --- 7 weeks later: heartbeat speeding up, stops dead on "dead", the drip
t = w["weeks"] - 0.2; iv = 1.0
while t < w["was"] - 0.1:
    put(mix, beat, t, -6); t += iv; iv = max(0.42, iv * 0.86)
put(mix, S["08_boom"], w["dead"] - 0.05, -5, fade_out=1.5)
put(mix, S["w5_drip"], w["dead"] + 0.3, -8, fade_out=0.5)
# --- 8 still shut / would you open it: rumble, then the last strike and a big boom
rumble = S["06_choir_drone"][int(4 * SR):int(8 * SR)].copy(); rumble *= np.linspace(0.2, 1, len(rumble))[:, None]
put(bed, rumble, w["still"] - 0.3, -12, fade_in=0.6, fade_out=0.1)
put(mix, S["01_hiss"], w["would"] + 0.2, -10, b=1.4, fade_out=0.3)
t_end = w["end"] + 0.55
put(mix, S["w4_strike"], t_end - 0.25, 0, fade_out=0.3)
put(mix, S["08_boom"], t_end + 0.02, 0, fade_out=1.8)
put(mix, S["impact"], t_end + 0.02, -3, fade_out=1.6)

# --- VO on top, duck everything else under speech
env = np.convolve(np.abs(v[:, 0]), np.ones(int(0.12 * SR)) / int(0.12 * SR), "same"); duck = 1 - 0.5 * np.clip(env / 0.05, 0, 1)
out = mix * (1 - 0.35 * (1 - duck))[:, None] + bed * duck[:, None] + v * db(2.0)
meter = pyln.Meter(SR)
def limit(x, ceil=0.89, rel=0.12):
    pk = np.abs(x).max(1); la = int(0.005 * SR); need = np.r_[np.maximum(1, pk / ceil)[la:], np.ones(la)]
    need = maximum_filter1d(need, la * 2 + 1); g = np.empty_like(need); a = np.exp(-1 / (rel * SR)); cur = 1.0
    for i in range(len(need)):
        cur = need[i] if need[i] > cur else need[i] + (cur - need[i]) * a; g[i] = cur
    return x / g[:, None]
for _ in range(3):
    L = meter.integrated_loudness(out); out *= db(-15.0 - L); out = limit(out)
sf.write(f"{R}/audio/vault-b-v4-mix.wav", out.astype(np.float32), SR, subtype="PCM_24")
print("dur", round(DUR, 2), "LUFS", round(meter.integrated_loudness(out), 1), "peak", round(np.abs(out).max(), 3))
