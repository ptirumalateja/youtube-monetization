#!/usr/bin/env python3
"""Sound for the hole-becomes-hill reel (18.2 s): processed deep VO + synthesized drone, heartbeat, sub drops, shovel thumps + CC0 Freesound hits (tools/sfxlib).
usage: audio_mix_hh.py VO_PROC.wav OUT.wav"""
import subprocess, sys, wave
import numpy as np
SR = 44100; DUR = 18.2
LIB = "/home/user/youtube-monetization/tools/sfxlib/"
N = int(SR * DUR); t = np.arange(N) / SR
out = np.zeros(N, np.float32); rng = np.random.RandomState(3)
def add(sig, t0, amp=1.0):
    i0 = int(t0 * SR)
    if i0 >= N: return
    seg = sig[:N - i0] * amp; out[i0:i0 + len(seg)] += seg
env = np.interp(t, [0, 4.5, 6, 13.3, 16, 18.2], [0.45, 0.7, 0.55, 0.9, 0.6, 0.0])
dr = (np.sin(2 * np.pi * 49 * t) + 0.5 * np.sin(2 * np.pi * 73.5 * t + 0.7) + 0.3 * np.sin(2 * np.pi * 98 * t + 1.3)) * 0.25
nz = np.convolve(rng.randn(N).astype(np.float32), np.ones(400) / 400, "same") * 3
out += ((dr + nz * 0.10) * env * 0.55).astype(np.float32)
def beat(t0, amp):
    for off, a in ((0.0, 1.0), (0.23, 0.62)):
        L = int(0.3 * SR); tt = np.arange(L) / SR
        add((np.sin(2 * np.pi * (64 - 20 * tt / 0.3) * tt) * np.exp(-tt / 0.075) * a).astype(np.float32), t0 + off, amp)
tb = 0.3
while tb < 4.5: beat(tb, 0.30 + 0.3 * tb / 4.5); tb += 1.0 - 0.1 * tb / 4.5
tb = 16.2
while tb < 18.0: beat(tb, 0.32); tb += 0.95
def subdrop(t0, f0, f1, dur, amp):
    L = int(dur * SR); tt = np.arange(L) / SR
    f = f0 * (f1 / f0) ** (tt / dur); ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.tanh(np.sin(ph) * np.exp(-tt / (dur / 3.2)) * 1.8) * 0.7; add(s.astype(np.float32), t0, amp)
subdrop(3.10, 90, 30, 1.2, 0.9)   # "you build a hill"
subdrop(4.75, 96, 28, 1.2, 1.0)   # shove
subdrop(5.88, 80, 26, 1.4, 1.1)   # landing
subdrop(13.40, 88, 30, 1.3, 1.0)  # on top
subdrop(16.20, 96, 28, 1.5, 1.0)
# shovel scoops: thump + soft scrape + falling dirt
for k in range(7):
    ts = 8.5 + 0.77 * k - 0.38
    L = int(0.35 * SR); tt = np.arange(L) / SR
    th = np.sin(2 * np.pi * (110 - 60 * tt / 0.35) * tt) * np.exp(-tt / 0.09)
    sc = np.convolve(rng.randn(L), np.ones(30) / 30, "same") * np.exp(-tt / 0.16) * 0.6
    add((th + sc).astype(np.float32) * 0.8, ts, 0.7)
synth = np.clip(out, -1, 1)
with wave.open("/tmp/hh_synth.wav", "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((synth * 32767).astype(np.int16).tobytes())
vo, outp = sys.argv[1], sys.argv[2]
ms = lambda x: int(round(x * 1000))
fc = (
    "[0:a]aformat=channel_layouts=mono,asplit=2[vo_sc][vo_m];"
    "[1:a]aformat=channel_layouts=mono,volume=0.9[syn];"
    "[2:a]aformat=channel_layouts=mono,atrim=0:3.2,afade=t=out:st=2.3:d=0.9,lowpass=f=2200,volume=0.7,asplit=3[e1][e2][e3];"
    f"[e1]adelay={ms(4.72)}:all=1[e1d];[e2]adelay={ms(5.85)}:all=1,volume=1.1[e2d];[e3]adelay={ms(13.38)}:all=1,volume=1.1[e3d];"
    "[3:a]aformat=channel_layouts=mono,atrim=0:3.0,afade=t=in:st=0:d=0.6,afade=t=out:st=2.4:d=0.6,volume=0.5,"
    f"adelay={ms(10.6)}:all=1[rs];"
    "[4:a]aformat=channel_layouts=mono,atrim=0:3.0,afade=t=out:st=2.0:d=1.0,volume=0.55,asplit=2[w1][w2];"
    f"[w1]adelay={ms(4.55)}:all=1[w1d];[w2]adelay={ms(15.8)}:all=1[w2d];"
    "[5:a]aformat=channel_layouts=mono,atrim=0:3.5,afade=t=out:st=2.5:d=1.0,volume=0.7,asplit=2[a1][a2];"
    f"[a1]adelay={ms(3.05)}:all=1[a1d];[a2]adelay={ms(16.15)}:all=1[a2d];"
    "[6:a]aformat=channel_layouts=mono,atrim=3:12,lowpass=f=520,volume=0.5,afade=t=in:st=0:d=1.0,afade=t=out:st=7.5:d=1.5,"
    f"adelay={ms(8.6)}:all=1[wind];"
    "[syn][e1d][e2d][e3d][rs][w1d][w2d][a1d][a2d][wind]amix=inputs=10:normalize=0,volume=0.9[sfx];"
    "[sfx][vo_sc]sidechaincompress=threshold=0.035:ratio=7:attack=12:release=260:makeup=1[sfxd];"
    "[sfxd]volume=0.85[sfxv];"
    f"[vo_m]apad=whole_dur={DUR}[vop];[vop][sfxv]amix=inputs=2:normalize=0:duration=longest,alimiter=limit=0.95,loudnorm=I=-14:TP=-1.2:LRA=9,aformat=channel_layouts=stereo[out]"
)
cmd = ["ffmpeg", "-v", "error", "-y", "-i", vo, "-i", "/tmp/hh_synth.wav",
       "-i", LIB + "814046__qubodup__explosion-from-another-dimension.wav", "-i", LIB + "822420__audiopapkin__riser-hit-sfx-120.wav",
       "-i", LIB + "649445__audiopapkin__cinematic-woosh-sfx-015.wav", "-i", LIB + "869757__mikiko850__dark-suspense-accent.wav",
       "-i", LIB + "22331__sleepcircle__wind.ogg", "-filter_complex", fc, "-map", "[out]", "-t", f"{DUR}", "-ar", "44100", outp]
subprocess.run(cmd, check=True); print("wrote", outp)
