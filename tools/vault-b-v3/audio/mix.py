"""Vault B v3 sound design: ElevenLabs VO + ElevenLabs SFX + Freesound CC0, placed on the VO timeline."""
import json, subprocess, os, numpy as np, soundfile as sf, pyloudnorm as pyln
R = os.path.dirname(os.path.abspath(__file__)) + "/.."; SR = 48000
def load(p):
    a = np.frombuffer(subprocess.run(["ffmpeg","-v","error","-i",p,"-ac","2","-ar",str(SR),"-f","f32le","-"],capture_output=True,check=True).stdout,np.float32)
    return a.reshape(-1,2).astype(np.float64)
S = {k: load(f"{R}/sfx/{k}.mp3") for k in ["01_hiss","02_scales_coins","03_iron_door","04_bell","05_heartbeat","06_choir_drone","07_breath","08_boom"]}
S["coins"] = load(f"{R}/../vault-b/audio/src/coins-pour-363089.wav"); S["impact"] = load(f"{R}/../vault-b/audio/src/bass-impact-512389.mp3")
vo = load(f"{R}/vo/vo_cut.wav"); T = {x["key"]: x for x in json.load(open(f"{R}/vo/vo_timeline.json"))}
DUR = T["would"]["end"] + 2.6
mix = np.zeros((int(DUR*SR),2)); bed = np.zeros_like(mix)
def db(x): return 10**(x/20)
def put(buf, clip, t, gain=0, a=0, b=None, fade_in=0.005, fade_out=0.05, pan=0.0, rate=1.0):
    c = clip[int(a*SR): int(b*SR) if b else None].copy()
    if rate != 1.0:
        idx = np.arange(0, len(c)-1, rate); c = np.stack([np.interp(idx, np.arange(len(c)), c[:,i]) for i in (0,1)],1)
    fi, fo = max(1,int(fade_in*SR)), max(1,int(fade_out*SR))
    c[:fi] *= np.linspace(0,1,fi)[:,None]; c[-fo:] *= np.linspace(1,0,fo)[:,None]
    c *= db(gain); c[:,0] *= min(1,1-pan); c[:,1] *= min(1,1+pan)
    s = int(t*SR); e = min(len(buf), s+len(c)); 
    if s < len(buf): buf[s:e] += c[:e-s]
def st(k): return T[k]["start"]
def en(k): return T[k]["end"]
beat = S["05_heartbeat"][:int(0.75*SR)]

# 1 cold open: hiss + one coin + scales
put(mix, S["01_hiss"], 0.0, -4, fade_out=0.6)
put(mix, S["coins"], 1.15, -10, a=1.55, b=2.2, fade_out=0.3)
put(mix, S["02_scales_coins"], 1.6, 0, a=1.6, b=3.9, fade_in=0.2, fade_out=0.4)
# drone bed from "six" to "then"
put(bed, S["06_choir_drone"], st("six")-0.3, -12, fade_in=1.5, fade_out=1.0)
put(bed, S["06_choir_drone"], st("six")+8.8, -12, a=1.0, fade_in=1.2, fade_out=0.4)
# 2011 / opened five: the iron door groans
put(mix, S["03_iron_door"], st("five")-0.2, -9, fade_out=0.8)
# treasure list: one coin shimmer + soft impact per label, rising
for i,k in enumerate(["idols","chain","sacks","diamonds","crowns"]):
    put(mix, S["coins"], st(k)-0.05, -16+i*1.5, a=6.0+i*0.4, b=6.0+i*0.4+0.9, fade_out=0.4)
    put(mix, S["impact"], st(k)-0.03, -20+i*1.5, b=1.2, fade_out=0.6)
# lakh crore: the money pours, sub swell
put(mix, S["coins"], st("lakh")-0.4, -8, a=5.6, b=8.6, fade_in=0.2, fade_out=0.8)
put(mix, S["impact"], st("lakh")-0.05, -6, fade_out=1.5)
# temple name: the bell
put(mix, S["04_bell"], st("temple")-0.15, -8, fade_out=1.6)
# THEN: dead silence 0.4s before, one heartbeat, boom on "Vault B"
gap0 = st("then")-0.45
for buf in (mix,bed):
    s=int(gap0*SR); buf[s-int(0.05*SR):] *= 0  # wipe everything placed so far after this point (beds placed later)
