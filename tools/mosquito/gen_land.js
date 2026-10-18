// Fibonacci-lattice Earth: tags each lattice point land/ocean from Natural Earth 1:110m land (public domain).
// usage: node gen_land.js <node_modules dir> > land.json
const nm=process.argv[2]; const fs=require('fs');
const {feature}=require(nm+'/topojson-client'); const {geoContains}=require(nm+'/d3-geo');
const topo=JSON.parse(fs.readFileSync(nm+'/world-atlas/land-110m.json')); const land=feature(topo,topo.objects.land);
const N=36000, out=[]; const ga=Math.PI*(3-Math.sqrt(5));
for(let i=0;i<N;i++){const y=1-2*(i+0.5)/N, lat=Math.asin(y)*180/Math.PI, lon=(((ga*i)*180/Math.PI+180)%360+360)%360-180;
  const L=geoContains(land,[lon,lat]); if(L||i%3===0) out.push([Math.round(lat*100),Math.round(lon*100),L?1:0]);}
console.log(JSON.stringify(out));
