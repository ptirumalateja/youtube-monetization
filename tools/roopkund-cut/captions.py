#!/usr/bin/env python3
"""ASS captions for the Roopkund cut. Yellow = {Y}...{W}."""
import sys
OUT = sys.argv[1]
CAPS = [
 (0.10, 2.45, "{Y}HUNDREDS{W}\\NOF SKELETONS"),
 (2.53, 4.73, "{Y}ROOPKUND{W}\\N5,000 m UP"),
 (4.81, 6.58, "DIED TOGETHER?"),
 (6.66, 8.88, "THEN: {Y}DNA{W}"),
 (8.96, 10.95, "GROUP 1\\N{Y}~800 AD{W}"),
 (11.03, 12.92, "GROUP 2\\N{Y}~1800{W}"),
 (13.00, 14.53, "{Y}1,000 YEARS{W}\\NAPART"),
 (14.60, 15.74, "CLOSEST\\NMATCH?"),
 (15.82, 17.80, "{Y}GREECE{W}\\N& {Y}CRETE{W}"),
 (17.88, 19.90, "CRACKED\\NFROM {Y}ABOVE{W}"),
 (19.98, 21.85, "THE LOCAL\\NLEGEND"),
 (21.85, 23.94, "{Y}IRON HAIL{W}"),
 (24.02, 25.60, "WHO WERE\\N{Y}THEY?{W}"),
]
def ts(t):
    h=int(t//3600); m=int(t%3600//60); s=t%60
    return f"{h}:{m:02d}:{s:05.2f}"
hdr = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter ExtraBold,92,&H00FFFFFF,&H00FFFFFF,&H00101010,&H90000000,0,0,0,0,100,100,1,0,1,5,3,5,60,60,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
with open(OUT,'w') as f:
    f.write(hdr)
    for a,b,t in CAPS:
        t = t.replace("{Y}","{\\c&H2FD8FF&}").replace("{W}","{\\c&HFFFFFF&}")
        # pop-in: 112% -> 100% over 90 ms, 60 ms fade
        f.write(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\pos(540,1230)\\fad(60,80)\\fscx112\\fscy112\\t(0,90,\\fscx100\\fscy100)}}{t}\n")
