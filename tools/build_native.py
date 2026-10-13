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
p.add_argument('--campaign',action='store_true',help='Build the nine-level dual-core campaign')
p.add_argument('--revision',type=int,default=16,help='Distinct firmware identity and output revision')
p.add_argument('--toolchain',type=Path,default=os.environ.get('JIELI_TOOLCHAIN'))
a=p.parse_args()
if not a.toolchain:p.error('Set JIELI_TOOLCHAIN or pass --toolchain')
if not 16<=a.revision<=999:p.error('New candidates must use revision 16..999; published revisions are immutable')
tc=Path(a.toolchain).resolve();cc=tc/'pi32v2/bin/clang';ld=tc/'pi32v2/bin/ld';objcopy=tc/'common/bin/objcopy';objdump=tc/'common/bin/objdump'
if not cc.exists():p.error('Native compiler not found')
out=ROOT/'build/native'/a.board;out.mkdir(parents=True,exist_ok=True)
version='test'+str(a.revision) if a.campaign else 'test04'
engine=prepare(out/'engine',campaign=a.campaign);native=ROOT/'src/native';common=ROOT/'src/common'
# The native display frontend consumes the indexed framebuffer directly.
path=engine/'i_video.c';text=path.read_text();start=text.index('void I_FinishUpdate (void)');end=text.index('\n}',start)+2
text=text[:start]+'void I_FinishUpdate(void) { DG_DrawFrame(); }'+text[end:];path.write_text(text)
wad=ROOT/'build/fixtures'/('native-art.wad' if a.campaign else 'miniwad-room.wad')
if not wad.exists():p.error('Build the selected pinned fixture first')
lump_count=freeze(engine,wad,campaign=a.campaign,expected_sha=json.loads(wad.with_suffix('.json').read_text())['sha256'] if a.campaign else None)
asset=out/'wad.S';asset.write_text('.section .rodata.wad,"a",@progbits\n.balign 4\n.globl dp_wad_start\n.globl dp_wad_end\ndp_wad_start:\n.incbin "'+wad.as_posix()+'"\ndp_wad_end:\n')
line=re.search(r'^SRC_DOOM\s*=\s*(.+)$',(UPSTREAM/'Makefile').read_text(),re.M)
sources=[engine/(name[:-2]+'.c') for name in line[1].split() if name!='doomgeneric_xlib.o']
replace={'i_system.c':native/'system.c','w_file_stdc.c':native/'w_file_flash.c',
         'doomgeneric.c':common/'doomgeneric_create.c','f_wipe.c':common/'wipe_disabled.c'}
sources=[replace.get(s.name,s) for s in sources]
sources += [common/'lcd_frame.c',common/'menu_view.c',common/'wad_view.c',native/'doomgeneric_native.c',native/'libc_support.c',ROOT/'third_party/printf/printf.c',
            native/'syscalls.c',native/'board.c',native/'crt0.S',native/'hal/fm1_vec.S',asset]
flags=['-target','pi32v2','-mcpu=r3','-mfprev1','-Os','-ffunction-sections','-fdata-sections',
       '-isystem',str(tc/'pi32v2/include'),
       '-fno-builtin','-std=gnu11','-DDOOMGENERIC_RESX=320','-DDOOMGENERIC_RESY=200',
       '-DCMAP256','-DNORMALUNIX','-DLINUX','-DMELODEE_DUAL_CORE='+('1' if a.campaign else '0'),'-DMELODEE_CACHE_RAM=0','-DDP_DUAL_CORE='+('1' if a.campaign else '0'),
       '-DDP_SMK='+('0' if a.board=='fm1' else '1'),'-I'+str(engine),'-I'+str(common),
       '-I'+str(native),'-I'+str(native/'hal')]
if a.campaign:
    sources.extend([common/'campaign.c',common/'sfx.c',common/'music.c',common/'game_sound.c',common/'native_hud.c',ROOT/'src/browser/browser_splash.c',native/'audio_isr.S']);flags+=['-DDP_CAMPAIGN','-DDP_NATIVE_ART','-DDP_NATIVE_AUDIO','-DDP_ELITE='+('1' if a.board=='smk37-elite' else '0')]
    from build_usb_loader import build as build_loader
    gen,loader_report=build_loader(tc,out,a.board,revision=a.revision)
    flags+=['-DDP_USB_UPDATE','-I'+str(gen)]

def compile_one(src):
    obj=out/(src.stem+'.o')
    result=subprocess.run([str(cc),*flags,'-c',str(src),'-o',str(obj)],capture_output=True,text=True)
    (out/(src.stem+'.log')).write_text(result.stdout+result.stderr)
    return (obj,result.returncode,result.stderr)
with ThreadPoolExecutor(4) as pool:compiled=list(pool.map(compile_one,sources))
errors=[str(o)+':\n'+err for o,code,err in compiled if code]
if errors:raise SystemExit('\n'.join(errors))
objects=[o for o,_,_ in compiled]
elf=out/('doom-'+version+'.elf')
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
if a.campaign:
    if not sym('_data_start')<=sym('audio_worker_loop')<sym('_data_end'):raise SystemExit('CPU1 polling loop must run in SRAM')
    if not 0x01c7c000<=sym('_cpu1_stacks_lo')<sym('_cpu1_stacks_hi')<=0x01c7fd50:raise SystemExit('CPU1 private stack bounds failed')
path=out/('doom-'+a.board+'-'+version+'.bin');path.write_bytes(image)
report={'board':a.board,'kind':'native-application-only','hardware_tested':False,'version':version,
        'image':path.name,'bytes':len(image),'sha256':hashlib.sha256(image).hexdigest(),
        'entry':hex(sym('_start')),'bss_end':hex(sym('_bss_end')),'ram_data_bss':sym('_bss_end')-sym('_data_start'),
        'dual_core':a.campaign,'audio_worker':'CPU1 with serial fallback' if a.campaign else None,
        'cpu1_stack_bytes':sym('_cpu1_stacks_hi')-sym('_cpu1_stacks_lo'),
        'static_lump_count':lump_count,'directory_storage':'XIP','zone_bytes':256*1024,'libc_heap_bytes':24*1024,'audio':a.campaign,'flash_writes':False,
        'usb_updater':a.campaign,'loader':loader_report if a.campaign else None,'assets':'Freedoom front-facing enemies and face HUD over original Miniwad campaign' if a.campaign else 'Miniwad MAP01 trimmed','campaign':a.campaign,'wad_sha256':hashlib.sha256(wad.read_bytes()).hexdigest(),'install_package':False}
(out/'manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
