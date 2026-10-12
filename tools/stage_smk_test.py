#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Prepare a private Pro test kit from two verified stock reads; no device access."""
import argparse,hashlib,json,shutil,struct,sys,zlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools/vendor'))
from smk37_backup import inspect_backup
from smk37_test_image import replace_application
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--backups',nargs=2,type=Path,required=True)
p.add_argument('--stock-package',type=Path,required=True)
a=p.parse_args()
stock=a.backups[0].read_bytes();inspect_backup(stock,a.backups[1].read_bytes(),a.stock_package.read_bytes())
source=ROOT/'build/native/smk37-pro';manifest=json.loads((source/'manifest.json').read_text())
app=(source/manifest['image']).read_bytes()
sha=lambda b:hashlib.sha256(b).hexdigest()
if manifest['board']!='smk37-pro' or manifest['version']!='test02' or sha(app)!=manifest['sha256'] or manifest['flash_writes']:raise SystemExit('Unexpected native candidate')
image=replace_application(stock,app);lo,hi,header=0x4000,0x9d000,1024
if image[:lo]!=stock[:lo] or image[hi:]!=stock[hi:]:raise SystemExit('Protected data changed')
payload=image[lo:hi];h=bytearray(header);h[:16]=b'SMK37-SALT-USB1'.ljust(16,b'\0')
struct.pack_into('<7I',h,16,1,lo,hi,len(payload),zlib.crc32(stock[:lo]),zlib.crc32(stock[0xc1000:0xc1000+556]),zlib.crc32(payload))
h[48:80]=b'SMK-37_991'.ljust(32,b'\0');h[80:112]=b'DOOM SMK TEST02'.ljust(32,b'\0')
for i in range((hi-lo)//4096):struct.pack_into('<I',h,128+i*4,zlib.crc32(payload[i*4096:(i+1)*4096]))
struct.pack_into('<I',h,44,zlib.crc32(h));package=bytes(h)+payload
kit=ROOT/'build/try-smk-pro';site=kit/'site';site.mkdir(parents=True,exist_ok=True)
shutil.copytree(ROOT/'web',site,dirs_exist_ok=True)
(site/'doom-test02.smkupdate').write_bytes(package)
(kit/'doom-device-image.bin').write_bytes(image);(kit/'stock-restore.bin').write_bytes(stock)
release={'version':'Doom SMK Test02','board':'SMK-37 Pro','package':'doom-test02.smkupdate',
         'sha256':sha(package),'app_sha256':sha(app),'bytes':len(package),'private':True,'hardware_tested':False,
         'image_sha256':sha(image),'restore_sha256':sha(stock),'no_usb_after_boot':True}
(site/'candidate.json').write_text(json.dumps(release,indent=2)+'\n')
(kit/'manifest.json').write_text(json.dumps(release,indent=2)+'\n')
(kit/'README.txt').write_text('PRIVATE SMK-37 PRO DOOM TEST02\n\nNot for FM-1 or another SMK. Package is bound to the existing stock backup header and calibration CRC.\n\nInstall only while running updater-enabled Felucca/Sloop/Melodee SMK.\nDoom has NO USB MIDI updater. Normal USB disappearing after installation is expected.\nHave the XIAO SMK recovery adapter ready. Hold both OCT buttons for two seconds to request ROM recovery.\nIf software cannot reach recovery, use the same adapter power-off/USB-key procedure already used for this unit.\n\nStock restore image is the verified original backup. Never program it wholesale: preserve the current bootloader, calibration and all bytes outside 0x4000..0x9d000.\nRestoring application sectors requires a fresh read and bounded adapter write/readback, not an FM-1 writer.\n\nControls: lowest seven white piano keys = left, forward, right, back, fire, use, menu.\nNext four white keys = enter, run, strafe left, strafe right. PATCH = menu; PARA = enter.\nNo sound, pads, saves or additional levels in this test.\n\nExpected: DOOM TEST02 startup text, then a plain Miniwad room. Test display orientation and movement/fire.\nIf DOOM STOPPED appears, photograph the entire message; do not repeat installation.\n')
print('Private kit:',kit);print('Package SHA-256:',release['sha256'])
