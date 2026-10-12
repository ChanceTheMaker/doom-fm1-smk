// SPDX-License-Identifier: GPL-3.0-only
// Offline transport decisions; never opens a MIDI port.
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync,mkdirSync} from 'node:fs';
import {buildFirmware,installFm1} from '../site/firmware-builder.js?v=release08';
import {Package,logicalImage} from '../site/vendor/fm1pkg.js?v=release08';
import {smkLogicalImage} from '../site/vendor/smk37-package.js?v=release08';
import {parsePackage,installStockSmk,installSmk,LO,HI} from '../site/vendor/smk37-update.js?v=release08';
import {Updater} from '../site/vendor/fm1ota.js?v=release08';

const saved=Object.fromEntries(['findAny','waitForAny','serve','write'].map(k=>[k,Updater.prototype[k]]));
let identity, nextIdentity, transfers=[], sends=0, closes=0, failStage=0;
const device=id=>({id:{...id,text:id.model+'_'+id.version},name:'Test MIDI',link:{send(){sends++;return true;},async close(){closes++;}}});
const reset=(id,next)=>{identity=id;nextIdentity=next;transfers=[];sends=closes=failStage=0;};
const pkg={format:2,image:new Uint8Array(64),bytes:new Uint8Array(64),stockModel:'SMK-37 Pro',product:'SMK-37_995',version:'DOOM SMK TEST06'};
try{
 Updater.prototype.findAny=async function(filter){return identity&&filter(identity)?device(identity):null;};
 Updater.prototype.waitForAny=async function(filter){return nextIdentity&&filter(nextIdentity)?device(nextIdentity):null;};
 Updater.prototype.serve=async function(link,image,end){transfers.push(end);return {finished:transfers.length!==failStage};};
 Updater.prototype.write=async function(dev,image){transfers.push(0xf0000000);await dev.link.close();return {finished:true};};
 for(const model of ['SMK-37 Pro','SMK-37 Elite']){
  pkg.stockModel=model;
  reset({model,version:16},{model:'ota-'+model,version:16});
  await installStockSmk({},pkg);assert.deepEqual(transfers,[0xe0000000,0xf0000000]);assert.equal(closes,2);
  for(const bad of ['FM-1',model==='SMK-37 Pro'?'SMK-37 Elite':'SMK-37 Pro']){
   reset({model:bad,version:16});await assert.rejects(installStockSmk({},pkg),/No matching/);assert.equal(sends,0);
  }
  reset({model,version:15});await assert.rejects(installStockSmk({},pkg),/No matching/);assert.equal(sends,0);
  reset({model,version:16},null);await assert.rejects(installStockSmk({},pkg),/not replied/);assert.deepEqual(transfers,[0xe0000000]);
  for(const stage of [1,2]){
   reset({model,version:16},{model:'ota-'+model,version:16});failStage=stage;
   await assert.rejects(installStockSmk({},pkg),stage===1?/preparation/:/did not finish/);assert.equal(transfers.length,stage);
  }
 }
 reset({model:'ota-FM-1',version:16});pkg.stockModel='SMK-37 Elite';
 await assert.rejects(installStockSmk({},pkg),/paused/);assert.equal(sends,0);
 reset({model:'ota-FM-1',version:16});
 await installStockSmk({},pkg,()=>{},{confirmGeneric:async()=>true});assert.deepEqual(transfers,[0xf0000000]);
 reset({model:'ota-FM-1',version:16});pkg.stockModel='SMK-37 Pro';
 await assert.rejects(installStockSmk({},pkg,()=>{},{confirmGeneric:async()=>true}),/does not match/);assert.equal(sends,0);
 reset({model:'SMK-37',version:921});await assert.rejects(installSmk({},pkg),/older private/);assert.equal(sends,0);
 reset({model:'SMK-37',version:931},{model:'ota-SMK-37',version:931});
 await installStockSmk({},pkg);assert.deepEqual(transfers,[0xf0000000]);assert.equal(closes,2);
 reset({model:'Doom-SMK-37',version:7},{model:'ota-Doom-SMK-37',version:7});
 await installStockSmk({},pkg);assert.deepEqual(transfers,[0xf0000000]);assert.equal(closes,2);
 reset({model:'Doom-SMK-37',version:7},{model:'ota-Doom-FM-1',version:7});
 await assert.rejects(installStockSmk({},pkg),/did not appear/);assert.equal(transfers.length,0);
 reset({model:'ota-Doom-SMK-37',version:7});
 await installStockSmk({},pkg);assert.deepEqual(transfers,[0xf0000000]);assert.equal(closes,1);
 reset({model:'Doom-FM-1',version:7},{model:'ota-Doom-FM-1',version:7});
 await installFm1({},pkg,()=>{});assert.deepEqual(transfers,[0xf0000000]);assert.equal(closes,2);
 reset({model:'Doom-FM-1',version:7},{model:'ota-Doom-SMK-37',version:7});
 await assert.rejects(installFm1({},pkg,()=>{}),/did not appear/);assert.equal(transfers.length,0);
 reset({model:'Doom-FM-1',version:7});
 await assert.rejects(installStockSmk({},pkg),/No matching/);assert.equal(sends,0);
 reset({model:'ota-FM-1',version:900});await assert.rejects(installFm1({},pkg,()=>{}),/cancelled/);assert.equal(sends,0);
 reset({model:'ota-FM-1',version:900});await installFm1({},pkg,()=>{},{confirmGeneric:async()=>true});assert.equal(transfers.length,1);
 reset({model:'SMK-37',version:931});await assert.rejects(installFm1({},pkg,()=>{}),/No updater/);assert.equal(sends,0);
 console.log('PASS: model/version filters, loader handoff failures, generic Elite confirmation, legacy refusal, completion without returning MIDI identity.');
}finally{Object.assign(Updater.prototype,saved);}

