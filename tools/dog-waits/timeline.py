# v5 output timeline shared by compose.py and mix.py: (body_start, body_end, speed) after the cold open.
# speed<1 = slow motion (frame blend + time-stretched beds). Emotional beats get room: lie-down at 1x,
# 0.9 s day panels, a 0.7x hold at the door, a 0.5x embrace after the leap.
COLD=0.5
SEGS=[(0.18,0.30,1.0),(0.30,0.54,0.72),(0.63,1.53,1.0),(1.6,2.5,1.0),(2.7,3.6,1.0),(4.25,5.0,1.0),
      (5.0,5.7,0.7),(5.7,8.1,1.0),(8.1,8.6,0.5),(8.6,13.0,1.0)]
OUT=[]; _o=COLD
for b0,b1,s in SEGS: OUT.append(_o); _o+=(b1-b0)/s
OUTDUR=_o
def body_t(to):
    """output time -> (body time, speed)"""
    for (b0,b1,s),o0 in zip(SEGS,OUT):
        if to<o0+(b1-b0)/s: return b0+(max(to,o0)-o0)*s, s
    b0,b1,s=SEGS[-1]; return b1, s
def T(b):
    """body time -> output time; skipped body time snaps to the next cut, before the first segment extrapolates"""
    if b<SEGS[0][0]: return OUT[0]+(b-SEGS[0][0])
    for (b0,b1,s),o0 in zip(SEGS,OUT):
        if b<b0: return o0
        if b<b1: return o0+(b-b0)/s
    return OUTDUR+(b-SEGS[-1][1])
if __name__=='__main__':
    print('OUTDUR',round(OUTDUR,3)); [print(f'{o:6.3f}  body {b0}-{b1} x{s}') for (b0,b1,s),o in zip(SEGS,OUT)]
