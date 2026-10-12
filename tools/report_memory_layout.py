#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Record host static sections and compiler stack frames, not device RAM usage."""
import argparse,json,subprocess
from pathlib import Path
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('executable',type=Path)
a=p.parse_args();exe=a.executable.resolve()
line=subprocess.check_output(['size',str(exe)],text=True).splitlines()[1].split()
text,data,bss=map(int,line[:3])
symbols=[]
for line in subprocess.check_output(['nm','-S','--size-sort',str(exe)],text=True).splitlines():
    fields=line.split()
    if len(fields)==4 and fields[2] in 'bBdD':
        symbols.append({'name':fields[3],'bytes':int(fields[1],16),'section':fields[2]})
frames=[]
for path in exe.parent.glob(exe.name+'-*.su'):
    for line in path.read_text().splitlines():
        fields=line.split('\t')
        if len(fields)==3:
            frames.append({'function':fields[0].rsplit(':',1)[-1],
                           'bytes':int(fields[1]),'kind':fields[2]})
report={'scope':'host ELF only; ABI differs from native pi32v2; stack frames are not whole-call-chain peaks',
        'text_bytes':text,'data_bytes':data,'bss_bytes':bss,'static_writable_bytes':data+bss,
        'largest_writable_symbols':sorted(symbols,key=lambda s:s['bytes'],reverse=True)[:16],
        'largest_compiler_stack_frames':sorted(frames,key=lambda s:s['bytes'],reverse=True)[:12]}
(exe.parent/'layout.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
