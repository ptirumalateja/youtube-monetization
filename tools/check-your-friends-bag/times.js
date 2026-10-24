// node times.js port out.json -> the timeline (placements, step passes, X-ray, bridge) for the overlay and the mix
const fs=require('fs');const {open}=require('./browser.js');
(async()=>{const [port,out]=process.argv.slice(2);const {b,p}=await open(108,192,port);
const r=await p.evaluate(()=>({...window.TL,dur:window.DUR}));fs.writeFileSync(out,JSON.stringify(r,null,1));await b.close();})();
