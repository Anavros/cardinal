#version 120

attribute vec2 a_position;
attribute vec2 a_texcoord;

uniform mat4 u_ortho;
//uniform vec4 u_color;
//uniform vec2 u_scale;
//uniform vec2 u_slide;
//uniform mat4 u_transform;
//varying vec3 v_color; //goes into fragment shader

void main(void) {
/*
    gl_Position = vec4(
        a_position.x*u_scale.x+u_slide.x,
        a_position.y*u_scale.y+u_slide.y,
        0.0,
        1.0);
*/
    gl_Position = vec4(a_position, 0.0, 1.0);
    //gl_Position = u_ortho * vec4(a_position, 0.0, 1.0);
    gl_TexCoord[0] = vec4(a_texcoord, 0.0, 0.0);
    //v_color = vec3(a_position.x, 0.0, -a_position.x);
}
