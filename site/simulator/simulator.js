// SPDX-License-Identifier: GPL-3.0-only
import {createSMKPanel} from './smk-panel.js?v=knobs16-1';
import {bindKnob} from './knobs.js?v=knobs16-1';
import {actions,keymap,createInput} from './input.js';
import {fm1NoteActions,actionColors} from './fm1-controls.js';
const $=id=>document.getElementById(id),sim=$('simulator'),canvas=$('screen'),ctx=canvas.getContext('2d',{alpha:false});
let worker,ready=false,running=false,context,node,gain,audioSetup,generation=0,drag=null;
let soundFailed=false,played=false,model='fm1';
let smk;
const activeCanvas=()=>model==='fm1'?canvas:smk.canvas;
const input=createInput((action,down)=>{if(ready)worker.postMessage({type:'key',action,down});},(action,down)=>{for(const b of sim.querySelectorAll(`[data-action="${action}"]`))b.setAttribute('aria-pressed',String(down));});
const status=text=>{$('sim-status').textContent=text;};
function controls(){for(const b of sim.querySelectorAll('[data-action]'))b.disabled=!ready;$('start').disabled=!ready;$('screen-start').disabled=!ready;$('restart').disabled=!ready;$('start').textContent=running?'Ⅱ Pause':'▶ Play + sound';$('start').setAttribute('aria-pressed',String(running));$('screen-start').textContent=ready?(played?'Resume game':'Start game + sound'):'Loading…';$('screen-overlay').hidden=running;if(smk){smk.overlay.hidden=running;smk.play.disabled=!ready;smk.play.textContent=$('screen-start').textContent;}}
function volume(){const v=Number($('volume').value)/100;$('volume-value').value=Math.round(v*100)+'%';sim.style.setProperty('--angle',(-135+v*270)+'deg');for(const d of sim.querySelectorAll('[data-knob="volume"]')){d.setAttribute('aria-valuenow',String(Math.round(v*100)));d.setAttribute('aria-valuetext',Math.round(v*100)+'%');}if(smk)smk.range.value=$('volume').value;if(gain)gain.gain.setTargetAtTime(v,context.currentTime,.015);}
function knob(dial,number){bindKnob(dial,number===1?'volume':'menu',steps=>{if(number===1){$('volume').value=Math.max(0,Math.min(100,+$('volume').value+steps*3));volume();}else if(ready){if(!running)start();worker.postMessage({type:'menu-scroll',steps});}});}
async function enableSound(){
 if(!context){const Audio=window.AudioContext||window.webkitAudioContext;if(!Audio)throw Error('Web Audio is not available');context=new Audio({sampleRate:44100,latencyHint:'interactive'});gain=context.createGain();gain.gain.value=+$('volume').value/100;gain.connect(context.destination);}
 const resumed=context.resume();
 if(!audioSetup)audioSetup=context.audioWorklet.addModule(new URL('./sound.js',import.meta.url)).then(()=>{node=new AudioWorkletNode(context,'doom-sound',{numberOfInputs:0,numberOfOutputs:1,outputChannelCount:[2]});node.connect(gain);});
 try{await Promise.all([resumed,audioSetup]);}catch(e){audioSetup=null;throw e;}
}
function start(){if(!ready)return;if(!running){played=true;running=true;worker.postMessage({type:'run',value:true});controls();status('Playing');if(document.activeElement?.closest('.sim-toolbar,#screen-overlay'))activeCanvas().focus({preventScroll:true});}enableSound().then(()=>{soundFailed=false;if(running)status('Playing · sound on');}).catch(()=>{soundFailed=true;if(running)status('Playing · audio unavailable');});}
function pause(){input.clear();if(worker)worker.postMessage({type:'run',value:false});running=false;node?.port.postMessage({clear:true});controls();if(ready)status('Paused');}
function press(owner,action){if(!ready)return;if(!running)start();input.press(owner,action);}
function bind(button,action){button.dataset.action=action;button.setAttribute('aria-pressed','false');button.disabled=true;
 button.addEventListener('pointerdown',e=>{if(e.pointerType==='mouse'&&e.button!==0)return;e.preventDefault();activeCanvas().focus({preventScroll:true});button.setPointerCapture(e.pointerId);press('p'+e.pointerId,action);});
 button.addEventListener('pointermove',e=>{if(!button.hasPointerCapture(e.pointerId)||!button.matches('.touch-key,.sim-key'))return;if(e.pointerType==='mouse'&&!(e.buttons&1)){input.release('p'+e.pointerId);return;}const target=document.elementFromPoint(e.clientX,e.clientY)?.closest('.touch-key[data-action],.sim-key[data-action]');if(target&&sim.contains(target))press('p'+e.pointerId,+target.dataset.action);else input.release('p'+e.pointerId);});
 for(const name of ['pointerup','pointercancel','lostpointercapture'])button.addEventListener(name,e=>input.release('p'+e.pointerId));
 button.addEventListener('keydown',e=>{if(e.code==='Space'||e.code==='Enter'){e.preventDefault();e.stopPropagation();if(!e.repeat)press('button:'+e.code,action);}});
 button.addEventListener('keyup',e=>{if(e.code==='Space'||e.code==='Enter'){e.preventDefault();e.stopPropagation();input.release('button:'+e.code);}});
 button.addEventListener('blur',()=>{input.release('button:Space');input.release('button:Enter');});
 button.addEventListener('click',e=>{if(e.detail===0){const owner='assistive:'+action;press(owner,action);setTimeout(()=>input.release(owner),100);}});
}
const make=(tag,cls,text)=>{const e=document.createElement(tag);e.className=cls;e.textContent=text;return e;};
for(let i=1;i<=4;i++){const wrap=make('div',i<=2?'control-knob':'dummy-knob',i===1?'K1 VOLUME':i===2?'K2 MENU':'KNOB '+i),dial=make(i<=2?'button':'div','dial','');if(i<=2)knob(dial,i);else dial.setAttribute('aria-hidden','true');dial.append(document.createElement('i'));wrap.append(dial);$('right-knobs').append(wrap);}
for(const [name,action] of [['FX',null],['SCL',null],['ENV',null],['LFO',null],['EDIT',null],['GLO',null],['HOME',null],['SAVE',null],['ARP',null],['SEQ',null],['PLAY',6],['REC',7]]){const b=make('button','',name);b.type='button';if(action!==null){b.title=action===6?'Game menu':'Select';b.setAttribute('aria-label',b.title);bind(b,action);}else if(name==='PLAY'){b.title='Pause / resume browser game';b.onclick=()=>running?pause():start();}else{b.disabled=true;b.title='Not used in Doom';} $('panel-buttons').append(b);}
const noteNames=['C','C#','D','D#','E','F','F#','G','G#','A','A#','B'],short=['LEFT','FWD','RIGHT','BACK','FIRE','USE','MENU','OK','RUN','◀ STR','STR ▶','WEAPON'],hints=['A / ←','W / ↑','D / →','S / ↓','SPACE','F','ESC','ENTER','SHIFT','Q','E','R'];
let white=0;
for(let note=53;note<=79;note++){const black=[1,3,6,8,10].includes(note%12),name=noteNames[note%12]+(Math.floor(note/12)-1);const b=make('button','touch-key'+(black?' black-key':''),'');b.type='button';b.style.gridRow=black?'1':'2';b.style.gridColumn=(black?white*2:white*2+1)+' / span 2';
 if(fm1NoteActions[note-53]>=0){const a=fm1NoteActions[note-53];b.style.setProperty('--control-light',actionColors[a]);b.append(make('span','',name),make('strong','',short[a]),make('small','',hints[a]));b.setAttribute('aria-label',`${name}: ${actions[a]}`);b.title=`${actions[a]} · ${hints[a]}`;bind(b,a);}else{b.append(make('span','',name));b.disabled=true;b.classList.add('unused');b.title=name+' · unused in Doom';}if(!black)white++;$('keys').append(b);}
