// SPDX-License-Identifier: GPL-3.0-only
import {Updater} from './vendor/fm1ota.js';
const button=document.querySelector('#install'),ack=document.querySelector('#ack'),output=document.querySelector('#log');
let image,busy=false;
const log=s=>{output.textContent+='\n'+s;};
function sync(){button.disabled=busy||!image||!ack.checked||!navigator.requestMIDIAccess;}
ack.onchange=sync;
try{
  if(!['localhost','127.0.0.1','[::1]'].includes(location.hostname))throw Error('Local test installer only.');
  const r=await fetch('./candidate.json',{cache:'no-store'});if(!r.ok)throw Error('No FM-1 candidate staged.');
  const m=await r.json();
  if(m.board!=='FM-1'||m.product!=='FM-1_995'||m.package!=='doom-fm1-test06.fwsc')throw Error('Wrong candidate identity.');
  const response=await fetch('./'+m.package,{cache:'no-store'});if(!response.ok)throw Error('Package unavailable.');
  const b=new Uint8Array(await response.arrayBuffer());
  const hash=[...new Uint8Array(await crypto.subtle.digest('SHA-256',b))].map(v=>v.toString(16).padStart(2,'0')).join('');
  if(b.length!==m.bytes||hash!==m.sha256)throw Error('Package hash/size mismatch.');
  let product='';for(let i=0;i<20;i++){const c=b[i*48+47];if(c!==0x7d)product+=String.fromCharCode((c-i-1)&255);}
  if(product!==m.product)throw Error('Not the expected FM-1 package.');
  image=new Uint8Array(b.length-20);
  for(let i=0;i<20;i++)image.set(b.subarray(i*48,i*48+47),i*47);
  image.set(b.subarray(960),940);
  output.textContent='Package verified. Doom FM-1 Test06 is ready.';
}catch(e){image=null;log(e.message);}sync();
window.addEventListener('beforeunload',e=>{if(busy){e.preventDefault();e.returnValue='';}});
button.onclick=async()=>{
  if(button.disabled)return;busy=true;sync();let link;
  try{
    const access=await navigator.requestMIDIAccess({sysex:true});
    const up=new Updater(access,log,/fm-1|felucca|sloop|melodee|ota|composite|sinco|usb-midi/i);
    let dev=await up.find(id=>id.model==='FM-1');
    if(!dev)throw Error('Running FM-1 not found. No update started. SMK devices are not accepted.');
    link=dev.link;
    log('Found '+dev.id.text+'. Staging the existing Felucca FM-1 loader. Keep USB and power connected.');
    if(!link.send([0xf0,0x22,0x24,0x35,0x7f,0xf7]))throw Error('FM-1 disconnected.');
    await new Promise(r=>setTimeout(r,2000));
    const first=await up.serve(link,image,0xe0000000,15000,n=>{if(n%32===0)log('Preparing loader: '+n);});
    link.close();link=null;
    if(!first.finished)throw Error('Loader preparation did not finish. Stop and inspect the device.');
    log('Waiting for the FM-1 loader.');
    dev=await up.waitFor(id=>id.model==='ota-FM-1',30000);
    if(!dev)throw Error('FM-1 loader did not appear. Stop; save this log before retrying.');
    link=dev.link;
    log('Installing application; keep power connected.');
    const result=await up.write(dev,image,(step,n)=>{if(step==='write'&&n%64===0)log('Transfer request '+n);});
    link=null;
    if(!result.finished)throw Error('Transfer interrupted. Keep power connected and save this log before recovery.');
    log('Loader reported transfer completion. Doom has no MIDI identity; check the physical screen. This does not confirm a successful boot.');
  }catch(e){log(e.message);}finally{link?.close();busy=false;image=null;sync();}
};
