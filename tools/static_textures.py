# SPDX-License-Identifier: GPL-3.0-only
"""Precompose this fixed room's multi-patch columns into deduplicated XIP data.
The pinned WAD is checked by static_wad before calling this generator.
"""
import json, re, struct

def freeze_textures(engine, data):
    _, n, directory=struct.unpack_from('<4sII',data)
    lumps={}
    for i in range(n):
        off,size,name=struct.unpack_from('<II8s',data,directory+16*i)
        lumps[name.rstrip(b'\0').decode('ascii')]=data[off:off+size]
    pn=lumps['PNAMES']
    names=[pn[4+i*8:12+i*8].rstrip(b'\0').decode('ascii') for i in range(struct.unpack_from('<I',pn)[0])]
    sides=lumps['SIDEDEFS']
    needed={sides[i+j:i+j+8].rstrip(b'\0').decode('ascii') for i in range(0,len(sides),30) for j in (4,12,20)}
    needed.update(('SKY1','SKY2','SKY3'))
    switches=re.findall(r'\{\s*"(SW[12][A-Z0-9]+)"\s*,\s*"(SW[12][A-Z0-9]+)"',(engine/'p_switch.c').read_text())
    for pair in switches:
        if needed.intersection(pair): needed.update(pair)
    t=lumps['TEXTURE1'];records=[]
    for i in range(struct.unpack_from('<I',t)[0]):
        off=struct.unpack_from('<I',t,4+i*4)[0]
        name=t[off:off+8].rstrip(b'\0').decode('ascii')
        records.append((name,off))
    texture_names=[name for name,_ in records]
    animations=re.findall(r'\{true,\s*"([A-Z0-9]+)"\s*,\s*"([A-Z0-9]+)"',(engine/'p_spec.c').read_text())
    for end,start in animations:
        if start in texture_names and end in texture_names:
            cycle=texture_names[texture_names.index(start):texture_names.index(end)+1]
            if needed.intersection(cycle):needed.update(cycle)
    unique={};blob=bytearray();tables=[];report=[]
    for index,(name,off) in enumerate(records):
        if name not in needed:continue
        w,h=struct.unpack_from('<hh',t,off+12);np=struct.unpack_from('<h',t,off+20)[0]
        assert 0<w<=1024 and 0<h<=256
        hits=[0]*w;patches=[]
        for i in range(np):
            ox,oy,k=struct.unpack_from('<hhh',t,off+22+i*10)
            patch=lumps[names[k]];pw=struct.unpack_from('<h',patch)[0]
            patches.append((ox,oy,pw,patch))
            for x in range(max(0,ox),min(w,ox+pw)):hits[x]+=1
        columns={x:bytearray(h) for x in range(w) if hits[x]>1}
        coverage={x:bytearray(h) for x in columns}
        for ox,oy,pw,patch in patches:
            for x,column in columns.items():
                if not ox<=x<ox+pw:continue
                pos=struct.unpack_from('<I',patch,8+4*(x-ox))[0]
                while patch[pos]!=255:
                    count=patch[pos+1];y=oy+patch[pos]
                    # Match vanilla R_DrawColumnInCache, including top clipping.
                    if y<0:count+=y;y=0
                    count=min(count,h-y)
                    if count>0:
                        assert pos+3+count<=len(patch)
                        column[y:y+count]=patch[pos+3:pos+3+count]
                        coverage[x][y:y+count]=bytes([1])*count
                    pos+=patch[pos+1]+4
        if not columns:continue
        offsets=[65535]*w
        for x,column in columns.items():
            assert all(coverage[x]), ('Uninitialized composite pixels',name,x)
            value=bytes(column)
            if value not in unique:unique[value]=len(blob);blob.extend(value)
            offsets[x]=unique[value]
        tables.append((index,name,offsets))
        report.append(dict(index=index,name=name,width=w,height=h,composite_bytes=len(columns)*h))
    assert len(blob)<65535
    lines=['/* Generated from the pinned room WAD. Read-only, not zone allocated. */',
           'static const unsigned char dp_texture_columns[] = {']
    for i in range(0,len(blob),24):lines.append(','.join(map(str,blob[i:i+24]))+',')
    lines.append('};')
    for index,name,offsets in tables:
        lines.append('static const unsigned short dp_columns_%d[] = {%s};'%(index,','.join(map(str,offsets))))
    lines.append('static const byte *DP_FixedColumn(int texture, int column) {\n unsigned offset;\n switch(texture) {')
    for index,name,offsets in tables:
        lines.append('case %d: if ((unsigned)column >= %d) I_Error("Fixed texture bounds"); offset=dp_columns_%d[column]; break;'%(index,len(offsets),index))
    lines.append('default: return NULL; }\n if(offset==65535) I_Error("Fixed texture mapping");\n return dp_texture_columns+offset;\n}')
    (engine/'dp_static_textures.h').write_text('\n'.join(lines)+'\n')
    p=engine/'r_data.c';s=p.read_text();anchor='byte*\nR_GetColumn'
    assert s.count(anchor)==1;s=s.replace(anchor,'#include "dp_static_textures.h"\n\n'+anchor)
    anchor='    if (!texturecomposite[tex])'
    assert s.count(anchor)==1
    s=s.replace(anchor,'    const byte *fixed = DP_FixedColumn(tex, col);\n    if (fixed) return (byte *)fixed;\n\n'+anchor)
    p.write_text(s)
    result=dict(column_bytes=len(blob),index_bytes=sum(len(t[2])*2 for t in tables),textures=report)
    (engine/'static-textures.json').write_text(json.dumps(result,indent=2)+'\n')
    return result
