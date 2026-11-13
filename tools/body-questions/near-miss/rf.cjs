// node rf.cjs OUTDIR t0 t1 fps worker nworkers   OR  node rf.cjs OUTDIR --times 0.2,1.0,...
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const a=process.argv.slice(2);const out=a[0];fs.mkdirSync(out,{recursive:true});
let list=[];if(a[1]=='--times')list=a[2].split(',').map(Number).map((t,i)=>[t,`t${t.toFixed(2)}`]);
else{const [t0,t1,fps,w,nw]=a.slice(1).map(Number);for(let f=Math.round(t0*fps);f<Math.round(t1*fps);f++)if(f%nw==w)list.push([f/fps,String(f).padStart(4,'0')])}
list=list.filter(([t,n])=>!fs.existsSync(`${out}/${n}.jpg`));
const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader']});const p=await b.newPage({viewport:{width:1080,height:1920}});
p.on('pageerror',e=>{console.log('ERR',e.message);process.exit(1)});p.on('console',m=>{const s=m.text();if(!s.includes('GL Driver')&&!s.includes('GPU stall'))console.log(s)});
await p.goto('http://localhost:8765/film.html');await p.waitForFunction('window.DONE',null,{timeout:600000});
for(const [t,n] of list){const t0=Date.now();const d=await p.evaluate(t=>window.renderFrame(t),t);fs.writeFileSync(`${out}/${n}.jpg`,Buffer.from(d.split(',')[1],'base64'));if(a[1]=='--times')console.log(n,Date.now()-t0,'ms')}
await b.close()})();
