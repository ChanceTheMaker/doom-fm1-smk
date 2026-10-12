# SPDX-License-Identifier: GPL-3.0-only
"""Freeze the pinned mapped WAD's directory in read-only program storage."""
import hashlib,struct
EXPECTED='5382808534297f82d29873d9132410dcb20f314e01f58f1ec4c653f7f0ddf98d'
def freeze(engine,wad):
    data=wad.read_bytes()
    if hashlib.sha256(data).hexdigest()!=EXPECTED: raise ValueError('Unexpected static WAD')
    _,count,directory=struct.unpack_from('<4sII',data)
    def change(file,old,new):
        p=engine/file;s=p.read_text()
        if s.count(old)!=1: raise ValueError('Pinned engine changed: '+file)
        p.write_text(s.replace(old,new))
    change('w_wad.h','extern lumpinfo_t *lumpinfo;', 'extern const lumpinfo_t *lumpinfo;')
    change('w_checksum.c','sha1_context_t *sha1_context, lumpinfo_t *lump', 'sha1_context_t *sha1_context, const lumpinfo_t *lump')
    p=engine/'w_wad.c';s=p.read_text()
    # Exact top-level function boundaries in the pinned source.
    def function(signature,body):
        nonlocal s
        start=s.index(signature);end=s.index('\n}',start)+2
        s=s[:start]+signature+'\n{\n'+body+'\n}'+s[end:]
    start=s.index('static void ExtendLumpInfo(');end=s.index('\n}',start)+2
    s=s[:start]+s[end:]
    rows=[]
    for i in range(count):
        off,size,name=struct.unpack_from('<II8s',data,directory+16*i)
        assert off+size<=len(data)
        rows.append('    {{'+','.join(str(x) for x in name)+'}, &dp_static_file, '+str(off)+', '+str(size)+', NULL, NULL},')
    table='static wad_file_t dp_static_file;\nstatic const lumpinfo_t dp_static_lumps[] = {\n'+'\n'.join(rows)+'\n};\n'
    s=s.replace('lumpinfo_t *lumpinfo;', table+'const lumpinfo_t *lumpinfo = dp_static_lumps;')
    s=s.replace('static lumpinfo_t **lumphash;', 'static const lumpinfo_t **lumphash;')
    function('wad_file_t *W_AddFile (char *filename)', '''    if (numlumps) I_Error("Only the embedded WAD is supported");
    wad_file_t *file = W_OpenFile(filename);
    if (!file) return NULL;
    if (!file->mapped || file->length != '''+str(len(data))+''') I_Error("Static WAD mapping mismatch");
    for (unsigned i=0;i<'''+str(count)+''';i++) {
        const unsigned char *d=file->mapped+'''+str(directory)+'''+16*i;
        unsigned off=(unsigned)d[0]|(unsigned)d[1]<<8|(unsigned)d[2]<<16|(unsigned)d[3]<<24;
        unsigned len=(unsigned)d[4]|(unsigned)d[5]<<8|(unsigned)d[6]<<16|(unsigned)d[7]<<24;
        if (off!=(unsigned)dp_static_lumps[i].position || len!=(unsigned)dp_static_lumps[i].size || memcmp(d+8,dp_static_lumps[i].name,8)) I_Error("Static WAD directory mismatch");
    }
    dp_static_file=*file;
    numlumps='''+str(count)+''';
    return file;''')
    function('void *W_CacheLumpNum(int lumpnum, int tag)', '''    (void)tag;
    if ((unsigned)lumpnum >= numlumps) I_Error("W_CacheLumpNum bounds");
    return dp_static_file.mapped + lumpinfo[lumpnum].position;''')
    function('void W_ReleaseLumpNum(int lumpnum)', '''    if ((unsigned)lumpnum >= numlumps) I_Error("W_ReleaseLumpNum bounds");''')
    function('void W_GenerateHashTable(void)', '    /* One immutable WAD: use the bounded linear lookup, no RAM hash chains. */')
    s=s.replace('    lumpinfo_t *lump_p;', '    const lumpinfo_t *lump_p;').replace('    lumpinfo_t *l;', '    const lumpinfo_t *l;')
    p.write_text(s)
    return count
