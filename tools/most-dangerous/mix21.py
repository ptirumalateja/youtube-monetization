"""Sound bed for the 16.4 s psychology remake (VO goes on top when it arrives).
python3 mix.py OUT.wav [vo.wav]   cut whooshes at each shot change, braaam on ANGER, rain/hum/wind beds per shot, dark accent on UNTIL ONE DAY."""
import subprocess, sys, wave
import numpy as np
SR, DUR = 48000, 19.0
out = np.zeros((int(DUR * SR), 2), np.float32); rng = np.random.default_rng(3)
CUTS = [1.9, 4.15, 7.1, 10.05, 12.0, 15.2]
def load(name, a=0, b=None):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', name if '/' in name else '../sfxlib/' + name, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.float32).reshape(-1, 2).copy(); x = x[int(a * SR):int(b * SR) if b else None]
    f = min(int(0.05 * SR), len(x)); x[-f:] *= np.linspace(1, 0, f)[:, None]; return x
def put(x, t, db=0.0):
    a = int(t * SR); x = x[:max(0, len(out) - a)]; out[a:a + len(x)] += x * 10 ** (db / 20)
def lp(x, k):
    X = np.fft.rfft(x); w = np.linspace(0, np.pi, len(X)); H = k / (1 - (1 - k) * np.exp(-1j * w))
    y = np.fft.irfft(X * H, len(x)); return (y / (np.abs(y).max() + 1e-9)).astype(np.float32)
def bed(t0, t1, k, db, fade=0.08):
    n = int((t1 - t0) * SR); x = np.stack([lp(rng.normal(0, 1, n), k), lp(rng.normal(0, 1, n), k)], 1)
    f = int(fade * SR); x[:f] *= np.linspace(0, 1, f)[:, None]; x[-f:] *= np.linspace(1, 0, f)[:, None]; put(x, t0, db)
def hum(t0, t1, hz, db):
    n = int((t1 - t0) * SR); t = np.arange(n) / SR; s = (np.sin(2 * np.pi * hz * t) + 0.4 * np.sin(4 * np.pi * hz * t)) * (0.8 + 0.2 * np.sin(t * 37) * np.sin(t * 13))
    put(np.repeat(s[:, None], 2, 1).astype(np.float32), t0, db)
# low drone under everything, swelling into the end
t = np.arange(len(out)) / SR; dr = (np.sin(2 * np.pi * 55 * t) * 0.6 + np.sin(2 * np.pi * 82.4 * t) * 0.3) * (0.5 + 0.5 * t / DUR)
# no drone (Teja: musical beds kill the feel)
bed(0, 1.9, 0.01, -26)                                     # empty room
bed(1.9, 4.15, 0.25, -24); hum(1.9, 4.15, 120, -38)       # alley rain + fluorescent buzz
put(load('22331__sleepcircle__wind.ogg', 4, 7.0), 4.15, -18)  # park breeze
bed(7.1, 10.05, 0.006, -22)
n = int((8.15 - 7.1) * SR); tt = np.arange(n) / SR; m = lp(rng.normal(0, 1, n), 0.08) * (0.5 + 0.5 * np.sign(np.sin(tt * 2 * np.pi * 5.3)) * np.abs(np.sin(tt * 2 * np.pi * 2.1)))
put(np.repeat(m[:, None], 2, 1).astype(np.float32), 7.1, -24)                                  # office air
bed(10.05, 12.0, 0.3, -23)                                   # rain on cafe glass
bed(12.0, 14.9, 0.004, -26)                                # bedroom hush
put(load('22331__sleepcircle__wind.ogg', 12, 15.8), 15.2, -14)  # rooftop wind
for c in CUTS: put(load('649445__audiopapkin__cinematic-woosh-sfx-015.wav', 2.35, 2.95), c - 0.12, -14)
put(load('722633__chakong__cinematic-braaam.wav', 0, 3.5), 2.78, -7)          # ANGER
put(load('869757__mikiko850__dark-suspense-accent.wav', 0, 3.8), 15.2, -9)
put(load('722633__chakong__cinematic-braaam.wav', 0, 1.8), 0.0, -16)   # frame-0 low hit so the start isn't dry
# slow heartbeat under 'carry pain / nobody noticed'
for k, tb in enumerate(np.arange(12.15, 14.7, 0.92)):
    n = int(0.35 * SR); tt = np.arange(n) / SR
    for off, a in ((0, 1.0), (0.17, 0.6)):
        m = int(off * SR); s_ = np.zeros(n, np.float32); s_[m:] = (np.sin(2 * np.pi * 48 * tt[:n - m]) * np.exp(-tt[:n - m] / 0.07) * a)
        put(np.repeat(s_[:, None], 2, 1), tb, -10)      # UNTIL ONE DAY
if len(sys.argv) > 2:
    vo = load(sys.argv[2]); out[:, :] *= 0.5; put(vo, float(sys.argv[3]) if len(sys.argv) > 3 else 0.0, 0)
out *= 0.89 / np.abs(out).max()
with wave.open(sys.argv[1] if len(sys.argv) > 1 else 'bed.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((np.clip(out, -1, 1) * 32767).astype('<i2').tobytes())
print('ok')
