"""V7 = the V6 sound design retimed for the V7 cut (laptop + phone montage, V6 output 6.4-8.4 s, slowed to 0.8x: +0.5 s).
Every time below is still written in V6 output time; place/curve/the lids map it through m().

V6 sound design for You Were Blind for 20 Minutes Today, built straight on the V6 output timeline (23.267 s).

Teja (28 Oct): the V3-V5 sound read as amateur and the "music" killed the feel. So: no tonal content at all (the 55 Hz chord drone,
the A-major brain pad and the CTA chime are gone). What is left is sound design with a cause on screen:
  * every blink is a hard cut to near silence for as long as the lids are shut (dark = silent), framed by a tight lid "thock";
  * recorded impacts for the three payoffs: the Freesound riser-hit into "20:00", the explosion (read low) on "~1 YEAR",
    a subby whoosh + slam on "3 METRES BLIND", the fantasy implosion sucking the eye into the brain;
  * non-tonal low rumble for tension, room tone, real-feeling foley (footsteps, palm on glass), real sparks for the brain;
  * hits sit on a post-gate bus so they ring through the blackouts.

  python3 mix_v6.py OUT.wav
"""
import os, sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sld_sound import *
from mix import tick, key_click, page

D6 = 698 / 30; D = 713 / 30; N = int(round(D * SR)); t = np.arange(N) / SR

def m(x):
    """V6 output time -> V7 output time."""
    if x < 6.4: return x
    if x < 8.4: return 6.4 + (x - 6.4) / 0.8
    return D if x >= D6 - 1e-6 else x + 0.5
_place, _curve = place, curve
def place(bus, sig, ts, gain=1.0, pan=0.0): _place(bus, sig, m(ts), gain, pan)
def curve(n, K): return _curve(n, [(m(a), v) for a, v in K])

def o(s):
    """Scene time (scene_dark.js) -> V6 output time (build_v6 SEGS)."""
    if s < 12.6: return s
    if s >= 22.0: return 12.6 + (s - 22.0)
    if s < 14.467: return 14.8 + (s - 13.0)
    return 16.2667 + (s - 15.0)

# lids in output time: (start, shut length). Screen blinks, the two real-eye blinks, the brain blinks, the road blink, the loop close.
BL = [3.3, 4.75, 5.9, 6.85, 7.8, 8.65, 9.05, 9.3, 9.5, 9.66, 9.8, 9.9, 12.4, 18.6, 19.75]
LIDS = [(m(s_), L_) for s_, L_ in [(o(b), 0.13) for b in BL] + [(1.2, 0.12), (o(13.45), 0.12), (o(15.5), 0.14), (o(16.35), 0.14), (13.7, 0.16)]]

def sfx(name, a=0.0, b=None, fade=0.05):
    x = load(name); x = x[int(a * SR):int(b * SR) if b else None].copy(); f = int(fade * SR)
    if f: x[-f:] *= np.linspace(1, 0, f)
    return x / (np.abs(x).max() + 1e-9)

def thock(seed, g=1.0):
    """Lid shutting: a tight, dry, low knock with a little skin, no ring."""
    n = int(0.12 * SR); tt = np.arange(n) / SR
    body = np.sin(2 * np.pi * (95 + 70 * np.exp(-tt / 0.008)) * tt) * np.exp(-tt / 0.03)
    skin = bp(np.random.default_rng(seed).standard_normal(n), 1800, 1.2) * np.exp(-tt / 0.006) * 0.35
    return (body + skin) * g

def step(seed, g=1.0):
    """Bare foot on a hard floor: heel thump then a soft scuff."""
    n = int(0.25 * SR); tt = np.arange(n) / SR; r = np.random.default_rng(seed)
    heel = lp(r.standard_normal(n), 380) * np.exp(-tt / 0.018) * 2.2 + np.sin(2 * np.pi * 70 * tt) * np.exp(-tt / 0.03)
    scuff = bp(r.standard_normal(n), 2600, 1.0) * np.exp(-((tt - 0.06) / 0.04) ** 2) * 0.12
    return (heel + scuff) * g

def glass_touch(g=1.0):
    """Palm meeting a mirror: soft flesh slap, a damped low knock through the frame, a faint squeak of skin on glass."""
    n = int(0.5 * SR); tt = np.arange(n) / SR; r = np.random.default_rng(91)
    slap = bp(r.standard_normal(n), 1100, 1.0) * np.exp(-tt / 0.012)
    knock = np.sin(2 * np.pi * 160 * tt) * np.exp(-tt / 0.04) * 0.5
    squeak = bp(r.standard_normal(n), 3800, 3.0) * np.exp(-((tt - 0.12) / 0.05) ** 2) * 0.15
    return (slap + knock + squeak) * g

