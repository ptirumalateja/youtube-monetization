// Downloads the Earth textures into tex/. Both are NASA imagery (public domain), via the three-globe example mirror:
// earth-blue-marble.jpg = NASA Blue Marble (Visible Earth), earth-night.jpg = NASA Black Marble city lights,
// earth-water.png = ocean mask derived from the same. Clouds are generated locally by make_clouds.py.
import fs from 'node:fs';
const base = 'https://raw.githubusercontent.com/vasturiano/three-globe/master/example/img/';
fs.mkdirSync(new URL('./tex/', import.meta.url), { recursive: true });
for (const f of ['earth-blue-marble.jpg', 'earth-night.jpg', 'earth-water.png']) {
  const r = await fetch(base + f); if (!r.ok) throw Error(`${f}: ${r.status}`);
  fs.writeFileSync(new URL('./tex/' + f, import.meta.url), Buffer.from(await r.arrayBuffer())); console.log('tex/' + f);
}
