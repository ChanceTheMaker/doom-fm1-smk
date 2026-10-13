// SPDX-License-Identifier: GPL-3.0-only
// Device layout adapted from sloop-smk 090588d. Doom input only.
export function createSMKPanel(host,bind,actions,start,volume,knob){
 const el=(tag,cls,text='')=>{const e=document.createElement(tag);e.className=cls;e.textContent=text;return e;};
 const shell=el('div','smk-simulator-shell'),name=el('div','smk-name','SMK-37 PRO');host.append(shell);shell.append(name);
 const top=el('div','sim-top');shell.append(top);
 const wheels=el('div','sim-wheels');top.append(wheels);
 for(const label of ['PITCH','MOD']){const w=el('div','sim-wheel',label),housing=el('span','sim-wheel-housing');housing.append(el('span','sim-wheel-tread'));w.append(housing);wheels.append(w);}
 const left=el('div','sim-left'),bezel=el('div','sim-bezel'),canvas=el('canvas','sim-lcd');canvas.width=canvas.height=240;canvas.tabIndex=0;canvas.setAttribute('aria-label','SMK Doom display');
 const overlay=el('div','smk-overlay'),play=el('button','','Play + sound');play.type='button';play.onclick=start;overlay.append(play);bezel.append(canvas,overlay);left.append(bezel);top.append(left);
 const label=el('label','volume-label','BROWSER VOLUME'),range=el('input','browser-volume');range.type='range';range.min=0;range.max=100;range.value=70;range.oninput=()=>volume(range.value);label.append(range);left.append(label);
 const center=el('div','sim-center'),knobs=el('div','sim-knobs'),pads=el('div','sim-pads');top.append(center);center.append(knobs,pads);
 for(let i=1;i<=8;i++){const wrap=el('div','sim-encoder','K'+i),dial=el('button','sim-dial');if(i<=2){knob(dial,i);wrap.append(el('small','',i===1?'VOLUME':'MENU'));}else{dial.disabled=true;dial.setAttribute('aria-label','Knob '+i+' unused in Doom');}wrap.append(dial);knobs.append(wrap);}
 for(let i=1;i<=16;i++){const pad=el('button','sim-pad',String(i));pad.disabled=true;pad.title='Unused in Doom';pads.append(pad);}
 const right=el('div','sim-right'),faders=el('div','sim-faders'),buttons=el('div','sim-buttons');right.append(faders,buttons);top.append(right);
 for(let i=1;i<=4;i++){const label=el('label','sim-fader','F'+i),f=el('input','');f.type='range';f.disabled=true;label.append(f);faders.append(label);}
 for(const [label,action] of [['PATCH',6],['PARA',7],['BANK',null],['ARP',null],['SEQ',null],['REC',null]]){const b=el('button','sim-button',label);b.type='button';if(action===null)b.disabled=true;else {b.setAttribute('aria-label',actions[action]);bind(b,action);}buttons.append(b);}
 const bottom=el('div','sim-bottom'),piano=el('div','sim-piano');piano.style.setProperty('--white-count',22);bottom.append(piano);shell.append(bottom);
 const short=['LEFT','FWD','RIGHT','BACK','FIRE','USE','MENU','OK','RUN','STR L','STR R','WEAPON'];let white=0;
 for(let note=48;note<=84;note++){const black=[1,3,6,8,10].includes(note%12),b=el('button','sim-key '+(black?'black':'white'));b.type='button';b.style.setProperty('--key-x',black?white-.31:white);
  if(!black&&white<12){b.append(el('strong','',short[white]));b.title=actions[white];b.setAttribute('aria-label',`White key ${white+1}: ${actions[white]}`);bind(b,white);}else{b.disabled=true;b.classList.add('unused');b.setAttribute('aria-label','Unused key');}piano.append(b);if(!black)white++;
 }
 return {canvas,overlay,play,range,model(id){shell.dataset.finish=id==='elite'?'elite':'red';name.textContent=id==='elite'?'SMK-37 ELITE':'SMK-37 PRO';}};
}
