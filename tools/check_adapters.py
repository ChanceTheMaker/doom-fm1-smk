#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Build and run the portable LCD and WAD boundary tests on Linux/WSL."""
import subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'build/tests';out.mkdir(parents=True,exist_ok=True)
for name in ('lcd_frame','wad_view'):
    binary=out/(name+'_test')
    subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror',
                    '-I'+str(ROOT/'src/common'),str(ROOT/'src/common'/(name+'.c')),
                    str(ROOT/'tests'/(name+'_test.c')),'-o',str(binary)],check=True)
    subprocess.run([str(binary)],check=True)
    print('PASS:',name)
