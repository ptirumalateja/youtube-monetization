#!/bin/bash
# Regenerates the ElevenLabs foley used by mix.py. Needs ELEVENLABS_API_KEY; max 6 concurrent requests, so one at a time.
cd "$(dirname "$0")"
gen(){ n=$1; d=$2; p="$3"; for i in 1 2 3; do curl -sS -o $n.mp3 -X POST https://api.elevenlabs.io/v1/sound-generation -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" -d "{\"text\":\"$p\",\"duration_seconds\":$d,\"prompt_influence\":0.75}"; [ $(stat -c%s $n.mp3) -gt 2000 ] && break; sleep 4; done; }
gen hammer1 1.0 "One single sharp claw hammer strike driving a nail into a wooden plank, dry close-up foley, crisp wood knock, no reverb, no music"
gen hammer2 1.0 "One single hammer blow on a nail into a wooden beam, short dry thwack, close microphone, no echo, no music"
gen hammer3 1.0 "A single hammer hit on a nail into soft pine wood, solid thunk, close-up, dry, no music"
gen hammer4 1.0 "One quick hammer tap setting a nail head into wood, tight dry knock, close microphone, no music"
gen tape_out 1.6 "A metal tape measure being pulled out quickly with a ratcheting zipping sound, then a small click as it locks, close-up foley, no music"
gen tape_back 1.2 "A metal tape measure retracting fast with a zip and a snap as the case slams shut, close-up foley, no music"
gen sand 4.0 "Slow steady sanding of a piece of wood with fine sandpaper, rhythmic strokes, close-up foley, quiet room, no music"
gen plank_grab 0.8 "A wooden plank pulled out of a bundle of planks, a short wood scrape and clatter, dry close-up foley, no music"
gen step1 0.6 "A single soft footstep of a barefoot stick figure stepping up onto a wooden ladder rung, small dry wooden creak and tap, close-up, no music"
gen step2 0.6 "One boot stepping onto a wooden ladder rung, a short wooden tap with a tiny creak, close-up, dry, no music"
gen click 0.8 "A smooth wooden dowel sliding and clicking perfectly into place between two stone pillars, one satisfying precise wooden click, dry close-up, no music"
gen thud 1.0 "A person sitting down heavily on the ground, one soft low thud, then silence, close-up, no music"
gen light 4.0 "A warm swelling rush of bright light and air, a soft cinematic whoosh rising and opening up, no music, no voice"
