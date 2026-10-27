// node render_recon.js frames.jsonl out.mp4  -- renders recon.html frames, pipes JPEGs into ffmpeg
const {chromium}=require('playwright');const fs=require('fs');const {spawn}=require('child_process');
(async()=>{
 const lines=fs.readFileSync(process.argv[2],'utf8').trim().split('\n').map(JSON.parse);
 const ff=spawn('ffmpeg',['-v','error','-y','-f','image2pipe','-framerate','30','-c:v','mjpeg','-i','-','-c:v','libx264','-preset','medium','-crf','14','-pix_fmt','yuv420p',process.argv[3]],{stdio:['pipe','inherit','inherit']});
 const b=await chromium.launch({args:['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
 const p=await b.newPage({viewport:{width:1920,height:1080}});
 p.on('pageerror',e=>console.log('ERR',e.message));
 await p.goto('file://'+__dirname+'/recon.html?w=1920&h=1080');await p.waitForFunction('window.ready');
 const t0=Date.now();
 for(let i=0;i<lines.length;i++){
  const d=await p.evaluate(P=>{draw(P);return grab();},lines[i]);
  const buf=Buffer.from(d.split(',')[1],'base64');
  if(!ff.stdin.write(buf)) await new Promise(r=>ff.stdin.once('drain',r));
  if(i%60==0) console.log(process.argv[3],i,'/',lines.length,((Date.now()-t0)/1000).toFixed(0)+'s');
 }
 ff.stdin.end(); await new Promise(r=>ff.on('close',r)); await b.close();
})();
