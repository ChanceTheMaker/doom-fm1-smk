/* SPDX-License-Identifier: GPL-3.0-only */
/* Appended to the host r_data.c copy only. Compare every room composite column. */
void DP_ExportTextureColumns(void) {
    const char *path=getenv("DOOM_TEXTURE_REPORT");
    if(!path)return;
    const char *names[]={"GRAY1","GRAYBIG","LITE3","SW1GRAY","SW2GRAY","DLEVSIGN"};
    FILE *f=fopen(path,"wb");
    if(!f)I_Error("Texture report open failed");
    for(unsigned n=0;n<sizeof(names)/sizeof(names[0]);n++) {
        int t=R_TextureNumForName(names[n]);
        for(int x=0;x<textures[t]->width;x++) {
            if(texturecolumnlump[t][x]>=0)continue;
            const byte *p=R_GetColumn(t,x);
            unsigned h=textures[t]->height;
            if(fwrite(p,1,h,f)!=h)I_Error("Texture report write failed");
        }
    }
    if(fclose(f))I_Error("Texture report close failed");
}
