#!/usr/bin/env python3

from vispy import gloo, app, io
from vispy.gloo import gl
from vispy.util import transforms
import numpy as np
import random

from objects import AutoCanvas

W, H, Z = 200, 200, 4
COLS, ROWS = 8, 8
SIZE, FLAT = 1, 1

def main():
    app.use_app('glfw')
    gl.glEnable(gl.GL_BLEND)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    canvas = AutoCanvas(
        title="Hexes", size=(W, H), keys="interactive", px_scale=Z)
    program = gloo.Program(VERTEX, FRAGMENT)

    dirt_texture = gloo.Texture2D(io.imread('images/dirt.png'), wrapping='repeat')
    grav_texture = gloo.Texture2D(io.imread('images/gravel.png'), wrapping='repeat')
    farm_texture = gloo.Texture2D(io.imread('images/farmland_dry.png'), wrapping='repeat')
    hex_vertex = gloo.VertexBuffer(gen_single(SIZE))
    hex_index = gloo.IndexBuffer(gen_index())
    hex_texcoords = gen_texcoords()

    hexmap, heightmap = gen_map(COLS, ROWS)
    #io.imsave('hexmap.png', hexmap)

    program['a_position'] = hex_vertex
    program['a_texcoord'] = hex_texcoords
    program['u_texture'] = dirt_texture

    # 3D Matrices
    mats = CheatyStorage(
        model=np.eye(4, dtype=np.float32),
        view=np.eye(4, dtype=np.float32),
        perspective=transforms.perspective(90.0, 1.0, 1.0, 20.0),
    )

    mats.model = np.dot(mats.model, transforms.translate((0, 0, -2)))
    program['m_model'] = mats.model
    program['m_view'] = mats.view
    program['m_perspective'] = mats.perspective

    gloo.set_state(clear_color=(1, 1, 1, 1), depth_test=True)

    @canvas.connect
    def on_draw(event):
        global printed
        gloo.clear(color=True, depth=True)
        for c in range(COLS):
            for r in range(ROWS):
                z = hexmap[r, c]
                if z == 0:
                    program['u_texture'] = farm_texture
                    dip = (0, 0, 0)
                elif z == 1:
                    program['u_texture'] = dirt_texture
                    dip = (0, 0.5, 0.5)
                elif z == 2:
                    program['u_texture'] = grav_texture
                    dip = (0.5, 0.5, 0.5)
                x, y = (c*(3*SIZE/4), r*SIZE + (SIZE/2 if (c%2==0) else 0))

                ver, tex, tops, sides = gen(SIZE, z/2, dip)
                program['a_position'] = gloo.VertexBuffer(ver)
                program['a_texcoord'] = tex

                mats.model = transforms.translate((x, y, -2))
                program['m_model'] = mats.model
                program['u_shade'] = 0.0
                program.draw('triangles', gloo.IndexBuffer(tops))
                program['u_shade'] = 0.1
                program.draw('triangles', gloo.IndexBuffer(sides))

    @canvas.connect
    def on_mouse_move(event):
        # Middle-Click
        if event.buttons == [3]:
            (nx, ny) = event.pos
            (ox, oy) = event.last_event.pos
            (dx, dy) = (nx-ox, ny-oy)
            wx = dx*10/W/Z
            wy = dy*10/H/Z
            mats.view = np.dot(mats.view, transforms.rotate(wy*10, [1,0,0]))
            mats.view = np.dot(mats.view, transforms.rotate(wx*10, [0,1,0]))
            program['m_view'] = mats.view
        # Right-Click
        if event.buttons == [2]:
            (nx, ny) = event.pos
            (ox, oy) = event.last_event.pos
            (dx, dy) = (nx-ox, ny-oy)
            wx = dx*10/W/Z
            wy = dy*10/H/Z
            mats.view = np.dot(mats.view, transforms.rotate(wy*25, [1,0,0]))
            mats.view = np.dot(mats.view, transforms.rotate(-wx*25, [0,1,0]))
            mats.view = np.dot(mats.view, transforms.translate((-wx*1, wy*1, 0)))
            program['m_view'] = mats.view
        elif event.buttons == [1]:
            (nx, ny) = event.pos
            (ox, oy) = event.last_event.pos
            (dx, dy) = (nx-ox, ny-oy)
            wx = dx*10/W/Z
            wy = dy*10/H/Z
            mats.view = np.dot(mats.view, transforms.translate((wx, -wy, 0)))
            program['m_view'] = mats.view

    @canvas.connect
    def on_mouse_wheel(event):
        #print(event.delta)
        #cam[2] += event.delta[1]/10
        #program['u_camera'] = cam
        mats.view = np.dot(mats.view, transforms.translate((0, 0, event.delta[1])))
        #mats.view = np.dot(mats.view, transforms.rotate(event.delta[1], [0,0,1]))
        program['m_view'] = mats.view

    @canvas.connect
    def on_mouse_release(event):
        if len(event.trail()) <= 1:
            mats.view = np.dot(mats.view, transforms.translate((+0.01, +0.01, -0.1)))
            program['m_view'] = mats.view

            #x, y = event.pos
            #x, y = screen_to_world(x, y, cam)
            #c, r = world_to_index(x, y)
            #print("x:{:.2f} y:{:.2f}".format(x, y))
            #touch(hexmap, c, r)

    canvas.start()
    app.run()


