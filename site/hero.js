// SPDX-License-Identifier: GPL-3.0-only
// Decorative camera only: never changes firmware selection or requests MIDI.
const stage=document.querySelector('.hardware-showcase');
const layers=Object.fromEntries([...stage.querySelectorAll('[data-hardware]')].map(el=>[el.dataset.hardware,el]));
const fm1=[['purple','Purple'],['orange','Orange'],['mint','Graphite / mint'],['blue','Ivory / blue'],['red','Ivory / red'],['cream','Cream / charcoal'],['black','Black']];
const smk=[['red','Pro / Red'],['white','Pro / White'],['elite','Elite / Slate & orange'],['black','Pro / All black'],['pink','Pro / Pink'],['charcoal','Pro / Charcoal']];
const cameras={fm1:{wide:[0,-105,640,640],close:[185,76,133,133]},smk:{wide:[0,-255,960,960],close:[125,64,96,96]}};
const motion=matchMedia('(prefers-reduced-motion: reduce)');
const button=stage.querySelector('.showcase-pause'),caption=document.querySelector('#hardware-caption');
const cycle=11000;
let time=0,last=null,frame=0,current=-1,paused=false,visible=true;
const ease=t=>t*t*(3-2*t);
function render(){
 const step=Math.floor(time/cycle),model=step%2?'smk':'fm1',pair=Math.floor(step/2),palette=model==='fm1'?fm1:smk;
 const [finish,label]=palette[pair%palette.length],layer=layers[model];
 if(step!==current){
  layer.dataset.finish=finish;
  for(const [name,el] of Object.entries(layers)){el.classList.toggle('is-visible',name===model);el.setAttribute('aria-hidden',String(name!==model));}
  caption.textContent=(model==='fm1'?'FM-1 / ':'SMK-37 / ')+label;
  stage.dataset.currentModel=model;stage.dataset.currentFinish=finish;
  current=step;
 }
 const t=time%cycle;
 // Establish the hardware, approach its actual LCD, hold, then pull back.
 let zoom=t<1800?0:t<4200?ease((t-1800)/2400):t<6500?1:t<9100?1-ease((t-6500)/2600):0;
 if(motion.matches)zoom=0;
 const {wide,close}=cameras[model];
 layer.querySelector('svg').setAttribute('viewBox',wide.map((v,i)=>(v+(close[i]-v)*zoom).toFixed(3)).join(' '));
}
function tick(now){
 if(last!==null)time+=now-last;last=now;render();frame=requestAnimationFrame(tick);
}
function schedule(){
 cancelAnimationFrame(frame);last=null;
 button.setAttribute('aria-label',paused?'Play hardware animation':'Pause hardware animation');
 button.title=paused?'Play animation':'Pause animation';button.firstElementChild.textContent=paused?'▶':'Ⅱ';
 button.hidden=motion.matches;
 if(!paused&&!document.hidden&&visible&&!motion.matches)frame=requestAnimationFrame(tick);
}
button.addEventListener('click',()=>{paused=!paused;schedule();});
document.addEventListener('visibilitychange',schedule);
motion.addEventListener('change',()=>{render();schedule();});
new IntersectionObserver(([entry])=>{visible=entry.isIntersecting;schedule();},{threshold:0.05}).observe(stage);
render();schedule();
