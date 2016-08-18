#version 120

uniform sampler2D tex_color;

void main(void) {
    gl_FragColor = texture2D(tex_color, gl_TexCoord[0].st);
}
