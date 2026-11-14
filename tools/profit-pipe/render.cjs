// node render.cjs stills            -> $OUT/still-*.jpg (TIMES=0.5,2.9)
// node render.cjs events            -> $OUT/events.json (sound cues)
// node render.cjs frames WORKER N   -> every Nth frame from WORKER into $OUT/frames/f00000.jpg
// env: W, H (default 1080x1920), SUB (motion-blur sub-frames, default 2), OUT (default ./output), FPS (30)
const { chromium } = require('playwright');
const fs = require('node:fs'), path = require('node:path');
const root = __dirname, out = process.env.OUT || path.join(root, 'output'); fs.mkdirSync(path.join(out, 'frames'), { recursive: true });
(async () => {
  const [mode, a1, a2] = process.argv.slice(2);
  const browser = await chromium.launch();
  try {
    const W = +(process.env.W || 1080), H = +(process.env.H || 1920), SUB = +(process.env.SUB || 2), FPS = +(process.env.FPS || 30);
    const page = await browser.newPage({ viewport: { width: 400, height: 400 } });
    page.on('pageerror', e => { console.error('[pageerror]', e.message); process.exitCode = 1; });
    page.on('console', m => console.error('[console]', m.text()));
    await page.goto('file://' + path.join(root, 'index.html') + `?w=${W}&h=${H}`);
    await page.waitForFunction(() => window.ready === true, null, { timeout: 60000 });
    const dur = await page.evaluate(() => window.DUR), total = Math.round(dur * FPS);
    const shot = async (t, file) => { const b64 = await page.evaluate(([t, k]) => window.renderAt(t, k), [t, SUB]); fs.writeFileSync(file, Buffer.from(b64.split(',')[1], 'base64')); };
    if (mode === 'stills') {
      for (const t of (process.env.TIMES || '0.3,1.2,2.6,3.9,4.8,6.5,7.3,9.9,11.2').split(',').map(Number)) await shot(t, path.join(out, `still-${t.toFixed(2).padStart(5, '0')}.jpg`));
    } else if (mode === 'events') {
      fs.writeFileSync(path.join(out, 'events.json'), JSON.stringify({ dur, tl: await page.evaluate(() => window.TL), events: await page.evaluate(() => window.events) }, null, 1));
    } else if (mode === 'frames') {
      const wk = +(a1 || 0), n = +(a2 || 1), t0 = Date.now();
      for (let f = wk; f < total; f += n) {
        const file = path.join(out, 'frames', `f${String(f).padStart(5, '0')}.jpg`);
        await shot(f / FPS, file + '.tmp'); fs.renameSync(file + '.tmp', file);
        if ((f - wk) % (n * 30) === 0) console.log(`w${wk} ${f}/${total} ${((Date.now() - t0) / 1000).toFixed(0)}s`);
      }
    }
  } finally { await browser.close(); }
})().catch(e => { console.error(e); process.exitCode = 1; });
