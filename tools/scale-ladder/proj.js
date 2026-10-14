const {chromium}=require('/tmp/claude-0/-home-user-youtube-monetization/43e84261-6c7e-57fc-924c-617953374ae4/scratchpad/spike/node_modules/playwright-core'); const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:180,height:320}}); await p.goto('http://localhost:8766/index.html?w=180&h=320'); await p.waitForFunction('window.ready===true&&window.earthReady===true');
const r=await p.evaluate(()=>{ const out=[]; const v=new window.THREE.Vector3(); const pts=[new window.THREE.Vector3(0,0,0),new window.THREE.Vector3(80,-20,0)]; 
 for(let f=0;f<780;f++){ const t=f/30; window.setT(t); window.cam.updateMatrixWorld(); const row=[]; pts.forEach(q=>{ v.copy(q).project(window.cam); row.push([(v.x*0.5+0.5),(1-(v.y*0.5+0.5))]); }); out.push(row);} return out;});
fs.writeFileSync('proj.json',JSON.stringify(r)); await b.close();})();
