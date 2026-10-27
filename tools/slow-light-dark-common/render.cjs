// node render.cjs stills   TIMES=0.5,3 -> $OUT/still-*.jpg      (env W, H, SUB, OUT; page = PAGE or index.html)
// node render.cjs frames WORKER N DURATION FPS -> $OUT/frames/f00000.jpg (every Nth frame from WORKER)
const { chromium } = require(process.env.PW || 'playwright');
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const root = __dirname, out = process.env.OUT || path.join(root, 'output'); fs.mkdirSync(path.join(out, 'frames'), { recursive: true });
const mime = { '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json' };
const server = http.createServer((req, res) => {
  const u = req.url.split('?')[0]; const file = path.resolve(root, '.' + decodeURIComponent(u === '/' ? '/' + (process.env.PAGE || 'index.html') : u));
  if (!file.startsWith(root + path.sep)) { res.writeHead(403).end(); return; }
  fs.readFile(file, (e, d) => { if (e) res.writeHead(404).end(); else { res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream'); res.end(d); } });
});
(async () => {
  const [mode, a1, a2, a3, a4] = process.argv.slice(2);
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch({ headless: true, args: ['--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  try {
    const W = Number(process.env.W || 1080), H = Number(process.env.H || 1920), SUB = Number(process.env.SUB || 3);
    const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
    page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; });
    page.on('console', m => { if (m.type() === 'error' || m.type() === 'warning') console.error('[console]', m.text()); });
    await page.goto(`http://127.0.0.1:${server.address().port}/?w=${W}&h=${H}`);
    await page.waitForFunction(() => window.ready === true, null, { timeout: 180000 });
    const shot = async (t, file) => { const b64 = await page.evaluate(([t, k]) => window.renderAt(t, k), [t, SUB]); fs.writeFileSync(file, Buffer.from(b64.split(',')[1], 'base64')); };
    if (mode === 'stills') {
      for (const t of (process.env.TIMES || '0').split(',').map(Number)) { await shot(t, path.join(out, `still-${t.toFixed(2).padStart(5, '0')}.jpg`)); console.log('still', t); }
    } else if (mode === 'frames') {
      const wk = Number(a1 || 0), n = Number(a2 || 1), fps = Number(a4 || 30), total = Math.round(Number(a3) * fps);
      for (let f = wk; f < total; f += n) { const file = path.join(out, 'frames', `f${String(f).padStart(5, '0')}.jpg`); if (fs.existsSync(file) && !process.env.FORCE) continue;
        await shot(f / fps, file + '.tmp'); fs.renameSync(file + '.tmp', file); }
    }
  } finally { await browser.close(); server.close(); }
})().catch(e => { console.error(e); server.close(); process.exitCode = 1; });
