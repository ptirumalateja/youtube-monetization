# Time warp for the 16 s cut: new video time -> scene time of the 20 s master render (frames are re-used, not re-rendered).
import json, os, sys, numpy as np
TL = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timeline.json'))); CUT = TL['cut']
_W = np.array(CUT['warp'], float)
def old_of_new(t): return np.interp(t, _W[:, 0], _W[:, 1])
def new_of_old(t): return np.interp(t, _W[:, 1], _W[:, 0])
if __name__ == '__main__':      # python3 cut.py FRAMES_DIR OUT_DIR  -> symlinks f0000..f(T*30-1) pointing at the master frames
    src, dst = sys.argv[1], sys.argv[2]; os.makedirs(dst, exist_ok=True)
    for n in range(int(CUT['T'] * 30)):
        o = min(int(round(float(old_of_new(n / 30)) * 30)), int(TL['T'] * 30) - 1)
        l = os.path.join(dst, 'f%04d.jpg' % n)
        if os.path.lexists(l): os.remove(l)
        os.symlink(os.path.join(src, 'f%04d.jpg' % o), l)
