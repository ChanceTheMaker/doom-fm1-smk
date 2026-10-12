// Public emergency pause must prevent entry into any transport or package build.
import assert from 'node:assert/strict';
import {readFileSync,readdirSync} from 'node:fs';
import {buildFirmware,installFm1} from '../site/firmware-builder.js';
import {installSmk,installStockSmk} from '../site/vendor/smk37-update.js';
const touched=new Proxy({}, {get(){throw Error('Device or package accessed before pause');}});
for(const operation of [buildFirmware,installFm1,installSmk,installStockSmk])
  await assert.rejects(operation(touched,touched,touched), /Public firmware installation is paused/);
const read=p=>readFileSync(new URL('../site/'+p,import.meta.url),'utf8');
assert.deepEqual(JSON.parse(read('firmware/releases.json')),[]);
assert.deepEqual(readdirSync(new URL('../site/firmware/',import.meta.url)),['releases.json']);
const html=read('index.html');
for(const id of ['build','install-button','download']) assert.match(html,new RegExp('<button[^>]*id="'+id+'"[^>]*disabled'));
assert.doesNotMatch(read('app.js'),/requestMIDIAccess|\.onclick|fetch\(|import /);
assert.match(html,/If a transfer is still in progress/);
assert.match(html,/Test06 does not contain a USB MIDI updater/);
console.log('PASS: public build/install entry points reject before access; no firmware artifacts or active UI.');
