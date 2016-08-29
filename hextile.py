#!/usr/bin/env python3

from vispy import gloo, app, io
from vispy.gloo import gl
import numpy as np

from objects import AutoCanvas


def main():
    app.use_app('glfw')
    W, H, Z = 200, 200, 4
    canvas = AutoCanvas(
        title="Hexes", size=(W, H), keys="interactive", px_scale=Z)
    program = gloo.Program(VERTEX, FRAGMENT)

#    vertices = np.array([
#        (0, 0),         # center
#        (+0.5, 0),      # right point
#        (+0.25, +0.5),  # top right corner
#        (-0.25, +0.5),  # top left corner
#        (-0.5, 0),      # left point
#        (-0.25, -0.5),  # bottom left corner
#        (+0.25, -0.5),  # bottom right corner
#    ]).astype(np.float32)
#    indices = np.array([
#        0, 1, 2, 3, 4, 5, 6, 1
#    ]).astype(np.uint32)

    texture = gloo.Texture2D(io.imread('images/dirt.png'))
    vertex_data, indices = gen_vertices(0.5, 2, 2)
    buffers = gloo.VertexBuffer(vertex_data)
    element_buffer = gloo.IndexBuffer(indices)

    program.bind(buffers)
    program['u_texture'] = texture

    cam = [0, 0, 1]  # mutable
    program['u_camera'] = cam

    @canvas.connect
    def on_draw(event):
        gloo.clear((1,1,1,1))
        #program.draw('triangle_fan', element_buffer)
        program.draw('triangle_fan')

    @canvas.connect
    def on_mouse_move(event):
        if not event.buttons: return
        (nx, ny) = event.pos
        (ox, oy) = event.last_event.pos
        (dx, dy) = (nx-ox, ny-oy)
        cam[0] += dx/W/Z*2/cam[2]
        cam[1] += -dy/H/Z*2/cam[2]
        program['u_camera'] = cam

    @canvas.connect
    def on_mouse_wheel(event):
        #print(event.delta)
        cam[2] += event.delta[1]/10
        program['u_camera'] = cam

    canvas.start()
    app.run()


def gen_vertices(size, cols, rows):
    buf = np.zeros((rows*cols*7), 
        dtype=[("a_position", np.float32, 2), ("a_texcoord", np.float32, 2)])
    n_ind = 7
    ind = np.zeros((rows*cols*n_ind), dtype=np.uint32)
    half = size/2
    quarter = size/4
    v = 0
    i = 0
    for c in range(cols):
        for r in range(rows):
            (x, y) = (c*(3*quarter), r*size + (half if c%2 else 0))
            buf['a_position'][v] = (x, y)
            buf['a_texcoord'][v] = 0
            buf['a_position'][v+1] = (x-quarter, y+half) # tl
            buf['a_texcoord'][v+1] = 0
            buf['a_position'][v+2] = (x+quarter, y+half) # tr
            buf['a_texcoord'][v+2] = 0
            buf['a_position'][v+3] = (x+half, y) # re
            buf['a_texcoord'][v+3] = 0
            buf['a_position'][v+4] = (x+quarter, y-half) # br
            buf['a_texcoord'][v+4] = 0
            buf['a_position'][v+5] = (x-quarter, y-half) # bl
            buf['a_texcoord'][v+5] = 0
            buf['a_position'][v+6] = (x-half, y) # le
            buf['a_texcoord'][v+6] = 0
            
            #ind[i:i+8] = np.array([0, 1, 2, 3, 4, 5, 6, 1]) + v
            #v += 7
            #i += 8

#            ind[i:i+n_ind] = np.array([
#                0, 1, 2,
#                0, 2, 3,
#                0, 3, 4,
#                0, 4, 5,
#                0, 5, 6,
#                0, 6, 1,
#            ]).astype(np.uint32) + v
            ind[i:i+n_ind] = np.array([
                0, 1, 2, 3, 4, 5, 6
            ]).astype(np.uint32) + v
            v += 7
            i += n_ind
    return buf, ind


def gen_indices(vertex_data, mode, cols, rows):
    if mode == 'triangles':
        indices = np.zeros((rows*cols*15), dtype=np.uint32)
        form = np.array([
            0, 1, 2,
            0, 2, 3,
            0, 3, 4,
            0, 4, 5,
            0, 5, 6,
        ]).astype(np.uint32)

VERTEX = r"""
#version 120

attribute vec2 a_position;
attribute vec2 a_texcoord;
uniform vec3 u_camera;

void main(void) {
    gl_Position = vec4((a_position+u_camera.xy)*u_camera.z, 0.0, 1.0);
    gl_TexCoord[0] = vec4(a_texcoord, 0.0, 0.0);
}
"""
FRAGMENT = r"""
#version 120

uniform sampler2D u_texture;

void main(void) {
    gl_FragColor = texture2D(u_texture, gl_TexCoord[0].st);
}
"""

if __name__ == '__main__':
    main()
