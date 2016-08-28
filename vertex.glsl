#version 120

attribute vec2 a_position;
attribute vec2 a_texcoord;

void main(void) {
    gl_Position = vec4(a_position, 0.0, 1.0);
    gl_TexCoord[0] = vec4(a_texcoord, 0.0, 0.0);
}
