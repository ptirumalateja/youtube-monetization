#!/usr/bin/env python3
"""Sound for 'How Much of You Is Actually You?' v2 (24.9 s).
Layers: processed deep-voice VO (ElevenLabs, voice 'Rex Thunder - Deep N Tough', eleven_v4) + synthesized drone, heartbeat, sub-bass drops
+ CC0 Freesound hits/whooshes/wind from tools/sfxlib (no credit required). SFX are ducked under the voice.

usage: audio_mix.py VO_PROC.wav OUT.wav
"""
import subprocess, sys, wave
import numpy as np

SR = 44100; DUR = 24.9
LIB = "/home/user/youtube-monetization/tools/sfxlib/"
N = int(SR * DUR); t = np.arange(N) / SR
out = np.zeros(N, np.float32)
rng = np.random.RandomState(1)

def add(sig, t0, amp=1.0):
    i0 = int(t0 * SR)
    if i0 >= N: return
    seg = sig[:N - i0] * amp
    out[i0:i0 + len(seg)] += seg

# ---- drone bed
env = np.interp(t, [0, 5, 7.5, 14, 17.5, 20, 24.9], [0.45, 0.7, 1.0, 0.8, 1.0, 0.7, 0.0])
dr = (np.sin(2 * np.pi * 55 * t) + 0.5 * np.sin(2 * np.pi * 82.5 * t + 0.7) + 0.35 * np.sin(2 * np.pi * 110 * t + 1.3)) * 0.25
nz = np.convolve(rng.randn(N).astype(np.float32), np.ones(400) / 400, "same") * 3
out += ((dr + nz * 0.12) * env * 0.55).astype(np.float32)

# ---- heartbeat (lub-dub)
def beat(t0, amp):
    for off, a in ((0.0, 1.0), (0.23, 0.62)):
        L = int(0.3 * SR); tt = np.arange(L) / SR
        s = np.sin(2 * np.pi * (64 - 20 * tt / 0.3) * tt) * np.exp(-tt / 0.075) * a
        add(s.astype(np.float32), t0 + off, amp)
tb = 0.35
while tb < 5.1:
    beat(tb, 0.35 + 0.5 * tb / 5); tb += 0.98 - 0.14 * tb / 5
tb = 17.9
while tb < 24.6:
    beat(tb, 0.32 * (1 - max(0, tb - 22) / 3)); tb += 1.08

# ---- sub-bass drops on the hits
def subdrop(t0, f0, f1, dur, amp):
    L = int(dur * SR); tt = np.arange(L) / SR
    f = f0 * (f1 / f0) ** (tt / dur); ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.sin(ph) * np.exp(-tt / (dur / 3.2)); s = np.tanh(s * 1.8) * 0.7
    add(s.astype(np.float32), t0, amp)
subdrop(3.70, 92, 30, 1.3, 1.0)
subdrop(7.50, 80, 32, 1.0, 0.7)
subdrop(12.58, 88, 30, 1.2, 0.9)
subdrop(14.12, 70, 34, 0.7, 0.5)
subdrop(17.66, 96, 28, 1.5, 1.1)

# ---- tiny ding when the apple appears
L = int(0.7 * SR); tt = np.arange(L) / SR
ding = (np.sin(2 * np.pi * 1760 * tt) + 0.4 * np.sin(2 * np.pi * 2637 * tt)) * np.exp(-tt / 0.18) * 0.12
add(ding.astype(np.float32), 16.35)

synth = np.clip(out, -1, 1)
with wave.open("/tmp/cells_synth.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((synth * 32767).astype(np.int16).tobytes())

vo, outp = sys.argv[1], sys.argv[2]
def ms(x): return int(round(x * 1000))
fc = (
    "[0:a]aformat=channel_layouts=mono,asplit=2[vo_sc][vo_m];"
    "[1:a]aformat=channel_layouts=mono,volume=0.9[syn];"
    # explosion hits (lowpassed so they are felt more than heard on a phone)
    "[2:a]aformat=channel_layouts=mono,atrim=0:3.2,afade=t=out:st=2.3:d=0.9,lowpass=f=2200,volume=0.75,asplit=2[e1][e2];"
    f"[e1]adelay={ms(3.69)}:all=1[e1d];[e2]adelay={ms(17.64)}:all=1,volume=1.15[e2d];"
    # riser + whoosh into the dive
    "[3:a]aformat=channel_layouts=mono,atrim=0:3.0,afade=t=in:st=0:d=0.6,afade=t=out:st=2.4:d=0.6,volume=0.55,"
    f"adelay={ms(4.95)}:all=1[rs];"
    "[4:a]aformat=channel_layouts=mono,atrim=0:3.6,afade=t=out:st=2.4:d=1.2,volume=0.55,asplit=3[w1][w2][w3];"
    f"[w1]adelay={ms(5.15)}:all=1[w1d];[w2]atrim=0:2.0,afade=t=out:st=1.2:d=0.8,adelay={ms(13.95)}:all=1[w2d];"
    f"[w3]atrim=0:2.4,areverse,adelay={ms(15.3)}:all=1,volume=1.1[w3d];"
    # dark accents on the punchlines
    "[5:a]aformat=channel_layouts=mono,atrim=0:3.5,afade=t=out:st=2.5:d=1.0,volume=0.7,asplit=2[a1][a2];"
    f"[a1]adelay={ms(7.45)}:all=1[a1d];[a2]adelay={ms(12.56)}:all=1,volume=1.1[a2d];"
    # underwater wind bed in the micro world
    "[6:a]aformat=channel_layouts=mono,atrim=3:12,lowpass=f=480,volume=0.55,afade=t=in:st=0:d=1.0,afade=t=out:st=7.5:d=1.5,"
    f"adelay={ms(7.4)}:all=1[wind];"
    "[syn][e1d][e2d][rs][w1d][w2d][w3d][a1d][a2d][wind]amix=inputs=10:normalize=0,volume=0.9[sfx];"
    "[sfx][vo_sc]sidechaincompress=threshold=0.035:ratio=7:attack=12:release=260:makeup=1[sfxd];"
    "[sfxd]volume=0.85[sfxv];"
    "[vo_m]apad=whole_dur=24.9[vop];[vop][sfxv]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.2:LRA=9,aformat=channel_layouts=stereo[out]"
)
cmd = ["ffmpeg", "-v", "error", "-y", "-i", vo, "-i", "/tmp/cells_synth.wav",
       "-i", LIB + "814046__qubodup__explosion-from-another-dimension.wav",
       "-i", LIB + "822420__audiopapkin__riser-hit-sfx-120.wav",
       "-i", LIB + "649445__audiopapkin__cinematic-woosh-sfx-015.wav",
       "-i", LIB + "869757__mikiko850__dark-suspense-accent.wav",
       "-i", LIB + "22331__sleepcircle__wind.ogg",
       "-filter_complex", fc, "-map", "[out]", "-t", f"{DUR}", "-ar", "44100", outp]
subprocess.run(cmd, check=True)
print("wrote", outp)
