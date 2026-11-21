// GTA 6 by the numbers, v1. Every figure is sourced in SOURCES.md next to this file.
const B=v=>'$'+v.toFixed(2)+'B', M1=v=>v.toFixed(1)+'M', M0=v=>Math.round(v)+'M', BN=v=>Math.round(v)+'B';
const USD=v=>'$'+Math.round(v).toLocaleString('en-US');
window.REEL={
  header:'GTA 6  •  BY THE NUMBERS',
  hookTop:'',
  scenes:[
    {type:'stat',dur:3.4,instant:true,tag:'#1  DAY ONE',col:'#ffd23f',from:3.2,to:3.79,fmt:B,
     cap:['IN SALES. IN ONE DAY.'],chip:'Biggest entertainment launch ever'},
    {type:'stat',dur:3.0,tag:'#2  COPIES',col:'#3ff0ff',from:20,to:32.5,fmt:M1,
     cap:['COPIES SOLD ON DAY ONE'],chip:'≈ 376 every single second'},
    {type:'stat',dur:3.0,tag:'#3  LIVE',col:'#ff5fc0',from:4,to:7.8,fmt:M1,
     cap:['PEOPLE WATCHING STREAMS','AT THE SAME TIME'],chip:'Old record: 1.74M'},
    {type:'vs',dur:3.8,tag:'#4  VS HOLLYWOOD',col:'#ffd23f',title:'ONE DAY vs ONE SUMMER',fmt:B,
     a:{label:'Spider-Man: Brand New Day',v:2.5,sub:'whole box office run'},
     b:{label:'GTA 6',v:3.79,sub:'in just 24 hours'},chip:'A game just beat a blockbuster'},
    {type:'stat',dur:3.0,tag:'#5  TRAILER',col:'#3ff0ff',from:300,to:475,fmt:M0,
     cap:['TRAILER 2 VIEWS','IN 24 HOURS'],chip:'Biggest video debut ever'},
    {type:'stat',dur:3.0,tag:'#6  YOUTUBE',col:'#ff5fc0',from:25,to:40,fmt:BN,
     cap:['VIEWS ON GTA 6 VIDEOS','BEFORE IT EVEN CAME OUT'],chip:'≈ 5 for every human alive'},
    {type:'stat',dur:3.2,tag:'#7  DREAM JOB',col:'#ffd23f',from:90000,to:120000,fmt:USD,
     cap:['SALARY TO PLAY GTA 6','FOR A YEAR'],chip:'≈ ₹1 crore. To play a game.'},
    {type:'cta',dur:3.4,lines:['WHICH NUMBER','SHOCKED YOU?'],sub:'Drop it in the comments',btn:'FOLLOW FOR MORE'}
  ]
};
