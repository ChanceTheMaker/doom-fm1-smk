# SPDX-License-Identifier: GPL-3.0-only
"""Compile the unchanged source logo to a bounded LCD scanline asset."""
import hashlib,json,struct
from pathlib import Path
from PIL import Image
ROOT=Path(__file__).resolve().parents[1]
def build_logo():
    root=ROOT/'assets/branding';meta=json.loads((root/'provenance.json').read_text())
    source=root/'doom-classic.png'
    if hashlib.sha256(source.read_bytes()).hexdigest()!=meta['sha256']:raise ValueError('Logo source mismatch')
    im=Image.open(source).convert('RGBA');im=im.resize((192,round(im.height*192/im.width)),Image.Resampling.LANCZOS)
    indexed=im.convert('RGB').quantize(colors=15,method=Image.Quantize.MEDIANCUT,dither=Image.Dither.NONE)
    pal=indexed.getpalette();out=bytearray(struct.pack('<HH',im.width,im.height)+b'\0\0')
    for i in range(15):
        r,g,b=pal[i*3:i*3+3];out.extend(struct.pack('<H',((r>>3)<<11)|((g>>2)<<5)|(b>>3)))
    px=list(indexed.getdata());alpha=list(im.getchannel('A').getdata())
    for i in range(0,len(px),2):
        a=px[i]+1 if alpha[i]>=128 else 0;b=px[i+1]+1 if alpha[i+1]>=128 else 0
        out.append(a|(b<<4))
    return bytes(out)
