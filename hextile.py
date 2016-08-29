#!/usr/bin/env python3

from vispy import gloo, app, io
from vispy.gloo import gl
from vispy.util import transforms
import numpy as np
import random

from objects import AutoCanvas

W, H, Z = 200, 200, 4
COLS, ROWS = 32, 16
SIZE, FLAT = 0.2, 1

def main():
    app.use_app('glfw')
    gl.glEnable(gl.GL_BLEND)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    canvas = AutoCanvas(
        title="Hexes", size=(W, H), keys="interactive", px_scale=Z)
    program = gloo.Program(VERTEX, FRAGMENT)

    dirt_texture = gloo.Texture2D(io.imread('images/dirt.png'))
    grav_texture = gloo.Texture2D(io.imread('images/gravel.png'))
    hex_vertex = gloo.VertexBuffer(gen_single(SIZE, FLAT))
    hex_index = gloo.IndexBuffer(gen_index())
    hex_texcoords = gen_texcoords()

    hexmap, heightmap = gen_map(COLS, ROWS)
    #io.imsave('hexmap.png', hexmap)

    program['a_position'] = hex_vertex
    program['a_texcoord'] = hex_texcoords
    program['u_texture'] = dirt_texture
    program['u_offset'] = (0, 0)
    program['u_overlay'] = 0.0

    cam = [0, 0, 1]  # mutable
    hover = [0, 0]
    program['u_camera'] = cam

    # 3D Matrices
    mats = CheatyStorage(
        model=np.eye(4, dtype=np.float32),
        view=np.eye(4, dtype=np.float32),
        #perspective=transforms.ortho(0, 1, 0, 1, 0, 1),
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
                if hexmap[r, c] == 0:
                    program['u_texture'] = dirt_texture
                else:
                    program['u_texture'] = grav_texture
                x, y = (c*(3*SIZE/4), r*SIZE/FLAT + (SIZE/2/FLAT if (c%2==0) else 0))
                z = heightmap[r, c]

                #program['u_offset'] = (x, y)
                mats.model = transforms.translate((x, y, -2-z/10))
                program['m_model'] = mats.model
#                if [c, r] == hover:
#                    program['u_overlay'] = 0.1
#                else:
#                    program['u_overlay'] = 0.0
                program.draw('triangles', hex_index)

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
        elif event.buttons == []:
            x, y = event.pos
            c, r = screen_to_index(x, y, cam)
            hover[0] = c
            hover[1] = r
        elif event.buttons == [1]:
            (nx, ny) = event.pos
            (ox, oy) = event.last_event.pos
            (dx, dy) = (nx-ox, ny-oy)
            #cam[0] += dx/W/Z*2/cam[2]
            #cam[1] += -dy/H/Z*2/cam[2]
            #program['u_camera'] = cam
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
    hexmap = np.random.randint(2, size=(rows, cols), dtype=np.uint32)
    heightmap = np.random.randint(2, size=(rows, cols), dtype=np.uint32)
    return hexmap, heightmap


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


class CheatyStorage(object):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v


VERTEX = r"""
#version 120

attribute vec2 a_position;
attribute vec2 a_texcoord;
uniform mat4 m_model;
uniform mat4 m_view;
uniform mat4 m_perspective;

uniform float u_overlay;

void main(void) {
    gl_Position = m_perspective * m_view * m_model * vec4(a_position, 0.0, 1.0);
    gl_TexCoord[0] = vec4(a_texcoord, 0.0, 0.0);
}
"""
FRAGMENT = r"""
#version 120

uniform sampler2D u_texture;
uniform float u_overlay;

void main(void) {
    gl_FragColor = texture2D(u_texture, gl_TexCoord[0].st) + vec4(u_overlay);
}
"""

if __name__ == '__main__':
    main()
