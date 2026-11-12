// Renders the brand assets from brand.html to PNG.
const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const out = path.resolve(__dirname, '..');
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 2700, height: 3200 }, deviceScaleFactor: 1 });
  await page.goto('file://' + path.join(__dirname, 'brand.html'));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(800);
  await (await page.$('#avatar')).screenshot({ path: path.join(out, 'profile_picture_800x800.png') });
  await (await page.$('#banner')).screenshot({ path: path.join(out, 'banner_2560x1440.png') });
  await page.evaluate(() => { document.body.style.background = 'transparent'; });
  await (await page.$('#wm')).screenshot({ path: path.join(out, 'watermark_600.png'), omitBackground: true });
  await browser.close();
})();
