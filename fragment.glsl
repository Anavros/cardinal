#version 120

uniform sampler2D tex_color;

void main(void) {
    // gl_TexCoord[0].st is a vec2 with uv coords
    // we could probably manipulate those in the split function
    // it's actually directly set from a_texcoords
    // so 0, 0; 0, 1; etc
    gl_FragColor = texture2D(tex_color, gl_TexCoord[0].st);
}

void split_stretch(void) {
    // we need to know three things
    // the normal texture coords
    // the size of the texture in pixels
    // and the amount of edge we're supposed to preserve
    // assume for this first test:
    // texcoords are 00 01 10 11 like normal
    // size of the texture is 32x32
    // and the edge depth is 12 pixels
    // so we need 12 pixels out of 32 in terms of texcoords
    // which we can get by division
    // each pixel takes up 1/32 of the texture
    // so the edge depth would be 12/32 or 3/8 aka 0.375
    // 0.375 -> 0.625 would give us the internal part
    // the other part is making sure the rest stays pixel-perfect
    // so we would actually need the screen size as well
    // btw most of this could just be calculated cpu-side
    // 12 pixels in a 100x100 screen would be 0.12
    // so our split function would take screen size and texture size
    // and generate vertices and texcoords
    // for this example:
    /* a_vertices = -1, +1; +1, +1
     *  -1 +1
     *
     *
     *
     *
     *
     */
}
