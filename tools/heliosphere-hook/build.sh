#!/bin/sh
# frames (output/frames/f0000.jpg ...) + output/sound.wav -> master (CRF 16) and a share encode (~8 Mb/s two-pass)
set -e
cd "$(dirname "$0")/output"
ffmpeg -y -hide_banner -loglevel warning -framerate 30 -i frames/f%04d.jpg -i sound.wav -map 0:v -map 1:a -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 -af "volume=2dB,alimiter=limit=0.7:level=false" -c:a aac -b:a 192k -ar 48000 -t 26 -movflags +faststart not-a-vortex_master.mp4
ffmpeg -y -hide_banner -loglevel warning -i not-a-vortex_master.mp4 -c:v libx264 -preset slow -b:v 7.5M -pass 1 -an -f mp4 /dev/null
ffmpeg -y -hide_banner -loglevel warning -i not-a-vortex_master.mp4 -c:v libx264 -preset slow -b:v 7.5M -pass 2 -c:a copy -movflags +faststart not-a-vortex.mp4
rm -f ffmpeg2pass-0.log ffmpeg2pass-0.log.mbtree
ls -la not-a-vortex*.mp4
