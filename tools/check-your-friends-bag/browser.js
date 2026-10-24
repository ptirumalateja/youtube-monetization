// shared headless Chromium launcher (SwiftShader). CHROME env overrides the path.
const {chromium}=require('playwright-core');
const fs=require('fs');
const CANDIDATES=[process.env.CHROME,'/opt/pw-browsers/chromium-1243/chrome-linux64/chrome','/opt/pw-browsers/chromium-1194/chrome-linux/chrome'].filter(Boolean);
const exe=CANDIDATES.find(p=>fs.existsSync(p));
module.exports.open=async(W,H,port)=>{
  const b=await chromium.launch({executablePath:exe,args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
  const p=await b.newPage({viewport:{width:+W,height:+H}});
  p.on('pageerror',e=>console.log('[err]',e.message));p.on('console',m=>{if(m.type()==='error')console.log('[console]',m.text())});
  await p.goto(`http://localhost:${port}/index.html?w=${W}&h=${H}`);await p.waitForFunction('window.ready===true',{timeout:180000});
  return {b,p};
};
