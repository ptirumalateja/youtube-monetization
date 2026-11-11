"""Sound for the umbrella reel. No music, no voice-over: every sound has a visible cause (Teja's rule).
  python3 mix.py OUT.wav
Rain bed + rain on the canopy, wet footsteps, the grey man's laughs, the thunder crack at the flash, the umbrella
snapped shut and thrown, its clatter, the ground cracking, dry heat, the pour into the cup, the gulps, panting,
knees hitting the dirt, the umbrella popping open. All foley from the ElevenLabs sound-effects API (sfx/gen.sh)."""
import os, subprocess, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'slow-light-dark-common'))
from sld_sound import SR, hp, lp, place, curve, write_wav
DUR = 11.8; N = int(DUR * SR)


def samp(name):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, 'sfx', name + '.mp3'), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    s = hp(np.frombuffer(raw, np.float32).astype(np.float64), 40); return s / (np.abs(s).max() + 1e-9)


def onset(s, th=0.3): return int(np.argmax(np.abs(s) > th))


def put(bus, name, t, g, pan=0.0, at='start', off=0.0, dur=None, fade=0.04):
    s = samp(name)[int(off * SR):]
    if dur: s = s[:int(dur * SR)]
    f = int(fade * SR); s = s.copy(); s[:f] *= np.linspace(0, 1, f); s[-f:] *= np.linspace(1, 0, f)
    t0 = t - (onset(s) / SR if at == 'onset' else 0); place(bus, s, max(0, t0), g, pan)


def loop_bed(name, g_curve, pan=0.0):
    s = samp(name); s = np.tile(s, int(np.ceil(N / len(s))) + 1)[:N]
    return np.stack([s * g_curve * (1 - pan * 0.5), s * g_curve * (1 + pan * 0.5)])


mix = np.zeros((2, N))
mix += loop_bed('rain', curve(N, [(0, 0.55), (2.95, 0.55), (3.05, 0.65), (3.7, 0.0), (DUR, 0)]))
mix += loop_bed('rain_umb', curve(N, [(0, 0.28), (2.95, 0.28), (3.6, 0.0), (DUR, 0)]), -0.3)
mix += loop_bed('heat', curve(N, [(0, 0), (3.6, 0), (4.6, 0.32), (11.2, 0.32), (11.8, 0)]))
fol = np.zeros((2, N))
put(fol, 'steps_wet', 0.0, 0.35, 0.0, dur=3.0)
put(fol, 'laugh', 0.08, 0.75, 0.3, at='onset')
put(fol, 'laugh2', 1.18, 0.8, 0.3, at='onset')
put(fol, 'thunder', 2.98, 1.0, 0.2, at='onset')
put(fol, 'drip', 3.5, 0.3, -0.3)
put(fol, 'umb_close', 3.98, 0.55, 0.3, at='onset')
put(fol, 'throw', 4.32, 0.6, 0.4, at='onset')
put(fol, 'clatter', 5.0, 0.6, 0.45, at='onset')
put(fol, 'crack', 4.4, 0.45, 0.0)
put(fol, 'steps_dry', 4.4, 0.3, 0.0, dur=1.6)
put(fol, 'pant', 5.7, 0.35, 0.3, dur=2.2)
put(fol, 'pour', 6.42, 0.6, -0.25, dur=0.65)
put(fol, 'gulp', 7.33, 0.7, -0.25, at='onset', dur=0.8)
put(fol, 'kneel', 8.18, 0.65, 0.3, at='onset')
put(fol, 'kneel', 8.42, 0.4, 0.35, at='onset')
put(fol, 'umb_open', 9.12, 0.6, 0.3, at='onset')
put(fol, 'pant', 9.6, 0.25, 0.3, off=0.3, dur=1.6)
mix += fol
mix *= curve(N, [(0, 1), (11.25, 1), (11.8, 0)])[None]
mix = np.tanh(mix / np.abs(mix).max() * 1.4) / np.tanh(1.4)
write_wav(mix, sys.argv[1]); print('ok')
