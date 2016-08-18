#version 120

attribute vec2 a_position;
attribute vec2 a_texcoord;

uniform float u_scale;

void main(void) {
    gl_Position = u_scale * vec4(a_position, 0.0, 1.0);
    gl_TexCoord[0] = vec4(a_texcoord, 0.0, 0.0);
}
