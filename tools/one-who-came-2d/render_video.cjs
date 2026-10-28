// Frames for the One Came reel: node render_video.cjs  (env FPS, DUR, F0, F1, OUT, W, H; or STILLS=1 for the named stills)
const { chromium } = require(process.env.PW || 'playwright');
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const root = __dirname, out = process.env.OUT || path.join(root, 'output', 'frames'); fs.mkdirSync(out, { recursive: true });
const mime = { '.html': 'text/html', '.js': 'text/javascript' };
const server = http.createServer((req, res) => { const u = req.url.split('?')[0]; const file = path.resolve(root, '.' + decodeURIComponent(u === '/' ? '/index.html' : u));
  fs.readFile(file, (e, d) => { if (e) res.writeHead(404).end(); else { res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream'); res.end(d); } }); });
(async () => {
  await new Promise(r => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch({ headless: true });
  try { const W = +process.env.W || 1080, H = +process.env.H || 1920, FPS = +process.env.FPS || 30, DUR = +process.env.DUR || 20;
    const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
    page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exit(1); });
    await page.goto(`http://127.0.0.1:${server.address().port}/?w=${W}&h=${H}`);
    await page.waitForFunction(() => window.ready === true);
    const jobs = process.env.TIMES ? process.env.TIMES.split(',').map(s => { const [n, t] = s.split(':'); return [n, +t]; })
      : Array.from({ length: (+process.env.F1 || FPS * DUR) - (+process.env.F0 || 0) }, (_, i) => { const f = i + (+process.env.F0 || 0); return [String(f).padStart(5, '0'), f / FPS]; });
    const t0 = Date.now();
    for (const [name, t] of jobs) { const b64 = await page.evaluate(t => window.renderAt(t), t); fs.writeFileSync(path.join(out, `${name}.jpg`), Buffer.from(b64.split(',')[1], 'base64')); }
    console.log(jobs.length, 'frames', Date.now() - t0, 'ms');
  } finally { await browser.close(); server.close(); } })().catch(e => { console.error(e); server.close(); process.exitCode = 1; });