smk=createSMKPanel($('smk-panel'),bind,actions,start,v=>{$('volume').value=v;volume();},knob);
for(const b of sim.querySelectorAll('[data-model]'))b.onclick=()=>{input.clear();model=b.dataset.model;$('fm1-panel').hidden=model!=='fm1';$('smk-panel').hidden=model==='fm1';$('finishes').hidden=model!=='fm1';smk.model(model);for(const choice of sim.querySelectorAll('[data-model]'))choice.setAttribute('aria-pressed',String(choice===b));activeCanvas().focus({preventScroll:true});};
const finishes=[['mint','Graphite / mint',['#2e3335','#75b6a9','#89c5b8','#e3ebe5','#16352f']],['orange','Orange',['#e44a23','#b13b2b','#c44a35','#fff4e3','#fff2dc']],['purple','Purple',['#b389c5','#79609d','#957bb6','#35233f','#221b2c']],['blue','Ivory / blue',['#e8e5da','#527399','#6c8db3','#2c3f50','#eef5f9']],['red','Ivory / red',['#ece5d8','#964a3c','#b5604c','#46352d','#fff1db']],['cream','Cream / charcoal',['#ded8ce','#353c3d','#485051','#303638','#eceddf']],['black','Black',['#272b2c','#191f20','#333b3c','#d8dcd6','#e6e9e3']]];
function finish(id){const f=finishes.find(v=>v[0]===id)||finishes[0];sim.dataset.finish=f[0];['shell','pad','key','case-ink','key-ink'].forEach((k,i)=>sim.style.setProperty('--'+k,f[2][i]));for(const b of $('finish-menu').children)b.setAttribute('aria-pressed',String(b.dataset.finish===f[0]));try{localStorage.setItem('doom.fm1.finish',f[0]);}catch{}}
for(const [id,label,c] of finishes){const b=make('button','',label);b.type='button';b.dataset.finish=id;const sw=make('span','swatch','');sw.style.background=`conic-gradient(${c[0]} 0 50%,${c[1]} 50% 75%,${c[2]} 75%)`;b.prepend(sw);b.onclick=()=>{finish(id);$('finishes').open=false;};$('finish-menu').append(b);}
let stored;try{stored=localStorage.getItem('doom.fm1.finish');}catch{}finish(stored);
$('volume').oninput=volume;volume();
const dial=sim.querySelector('.master-dial');dial.addEventListener('pointerdown',e=>{if(e.button)return;drag={id:e.pointerId,y:e.clientY,value:+$('volume').value};dial.setPointerCapture(e.pointerId);e.preventDefault();});dial.addEventListener('pointermove',e=>{if(drag?.id!==e.pointerId)return;$('volume').value=Math.max(0,Math.min(100,drag.value+(drag.y-e.clientY)));volume();});for(const n of ['pointerup','pointercancel','lostpointercapture'])dial.addEventListener(n,()=>drag=null);
$('start').onclick=()=>running?pause():start();$('screen-start').onclick=()=>ready?start():boot();
$('restart').onclick=()=>{boot();};
$('screen-size').onclick=()=>{const on=sim.classList.toggle('expanded');$('screen-size').setAttribute('aria-pressed',String(on));$('screen-size').title=on?'Show device controls':'Expand screen';$('screen-size').setAttribute('aria-label',$('screen-size').title);};
function reflectFullscreen(){const full=!!document.fullscreenElement||sim.classList.contains('window-full');$('fullscreen').title=full?'Exit fullscreen':'Enter fullscreen';$('fullscreen').setAttribute('aria-label',$('fullscreen').title);}
function windowFullscreen(on){sim.classList.toggle('window-full',on);document.body.style.overflow=on?'hidden':'';reflectFullscreen();}
$('fullscreen').onclick=async()=>{if(sim.classList.contains('window-full')){windowFullscreen(false);return;}try{if(document.fullscreenElement)await document.exitFullscreen();else await sim.requestFullscreen();}catch{windowFullscreen(true);}reflectFullscreen();};
document.addEventListener('fullscreenchange',reflectFullscreen);
for(let i=0;i<actions.length;i++)$('help-controls').append(make('div','',`${i+1}. ${actions[i]} · ${hints[i]}`));
$('help').onclick=()=>{pause();$('help-dialog').showModal();};$('close-help').onclick=()=>$('help-dialog').close();
document.addEventListener('pointerdown',e=>{if(!$('finishes').contains(e.target))$('finishes').open=false;});
window.addEventListener('keydown',e=>{if(e.code==='Escape'&&sim.classList.contains('window-full')){windowFullscreen(false);e.preventDefault();return;}if(e.altKey||e.ctrlKey||e.metaKey||$('help-dialog').open||e.target.closest('input,select,textarea,.sim-toolbar,dialog'))return;const a=keymap[e.code];if(a===undefined)return;e.preventDefault();if(!e.repeat)press('key:'+e.code,a);});
window.addEventListener('keyup',e=>{if(keymap[e.code]!==undefined){input.release('key:'+e.code);if(!e.target.closest('input,select,textarea,dialog'))e.preventDefault();}});
window.addEventListener('blur',()=>{if(running)pause();else input.clear();});document.addEventListener('visibilitychange',()=>{if(document.hidden&&running)pause();});window.addEventListener('pagehide',()=>{pause();worker?.terminate();context?.close();});
function boot(){generation++;const g=generation;pause();ready=false;played=false;controls();status('Loading engine…');worker?.terminate();worker=new Worker(new URL('./worker.js?v=knobs16-1',import.meta.url),{type:'module'});const timeout=setTimeout(()=>{if(g===generation&&!ready){worker.terminate();status('Engine did not load. Check your connection, then Retry.');$('restart').disabled=false;$('screen-start').disabled=false;$('screen-start').textContent='Retry';}},30000);
 worker.onmessage=({data})=>{if(g!==generation)return;if(data.type==='frame'){const frame=new ImageData(new Uint8ClampedArray(data.pixels.buffer),240,240);ctx.putImageData(frame,0,0);smk.canvas.getContext('2d',{alpha:false}).putImageData(frame,0,0);}else if(data.type==='ready'){clearTimeout(timeout);ready=true;controls();status('Ready · press Play');}else if(data.type==='audio'){if(running&&node&&context.state==='running')node.port.postMessage(data.audio,[data.audio.buffer]);}else if(data.type==='state'){if(running)status(`L${data.level}/9 · HP ${Math.max(0,data.health)} · AM ${data.ammo} · ${data.score} pts${soundFailed?' · silent':''}`);}else if(data.type==='error'){clearTimeout(timeout);pause();ready=false;controls();status('Game stopped · use Restart to retry.');$('restart').disabled=false;$('screen-start').disabled=false;$('screen-start').textContent='Retry';console.error('Doom simulator:',data.message);}};
 worker.onerror=e=>{clearTimeout(timeout);pause();ready=false;controls();status('Could not load Doom · use Restart to retry.');$('restart').disabled=false;$('screen-start').disabled=false;$('screen-start').textContent='Retry';console.error(e.message);};
}
boot();
