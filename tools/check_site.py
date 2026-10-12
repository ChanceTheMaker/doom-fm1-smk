#!/usr/bin/env python3
"""Check deploy allowlist, release hashes and local page references; no device I/O."""
import hashlib,json,re
from pathlib import Path
root=Path(__file__).resolve().parents[1]/'site'
releases=json.loads((root/'firmware/releases.json').read_text())
assert {r['id'] for r in releases}=={'fm1','smk37-pro','smk37-elite'}
apps=set()
for r in releases:
    p=root/'firmware'/r['app'];b=p.read_bytes();apps.add(p)
    assert len(b)==r['bytes'] and hashlib.sha256(b).hexdigest()==r['sha256'],p
    assert b[:4]==bytes.fromhex('04818000') and r['public'] is True,p
    assert r['version'].endswith('TEST07') and r['product'].endswith('_996'),p
for p in root.rglob('*'):
    if not p.is_file():continue
    assert p.suffix.lower() not in {'.fwsc','.smkupdate','.wad','.elf','.map'},p
    assert p.suffix!='.bin' or p in apps,p
    if p.suffix=='.html':
        for link in re.findall(r'(?:href|src)="([^"]+)"',p.read_text(encoding='utf-8')):
            link=link.split('#')[0].split('?')[0]
            if link and not re.match(r'[a-z]+:',link):assert (p.parent/link).exists(),(p,link)
print('Site release hashes, entry points, artifact allowlist and local links passed.')
