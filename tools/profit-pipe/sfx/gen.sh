#!/bin/bash
# ElevenLabs foley for mix.py. Needs ELEVENLABS_API_KEY. One request at a time.
cd "$(dirname "$0")"
gen(){ n=$1; d=$2; p="$3"; [ -s $n.mp3 ] && [ -z "$FORCE" ] && return; for i in 1 2 3; do curl -sS -o $n.mp3 -X POST https://api.elevenlabs.io/v1/sound-generation -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" -d "{\"text\":\"$p\",\"duration_seconds\":$d,\"prompt_influence\":0.7}"; [ $(stat -c%s $n.mp3) -gt 2000 ] && break; sleep 4; done; echo $n $(stat -c%s $n.mp3); }
gen pour 10 "A continuous heavy stream of gold coins pouring from a metal pipe, jingling cascade of coins, rich and loud, no music"
gen gulp 1.0 "One big greedy gulp swallowing, cartoonish but realistic throat gulp, close-up, no music"
gen tink 0.7 "A single small coin dropping and landing with one tiny lonely metallic tink, quiet room, no music"
gen pile 4 "Gold coins spilling and clattering onto a growing pile on a hard floor, lots of jingling, no music"
gen choke 1.5 "A greedy man choking and spluttering on too much food, muffled gasp and cough, comic but realistic, no words, no music"
gen typing 6 "Tired steady typing on a laptop keyboard in a quiet office at night, soft clicks, no music"
gen hum 6 "Low metallic hum and gurgle of liquid flowing through a big metal pipe, industrial, subtle, no music"
gen clunk 0.8 "A heavy metal valve wheel turning with a clunk, industrial pipe, close-up, no music"
