// usage: node shot.js <outdir> [A B C]   (renders 1080x1920 PNG style frames)
const {chromium}=require('/opt/node-tools/node_modules/playwright-core');
const fs=require('fs'),path=require('path');
(async()=>{
  const out=process.argv[2]; const vs=process.argv.slice(3).length?process.argv.slice(3):['A','B','C'];
  fs.mkdirSync(out,{recursive:true});
  const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
  const p=await b.newPage({viewport:{width:1080,height:1920}});
  p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
  for(const v of vs){
    await p.goto('file://'+path.resolve(__dirname,'index.html')+'?v='+v);
    await p.waitForFunction('window.ready===true');
    await p.waitForTimeout(150);
    await p.screenshot({path:`${out}/style_${v}.png`});
    console.log('style',v);
  }
  await b.close();
})();
