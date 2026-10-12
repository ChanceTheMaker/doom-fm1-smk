// SPDX-License-Identifier: GPL-3.0-only
import {Package,logicalImage,sha256hex} from './vendor/fm1pkg.js';
import {buildSmkPublicPackage} from './vendor/smk37-package.js';
import {STOCK_SOURCES} from './vendor/smk37-stock.js';
import {Updater} from './vendor/fm1ota.js';
export const FM1_BASE='https://raw.githubusercontent.com/ChanceTheMaker/Felucca/ab9e880890eeda57a1772b2d1250f107a3e199c6/firmware/felucca-0.9-salt14.fwsc';
const BASE_SHA='efb516a7131d12eb5c008ff9af5a380d07e82eb1040bd03990f28d1233417e28';
export async function download(url){const r=await fetch(url,{cache:'no-store'});if(!r.ok)throw Error(`Download failed (${r.status}). Try again or provide the matching original firmware file.`);return new Uint8Array(await r.arrayBuffer());}
export async function buildFirmware(release,app,base){
 if(!release?.public||app.length!==release.bytes||await sha256hex(app)!==release.sha256||app.length%4||app[0]!==4||app[1]!==129||app[2]!==128||app[3]!==0)throw Error('Application identity, size or checksum failed. Nothing can be installed.');
 if(release.id!=='fm1')return buildSmkPublicPackage(base,app,release);
 if(release.board!=='FM-1'||release.product!=='FM-1_995'||await sha256hex(base)!==BASE_SHA)throw Error('Wrong FM-1 base or release.');
 const pkg=new Package(base);
 if(pkg.appBase!==0x4000||pkg.appOff!==0x4120||pkg.app.size!==0x8dfbc||pkg.flashSize!==0x93000||pkg.chipKey!==0x980f)throw Error('Unsupported FM-1 layout.');
 const before=pkg.flash.slice();pkg.setApp(app);pkg.setProduct(release.product);
 for(let i=0;i<before.length;i++)if(before[i]!==pkg.flash[i]&&!((i>=0x4000&&i<0x4004)||(i>=0x4020&&i<0x4024)||(i>=0x4120&&i<0x4120+0x8dfbc)))throw Error('Protected FM-1 bytes changed.');
 const factory=pkg.serialize(),checked=new Package(factory);
 if(checked.product!==release.product||checked.flash.some((v,i)=>v!==pkg.flash[i]))throw Error('FM-1 package round-trip failed.');
 return {factory,image:logicalImage(factory),version:release.version,product:release.product,sha:await sha256hex(factory)};
}
export function sourceFor(release){return release.id==='fm1'?FM1_BASE:STOCK_SOURCES[release.board];}
export async function installFm1(access,pkg,log,{confirmGeneric}={}){
 const up=new Updater(access,log,/fm-1|felucca|sloop|melodee|ota|composite|sinco|usb-midi/i);let link;
 try{
  let dev=await up.findAny(id=>id.model==='FM-1'||id.model==='ota-FM-1');
  if(!dev)throw Error('No updater-enabled FM-1 found. Already running Doom? Use the recovery adapter; Doom has no USB updater.');
  link=dev.link;
  if(dev.id.model==='ota-FM-1'&&(!confirmGeneric||!await confirmGeneric()))throw Error('FM-1 loader confirmation cancelled. No programming started.');
  if(dev.id.model==='FM-1'){
   log('Found '+dev.id.text+'. Loading the FM-1 update loader. Keep power connected.');
   if(!link.send([0xf0,0x22,0x24,0x35,0x7f,0xf7]))throw Error('FM-1 disconnected.');
   await new Promise(r=>setTimeout(r,2000));
   const r=await up.serve(link,pkg.image,0xe0000000,15000,n=>{if(n%64===0)log('Preparing loader: '+n);});
   await link.close();link=null;if(!r.finished)throw Error('Loader preparation stopped. Inspect the device; no automatic retry.');
   dev=await up.waitForAny(id=>id.model==='ota-FM-1',30000);if(!dev)throw Error('FM-1 loader did not appear. Save the log before retrying.');link=dev.link;
  }
  log('Installing Doom application. Do not disconnect power or USB.');
  const r=await up.write(dev,pkg.image,(step,n)=>{if(step==='write'&&n%64===0)log('Transfer request '+n);});link=null;
  if(!r.finished)throw Error('Transfer interrupted. Keep power connected and save the log.');
  log('Loader transfer complete. Doom has no USB MIDI identity; check the game on the physical screen.');
 }finally{await link?.close();}
}
