#version 120

attribute vec2 a_ver;
attribute vec2 a_tex;

void main(void) {
    gl_Position = vec4(a_ver, 0.0, 1.0);
    gl_TexCoord[0] = vec4(a_tex, 0.0, 0.0);
}
