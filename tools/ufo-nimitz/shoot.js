// usage: node shoot.js params.json outdir   (params.json = [{name, ...P}])
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{
 const shots=JSON.parse(fs.readFileSync(process.argv[2]));const out=process.argv[3];fs.mkdirSync(out,{recursive:true});
 const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
 const p=await b.newPage({viewport:{width:1920,height:1080}});
 p.on('console',m=>console.log('console',m.text()));p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('file://'+__dirname+'/recon.html?w=1920&h=1080');await p.waitForFunction('window.ready');
 for(const s of shots){const t0=Date.now();
  const d=await p.evaluate(P=>{draw(P);return grab();},s);
  fs.writeFileSync(out+'/'+s.name+'.jpg',Buffer.from(d.split(',')[1],'base64'));console.log(s.name,Date.now()-t0,'ms');}
 await b.close();})();
