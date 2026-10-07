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

sd *= ramp([(0, -99), (3.5, -99), (7.0, 0), (26.6, 0), (27.4, -9), (29.0, -9), (30.0, 0), (30.6, 3), (34.6, 3),
            (35.6, 0), (128.2, 0), (128.8, -10), (131.2, -10), (132.2, 0), (196.0, 0), (210.0, -8), (216.0, -99),
            (TOTAL, -99)])[:, None]
dc *= ramp([(0, -99), (226.0, -99), (229.0, 0), (LAST_WORD, 0), (LAST_WORD + 2.5, 7), (TOTAL - 4.0, 7),
            (TOTAL - 0.3, -99), (TOTAL, -99)])[:, None]
music = sd + dc
music /= np.abs(music).max() + 1e-9
with wave.open("out/music.wav", "wb") as wf:
    wf.setnchannels(2); wf.setsampwidth(2); wf.setframerate(SR)
    wf.writeframes((np.clip(music * 0.9, -1, 1) * 32767).astype(np.int16).tobytes())

MUSIC_VOL = float(__import__("os").environ.get("MUSIC_VOL", "0.55"))
FINAL_VOL = float(__import__("os").environ.get("FINAL_VOL", "3.0"))
run(["ffmpeg", "-v", "error", "-y", "-i", "out/narr_shifted.wav", "-i", "out/bed.wav", "-i", "out/music.wav",
     "-filter_complex",
     "[0:a]highpass=f=70,acompressor=threshold=0.1:ratio=2.5:attack=15:release=250,asplit=2[n][sc];"
     # the score: carve room for the voice (2-3 kHz dip), then duck it whenever the narrator speaks
     f"[2:a]equalizer=f=2500:t=q:w=1.0:g=-5,equalizer=f=250:t=q:w=1.0:g=-2,volume={MUSIC_VOL}[m0];"
     "[sc]aformat=channel_layouts=stereo,volume=4[scs];"
     "[m0][scs]sidechaincompress=threshold=0.03:ratio=5:attack=40:release=600:makeup=1[m];"
     "[1:a]volume=1.5,lowpass=f=6000[b];"
     "[n][b][m]amix=inputs=3:normalize=0:duration=longest,"
     f"volume={FINAL_VOL},alimiter=limit=0.89:level=disabled[a]",
     "-map", "[a]", "-ar", str(SR), "-ac", "2", "out/mix_music.wav"])
run(["ffmpeg", "-v", "error", "-y", "-i", "out/aliens_long.mp4", "-i", "out/mix_music.wav", "-map", "0:v", "-map", "1:a",
     "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-movflags", "+faststart", "-shortest", "out/aliens_long_music.mp4"])
print("done")
