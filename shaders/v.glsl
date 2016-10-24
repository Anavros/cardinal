#version 120

attribute vec2 a_vertices;
attribute vec2 a_texcoords;
attribute vec3 a_color;

varying vec3 v_color;

void main(void) {
    gl_Position = vec4(a_vertices, 0.0, 1.0);
    v_color = a_color;
}
