// Dumps Natural Earth land (public domain, via the world-atlas npm package) as lon/lat rings for make_earth.py.
// node land_rings.js <world-atlas dir> <topojson-client.js> > land_rings.json
const fs=require('fs'); const topo=require(process.argv[3]);
const t=JSON.parse(fs.readFileSync(process.argv[2]+'/land-50m.json'));
const g=topo.feature(t,t.objects.land); const rings=[];
for(const f of (g.features||[g])){ const geo=f.geometry; const polys=geo.type==='Polygon'?[geo.coordinates]:geo.coordinates; for(const p of polys) rings.push(p); }
process.stdout.write(JSON.stringify(rings));
