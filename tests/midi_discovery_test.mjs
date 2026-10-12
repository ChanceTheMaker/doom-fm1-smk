// Discovery must never start an update, including when no compatible firmware replies.
import assert from 'node:assert/strict';
import {Updater,pack7} from '../site/vendor/fm1ota.js?v=release08';

const logs=[];
assert.equal(await new Updater({inputs:new Map(),outputs:new Map()},s=>logs.push(s)).findAny(()=>true),null);
assert(logs.some(s=>s==='MIDI ports: []'));
assert(logs.some(s=>s.includes('Older Doom builds lack a USB MIDI updater')));

const listeners=new Set(),sent=[];
const input={type:'input',name:'Different input name',state:'connected',connection:'closed',
 async open(){this.connection='open';},async close(){this.connection='closed';},
 addEventListener(_,fn){listeners.add(fn);},removeEventListener(_,fn){listeners.delete(fn);}};
const output={type:'output',name:'SMK output',state:'connected',connection:'closed',
 async open(){this.connection='open';},async close(){this.connection='closed';},
 send(data){
  sent.push([...data]);
  const reply=new Uint8Array(34);reply.set([0,0x59,0x11]);reply.set(new TextEncoder().encode('SMK-37_931'),6);
  for(const fn of listeners)fn({data:[0xf0,...pack7(reply),0xf7]});
 }};
const access={inputs:new Map([['in',input]]),outputs:new Map([['out',output]])};
const updater=new Updater(access,s=>logs.push(s));
assert.equal(await updater.findAny(id=>id.model==='FM-1',{probeMs:0}),null);
assert(logs.some(s=>s.includes('SMK-37_931')&&s.includes('not the expected identity')));
assert.equal(input.connection,'closed');assert.equal(output.connection,'closed');
const device=await updater.findAny(id=>id.model==='SMK-37',{probeMs:0});
assert.equal(device.id.version,931);await device.link.close();
assert.equal(listeners.size,0);
assert(sent.length===2&&sent.every(s=>JSON.stringify(s)===JSON.stringify([0xf0,0,0x32,0x45,0,0,0,0x40,0x7f,0xf7])));
console.log('PASS: missing ports, rejected identity, differently named ports, cleanup and identity-only discovery.');
