#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Explicit local HAL import with per-file provenance; never imports firmware images."""
import hashlib,json,re,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
donor=Path(sys.argv[1]).resolve();source=donor/'firmware/hal'
out=ROOT/'src/native/hal';out.mkdir(parents=True,exist_ok=True)
names=['fm1_time.h','fm1_sys.h','fm1_irq.h','fm1_input.h','fm1_lcd_hw.h','fm1_vec.S','fm1_audio.h','smk37_audio.h',
       'smk37_lcd_hw.h','smk37_panel.h','smk37_boot.h','smk37_time.h','smk37_scanner.h',
       'smk37_contacts.h','smk37_keyscan.h','smk37_controls.h']
files={}
while names:
    name=names.pop()
    if name in files:continue
    data=(source/name).read_bytes()
    files[name]=hashlib.sha256(data).hexdigest()
    (out/name).write_bytes(data)
    for include in re.findall(r'#include "([^"]+)"',data.decode()):
        if (source/include).exists():names.append(include)
revision=subprocess.check_output(['git','-C',str(donor),'rev-parse','HEAD'],text=True).strip()
(out/'PROVENANCE.json').write_text(json.dumps({'repository':'https://github.com/ChanceTheMaker/melodee-smk',
    'revision':revision,'source_directory':'firmware/hal','files_sha256':files,
    'note':'Exact local source hashes recorded; original per-file notices retained.'},indent=2)+'\n')
print('Imported',len(files),'HAL files at',revision)