fade=int(0.25*SR); bed[int(gap0*SR)-fade:int(gap0*SR)] *= np.linspace(1,0,fade)[:,None]
put(mix, beat, st("then")-0.2, -4)
put(mix, S["08_boom"], st("then")+1.25, -6, fade_out=2.0)
# no handle / no lock / no keyhole: iron hits, breath in the left ear
for k in ["handle","lock","keyhole"]:
    put(mix, S["03_iron_door"], st(k)-0.05, -14, a=0.55, b=1.4, fade_out=0.3)
    put(mix, S["impact"], st(k)-0.02, -16, b=0.8, fade_out=0.4)
put(mix, S["07_breath"], en("keyhole")+0.05, -6, pan=-0.85, fade_out=0.3)
# legend / chant: choir returns low, reversed breath swell into "Get one word wrong"
put(bed, S["06_choir_drone"], st("legend")-0.3, -10, a=2.0, b=8.4, fade_in=0.8, fade_out=0.3)
rev = S["07_breath"][::-1].copy(); put(mix, rev, st("wrong")-1.9, -8, pan=0.6)
put(mix, S["01_hiss"], st("wrong")+0.7, -6, b=1.6, fade_out=0.25)
# total silence after "wrong" (mix and bed are both empty from en(wrong)+0.3 to st(weeks))
# weeks later: heartbeat speeding up, stops dead after "dead"
t = st("weeks")-0.2; iv = 1.05
while t < en("weeks")+0.05:
    put(mix, beat, t, -5); t += iv; iv = max(0.42, iv*0.86)
put(bed, S["06_choir_drone"], st("weeks"), -24, a=3.0, b=8.0, fade_in=1.5, fade_out=0.05)
s=int((en("weeks")+0.1)*SR); bed[s:int(st("warning")*SR)] = 0
# warning: eyes ignite (boom with metallic shing)
put(mix, S["08_boom"], st("warning")-0.15, -9, fade_out=1.5)
# never opened: rising sub rumble
rumble = S["06_choir_drone"][int(4*SR):int(8*SR)].copy(); ramp=np.linspace(0.2,1,len(rumble))[:,None]; rumble*=ramp
put(bed, rumble, st("never")-0.4, -9, fade_in=0.6, fade_out=0.06)
put(mix, S["impact"], st("never")-0.3, -12, fade_out=1.0)
# black -> "Would you?" whispered, one huge boom, hiss tail
put(mix, S["08_boom"], en("would")+0.25, 0, fade_out=2.2)
put(mix, S["impact"], en("would")+0.25, -4, fade_out=2.0)
put(mix, S["01_hiss"], en("would")+0.9, -10, fade_in=0.3, fade_out=1.2)
# VO on top, sidechain duck the bed under speech
v = np.zeros_like(mix); v[:min(len(vo),len(v))] = vo[:len(v)]
env = np.convolve(np.abs(v[:,0]), np.ones(int(0.12*SR))/int(0.12*SR), "same"); duck = 1 - 0.55*np.clip(env/0.05,0,1)
out = mix + bed*duck[:,None] + v*db(1.5)
meter = pyln.Meter(SR)
def limit(x, ceil=0.89, rel=0.12):
    """peak limiter: instant attack (5 ms look-ahead), smooth release"""
    pk = np.abs(x).max(1); need = np.maximum(1, pk / ceil); la = int(0.005 * SR)
    need = np.maximum.accumulate(np.r_[need[la:], np.ones(la)][::-1].reshape(-1))[::-1] if False else np.r_[need[la:], np.ones(la)]
    from scipy.ndimage import maximum_filter1d
    need = maximum_filter1d(need, la * 2 + 1)
    g = np.empty_like(need); a = np.exp(-1 / (rel * SR)); cur = 1.0
    for i in range(len(need)):
        cur = need[i] if need[i] > cur else need[i] + (cur - need[i]) * a; g[i] = cur
    return x / g[:, None]
for _ in range(3):
    L = meter.integrated_loudness(out); out *= db(-15.0 - L); out = limit(out)
sf.write(f"{R}/audio/vault-b-v3-mix.wav", out.astype(np.float32), SR, subtype="PCM_24")
print("dur", round(DUR,2), "LUFS", round(meter.integrated_loudness(out),1), "peak", round(np.abs(out).max(),3))
