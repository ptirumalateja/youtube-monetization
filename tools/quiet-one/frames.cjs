// node frames.cjs  -> $OUT/frames/f00000.jpg ... (env W, H, FPS, TIMES=comma list renders only those times as still-*.jpg)
const { chromium } = require(process.env.PW || 'playwright');
const fs = require('node:fs'), path = require('node:path'), http = require('node:http');
const root = __dirname, out = process.env.OUT || path.join(root, 'output/anim'); fs.mkdirSync(path.join(out, 'frames'), { recursive: true });
const server = http.createServer((req, res) => { const u = req.url.split('?')[0]; const file = path.resolve(root, '.' + decodeURIComponent(u === '/' ? '/index.html' : u));
  fs.readFile(file, (e, d) => { if (e) res.writeHead(404).end(); else { res.setHeader('Content-Type', file.endsWith('.js') ? 'text/javascript' : 'text/html'); res.end(d); } }); });
(async () => { await new Promise(r => server.listen(0, '127.0.0.1', r));
  const browser = await chromium.launch({ headless: true });
  try { const W = +process.env.W || 1080, H = +process.env.H || 1920, FPS = +process.env.FPS || 30;
    const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
    page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; });
    await page.goto(`http://127.0.0.1:${server.address().port}/?w=${W}&h=${H}`); await page.waitForFunction(() => window.ready === true);
    const shot = async (t, file) => { const b64 = await page.evaluate(t => window.renderAt(t), t); fs.writeFileSync(file, Buffer.from(b64.split(',')[1], 'base64')); };
    if (process.env.TIMES) { for (const t of process.env.TIMES.split(',').map(Number)) await shot(t, path.join(out, `still-${t.toFixed(2)}.jpg`)); }
    else { const n = Math.round(await page.evaluate(() => window.DUR) * FPS); for (let f = 0; f < n; f++) await shot(f / FPS, path.join(out, 'frames', `f${String(f).padStart(5, '0')}.jpg`)); console.log('frames', n); }
  } finally { await browser.close(); server.close(); } })();
