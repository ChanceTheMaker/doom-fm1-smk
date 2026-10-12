# SPDX-License-Identifier: GPL-3.0-only
"""Validate the staged FM-1 package, including unhashed container padding."""
import hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from stage_fm1_test import unpack
site=Path(__file__).resolve().parents[1]/'build/try-fm1/site'
m=json.loads((site/'candidate.json').read_text());b=(site/m['package']).read_bytes()
assert hashlib.sha256(b).hexdigest()==m['sha256']
r,files=unpack(b);assert r['product']=='FM-1_994'
assert hashlib.sha256(files['ota.bin']).hexdigest()==m['loader_sha256']
# 1024 is package padding: the full SHA check covers it even though payload CRCs do not.
for at in (10,1024,1044,2000,len(b)-1):
    damaged=bytearray(b);damaged[at]^=1
    assert hashlib.sha256(damaged).hexdigest()!=m['sha256']
    if at==1024: continue
    try: unpack(bytes(damaged))
    except ValueError: pass
    else: raise AssertionError('Payload/header corruption accepted at '+str(at))
print('PASS: FM-1 identity, SHA, retained loader, payload/header CRC and padding-hash checks')
