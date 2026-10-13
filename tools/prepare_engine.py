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
        # The LCD frontend draws the menu snapshot itself. Do not also invoke
        # legacy bitmap menus: their patches are absent from the compact WAD.
        change('m_menu.c','void M_Drawer (void)\n{',
               'void M_Drawer (void)\n{\n#ifdef DP_NATIVE_ART\n    return;\n#endif')
        change('m_menu.c','        // Deactivate menu\n',
               '        // Deactivate menu\n#ifdef DP_NATIVE_ART\n        if (currentMenu != &MainDef && currentMenu->prevMenu) {\n            currentMenu->lastOn = itemOn; currentMenu = currentMenu->prevMenu;\n            itemOn = currentMenu->lastOn; S_StartSound(NULL,sfx_swtchn); return true;\n        }\n#endif\n')
        # View-weapon sources are stored at half resolution only in native-art
        # builds. Restore their original projection without a decode buffer.
        path=out/'r_things.c';text=path.read_text()
        begin=text.index('void R_DrawPSprite (');end=text.index('\nvoid R_DrawPlayerSprites',begin)
        part=text[begin:end]
        part=part.replace('    // calculate edges of the shape', '#ifdef DP_NATIVE_ART\n    const int asset_scale=2;\n#else\n    const int asset_scale=1;\n#endif\n    // calculate edges of the shape')
        part=part.replace('tx -= spriteoffset[lump];','tx -= spriteoffset[lump]*asset_scale;')
        part=part.replace('tx +=  spritewidth[lump];','tx += spritewidth[lump]*asset_scale;')
        part=part.replace('(BASEYCENTER<<FRACBITS)+FRACUNIT/2-(psp->sy-spritetopoffset[lump])','((BASEYCENTER<<FRACBITS)+FRACUNIT/2-psp->sy)/asset_scale+spritetopoffset[lump]')
        part=part.replace('vis->scale = pspritescale<<detailshift;', 'vis->scale = (pspritescale*asset_scale)<<detailshift;')
        part=part.replace('vis->xiscale = -pspriteiscale;', 'vis->xiscale = -pspriteiscale/asset_scale;')
        part=part.replace('vis->xiscale = pspriteiscale;', 'vis->xiscale = pspriteiscale/asset_scale;')
        path.write_text(text[:begin]+part+text[end:])
        change('m_controls.c','int key_nextweapon = 0;', "int key_nextweapon = ']' ;")
        change('p_switch.c', '\t    switchlist[index++] = R_TextureNumForName(DEH_String(alphSwitchList[i].name1));',
               '            if (R_CheckTextureNumForName(DEH_String(alphSwitchList[i].name1)) < 0 || R_CheckTextureNumForName(DEH_String(alphSwitchList[i].name2)) < 0) continue;\n\t    switchlist[index++] = R_TextureNumForName(DEH_String(alphSwitchList[i].name1));')
        path=out/'s_sound.c';path.write_text('#include "music.h"\nvoid dp_game_sound(void *,int,int);\n'+path.read_text())
        change('s_sound.c','void S_StartSound(void *origin_p, int sfx_id)\n{', 'void S_StartSound(void *origin_p, int sfx_id)\n{\n    dp_game_sound(origin_p,sfx_id,snd_SfxVolume); return;')
        for signature, action in [
            ('void S_SetMusicVolume(int volume)', 'dp_music_volume(volume < 0 ? 0 : (unsigned)volume);'),
            ('void S_ChangeMusic(int musicnum, int looping)', 'dp_music_start();'),
            ('void S_StopMusic(void)', 'dp_music_stop();'),
            ('void S_PauseSound(void)', 'dp_music_pause(1);'),
            ('void S_ResumeSound(void)', 'dp_music_pause(0);')]:
            change('s_sound.c', signature+'\n{', signature+'\n{\n    '+action+' return;')
        for file in ('p_inter.c','g_game.c'):
            path=out/file;path.write_text('#include "campaign.h"\n'+path.read_text())
        change('p_inter.c','    target->flags &= ~(MF_SHOOTABLE|MF_FLOAT|MF_SKULLFLY);',
               '    if(source && source->player && (target->flags & MF_COUNTKILL)) dp_campaign_kill(target->type==MT_TROOP?200:100);\n    target->flags &= ~(MF_SHOOTABLE|MF_FLOAT|MF_SKULLFLY);')
        change('g_game.c','    p->readyweapon = p->pendingweapon = wp_pistol;',
               '    p->readyweapon = p->pendingweapon = wp_shotgun;\n    p->weaponowned[wp_shotgun]=true; p->ammo[am_shell]=40;')
        change('g_game.c','    P_SetupLevel (gameepisode, gamemap, 0, gameskill);',
               '    dp_campaign_load();\n    P_SetupLevel (gameepisode, gamemap, 0, gameskill);')
        change('g_game.c','    gamemap = map;', '    gamemap = map;\n    dp_campaign_reset();')
        # The original campaign supplies its own results/replay screen. MAP06
        # must not enter Doom II's commercial story finale after intermission.
        change('g_game.c','    gameaction = ga_worlddone;',
               '    gameaction = ga_worlddone;\n    return; /* custom campaign: no commercial story finale */')
        change('g_game.c','    gamemap = wminfo.next+1;',
               '    if (gamemap>=DP_CAMPAIGN_LEVELS) { G_DeferedInitNew(gameskill,1,1); return; }\n    gamemap = wminfo.next+1;')
        change('m_menu.c','int\t\t\tscreenblocks = 10;', 'int\t\t\tscreenblocks = 11;')
    return out
if __name__=='__main__':
    import sys
    prepare(Path(sys.argv[1]))
