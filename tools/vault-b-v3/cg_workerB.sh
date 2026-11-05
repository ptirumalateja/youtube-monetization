cd /home/user/youtube-monetization/tools/vault-b
node render_anim.cjs hand /home/user/youtube-monetization/tools/vault-b-v3/cg/hand 130 24 '{"dp":[0,0,-0.35],"hand":[-0.75,0.0],"liveShadow":1,"ease":"lin"}'
node render_anim.cjs eyes /home/user/youtube-monetization/tools/vault-b-v3/cg/eyes 76 24 '{"dp":[0,0.1,-1.3],"eyes":[0.08,0.4],"ease":"in"}'
node render_anim.cjs lamp /home/user/youtube-monetization/tools/vault-b-v3/cg/lamp 90 24 '{"dp":[0.1,0,-0.7],"flick":0.18,"ease":"lin"}'
W=1620 H=2880 node render_anim.cjs gold /home/user/youtube-monetization/tools/vault-b-v3/cg/gold_wide 1 24 '{}'
W=1620 H=2880 node render_anim.cjs gold /home/user/youtube-monetization/tools/vault-b-v3/cg/gold_close 1 24 '{"dp":[0.5,-0.25,-1.3],"dl":[0.4,-0.2,0]}'
W=1620 H=2880 node render_anim.cjs gold /home/user/youtube-monetization/tools/vault-b-v3/cg/gold_low 1 24 '{"dp":[-0.8,-0.7,-0.3],"dl":[-0.6,-0.1,0],"dfov":6}'
echo WORKER_B_DONE
