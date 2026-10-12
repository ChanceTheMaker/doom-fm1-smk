# SPDX-License-Identifier: GPL-3.0-only
"""Build-directory adaptations of the pinned engine; original notices stay intact."""
import re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
UPSTREAM=ROOT/'third_party/doomgeneric/doomgeneric'
def prepare(out,campaign=False):
    out.mkdir(parents=True,exist_ok=True)
    for path in UPSTREAM.iterdir():
        if path.suffix in ('.c','.h'):
            (out/path.name).write_bytes(path.read_bytes())
    def change(file,old,new):
        path=out/file;s=path.read_text()
        if s.count(old)!=1:raise RuntimeError('Pinned engine changed: '+file+' '+repr(old))
        path.write_text(s.replace(old,new))
    for file,macro,value in [('net_defs.h','BACKUPTICS',16),('r_defs.h','MAXDRAWSEGS',64),('r_things.h','MAXVISSPRITES',32),
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
    # A display-only snapshot lets the physical 240px LCD render readable menus.
    with (out/'m_menu.c').open('a') as f:
        f.write('\n'+(ROOT/'src/common/menu_engine.inc').read_text())
    change('m_menu.c', '    if (messageToPrint)\n    {\n\tif (messageNeedsInput)',
           '    if (messageToPrint)\n    {\n        if (key == KEY_ENTER) key = key_menu_confirm;\n\tif (messageNeedsInput)')
    for function in ('M_LoadGame', 'M_SaveGame'):
        change('m_menu.c','void '+function+' (int choice)\n{',
               'void '+function+' (int choice)\n{\n    M_StartMessage("Saves are not available in this test build.", NULL, false);\n    return;')
    if campaign:
        path=out/'s_sound.c';path.write_text('void dp_game_sound(void *,int,int);\n'+path.read_text())
        change('s_sound.c','void S_StartSound(void *origin_p, int sfx_id)\n{', 'void S_StartSound(void *origin_p, int sfx_id)\n{\n    dp_game_sound(origin_p,sfx_id,snd_SfxVolume); return;')
        for file in ('p_inter.c','g_game.c'):
            path=out/file;path.write_text('#include "campaign.h"\n'+path.read_text())
        change('p_inter.c','    target->flags &= ~(MF_SHOOTABLE|MF_FLOAT|MF_SKULLFLY);',
               '    if(source && source->player && (target->flags & MF_COUNTKILL)) dp_campaign_kill(target->type==MT_TROOP?200:100);\n    target->flags &= ~(MF_SHOOTABLE|MF_FLOAT|MF_SKULLFLY);')
        change('g_game.c','    p->readyweapon = p->pendingweapon = wp_pistol;',
               '    p->readyweapon = p->pendingweapon = wp_shotgun;\n    p->weaponowned[wp_shotgun]=true; p->ammo[am_shell]=40;')
        change('g_game.c','    P_SetupLevel (gameepisode, gamemap, 0, gameskill);',
               '    dp_campaign_load();\n    P_SetupLevel (gameepisode, gamemap, 0, gameskill);')
        change('g_game.c','    gamemap = map;', '    gamemap = map;\n    dp_campaign_reset();')
        change('g_game.c','    gamemap = wminfo.next+1;',
               '    if (gamemap>=3) { G_DeferedInitNew(gameskill,1,1); return; }\n    gamemap = wminfo.next+1;')
        change('m_menu.c','int\t\t\tscreenblocks = 10;', 'int\t\t\tscreenblocks = 11;')
    return out
if __name__=='__main__':
    import sys
    prepare(Path(sys.argv[1]))
