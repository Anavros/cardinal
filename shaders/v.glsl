
attribute vec2 a_vertices;
attribute vec2 a_texcoords;

void main(void) {
    gl_Position = vec4(a_vertices, 0.0, 1.0);
}
