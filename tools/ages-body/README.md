# ages-body: one 3D person, ages 1 to 100 (test stills)

Own figure for the "Ages 1 to 100" long-form concept (see project file `concepts/mrbeast-topic-remakes.md`).

- Source mesh and age targets: MakeHuman base mesh + macro targets, released CC0 in Sept 2020 (makehumancommunity/makehuman). Run `./fetch_mh.sh` to download them into `mh_src/` (git-ignored).
- `python3 build_body.py <gender 0..1> <ages...>` blends race/gender/age targets (MakeHuman's own age curve: 1 / 11 / 25 / 90 years) and writes `out/body_<age>.bin` + joint positions. Metres, feet on y=0.
- `index.html` (three.js) renders `?mode=skin|xray|wire|nerve&age=N`. Serve this folder with `python3 -m http.server 8777`, then `node shot.js shots 1080 1920 name:mode:age ...` (needs `npm i`).
- Skin mode: dark-warm look (one ~3000K spot, navy ambient, charcoal background), bald-to-hair cap, shorts band, simple eyes.

Known gaps: MakeHuman only goes to 90 years, so ages above 90 clamp; no wrinkles or posture change yet (age 80 reads old mostly via colour and hair); skin face is mannequin-grade; x-ray organs are procedural (brain shows as a ring); shorts edge is jagged from vertex colours.
