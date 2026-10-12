#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Stage an FM-1-only local Doom package from a pinned Felucca release. No device access."""
import argparse, hashlib, json, shutil, struct, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools/vendor'))
from fm1pkg_make import crc16, sfc, ufw, APP_SLOT
from smk37_package import inspect_bytes
from smk37_layout import entry
BASE_SHA = 'efb516a7131d12eb5c008ff9af5a380d07e82eb1040bd03990f28d1233417e28'
LOADER_SHA = '2c9f43bf7dff81a953c07f3c82cedf5f5899aac14e5b62c2cb23ba7f560ce7db'
def sha(b): return hashlib.sha256(b).hexdigest()
def unpack(raw):
    m = inspect_bytes(raw)
    if m['marker_blocks'] != 20: raise ValueError('Not an FM-1 container')
    logical = b''.join(raw[i:i+47] for i in range(0, 960, 48))+raw[960:]
    return m, {e['name']:logical[e['offset']:e['offset']+e['bytes']] for e in m['entries']}
def replace_app(flash, app):
    if len(flash) != 0x93000 or not app or len(app)%4 or app[:4] != bytes.fromhex('04818000'):
        raise ValueError('Unexpected FM-1 flash/application envelope')
    area = bytearray(flash[0x4000:]); sfc(area, 0, len(area), 0, 0x980f)
    h = entry(area[:32]); e = entry(area[32:64])
    if h['name'] != 'app_area_head' or h['offset'] != 0x02000120 or e['name'] != 'app.bin' or e['offset'] != 0x120 or e['bytes'] != APP_SLOT or len(app)>APP_SLOT:
        raise ValueError('Unexpected FM-1 application layout')
    extent=h['bytes']
    if not 0x120+APP_SLOT <= extent <= len(area): raise ValueError('Invalid block extent')
    if crc16(area[32:extent]) != h['stored_crc16'] or crc16(area[0x120:0x120+APP_SLOT]) != e['stored_crc16']:
        raise ValueError('Original application CRC mismatch')
    replacement=app+b'\xff'*(APP_SLOT-len(app));area[0x120:0x120+APP_SLOT]=replacement
    struct.pack_into('<H', area, 34, crc16(replacement))
    struct.pack_into('<H', area, 32, crc16(area[34:64]))
    struct.pack_into('<H', area, 2, crc16(area[32:extent]))
    struct.pack_into('<H', area, 0, crc16(area[2:32]))
    sfc(area,0,len(area),0,0x980f);result=flash[:0x4000]+bytes(area)
    allowed=((0x4000,0x4004),(0x4020,0x4024),(0x4120,0x4120+APP_SLOT))
    if any(a!=b and not any(lo<=i<hi for lo,hi in allowed) for i,(a,b) in enumerate(zip(flash,result))):
        raise ValueError('Changed data outside application/CRC fields')
    check=bytearray(result[0x4000:]);sfc(check,0,len(check),0,0x980f)
    if check[0x120:0x120+APP_SLOT]!=replacement or crc16(check[32:extent])!=entry(check[:32])['stored_crc16']:
        raise ValueError('Application round trip failed')
    return result
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True);a=p.parse_args()
    raw=a.base.read_bytes()
    if sha(raw)!=BASE_SHA: p.error('Expected pinned Felucca Salt14 FM-1 release')
    _,files=unpack(raw)
    if set(files)!={'flash.bin','ota.bin'} or sha(files['ota.bin'])!=LOADER_SHA: p.error('Unexpected loader')
    native=ROOT/'build/native/fm1';m=json.loads((native/'manifest.json').read_text());app=(native/m['image']).read_bytes()
    if m['board']!='fm1' or sha(app)!=m['sha256'] or m['flash_writes']: p.error('Unexpected application')
    flash=replace_app(files['flash.bin'],app);package=ufw(flash,files['ota.bin'],'FM-1_990')
    checked,back=unpack(package)
    if checked['product']!='FM-1_990' or back!={'flash.bin':flash,'ota.bin':files['ota.bin']}: p.error('Package round trip failed')
    kit=ROOT/'build/try-fm1';site=kit/'site';site.mkdir(parents=True,exist_ok=True)
    shutil.copytree(ROOT/'web/fm1',site,dirs_exist_ok=True)
    (site/'vendor').mkdir(exist_ok=True);shutil.copyfile(ROOT/'web/vendor/fm1ota.js',site/'vendor/fm1ota.js')
    (site/'doom-fm1-test01.fwsc').write_bytes(package)
    (kit/'doom-application-region.bin').write_bytes(flash[0x4000:0x93000])
    (kit/'felucca-salt14-restore.fwsc').write_bytes(raw)
    (kit/'felucca-restore-application-region.bin').write_bytes(files['flash.bin'][0x4000:0x93000])
    manifest={'board':'FM-1','version':'Doom FM-1 Test01','product':'FM-1_990','package':'doom-fm1-test01.fwsc',
              'sha256':sha(package),'app_sha256':sha(app),'bytes':len(package),'hardware_tested':False,
              'usb_updater':False,'base_sha256':BASE_SHA,'loader_sha256':LOADER_SHA,
              'application_write_start':'0x4000','application_write_end':'0x93000'}
    (site/'candidate.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (kit/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    shutil.copyfile(ROOT/'docs/FM1_TEST01.md',kit/'README.md')
    shutil.copyfile(ROOT/'LICENSE',site/'LICENSE')
    shutil.copyfile(ROOT/'licenses/miniwad.txt',site/'miniwad-LICENSE.txt')
    shutil.copyfile(ROOT/'licenses/Apache-2.0.txt',site/'Apache-2.0.txt')
    print(json.dumps(manifest,indent=2));print('Local FM-1 kit:',kit)
if __name__=='__main__': main()
