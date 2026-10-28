"""Slow Light Dark: shared sound kit (numpy only). Lifted from the pilot's mix (tools/chain-never-locked/mix.py).

Approach: minimal but heavy. A quiet room bed (CC0 wind, low-passed) + the lamp's mains hum (series signature) +
a 55 Hz drone that swells toward the twist; weighty foley with a visible cause for every sound; one held-breath silence
(about 0.25 s, everything ducked) right before the twist; the twist is the only big hit (sub_boom + a CC0 explosion read
two octaves down). No music bed. High-pass everything except the hit bus at 75-90 Hz (phones), keep the sub on the hit bus.
Master: gain to -15 LUFS then a look-ahead limiter; measure true peak AFTER AAC (see master_to_mp4).

  import sys; sys.path.insert(0, '../slow-light-dark-common'); from sld_sound import *
  N = int(DUR*SR); bus = new_buses(N); bed(bus, t_curve_room, t_curve_drone, duck)
  place(bus['hit'], clank(1.2, 40), 2.86, 0.6, -0.5) ...; write_wav(finish(bus, duck), 'mix.wav')
"""
import json, os, re, subprocess, sys, wave
import numpy as np

SR = 48000
HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, '..', 'sfxlib')
rng = np.random.default_rng(7)


# ---------------------------------------------------------------- helpers
def load(name, sr=SR):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(LIB, name), '-f', 'f32le', '-ac', '1', '-ar', str(sr), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).astype(np.float64)


def spec_filter(x, f):
    """Zero-phase filter: multiply the spectrum by gain(f) where f is an array of bin frequencies."""
    n = len(x); N = 1 << int(np.ceil(np.log2(n + 1)))
    X = np.fft.rfft(x, N); fr = np.fft.rfftfreq(N, 1 / SR)
    return np.fft.irfft(X * f(fr), N)[:n]


def lp(x, fc, order=2): return spec_filter(x, lambda f: 1 / np.sqrt(1 + (f / fc) ** (2 * order)))
def hp(x, fc, order=2): return spec_filter(x, lambda f: 1 / np.sqrt(1 + (fc / np.maximum(f, 1e-3)) ** (2 * order)))
def bp(x, fc, q): return spec_filter(x, lambda f: np.exp(-0.5 * (np.log(np.maximum(f, 1) / fc) * q) ** 2))


def env(n, a, d, sus=0.0):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * (sus + (1 - sus) * np.exp(-t / d))


def noise(n): return rng.standard_normal(n)


def place(bus, sig, t, gain=1.0, pan=0.0):
    i = int(round(t * SR))
    if i >= bus.shape[1]: return
    if i < 0: sig = sig[-i:]; i = 0
    n = min(len(sig), bus.shape[1] - i)
    l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    bus[0, i:i + n] += sig[:n] * gain * l * 1.414
    bus[1, i:i + n] += sig[:n] * gain * r * 1.414


def reverb_ir(sec, damp, seed):
    r = np.random.default_rng(seed); n = int(sec * SR); t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t * 6.9 / sec)
    ir = lp(ir, damp); ir[:int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    return ir / np.sqrt(np.sum(ir ** 2))


def convolve(x, ir):
    n = len(x) + len(ir); N = 1 << int(np.ceil(np.log2(n)))
    return np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:len(x)]


# ---------------------------------------------------------------- sources
def clank(weight=1.0, seed=0, bright=1.0):
    """A heavy iron impact: inharmonic modes + a short crack + a body thump (weight 0..1.5)."""
    r = np.random.default_rng(seed); n = int(1.6 * SR); t = np.arange(n) / SR; y = np.zeros(n)
    base = 165 * (1 - 0.18 * (weight - 1)) * (0.94 + 0.12 * r.random())
    for k, m in enumerate([1.0, 2.43, 4.1, 6.37, 8.9, 12.1, 15.7, 19.4]):
        f = base * m * (0.97 + 0.06 * r.random()); dec = (0.2 / (1 + 0.6 * k)) * (0.7 + 0.6 * r.random())   # short: dense iron, not a bell
        y += np.sin(2 * np.pi * f * t + r.random() * 6) * np.exp(-t / dec) * (0.9 / (1 + 0.5 * k)) * (bright if k > 3 else 1)
    crack = hp(noise(n), 2200) * env(n, 0.0004, 0.006) * 1.6 * bright
    grit = bp(noise(n), 1400, 0.8) * env(n, 0.001, 0.05) * 0.9   # link-on-link grind under the hit
    body = np.sin(2 * np.pi * (95 + 40 * np.exp(-t / 0.03)) * t) * env(n, 0.001, 0.09) * 1.2 * weight
    return (y * 0.55 + crack + grit + body) * env(n, 0.0006, 9)


