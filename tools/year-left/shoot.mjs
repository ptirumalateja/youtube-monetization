// node shoot.mjs <outdir> [today] [t0] [t1] [fps] [step]
import { createRequire } from 'module'; const { chromium } = createRequire(import.meta.url)('playwright');
import fs from 'fs'; import path from 'path'; import url from 'url';
const [out, today = '2026-11-12', t0 = '0', t1 = '18', fps = '30', only] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const here = path.dirname(url.fileURLToPath(import.meta.url));
const b = await chromium.launch({ args: ['--disable-gpu-vsync'] });
const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
p.on('console', m => console.log('page:', m.text())); p.on('pageerror', e => console.log('ERR', e.message));
await p.goto('file://' + path.join(here, 'index.html') + '?today=' + today);
await p.waitForFunction('window.READY === true');
console.log(JSON.stringify(await p.evaluate('window.INFO')));
const times = only ? only.split(',').map(Number) : null;
const F = +fps, list = times || Array.from({ length: Math.round((+t1 - +t0) * F) }, (_, i) => +t0 + i / F);
for (let i = 0; i < list.length; i++) {
  const t = list[i];
  const data = await p.evaluate(t => { renderAt(t); return document.getElementById('c').toDataURL('image/png'); }, t);
  const name = times ? `t_${t.toFixed(2)}.png` : `f_${String(Math.round(t * F)).padStart(4, '0')}.png`;
  fs.writeFileSync(path.join(out, name), Buffer.from(data.split(',')[1], 'base64'));
}
await b.close();
