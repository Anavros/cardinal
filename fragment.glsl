#version 120

//varying vec3 v_color;
//uniform sampler2D texture1;
uniform vec4 u_color;

void main(void) {
    //gl_FragColor = vec4(v_color, 1.0);
    gl_FragColor = u_color;
    //gl_FragColor = texture2D(texture1, gl_TexCoord[0].st);
}
