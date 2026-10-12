import assert from 'node:assert/strict';
import {Updater} from '../site/vendor/fm1ota.js?v=release14';
import {verifyDoomBoot} from '../site/verify-boot.js?v=release14';
const old=Updater.prototype.waitForAny;let identity,closed=0;
Updater.prototype.waitForAny=async function(filter){return identity&&filter(identity)?{id:identity,link:{close(){closed++;}}}:null;};
try{
 for(const target of ['fm1','smk37-pro','smk37-elite']){
   const expected=target==='fm1'?'Doom-FM-1':'Doom-SMK-37';
   for(const model of ['ota-'+expected,expected==='Doom-FM-1'?'Doom-SMK-37':'Doom-FM-1','SMK-37','FM-1']){
     identity={model,version:14};assert.equal(await verifyDoomBoot({},target),false);
   }
   identity=null;assert.equal(await verifyDoomBoot({},target),false);
   for(const version of [7,10,13,15]){
     identity={model:expected,version};assert.equal(await verifyDoomBoot({},target),false);
   }
   identity={model:expected,version:14,text:expected+'_014'};assert.equal(await verifyDoomBoot({},target),true);
 }
 assert.equal(closed,3);
 await assert.rejects(verifyDoomBoot({},'other'),/Unknown/);
 console.log('PASS: boot confirmation requires exact runtime model/version; absent, wrong and loader identities do not report success.');
}finally{Updater.prototype.waitForAny=old;}
