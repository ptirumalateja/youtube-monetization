const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const pg = await b.newPage();
  await pg.goto('file:///home/user/youtube-monetization/tools/cant-inspire-change/scene.html');
  await pg.waitForFunction(() => window.READY === true);
  const r = await pg.evaluate(() => { const T = window.TIMES; return { dur: window.DURATION, slamHook: T.SLAM - T.HOOK_TAU0, slam: window.v(T.SLAM),
    knocks: [5.33, 5.69].map(window.v), lit: T.chars.filter(c => isFinite(c.litAt) && c.litAt > -1e9).map(c => [c.i, +window.v(c.litAt).toFixed(2)]),
    pours: T.pours.map(p => [p.f, p.to, +window.v(p.s0).toFixed(2), +window.v(p.s1).toFixed(2), !!p.refused]), cta: window.v(13.0), cta2: window.v(13.7), twist: [window.v(6.2), window.v(7.2)], sigh: window.v(8.35) }; });
  console.log(JSON.stringify(r)); await b.close();
})();
