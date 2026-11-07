import json, os
TL = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'timeline.json')))
K = TL['warp']
def fwd(o):   # output time -> story time
    for (s0, o0), (s1, o1) in zip(K, K[1:]):
        if o <= o1: return s0 + (o - o0) / (o1 - o0) * (s1 - s0)
    return K[-1][0]
def inv(s):   # story time -> output time
    for (s0, o0), (s1, o1) in zip(K, K[1:]):
        if s <= s1: return o0 + (s - s0) / (s1 - s0) * (o1 - o0)
    return K[-1][1]
