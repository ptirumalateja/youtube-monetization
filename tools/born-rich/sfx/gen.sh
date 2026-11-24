#!/bin/bash
# Regenerates the ElevenLabs sound effects used by mix.py (POST /v1/sound-generation). Needs an ElevenLabs key:
# ELEVENLABS_API_KEY, or a key injected by the session's network proxy (then any placeholder value works). One request at a time.
cd "$(dirname "$0")"
KEY="${ELEVENLABS_API_KEY:-proxy-injected}"
gen(){ n=$1; d=$2; p="$3"; [ -s $n.mp3 ] && [ -z "$FORCE" ] && return; for i in 1 2 3; do curl -sS -o $n.mp3 -X POST https://api.elevenlabs.io/v1/sound-generation -H "xi-api-key: $KEY" -H "Content-Type: application/json" -d "{\"text\":\"$p\",\"duration_seconds\":$d,\"prompt_influence\":0.7}"; [ $(stat -c%s $n.mp3) -gt 2000 ] && break; sleep 4; done; echo "$n $(stat -c%s $n.mp3)"; }
gen lamp_on 1.2 "A heavy stadium floodlight switching on, one deep electric clunk then a low hum, no music"
gen start 1.2 "Three runners exploding off a starting line at once, sharp scuffs of shoes on gritty dirt, no music"
gen sprint 3.5 "One sprinter running very fast on a gritty dirt track, rapid hard footsteps, close, no music"
gen jog 7.0 "Two runners jogging steadily on a gritty dirt track, even footsteps rhythm, close, no music"
gen pant 2.6 "An exhausted man bent over, panting heavily and gasping for breath, no music"
gen cheer 1.4 "A cocky man letting out a short triumphant whoop while running, dry, no words, no music"
gen engine 3.0 "A supercar approaching from far away at very high speed, rising engine roar and turbo whistle, then blasting past close, no music"
gen nitro 1.2 "A nitro boost firing from a race car exhaust, a sharp whoosh and a pop of flame, no music"
gen skid 1.6 "Car tyres screeching to a hard sudden stop on asphalt, short skid, no music"
gen tape 0.8 "A finish line ribbon tape snapping and whipping in the air, close, no music"
gen idle 4.5 "A powerful sports car engine idling low and steady after stopping, deep rumble, no music"
gen boom 3.0 "A single deep cinematic low boom hit with a long dark tail, no music"
gen surge 1.6 "A runner suddenly kicking into a much faster sprint, a rising rush of air and quickening hard footsteps, no music"
gen pack 7.0 "Two runners sprinting hard side by side on a gritty dirt track, fast heavy footsteps and breathing, close, no music"
