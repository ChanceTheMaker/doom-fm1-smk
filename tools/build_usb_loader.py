#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Build a model-bounded RAM updater and embed it in Doom. No device access."""
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def build(tc,out,board):
    src=ROOT/'src/native';ldr=src/'update';gen=out/'update';gen.mkdir(exist_ok=True)
    product=('Doom-FM-1' if board=='fm1' else 'Doom-SMK-37')+'_014'
    (gen/'doom_update_config.h').write_text('#define DP_UPDATE_PRODUCT "'+product+'"\n')
    (gen/'smk37_unit.h').write_text('#define SMK37_PUBLIC_BUILD 1\n#define SMK37_UNIT_HEAD_CRC 0x3a04ad23u\n#define SMK37_UNIT_TRIM_CRC 0u\n')
    cc=tc/'pi32v2/bin/clang';ld=tc/'pi32v2/bin/ld';obj=tc/'common/bin/objcopy';dump=tc/'common/bin/objdump'
    flags=['-target','pi32v2','-mcpu=r3','-mfprev1','-Os','-ffunction-sections','-fdata-sections','-fno-builtin','-std=gnu11','-isystem',str(tc/'pi32v2/include'),'-I'+str(src/'hal'),'-I'+str(gen)]
    for source,name in [(ldr/'crt0_ldr.S','start'),(ldr/('loader.c' if board=='fm1' else 'smk37_loader.c'),'loader')]:
        result=subprocess.run([str(cc),*flags,'-c',str(source),'-o',str(gen/(name+'.o'))],capture_output=True,text=True)
        (gen/(name+'.log')).write_text(result.stdout+result.stderr)
        if result.returncode:raise RuntimeError(result.stderr)
    elf=gen/'loader.elf';binary=gen/'loader.bin'
    subprocess.run([str(ld),'--gc-sections','-e','_start','-T',str(ldr/'loader.ld'),str(gen/'start.o'),str(gen/'loader.o'),'-o',str(elf)],check=True)
    symbols=subprocess.check_output([str(dump),'-t',str(elf)],text=True)
    sections=subprocess.check_output([str(dump),'-h',str(elf)],text=True)
    (gen/'symbols.txt').write_text(symbols);(gen/'sections.txt').write_text(sections)
    for name in ['_start','_bss_end','fl_read_ram','fl_prog_ram','fl_erase4k_ram','ldr_session' if board=='fm1' else 'smku_session']:
        m=re.search(r'^([0-9a-f]+) .*\s'+name+'$',symbols,re.M)
        if not m or not 0x1c0a800<=int(m[1],16)<0x1c1e800:raise ValueError('Loader RAM symbol invalid: '+name)
    for line in sections.splitlines():
        p=line.split()
        if len(p)>5 and p[0].isdigit() and int(p[2],16) and p[1] not in ('.symtab','.strtab','.shstrtab'):
            address=int(p[3],16);size=int(p[2],16)
            if not 0x1c0a800<=address<=address+size<=0x1c1e800:raise ValueError('Loader section outside RAM: '+line)
    if re.search(r'\b(?:ota_session|ota_commit|ota_stage)\b',symbols):raise ValueError('Flash staging must not link')
    subprocess.run([str(obj),'-O','binary','-j','.text',str(elf),str(binary)],check=True)
    data=binary.read_bytes()
    if len(data)>0x14000:raise ValueError('Loader too large')
    body=product.encode().ljust(27,b'\0');message=bytes([0,0x59,0x11,27,0,0])+body+bytes([~sum(body)&255])
    packed=[];acc=bits=0
    for b in message:
        acc|=b<<bits;bits+=8
        while bits>=7:packed.append(acc&127);acc>>=7;bits-=7
    if bits:packed.append(acc&127)
    def array(name,raw):return 'static const uint8_t '+name+'[]={'+','.join(map(str,raw))+'};\n'
    (gen/'doom_loader_image.h').write_text(array('dp_loader_image',data)+array('dp_identity_wire',[0xf0,*packed,0xf7]))
    report={'product':product,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'entry':'0x01c0a800','write_lo':'0x4000','write_hi':'0x93000' if board=='fm1' else '0x9d000','flash_staging':False}
    (gen/'manifest.json').write_text(json.dumps(report,indent=2)+'\n')
    return gen,report
