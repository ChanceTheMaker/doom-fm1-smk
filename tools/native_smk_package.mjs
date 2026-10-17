// SPDX-License-Identifier: GPL-3.0-only
// Reuse Doom's verified public package builders; never accept caller firmware.
import fs from 'node:fs/promises';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {buildSmkPublicPackage,smkLogicalImage} from '../site/vendor/smk37-package.js';
import {buildSmkStock} from '../site/restore-stock/package-smk.js';
import {sha256hex} from '../site/vendor/fm1pkg.js';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const [action,mode,out]=process.argv.slice(2);
if(!['install','restore'].includes(action)||mode!=='public'||!out)throw Error('Invalid local installer request');
const stock=new Uint8Array(await fs.readFile(path.join(root,'build/smk37/stock-pro.fwsc')));
const original=await buildSmkStock(stock,'SMK-37 Pro');
let image,packet,expected;
if(action==='restore'){
  image=smkLogicalImage(stock).raw;packet=original.bytes;expected=original.product;
}else{
  const releases=JSON.parse(await fs.readFile(path.join(root,'site/firmware/releases.json'),'utf8'));
  const release=releases.find(r=>r.id==='smk37-pro');
  if(release?.product!=='SMK-37_999'||release.app!=='doom-smk37-pro-16.bin'||release.sha256!=='6c0c0cb7172b7ef7257cc2e2195c4c169d3264f73c5527f9fec19a8f694c6840')throw Error('Unrecognized Doom public release');
  const app=new Uint8Array(await fs.readFile(path.join(root,'site/firmware',release.app)));
  const built=await buildSmkPublicPackage(stock,app,release);
  if(built.stockModel!=='SMK-37 Pro')throw Error('Incorrect physical model');
  image=built.image;packet=built.bytes;expected='Doom-SMK-37_016';
}
await fs.mkdir(out,{recursive:true});
await fs.writeFile(path.join(out,'image.bin'),image);
await fs.writeFile(path.join(out,'packet.bin'),packet);
await fs.writeFile(path.join(out,'verified.json'),JSON.stringify({model:'SMK-37 Pro',expected,image:{bytes:image.length,sha256:await sha256hex(image)},packet:{bytes:packet.length,sha256:await sha256hex(packet)}}));
