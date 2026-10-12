// SPDX-License-Identifier: GPL-3.0-only
import {parsePackage} from './vendor/smk37-update.js';
import {Updater} from './vendor/fm1ota.js';
const logEl=document.querySelector('#log'),button=document.querySelector('#install'),ack=document.querySelector('#ack');
const log=s=>{logEl.textContent+='\n'+s;};
let pkg,busy=false;
function sync(){button.disabled=busy||!pkg||!ack.checked||!navigator.requestMIDIAccess;}
ack.onchange=sync;
try{
  if(!['localhost','127.0.0.1','[::1]'].includes(location.hostname))throw Error('This private installer runs on localhost only.');
  const response=await fetch('./candidate.json',{cache:'no-store'});if(!response.ok)throw Error('Stage the private candidate first.');
  const m=await response.json();if(m.board!=='SMK-37 Pro'||m.private!==true||m.package!=='doom-test01.smkupdate')throw Error('Unexpected candidate metadata.');
  const bytes=new Uint8Array(await (await fetch('./'+m.package,{cache:'no-store'})).arrayBuffer());
  pkg=await parsePackage(bytes,m.sha256);
  if(pkg.product!=='SMK-37_990'||pkg.version!=='DOOM SMK TEST01'||pkg.format!==1)throw Error('Unexpected Doom package identity.');
  logEl.textContent='Package verified. '+m.version+' is ready for your SMK-37 Pro.';
}catch(e){pkg=null;log(e.message);}sync();
window.addEventListener('beforeunload',e=>{if(busy){e.preventDefault();e.returnValue='';}});
button.onclick=async()=>{
  if(button.disabled)return;busy=true;sync();let link;
  try{
    const access=await navigator.requestMIDIAccess({sysex:true});
    const up=new Updater(access,log,/smk|felucca|sloop|melodee|ota|composite|sinco|usb-midi/i);
    let dev=await up.find(id=>['SMK-37','ota-SMK-37'].includes(id.model)&&id.version>=911);
    if(!dev)throw Error('Updater-enabled SMK not found. No installation started.');
    link=dev.link;const START=[0xf0,0x22,0x24,0x35,0x7f,0xf7];
    if(dev.id.model==='SMK-37'){
      log('Entering the existing SMK RAM updater.');if(!link.send(START))throw Error('SMK disconnected.');
      link.close();link=null;
      dev=await up.waitFor(id=>id.model==='ota-SMK-37',30000);
      if(!dev)throw Error('RAM updater did not appear. No browser programming started.');link=dev.link;
    }
    log('Loader will validate header/calibration and write application sectors only. Keep power connected.');
    if(!link.send(START))throw Error('Loader disconnected.');
    const result=await up.serve(link,pkg.bytes,0xf0000000,30000,n=>{if(n%64===0)log('Transfer request '+n);});
    if(!result.finished)throw Error('Transfer did not finish. Keep power on and save this log. Do not retry blindly.');
    link.close();link=null;
    log('Loader reported transfer completion. Doom does not return a MIDI identity. Check the physical screen for DOOM TEST01 and the room; boot success is not confirmed by this page.');
  }catch(e){log(e.message);}finally{link?.close();busy=false;pkg=null;sync();}
};
