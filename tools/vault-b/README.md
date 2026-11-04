# Vault B: key stills

This renders the key stills for "The Door", the Padmanabhaswamy Vault B reel. Treatment: /mnt/project-files/concepts/vault-b-treatment.md

- `scene.js`: the Three.js r170 scenes (gold, door, tower, vaults, lamp, macro, hand, eyes). They are procedural: coins, crowns, chains, nilavilakku lamps, the cobra door and the gopuram.
- `render.cjs`: headless Chromium with swiftshader. Example: `OUT=output/full W=1080 H=1920 node render.cjs gold,door`. The whole set takes about 1 min at 1080x1920.
- `overlay.py`: adds the engraved-gold PADMANABHASWAMY tag and the beat lines. Example: `python3 overlay.py output/full output/stills`. Fonts are Cinzel/Anton (OFL) in fonts/.

Render at 1x. Bump detail washes out at 2x supersample.
Setup: `npm i` in this folder.
