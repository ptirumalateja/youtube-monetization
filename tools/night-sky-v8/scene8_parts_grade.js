// ---------------------------------------------------------------- unified cinematic grade (teal shadows, warm highlights, vignette, grain)
{ const gp=new ShaderPass({uniforms:{tDiffuse:{value:null},uTime:{value:0}},vertexShader:`varying vec2 vUv; void main(){vUv=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
  fragmentShader:`uniform sampler2D tDiffuse; uniform float uTime; varying vec2 vUv; float hash(vec2 p){ return fract(sin(dot(p,vec2(12.9898,78.233)))*43758.5453); }
   void main(){ vec3 col=texture2D(tDiffuse,vUv).rgb; float l=dot(col,vec3(0.299,0.587,0.114)); col+=vec3(0.004,0.012,0.020)*(1.0-smoothstep(0.0,0.30,l));
    col*=mix(vec3(1.0),vec3(1.06,1.0,0.93),smoothstep(0.35,1.1,l)); vec2 q=vUv-0.5; col*=1.0-0.9*dot(q,q); col+=(hash(vUv*vec2(540.0,960.0)+fract(uTime)*37.0)-0.5)*0.012; gl_FragColor=vec4(col,1.0);} `}); comp.insertPass(gp,comp.passes.length-1); window.gradePass=gp; }
// (portals placed after camera path is defined)
const warpGlow=glowMesh([0.7,0.82,1.0],900,0.0,0,2.4); warpGlow.renderOrder=3;