// Optional private fixture paths: FM-1 base, official Pro016, official Elite016.
if(process.argv.length>2){
 const paths=process.argv.slice(2);assert.equal(paths.length,3);
 const releases=JSON.parse(readFileSync(new URL('../site/firmware/releases.json',import.meta.url)));
 mkdirSync('build/site-tests',{recursive:true});
 for(let n=0;n<3;n++){
  const r=releases[n],base=new Uint8Array(readFileSync(paths[n])),original=base.slice();
  const app=new Uint8Array(readFileSync(new URL('../site/firmware/'+r.app,import.meta.url)));
  const result=await buildFirmware(r,app,base);assert.deepEqual(base,original);
  if(n===0){
   const a=new Package(base),b=new Package(result.factory);
   assert.deepEqual(a.flash.subarray(0,LO),b.flash.subarray(0,LO));
   assert.deepEqual(b.dec.subarray(b.appOff,b.appOff+app.length),app);
   assert.equal(b.product,r.product);assert.deepEqual(result.image,logicalImage(result.factory));
  }else{
   assert.equal((await parsePackage(result.bytes,result.sha)).product,r.product);
   const a=smkLogicalImage(base).raw,b=result.image;
   assert.deepEqual(a.subarray(1024,1024+LO),b.subarray(1024,1024+LO));
   assert.deepEqual(a.subarray(1024+HI),b.subarray(1024+HI));
   await assert.rejects(buildFirmware({...r,board:n===1?'SMK-37 Elite':'SMK-37 Pro'},app,base),/does not match/);
   writeFileSync('build/site-tests/'+r.id+'.smkupdate',result.bytes);
   const flash=new Uint8Array(0x100000).fill(0xa5);flash.set(a.subarray(1024,1024+HI));
   const points=[5,640,800,920,980];
   for(let k=0;k<37;k++)for(let j=0;j<5;j++){const p=0xc1000+168+k*10+j*2;flash[p]=points[j]&255;flash[p+1]=points[j]>>8;}
   flash.set(new TextEncoder().encode('trimdat\0'),0xc1000+548);
   writeFileSync('build/site-tests/'+r.id+'-synthetic-flash.bin',flash);
  }
  const bad=base.slice();bad[2000]^=1;await assert.rejects(buildFirmware(r,app,bad));
  const badApp=app.slice();badApp[99]^=1;await assert.rejects(buildFirmware(r,badApp,base),/checksum/);
  writeFileSync('build/site-tests/'+r.id+'.fwsc',result.factory);
  console.log('PASS:',r.board,'actual release package round trip, protected bytes, corruption rejection',result.factory.length,'bytes');
 }
}
