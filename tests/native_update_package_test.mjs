// Offline package validation for native candidates; no website staging or device I/O.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {buildFirmware} from '../site/firmware-builder.js?v=test07';
import {Package} from '../site/vendor/fm1pkg.js?v=test07';
import {smkLogicalImage} from '../site/vendor/smk37-package.js?v=test07';
import {parsePackage} from '../site/vendor/smk37-update.js?v=test07';
import {unpack7} from '../site/vendor/fm1ota.js?v=test07';
const paths=process.argv.slice(2);assert.equal(paths.length,3,'Pass the pinned FM-1, Pro016 and Elite016 bases.');
const targets=['fm1','smk37-pro','smk37-elite'];
mkdirSync('build/test07-packages',{recursive:true});
for(let i=0;i<targets.length;i++){
 const id=targets[i],manifest=JSON.parse(readFileSync(`build/native/${id}/manifest.json`));
 assert.equal(manifest.version,'test07');assert.equal(manifest.usb_updater,true);
 const header=readFileSync(`build/native/${id}/update/doom_loader_image.h`,'utf8');
 const wire=header.match(/dp_identity_wire\[\]=\{([^}]+)\}/)[1].split(',').map(Number);
 assert.equal(wire[0],0xf0);assert.equal(wire.at(-1),0xf7);
 const decoded=unpack7(wire.slice(1,-1));assert.equal(decoded.length,34);
 assert.deepEqual(decoded.slice(0,6),[0,0x59,0x11,27,0,0]);
 assert.equal(String.fromCharCode(...decoded.slice(6,33)).replace(/\0+$/,''),manifest.loader.product);
 assert.equal(decoded[33],~decoded.slice(6,33).reduce((a,b)=>a+b,0)&255);
 const base=new Uint8Array(readFileSync(paths[i])),app=new Uint8Array(readFileSync(`build/native/${id}/${manifest.image}`));
 const release={id,board:['FM-1','SMK-37 Pro','SMK-37 Elite'][i],public:true,product:i?'SMK-37_996':'FM-1_996',version:i?'DOOM SMK TEST07':'DOOM FM1 TEST07',bytes:manifest.bytes,sha256:manifest.sha256};
 const result=await buildFirmware(release,app,base);
 if(i===0){
  const before=new Package(base),after=new Package(result.factory);
  assert.equal(after.product,release.product);
  assert.deepEqual(after.flash.subarray(0,0x4000),before.flash.subarray(0,0x4000));
  assert.deepEqual(after.dec.subarray(after.appOff,after.appOff+app.length),app);
 }else{
  assert.equal((await parsePackage(result.bytes,result.sha)).product,release.product);
  const before=smkLogicalImage(base).raw;
  assert.deepEqual(result.image.subarray(1024,1024+0x4000),before.subarray(1024,1024+0x4000));
  assert.deepEqual(result.image.subarray(1024+0x9d000),before.subarray(1024+0x9d000));
  writeFileSync(`build/test07-packages/${id}.smkupdate`,result.bytes);
 }
 writeFileSync(`build/test07-packages/${id}.fwsc`,result.factory);
 writeFileSync(`build/test07-packages/${id}.json`,JSON.stringify({...release,loader:manifest.loader,package_sha256:result.sha,hardware_tested:false},null,2)+'\n');
 console.log('PASS:',id,'Test07 package round trip and protected bytes; local build output only.');
}
