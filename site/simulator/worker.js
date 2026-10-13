// SPDX-License-Identifier: GPL-3.0-only
import createEngine from './doom-engine.js?v=knobs16-1';
let engine, timer=null, step=0, failed=false, next=0;
const releases=new Set();
function frame(){const ptr=engine._browser_frame();const pixels=engine.HEAPU8.slice(ptr,ptr+240*240*4);postMessage({type:'frame',pixels},[pixels.buffer]);}
function stop(){clearTimeout(timer);timer=null;releases.clear();engine?._browser_release();}
function fail(error){stop();failed=true;postMessage({type:'error',message:String(error?.message||error)});}
function schedule(){next+=1000/35;const now=performance.now();if(next<now-100)next=now;timer=setTimeout(()=>{tick();if(timer!==null&&!failed)schedule();},Math.max(0,next-now));}
function tick(){try{engine._browser_step();for(const action of releases)engine._browser_key(action,0);releases.clear();frame();const ptr=engine._browser_audio();const audio=engine.HEAPF32.slice(ptr/4,ptr/4+1260);postMessage({type:'audio',audio},[audio.buffer]);if(++step%10===0)postMessage({type:'state',health:engine._browser_stat(1),ammo:engine._browser_stat(7),score:engine._browser_stat(2),level:engine._browser_stat(3)});}catch(e){fail(e);}}
self.onmessage=({data})=>{if(!engine||failed)return;try{if(data.type==='key'){if(data.down){releases.delete(data.action);engine._browser_key(data.action,1);}else releases.add(data.action);}if(data.type==='menu-scroll'&&engine._browser_stat(9)){engine._browser_menu_scroll(Math.max(-16,Math.min(16,Math.trunc(Number(data.steps)||0))));engine._browser_step();frame();}if(data.type==='release'){releases.clear();engine._browser_release();}if(data.type==='run'){if(data.value&&!timer){engine._browser_release();next=performance.now();schedule();}else if(!data.value)stop();}}catch(e){fail(e);}};
try{engine=await createEngine({locateFile:name=>new URL(name+'?v=knobs16-1',import.meta.url).href,print:()=>{},printErr:message=>postMessage({type:'log',message}),onAbort:message=>fail(new Error(String(message)))});engine._browser_init();engine._browser_splash();frame();postMessage({type:'ready'});}catch(e){fail(e);}
