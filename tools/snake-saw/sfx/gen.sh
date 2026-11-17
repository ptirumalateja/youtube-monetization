#!/bin/bash
# ElevenLabs foley for mix.py (swipe, thud, marker, boom, ding, clock copied from hall-of-mirrors). Needs ELEVENLABS_API_KEY.
cd "$(dirname "$0")"
gen(){ n=$1; d=$2; p="$3"; [ -s $n.mp3 ] && [ -z "$FORCE" ] && return; for i in 1 2 3; do curl -sS -o $n.mp3 -X POST https://api.elevenlabs.io/v1/sound-generation -H "xi-api-key: $ELEVENLABS_API_KEY" -H "Content-Type: application/json" -d "{\"text\":\"$p\",\"duration_seconds\":$d,\"prompt_influence\":0.7}"; [ $(stat -c%s $n.mp3) -gt 2000 ] && break; sleep 4; done; echo $n $(stat -c%s $n.mp3); }
gen slither 1.2 "A snake slithering over a dusty wooden floor, soft scaly rustle, no music" &
gen hiss 1.2 "An angry snake hissing loudly, close-up, no music" &
gen clang 0.8 "A snake striking a metal hand saw blade, short metallic clang and twang, no music" &
gen scrape 1.2 "Skin dragging across sharp saw teeth, a short gritty metal scrape, no music" &
gen drip 1.0 "A few thick drops dripping onto a wooden floor, soft, no music" &
gen creak 1.4 "A tight creaking squeeze, rope tightening around metal, strain, no music" &
wait
gen heart 2.0 "A slow heartbeat that slows down and stops, soft, no music" &
gen tick 0.8 "A quick mechanical counter ticking up fast, short, no music" &
gen wind 2.0 "Soft wind over an open grassland plain, gentle, no music" &
gen flap 1.0 "A small bat flapping its leathery wings quickly as it flies past, no music" &
gen nip 0.5 "A tiny quick bite nip, very short, no music" &
gen neigh 1.6 "A wild horse neighing in panic and rearing up, no music" &
wait
gen gallop 3.0 "A horse galloping fast across hard ground, hooves pounding, no music" &
gen crack 0.9 "A short sharp crack like a heart breaking, glass-like crack, no music" &
gen typing 0.8 "Furious fast typing on a phone screen, rapid taps, no music" &
gen drain 0.9 "A short descending power-down tone, battery draining, no music" &
gen room 8 "Quiet empty wooden workshop room tone, faint air, very soft, no music" &
wait
