// SPDX-License-Identifier: GPL-3.0-only
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const source=readFileSync(new URL('../site/analytics.js',import.meta.url),'utf8');
function setup({host='chancethemaker.github.io',path='/doom-fm1-smk/',saved='',blocked=false}={}){
 const scripts=[],storage=new Map([['doom.fm1.smk.analyticsConsent',saved]]),handlers={},listeners={};
 const panel={setAttribute(){},querySelectorAll(){return[];},addEventListener(k,f){handlers[k]=f;},close(){}};
 const banner={setAttribute(){},querySelectorAll(){return[];},addEventListener(){}};
 const ctx={URL,Date,Set,location:{hostname:host,pathname:path,origin:'https://'+host,href:'https://'+host+path+'?private=yes'},
  localStorage:{getItem(k){if(blocked)throw Error('blocked');return storage.get(k);},setItem(k,v){if(blocked)throw Error('blocked');storage.set(k,v);}},
  document:{readyState:'loading',referrer:'https://example.org/private?secret=yes',createElement:n=>n==='dialog'?panel:n==='section'?banner:{},head:{append:s=>scripts.push(s)},addEventListener(k,f){listeners[k]=f;}},
  addEventListener(){}};
 ctx.window=ctx;vm.runInNewContext(source,ctx);
 return {ctx,scripts,banner,storage,choose(choice){handlers.click({target:{closest:s=>s==='[data-choice]'?{dataset:{choice}}:null}});}};
}
const fresh=setup();assert.equal(fresh.scripts.length,1);assert.equal(fresh.banner.hidden,false);
assert.match(fresh.scripts[0].src,/G-JVF09MZEGD$/);
const config=fresh.ctx.dataLayer.find(x=>x[0]==='config')[2];
assert.equal(config.product,'doom-fm1-smk');assert.equal(config.cookie_path,'/doom-fm1-smk/');
assert.equal(config.page_location,'https://chancethemaker.github.io/doom-fm1-smk/');assert.equal(config.page_referrer,'https://example.org');
assert.equal(config.allow_google_signals,false);assert.equal(config.allow_ad_personalization_signals,false);
fresh.ctx.DoomAnalytics.track('install_transfer_complete',{device_model:'smk37-elite',firmware_version:'test06',file_type:'fwsc',serial:'private',error_code:'unsafe raw message'});
let event=fresh.ctx.dataLayer.at(-1);assert.equal(event[1],'install_transfer_complete');assert.equal(event[2].device_model,'smk37-elite');assert.equal(event[2].serial,undefined);assert.equal(event[2].error_code,undefined);
const count=fresh.ctx.dataLayer.length;fresh.ctx.DoomAnalytics.track('install_success');assert.equal(fresh.ctx.dataLayer.length,count,'Do not claim a confirmed boot');
fresh.choose('denied');assert.equal(fresh.ctx['ga-disable-G-JVF09MZEGD'],true);assert.equal(fresh.banner.hidden,true);
const deniedCount=fresh.ctx.dataLayer.length;fresh.ctx.DoomAnalytics.track('download_click');assert.equal(fresh.ctx.dataLayer.length,deniedCount);
fresh.choose('granted');assert.equal(fresh.scripts.length,1,'No duplicate tag');assert.equal(fresh.ctx['ga-disable-G-JVF09MZEGD'],false);
for(const args of [{host:'localhost'},{host:'another.github.io'},{path:'/sloop-smk/'},{path:'/doom-fm1-smk-other/'},{saved:'denied'}])assert.equal(setup(args).scripts.length,0);
const basic=setup({saved:'basic'});assert.equal(basic.ctx.dataLayer.find(x=>x[0]==='consent'&&x[1]==='update')[2].analytics_storage,'denied');
assert.doesNotThrow(()=>setup({blocked:true}).choose('granted'));
console.log('Analytics: production isolation, same GA ID, opt-out, safe metadata and no false boot-success events passed.');
