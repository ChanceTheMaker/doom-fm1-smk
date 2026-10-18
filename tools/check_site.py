#!/usr/bin/env python3
"""Check deploy allowlist, release hashes and local page references; no device I/O."""
import hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'site'
releases=json.loads((root/'firmware/releases.json').read_text())
assert {r['id'] for r in releases}=={'fm1','smk37-pro','smk37-elite'}
archived=sum((json.loads((root/'firmware'/name).read_text()) for name in
              ['archive-test07.json','archive-test08.json','archive-release10.json','archive-release14.json','archive-release15.json','archive-release16.json']),[])
apps=set()
for r in releases+archived:
    p=root/'firmware'/r['app'];b=p.read_bytes();apps.add(p)
    assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],p
    assert b[:4]==bytes.fromhex('04818000') and r['public'] is True,p
    number=int(re.search(r'TEST(\d+)$',r['version'])[1])
    assert number==(16 if r['id']=='fm1' else 17) if r in releases else number in (7,8,10,14,15,16),p
    version,product=f'TEST{number:02d}',{7:'_996',8:'_997',10:'_999',14:'_999',15:'_999',16:'_999',17:'_999'}[number]
    assert r['version'].endswith(version) and r['product'].endswith(product),p
    suffix=str(number) if number>=10 else version.lower()
    assert r['app']==f"doom-{r['id']}-{suffix}.bin",p
stock=root/'restore-stock/FM-1-v15.fwsc'
assert stock.stat().st_size==699956 and hashlib.sha256(stock.read_bytes()).hexdigest()=='db1642b2b6fa5c2cccb11ffd13878068bb28601678d3644049f99dc40e7edb8a'
sim=root/'simulator'
build=json.loads((sim/'build.json').read_text())
assert set(build['files'])=={'doom-engine.js','doom-engine.wasm'}
for name,digest in build['files'].items():
    assert hashlib.sha256((sim/name).read_bytes()).hexdigest()==digest,name
assert (sim/'doom-engine.wasm').read_bytes()[:4]==b'\0asm'
assert build['wad_sha256']==build['artwork']['sha256']
for p in root.rglob('*'):
    if not p.is_file():continue
    assert p==stock or p.suffix.lower() not in {'.fwsc','.smkupdate','.wad','.elf','.map'},p
    assert p.suffix!='.bin' or p in apps,p
    if p.suffix=='.html':
        for link in re.findall(r'(?:href|src)="([^"]+)"',p.read_text(encoding='utf-8')):
            link=link.split('#')[0].split('?')[0]
            if link and not re.match(r'[a-z]+:',link):assert (p.parent/link).exists(),(p,link)
print('Site release hashes, entry points, artifact allowlist and local links passed.')
