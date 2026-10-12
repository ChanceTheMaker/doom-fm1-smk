#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Build an application-only Doom test image. Does not connect to or flash devices."""
import argparse,hashlib,json,os,re,subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from prepare_engine import prepare,ROOT,UPSTREAM
from static_wad import freeze
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--board',required=True,choices=['fm1','smk37-pro','smk37-elite'])
p.add_argument('--toolchain',type=Path,default=os.environ.get('JIELI_TOOLCHAIN'))
a=p.parse_args()
if not a.toolchain:p.error('Set JIELI_TOOLCHAIN or pass --toolchain')
tc=Path(a.toolchain).resolve();cc=tc/'pi32v2/bin/clang';ld=tc/'pi32v2/bin/ld';objcopy=tc/'common/bin/objcopy';objdump=tc/'common/bin/objdump'
if not cc.exists():p.error('Native compiler not found')
out=ROOT/'build/native'/a.board;out.mkdir(parents=True,exist_ok=True)
engine=prepare(out/'engine');native=ROOT/'src/native';common=ROOT/'src/common'
# The native display frontend consumes the indexed framebuffer directly.
path=engine/'i_video.c';text=path.read_text();start=text.index('void I_FinishUpdate (void)');end=text.index('\n}',start)+2
text=text[:start]+'void I_FinishUpdate(void) { DG_DrawFrame(); }'+text[end:];path.write_text(text)
wad=ROOT/'build/fixtures/miniwad-room.wad'
if not wad.exists() or hashlib.sha256(wad.read_bytes()).hexdigest()!='5382808534297f82d29873d9132410dcb20f314e01f58f1ec4c653f7f0ddf98d':p.error('Build the pinned trimmed-room fixture first')
lump_count=freeze(engine,wad)
asset=out/'wad.S';asset.write_text('.section .rodata.wad,"a",@progbits\n.balign 4\n.globl dp_wad_start\n.globl dp_wad_end\ndp_wad_start:\n.incbin "'+wad.as_posix()+'"\ndp_wad_end:\n')
line=re.search(r'^SRC_DOOM\s*=\s*(.+)$',(UPSTREAM/'Makefile').read_text(),re.M)
sources=[engine/(name[:-2]+'.c') for name in line[1].split() if name!='doomgeneric_xlib.o']
replace={'i_system.c':native/'system.c','w_file_stdc.c':native/'w_file_flash.c',
         'doomgeneric.c':common/'doomgeneric_create.c','f_wipe.c':common/'wipe_disabled.c'}
sources=[replace.get(s.name,s) for s in sources]
sources += [common/'lcd_frame.c',common/'wad_view.c',native/'doomgeneric_native.c',native/'libc_support.c',ROOT/'third_party/printf/printf.c',
            native/'syscalls.c',native/'board.c',native/'crt0.S',native/'hal/fm1_vec.S',asset]
flags=['-target','pi32v2','-mcpu=r3','-mfprev1','-Os','-ffunction-sections','-fdata-sections',
       '-isystem',str(tc/'pi32v2/include'),
       '-fno-builtin','-std=gnu11','-DDOOMGENERIC_RESX=320','-DDOOMGENERIC_RESY=200',
       '-DCMAP256','-DNORMALUNIX','-DLINUX','-DMELODEE_DUAL_CORE=0','-DMELODEE_CACHE_RAM=0',
       '-DDP_SMK='+('0' if a.board=='fm1' else '1'),'-I'+str(engine),'-I'+str(common),
       '-I'+str(native),'-I'+str(native/'hal')]
def compile_one(src):
    obj=out/(src.stem+'.o')
    result=subprocess.run([str(cc),*flags,'-c',str(src),'-o',str(obj)],capture_output=True,text=True)
    (out/(src.stem+'.log')).write_text(result.stdout+result.stderr)
    return (obj,result.returncode,result.stderr)
with ThreadPoolExecutor(4) as pool:compiled=list(pool.map(compile_one,sources))
errors=[str(o)+':\n'+err for o,code,err in compiled if code]
if errors:raise SystemExit('\n'.join(errors))
objects=[o for o,_,_ in compiled]
elf=out/'doom-test02.elf'
libs=tc/'pi32v2/lib/r3'
cmd=[str(ld),'--gc-sections','-T',str(native/'app.ld'),*[str(o) for o in objects],
     '-L'+str(libs),'--start-group','-lc','-lm','-lcompiler_rt','--end-group','-o',str(elf)]
result=subprocess.run(cmd,capture_output=True,text=True);(out/'link.log').write_text(result.stdout+result.stderr)
if result.returncode:raise SystemExit(result.stderr)
symbols=subprocess.check_output([str(objdump),'-t',str(elf)],text=True)
(out/'symbols.txt').write_text(symbols)
(out/'sections.txt').write_text(subprocess.check_output([str(objdump),'-h',str(elf)],text=True))
def sym(name):return int(re.search(r'^([0-9a-f]+) .*\s'+re.escape(name)+r'$',symbols,re.M)[1],16)
image=bytearray()
for section,address in [('.text',0x02000120),('.data',sym('_data_load'))]:
    part=out/(section[1:]+'.bin')
    subprocess.run([str(objcopy),'-O','binary','-j',section,str(elf),str(part)],check=True)
    blob=part.read_bytes();offset=address-0x02000120
    if offset<len(image):raise SystemExit('Overlapping load sections')
    image.extend(b'\xff'*(offset-len(image)));image.extend(blob)
image.extend(b'\xff'*(-len(image)%4))
if sym('_start')!=0x02000120 or len(image)>0x8dfbc or sym('_bss_end')>0x01c74000:raise SystemExit('Native application bounds failed')
path=out/('doom-'+a.board+'-test02.bin');path.write_bytes(image)
report={'board':a.board,'kind':'native-application-only','hardware_tested':False,'version':'test02',
        'image':path.name,'bytes':len(image),'sha256':hashlib.sha256(image).hexdigest(),
        'entry':hex(sym('_start')),'bss_end':hex(sym('_bss_end')),'ram_data_bss':sym('_bss_end')-sym('_data_start'),
        'static_lump_count':lump_count,'directory_storage':'XIP','zone_bytes':256*1024,'libc_heap_bytes':24*1024,'audio':False,'flash_writes':False,
        'usb_updater':False,'assets':'Miniwad MAP01 trimmed','install_package':False}
(out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
