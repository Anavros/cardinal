#version 120

uniform sampler2D t_gui;

void main(void) {
    gl_FragColor = texture2D(t_gui, gl_TexCoord[0].st);
}