def chink(seed, f0=2400):
    """One small link-on-link tick."""
    r = np.random.default_rng(seed); n = int(0.25 * SR); t = np.arange(n) / SR; y = np.zeros(n)
    for m in [1.0, 1.53, 2.31, 3.07]:
        y += np.sin(2 * np.pi * f0 * m * (0.9 + 0.2 * r.random()) * t) * np.exp(-t / (0.03 + 0.04 * r.random()))
    return y * 0.25 + hp(noise(n), 3000) * env(n, 0.0003, 0.004) * 0.6


def rattle(dur, rate, seed, f0=2000, gain=1.0):
    """A run of link ticks (chain moving)."""
    r = np.random.default_rng(seed); n = int((dur + 0.3) * SR); y = np.zeros(n); t = 0.0; k = 0
    while t < dur:
        s = chink(seed * 100 + k, f0 * (0.8 + 0.5 * r.random())); i = int(t * SR); m = min(len(s), n - i)
        y[i:i + m] += s[:m] * (0.4 + 0.6 * r.random()); t += r.exponential(1 / rate); k += 1
    return y * gain


def scrape(dur, seed, gain=1.0):
    """Iron dragged on concrete: band noise with grain."""
    n = int(dur * SR); x = noise(n)
    grain = np.repeat(np.random.default_rng(seed).random(n // 240 + 1), 240)[:n] ** 3
    y = bp(x, 900, 1.2) * (0.3 + grain) + bp(x, 2600, 2.0) * grain * 0.6
    e = np.minimum(1, np.arange(n) / (0.05 * SR)) * np.minimum(1, (n - np.arange(n)) / (0.12 * SR))
    return y * e * gain * 0.5


def breath(dur, kind, seed, gain=1.0):
    """Unvoiced breath. kind 'in' (sharp, higher) or 'out' (heavy, lower, chesty)."""
    n = int(dur * SR); x = np.random.default_rng(seed).standard_normal(n); t = np.arange(n) / dur / SR
    if kind == 'in':
        y = bp(x, 1500, 1.4) * 0.7 + bp(x, 2900, 2.2) * 0.35; e = np.sin(np.pi * np.minimum(1, t)) ** 0.8 * (0.4 + 0.6 * t)
    else:
        y = bp(x, 520, 1.3) * 1.0 + bp(x, 1150, 1.8) * 0.5 + lp(x, 260) * 0.35; e = (1 - np.exp(-t * 18)) * np.exp(-t * 2.4)
    return y * e * gain


def thud(seed, f=70, dec=0.16, gain=1.0):
    """Body / footstep weight: low sine drop + a soft noise slap."""
    n = int(0.8 * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * (f + 60 * np.exp(-t / 0.02)) * t) * env(n, 0.002, dec)
    return (s + lp(noise(n), 900) * env(n, 0.001, 0.025) * 0.6) * gain


def creak(seed, dur=0.9):
    """Iron link rocking under load: a slow stick-slip squeak with resonance."""
    n = int(dur * SR); t = np.arange(n) / SR; r = np.random.default_rng(seed)
    f = 420 + 120 * np.sin(2 * np.pi * 1.3 * t) + 40 * r.standard_normal(n).cumsum() / np.sqrt(np.arange(1, n + 1))
    pulses = (np.sin(2 * np.pi * np.cumsum(f) / SR) > 0.96).astype(float)
    y = bp(pulses, 900, 1.0) * 0.8 + bp(pulses, 2300, 2.2) * 0.4
    return y * np.sin(np.pi * t / dur) ** 1.5


def sub_boom(dur=4.5):
    """The reveal: a deep pitch-drop sub with an audible 90-300 Hz body (phones) and a slow tail."""
    n = int(dur * SR); t = np.arange(n) / SR
    f = 34 + 52 * np.exp(-t / 0.35); ph = 2 * np.pi * np.cumsum(f) / SR
    sub = np.sin(ph) * env(n, 0.004, 1.4)
    body = np.tanh(2.2 * (np.sin(ph * 2) * 0.7 + np.sin(ph * 3) * 0.35)) * env(n, 0.003, 0.5) * 0.55
    crack = lp(hp(noise(n), 300), 3500) * env(n, 0.0008, 0.035) * 0.5
    return sub * 1.0 + body + crack



# ---------------------------------------------------------------- buses, bed, master
def new_buses(N):
    return {k: np.zeros((2, N)) for k in ['bed', 'drone', 'fol', 'hit', 'air']}


def curve(N, K):
    """Piecewise-linear gain curve from [(t, g), ...] keys."""
    t = np.arange(N) / SR; xs, ys = zip(*K); return np.interp(t, xs, ys)


def bed(bus, room_g, drone_g, duck):
    """Room tone (CC0 sleepCircle wind.ogg, low-passed) + lamp hum + 55 Hz drone. room_g/drone_g/duck: per-sample gain arrays."""
    N = bus['bed'].shape[1]; t = np.arange(N) / SR
    w = load('22331__sleepcircle__wind.ogg'); w = np.tile(w, int(np.ceil((N + SR) / len(w))))[:N + SR]
    room = lp(hp(w, 60), 520)[:N]; room /= np.abs(room).max()
    room2 = lp(hp(w[SR // 2:SR // 2 + N], 60), 700); room2 /= np.abs(room2).max()
    hum = sum(np.sin(2 * np.pi * h * 60 * t + h) / h ** 1.2 for h in (2, 3, 4, 6)) * (1 + 0.15 * np.sin(2 * np.pi * 0.31 * t))
    hum = lp(hum, 600) * 0.012
    dr = np.sin(2 * np.pi * 55 * t) + 0.6 * np.sin(2 * np.pi * 110.4 * t) + 0.35 * np.sin(2 * np.pi * 82.6 * t) + 0.22 * np.sin(2 * np.pi * 164.7 * t)
    dr = np.tanh(1.4 * dr) * 0.09
    for c, a in enumerate([room, room2]):
        bus['bed'][c] += a * room_g + hum * duck
        bus['drone'][c] += dr * drone_g * (1 + 0.04 * np.sin(2 * np.pi * (0.13 + 0.02 * c) * t))


def finish(bus, duck):
    """Bus EQ, reverbs, side-chain, the silence window (hits survive it), soft clip. Returns (2, N) float."""
    for k in bus: bus[k] = np.nan_to_num(bus[k])
    for c in range(2):
        for k in ['fol', 'air', 'bed', 'drone']: bus[k][c] = hp(bus[k][c], 90 if k in ('fol', 'air') else 75, 3)
    ir_room = [reverb_ir(1.6, 3500, 1), reverb_ir(1.6, 3500, 2)]
    ir_hall = [reverb_ir(3.4, 1800, 3), reverb_ir(3.4, 1800, 4)]
    wet_f = np.stack([convolve(bus['fol'][c], ir_room[c]) for c in range(2)])
    wet_h = np.stack([convolve(bus['hit'][c], ir_hall[c]) for c in range(2)])
    hit_env = lp(np.abs(bus['hit']).max(0), 8); sc = 1 - 0.5 * np.clip(hit_env / (hit_env.max() + 1e-9) * 3, 0, 1)
    mix = bus['bed'] * sc + bus['drone'] * sc + bus['fol'] + wet_f * 0.22 + bus['hit'] + wet_h * 0.3 + bus['air']
    mix = mix * duck[None] + (bus['hit'] + wet_h * 0.3) * (1 - duck[None])
    mix = np.tanh(mix / np.abs(mix).max() * 1.6) / np.tanh(1.6)
    f = int(0.004 * SR); mix[:, :f] *= np.linspace(0, 1, f); mix[:, -f:] *= np.linspace(1, 0, f)
    return mix


def write_wav(mix, path):
    pcm = (np.clip(mix, -1, 1) * 0.95 * 32767).astype('<i2').T.copy()
    with wave.open(path, 'wb') as wv:
        wv.setnchannels(2); wv.setsampwidth(2); wv.setframerate(SR); wv.writeframes(pcm.tobytes())


def master_to_mp4(video, wav, out, target=-15.0):
    """Mux wav onto a silent video: gain to target LUFS + look-ahead limiter; returns (LUFS, true peak) measured after AAC."""
    def meas(path, af=None):
        r = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', (af + ',' if af else '') + 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
        s = r[r.rindex('Summary:'):]; return float(re.search(r'I:\s+(\S+) LUFS', s).group(1)), float(re.search(r'Peak:\s+(\S+) dBFS', s).group(1))
    g = target - meas(wav)[0]
    for _ in range(3):
        af = f"volume={g:.2f}dB,alimiter=limit=0.75:attack=4:release=60:level=false,aresample=48000"; g += target - meas(wav, af)[0]
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', video, '-i', wav, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-af', af,
                    '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', out], check=True)
    return meas(out)
