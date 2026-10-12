#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Explicitly fetch the small open-content Miniwad fixture; never runs a binary."""
import hashlib, io, json, urllib.request, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL='https://soulsphere.org/random/miniwad.zip'
ZIP_SHA='b4c9804343be34e485fddab802c18ecf836168d733c2f03441d8a9dff80b2393'
WAD_SHA='daed5e9dc341a9ff4b9c6901cb8467a630bd31b87f3ecb58a93a8b2bc186fbfb'
with urllib.request.urlopen(URL,timeout=30) as r:
    blob=r.read(2*1024*1024)
if hashlib.sha256(blob).hexdigest()!=ZIP_SHA:raise SystemExit('Miniwad archive hash changed; review the source before updating the pin.')
with zipfile.ZipFile(io.BytesIO(blob)) as z:
    if z.getinfo('miniwad.wad').file_size!=230497:raise SystemExit('Unexpected Miniwad size')
    wad=z.read('miniwad.wad')
if hashlib.sha256(wad).hexdigest()!=WAD_SHA:raise SystemExit('Miniwad content hash mismatch')
out=ROOT/'build/fixtures';out.mkdir(parents=True,exist_ok=True)
(out/'miniwad.wad').write_bytes(wad)
(out/'miniwad-license.txt').write_bytes((ROOT/'licenses/miniwad.txt').read_bytes())
(out/'miniwad-provenance.json').write_text(json.dumps({'url':URL,'archive_sha256':ZIP_SHA,'wad_sha256':WAD_SHA,'bytes':len(wad),'project':'https://github.com/fragglet/miniwad'},indent=2)+'\n')
print('Verified open-content Miniwad:',out/'miniwad.wad')
