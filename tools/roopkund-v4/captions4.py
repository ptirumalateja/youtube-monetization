#!/usr/bin/env python3
"""ASS keyword captions for V4. Times in tight-VO seconds, divided by TEMPO. Yellow = {Y}...{W}."""
import sys, os
OUT = sys.argv[1]; TEMPO = float(os.environ.get('TEMPO', '1.08'))
CAPS = [
 (0.10, 2.60, "WHEN THE {Y}ICE{W}\\NMELTS..."),
 (2.70, 5.30, "THE LAKE GIVES\\NBACK ITS {Y}DEAD{W}"),
 (5.40, 6.40, "{Y}ROOPKUND{W}"),
 (6.45, 8.15, "{Y}5,000 m{W} UP"),
 (8.20, 9.20, "THE {Y}HIMALAYAS{W}"),
 (9.30, 11.10, "{Y}HUNDREDS{W}\\NOF SKELETONS"),
 (11.20, 13.30, "EVERYONE\\NBELIEVED..."),
 (13.35, 15.70, "THEY DIED\\N{Y}TOGETHER{W}"),
 (16.60, 18.00, "{Y}THEY DIDN'T.{W}"),
 (18.10, 22.45, "GROUP 1\\N{Y}~800 AD{W}"),
 (22.55, 25.10, "GROUP 2\\N{Y}~1800{W}"),
 (25.20, 28.90, "{Y}1,000 YEARS{W}\\NAPART"),
 (29.00, 30.40, "THE SECOND\\NGROUP?"),
 (30.50, 31.90, "THEIR CLOSEST\\NDNA MATCH..."),
 (31.95, 34.85, "{Y}GREECE{W} & {Y}CRETE{W}"),
 (35.00, 37.20, "SKULLS\\N{Y}CRACKED{W}"),
 (37.30, 38.40, "FROM {Y}ABOVE{W}"),
 (38.50, 41.60, "THE VILLAGERS'\\N{Y}SONG{W}"),
 (41.70, 44.20, "HAIL HARD\\NAS {Y}IRON{W}"),
 (44.30, 48.45, "THE ICE GIVES\\NBACK {Y}MORE{W}"),
 (48.55, 50.30, "WHO WERE\\N{Y}THEY?{W}"),
 (48.90, 50.30, "{\\pos(540,1470)\\fs60}YOUR THEORY? ↓"),
]
if os.environ.get('AB'):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from ab_cut import CAPS
def ts(t):
    t /= TEMPO; h = int(t//3600); m = int(t%3600//60); s = t%60
    return f"{h}:{m:02d}:{s:05.2f}"
hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter ExtraBold,88,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,0,0,0,0,100,100,1,0,1,5,3,5,60,60,0,1\nStyle: Back,Inter ExtraBold,88,&HFF000000,&HFF000000,&H70000000,&HFF000000,0,0,0,0,100,100,1,0,1,26,0,5,60,60,0,1

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
