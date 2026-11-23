# Hole-becomes-hill: LOCKED hero design (glossy white vinyl stickman)

Status: LOCKED. Change only with the user's explicit approval. All hole-and-hill reels use `tools/hole-hill/vinyl.py`.

Reference: the Meta AI glossy white vinyl stickman the user supplied.

- Proportions: LEN = thigh 215, shin 205, torso 200, uarm 148, farm 138. RAD = head 118, torso0 46, torso1 60, uarm 17, farm 16, hand 29, thigh 21, shin 18, foot 21.
- Head: big smooth sphere sunk into the torso. No neck.
- Hands: SDF fists (palm ellipsoid, 4 curled fingers, thumb), as in the reference. Do not simplify to balls.
- Face: black ball eyes with a white highlight, thick brow lines, simple mouth. No hearts, no pink.
- Shading: glossy white-gray (Lambert, sky ambient, AO, Blinn specular), soft contact shadow, light grey backdrop.
- Moods: neutral, determined, shocked, strain, joy. Poses: guard, dig, fall, stand, triumph.
- Render at `V.RES["k"] = 1` for final frames (about 7 s per frame); k=2 for previews.
- Thick lines and expressive faces always.
