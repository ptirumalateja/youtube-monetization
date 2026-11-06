# Paper fold 103 (look test)

Three still plates for the "Fold your notebook page 103 times" reel, rendered with Three.js in headless Chromium, plus a PIL HUD pass.

    cd tools/paper-fold && npm i && python3 -m http.server 8771 &
    node shoot.js 1080 1920 out desk unity moon
    python3 hud.py out/moon.png out/C.jpg 42 "440,000 km" "42 folds: past the Moon." "THE MOON" "384,400 km away" 760 870 down

Textures in tex/ are the three.js r160 example planet maps (clouds_a.png is the alpha channel of earth_clouds_1024.png).
Milestones use a 0.1 mm sheet: thickness = 0.1 mm x 2^folds.
