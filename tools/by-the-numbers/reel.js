// GTA 6 by the numbers, v3 (latest stats as of 21 Nov 2026). Every figure is sourced in SOURCES.md.
const B=v=>'$'+v.toFixed(2)+'B', B1=v=>'$'+v.toFixed(1)+'B', M2=v=>v.toFixed(2)+'M', I=v=>String(Math.round(v));
const P=v=>'+'+Math.round(v)+'%', GB=v=>Math.round(v)+' GB';
window.REEL={
  header:'GTA 6  •  BY THE NUMBERS',
  scenes:[
    {type:'stat',dur:3.4,instant:true,tag:'#1  DAY ONE',col:'#ffd23f',from:3.2,to:3.79,fmt:B,
     cap:['IN SALES. IN ONE DAY.'],chip:'Biggest entertainment launch ever'},
    {type:'stat',dur:3.0,tag:'#2  CRITICS',col:'#3ff0ff',from:60,to:99,fmt:I,
     cap:['METACRITIC SCORE','TIES THE ALL-TIME RECORD'],chip:'~150 reviews. Not one negative.'},
    {type:'vs',dur:3.8,tag:'#3  5 vs 6',col:'#ff5fc0',title:'DAY ONE: GTA 5 vs GTA 6',fmt:B,
     a:{label:'GTA 5 (2013)',v:0.8,sub:'first-day sales'},
     b:{label:'GTA 6 (2026)',v:3.79,sub:'first-day sales'},chip:'Nearly 5x bigger'},
    {type:'stat',dur:3.0,tag:'#4  LIVE',col:'#3ff0ff',from:5,to:7.91,fmt:M2,
     cap:['PEOPLE WATCHING STREAMS','AT THE SAME TIME'],chip:'4.5x the old record'},
    {type:'stat',dur:3.0,tag:'#5  INDIA',col:'#ffd23f',from:10,to:60,fmt:P,
     cap:['JUMP IN INDIANS TAKING LEAVE','ON LAUNCH DAY'],chip:'Worldwide: +32%'},
    {type:'stat',dur:3.0,tag:'#6  DOWNLOAD',col:'#ff5fc0',from:90,to:212,fmt:GB,
     cap:['DOWNLOAD SIZE','BEFORE YOU CAN EVEN PLAY'],chip:'≈ 45 DVDs worth of data'},
    {type:'stat',dur:3.2,tag:'#7  BUDGET',col:'#ffd23f',from:0.8,to:1.5,fmt:B1,
     cap:['REPORTED COST TO MAKE IT','13 YEARS IN THE MAKING'],chip:'≈ ₹13,000 crore'},
    {type:'cta',dur:3.4,lines:['WHICH NUMBER','SHOCKED YOU?'],sub:'Drop it in the comments',btn:'FOLLOW FOR MORE'}
  ]
};
