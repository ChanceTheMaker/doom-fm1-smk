// SPDX-License-Identifier: GPL-3.0-only
// Shared pointer, wheel and keyboard behavior for both device panels.
export function bindKnob(dial,kind,turn){
 dial.type='button';dial.classList.add('active-knob');dial.dataset.knob=kind;
 dial.setAttribute('aria-label',kind==='volume'?'K1 volume':'K2 menu up and down');
 dial.title=kind==='volume'?'K1 volume: drag up/down, scroll, or use arrow keys':'K2 menu: drag up/down, scroll, or use arrow keys';
 if(kind==='volume'){dial.setAttribute('role','slider');dial.setAttribute('aria-valuemin','0');dial.setAttribute('aria-valuemax','100');}
 let drag=null;
 dial.addEventListener('pointerdown',e=>{if(e.button!==0)return;drag={id:e.pointerId,y:e.clientY};dial.setPointerCapture(e.pointerId);dial.focus({preventScroll:true});e.preventDefault();});
 dial.addEventListener('pointermove',e=>{if(drag?.id!==e.pointerId)return;const steps=Math.trunc((drag.y-e.clientY)/6);if(steps){drag.y-=steps*6;turn(steps);}});
 for(const name of ['pointerup','pointercancel','lostpointercapture'])dial.addEventListener(name,()=>drag=null);
 dial.addEventListener('wheel',e=>{if(!e.deltaY)return;e.preventDefault();turn(e.deltaY<0?1:-1);},{passive:false});
 dial.addEventListener('keydown',e=>{let steps=0;if(e.key==='ArrowRight')steps=1;if(e.key==='ArrowLeft')steps=-1;if(e.key==='ArrowUp')steps=kind==='volume'?1:-1;if(e.key==='ArrowDown')steps=kind==='volume'?-1:1;if(steps){e.preventDefault();e.stopPropagation();turn(steps);}});
 dial.addEventListener('keyup',e=>{if(e.key.startsWith('Arrow')){e.preventDefault();e.stopPropagation();}});
}