def screen_to_index(x, y, camera):
    x, y = screen_to_world(x, y, camera)
    return world_to_index(x, y)


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
    hexmap = np.random.randint(3, size=(rows, cols), dtype=np.uint32)
    heightmap = np.random.randint(2, size=(rows, cols), dtype=np.uint32)
    return hexmap, heightmap


def gen(size, height, dip=(0, 0, 0)):
    d_top, d_left, d_right = dip
    half = size/2
    quar = size/4
    x, y = 0, 0
    vertices = np.array([
        (x, y, height),
        (x-quar, y+half, height-d_top),   # tl
        (x+quar, y+half, height-d_top),   # tr
        (x+half, y, height-d_right),        # re
        (x+quar, y-half, height-d_right),   # br
        (x-quar, y-half, height-d_left),   # bl
        (x-half, y, height-d_left),        # le
        (x, y, -1),
        (x-quar, y+half, -1),   # tl
        (x+quar, y+half, -1),   # tr
        (x+half, y, -1),        # re
        (x+quar, y-half, -1),   # br
        (x-quar, y-half, -1),   # bl
        (x-half, y, -1),        # le
    ], dtype=np.float32)
    texcoords = np.array([
        (0.5, 0.5),   # 00 0
        (0.25, 1.0),  # tl 1
        (0.75, 1.0),  # tr 2
        (1.0, 0.5),   # re 3
        (0.75, 0.0),  # br 4
        (0.25, 0.0),  # bl 5
        (0.0, 0.5),   # le 6
        (1.5, 1.5),   # 00 7
        (1.25, 2.0),  # tl 8
        (1.75, 2.0),  # tr 9
        (2.0, 1.5),   # re 10
        (1.75, 1.0),  # br 11
        (1.25, 1.0),  # bl 12
        (1.0, 1.5),   # le 13
    ], dtype=np.float32)
    tops = np.array([
        0, 1, 2,
        0, 2, 3,
        0, 3, 4,
        0, 4, 5,
        0, 5, 6,
        0, 6, 1,
        7, 8, 9,
        7, 9, 10,
        7, 10, 11,
        7, 11, 12,
        7, 12, 13,
        7, 13, 8,
    ], dtype=np.uint8)
    sides = np.array ([
        1, 8, 2,
        9, 8, 2,
        2, 9, 3,
        10, 9, 3,
        3, 10, 4,
        11, 10, 4,
        4, 11, 5,
        12, 11, 5,
        5, 12, 6,
        13, 12, 6,
        6, 13, 1,
        8, 13, 1,
    ], dtype=np.uint8)
    return vertices, texcoords, tops, sides


def gen_single(size):
    half = size/2
    quar = size/4
    x, y = 0, 0
    return np.array([
        (x, y, 0),
        (x-quar, y+half, 0),   # tl
        (x+quar, y+half, 0),   # tr
        (x+half, y, 0),        # re
        (x+quar, y-half, 0),   # br
        (x-quar, y-half, 0),   # bl
        (x-half, y, 0),        # le
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


class CheatyStorage(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v


VERTEX = r"""
#version 120

attribute vec3 a_position;
attribute vec2 a_texcoord;
uniform mat4 m_model;
uniform mat4 m_view;
uniform mat4 m_perspective;
uniform float u_shade;

void main(void) {
    gl_Position = m_perspective * m_view * m_model * vec4(a_position, 1.0);
    gl_TexCoord[0] = vec4(a_texcoord, 0.0, 0.0);
}
"""
FRAGMENT = r"""
#version 120

uniform sampler2D u_texture;
uniform float u_shade;

void main(void) {
    gl_FragColor = texture2D(u_texture, gl_TexCoord[0].st);
    gl_FragColor.xyz -= vec3(u_shade);
}
"""

if __name__ == '__main__':
    main()
