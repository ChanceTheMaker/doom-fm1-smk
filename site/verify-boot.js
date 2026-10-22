// SPDX-License-Identifier: GPL-3.0-only
import {Updater} from './vendor/fm1ota.js?v=release16';
// Read-only confirmation: never START, retry programming, or infer boot from transfer success.
export async function verifyDoomBoot(access,target,log=()=>{},timeout=30000){
  if(!['fm1','smk37-pro','smk37-elite'].includes(target))throw Error('Unknown Doom target');
  const model=target==='fm1'?'Doom-FM-1':'Doom-SMK-37';
  const revision=target==='fm1'?26:24;
  const up=new Updater(access,log,/doom/i);
  const dev=await up.waitForAny(id=>id.model===model&&id.version===revision,timeout);
  if(!dev){log('Boot NOT confirmed: expected '+model+'_'+String(revision).padStart(3,'0')+'. Keep power connected and save this log. No automatic retry.');return false;}
  try{log('Runtime USB identity confirmed: '+dev.id.text+'. Check game graphics, sound and controls on the device.');return true;}
  finally{await dev.link.close();}
}
