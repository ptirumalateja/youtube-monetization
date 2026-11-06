#!/usr/bin/env python3
"""ASS keyword captions for V4. Times in tight-VO seconds, divided by TEMPO. Yellow = {Y}...{W}."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1]; TEMPO = float(os.environ.get('TEMPO', '1.08'))
from caps_en import CAPS
if os.environ.get('AB'):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ab_cut import CAPS
if os.environ.get('CUTMOD'):
    import importlib.util as _u; _sp = _u.spec_from_file_location('cm', os.environ['CUTMOD']); _m = _u.module_from_spec(_sp); _sp.loader.exec_module(_m); CAPS = _m.CAPS
FONT = os.environ.get('FONT', 'Inter ExtraBold')
def ts(t):
    t /= TEMPO; h = int(t//3600); m = int(t%3600//60); s = t%60
    return f"{h}:{m:02d}:{s:05.2f}"
hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{FONT},88,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,0,0,0,0,100,100,1,0,1,5,3,5,60,60,0,1\nStyle: Back,{FONT},88,&HFF000000,&HFF000000,&H70000000,&HFF000000,0,0,0,0,100,100,1,0,1,26,0,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open(OUT, 'w') as f:
    f.write(hdr)
    for a, b, t in CAPS:
        t = t.replace("{Y}", "{\\c&H2FD8FF&}").replace("{W}", "{\\c&HFFFFFF&}")
        pos = "" if t.startswith("{\\pos") else "\\pos(540,1230)"
        plain = t
        f.write(f"Dialogue: 0,{ts(a)},{ts(b)},Back,,0,0,0,,{{{pos}\\fad(60,80)\\blur14}}{plain}\n")
        f.write(f"Dialogue: 1,{ts(a)},{ts(b)},Cap,,0,0,0,,{{{pos}\\fad(60,80)\\fscx112\\fscy112\\t(0,90,\\fscx100\\fscy100)}}{t}\n")
