# SPDX-License-Identifier: GPL-3.0-only
"""Build-directory adaptations of the pinned engine; original notices stay intact."""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
UPSTREAM=ROOT/'third_party/doomgeneric/doomgeneric'
def prepare(out):
    out.mkdir(parents=True,exist_ok=True)
    for path in UPSTREAM.iterdir():
        if path.suffix in ('.c','.h'):
            (out/path.name).write_bytes(path.read_bytes())
    def change(file,old,new):
        path=out/file;s=path.read_text()
        if s.count(old)!=1:raise RuntimeError('Pinned engine changed: '+file+' '+repr(old))
        path.write_text(s.replace(old,new))
    for file,macro,value in [('r_defs.h','MAXDRAWSEGS',64),('r_things.h','MAXVISSPRITES',32),
                              ('r_plane.c','MAXVISPLANES',32),('r_plane.c','MAXOPENINGS','(SCREENWIDTH*16)'),
                              ('r_draw.c','MAXWIDTH','SCREENWIDTH'),('r_draw.c','MAXHEIGHT','SCREENHEIGHT')]:
        path=out/file;s=path.read_text();s,n=re.subn(r'^#define\s+'+macro+r'\s+[^\n]+',
            '#define '+macro+' '+str(value),s,flags=re.M)
        if n!=1:raise RuntimeError('Missing renderer limit: '+macro)
        path.write_text(s)
    change('r_plane.c','    // make a new visplane','    if (lastvisplane >= visplanes + MAXVISPLANES)\n        I_Error("R_CheckPlane capacity");\n    // make a new visplane')
    # Guard BEFORE each allocation/copy, unlike vanilla's post-frame range check.
    change('r_plane.h','extern  short*\t\tlastopening;','extern  short*\t\tlastopening;\nvoid DP_CheckOpenings(int n);')
    with (out/'r_plane.c').open('a') as f:
        f.write('\nvoid DP_CheckOpenings(int n) { if (n < 0 || lastopening < openings || n > MAXOPENINGS-(lastopening-openings)) I_Error("Doom room: openings capacity"); }\n')
    change('r_segs.c','\t    ds_p->maskedtexturecol = maskedtexturecol = lastopening - rw_x;',
           '\t    DP_CheckOpenings(rw_stopx-rw_x);\n\t    ds_p->maskedtexturecol = maskedtexturecol = lastopening - rw_x;')
    for part in ('ceilingclip','floorclip'):
        old='\tmemcpy (lastopening, '+part+'+start, 2*(rw_stopx-start));'
        change('r_segs.c',old,'\tDP_CheckOpenings(rw_stopx-start);\n'+old)
    return out
if __name__=='__main__':
    import sys
    prepare(Path(sys.argv[1]))
