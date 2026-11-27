// Usage: node render.js out.mp4 [fps] [t0] [t1]   |  node render.js --stills dir t1,t2,...
const { chromium } = require('playwright');
const http = require('http'), fs = require('fs'), path = require('path');
const { spawn } = require('child_process');
const dir = __dirname;
const srv = http.createServer((q, r) => {
  const f = path.join(dir, decodeURIComponent(q.url.split('?')[0]));
  fs.readFile(f, (e, d) => { if (e) { r.writeHead(404); r.end(); return; }
    r.writeHead(200, { 'Content-Type': f.endsWith('.html') ? 'text/html' : f.endsWith('.js') ? 'text/javascript' : f.endsWith('.ttf') ? 'font/ttf' : 'application/octet-stream' }); r.end(d); });
}).listen(0);
(async () => {
  const port = srv.address().port;
  const b = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  await p.goto(`http://127.0.0.1:${port}/${process.env.SCENE || 'scene.html'}`);
  await p.evaluate(() => window.ready);
  const grab = async t => {
    const u = await p.evaluate(t => { renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', 0.95); }, t);
    return Buffer.from(u.split(',')[1], 'base64');
  };
  if (process.argv[2] === '--stills') {
    const od = process.argv[3]; fs.mkdirSync(od, { recursive: true });
    for (const t of process.argv[4].split(',').map(Number)) fs.writeFileSync(`${od}/s_${t.toFixed(2)}.jpg`, await grab(t));
  } else {
    const out = process.argv[2], fps = +(process.argv[3] || 30), t0 = +(process.argv[4] || 0), t1 = +(process.argv[5] || 13.93);
    const ff = spawn('ffmpeg', ['-y', '-v', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-i', '-', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'medium', out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const n = Math.round((t1 - t0) * fps);
    for (let i = 0; i < n; i++) { const buf = await grab(t0 + i / fps); if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r)); if (i % 60 === 0) console.log('frame', i, '/', n); }
    ff.stdin.end(); await new Promise(r => ff.on('close', r));
  }
  await b.close(); srv.close();
})();
