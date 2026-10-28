# One of these Simpsons predictions is fake: look stills (28 Oct 2026)
Character-free (no Simpsons footage, characters or yellow). Six 1080x1920 look stills in the dark-warm grade: room (hook), tiger, gate, president, chalk, shelf (close).
`npm i`, then `OUT=output/full SUB=1 SHOTS=room,tiger,gate,president,chalk,shelf node render.cjs`, then `python3 overlay.py output/full output/text`. About 40 s total on 4 CPUs.
Built on the Slow Light Dark kit (sld.js, copied from tools/salary-dark-warm).
