#!/usr/bin/env python3
"""Camera-time warp for the trimmed cut. Maps video time tau -> scene camera time T (the original 28.2 s timeline).
Holds are trimmed by running the camera faster through them (animation time stays real time). Speed changes are smoothed."""
import numpy as np, json
ANCH = [(0,0),(1.5,1.5),(4.8,3.0),(6.4,4.4),(7.0,5.0),(8.6,6.5),(12.4,9.1),(14.6,11.1),(18.4,13.8),(20.8,15.9),(24.0,18.1),(25.0,19.0),(27.0,20.9),(28.2,22.0)]
DT = 1/240.0; TAU_END = ANCH[-1][1]; T_END = ANCH[-1][0]
tau = np.arange(0, TAU_END + 1.0, DT)
speed = np.ones_like(tau)
for (T0, t0), (T1, t1) in zip(ANCH, ANCH[1:]):
    m = (tau >= t0) & (tau < t1); speed[m] = (T1 - T0) / (t1 - t0)
speed[tau >= TAU_END] = 1.0
k = int(0.45 / DT) | 1; ker = np.ones(k) / k
pad = np.pad(speed, (k // 2, k // 2), mode='edge'); sm = np.convolve(pad, ker, mode='valid')
T = np.concatenate([[0], np.cumsum(sm[:-1]) * DT])
# renormalise so the end lands exactly on the original timeline length
i_end = int(round(TAU_END / DT)); T *= T_END / T[i_end]
json.dump({'dt': DT, 'tau_end': TAU_END, 'T_end': T_END, 'anch': ANCH, 'T': [round(float(x), 5) for x in T]}, open('warp.json', 'w'))
chk = lambda t0: float(np.interp(t0, tau, T))
print('T at tau anchors:', [(a, round(chk(b), 3)) for a, b in ANCH])
