#!/usr/bin/env python3

from vispy import gloo, app, io
from vispy.gloo import gl
import numpy as np
import random

from objects import AutoCanvas

W, H, Z = 200, 200, 2
COLS, ROWS = 4, 4
SIZE, FLAT = 0.2, 1

def main():
    app.use_app('glfw')
    canvas = AutoCanvas(
        title="Hexes", size=(W, H), keys="interactive", px_scale=Z)
    program = gloo.Program(VERTEX, FRAGMENT)

    dirt_texture = gloo.Texture2D(io.imread('images/dirt.png'))
    grav_texture = gloo.Texture2D(io.imread('images/gravel.png'))
    hex_vertex = gloo.VertexBuffer(gen_single(SIZE, FLAT))
    hex_index = gloo.IndexBuffer(gen_index())
    hex_texcoords = gen_texcoords()

    hexmap = gen_map(COLS, ROWS)
    #io.imsave('hexmap.png', hexmap)

    program['a_position'] = hex_vertex
    program['a_texcoord'] = hex_texcoords
    program['u_texture'] = dirt_texture
    program['u_offset'] = (0, 0)

    cam = [0, 0, 1]  # mutable
    program['u_camera'] = cam


    @canvas.connect
    def on_draw(event):
        global printed
        gloo.clear((1,1,1,1))
        for c in range(COLS):
            for r in range(ROWS):
                if hexmap[c, r] == 0:
                    program['u_texture'] = dirt_texture
                else:
                    program['u_texture'] = grav_texture
                x, y = (c*(3*SIZE/4), r*SIZE/FLAT + (SIZE/2/FLAT if (c%2==0) else 0))
                program['u_offset'] = (x, y)
                program.draw('triangles', hex_index)

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

    @canvas.connect
    def on_mouse_release(event):
        if len(event.trail()) <= 1:
            x, y = event.pos
            x, y = screen_to_world(x, y, cam)
            c, r = world_to_index(x, y)
            print("x:{:.2f} y:{:.2f}".format(x, y))
            #touch(hexmap, c, r)

    canvas.start()
    app.run()


# TODO: integrate camera transformations
def world_to_index(x, y):
    c = int(round(x/(0.75*SIZE)))
    r = int(round((y-SIZE/2)/SIZE if c%2==0 else y/SIZE))
    #print("even" if c%2==0 else "odd")
    return c, r


def screen_to_world(x, y, camera):
    a, b, c = camera
    q = ((((x)/Z/W)*2)-1)/c - a
    r = ((((y)/Z/H)*2)-1)/c + b
    return q, -r


def touch(hexmap, c, r):
    hexmap[c, r] = 1 if hexmap[c, r] != 1 else 0
    return hexmap


def gen_map(cols, rows):
    return np.random.randint(2, size=(rows, cols)).astype(np.uint32)


def gen_single(size, flat=1):
    half = size/2
    quar = size/4
    x, y = 0, 0
    return np.array([
        (x, y),
        (x-quar, y+half/flat),   # tl
        (x+quar, y+half/flat),   # tr
        (x+half, y/flat),        # re
        (x+quar, y-half/flat),   # br
        (x-quar, y-half/flat),   # bl
        (x-half, y/flat),        # le
    ]).astype(np.float32)


def gen_texcoords():
    return np.array([
        (0.5, 0.5),
        (0.25, 1.0),  # tl
        (0.75, 1.0),  # tr
        (1.0, 0.5),   # re
        (0.75, 0.0),  # br
        (0.25, 0.0),  # bl
        (0.0, 0.5),   # le
    ]).astype(np.float32)


def gen_index():
    return np.array([
        0, 1, 2,
        0, 2, 3,
        0, 3, 4,
        0, 4, 5,
        0, 5, 6,
        0, 6, 1,
    ]).astype(np.uint32)


VERTEX = r"""
#version 120

attribute vec2 a_position;
attribute vec2 a_texcoord;
uniform vec3 u_camera;
uniform vec2 u_offset;

void main(void) {
    gl_Position = vec4((a_position+u_camera.xy+u_offset.xy)*u_camera.z, 0.0, 1.0);
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
