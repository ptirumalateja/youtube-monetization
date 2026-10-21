# Sound for The Dipper Is Melting: python3 mix_dipper.py out.wav
# Family: "the seven-star chord". Each Dipper star is one voice of a pure D chord. As the years run, the five
# Ursa Major Moving Group voices bend together (still in tune with each other) while Dubhe and Alkaid drift
# away, so the chord melts with the shape. The rewind bends it back to pure for the loop.
# Everything is synthesized here except two CC0 Freesound files (wind 22331, explosion 814046).
import subprocess, json, sys, wave
import numpy as np
SR = 48000; T = 20.0; N = int(SR*T); LIB = "../sfxlib/"
TL = json.load(open("timeline.json")); t = np.arange(N)/SR; rng = np.random.default_rng(11)
def mono_interp(keys, x):
    xs = np.array([k[0] for k in keys], float); ys = np.array([k[1] for k in keys], float); n = len(xs)
    d = np.diff(ys)/np.diff(xs); m = np.zeros(n); m[0] = d[0]; m[-1] = d[-1]
    for i in range(1, n-1): m[i] = 0 if d[i-1]*d[i] <= 0 else (d[i-1]+d[i])/2
    for i in range(n-1):
        if d[i] == 0: m[i] = m[i+1] = 0; continue
        a, b = m[i]/d[i], m[i+1]/d[i]; s = a*a+b*b
        if s > 9: k = 3/np.sqrt(s); m[i] = k*a*d[i]; m[i+1] = k*b*d[i]
    x = np.clip(x, xs[0], xs[-1]); i = np.clip(np.searchsorted(xs, x, 'right')-1, 0, n-2); h = xs[i+1]-xs[i]; u = (x-xs[i])/h
    return (2*u**3-3*u**2+1)*ys[i]+(u**3-2*u**2+u)*h*m[i]+(-2*u**3+3*u**2)*ys[i+1]+(u**3-u**2)*h*m[i+1]