def heart(g=1.0):
    n = int(0.6 * SR); tt = np.arange(n) / SR
    k = lambda t0, a: np.where(tt >= t0, (np.sin(2 * np.pi * 48 * (tt - t0)) + 0.4 * lp(np.random.default_rng(int(t0 * 99)).standard_normal(n), 120)) * np.exp(-(tt - t0) / 0.06) * a, 0)
    return k(0, 1.0) + k(0.17, 0.65)

def rumble(seed, fc=70):
    return lp(hp(np.random.default_rng(seed).standard_normal(N), 22), fc, 3)

def main(out):
    B = {k: np.zeros((2, N)) for k in ('amb', 'fol', 'fx', 'hit')}
    # ---- the gate: everything but the hit bus drops ~30 dB while the lids are shut
    lid = np.zeros(N)
    for s, L in LIDS:
        u = t - s; lid = np.maximum(lid, np.where((u >= 0) & (u <= L + 0.05), np.clip(np.minimum(u / 0.025, (L + 0.05 - u) / 0.05), 0, 1), 0))
    lid = np.maximum(lid, np.clip((t - m(23.09)) / 0.05, 0, 1))                                           # lids close into the loop
    lid = np.maximum(lid, np.clip(1 - t / 0.08, 0, 1))                                                  # frame 0 opens out of black
    # ---- beds (non-tonal)
    w = load('22331__sleepcircle__wind.ogg'); w = np.tile(w, int(np.ceil((N + SR) / len(w))) + 1)
    room = lp(hp(w[:N], 80), 600); room /= np.abs(room).max()
    room_g = curve(N, [(0, 0.10), (2.4, 0.14), (12.6, 0.14), (12.62, 0.0), (14.8, 0.0), (14.82, 0.06), (16.27, 0.0), (18.27, 0.0), (18.29, 0.13), (D, 0.13)])
    rb = rumble(3); rb /= np.abs(rb).max()
    rb_g = curve(N, [(0, 0.5), (2.4, 0.18), (5.4, 0.2), (9.7, 0.75), (9.74, 0.0), (9.9, 0.0), (10.3, 0.35), (11.2, 0.3), (12.6, 0.0), (14.8, 0.25), (16.27, 0.4),
                     (18.27, 0.15), (21.0, 0.35), (D, 0.5)])
    for c in range(2): B['amb'][c] += room * room_g * (1 + 0.1 * c) + rb * rb_g
    # ---- hook: open out of black on a hit, the eye's real blink at 1.2 is wet and close
    place(B['hit'], lp(sfx('814046__qubodup__explosion-from-another-dimension.wav', 0, 1.4, 0.8), 1800), 0.0, 0.8)
    place(B['hit'], thud(3, 50, 0.3, 1.0), 0.0, 0.9)
    n = int(0.22 * SR); wet = bp(noise(n), 1400, 1.4) * np.exp(-np.arange(n) / SR / 0.035)
    place(B['fol'], wet * 0.5, 1.19, 1.0); place(B['fol'], wet[::-1] * 0.35, 1.32, 1.0)
    for tb in (0.75, 1.75): place(B['hit'], heart(0.55), tb, 1.0)
    # ---- lock-in: each line lands on a low, dry hit
    for ts in (2.45, 3.95): place(B['hit'], thud(int(ts * 10), 62, 0.12, 0.7), ts, 1.0)
    place(B['fol'], page(0.4, 0.35), 4.2, 1.0, -0.2)
    # ---- every lid: thock on close (the gate does the dark); quieter in the rapid run
    for i, (s, L) in enumerate(LIDS):
        g = 0.55 if 9.0 < s < 10.0 else 0.9
        place(B['hit'], thock(i, g), s, 1.0)
    # ---- day montage: one real-world cue per time of day, cut by the lids, a riser under the whole run
    for k in range(10): place(B['fol'], key_click(50 + k), 6.5 + k * 0.085, 0.4, 0.25)              # 1 PM keys
    for k in range(3): place(B['fol'], key_click(70 + k) * 0.6, 7.55 + k * 0.22, 0.35, 0.3)            # 6 PM phone taps
    place(B['fol'], page(0.4, 0.4), 8.55, 1.0, -0.2)                                                    # 11 PM page
    rh = sfx('822420__audiopapkin__riser-hit-sfx-120.wav', 0, 9.0, 1.5)                                 # its hit is at 6.08 s
    place(B['fx'], rh[:int(6.06 * SR)], 9.9 - 6.06, 0.9); place(B['hit'], rh[int(6.06 * SR):], 9.9, 1.0)   # riser gated by the blinks, hit rings free
    place(B['hit'], sub_boom(2.0), 9.9, 0.8)
    # ---- lifetime: days flick past, then the biggest hit on "~1 YEAR"
    tk, k = 11.25, 0
    while tk < 12.5: place(B['fol'], tick(200 + k, 0.45), tk, 0.6, 0.3 * np.sin(k)); tk += max(0.035, 0.2 * (1 - (tk - 11.25) / 1.3)); k += 1
    ex = sfx('814046__qubodup__explosion-from-another-dimension.wav', 0, 1.25, 0.3)
    place(B['hit'], lp(ex, 2500), 11.45, 1.1); place(B['hit'], sub_boom(1.2), 11.45, 1.0); place(B['hit'], thud(612, 40, 0.4, 1.0), 11.45, 1.0)
    # ---- danger beat 12.6-14.8: hard cut into road roar; the blink at 13.7 kills it; the number slams
    dn = int(2.2 * SR); dt = np.arange(dn) / SR; r = np.random.default_rng(5)
    eng = lp(r.standard_normal(dn), 110, 3) * 3 * (1 + 0.25 * np.sin(2 * np.pi * 31 * dt))
    tyre = bp(r.standard_normal(dn), 650, 0.8) * 0.8 + hp(r.standard_normal(dn), 4000) * 0.08
    wind = hp(w[SR:SR + dn], 500) * 6
    road = (eng + tyre + wind) * np.minimum(1, dt / 0.01)
    for c in range(2): B['fx'][c, int(m(12.6) * SR):int(m(12.6) * SR) + dn] += road[:N - int(m(12.6) * SR)] * 0.5
    for kk, tk in enumerate(np.arange(12.66, 14.8, 0.432)): place(B['fol'], step(300 + kk, 0.35), tk, 0.5, 0.0)   # reflector joints under the tyres
    sw = sfx('238375__stewdio2003__cp_subby_whoosh.aiff', 0.9, 2.4, 0.2); place(B['hit'], sw, 13.91 - 0.63, 0.8)
    place(B['hit'], lp(ex, 3000), 13.91, 0.9); place(B['hit'], thud(901, 44, 0.35, 1.1), 13.91, 1.0)
    # ---- eye push: woosh across the cut, wet blink, implosion sucks into the pupil and lands on the brain
    wo = sfx('649445__audiopapkin__cinematic-woosh-sfx-015.wav', 2.0, 4.2, 0.4); place(B['fx'], wo, 14.8 - 0.5, 0.7)
    place(B['fol'], wet * 0.5, o(13.45) - 0.01, 1.0)
    im = sfx('814047__qubodup__fantasy-implosion.wav', 0, 1.6, 0.5); place(B['fx'], hp(im, 60), 16.2667 - 0.93, 0.85)
    place(B['hit'], thud(130, 55, 0.25, 0.9), 16.2667, 1.0)
    # ---- brain: real sparks, thinned, cut dead on each blink (the gate does it)
    sp = sfx('849772__mikiko850__electric-sparks.wav', 3.0, 5.2, 0.2); sp = lp(hp(sp, 1500), 7000)
    place(B['fx'], sp, 16.3, 0.6, -0.3); place(B['fx'], sp[::-1], 16.6, 0.45, 0.3)
    # ---- mirror: footsteps, breath as he leans in, palm on the glass, slow heart, lids close into the loop
    for k, ts in enumerate([17.22, 17.72]): place(B['fol'], step(410 + k, 0.8), o(ts), 1.0, -0.1 + 0.2 * k)
    place(B['fol'], breath(0.7, 'in', 3, 0.3), o(18.3), 1.0, -0.1)
    place(B['fol'], glass_touch(0.9), o(19.3), 1.0, 0.15)
    tb = o(19.6)
    while tb < 22.9: place(B['hit'], heart(0.45), tb, 1.0); tb += 0.9
    place(B['hit'], thock(99, 1.2), 23.09, 1.0); place(B['hit'], thud(700, 46, 0.25, 0.9), 23.09, 1.0)
    # ---- mix: gate, short room on foley, a hall on the hits, soft clip
    for k in ('amb', 'fol', 'fx'):
        for c in range(2): B[k][c] = hp(B[k][c], 35 if k == 'amb' else 70, 2)
    ir_r = [reverb_ir(0.9, 4000, 1), reverb_ir(0.9, 4000, 2)]; ir_h = [reverb_ir(2.6, 2200, 3), reverb_ir(2.6, 2200, 4)]
    fol = B['fol'] + np.stack([convolve(B['fol'][c], ir_r[c]) for c in range(2)]) * 0.18
    hit = B['hit'] + np.stack([convolve(B['hit'][c], ir_h[c]) for c in range(2)]) * 0.22
    he = lp(np.abs(B['hit']).max(0), 6); sc = 1 - 0.55 * np.clip(he / (he.max() + 1e-9) * 3, 0, 1)    # the bed breathes under the hits
    gate = 1 - 0.97 * lid
    mix = (B['amb'] * 0.9 * sc + fol + B['fx'] * sc) * gate[None] + hit
    mix = np.tanh(mix / np.abs(mix).max() * 1.8) / np.tanh(1.8)
    f = int(0.004 * SR); mix[:, :f] *= np.linspace(0, 1, f); mix[:, -f:] *= np.linspace(1, 0, f)
    write_wav(mix, out); print('wrote', out, mix.shape[1] / SR)

if __name__ == '__main__': main(sys.argv[1])
