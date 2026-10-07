#!/usr/bin/env python3
"""Re-mix the long film's audio with Scott Buckley's score (CC BY 4.0) and mux onto the existing picture.

Arc: static intro, no music -> "Shadows and Dust" carries the film (ducked under the voice, lifts on the
title card, dips at the two breaths) -> fades to nothing before the hot-tub line, so it lands in near silence
-> "Decoherence" rises from silence for the ending and plays the film out to black.
Needs out/narr_shifted.wav, out/bed.wav and out/aliens_long.mp4 from build_long.py.
"""
import subprocess, wave
import numpy as np

SR = 48000
TOTAL = 251.4
LAST_WORD = 240.3


def run(cmd):
    subprocess.run(cmd, check=True)


def load(path, start=0.0, dur=None):
    cmd = ["ffmpeg", "-v", "error", "-ss", str(start), "-i", path]
    if dur:
        cmd += ["-t", str(dur)]
    cmd += ["-ac", "2", "-ar", str(SR), "-f", "f32le", "-"]
    a = np.frombuffer(subprocess.run(cmd, capture_output=True, check=True).stdout, np.float32)
    return a.reshape(-1, 2).astype(np.float64)


N = int(TOTAL * SR)
t = np.arange(N) / SR


def ramp(points):
    """Piecewise-linear gain envelope from (time, dB) points; -99 dB = off."""
    ts, db = zip(*points)
    g = np.interp(t, ts, db)
    return np.where(g <= -98, 0.0, 10 ** (g / 20))


def place(track, at):
    out = np.zeros((N, 2))
    i0 = int(at * SR)
    n = min(len(track), N - i0)
    out[i0:i0 + n] = track[:n]
    return out


# Shadows and Dust from its own start; Decoherence from its start too (it rises out of silence by itself).
sd = place(load("audio/music/ShadowsAndDust.mp3", 0, 230), 3.5)
dc = place(load("audio/music/Decoherence.mp3", 0, 30), 226.0)



def smooth(x, k):
    c = np.cumsum(np.concatenate([[0.0], x]))
    y = (c[k:] - c[:-k]) / k
    return np.concatenate([np.full(k // 2, y[0]), y, np.full(len(x) - len(y) - k // 2, y[-1])])


def db(x):
    return 20 * np.log10(np.maximum(x, 1e-7))


# --- auto-levelling: keep the score a fixed distance under the voice ---
narr = load("out/narr_shifted.wav")[:N, 0]
narr = np.concatenate([narr, np.zeros(N - len(narr))])
v_env = np.sqrt(smooth(narr ** 2, int(0.4 * SR)))
speaking = smooth((v_env > 10 ** (-38 / 20)).astype(float), int(0.6 * SR))        # 0..1, soft edges
speaking = np.maximum(speaking, np.concatenate([speaking[int(0.3 * SR):], np.zeros(int(0.3 * SR))]))  # lead in early
V = 20 * np.log10(np.sqrt(np.mean(narr[v_env > 10 ** (-38 / 20)] ** 2)))          # voice level while speaking
UNDER, GAPS = float(__import__("os").environ.get("UNDER", "20")), 12.0
target = (V - UNDER) * speaking + (V - GAPS) * (1 - speaking)
m_env = db(np.sqrt(smooth(sd.mean(1) ** 2, int(3.0 * SR))))
lev = np.clip(target - m_env, -30, 10)
lev = smooth(lev, int(1.0 * SR))
sd *= (10 ** (lev / 20))[:, None]

# Decoherence keeps its own slow rise; it only sits lower under the last line.
d_env = db(np.sqrt(smooth(dc.mean(1) ** 2, int(3.0 * SR))))
dlev = smooth(np.clip((V - UNDER) * speaking + (V - 3) * (1 - speaking) - d_env, -30, 0), int(1.0 * SR))
dc *= (10 ** (dlev / 20))[:, None]

# --- the arc (artistic automation on top) ---
sd *= ramp([(0, -99), (3.5, -99), (7.0, 0), (26.6, 0), (27.4, -9), (29.0, -9), (30.0, 0), (30.6, 3), (34.6, 3),
            (35.6, 0), (128.2, 0), (128.8, -10), (131.2, -10), (132.2, 0), (196.0, 0), (210.0, -8), (216.0, -99),
            (TOTAL, -99)])[:, None]
dc *= ramp([(0, -99), (226.0, -99), (229.0, 0), (TOTAL - 4.0, 0), (TOTAL - 0.3, -99), (TOTAL, -99)])[:, None]
music = sd + dc
peak = np.abs(music).max()
print("voice", round(V, 1), "dB; music peak", round(db(peak), 1))
with wave.open("out/music.wav", "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((np.clip(music, -1, 1) * 32767).astype(np.int16).tobytes())

MUSIC_VOL = float(__import__("os").environ.get("MUSIC_VOL", "1.0"))
FINAL_VOL = float(__import__("os").environ.get("FINAL_VOL", "3.8"))
run(["ffmpeg", "-v", "error", "-y", "-i", "out/narr_shifted.wav", "-i", "out/bed.wav", "-i", "out/music.wav",
     "-filter_complex",
     "[0:a]highpass=f=70,acompressor=threshold=0.1:ratio=2.5:attack=15:release=250[n];"
     # the score: carve room for the voice (2-3 kHz dip), then duck it whenever the narrator speaks
     f"[2:a]equalizer=f=2500:t=q:w=1.0:g=-4,equalizer=f=250:t=q:w=1.0:g=-2,volume={MUSIC_VOL}[m];"
     "[1:a]volume=1.5,lowpass=f=6000[b];"
     "[n][b][m]amix=inputs=3:normalize=0:duration=longest,"
     f"volume={FINAL_VOL},alimiter=limit=0.89:level=disabled[a]",
     "-map", "[a]", "-ar", str(SR), "-ac", "2", "out/mix_music.wav"])
run(["ffmpeg", "-v", "error", "-y", "-i", "out/aliens_long.mp4", "-i", "out/mix_music.wav", "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", "out/aliens_long_music.mp4"])
print("done")