Y = np.clip(mono_interp(TL['year'], t), 0, 1e5); yrate = np.abs(np.gradient(Y, 1/SR))
def db(g): return 10**(g/20)
def load(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", LIB+f, "-f", "f32le", "-ac", "2", "-ar", str(SR), "-"], capture_output=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()
def fft_filter(x, kind, fc, order=2):
    n = len(x); X = np.fft.rfft(x, axis=0); f = np.fft.rfftfreq(n, 1/SR)[:, None]; r = f/fc+1e-9
    mag = 1/np.sqrt(1+r**(2*order)) if kind == 'lp' else (1-1/np.sqrt(1+r**(2*order)))
    return np.fft.irfft(X*mag, n=n, axis=0)
def bandpass(x, lo, hi): return fft_filter(fft_filter(x if x.ndim > 1 else np.stack([x, x], 1), 'hp', lo), 'lp', hi)
def sstep(a, b, x): k = np.clip((x-a)/(b-a), 0, 1); return k*k*(3-2*k)
buses = {k: np.zeros((N, 2), np.float32) for k in ['hit', 'chord', 'sfx', 'bed', 'air', 'riser']}
def add(bus, sig, t0, gain=0.0, pan=0.0):
    a = int(round(t0*SR))
    if sig.ndim == 1: sig = np.stack([sig, sig], 1)
    sig = sig.astype(np.float32)*db(gain); l = 1-max(0, pan); r = 1+min(0, pan)
    if a < 0: sig = sig[-a:]; a = 0
    n = min(len(sig), N-a)
    if n <= 0: return
    buses[bus][a:a+n, 0] += sig[:n, 0]*l; buses[bus][a:a+n, 1] += sig[:n, 1]*r
def nz1(n): return rng.standard_normal(n).astype(np.float32)
def sat(x, d): return np.tanh(x*d)/np.tanh(d)
def hit(t0, size, gain=0.0):
    """playbook hit anatomy: crack + saturated pitch-drop body (88-320 Hz) + small sub + gong partials (tuned to D)"""
    n = int(4.0*SR); tt = np.arange(n)/SR
    f = 88+(300-88)*np.exp(-tt*(16-4*size)); ph = 2*np.pi*np.cumsum(f)/SR
    body = sat(np.sin(ph)*np.exp(-tt/(0.26+0.40*size))*(1-np.exp(-tt/0.0015)), 2.8+2.2*size)*0.85
    sub = np.sin(2*np.pi*(37+5*size)*tt)*np.exp(-tt/(0.5+0.6*size))*0.22*size
    crack = bandpass(nz1(n), 1800, 9500)[:, 0]*np.exp(-tt/0.012)*1.3
    gong = np.zeros(n, np.float32)
    for i, (fp, ap) in enumerate(((146.8, 1.0), (220.0, 0.7), (293.7, 0.7), (440.0, 0.45), (587.3, 0.35), (881, 0.2), (1175, 0.15))):
        gong += np.sin(2*np.pi*fp*1.003**i*tt+i*1.3)*ap*np.exp(-tt/(1.4+0.9*size))
    gong *= 0.17*size**0.8*(1-np.exp(-tt/0.004))
    add('hit', (body+sub+crack*0.9+gong*1.3).astype(np.float32), t0, gain)
def suck(t0, t1, gain=-8, lo=500, hi=7000):
    n = int((t1-t0)*SR); tt = np.arange(n)/SR; env = (tt/(t1-t0))**3*np.clip((t1-t0-tt)/0.03, 0, 1)
    add('riser', bandpass(nz1(n), lo, hi)*env[:, None], t0, gain)
def ping(t0, f, dec, gain, pan=0.0, bus='air'):
    n = int((dec+0.3)*SR); tt = np.arange(n)/SR; ph = 2*np.pi*f*tt
    s = (np.sin(ph)+0.25*np.sin(2.76*ph)*np.exp(-tt*5)+0.08*np.sin(5.4*ph)*np.exp(-tt*9))*np.exp(-tt/(dec*0.35))*(1-np.exp(-tt/0.004))
    add(bus, s.astype(np.float32), t0, gain, pan)
def whoosh(t0, dur, gain, pan0=-0.7, pan1=0.7, peak=0.5, rev=False):
    n = int(dur*SR); u = np.arange(n)/n; base = nz1(n); out = np.zeros((n, 2), np.float32)
    for i, (lo, hi) in enumerate(((150, 500), (500, 1500), (1500, 4000), (4000, 10000))):
        out += bandpass(base, lo, hi)*np.exp(-0.5*((u-(0.15+0.7*i/3.0))/0.2)**2)[:, None]
    out *= (np.sin(np.pi*np.clip(u**(np.log(0.5)/np.log(peak)), 0, 1))**1.5)[:, None]
    if rev: out = out[::-1].copy()
    m = out.mean(1); ang = (np.linspace(pan0, pan1, n)+1)*np.pi/4
    add('sfx', np.stack([m*np.cos(ang), m*np.sin(ang)], 1), t0, gain)

# ------------------------------------------------ the seven-star chord (D: D3 A3 D4 F#4 A4 D5 E5 as add9)
#  id: 0 Dubhe 1 Merak 2 Phecda 3 Megrez 4 Alioth 5 Mizar 6 Alkaid ; cents of drift at 100,000 years
VOICES = [(587.33, +85, 0.55, 0.6), (440.00, -35, 0.7, 0.35), (293.66, -35, 0.8, 0.1), (369.99, -35, 0.6, -0.1),
          (220.00, -35, 0.9, -0.3), (146.83, -35, 1.0, -0.5), (659.26, -120, 0.5, -0.65)]
yk = Y/1e5
rw = (t >= TL['rewind'][0])*(t < TL['rewind'][1]+0.15)
speed = 1+0.5*np.sin(np.pi*np.clip((t-TL['rewind'][0])/(TL['rewind'][1]+0.15-TL['rewind'][0]), 0, 1))*rw   # tape-rewind pitch rise
cenv = np.clip(t/0.04, 0, 1)*(0.55+0.45*np.exp(-t/0.8))                                  # bloom with the frame-0 hit
cenv *= 1-0.92*sstep(12.45, 12.62, t)*(1-sstep(13.17, 13.22, t))                          # held breath
cenv *= np.where(t >= 13.2, 1.35-0.45*sstep(13.4, 15.0, t), 1.0)                          # swell on the reveal
cenv *= 1-0.35*sstep(19.2, 19.97, t)                                                      # ease into the loop
chord = np.zeros((N, 2), np.float32)
for i, (f0, cents, amp, pan) in enumerate(VOICES):
    vib = 1+0.0025*np.sin(2*np.pi*(4.6+0.3*i)*t+i)
    f = f0*2**(cents*yk/1200)*vib*speed; ph = 2*np.pi*np.cumsum(f)/SR
    v = (np.sin(ph)+0.30*np.sin(2*ph+0.3)+0.12*np.sin(3*ph+1.1)+0.05*np.sin(4*ph))*amp
    v *= 0.85+0.15*np.sin(2*np.pi*(0.15+0.05*i)*t+i*2.1)                                  # each star breathes on its own
    ang = (pan+1)*np.pi/4; chord += np.stack([v*np.cos(ang), v*np.sin(ang)], 1).astype(np.float32)
chord = fft_filter(chord, 'lp', 3200)*cenv[:, None]
buses['chord'] += (chord/np.abs(chord).max()*0.62).astype(np.float32)

# ------------------------------------------------ the time-lapse itself: a whirr whose pitch is the speed of time
sp = np.clip(yrate/16000, 0, 1.2)*(t < TL['rewind'][0]); sp_s = np.convolve(sp, np.ones(2400)/2400, 'same')
nzw = np.stack([nz1(N), nz1(N)], 1); whirr = np.zeros((N, 2), np.float32)
for lo, hi, w in ((300, 700, 1.0), (700, 1600, 0.8), (1600, 3600, 0.5)):
    whirr += bandpass(nzw, lo, hi)*w*np.clip(sp_s*1.6-(lo/1600)*0.4, 0, 1)[:, None]
mod = 0.7+0.3*np.sin(2*np.pi*np.cumsum(3+14*sp_s)/SR)
buses['sfx'] += (whirr*(sp_s*mod)[:, None]*db(-12)).astype(np.float32)
for _ in range(900):                                                                       # star-dust grains, denser when time runs faster
    t0 = rng.uniform(2.0, TL['rewind'][0])
    if rng.random() < sp_s[int(t0*SR)]:
        ping(t0, rng.choice([1174.7, 1318.5, 1480.0, 1760.0, 2349.3, 2637.0]), rng.uniform(0.08, 0.25), -31+rng.uniform(-4, 3), pan=rng.uniform(-0.9, 0.9))

# ------------------------------------------------ cue sheet
hit(0.0, 0.7, gain=-1)                                                                     # frame 0
suck(1.62, 1.97, gain=-9); hit(2.0, 0.55, gain=-3); whoosh(2.0, 1.3, -10, peak=0.25)        # snap: time starts
for k, i in enumerate([1, 2, 3, 4, 5]):                                                    # 9.4 the family: five voices, one unison ping
    ping(9.45+0.07*k, 587.33*2**(-35*0.62/1200), 1.6, -19, pan=-0.5+0.25*k)
ping(9.45, 293.66*2**(-35*0.62/1200), 2.2, -22)
for k, (f0, c) in enumerate(((587.33, 85), (659.26, -120))):                              # 11.0 the two loners, sour
    ping(11.05+0.18*k, f0*2**(c*0.8/1200), 1.4, -18, pan=(0.6 if k == 0 else -0.6))
suck(12.7, 13.17, gain=-13, lo=400, hi=5000)                                               # held breath, then the reveal
hit(13.2, 1.4, gain=0)
EXP = load("814046__qubodup__explosion-from-another-dimension.wav"); add('hit', EXP[int(0.12*SR):int(3.2*SR)]*np.linspace(1, 0, int(3.08*SR))[:, None]**1.5, 13.2, -14)
n_ = int(3.2*SR); tt_ = np.arange(n_)/SR; wall = np.sin(2*np.pi*36*tt_)*np.exp(-tt_/0.9)*np.minimum(1, tt_/0.004); add('hit', wall*0.7, 13.2, -16)
whoosh(14.3, 3.0, -15, pan0=0.6, pan1=-0.6, peak=0.6)                                       # pull back into the wide sky
whoosh(17.75, 1.85, -8, pan0=-0.8, pan1=0.8, peak=0.75, rev=True)                          # rewind
n_ = int(1.75*SR); tt_ = np.arange(n_)/SR; fch = 300+2600*(tt_/1.75)**0.7                  # tape chirps up through the rewind
chirp = bandpass(nz1(n_), 600, 6000)[:, 0]*(0.5+0.5*np.sign(np.sin(2*np.pi*np.cumsum(9+40*tt_/1.75)/SR)))*np.sin(np.pi*tt_/1.75)
add('sfx', chirp, 17.8, -24)
u = np.clip((t-19.35)/0.6, 0, 1)*(t >= 19.35); lk = np.sin(2*np.pi*np.cumsum(146.83*(0.5+0.5*u**1.4))/SR)*u**1.6*db(-16)
buses['riser'] += np.stack([lk, lk], 1).astype(np.float32)                                # loop-link tone into frame 0
wd = load("22331__sleepcircle__wind.ogg"); bed = np.tile(wd, (int(np.ceil(N/len(wd)))+1, 1))[int(3*SR):int(3*SR)+N]
buses['bed'] += (fft_filter(bed, 'hp', 200)*(0.6+0.4*sstep(13.2, 15, t))[:, None]*db(-27)).astype(np.float32)

# ------------------------------------------------ bus processing, ducking, master
def reverb(x, rt=2.4, wet=0.3):
    n = int(rt*SR); ir = rng.standard_normal((n, 2)).astype(np.float32)*np.exp(-np.arange(n)/(0.45*SR))[:, None]; ir = fft_filter(ir, 'lp', 4200); ir /= np.abs(ir).max()
    out = np.zeros_like(x); L_ = len(x)+n
    for ch in (0, 1): out[:, ch] = np.fft.irfft(np.fft.rfft(x[:, ch], L_)*np.fft.rfft(ir[:, ch], L_), L_)[:len(x)]*wet*0.05
    return out
buses['hit'] += reverb(buses['hit']); buses['chord'] += reverb(buses['chord'], 3.2, 0.35); buses['air'] += reverb(buses['air'], 2.2, 0.45)
for k in ('sfx', 'bed', 'air', 'riser', 'chord'): buses[k] = fft_filter(buses[k], 'hp', 90)
buses['hit'] = fft_filter(buses['hit'], 'hp', 70)+fft_filter(buses['hit'], 'lp', 70)*0.45
duck = np.ones(N)
for h in (0.0, 2.0, 13.2):
    i1 = int(h*SR); rel = int(0.6*SR); duck[i1:i1+rel] = np.minimum(duck[i1:i1+rel], 0.15+0.85*np.linspace(0, 1, rel)**1.6)
for k in ('sfx', 'bed', 'air', 'riser'): buses[k] *= duck[:, None]
mix = sum(buses.values())
vac = np.ones(N)
def vacuum(a, b, floor=0.0, ramp=0.012):
    i0, i1 = int(a*SR), int(b*SR); vac[i0:i1] = np.minimum(vac[i0:i1], floor); r = int(ramp*SR); vac[i0-r:i0] = np.minimum(vac[i0-r:i0], np.linspace(1, floor, r))
vacuum(1.955, 1.997); vacuum(12.62, 13.15, floor=0.04, ramp=0.06); vacuum(13.155, 13.197); vacuum(19.93, 20.0, floor=0.0, ramp=0.02)
mix *= vac[:, None]
mix = fft_filter(mix, 'hp', 24); mix = np.tanh(mix*0.85)/np.tanh(0.85); mix = mix/np.abs(mix).max()*0.95
w_ = wave.open(sys.argv[1], "wb"); w_.setnchannels(2); w_.setsampwidth(2); w_.setframerate(SR); w_.writeframes((mix*32767).astype(np.int16).tobytes()); w_.close()
print("mixed", sys.argv[1])
