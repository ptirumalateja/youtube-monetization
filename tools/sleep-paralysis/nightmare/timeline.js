// One continuous take. Every value is a pure function of time t (seconds).
export const SPEC={duration:20,fps:30,width:1080,height:1920};

// C1 Hermite through time-stamped keys (finite-difference tangents in time).
export function track(keys){
 return t=>{const n=keys.length;if(t<=keys[0][0])return keys[0][1];if(t>=keys[n-1][0])return keys[n-1][1];
  let i=0;while(t>keys[i+1][0])i++;const [t0,a]=keys[i],[t1,b]=keys[i+1],h=t1-t0,u=(t-t0)/h;
  const tan=(j)=>{if(keys[j][2]==='hold')return Array.isArray(keys[j][1])?keys[j][1].map(()=>0):0;const jp=Math.max(0,j-1),jn=Math.min(n-1,j+1);const dt=keys[jn][0]-keys[jp][0];
   const A=keys[jp][1],B=keys[jn][1];return Array.isArray(A)?A.map((v,k)=>(B[k]-v)/dt):(B-A)/dt;};
  const ma=tan(i),mb=tan(i+1);const h00=2*u*u*u-3*u*u+1,h10=u*u*u-2*u*u+u,h01=-2*u*u*u+3*u*u,h11=u*u*u-u*u;
  return Array.isArray(a)?a.map((v,k)=>h00*v+h10*h*ma[k]+h01*b[k]+h11*h*mb[k]):h00*a+h10*h*ma+h01*b+h11*h*mb;};
}

// Camera: [time, value]. Sleeper's head ~(-2.95,.84,-.62); wraith head ~(-2.0,2.4,-1.6).
export const camPos=track([
 [0,   [-1.25,0.95, 0.55]],
 [3.6, [-1.22,1.00, 0.75]],
 [5.4, [-1.40,1.08, 1.10]],          // deliberate acceleration out of the close-up
 [7.2, [-1.45,1.25, 2.50]],
 [9.4, [-1.50,1.35, 3.40]],          // wide: the whole room, the thing beside the bed
 [11.4,[-1.00,1.25, 2.80]],
 [13.6,[-0.90,1.05, 1.50]],          // creeping back in along the bed
 [15.3,[-1.40,0.95, 0.60]],
 [16.9,[-1.75,0.95, 0.35]],          // under its face, the hand above
 [18.6,[-1.45,0.92, 0.35]],
 [20,  [-1.25,0.95, 0.55]],
]);
export const camLook=track([
 [0,   [-2.27,1.44,-0.55]],
 [3.6, [-2.25,1.50,-0.62]],
 [5.4, [-2.40,1.70,-1.30]],
 [7.2, [-2.20,1.55,-1.30]],
 [9.4, [-2.10,1.45,-1.30]],
 [11.4,[-2.20,1.40,-1.00]],
 [13.6,[-2.60,1.30,-0.80]],
 [15.3,[-2.70,1.60,-0.90]],
 [16.9,[-2.80,1.75,-0.85]],
 [18.6,[-2.35,1.60,-0.75]],
 [20,  [-2.27,1.44,-0.55]],
]);
export const camFov=track([[0,64],[3.6,62],[7.2,54],[9.4,52],[13.6,52],[16.9,64],[18.6,64],[20,64]]);
// Wraith performance.
export const W={
 reach:track([[0,.08],[8.5,.1],[10,.25],[13.5,.95],[16.5,1.05],[18.4,1.0],[19.6,.3],[20,.08]]),
 open: track([[0,.15],[9.5,.15],[12.5,.95],[15.5,.85],[17,.55],[19.6,.2],[20,.15]]),
 claw: track([[0,0],[14.5,0],[16.8,.6],[18.5,.8],[20,0]]),
 lean: track([[0,0],[9,0],[14,.25],[17,.5],[18.6,.55],[20,0]]),
 headTilt:track([[0,0],[1,0],[3.5,.122],[9,.1],[13,.16],[17,.2],[20,0]]),   // .122 rad = 7 degrees
 headTurn:track([[0,.1],[4,.18],[9,.05],[14,.25],[17,.3],[20,.1]]),
 headDown:track([[0,0],[13,0],[16.5,.18],[20,0]]),
};
export const FX={
 attempt:track([[0,0],[10.6,0],[11.2,.9],[11.7,.2],[12.4,1],[12.9,.1],[13.6,.6],[14.2,0],[20,0]]),  // the covered arm tries to lift
 moon:track([[0,1],[9,1],[12,.72],[15,.6],[17.5,.85],[20,1]]),                                      // a slow cloud passes
 pulse:track([[0,.6],[9,.7],[13,1.3],[17,1.7],[19,1],[20,.6]]),
 eye:track([[0,0],[.55,0,'hold'],[.85,1.08],[1.1,1,'hold'],[19.5,1,'hold'],[19.9,0,'hold'],[20,0,'hold']]),
 ink:track([[0,.55],[.5,0],[18.4,0],[19.4,.6],[20,.55]]),                                             // the loop closes through ink
};
