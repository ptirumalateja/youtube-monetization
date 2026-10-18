#!/usr/bin/env python3
"""Thumbnail / cover stills for the Speed Ladder reel, built from the reel's own frames (render12.py). usage: BGTL=<bgtl3.mp4> thumbs.py <out_dir>
A: bullet stop with a bigger "HOW FAST IS FAST?" | B: Earth stop with "YOU'RE MOVING 107,000 KM/H". 1080x1920; the key content stays inside the centre 3:4 / 1:1 crop that Instagram and YouTube grids show."""
import sys, os
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import render12 as R
out=sys.argv[1]; os.makedirs(out,exist_ok=True); R.NO_TITLE=True
def darken_top(im,h=520,k=0.85):
    a=np.asarray(im.convert('RGB')).astype(np.float32); g=np.clip(1-np.linspace(0,1,h)[:,None,None],0,1)**1.2*k; a[:h]*=(1-g); return Image.fromarray(a.astype(np.uint8)).convert('RGBA')
def mask_title(im):
    return darken_top(im,380,0.6)
# A: bullet, counter and name stay, new bigger title
fa=R.draw(2.4); fa=mask_title(fa); tx=Image.new('RGBA',(R.W,R.H),(0,0,0,0))
R.put(tx,R.row(['HOW FAST IS','#FAST','?'],150),R.CX,150,1.0); fa.alpha_composite(tx); fa.convert('RGB').save(os.path.join(out,'thumb_A_bullet.png'))
# B: Earth, headline = the title's hook
fb=R.draw(3.9); fb=mask_title(fb); tx=Image.new('RGBA',(R.W,R.H),(0,0,0,0))
R.put(tx,R.txt("YOU'RE MOVING",150),R.CX,140,1.0); R.put(tx,R.row(['#107,000 KM/H'],160),R.CX,140+150,1.0); fb.alpha_composite(tx); fb.convert('RGB').save(os.path.join(out,'thumb_B_earth.png'))
print('ok')
