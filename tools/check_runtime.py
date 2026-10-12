#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Test the native runtime on host without interposing on the host C library."""
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'build/runtime-tests';out.mkdir(parents=True,exist_ok=True)
names='malloc free calloc realloc vsnprintf snprintf printf fprintf puts fopen fclose fread fwrite fseek ftell fflush remove rename exit'.split()
flags=['-std=gnu11','-O1','-g','-fno-builtin','-fsanitize=address,undefined']
rename=['-D'+s+'=dp_'+s for s in names]+['-DDP_SCANF=dp_sscanf']
sources=[ROOT/'src/native/libc_support.c',ROOT/'src/native/syscalls.c',ROOT/'third_party/printf/printf.c',ROOT/'tests/native_runtime_test.c']
objects=[]
for i,src in enumerate(sources):
    obj=out/(src.stem+'.o');objects.append(obj)
    subprocess.run(['cc',*flags,*(rename if i==0 else []),'-c',str(src),'-o',str(obj)],check=True)
exe=out/'runtime-test'
subprocess.run(['cc',*flags,*map(str,objects),'-o',str(exe)],check=True)
subprocess.run([str(exe)],check=True)
