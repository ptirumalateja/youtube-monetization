"""Shot order and timing for the Vault B fact cut (v2). Frame counts come from output/anim/rt/<shot> (retime.py)."""
import os, glob
HERE = os.path.dirname(os.path.abspath(__file__))
RT = os.path.join(HERE, 'output', 'anim', 'rt')
ORDER = ['gold', 'door', 'gopuram', 'vaults', 'lamp', 'heads', 'seam', 'hand', 'eyes']
RAW = {'gold': 60, 'door': 60, 'gopuram': 60, 'vaults': 60, 'lamp': 36, 'heads': 42, 'seam': 42, 'hand': 42, 'eyes': 78}
FPS = 24


def counts():
    return {s: len(glob.glob(os.path.join(RT, s, 'f*.png'))) for s in ORDER}


def starts():
    c = counts(); t = 0; st = {}
    for s in ORDER:
        st[s] = t; t += c[s]
    st['end'] = t
    return st, c


def raw_to_cut(shot, raw_frame):
    """Seconds in the cut at which a raw (pre-retime) frame of `shot` lands."""
    st, c = starts()
    return (st[shot] + raw_frame * c[shot] / RAW[shot]) / FPS
