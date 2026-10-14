const {chromium}=require('/tmp/claude-0/-home-user-youtube-monetization/43e84261-6c7e-57fc-924c-617953374ae4/scratchpad/spike/node_modules/playwright-core'); const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:120,height:200}}); await p.goto('http://localhost:8767/index.html?w=120&h=200'); await p.waitForFunction('window.ready===true',{timeout:120000});
const r=await p.evaluate(()=>{ const zs=[]; window.scene.children.forEach(c=>{}); const out={rings:[],ripples:[3.3,5.2,7.1,10.9]}; const rz=[[-14,'moon'],[-22,'moon'],[-30,'moon'],[-38,'moon'],[-100,'sun'],[-125,'sun'],[-150,'sun'],[-175,'sun'],[-450,'prox'],[-530,'prox'],[-610,'prox'],[-690,'prox'],[-770,'prox']]; for(let i=0;i<23;i++) rz.push([-1500-500*i,'hyper']);
 for(const [z,g] of rz){ let tc=null; for(let t=2.1;t<12.0;t+=0.002){ if(window.camPos(t).z<=z){ tc=t; break; } } out.rings.push([z,g,tc]); }
 // object closest approach / hold times
 return out; });
fs.writeFileSync('ring_times.json',JSON.stringify(r)); await b.close();})();
