"""Sound for Nobody Claps at 6 AM. No music, no voice: every sound has a visible cause.
  python3 mix.py EVENTS_JSON OUT.wav
Foley = ElevenLabs sound effects (sfx/*.mp3, sfx/gen.sh). Cue times come from window.events / window.TL in scene.js.
The contrast is the whole edit: a roar at frame 0 that is cut dead at the hard cut, then only alarm, footsteps, breath,
wind and rain for 10 s, then the roar comes back bigger at the finale and fades to one set of footsteps."""
import json, subprocess, sys, os, wave
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SR = 48000
ev = json.load(open(sys.argv[1])); DUR = ev['dur']; N = int(DUR * SR); TL = ev['tl']
mixb = np.zeros((N, 2)); tt = np.arange(N) / SR
cache = {}
def load(name, rate=1.0):
    k = (name, rate)
    if k not in cache:
        af = [] if rate == 1 else ['-af', f'asetrate={int(SR*rate)},aresample={SR}']
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', os.path.join(HERE, 'sfx', name + '.mp3'), *af, '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
        s = np.frombuffer(raw, np.float32).astype(np.float64); s /= np.abs(s).max() + 1e-9; cache[k] = s
    return cache[k]
def bed(name):
    s = load(name); n = len(s); xf = int(0.3 * SR); o = np.zeros(N + n); pos = 0; ramp = np.linspace(0, 1, xf)
    while pos < N:
        seg = s.copy(); seg[:xf] *= ramp; seg[-xf:] *= ramp[::-1]; o[pos:pos + n] += seg; pos += n - xf
    return o[:N]
def env(keys): return np.interp(tt, [k[0] for k in keys], [k[1] for k in keys])
C = TL['T_CUT']; R1, RA, FA, TR, ST, SP, F365, TP, CL = TL['T_RUN1'], TL['T_RAIN'], TL['T_FALL'], TL['T_TRACK'], TL['T_STEPS'], TL['T_STOP'], TL['T_365'], TL['T_TAPE2'], TL['T_CLOSE']
FH = TL['FALL_SND']
# beds
run = env([(0, 0), (R1 - 0.05, 0), (R1, 1), (FH - 0.15, 1), (FH, 0), (8.42, 0), (8.52, 1), (SP + 0.2, 1), (SP + 0.5, 0), (F365 + 0.05, 0), (F365 + 0.25, 1.1), (TP, 1.1), (TP + 0.6, 0),
           (CL + 1.4, 0), (CL + 1.8, 0.45), (DUR, 0.45)])
steps = bed('steps'); mixb[:, 0] += steps * run * 0.55; mixb[:, 1] += np.roll(steps, 900) * run * 0.55
br = bed('breath'); bg = env([(0, 0), (R1 - 0.05, 0), (R1, 0.5), (SP, 0.5), (SP + 0.6, 0), (DUR, 0)]); mixb += (br * bg * 0.45)[:, None]
wind = bed('wind'); wg = env([(0, 0), (C, 0), (C + 0.02, 0.35), (F365 - 0.05, 0.35), (F365, 0), (DUR, 0)]); mixb[:, 0] += wind * wg * 0.5; mixb[:, 1] += np.roll(wind, 7000) * wg * 0.5
rain = bed('rain'); rg = env([(0, 0), (RA - 0.02, 0), (RA, 0.8), (FA - 0.02, 0.8), (FA, 0), (DUR, 0)]); mixb[:, 0] += rain * rg * 0.6; mixb[:, 1] += np.roll(rain, 5000) * rg * 0.6
# one-shots
for e in ev['events']:
    s = load(e['s'], e.get('rate', 1.0)) * e['g']; i = int(e['t'] * SR); s = s[:max(0, N - i)]
    if i < 0: s = s[-i:]; i = 0
    s = s.copy(); te = e['t'] + np.arange(len(s)) / SR
    if e['t'] < C: s *= np.clip((C - te) / 0.015, 0, 1)                        # the hard cut kills the roar dead
    if e['s'] in ('heart', 'pant'): s *= np.clip((F365 - te) / 0.03, 0, 1)      # lights out: dead silence before the slam
    if e['s'] in ('roar', 'roar2') and e['t'] > F365:
        if e['t'] < TP - 0.5: s *= np.clip((te - e['t']) / 0.9, 0, 1)          # stands filling: roar swells in
        s *= np.interp(te, [CL + 0.4, CL + 2.0], [1, 0.12])                    # fades to his footsteps
    if e['s'] == 'roar' and e['t'] == 0: s *= np.clip(te / 0.004, 0, 1)
    l, r = np.sqrt((1 - e['pan']) / 2), np.sqrt((1 + e['pan']) / 2)
    mixb[i:i + len(s), 0] += s * l; mixb[i:i + len(s), 1] += s * r
fade = env([(0, 1), (DUR - 0.5, 1), (DUR, 0.3)]); mixb *= fade[:, None]
mixb *= 0.89 / (np.abs(mixb).max() + 1e-9)
with wave.open(sys.argv[2], 'wb') as f:
    f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR); f.writeframes((mixb * 32767).astype('<i2').tobytes())
print('ok', sys.argv[2])
