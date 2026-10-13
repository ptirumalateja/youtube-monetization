const {chromium}=require('playwright-core'); const fs=require('fs');
(async()=>{
 const W=+process.argv[2]||540,H=+process.argv[3]||960,T0=+process.argv[4]||0,T1=+process.argv[5]||5,FPS=30,out=process.argv[6]||'frames';
 fs.mkdirSync(out,{recursive:true});
 const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
 const p=await b.newPage({viewport:{width:W,height:H}}); p.on('console',m=>console.log('[page]',m.text())); p.on('pageerror',e=>console.log('[err]',e.message));
 await p.goto(`http://localhost:8765/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:60000});
 const n=Math.round((T1-T0)*FPS); const t0=Date.now();
 for(let i=0;i<n;i++){const t=T0+i/FPS; const d=await p.evaluate(t=>window.renderAt(t),t); fs.writeFileSync(`${out}/f${String(i).padStart(4,'0')}.jpg`,Buffer.from(d.split(',')[1],'base64')); if(i%15==0)console.log('frame',i,'/',n,((Date.now()-t0)/1000).toFixed(1)+'s');}
 console.log('done',((Date.now()-t0)/1000).toFixed(1)+'s'); await b.close();
})();
